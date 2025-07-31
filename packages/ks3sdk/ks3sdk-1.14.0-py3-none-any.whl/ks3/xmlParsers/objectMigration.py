from ks3.responseResult import ResponseMetadata


class MigrationConfiguration:
    def __init__(self, migration_id=None, status=None, migration_failure=None, operation=None, creation_time=None,
                 termination_time=None, *args, **kwargs):
        self.migration_id = migration_id
        self.status = status
        self.migration_failure = migration_failure
        self.operation = operation
        self.creation_time = creation_time
        self.termination_time = termination_time

        self.response_metadata = ResponseMetadata(**kwargs)

    def to_xml(self):
        s = '<MigrationConfiguration>'
        if self.migration_id is not None:
            s += '<Id>%s</Id>' % self.migration_id
        if self.status is not None:
            s += '<Status>%s</Status>' % self.status
        if self.migration_failure is not None:
            s += self.migration_failure.to_xml()
        if self.operation is not None:
            s += self.operation.to_xml()
        if self.creation_time is not None:
            s += '<CreationTime>%s</CreationTime>' % self.creation_time
        if self.termination_time is not None:
            s += '<TerminationTime>%s</TerminationTime>' % self.termination_time
        s += '</MigrationConfiguration>'
        return s

    def startElement(self, name, attrs, connection):
        if name == 'MigrationFailure':
            self.migration_failure = MigrationFailure()
            return self.migration_failure
        elif name == 'Operation':
            self.operation = Operation()
            return self.operation
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'Id':
            self.migration_id = value
        elif name == 'Status':
            self.status = value
        elif name == 'CreationTime':
            self.creation_time = value
        elif name == 'TerminationTime':
            self.termination_time = value
        else:
            setattr(self, name, value)


class MigrationFailure:
    def __init__(self, code=None, reason=None):
        self.code = code
        self.reason = reason

    def to_xml(self):
        s = '<MigrationFailure>'
        if self.code is not None:
            s += '<Code>%s</Code>' % self.code
        if self.reason is not None:
            s += '<Reason>%s</Reason>' % self.reason
        s += '</MigrationFailure>'
        return s

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Code':
            self.code = value
        elif name == 'Reason':
            self.reason = value
        else:
            setattr(self, name, value)


class Operation:
    def __init__(self, migration_source=None, migration_dest=None, storage_class=None):
        self.migration_source = migration_source
        self.migration_dest = migration_dest
        self.storage_class = storage_class

    def to_xml(self):
        s = '<Operation>'
        if self.migration_source is not None:
            s += '<MigrationSource>%s</MigrationSource>' % self.migration_source
        if self.migration_dest is not None:
            s += '<MigrationDest>%s</MigrationDest>' % self.migration_dest
        if self.storage_class is not None:
            s += '<StorageClass>%s</StorageClass>' % self.storage_class
        s += '</Operation>'
        return s

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'MigrationSource':
            self.migration_source = value
        elif name == 'MigrationDest':
            self.migration_dest = value
        elif name == 'StorageClass':
            self.storage_class = value
        else:
            setattr(self, name, value)


class MigrationResult:
    def __init__(self, migration_id=None, *args, **kwargs):
        self.migration_id = migration_id
        self.response_metadata = ResponseMetadata(**kwargs)

    def to_xml(self):
        s = '<MigrationResult>'
        if self.migration_id is not None:
            s += '<Id>%s</Id>' % self.migration_id
        s += '</MigrationResult>'
        return s

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Id':
            self.migration_id = value
        else:
            setattr(self, name, value)