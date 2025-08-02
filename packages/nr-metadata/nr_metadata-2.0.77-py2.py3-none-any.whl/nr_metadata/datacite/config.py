from nr_metadata.datacite.records.api import DataciteRecord
from nr_metadata.datacite.resources.records.config import DataciteResourceConfig
from nr_metadata.datacite.resources.records.resource import DataciteResource
from nr_metadata.datacite.services.records.config import DataciteServiceConfig
from nr_metadata.datacite.services.records.service import DataciteService

DATACITE_RECORD_RESOURCE_CONFIG = DataciteResourceConfig


DATACITE_RECORD_RESOURCE_CLASS = DataciteResource


DATACITE_RECORD_SERVICE_CONFIG = DataciteServiceConfig


DATACITE_RECORD_SERVICE_CLASS = DataciteService


OAREPO_PRIMARY_RECORD_SERVICE = {DataciteRecord: "datacite"}
