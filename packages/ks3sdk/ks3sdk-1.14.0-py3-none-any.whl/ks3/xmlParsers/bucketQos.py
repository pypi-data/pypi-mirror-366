from ks3.responseResult import ResponseMetadata


class BucketQos:
    def __init__(self, quotas=None, *args, **kwargs):
        self.quotas = [] if quotas is None else quotas

        self.response_metadata = ResponseMetadata(**kwargs)

    def to_xml(self):
        s = '<BucketQosConfiguration>'
        for q in self.quotas:
            s += q.to_xml()
        s += '</BucketQosConfiguration>'
        return s

    def startElement(self, name, attrs, connection):
        if name == "Quota":
            self.quotas.append(Quota())
            return self.quotas[-1]
        return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)


class Quota:
    def __init__(
            self,
            storage_medium=None,
            extranet_upload_bandwidth=None,
            intranet_upload_bandwidth=None,
            extranet_download_bandwidth=None,
            intranet_download_bandwidth=None,
    ):
        self.storage_medium = storage_medium
        self.extranet_upload_bandwidth = extranet_upload_bandwidth
        self.intranet_upload_bandwidth = intranet_upload_bandwidth
        self.extranet_download_bandwidth = extranet_download_bandwidth
        self.intranet_download_bandwidth = intranet_download_bandwidth

    def to_xml(self):
        s = '<Quota>'
        if self.storage_medium is not None:
            s += '<StorageMedium>%s</StorageMedium>' % self.storage_medium
        if self.extranet_upload_bandwidth is not None:
            s += '<ExtranetUploadBandwidth>%s</ExtranetUploadBandwidth>' % self.extranet_upload_bandwidth
        if self.intranet_upload_bandwidth is not None:
            s += '<IntranetUploadBandwidth>%s</IntranetUploadBandwidth>' % self.intranet_upload_bandwidth
        if self.extranet_download_bandwidth is not None:
            s += '<ExtranetDownloadBandwidth>%s</ExtranetDownloadBandwidth>' % self.extranet_download_bandwidth
        if self.intranet_download_bandwidth is not None:
            s += '<IntranetDownloadBandwidth>%s</IntranetDownloadBandwidth>' % self.intranet_download_bandwidth
        s += '</Quota>'
        return s

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'StorageMedium':
            self.storage_medium = value
        elif name == 'ExtranetUploadBandwidth':
            self.extranet_upload_bandwidth = value
        elif name == 'IntranetUploadBandwidth':
            self.intranet_upload_bandwidth = value
        elif name == 'ExtranetDownloadBandwidth':
            self.extranet_download_bandwidth = value
        elif name == 'IntranetDownloadBandwidth':
            self.intranet_download_bandwidth = value
        else:
            setattr(self, name, value)
