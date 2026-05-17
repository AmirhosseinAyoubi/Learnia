# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Database CRUD helpers for the Content Service.

All functions accept a SQLAlchemy ``Session`` as the first argument so they
work with any database backend (PostgreSQL in production, SQLite in tests).
"""
from typing import Any

from sqlalchemy.orm import Session

from .models import DocumentChunk, GeneratedMaterial


def save_chunks(db: Session, document_id: str, chunks: list) -> list:
    """Persist a list of text chunks for a document, assigning sequential indices.

    Args:
        db: Active SQLAlchemy database session.
        document_id: UUID string of the owning document.
        chunks: Ordered list of text strings to persist.

    Returns:
        List of committed :class:`DocumentChunk` ORM instances.
    """
    db_chunks = [
        DocumentChunk(document_id=document_id, chunk_index=i, content=chunk)
        for i, chunk in enumerate(chunks)
    ]
    db.add_all(db_chunks)
    db.commit()
    for chunk in db_chunks:
        db.refresh(chunk)
    return db_chunks


def get_chunks(db: Session, document_id: str) -> list:
    """Retrieve all chunks for a document ordered by chunk index.

    Args:
        db: Active SQLAlchemy database session.
        document_id: UUID string of the owning document.

    Returns:
        List of :class:`DocumentChunk` instances in ascending ``chunk_index`` order.
    """
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )


def delete_chunks(db: Session, document_id: str) -> int:
    """Delete all chunks for a document.

    Args:
        db: Active SQLAlchemy database session.
        document_id: UUID string of the document whose chunks to remove.

    Returns:
        Number of rows deleted.
    """
    deleted = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .delete()
    )
    db.commit()
    return deleted


def save_material(db: Session, document_id: str, material_type: str, content: Any) -> GeneratedMaterial:
    """Persist a single generated material for a document.

    Args:
        db: Active SQLAlchemy database session.
        document_id: UUID string of the owning document.
        material_type: Category string (``"summary"``, ``"key_concepts"``, or ``"flashcards"``).
        content: Material data — a string for summary, list for key_concepts,
            list of dicts for flashcards.

    Returns:
        The committed :class:`GeneratedMaterial` ORM instance.
    """
    material = GeneratedMaterial(
        document_id=document_id,
        material_type=material_type,
        content=content,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def get_materials(db: Session, document_id: str) -> list:
    """Retrieve all generated materials for a document.

    Args:
        db: Active SQLAlchemy database session.
        document_id: UUID string of the owning document.

    Returns:
        List of :class:`GeneratedMaterial` instances (unordered).
    """
    return (
        db.query(GeneratedMaterial)
        .filter(GeneratedMaterial.document_id == document_id)
        .all()
    )


def delete_materials(db: Session, document_id: str) -> int:
    """Delete all generated materials for a document.

    Args:
        db: Active SQLAlchemy database session.
        document_id: UUID string of the document whose materials to remove.

    Returns:
        Number of rows deleted.
    """
    deleted = (
        db.query(GeneratedMaterial)
        .filter(GeneratedMaterial.document_id == document_id)
        .delete()
    )
    db.commit()
    return deleted
