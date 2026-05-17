# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""HTTP router for the Processing Service.

Exposes a single endpoint that acts as a synchronous alternative to the
RabbitMQ consumer, allowing callers to trigger processing via HTTP POST.
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..schemas import ProcessDocumentMessage
from ..services import process_document

router = APIRouter(prefix="/api/v1/processing", tags=["processing"])


@router.post("/documents/process")
def trigger_processing(
    message: ProcessDocumentMessage,
    background_tasks: BackgroundTasks,
) -> dict:
    """Manually trigger document processing via HTTP (alternative to RabbitMQ).

    Accepts a document message, enqueues processing as a background task,
    and immediately returns ``202 Accepted``-style JSON so the caller is not
    blocked by the potentially long extraction/AI pipeline.

    Args:
        message: Document metadata including ID, file URL, and file type.
        background_tasks: FastAPI dependency that schedules async work.

    Returns:
        JSON object with ``status`` and ``documentId`` keys.

    Raises:
        HTTPException: 500 if background task scheduling itself fails
            (this should never occur in normal operation).
    """
    try:
        background_tasks.add_task(
            process_document,
            message.documentId,
            message.fileUrl,
            message.fileType,
        )
        return {"status": "accepted", "documentId": message.documentId}
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc)) from exc
