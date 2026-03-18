"""
conftest.py — shared fixtures for all functional tests.

Sets up base URLs and provides a registered+logged-in user
so individual test modules don't repeat the setup boilerplate.

Services are expected to be running locally (or via Docker) at:
  Auth service    : AUTH_BASE_URL  (default http://localhost:8081)
  Document service: DOC_BASE_URL   (default http://localhost:8084)

Override with environment variables if your setup differs.
"""

import os
import uuid

import pytest
import requests

# ── base URLs ─────────────────────────────────────────────────────────────────
AUTH_BASE = os.getenv("AUTH_BASE_URL", "http://localhost:8081/api/v1/auth")
DOC_BASE  = os.getenv("DOC_BASE_URL",  "http://localhost:8084/api/v1/documents")

# ── helpers ───────────────────────────────────────────────────────────────────

def unique_email():
    """Return a unique email so parallel test runs don't collide."""
    return f"test_{uuid.uuid4().hex[:8]}@learnia.test"


# ── session-scoped fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="session")
def registered_user():
    """
    Register a fresh user once per test session.
    Returns the full registration response body (dict).
    Fails fast if the auth service is unreachable.
    """
    payload = {
        "email":     unique_email(),
        "username":  f"tester_{uuid.uuid4().hex[:6]}",
        "password":  "TestPass123!",
        "firstName": "Test",
        "lastName":  "User",
    }
    resp = requests.post(f"{AUTH_BASE}/register", json=payload, timeout=10)
    assert resp.status_code == 201, (
        f"Registration failed ({resp.status_code}): {resp.text}"
    )
    return {"credentials": payload, "response": resp.json()}


@pytest.fixture(scope="session")
def auth_tokens(registered_user):
    """
    Log in with the session user and return access + refresh tokens.
    """
    creds = registered_user["credentials"]
    resp = requests.post(
        f"{AUTH_BASE}/login",
        json={"email": creds["email"], "password": creds["password"]},
        timeout=10,
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()


@pytest.fixture(scope="session")
def auth_headers(auth_tokens):
    """Bearer Authorization header ready for use in requests."""
    return {"Authorization": f"Bearer {auth_tokens['accessToken']}"}
