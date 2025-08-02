from nr_metadata.documents.records.api import DocumentsRecord
from nr_metadata.documents.resources.records.config import DocumentsResourceConfig
from nr_metadata.documents.resources.records.resource import DocumentsResource
from nr_metadata.documents.services.records.config import DocumentsServiceConfig
from nr_metadata.documents.services.records.service import DocumentsService

DOCUMENTS_RECORD_RESOURCE_CONFIG = DocumentsResourceConfig


DOCUMENTS_RECORD_RESOURCE_CLASS = DocumentsResource


DOCUMENTS_RECORD_SERVICE_CONFIG = DocumentsServiceConfig


DOCUMENTS_RECORD_SERVICE_CLASS = DocumentsService


OAREPO_PRIMARY_RECORD_SERVICE = {DocumentsRecord: "documents"}
