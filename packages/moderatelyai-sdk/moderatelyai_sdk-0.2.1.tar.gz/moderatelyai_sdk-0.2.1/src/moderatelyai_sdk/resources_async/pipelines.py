"""Async pipelines resource for the Moderately AI API."""

from typing import Any, Dict, Optional

from ..types import Pipeline, PaginatedResponse
from ._base import AsyncBaseResource


class AsyncPipelines(AsyncBaseResource):
    """Manage pipelines in your teams (async version)."""

    async def list(
        self,
        *,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all pipelines with pagination (async)."""
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        if status is not None:
            query["status"] = status

        return await self._get("/pipelines", options={"query": query})

    async def retrieve(self, pipeline_id: str) -> Pipeline:
        """Retrieve a specific pipeline by ID (async)."""
        return await self._get(f"/pipelines/{pipeline_id}")

    async def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Pipeline:
        """Create a new pipeline (async)."""
        body = {
            "name": name,
            "teamId": self._client.team_id,  # API expects camelCase
            **kwargs,
        }
        if description is not None:
            body["description"] = description
        if config is not None:
            body["config"] = config

        return await self._post("/pipelines", body=body)

    async def update(
        self,
        pipeline_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        **kwargs,
    ) -> Pipeline:
        """Update an existing pipeline (async)."""
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if config is not None:
            body["config"] = config
        if status is not None:
            body["status"] = status

        return await self._patch(f"/pipelines/{pipeline_id}", body=body)

    async def delete(self, pipeline_id: str) -> None:
        """Delete a pipeline (async)."""
        await self._delete(f"/pipelines/{pipeline_id}")

    async def run(self, pipeline_id: str, *, input_data: Optional[Dict[str, Any]] = None) -> Pipeline:
        """Run a pipeline (async)."""
        body = {}
        if input_data is not None:
            body["input_data"] = input_data

        return await self._post(f"/pipelines/{pipeline_id}/run", body=body)
