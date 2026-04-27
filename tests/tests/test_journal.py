"""Journal alimentaire (Postgres santé)."""

from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest


@pytest.mark.integration
def test_create_journal_and_calories_jour(client: httpx.Client, client_token: str) -> None:
    now = datetime.now(timezone.utc)
    date_str = now.date().isoformat()
    r = client.post(
        "/api/journal",
        headers={"Authorization": f"Bearer {client_token}"},
        json={
            "horodatage": now.isoformat(),
            "nom_repas": "Repas test pytest",
            "type_repas": "dejeuner",
            "total_calories": 520.0,
            "total_proteines": 30.0,
            "total_glucides": 50.0,
            "total_lipides": 15.0,
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body.get("nom_repas") == "Repas test pytest"
    assert body.get("total_calories") == 520.0

    r2 = client.get(
        "/api/journal/calories/jour",
        headers={"Authorization": f"Bearer {client_token}"},
        params={"date_jour": date_str},
    )
    assert r2.status_code == 200, r2.text
    cal = r2.json()
    assert cal.get("date") == date_str
    assert float(cal.get("total_calories", 0)) >= 520.0


@pytest.mark.integration
def test_journal_requires_auth(client: httpx.Client) -> None:
    r = client.post(
        "/api/journal",
        json={"horodatage": datetime.now(timezone.utc).isoformat()},
    )
    assert r.status_code == 403
