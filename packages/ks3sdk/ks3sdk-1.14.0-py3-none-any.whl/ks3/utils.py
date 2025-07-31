"""
Some handy utility functions used by several classes.
"""
import abc
import logging
import os
import pickle
import random
import socket
import threading
import time
import sys
from concurrent.futures import ThreadPoolExecutor, Future

import crcmod
import errno

from urllib3.util import connection
from urllib3.util.connection import allowed_gai_family, _set_socket_options

import ks3
import six
import io
import base64

from hashlib import md5

from ks3.compat import encodebytes
from ks3.crc64_combine import mkCombineFun
from ks3.exception import KS3ClientError

try:
    import urllib.parse as parse  # for Python 3
except ImportError:
    import urllib as parse  # for Python 2

# urllib3.util.connection.create_connection
_orig_create_connection = connection.create_connection


logger = logging.getLogger(__name__)


KB = 1024
MB = KB * KB
GB = KB * MB
DEFAULT_PART_SIZE = 100 * MB
MAX_PARTS = 10_000
MAX_SIZE = 5 * GB
MIN_SIZE = 100 * KB


def get_utf8_value(value):
    if not six.PY2 and isinstance(value, bytes):
        return value

    if not isinstance(value, six.string_types):
        value = six.text_type(value)

    if isinstance(value, six.text_type):
        value = value.encode('utf-8')

    return value


def merge_headers_by_name(name, headers):
    """
    Takes a specific header name and a dict of headers {"name": "value"}.
    Returns a string of all header values, comma-separated, that match thepyo
    input header name, case-insensitive.

    """
    matching_headers = find_matching_headers(name, headers)
    return ','.join(str(headers[h]) for h in matching_headers
                    if headers[h] is not None)


def find_matching_headers(name, headers):
    """
    Takes a specific header name and a dict of headers {"name": "value"}.
    Returns a list of matching header names, case-insensitive.

    """
    return [h for h in headers if h.lower() == name.lower()]


def merge_meta(headers, metadata, provider=None):
    if not provider:
        provider = ks3.provider.get_default()
    metadata_prefix = provider.metadata_prefix
    final_headers = headers.copy()
    for k in list(metadata.keys()):
        if k.lower() in ks3.key.Key.base_user_settable_fields:
            final_headers[k] = metadata[k]
        else:
            final_headers[metadata_prefix + k] = metadata[k]

    return final_headers


def compute_md5(fp, buf_size=8192, size=None):
    """
    Compute MD5 hash on passed file and return results in a tuple of values.
    """
    return compute_hash(fp, buf_size, size, hash_algorithm=md5)


def compute_hash(fp, buf_size=8192, size=None, hash_algorithm=md5):
    hash_obj = hash_algorithm()
    spos = fp.tell()
    if size and size < buf_size:
        s = fp.read(size)
    else:
        s = fp.read(buf_size)
    while s:
        if not isinstance(s, bytes):
            s = s.encode('utf-8')
        hash_obj.update(s)
        if size:
            size -= len(s)
            if size <= 0:
                break
        if size and size < buf_size:

            s = fp.read(size)
        else:
            s = fp.read(buf_size)
    hex_digest = hash_obj.hexdigest()
    base64_digest = encodebytes(hash_obj.digest()).decode('utf-8')
    if base64_digest[-1] == '\n':
        base64_digest = base64_digest[0:-1]
    # data_size based on bytes read.
    data_size = fp.tell() - spos
    fp.seek(spos)
    return (hex_digest, base64_digest, data_size)


def compute_encrypted_md5(fp, buf_size=8192, hash_algorithm=md5):
    hash_obj = hash_algorithm()
    s = fp.read(buf_size)
    while s:
        if not isinstance(s, bytes):
            s = s.encode('utf-8')
        hash_obj.update(s)
        s = fp.read(buf_size)
    hex_digest = hash_obj.hexdigest()
    base64_digest = encodebytes(hash_obj.digest()).decode('utf-8')
    if base64_digest[-1] == '\n':
        base64_digest = base64_digest[0:-1]
    # data_size based on bytes read.
    SEEK_SET = getattr(io, 'SEEK_SET', 0)
    fp.seek(SEEK_SET)
    return (hex_digest, base64_digest)


