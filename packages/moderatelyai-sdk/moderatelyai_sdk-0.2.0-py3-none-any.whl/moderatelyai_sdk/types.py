"""Type definitions for the Moderately AI SDK."""

from typing import Any, Dict, List, Literal, Optional, Union

from typing_extensions import TypedDict

# HTTP Method types
HTTPMethod = Literal["GET", "POST", "PATCH", "PUT", "DELETE"]

# JSON serializable types
JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


class APIResponse(TypedDict):
    """Standard API response structure."""

    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    message: Optional[str]


class PaginationInfo(TypedDict):
    """Pagination metadata for list responses."""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next_page: bool
    has_previous_page: bool


class PaginatedResponse(TypedDict):
    """Response structure for paginated endpoints."""

    items: List[Dict[str, Any]]
    pagination: PaginationInfo


class ErrorDetail(TypedDict):
    """Detailed error information for validation errors."""

    field: str
    message: str
    value: Optional[Any]


class APIError(TypedDict):
    """Error response structure."""

    code: str
    message: str
    details: Optional[List[ErrorDetail]]
    path: Optional[str]
    timestamp: Optional[str]
    request_id: Optional[str]


# Resource types based on the API
class User(TypedDict, total=False):
    """User resource type."""

    id: str
    email: str
    name: Optional[str]
    created_at: str
    updated_at: str


class Team(TypedDict, total=False):
    """Team resource type."""

    id: str
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str


class Agent(TypedDict, total=False):
    """Agent resource type."""

    id: str
    name: str
    description: Optional[str]
    team_id: str
    created_at: str
    updated_at: str


class AgentExecution(TypedDict, total=False):
    """Agent execution resource type."""

    id: str
    agent_id: str
    status: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    completed_at: Optional[str]


class Dataset(TypedDict, total=False):
    """Dataset resource type."""

    dataset_id: str  # API uses datasetId, but kept snake_case for SDK consistency
    name: str
    description: Optional[str]
    team_id: str
    record_count: Optional[int]  # Number of records in current data version
    total_size_bytes: Optional[int]  # Total size in bytes
    current_schema_version_id: Optional[str]  # Current schema version ID
    current_data_version_id: Optional[str]  # Current data version ID
    active_data_schema_version_id: Optional[str]  # Active schema version ID
    active_data_version_id: Optional[str]  # Active data version ID
    processing_status: Optional[str]  # Processing status: completed, failed, in_progress, needs-processing
    created_at: str
    updated_at: str


class Pipeline(TypedDict, total=False):
    """Pipeline resource type."""

    id: str
    name: str
    description: Optional[str]
    team_id: str
    status: Optional[str]
    config: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    last_run_at: Optional[str]


class File(TypedDict, total=False):
    """File resource type."""

    id: str
    name: str
    original_name: Optional[str]
    team_id: str
    dataset_id: Optional[str]
    size: Optional[int]
    mime_type: Optional[str]
    status: Optional[str]
    upload_url: Optional[str]
    download_url: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
