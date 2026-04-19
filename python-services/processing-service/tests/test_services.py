from unittest.mock import patch, call

import pytest

from src.services import process_document


class TestProcessDocument:
    def test_success_flow_completes(self):
        with patch("src.services.extract_text", return_value=("full text", 3)) as mock_extract, \
             patch("src.services.chunk_text", return_value=["chunk1", "chunk2"]) as mock_chunk, \
             patch("src.services.update_document_status") as mock_update:

            process_document("doc-1", "/tmp/file.pdf", "PDF")

        mock_extract.assert_called_once_with("/tmp/file.pdf", "PDF")
        mock_chunk.assert_called_once_with("full text")
        assert mock_update.call_count == 2
        mock_update.assert_any_call("doc-1", "PROCESSING")
        mock_update.assert_any_call("doc-1", "COMPLETED", page_count=3)

    def test_marks_processing_before_extraction(self):
        calls = []
        def track_update(doc_id, status, **kwargs):
            calls.append(status)
        def slow_extract(url, ftype):
            calls.append("EXTRACTING")
            return ("text", 1)

        with patch("src.services.extract_text", side_effect=slow_extract), \
             patch("src.services.chunk_text", return_value=[]), \
             patch("src.services.update_document_status", side_effect=track_update):

            process_document("doc-1", "/f.pdf", "PDF")

        assert calls[0] == "PROCESSING"
        assert "EXTRACTING" in calls
        assert calls[-1] == "COMPLETED"

    def test_extraction_failure_marks_failed(self):
        with patch("src.services.extract_text", side_effect=ValueError("bad file")), \
             patch("src.services.update_document_status") as mock_update:

            process_document("doc-2", "/tmp/bad.pdf", "PDF")

        mock_update.assert_any_call("doc-2", "FAILED", error="bad file")
        completed_calls = [c for c in mock_update.call_args_list
                           if c[0][1] == "COMPLETED"]
        assert len(completed_calls) == 0

    def test_chunking_failure_marks_failed(self):
        with patch("src.services.extract_text", return_value=("text", 1)), \
             patch("src.services.chunk_text", side_effect=RuntimeError("tokenizer error")), \
             patch("src.services.update_document_status") as mock_update:

            process_document("doc-3", "/tmp/file.txt", "TXT")

        mock_update.assert_any_call("doc-3", "FAILED", error="tokenizer error")

    def test_processing_status_failure_does_not_abort(self):
        call_count = {"n": 0}

        def flaky_update(doc_id, status, **kwargs):
            call_count["n"] += 1
            if status == "PROCESSING":
                raise ConnectionError("RabbitMQ down")

        with patch("src.services.extract_text", return_value=("text", 2)), \
             patch("src.services.chunk_text", return_value=["c1"]), \
             patch("src.services.update_document_status", side_effect=flaky_update):

            process_document("doc-4", "/tmp/file.pdf", "PDF")

        assert call_count["n"] == 2

    def test_empty_text_still_completes(self):
        with patch("src.services.extract_text", return_value=("", 0)), \
             patch("src.services.chunk_text", return_value=[]) as mock_chunk, \
             patch("src.services.update_document_status") as mock_update:

            process_document("doc-5", "/tmp/empty.txt", "TXT")

        mock_chunk.assert_called_once_with("")
        mock_update.assert_any_call("doc-5", "COMPLETED", page_count=0)
