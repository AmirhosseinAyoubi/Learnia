import json
from unittest.mock import patch, MagicMock, call

import pytest

from src.consumers import _on_message


class TestOnMessage:
    def _make_channel(self):
        ch = MagicMock()
        ch.basic_ack = MagicMock()
        ch.basic_nack = MagicMock()
        return ch

    def _make_method(self, delivery_tag=1):
        m = MagicMock()
        m.delivery_tag = delivery_tag
        return m

    def _body(self, doc_id="doc-123", file_url="/tmp/file.pdf", file_type="PDF"):
        return json.dumps({"documentId": doc_id, "fileUrl": file_url, "fileType": file_type}).encode()

    def test_valid_message_calls_process_and_acks(self):
        channel = self._make_channel()
        method = self._make_method(delivery_tag=42)

        with patch("src.consumers.process_document") as mock_process:
            _on_message(channel, method, None, self._body())

        mock_process.assert_called_once_with("doc-123", "/tmp/file.pdf", "PDF")
        channel.basic_ack.assert_called_once_with(delivery_tag=42)
        channel.basic_nack.assert_not_called()

    def test_process_failure_nacks_without_requeue(self):
        channel = self._make_channel()
        method = self._make_method(delivery_tag=7)

        with patch("src.consumers.process_document", side_effect=RuntimeError("crash")):
            _on_message(channel, method, None, self._body())

        channel.basic_nack.assert_called_once_with(delivery_tag=7, requeue=False)
        channel.basic_ack.assert_not_called()

    def test_malformed_json_nacks(self):
        channel = self._make_channel()
        method = self._make_method()

        with patch("src.consumers.process_document") as mock_process:
            _on_message(channel, method, None, b"not valid json{{{")

        mock_process.assert_not_called()
        channel.basic_nack.assert_called_once_with(delivery_tag=method.delivery_tag, requeue=False)

    def test_missing_field_nacks(self):
        channel = self._make_channel()
        method = self._make_method()
        body = json.dumps({"documentId": "doc-1"}).encode()  # missing fileUrl and fileType

        with patch("src.consumers.process_document") as mock_process:
            _on_message(channel, method, None, body)

        mock_process.assert_not_called()
        channel.basic_nack.assert_called_once_with(delivery_tag=method.delivery_tag, requeue=False)

    def test_message_with_all_fields_passes_correct_values(self):
        channel = self._make_channel()
        method = self._make_method()
        body = json.dumps({
            "documentId": "abc-999",
            "fileUrl": "/uploads/2024_doc.pptx",
            "fileType": "PPTX"
        }).encode()

        with patch("src.consumers.process_document") as mock_process:
            _on_message(channel, method, None, body)

        mock_process.assert_called_once_with("abc-999", "/uploads/2024_doc.pptx", "PPTX")
        channel.basic_ack.assert_called_once()
