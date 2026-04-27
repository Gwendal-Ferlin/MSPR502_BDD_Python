"""Santé de l'API et documentation OpenAPI."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.integration
def test_health_ok(client: httpx.Client) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


@pytest.mark.integration
def test_root(client: httpx.Client) -> None:
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert "message" in body


@pytest.mark.integration
def test_openapi_json(client: httpx.Client) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert spec.get("openapi")
    assert "paths" in spec
