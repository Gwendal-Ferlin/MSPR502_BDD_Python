"""Routes protégées sans jeton."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.integration
def test_inventory_requires_auth(client: httpx.Client) -> None:
    r = client.get("/api/gamification/inventory")
    assert r.status_code == 403


@pytest.mark.integration
def test_sante_profils_requires_auth(client: httpx.Client) -> None:
    r = client.get("/api/sante/profils")
    assert r.status_code == 403
