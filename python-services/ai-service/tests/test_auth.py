# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Unit tests for the AI Service auth dependency.

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

        The key is passed through so downstream service calls can forward it
        in their own X-API-Key headers.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.auth.httpx.AsyncClient", return_value=mock_client):
            result = await require_api_key("valid-key-abc")

        assert result == "valid-key-abc"

    @pytest.mark.asyncio
    async def test_invalid_key_raises_401(self):
        """A key rejected by the auth-service (non-200) raises HTTPException 401.

        Callers always receive 401 regardless of the exact status the
        auth-service returns, keeping the API surface consistent.
        """
        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.auth.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await require_api_key("expired-key")

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_service_unavailable_raises_503(self):
        """A connection error to the auth-service raises HTTPException 503.

        503 signals a transient upstream issue rather than a client error,
        allowing callers to retry after a delay.
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
    async def test_revoked_key_with_403_maps_to_401(self):
        """Any non-200 response (including 403 for revoked keys) maps to 401.

        This prevents leaking auth-service internals to external callers.
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
