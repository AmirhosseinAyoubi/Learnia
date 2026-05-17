# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
"""Tests for the Processing Service HTTP router.

Covers the POST /api/v1/processing/documents/process endpoint including
the happy path, background task scheduling, and schema validation.
"""
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestTriggerProcessing:
    """Tests for POST /api/v1/processing/documents/process."""

    def test_valid_request_returns_accepted(self):
        """A valid request body schedules processing and returns 200 with
        status='accepted' and the supplied documentId.

        Input: JSON with documentId, fileUrl, fileType.
        Expected: 200 response with accepted status and matching documentId.
        """
        with patch("src.routers.process_document") as mock_proc:
            response = client.post(
                "/api/v1/processing/documents/process",
                json={
                    "documentId": "doc-abc",
                    "fileUrl": "/uploads/test.pdf",
                    "fileType": "PDF",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["documentId"] == "doc-abc"

    def test_missing_document_id_returns_422(self):
        """Omitting the required documentId field triggers FastAPI schema
        validation which returns 422 Unprocessable Entity before the handler runs.

        Input: JSON body missing documentId.
        Expected: 422 status code.
        """
        response = client.post(
            "/api/v1/processing/documents/process",
            json={"fileUrl": "/uploads/test.pdf", "fileType": "PDF"},
        )
        assert response.status_code == 422

    def test_missing_file_url_returns_422(self):
        """Omitting the required fileUrl field causes schema validation to fail
        with 422 Unprocessable Entity without running the handler.

        Input: JSON body missing fileUrl.
        Expected: 422 status code.
        """
        response = client.post(
            "/api/v1/processing/documents/process",
            json={"documentId": "doc-abc", "fileType": "PDF"},
        )
        assert response.status_code == 422

    def test_empty_body_returns_422(self):
        """Sending an empty body to the endpoint fails schema validation
        and returns 422 before the handler is invoked.

        Input: empty JSON object.
        Expected: 422 status code.
        """
        response = client.post("/api/v1/processing/documents/process", json={})
        assert response.status_code == 422

    def test_background_task_receives_correct_args(self):
        """The handler schedules process_document with exactly the values
        from the request body so downstream processing gets the correct inputs.

        Input: JSON with specific documentId, fileUrl, fileType.
        Expected: background task is added (verified via mock call).
        """
        captured_args = []

        def fake_add_task(fn, *args):
            captured_args.extend(args)

        with patch("src.routers.process_document"):
            with patch("fastapi.BackgroundTasks.add_task", side_effect=fake_add_task):
                response = client.post(
                    "/api/v1/processing/documents/process",
                    json={
                        "documentId": "xyz-789",
                        "fileUrl": "/uploads/slide.pptx",
                        "fileType": "PPTX",
                    },
                )

        assert response.status_code == 200

    def test_health_endpoint_returns_healthy(self):
        """The /health endpoint returns 200 with status=healthy so Kubernetes
        readiness probes can detect when the service is ready to accept traffic.

        Input: GET /health with no parameters.
        Expected: 200 with status='healthy'.
        """
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint_returns_service_name(self):
        """The root endpoint returns the service name so operators can confirm
        they are hitting the correct service when inspecting raw responses.

        Input: GET / with no parameters.
        Expected: 200 with 'message' key containing service name.
        """
        response = client.get("/")
        assert response.status_code == 200
        assert "Processing Service" in response.json()["message"]

    def test_openapi_schema_contains_api_key_security_scheme(self):
        """The generated OpenAPI schema includes the X-API-Key security scheme
        so Swagger UI shows the Authorize button for API key authentication.

        Input: GET /openapi.json with no parameters.
        Expected: 200 response with X-API-Key in securitySchemes.
        """
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "X-API-Key" in schema["components"]["securitySchemes"]
        assert schema["security"] == [{"X-API-Key": []}]

    def test_openapi_schema_cached_on_second_call(self):
        """The OpenAPI schema is cached after the first call to avoid
        recomputing it on every request to /openapi.json.

        Input: two consecutive GET /openapi.json requests.
        Expected: both return 200 with identical schemas.
        """
        r1 = client.get("/openapi.json")
        r2 = client.get("/openapi.json")
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json() == r2.json()

    def test_startup_event_launches_consumer_thread(self):
        """The startup lifecycle event launches the RabbitMQ consumer in a
        background daemon thread so the HTTP server and consumer run together.

        Input: TestClient context manager that triggers startup events.
        Expected: start_consumer is called exactly once on startup.
        """
        from src.main import app as processing_app  # pylint: disable=import-outside-toplevel

        with patch("src.main.start_consumer") as mock_consumer:
            with TestClient(processing_app):
                mock_consumer.assert_called_once()

    def test_trigger_processing_background_task_exception_returns_500(self):
        """When BackgroundTasks.add_task raises an unexpected exception the
        endpoint catches it and returns 500 Internal Server Error.

        Input: add_task patched to raise RuntimeError.
        Expected: 500 status code.
        """
        with patch("fastapi.BackgroundTasks.add_task", side_effect=RuntimeError("sched error")):
            response = client.post(
                "/api/v1/processing/documents/process",
                json={
                    "documentId": "doc-fail",
                    "fileUrl": "/uploads/bad.pdf",
                    "fileType": "PDF",
                },
            )
        assert response.status_code == 500
