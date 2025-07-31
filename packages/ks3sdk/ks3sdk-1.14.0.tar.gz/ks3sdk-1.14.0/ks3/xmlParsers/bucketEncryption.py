from ks3.responseResult import ResponseMetadata

"""
<ServerSideEncryptionConfiguration>
    <Rule>
        <ApplyServerSideEncryptionByDefault>
            <SSEAlgorithm>AES256</SSEAlgorithm>
        </ApplyServerSideEncryptionByDefault>
    </Rule>
</ServerSideEncryptionConfiguration>
"""


class BucketEncryption(object):

    def __init__(self, algorithm=None, *args, **kwargs):
        self.algorithm = algorithm

        self.response_metadata = ResponseMetadata(**kwargs)

    def startElement(self, name, value, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'SSEAlgorithm':
            self.algorithm = value

    def to_xml(self):
        s = '<ServerSideEncryptionConfiguration>' \
            '<Rule>' \
            '<ApplyServerSideEncryptionByDefault>'

        if self.algorithm is not None:
            s += '<SSEAlgorithm>%s</SSEAlgorithm>' % self.algorithm
        s += '</ApplyServerSideEncryptionByDefault>' \
             '</Rule>' \
             '</ServerSideEncryptionConfiguration>'
        return s
