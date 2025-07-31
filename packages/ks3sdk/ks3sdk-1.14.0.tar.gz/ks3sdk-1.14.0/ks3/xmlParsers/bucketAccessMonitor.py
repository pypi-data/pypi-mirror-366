from ks3.responseResult import ResponseMetadata

"""
<AccessMonitorConfiguration>
  <Status>Enabled</Status>
</AccessMonitorConfiguration>
"""


class BucketAccessMonitor(object):

    def __init__(self, status=None, *args, **kwargs):
        """
        :param status: Enabled 或者 Disabled
        """
        self.status = status

        self.response_metadata = ResponseMetadata(**kwargs)

    def startElement(self, name, value, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Status':
            self.status = value

    def to_xml(self):
        s = '<AccessMonitorConfiguration>' \

        if self.status is not None:
            s += '<Status>%s</Status>' % self.status
        s += '</AccessMonitorConfiguration>'
        return s
