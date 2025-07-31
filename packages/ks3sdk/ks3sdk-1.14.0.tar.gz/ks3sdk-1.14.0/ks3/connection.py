# coding:utf-8
import base64
import json
import logging
import os
import time
import xml.sax

import requests

from ks3 import auth
from ks3 import handler
from ks3 import utils
from ks3.auth import url_encode, format_policy_param
from ks3.bucket import Bucket, BucketLocation
from ks3.exception import S3ResponseError, S3CreateError, KS3ClientError, ParamValidationError
from ks3.http import make_request
from ks3.http import KS3HTTPAdapter
from ks3.provider import Provider
from ks3.responseResult import ResponseResult
from ks3.resultset import ResultSet
from ks3.utils import Ks3DnsResolver, RetryPolicy

logger = logging.getLogger(__name__)

try:
    import urllib.parse as parse  # for Python 3
except ImportError:
    import urllib as parse  # for Python 2

dns_resolver = Ks3DnsResolver()


def check_lowercase_bucketname(n):
    """
    Bucket names must not contain uppercase characters. We check for
    this by appending a lowercase character and testing with islower().
    Note this also covers cases like numeric bucket names with dashes.

    >>> check_lowercase_bucketname("Aaaa")
    Traceback (most recent call last):
    ...
    BotoClientError: S3Error: Bucket names cannot contain upper-case
    characters when using either the sub-domain or virtual hosting calling
    format.

    >>> check_lowercase_bucketname("1234-5678-9123")
    True
    >>> check_lowercase_bucketname("abcdefg1234")
    True
    """
    if not (n + 'a').islower():
        raise KS3ClientError("Bucket names cannot contain upper-case " \
                             "characters when using either the sub-domain or virtual " \
                             "hosting calling format.")
    return True


class _CallingFormat(object):

    def get_bucket_server(self, server, bucket):
        return ''

    def build_url_base(self, connection, protocol, server, bucket, key=''):
        url_base = '%s://' % protocol
        url_base += self.build_host(server, bucket)
        url_base += connection.get_path(self.build_path_base(bucket, key))
        return url_base

    def build_host(self, server, bucket):
        if bucket == '':
            return server
        else:
            return self.get_bucket_server(server, bucket)

    def build_auth_path(self, bucket, key=''):
        key = utils.get_utf8_value(key)
        path = ''
        if bucket != '':
            path = '/' + bucket
        buf = path + '/%s' % parse.quote(key)
        buf = buf.replace('//', '/%2F')
        return buf

    def build_path_base(self, bucket, key=''):
        buf = '/%s' % url_encode(key)
        buf = buf.replace('//', '/%2F')
        return buf


class PathCallingFormat(_CallingFormat):

    def get_bucket_server(self, server, bucket):
        return server

    def build_path_base(self, bucket, key=''):
        path_base = '/'
        if bucket:
            path_base += "%s/" % bucket
        path_base += url_encode(key)
        path_base = path_base.replace('//', '/%2F')
        return path_base


class SubdomainCallingFormat(_CallingFormat):

    def get_bucket_server(self, server, bucket):
        return '%s.%s' % (bucket, server)


# 习惯上倾向于称之为VirtualHostCallingFormat，故添加此别名类
class VirtualHostCallingFormat(SubdomainCallingFormat):
    pass


def _format_policy(expiration=None, conditions=[]):
  # if not expiration:
  #   raise ValueError("expiration must be set")
  policy = {
    'conditions': conditions
  }
  if expiration:
    policy['expiration'] = expiration

  logger.debug("policy: %s" % (policy))
  return policy


