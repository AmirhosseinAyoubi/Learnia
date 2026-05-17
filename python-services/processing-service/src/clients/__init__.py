# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""HTTP client helpers for calling downstream services.

Each function opens a short-lived httpx.Client, makes one request, and either
returns the result or raises on non-2xx status so the caller can handle it.
"""
import logging
from typing import Optional

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


def update_document_status(
    document_id: str,
    status: str,
    page_count: Optional[int] = None,
    error: Optional[str] = None,
) -> None:
    """PATCH the processing status of a document in the document-service.

    Args:
        document_id: UUID string of the document to update.
        status: New status string (e.g. ``"PROCESSING"``, ``"COMPLETED"``, ``"FAILED"``).
        page_count: Optional page count to persist alongside the status.
        error: Optional error message to persist when status is ``"FAILED"``.

    Raises:
        httpx.HTTPStatusError: When the document-service returns a non-2xx response.
        httpx.ConnectError: When the document-service is unreachable.
    """
    url = f"{settings.document_service_url}/documents/{document_id}/status"
    payload: dict = {"status": status}
    if page_count is not None:
        payload["pageCount"] = page_count
    if error is not None:
        payload["error"] = error

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.patch(url, json=payload)
            response.raise_for_status()
            logger.debug("Updated document %s status to %s", document_id, status)
    except Exception as exc:
        logger.error("Failed to update status for document %s: %s", document_id, exc)
        raise


def save_chunks_to_content_service(
    document_id: str,
    chunks: list,
    api_key: str,
) -> None:
    """POST extracted text chunks to the content-service for storage.

    Args:
        document_id: UUID string of the owning document.
        chunks: Ordered list of text chunk strings to persist.
        api_key: Valid API key forwarded in the ``X-API-Key`` header.

    Raises:
        httpx.HTTPStatusError: When the content-service returns a non-2xx response.
        httpx.ConnectError: When the content-service is unreachable.
    """
    url = f"{settings.content_service_url}/api/v1/content/chunks"
    payload = {"document_id": document_id, "chunks": chunks}

    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload, headers={"X-API-Key": api_key})
        response.raise_for_status()
        logger.info("Saved %d chunks for document %s", len(chunks), document_id)


def trigger_ai_analysis(document_id: str, api_key: str) -> None:
    """POST an analysis request to the ai-service.

    The ai-service will fetch the stored chunks from content-service, call
    OpenAI, and persist the generated study materials.

    Args:
        document_id: UUID string of the document to analyse.
        api_key: Valid API key forwarded in the ``X-API-Key`` header.

    Raises:
        httpx.HTTPStatusError: When the ai-service returns a non-2xx response.
        httpx.ConnectError: When the ai-service is unreachable.
    """
    url = f"{settings.ai_service_url}/api/v1/ai/analyze"
    payload = {"document_id": document_id}

    with httpx.Client(timeout=120.0) as client:
        response = client.post(url, json=payload, headers={"X-API-Key": api_key})
        response.raise_for_status()
        logger.info("Triggered AI analysis for document %s", document_id)
