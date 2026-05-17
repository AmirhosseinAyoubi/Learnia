# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Pydantic schemas for the Processing Service request/response models."""
from typing import Optional

from pydantic import BaseModel


class ProcessDocumentMessage(BaseModel):
    """Incoming message describing a document to process.

    Matches the payload published by the Java document-service to RabbitMQ
    and also accepted by the HTTP ``POST /api/v1/processing/documents/process`` endpoint.
    """

    documentId: str
    fileUrl: str
    fileType: str


class StatusUpdate(BaseModel):
    """Payload for updating a document's processing status.

    Sent to the document-service ``PATCH /documents/{id}/status`` endpoint.
    """

    status: str  # PENDING | PROCESSING | COMPLETED | FAILED
    pageCount: Optional[int] = None
    error: Optional[str] = None
