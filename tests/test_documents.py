"""
test_documents.py — functional tests for the Document Service.

Covers every endpoint defined in the wiki resource table:
  GET  /api/v1/documents
  GET  /api/v1/documents/{id}
  POST /api/v1/documents
  POST /api/v1/documents/upload

Each test checks:
  - correct HTTP status code
  - expected response fields
  - _links presence (HATEOAS / Connectedness)
  - error handling for invalid inputs
"""

import io
import uuid

import pytest
import requests

from conftest import DOC_BASE


# ── helpers ───────────────────────────────────────────────────────────────────

def _create_doc_payload(uploader_id: str = None) -> dict:
    """Return a minimal valid CreateDocumentRequest body."""
    return {
        "title":      f"Test Doc {uuid.uuid4().hex[:6]}",
        "fileName":   "lecture.pdf",
        "fileType":   "PDF",
        "fileSize":   1024000,
        "fileUrl":    "/uploads/lecture.pdf",
        "uploadedBy": uploader_id or str(uuid.uuid4()),
        "workspaceId": str(uuid.uuid4()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/documents
# ─────────────────────────────────────────────────────────────────────────────

class TestListDocuments:

    def test_list_returns_200(self, auth_headers):
        """GET /documents must return 200 OK with a list."""
        resp = requests.get(DOC_BASE, headers=auth_headers, timeout=10)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_items_have_self_link(self, auth_headers):
        """
        Each document in the list must have a _links.self entry
        pointing to its individual resource URI.
        """
        # ensure at least one document exists
        requests.post(DOC_BASE, json=_create_doc_payload(), headers=auth_headers, timeout=10)

        resp = requests.get(DOC_BASE, headers=auth_headers, timeout=10)
        docs = resp.json()

        if docs:  # only assert if there is something to check
            for doc in docs:
                assert "_links" in doc, "Document in list missing _links"
                assert "self"   in doc["_links"], "Document in list missing _links.self"
                expected_href = f"/api/v1/documents/{doc['id']}"
                assert doc["_links"]["self"]["href"] == expected_href

    def test_list_without_auth_returns_401(self):
        """GET /documents without a token must return 401."""
        resp = requests.get(DOC_BASE, timeout=10)
        assert resp.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/v1/documents
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateDocument:

    def test_create_returns_201(self, auth_headers):
        """Valid POST must return 201 Created with the new document."""
        resp = requests.post(
            DOC_BASE,
            json=_create_doc_payload(),
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "id"    in body
        assert "title" in body

    def test_create_returns_hateoas_links(self, auth_headers):
        """Created document response must include _links with self and collection."""
        resp = requests.post(
            DOC_BASE,
            json=_create_doc_payload(),
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 201
        links = resp.json().get("_links", {})
        assert "self"       in links
        assert "collection" in links
        assert links["collection"]["href"] == "/api/v1/documents"

    def test_create_uploader_link_present(self, auth_headers):
        """If uploadedBy is set, _links must include an uploader link."""
        uploader_id = str(uuid.uuid4())
        resp = requests.post(
            DOC_BASE,
            json=_create_doc_payload(uploader_id=uploader_id),
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 201
        links = resp.json().get("_links", {})
        assert "uploader" in links
        assert f"/api/v1/users/{uploader_id}" in links["uploader"]["href"]

    def test_create_without_auth_returns_401(self):
        """POST without a token must return 401."""
        resp = requests.post(DOC_BASE, json=_create_doc_payload(), timeout=10)
        assert resp.status_code == 401

    def test_create_empty_body_returns_400(self, auth_headers):
        """POST with an empty body must return 400 Bad Request."""
        resp = requests.post(DOC_BASE, json={}, headers=auth_headers, timeout=10)
        assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/documents/{id}
# ─────────────────────────────────────────────────────────────────────────────

class TestGetDocumentById:

    @pytest.fixture(scope="class")
    def created_doc(self, auth_headers):
        """Create one document to reuse across get-by-id tests."""
        resp = requests.post(
            DOC_BASE,
            json=_create_doc_payload(),
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 201
        return resp.json()

    def test_get_by_id_returns_200(self, auth_headers, created_doc):
        """GET /documents/{id} for an existing document must return 200."""
        resp = requests.get(
            f"{DOC_BASE}/{created_doc['id']}",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == created_doc["id"]

    def test_get_by_id_has_hateoas_links(self, auth_headers, created_doc):
        """Single document response must include self and collection links."""
        resp = requests.get(
            f"{DOC_BASE}/{created_doc['id']}",
            headers=auth_headers,
            timeout=10,
        )
        links = resp.json().get("_links", {})
        assert "self"       in links
        assert "collection" in links
        assert links["self"]["href"] == f"/api/v1/documents/{created_doc['id']}"

    def test_get_nonexistent_id_returns_404(self, auth_headers):
        """GET /documents/{id} for an unknown UUID must return 404."""
        resp = requests.get(
            f"{DOC_BASE}/{uuid.uuid4()}",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 404

    def test_get_invalid_uuid_returns_400(self, auth_headers):
        """GET /documents/not-a-uuid must return 400 Bad Request."""
        resp = requests.get(
            f"{DOC_BASE}/not-a-uuid",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 400

    def test_get_by_id_without_auth_returns_401(self, created_doc):
        """GET /documents/{id} without a token must return 401."""
        resp = requests.get(f"{DOC_BASE}/{created_doc['id']}", timeout=10)
        assert resp.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/v1/documents/upload
# ─────────────────────────────────────────────────────────────────────────────

class TestUploadDocument:

    def test_upload_returns_200(self, auth_headers):
        """Valid file upload must return 200 OK with a success message."""
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake pdf content")
        resp = requests.post(
            f"{DOC_BASE}/upload",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            data={"title": "Test Upload"},
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        assert "uploaded successfully" in resp.text

    def test_upload_without_auth_returns_401(self):
        """Upload without a token must return 401."""
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")
        resp = requests.post(
            f"{DOC_BASE}/upload",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            data={"title": "No Auth"},
            timeout=10,
        )
        assert resp.status_code == 401

    def test_upload_missing_file_returns_400(self, auth_headers):
        """Upload without a file field must return 400 Bad Request."""
        resp = requests.post(
            f"{DOC_BASE}/upload",
            data={"title": "Missing File"},
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 400
