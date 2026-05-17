# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Unit tests for the AI Service HTTP client helpers.

``httpx.Client`` is patched to avoid real network calls.  Tests verify
that each client function sends the correct request and handles errors.

Coverage:
- get_chunks: success, HTTP error
- save_material: success
- get_materials: success, returns list
- delete_materials: success, calls DELETE
- Connection errors propagate to the caller
"""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.clients import delete_materials, get_chunks, get_materials, save_material


def _mock_http_client(status_code: int = 200, json_body=None):
    """Return a context-manager-compatible mock httpx.Client."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    if json_body is not None:
        response.json.return_value = json_body
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=response
        )
    else:
        response.raise_for_status = MagicMock()

    client_mock = MagicMock()
    client_mock.get.return_value = response
    client_mock.post.return_value = response
    client_mock.delete.return_value = response
    client_mock.__enter__ = MagicMock(return_value=client_mock)
    client_mock.__exit__ = MagicMock(return_value=False)
    return client_mock


class TestGetChunks:
    """Tests for the ``get_chunks`` client function."""

    def test_get_chunks_returns_content_strings(self):
        """A 200 response with chunk objects returns only the content strings.

        Input: content-service returns list of chunk dicts with "content" keys.
        Expected: list of plain text strings (content values extracted).
        """
        chunk_data = [{"content": "first chunk"}, {"content": "second chunk"}]
        mock_client = _mock_http_client(200, json_body=chunk_data)

        with patch("src.clients.httpx.Client", return_value=mock_client):
            result = get_chunks("doc-1", "api-key")

        assert result == ["first chunk", "second chunk"]

    def test_get_chunks_http_error_propagates(self):
        """A non-2xx response from the content-service raises HTTPStatusError.

        Input: content-service returns 404.
        Expected: httpx.HTTPStatusError propagates to the caller.
        """
        mock_client = _mock_http_client(404)

        with patch("src.clients.httpx.Client", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                get_chunks("doc-missing", "api-key")

    def test_get_chunks_sends_api_key_header(self):
        """The X-API-Key header is included in the GET request.

        Ensures the content-service can authenticate the incoming call.
        """
        mock_client = _mock_http_client(200, json_body=[])

        with patch("src.clients.httpx.Client", return_value=mock_client):
            get_chunks("doc-1", "my-secret-key")

        call_kwargs = mock_client.get.call_args[1]
        assert call_kwargs["headers"]["X-API-Key"] == "my-secret-key"


class TestSaveMaterial:
    """Tests for the ``save_material`` client function."""

    def test_save_material_success_does_not_raise(self):
        """A 200 response from the content-service completes without error.

        Input: valid document_id, material_type "summary", string content.
        Expected: function returns without raising.
        """
        mock_client = _mock_http_client(200)

        with patch("src.clients.httpx.Client", return_value=mock_client):
            save_material("doc-1", "summary", "A summary.", "api-key")

        mock_client.post.assert_called_once()

    def test_save_material_http_error_propagates(self):
        """A non-2xx response raises HTTPStatusError.

        Input: content-service returns 500.
        Expected: httpx.HTTPStatusError propagates to the caller.
        """
        mock_client = _mock_http_client(500)

        with patch("src.clients.httpx.Client", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                save_material("doc-1", "summary", "text", "api-key")


class TestGetMaterials:
    """Tests for the ``get_materials`` client function."""

    def test_get_materials_returns_list(self):
        """A 200 response with a list of materials is returned as-is.

        Input: content-service returns two material dicts.
        Expected: list of two dicts with material_type and content keys.
        """
        material_data = [
            {"material_type": "summary", "content": "text"},
            {"material_type": "key_concepts", "content": ["k1"]},
        ]
        mock_client = _mock_http_client(200, json_body=material_data)

        with patch("src.clients.httpx.Client", return_value=mock_client):
            result = get_materials("doc-1", "api-key")

        assert len(result) == 2
        assert result[0]["material_type"] == "summary"


class TestDeleteMaterials:
    """Tests for the ``delete_materials`` client function."""

    def test_delete_materials_sends_delete_request(self):
        """The function issues a DELETE request to the correct URL.

        Input: document_id and api_key.
        Expected: httpx client's delete method is called once.
        """
        mock_client = _mock_http_client(204)

        with patch("src.clients.httpx.Client", return_value=mock_client):
            delete_materials("doc-1", "api-key")

        mock_client.delete.assert_called_once()

    def test_delete_materials_connection_error_propagates(self):
        """A connection error to the content-service propagates to the caller.

        Input: content-service is unreachable (ConnectError).
        Expected: exception propagates without being swallowed.
        """
        mock_client = MagicMock()
        mock_client.delete.side_effect = httpx.ConnectError("refused")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)

        with patch("src.clients.httpx.Client", return_value=mock_client):
            with pytest.raises(httpx.ConnectError):
                delete_materials("doc-1", "api-key")
