import base64
import hmac
import logging
import time

from ks3 import utils

try:
    import urllib.parse as parse  # for Python 3
except ImportError:
    import urllib as parse  # for Python 2

try:
    from hashlib import sha1 as sha
    from hashlib import sha256 as sha256
except ImportError:
    import sha

    sha256 = None

logger = logging.getLogger(__name__)

# query string argument of interest
qsa_of_interest = ['acl', 'cors', 'defaultObjectAcl', 'location', 'logging',
                   'partNumber', 'policy', 'requestPayment', 'torrent',
                   'versioning', 'versionId', 'versions', 'website',
                   'uploads', 'uploadId', 'response-content-type',
                   'response-content-language', 'response-expires',
                   'response-cache-control', 'response-content-disposition',
                   'response-content-encoding', 'delete', 'lifecycle',
                   'tagging', 'restore', 'notification', 'thumbnail', 'queryadp',
                   'adp', 'asyntask', 'querytask', 'domain',
                   'storageClass',
                   'websiteConfig',
                   'compose', 'quota', 'crr', 'fetch', 'append', 'position',
                   'mirror', 'retention', 'recycle', 'recover', 'clear', 'inventory',
                   'id', 'x-kss-process', 'encryption', 'accessmonitor', 'decompresspolicy',
                   'migration', 'bucketqos', 'requesterqos']


def url_encode(key):
    if not key:
        return ""
    encode_key = parse.quote(utils.get_utf8_value(key))
    # if '%20' in encode_key:
    #     encode_key = encode_key.replace('%20', '+')

    # if '%2A' in encode_key:
    #     encode_key = encode_key.replace('%2A', '*')

    if '%7E' in encode_key:
        encode_key = encode_key.replace('%7E', '~')

    if '%2F' in encode_key:
        encode_key = encode_key.replace('%2F', '/')

    return encode_key


def encode_params(query_args):
    if not query_args:
        return ""
    map_args = {}
    if isinstance(query_args, dict):
        map_args = query_args
    else:
        for param in query_args.split("&"):
            kv = param.split("=", 1)
            k = kv[0]
            if len(kv) == 1:
                map_args[k] = ""
            else:
                v = kv[1]
                map_args[k] = v
    if not map_args:
        return ""
    sorted_keys = list(map_args.keys())
    sorted_keys.sort()
    buf_list = []
    for k in sorted_keys:
        if k in qsa_of_interest:
            v = map_args.get(k)
            if v:
                buf_list.append("%s=%s" % (k, v))
            else:
                buf_list.append("%s" % k)
    return "&".join(buf_list)


def canonical_resource(bucket, key, query_args):
    buf = "/"
    if bucket:
        buf += "%s/" % bucket
    if key:
        buf += "%s" % url_encode(key)

    buf = buf.replace('//', '/%2F')
    params = encode_params(query_args)
    if params:
        buf += "?%s" % params
    return buf


def canonical_headers(headers):
    if not headers:
        return ""
    interesting_headers = {}
    for header_key in headers:
        lk = header_key.lower()
        if lk.startswith("x-kss-"):
            interesting_headers[lk] = headers[header_key]
    if not interesting_headers:
        return ""
    sorted_header_keys = list(interesting_headers.keys())
    sorted_header_keys.sort()
    buf_list = []
    for header_key in sorted_header_keys:
        buf_list.append("%s:%s" % (header_key, interesting_headers.get(header_key)))
    return "\n".join(buf_list)


def canonical_string(method, bucket="", key="", query_args=None, headers=None, expires=None, policy=None):
    if policy:
        return policy_canonical_string(bucket, expires, policy)
    if not headers:
        headers = {}
    if not query_args:
        query_args = ""

    can_resource = canonical_resource(bucket, key, query_args)
    can_headers = canonical_headers(headers)
    content_md5 = ""
    content_type = ""
    date = ""
    for header_key in headers:
        lk = header_key.lower()
        val = headers.get(header_key)
        if not val:
            continue
        if lk == "content-md5":
            content_md5 = val
        elif lk == "content-type":
            content_type = val
        elif lk == "date":
            date = val
    if expires:
        date = str(expires)
    sign_list = [method, content_md5, content_type, date]
    if can_headers:
        sign_list.append(can_headers)
    sign_list.append(can_resource)
    sign_str = "\n".join(sign_list)
    logger.debug('sign_list: {0}'.format(sign_list))
    return sign_str

def format_policy_param(policy):
    return "X-Kss-Policy={0}".format(policy)

def policy_canonical_string(bucket, expires, policy):
    sign_str = "{0}\n/{1}/?{2}".format(expires, bucket, format_policy_param(policy))
    logger.debug('sign_str: {0}'.format(sign_str))
    return sign_str

def encode(secret_access_key, str_to_encode, urlencode=False):
    secret_access_key = secret_access_key.encode('utf-8')
    str_to_encode = str_to_encode.encode('utf-8')
    b64_hmac = base64.b64encode(hmac.new(secret_access_key, str_to_encode, sha).digest()).strip().decode('utf-8')
    if urlencode:
        return parse.quote_plus(b64_hmac)
    else:
        return b64_hmac


def add_auth_header(access_key_id, secret_access_key, headers, method, bucket, key, query_args):
    if not access_key_id:
        return
    if 'Date' not in headers:
        from email.utils import formatdate
        headers['Date'] = formatdate(time.time(), usegmt=True)

    c_string = canonical_string(method, bucket, key, query_args, headers)
    c_string_encoded = encode(secret_access_key, c_string)
    logger.debug('c_string_encoded: {0}'.format(c_string_encoded))
    headers['Authorization'] = \
        "%s %s:%s" % ("KSS", access_key_id, c_string_encoded)
