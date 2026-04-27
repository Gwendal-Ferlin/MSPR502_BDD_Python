"""Comptes utilisateurs."""

from __future__ import annotations

import httpx
import pytest

from tests.constants import SEED_CLIENT_EMAIL


@pytest.mark.integration
def test_get_me(client: httpx.Client, client_token: str) -> None:
    r = client.get(
        "/api/utilisateurs/me",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("email") == SEED_CLIENT_EMAIL
    assert body.get("role") == "Client"


@pytest.mark.integration
def test_list_comptes_admin(client: httpx.Client, admin_token: str) -> None:
    r = client.get(
        "/api/utilisateurs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200, r.text
    comptes = r.json()
    assert isinstance(comptes, list)
    assert len(comptes) >= 4


@pytest.mark.integration
def test_list_comptes_forbidden_for_client(client: httpx.Client, client_token: str) -> None:
    r = client.get(
        "/api/utilisateurs",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 403


@pytest.mark.integration
def test_me_requires_auth(client: httpx.Client) -> None:
    r = client.get("/api/utilisateurs/me")
    assert r.status_code == 403
