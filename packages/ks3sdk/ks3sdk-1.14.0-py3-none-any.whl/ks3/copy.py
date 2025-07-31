import copy
import logging
from urllib import parse

from ks3 import utils
from ks3.exception import KS3ClientError, S3ResponseError
from ks3.keyfile import KeyFile
from ks3.multipart import PartInfo
from ks3.upload import UploadTask, sse_c_header_keys, UploadResult
from ks3.utils import DEFAULT_PART_SIZE, calculate_string_md5

logger = logging.getLogger(__name__)

# ssec加密copy操作需要 额外 用到的headers
copy_sse_c_header_keys = ['x-kss-copy-source-server-side-encryption-customer-key',
                          'x-kss-copy-source-server-side-encryption-customer-algorithm',
                          'x-kss-copy-source-server-side-encryption-customer-key-MD5']
# copy part需要用到的headers
copy_part_header_keys = ['x-kss-copy-source-if-match', 'x-kss-copy-source-if-none-match',
                         'x-kss-copy-source-if-modified-since', 'x-kss-copy-source-if-unmodified-since',]
copy_part_header_keys.extend(copy_sse_c_header_keys)
copy_part_header_keys.extend(sse_c_header_keys)

# metadata需要忽略的headers
metadata_ignore_header_keys = ['Date', 'Server', 'x-kss-request-id', 'X-Application-Context', 'Connection',
                               'Accept-Ranges',
                               'Content-Length',  # 复制的场景，不设置Content-Length
                               ]


class CopyTask(UploadTask):
    def __init__(
            self, src_key, dest_key,
            executor,
            part_size=DEFAULT_PART_SIZE,
            resumable=False,
            resumable_filename=None,
            copy_src_metadata=True,
            copy_src_tagging=True,
    ):
        """
        src_key: 源key对象，需要包含bucket和connection属性（ks3.key.Key）
        dest_key: 目标key对象，需要包含bucket和connection属性（ks3.key.Key）
        executor: 线程池
        part_size: 分块大小。小于分块大小的文件，使用简单复制；大于分块大小的文件，使用分块复制
        resumable: 是否开启断点续传，默认False。开启断点续传时，如果本地存在有效的断点续传记录，则尝试恢复上传，否则初始化分块上传
        resumable_filename: 断点续传记录文件路径。如果不指定，则使用默认路径（md5[src_bucket/src_key_dest_bucket/dest_key] + '.ks3resume'）
        copy_src_metadata: 是否复制源端的metadata，默认True
        copy_src_tagging: 是否复制源端的tagging，默认True
        """
        super().__init__(dest_key, dest_key.bucket, src_key, executor, part_size, resumable, resumable_filename)
        # 是否使用源端相关信息
        self.copy_src_metadata = copy_src_metadata
        self.copy_src_tagging = copy_src_tagging
        # 源key的metadata
        self._src_metadata = None

    def copy(self, headers=None):
        ur = super().upload(headers)
        # 额外对比一次源端服务端的crc和目标端服务端的crc
        if self.bucket.connection.enable_crc:
            src_crc = self.src_file.server_crc
            dest_crc = ur.crc64ecma
            crc_valid = utils.check_crc(src_crc, dest_crc)
            if not crc_valid:
                if self.resumable:
                    self.record_manager.delete()
                raise KS3ClientError('src_key={0}, dest_key={1}, Inconsistent CRC checksum src_crc: {2}, dest_crc: {3}'
                                     .format(self.src_file.name, self.key.name, src_crc, dest_crc))
        return ur

    def single_transfer(self, headers):
        resp = self.bucket.copy_key(self.key.name, self.src_file.bucket.name, self.src_file.name, headers=headers)
        ur = UploadResult(
            upload_id=None,
            response_metadata=resp.response_metadata,
        )
        ur.etag = resp.etag
        return ur

    def _prepare(self, headers):
        head_headers = {}
        for k in sse_c_header_keys:
            if k in headers:
                head_headers[k] = headers[k]
        self._init_src_info(head_headers)
        self._handle_headers(headers)
        self.part_size = self._adjust_part_size(self.part_size)

    # 如果选择copy源key相关信息，需要将源key的headers覆盖到当前请求的headers中
    def _handle_headers(self, headers):
        if self.copy_src_metadata:
            headers.update(self._src_metadata)
        if self.copy_src_tagging:
            tagging = self.src_file.get_object_tagging()
            if tagging.tagging_set is not None and len(tagging.tagging_set) > 0:
                tagging_value = '&'.join(
                    '{0}={1}'.format(parse.quote(tag.key), parse.quote(tag.value)) for tag in tagging.tagging_set)
                headers['x-kss-tagging'] = tagging_value
        # 如果没有传入任何acl头，则设置和源key一样的acl
        acl_header_keys = ['x-kss-acl', 'x-kss-grant-read', 'x-kss-grant-full-control']
        if not any(k in headers for k in acl_header_keys):
            # 得到源acl并设置
            policy = self.src_file.bucket.get_acl(self.src_file.name)
            read_list = []
            full_control_list = []
            for grant in policy.acl.grants:
                value_format = '{0}="{1}"'
                if grant.email_address is not None:
                    value = value_format.format('emailAddress', grant.email_address)
                elif grant.uri is not None:
                    value = value_format.format('uri', grant.uri)
                else:
                    # 通过请求头设置，只有id会生效
                    value = value_format.format('id', grant.id)
                if grant.permission == 'READ':
                    if 'http://acs.ksyun.com/groups/global/AllUsers' in value:
                        headers['x-kss-acl'] = 'public-read'
                    read_list.append(value)
                elif grant.permission == 'FULL_CONTROL':
                    full_control_list.append(value)
            if 'x-kss-acl' not in headers:
                if read_list:
                    headers['x-kss-grant-read'] = ','.join(read_list)
                if full_control_list:
                    headers['x-kss-grant-full-control'] = ','.join(full_control_list)

    def _put_part(self, mp, part_num, headers):
        start_offset = (part_num - 1) * self.part_size
        remain_bytes = self._file_size - start_offset
        upload_size = min(self.part_size, remain_bytes)
        end_offset = start_offset + upload_size - 1
        resp = mp.copy_part_from_key(self.src_file.bucket.name, self.src_file.name, part_num, start_offset, end_offset,
                                     headers)
        if self.resumable and self.bucket.connection.enable_crc:
            self.record_manager.record.part_crc_infos[part_num] = PartInfo(
                upload_size,
                resp.response_metadata.headers[self.bucket.connection.provider.checksum_crc64ecma_header]
            )
            # 保存crc信息
            self.record_manager.save()

    # 初始化源key信息
    def _init_src_info(self, headers=None):
        key, resp = self.src_file.bucket._get_key_internal(self.src_file.name, headers, None)
        if key is None:
            logger.error('Failed to head src key {0} from bucket {1}'
                         .format(self.src_file.name, self.src_file.bucket.name))
            raise S3ResponseError(resp.status, resp.reason, None, request_id=resp.getheader('x-kss-request-id'))
        self.src_file = key
        self._mtime = self.src_file.last_modified
        self._file_size = self.src_file.size
        metadata = {}
        for k in resp.headers:
            if k not in metadata_ignore_header_keys:
                metadata[k] = resp.headers[k]
        self._src_metadata = metadata

    def _gen_resumable_filename(self):
        str_for_md5 = '{0}/{1}_{2}/{3}'.format(
            self.src_file.bucket.name, self.src_file.name, self.bucket.name, self.key.name,
        )
        md5_str = calculate_string_md5(str_for_md5)
        return md5_str + '.ks3resume'

    def _set_header_keys(self):
        super()._set_header_keys()
        self._part_header_keys.extend(copy_part_header_keys)

    def upload(self, headers=None):
        raise NotImplementedError('CopyTask does not support upload method')


