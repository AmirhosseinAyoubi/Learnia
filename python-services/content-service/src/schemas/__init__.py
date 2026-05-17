# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Pydantic request/response models for the Content Service."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ChunksCreate(BaseModel):
    """Request body for storing a batch of text chunks.

    Attributes:
        document_id: UUID string of the owning document.
        chunks: Ordered list of text chunk strings to persist.
    """

    document_id: str
    chunks: list[str]


class ChunkResponse(BaseModel):
    """Response representation of a single stored chunk.

    Attributes:
        id: Assigned UUID primary key.
        document_id: UUID of the owning document.
        chunk_index: Zero-based sequential position.
        content: The chunk text.
        created_at: UTC timestamp of insertion.
    """

    id: str
    document_id: str
    chunk_index: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MaterialCreate(BaseModel):
    """Request body for storing a single generated material.

    Attributes:
        document_id: UUID string of the owning document.
        material_type: Category — one of ``"summary"``, ``"key_concepts"``,
            or ``"flashcards"``.
        content: Material data (string, list, or list of dicts).
    """

    document_id: str
    material_type: str
    content: Any


class MaterialResponse(BaseModel):
    """Response representation of a single generated material.

    Attributes:
        id: Assigned UUID primary key.
        document_id: UUID of the owning document.
        material_type: Category string.
        content: Material data (string, list, or list of dicts).
        created_at: UTC timestamp of insertion.
    """

    id: str
    document_id: str
    material_type: str
    content: Any
    created_at: datetime

    model_config = {"from_attributes": True}
