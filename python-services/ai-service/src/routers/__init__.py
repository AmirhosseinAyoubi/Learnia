# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""HTTP router for the AI Service.

Exposes three endpoints:
- ``POST /api/v1/ai/analyze`` — fetch chunks, call OpenAI, persist results
- ``GET  /api/v1/ai/materials/{document_id}`` — retrieve generated materials
- ``DELETE /api/v1/ai/materials/{document_id}`` — delete generated materials
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from ..auth import require_api_key
from ..clients import delete_materials, get_chunks, get_materials, save_material
from ..schemas import AnalyzeRequest, AnalyzeResponse
from ..services import analyze_document

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai"])


@router.post("/api/v1/ai/analyze", response_model=AnalyzeResponse)
async def analyze(
    body: AnalyzeRequest,
    api_key: str = Depends(require_api_key),
) -> dict:
    """Fetch stored chunks for a document, call OpenAI, and persist the results.

    Retrieves text chunks from the content-service, sends them to
    ``gpt-4o-mini`` for summarisation and flashcard generation, then saves
    each generated material (summary, key_concepts, flashcards) back to the
    content-service.

    Args:
        body: Request body containing ``document_id``.
        api_key: Validated API key injected by the ``require_api_key``
            dependency; forwarded to downstream content-service calls.

    Returns:
        ``AnalyzeResponse`` with ``document_id``, ``summary``,
        ``key_concepts``, and ``flashcards``.

    Raises:
        HTTPException: 404 when no chunks exist for the document.
        HTTPException: 500 on any OpenAI or persistence error.
    """
    chunks = get_chunks(body.document_id, api_key)
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found for document")

    try:
        result = analyze_document(body.document_id, chunks)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("OpenAI analysis failed for document=%s: %s", body.document_id, exc)
        raise HTTPException(status_code=500, detail="AI analysis failed") from exc

    save_material(body.document_id, "summary", result["summary"], api_key)
    save_material(body.document_id, "key_concepts", result["key_concepts"], api_key)
    save_material(body.document_id, "flashcards", result["flashcards"], api_key)

    return result


@router.get("/api/v1/ai/materials/{document_id}")
async def list_materials(
    document_id: str,
    api_key: str = Depends(require_api_key),
) -> dict:
    """Return all AI-generated materials for a document as a single object.

    Fetches the persisted materials from the content-service and reshapes
    them into a flat dict keyed by material type (e.g. ``summary``,
    ``key_concepts``, ``flashcards``).

    Args:
        document_id: UUID string of the document.
        api_key: Validated API key forwarded to content-service.

    Returns:
        Dict with ``document_id`` plus one key per material type.

    Raises:
        HTTPException: 404 when no materials have been generated yet.
    """
    materials = get_materials(document_id, api_key)
    if not materials:
        raise HTTPException(status_code=404, detail="No materials found for document")

    result: dict = {"document_id": document_id}
    for material in materials:
        result[material["material_type"]] = material["content"]
    return result


@router.delete("/api/v1/ai/materials/{document_id}", status_code=204)
async def remove_materials(
    document_id: str,
    api_key: str = Depends(require_api_key),
) -> Response:
    """Delete all AI-generated materials for a document.

    Proxies the delete request to the content-service, which removes all
    ``generated_materials`` rows for the given document.

    Args:
        document_id: UUID string of the document.
        api_key: Validated API key forwarded to content-service.

    Returns:
        204 No Content on success.
    """
    delete_materials(document_id, api_key)
    return Response(status_code=204)
