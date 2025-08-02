from oarepo_runtime.services.results import RecordItem, RecordList


class DataciteRecordItem(RecordItem):
    """DataciteRecord record item."""

    components = [*RecordItem.components]


class DataciteRecordList(RecordList):
    """DataciteRecord record list."""

    components = [*RecordList.components]
