"""HTTP client for all Learnia service API calls.

Wraps httpx with per-service base URLs configurable via environment variables.
All Python-service endpoints require the X-API-Key header; Java document-service
endpoints are accessed directly without auth enforcement.
"""
import os
from pathlib import Path

import httpx

# Service base URLs — can be overridden per environment
DOC_BASE = os.getenv(
    "LEARNIA_DOC_URL",
    "https://document-service-learnia.2.rahtiapp.fi",
)
AI_BASE = os.getenv(
    "LEARNIA_AI_URL",
    "https://ai-service-learnia.2.rahtiapp.fi",
)
AUTH_BASE = os.getenv(
    "LEARNIA_AUTH_URL",
    "https://auth-service-learnia.2.rahtiapp.fi",
)
EXPORT_BASE = os.getenv(
    "LEARNIA_EXPORT_URL",
    "http://localhost:8004",
)

_DEFAULT_TIMEOUT = 15.0
_AI_TIMEOUT = 90.0  # OpenAI calls can take longer


class APIError(Exception):
    """Raised when an API call returns a non-2xx status or times out."""

    def __init__(self, message: str, status_code: int = 0) -> None:
        """Initialise with a human-readable message and optional HTTP status code."""
        super().__init__(message)
        self.status_code = status_code


class LearniaClient:
    """Thin synchronous wrapper around the Learnia microservice APIs.

    Args:
        api_key: The X-API-Key value used for Python service calls.
    """

    def __init__(self, api_key: str) -> None:
        """Store the API key; build the shared auth header."""
        self._api_key = api_key
        self._auth_headers = {"X-API-Key": api_key}

    # ------------------------------------------------------------------
    # Document Service  (GET / POST / DELETE /documents/*)
    # ------------------------------------------------------------------

    def list_documents(self) -> list[dict]:
        """Return all documents from the document-service.

        Returns:
            List of document dicts with id, title, fileType, status, createdAt.

        Raises:
            APIError: On HTTP error or network failure.
        """
        try:
            r = httpx.get(f"{DOC_BASE}/documents", timeout=_DEFAULT_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    def upload_file(self, file_path: str, title: str) -> dict:
        """Upload a file to the document-service storage.

        Args:
            file_path: Absolute or relative local file path.
            title: Human-readable title for the document.

        Returns:
            Dict with ``fileUrl`` and ``fileName`` from the server.

        Raises:
            APIError: On HTTP error, network failure, or missing file.
        """
        path = Path(file_path)
        if not path.exists():
            raise APIError(f"File not found: {file_path}")
        try:
            with path.open("rb") as fh:
                r = httpx.post(
                    f"{DOC_BASE}/documents/upload",
                    files={"file": (path.name, fh)},
                    params={"title": title},
                    timeout=_DEFAULT_TIMEOUT,
                )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    def create_document(
        self,
        title: str,
        file_name: str,
        file_type: str,
        file_size: int,
        file_url: str,
    ) -> dict:
        """Create a document metadata record and trigger async processing.

        Args:
            title: Document title.
            file_name: Original filename (e.g. ``report.pdf``).
            file_type: MIME or extension type (e.g. ``PDF``).
            file_size: File size in bytes.
            file_url: Path returned by :meth:`upload_file`.

        Returns:
            Created document dict with ``id`` and ``status``.

        Raises:
            APIError: On HTTP error or network failure.
        """
        try:
            r = httpx.post(
                f"{DOC_BASE}/documents",
                json={
                    "title": title,
                    "fileName": file_name,
                    "fileType": file_type,
                    "fileSize": file_size,
                    "fileUrl": file_url,
                    "uploadedBy": "11111111-1111-1111-1111-111111111111",
                    "workspaceId": "22222222-2222-2222-2222-222222222222",
                },
                timeout=_DEFAULT_TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    def delete_document(self, doc_id: str) -> None:
        """Delete a document by ID (returns 204 No Content).

        Args:
            doc_id: UUID string of the document to delete.

        Raises:
            APIError: On HTTP error or network failure.
        """
        try:
            r = httpx.delete(
                f"{DOC_BASE}/documents/{doc_id}", timeout=_DEFAULT_TIMEOUT
            )
            r.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    # ------------------------------------------------------------------
    # AI Service  (GET / POST / DELETE /api/v1/ai/*)
    # ------------------------------------------------------------------

    def get_ai_materials(self, doc_id: str) -> dict:
        """Fetch previously generated AI study materials for a document.

        Args:
            doc_id: UUID string of the document.

        Returns:
            Dict with ``document_id``, ``summary``, ``key_concepts``,
            ``flashcards`` (404 raises APIError).

        Raises:
            APIError: On HTTP error or network failure.
        """
        try:
            r = httpx.get(
                f"{AI_BASE}/api/v1/ai/materials/{doc_id}",
                headers=self._auth_headers,
                timeout=_DEFAULT_TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    def analyze_document(self, doc_id: str) -> dict:
        """Trigger OpenAI analysis for a document and return the result.

        Args:
            doc_id: UUID string of the document to analyse.

        Returns:
            Dict with ``summary``, ``key_concepts``, ``flashcards``.

        Raises:
            APIError: On HTTP error, missing chunks (404), or AI failure (500).
        """
        try:
            r = httpx.post(
                f"{AI_BASE}/api/v1/ai/analyze",
                headers=self._auth_headers,
                json={"document_id": doc_id},
                timeout=_AI_TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    def delete_ai_materials(self, doc_id: str) -> None:
        """Delete all AI-generated materials for a document.

        Args:
            doc_id: UUID string of the document.

        Raises:
            APIError: On HTTP error or network failure.
        """
        try:
            r = httpx.delete(
                f"{AI_BASE}/api/v1/ai/materials/{doc_id}",
                headers=self._auth_headers,
                timeout=_DEFAULT_TIMEOUT,
            )
            r.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    # ------------------------------------------------------------------
    # Auth Service  (GET / POST / DELETE /api/v1/auth/keys)
    # ------------------------------------------------------------------

    def list_api_keys(self, user_id: str) -> list[dict]:
        """List all API keys for the given user.

        Args:
            user_id: UUID string of the user.

        Returns:
            List of key dicts with ``id``, ``note``, ``active``, ``createdAt``.

        Raises:
            APIError: On HTTP error or network failure.
        """
        try:
            r = httpx.get(
                f"{AUTH_BASE}/api/v1/auth/keys",
                params={"userId": user_id},
                timeout=_DEFAULT_TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    def create_api_key(self, user_id: str, note: str) -> dict:
        """Create a new API key for the given user.

        Args:
            user_id: UUID string of the user who will own the key.
            note: Human-readable label for the key.

        Returns:
            Created key dict including ``keyValue`` (shown once only).

        Raises:
            APIError: On HTTP error or network failure.
        """
        try:
            r = httpx.post(
                f"{AUTH_BASE}/api/v1/auth/keys",
                json={"userId": user_id, "note": note},
                timeout=_DEFAULT_TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    def revoke_api_key(self, key_id: str) -> None:
        """Revoke (soft-delete) an API key.

        Args:
            key_id: UUID string of the key to revoke.

        Raises:
            APIError: On HTTP error or network failure.
        """
        try:
            r = httpx.delete(
                f"{AUTH_BASE}/api/v1/auth/keys/{key_id}",
                timeout=_DEFAULT_TIMEOUT,
            )
            r.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    # ------------------------------------------------------------------
    # Export Service  (GET /export/{id}?format=…)
    # ------------------------------------------------------------------

    def export_materials(self, doc_id: str, fmt: str) -> bytes:
        """Download study materials from the export service as a formatted file.

        Args:
            doc_id: UUID string of the document to export.
            fmt: One of ``"markdown"``, ``"anki"``, or ``"text"``.

        Returns:
            Raw file bytes ready to be written to disk.

        Raises:
            APIError: On HTTP error or network failure.
        """
        try:
            r = httpx.get(
                f"{EXPORT_BASE}/export/{doc_id}",
                params={"format": fmt},
                headers=self._auth_headers,
                timeout=_DEFAULT_TIMEOUT,
            )
            r.raise_for_status()
            return r.content
        except httpx.HTTPStatusError as exc:
            raise APIError(str(exc), exc.response.status_code) from exc
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    # ------------------------------------------------------------------
    # Health checks
    # ------------------------------------------------------------------

    def validate_api_key(self) -> bool:
        """Return True when the auth-service accepts the configured API key.

        Calls the authenticated ``/api/v1/auth/validate`` endpoint so that
        an incorrect key is correctly rejected at login time.

        Returns:
            ``True`` if the key is valid and active.

        Raises:
            APIError: On network failure (invalid key returns False, not an error).
        """
        try:
            r = httpx.get(
                f"{AUTH_BASE}/api/v1/auth/validate",
                headers=self._auth_headers,
                timeout=5.0,
            )
            return r.status_code == 200
        except httpx.RequestError as exc:
            raise APIError(f"Network error: {exc}") from exc

    def health(self, service: str) -> bool:
        """Return True when the named service responds with HTTP 200.

        Args:
            service: One of ``"document"``, ``"ai"``, ``"auth"``.

        Returns:
            ``True`` if the service is reachable and healthy.
        """
        urls = {
            "document": f"{DOC_BASE}/actuator/health",
            "ai": f"{AI_BASE}/health",
            "auth": f"{AUTH_BASE}/actuator/health",
        }
        try:
            r = httpx.get(urls[service], timeout=5.0)
            return r.status_code == 200
        except Exception:  # pylint: disable=broad-except
            return False
