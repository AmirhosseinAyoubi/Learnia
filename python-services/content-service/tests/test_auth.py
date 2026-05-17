# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Unit tests for the Content Service auth dependency.

Tests verify the three outcomes of ``require_api_key``:
- Valid key   → returns the key string
- Invalid key → raises HTTPException 401
- Service down → raises HTTPException 503

The ``httpx.AsyncClient`` is patched to avoid real network calls.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.auth import require_api_key


class TestRequireApiKey:
    """Tests for the ``require_api_key`` FastAPI dependency."""

    @pytest.mark.asyncio
    async def test_valid_key_returns_key_string(self):
        """A key accepted by the auth-service (200) is returned unchanged.

        The function should pass the validated key through so downstream
        service calls can forward it.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.auth.httpx.AsyncClient", return_value=mock_client):
            result = await require_api_key("valid-key-123")

        assert result == "valid-key-123"

    @pytest.mark.asyncio
    async def test_invalid_key_raises_401(self):
        """A key rejected by the auth-service (non-200) raises HTTPException 401.

        This ensures callers always receive a consistent 401 for bad keys
        regardless of the exact non-200 status the auth-service returns.
        """
        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.auth.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await require_api_key("bad-key")

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_service_unavailable_raises_503(self):
        """A connection error to the auth-service raises HTTPException 503.

        If the auth-service is down callers should receive a 503 rather than
        an unhandled exception, allowing them to retry or fail gracefully.
        """
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.auth.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await require_api_key("any-key")

        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_403_from_auth_service_also_raises_401(self):
        """Any non-200 response from auth-service (e.g. 403) maps to 401.

        The content-service should never expose the auth-service's internal
        status codes to its callers.
        """
        mock_response = MagicMock()
        mock_response.status_code = 403

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.auth.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await require_api_key("revoked-key")

        assert exc_info.value.status_code == 401
