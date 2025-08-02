"""Async files resource for the Moderately AI API."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles
import httpx

from ..exceptions import APIError
from ..models.file_async import FileAsyncModel
from ..types import File, PaginatedResponse
from ._base import AsyncBaseResource


class AsyncFiles(AsyncBaseResource):
    """Manage files in your teams (async version).

    All methods return FileAsyncModel instances which provide rich functionality
    for file operations like downloading, deleting, and checking file properties.

    Examples:
        ```python
        # List all files (returns raw data)
        files = await client.files.list()

        # Get a file with rich functionality
        file = await client.files.retrieve("file_123")

        # Upload a new file and get FileAsyncModel
        file = await client.files.upload(
            file_path="/path/to/document.pdf",
            name="Important Document"
        )

        # Use rich file operations
        if file.is_ready() and file.is_document():
            content = await file.download()  # Download to memory
            await file.download(path="./local_copy.pdf")  # Download to disk
            
        # Check file properties
        print(f"File: {file.name} ({file.file_size} bytes)")
        print(f"Type: {file.mime_type}, Extension: {file.get_extension()}")

        # Update file metadata
        file = await client.files.update(
            "file_123",
            name="Updated Document Name"
        )

        # Delete file using rich model
        await file.delete()
        ```
    """

    async def list(
        self,
        *,
        dataset_id: Optional[str] = None,
        status: Optional[str] = None,
        mime_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> Dict[str, Any]:
        """List all files with pagination.

        Note: Results are automatically filtered to the team specified in the client.

        Args:
            dataset_id: Filter files by dataset ID.
            status: Filter files by status (e.g., "uploaded", "processing", "ready", "error").
            mime_type: Filter files by MIME type (e.g., "text/csv", "application/pdf").
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by. Defaults to "created_at".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Paginated list of files for the client's team.
        """
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        if dataset_id is not None:
            query["dataset_id"] = dataset_id
        if status is not None:
            query["status"] = status
        if mime_type is not None:
            query["mime_type"] = mime_type

        response = await self._get("/files", options={"query": query})
        
        # Convert items to FileAsyncModel instances
        if "items" in response:
            response["items"] = [
                FileAsyncModel(item, self._client) for item in response["items"]
            ]
        
        return response

    async def retrieve(self, file_id: str) -> FileAsyncModel:
        """Retrieve a specific file by ID.

        Args:
            file_id: The ID of the file to retrieve.

        Returns:
            The file model with rich functionality.

        Raises:
            NotFoundError: If the file doesn't exist.
        """
        data = await self._get(f"/files/{file_id}")
        return FileAsyncModel(data, self._client)

    async def upload(
        self,
        *,
        file_path: Optional[Union[str, Path]] = None,
        file_data: Optional[bytes] = None,
        name: Optional[str] = None,
        original_name: Optional[str] = None,
        dataset_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> FileAsyncModel:
        """Upload a new file.

        Note: The file will be uploaded to the team specified in the client.

        Args:
            file_path: Path to the file to upload (either this or file_data is required).
            file_data: Raw file data to upload (either this or file_path is required).
            name: Display name for the file. If not provided, will use filename.
            original_name: Original filename. If not provided, will use filename from path.
            dataset_id: Optional dataset ID to associate the file with.
            metadata: Additional metadata for the file.
            **kwargs: Additional file properties.

        Returns:
            The uploaded file model with rich functionality.

        Raises:
            ValueError: If neither file_path nor file_data is provided.
            ValidationError: If the file is invalid.
            NotFoundError: If the dataset doesn't exist.
        """
        if file_path is None and file_data is None:
            raise ValueError("Either file_path or file_data must be provided")

        # Prepare file data
        if file_path is not None:
            file_path = Path(file_path)
            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")

            with open(file_path, "rb") as f:
                file_data = f.read()

            if original_name is None:
                original_name = file_path.name
            if name is None:
                name = file_path.name

        body = {
            "team_id": self._client.team_id,  # Use client's team_id
            **kwargs,
        }

        if name is not None:
            body["name"] = name
        if original_name is not None:
            body["original_name"] = original_name
        if dataset_id is not None:
            body["dataset_id"] = dataset_id
        if metadata is not None:
            body["metadata"] = metadata

        # Note: In a real implementation, this would likely use multipart/form-data
        # For now, we'll encode the file data (this might need API-specific handling)
        if file_data is not None:
            # Convert bytes to base64 or handle according to API requirements
            import base64

            body["file_data"] = base64.b64encode(file_data).decode("utf-8")
            body["file_size"] = len(file_data)

        data = await self._post("/files", body=body)
        return FileAsyncModel(data, self._client)

    async def update(
        self,
        file_id: str,
        *,
        name: Optional[str] = None,
        dataset_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> FileAsyncModel:
        """Update an existing file's metadata.

        Args:
            file_id: The ID of the file to update.
            name: New file name.
            dataset_id: New dataset ID to associate with.
            metadata: Updated metadata.
            **kwargs: Additional properties to update.

        Returns:
            The updated file model with rich functionality.

        Raises:
            NotFoundError: If the file doesn't exist.
            ValidationError: If the request data is invalid.
        """
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if dataset_id is not None:
            body["dataset_id"] = dataset_id
        if metadata is not None:
            body["metadata"] = metadata

        data = await self._patch(f"/files/{file_id}", body=body)
        return FileAsyncModel(data, self._client)

    async def delete(self, file_id: str) -> None:
        """Delete a file.

        Args:
            file_id: The ID of the file to delete.

        Raises:
            NotFoundError: If the file doesn't exist.
        """
        await self._delete(f"/files/{file_id}")

    async def download(self, file_id: str) -> bytes:
        """Download file content.

        Args:
            file_id: The ID of the file to download.

        Returns:
            The file content as bytes.

        Raises:
            NotFoundError: If the file doesn't exist.
        """
        # This would typically return the raw file content
        # For now, we'll make a request to a download endpoint
        response = await self._client._make_request(
            "GET", f"/files/{file_id}/download", cast_type=dict
        )

        # In a real implementation, this might return binary data directly
        # or a download URL that needs to be fetched separately
        if isinstance(response, dict) and "download_url" in response:
            # If API returns a download URL, we'd need to fetch it
            import httpx

            async with httpx.AsyncClient() as client:
                download_response = await client.get(response["download_url"])
                return download_response.content
        elif isinstance(response, dict) and "content" in response:
            # If API returns base64 encoded content
            import base64

            return base64.b64decode(response["content"])
        else:
            # Assume response is already binary data
            return response if isinstance(response, bytes) else str(response).encode()

    async def get_upload_url(
        self,
        *,
        filename: str,
        file_size: int,
        mime_type: Optional[str] = None,
        dataset_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Get a presigned upload URL for large file uploads.

        This is useful for uploading large files directly to cloud storage.

        Args:
            filename: Name of the file to upload.
            file_size: Size of the file in bytes.
            mime_type: MIME type of the file.
            dataset_id: Optional dataset ID to associate the file with.
            **kwargs: Additional upload parameters.

        Returns:
            Upload URL and metadata.

        Raises:
            ValidationError: If the request data is invalid.
        """
        body = {
            "filename": filename,
            "file_size": file_size,
            "team_id": self._client.team_id,
            **kwargs,
        }

        if mime_type is not None:
            body["mime_type"] = mime_type
        if dataset_id is not None:
            body["dataset_id"] = dataset_id

        return await self._client._make_request(
            "POST", "/files/upload-url", cast_type=dict, body=body
        )
