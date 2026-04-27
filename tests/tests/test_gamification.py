"""Gamification : catalogue public et inventaire authentifié."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.integration
def test_animals_catalog_no_auth(client: httpx.Client) -> None:
    r = client.get("/api/gamification/animals/catalog")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    data = body.get("data") or {}
    animals = data.get("animals")
    assert isinstance(animals, list)
    assert len(animals) >= 1


@pytest.mark.integration
def test_inventory_with_token(client: httpx.Client, client_token: str) -> None:
    r = client.get(
        "/api/gamification/inventory",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    data = body.get("data") or {}
    assert "coins" in data
    assert isinstance(data["coins"], int)


@pytest.mark.integration
def test_gamification_stats(client: httpx.Client, client_token: str) -> None:
    r = client.get(
        "/api/gamification/stats",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
