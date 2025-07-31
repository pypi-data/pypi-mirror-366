import logging
import os
import math
from concurrent import futures

from ks3.exception import KS3ClientError
from ks3.multipart import MultiPartUpload, PartInfo
from ks3.utils import ChunkIO, ResumeRecordManager, DEFAULT_PART_SIZE, MAX_PARTS, MAX_SIZE, MIN_SIZE, \
    calculate_string_md5

logger = logging.getLogger(__name__)

sse_c_header_keys = ['x-kss-server-side-encryption-customer-algorithm',
                     'x-kss-server-side-encryption-customer-key',
                     'x-kss-server-side-encryption-customer-key-MD5']

init_header_keys = ['Cache-Control', 'Content-Disposition', 'Content-Encoding', 'Content-Type', 'Expires',
                    'x-kss-storage-class', 'x-kss-tagging', 'x-kss-forbid-overwrite', 'x-kss-acl',
                    'x-kss-grant-read', 'x-kss-grant-full-control', 'x-kss-server-side-encryption',
                    ]
init_header_keys.extend(sse_c_header_keys)

upload_part_header_keys = sse_c_header_keys

complete_upload_header_keys = ['x-kss-forbid-overwrite', 'x-kss-callbackurl', 'x-kss-callbackbody',
                               'x-kss-callbackauth']


