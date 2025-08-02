from oarepo_runtime.services.results import RecordItem, RecordList


class DataRecordItem(RecordItem):
    """DataRecord record item."""

    components = [*RecordItem.components]


class DataRecordList(RecordList):
    """DataRecord record list."""

    components = [*RecordList.components]
