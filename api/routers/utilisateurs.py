from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.auth.dependencies import get_current_user, require_roles
from api.db.postgres_utilisateur import get_session_utilisateur
from api.db.mongo_logs import get_mongo_logs
from api.schemas.auth import CurrentUser
from api.schemas.utilisateurs import CompteUtilisateurRead, VaultRead
from api.services.log_admin import log_admin_consultation_tiers

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])

AdminOrSuperAdmin = Annotated[CurrentUser, Depends(require_roles(["Admin", "Super-Admin"]))]


@router.get("", response_model=list[CompteUtilisateurRead])
def list_comptes(
    current_user: AdminOrSuperAdmin,
    db: Session = Depends(get_session_utilisateur),
    db_logs: Database = Depends(get_mongo_logs),
):
    log_admin_consultation_tiers(
        db_logs, current_user, "GET /api/utilisateurs", details_extra={"liste_complete": True}
    )
    rows = db.execute(text("SELECT id_user, email, role, type_abonnement, date_consentement_rgpd FROM compte_utilisateur")).fetchall()
    return [CompteUtilisateurRead.model_validate(dict(r._mapping)) for r in rows]


@router.get("/{id_user}", response_model=CompteUtilisateurRead)
def get_compte(
    id_user: int,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
    db_logs: Database = Depends(get_mongo_logs),
):
    if current_user.role not in ("Admin", "Super-Admin") and current_user.id_user != id_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Droits insuffisants")
    log_admin_consultation_tiers(
        db_logs, current_user, "GET /api/utilisateurs/{id_user}", id_user_cible=id_user
    )
    row = db.execute(
        text("SELECT id_user, email, role, type_abonnement, date_consentement_rgpd FROM compte_utilisateur WHERE id_user = :id"),
        {"id": id_user},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Compte non trouvé")
    return CompteUtilisateurRead.model_validate(dict(row._mapping))


@router.get("/{id_user}/vault", response_model=VaultRead)
def get_vault_by_user(
    id_user: int,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
    db_logs: Database = Depends(get_mongo_logs),
):
    if current_user.role not in ("Admin", "Super-Admin") and current_user.id_user != id_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Droits insuffisants")
    log_admin_consultation_tiers(
        db_logs, current_user, "GET /api/utilisateurs/{id_user}/vault", id_user_cible=id_user
    )
    row = db.execute(
        text("SELECT id_anonyme, id_user, date_derniere_activite, consentement_sante_actif FROM vault_correspondance WHERE id_user = :id"),
        {"id": id_user},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Vault non trouvé pour cet utilisateur")
    return VaultRead.model_validate(dict(row._mapping))


@router.get("/vault/{id_anonyme}", response_model=VaultRead)
def get_vault_by_anonyme(
    id_anonyme: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
    db_logs: Database = Depends(get_mongo_logs),
):
    id_anonyme_str = str(id_anonyme)
    if current_user.role not in ("Admin", "Super-Admin") and current_user.id_anonyme != id_anonyme_str:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Droits insuffisants")
    log_admin_consultation_tiers(
        db_logs, current_user, "GET /api/utilisateurs/vault/{id_anonyme}", id_anonyme_cible=id_anonyme_str
    )
    row = db.execute(
        text("SELECT id_anonyme, id_user, date_derniere_activite, consentement_sante_actif FROM vault_correspondance WHERE id_anonyme = :id"),
        {"id": id_anonyme_str},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Vault non trouvé")
    return VaultRead.model_validate(dict(row._mapping))