def calculate_string_md5(input_string):
    md5_hash = md5()
    md5_hash.update(input_string.encode('utf-8'))
    hex_md5 = md5_hash.hexdigest()
    return hex_md5


def convert_adp_headers(adps):
    if adps:
        fop = ""
        for op in adps:
            fop = "%s|tag=saveas" % op["command"]
            if op["bucket"]:
                fop += "&bucket=%s" % (op["bucket"])
            if op["key"]:
                fop += "&object=%s" % (base64.b64encode(op["key"]))
            fop = "%s;" % fop
        fop = fop.rstrip(";")
        headers = {"kss-async-process": parse.quote(fop),
                   "kss-notifyurl": parse.quote("http://127.0.0.1:9000/notify/url")}
        return headers
    else:
        return None


def compute_base64_md5_digest(data):
    m = md5()
    m.update(data)
    base64_digest = encodebytes(m.digest()).decode('utf-8')
    if base64_digest[-1] == '\n':
        base64_digest = base64_digest[0:-1]
    return base64_digest


def get_default_user_agent():
    # import platform
    # platform.version()
    # platform.version()
    return 'PythonSDK/' + ks3.__version__


def to_boolean(value, true_value='true'):
    if value == true_value:
        return True
    else:
        return False


def silently_remove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def force_rename(src, dst):
    try:
        os.rename(src, dst)
    except OSError as e:
        if e.errno == errno.EEXIST:
            silently_remove(dst)
            os.rename(src, dst)
        else:
            raise


class Crc64(object):
    _POLY = 0x142F0E1EBA9EA3693
    _XOROUT = 0XFFFFFFFFFFFFFFFF

    def __init__(self, init_crc=0):
        self.crc64 = crcmod.Crc(self._POLY, initCrc=init_crc, rev=True, xorOut=self._XOROUT)

        self.crc64_combineFun = mkCombineFun(self._POLY, initCrc=init_crc, rev=True, xorOut=self._XOROUT)

    def __call__(self, data):
        self.update(data)

    def update(self, data):
        self.crc64.update(data)

    def combine(self, crc1, crc2, len2):
        return self.crc64_combineFun(crc1, crc2, len2)

    @property
    def crc(self):
        return self.crc64.crcValue


def compute_file_crc64(file_name, start=None, end=None, block_size=64 * 1024):
    with open(file_name, 'rb') as fp:
        fp = FpAdapter(fp)
        if start is not None:
            fp.seek(start)
        while True:
            if end is not None:
                if fp.tell() >= end:
                    break
                else:
                    data = fp.read(min(block_size, end - fp.tell() + 1))
            else:
                data = fp.read(block_size)
            if not data:
                break

    return str(fp.crc)


def compute_data_crc64(data, init_crc=0):
    """
    Calculate the crc64 of a string

    :param data: The content of the string
    :param init_crc: The initial value of crc64, default is 0
    :return The crc64 value of the string
    """
    if not isinstance(data, bytes):
        data = data.encode('utf-8')
    crc64 = Crc64(init_crc)
    crc64.update(data)
    return str(crc64.crc)


class FpAdapter(object):
    def __init__(self, fp):
        super(FpAdapter, self).__init__()
        self.fp = fp
        self.crc64_handler = Crc64()
        self.first_read_done = False
        self.counter = 0

    def read(self, size=0):
        try:
            data = self.fp.read(size)
            self.counter += len(data) if data else 0
        except Exception as e:
            raise KS3ClientError('Read file error: fileName:%s, readSize:%d, readOffset: %d, error:%s' % (
                self.fp.name, size, self.counter, e))
        if data and not self.first_read_done:
            self.crc64_handler.update(data)
        else:
            self.first_read_done = True
        return data

    @property
    def crc(self):
        return self.crc64_handler.crc

    @property
    def name(self):
        return self.fp.name

    def reset_crc_process(self):
        self.crc64_handler = Crc64()
        self.first_read_done = False
        self.counter = 0

    def seek(self, *args, **kwargs):
        return self.fp.seek(*args, **kwargs)

    def tell(self, *args, **kwargs):
        return self.fp.tell(*args, **kwargs)

    def close(self):
        self.fp.close()

    def __len__(self):
        total_len = None
        if hasattr(self.fp, '__len__'):
            total_len = len(self.fp)
        elif hasattr(self.fp, 'fileno'):
            try:
                total_len = os.fstat(self.fp.fileno()).st_size
            except (io.UnsupportedOperation, AttributeError):
                pass
        if total_len is None:
            current_pos = self.tell()
            self.seek(0, io.SEEK_END)
            total_len = self.tell()
            self.seek(current_pos)
        return total_len or 0

    def __bool__(self):
        return bool(self.fp)

    def __str__(self):
        return str(self.fp)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# return if client_crc == server_crc
