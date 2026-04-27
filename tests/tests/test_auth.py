"""Authentification JWT."""

from __future__ import annotations

import httpx
import pytest

from tests.constants import SEED_ADMIN_EMAIL, SEED_CLIENT_EMAIL, SEED_CLIENT_PASSWORD


@pytest.mark.integration
def test_login_success(client: httpx.Client) -> None:
    r = client.post(
        "/api/auth/login",
        json={"email": SEED_CLIENT_EMAIL, "password": SEED_CLIENT_PASSWORD},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("token_type") == "bearer"
    assert data.get("access_token")
    assert len(data["access_token"]) > 20


@pytest.mark.integration
def test_login_wrong_password(client: httpx.Client) -> None:
    r = client.post(
        "/api/auth/login",
        json={"email": SEED_CLIENT_EMAIL, "password": "wrong-password"},
    )
    assert r.status_code == 401


@pytest.mark.integration
def test_login_unknown_email(client: httpx.Client) -> None:
    r = client.post(
        "/api/auth/login",
        json={"email": "inconnu@example.com", "password": SEED_CLIENT_PASSWORD},
    )
    assert r.status_code == 401


@pytest.mark.integration
def test_login_admin_success(client: httpx.Client) -> None:
    r = client.post(
        "/api/auth/login",
        json={"email": SEED_ADMIN_EMAIL, "password": SEED_CLIENT_PASSWORD},
    )
    assert r.status_code == 200, r.text
    assert r.json().get("access_token")
