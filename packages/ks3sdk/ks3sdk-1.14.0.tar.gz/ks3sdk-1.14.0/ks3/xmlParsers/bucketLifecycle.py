from ks3.tagging import Tag
from ks3.responseResult import ResponseMetadata


class BucketLifecycle(object):
    def __init__(self, rule=None, *args, **kwargs):
        if rule is None:
            self.rule = []
        else:
            self.rule = rule

        self.response_metadata = ResponseMetadata(**kwargs)

    def __repr__(self):
        return "rules: " + str(len(self.rule))

    def startElement(self, name, attrs, connection):
        if name == "Rule":
            self.rule.append(Rule())
            return self.rule[-1]
        return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def to_xml(self):
        s = '<LifecycleConfiguration>'
        if self.rule is not None:
            for r in self.rule:
                s += r.to_xml()
        s += '</LifecycleConfiguration>'
        return s


class Rule(object):
    def __init__(self, id=None, filter=None, status=None, expiration=None, transitions=None,
                 noncurrent_version_expiration=None,
                 noncurrent_version_transition=None, abort_incomplete_multipart_upload=None):
        self.id = id
        self.filter = filter
        self.status = status
        self.expiration = expiration
        self.noncurrent_version_expiration = noncurrent_version_expiration
        self.noncurrent_version_transition = noncurrent_version_transition
        self.abort_incomplete_multipart_upload = abort_incomplete_multipart_upload
        if transitions is None:
            self.transitions = []
        else:
            self.transitions = transitions

    def startElement(self, name, attrs, connection):
        if name == 'Expiration':
            self.expiration = Expiration()
            return self.expiration
        if name == 'Filter':
            self.filter = Filter()
            return self.filter
        if name == 'Transition':
            self.transitions.append(Transition())
            return self.transitions[-1]
        if name == 'AbortIncompleteMultipartUpload':
            self.abort_incomplete_multipart_upload = AbortIncompleteMultipartUpload()
        if name == 'NoncurrentVersionTransition':
            self.noncurrent_version_transition = NoncurrentVersionTransition()
            return self.noncurrent_version_transition
        if name == 'NoncurrentVersionExpiration':
            self.noncurrent_version_expiration = NoncurrentVersionExpiration()
            return self.noncurrent_version_expiration
        return None

    def endElement(self, name, value, connection):
        if name == 'ID':
            self.id = value
        elif name == 'Status':
            self.status = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<Rule>'
        if self.id is not None:
            s += '<ID>%s</ID>' % self.id
        if self.status is not None:
            s += '<Status>%s</Status>' % self.status
        if self.filter is not None:
            s += self.filter.to_xml()
        if self.expiration is not None:
            s += self.expiration.to_xml()
        if self.transitions is not None:
            for t in self.transitions:
                s += t.to_xml()
        if self.abort_incomplete_multipart_upload is not None:
            s += self.abort_incomplete_multipart_upload.to_xml()
        if self.noncurrent_version_expiration is not None:
            s += self.noncurrent_version_expiration.to_xml()
        if self.noncurrent_version_transition is not None:
            s += self.noncurrent_version_transition.to_xml()
        s += '</Rule>'
        return s


class Filter(object):
    def __init__(self, prefix=None, tags=None):
        self.prefix = prefix
        if tags is None:
            self.tags = []
        else:
            self.tags = tags

    def startElement(self, name, attrs, connection):
        if name == "Tag":
            self.tags.append(Tag())
            return self.tags[-1]
        return None

    def endElement(self, name, value, connection):
        if name == 'Prefix':
            self.prefix = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<Filter>'
        if len(self.tags) != 0:
            s += '<And>'

        if self.prefix is not None:
            s += '<Prefix>%s</Prefix>' % self.prefix

        if len(self.tags) != 0:
            for tag in self.tags:
                s += tag.to_xml()
            s += '</And>'
        s += '</Filter>'
        return s


class Transition(object):
    def __init__(self, days=None, date=None, storage_class=None, is_access_time=None, return_to_std_when_visit=None):
        self.days = days
        self.storage_class = storage_class
        self.date = date
        self.is_access_time = is_access_time
        self.return_to_std_when_visit = return_to_std_when_visit

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Days':
            self.days = value
        elif name == 'StorageClass':
            self.storage_class = value
        elif name == 'Date':
            self.date = value
        elif name == 'IsAccessTime':
            self.is_access_time = value
        elif name == 'ReturnToStdWhenVisit':
            self.return_to_std_when_visit = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<Transition>'
        if self.days is not None:
            s += '<Days>%s</Days>' % self.days
        if self.date is not None:
            s += '<Date>%s</Date>' % self.date
        if self.storage_class is not None:
            s += '<StorageClass>%s</StorageClass>' % self.storage_class
        if self.is_access_time is not None:
            s += '<IsAccessTime>%s</IsAccessTime>' % self.is_access_time
        if self.return_to_std_when_visit is not None:
            s += '<ReturnToStdWhenVisit>%s</ReturnToStdWhenVisit>' % self.return_to_std_when_visit
        s += '</Transition>'
        return s


class Expiration(object):
    def __init__(self, days=None, date=None):
        self.days = days
        self.date = date

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Days':
            self.days = value
        elif name == 'Date':
            self.date = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<Expiration>'
        if self.days is not None:
            s += '<Days>%s</Days>' % self.days
        if self.date is not None:
            s += '<Date>%s</Date>' % self.date
        s += '</Expiration>'
        return s


class NoncurrentVersionTransition(object):
    def __init__(self, noncurrent_days=None, storage_class=None):
        self.noncurrent_days = noncurrent_days
        self.storage_class = storage_class

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'StorageClass':
            self.storage_class = value
        elif name == 'NoncurrentDays':
            self.noncurrent_days = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<NoncurrentVersionTransition>'
        if self.storage_class is not None:
            s += '<StorageClass>%s</StorageClass>' % self.storage_class
        if self.noncurrent_days is not None:
            s += '<NoncurrentDays>%s</NoncurrentDays>' % self.noncurrent_days
        s += '</NoncurrentVersionTransition>'
        return s


class NoncurrentVersionExpiration(object):
    def __init__(self, noncurrent_days=None):
        self.noncurrent_days = noncurrent_days

    def to_xml(self):
        s = '<NoncurrentVersionExpiration>'
        if self.noncurrent_days is not None:
            s += '<NoncurrentDays>%s</NoncurrentDays>' % self.noncurrent_days
        s += '</NoncurrentVersionExpiration>'
        return s


class AbortIncompleteMultipartUpload(object):
    def __init__(self, days_after_initiation=None, date=None):
        self.days_after_initiation = days_after_initiation
        self.date = date

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'DaysAfterInitiation':
            self.days_after_initiation = value
        elif name == 'Date':
            self.date = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<AbortIncompleteMultipartUpload>'
        if self.days_after_initiation is not None:
            s += '<DaysAfterInitiation>%s</DaysAfterInitiation>' % self.days_after_initiation
        if self.date is not None:
            s += '<Date>%s</Date>' % self.date
        s += '</AbortIncompleteMultipartUpload>'
        return s
