"""Fixtures pour tests d'intégration / E2E contre l'API (pré-prod ou locale)."""

from __future__ import annotations

import os

import httpx
import pytest

from tests.constants import (
    SEED_ADMIN_EMAIL,
    SEED_CLIENT_EMAIL,
    SEED_CLIENT_PASSWORD,
)


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("API_BASE_URL", "http://127.0.0.1:18000").rstrip("/")


@pytest.fixture(scope="session")
def client(base_url: str) -> httpx.Client:
    with httpx.Client(base_url=base_url, timeout=30.0) as c:
        yield c


@pytest.fixture(scope="session")
def client_token(client: httpx.Client) -> str:
    r = client.post(
        "/api/auth/login",
        json={"email": SEED_CLIENT_EMAIL, "password": SEED_CLIENT_PASSWORD},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def admin_token(client: httpx.Client) -> str:
    r = client.post(
        "/api/auth/login",
        json={"email": SEED_ADMIN_EMAIL, "password": SEED_CLIENT_PASSWORD},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


