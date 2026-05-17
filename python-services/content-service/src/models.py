# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""SQLAlchemy ORM models for the Content Service.

Two tables are defined:
- ``document_chunks`` — raw text chunks extracted from uploaded documents.
- ``generated_materials`` — AI-generated study materials (summary,
  key concepts, flashcards) stored as JSONB.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from .database import Base


def _new_uuid() -> str:
    """Generate a new UUID4 string for use as a primary key."""
    return str(uuid.uuid4())


class DocumentChunk(Base):
    """A single text chunk extracted from a document.

    Attributes:
        id: Auto-generated UUID primary key stored as VARCHAR(36).
        document_id: UUID of the owning document (FK handled in the document-service).
        chunk_index: Zero-based sequential position within the document.
        content: The raw text of this chunk.
        created_at: UTC timestamp of insertion.
    """

    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    document_id = Column(String(36), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class GeneratedMaterial(Base):
    """An AI-generated study material associated with a document.

    Attributes:
        id: Auto-generated UUID primary key stored as VARCHAR(36).
        document_id: UUID of the owning document.
        material_type: Category of material — one of ``"summary"``,
            ``"key_concepts"``, or ``"flashcards"``.
        content: JSON column; a string for summaries, a list of strings
            for key concepts, and a list of ``{question, answer}`` dicts
            for flashcards.
        created_at: UTC timestamp of insertion.
    """

    __tablename__ = "generated_materials"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    document_id = Column(String(36), nullable=False, index=True)
    material_type = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
