from ks3.responseResult import ResponseMetadata


class BucketCrossReplicate(object):
    ENABLED = 'Enabled'
    DISABLED = 'Disabled'

    def __init__(self, target_bucket=None, delete_marker_status=None, prefix_list=None,
                 historical_object_replication=None, region=None, *args, **kwargs):
        self.target_bucket = target_bucket
        self.delete_marker_status = delete_marker_status
        self.prefix = prefix_list
        self.historical_object_replication = historical_object_replication
        self.region = region

        self.response_metadata = ResponseMetadata(**kwargs)

    def __repr__(self):
        list_prefix = ''
        if self.prefix is not None:
            for x in self.prefix:
                list_prefix += x
        return "targetBucket " + self.target_bucket \
               + " deleteMarkerStatus " + self.delete_marker_status \
               + " prefix " + list_prefix \
               + " historicalObjectReplication " + self.historical_object_replication \
               + " region " + self.region

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'targetBucket':
            self.target_bucket = value
        elif name == 'DeleteMarkerStatus':
            self.delete_marker_status = value
        elif name == 'HistoricalObjectReplication':
            self.historical_object_replication = value
        elif name == 'region':
            self.region = value
        elif name == 'prefix':
            if self.prefix is None:
                self.prefix = []
            self.prefix.append(value)
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = u'<?xml version="1.0" encoding="UTF-8"?>'
        s += u'<Replication xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
        # s += '<BucketLoggingStatus xmlns="http://ks3.ksyun.com">'
        if self.target_bucket is not None:
            s += '<targetBucket>%s</targetBucket>' % self.target_bucket
        if self.delete_marker_status is not None:
            s += '<DeleteMarkerStatus>%s</DeleteMarkerStatus>' % self.delete_marker_status
        if self.historical_object_replication is not None:
            s += '<HistoricalObjectReplication>%s</HistoricalObjectReplication>' % self.historical_object_replication
        if self.region is not None:
            s += '<region>%s</region>' % self.region
        if self.prefix is not None and len(self.prefix) > 0:
            for x in self.prefix:
                s += '<prefix>%s</prefix>' % x
        s += '</Replication>'
        return s
