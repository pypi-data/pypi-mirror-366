# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import logging
import os
import re
from concurrent import futures
from pathlib import Path

import six
import xml

from ks3.bucketDecompressPolicy import BucketDecompressPolicy
from ks3.responseResult import ResponseResult, ResponseMetadata
from ks3.share_encryption import ShareCryptor
from ks3.xmlParsers.bucketAccessMonitor import BucketAccessMonitor
from ks3.xmlParsers.bucketCors import BucketCors
from ks3.xmlParsers.bucketCrossReplicate import BucketCrossReplicate
from ks3.xmlParsers.bucketEncryption import BucketEncryption
from ks3.xmlParsers.bucketLifecycle import BucketLifecycle
from ks3.tagging import Tagging
from ks3.xmlParsers.bucketQos import BucketQos
from ks3.xmlParsers.requesterQos import RequesterQos

try:
    import urllib.parse as parse  # for Python 3
except ImportError:
    import urllib as parse  # for Python 2

from datetime import datetime as DT
from dateutil.tz import tzutc
from dateutil import parser
import ks3.utils
from ks3 import handler
from ks3.utils import RetryPolicy, ExponentialWait, StopAfterAttempt
from ks3.acl import Policy, CannedACLStrings
from ks3.bucketlistresultset import BucketListResultSet
from ks3.bucketlistresultset import MultiPartUploadListResultSet
from ks3.bucketlistresultset import VersionedBucketListResultSet
from ks3.bucketlistresultset import BucketRetentionListResultSet
from ks3.xmlParsers.bucketLogging import BucketLogging
from ks3.exception import S3ResponseError
from ks3.key import Key
from ks3.multipart import MultiPartUpload, CompleteMultiPartUpload
from ks3.prefix import Prefix
from ks3.resultset import ResultSet
from ks3.xmlParsers.bucketQuota import BucketQuota
from ks3.xmlParsers.bucketVersioning import BucketVersioningConfig
from ks3.deletemarker import DeleteMarker
from ks3.xmlParsers.bucketRetention import BucketRetention
from ks3.xmlParsers.bucketInventory import BucketInventory, ListInventoryConfigurationsResult

try:
    from ks3.encryption import Crypts
except:
    pass

logger = logging.getLogger(__name__)


# 检验conditions参数是否符合要求
def _check_conditions(conditions):
    allowed_types = {'eq', 'starts-with', 'content-length-range'}
    if conditions is not None:
        if not isinstance(conditions, list):
            raise ValueError("conditions必须是列表")
    bucket_flag = False
    for condition in conditions:
        if isinstance(condition, list):
            if len(condition) != 3:
                raise ValueError("列表格式的condition必须有3个元素")
            if condition[0] not in allowed_types:
                raise ValueError("condition的操作符必须是%s之一" % allowed_types)
            if condition[1] == '$bucket':
                bucket_flag = True
        if isinstance(condition, dict) and 'bucket' in condition:
            bucket_flag = True
    if not bucket_flag:
        raise ValueError("必须有包含bucket的condition")


