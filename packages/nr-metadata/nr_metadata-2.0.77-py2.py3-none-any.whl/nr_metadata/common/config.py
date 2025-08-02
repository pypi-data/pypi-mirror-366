from nr_metadata.common.records.api import CommonRecord
from nr_metadata.common.resources.records.config import CommonResourceConfig
from nr_metadata.common.resources.records.resource import CommonResource
from nr_metadata.common.services.records.config import CommonServiceConfig
from nr_metadata.common.services.records.service import CommonService

COMMON_RECORD_RESOURCE_CONFIG = CommonResourceConfig


COMMON_RECORD_RESOURCE_CLASS = CommonResource


COMMON_RECORD_SERVICE_CONFIG = CommonServiceConfig


COMMON_RECORD_SERVICE_CLASS = CommonService


OAREPO_PRIMARY_RECORD_SERVICE = {CommonRecord: "common"}
