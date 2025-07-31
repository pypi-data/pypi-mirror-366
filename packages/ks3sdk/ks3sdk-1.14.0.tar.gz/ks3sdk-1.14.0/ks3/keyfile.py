# Copyright 2013 Google Inc.
# Copyright 2011, Nexenta Systems Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
Wrapper class to expose a Key being read via a partial implementaiton of the
Python file interface. The only functions supported are those needed for seeking
in a Key open for reading.
"""


class KeyFile:

    def __init__(self, key, start_offset=0, limit_size=None, headers=None):
        if key.etag is None:
            key = key.bucket.get_key(key.name, validate=True)
        self.location = 0
        self.key = key
        self.closed = False
        self.mode = 'r'
        self.name = key.name

        self.start_offset = start_offset
        self.limit_size = limit_size
        self.size = limit_size if limit_size is not None else key.size - start_offset
        self.headers = headers

    @property
    def crc(self):
        return self.key.client_crc

    def tell(self):
        return self.location

    def read(self, size):
        self.open_read()
        s = self.key.read(size)
        if not s:
            self.close()
            return s
        self.location += len(s)
        return s

    def open_read(self):
        if self.key.resp is not None:
            return
        end_offset = '' if self.limit_size is None else self.limit_size + self.start_offset - 1
        headers = {'Range': 'bytes={0}-{1}'.format(self.start_offset, end_offset)}
        if self.headers is not None:
            headers.update(self.headers)
        self.key.open_read(headers=headers)

    def close(self):
        self.key.close()
        self.closed = True

    # Non-file interface, useful for code that wants to dig into underlying Key
    # state.
    def getkey(self):
        return self.key
