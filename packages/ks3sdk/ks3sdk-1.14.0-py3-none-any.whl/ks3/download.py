import copy
import logging
import os
import tempfile
from concurrent import futures

from ks3.exception import KS3ClientError, S3ResponseError
from ks3.upload import sse_c_header_keys
from ks3.utils import ResumeRecordManager, compute_file_crc64, check_crc, force_rename, \
    DEFAULT_PART_SIZE
import math

logger = logging.getLogger(__name__)


class DownloadTask:
    def __init__(
            self, key, bucket, filename,
            executor,
            part_size=DEFAULT_PART_SIZE,
            resumable=False,
            resumable_filename=None,
    ):
        """
        key: 需要下载的Key对象（ks3.key.Key）
        bucket: Bucket对象（ks3.bucket.Bucket）
        filename: 下载到的本地文件路径
        executor: 线程池
        part_size: 分块大小
        resumable: 是否开启断点续传，默认False。开启断点续传时，如果本地存在有效的断点续传记录，则尝试恢复下载
        resumable_filename: 断点续传记录文件路径。如果不指定，则使用默认路径（self.filename + '.ks3resume'）
        """
        self.key = key
        self.bucket = bucket
        self.filename = filename
        self.executor = executor
        self.part_size = part_size
        self.resumable = resumable
        if self.resumable:
            if resumable_filename is None:
                resumable_filename = self.filename + '.ks3resume'
            self.record_manager = ResumeRecordManager(resumable_filename)
        else:
            self.record_manager = None
        # 下载过程中临时文件名
        self.tmp_file_name = None

    def download(self, headers=None):
        if headers is None:
            headers = {}
        # 传入的key对象没有etag属性，则认为缺少元数据信息，需要head获取
        head_headers = {}
        for k in sse_c_header_keys:
            if k in headers:
                head_headers[k] = headers[k]
        if self.key.etag is None:
            head_k, resp = self.bucket._get_key_internal(self.key.name, head_headers, None)
            if head_k is None:
                logger.error('Failed to head key {0} from bucket {1}'
                             .format(self.key.name, self.bucket.name))
                raise S3ResponseError(resp.status, resp.reason, None, request_id=resp.getheader('x-kss-request-id'))
            self.key = head_k
        self.multipart_download(headers)
        return DownloadResult(self.key.server_crc, self.key.etag)

    def multipart_download(self, headers=None):
        self._prepare_record_and_tmp_file()
        # 如果开启断点续传则获取已下载的分块信息，否则赋值为空字典
        part_downloaded = self.record_manager.record.part_infos if self.resumable else {}

        num_parts = int(math.ceil(self.key.size / float(self.part_size)))
        remain_size = self.key.size

        part_futures = {}
        for part_num in range(1, num_parts + 1):
            if part_num in part_downloaded:
                logger.debug('key_name={0}, part_num={1} already downloaded, skip'.format(self.key.name, part_num))
                remain_size -= self.part_size
                continue
            part_info = DownloadPartInfo(part_num, self.part_size * (part_num - 1), min(self.part_size, remain_size))
            part_futures[self.executor.submit(
                self._download_part,
                part_info=part_info,
                headers=headers,
            )] = part_num
            remain_size -= self.part_size
        self.executor.shutdown(wait=True)
        for future in futures.as_completed(part_futures):
            try:
                future.result()
            except Exception as e:
                logger.error(
                    'key_name={0}, part {1} download failed: {2}'.format(self.key.name, part_futures[future], e))
                raise e

        if self.bucket.connection.enable_crc:
            client_crc = compute_file_crc64(self.tmp_file_name)
            if not check_crc(client_crc, self.key.server_crc):
                if self.resumable:
                    self.record_manager.delete()
                logger.error(
                    "key_name={0}, Inconsistent CRC checksum client_crc: {1}, server_crc: {2}"
                    .format(self.key.name, client_crc, self.key.server_crc))
                raise KS3ClientError(
                    "Inconsistent CRC checksum client_crc: %s, server_crc: %s" % (client_crc, self.key.server_crc))
        force_rename(self.tmp_file_name, self.filename)
        if self.resumable:
            self.record_manager.delete()

    def _download_part(self, part_info, headers=None):
        with open(self.tmp_file_name, 'rb+') as f:
            f.seek(part_info.start, os.SEEK_SET)
            # 下载对象会读写当前key对象的resp属性，线程不安全
            # 需要使用线程独享的key对象进行下载
            byte_range = (part_info.start, part_info.start + part_info.part_size - 1)
            copy.copy(self.key).get_contents_to_file(f, byte_range=byte_range, headers=headers)
            if self.resumable:
                self.record_manager.record.part_infos[part_info.part_num] = part_info
                self.record_manager.save()

    def _prepare_record_and_tmp_file(self):
        if not self.resumable:
            self.tmp_file_name = self._create_tmp_file()
            return

        self.record_manager.load()
        if self.record_manager.record is not None and not self._check_record_valid():
            logger.debug('key_name={0}, found invalid record, delete it'.format(self.key.name))
            self.record_manager.delete()
        if self.record_manager.record is None:
            logger.debug('key_name={0}, not found record, initiate multipart download'.format(self.key.name))
            self.record_manager.record = DownloadRecord(self.key.size, self.key.last_modified, self.key.etag,
                                                        self.bucket.name, self.key.name, self.part_size,
                                                        self._create_tmp_file(), {})
            self.record_manager.save()
        self.tmp_file_name = self.record_manager.record.tmp_file_name
        self.part_size = self.record_manager.record.part_size

    def _create_tmp_file(self):
        directory_path = os.path.dirname(self.filename)
        base_name = os.path.basename(self.filename)
        with tempfile.NamedTemporaryFile(
                mode='a', dir=directory_path, prefix=base_name + '.', suffix='.ks3temp', delete=False) as tmp_fp:
            tmp_name = tmp_fp.name
        return tmp_name

    def _check_record_valid(self):
        record = self.record_manager.record
        if not isinstance(record, DownloadRecord):
            return False
        if not os.path.exists(record.tmp_file_name):
            return False
        for attr in [record.bucket_name, record.key_name, record.mtime, record.etag]:
            if not isinstance(attr, str):
                return False
        for attr in [record.file_size, record.part_size]:
            if not isinstance(attr, int):
                return False
        if not isinstance(record.part_infos, dict):
            return False
        if record.mtime != self.key.last_modified or record.file_size != self.key.size or record.etag != self.key.etag:
            return False
        return True


class DownloadRecord(object):
    def __init__(self, file_size, mtime, etag, bucket_name, key_name, part_size, tmp_file_name, part_infos):
        self.file_size = file_size
        self.mtime = mtime
        self.etag = etag
        self.bucket_name = bucket_name
        self.key_name = key_name
        self.part_size = part_size
        self.tmp_file_name = tmp_file_name
        # <part_num, DownloadPartInfo>
        self.part_infos = part_infos


class DownloadPartInfo(object):
    def __init__(self, part_num, start, part_size):
        self.part_num = part_num
        self.start = start
        self.part_size = part_size


class DownloadResult:
    def __init__(
            self,
            crc64ecma=None,
            etag=None,
    ):
        self.crc64ecma = crc64ecma
        self.etag = etag
