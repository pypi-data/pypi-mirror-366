from oarepo_runtime.records.dumpers.edtf_interval import EDTFIntervalDumperExt


class DataEDTFIntervalDumperExt(EDTFIntervalDumperExt):
    """edtf interval dumper."""

    paths = [
        "metadata/dateCollected",
        "metadata/dateCreated",
        "metadata/events/eventDate",
    ]
