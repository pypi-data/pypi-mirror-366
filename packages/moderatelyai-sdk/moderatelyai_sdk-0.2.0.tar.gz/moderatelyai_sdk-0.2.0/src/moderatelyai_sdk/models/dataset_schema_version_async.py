"""Async dataset schema version model."""

from typing import Any, Dict, List, Optional

from ._base_async import BaseAsyncModel


class DatasetSchemaVersionAsyncModel(BaseAsyncModel):
    """Async model representing a dataset schema version.
    
    A schema version defines the structure and data types for a dataset.
    This async model provides access to schema metadata and validation functionality.
    """

    @property
    def dataset_schema_version_id(self) -> str:
        """The unique identifier for this schema version."""
        return self._data["datasetSchemaVersionId"]

    @property
    def dataset_id(self) -> str:
        """The ID of the parent dataset."""
        return self._data["datasetId"]

    @property
    def version_no(self) -> int:
        """The schema version number (incremental)."""
        return self._data["versionNo"]

    @property
    def columns(self) -> List[Dict[str, Any]]:
        """The column definitions for this schema."""
        return self._data.get("columns", [])

    @property
    def parsing_config(self) -> Optional[Dict[str, Any]]:
        """Parsing configuration for CSV files."""
        return self._data.get("parsingConfig")

    @property
    def is_current(self) -> bool:
        """Whether this is the current schema version."""
        return self._data.get("isCurrent", False)

    @property
    def created_at(self) -> str:
        """When this schema version was created."""
        return self._data["createdAt"]

    @property
    def updated_at(self) -> str:
        """When this schema version was last updated."""
        return self._data["updatedAt"]

    async def _refresh(self) -> None:
        """Refresh this schema version from the API."""
        fresh_data = await self._client._request(
            method="GET",
            path=f"/dataset-schema-versions/{self.dataset_schema_version_id}",
            cast_type=dict,
        )
        self._data = fresh_data