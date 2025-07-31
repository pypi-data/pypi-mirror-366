# coding:utf-8
import logging
import time
import re
import os

from requests.adapters import DEFAULT_POOLBLOCK
from requests import Request
from urllib3 import poolmanager

from ks3 import utils
from requests.adapters import HTTPAdapter
from ks3.utils import get_default_user_agent

try:
    import http.client as httpcli  # for Python 3
    import urllib.parse as parse
    from urllib import parse as urlparse
except ImportError:
    print('python@2.x no longer supported by ks3sdk@2.x, please refer to ks3sdk@1.x for python@2.x support')

from ks3.auth import canonical_string, add_auth_header, url_encode, encode
from ks3.authV4 import add_auth_header as add_auth_header_v4

logger = logging.getLogger(__name__)


class CallingFormat:
    PATH = 1
    SUBDOMAIN = 2
    VANITY = 3


class AuthingFormat:
    V2 = 1
    V4 = 2


def merge_meta(headers, metadata):
    final_headers = headers.copy()
    for k in list(metadata.keys()):
        final_headers["x-kss-" + "meta-" + k] = metadata[k]

    return final_headers


def query_args_hash_to_string(query_args):
    pairs = []
    for k, v in list(query_args.items()):
        piece = k
        if v is not None:
            piece += "=%s" % parse.quote_plus(str(v).encode('utf-8'))
            # piece += "=%s" % v
        pairs.append(piece)

    return '&'.join(pairs)


# TODO: 删除
def get_object_url(age, bucket="", key="", secret_access_key="", access_key_id="", query_args={}):
    expire = str(int(time.time()) + age)
    headers = {"Date": expire}
    c_string = canonical_string("GET", bucket, key, query_args, headers)
    path = c_string.split("\n")[-1]

    signature = parse.quote_plus(encode(secret_access_key, c_string))
    if "?" in path:
        url = "http://kss.ksyun.com%s&Expires=%s&AccessKeyId=%s&Signature=%s" % \
              (path, expire, access_key_id, signature)
    else:
        url = "http://kss.ksyun.com%s?Expires=%s&AccessKeyId=%s&Signature=%s" % \
              (path, expire, access_key_id, signature)
    return url


def get_proxy_url(scheme, host, port, proxy_username, proxy_password):
    if host is None:
        return None
    if port is None:
        address = host
    else:
        address = '{0}:{1}'.format(host, port)
    if proxy_username is not None and proxy_password is not None:
        proxy_auth = '{0}:{1}@'.format(proxy_username, proxy_password)
    else:
        proxy_auth = ''
    return {scheme: 'http://{0}{1}'.format(proxy_auth, address)}


def do_request(session, method, url, headers=None, data=None, proxy=None, timeout=10):
    headers = headers or {}
    data = data or {}
    proxy = proxy or {}

    req = Request(
        method=method.upper(),
        url=url,
        headers=headers,
        data=data,
    )
    prep = session.prepare_request(req)
    prep.headers.update(headers)
    stream = True
    verify = True
    settings = session.merge_environment_settings(
        prep.url, proxy, stream, verify, None
    )
    send_kwargs = {
        "timeout": timeout,
        "allow_redirects": False,
    }
    send_kwargs.update(settings)
    resp = session.send(prep, **send_kwargs)
    resp = KS3Response(resp)
    return resp


