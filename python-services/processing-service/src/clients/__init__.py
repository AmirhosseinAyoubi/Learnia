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
    """Call Java document-service to update the processing status of a document."""
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
    except Exception as e:
        logger.error("Failed to update status for document %s: %s", document_id, e)
        raise
