from ks3.responseResult import ResponseMetadata


class BucketRetention(object):

    def __init__(self, rule=None, *args, **kwargs):
        self.rule = rule

        self.response_metadata = ResponseMetadata(**kwargs)

    def startElement(self, name, attrs, connection):
        if name == 'Rule':
            self.rule = Rule()
            return self.rule
        return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def to_xml(self):
        s = u'<RetentionConfiguration>'
        if self.rule is not None:
            s += self.rule.to_xml()
        s += '</RetentionConfiguration>'
        return s


class Rule(object):
    ENABLED = 'Enabled'
    DISABLED = 'Disabled'

    def __init__(self, status=None, days=-1):
        self.status = status
        self.days = days

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == "Status":
            self.status = value
        if name == "Days":
            self.days = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = u'<Rule>'
        if self.status is not None:
            s += '<Status>%s</Status>' % self.status
        if self.days is not None:
            s += '<Days>%s</Days>' % self.days
        s += '</Rule>'
        return s
