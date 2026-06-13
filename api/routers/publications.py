from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from api.db.postgres_utilisateur import get_session_utilisateur
from api.schemas.auth import CurrentUser
from api.schemas.social import (
    AuteurPublicRead,
    CommentaireCreate,
    CommentaireRead,
    PublicationCreate,
    PublicationRead,
)
from api.services.minio_storage import infer_media_type_from_url
from api.services.social_helpers import fetch_auteur_public, fetch_auteurs_public, is_admin

router = APIRouter(prefix="/publications", tags=["Publications"])


def _build_publication_read(
    row,
    auteur: AuteurPublicRead,
) -> PublicationRead:
    data = dict(row._mapping)
    return PublicationRead(
        id_publication=data["id_publication"],
        auteur=auteur,
        texte=data["texte"],
        media_url=data["media_url"],
        media_type=data["media_type"],
        date_creation=data["date_creation"],
        nb_likes=data["nb_likes"],
        est_like_par_moi=data["est_like_par_moi"],
        nb_commentaires=data["nb_commentaires"],
    )


def _get_publication_or_404(db: Session, id_publication: str):
    row = db.execute(
        text(
            """
            SELECT id_publication, id_anonyme, texte, media_url, media_type, date_creation, est_supprime
            FROM publication
            WHERE id_publication = :id
            """
        ),
        {"id": id_publication},
    ).fetchone()
    if not row or row._mapping["est_supprime"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication non trouvée")
    return row


@router.get("", response_model=list[PublicationRead])
def lister_publications(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    offset = (page - 1) * limit
    rows = db.execute(
        text(
            """
            SELECT
                p.id_publication,
                p.id_anonyme,
                p.texte,
                p.media_url,
                p.media_type,
                p.date_creation,
                (SELECT COUNT(*)::int FROM publication_like pl WHERE pl.id_publication = p.id_publication) AS nb_likes,
                EXISTS (
                    SELECT 1 FROM publication_like pl
                    WHERE pl.id_publication = p.id_publication AND pl.id_anonyme = :current_id
                ) AS est_like_par_moi,
                (SELECT COUNT(*)::int FROM publication_commentaire pc
                 WHERE pc.id_publication = p.id_publication AND COALESCE(pc.est_supprime, false) = false) AS nb_commentaires
            FROM publication p
            WHERE COALESCE(p.est_supprime, false) = false
            ORDER BY p.date_creation DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        {"current_id": current_user.id_anonyme, "limit": limit, "offset": offset},
    ).fetchall()

    auteur_ids = {str(r._mapping["id_anonyme"]) for r in rows}
    auteurs = fetch_auteurs_public(db, auteur_ids)

    result = []
    for row in rows:
        id_anonyme = str(row._mapping["id_anonyme"])
        auteur = auteurs.get(id_anonyme) or AuteurPublicRead(
            id_anonyme=row._mapping["id_anonyme"],
            nom_affichage=None,
            photo_profil_url=None,
        )
        result.append(_build_publication_read(row, auteur))
    return result


@router.post("", response_model=PublicationRead, status_code=status.HTTP_201_CREATED)
def creer_publication(
    body: PublicationCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    media_type = infer_media_type_from_url(body.media_url) if body.media_url else None
    row = db.execute(
        text(
            """
            INSERT INTO publication (id_anonyme, texte, media_url, media_type)
            VALUES (:id_anonyme, :texte, :media_url, :media_type)
            RETURNING id_publication, id_anonyme, texte, media_url, media_type, date_creation
            """
        ),
        {
            "id_anonyme": current_user.id_anonyme,
            "texte": body.texte.strip(),
            "media_url": body.media_url,
            "media_type": media_type,
        },
    ).fetchone()
    db.commit()

    auteur = fetch_auteur_public(db, current_user.id_anonyme)
    if not auteur:
        auteur = AuteurPublicRead(
            id_anonyme=UUID(current_user.id_anonyme),
            nom_affichage=None,
            photo_profil_url=None,
        )

    data = dict(row._mapping)
    return PublicationRead(
        id_publication=data["id_publication"],
        auteur=auteur,
        texte=data["texte"],
        media_url=data["media_url"],
        media_type=data["media_type"],
        date_creation=data["date_creation"],
        nb_likes=0,
        est_like_par_moi=False,
        nb_commentaires=0,
    )


@router.delete("/commentaires/{id_commentaire}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_commentaire(
    id_commentaire: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    row = db.execute(
        text(
            """
            SELECT pc.id_commentaire, pc.id_anonyme, pc.est_supprime, p.id_anonyme AS auteur_publication
            FROM publication_commentaire pc
            JOIN publication p ON p.id_publication = pc.id_publication
            WHERE pc.id_commentaire = :id
            """
        ),
        {"id": str(id_commentaire)},
    ).fetchone()
    if not row or row._mapping["est_supprime"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commentaire non trouvé")

    mapping = row._mapping
    is_owner = str(mapping["id_anonyme"]) == current_user.id_anonyme
    is_pub_owner = str(mapping["auteur_publication"]) == current_user.id_anonyme
    if not (is_owner or is_pub_owner or is_admin(current_user.role)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Droits insuffisants")

    db.execute(
        text("UPDATE publication_commentaire SET est_supprime = true WHERE id_commentaire = :id"),
        {"id": str(id_commentaire)},
    )
    db.commit()
    return None


@router.delete("/{id_publication}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_publication(
    id_publication: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    row = _get_publication_or_404(db, str(id_publication))
    if str(row._mapping["id_anonyme"]) != current_user.id_anonyme and not is_admin(current_user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Droits insuffisants")

    db.execute(
        text("UPDATE publication SET est_supprime = true WHERE id_publication = :id"),
        {"id": str(id_publication)},
    )
    db.commit()
    return None


@router.post("/{id_publication}/like", status_code=status.HTTP_204_NO_CONTENT)
def ajouter_like(
    id_publication: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    _get_publication_or_404(db, str(id_publication))
    db.execute(
        text(
            """
            INSERT INTO publication_like (id_publication, id_anonyme)
            VALUES (:pub_id, :user_id)
            ON CONFLICT (id_publication, id_anonyme) DO NOTHING
            """
        ),
        {"pub_id": str(id_publication), "user_id": current_user.id_anonyme},
    )
    db.commit()
    return None


@router.delete("/{id_publication}/like", status_code=status.HTTP_204_NO_CONTENT)
def retirer_like(
    id_publication: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    _get_publication_or_404(db, str(id_publication))
    db.execute(
        text(
            "DELETE FROM publication_like WHERE id_publication = :pub_id AND id_anonyme = :user_id"
        ),
        {"pub_id": str(id_publication), "user_id": current_user.id_anonyme},
    )
    db.commit()
    return None


@router.get("/{id_publication}/commentaires", response_model=list[CommentaireRead])
def lister_commentaires(
    id_publication: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    _get_publication_or_404(db, str(id_publication))
    rows = db.execute(
        text(
            """
            SELECT id_commentaire, id_anonyme, texte, date_creation
            FROM publication_commentaire
            WHERE id_publication = :pub_id AND COALESCE(est_supprime, false) = false
            ORDER BY date_creation ASC
            """
        ),
        {"pub_id": str(id_publication)},
    ).fetchall()

    auteur_ids = {str(r._mapping["id_anonyme"]) for r in rows}
    auteurs = fetch_auteurs_public(db, auteur_ids)

    result = []
    for row in rows:
        id_anonyme = str(row._mapping["id_anonyme"])
        auteur = auteurs.get(id_anonyme) or AuteurPublicRead(
            id_anonyme=row._mapping["id_anonyme"],
            nom_affichage=None,
            photo_profil_url=None,
        )
        data = dict(row._mapping)
        result.append(
            CommentaireRead(
                id_commentaire=data["id_commentaire"],
                auteur=auteur,
                texte=data["texte"],
                date_creation=data["date_creation"],
            )
        )
    return result


@router.post(
    "/{id_publication}/commentaires",
    response_model=CommentaireRead,
    status_code=status.HTTP_201_CREATED,
)
def ajouter_commentaire(
    id_publication: UUID,
    body: CommentaireCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    _get_publication_or_404(db, str(id_publication))
    row = db.execute(
        text(
            """
            INSERT INTO publication_commentaire (id_publication, id_anonyme, texte)
            VALUES (:pub_id, :user_id, :texte)
            RETURNING id_commentaire, id_anonyme, texte, date_creation
            """
        ),
        {
            "pub_id": str(id_publication),
            "user_id": current_user.id_anonyme,
            "texte": body.texte.strip(),
        },
    ).fetchone()
    db.commit()

    auteur = fetch_auteur_public(db, current_user.id_anonyme)
    if not auteur:
        auteur = AuteurPublicRead(
            id_anonyme=UUID(current_user.id_anonyme),
            nom_affichage=None,
            photo_profil_url=None,
        )

    data = dict(row._mapping)
    return CommentaireRead(
        id_commentaire=data["id_commentaire"],
        auteur=auteur,
        texte=data["texte"],
        date_creation=data["date_creation"],
    )
