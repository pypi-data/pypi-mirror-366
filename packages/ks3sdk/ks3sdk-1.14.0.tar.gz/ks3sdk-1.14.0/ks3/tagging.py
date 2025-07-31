from ks3.responseResult import ResponseMetadata


class Tagging(object):
    def __init__(self, tagging_set=None, *args, **kwargs):
        if tagging_set is None:
            self.tagging_set = []
        else:
            self.tagging_set = tagging_set

        self.response_metadata = ResponseMetadata(**kwargs)

    def __repr__(self):
        s = "tagging "
        for tag in self.tagging_set:
            s += tag.key + ':' + (lambda x: ['', tag.value][tag.value is not None])(tag.value) + ' '
        return s

    def startElement(self, name, attrs, connection):
        if name == 'Tag':
            self.tagging_set.append(Tag())
            return self.tagging_set[-1]
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def to_xml(self):
        s = '<?xml version="1.0" encoding="UTF-8"?>'
        s += '<Tagging>'
        if self.tagging_set is not None:
            s += '<TagSet>'
            for tag in self.tagging_set:
                s += tag.to_xml()
            s += '</TagSet>'
        s += '</Tagging>'
        return s


class Tag(object):
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Key':
            self.key = value
        elif name == 'Value':
            self.value = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<Tag>'
        if self.key is not None:
            s += '<Key>%s</Key>' % self.key
        if self.value is not None:
            s += '<Value>%s</Value>' % self.value
        s += '</Tag>'
        return s
