# coding:utf-8

def set_response_func(self, **kwargs):
    self.response_metadata = dict()
    if "headers" in kwargs:
        self.response_metadata["headers"] = kwargs["headers"]
        self.response_metadata["request_id"] = kwargs["headers"].get("x-kss-request-id")
    if "status" in kwargs:
        self.response_metadata["status"] = kwargs["status"]
    if "reason" in kwargs:
        self.response_metadata["reason"] = kwargs["reason"]
    if "raw_body" in kwargs:
        self.response_metadata["raw_body"] = kwargs["raw_body"]


class ResponseResult(object):
    def __init__(self, data, **kwargs):
        self.data = data
        self.response_metadata = ResponseMetadata(**kwargs)

    @property
    def status(self):
        return self.response_metadata.status

    @property
    def headers(self):
        return self.response_metadata.headers

    def getheader(self, item, default=None):
        # 避免使用data里的属性
        # return self.data.getheader(item)
        headers = self.response_metadata.headers.get(item) or default
        if isinstance(headers, str) or not hasattr(headers, '__iter__'):
            return headers
        else:
            return ', '.join(headers)

    @property
    def msg(self):
        return self.headers

    @property
    def request_id(self):
        return self.response_metadata.request_id

    def __repr__(self):
        return 'ResponseResult, status: %s, reason: %s, request_id: %s' % (self.response_metadata.status,
                                                                           self.response_metadata.reason,
                                                                           self.response_metadata.request_id)


class IterableResponseResult(ResponseResult):
    def __iter__(self):
        return iter(self.data)

    def __next__(self):
        return next(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __delitem__(self, index):
        del self.data[index]

    def insert(self, index, value):
        self.data.insert(index, value)


class ResponseMetadata(object):
    def __init__(self, **kwargs):
        self.headers = None
        self.request_id = None
        self.status = None
        self.reason = None
        self.raw_body = None

        if "headers" in kwargs:
            self.headers = kwargs["headers"]
            self.request_id = kwargs["headers"].get("x-kss-request-id")
        if "status" in kwargs:
            self.status = kwargs["status"]
        if "reason" in kwargs:
            self.reason = kwargs["reason"]
        if "raw_body" in kwargs:
            self.raw_body = kwargs["raw_body"]
