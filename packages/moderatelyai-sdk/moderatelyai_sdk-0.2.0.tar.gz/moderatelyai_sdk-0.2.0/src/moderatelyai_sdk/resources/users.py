"""Users resource for the Moderately AI API."""

from typing import Optional

from ..types import PaginatedResponse, User
from ._base import BaseResource


class Users(BaseResource):
    """Manage users in your organization.

    Examples:
        ```python
        # List all users
        users = client.users.list()

        # Get a specific user
        user = client.users.retrieve("user_123")

        # Create a new user
        user = client.users.create(
            email="user@example.com",
            name="John Doe"
        )

        # Update a user
        user = client.users.update(
            "user_123",
            name="Jane Doe"
        )

        # Delete a user
        client.users.delete("user_123")
        ```
    """

    def list(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all users with pagination.

        Args:
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by. Defaults to "created_at".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Paginated list of users.
        """
        return self._get(
            "/users",
            options={
                "query": {
                    "page": page,
                    "page_size": page_size,
                    "order_by": order_by,
                    "order_direction": order_direction,
                }
            },
        )

    def retrieve(self, user_id: str) -> User:
        """Retrieve a specific user by ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The user data.

        Raises:
            NotFoundError: If the user doesn't exist.
        """
        return self._get(f"/users/{user_id}")

    def create(
        self,
        *,
        email: str,
        name: Optional[str] = None,
        **kwargs,
    ) -> User:
        """Create a new user.

        Args:
            email: The user's email address.
            name: The user's display name.
            **kwargs: Additional user properties.

        Returns:
            The created user data.

        Raises:
            ValidationError: If the request data is invalid.
            ConflictError: If a user with this email already exists.
        """
        body = {
            "email": email,
            **kwargs,
        }
        if name is not None:
            body["name"] = name

        return self._post("/users", body=body)

    def update(
        self,
        user_id: str,
        *,
        email: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> User:
        """Update an existing user.

        Args:
            user_id: The ID of the user to update.
            email: New email address.
            name: New display name.
            **kwargs: Additional properties to update.

        Returns:
            The updated user data.

        Raises:
            NotFoundError: If the user doesn't exist.
            ValidationError: If the request data is invalid.
        """
        body = {**kwargs}
        if email is not None:
            body["email"] = email
        if name is not None:
            body["name"] = name

        return self._patch(f"/users/{user_id}", body=body)

    def delete(self, user_id: str) -> None:
        """Delete a user.

        Args:
            user_id: The ID of the user to delete.

        Raises:
            NotFoundError: If the user doesn't exist.
        """
        self._delete(f"/users/{user_id}")
