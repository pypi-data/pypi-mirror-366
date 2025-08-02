"""Pipelines resource for the Moderately AI API."""

from typing import Any, Dict, Optional

from ..types import PaginatedResponse, Pipeline
from ._base import BaseResource


class Pipelines(BaseResource):
    """Manage data processing pipelines in your teams.

    Examples:
        ```python
        # List all pipelines
        pipelines = client.pipelines.list()

        # Get a specific pipeline
        pipeline = client.pipelines.retrieve("pipeline_123")

        # Create a new pipeline
        pipeline = client.pipelines.create(
            name="Data Processing Pipeline",
            team_id="team_123",
            description="Processes customer data",
            config={"batch_size": 100}
        )

        # Update a pipeline
        pipeline = client.pipelines.update(
            "pipeline_123",
            name="Updated Pipeline Name"
        )

        # Run a pipeline
        run = client.pipelines.run(
            "pipeline_123",
            input_data={"source": "dataset_123"}
        )

        # Get pipeline runs
        runs = client.pipelines.list_runs("pipeline_123")

        # Delete a pipeline
        client.pipelines.delete("pipeline_123")
        ```
    """

    def list(
        self,
        *,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all pipelines with pagination.

        Note: Results are automatically filtered to the team specified in the client.

        Args:
            status: Filter pipelines by status (e.g., "active", "inactive", "error").
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by. Defaults to "created_at".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Paginated list of pipelines for the client's team.
        """
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        if status is not None:
            query["status"] = status

        return self._get(
            "/pipelines",
            options={"query": query},
        )

    def retrieve(self, pipeline_id: str) -> Pipeline:
        """Retrieve a specific pipeline by ID.

        Args:
            pipeline_id: The ID of the pipeline to retrieve.

        Returns:
            The pipeline data.

        Raises:
            NotFoundError: If the pipeline doesn't exist.
        """
        return self._get(f"/pipelines/{pipeline_id}")

    def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Pipeline:
        """Create a new pipeline.

        Note: The pipeline will be created in the team specified in the client.

        Args:
            name: The pipeline's name.
            description: The pipeline's description.
            config: Pipeline configuration settings.
            **kwargs: Additional pipeline properties.

        Returns:
            The created pipeline data.

        Raises:
            ValidationError: If the request data is invalid.
        """
        body = {
            "name": name,
            "team_id": self._client.team_id,  # Use client's team_id
            **kwargs,
        }
        if description is not None:
            body["description"] = description
        if config is not None:
            body["config"] = config

        return self._post("/pipelines", body=body)

    def update(
        self,
        pipeline_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Pipeline:
        """Update an existing pipeline.

        Args:
            pipeline_id: The ID of the pipeline to update.
            name: New pipeline name.
            description: New pipeline description.
            config: New pipeline configuration.
            **kwargs: Additional properties to update.

        Returns:
            The updated pipeline data.

        Raises:
            NotFoundError: If the pipeline doesn't exist.
            ValidationError: If the request data is invalid.
        """
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if config is not None:
            body["config"] = config

        return self._patch(f"/pipelines/{pipeline_id}", body=body)

    def delete(self, pipeline_id: str) -> None:
        """Delete a pipeline.

        Args:
            pipeline_id: The ID of the pipeline to delete.

        Raises:
            NotFoundError: If the pipeline doesn't exist.
        """
        self._delete(f"/pipelines/{pipeline_id}")

    def run(
        self,
        pipeline_id: str,
        *,
        input_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Run a pipeline with optional input data.

        Args:
            pipeline_id: The ID of the pipeline to run.
            input_data: Input data for the pipeline run.
            **kwargs: Additional run options.

        Returns:
            Pipeline run data.

        Raises:
            NotFoundError: If the pipeline doesn't exist.
            ValidationError: If the input data is invalid.
        """
        body = {**kwargs}
        if input_data is not None:
            body["input_data"] = input_data

        return self._post(f"/pipelines/{pipeline_id}/run", body=body)

    def list_runs(
        self,
        pipeline_id: str,
        *,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List runs for a specific pipeline.

        Args:
            pipeline_id: The ID of the pipeline.
            status: Filter runs by status (e.g., "running", "completed", "failed").
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by. Defaults to "created_at".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Paginated list of pipeline runs.

        Raises:
            NotFoundError: If the pipeline doesn't exist.
        """
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        if status is not None:
            query["status"] = status

        return self._get(
            f"/pipelines/{pipeline_id}/runs",
            options={"query": query},
        )

    def get_run(
        self,
        pipeline_id: str,
        run_id: str,
    ) -> Dict[str, Any]:
        """Get details of a specific pipeline run.

        Args:
            pipeline_id: The ID of the pipeline.
            run_id: The ID of the run.

        Returns:
            Pipeline run data.

        Raises:
            NotFoundError: If the pipeline or run doesn't exist.
        """
        return self._get(f"/pipelines/{pipeline_id}/runs/{run_id}")

    def cancel_run(
        self,
        pipeline_id: str,
        run_id: str,
    ) -> Dict[str, Any]:
        """Cancel a running pipeline.

        Args:
            pipeline_id: The ID of the pipeline.
            run_id: The ID of the run to cancel.

        Returns:
            Updated run data.

        Raises:
            NotFoundError: If the pipeline or run doesn't exist.
            ConflictError: If the run cannot be cancelled.
        """
        return self._post(f"/pipelines/{pipeline_id}/runs/{run_id}/cancel")
