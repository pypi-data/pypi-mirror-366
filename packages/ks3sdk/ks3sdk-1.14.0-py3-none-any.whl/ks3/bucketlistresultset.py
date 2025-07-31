import logging
import time

from ks3.utils import RetryPolicy, ExponentialWait, StopAfterAttempt

try:
    import urllib.parse as parse  # for Python 3
except ImportError:
    import urllib as parse  # for Python 2

logger = logging.getLogger(__name__)


class _BaseListResultSet(object):
    """
    A base class for listing items which can be configured with retry and request interval settings.
    """
    def __init__(self, retry_policy=RetryPolicy(), request_interval=0):
        self.retry_policy = retry_policy
        if retry_policy is None:
            self.retry_policy = RetryPolicy(None, None)
        self.request_interval = request_interval

    def auto_list(self, fn, **params):
        """
        Automatic list using specific methods.

        :param fn: specific method for listing items.
        :param params: parameters for fn.
        """
        more_results = True
        k = None
        cursor_dict = self.init_cursor()
        while more_results:
            params.update(cursor_dict)

            rs = fn(**params)
            # rs = self.retry_policy.call(fn, **params)

            start_time = time.time()
            for k in rs:
                yield k
            cursor_dict = self.update_cursor(rs, k)
            more_results = rs.is_truncated
            if more_results:
                elapsed_time = time.time() - start_time
                if elapsed_time < self.request_interval:
                    time.sleep(self.request_interval - elapsed_time)

    def init_cursor(self):
        """
        Implement this method to initially obtain paging cursor parameters for listing.
        'Paging cursor parameters' such as marker, continuation_token, etc.

        :return: dict[str, str]
        """
        raise NotImplementedError

    def update_cursor(self, rs, k):
        """
        Implement this method to update paging cursor parameters for listing.
        so that the next request can pick up where the previous one left off.

        :param rs: the result set returned by the request.
        :param k: the last key returned by the request.
        :return: dict[str, str]
        """
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


class BucketListResultSet(_BaseListResultSet):
    """
    A result set for listing keys within a bucket.  This transparently handles the results paging from S3
    so even if you have many thousands of keys within the bucket you can iterate over all
    keys in a reasonably efficient manner.
    """

    def __init__(self, bucket=None, prefix='', delimiter='', marker='', max_keys='', encoding_type='',
                 continuation_token='', fetch_owner='', list_type=None, start_after='',
                 retry_policy=RetryPolicy(), request_interval=0):
        super().__init__(retry_policy, request_interval)
        self.bucket = bucket
        self.prefix = prefix
        self.delimiter = delimiter
        self.marker = marker
        self.max_keys = max_keys
        self.encoding_type = encoding_type
        self.continuation_token = continuation_token
        self.fetch_owner = fetch_owner
        self.list_type = list_type
        self.start_after = start_after

    def init_cursor(self):
        return {'marker': self.marker, 'continuation_token': self.continuation_token}

    def update_cursor(self, rs, k):
        marker = ''
        continuation_token = ''
        if rs.next_continuation_token:
            continuation_token = rs.next_continuation_token
        elif k:
            marker = rs.next_marker or k.name
        if marker:
            marker = parse.unquote(marker)
        return {'marker': marker, 'continuation_token': continuation_token}

    def __iter__(self):
        return self.auto_list(self.bucket.get_all_keys, retry_policy=self.retry_policy, prefix=self.prefix, delimiter=self.delimiter,
                              max_keys=self.max_keys, encoding_type=self.encoding_type,
                              fetch_owner=self.fetch_owner, list_type=self.list_type, start_after=self.start_after)


class VersionedBucketListResultSet(_BaseListResultSet):
    """
    A result set for listing versions within a bucket. This transparently handles the results paging from S3
    so even if you have many thousands of keys within the bucket you can iterate over all
    keys in a reasonably efficient manner.
    """

    def __init__(self, bucket=None, prefix='', delimiter='', key_marker='', version_id_marker='', headers=None,
                 encoding_type=None, retry_policy=RetryPolicy(),
                 request_interval=0):
        super().__init__(retry_policy, request_interval)
        self.bucket = bucket
        self.prefix = prefix
        self.delimiter = delimiter
        self.key_marker = key_marker
        self.version_id_marker = version_id_marker
        self.headers = headers
        self.encoding_type = encoding_type

    def init_cursor(self):
        return {'key_marker': self.key_marker}

    def update_cursor(self, rs, k):
        key_marker = rs.next_key_marker
        if key_marker:
            key_marker = parse.unquote(key_marker)
        return {'key_marker': key_marker}

    def __iter__(self):
        return self.auto_list(self.bucket.get_all_versions, prefix=self.prefix, delimiter=self.delimiter,
                              key_marker=self.key_marker, version_id_marker=self.version_id_marker,
                              headers=self.headers, encoding_type=self.encoding_type)


class BucketRetentionListResultSet(_BaseListResultSet):
    def __init__(self, bucket=None, prefix='', delimiter='', marker='', max_keys='',
                 retry_policy=RetryPolicy(), request_interval=0):
        super().__init__(retry_policy, request_interval)
        self.bucket = bucket
        self.prefix = prefix
        self.delimiter = delimiter
        self.marker = marker
        self.max_keys = max_keys

    def init_cursor(self):
        return {'marker': self.marker}

    def update_cursor(self, rs, k):
        marker = ''
        if k:
            marker = rs.next_marker or k.name
        if marker:
            marker = parse.unquote(marker)
        return {'marker': marker}

    def __iter__(self):
        return self.auto_list(self.bucket.get_all_retention_keys, prefix=self.prefix, delimiter=self.delimiter,
                              marker=self.marker, max_keys=self.max_keys)


class MultiPartUploadListResultSet(_BaseListResultSet):
    """
    A result set for listing multipart uploads within a bucket.
    This transparently handles the results paging from S3 so even if you have
    many thousands of uploads within the bucket you can iterate over all
    keys in a reasonably efficient manner.
    """

    def __init__(self, bucket=None, key_marker='', upload_id_marker='', prefix='', delimiter='', max_uploads=None,
                 headers=None, encoding_type=None,
                 retry_policy=RetryPolicy(), request_interval=0):
        super().__init__(retry_policy, request_interval)
        self.bucket = bucket
        self.key_marker = key_marker
        self.upload_id_marker = upload_id_marker
        self.prefix = prefix
        self.delimiter = delimiter
        self.max_uploads = max_uploads
        self.headers = headers
        self.encoding_type = encoding_type

    def init_cursor(self):
        return {'key_marker': self.key_marker, 'upload_id_marker': self.upload_id_marker}

    def update_cursor(self, rs, k):
        return {'key_marker': rs.next_key_marker, 'upload_id_marker': rs.next_upload_id_marker}

    def __iter__(self):
        return self.auto_list(self.bucket.get_all_multipart_uploads, key_marker=self.key_marker,
                              upload_id_marker=self.upload_id_marker, headers=self.headers,
                              encoding_type=self.encoding_type, prefix=self.prefix, delimiter=self.delimiter,
                              max_uploads=self.max_uploads)