class AcrossRegionCopyTask(CopyTask):
    """
    跨region复制，本质上是调用下载接口得到数据流，使用该数据流调用上传接口
    """
    def __init__(
            self, src_key, dest_key,
            executor,
            part_size=DEFAULT_PART_SIZE,
            resumable=False,
            resumable_filename=None,
            copy_src_metadata=True,
            copy_src_tagging=True,
    ):
        super().__init__(
            src_key, dest_key,
            executor,
            part_size,
            resumable,
            resumable_filename,
            copy_src_metadata,
            copy_src_tagging,
        )

    def single_transfer(self, headers):
        key_file_headers = {}
        for k in self._key_file_header_keys:
            if k in headers:
                key_file_headers[k] = headers[k]
        kf = KeyFile(self.src_file, headers=key_file_headers)
        resp = self.key.set_contents_from_file(fp=kf, headers=headers)

        ur = UploadResult(
            upload_id=None,
            response_metadata=resp.response_metadata,
        )
        return ur

    def _put_part(self, mp, part_num, headers):
        # 下载 和 上传分块 的header目前是一样的，可以不筛选
        start_offset = (part_num - 1) * self.part_size
        remain_bytes = self._file_size - start_offset
        upload_size = min(self.part_size, remain_bytes)
        kf = KeyFile(copy.copy(self.src_file), start_offset, upload_size, headers)
        resp = mp.upload_part_from_file(kf, part_num, headers=headers)
        if self.resumable and self.bucket.connection.enable_crc:
            self.record_manager.record.part_crc_infos[part_num] = PartInfo(
                upload_size, resp.getheader(self.bucket.connection.provider.checksum_crc64ecma_header))
            # 保存crc信息
            self.record_manager.save()

    def _set_header_keys(self):
        UploadTask._set_header_keys(self)
        # 下载传入的header
        self._key_file_header_keys = sse_c_header_keys
