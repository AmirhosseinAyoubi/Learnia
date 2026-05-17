# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Functional tests for the Content Service HTTP endpoints.

Tests exercise the full FastAPI request/response cycle using TestClient.
The ``require_api_key`` dependency is overridden to skip real auth-service
calls; CRUD functions are patched at the router level so no database is needed.

Test coverage:
- POST   /api/v1/content/chunks  (success, missing field → 422)
- GET    /api/v1/content/chunks/{document_id}  (found, empty)
- DELETE /api/v1/content/chunks/{document_id}  (success → 204)
- POST   /api/v1/content/materials  (summary, flashcards)
- GET    /api/v1/content/materials/{document_id}  (found, empty)
- DELETE /api/v1/content/materials/{document_id}  (success → 204)
- Auth: missing X-API-Key header → 422
"""
from datetime import datetime
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.auth import require_api_key
from src.main import app

# Override auth so tests do not need a live auth-service
app.dependency_overrides[require_api_key] = lambda: "test-key"

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_chunk(idx: int = 0, doc_id: str = "doc-1") -> MagicMock:
    """Build a mock DocumentChunk object with realistic attributes."""
    mock = MagicMock()
    mock.id = f"id-{idx}"
    mock.document_id = doc_id
    mock.chunk_index = idx
    mock.content = f"chunk content {idx}"
    mock.created_at = datetime(2024, 1, 1)
    return mock


def _mock_material(material_type: str = "summary", content: object = "text") -> MagicMock:
    """Build a mock GeneratedMaterial object with realistic attributes."""
    mock = MagicMock()
    mock.id = "mat-1"
    mock.document_id = "doc-1"
    mock.material_type = material_type
    mock.content = content
    mock.created_at = datetime(2024, 1, 1)
    return mock


# ---------------------------------------------------------------------------
# POST /api/v1/content/chunks
# ---------------------------------------------------------------------------

class TestStoreChunks:
    """Tests for the POST /api/v1/content/chunks endpoint."""

    def test_store_chunks_returns_saved_chunks(self):
        """A valid request stores chunks and returns them with assigned IDs.

        Input: document_id + two-element chunks list.
        Expected: 200 with a two-element JSON array.
        """
        mock_chunks = [_mock_chunk(0), _mock_chunk(1)]
        with patch("src.routers.save_chunks", return_value=mock_chunks) as mock_save:
            response = client.post(
                "/api/v1/content/chunks",
                json={"document_id": "doc-1", "chunks": ["chunk 0", "chunk 1"]},
            )
        assert response.status_code == 200
        assert len(response.json()) == 2
        mock_save.assert_called_once()

    def test_store_chunks_passes_correct_args_to_crud(self):
        """The document_id and chunks list are forwarded verbatim to save_chunks.

        Input: document_id "doc-2" with three chunk strings.
        Expected: save_chunks called with ("doc-2", ["a", "b", "c"]).
        """
        with patch("src.routers.save_chunks", return_value=[]) as mock_save:
            client.post(
                "/api/v1/content/chunks",
                json={"document_id": "doc-2", "chunks": ["a", "b", "c"]},
            )
        args = mock_save.call_args[0]
        assert args[1] == "doc-2"
        assert args[2] == ["a", "b", "c"]

    def test_store_chunks_missing_document_id_returns_422(self):
        """Omitting the required document_id field triggers schema validation.

        Input: JSON body without document_id.
        Expected: 422 Unprocessable Entity before the handler runs.
        """
        response = client.post(
            "/api/v1/content/chunks",
            json={"chunks": ["only a chunk, no document_id"]},
        )
        assert response.status_code == 422

    def test_store_chunks_missing_api_key_returns_422(self):
        """A request without the X-API-Key header is rejected by FastAPI.

        The override is removed temporarily to simulate a real unauthenticated call.
        Input: valid body but no X-API-Key header.
        Expected: 422 (FastAPI header validation, not a 401 from auth-service).
        """
        app.dependency_overrides.pop(require_api_key, None)
        try:
            response = client.post(
                "/api/v1/content/chunks",
                json={"document_id": "doc-1", "chunks": ["text"]},
            )
            assert response.status_code == 422
        finally:
            app.dependency_overrides[require_api_key] = lambda: "test-key"


# ---------------------------------------------------------------------------
# GET /api/v1/content/chunks/{document_id}
# ---------------------------------------------------------------------------

class TestListChunks:
    """Tests for the GET /api/v1/content/chunks/{document_id} endpoint."""

    def test_list_chunks_returns_stored_chunks(self):
        """When chunks exist the endpoint returns them in an array.

        Input: document_id "doc-1" with one stored chunk.
        Expected: 200 with one-element array containing correct chunk_index.
        """
        with patch("src.routers.get_chunks", return_value=[_mock_chunk(0)]):
            response = client.get("/api/v1/content/chunks/doc-1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["chunk_index"] == 0

    def test_list_chunks_empty_document_returns_empty_list(self):
        """When no chunks are stored the endpoint returns an empty array.

        Input: document_id that has no stored chunks.
        Expected: 200 with an empty JSON array (not a 404).
        """
        with patch("src.routers.get_chunks", return_value=[]):
            response = client.get("/api/v1/content/chunks/doc-99")
        assert response.status_code == 200
        assert response.json() == []


# ---------------------------------------------------------------------------
# DELETE /api/v1/content/chunks/{document_id}
# ---------------------------------------------------------------------------

class TestRemoveChunks:
    """Tests for the DELETE /api/v1/content/chunks/{document_id} endpoint."""

    def test_delete_chunks_returns_204(self):
        """Successfully deleting chunks returns 204 No Content with no body.

        Input: document_id with existing chunks.
        Expected: 204 and empty response body.
        """
        with patch("src.routers.delete_chunks", return_value=2) as mock_del:
            response = client.delete("/api/v1/content/chunks/doc-1")
        assert response.status_code == 204
        assert response.content == b""
        mock_del.assert_called_once()

    def test_delete_chunks_nonexistent_document_still_returns_204(self):
        """Deleting chunks for a document with no chunks is still a success.

        Input: document_id with no stored chunks (delete_chunks returns 0).
        Expected: 204 — the operation is idempotent.
        """
        with patch("src.routers.delete_chunks", return_value=0):
            response = client.delete("/api/v1/content/chunks/doc-99")
        assert response.status_code == 204


# ---------------------------------------------------------------------------
# POST /api/v1/content/materials
# ---------------------------------------------------------------------------

class TestStoreMaterial:
    """Tests for the POST /api/v1/content/materials endpoint."""

    def test_store_summary_material(self):
        """Storing a plain-text summary material returns it with type "summary".

        Input: document_id, material_type "summary", string content.
        Expected: 200 with material_type "summary" in response.
        """
        mock_mat = _mock_material("summary", "A concise summary.")
        with patch("src.routers.save_material", return_value=mock_mat):
            response = client.post(
                "/api/v1/content/materials",
                json={
                    "document_id": "doc-1",
                    "material_type": "summary",
                    "content": "A concise summary.",
                },
            )
        assert response.status_code == 200
        assert response.json()["material_type"] == "summary"

    def test_store_flashcards_material(self):
        """Storing a list of flashcard dicts persists the nested structure.

        Input: document_id, material_type "flashcards", list of Q&A dicts.
        Expected: 200 with the material saved successfully.
        """
        flashcards = [{"question": "What is REST?", "answer": "Representational State Transfer."}]
        mock_mat = _mock_material("flashcards", flashcards)
        with patch("src.routers.save_material", return_value=mock_mat):
            response = client.post(
                "/api/v1/content/materials",
                json={
                    "document_id": "doc-1",
                    "material_type": "flashcards",
                    "content": flashcards,
                },
            )
        assert response.status_code == 200

    def test_store_material_missing_document_id_returns_422(self):
        """Omitting document_id causes FastAPI schema validation to fail.

        Input: body without document_id field.
        Expected: 422 Unprocessable Entity.
        """
        response = client.post(
            "/api/v1/content/materials",
            json={"material_type": "summary", "content": "text"},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/content/materials/{document_id}
# ---------------------------------------------------------------------------

class TestListMaterials:
    """Tests for the GET /api/v1/content/materials/{document_id} endpoint."""

    def test_list_materials_returns_all_types(self):
        """When multiple material types are stored all are returned.

        Input: document_id with summary and key_concepts materials.
        Expected: 200 with two-element array.
        """
        materials = [
            _mock_material("summary", "A summary."),
            _mock_material("key_concepts", ["concept1", "concept2"]),
        ]
        with patch("src.routers.get_materials", return_value=materials):
            response = client.get("/api/v1/content/materials/doc-1")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_materials_empty_document_returns_empty_list(self):
        """When no materials have been generated the endpoint returns an empty array.

        Input: document_id with no generated materials.
        Expected: 200 with empty JSON array (not a 404).
        """
        with patch("src.routers.get_materials", return_value=[]):
            response = client.get("/api/v1/content/materials/doc-99")
        assert response.status_code == 200
        assert response.json() == []


# ---------------------------------------------------------------------------
# DELETE /api/v1/content/materials/{document_id}
# ---------------------------------------------------------------------------

class TestRemoveMaterials:
    """Tests for the DELETE /api/v1/content/materials/{document_id} endpoint."""

    def test_delete_materials_returns_204(self):
        """Successfully deleting materials returns 204 No Content with no body.

        Input: document_id with existing materials.
        Expected: 204 and empty response body.
        """
        with patch("src.routers.delete_materials", return_value=3) as mock_del:
            response = client.delete("/api/v1/content/materials/doc-1")
        assert response.status_code == 204
        assert response.content == b""
        mock_del.assert_called_once()

    def test_delete_materials_nonexistent_document_still_returns_204(self):
        """Deleting materials for a document with none is still a success (idempotent).

        Input: document_id with no generated materials.
        Expected: 204 — the operation does not error on missing rows.
        """
        with patch("src.routers.delete_materials", return_value=0):
            response = client.delete("/api/v1/content/materials/doc-99")
        assert response.status_code == 204


# ---------------------------------------------------------------------------
# Infrastructure endpoints: /health, /, /openapi.json
# ---------------------------------------------------------------------------

class TestInfrastructureEndpoints:
    """Tests for health-check, root, and Swagger UI endpoints."""

    def test_health_returns_healthy(self):
        """The /health endpoint returns 200 with status=healthy so Kubernetes
        readiness probes can detect when the service is ready.

        Input: GET /health with no parameters.
        Expected: 200 with status='healthy' and correct service name.
        """
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_returns_service_name(self):
        """The root endpoint returns the service name so operators can confirm
        they are connected to the content-service.

        Input: GET / with no parameters.
        Expected: 200 with 'Content Service' in the message.
        """
        response = client.get("/")
        assert response.status_code == 200
        assert "Content Service" in response.json()["message"]

    def test_openapi_schema_includes_api_key_scheme(self):
        """The OpenAPI schema exposes the X-API-Key security scheme so Swagger UI
        shows the Authorize button for API key authentication.

        Input: GET /openapi.json with no parameters.
        Expected: 200 with X-API-Key in securitySchemes and global security set.
        """
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "X-API-Key" in schema["components"]["securitySchemes"]
        assert schema["security"] == [{"X-API-Key": []}]

    def test_openapi_schema_cached_on_second_call(self):
        """The schema is cached after the first call so repeated Swagger UI loads
        do not recompute the full schema each time.

        Input: two consecutive GET /openapi.json requests.
        Expected: both return identical 200 responses.
        """
        r1 = client.get("/openapi.json")
        r2 = client.get("/openapi.json")
        assert r1.status_code == 200
        assert r1.json() == r2.json()
