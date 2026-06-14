"""Routes IA en mode mock (offline / performance) — sans HF_API_TOKEN."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import httpx
import pytest

_IA_MOCK_PATH = Path(__file__).resolve().parents[2] / "api" / "services" / "ia_mock.py"
_spec = importlib.util.spec_from_file_location("ia_mock", _IA_MOCK_PATH)
assert _spec is not None and _spec.loader is not None
_ia_mock = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ia_mock)

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
    "repas_par_jour": 2,
    "repas_types": ["dejeuner", "souper"],
    "restrictions": [],
}


def test_ia_mock_generer_programme_structure() -> None:
    result = _ia_mock.generer_programme(_MIN_BODY_EXERCICES)
    assert result.get("_mock") is True
    assert "programme" in result
    assert len(result["programme"]) >= 3
    assert "progression" in result


def test_ia_mock_generer_plats_structure() -> None:
    result = _ia_mock.generer_plats(_MIN_BODY_PLATS)
    assert result.get("_mock") is True
    assert "plan_repas" in result
    assert "liste_courses" in result
    assert result["repas_par_jour"] == 2


@pytest.mark.integration
def test_ia_recommandations_mock_via_api(client: httpx.Client, client_token: str) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    if health.json().get("ia_mode") != "mock":
        pytest.skip("API non en mode mock — lancer avec IA_MOCK_MODE=true (profil offline ou performance)")

    r = client.post(
        "/api/ia/recommandations",
        headers={"Authorization": f"Bearer {client_token}"},
        json=_MIN_BODY_EXERCICES,
        timeout=30.0,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("_mock") is True
    assert "programme" in body


@pytest.mark.integration
def test_ia_plats_mock_via_api(client: httpx.Client, client_token: str) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    if health.json().get("ia_mode") != "mock":
        pytest.skip("API non en mode mock — lancer avec IA_MOCK_MODE=true (profil offline ou performance)")

    r = client.post(
        "/api/ia/plats",
        headers={"Authorization": f"Bearer {client_token}"},
        json=_MIN_BODY_PLATS,
        timeout=30.0,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("_mock") is True
    assert "plan_repas" in body