class Connection(object):
    QueryString = 'Signature=%s&Expires=%d&KSSAccessKeyId=%s'

    def __init__(self, access_key_id, access_key_secret, host="",
                 port=80, provider='kss', security_token=None, profile_name=None, path='/',
                 is_secure=False, debug=0, calling_format=VirtualHostCallingFormat(), domain_mode=False,
                 local_encrypt=False, local_key_path="", timeout=10, ua_addon='', enable_crc=True, block_size=8192,
                 proxy_host=None, proxy_port=None, proxy_username=None, proxy_password=None, connection_pool_size=1024,
                 dns_cache_time=30, retry_policy=RetryPolicy(), need_auth_header=True):
        """
        :param access_key_id: 金山云提供的ACCESS KEY ID
        :param access_key_secret: 金山云提供的SECRET KEY ID
        :param host: 请参考官网API文档说明中的Region定义(https://docs.ksyun.com/read/latest/65/_book/index.html)
        :param port: 请求端口，默认80
        :param is_secure: 是否启用HTTPS，True:启用  False:关闭
        :param domain_mode: 是否使用自定义域名访问，True:是 False:否
        :param local_encrypt: 是否启用本地加密， True:是 False:否，默认False，如选是，需要配置本地密钥路径
        :param enable_crc: 是否启用crc64校验，True:是 False:否，默认True
        :param block_size: 发送请求时，从本地读数据或者向服务器发数据的数据块大小
        """
        if host is None or host.strip() == '':
            raise ParamValidationError("host cannot be blank")

        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.is_secure = is_secure
        self.host = host
        self.port = port
        self.debug = debug
        self.path = path
        self.calling_format = calling_format
        self.domain_mode = domain_mode
        self.local_encrypt = local_encrypt
        self.key = ""
        self.timeout = timeout
        self.block_size = block_size
        self.ua_addon = ua_addon
        self.enable_crc = enable_crc
        self.need_auth_header = need_auth_header
        if self.is_secure:
            self.protocol = 'https'
            if self.port == 80:
                self.port = 443
        else:
            self.protocol = 'http'

        if isinstance(provider, Provider):
            # Allow overriding Provider
            self.provider = provider
        else:
            self._provider_type = provider
            self.provider = Provider(self._provider_type,
                                     access_key_id,
                                     access_key_secret,
                                     security_token,
                                     profile_name)

        # Allow config file to override default host, port, and host header.
        if self.provider.host:
            self.host = self.provider.host
        if self.provider.port:
            self.port = self.provider.port
        if self.provider.host_header:
            self.host_header = self.provider.host_header
        if self.local_encrypt:
            self.load_key(local_key_path)
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password

        self.session = requests.Session()
        adapter_kwargs = {
            'pool_connections': connection_pool_size,
            'pool_maxsize': connection_pool_size,
            'max_retries': 0,
            'block_size': block_size,
        }
        self.session.mount('http://', KS3HTTPAdapter(**adapter_kwargs))
        self.session.mount('https://', KS3HTTPAdapter(**adapter_kwargs))

        if dns_cache_time > 0 and dns_cache_time is not None:
            dns_resolver.ttl = dns_cache_time
            dns_resolver.open_cache()
        self.retry_policy = retry_policy

    def load_key(self, path):
        error_msg = "In local_encrypt mode, we need you to indicate the location of your private key. Set value for 'local_key_path' while initiate connection."
        assert path, error_msg
        with open(path, 'rb') as ak_file:
            assert os.path.getsize(path), "The key file should not be empty"
            content = ak_file.read()
            assert len(content.strip()) == 16, "The key's length should be 16"
            self.key = content.strip()

    def make_request(
            self, method, bucket="", key="", data="",
            headers=None, query_args=None, metadata=None, timeout=10,
            retry_policy=None,  # 兼容list方法的重试策略
    ):
        if not headers:
            headers = {}
        if not query_args:
            query_args = {}
        if not metadata:
            metadata = {}
        timeout = self.timeout

        request_kwargs = {
            'server': self.host,
            'port': self.port,
            'access_key_id': self.access_key_id,
            'access_key_secret': self.access_key_secret,
            'bucket': bucket,
            'key': key,
            'query_args': query_args,
            'headers': headers,
            'data': data,
            'metadata': metadata,
            'method': method,
            'is_secure': self.is_secure,
            'domain_mode': self.domain_mode,
            'timeout': timeout,
            'ua_addon': self.ua_addon,
            'proxy_host': self.proxy_host,
            'proxy_port': self.proxy_port,
            'proxy_username': self.proxy_username,
            'proxy_password': self.proxy_password,
            'calling_format': self.calling_format,
            'session': self.session,
            'need_auth_header': self.need_auth_header,
        }
        if retry_policy is None:
            retry_policy = self.retry_policy
        if retry_policy is not None:
            resp = retry_policy.call(
                make_request,
                **request_kwargs
            )
        else:
            resp = make_request(**request_kwargs)

        return resp

    def get_all_buckets(self, headers=None, project_ids=None,
                        region=None, prefix=None, visit_type=None, storage_type=None):
        query_args = {}
        if project_ids is not None:
            query_args = {
                "projectIds": project_ids
            }
        response = self.make_request('GET', headers=headers, query_args=query_args)
        body = response.read()
        if response.status > 300:
            raise S3ResponseError(response.status, response.reason, body)
        result = ResultSet(marker_elem=[('Bucket', Bucket)], status=response.status, reason=response.reason,
                           headers=response.headers, raw_body=body)
        h = handler.XmlHandler(result, self)
        if not isinstance(body, bytes):
            body = body.encode('utf-8')
        xml.sax.parseString(body, h)

        # 按条件过滤
        if region is not None:
            new_result = list(filter(lambda b: b.region == region, result))
            result.clear()
            result.extend(new_result)
        if prefix is not None:
            new_result = list(filter(lambda b: b.name.startswith(prefix), result))
            result.clear()
            result.extend(new_result)
        if visit_type is not None:
            new_result = list(filter(lambda b: b.VisitType == visit_type, result))
            result.clear()
            result.extend(new_result)
        if storage_type is not None:
            new_result = list(filter(lambda b: b.type == storage_type, result))
            result.clear()
            result.extend(new_result)

        return result

    def get_bucket(self, bucket_name, headers=None):
        return Bucket(self, bucket_name)

    def head_bucket(self, bucket_name, headers=None):
        response = self.make_request('HEAD', bucket_name)
        body = response.read()
        if response.status == 200:
            return ResponseResult(response.headers, status=response.status, reason=response.reason,
                                  headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, None,
                                  request_id=response.getheader('x-kss-request-id'))

    def get_bucket_location(self, bucket_name):
        response = self.make_request('GET', bucket_name, query_args='location')
        body = response.read()
        if response.status == 200:
            loc = BucketLocation(status=response.status, reason=response.reason, headers=response.headers,
                                 raw_body=body)
            h = handler.XmlHandler(loc, self)
            xml.sax.parseString(body, h)
            return loc
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def create_bucket(self, bucket_name, headers=None, project_id=None,
                      location=None, policy=None):
        check_lowercase_bucketname(bucket_name)

        if policy:
            if headers:
                headers[self.provider.acl_header] = policy
            else:
                headers = {self.provider.acl_header: policy}
        if location is None:
            data = ''
        else:
            data = '<CreateBucketConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><LocationConstraint>' + \
                   location + '</LocationConstraint></CreateBucketConfiguration>'

        query_args = {}
        if project_id is not None:
            query_args = {
                "projectId": project_id
            }
        response = self.make_request('PUT', bucket_name, headers=headers, query_args=query_args,
                                     data=data)
        body = response.read()
        if response.status == 409:
            raise S3CreateError(response.status, response.reason, body)
        if response.status == 200:
            return Bucket(self, bucket_name, status=response.status, reason=response.reason,
                          headers=response.headers)
        else:
            raise S3ResponseError(response.status, response.reason, body)

    def delete_bucket(self, bucket_name, headers=None):
        """
        Removes an S3 bucket.

        In order to remove the bucket, it must first be empty. If the bucket is
        not empty, an ``S3ResponseError`` will be raised.
        """
        response = self.make_request('DELETE', bucket_name, headers=headers)
        body = response.read()
        if response.status != 204:
            raise S3ResponseError(response.status, response.reason, body)
        return ResponseResult(None, status=response.status, reason=response.reason,
                              headers=response.headers)

    def generate_url(self, expires_in, method, bucket='', key='', headers=None,
                     query_auth=True, force_http=False, response_headers=None, params=None,
                     expires_in_absolute=False, version_id=None, conditions=None):

        headers = headers or {}
        if expires_in_absolute:
          expires = int(expires_in)
        else:
          expires = int(time.time() + expires_in)
        extra_qp = []
        extra_qp_encoded = []
        query_args = None
        if version_id is not None:
          extra_qp.append("versionId=%s" % version_id)

        # response_headers应该被替换为params，
        # 但是为了兼容老版本，暂时保留response_headers
        # params更具备通用性，可以传入更多的参数
        all_params = params or {}
        if response_headers:
          logger.warning("""response_headers is deprecated. Please use params instead.""")
          all_params.update(response_headers)

        policy = None
        if conditions:
          policy = base64.b64encode(
            json.dumps(_format_policy(conditions=conditions)).encode('utf-8')).decode('utf-8')

        if all_params:
          for k, v in list(all_params.items()):
            if v is not None:
              extra_qp.append("%s=%s" % (k, v))
              extra_qp_encoded.append("%s=%s" % (k, parse.quote(str(v))))
            else:
              extra_qp.append("%s" % k)
              extra_qp_encoded.append("%s" % k)

        # 放入到query_args中，用来计算签名
        if extra_qp:
          query_args = '&'.join(extra_qp)

        # if not headers.has_key('Date'):
        #    headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

        c_string = auth.canonical_string(method, bucket, key, query_args=query_args, headers=headers, expires=expires, policy=policy)
        logger.debug('sign_str: {0}'.format(c_string))
        b64_hmac = auth.encode(self.access_key_secret, c_string)
        logger.debug('sign str encoded: {0}'.format(b64_hmac))
        encoded_canonical = parse.quote(b64_hmac, safe='')
        if query_auth:
          encode_ak = self.access_key_id
          # encode_ak = parse.quote(self.access_key_id)
          # print 'encode_ak:%s'%encode_ak
          query_part = '?' + self.QueryString % (encoded_canonical, expires, encode_ak)
          if policy:
            query_part += '&%s' % format_policy_param(policy)
        else:
          query_part = ''

        # 这段代码现在没有用
        if headers:
          hdr_prefix = self.provider.header_prefix
          for k, v in list(headers.items()):
            if k.startswith(hdr_prefix):
              # headers used for sig generation must be
              # included in the url also.
              extra_qp.append("%s=%s" % (k, parse.quote(v)))
        if extra_qp_encoded:
          delimiter = '?' if not query_part else '&'
          query_part += delimiter + '&'.join(extra_qp_encoded)
        if force_http:
          protocol = 'http'
          port = 80
        else:
          protocol = self.protocol
          port = self.port
        return self.calling_format.build_url_base(self, protocol,
                                                  self.server_name(port),
                                                  bucket, key) + query_part

    def server_name(self, port=None):
        if not port:
            port = self.port
        if port == 80:
            signature_host = self.host
        else:
            signature_host = "%s:%s" % (self.host, port)
        return signature_host

    def get_path(self, path='/'):
        # The default behavior is to suppress consecutive slashes for reasons
        # discussed at
        # https://groups.google.com/forum/#!topic/boto-dev/-ft0XPUy0y8
        # You can override that behavior with the suppress_consec_slashes param.
        pos = path.find('?')
        if pos >= 0:
            params = path[pos:]
            path = path[:pos]
        else:
            params = None
        if path[-1] == '/':
            need_trailing = True
        else:
            need_trailing = False
        path_elements = self.path.split('/')
        path_elements.extend(path.split('/'))
        path_elements = [p for p in path_elements if p]
        path = '/' + '/'.join(path_elements)
        if path[-1] != '/' and need_trailing:
            path += '/'
        if params:
            path = path + params
        return path

    def get_adp(self, task_id):
        query_args = 'queryadp'
        response = self.make_request('GET', task_id, query_args=query_args)
        body = response.read()
        if response.status != 200:
          raise S3ResponseError(response.status, response.reason, body)
        return ResponseResult(body, status=response.status, reason=response.reason,
                              headers=response.headers)