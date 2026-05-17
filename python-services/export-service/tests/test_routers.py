# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Integration tests for the export router and infrastructure endpoints."""
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.auth import require_api_key
from src.main import app

SAMPLE_MATERIALS = {
    "document_id": "doc-1234",
    "summary": "Test summary.",
    "key_concepts": ["Alpha", "Beta"],
    "flashcards": [
        {"question": "What is Alpha?", "answer": "The first letter."},
    ],
}

VALID_KEY = "test-api-key"


def _auth_ok() -> str:
    """Stub that bypasses real auth-service validation."""
    return VALID_KEY


def _export_client(materials: dict = SAMPLE_MATERIALS) -> TestClient:
    """Build a TestClient with auth bypassed and ai-service call mocked."""
    app.dependency_overrides[require_api_key] = _auth_ok
    client = TestClient(app)

    def _patched_fetch(document_id: str, api_key: str) -> dict:  # noqa: ARG001
        return materials

    client._export_patch = patch(  # type: ignore[attr-defined]
        "src.routers.export._fetch_materials",
        new=AsyncMock(side_effect=_patched_fetch),
    )
    return client


class TestInfrastructureEndpoints:
    """Tests for /health and / endpoints."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_health_returns_200(self):
        """Health endpoint is always accessible without auth."""
        resp = TestClient(app).get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
        assert resp.json()["service"] == "export-service"

    def test_root_lists_formats(self):
        """Root endpoint advertises all three supported formats."""
        data = TestClient(app).get("/").json()
        assert "markdown" in data["formats"]
        assert "anki" in data["formats"]
        assert "text" in data["formats"]

    def test_openapi_schema_contains_security_scheme(self):
        """OpenAPI spec includes the X-API-Key security scheme."""
        schema = TestClient(app).get("/openapi.json").json()
        assert "X-API-Key" in schema["components"]["securitySchemes"]

    def test_openapi_global_security(self):
        """OpenAPI spec applies the security scheme globally."""
        schema = TestClient(app).get("/openapi.json").json()
        assert {"X-API-Key": []} in schema["security"]


class TestExportEndpoint:
    """Tests for GET /export/{document_id}."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_markdown_export_returns_200(self):
        """Markdown export returns 200 with text/markdown content-type."""
        app.dependency_overrides[require_api_key] = _auth_ok
        with patch(
            "src.routers.export._fetch_materials",
            new=AsyncMock(return_value=SAMPLE_MATERIALS),
        ):
            resp = TestClient(app).get(
                "/export/doc-1234",
                params={"format": "markdown"},
                headers={"X-API-Key": VALID_KEY},
            )
        assert resp.status_code == 200
        assert "text/markdown" in resp.headers["content-type"]
        assert "Test summary." in resp.text

    def test_anki_export_returns_200(self):
        """Anki export returns 200 with Anki TSV header lines."""
        app.dependency_overrides[require_api_key] = _auth_ok
        with patch(
            "src.routers.export._fetch_materials",
            new=AsyncMock(return_value=SAMPLE_MATERIALS),
        ):
            resp = TestClient(app).get(
                "/export/doc-1234",
                params={"format": "anki"},
                headers={"X-API-Key": VALID_KEY},
            )
        assert resp.status_code == 200
        assert "#separator:tab" in resp.text
        assert "What is Alpha?" in resp.text

    def test_text_export_returns_200(self):
        """Plain-text export returns 200 with LEARNIA header."""
        app.dependency_overrides[require_api_key] = _auth_ok
        with patch(
            "src.routers.export._fetch_materials",
            new=AsyncMock(return_value=SAMPLE_MATERIALS),
        ):
            resp = TestClient(app).get(
                "/export/doc-1234",
                params={"format": "text"},
                headers={"X-API-Key": VALID_KEY},
            )
        assert resp.status_code == 200
        assert "LEARNIA STUDY NOTES" in resp.text

    def test_default_format_is_markdown(self):
        """Omitting the format param defaults to Markdown output."""
        app.dependency_overrides[require_api_key] = _auth_ok
        with patch(
            "src.routers.export._fetch_materials",
            new=AsyncMock(return_value=SAMPLE_MATERIALS),
        ):
            resp = TestClient(app).get(
                "/export/doc-1234", headers={"X-API-Key": VALID_KEY}
            )
        assert resp.status_code == 200
        assert "text/markdown" in resp.headers["content-type"]

    def test_content_disposition_has_short_id(self):
        """Content-Disposition attachment filename includes the short document ID."""
        app.dependency_overrides[require_api_key] = _auth_ok
        with patch(
            "src.routers.export._fetch_materials",
            new=AsyncMock(return_value=SAMPLE_MATERIALS),
        ):
            resp = TestClient(app).get(
                "/export/doc-1234", headers={"X-API-Key": VALID_KEY}
            )
        assert "attachment" in resp.headers["content-disposition"]
        assert "doc-123" in resp.headers["content-disposition"]

    def test_invalid_format_returns_422(self):
        """An unsupported format value triggers a 422 validation error."""
        app.dependency_overrides[require_api_key] = _auth_ok
        resp = TestClient(app).get(
            "/export/doc-1234",
            params={"format": "pdf"},
            headers={"X-API-Key": VALID_KEY},
        )
        assert resp.status_code == 422

    def test_missing_api_key_returns_422(self):
        """A request without X-API-Key header returns 422."""
        resp = TestClient(app).get("/export/doc-1234")
        assert resp.status_code == 422
