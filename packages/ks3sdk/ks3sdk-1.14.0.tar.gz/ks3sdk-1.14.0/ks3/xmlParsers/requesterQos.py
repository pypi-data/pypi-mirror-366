from ks3.responseResult import ResponseMetadata
from ks3.xmlParsers.bucketQos import Quota


class RequesterQos:
    def __init__(self, rules=None, *args, **kwargs):
        self.rules = [] if rules is None else rules

        self.response_metadata = ResponseMetadata(**kwargs)

    def to_xml(self):
        s = '<RequesterQosConfiguration>'
        for r in self.rules:
            s += r.to_xml()
        s += '</RequesterQosConfiguration>'
        return s

    def startElement(self, name, attrs, connection):
        if name == "Rule":
            self.rules.append(Rule())
            return self.rules[-1]
        return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)


class Rule:
    def __init__(self, user_type=None, krn=None, quotas=None):
        self.user_type = user_type
        self.krn = krn
        self.quotas = [] if quotas is None else quotas

    def to_xml(self):
        s = '<Rule>'
        if self.user_type is not None:
            s += '<UserType>%s</UserType>' % self.user_type
        if self.krn is not None:
            s += '<Krn>%s</Krn>' % self.krn
        for r in self.quotas:
            s += r.to_xml()
        s += '</Rule>'
        return s

    def startElement(self, name, attrs, connection):
        if name == "Quota":
            self.quotas.append(Quota())
            return self.quotas[-1]
        return None

    def endElement(self, name, value, connection):
        if name == "UserType":
            self.user_type = value
        elif name == "Krn":
            self.krn = value
        else:
            setattr(self, name, value)
