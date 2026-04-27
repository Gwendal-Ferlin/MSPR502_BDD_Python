"""Microservice santé avec utilisateur seed."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.integration
def test_profils_list_client(client: httpx.Client, client_token: str) -> None:
    r = client.get(
        "/api/sante/profils",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200, r.text
    profils = r.json()
    assert isinstance(profils, list)