def check_crc(client_crc, server_crc):
    if client_crc is None or server_crc is None:
        return True
    return client_crc is not None and server_crc is not None and client_crc == server_crc


class ChunkIO(io.FileIO):
    def __init__(self, filename, start_offset, limit_size):
        super(ChunkIO, self).__init__(filename, 'rb')
        self.start_offset = start_offset
        self.limit_size = limit_size
        self.seek(0)

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            super(ChunkIO, self).seek(self.start_offset + offset)
        elif whence == io.SEEK_CUR:
            self.seek(self.tell() + offset)
        elif whence == io.SEEK_END:
            self.seek(self.limit_size + offset)

    def read(self, size=-1):
        current_pos = self.tell()
        if current_pos >= self.limit_size:
            return b''
        if size == -1 or current_pos + size > self.limit_size:
            size = self.limit_size - current_pos
        return super(ChunkIO, self).read(size)

    def tell(self):
        return super(ChunkIO, self).tell() - self.start_offset


class ResumeRecordManager(object):

    def __init__(self, filename):
        self.filename = filename
        self.record = None
        self.__lock = threading.Lock()

    def load(self):
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, 'rb') as f:
                record = pickle.load(f)
        except ValueError:
            os.remove(self.filename)
        else:
            self.record = record

    def save(self):
        with self.__lock:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.record, f)

    def delete(self):
        silently_remove(self.filename)
        self.record = None


class BlockThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers, *args, **kwargs):
        super().__init__(max_workers=max_workers, *args, **kwargs)
        self.__semaphore = threading.Semaphore(max_workers)

    def submit(self, fn, *args, **kwargs) -> Future:
        self.__semaphore.acquire()
        future = super().submit(fn, *args, **kwargs)

        def release_semaphore():
            self.__semaphore.release()

        future.add_done_callback(lambda _: release_semaphore())
        return future


class RetryState:
    def __init__(self):
        self.attempt_number = 1
        self.start_time = time.time()
        self.exception = None
        self.result = None

    def prepare_for_next_attempt(self):
        self.attempt_number += 1

    @property
    def seconds_since_start(self):
        return time.time() - self.start_time

    def set_exception(self, exception):
        self.exception = exception

    def set_result(self, result):
        self.result = result


class BaseWait(abc.ABC):
    @abc.abstractmethod
    def __call__(self, retry_state):
        """
        return: 等待时间，单位为秒
        """
        pass

    def __add__(self, other):
        """
        :param other: BaseWait
        return: CombineWait
        """
        return CombineWait(self, other)

    def __radd__(self, other):
        """
        支持wait策略进行加运算，wait1 + wait2
        
        :param other: BaseWait
        :return: Union['CombineWait', 'BaseWait']
        """
        if other == 0:
            return self
        return self.__add__(other)


class CombineWait(BaseWait):
    """Combine several waiting strategies."""

    def __init__(self, *waits: BaseWait):
        self.waits = waits

    def __call__(self, retry_state):
        return sum(wait(retry_state=retry_state) for wait in self.waits)


class NeverWait(BaseWait):
    def __call__(self, retry_state):
        return 0


class ExponentialWait(BaseWait):
    """指数增加时间的等待策略"""

    def __init__(self, multiplier=1.5, min_interval=1, max_interval=10):
        self.multiplier = multiplier
        self.min_interval = min_interval
        self.max_interval = max_interval

    def __call__(self, retry_state):
        wait_time = self.multiplier * (2 ** (retry_state.attempt_number - 1))
        wait_time = max(self.min_interval, min(wait_time, self.max_interval))
        return wait_time


class FixedWait(BaseWait):
    """固定时间的等待策略"""

    def __init__(self, fixed_interval=2):
        self.fixed_interval = fixed_interval

    def __call__(self, retry_state):
        return self.fixed_interval


