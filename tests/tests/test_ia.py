"""Routes IA : garde d’auth ; smoke HF optionnel."""

from __future__ import annotations

import os

import httpx
import pytest

_MIN_BODY_EXERCICES = {
    "niveau": "normal",
    "objectif": "perte_de_poids",
    "date_debut": "2026-01-01T00:00:00",
    "date_fin": "2026-02-01T00:00:00",
    "valeur_cible": 70.0,
    "unite": "kg",
    "materiels": ["Haltères", "Tapis de course"],
    "biometrie": {"poids_kg": 75.0},
}

_MIN_BODY_PLATS = {
    "objectif_alimentaire": "perte_de_poids",
    "repas_par_jour": 1,
    "restrictions": [],
}


@pytest.mark.integration
def test_ia_recommandations_requires_auth(client: httpx.Client) -> None:
    r = client.post("/api/ia/recommandations", json=_MIN_BODY_EXERCICES)
    assert r.status_code == 403


@pytest.mark.integration
def test_ia_plats_requires_auth(client: httpx.Client) -> None:
    r = client.post("/api/ia/plats", json=_MIN_BODY_PLATS)
    assert r.status_code == 403


@pytest.mark.integration
@pytest.mark.slow
def test_ia_recommandations_smoke_if_enabled(client: httpx.Client, client_token: str) -> None:
    if os.environ.get("RUN_IA_SMOKE") != "1":
        pytest.skip("Définir RUN_IA_SMOKE=1 pour un appel réel Hugging Face (long, token requis côté API)")

    r = client.post(
        "/api/ia/recommandations",
        headers={"Authorization": f"Bearer {client_token}"},
        json=_MIN_BODY_EXERCICES,
        timeout=120.0,
    )
    assert r.status_code in (200, 400, 502), r.text
    if r.status_code == 200:
        assert isinstance(r.json(), dict)


@pytest.mark.integration
@pytest.mark.slow
def test_ia_plats_smoke_if_enabled(client: httpx.Client, client_token: str) -> None:
    if os.environ.get("RUN_IA_SMOKE") != "1":
        pytest.skip("Définir RUN_IA_SMOKE=1 pour un appel réel Hugging Face (long, token requis côté API)")

    r = client.post(
        "/api/ia/plats",
        headers={"Authorization": f"Bearer {client_token}"},
        json=_MIN_BODY_PLATS,
        timeout=120.0,
    )
    assert r.status_code in (200, 400, 502), r.text
    if r.status_code == 200:
        assert isinstance(r.json(), dict)
