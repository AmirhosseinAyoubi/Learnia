# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""HTTP client helpers for communicating with the content-service.

Every function opens a short-lived httpx.Client, performs one request,
and raises on non-2xx status so the caller can decide how to handle it.
"""
import logging
from typing import Any

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


def get_chunks(document_id: str, api_key: str) -> list:
    """Fetch stored text chunks for a document from the content-service.

    Args:
        document_id: UUID string of the document.
        api_key: Valid ``X-API-Key`` value for authentication.

    Returns:
        Ordered list of chunk text strings.

    Raises:
        httpx.HTTPStatusError: On non-2xx response.
        httpx.ConnectError: When the content-service is unreachable.
    """
    url = f"{settings.content_service_url}/api/v1/content/chunks/{document_id}"
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url, headers={"X-API-Key": api_key})
        response.raise_for_status()
    return [chunk["content"] for chunk in response.json()]


def save_material(
    document_id: str,
    material_type: str,
    content: Any,
    api_key: str,
) -> None:
    """Persist a single generated material to the content-service.

    Args:
        document_id: UUID string of the owning document.
        material_type: One of ``"summary"``, ``"key_concepts"``, or ``"flashcards"``.
        content: The material data (string, list, or list of dicts).
        api_key: Valid ``X-API-Key`` value for authentication.

    Raises:
        httpx.HTTPStatusError: On non-2xx response.
        httpx.ConnectError: When the content-service is unreachable.
    """
    url = f"{settings.content_service_url}/api/v1/content/materials"
    payload = {
        "document_id": document_id,
        "material_type": material_type,
        "content": content,
    }
    with httpx.Client(timeout=10.0) as client:
        response = client.post(url, json=payload, headers={"X-API-Key": api_key})
        response.raise_for_status()


def get_materials(document_id: str, api_key: str) -> list:
    """Retrieve all generated materials for a document from the content-service.

    Args:
        document_id: UUID string of the document.
        api_key: Valid ``X-API-Key`` value for authentication.

    Returns:
        List of material dicts with ``material_type`` and ``content`` keys.

    Raises:
        httpx.HTTPStatusError: On non-2xx response.
        httpx.ConnectError: When the content-service is unreachable.
    """
    url = f"{settings.content_service_url}/api/v1/content/materials/{document_id}"
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url, headers={"X-API-Key": api_key})
        response.raise_for_status()
    return response.json()


def delete_materials(document_id: str, api_key: str) -> None:
    """Delete all generated materials for a document via the content-service.

    Args:
        document_id: UUID string of the document.
        api_key: Valid ``X-API-Key`` value for authentication.

    Raises:
        httpx.HTTPStatusError: On non-2xx response.
        httpx.ConnectError: When the content-service is unreachable.
    """
    url = f"{settings.content_service_url}/api/v1/content/materials/{document_id}"
    with httpx.Client(timeout=10.0) as client:
        response = client.delete(url, headers={"X-API-Key": api_key})
        response.raise_for_status()
    logger.info("Deleted materials for document_id=%s", document_id)
