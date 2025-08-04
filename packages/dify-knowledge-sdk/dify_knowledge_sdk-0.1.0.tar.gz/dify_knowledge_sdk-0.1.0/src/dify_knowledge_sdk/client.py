import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient
from .models import (
    CreateDatasetRequest,
    Dataset,
    DocumentResponse,
    IndexingStatusResponse,
    Metadata,
    MetadataListResponse,
    PaginatedResponse,
    SegmentResponse,
    SuccessResponse,
)


class DifyDatasetClient(BaseClient):
    """Dify Dataset API client for knowledge base management."""

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai", timeout: float = 30.0):
        """
        Initialize the Dify Dataset client.

        Args:
            api_key: Dify API key
            base_url: Base URL for Dify API (default: https://api.dify.ai)
            timeout: Request timeout in seconds (default: 30.0)
        """
        super().__init__(api_key, base_url, timeout)

    # Dataset management methods
    def create_dataset(self, name: str, permission: str = "only_me", description: Optional[str] = None) -> Dataset:
        """
        Create an empty dataset.

        Args:
            name: Dataset name
            permission: Dataset permission (default: "only_me")
            description: Dataset description

        Returns:
            Created dataset information
        """
        request = CreateDatasetRequest(name=name, permission=permission, description=description)
        response = self.post("/v1/datasets", json=request.model_dump(exclude_none=True))
        return Dataset(**response)

    def list_datasets(self, page: int = 1, limit: int = 20) -> PaginatedResponse:
        """
        Get list of datasets.

        Args:
            page: Page number (default: 1)
            limit: Items per page (default: 20)

        Returns:
            Paginated list of datasets
        """
        params = {"page": page, "limit": limit}
        response = self.get("/v1/datasets", params=params)
        return PaginatedResponse(**response)

    def delete_dataset(self, dataset_id: str) -> Dict[str, str]:
        """
        Delete a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            Success response
        """
        response = self.delete(f"/v1/datasets/{dataset_id}")
        return response

    # Document management methods
    def create_document_by_text(
        self,
        dataset_id: str,
        name: str,
        text: str,
        indexing_technique: str = "high_quality",
        process_rule_mode: str = "automatic",
        process_rule_config: Optional[Dict[str, Any]] = None,
    ) -> DocumentResponse:
        """
        Create a document from text.

        Args:
            dataset_id: Dataset ID
            name: Document name
            text: Document text content
            indexing_technique: Indexing technique (default: "high_quality")
            process_rule_mode: Process rule mode (default: "automatic")
            process_rule_config: Custom process rule configuration

        Returns:
            Created document information
        """
        process_rule = {"mode": process_rule_mode}
        if process_rule_config:
            process_rule.update(process_rule_config)

        request_data = {"name": name, "text": text, "indexing_technique": indexing_technique, "process_rule": process_rule}

        response = self.post(f"/v1/datasets/{dataset_id}/document/create_by_text", json=request_data)
        return DocumentResponse(**response)

    def create_document_by_file(
        self,
        dataset_id: str,
        file_path: Union[str, Path],
        indexing_technique: str = "high_quality",
        process_rule_mode: str = "automatic",
        process_rule_config: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
    ) -> DocumentResponse:
        """
        Create a document from file.

        Args:
            dataset_id: Dataset ID
            file_path: Path to the file
            indexing_technique: Indexing technique (default: "high_quality")
            process_rule_mode: Process rule mode (default: "automatic")
            process_rule_config: Custom process rule configuration
            name: Custom document name (default: use filename)

        Returns:
            Created document information
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        process_rule = {"mode": process_rule_mode}
        if process_rule_config:
            process_rule.update(process_rule_config)

        # Create JSON data payload exactly as shown in official docs
        data_payload = {
            "indexing_technique": indexing_technique,
            "process_rule": process_rule
        }
        if name:
            data_payload["name"] = name

        json_string = json.dumps(data_payload, separators=(',', ':'))  # Compact JSON like curl

        with open(file_path, "rb") as file:
            files = {
                "file": (file_path.name, file, "application/octet-stream"),
                "data": ('', json_string, "text/plain")
            }

            response = self.post(f"/v1/datasets/{dataset_id}/document/create_by_file", files=files)
            return DocumentResponse(**response)

    def list_documents(self, dataset_id: str, page: int = 1, limit: int = 20) -> PaginatedResponse:
        """
        Get list of documents in a dataset.

        Args:
            dataset_id: Dataset ID
            page: Page number (default: 1)
            limit: Items per page (default: 20)

        Returns:
            Paginated list of documents
        """
        params = {"page": page, "limit": limit}
        response = self.get(f"/v1/datasets/{dataset_id}/documents", params=params)
        return PaginatedResponse(**response)

    def update_document_by_text(self, dataset_id: str, document_id: str, name: str, text: str) -> DocumentResponse:
        """
        Update a document with text.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            name: Updated document name
            text: Updated document text

        Returns:
            Updated document information
        """
        request_data = {"name": name, "text": text}
        response = self.post(f"/v1/datasets/{dataset_id}/documents/{document_id}/update_by_text", json=request_data)
        return DocumentResponse(**response)

    def update_document_by_file(
        self,
        dataset_id: str,
        document_id: str,
        file_path: Union[str, Path],
        name: Optional[str] = None,
        indexing_technique: str = "high_quality",
        process_rule_mode: str = "automatic",
        process_rule_config: Optional[Dict[str, Any]] = None,
    ) -> DocumentResponse:
        """
        Update a document with file.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            file_path: Path to the file
            name: Updated document name
            indexing_technique: Indexing technique (default: "high_quality")
            process_rule_mode: Process rule mode (default: "automatic")
            process_rule_config: Custom process rule configuration

        Returns:
            Updated document information
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        process_rule = {"mode": process_rule_mode}
        if process_rule_config:
            process_rule.update(process_rule_config)

        # Create JSON data payload exactly as shown in official docs
        data_payload = {
            "indexing_technique": indexing_technique,
            "process_rule": process_rule
        }
        if name:
            data_payload["name"] = name

        json_string = json.dumps(data_payload, separators=(',', ':'))  # Compact JSON like curl

        with open(file_path, "rb") as file:
            files = {
                "file": (file_path.name, file, "application/octet-stream"),
                "data": ('', json_string, "text/plain")  # Use empty string instead of None
            }

            response = self.post(f"/v1/datasets/{dataset_id}/documents/{document_id}/update_by_file", files=files)
            return DocumentResponse(**response)

    def delete_document(self, dataset_id: str, document_id: str) -> SuccessResponse:
        """
        Delete a document.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID

        Returns:
            Success response
        """
        response = self.delete(f"/v1/datasets/{dataset_id}/documents/{document_id}")
        return SuccessResponse(**response)

    def get_document_indexing_status(self, dataset_id: str, batch: str) -> IndexingStatusResponse:
        """
        Get document indexing status.

        Args:
            dataset_id: Dataset ID
            batch: Batch ID from document creation

        Returns:
            Indexing status information
        """
        response = self.get(f"/v1/datasets/{dataset_id}/documents/{batch}/indexing-status")
        return IndexingStatusResponse(**response)

    # Segment management methods
    def create_segments(self, dataset_id: str, document_id: str, segments: List[Dict[str, Any]]) -> SegmentResponse:
        """
        Create segments for a document.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segments: List of segment data

        Returns:
            Created segments information
        """
        request_data = {"segments": segments}
        response = self.post(f"/v1/datasets/{dataset_id}/documents/{document_id}/segments", json=request_data)
        return SegmentResponse(**response)

    def list_segments(self, dataset_id: str, document_id: str) -> SegmentResponse:
        """
        Get list of segments in a document.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID

        Returns:
            List of segments
        """
        response = self.get(f"/v1/datasets/{dataset_id}/documents/{document_id}/segments")
        return SegmentResponse(**response)

    def update_segment(self, dataset_id: str, document_id: str, segment_id: str, segment_data: Dict[str, Any]) -> SegmentResponse:
        """
        Update a segment.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segment_id: Segment ID
            segment_data: Updated segment data

        Returns:
            Updated segment information
        """
        request_data = {"segment": segment_data}
        response = self.post(f"/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}", json=request_data)
        return SegmentResponse(**response)

    def delete_segment(self, dataset_id: str, document_id: str, segment_id: str) -> SuccessResponse:
        """
        Delete a segment.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segment_id: Segment ID

        Returns:
            Success response
        """
        response = self.delete(f"/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}")
        return SuccessResponse(**response)

    # Metadata management methods
    def create_metadata_field(self, dataset_id: str, field_type: str, name: str) -> Metadata:
        """
        Create a metadata field for a dataset.

        Args:
            dataset_id: Dataset ID
            field_type: Field type (string, number, time)
            name: Field name

        Returns:
            Created metadata field information
        """
        request_data = {"type": field_type, "name": name}
        response = self.post(f"/v1/datasets/{dataset_id}/metadata", json=request_data)
        return Metadata(**response)

    def update_metadata_field(self, dataset_id: str, metadata_id: str, name: str) -> Metadata:
        """
        Update a metadata field.

        Args:
            dataset_id: Dataset ID
            metadata_id: Metadata field ID
            name: Updated field name

        Returns:
            Updated metadata field information
        """
        request_data = {"name": name}
        response = self.patch(f"/v1/datasets/{dataset_id}/metadata/{metadata_id}", json=request_data)
        return Metadata(**response)

    def delete_metadata_field(self, dataset_id: str, metadata_id: str) -> Dict[str, str]:
        """
        Delete a metadata field.

        Args:
            dataset_id: Dataset ID
            metadata_id: Metadata field ID

        Returns:
            Success response
        """
        response = self.delete(f"/v1/datasets/{dataset_id}/metadata/{metadata_id}")
        return response

    def toggle_built_in_metadata_field(self, dataset_id: str, action: str) -> Dict[str, str]:
        """
        Enable or disable built-in metadata fields.

        Args:
            dataset_id: Dataset ID
            action: Action to perform (enable/disable)

        Returns:
            Success response
        """
        response = self.delete(f"/v1/datasets/{dataset_id}/metadata/built-in/{action}")
        return response

    def update_document_metadata(self, dataset_id: str, operation_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Update document metadata values.

        Args:
            dataset_id: Dataset ID
            operation_data: List of document metadata operations

        Returns:
            Success response
        """
        request_data = {"operation_data": operation_data}
        response = self.post(f"/v1/datasets/{dataset_id}/documents/metadata", json=request_data)
        return response

    def list_metadata_fields(self, dataset_id: str) -> MetadataListResponse:
        """
        Get list of metadata fields for a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            List of metadata fields
        """
        response = self.get(f"/v1/datasets/{dataset_id}/metadata")
        return MetadataListResponse(**response)
