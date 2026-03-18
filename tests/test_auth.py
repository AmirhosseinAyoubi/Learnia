"""
test_auth.py — functional tests for the Auth Service.

Covers every endpoint defined in the wiki resource table:
  POST /api/v1/auth/register
  POST /api/v1/auth/login
  GET  /api/v1/auth/me
  POST /api/v1/auth/refresh
  POST /api/v1/auth/logout

Each test checks:
  - correct HTTP status code
  - expected response fields
  - _links presence (HATEOAS / Connectedness)
  - error handling for invalid inputs
"""

import uuid

import pytest
import requests

from conftest import AUTH_BASE, unique_email


# ─────────────────────────────────────────────────────────────────────────────
# POST /register
# ─────────────────────────────────────────────────────────────────────────────

class TestRegister:

    def test_register_success_returns_201(self):
        """Valid registration must return 201 Created with tokens and user."""
        payload = {
            "email":     unique_email(),
            "username":  f"u_{uuid.uuid4().hex[:6]}",
            "password":  "StrongPass1!",
            "firstName": "Alice",
            "lastName":  "Smith",
        }
        resp = requests.post(f"{AUTH_BASE}/register", json=payload, timeout=10)

        assert resp.status_code == 201
        body = resp.json()
        assert "accessToken" in body
        assert "refreshToken" in body
        assert body["user"]["email"] == payload["email"]
        assert body["user"]["username"] == payload["username"]

    def test_register_returns_hateoas_links(self):
        """Registration response must include _links for navigation."""
        payload = {
            "email":     unique_email(),
            "username":  f"u_{uuid.uuid4().hex[:6]}",
            "password":  "StrongPass1!",
            "firstName": "Bob",
            "lastName":  "Jones",
        }
        resp = requests.post(f"{AUTH_BASE}/register", json=payload, timeout=10)

        assert resp.status_code == 201
        links = resp.json().get("_links", {})
        assert "profile" in links
        assert "me"      in links
        assert "refresh" in links
        assert "logout"  in links

    def test_register_duplicate_email_returns_409(self, registered_user):
        """Registering with an already-used email must return 409 Conflict."""
        payload = {
            "email":     registered_user["credentials"]["email"],  # duplicate
            "username":  f"u_{uuid.uuid4().hex[:6]}",
            "password":  "StrongPass1!",
            "firstName": "Dup",
            "lastName":  "User",
        }
        resp = requests.post(f"{AUTH_BASE}/register", json=payload, timeout=10)
        assert resp.status_code == 409

    def test_register_missing_fields_returns_400(self):
        """Registration with missing required fields must return 400 Bad Request."""
        # email is missing
        resp = requests.post(
            f"{AUTH_BASE}/register",
            json={"username": "noemail", "password": "Pass123!"},
            timeout=10,
        )
        assert resp.status_code == 400

    def test_register_missing_password_returns_400(self):
        """Registration without a password must return 400 Bad Request."""
        resp = requests.post(
            f"{AUTH_BASE}/register",
            json={"email": unique_email(), "username": "nopass"},
            timeout=10,
        )
        assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# POST /login
# ─────────────────────────────────────────────────────────────────────────────

class TestLogin:

    def test_login_success_returns_200(self, registered_user):
        """Valid credentials must return 200 OK with tokens and user."""
        creds = registered_user["credentials"]
        resp = requests.post(
            f"{AUTH_BASE}/login",
            json={"email": creds["email"], "password": creds["password"]},
            timeout=10,
        )

        assert resp.status_code == 200
        body = resp.json()
        assert "accessToken"  in body
        assert "refreshToken" in body
        assert body["user"]["email"] == creds["email"]

    def test_login_returns_hateoas_links(self, registered_user):
        """Login response must include _links."""
        creds = registered_user["credentials"]
        resp = requests.post(
            f"{AUTH_BASE}/login",
            json={"email": creds["email"], "password": creds["password"]},
            timeout=10,
        )

        links = resp.json().get("_links", {})
        assert "profile" in links
        assert "me"      in links
        assert "refresh" in links
        assert "logout"  in links

    def test_login_wrong_password_returns_401(self, registered_user):
        """Wrong password must return 401 Unauthorized."""
        resp = requests.post(
            f"{AUTH_BASE}/login",
            json={
                "email":    registered_user["credentials"]["email"],
                "password": "WrongPassword!",
            },
            timeout=10,
        )
        assert resp.status_code == 401

    def test_login_unknown_email_returns_401(self):
        """Login with an email that does not exist must return 401."""
        resp = requests.post(
            f"{AUTH_BASE}/login",
            json={"email": "nobody@nowhere.test", "password": "Pass123!"},
            timeout=10,
        )
        assert resp.status_code == 401

    def test_login_missing_fields_returns_400(self):
        """Login with empty body must return 400 Bad Request."""
        resp = requests.post(f"{AUTH_BASE}/login", json={}, timeout=10)
        assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# GET /me
