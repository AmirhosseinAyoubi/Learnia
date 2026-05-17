# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Export router — fetches AI materials and converts them to study formats.

Exposes a single endpoint:

    GET /export/{document_id}?format=<markdown|anki|text>

The route fetches JSON materials from the ai-service, delegates conversion
to the appropriate formatter, and returns the result as a downloadable file.
"""
import logging
from typing import Annotated, Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from ..auth import require_api_key
from ..config import settings
from ..formatters.anki_csv import to_anki_csv
from ..formatters.markdown import to_markdown
from ..formatters.plain_text import to_plain_text

logger = logging.getLogger(__name__)

router = APIRouter(tags=["export"])

ExportFormat = Literal["markdown", "anki", "text"]

_MEDIA_TYPES: dict[str, str] = {
    "markdown": "text/markdown; charset=utf-8",
    "anki": "text/tab-separated-values; charset=utf-8",
    "text": "text/plain; charset=utf-8",
}

_EXTENSIONS: dict[str, str] = {
    "markdown": "md",
    "anki": "txt",
    "text": "txt",
}


async def _fetch_materials(document_id: str, api_key: str) -> dict:
    """Call the ai-service and return the materials dict.

    Args:
        document_id: UUID of the document whose materials to fetch.
        api_key: Validated X-API-Key forwarded from the incoming request.

    Returns:
        Materials dict with ``summary``, ``key_concepts``, ``flashcards``.

    Raises:
        HTTPException: 404 when the ai-service has no materials for the doc.
        HTTPException: 502 on any other ai-service error or network failure.
    """
    url = f"{settings.ai_service_url}/api/v1/ai/materials/{document_id}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers={"X-API-Key": api_key})
    except httpx.RequestError as exc:
        logger.error("Failed to reach ai-service: %s", exc)
        raise HTTPException(status_code=502, detail="AI service unreachable") from exc

    if resp.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="No AI materials found for this document. Run analysis first.",
        )
    if resp.status_code != 200:
        logger.error("ai-service returned %d for document %s", resp.status_code, document_id)
        raise HTTPException(
            status_code=502,
            detail=f"AI service error (HTTP {resp.status_code})",
        )

    return resp.json()


@router.get(
    "/export/{document_id}",
    summary="Export AI study materials",
    response_description="Downloadable study file in the requested format",
)
async def export_materials(
    document_id: str,
    fmt: Annotated[
        ExportFormat,
        Query(
            alias="format",
            description=(
                "**markdown** — structured Markdown study guide (default)\n\n"
                "**anki** — Anki-importable tab-separated flashcards\n\n"
                "**text** — plain-text study sheet for printing / note apps"
            ),
        ),
    ] = "markdown",
    api_key: str = Depends(require_api_key),
) -> Response:
    """Fetch AI-generated materials for *document_id* and convert to the
    requested study format.

    The export service acts as a transformation layer: it pulls raw JSON from
    the ai-service and converts it to a portable, human-readable file.  This
    separation keeps format-specific logic out of the ai-service, which is
    responsible only for generating and storing structured data.

    Args:
        document_id: UUID of the document to export.
        fmt: Target format — one of ``markdown``, ``anki``, or ``text``.
        api_key: Validated API key (injected by ``require_api_key``).

    Returns:
        File download response with an appropriate ``Content-Disposition``
        header and MIME type for the chosen format.

    Raises:
        HTTPException 404: Document has no AI materials yet.
        HTTPException 502: ai-service is unreachable or returned an error.
        HTTPException 401: API key is invalid or inactive.
        HTTPException 503: Auth service is unreachable.
    """
    data = await _fetch_materials(document_id, api_key)

    short_id = document_id[:8]
    ext = _EXTENSIONS[fmt]

    if fmt == "markdown":
        body = to_markdown(data)
        filename = f"{short_id}-study-guide.{ext}"
    elif fmt == "anki":
        body = to_anki_csv(data)
        filename = f"{short_id}-anki-cards.{ext}"
    else:
        body = to_plain_text(data)
        filename = f"{short_id}-notes.{ext}"

    return Response(
        content=body,
        media_type=_MEDIA_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
