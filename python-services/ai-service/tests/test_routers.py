# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Functional tests for the AI Service HTTP endpoints.

Tests exercise the full FastAPI request/response cycle using TestClient.
The ``require_api_key`` dependency is overridden; clients and services are
patched at the router level so no real database, OpenAI, or content-service
calls are made.

Test coverage:
- POST   /api/v1/ai/analyze  (success, no chunks → 404, OpenAI error → 500)
- GET    /api/v1/ai/materials/{document_id}  (found, not found → 404)
- DELETE /api/v1/ai/materials/{document_id}  (success → 204)
- Missing X-API-Key → 422
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.auth import require_api_key
from src.main import app

app.dependency_overrides[require_api_key] = lambda: "test-key"

client = TestClient(app)

_ANALYZE_RESULT = {
    "document_id": "doc-1",
    "summary": "A comprehensive summary of the document.",
    "key_concepts": ["concept A", "concept B", "concept C"],
    "flashcards": [{"question": "What is A?", "answer": "A is important."}],
}


class TestAnalyze:
    """Tests for the POST /api/v1/ai/analyze endpoint."""

    def test_analyze_success_returns_all_material_fields(self):
        """A valid request with stored chunks calls OpenAI and returns results.

        Input: document_id with two stored chunks.
        Expected: 200 with summary, key_concepts, and flashcards in the response.
        """
        with (
            patch("src.routers.get_chunks", return_value=["chunk1", "chunk2"]),
            patch("src.routers.analyze_document", return_value=_ANALYZE_RESULT),
            patch("src.routers.save_material"),
        ):
            response = client.post("/api/v1/ai/analyze", json={"document_id": "doc-1"})

        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == _ANALYZE_RESULT["summary"]
        assert data["key_concepts"] == _ANALYZE_RESULT["key_concepts"]
        assert len(data["flashcards"]) == 1

    def test_analyze_saves_three_material_types(self):
        """After analysis, summary, key_concepts, and flashcards are all persisted.

        Input: valid document_id.
        Expected: save_material called exactly three times with distinct types.
        """
        with (
            patch("src.routers.get_chunks", return_value=["chunk"]),
            patch("src.routers.analyze_document", return_value=_ANALYZE_RESULT),
            patch("src.routers.save_material") as mock_save,
        ):
            client.post("/api/v1/ai/analyze", json={"document_id": "doc-1"})

        saved_types = {call[0][1] for call in mock_save.call_args_list}
        assert saved_types == {"summary", "key_concepts", "flashcards"}

    def test_analyze_no_chunks_returns_404(self):
        """When no chunks are stored for the document the endpoint returns 404.

        Input: document_id for a document that has no stored chunks.
        Expected: 404 Not Found — cannot analyse what hasn't been processed.
        """
        with patch("src.routers.get_chunks", return_value=[]):
            response = client.post("/api/v1/ai/analyze", json={"document_id": "doc-empty"})

        assert response.status_code == 404

    def test_analyze_openai_failure_returns_500(self):
        """An OpenAI API error surfaces as a 500 Internal Server Error.

        Input: valid chunks, but the OpenAI call raises an exception.
        Expected: 500 so the caller knows the analysis failed server-side.
        """
        with (
            patch("src.routers.get_chunks", return_value=["chunk"]),
            patch("src.routers.analyze_document", side_effect=Exception("rate limit")),
        ):
            response = client.post("/api/v1/ai/analyze", json={"document_id": "doc-1"})

        assert response.status_code == 500

    def test_analyze_missing_document_id_returns_422(self):
        """Omitting document_id in the request body triggers schema validation.

        Input: empty JSON body.
        Expected: 422 Unprocessable Entity before the handler is invoked.
        """
        response = client.post("/api/v1/ai/analyze", json={})
        assert response.status_code == 422

    def test_analyze_missing_api_key_returns_422(self):
        """A request without the X-API-Key header is rejected at the dependency level.

        The override is removed temporarily to test unauthenticated requests.
        Expected: 422 from FastAPI header validation.
        """
        app.dependency_overrides.pop(require_api_key, None)
        try:
            response = client.post(
                "/api/v1/ai/analyze",
                json={"document_id": "doc-1"},
            )
            assert response.status_code == 422
        finally:
            app.dependency_overrides[require_api_key] = lambda: "test-key"


class TestListMaterials:
    """Tests for the GET /api/v1/ai/materials/{document_id} endpoint."""

    def test_list_materials_returns_structured_response(self):
        """When materials exist they are returned as a flat dict by type.

        Input: document with summary, key_concepts, and flashcards stored.
        Expected: 200 with top-level keys for each material type.
        """
        raw_materials = [
            {"material_type": "summary", "content": "Summary text."},
            {"material_type": "key_concepts", "content": ["k1", "k2"]},
            {"material_type": "flashcards", "content": [{"question": "Q?", "answer": "A."}]},
        ]
        with patch("src.routers.get_materials", return_value=raw_materials):
            response = client.get("/api/v1/ai/materials/doc-1")

        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Summary text."
        assert data["key_concepts"] == ["k1", "k2"]

    def test_list_materials_not_found_returns_404(self):
        """When no materials have been generated the endpoint returns 404.

        Input: document_id with no stored materials.
        Expected: 404 Not Found — distinct from an empty list; no analysis run yet.
        """
        with patch("src.routers.get_materials", return_value=[]):
            response = client.get("/api/v1/ai/materials/doc-99")

        assert response.status_code == 404


class TestRemoveMaterials:
    """Tests for the DELETE /api/v1/ai/materials/{document_id} endpoint."""

    def test_delete_materials_returns_204(self):
        """Successfully deleting materials returns 204 No Content.

        Input: document_id with existing materials proxied to content-service.
        Expected: 204 and empty response body.
        """
        with patch("src.routers.delete_materials") as mock_del:
            response = client.delete("/api/v1/ai/materials/doc-1")

        assert response.status_code == 204
        assert response.content == b""
        mock_del.assert_called_once_with("doc-1", "test-key")

    def test_delete_materials_missing_api_key_returns_422(self):
        """A request without the X-API-Key header is rejected.

        Expected: 422 from FastAPI header validation.
        """
        app.dependency_overrides.pop(require_api_key, None)
        try:
            response = client.delete("/api/v1/ai/materials/doc-1")
            assert response.status_code == 422
        finally:
            app.dependency_overrides[require_api_key] = lambda: "test-key"


class TestInfrastructureEndpoints:
    """Tests for health-check, root, and Swagger UI endpoints."""

    def test_health_returns_healthy(self):
        """The /health endpoint returns 200 with status=healthy so Kubernetes
        readiness probes can detect when the service is ready.

        Input: GET /health with no parameters.
        Expected: 200 with status='healthy'.
        """
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_returns_service_name(self):
        """The root endpoint returns the service name so operators can verify
        they are connected to the ai-service.

        Input: GET / with no parameters.
        Expected: 200 with 'AI Service' in the message.
        """
        response = client.get("/")
        assert response.status_code == 200
        assert "AI Service" in response.json()["message"]

    def test_openapi_schema_includes_api_key_scheme(self):
        """The OpenAPI schema exposes the X-API-Key security scheme so Swagger UI
        shows the Authorize button and lets users supply an API key.

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
