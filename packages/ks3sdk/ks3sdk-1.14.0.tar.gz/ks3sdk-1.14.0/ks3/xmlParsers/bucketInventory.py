from ks3.responseResult import ResponseMetadata


class BucketInventory(object):
    OPTIONAL_FIELD_SIZE = 'Size'
    OPTIONAL_FIELD_LAST_MODIFIED_DATE = 'LastModifiedDate'
    OPTIONAL_FIELD_ETAG = 'ETag'
    OPTIONAL_FIELD_STORAGE_CLASS = 'StorageClass'
    OPTIONAL_FIELD_IS_MULTIPART_UPLOADED = 'IsMultipartUploaded'
    OPTIONAL_FIELD_ENCRYPTION_STATUS = 'EncryptionStatus'

    def __init__(self, id=None, is_enabled=None, filter=None, destination=None, schedule=None,
                 optional_fields=None, *args, **kwargs):
        if optional_fields is None:
            optional_fields = []
        self.id = id
        self.is_enabled = 'true' if is_enabled else 'false'
        self.filter = filter
        self.destination = destination
        self.schedule = schedule
        self.optional_fields = optional_fields

        self.response_metadata = ResponseMetadata(**kwargs)

    def startElement(self, name, attrs, connection):
        if name == 'Destination':
            self.destination = Destination()
            return self.destination
        if name == 'Schedule':
            self.schedule = Schedule()
            return self.schedule
        if name == 'Filter':
            self.filter = Filter()
            return self.filter
        return None

    def endElement(self, name, value, connection):
        if name == 'Id':
            self.id = value
        if name == 'IsEnabled':
            self.is_enabled = value
        if name == 'Field':
            self.optional_fields.append(value)
        setattr(self, name, value)

    def to_xml(self):
        s = u'<InventoryConfiguration>'
        if self.id is not None:
            s += '<Id>%s</Id>' % self.id
        if self.is_enabled is not None:
            s += '<IsEnabled>%s</IsEnabled>' % self.is_enabled
        if self.destination is not None:
            s += '<Destination>%s</Destination>' % self.destination.to_xml()
        if self.schedule is not None:
            s += self.schedule.to_xml()
        if self.filter is not None:
            s += self.filter.to_xml()
        if self.optional_fields is not None:
            s += '<OptionalFields>'
            for i in self.optional_fields:
                s += '<Field>%s</Field>' % i
            s += '</OptionalFields>'
        s += '</InventoryConfiguration>'
        return s


class Destination(object):
    FORMAT_CSV = 'CSV'
    FORMAT_ORC = 'ORC'
    FORMAT_PARQUET = 'Parquet'

    def __init__(self, format=None, account_id=None, bucket=None, prefix=None):
        self.format = format
        self.account_id = account_id
        self.bucket = bucket
        self.prefix = prefix

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Format':
            self.format = value
        if name == 'AccountId':
            self.account_id = value
        if name == 'Bucket':
            self.bucket = value
        if name == 'Prefix':
            self.prefix = value
        setattr(self, name, value)

    def to_xml(self):
        s = u'<KS3BucketDestination>'
        if self.format is not None:
            s += '<Format>%s</Format>' % self.format
        if self.account_id is not None:
            s += '<AccountId>%s</AccountId>' % self.account_id
        if self.bucket is not None:
            s += '<Bucket>%s</Bucket>' % self.bucket
        if self.prefix is not None:
            s += '<Prefix>%s</Prefix>' % self.prefix
        s += '</KS3BucketDestination>'
        return s


class Filter(object):

    def __init__(self, prefix=None, last_modify_begin_time_stamp=None, last_modify_end_time_stamp=None):
        self.prefix = prefix
        self.last_modify_begin_time_stamp = last_modify_begin_time_stamp
        self.last_modify_end_time_stamp = last_modify_end_time_stamp

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Prefix':
            self.prefix = value
        if name == 'LastModifyBeginTimeStamp':
            self.last_modify_begin_time_stamp = value
        if name == 'LastModifyEndTimeStamp':
            self.last_modify_end_time_stamp = value
        setattr(self, name, value)

    def to_xml(self):
        s = u'<Filter>'
        if self.prefix is not None:
            s += '<Prefix>%s</Prefix>' % self.prefix
        if self.last_modify_begin_time_stamp is not None:
            s += '<LastModifyBeginTimeStamp>%s</LastModifyBeginTimeStamp>' % self.last_modify_begin_time_stamp
        if self.last_modify_end_time_stamp is not None:
            s += '<LastModifyEndTimeStamp>%s</LastModifyEndTimeStamp>' % self.last_modify_end_time_stamp
        s += '</Filter>'
        return s


class Schedule(object):
    ONCE = 'Once'
    WEEKLY = 'Weekly'

    def __init__(self, frequency=None):
        self.frequency = frequency

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Frequency':
            self.frequency = value
        setattr(self, name, value)

    def to_xml(self):
        s = u'<Schedule>'
        if self.frequency is not None:
            s += '<Frequency>%s</Frequency>' % self.frequency
        s += '</Schedule>'
        return s


class ListInventoryConfigurationsResult(object):
    def __init__(self, **kwargs):
        self.inventory_configurations = []

        self.response_metadata = ResponseMetadata(**kwargs)

    def startElement(self, name, attrs, connection):
        if name == 'InventoryConfiguration':
            self.inventory_configurations.append(BucketInventory())
            return self.inventory_configurations[-1]
        return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)