class LinearWait(BaseWait):
    """线性增加时间的等待策略"""

    def __init__(self, start=1, increment=1, max_interval=10):
        self.start = start
        self.increment = increment
        self.max_interval = max_interval

    def __call__(self, retry_state):
        wait_time = self.start + (self.increment * (retry_state.attempt_number - 1))
        return max(0, min(wait_time, self.max_interval))


class JitterWait(BaseWait):
    """抖动时间的等待策略"""

    def __init__(self, initial=1, jitter=5, max_interval=10):
        self.initial = initial
        self.jitter = jitter
        self.max_interval = max_interval

    def __call__(self, retry_state):
        wait_time = self.initial + (random.uniform(0, self.jitter))
        return min(wait_time, self.max_interval)


class BaseStop(abc.ABC):
    @abc.abstractmethod
    def __call__(self, retry_state):
        """
        :param retry_state: RetryState
        :return: True表示停止重试，False表示继续重试
        """
        pass

    def __and__(self, other):
        """
        支持stop策略进行与运算，stop1 & stop2
        
        :param other: BaseStop
        :return: AllStop
        """
        return AllStop(self, other)

    def __or__(self, other):
        """
        支持stop策略进行或运算，stop1 | stop2
        
        :param other: BaseStop
        :return: AnyStop
        """
        return AnyStop(self, other)


class AnyStop(BaseStop):
    """Stop if any of the stop condition is valid."""

    def __init__(self, *stops):
        """
        :param stops: BaseStop
        """
        self.stops = stops

    def __call__(self, retry_state):
        return any(stop(retry_state) for stop in self.stops)


class AllStop(BaseStop):
    """Stop if all the stop conditions are valid."""

    def __init__(self, *stops):
        """
        :param stops: BaseStop
        """
        self.stops = stops

    def __call__(self, retry_state):
        return all(stop(retry_state) for stop in self.stops)


class NeverStop(BaseStop):
    def __call__(self, retry_state):
        return False


class StopAfterAttempt(BaseStop):
    """在尝试指定次数后停止重试，包括首次调用。"""

    def __init__(self, max_attempts=3):
        self.max_attempts = max_attempts

    def __call__(self, retry_state):
        return retry_state.attempt_number >= self.max_attempts


class StopAfterDelay(BaseStop):
    """在经过指定时间后停止重试，包括首次调用的时间。"""

    def __init__(self, max_delay=10):
        self.max_delay = max_delay

    def __call__(self, retry_state):
        return retry_state.seconds_since_start >= self.max_delay


class StopWhenStatusCodeNotIn(BaseStop):
    """重试特定的HTTP状态码"""

    def __init__(self, status_code_list):
        self.status_code_list = status_code_list

    def __call__(self, retry_state):
        # result为None，表示有异常发生，不停止重试
        if not retry_state.result:
            return False
        return retry_state.result.status not in self.status_code_list


class RetryPolicy:
    DEFAULT_RETRY_STATUS_CODES = [408, 429, 500, 502, 503, 504]

    """重试策略，默认尝试3次，第一次等待1.5秒，第二次等待3秒"""

    def __init__(
            self,
            wait_strategy=ExponentialWait(),
            stop_strategy=StopAfterAttempt(),
            retry_status_codes=None,
    ):
        """
        :param wait_strategy: 等待策略，用于控制两次尝试的间隔时间
        :param stop_strategy: 停止策略，用于控制何时停止重试
        :param retry_status_codes: 除Exception外，哪些HTTP状态码需要重试，如不希望任何的状态码重试，则传入空列表[]
        """
        self.wait_strategy = wait_strategy
        self.stop_strategy = stop_strategy
        # wait_strategy为None时，不等待
        if wait_strategy is None:
            self.wait_strategy = NeverWait()
        # stop_strategy为None时，只尝试一次（不重试）
        if stop_strategy is None:
            self.stop_strategy = StopAfterAttempt(1)
        if retry_status_codes is None:
            retry_status_codes = self.DEFAULT_RETRY_STATUS_CODES
        self.stop_strategy = self.stop_strategy | StopWhenStatusCodeNotIn(retry_status_codes)

    def call(self, fn, **params):
        retry_state = RetryState()
        while True:
            try:
                result = fn(**params)
            except Exception:
                retry_state.set_exception(sys.exc_info())
                logger.warning(retry_state.exception[1])
            else:
                retry_state.set_result(result)

            if self.stop_strategy(retry_state):
                return self._get_result(retry_state)

            wait_interval = self.wait_strategy(retry_state)
            logger.debug('waiting for {} seconds before retrying...'.format(wait_interval))
            time.sleep(wait_interval)
            retry_state.prepare_for_next_attempt()

    @staticmethod
    def _get_result(retry_state):
        if retry_state.result:
            return retry_state.result
        else:
            _, exc_value, exc_traceback = retry_state.exception
            raise exc_value.with_traceback(exc_traceback)


