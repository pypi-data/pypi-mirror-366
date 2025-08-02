from oarepo_runtime.services.results import RecordItem, RecordList


class DocumentsRecordItem(RecordItem):
    """DocumentsRecord record item."""

    components = [*RecordItem.components]


class DocumentsRecordList(RecordList):
    """DocumentsRecord record list."""

    components = [*RecordList.components]
