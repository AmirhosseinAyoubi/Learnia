import logging
from ..processors import extract_text, chunk_text
from ..clients import update_document_status

logger = logging.getLogger(__name__)


def process_document(document_id: str, file_url: str, file_type: str) -> None:
    """Full processing pipeline: mark processing → extract → chunk → report result."""
    logger.info("Starting processing for document=%s file=%s type=%s", document_id, file_url, file_type)

    try:
        update_document_status(document_id, "PROCESSING")
    except Exception:
        logger.warning("Could not mark document %s as PROCESSING, continuing anyway", document_id)

    try:
        text, page_count = extract_text(file_url, file_type)
        chunks = chunk_text(text)

        logger.info(
            "document=%s extracted %d chars, %d chunks, %d pages",
            document_id, len(text), len(chunks), page_count,
        )

        # TODO: forward chunks to content-service for embedding storage

        update_document_status(document_id, "COMPLETED", page_count=page_count)
        logger.info("document=%s processing complete", document_id)

    except Exception as e:
        logger.error("Processing failed for document=%s: %s", document_id, e)
        update_document_status(document_id, "FAILED", error=str(e))
