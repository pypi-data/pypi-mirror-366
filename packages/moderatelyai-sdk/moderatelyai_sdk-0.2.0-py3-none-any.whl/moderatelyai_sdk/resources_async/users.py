"""Async users resource for the Moderately AI API."""

from typing import Optional

from ..types import User, PaginatedResponse
from ._base import AsyncBaseResource


class AsyncUsers(AsyncBaseResource):
    """Manage users in your teams (async version)."""

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all users with pagination (async)."""
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        return await self._get("/users", options={"query": query})

    async def retrieve(self, user_id: str) -> User:
        """Retrieve a specific user by ID (async)."""
        return await self._get(f"/users/{user_id}")

    async def create(
        self,
        *,
        email: str,
        name: Optional[str] = None,
        **kwargs,
    ) -> User:
        """Create a new user (async)."""
        body = {
            "email": email,
            "teamId": self._client.team_id,  # API expects camelCase
            **kwargs,
        }
        if name is not None:
            body["name"] = name
        return await self._post("/users", body=body)

    async def update(
        self,
        user_id: str,
        *,
        name: Optional[str] = None,
        email: Optional[str] = None,
        **kwargs,
    ) -> User:
        """Update an existing user (async)."""
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if email is not None:
            body["email"] = email
        return await self._patch(f"/users/{user_id}", body=body)

    async def delete(self, user_id: str) -> None:
        """Delete a user (async)."""
        await self._delete(f"/users/{user_id}")
