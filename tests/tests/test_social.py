"""Publications, likes, commentaires et profil public."""

from __future__ import annotations

import io

import httpx
import pytest


@pytest.mark.integration
def test_profil_public_et_publications(client: httpx.Client, client_token: str) -> None:
    headers = {"Authorization": f"Bearer {client_token}"}

    r = client.patch(
        "/api/utilisateurs/me",
        headers=headers,
        json={"nom_affichage": "Marie Test", "photo_profil_url": "https://example.com/avatar.jpg"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["nom_affichage"] == "Marie Test"

    me = client.get("/api/utilisateurs/me", headers=headers)
    assert me.status_code == 200

    r_pub = client.post(
        "/api/publications",
        headers=headers,
        json={"texte": "Super séance de sport aujourd'hui !"},
    )
    assert r_pub.status_code == 201, r_pub.text
    pub = r_pub.json()
    pub_id = pub["id_publication"]
    assert pub["texte"].startswith("Super séance")
    assert pub["nb_likes"] == 0
    assert pub["est_like_par_moi"] is False

    r_feed = client.get("/api/publications?page=1&limit=10", headers=headers)
    assert r_feed.status_code == 200, r_feed.text
    feed = r_feed.json()
    assert any(p["id_publication"] == pub_id for p in feed)

    r_like = client.post(f"/api/publications/{pub_id}/like", headers=headers)
    assert r_like.status_code == 204, r_like.text

    r_feed2 = client.get("/api/publications?page=1&limit=10", headers=headers)
    item = next(p for p in r_feed2.json() if p["id_publication"] == pub_id)
    assert item["nb_likes"] == 1
    assert item["est_like_par_moi"] is True

    r_comment = client.post(
        f"/api/publications/{pub_id}/commentaires",
        headers=headers,
        json={"texte": "Bravo !"},
    )
    assert r_comment.status_code == 201, r_comment.text
    comment_id = r_comment.json()["id_commentaire"]

    r_comments = client.get(f"/api/publications/{pub_id}/commentaires", headers=headers)
    assert r_comments.status_code == 200
    assert len(r_comments.json()) >= 1

    auteur_id = pub["auteur"]["id_anonyme"]
    r_profil = client.get(f"/api/utilisateurs/public/{auteur_id}", headers=headers)
    assert r_profil.status_code == 200, r_profil.text
    assert r_profil.json()["nom_affichage"] == "Marie Test"

    r_unlike = client.delete(f"/api/publications/{pub_id}/like", headers=headers)
    assert r_unlike.status_code == 204

    r_del_comment = client.delete(
        f"/api/publications/commentaires/{comment_id}",
        headers=headers,
    )
    assert r_del_comment.status_code == 204

    r_del_pub = client.delete(f"/api/publications/{pub_id}", headers=headers)
    assert r_del_pub.status_code == 204


@pytest.mark.integration
def test_publications_require_auth(client: httpx.Client) -> None:
    r = client.get("/api/publications")
    assert r.status_code == 403


@pytest.mark.integration
def test_upload_media(client: httpx.Client, client_token: str) -> None:
    headers = {"Authorization": f"Bearer {client_token}"}
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    r = client.post(
        "/api/medias/upload",
        headers=headers,
        files={"fichier": ("test.png", io.BytesIO(png_bytes), "image/png")},
    )
    if r.status_code == 503:
        pytest.skip("MinIO non disponible dans cet environnement de test")
    assert r.status_code == 201, r.text
    assert "url" in r.json()