class DnsCacheEntry:
    def __init__(self, host, port, ip_list, expire):
        """
        :param host: 域名
        :param port: 端口
        :param ip_list: socket.getaddrinfo返回的ip列表
        :param expire: 过期时间
        """
        self.host = host
        self.port = port
        self.ip_list = ip_list
        self.expire = expire

    def remove(self, ip_info):
        if len(self.ip_list) == 0:
            return
        try:
            self.ip_list.remove(ip_info)
        except ValueError:
            pass

    def copy_ip_list(self):
        """返回ip列表的快照"""
        return self.ip_list.copy()

    def get_key(self):
        return self.gen_key(self.host, self.port)

    def is_expired(self):
        return int(time.time()) > self.expire

    def __len__(self):
        """
        return: ip_list为None时返回0，否则返回原本长度
        """
        return len(self.ip_list) if self.ip_list else 0

    @staticmethod
    def gen_key(host, port):
        return '{}:{}'.format(host, port)


class Ks3DnsResolver:

    def __init__(self, ttl=30):
        self.cache = {}
        self.ttl = ttl

    def get_cache(self, host, port):
        """
        return: DnsCacheEntry，缓存的ip_list可能为None
                如果没有缓存，则查询dns，缓存后再返回
        """
        key = DnsCacheEntry.gen_key(host, port)
        entry = self.cache.get(key)
        if entry:
            return entry
        else:
            ip_list = self.allowed_getaddrinfo(host, port)
            return self.put(host, port, ip_list, int(time.time()) + self.ttl)

    def refresh_if_needed(self, cache_entry):
        if cache_entry.is_expired():
            host = cache_entry.host
            port = cache_entry.port
            ip_list = self.allowed_getaddrinfo(host, port)
            if ip_list:
                # 覆盖缓存
                cache_entry = self.put(host, port, ip_list, int(time.time()) + self.ttl)
            # ip_list为空，则继续使用原缓存，不覆盖
        return cache_entry

    def put(self, host, port, ip_list, expire):
        key = DnsCacheEntry.gen_key(host, port)
        entry = DnsCacheEntry(host, port, ip_list, expire)
        self.cache[key] = entry
        logger.debug('put cache address:{}'.format(key))
        return entry

    @staticmethod
    def allowed_getaddrinfo(host, port):
        """
        return: 返回ip列表，失败返回None
        """
        try:
            family = allowed_gai_family()
            return socket.getaddrinfo(host, port, family, socket.SOCK_STREAM)
        except:
            return None

    def open_cache(self):

        def create_connection_by_cache(cache_entry, timeout, source_address, socket_options):
            if len(cache_entry) == 0:
                return None
            for res in cache_entry.copy_ip_list():
                af, socktype, proto, canonname, sa = res
                sock = None
                try:
                    sock = socket.socket(af, socktype, proto)
                    _set_socket_options(sock, socket_options)
                    if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                        sock.settimeout(timeout)
                    if source_address:
                        sock.bind(source_address)
                    logger.debug('connecting to cache address: {}'.format(sa))
                    sock.connect(sa)
                    return sock
                except socket.error:
                    # 删除失败的ip信息
                    cache_entry.remove(res)
                    if len(cache_entry) == 0:
                        self.cache.pop(cache_entry.get_key(), None)
                    if sock is not None:
                        sock.close()

            return None

        def patched_create_connection(address,
                                      timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                                      source_address=None,
                                      socket_options=None, ):
            host, port = address
            cache_entry = self.get_cache(host, port)
            cache_entry = self.refresh_if_needed(cache_entry)
            conn = create_connection_by_cache(cache_entry, timeout, source_address, socket_options)
            return conn if conn else _orig_create_connection(address, timeout, source_address, socket_options)

        connection.create_connection = patched_create_connection