def make_request(server, port, access_key_id, access_key_secret, bucket="", key="", query_args=None, headers=None,
                 data="", metadata=None, method="PUT", calling_format=None, is_secure=False,
                 domain_mode=False, need_auth_header=True, timeout=10, ua_addon='', proxy_host=None,
                 proxy_port=None, proxy_username=None, proxy_password=None, session=None):
    if not headers:
        headers = {}
    # if not query_args:
    #    query_args = {}
    if not metadata:
        metadata = {}

    if bucket and not domain_mode:
        server = calling_format.get_bucket_server(server, bucket)
    path = calling_format.build_path_base(bucket, key)
    # path += "/%s" % url_encode(key)
    # path = path.replace('//', '/%2F')

    if query_args:
        if isinstance(query_args, dict):
            path += "?" + query_args_hash_to_string(query_args)
        else:
            path += "?" + query_args

    host = "%s:%d" % (server, port)

    headers['User-Agent'] = get_default_user_agent() + ' ' + ua_addon
    final_headers = merge_meta(headers, metadata)
    if method == "PUT" and "Content-Length" not in final_headers and not data:
        final_headers["Content-Length"] = "0"
    if method.upper() == "POST" and "Content-Length" not in final_headers and not data:
        final_headers["Content-Length"] = str(len(data))
    if need_auth_header:
        add_auth_header(access_key_id, access_key_secret, final_headers, method,
                        bucket, key, query_args)
    final_headers['Accept-Encoding'] = 'identity'
    logger.info('send [{method}] request, host: {host}, port: {port}, path: {path}, headers: {headers}'
                .format(method=method, host=host, port=port, path=path, headers=final_headers))

    scheme = 'https' if is_secure else 'http'
    proxy = get_proxy_url(scheme, proxy_host, proxy_port, proxy_username, proxy_password)

    resp = do_request(
        session=session,
        method=method,
        url='{scheme}://{host}{path}'.format(scheme=scheme, host=host, path=path),
        headers=final_headers,
        data=data,
        proxy=proxy,
        timeout=timeout
    )

    logger.info(
        'complete [{method}] request, host: {host}, port: {port}, path: {path}, request_id: {request_id}, status_code:{status}'
        .format(
            method=method,
            host=host,
            port=port,
            path=path,
            request_id=resp.getheader('x-kss-request-id') if resp else '',
            status=resp.status,
        )
    )
    if 300 <= resp.status < 400:
        loc = resp.getheader('location')
        if loc:
            reg = re.findall(r'http[s]?://(.*?)(:\d+)?/', loc)
            if reg:
                # 如果返回的是bucket style域名，需要提取region域名出来
                if len(reg[0][0].split('.')) == 4:
                    new_server = reg[0][0].split('.', 1)[1]
                else:
                    new_server = reg[0][0]
                loc_parse = urlparse.urlparse(loc)
                if 'Signature' in loc_parse.query:
                    try:
                        resp_temp = do_request(
                            session=session,
                            method=method,
                            url='{scheme}://{host}{path}'.format(
                                scheme=scheme, host=new_server,
                                path=loc_parse.path + '?' + loc_parse.query
                            ),
                            headers=final_headers,
                            data=data,
                            proxy=proxy,
                            timeout=timeout
                        )
                        return resp_temp
                    except Exception as err:
                        print(str(err))
                else:
                    if hasattr(data, 'read'):
                        data.seek(0, os.SEEK_SET)
                        if isinstance(data, utils.FpAdapter):
                            data.reset_crc_process()
                    return make_request(new_server, port, access_key_id, access_key_secret, bucket, key, query_args,
                                        headers, data, metadata, method=method, calling_format=calling_format,
                                        is_secure=is_secure, domain_mode=domain_mode,
                                        need_auth_header=True, timeout=timeout, ua_addon=ua_addon,
                                        proxy_host=proxy_host, proxy_port=proxy_port, session=session)
    return resp


# 发送awsv4的请求
def make_request_v4(access_key_id, access_key_secret, method='', service='', region='', query_args=None, headers={},
                    body="", is_secure=False, timeout=10, inner_api=False):
    inner_string = '.inner' if inner_api else ''
    host = service + inner_string + '.api.ksyun.com'

    if (is_secure):
        connection = httpcli.HTTPSConnection(host)
    else:
        connection = httpcli.HTTPConnection(host)
    connection.timeout = timeout

    path = "/"
    if query_args:
        if isinstance(query_args, dict):
            query_args = query_args_hash_to_string(query_args)
    path += "?" + query_args

    headers = add_auth_header_v4(access_key_id, access_key_secret, region, service, host, method, query_args, body,
                                 headers)

    connection.request(method, path, body, headers)
    resp = connection.getresponse()
    return resp


class KS3Response:
    def __init__(self, resp):
        self.raw_resp = resp  # requests.models.Response
        self.status = resp.status_code
        self.headers = self.msg = resp.raw.headers
        self.reason = resp.reason

    def __bool__(self):
        return self.raw_resp is not None

    def getheader(self, name, default=None):
        return self.headers.get(name, default)

    def getheaders(self):
        return self.headers

    def read(self, amt=None):
        # urllib3.response.HTTPResponse.read()
        return self.raw_resp.raw.read(amt)


def repair_pool_key():
    if 'key_blocksize' in poolmanager.PoolKey._fields:
        return
    try:
        key_fields_tuple = poolmanager._key_fields
        key_list = list(key_fields_tuple)
        key_list.append('key_blocksize')
        patched_key_fields = tuple(key_list)

        import collections
        import functools

        PatchedPoolKey = collections.namedtuple("PatchedPoolKey", patched_key_fields)
        poolmanager.PoolKey = PatchedPoolKey
        poolmanager.key_fn_by_scheme = {
            "http": functools.partial(poolmanager._default_key_normalizer, PatchedPoolKey),
            "https": functools.partial(poolmanager._default_key_normalizer, PatchedPoolKey),
        }
    except AttributeError:
        pass


class KS3HTTPAdapter(HTTPAdapter):
    def __init__(self, block_size=8 * 1024, *args, **kwargs):
        self.block_size = block_size

        repair_pool_key()
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs):
        if 'key_blocksize' in poolmanager.PoolKey._fields:
            pool_kwargs['blocksize'] = self.block_size
        super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)