class UploadTask:
    def __init__(
            self, key, bucket, src_file,
            executor,
            part_size=DEFAULT_PART_SIZE,
            resumable=False,
            resumable_filename=None,
    ):
        """
        key: 需要上传的Key对象（ks3.key.Key）
        bucket: 需要上传到的Bucket对象（ks3.bucket.Bucket）
        filename: 待上传的本地文件路径
        executor: 线程池
        part_size: 分块大小。小于分块大小的文件，使用简单上传；大于分块大小的文件，使用分块上传
        resumable: 是否开启断点续传，默认False。开启断点续传时，如果本地存在有效的断点续传记录，则尝试恢复上传，否则初始化分块上传
        resumable_filename: 断点续传记录文件路径。如果不指定，则使用默认路径（md5[src_file] + '.ks3resume'）
        """
        self.key = key
        self.bucket = bucket
        self.src_file = src_file
        self.executor = executor
        self.part_size = part_size
        self.resumable = resumable
        if self.resumable:
            if resumable_filename is None:
                resumable_filename = self._gen_resumable_filename()
            self.record_manager = ResumeRecordManager(resumable_filename)
        else:
            self.record_manager = None
        # 源文件的修改时间
        self._mtime = None
        # 源文件的大小
        self._file_size = None
        self._set_header_keys()

    def upload(self, headers=None):
        if headers is None:
            headers = {}
        self._prepare(headers)
        if self._file_size <= self.part_size:
            return self.single_transfer(headers)
        return self.multipart_transfer(headers)

    def single_transfer(self, headers):
        resp = self.key.set_contents_from_filename(self.src_file, headers=headers)
        ur = UploadResult(
            upload_id=None,
            response_metadata=resp.response_metadata,
        )
        return ur

    def multipart_transfer(self, headers):
        # 初始化分块上传
        mp = self._get_or_init_record_as_mp(headers)

        if not self.resumable:
            part_uploaded = set()
        elif self.bucket.connection.enable_crc:
            # 开启了crc校验，已上传分块以本地记录为准，防止本地与远端记录分块数据不一致。
            part_uploaded = set(self.record_manager.record.part_crc_infos.keys())
        else:
            # 未开启crc校验，已上传分块以远端记录为准（通过断点续传文件内记录的upload_id等信息获取远端分块记录）。
            part_uploaded = set()
            # for循环将调用 List Parts 接口
            for p in mp:
                part_uploaded.add(p.part_number)

        num_parts = int(math.ceil(self._file_size / float(self.part_size)))
        # 分块上传
        # part_futures<future, part_num>
        part_futures = {}
        # 筛选出上传分块需要携带的headers
        part_headers = {}
        for key in headers:
            if key in self._part_header_keys:
                part_headers[key] = headers[key]
        for part_num in range(1, num_parts + 1):
            # 跳过已上传的part
            if part_num in part_uploaded:
                logger.debug('key_name={0}, part {1} already uploaded, skip'.format(self.key.name, part_num))
                continue

            part_futures[self.executor.submit(
                self._put_part,
                mp=mp,
                part_num=part_num,
                headers=part_headers,
            )] = part_num
        # 不能及时处理中断信号
        self.executor.shutdown(wait=True)
        for future in futures.as_completed(part_futures):
            try:
                future.result()
            except Exception as e:
                logger.error('key_name={0}, part {1} upload failed: {2}'.format(self.key.name, part_futures[future], e))
                raise e
        try:
            # 筛选出完成上传需要携带的headers
            complete_headers = {}
            for key in headers:
                if key in self._complete_header_keys or key.startswith('kss-'):
                    complete_headers[key] = headers[key]
            resp = mp.complete_upload(headers=complete_headers)
        except KS3ClientError as e:
            # crc校验失败，删除本地断点续传记录，以便于下次重新上传
            if 'Inconsistent CRC checksum' in e.reason:
                if self.resumable:
                    self.record_manager.delete()
            raise e
        # 正常上传完成，未抛出异常，则删除本地断点续传记录
        if self.resumable:
            self.record_manager.delete()

        ur = UploadResult(
            upload_id=mp.id,
            response_metadata=resp.response_metadata,
        )
        ur.etag = resp.etag
        return ur

    def _prepare(self, headers):
        self._mtime = os.path.getmtime(self.src_file)
        self._file_size = os.path.getsize(self.src_file)
        self.part_size = self._adjust_part_size(self.part_size)

    def _get_or_init_record_as_mp(self, headers):
        """
        获取或初始化分块上传:
        1. 如果没有开启断点续传，则初始化分块上传
        2. 如果开启断点续传，则尝试加载本地记录，如果记录存在且有效，则恢复分块上传，否则初始化分块上传
        return: 返回分块上传对象MultiPartUpload类型
        """
        # 筛选出初始化上传需要携带的headers
        init_headers = {}
        for key in headers:
            if key in self._init_header_keys or key.startswith('x-kss-meta-'):
                init_headers[key] = headers[key]
        if not self.resumable:
            mp = self.bucket.initiate_multipart_upload(self.key.name, headers=init_headers)
            return mp

        self.record_manager.load()

        if self.record_manager.record is not None and not self._check_record_valid():
            logger.debug('key_name={0}, found invalid record, delete it'.format(self.key.name))
            self.record_manager.delete()
        if self.record_manager.record is None:
            logger.debug('key_name={0}, not found record, initiate multipart upload'.format(self.key.name))
            mp = self.bucket.initiate_multipart_upload(self.key.name, headers=init_headers)
            self.record_manager.record = UploadRecord(mp.id, self._file_size, self._mtime,
                                                      self.bucket.name, self.key.name, self.part_size, {})
            self.record_manager.save()
        else:
            logger.debug('key_name={0}, found record, resume multipart upload: {1}'
                         .format(self.key.name, self.record_manager.record.upload_id))
            mp = MultiPartUpload(self.bucket)
            mp.id = self.record_manager.record.upload_id
            mp.key_name = self.record_manager.record.key_name
            mp.part_crc_infos = self.record_manager.record.part_crc_infos
            self.part_size = self.record_manager.record.part_size
        return mp

    def _check_record_valid(self):
        record = self.record_manager.record
        if not isinstance(record, UploadRecord):
            return False
        for attr in [record.upload_id, record.bucket_name, record.key_name]:
            if not isinstance(attr, str):
                return False
        for attr in [record.file_size, record.part_size]:
            if not isinstance(attr, int):
                return False
        if not isinstance(record.part_crc_infos, dict):
            return False
        if record.mtime != self._mtime or record.file_size != self._file_size:
            return False
        return True

    def _adjust_part_size(self, part_size):
        num_parts = int(math.ceil(self._file_size / float(part_size)))
        # 以分块数的标准，调整分块大小
        while num_parts > MAX_PARTS:
            part_size *= 2
            num_parts = int(math.ceil(self._file_size / float(part_size)))
        # 以单次上传大小的标准，调整分块大小
        if part_size > MAX_SIZE:
            part_size = MAX_SIZE
        elif part_size < MIN_SIZE:
            part_size = MIN_SIZE
        return part_size

    def _put_part(self, mp, part_num, headers):
        start_offset = (part_num - 1) * self.part_size
        remain_bytes = self._file_size - start_offset
        upload_size = min(self.part_size, remain_bytes)
        with ChunkIO(self.src_file, start_offset, upload_size) as fp:
            resp = mp.upload_part_from_file(fp, part_num, headers=headers)
            if self.resumable and self.bucket.connection.enable_crc:
                self.record_manager.record.part_crc_infos[part_num] = PartInfo(
                    upload_size, resp.getheader(self.bucket.connection.provider.checksum_crc64ecma_header))
                # 保存crc信息
                self.record_manager.save()

    def _gen_resumable_filename(self):
        absolute_path = os.path.abspath(self.src_file)
        md5_str = calculate_string_md5(absolute_path)
        return md5_str + '.ks3resume'

    def _set_header_keys(self):
        self._init_header_keys = init_header_keys
        self._part_header_keys = upload_part_header_keys
        self._complete_header_keys = complete_upload_header_keys


class UploadRecord(object):
    def __init__(self, upload_id, file_size, mtime, bucket_name, key_name, part_size, part_crc_infos):
        self.upload_id = upload_id
        self.file_size = file_size
        self.mtime = mtime
        self.bucket_name = bucket_name
        self.key_name = key_name
        self.part_size = part_size
        self.part_crc_infos = part_crc_infos


class UploadResult:
    def __init__(
            self,
            upload_id=None,
            response_metadata=None,
    ):
        self.upload_id = upload_id
        self.response_metadata = response_metadata

        self.etag = response_metadata.headers.get('ETag')
        self.crc64ecma = response_metadata.headers.get('x-kss-checksum-crc64ecma')
        self.request_id = response_metadata.request_id
