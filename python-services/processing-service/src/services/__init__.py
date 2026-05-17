# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Document processing pipeline.

Orchestrates extraction → chunking → content storage → AI analysis
as a single synchronous pipeline invoked by the RabbitMQ consumer.
"""
import logging
import os

from ..clients import save_chunks_to_content_service, trigger_ai_analysis, update_document_status
from ..config import settings
from ..processors import chunk_text, extract_text

logger = logging.getLogger(__name__)


def _resolve_file_path(file_url: str) -> str:
    """Resolve a file URL to an absolute path on the local filesystem.

    The document-service stores absolute paths (``/app/uploads/...``).
    Legacy records and seed data may store ``/uploads/...`` without the
    ``/app`` prefix.  This function normalises both forms.

    Args:
        file_url: Raw fileUrl value from the RabbitMQ message.

    Returns:
        Absolute path that can be opened directly.
    """
    if os.path.exists(file_url):
        return file_url
    # Try prepending the configured upload base dir
    basename = os.path.basename(file_url)
    candidate = os.path.join(settings.file_upload_dir, basename)
    if os.path.exists(candidate):
        return candidate
    # Return original and let the caller raise a clear error
    return file_url


def process_document(document_id: str, file_url: str, file_type: str) -> None:
    """Run the full processing pipeline for a single document.

    Steps:
    1. Mark the document as ``PROCESSING`` in the document-service.
    2. Extract raw text and page count from the file.
    3. Split the text into token-bounded chunks via tiktoken.
    4. Persist chunks to the content-service.
    5. Trigger AI analysis in the ai-service.
    6. Mark the document as ``COMPLETED`` (or ``FAILED`` on any error).

    Args:
        document_id: UUID string identifying the document to process.
        file_url: Absolute path (or URL) to the uploaded file on disk.
        file_type: File extension in upper case (``"PDF"``, ``"PPTX"``, ``"TXT"``).
    """
    logger.info(
        "Starting processing for document=%s file=%s type=%s",
        document_id, file_url, file_type,
    )

    try:
        update_document_status(document_id, "PROCESSING")
    except Exception:  # pylint: disable=broad-except
        logger.warning(
            "Could not mark document %s as PROCESSING, continuing anyway",
            document_id,
        )

    try:
        resolved_path = _resolve_file_path(file_url)
        logger.info("document=%s resolved path: %s", document_id, resolved_path)
        text, page_count = extract_text(resolved_path, file_type)
        chunks = chunk_text(text)

        logger.info(
            "document=%s extracted %d chars, %d chunks, %d pages",
            document_id, len(text), len(chunks), page_count,
        )

        save_chunks_to_content_service(document_id, chunks, settings.internal_api_key)
        trigger_ai_analysis(document_id, settings.internal_api_key)

        update_document_status(document_id, "COMPLETED", page_count=page_count)
        logger.info("document=%s processing complete", document_id)

    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Processing failed for document=%s: %s", document_id, exc)
        update_document_status(document_id, "FAILED", error=str(exc))