class Bucket(object):
    def __init__(self, connection=None, name=None, region=None, type=None, creation_date=None, *args, **kwargs):
        self.connection = connection
        self.name = name
        self.region = region
        self.type = type
        self.creation_date = creation_date

        self.response_metadata = ResponseMetadata(**kwargs)

    def __repr__(self):
        return '<Bucket: %s>' % self.name

    def __iter__(self):
        return iter(BucketListResultSet(self))

    def __contains__(self, key_name):
        return not (self.get_key(key_name, validate=True) is None)

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Name':
            self.name = value
        elif name == 'CreationDate':
            self.creation_date = value
        elif name == 'Region':
            self.region = value
            setattr(self, name, value)  # 兼容旧的处理
        elif name == 'Type':
            self.type = value
            setattr(self, name, value)
        else:
            setattr(self, name, value)

    def new_key(self, key_name=None):
        """
        Creates a new key 
        
        :type key_name: string
        :param key_name: The name of the key to create

        :rtype: :class:`boto.s3.key.Key` or subclass
        :returns: An instance of the newly created key object
        """
        if not key_name:
            raise ValueError('Empty key names are not allowed')
        return Key(self, key_name)

    def copy_key(self, new_key_name, src_bucket_name, src_key_name, src_version_id=None, headers=None, query_args=None,
                 encrypt_key=False):
        """
        Create a new key in the bucket by copying another existing key.
        :param new_key_name: The name of the new key
        :param src_bucket_name: The name of the source bucket
        :param src_key_name: The name of the source key
        :param headers: A dictionary of header name/value pairs.
        :param query_args: A string of additional querystring arguments
            to append to the request
        :param encrypt_key: If True, the new copy of the object will
            be encrypted on the server-side by KS3 and will be stored
            in an encrypted form while at rest in KS3.
        :return:
        """
        if not new_key_name or not src_key_name:
            raise ValueError('Empty key names are not allowed')
        if not src_bucket_name:
            raise ValueError('Empty bucket name are not allowed')
        headers = headers or {}
        provider = self.connection.provider
        if encrypt_key:
            headers[provider.server_side_encryption_header] = 'AES256'
        src = '/%s/%s' % (src_bucket_name, parse.quote_plus(src_key_name.encode('utf-8')))
        src = src.replace('//', '/%2F')
        if src_version_id:
            src += '?versionId=%s' % src_version_id
        headers[provider.copy_source_header] = str(src)
        response = self.connection.make_request('PUT', self.name, new_key_name,
                                                headers=headers,
                                                query_args=query_args)
        body = response.read()
        if response.status == 200:
            key = self.new_key(new_key_name)
            key.handle_checksum_crc64ecma(response)
            h = handler.XmlHandler(key, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            if hasattr(key, 'Error'):
                raise provider.storage_copy_error(key.Code, key.Message, body)
            key.response_metadata = ResponseMetadata(status=response.status, reason=response.reason,
                                                     headers=response.headers)
            return key
        else:
            raise provider.storage_response_error(response.status,
                                                  response.reason, body)

    def generate_url(self, expires_in, method='GET', headers=None,
                     force_http=False, response_headers=None,
                     expires_in_absolute=False):
        return self.connection.generate_url(expires_in, method, self.name,
                                            headers=headers,
                                            force_http=force_http,
                                            response_headers=response_headers,
                                            expires_in_absolute=expires_in_absolute)

    def lookup(self, key_name):
        k, resp = self._get_key_internal(key_name, None, None)
        return k is not None

    # def delete_keys(self, keys, quiet=False, mfa_token=None, headers=None):
    #     """
    #     Deletes a set of keys using S3's Multi-object delete API. If a
    #     VersionID is specified for that key then that version is removed.
    #     Returns a MultiDeleteResult Object, which contains Deleted
    #     and Error elements for each key you ask to delete.
    #     """
    #     ikeys = iter(keys)
    #     result = MultiDeleteResult(self)
    #     provider = self.connection.provider
    #     query_args = 'delete'
    #
    #     def delete_keys2(hdrs):
    #         hdrs = hdrs or {}
    #         data = u"""<?xml version="1.0" encoding="UTF-8"?>"""
    #         data += u"<Delete>"
    #         if quiet:
    #             data += u"<Quiet>true</Quiet>"
    #         count = 0
    #         while count < 1000:
    #             try:
    #                 key = next(ikeys)
    #             except StopIteration:
    #                 break
    #             if isinstance(key, six.string_types):
    #                 key_name = key
    #                 version_id = None
    #             elif isinstance(key, tuple) and len(key) == 2:
    #                 key_name, version_id = key
    #             elif (isinstance(key, Key) or isinstance(key, DeleteMarker)) and key.name:
    #                 key_name = key.name
    #                 version_id = key.version_id
    #             else:
    #                 if isinstance(key, Prefix):
    #                     key_name = key.name
    #                     code = 'PrefixSkipped'   # Don't delete Prefix
    #                 else:
    #                     key_name = repr(key)   # try get a string
    #                     code = 'InvalidArgument'  # other unknown type
    #                 message = 'Invalid. No delete action taken for this object.'
    #                 error = Error(key_name, code=code, message=message)
    #                 result.errors.append(error)
    #                 continue
    #             count += 1
    #             data += u"<Object><Key>%s</Key>" % xml.sax.saxutils.escape(key_name)
    #             if version_id:
    #                 data += u"<VersionId>%s</VersionId>" % version_id
    #             data += u"</Object>"
    #         data += u"</Delete>"
    #         if count <= 0:
    #             return False  # no more
    #         data = data.encode('utf-8')
    #         fp = BytesIO(data)
    #         md5 = boto.utils.compute_md5(fp)
    #         hdrs['Content-MD5'] = md5[1]
    #         hdrs['Content-Type'] = 'text/xml'
    #         if mfa_token:
    #             hdrs[provider.mfa_header] = ' '.join(mfa_token)
    #         response = self.connection.make_request('POST', self.name,
    #                                                 headers=hdrs,
    #                                                 query_args=query_args,
    #                                                 data=data)
    #         body = response.read()
    #         if response.status == 200:
    #             h = handler.XmlHandler(result, self)
    #             if not isinstance(body, bytes):
    #                 body = body.encode('utf-8')
    #             xml.sax.parseString(body, h)
    #             return count >= 1000  # more?
    #         else:
    #             raise provider.storage_response_error(response.status,
    #                                                   response.reason,
    #                                                   body)
    #     while delete_keys2(headers):
    #         pass
    #     return result

    def get_key(self, key_name, headers=None, version_id=None,
                response_headers=None, validate=False):
        """
        Check to see if a particular key exists within the bucket.
        """
        if validate is False:
            # if headers or version_id or response_headers:
            #     raise BotoClientError(
            #         "When providing 'validate=False', no other params " + \
            #         "are allowed."
            #     )

            # This leans on the default behavior of ``new_key`` (not hitting
            # the service). If that changes, that behavior should migrate here.
            return self.new_key(key_name)

        query_args_l = {}
        if version_id:
            query_args_l['versionId'] = version_id
        if response_headers:
            for rk, rv in six.iteritems(response_headers):
                query_args_l[rk] = parse.quote(rv)

        key, resp = self._get_key_internal(key_name, headers, query_args_l)
        return key

    def get_key_meta(self, key_name, headers=None, version_id=None,
                     response_headers=None, validate=True):
        """
        Check to see if a particular key exists within the bucket.
        """
        if validate is False:
            # if headers or version_id or response_headers:
            #     raise BotoClientError(
            #         "When providing 'validate=False', no other params " + \
            #         "are allowed."
            #     )

            # This leans on the default behavior of ``new_key`` (not hitting
            # the service). If that changes, that behavior should migrate here.
            return self.new_key(key_name)

        query_args_l = {}
        if version_id:
            query_args_l['versionId'] = version_id
        if response_headers:
            for rk, rv in six.iteritems(response_headers):
                query_args_l[rk] = parse.quote(rv)

        k, resp = self._get_key_internal(key_name, headers, query_args_l)
        return ResponseResult(data=resp, status=resp.status, reason=resp.reason,
                              headers=resp.headers)

    def _get_key_internal(self, key_name, headers, query_args_l):
        query_args = query_args_l or None
        response = self.connection.make_request('HEAD', self.name, key_name,
                                                headers=headers,
                                                query_args=query_args)
        response.read()
        # Allow any success status (2xx) - for example this lets us
        # support Range gets, which return status 206:
        if response.status // 100 == 2:
            k = Key(self)
            # provider = self.connection.provider
            # k.metadata = boto.utils.get_aws_metadata(response.msg, provider)
            for field in Key.base_fields:
                k.__dict__[field.lower().replace('-', '_')] = \
                    response.getheader(field)
            # the following machinations are a workaround to the fact that
            # apache/fastcgi omits the content-length header on HEAD
            # requests when the content-length is zero.
            # See http://goo.gl/0Tdax for more details.
            clen = response.getheader('content-length')
            if clen:
                k.size = int(response.getheader('content-length'))
            else:
                k.size = 0
            k.name = key_name
            k.handle_version_headers(response)
            k.handle_encryption_headers(response)
            k.handle_restore_headers(response)
            k.handle_addl_headers(response.getheaders())
            k.handle_user_metas(response)
            k.handle_storage_class(response)
            k.handle_tagging_count(response)
            k.handle_object_type(response)
            k.handle_next_position(response)
            k.handle_checksum_crc64ecma(response)
            k.response_metadata = ResponseMetadata(status=response.status, reason=response.reason,
                                                   headers=response.headers)
            return k, response
        else:
            if response.status == 404:
                return None, response
            else:
                raise S3ResponseError(response.status, response.reason, None,
                                      request_id=response.getheader('x-kss-request-id'))

    def list(self, prefix=None, delimiter='/', marker=None, max_keys=None,
             retry_policy=RetryPolicy(), request_interval=0):
        """
        List object keys within specified bucket.
        delimiter: str 默认为 '/' 。只会列举当前一层的文件和目录，且单次列举最多100个对象。
        如果设置为 delimiter='' 可以列举所有对象，且单次列举最多1000个对象。
        """
        return BucketListResultSet(self, prefix, delimiter, marker, max_keys,
                                   retry_policy=retry_policy, request_interval=request_interval)

    def list_retention(self, prefix=None, delimiter='/', marker=None, max_keys=None, request_interval=0):
        """
        delimiter: str 默认为 '/' 。只会列举当前一层的文件和目录，且单次列举最多100个对象。
        如果设置为 delimiter='' 可以列举所有对象，且单次列举最多1000个对象。
        """
        return BucketRetentionListResultSet(self, prefix, delimiter, marker, max_keys, request_interval=request_interval)

    def listObjects(self, prefix=None, delimiter=None, marker=None, max_keys=None,
                    filename=None, start_time=None, end_time=None, request_interval=0):
        keys = self.list(prefix, delimiter, marker, max_keys, request_interval=request_interval)
        keyLists = list()
        fd = None
        if filename is not None:
            fd = open(filename, "a")  # 利用追加模式,参数从w替换为a即可
            fd.seek(0)
        for k in keys:
            if isinstance(k, Key):
                if hasattr(DT, "timestamp"):
                    datetime = int(round(parser.parse(k.last_modified).timestamp()))
                else:
                    datetime = int(
                        round((parser.parse(k.last_modified) - DT(1970, 1, 1, tzinfo=tzutc())).total_seconds()))
                if start_time is None and end_time is not None:
                    if datetime >= end_time:
                        keyLists.append(k.name)
                        if fd:
                            fd.write("{}\n".format(k.name))
                elif end_time is None and start_time is not None:
                    if datetime <= start_time:
                        keyLists.append(k.name)
                        if fd:
                            fd.write("{}\n".format(k.name))
                elif end_time is not None and start_time is not None:
                    if start_time <= datetime or datetime <= end_time:
                        keyLists.append(k.name)
                        if fd:
                            fd.write("{}\n".format(k.name))
                elif end_time is None and start_time is None:
                    keyLists.append(k.name)
                    if fd:
                        fd.write("{}\n".format(k.name))

        if fd:
            fd.flush()
            fd.close()
        return keyLists

    def list_versions(self, prefix='', delimiter='', key_marker='',
                      version_id_marker='', headers=None, encoding_type=None,
                      request_interval=0):
        return VersionedBucketListResultSet(self, prefix, delimiter,
                                            key_marker, version_id_marker,
                                            headers,
                                            encoding_type=encoding_type,
                                            request_interval=request_interval)

    def list_v2(self, **params):
        """
        List object V2.
        """
        params_v2 = params.copy()
        params_v2['list_type'] = 2
        params_v2['delimiter'] = params_v2.get('delimiter', '/')
        return BucketListResultSet(self, **params_v2)

    def get_all_keys(self, retry_policy=None, **params):
        """
        A lower-level method for listing contents of a bucket.
        """
        return self._get_all([('Contents', Key), ('CommonPrefixes', Prefix)], '', retry_policy=retry_policy, **params)

    def get_all_versions(self, headers=None, **params):
        """
        A lower-level method for listing contents of a bucket.
        """
        return self._get_all([('Version', Key),
                              ('CommonPrefixes', Prefix),
                              ('DeleteMarker', DeleteMarker)],
                             'versions', headers, **params)

    def get_all_retention_keys(self, **params):
        return self._get_all([('Contents', Key), ('CommonPrefixes', Prefix)], initial_query_string='recycle', **params)

    def _get_all(self, element_map, initial_query_string='',
                 headers=None, retry_policy=None, **params):
        query_args = self._get_all_query_args(
            params,
            initial_query_string=initial_query_string
        )
        response = self.connection.make_request('GET', self.name,
                                                headers=headers,
                                                query_args=query_args,
                                                retry_policy=retry_policy)
        body = response.read()
        if response.status == 200:
            rs = ResultSet(element_map, status=response.status, reason=response.reason, headers=response.headers,
                           raw_body=body)
            h = handler.XmlHandler(rs, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return rs
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def _get_all_query_args(self, params, initial_query_string=''):
        pairs = []

        if initial_query_string:
            pairs.append(initial_query_string)

        for key, value in sorted(list(params.items()), key=lambda x: x[0]):
            if value is None:
                continue
            key = key.replace('_', '-')
            if key == 'maxkeys':
                key = 'max-keys'
            if not isinstance(value, six.string_types + (six.binary_type,)):
                value = six.text_type(value)
            if not isinstance(value, six.binary_type):
                value = value.encode('utf-8')
            if value:
                pairs.append('%s=%s' % (
                    parse.quote(key),
                    parse.quote(value)
                ))

        return '&'.join(pairs)

    def set_xml_acl(self, acl_str, key_name='', headers=None, version_id=None,
                    query_args=None):
        if query_args is None:
            query_args = {'acl': ''}
        if version_id:
            query_args['versionId'] = version_id
        if not isinstance(acl_str, bytes):
            acl_str = acl_str.encode('utf-8')
        if headers is None:
            headers = {}
        headers['content-type'] = 'application/xml'
        response = self.connection.make_request('PUT', self.name, key_name,
                                                data=acl_str,
                                                query_args=query_args,
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        if response.status != 200:
            raise S3ResponseError(response.status, response.reason, body)

    def set_acl(self, acl_or_str, key_name='', headers=None, version_id=None):
        if isinstance(acl_or_str, Policy):
            return self.set_xml_acl(acl_or_str.to_xml(), key_name,
                                    headers, version_id)
        else:
            return self.set_canned_acl(acl_or_str, key_name,
                                       headers, version_id)

    def set_canned_acl(self, acl_str, key_name='', headers=None,
                       version_id=None):
        assert acl_str in CannedACLStrings

        if headers:
            headers[self.connection.provider.acl_header] = acl_str
        else:
            headers = {self.connection.provider.acl_header: acl_str}

        query_args = 'acl'
        if version_id:
            query_args += '&versionId=%s' % version_id
        response = self.connection.make_request('PUT', self.name, key_name,
                                                headers=headers, query_args=query_args)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        elif response.status != 200:
            raise S3ResponseError(response.status, response.reason, body)

    def get_acl(self, key_name='', headers=None, version_id=None):
        query_args = 'acl'
        if version_id:
            query_args += '&versionId=%s' % version_id
        response = self.connection.make_request('GET', self.name, key_name,
                                                query_args=query_args,
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            policy = Policy(self, status=response.status, reason=response.reason, headers=response.headers,
                            raw_body=body)
            h = handler.XmlHandler(policy, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return policy
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def enable_logging(self, target_bucket, target_prefix='',
                       grants=None, headers=None):
        """
        Enable logging on a bucket.

        :param headers:
        :type target_bucket: bucket or string
        :param target_bucket: The bucket to log to.

        :type target_prefix: string
        :param target_prefix: The prefix which should be prepended to the
            generated log files written to the target_bucket.

        :type grants: list of Grant objects
        :param grants: A list of extra permissions which will be granted on
            the log files which are created.

        :rtype: bool
        :return: True if ok or raises an exception.
        """
        if isinstance(target_bucket, Bucket):
            target_bucket = target_bucket.name
        blogging = BucketLogging(target=target_bucket, target_prefix=target_prefix,
                                 grants=grants)
        return self.set_bucket_logging(blogging.to_xml(), headers=headers)

    def set_bucket_logging(self, logging_xml, headers=None):
        """
        Set logging on a bucket directly to the given xml string.

        :param headers:
        :type logging_xml: unicode string
        :param logging_xml: The XML for the bucketloggingstatus which
            will be set.  The string will be converted to utf-8 before
            it is sent.  Usually, you will obtain this XML from the
            BucketLogging object.

        :rtype: bool
        :return: True if ok or raises an exception.
        """

        if headers is None:
            headers = {}
        body = logging_xml
        if not isinstance(body, bytes):
            body = body.encode('utf-8')

        # md5 = ks3.utils.compute_base64_md5_digest(body)
        # headers['Content-MD5'] = md5
        headers['content-type'] = 'application/xml'
        response = self.connection.make_request('PUT', self.name, data=body,
                                                query_args='logging', headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def disable_logging(self, headers=None):
        """
        Disable logging on a bucket.

        :rtype: bool
        :return: True if ok or raises an exception.
        """
        blogging = BucketLogging()
        return self.set_bucket_logging(blogging.to_xml(), headers=headers)

    def get_bucket_logging(self, headers=None):
        """
        Get the logging for this bucket.

        :rtype: :class:`ks3.xmlParsers.bucketLogging.BucketLogging`
        :return: A BucketLogging object for this bucket.
        """
        response = self.connection.make_request('GET', self.name,
                                                query_args='logging', headers=headers)
        body = response.read()
        if response.status == 200:
            blogging = BucketLogging(status=response.status, reason=response.reason, headers=response.headers,
                                     raw_body=body)
            h = handler.XmlHandler(blogging, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return blogging
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_key(self, key_name, headers=None, version_id=None,
                   mfa_token=None):
        """
        Deletes a key from the bucket.
        """
        if not key_name:
            raise ValueError('Empty key names are not allowed')
        return self._delete_key_internal(key_name, headers=headers,
                                         version_id=version_id,
                                         mfa_token=mfa_token)

    def _delete_key_internal(self, key_name, headers=None, version_id=None,
                             mfa_token=None, query_args_l=None):
        query_args_l = query_args_l or ""
        provider = self.connection.provider
        if version_id:
            query_args_l.append('versionId=%s' % version_id)
        query_args = '&'.join(query_args_l) or None
        if mfa_token:
            if not headers:
                headers = {}
            headers[provider.mfa_header] = ' '.join(mfa_token)
        response = self.connection.make_request('DELETE', self.name, key_name,
                                                headers=headers,
                                                query_args=query_args)
        body = response.read()
        if response.status != 204:
            raise provider.storage_response_error(response.status,
                                                  response.reason, body)
        else:
            # return a key object with information on what was deleted.
            k = Key(self)
            k.name = key_name
            k.handle_version_headers(response)
            k.handle_addl_headers(response.getheaders())
            k.response_metadata = ResponseMetadata(status=response.status, reason=response.reason,
                                                   headers=response.headers)
            return k

    def list_multipart_uploads(self, key_marker='',
                               upload_id_marker='', prefix='', max_uploads=None, delimiter='',
                               headers=None, encoding_type=None, request_interval=0):
        """
        List multipart upload objects within a bucket.  This returns an
        instance of an MultiPartUploadListResultSet that automatically
        handles all of the result paging, etc. from S3.  You just need
        to keep iterating until there are no more results.

        :type key_marker: string
        :param key_marker: The "marker" of where you are in the result set

        :type upload_id_marker: string
        :param upload_id_marker: The upload identifier

        :param encoding_type: Requests Amazon S3 to encode the response and
            specifies the encoding method to use.

            An object key can contain any Unicode character; however, XML 1.0
            parser cannot parse some characters, such as characters with an
            ASCII value from 0 to 10. For characters that are not supported in
            XML 1.0, you can add this parameter to request that Amazon S3
            encode the keys in the response.

            Valid options: ``url``
        :type encoding_type: string

        :rtype: :class:`boto.s3.bucketlistresultset.BucketListResultSet`
        :return: an instance of a BucketListResultSet that handles paging, etc
        """
        return MultiPartUploadListResultSet(self, key_marker,
                                            upload_id_marker, prefix=prefix,
                                            max_uploads=max_uploads, delimiter=delimiter,
                                            headers=headers,
                                            encoding_type=encoding_type,
                                            request_interval=request_interval)

    def get_all_multipart_uploads(self, headers=None, **params):
        """
        A lower-level, version-aware method for listing active
        MultiPart uploads for a bucket.
        """
        # self.validate_kwarg_names(params, ['max_uploads', 'key_marker',
        #                                   'upload_id_marker', 'encoding_type',
        #                                   'delimiter', 'prefix'])
        return self._get_all([('Upload', MultiPartUpload),
                              ('CommonPrefixes', Prefix)],
                             'uploads', headers, **params)

    def initiate_multipart_upload(self, key_name, headers=None,
                                  reduced_redundancy=False,
                                  metadata=None, encrypt_key=False,
                                  policy=None, calc_encrypt_md5=True):
        """
        Start a multipart upload operation.
            Note: After you initiate multipart upload and upload one or more
            parts, you must either complete or abort multipart upload in order
            to stop getting charged for storage of the uploaded parts. Only
            after you either complete or abort multipart upload, Amazon S3
            frees up the parts storage and stops charging you for the parts
            storage.
        """
        query_args = 'uploads'
        provider = self.connection.provider
        headers = headers or {}
        if policy:
            headers[provider.acl_header] = policy
        if reduced_redundancy:
            storage_class_header = provider.storage_class_header
            if storage_class_header:
                headers[storage_class_header] = 'REDUCED_REDUNDANCY'
                # TODO: what if the provider doesn't support reduced redundancy?
        if encrypt_key:
            headers[provider.server_side_encryption_header] = 'AES256'
        if metadata is None:
            metadata = {}

        headers = ks3.utils.merge_meta(headers, metadata,
                                       self.connection.provider)
        if self.connection.local_encrypt:
            crypts = Crypts(self.connection.key)
            crypts.calc_md5 = calc_encrypt_md5
            crypts.action_info = "init_multi"
            md5_generator = hashlib.md5()
            md5_generator.update(crypts.key)
            headers["x-kss-meta-key"] = base64.b64encode(md5_generator.hexdigest().encode()).decode()
            headers["x-kss-meta-iv"] = base64.b64encode(crypts.first_iv).decode()
            response = self.connection.make_request('POST', self.name, key_name,
                                                    query_args=query_args,
                                                    headers=headers)
        else:
            response = self.connection.make_request('POST', self.name, key_name,
                                                    query_args=query_args,
                                                    headers=headers)
        body = response.read()
        if response.status == 200:
            resp = MultiPartUpload(self, status=response.status, reason=response.reason,
                                   headers=response.headers)
            if self.connection.local_encrypt:
                resp.set_crypt_context(crypts)
            h = handler.XmlHandler(resp, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return resp
        else:
            raise self.connection.provider.storage_response_error(
                response.status, response.reason, body)

    def complete_multipart_upload(self, key_name, upload_id,
                                  xml_body, headers=None):
        """
        Complete a multipart upload operation.
        """
        query_args = 'uploadId=%s' % upload_id
        if headers is None:
            headers = {}
        headers['Content-Type'] = 'text/xml'
        logger.debug('key: {0}, bucket: {1}, upload_id: {2}, request_body: {3}'
                     .format(key_name, self.name, upload_id, xml_body))
        response = self.connection.make_request('POST', self.name, key_name,
                                                query_args=query_args,
                                                headers=headers, data=xml_body)
        contains_error = False
        body = response.read().decode('utf-8')
        # Some errors will be reported in the body of the response
        # even though the HTTP response code is 200.  This check
        # does a quick and dirty peek in the body for an error element.
        if body.find('<Error>') > 0:
            contains_error = True
        if response.status == 200 and not contains_error:
            resp = CompleteMultiPartUpload(self, status=response.status, reason=response.reason,
                                           headers=response.headers)
            h = handler.XmlHandler(resp, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            # Use a dummy key to parse various response headers
            # for versioning, encryption info and then explicitly
            # set the completed MPU object values from key.
            k = Key(self)
            k.handle_version_headers(response)
            k.handle_encryption_headers(response)
            resp.version_id = k.version_id
            resp.encrypted = k.encrypted
            resp.status = response.status
            return resp
        else:
            raise self.connection.provider.storage_response_error(
                response.status, response.reason, body)

    def cancel_multipart_upload(self, key_name, upload_id, headers=None):
        """
        To verify that all parts have been removed, so you don't get charged
        for the part storage, you should call the List Parts operation and
        ensure the parts list is empty.
        """
        query_args = 'uploadId=%s' % upload_id
        response = self.connection.make_request('DELETE', self.name, key_name,
                                                query_args=query_args,
                                                headers=headers)
        body = response.read()
        if response.status != 204:
            raise self.connection.provider.storage_response_error(
                response.status, response.reason, body)
        return ResponseResult(data=response, status=response.status, reason=response.reason,
                              headers=response.headers)

    def set_adp(self, key_name, headers):
        query_args = 'adp'
        response = self.connection.make_request('PUT', self.name, key_name,
                                                headers=headers, query_args=query_args)
        body = response.read()
        if response.status != 200:
            raise S3ResponseError(response.status, response.reason, body)
        task_id = response.getheader("TaskID")
        return ResponseResult(task_id, status=response.status, reason=response.reason,
                              headers=response.headers)

    def set_bucket_quota(self, headers=None, quota=0):
        """
        :param quota: bucket quota default 0 not limit
        :param headers: custom header
        :return: True is ok or raises an exception.
        """
        bucketQuota = BucketQuota(quota)
        quota_to_xml = bucketQuota.to_xml()
        if not isinstance(quota_to_xml, bytes):
            quota_to_xml = quota_to_xml.encode('utf-8')
        if headers is None:
            headers = {}
        headers['Content-Type'] = 'text/xml'
        response = self.connection.make_request('PUT', self.name, data=quota_to_xml,
                                                query_args='quota', headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_quota(self, headers=None):
        response = self.connection.make_request('GET', self.name,
                                                query_args='quota', headers=headers)
        body = response.read()
        if response.status == 200:
            quota = BucketQuota()
            h = handler.XmlHandler(quota, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return quota
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_policy(self, policy, headers=None):
        logger.debug('bucket: {0}, bucket_policy request_body: {1}'.format(self.name, policy))
        response = self.connection.make_request('PUT', self.name, data=policy,
                                                query_args='policy', headers=headers)
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_policy(self, headers=None):
        response = self.connection.make_request('GET', self.name,
                                                query_args='policy', headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(body, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_bucket_policy(self, headers=None):
        response = self.connection.make_request('DELETE', self.name,
                                                query_args='policy', headers=headers)
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_crr(self, target_bucket, delete_marker_status=BucketCrossReplicate.DISABLED, prefix_list=None,
                       historical_object_replication=BucketCrossReplicate.DISABLED, headers=None):
        replicate = BucketCrossReplicate(target_bucket, delete_marker_status, prefix_list,
                                         historical_object_replication)
        if headers is None:
            headers = {}
        headers['Content-Type'] = 'text/xml'
        replicate_xml = replicate.to_xml()
        logger.debug('bucket: {0}, bucket_crr request_body: {1}'.format(self.name, replicate_xml))
        if not isinstance(replicate_xml, bytes):
            replicate_xml = replicate_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(replicate_xml)
        headers['Content-MD5'] = md5
        response = self.connection.make_request('PUT', self.name, data=replicate_xml,
                                                query_args='crr', headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_crr(self, headers=None):
        response = self.connection.make_request('GET', self.name,
                                                query_args='crr', headers=headers)
        body = response.read()
        if response.status == 200:
            replicate = BucketCrossReplicate(status=response.status, reason=response.reason, headers=response.headers,
                                             raw_body=body)
            h = handler.XmlHandler(replicate, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return replicate
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_bucket_crr(self, headers=None):
        response = self.connection.make_request('DELETE', self.name,
                                                query_args='crr', headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    # deprecated. moved to key.py
    def restore_object(self, object_key_name, days=None, headers=None):
        restore_body = '''<RestoreRequest>
                            <Days>{0}</Days>
                          </RestoreRequest>'''
        response = self.connection.make_request('POST', self.name, object_key_name,
                                                data=restore_body.format(days) if days is not None else '',
                                                query_args='restore', headers=headers)
        body = response.read()
        if response.status == 200 or response.status == 202:
            return ResponseResult(body, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    # deprecated. moved to key.py
    def set_object_tagging(self, object_key_name, tagging_set, version_id=None, headers=None):
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
        logger.debug('bucket: {0}, key: {1}, request_body: {2}'.format(self.name, object_key_name, object_tagging_xml))
        response = self.connection.make_request('PUT', self.name, object_key_name, data=object_tagging_xml,
                                                query_args=query_args, headers=headers)

        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    # deprecated. moved to key.py
    def get_object_tagging(self, object_key_name, version_id=None, headers=None):

        query_args = 'tagging'
        if version_id is not None:
            query_args = query_args + '&versionId=' + version_id
        response = self.connection.make_request('GET', self.name, object_key_name,
                                                query_args=query_args, headers=headers)
        body = response.read()
        if response.status == 200:
            objectTagging = Tagging()
            h = handler.XmlHandler(objectTagging, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return objectTagging
        else:
            raise S3ResponseError(response.status, response.reason, body)

    # deprecated. moved to key.py
    def delete_object_tagging(self, object_key_name, version_id=None, headers=None):
        query_args = 'tagging'
        if version_id is not None:
            query_args = query_args + '&versionId=' + version_id
        response = self.connection.make_request('DELETE', self.name, object_key_name,
                                                query_args=query_args, headers=headers)
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    # deprecated. moved to key.py
    def fetch_object(self, object_key_name, source_url=None, callback_url=None, headers=None):
        if headers is None:
            headers = {}
        if source_url is not None:
            headers['x-kss-sourceurl'] = source_url
        if callback_url is not None:
            headers['x-kss-callbackurl'] = callback_url

        response = self.connection.make_request('PUT', self.name, object_key_name,
                                                query_args='fetch', headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_lifecycle(self, bucketLifecycle, headers=None):
        if headers is None:
            headers = {}
        bucketLifecycle_xml = bucketLifecycle.to_xml()
        if not isinstance(bucketLifecycle_xml, bytes):
            bucketLifecycle_xml = bucketLifecycle_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(bucketLifecycle_xml)
        headers['Content-MD5'] = md5
        headers['content-type'] = 'application/xml'
        logger.debug('bucket: {0}, bucket_lifecycle request_body: {1}'.format(self.name, bucketLifecycle_xml))
        response = self.connection.make_request('PUT', self.name, data=bucketLifecycle_xml,
                                                query_args='lifecycle', headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_lifecycle(self, headers=None):
        response = self.connection.make_request('GET', self.name,
                                                query_args='lifecycle', headers=headers)
        body = response.read()
        if response.status == 200:
            lifecycle = BucketLifecycle(status=response.status, reason=response.reason, headers=response.headers,
                                        raw_body=body)
            h = handler.XmlHandler(lifecycle, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return lifecycle
        else:
            raise S3ResponseError(response.status, response.reason, body)

    # delete bucket lifecycle
    def delete_bucket_lifecycle(self, headers=None):
        response = self.connection.make_request('DELETE', self.name,
                                                query_args='lifecycle', headers=headers)
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_versioning(self, version_configuration, headers=None):
        if headers is None:
            headers = {}
        version_configuration_xml = version_configuration.to_xml()
        if not isinstance(version_configuration_xml, bytes):
            version_configuration_xml = version_configuration_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(version_configuration_xml)
        headers['Content-MD5'] = md5
        headers['content-type'] = 'application/xml'
        logger.debug('bucket: {0}, bucket_versioning request_body: {1}'.format(self.name, version_configuration_xml))
        response = self.connection.make_request('PUT', self.name, data=version_configuration_xml,
                                                query_args='versioning',
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_versioning(self, headers=None):
        response = self.connection.make_request('GET', self.name,
                                                query_args='versioning', headers=headers)
        body = response.read()
        if response.status == 200:
            versioningConfig = BucketVersioningConfig(status=response.status, reason=response.reason,
                                                      headers=response.headers, raw_body=body)
            h = handler.XmlHandler(versioningConfig, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return versioningConfig
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_cors(self):
        response = self.connection.make_request('GET', self.name,
                                                query_args='cors')
        body = response.read()
        if response.status == 200:
            bucketCors = BucketCors(status=response.status, reason=response.reason, headers=response.headers,
                                    raw_body=body)
            h = handler.XmlHandler(bucketCors, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return bucketCors
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_cors(self, bucket_cors):
        headers = {'content-type': 'application/xml'}
        bucket_cors_xml = bucket_cors.to_xml()
        if not isinstance(bucket_cors_xml, bytes):
            bucket_cors_xml = bucket_cors_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(bucket_cors_xml)
        headers['content-md5'] = md5
        logger.debug('bucket: {0}, bucket_cors request_body: {1}'.format(self.name, bucket_cors_xml))
        response = self.connection.make_request('PUT', self.name, data=bucket_cors_xml,
                                                query_args='cors',
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_bucket_cors(self):
        response = self.connection.make_request('DELETE', self.name, query_args='cors')
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_mirror(self):
        response = self.connection.make_request('GET', self.name, query_args='mirror')
        body = response.read()
        if response.status == 200:
            return ResponseResult(body, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_mirror(self, mirror, headers=None):
        headers = {'content-type': 'application/json'}
        if headers is None:
            headers = {}
        mirror_dict = dict(mirror)
        mirror_json = json.dumps(mirror_dict)
        if not isinstance(mirror_json, bytes):
            mirror_json = mirror_json.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(mirror_json)
        headers['content-md5'] = md5
        logger.debug('bucket: {0}, bucket_mirror request_body: {1}'.format(self.name, mirror_json))
        response = self.connection.make_request('PUT', self.name, data=mirror_json,
                                                query_args='mirror',
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_bucket_mirror(self):
        response = self.connection.make_request('DELETE', self.name, query_args='mirror')
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_bucket_encryption(self):
        response = self.connection.make_request('DELETE', self.name, query_args='encryption')
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_retention(self, bucket_retention):
        headers = {'content-type': 'application/xml'}
        retention_xml = bucket_retention.to_xml()
        if not isinstance(retention_xml, bytes):
            retention_xml = retention_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(retention_xml)
        headers['Content-MD5'] = md5
        logger.debug('bucket: {0}, bucket_retention request_body: {1}'.format(self.name, retention_xml))
        response = self.connection.make_request('PUT', self.name, data=retention_xml,
                                                query_args='retention',
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_encryption(self, bucket_encryption):
        headers = {'content-type': 'application/xml'}
        encryption_xml = bucket_encryption.to_xml()
        if not isinstance(encryption_xml, bytes):
            encryption_xml = encryption_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(encryption_xml)
        headers['Content-MD5'] = md5
        logger.debug('bucket: {0}, bucket_encryption request_body: {1}'.format(self.name, encryption_xml))
        response = self.connection.make_request('PUT', self.name, data=encryption_xml,
                                                query_args='encryption',
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_access_monitor(self, bucket_access_monitor):
        headers = {'content-type': 'application/xml'}
        ac_xml = bucket_access_monitor.to_xml()
        if not isinstance(ac_xml, bytes):
            ac_xml = ac_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(ac_xml)
        headers['Content-MD5'] = md5
        logger.debug('bucket: {0}, bucket_access_monitor request_body: {1}'.format(self.name, ac_xml))
        response = self.connection.make_request('PUT', self.name, data=ac_xml,
                                                query_args='accessmonitor',
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_retention(self):
        response = self.connection.make_request('GET', self.name, query_args='retention')
        body = response.read()
        if response.status == 200:
            retention = BucketRetention(status=response.status, reason=response.reason, headers=response.headers,
                                        raw_body=body)
            h = handler.XmlHandler(retention, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return retention
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_encryption(self):
        response = self.connection.make_request('GET', self.name, query_args='encryption')
        body = response.read()
        if response.status == 200:
            encryption = BucketEncryption(status=response.status, reason=response.reason, headers=response.headers,
                                          raw_body=body)
            h = handler.XmlHandler(encryption, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return encryption
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_access_monitor(self):
        response = self.connection.make_request('GET', self.name, query_args='accessmonitor')
        body = response.read()
        if response.status == 200:
            access_monitor = BucketAccessMonitor(status=response.status, reason=response.reason, headers=response.headers,
                                          raw_body=body)
            h = handler.XmlHandler(access_monitor, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return access_monitor
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_inventory(self, bucket_inventory):
        headers = {'content-type': 'application/xml'}
        inventory_xml = bucket_inventory.to_xml()
        if not isinstance(inventory_xml, bytes):
            inventory_xml = inventory_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(inventory_xml)
        headers['Content-MD5'] = md5
        logger.debug('bucket: {0}, bucket_inventory request_body: {1}'.format(self.name, inventory_xml))
        response = self.connection.make_request('PUT', self.name, data=inventory_xml,
                                                query_args='inventory&id=%s' % bucket_inventory.id,
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_inventory(self, inventory_id):
        response = self.connection.make_request('GET', self.name, query_args='inventory&id=%s' % inventory_id)
        body = response.read()
        if response.status == 200:
            inventory = BucketInventory(status=response.status, reason=response.reason, headers=response.headers,
                                        raw_body=body)
            h = handler.XmlHandler(inventory, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return inventory
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def list_bucket_inventory(self):
        response = self.connection.make_request('GET', self.name, query_args='inventory')
        body = response.read()
        if response.status == 200:
            result = ListInventoryConfigurationsResult(status=response.status, reason=response.reason,
                                                       headers=response.headers,
                                                       raw_body=body)
            h = handler.XmlHandler(result, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return result
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_bucket_inventory(self, inventory_id):
        response = self.connection.make_request('DELETE', self.name, query_args='inventory&id=%s' % inventory_id)
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def upload_dir(
            self, directory, key_prefix='',
            upload_threads=3,
            part_upload_threads=3,
            part_size=100 * 1024,
            headers=None,
    ):
        dir_path = Path(directory)
        executor = ks3.utils.BlockThreadPoolExecutor(
            max_workers=upload_threads,
            thread_name_prefix='upload-dir-task',
        )
        file_futures = []
        for file in dir_path.rglob('*'):
            if file.is_dir():
                continue
            key = self.new_key(key_prefix + file.relative_to(dir_path).as_posix())
            filename = file.as_posix()
            future = executor.submit(
                key.upload_file,
                filename,
                part_size=part_size,
                threads_num=part_upload_threads,
                headers=headers,
            )
            file_futures.append(future)
        executor.shutdown(wait=True)
        for future in futures.as_completed(file_futures):
            future.result()

    def set_bucket_tagging(self, tagging_set):
        headers = {'content-type': 'text/xml'}
        bucket_tagging = Tagging(tagging_set)
        tagging_xml = bucket_tagging.to_xml()
        if not isinstance(tagging_xml, bytes):
            tagging_xml = tagging_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(tagging_xml)
        headers['Content-MD5'] = md5
        logger.debug('bucket: {0}, bucket_tagging request_body: {1}'.format(self.name, tagging_xml))
        response = self.connection.make_request('PUT', self.name, data=tagging_xml,
                                                query_args='tagging',
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_tagging(self):
        response = self.connection.make_request('GET', self.name, query_args='tagging')
        body = response.read()
        if response.status == 200:
            tagging = Tagging(status=response.status, reason=response.reason, headers=response.headers,
                                          raw_body=body)
            h = handler.XmlHandler(tagging, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return tagging
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_bucket_tagging(self):
        response = self.connection.make_request('DELETE', self.name, query_args='tagging')
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_bucket_decompress_policy(self, decompress_policy: BucketDecompressPolicy=None):
        decompress_policy_raw = decompress_policy.to_json()
        return self.set_bucket_decompress_policy_raw(decompress_policy_raw)

    def set_bucket_decompress_policy_raw(self, decompress_policy_raw):
        headers = {'content-type': 'application/json'}
        logger.debug('bucket: {0}, decompress_policy request_body: {1}'.format(self.name, decompress_policy_raw))
        response = self.connection.make_request('PUT', self.name, data=decompress_policy_raw,
                                                query_args='decompresspolicy',
                                                headers=headers)
        body = response.read()
        if 200 <= response.status < 300:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_decompress_policy(self):
        response = self.connection.make_request('GET', self.name, query_args='decompresspolicy')
        body = response.read()
        if 200 <= response.status < 300:
            policy = BucketDecompressPolicy.from_json(body)
            response_metadata = ResponseMetadata(status=response.status, reason=response.reason, headers=response.headers)
            policy.response_metadata = response_metadata
            return policy
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_bucket_decompress_policy(self):
        response = self.connection.make_request('DELETE', self.name, query_args='decompresspolicy')
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)
    # 调整名字为 presign，以区分key里的get_presigned_url
    def presign(self, expires_in=3600, method="PUT", key_name=None, conditions=None, headers=None,
                          params=None, expires_in_absolute=False, version_id=None, domain=False):
        """
        生成临时上传链接
        :param conditions: policy 条件组
        :param expires_in: 过期时间 默认为 3600秒
        """
        if conditions is not None:
            _check_conditions(conditions)
        if headers is None:
            headers = {}
        else:
            headers = headers.copy()

        url = self.connection.generate_url(expires_in, method, bucket=self.name, key=key_name,
                                           headers=headers, params=params,
                                           expires_in_absolute=expires_in_absolute, version_id=version_id,
                                           conditions=conditions)
        if domain is True:
            url = url.replace('http://' + self.name + '.', 'http://')
            url = url.replace('https://' + self.name + '.', 'https://')

        return url

    def create_share_code(self, auth_code=None, expires_in=86400, prefix=None):
        """
        生成授权码的临时访问token
        :param auth_code: 授权码，6位数字或者字母的组合
        :param expires_in: 过期时间 默认为 1天
        :param prefix: 要分享的前缀
        """
        conditions = [{'bucket': self.name}]

        if auth_code is None:
            raise ValueError('auth_code is required')

        # auth_code应该是字母或者数字的组合，用正则检查
        if not re.match(rb'^[a-zA-Z0-9]{6}$', auth_code):
            raise ValueError('auth_code应该是6位数字或者字母的组合')

        list_params = {}
        if prefix is not None:
            conditions.append(['starts-with', '$key', prefix])
            list_params['prefix'] = prefix

        share_url = self.presign(expires_in, method='GET', params=list_params, conditions=conditions)
        logger.debug('share_url: {0}'.format(share_url))
        shareCryptor = ShareCryptor(auth_code)
        # salt = os.urandom(16)
        share_code = shareCryptor.encrypt(share_url)
        logger.debug('share_code: {0}'.format(share_code))
        return share_code

    def create_share_url(self, auth_code=None, expires_in=86400, prefix=None,
                         share_url_base='https://ks3.console.ksyun.com/doc-share.html?token='):
        """
        生成授权码的临时访问页面链接
        :param auth_code: 授权码
        :param expires_in: 过期时间 默认为 1天
        :param prefix: 要分享的前缀
        :param share_url_base: 分享页的承载地址
        """
        if isinstance(auth_code, int):
            auth_code = str(auth_code)
        if not isinstance(auth_code, bytes):
            auth_code = auth_code.encode('utf-8')
        share_code = self.create_share_code(auth_code=auth_code, expires_in=expires_in,
                                            prefix=prefix)
        share_url = share_url_base + share_code
        return share_url

    def set_bucket_qos(self, bucket_qos):
        headers = {'content-type': 'application/xml'}
        bucket_qos_xml = bucket_qos.to_xml()
        if not isinstance(bucket_qos_xml, bytes):
            bucket_qos_xml = bucket_qos_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(bucket_qos_xml)
        headers['Content-MD5'] = md5
        logger.debug('bucket: {0}, request_body: {1}'.format(self.name, bucket_qos_xml))
        response = self.connection.make_request('PUT', self.name, data=bucket_qos_xml, query_args='bucketqos',
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_bucket_qos(self):
        response = self.connection.make_request('GET', self.name, query_args='bucketqos')
        body = response.read()
        if response.status == 200:
            bucket_quota = BucketQos(status=response.status, reason=response.reason, headers=response.headers,
                                     raw_body=body)
            h = handler.XmlHandler(bucket_quota, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return bucket_quota
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_bucket_qos(self):
        response = self.connection.make_request('DELETE', self.name, query_args='bucketqos')
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def set_requester_qos(self, requester_qos):
        headers = {'content-type': 'application/xml'}
        requester_qos_xml = requester_qos.to_xml()
        if not isinstance(requester_qos_xml, bytes):
            requester_qos_xml = requester_qos_xml.encode('utf-8')
        md5 = ks3.utils.compute_base64_md5_digest(requester_qos_xml)
        headers['Content-MD5'] = md5
        logger.debug('bucket: {0}, request_body: {1}'.format(self.name, requester_qos_xml))
        response = self.connection.make_request('PUT', self.name, data=requester_qos_xml, query_args='requesterqos',
                                                headers=headers)
        body = response.read()
        if response.status == 200:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def get_requester_qos(self):
        response = self.connection.make_request('GET', self.name, query_args='requesterqos')
        body = response.read()
        if response.status == 200:
            bucket_quota = RequesterQos(status=response.status, reason=response.reason, headers=response.headers,
                                        raw_body=body)
            h = handler.XmlHandler(bucket_quota, self)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            xml.sax.parseString(body, h)
            return bucket_quota
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_requester_qos(self):
        response = self.connection.make_request('DELETE', self.name, query_args='requesterqos')
        body = response.read()
        if response.status == 204:
            return ResponseResult(None, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)


class BucketLocation(object):
    def __init__(self, *args, **kwargs):
        self.location = ''

        self.response_metadata = ResponseMetadata(**kwargs)

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, current_text, connection):
        if name == 'LocationConstraint':
            self.location = current_text
