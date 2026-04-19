from unittest.mock import patch, MagicMock

import httpx
import pytest

from src.clients import update_document_status


class TestUpdateDocumentStatus:
    def _mock_client(self, status_code=204):
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.raise_for_status = MagicMock()
        if status_code >= 400:
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "error", request=MagicMock(), response=response
            )
        client = MagicMock()
        client.patch.return_value = response
        client.__enter__.return_value = client
        client.__exit__.return_value = None
        return client

    def test_sends_status_only(self):
        mock_client = self._mock_client()
        with patch("src.clients.httpx.Client", return_value=mock_client):
            update_document_status("doc-123", "PROCESSING")

        mock_client.patch.assert_called_once()
        _, kwargs = mock_client.patch.call_args
        assert kwargs["json"] == {"status": "PROCESSING"}

    def test_sends_status_with_page_count(self):
        mock_client = self._mock_client()
        with patch("src.clients.httpx.Client", return_value=mock_client):
            update_document_status("doc-123", "COMPLETED", page_count=10)

        _, kwargs = mock_client.patch.call_args
        assert kwargs["json"] == {"status": "COMPLETED", "pageCount": 10}

    def test_sends_status_with_error(self):
        mock_client = self._mock_client()
        with patch("src.clients.httpx.Client", return_value=mock_client):
            update_document_status("doc-123", "FAILED", error="extraction failed")

        _, kwargs = mock_client.patch.call_args
        assert kwargs["json"] == {"status": "FAILED", "error": "extraction failed"}

    def test_sends_all_fields(self):
        mock_client = self._mock_client()
        with patch("src.clients.httpx.Client", return_value=mock_client):
            update_document_status("doc-123", "COMPLETED", page_count=5, error=None)

        _, kwargs = mock_client.patch.call_args
        assert kwargs["json"] == {"status": "COMPLETED", "pageCount": 5}

    def test_correct_url_built(self):
        mock_client = self._mock_client()
        with patch("src.clients.httpx.Client", return_value=mock_client), \
             patch("src.clients.settings") as mock_settings:
            mock_settings.document_service_url = "http://doc-service:8084"
            update_document_status("abc-456", "PROCESSING")

        called_url = mock_client.patch.call_args[0][0]
        assert "abc-456" in called_url
        assert "status" in called_url

    def test_raises_on_http_error(self):
        mock_client = self._mock_client(status_code=500)
        with patch("src.clients.httpx.Client", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                update_document_status("doc-123", "PROCESSING")

    def test_raises_on_connection_error(self):
        client = MagicMock()
        client.patch.side_effect = httpx.ConnectError("refused")
        client.__enter__.return_value = client
        client.__exit__.return_value = None
        with patch("src.clients.httpx.Client", return_value=client):
            with pytest.raises(httpx.ConnectError):
                update_document_status("doc-123", "PROCESSING")
