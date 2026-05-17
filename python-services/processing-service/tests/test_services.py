# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Unit tests for the Processing Service pipeline orchestration.

Tests verify the full ``process_document`` pipeline including the new
content-service and ai-service integration steps.  All external calls
(extract_text, chunk_text, update_document_status, save_chunks_to_content_service,
trigger_ai_analysis) are patched to avoid real I/O.

Test coverage:
- Happy path: extract → chunk → save chunks → trigger AI → COMPLETED
- PROCESSING status set before extraction begins
- Extraction failure → FAILED with error message
- Chunking failure → FAILED with error message
- PROCESSING status failure is non-fatal (pipeline continues)
- Empty text still completes
- Content-service failure → FAILED
- AI trigger failure → FAILED
"""
from unittest.mock import patch

import pytest

from src.services import process_document

_PATCH_EXTRACT = "src.services.extract_text"
_PATCH_CHUNK = "src.services.chunk_text"
_PATCH_STATUS = "src.services.update_document_status"
_PATCH_SAVE_CHUNKS = "src.services.save_chunks_to_content_service"
_PATCH_TRIGGER_AI = "src.services.trigger_ai_analysis"


class TestProcessDocument:
    """Tests for the ``process_document`` pipeline function."""

    def test_success_flow_completes(self):
        """The happy path marks PROCESSING, extracts, chunks, saves, triggers AI, then COMPLETED.

        Input: valid file URL and PDF type.
        Expected: update_document_status called with PROCESSING then COMPLETED;
        save_chunks and trigger_ai called exactly once each.
        """
        with (
            patch(_PATCH_EXTRACT, return_value=("full text", 3)),
            patch(_PATCH_CHUNK, return_value=["chunk1", "chunk2"]),
            patch(_PATCH_STATUS) as mock_update,
            patch(_PATCH_SAVE_CHUNKS) as mock_save,
            patch(_PATCH_TRIGGER_AI) as mock_ai,
        ):
            process_document("doc-1", "/tmp/file.pdf", "PDF")

        assert mock_update.call_count == 2
        mock_update.assert_any_call("doc-1", "PROCESSING")
        mock_update.assert_any_call("doc-1", "COMPLETED", page_count=3)
        mock_save.assert_called_once()
        mock_ai.assert_called_once()

    def test_marks_processing_before_extraction(self):
        """PROCESSING status is set before extraction begins.

        Verifies that the document is marked in-progress immediately so other
        services can see it is being handled.
        """
        call_order = []

        def track_update(doc_id, status, **_kwargs):
            call_order.append(status)

        def slow_extract(url, ftype):
            call_order.append("EXTRACTING")
            return ("text", 1)

        with (
            patch(_PATCH_EXTRACT, side_effect=slow_extract),
            patch(_PATCH_CHUNK, return_value=[]),
            patch(_PATCH_STATUS, side_effect=track_update),
            patch(_PATCH_SAVE_CHUNKS),
            patch(_PATCH_TRIGGER_AI),
        ):
            process_document("doc-1", "/f.pdf", "PDF")

        assert call_order[0] == "PROCESSING"
        assert "EXTRACTING" in call_order
        assert call_order[-1] == "COMPLETED"

    def test_extraction_failure_marks_failed(self):
        """An exception in extract_text marks the document as FAILED.

        Input: extract_text raises ValueError.
        Expected: update_document_status called with FAILED, never with COMPLETED.
        """
        with (
            patch(_PATCH_EXTRACT, side_effect=ValueError("bad file")),
            patch(_PATCH_STATUS) as mock_update,
        ):
            process_document("doc-2", "/tmp/bad.pdf", "PDF")

        mock_update.assert_any_call("doc-2", "FAILED", error="bad file")
        completed = [c for c in mock_update.call_args_list if c[0][1] == "COMPLETED"]
        assert len(completed) == 0

    def test_chunking_failure_marks_failed(self):
        """An exception in chunk_text marks the document as FAILED.

        Input: extract succeeds but chunk_text raises RuntimeError.
        Expected: update_document_status called with FAILED.
        """
        with (
            patch(_PATCH_EXTRACT, return_value=("text", 1)),
            patch(_PATCH_CHUNK, side_effect=RuntimeError("tokenizer error")),
            patch(_PATCH_STATUS) as mock_update,
        ):
            process_document("doc-3", "/tmp/file.txt", "TXT")

        mock_update.assert_any_call("doc-3", "FAILED", error="tokenizer error")

    def test_processing_status_failure_does_not_abort(self):
        """A failure when setting PROCESSING status does not abort the pipeline.

        The PROCESSING status update is best-effort; if it fails the document
        should still be processed and reach COMPLETED.
        """
        call_count = {"n": 0}

        def flaky_update(doc_id, status, **kwargs):
            call_count["n"] += 1
            if status == "PROCESSING":
                raise ConnectionError("service down")

        with (
            patch(_PATCH_EXTRACT, return_value=("text", 2)),
            patch(_PATCH_CHUNK, return_value=["c1"]),
            patch(_PATCH_STATUS, side_effect=flaky_update),
            patch(_PATCH_SAVE_CHUNKS),
            patch(_PATCH_TRIGGER_AI),
        ):
            process_document("doc-4", "/tmp/file.pdf", "PDF")

        assert call_count["n"] == 2  # PROCESSING (failed) + COMPLETED

    def test_empty_text_still_completes(self):
        """An empty document (zero chunks) completes without error.

        Input: extract_text returns empty string and zero pages.
        Expected: COMPLETED status with page_count=0.
        """
        with (
            patch(_PATCH_EXTRACT, return_value=("", 0)),
            patch(_PATCH_CHUNK, return_value=[]) as mock_chunk,
            patch(_PATCH_STATUS) as mock_update,
            patch(_PATCH_SAVE_CHUNKS),
            patch(_PATCH_TRIGGER_AI),
        ):
            process_document("doc-5", "/tmp/empty.txt", "TXT")

        mock_chunk.assert_called_once_with("")
        mock_update.assert_any_call("doc-5", "COMPLETED", page_count=0)

    def test_content_service_failure_marks_failed(self):
        """A failure saving chunks to the content-service marks the document FAILED.

        Input: save_chunks_to_content_service raises ConnectionError.
        Expected: FAILED status with the error message propagated.
        """
        with (
            patch(_PATCH_EXTRACT, return_value=("text", 1)),
            patch(_PATCH_CHUNK, return_value=["chunk"]),
            patch(_PATCH_SAVE_CHUNKS, side_effect=ConnectionError("content-service down")),
            patch(_PATCH_STATUS) as mock_update,
        ):
            process_document("doc-6", "/tmp/file.pdf", "PDF")

        mock_update.assert_any_call("doc-6", "FAILED", error="content-service down")

    def test_ai_trigger_failure_marks_failed(self):
        """A failure triggering AI analysis marks the document FAILED.

        Input: trigger_ai_analysis raises Exception.
        Expected: FAILED status — the document is processed but AI step failed.
        """
        with (
            patch(_PATCH_EXTRACT, return_value=("text", 1)),
            patch(_PATCH_CHUNK, return_value=["chunk"]),
            patch(_PATCH_SAVE_CHUNKS),
            patch(_PATCH_TRIGGER_AI, side_effect=Exception("ai-service timeout")),
            patch(_PATCH_STATUS) as mock_update,
        ):
            process_document("doc-7", "/tmp/file.pdf", "PDF")

        mock_update.assert_any_call("doc-7", "FAILED", error="ai-service timeout")
