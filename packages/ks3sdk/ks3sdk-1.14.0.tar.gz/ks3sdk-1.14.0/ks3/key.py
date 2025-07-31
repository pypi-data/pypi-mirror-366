# -*- coding: utf-8 -*-
import base64
import email
import hashlib
import logging
import math
import mimetypes
import os
import re
import tempfile
import xml
from hashlib import md5

import requests

from ks3 import handler, utils
from ks3.auth import url_encode
from ks3.copy import CopyTask, AcrossRegionCopyTask
from ks3.download import DownloadTask
from ks3.tagging import Tagging
from ks3.responseResult import ResponseMetadata, ResponseResult
from ks3.upload import UploadTask
from ks3.xmlParsers.objectMigration import MigrationResult, MigrationConfiguration

try:
    import urllib.parse as parse
except ImportError:
    import urllib as parse
import binascii

import errno
from ks3.exception import KS3ClientError, S3ResponseError, ParamValidationError
from ks3.exception import StorageDataError, PleaseRetryException
from ks3.keyfile import KeyFile
from ks3.user import User
from ks3.compat import BytesIO
from ks3.utils import compute_md5, compute_encrypted_md5, BlockThreadPoolExecutor, DEFAULT_PART_SIZE, GB, MAX_SIZE
from ks3.utils import find_matching_headers, merge_meta, merge_headers_by_name

try:
    from ks3.encryption import Crypts
    from ks3.encryptFp import EncryptFp
except:
    pass
import aiofiles


logger = logging.getLogger(__name__)


