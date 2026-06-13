from sqlalchemy import text
from sqlalchemy.orm import Session

from api.schemas.social import AuteurPublicRead


def fetch_auteur_public(db: Session, id_anonyme: str) -> AuteurPublicRead | None:
    row = db.execute(
        text(
            """
            SELECT v.id_anonyme, cu.nom_affichage, cu.photo_profil_url
            FROM vault_correspondance v
            JOIN compte_utilisateur cu ON cu.id_user = v.id_user
            WHERE v.id_anonyme = :id AND COALESCE(cu.est_supprime, false) = false
            """
        ),
        {"id": id_anonyme},
    ).fetchone()
    if not row:
        return None
    data = dict(row._mapping)
    return AuteurPublicRead(
        id_anonyme=data["id_anonyme"],
        nom_affichage=data["nom_affichage"],
        photo_profil_url=data["photo_profil_url"],
    )


def fetch_auteurs_public(db: Session, id_anonymes: set[str]) -> dict[str, AuteurPublicRead]:
    if not id_anonymes:
        return {}
    rows = db.execute(
        text(
            """
            SELECT v.id_anonyme, cu.nom_affichage, cu.photo_profil_url
            FROM vault_correspondance v
            JOIN compte_utilisateur cu ON cu.id_user = v.id_user
            WHERE v.id_anonyme = ANY(:ids) AND COALESCE(cu.est_supprime, false) = false
            """
        ),
        {"ids": list(id_anonymes)},
    ).fetchall()
    return {
        str(r._mapping["id_anonyme"]): AuteurPublicRead(
            id_anonyme=r._mapping["id_anonyme"],
            nom_affichage=r._mapping["nom_affichage"],
            photo_profil_url=r._mapping["photo_profil_url"],
        )
        for r in rows
    }


def is_admin(role: str) -> bool:
    return role in ("Admin", "Super-Admin")
