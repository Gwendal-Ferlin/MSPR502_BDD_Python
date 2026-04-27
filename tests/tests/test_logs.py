"""Logs Mongo : config publique et événements authentifiés."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.integration
def test_logs_config_public(client: httpx.Client) -> None:
    r = client.get("/api/logs/config")
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.integration
def test_list_evenements_client(client: httpx.Client, client_token: str) -> None:
    r = client.get(
        "/api/logs/evenements",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.integration
def test_evenements_requires_auth(client: httpx.Client) -> None:
    r = client.get("/api/logs/evenements")
    assert r.status_code == 403
