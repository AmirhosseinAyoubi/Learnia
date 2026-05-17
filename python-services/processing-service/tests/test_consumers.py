import json
from unittest.mock import patch, MagicMock, call

import pytest

from src.consumers import _on_message, start_consumer, _connect_and_consume


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


class TestStartConsumer:
    """Tests for start_consumer and _connect_and_consume."""

    def test_start_consumer_succeeds_on_first_attempt(self):
        """When the first connection attempt succeeds, start_consumer returns
        immediately without retrying.

        Input: _connect_and_consume succeeds on first call.
        Expected: _connect_and_consume called exactly once.
        """
        with patch("src.consumers._connect_and_consume") as mock_connect:
            start_consumer()

        mock_connect.assert_called_once()

    def test_start_consumer_retries_on_failure(self):
        """When _connect_and_consume raises on the first attempt, start_consumer
        retries up to _MAX_RETRIES times before giving up.

        Input: _connect_and_consume always raises RuntimeError.
        Expected: _connect_and_consume called _MAX_RETRIES times.
        """
        with patch("src.consumers._connect_and_consume", side_effect=RuntimeError("conn refused")):
            with patch("src.consumers.time.sleep"):
                start_consumer()

    def test_start_consumer_succeeds_on_second_attempt(self):
        """If the first attempt fails but the second succeeds, start_consumer
        stops retrying after the successful connection.

        Input: first call raises, second call succeeds.
        Expected: _connect_and_consume called exactly twice.
        """
        call_count = {"n": 0}

        def flaky_connect():
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("first failure")

        with patch("src.consumers._connect_and_consume", side_effect=flaky_connect):
            with patch("src.consumers.time.sleep"):
                start_consumer()

        assert call_count["n"] == 2

    def test_connect_and_consume_sets_up_channel(self):
        """_connect_and_consume declares the queue, sets QoS, and starts
        consuming — verifying the full RabbitMQ setup is performed correctly.

        Input: mocked pika.BlockingConnection.
        Expected: queue_declare, basic_qos, basic_consume, start_consuming all called.
        """
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.channel.return_value = mock_channel

        with patch("src.consumers.pika.BlockingConnection", return_value=mock_connection):
            with patch("src.consumers.pika.PlainCredentials", return_value=MagicMock()):
                with patch("src.consumers.pika.ConnectionParameters", return_value=MagicMock()):
                    _connect_and_consume()

        mock_channel.queue_declare.assert_called_once()
        mock_channel.basic_qos.assert_called_once_with(prefetch_count=1)
        mock_channel.basic_consume.assert_called_once()
        mock_channel.start_consuming.assert_called_once()
