from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.auth.dependencies import get_current_user
from api.db.postgres_sante import get_session_sante
from api.db.mongo_logs import get_mongo_logs
from api.schemas.auth import CurrentUser
from api.schemas.sante import ProfilSanteRead, ObjectifRead, JournalRead, SeanceRead, ReferentielRead, RestrictionRead
from api.services.log_admin import log_admin_consultation_tiers

router = APIRouter(prefix="/sante", tags=["Santé"])


def _check_id_anonyme(current_user: CurrentUser, id_anonyme: str | None) -> str | None:
    if current_user.role in ("Admin", "Super-Admin"):
        return id_anonyme
    if id_anonyme and id_anonyme != current_user.id_anonyme:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Droits insuffisants")
    return current_user.id_anonyme


@router.get("/profils", response_model=list[ProfilSanteRead])
def list_profils(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    id_anonyme: UUID | None = Query(None),
    db: Session = Depends(get_session_sante),
    db_logs: Database = Depends(get_mongo_logs),
):
    effective = _check_id_anonyme(current_user, str(id_anonyme) if id_anonyme else None)
    if effective:
        log_admin_consultation_tiers(
            db_logs, current_user, "GET /api/sante/profils", id_anonyme_cible=effective
        )
        rows = db.execute(
            text("SELECT id_profil, id_anonyme, annee_naissance, sexe, taille_cm FROM profil_sante WHERE id_anonyme = :id"),
            {"id": effective},
        ).fetchall()
    else:
        log_admin_consultation_tiers(
            db_logs, current_user, "GET /api/sante/profils", details_extra={"liste_complete": True}
        )
        rows = db.execute(text("SELECT id_profil, id_anonyme, annee_naissance, sexe, taille_cm FROM profil_sante")).fetchall()
    return [ProfilSanteRead.model_validate(dict(r._mapping)) for r in rows]


@router.get("/objectifs", response_model=list[ObjectifRead])
def list_objectifs(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    id_anonyme: UUID | None = Query(None),
    db: Session = Depends(get_session_sante),
    db_logs: Database = Depends(get_mongo_logs),
):
    effective = _check_id_anonyme(current_user, str(id_anonyme) if id_anonyme else None)
    if effective:
        log_admin_consultation_tiers(
            db_logs, current_user, "GET /api/sante/objectifs", id_anonyme_cible=effective
        )
        rows = db.execute(
            text("SELECT id_objectif_u, id_anonyme, type_objectif, valeur_cible, date_debut, statut FROM objectif_utilisateur WHERE id_anonyme = :id"),
            {"id": effective},
        ).fetchall()
    else:
        log_admin_consultation_tiers(
            db_logs, current_user, "GET /api/sante/objectifs", details_extra={"liste_complete": True}
        )
        rows = db.execute(text("SELECT id_objectif_u, id_anonyme, type_objectif, valeur_cible, date_debut, statut FROM objectif_utilisateur")).fetchall()
    return [ObjectifRead.model_validate(dict(r._mapping)) for r in rows]


@router.get("/journal", response_model=list[JournalRead])
def list_journal(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    id_anonyme: UUID | None = Query(None),
    db: Session = Depends(get_session_sante),
    db_logs: Database = Depends(get_mongo_logs),
):
    effective = _check_id_anonyme(current_user, str(id_anonyme) if id_anonyme else None) or current_user.id_anonyme
    if effective and effective != current_user.id_anonyme:
        log_admin_consultation_tiers(
            db_logs, current_user, "GET /api/sante/journal", id_anonyme_cible=effective
        )
    rows = db.execute(
        text("SELECT id_repas, id_anonyme, horodatage, nom_repas, type_repas, total_calories, total_proteines, total_glucides, total_lipides FROM journal_alimentaire WHERE id_anonyme = :id ORDER BY horodatage DESC"),
        {"id": effective},
    ).fetchall()
    return [JournalRead.model_validate(dict(r._mapping)) for r in rows]


@router.get("/seances", response_model=list[SeanceRead])
def list_seances(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    id_anonyme: UUID | None = Query(None),
    db: Session = Depends(get_session_sante),
    db_logs: Database = Depends(get_mongo_logs),
):
    effective = _check_id_anonyme(current_user, str(id_anonyme) if id_anonyme else None) or current_user.id_anonyme
    if effective and effective != current_user.id_anonyme:
        log_admin_consultation_tiers(
            db_logs, current_user, "GET /api/sante/seances", id_anonyme_cible=effective
        )
    rows = db.execute(
        text("SELECT id_seance, id_anonyme, horodatage, nom_seance, ressenti_effort_rpe FROM seance_activite WHERE id_anonyme = :id ORDER BY horodatage DESC"),
        {"id": effective},
    ).fetchall()
    return [SeanceRead.model_validate(dict(r._mapping)) for r in rows]


@router.get("/referentiels/restrictions", response_model=list[RestrictionRead])
def list_restrictions(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_sante),
):
    rows = db.execute(text("SELECT id_restriction AS id, nom, type FROM ref_restriction")).fetchall()
    return [RestrictionRead.model_validate(dict(r._mapping)) for r in rows]


@router.get("/referentiels/exercices", response_model=list[ReferentielRead])
def list_exercices(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_sante),
):
    rows = db.execute(text("SELECT id_exercice AS id, nom, muscle_principal FROM ref_exercice")).fetchall()
    return [ReferentielRead.model_validate(dict(r._mapping)) for r in rows]


@router.get("/referentiels/materiel", response_model=list[ReferentielRead])
def list_materiel(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_sante),
):
    rows = db.execute(text("SELECT id_materiel AS id, nom FROM materiel")).fetchall()
    return [ReferentielRead.model_validate(dict(r._mapping)) for r in rows]
