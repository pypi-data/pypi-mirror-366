from oarepo_runtime.services.results import RecordItem, RecordList


class CommonRecordItem(RecordItem):
    """CommonRecord record item."""

    components = [*RecordItem.components]


class CommonRecordList(RecordList):
    """CommonRecord record list."""

    components = [*RecordList.components]
