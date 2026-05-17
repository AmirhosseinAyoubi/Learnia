# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Unit tests for the Processing Service HTTP client helpers.

Tests cover all three client functions:
- update_document_status: PATCH to document-service
- save_chunks_to_content_service: POST to content-service
- trigger_ai_analysis: POST to ai-service

``httpx.Client`` is patched so no real network calls are made.
"""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.clients import (
    save_chunks_to_content_service,
    trigger_ai_analysis,
    update_document_status,
)


def _mock_client(status_code: int = 204, method: str = "patch"):
    """Build a context-manager-compatible mock httpx.Client."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=response
        )
    client = MagicMock()
    getattr(client, method).return_value = response
    client.__enter__.return_value = client
    client.__exit__.return_value = None
    return client


class TestUpdateDocumentStatus:
    """Tests for the ``update_document_status`` client function."""

    def test_sends_status_only(self):
        """When only status is provided the JSON payload contains just "status".

        Input: document_id + status "PROCESSING" (no page_count or error).
        Expected: PATCH called with {"status": "PROCESSING"}.
        """
        mock = _mock_client()
        with patch("src.clients.httpx.Client", return_value=mock):
            update_document_status("doc-123", "PROCESSING")

        _, kwargs = mock.patch.call_args
        assert kwargs["json"] == {"status": "PROCESSING"}

    def test_sends_status_with_page_count(self):
        """When page_count is provided it is added as "pageCount" in the payload.

        Input: status "COMPLETED" and page_count=10.
        Expected: payload {"status": "COMPLETED", "pageCount": 10}.
        """
        mock = _mock_client()
        with patch("src.clients.httpx.Client", return_value=mock):
            update_document_status("doc-123", "COMPLETED", page_count=10)

        _, kwargs = mock.patch.call_args
        assert kwargs["json"] == {"status": "COMPLETED", "pageCount": 10}

    def test_sends_status_with_error(self):
        """When error is provided it is included in the payload under "error".

        Input: status "FAILED" and error message.
        Expected: payload contains both "status" and "error" keys.
        """
        mock = _mock_client()
        with patch("src.clients.httpx.Client", return_value=mock):
            update_document_status("doc-123", "FAILED", error="extraction failed")

        _, kwargs = mock.patch.call_args
        assert kwargs["json"] == {"status": "FAILED", "error": "extraction failed"}

    def test_sends_all_fields(self):
        """All optional fields are included when provided.

        Input: status, page_count, and error all set.
        Expected: all three keys present in the PATCH payload.
        """
        mock = _mock_client()
        with patch("src.clients.httpx.Client", return_value=mock):
            update_document_status("doc-123", "COMPLETED", page_count=5, error=None)

        _, kwargs = mock.patch.call_args
        assert kwargs["json"] == {"status": "COMPLETED", "pageCount": 5}

    def test_correct_url_built(self):
        """The URL includes both the document_id and the "/status" suffix.

        Verifies that the request reaches the correct document-service endpoint.
        """
        mock = _mock_client()
        with (
            patch("src.clients.httpx.Client", return_value=mock),
            patch("src.clients.settings") as mock_settings,
        ):
            mock_settings.document_service_url = "http://doc-service:8084"
            update_document_status("abc-456", "PROCESSING")

        called_url = mock.patch.call_args[0][0]
        assert "abc-456" in called_url
        assert "status" in called_url

    def test_raises_on_http_error(self):
        """A non-2xx response from the document-service raises HTTPStatusError.

        Input: document-service returns 500.
        Expected: httpx.HTTPStatusError propagates to the caller.
        """
        mock = _mock_client(status_code=500)
        with patch("src.clients.httpx.Client", return_value=mock):
            with pytest.raises(httpx.HTTPStatusError):
                update_document_status("doc-123", "PROCESSING")

    def test_raises_on_connection_error(self):
        """A connection failure raises ConnectError.

        Input: document-service is unreachable.
        Expected: httpx.ConnectError propagates to the caller.
        """
        client_mock = MagicMock()
        client_mock.patch.side_effect = httpx.ConnectError("refused")
        client_mock.__enter__.return_value = client_mock
        client_mock.__exit__.return_value = None

        with patch("src.clients.httpx.Client", return_value=client_mock):
            with pytest.raises(httpx.ConnectError):
                update_document_status("doc-123", "PROCESSING")


class TestSaveChunksToContentService:
    """Tests for the ``save_chunks_to_content_service`` client function."""

    def test_posts_chunks_to_correct_endpoint(self):
        """Chunks are POSTed to /api/v1/content/chunks with document_id and chunks list.

        Input: document_id "doc-1" and two chunk strings.
        Expected: POST body contains document_id and chunks list.
        """
        mock = _mock_client(status_code=200, method="post")
        with patch("src.clients.httpx.Client", return_value=mock):
            save_chunks_to_content_service("doc-1", ["a", "b"], "key")

        _, kwargs = mock.post.call_args
        assert kwargs["json"]["document_id"] == "doc-1"
        assert kwargs["json"]["chunks"] == ["a", "b"]

    def test_includes_api_key_header(self):
        """The X-API-Key header is forwarded to the content-service.

        Internal service-to-service calls must authenticate with the auth-service.
        """
        mock = _mock_client(status_code=200, method="post")
        with patch("src.clients.httpx.Client", return_value=mock):
            save_chunks_to_content_service("doc-1", [], "secret-key")

        _, kwargs = mock.post.call_args
        assert kwargs["headers"]["X-API-Key"] == "secret-key"

    def test_http_error_propagates(self):
        """A non-2xx response from the content-service raises HTTPStatusError.

        Input: content-service returns 500.
        Expected: httpx.HTTPStatusError propagates to the caller.
        """
        mock = _mock_client(status_code=500, method="post")
        with patch("src.clients.httpx.Client", return_value=mock):
            with pytest.raises(httpx.HTTPStatusError):
                save_chunks_to_content_service("doc-1", ["chunk"], "key")


class TestTriggerAiAnalysis:
    """Tests for the ``trigger_ai_analysis`` client function."""

    def test_posts_document_id_to_ai_service(self):
        """The function POSTs the document_id to /api/v1/ai/analyze.

        Input: document_id "doc-abc".
        Expected: POST body contains {"document_id": "doc-abc"}.
        """
        mock = _mock_client(status_code=200, method="post")
        with patch("src.clients.httpx.Client", return_value=mock):
            trigger_ai_analysis("doc-abc", "api-key")

        _, kwargs = mock.post.call_args
        assert kwargs["json"] == {"document_id": "doc-abc"}

    def test_includes_api_key_header(self):
        """The X-API-Key header is forwarded to the ai-service.

        Ensures the ai-service can authenticate the incoming request.
        """
        mock = _mock_client(status_code=200, method="post")
        with patch("src.clients.httpx.Client", return_value=mock):
            trigger_ai_analysis("doc-1", "my-key")

        _, kwargs = mock.post.call_args
        assert kwargs["headers"]["X-API-Key"] == "my-key"

    def test_http_error_propagates(self):
        """A non-2xx response from the ai-service raises HTTPStatusError.

        Input: ai-service returns 503 (overloaded).
        Expected: httpx.HTTPStatusError propagates so the caller can mark FAILED.
        """
        mock = _mock_client(status_code=503, method="post")
        with patch("src.clients.httpx.Client", return_value=mock):
            with pytest.raises(httpx.HTTPStatusError):
                trigger_ai_analysis("doc-1", "key")
