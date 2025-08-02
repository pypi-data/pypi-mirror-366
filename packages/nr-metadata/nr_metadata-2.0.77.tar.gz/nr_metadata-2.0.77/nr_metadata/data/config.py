from nr_metadata.data.records.api import DataRecord
from nr_metadata.data.resources.records.config import DataResourceConfig
from nr_metadata.data.resources.records.resource import DataResource
from nr_metadata.data.services.records.config import DataServiceConfig
from nr_metadata.data.services.records.service import DataService

DATA_RECORD_RESOURCE_CONFIG = DataResourceConfig


DATA_RECORD_RESOURCE_CLASS = DataResource


DATA_RECORD_SERVICE_CONFIG = DataServiceConfig


DATA_RECORD_SERVICE_CLASS = DataService


OAREPO_PRIMARY_RECORD_SERVICE = {DataRecord: "data"}
