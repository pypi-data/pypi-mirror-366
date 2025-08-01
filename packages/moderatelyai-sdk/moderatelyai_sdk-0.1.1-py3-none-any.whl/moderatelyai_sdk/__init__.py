"""Moderately AI Python SDK - First-class API client for the Moderately AI platform."""

__version__ = "0.1.1"
__author__ = "Moderately AI"
__email__ = "sdk@moderately.ai"

from ._base_client import RetryConfig
from .client import ModeratelyAI
from .client_async import AsyncModeratelyAI
from .exceptions import (
    APIError,
    AuthenticationError,
    ConflictError,
    ModeratelyAIError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    UnprocessableEntityError,
    ValidationError,
)
from .models import DatasetModel, DatasetDataVersionModel, DatasetSchemaVersionModel, SchemaBuilder, FileModel
from .types import APIResponse

__all__ = [
    # Main clients
    "ModeratelyAI",
    "AsyncModeratelyAI",
    # Configuration
    "RetryConfig",
    # Models
    "DatasetModel",
    "DatasetDataVersionModel", 
    "DatasetSchemaVersionModel",
    "SchemaBuilder",
    "FileModel",
    # Exceptions
    "ModeratelyAIError",
    "APIError",
    "AuthenticationError",
    "ConflictError",
    "NotFoundError",
    "RateLimitError",
    "TimeoutError",
    "UnprocessableEntityError",
    "ValidationError",
    # Types
    "APIResponse",
]
