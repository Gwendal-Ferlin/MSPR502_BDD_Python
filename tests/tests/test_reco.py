"""Reco Mongo : recommandations et repas."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import httpx
import pytest


@pytest.mark.integration
def test_list_recommendations_client(client: httpx.Client, client_token: str) -> None:
    r = client.get(
        "/api/reco/recommendations",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list)
    # Seed Mongo reco : au moins une reco pour l'id_anonyme du client c@c.fr (b1ffcd00-...)
    assert len(data) >= 1
    assert all("type" in item for item in data)


@pytest.mark.integration
def test_list_repas_client(client: httpx.Client, client_token: str) -> None:
    r = client.get(
        "/api/reco/repas",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.integration
def test_get_repas_invalid_id(client: httpx.Client, client_token: str) -> None:
    r = client.get(
        "/api/reco/repas/not-a-valid-objectid",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 404


@pytest.mark.integration
def test_create_and_get_repas(client: httpx.Client, client_token: str) -> None:
    nom = f"pytest-{uuid.uuid4().hex[:10]}"
    r = client.post(
        "/api/reco/repas",
        headers={"Authorization": f"Bearer {client_token}"},
        json={
            "nom_repas": nom,
            "aliments": {"Poulet": "100 g", "Riz": "80 g"},
            "total_calories": 450.0,
            "lipides": 12.0,
            "glucides": 45.0,
            "proteines": 35.0,
        },
    )
    assert r.status_code == 201, r.text
    created = r.json()
    assert created.get("nom_repas") == nom
    assert created.get("id")
    rid = created["id"]
    r2 = client.get(
        f"/api/reco/repas/{rid}",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json().get("nom_repas") == nom


@pytest.mark.integration
def test_recommendations_requires_auth(client: httpx.Client) -> None:
    r = client.get("/api/reco/recommendations")
    assert r.status_code == 403
