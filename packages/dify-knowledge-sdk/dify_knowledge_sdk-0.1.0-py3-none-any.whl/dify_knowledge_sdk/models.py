from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DataSourceInfo(BaseModel):
    upload_file_id: Optional[str] = None


class ProcessRule(BaseModel):
    mode: str
    rules: Optional[Dict[str, Any]] = None


class PreProcessingRule(BaseModel):
    id: str
    enabled: bool


class Segmentation(BaseModel):
    separator: str
    max_tokens: int


class ProcessRuleConfig(BaseModel):
    pre_processing_rules: List[PreProcessingRule]
    segmentation: Segmentation


class Document(BaseModel):
    id: str
    position: int
    data_source_type: str
    data_source_info: Optional[DataSourceInfo] = None
    dataset_process_rule_id: Optional[str] = None
    name: str
    created_from: str
    created_by: str
    created_at: int
    tokens: int
    indexing_status: str
    error: Optional[str] = None
    enabled: bool
    disabled_at: Optional[int] = None
    disabled_by: Optional[str] = None
    archived: bool
    display_status: Optional[str] = None
    word_count: int
    hit_count: int
    doc_form: str


class Dataset(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    provider: Optional[str] = None
    permission: str
    data_source_type: Optional[str] = None
    indexing_technique: Optional[str] = None
    app_count: int
    document_count: int
    word_count: int
    created_by: str
    created_at: int
    updated_by: str
    updated_at: int
    embedding_model: Optional[str] = None
    embedding_model_provider: Optional[str] = None
    embedding_available: Optional[bool] = None


class Segment(BaseModel):
    id: str
    position: int
    document_id: str
    content: str
    answer: Optional[str] = None
    word_count: int
    tokens: int
    keywords: Optional[List[str]] = None
    index_node_id: str
    index_node_hash: str
    hit_count: int
    enabled: bool
    disabled_at: Optional[int] = None
    disabled_by: Optional[str] = None
    status: str
    created_by: str
    created_at: int
    indexing_at: int
    completed_at: Optional[int] = None
    error: Optional[str] = None
    stopped_at: Optional[int] = None


class IndexingStatus(BaseModel):
    id: str
    indexing_status: str
    processing_started_at: Optional[float] = None
    parsing_completed_at: Optional[float] = None
    cleaning_completed_at: Optional[float] = None
    splitting_completed_at: Optional[float] = None
    completed_at: Optional[float] = None
    paused_at: Optional[float] = None
    error: Optional[str] = None
    stopped_at: Optional[float] = None
    completed_segments: int
    total_segments: int


class Metadata(BaseModel):
    id: str
    type: str
    name: str
    use_count: Optional[int] = None


class MetadataValue(BaseModel):
    id: str
    value: str
    name: str


class DocumentMetadata(BaseModel):
    document_id: str
    metadata_list: List[MetadataValue]


class PaginatedResponse(BaseModel):
    data: List[Any]
    has_more: bool
    limit: int
    total: int
    page: int


class CreateDocumentByTextRequest(BaseModel):
    name: str
    text: str
    indexing_technique: str = "high_quality"
    process_rule: ProcessRule


class CreateDocumentByFileRequest(BaseModel):
    indexing_technique: str = "high_quality"
    process_rule: ProcessRule


class CreateDatasetRequest(BaseModel):
    name: str
    permission: str = "only_me"
    description: Optional[str] = None


class UpdateDocumentByTextRequest(BaseModel):
    name: str
    text: str


class CreateSegmentRequest(BaseModel):
    segments: List[Dict[str, Any]]


class UpdateSegmentRequest(BaseModel):
    segment: Dict[str, Any]


class CreateMetadataRequest(BaseModel):
    type: str
    name: str


class UpdateMetadataRequest(BaseModel):
    name: str


class DocumentMetadataRequest(BaseModel):
    operation_data: List[DocumentMetadata]


class DocumentResponse(BaseModel):
    document: Document
    batch: str


class SegmentResponse(BaseModel):
    data: List[Segment]
    doc_form: str


class MetadataListResponse(BaseModel):
    doc_metadata: List[Metadata]
    built_in_field_enabled: bool


class IndexingStatusResponse(BaseModel):
    data: List[IndexingStatus]


class SuccessResponse(BaseModel):
    result: str = "success"