class Key(object):
    DefaultContentType = 'application/octet-stream'

    RestoreBody = """<?xml version="1.0" encoding="UTF-8"?>
      <RestoreRequest xmlns="http://s3.ksyun.com">
        <Days>%s</Days>
      </RestoreRequest>"""

    # BufferSize = ks3.config.getint('Boto', 'key_buffer_size', 8192)
    BufferSize = 8192

    # The object metadata fields a user can set, other than custom metadata
    # fields (i.e., those beginning with a provider-specific prefix like
    # x-amz-meta).
    base_user_settable_fields = set(["cache-control", "content-disposition",
                                     "content-encoding", "content-language",
                                     "content-md5", "content-type",
                                     "x-robots-tag", "expires"])
    _underscore_base_user_settable_fields = set()
    for f in base_user_settable_fields:
        _underscore_base_user_settable_fields.add(f.replace('-', '_'))
    # Metadata fields, whether user-settable or not, other than custom
    # metadata fields (i.e., those beginning with a provider specific prefix
    # like x-amz-meta).
    base_fields = (base_user_settable_fields |
                   set(["last-modified", "content-length", "date", "etag"]))

    def __init__(self, bucket=None, name=None, *args, **kwargs):
        self.bucket = bucket
        self.name = name
        self.metadata = {}
        self.cache_control = None
        self.content_type = self.DefaultContentType
        self.content_encoding = None
        self.content_disposition = None
        self.content_language = None
        self.filename = None
        self.etag = None
        self.is_latest = False
        self.last_modified = None
        self.owner = None
        self.storage_class = None
        self.path = None
        self.resp = None
        self.mode = None
        self._size = None
        self.version_id = None
        self.source_version_id = None
        self.delete_marker = False
        self.encrypted = None
        self.retention_id = None
        self.recycle_time = None
        self.estimated_clear_time = None
        #
        self.local_hashes = {}
        self.user_meta = {}
        self.tagging_count = None
        self.object_type = None
        self.append_next_position = None
        self.server_crc = None
        self.client_crc = '0'

        self.response_metadata = ResponseMetadata(**kwargs)

    @property
    def size(self):
        if self._size is None and self.bucket:
            key = self.bucket.get_key(self.name, validate=True)
            if key:
                self._size = key.size
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    def __repr__(self):
        if self.bucket:
            name = '<Key: %s,%s>' % (self.bucket.name, self.name)
        else:
            name = '<Key: None,%s>' % self.name

        # Encode to bytes for Python 2 to prevent display decoding issues
        if not isinstance(name, str):
            name = name.encode('utf-8')

        return name

    def __iter__(self):
        return self

    @property
    def provider(self):
        provider = None
        if self.bucket and self.bucket.connection:
            provider = self.bucket.connection.provider
        return provider

    def _get_key(self):
        return self.name

    def _set_key(self, value):
        self.name = value

    def next(self):
        """
        By providing a next method, the key object supports use as an iterator.
        For example, you can now say:

        for bytes in key:
            write bytes to a file or whatever

        All of the HTTP connection stuff is handled for you.
        """
        self.open_read()
        data = self.resp.read(self.BufferSize)
        if not data:
            self.close()
            raise StopIteration
        return data

    # Python 3 iterator support
    __next__ = next

    def read(self, size=0):
        self.open_read()
        if size == 0:
            data = self.resp.read()
        else:
            data = self.resp.read(size)

        if self.bucket.connection.enable_crc and data:
            crc_calculater = utils.Crc64(init_crc=int(self.client_crc))
            crc_calculater.update(data)
            self.client_crc = str(crc_calculater.crc)

        if not data:
            self.close()
        return data

    def startElement(self, name, attrs, connection):
        if name == 'Owner':
            self.owner = User(self)
            return self.owner
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'Key':
            self.name = value
        elif name == 'ETag':
            self.etag = value
        elif name == 'IsLatest':
            if value == 'true':
                self.is_latest = True
            else:
                self.is_latest = False
        elif name == 'LastModified':
            self.last_modified = value
        elif name == 'Size':
            self.size = int(value)
        elif name == 'StorageClass':
            self.storage_class = value
        elif name == 'Owner':
            pass
        elif name == 'VersionId':
            self.version_id = value
        elif name == 'RetentionId':
            self.retention_id = value
        elif name == 'RecycleTime':
            self.recycle_time = value
        elif name == 'EstimatedClearTime':
            self.estimated_clear_time = value
        else:
            setattr(self, name, value)

    def delete(self, headers=None):
        """
        Delete this key from S3
        """
        return self.bucket.delete_key(self.name, version_id=self.version_id,
                                      headers=headers)

    def generate_url(self, expires_in, method='GET', headers=None,
                     query_auth=True, force_http=False, response_headers=None,
                     expires_in_absolute=False, version_id=None,
                     policy=None, reduced_redundancy=False, encrypt_key=False, domain=False, image_attrs=None):
        """
        Generate a URL to access this key.
        """
        provider = self.bucket.connection.provider
        version_id = version_id or self.version_id
        if headers is None:
            headers = {}
        else:
            headers = headers.copy()

        # add headers accordingly (usually PUT case)
        # if policy:
        #    headers[provider.acl_header] = policy
        # if reduced_redundancy:
        #    self.storage_class = 'REDUCED_REDUNDANCY'
        #    if provider.storage_class_header:
        #        headers[provider.storage_class_header] = self.storage_class
        # if encrypt_key:
        #    headers[provider.server_side_encryption_header] = 'AES256'
        # headers = merge_meta(headers, self.metadata, provider)

        name = self.name
        if image_attrs is not None:
            name = name + image_attrs

        url = self.bucket.connection.generate_url(expires_in, method,
                                                  self.bucket.name, name,
                                                  headers, query_auth,
                                                  force_http,
                                                  response_headers,
                                                  expires_in_absolute,
                                                  version_id)
        if domain is True:
            url = url.replace('http://' + self.bucket.name + '.', 'http://')
            url = url.replace('https://' + self.bucket.name + '.', 'https://')

        return url

    # GetObjectPresignedUrl 生成临时上传链接
    def get_presigned_url(self, expires_in, headers=None, expires_in_absolute=False, version_id=None, domain=False):
        """
        生成临时上传链接
        """
        return self.bucket.presign(expires_in, headers=headers, expires_in_absolute=expires_in_absolute,
                                             version_id=version_id, domain=domain, key_name=self.name)

    def should_retry(self, response, chunked_transfer=False):
        provider = self.bucket.connection.provider

        if not chunked_transfer:
            if response.status in [500, 503]:
                # 500 & 503 can be plain retries.
                return True

            if response.getheader('location'):
                # If there's a redirect, plain retry.
                return True

        if 200 <= response.status <= 299:
            self.etag = response.getheader('etag')
            md5 = self.md5
            if isinstance(md5, bytes):
                md5 = md5.decode('utf-8')

            # If you use customer-provided encryption keys, the ETag value that
            # Amazon S3 returns in the response will not be the MD5 of the
            # object.
            server_side_encryption_customer_algorithm = response.getheader(
                'x-amz-server-side-encryption-customer-algorithm', None)
            if server_side_encryption_customer_algorithm is None:
                if self.etag != '"%s"' % md5:
                    raise provider.storage_data_error(
                        'ETag from S3 did not match computed MD5. '
                        '%s vs. %s' % (self.etag, self.md5))

            return True

        if response.status == 400:
            # The 400 must be trapped so the retry handler can check to
            # see if it was a timeout.
            # If ``RequestTimeout`` is present, we'll retry. Otherwise, bomb
            # out.
            body = response.read()
            err = provider.storage_response_error(
                response.status,
                response.reason,
                body
            )

            if err.error_code in ['RequestTimeout']:
                raise PleaseRetryException(
                    "Saw %s, retrying" % err.error_code,
                    response=response
                )

        return False

    def send_file(self, fp, method="PUT", headers=None, cb=None, num_cb=10,
                  query_args=None, chunked_transfer=False, size=None,
                  crypt_context=None):
        """
        Upload a file to a key into a bucket on S3.
        """
        resp = self._send_file_internal(fp, method=method, headers=headers, cb=cb, num_cb=num_cb,
                                        query_args=query_args, chunked_transfer=chunked_transfer,
                                        size=size, crypt_context=crypt_context)
        resp.read()
        return resp

    def _send_file_internal(self, fp, method="PUT", headers=None, cb=None, num_cb=10,
                            query_args=None, chunked_transfer=False, size=None,
                            hash_algs=None, crypt_context=None):
        provider = self.bucket.connection.provider
        # try:
        #     spos = fp.tell()
        # except IOError:
        #     spos = None
        #     self.read_from_stream = False

        # If hash_algs is unset and the MD5 hasn't already been computed,
        # default to an MD5 hash_alg to hash the data on-the-fly.
        # if hash_algs is None and not self.md5:
        #     hash_algs = {'md5': md5}
        # digesters = dict((alg, hash_algs[alg]()) for alg in hash_algs or {})

        if not headers:
            headers = {}
        else:
            headers = headers.copy()
        # Overwrite user-supplied user-agent.
        for header in find_matching_headers('User-Agent', headers):
            del headers[header]
        # headers['User-Agent'] = UserAgent
        # If storage_class is None, then a user has not explicitly requested
        # a storage class, so we can assume STANDARD here
        if self.storage_class not in [None, 'STANDARD']:
            headers[provider.storage_class_header] = self.storage_class
        if find_matching_headers('Content-Encoding', headers):
            self.content_language = merge_headers_by_name(
                'Content-Language', headers)
        content_type_headers = find_matching_headers('Content-Type', headers)
        if content_type_headers:
            # Some use cases need to suppress sending of the Content-Type
            # header and depend on the receiving server to set the content
            # type. This can be achieved by setting headers['Content-Type']
            # to None when calling this method.
            if (len(content_type_headers) == 1 and
                    headers[content_type_headers[0]] is None):
                # Delete null Content-Type value to skip sending that header.
                del headers[content_type_headers[0]]
            else:
                self.content_type = merge_headers_by_name(
                    'Content-Type', headers)
        elif self.path:
            self.content_type = mimetypes.guess_type(self.path)[0]
            if self.content_type is None:
                self.content_type = self.DefaultContentType
            headers['Content-Type'] = self.content_type
        else:
            headers['Content-Type'] = self.content_type
        if self.base64md5:
            headers['Content-MD5'] = self.base64md5
        if chunked_transfer:
            headers['Transfer-Encoding'] = 'chunked'
            # if not self.base64md5:
            #    headers['Trailer'] = "Content-MD5"
        else:
            headers['Content-Length'] = str(self.size)
        # This is terrible. We need a SHA256 of the body for SigV4, but to do
        # the chunked ``sender`` behavior above, the ``fp`` isn't available to
        # the auth mechanism (because closures). Detect if it's SigV4 & embelish
        # while we can before the auth calculations occur.
        # if 'hmac-v4-s3' in self.bucket.connection._required_auth_capability():
        #    kwargs = {'fp': fp, 'hash_algorithm': hashlib.sha256}
        #    if size is not None:
        #        kwargs['size'] = size
        #    headers['_sha256'] = compute_hash(**kwargs)[0]
        # headers['Expect'] = '100-Continue'
        headers = merge_meta(headers, self.metadata, provider)
        if self.size < 0 or self.size > MAX_SIZE:
            raise ParamValidationError('Key size={0} should between 0 and {1} bytes'.format(self.size, MAX_SIZE))
        # keyFile类型没有本地加密
        if self.bucket.connection.local_encrypt and crypt_context and not isinstance(fp, KeyFile):
            if crypt_context.action_info == "put":
                fp = EncryptFp(fp, crypt_context, "put")
                md5_generator = hashlib.md5()
                md5_generator.update(crypt_context.key)
                headers["x-kss-meta-key"] = base64.b64encode(md5_generator.hexdigest().encode()).decode()
                headers["x-kss-meta-iv"] = base64.b64encode(crypt_context.first_iv).decode()
            if crypt_context.action_info == "upload_part":
                if crypt_context.part_num == 1:
                    fp = EncryptFp(fp, crypt_context, "upload_part", isUploadFirstPart=True,
                                   isUploadLastPart=crypt_context.is_last_part)
                else:
                    fp = EncryptFp(fp, crypt_context, "upload_part", isUploadFirstPart=False,
                                   isUploadLastPart=crypt_context.is_last_part)
            if self.base64md5:
                headers["x-kss-meta-unencrypted-content-md5"] = self.base64md5
            if headers.get("Content-MD5"):
                headers.pop("Content-MD5")
            if crypt_context.calc_md5:
                headers['Content-MD5'] = self.compute_encrypted_md5(fp)
                fp.block_count = 0
                fp.calc_iv = ""
            if chunked_transfer:
                headers['Transfer-Encoding'] = 'chunked'
            else:
                headers['Content-Length'] = str(len(fp))
            headers["x-kss-meta-unencrypted-content-length"] = str(self.size)
            if self.bucket.connection.enable_crc and not isinstance(fp, utils.FpAdapter):
                fp = utils.FpAdapter(fp)
            resp = self.bucket.connection.make_request(
                method,
                self.bucket.name,
                self.name,
                data=fp,
                headers=headers,
                query_args=query_args,
            )
            if resp and resp.status > 299:
                raise provider.storage_response_error(resp.status, resp.reason, resp.read())
            self.handle_version_headers(resp, force=True)
            self.handle_addl_headers(resp.getheaders())
            if self.bucket.connection.enable_crc:
                self.client_crc = str(fp.crc)
                server_crc = resp.getheader(self.provider.checksum_crc64ecma_header)
                logger.debug('upload key: {0}, bucket: {1}, check crc: [client crc: {2}, server crc: {3}]'
                             .format(self.name, self.bucket.name, self.client_crc, server_crc))
                if not utils.check_crc(self.client_crc, server_crc):
                    raise KS3ClientError("Inconsistent CRC checksum client_crc: %s, server_crc: %s" %
                                         (self.client_crc, resp.getheader(self.provider.checksum_crc64ecma_header)),
                                         resp.headers['x-kss-request-id'])
            return resp
        # keyFile类型不用
        if self.bucket.connection.enable_crc and not isinstance(fp, utils.FpAdapter) and not isinstance(fp, KeyFile):
            fp = utils.FpAdapter(fp)
        resp = self.bucket.connection.make_request(
            method,
            self.bucket.name,
            self.name,
            data=fp,
            headers=headers,
            query_args=query_args
        )
        if resp and resp.status > 299:
            raise provider.storage_response_error(resp.status, resp.reason, resp.read())
        self.handle_version_headers(resp, force=True)
        self.handle_addl_headers(resp.getheaders())
        if self.bucket.connection.enable_crc:
            self.client_crc = str(fp.crc)
            server_crc = resp.getheader(self.provider.checksum_crc64ecma_header)
            logger.debug('upload key: {0}, bucket: {1}, check crc: [client crc: {2}, server crc: {3}]'
                         .format(self.name, self.bucket.name, self.client_crc, server_crc))
            if not utils.check_crc(self.client_crc, server_crc):
                raise KS3ClientError("Inconsistent CRC checksum client_crc: %s, server_crc: %s" %
                                     (self.client_crc, resp.getheader(self.provider.checksum_crc64ecma_header)),
                                     resp.headers['x-kss-request-id'])
        return resp

    def set_contents_from_file(self, fp, method="PUT", headers=None, replace=True,
                               cb=None, num_cb=10, policy=None, md5=None,
                               reduced_redundancy=False, query_args=None,
                               encrypt_key=False, size=None, rewind=False,
                               crypt_context=None, calc_encrypt_md5=True):
        """
        Store an object in S3 using the name of the Key object as the
        key in S3 and the contents of the file pointed to by 'fp' as the
        contents. The data is read from 'fp' from its current position until
        'size' bytes have been read or EOF.
        :type fp: file
        :param fp: the file whose contents to upload

        :type headers: dict
        :param headers: Additional HTTP headers that will be sent with
            the PUT request.

        :type replace: bool
        :param replace: If this parameter is False, the method will
            first check to see if an object exists in the bucket with
            the same key.  If it does, it won't overwrite it.  The
            default value is True which will overwrite the object.

        :type cb: function
        :param cb: a callback function that will be called to report
            progress on the upload.  The callback should accept two
            integer parameters, the first representing the number of
            bytes that have been successfully transmitted to S3 and
            the second representing the size of the to be transmitted
            object.

        :type num_cb: int
        :param num_cb: (optional) If a callback is specified with the
            cb parameter this parameter determines the granularity of
            the callback by defining the maximum number of times the
            callback will be called during the file transfer.

        :type policy: :class:`boto.s3.acl.CannedACLStrings`
        :param policy: A canned ACL policy that will be applied to the
            new key in S3.

        :type md5: A tuple containing the hexdigest version of the MD5
            checksum of the file as the first element and the
            Base64-encoded version of the plain checksum as the second
            element.  This is the same format returned by the
            compute_md5 method.
        :type reduced_redundancy: bool
        :param reduced_redundancy: If True, this will set the storage
            class of the new Key to be REDUCED_REDUNDANCY. The Reduced
            Redundancy Storage (RRS) feature of S3, provides lower
            redundancy at lower storage cost.

        :type encrypt_key: bool
        :param encrypt_key: If True, the new copy of the object will
            be encrypted on the server-side by S3 and will be stored
            in an encrypted form while at rest in S3.

        :type size: int
        :param size: (optional) The Maximum number of bytes to read
            from the file pointer (fp). This is useful when uploading
            a file in multiple parts where you are splitting the file
            up into different ranges to be uploaded. If not specified,
            the default behaviour is to read all bytes from the file
            pointer. Less bytes may be available.

        :type rewind: bool
        :param rewind: (optional) If True, the file pointer (fp) will
            be rewound to the start before any bytes are read from
            it. The default behaviour is False which reads from the
            current position of the file pointer (fp).

        :rtype: int
        :return: The number of bytes written to the key.
        """
        provider = self.bucket.connection.provider
        headers = headers or {}
        if policy:
            headers[provider.acl_header] = policy
        if encrypt_key:
            headers[provider.server_side_encryption_header] = 'AES256'

        if rewind:
            # caller requests reading from beginning of fp.
            fp.seek(0, os.SEEK_SET)
        else:
            # The following seek/tell/seek logic is intended
            # to detect applications using the older interface to
            # set_contents_from_file(), which automatically rewound the
            # file each time the Key was reused. This changed with commit
            # 14ee2d03f4665fe20d19a85286f78d39d924237e, to support uploads
            # split into multiple parts and uploaded in parallel, and at
            # the time of that commit this check was added because otherwise
            # older programs would get a success status and upload an empty
            # object. Unfortuantely, it's very inefficient for fp's implemented
            # by KeyFile (used, for example, by gsutil when copying between
            # providers). So, we skip the check for the KeyFile case.
            # TODO: At some point consider removing this seek/tell/seek
            # logic, after enough time has passed that it's unlikely any
            # programs remain that assume the older auto-rewind interface.
            if not isinstance(fp, KeyFile):
                spos = fp.tell()
                fp.seek(0, os.SEEK_END)
                if fp.tell() == spos:
                    fp.seek(0, os.SEEK_SET)
                    if fp.tell() != spos:
                        # Raise an exception as this is likely a programming
                        # error whereby there is data before the fp but nothing
                        # after it.
                        fp.seek(spos)
                        raise AttributeError('fp is at EOF. Use rewind option '
                                             'or seek() to data start.')
                # seek back to the correct position.
                fp.seek(spos)
        if reduced_redundancy:
            self.storage_class = 'REDUCED_REDUNDANCY'
            if provider.storage_class_header:
                headers[provider.storage_class_header] = self.storage_class
                # TODO - What if provider doesn't support reduced reduncancy?
                # What if different providers provide different classes?
        if hasattr(fp, 'name'):
            self.path = fp.name
        if self.bucket is not None:
            if not md5 and provider.supports_chunked_transfer():
                # defer md5 calculation to on the fly and
                # we don't know anything about size yet.
                chunked_transfer = True
                self.size = None
            else:
                chunked_transfer = False
                if isinstance(fp, KeyFile):
                    # Avoid EOF seek for KeyFile case as it's very inefficient.
                    size = fp.size
                    self.size = size
                    # At present both GCS and S3 use MD5 for the etag for
                    # non-multipart-uploaded objects. If the etag is 32 hex
                    # chars use it as an MD5, to avoid having to read the file
                    # twice while transferring.
                    # keyFile类型，现用于跨region复制，对于源key为分块上传的，没有md5值，所以统一不计算
                    # 通过crc校验一致性，没有crc时，不保证一致性
                    md5 = (None, None)
                    # key = fp.getkey()
                    # if (re.match('^"[a-fA-F0-9]{32}"$', key.etag)):
                    #     etag = key.etag.strip('"')
                    #     md5 = (etag, base64.b64encode(binascii.unhexlify(etag)).decode('utf-8'))
                if not md5:
                    # compute_md5() and also set self.size to actual
                    # size of the bytes read computing the md5.
                    md5 = self.compute_md5(fp, size)
                    # adjust size if required
                    size = self.size
                elif size:
                    self.size = size
                else:
                    # If md5 is provided, still need to size so
                    # calculate based on bytes to end of content
                    spos = fp.tell()
                    fp.seek(0, os.SEEK_END)
                    self.size = fp.tell() - spos
                    fp.seek(spos)
                    size = self.size
                self.md5 = md5[0]
                self.base64md5 = md5[1]

            if self.name is None:
                self.name = self.md5
            if not replace:
                if self.bucket.lookup(self.name):
                    logger.debug('<Key: {0}> in {1} already exists, do not replace.'.format(self.name, self.bucket))
                    return
            try:
                from ks3.encryption import Crypts
            except:
                pass
            if self.bucket.connection.local_encrypt and self.size:
                if not crypt_context:
                    crypt_context = Crypts(self.bucket.connection.key)
                    crypt_context.action_info = "put"
                    crypt_context.calc_md5 = calc_encrypt_md5
                resp = self.send_file(fp, method=method, headers=headers, cb=cb, num_cb=num_cb,
                                      query_args=query_args,
                                      chunked_transfer=chunked_transfer, size=size,
                                      crypt_context=crypt_context)
            else:
                try:
                    resp = self.send_file(fp, method=method, headers=headers, cb=cb, num_cb=num_cb,
                                          query_args=query_args,
                                          chunked_transfer=chunked_transfer, size=size)
                except Exception as e:
                    if isinstance(e, requests.exceptions.ConnectionError) and e.request is not None:
                        e.args = e.args, 'Request URL: {}'.format(e.request.url)
                    raise e
            return ResponseResult(data=resp, status=resp.status, reason=resp.reason,
                          headers=resp.headers)
            # return number of bytes written.
            # return self.size

    def set_contents_from_filename(self, filename, method="PUT", headers=None, replace=True,
                                   cb=None, num_cb=10, policy=None, md5=None,
                                   reduced_redundancy=False,
                                   encrypt_key=False, calc_encrypt_md5=True, query_args=None):
        """
        Store an object in S3 using the name of the Key object as the
        key in S3 and the contents of the file named by 'filename'.
        See set_contents_from_file method for details about the
        parameters.
        """
        with open(filename, 'rb') as fp:
            return self.set_contents_from_file(fp, method, headers, replace, cb,
                                               num_cb, policy, md5,
                                               reduced_redundancy,
                                               encrypt_key=encrypt_key, calc_encrypt_md5=calc_encrypt_md5,
                                               query_args=query_args)

    def append_object_from_filename(self, filename, position, **kwargs):
        return self.set_contents_from_filename(filename, method="POST", query_args="append&position=%d" % position,
                                               **kwargs)

    # 读取大文件慎用——读取全部内容后，再上传，会占用大量内存
    async def upload_file_async(self, filename, method="PUT", headers=None, replace=True, cb=None, num_cb=10, policy=None,
                                md5=None,
                                reduced_redundancy=False, encrypt_key=False, calc_encrypt_md5=True,
                                query_args=None):
        """
        set_contents_from_filename的异步版本
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        data = await _read_file_async(filename)
        loop = asyncio.get_running_loop()
        # 使用线程池执行同步函数，实现异步效果
        with ThreadPoolExecutor() as pool:
            r = await loop.run_in_executor(pool, lambda: self.set_contents_from_string(
                data, method, headers, replace, cb,  num_cb, policy, md5, reduced_redundancy, encrypt_key=encrypt_key,
                calc_encrypt_md5=calc_encrypt_md5, query_args=query_args))
        return r

    def set_contents_from_string(self, string_data, method="PUT", headers=None, replace=True,
                                 cb=None, num_cb=10, policy=None, md5=None,
                                 reduced_redundancy=False,
                                 encrypt_key=False, calc_encrypt_md5=True, query_args=None):
        """
        Store an object in S3 using the name of the Key object as the
        key in S3 and the string 's' as the contents.
        See set_contents_from_file method for details about the
        parameters.
        """
        if not isinstance(string_data, bytes):
            string_data = string_data.encode('utf-8')
        fp = BytesIO(string_data)
        r = self.set_contents_from_file(fp, method, headers, replace, cb, num_cb,
                                        policy, md5, reduced_redundancy,
                                        encrypt_key=encrypt_key, calc_encrypt_md5=calc_encrypt_md5,
                                        query_args=query_args)
        fp.close()
        return r

    def append_object_from_string(self, string_data, position, **kwargs):
        return self.set_contents_from_string(string_data, method="POST", query_args="append&position=%d" % position,
                                             **kwargs)

    def get_file(self, fp, headers=None, cb=None, num_cb=10,
                 torrent=False, version_id=None, override_num_retries=None,
                 response_headers=None):
        """
        Retrieves a file from an S3 Key
        """
        return self._get_file_internal(fp, headers=headers, cb=cb, num_cb=num_cb,
                                       torrent=torrent, version_id=version_id,
                                       override_num_retries=override_num_retries,
                                       response_headers=response_headers,
                                       hash_algs=None,
                                       query_args=None)

    def _get_file_internal(self, fp, headers=None, cb=None, num_cb=10,
                           torrent=False, version_id=None, override_num_retries=None,
                           response_headers=None, hash_algs=None, query_args=None):
        if headers is None:
            headers = {}
        save_debug = self.bucket.connection.debug
        if self.bucket.connection.debug == 1:
            self.bucket.connection.debug = 0

        query_args = query_args or []
        if torrent:
            query_args.append('torrent')

        if hash_algs is None and not torrent:
            hash_algs = {'md5': md5}
        digesters = dict((alg, hash_algs[alg]()) for alg in hash_algs or {})

        # If a version_id is passed in, use that.  If not, check to see
        # if the Key object has an explicit version_id and, if so, use that.
        # Otherwise, don't pass a version_id query param.
        if version_id is None:
            version_id = self.version_id
        if version_id:
            query_args.append('versionId=%s' % version_id)
        if response_headers:
            for key in response_headers:
                query_args.append('%s=%s' % (
                    key, parse.quote(response_headers[key])))
        query_args = '&'.join(query_args)

        if self.bucket.connection.local_encrypt:
            start_offset = 0
            if self.size is None:
                response = self.bucket.connection.make_request('HEAD', self.bucket.name, self.name)
                if response.status < 199 or response.status > 299:
                    raise self.bucket.connection.provider.storage_response_error(response.status,
                                                                                 response.reason, None)
            end_offset = self.size - 1
            skip_bytes = 0
            cut_bytes = 0
            decrypted_total_part = None
        if 'range' in headers and self.bucket.connection.local_encrypt:
            range_value = headers['range'].replace("bytes=", "").strip()
            start_end = range_value.split('-')
            if len(start_end) == 2:
                desired_start = int(start_end[0]) if start_end[0] else 0
                desired_end = int(start_end[1]) if start_end[1] else self.size
                # Takes the position of the leftmost desired byte of a user specified range and calculates the
                # position of the start of the previous cipher block, or set 0 if the leftmost byte is in
                # the first cipher block.
                start_offset = max(desired_start - (desired_start % 16) - 16, 0)
                # Takes the position of the rightmost desired byte of a user specified range and calculates the
                # position of the end of the following cipher block.
                end_offset = min(desired_end + (16 - (desired_end % 16)) + 16 - 1, end_offset)

                headers['range'] = 'bytes={0}-{1}'.format(str(start_offset), str(end_offset))
                # When local encryption enabled, the value of the range header will be expanded,
                # resulting in more data than expected after decryption.
                # we need to calculate the length that needs to be skipped at the beginning
                # and the length that needs to be truncated at the end based on the user desired range.
                skip_bytes = max(desired_start - start_offset, 0)
                cut_bytes = end_offset - 16 - desired_end

                decrypted_size = end_offset - start_offset + 1 - 16
                decrypted_total_part = math.ceil(float(decrypted_size) / self.BufferSize)

        resp_result = self.open('r', headers, query_args=query_args,
                                override_num_retries=override_num_retries)

        data_len = 0
        if cb:
            if self.size is None:
                cb_size = 0
            else:
                cb_size = self.size
            if self.size is None and num_cb != -1:
                # If size is not available due to chunked transfer for example,
                # we'll call the cb for every 1MB of data transferred.
                cb_count = (1024 * 1024) / self.BufferSize
            elif num_cb > 1:
                cb_count = int(math.ceil(cb_size / self.BufferSize / (num_cb - 1.0)))
            elif num_cb < 0:
                cb_count = -1
            else:
                cb_count = 0
            i = 0
            cb(data_len, cb_size)
        try:
            counter = 1
            last_iv = ""
            # When end_offset + 1 === self.size, calculate the data size through start_offset and end_offset
            # In order to adapt to the situation when the range header is provided
            if self.bucket.connection.local_encrypt:
                if end_offset + 1 == self.size:
                    # adapt to the case where the range header (bytes=start-end) end + 1 == self.size
                    total_part = math.ceil(float(end_offset - start_offset + 1) / self.BufferSize)
                else:
                    # the case that the range header is not provided
                    total_part = math.ceil(float(self.size) / self.BufferSize)
            for byte in self:
                if self.bucket.connection.local_encrypt:
                    provider = self.bucket.connection.provider
                    user_key = self.bucket.connection.key
                    crypt_handler = Crypts(user_key)
                    if counter == 1:
                        # For first block, drop first 16 bytes(the subjoin iv).
                        local_iv = byte[:crypt_handler.block_size]
                        byte = byte[crypt_handler.block_size:]
                        server_iv = self.user_meta[provider.metadata_prefix + "iv"]
                        server_iv = base64.b64decode(server_iv)
                        if start_offset == 0 and server_iv and local_iv != server_iv:
                            raise ValueError("decryption error:file.iv not equel server.iv")
                        user_iv = local_iv
                    else:
                        user_iv = last_iv
                    last_iv = byte[-crypt_handler.block_size:]
                    # adapt to the case where the range header (bytes=start-end) end + 1 < self.size
                    # In order to adapt to the situation when the range header is provided
                    # The following two conditions need to be met
                    if end_offset + 1 == self.size and counter == total_part:
                        # Special process of the last part with check code appending to it's end.
                        full_content = crypt_handler.decrypt(byte, user_iv)
                        pad_content_char = full_content[-1]
                        if isinstance(pad_content_char, int):
                            pad_content_char = chr(pad_content_char)
                        for key in crypt_handler.pad_dict:
                            if crypt_handler.pad_dict[key] == pad_content_char:
                                pad_content_char = key
                        decrypt = full_content[:-int(pad_content_char)]
                    else:
                        decrypt = crypt_handler.decrypt(byte, user_iv)
                    byte = decrypt
                    if counter == 1:
                        byte = byte[skip_bytes:]
                    if decrypted_total_part is not None and counter == decrypted_total_part and cut_bytes > 0:
                        byte = byte[:-cut_bytes]
                    counter += 1
                if not isinstance(byte, bytes):
                    byte = byte.encode()
                fp.write(byte)
                data_len += len(byte)
                for alg in digesters:
                    digesters[alg].update(byte)
                if cb:
                    if cb_size > 0 and data_len >= cb_size:
                        break
                    i += 1
                    if i == cb_count or cb_count == -1:
                        cb(data_len, cb_size)
                        i = 0
        except IOError as e:
            if e.errno == errno.ENOSPC:
                raise StorageDataError('Out of space for destination file '
                                       '%s' % fp.name)
            raise
        if cb and (cb_count <= 1 or i > 0) and data_len > 0:
            cb(data_len, cb_size)
        for alg in digesters:
            self.local_hashes[alg] = digesters[alg].digest()
        if self._size is None and not torrent and "Range" not in headers:
            self.size = data_len
        self.close()
        self.bucket.connection.debug = save_debug

        return resp_result

    def open_read(self, headers=None, query_args='',
                  override_num_retries=None, response_headers=None):
        """
        Open this key for reading
        """
        if self.resp is None:
            self.mode = 'r'

            provider = self.bucket.connection.provider
            self.resp = self.bucket.connection.make_request(
                'GET', self.bucket.name, self.name, headers=headers,
                query_args=query_args)
            if self.resp.status < 199 or self.resp.status > 299:
                body = self.resp.read()
                raise provider.storage_response_error(self.resp.status,
                                                      self.resp.reason, body)
            response_headers = self.resp.msg
            # self.metadata = boto.utils.get_aws_metadata(response_headers,
            #                                            provider)
            for name, value in list(response_headers.items()):
                # To get correct size for Range GETs, use Content-Range
                # header if one was returned. If not, use Content-Length
                # header.
                if (name.lower() == 'content-length' and
                        'Content-Range' not in response_headers):
                    self.size = int(value)
                elif name.lower() == 'content-range':
                    end_range = re.sub('.*/(.*)', '\\1', value)
                    self.size = int(end_range)
                elif name.lower() in Key.base_fields:
                    self.__dict__[name.lower().replace('-', '_')] = value
            self.handle_version_headers(self.resp)
            self.handle_encryption_headers(self.resp)
            self.handle_restore_headers(self.resp)
            self.handle_addl_headers(self.resp.getheaders())
            self.handle_user_metas(self.resp)
            self.handle_storage_class(self.resp)
            self.handle_checksum_crc64ecma(self.resp)
        return ResponseResult(data=None, status=self.resp.status, reason=self.resp.reason,
                              headers=self.resp.headers)

    def open_write(self, headers=None, override_num_retries=None):
        """
        Open this key for writing.
        Not yet implemented

        :type headers: dict
        :param headers: Headers to pass in the write request

        :type override_num_retries: int
        :param override_num_retries: If not None will override configured
            num_retries parameter for underlying PUT.
        """
        raise KS3ClientError('Not Implemented')

    def open(self, mode='r', headers=None, query_args=None,
             override_num_retries=None):
        if mode == 'r':
            self.mode = 'r'
            return self.open_read(headers=headers, query_args=query_args,
                                  override_num_retries=override_num_retries)
        elif mode == 'w':
            self.mode = 'w'
            self.open_write(headers=headers,
                            override_num_retries=override_num_retries)
        else:
            raise KS3ClientError('Invalid mode: %s' % mode)

    closed = False

    def close(self, fast=False):
        """
        Close this key.

        :type fast: bool
        :param fast: True if you want the connection to be closed without first
        reading the content. This should only be used in cases where subsequent
        calls don't need to return the content from the open HTTP connection.
        Note: As explained at
        http://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.getresponse,
        callers must read the whole response before sending a new request to the
        server. Calling Key.close(fast=True) and making a subsequent request to
        the server will work because boto will get an httplib exception and
        close/reopen the connection.

        """
        if self.resp and not fast:
            self.resp.read()
        self.resp = None
        self.mode = None
        self.closed = True

    def get_contents_to_file(self, fp, byte_range=None, headers=None,
                             cb=None, num_cb=10,
                             torrent=False,
                             version_id=None,
                             res_download_handler=None,
                             response_headers=None):
        """
        Retrieve an object from S3 using the name of the Key object as the
        key in S3.  Write the contents of the object to the file pointed
        to by 'fp'.

        :param byte_range: 指定下载范围。参见: ref:`byte_range`
        """

        range_string = _make_range_string(byte_range)
        if range_string:
            if not headers:
                headers = {}
            headers['range'] = range_string

        if self.bucket is not None:
            if res_download_handler:
                return res_download_handler.get_file(self, fp, headers, cb, num_cb,
                                                     torrent=torrent,
                                                     version_id=version_id)
            else:
                return self.get_file(fp, headers, cb, num_cb, torrent=torrent,
                                     version_id=version_id,
                                     response_headers=response_headers)

    def get_contents_to_filename(self, filename, byte_range=None, headers=None,
                                 cb=None, num_cb=10,
                                 torrent=False,
                                 version_id=None,
                                 res_download_handler=None,
                                 response_headers=None):
        """
        Retrieve an object from S3 using the name of the Key object as the
        key in S3.  Store contents of the object to a file named by 'filename'.
        See get_contents_to_file method for details about the
        parameters.

        :param byte_range: 指定下载范围。参见: ref:`byte_range`
        """

        range_string = _make_range_string(byte_range)
        if range_string:
            if not headers:
                headers = {}
            headers['range'] = range_string

        directory_path = os.path.dirname(filename)
        base_name = os.path.basename(filename)
        try:
            with tempfile.NamedTemporaryFile(
                    mode='wb', dir=directory_path, prefix=base_name + '.', suffix='.ks3temp', delete=False) as tmp_fp:
                tmp_name = tmp_fp.name
                resp_result = self.get_contents_to_file(tmp_fp, byte_range, headers, cb, num_cb,
                                          torrent=torrent,
                                          version_id=version_id,
                                          res_download_handler=res_download_handler,
                                          response_headers=response_headers)
            if os.path.exists(filename):
                os.remove(filename)
            os.rename(tmp_name, filename)
        except Exception:
            os.remove(tmp_name)
            raise
        # if last_modified date was sent from s3, try to set file's timestamp
        if self.last_modified is not None:
            try:
                modified_tuple = email.utils.parsedate_tz(self.last_modified)
                modified_stamp = int(email.utils.mktime_tz(modified_tuple))
                os.utime(filename, (modified_stamp, modified_stamp))
            except:
                pass
        return resp_result

    async def download_file_async(self, filename, byte_range=None, headers=None,
                                  cb=None, num_cb=10,
                                  torrent=False,
                                  version_id=None,
                                  response_headers=None):

        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        loop = asyncio.get_running_loop()
        # 使用线程池执行同步函数，实现异步效果
        with ThreadPoolExecutor() as pool:
            ret = await loop.run_in_executor(pool, lambda: self.get_contents_as_obj_with_string(
                byte_range, headers, cb, num_cb, torrent=torrent, version_id=version_id,
                response_headers=response_headers))
        await _write_file_async(filename, ret.data)
        return ret

    def get_contents_as_string(self, byte_range=None, headers=None,
                               cb=None, num_cb=10,
                               torrent=False,
                               version_id=None,
                               response_headers=None, encoding=None):
        """
        Retrieve an object from S3 using the name of the Key object as the
        key in S3.  Return the contents of the object as a string.
        See get_contents_to_file method for details about the
        parameters.

        :param byte_range: 指定下载范围。参见: ref:`byte_range`
        """

        fp = BytesIO()
        self.get_contents_to_file(fp, byte_range, headers, cb, num_cb, torrent=torrent,
                                  version_id=version_id,
                                  response_headers=response_headers)
        value = fp.getvalue()
        if encoding is not None:
            value = value.decode(encoding)
        return value

    def get_contents_as_obj_with_string(self, byte_range=None, headers=None,
                               cb=None, num_cb=10,
                               torrent=False,
                               version_id=None,
                               response_headers=None, encoding=None):
        """
        Retrieve an object from S3 using the name of the Key object as the
        key in S3.  Return the contents of the object as a string.
        See get_contents_to_file method for details about the
        parameters.

        :param byte_range: 指定下载范围。参见: ref:`byte_range`
        """

        fp = BytesIO()
        resp = self.get_contents_to_file(fp, byte_range, headers, cb, num_cb, torrent=torrent,
                                  version_id=version_id,
                                  response_headers=response_headers)
        value = fp.getvalue()
        if encoding is not None:
            value = value.decode(encoding)
        resp.data = value
        return resp

    def restore_object(self, days=None, headers=None):
        return self.bucket.restore_object(self.name, days=days, headers=headers)

    def set_object_tagging(self, tagging_set, version_id=None, headers=None):
        object_tagging = Tagging(tagging_set)
        if headers is None:
            headers = {}
        headers['Content-Type'] = 'text/xml'
        object_tagging_xml = object_tagging.to_xml()
        if not isinstance(object_tagging_xml, bytes):
            object_tagging_xml = object_tagging_xml.encode('utf-8')

        query_args = 'tagging'
        if version_id is not None:
            query_args = query_args + '&versionId=' + version_id
        response = self.bucket.connection.make_request('PUT', self.bucket.name, self.name, data=object_tagging_xml,
                                                       query_args=query_args, headers=headers)

        body = response.read()
        if response.status == 200:
            return ResponseResult(True, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_object_tagging(self, version_id=None, headers=None):
        query_args = 'tagging'
        if version_id is not None:
            query_args = query_args + '&versionId=' + version_id
        response = self.bucket.connection.make_request('GET', self.bucket.name, self.name,
                                                       query_args=query_args, headers=headers)
        body = response.read()
        if response.status == 200:
            objectTagging = Tagging(status=response.status, reason=response.reason, headers=response.headers,
                                    raw_body=body)
            h = handler.XmlHandler(objectTagging, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return objectTagging
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_object_tagging(self, version_id=None, headers=None):
        query_args = 'tagging'
        if version_id is not None:
            query_args = query_args + '&versionId=' + version_id
        response = self.bucket.connection.make_request('DELETE', self.bucket.name, self.name,
                                                       query_args=query_args, headers=headers)
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def fetch_object(self, source_url=None, callback_url=None, headers=None):
        return self.bucket.fetch_object(self.name, source_url=source_url, callback_url=callback_url, headers=headers)

    def recover_object(self, overwrite=None, retention_id=None, headers=None):
        if headers is None:
            headers = {}
        if overwrite is not None:
            headers[self.provider.retention_overwrite_header] = 'true' if overwrite else 'false'
        if retention_id is not None:
            headers[self.provider.retention_id_header] = retention_id
        query_args = 'recover'

        response = self.bucket.connection.make_request('POST', self.bucket.name, self.name,
                                                       query_args=query_args, headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def clear_object(self, retention_id=None, headers=None):
        if headers is None:
            headers = {}
        if retention_id is not None:
            headers[self.provider.retention_id_header] = retention_id
        query_args = 'clear'
        response = self.bucket.connection.make_request('DELETE', self.bucket.name, self.name,
                                                       query_args=query_args, headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def upload_file(
            self,
            filename,
            part_size=DEFAULT_PART_SIZE,
            threads_num=3,
            resumable=False,
            resumable_filename=None,
            headers=None,
    ):
        real_threads_num = threads_num
        if self.bucket.connection.local_encrypt:
            real_threads_num = 1
            logger.debug("key_name={0}, local_encrypt={1}, set threads_num to {2}"
                         .format(self.name, self.bucket.connection.local_encrypt, real_threads_num))
        executor = BlockThreadPoolExecutor(
            max_workers=real_threads_num,
            thread_name_prefix='upload-task',
        )
        return UploadTask(
            self,
            self.bucket,
            filename,
            executor,
            part_size=part_size,
            resumable=resumable,
            resumable_filename=resumable_filename,
        ).upload(headers)

    def download_file(
            self,
            filename,
            part_size=DEFAULT_PART_SIZE,
            threads_num=3,
            resumable=False,
            resumable_filename=None,
            headers=None,
    ):
        executor = BlockThreadPoolExecutor(
            max_workers=threads_num,
            thread_name_prefix='download-task',
        )
        return DownloadTask(
            self,
            self.bucket,
            filename,
            executor,
            part_size=part_size,
            resumable=resumable,
            resumable_filename=resumable_filename,
        ).download(headers)

    def copy_file(
            self,
            src_key,
            part_size=DEFAULT_PART_SIZE,
            threads_num=3,
            resumable=False,
            resumable_filename=None,
            headers=None,
            copy_src_metadata=True,
            copy_src_tagging=True,
    ):
        executor = BlockThreadPoolExecutor(
            max_workers=threads_num,
            thread_name_prefix='copy-task',
        )
        return CopyTask(
            src_key,
            self,
            executor,
            part_size=part_size,
            resumable=resumable,
            resumable_filename=resumable_filename,
            copy_src_metadata=copy_src_metadata,
            copy_src_tagging=copy_src_tagging,
        ).copy(headers)

    def across_region_copy_file(
            self,
            src_key,
            part_size=DEFAULT_PART_SIZE,
            threads_num=3,
            resumable=False,
            resumable_filename=None,
            headers=None,
            copy_src_metadata=True,
            copy_src_tagging=True,
    ):
        executor = BlockThreadPoolExecutor(
            max_workers=threads_num,
            thread_name_prefix='across-region-copy-task',
        )
        return AcrossRegionCopyTask(
            src_key,
            self,
            executor,
            part_size=part_size,
            resumable=resumable,
            resumable_filename=resumable_filename,
            copy_src_metadata=copy_src_metadata,
            copy_src_tagging=copy_src_tagging,
        ).copy(headers)

    def set_object_migration(self, src_bucket_name, src_key_name, storage_class=None, headers=None):
        if headers is None:
            headers = {}
        migration_source = '/{0}/{1}'.format(src_bucket_name, url_encode(src_key_name)).replace('//', '/%2F')
        headers[self.provider.migration_source_header] = migration_source
        if storage_class is not None:
            headers[self.provider.storage_class_header] = storage_class

        response = self.bucket.connection.make_request('PUT', self.bucket.name, self.name, headers=headers,
                                                       query_args='migration')
        body = response.read()
        if response.status == 200:
            result = MigrationResult(status=response.status, reason=response.reason, headers=response.headers)
            h = handler.XmlHandler(result, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return result
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_object_migration(self, headers=None):
        if headers is None:
            headers = {}
        query_args = 'migration'
        response = self.bucket.connection.make_request('GET', self.bucket.name, self.name, headers=headers,
                                                       query_args=query_args)
        body = response.read()
        if response.status == 200:
            result = MigrationConfiguration(status=response.status, reason=response.reason, headers=response.headers)
            h = handler.XmlHandler(result, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return result
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def handle_version_headers(self, resp, force=False):
        provider = self.bucket.connection.provider
        # If the Key object already has a version_id attribute value, it
        # means that it represents an explicit version and the user is
        # doing a get_contents_*(version_id=<foo>) to retrieve another
        # version of the Key.  In that case, we don't really want to
        # overwrite the version_id in this Key object.  Comprende?
        if self.version_id is None or force:
            self.version_id = resp.getheader(provider.version_id, None)
        self.source_version_id = resp.getheader(provider.copy_source_version_id,
                                                None)
        if resp.getheader(provider.delete_marker, 'false') == 'true':
            self.delete_marker = True
        else:
            self.delete_marker = False

    def handle_encryption_headers(self, resp):
        provider = self.bucket.connection.provider
        if provider.server_side_encryption_header:
            self.encrypted = resp.getheader(
                provider.server_side_encryption_header, None)
        else:
            self.encrypted = None

    def handle_restore_headers(self, response):
        provider = self.bucket.connection.provider
        header = response.getheader(provider.restore_header)
        if header is None:
            return
        parts = header.split(',', 1)
        for part in parts:
            key, val = [i.strip() for i in part.split('=')]
            val = val.replace('"', '')
            if key == 'ongoing-request':
                self.ongoing_restore = True if val.lower() == 'true' else False
            elif key == 'expiry-date':
                self.expiry_date = val

    def handle_addl_headers(self, headers):
        """
        Used by Key subclasses to do additional, provider-specific
        processing of response headers. No-op for this base class.
        """
        pass

    def handle_user_metas(self, response):
        """
        If there are user set custom metas, this function will put them into a dict.
        """
        # print response.msg
        provider = self.bucket.connection.provider
        user_key_reg = provider.metadata_prefix + ".*"
        for header_key, header_value in list(response.msg.items()):
            reg_match = re.match(user_key_reg, header_key)
            if reg_match:
                self.user_meta[header_key] = header_value

    def handle_storage_class(self, response):
        provider = self.bucket.connection.provider
        if provider:
            sc = response.getheader(provider.storage_class_header)
            if sc:
                self.storage_class = sc
            else:
                self.storage_class = "STANDARD"

    def compute_md5(self, fp, size=None):
        hex_digest, b64_digest, data_size = compute_md5(fp, size=size)
        self.size = data_size
        return (hex_digest, b64_digest)

    def compute_encrypted_md5(self, fp):
        hex_digest, b64_digest = compute_encrypted_md5(fp)
        return b64_digest

    def handle_tagging_count(self, response):
        provider = self.bucket.connection.provider
        if provider:
            sc = response.getheader(provider.tagging_count_header)
            if sc:
                self.tagging_count = sc

    def handle_object_type(self, response):
        provider = self.bucket.connection.provider
        if provider:
            sc = response.getheader(provider.object_type_header)
            if sc:
                self.object_type = sc

    def handle_next_position(self, response):
        provider = self.bucket.connection.provider
        if provider:
            sc = response.getheader(provider.append_next_position_header)
            if sc:
                self.append_next_position = sc

    def handle_checksum_crc64ecma(self, response):
        provider = self.bucket.connection.provider
        if provider:
            sc = response.getheader(provider.checksum_crc64ecma_header)
            if sc:
                self.server_crc = sc


def _make_range_string(range):
    if range is None:
        return ''

    start = range[0]
    last = range[1]

    if start is None and last is None:
        return ''

    return 'bytes=' + _range(start, last)


def _range(start, last):
    def to_str(pos):
        if pos is None:
            return ''
        else:
            return str(pos)

    return to_str(start) + '-' + to_str(last)


async def _read_file_async(filename):
    async with aiofiles.open(filename, mode='rb') as file:
        return await file.read()


async def _write_file_async(filename, data):
    async with aiofiles.open(filename, mode='wb') as file:
        return await file.write(data)
