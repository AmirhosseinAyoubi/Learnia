# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""FastAPI dependency for stateless API-key authentication.

Validates the ``X-API-Key`` header on every protected request by forwarding
it to the auth-service ``/api/v1/auth/validate`` endpoint.  The content-service
itself holds no session state.
"""
import httpx
from fastapi import Header, HTTPException

from .config import settings


async def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """Validate the ``X-API-Key`` header against the auth-service.

    Args:
        x_api_key: Value of the ``X-API-Key`` request header.
            FastAPI raises 422 automatically when the header is absent.

    Returns:
        The validated API key string (passed through so it can be forwarded
        to downstream service calls).

    Raises:
        HTTPException: 401 when the auth-service reports the key as invalid
            or inactive.
        HTTPException: 503 when the auth-service is unreachable.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.auth_service_url}/api/v1/auth/validate",
                headers={"X-API-Key": x_api_key},
            )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=503, detail="Authentication service unavailable"
        ) from exc
    return x_api_key