# ─────────────────────────────────────────────────────────────────────────────

class TestMe:

    def test_me_returns_200_with_profile(self, auth_headers, registered_user):
        """Authenticated GET /me must return the caller's profile."""
        resp = requests.get(f"{AUTH_BASE}/me", headers=auth_headers, timeout=10)

        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == registered_user["credentials"]["email"]
        assert "id" in body
        assert "role" in body

    def test_me_without_token_returns_401(self):
        """GET /me without an Authorization header must return 401."""
        resp = requests.get(f"{AUTH_BASE}/me", timeout=10)
        assert resp.status_code == 401

    def test_me_with_invalid_token_returns_401(self):
        """GET /me with a garbage token must return 401."""
        resp = requests.get(
            f"{AUTH_BASE}/me",
            headers={"Authorization": "Bearer this.is.not.a.valid.jwt"},
            timeout=10,
        )
        assert resp.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# POST /refresh
# ─────────────────────────────────────────────────────────────────────────────

class TestRefresh:

    def test_refresh_returns_new_access_token(self, auth_tokens):
        """Valid refresh token must return a new accessToken."""
        resp = requests.post(
            f"{AUTH_BASE}/refresh",
            json={"refreshToken": auth_tokens["refreshToken"]},
            timeout=10,
        )

        assert resp.status_code == 200
        assert "accessToken" in resp.json()

    def test_refresh_with_invalid_token_returns_401(self):
        """Invalid refresh token must return 401 Unauthorized."""
        resp = requests.post(
            f"{AUTH_BASE}/refresh",
            json={"refreshToken": str(uuid.uuid4())},
            timeout=10,
        )
        assert resp.status_code == 401

    def test_refresh_missing_token_returns_400(self):
        """Missing refreshToken field must return 400 Bad Request."""
        resp = requests.post(f"{AUTH_BASE}/refresh", json={}, timeout=10)
        assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# POST /logout
# ─────────────────────────────────────────────────────────────────────────────

class TestLogout:

    def test_logout_returns_204(self, registered_user):
        """
        Logging out with a valid token must return 204 No Content.
        We log in fresh here so the main session token stays valid
        for other tests.
        """
        creds = registered_user["credentials"]
        login = requests.post(
            f"{AUTH_BASE}/login",
            json={"email": creds["email"], "password": creds["password"]},
            timeout=10,
        ).json()

        resp = requests.post(
            f"{AUTH_BASE}/logout",
            json={"refreshToken": login["refreshToken"]},
            headers={"Authorization": f"Bearer {login['accessToken']}"},
            timeout=10,
        )
        assert resp.status_code == 204

    def test_access_token_rejected_after_logout(self, registered_user):
        """
        After logout the blacklisted access token must be rejected on /me.
        """
        creds = registered_user["credentials"]
        login = requests.post(
            f"{AUTH_BASE}/login",
            json={"email": creds["email"], "password": creds["password"]},
            timeout=10,
        ).json()

        # logout
        requests.post(
            f"{AUTH_BASE}/logout",
            json={"refreshToken": login["refreshToken"]},
            headers={"Authorization": f"Bearer {login['accessToken']}"},
            timeout=10,
        )

        # the same access token must now be rejected
        me_resp = requests.get(
            f"{AUTH_BASE}/me",
            headers={"Authorization": f"Bearer {login['accessToken']}"},
            timeout=10,
        )
        assert me_resp.status_code == 401
