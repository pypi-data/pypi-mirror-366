"""Tests for the ModeratelyAI client."""

from unittest.mock import Mock, patch

import pytest

from moderatelyai_sdk.client import ModeratelyAIClient
from moderatelyai_sdk.exceptions import AuthenticationError


class TestModeratelyAIClient:
    """Test cases for ModeratelyAIClient."""

    def test_client_initialization(self):
        """Test client initialization with default parameters."""
        client = ModeratelyAIClient(api_key="test-key")

        assert client.api_key == "test-key"
        assert client.base_url == "https://api.moderately.ai"
        assert client.timeout == 30
        assert client.max_retries == 3

    def test_client_initialization_with_custom_params(self):
        """Test client initialization with custom parameters."""
        client = ModeratelyAIClient(
            api_key="test-key",
            base_url="https://custom.api.com",
            timeout=60,
            max_retries=5,
        )

        assert client.api_key == "test-key"
        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 60
        assert client.max_retries == 5

    def test_context_manager(self):
        """Test client as context manager."""
        with ModeratelyAIClient(api_key="test-key") as client:
            assert isinstance(client, ModeratelyAIClient)

    @patch("moderatelyai_sdk.client.httpx.Client")
    def test_get_status_success(self, mock_httpx_client):
        """Test successful status request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "status": "online"}

        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = ModeratelyAIClient(api_key="test-key")
        result = client.get_status()

        assert result == {"success": True, "status": "online"}

    @patch("moderatelyai_sdk.client.httpx.Client")
    def test_authentication_error(self, mock_httpx_client):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401

        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = ModeratelyAIClient(api_key="invalid-key")

        with pytest.raises(AuthenticationError):
            client.get_status()

    @patch("moderatelyai_sdk.client.httpx.Client")
    def test_moderate_content(self, mock_httpx_client):
        """Test content moderation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"score": 0.1, "flagged": False},
        }

        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = ModeratelyAIClient(api_key="test-key")
        result = client.moderate_content("Hello world", "text")

        assert result["success"] is True
        assert "data" in result
