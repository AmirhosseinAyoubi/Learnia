# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""HTTP router for the Content Service.

Exposes four resource endpoints covering the full range of HTTP verbs:

- ``POST   /api/v1/content/chunks``              — store chunks
- ``GET    /api/v1/content/chunks/{document_id}`` — retrieve chunks
- ``DELETE /api/v1/content/chunks/{document_id}`` — delete chunks
- ``POST   /api/v1/content/materials``              — store a material
- ``GET    /api/v1/content/materials/{document_id}`` — retrieve materials
- ``DELETE /api/v1/content/materials/{document_id}`` — delete materials
"""
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..auth import require_api_key
from ..crud import (
    delete_chunks,
    delete_materials,
    get_chunks,
    get_materials,
    save_chunks,
    save_material,
)
from ..database import get_db
from ..schemas import ChunkResponse, ChunksCreate, MaterialCreate, MaterialResponse

router = APIRouter()


@router.post("/api/v1/content/chunks", response_model=list[ChunkResponse])
async def store_chunks(
    body: ChunksCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> list:
    """Store a batch of text chunks extracted from a document.

    Args:
        body: Request body with ``document_id`` and ordered ``chunks`` list.
        db: Database session injected by FastAPI.
        _: Validated API key (checked but not used directly).

    Returns:
        List of persisted chunk objects with assigned IDs and indices.
    """
    return save_chunks(db, body.document_id, body.chunks)


@router.get("/api/v1/content/chunks/{document_id}", response_model=list[ChunkResponse])
async def list_chunks(
    document_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> list:
    """Retrieve all stored chunks for a document in index order.

    Args:
        document_id: UUID string of the document.
        db: Database session injected by FastAPI.
        _: Validated API key.

    Returns:
        Ordered list of chunk objects (empty list if none stored).
    """
    return get_chunks(db, document_id)


@router.delete("/api/v1/content/chunks/{document_id}", status_code=204)
async def remove_chunks(
    document_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> Response:
    """Delete all stored chunks for a document.

    Args:
        document_id: UUID string of the document.
        db: Database session injected by FastAPI.
        _: Validated API key.

    Returns:
        204 No Content.
    """
    delete_chunks(db, document_id)
    return Response(status_code=204)


@router.post("/api/v1/content/materials", response_model=MaterialResponse)
async def store_material(
    body: MaterialCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> object:
    """Store a single AI-generated material for a document.

    Args:
        body: Request body with ``document_id``, ``material_type``, and ``content``.
        db: Database session injected by FastAPI.
        _: Validated API key.

    Returns:
        The persisted material object with its assigned ID.
    """
    return save_material(db, body.document_id, body.material_type, body.content)


@router.get("/api/v1/content/materials/{document_id}", response_model=list[MaterialResponse])
async def list_materials(
    document_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> list:
    """Retrieve all generated materials for a document.

    Args:
        document_id: UUID string of the document.
        db: Database session injected by FastAPI.
        _: Validated API key.

    Returns:
        List of material objects (empty list if none stored).
    """
    return get_materials(db, document_id)


@router.delete("/api/v1/content/materials/{document_id}", status_code=204)
async def remove_materials(
    document_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> Response:
    """Delete all generated materials for a document.

    Args:
        document_id: UUID string of the document.
        db: Database session injected by FastAPI.
        _: Validated API key.

    Returns:
        204 No Content.
    """
    delete_materials(db, document_id)
    return Response(status_code=204)
