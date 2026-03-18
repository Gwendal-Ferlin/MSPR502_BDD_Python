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
from api.schemas.sante import (
    ProfilSanteRead,
    ProfilSanteUpdate,
    ObjectifRead,
    ObjectifUpdate,
    SuiviBiometriqueRead,
    SuiviBiometriqueUpdate,
    JournalRead,
    SeanceRead,
    ReferentielRead,
    RestrictionRead,
    MesRestrictionsUpdate,
)
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


@router.patch("/profils", response_model=ProfilSanteRead)
def modifier_mon_profil(
    body: ProfilSanteUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_sante),
):
    """Met à jour le profil santé de l'utilisateur connecté (annee_naissance, sexe, taille_cm). Crée le profil s'il n'existe pas."""
    id_anonyme = str(current_user.id_anonyme)
    row = db.execute(
        text("SELECT id_profil FROM profil_sante WHERE id_anonyme = :id"),
        {"id": id_anonyme},
    ).fetchone()
    updates = []
    params = {"id": id_anonyme}
    if body.annee_naissance is not None:
        updates.append("annee_naissance = :annee_naissance")
        params["annee_naissance"] = body.annee_naissance
    if body.sexe is not None:
        updates.append("sexe = :sexe")
        params["sexe"] = body.sexe
    if body.taille_cm is not None:
        updates.append("taille_cm = :taille_cm")
        params["taille_cm"] = body.taille_cm

    if not updates:
        if row:
            r = db.execute(
                text("SELECT id_profil, id_anonyme, annee_naissance, sexe, taille_cm FROM profil_sante WHERE id_anonyme = :id"),
                {"id": id_anonyme},
            ).fetchone()
            return ProfilSanteRead.model_validate(dict(r._mapping))
        db.execute(
            text("INSERT INTO profil_sante (id_anonyme) VALUES (:id)"),
            {"id": id_anonyme},
        )
        db.commit()
        r = db.execute(
            text("SELECT id_profil, id_anonyme, annee_naissance, sexe, taille_cm FROM profil_sante WHERE id_anonyme = :id"),
            {"id": id_anonyme},
        ).fetchone()
        return ProfilSanteRead.model_validate(dict(r._mapping))

    if row:
        set_clause = ", ".join(updates)
        db.execute(
            text(f"UPDATE profil_sante SET {set_clause} WHERE id_anonyme = :id"),
            params,
        )
    else:
        annee = params.get("annee_naissance")
        sexe = params.get("sexe")
        taille = params.get("taille_cm")
        db.execute(
            text("INSERT INTO profil_sante (id_anonyme, annee_naissance, sexe, taille_cm) VALUES (:id, :annee_naissance, :sexe, :taille_cm)"),
            {"id": id_anonyme, "annee_naissance": annee, "sexe": sexe, "taille_cm": taille},
        )
    db.commit()
    r = db.execute(
        text("SELECT id_profil, id_anonyme, annee_naissance, sexe, taille_cm FROM profil_sante WHERE id_anonyme = :id"),
        {"id": id_anonyme},
    ).fetchone()
    return ProfilSanteRead.model_validate(dict(r._mapping))


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
            text("SELECT id_objectif_u, id_anonyme, type_objectif, valeur_cible, unite, date_debut, date_fin, statut FROM objectif_utilisateur WHERE id_anonyme = :id"),
            {"id": effective},
        ).fetchall()
    else:
        log_admin_consultation_tiers(
            db_logs, current_user, "GET /api/sante/objectifs", details_extra={"liste_complete": True}
        )
        rows = db.execute(text("SELECT id_objectif_u, id_anonyme, type_objectif, valeur_cible, unite, date_debut, date_fin, statut FROM objectif_utilisateur")).fetchall()
    return [ObjectifRead.model_validate(dict(r._mapping)) for r in rows]


@router.patch("/objectifs/{id_objectif_u}", response_model=ObjectifRead)
def modifier_objectif(
    id_objectif_u: int,
    body: ObjectifUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_sante),
):
    """Met à jour un objectif appartenant à l'utilisateur connecté."""
    id_anonyme = str(current_user.id_anonyme)
    row = db.execute(
        text("SELECT id_objectif_u FROM objectif_utilisateur WHERE id_objectif_u = :id AND id_anonyme = :aid"),
        {"id": id_objectif_u, "aid": id_anonyme},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objectif non trouvé")
    updates = []
    params = {"id": id_objectif_u}
    if body.type_objectif is not None:
        updates.append("type_objectif = :type_objectif")
        params["type_objectif"] = body.type_objectif
    if body.valeur_cible is not None:
        updates.append("valeur_cible = :valeur_cible")
        params["valeur_cible"] = body.valeur_cible
    if body.unite is not None:
        updates.append("unite = :unite")
        params["unite"] = body.unite
    if body.date_debut is not None:
        updates.append("date_debut = :date_debut")
        params["date_debut"] = body.date_debut
    if body.date_fin is not None:
        updates.append("date_fin = :date_fin")
        params["date_fin"] = body.date_fin
    if body.statut is not None:
        updates.append("statut = :statut")
        params["statut"] = body.statut
    if not updates:
        r = db.execute(
            text("SELECT id_objectif_u, id_anonyme, type_objectif, valeur_cible, unite, date_debut, date_fin, statut FROM objectif_utilisateur WHERE id_objectif_u = :id"),
            {"id": id_objectif_u},
        ).fetchone()
        return ObjectifRead.model_validate(dict(r._mapping))
    set_clause = ", ".join(updates)
    db.execute(text(f"UPDATE objectif_utilisateur SET {set_clause} WHERE id_objectif_u = :id"), params)
    db.commit()
    r = db.execute(
        text("SELECT id_objectif_u, id_anonyme, type_objectif, valeur_cible, unite, date_debut, date_fin, statut FROM objectif_utilisateur WHERE id_objectif_u = :id"),
        {"id": id_objectif_u},
    ).fetchone()
    return ObjectifRead.model_validate(dict(r._mapping))


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


@router.get("/suivi-biometrique", response_model=list[SuiviBiometriqueRead])
def list_suivi_biometrique(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    id_anonyme: UUID | None = Query(None),
    db: Session = Depends(get_session_sante),
    db_logs: Database = Depends(get_mongo_logs),
):
    """Liste les relevés biométriques. Client : les siens ; Admin : avec id_anonyme optionnel."""
    effective = _check_id_anonyme(current_user, str(id_anonyme) if id_anonyme else None)
    if effective:
        log_admin_consultation_tiers(
            db_logs, current_user, "GET /api/sante/suivi-biometrique", id_anonyme_cible=effective
        )
        rows = db.execute(
            text("SELECT id_biometrie, id_anonyme, date_releve, poids_kg, score_sommeil FROM suivi_biometrique WHERE id_anonyme = :id ORDER BY date_releve DESC"),
            {"id": effective},
        ).fetchall()
    else:
        log_admin_consultation_tiers(
            db_logs, current_user, "GET /api/sante/suivi-biometrique", details_extra={"liste_complete": True}
        )
        rows = db.execute(text("SELECT id_biometrie, id_anonyme, date_releve, poids_kg, score_sommeil FROM suivi_biometrique ORDER BY date_releve DESC")).fetchall()
    return [SuiviBiometriqueRead.model_validate(dict(r._mapping)) for r in rows]


@router.patch("/suivi-biometrique/{id_biometrie}", response_model=SuiviBiometriqueRead)
def modifier_suivi_biometrique(
    id_biometrie: int,
    body: SuiviBiometriqueUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_sante),
):
    """Met à jour un relevé biométrique appartenant à l'utilisateur connecté."""
    id_anonyme = str(current_user.id_anonyme)
    row = db.execute(
        text("SELECT id_biometrie FROM suivi_biometrique WHERE id_biometrie = :id AND id_anonyme = :aid"),
        {"id": id_biometrie, "aid": id_anonyme},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relevé biométrique non trouvé")
    updates = []
    params = {"id": id_biometrie}
    if body.date_releve is not None:
        updates.append("date_releve = :date_releve")
        params["date_releve"] = body.date_releve
    if body.poids_kg is not None:
        updates.append("poids_kg = :poids_kg")
        params["poids_kg"] = body.poids_kg
    if body.score_sommeil is not None:
        updates.append("score_sommeil = :score_sommeil")
        params["score_sommeil"] = body.score_sommeil
    if not updates:
        r = db.execute(
            text("SELECT id_biometrie, id_anonyme, date_releve, poids_kg, score_sommeil FROM suivi_biometrique WHERE id_biometrie = :id"),
            {"id": id_biometrie},
        ).fetchone()
        return SuiviBiometriqueRead.model_validate(dict(r._mapping))
    set_clause = ", ".join(updates)
    db.execute(text(f"UPDATE suivi_biometrique SET {set_clause} WHERE id_biometrie = :id"), params)
    db.commit()
    r = db.execute(
        text("SELECT id_biometrie, id_anonyme, date_releve, poids_kg, score_sommeil FROM suivi_biometrique WHERE id_biometrie = :id"),
        {"id": id_biometrie},
    ).fetchone()
    return SuiviBiometriqueRead.model_validate(dict(r._mapping))


@router.get("/mes-restrictions", response_model=list[RestrictionRead])
def list_mes_restrictions(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_sante),
):
    """Liste les restrictions alimentaires (ou autres) associées à l'utilisateur connecté."""
    id_anonyme = str(current_user.id_anonyme)
    rows = db.execute(
        text("""
            SELECT r.id_restriction AS id, r.nom, r.type
            FROM ref_restriction r
            INNER JOIN utilisateur_restriction ur ON ur.id_restriction = r.id_restriction
            WHERE ur.id_anonyme = :id
        """),
        {"id": id_anonyme},
    ).fetchall()
    return [RestrictionRead.model_validate(dict(r._mapping)) for r in rows]


@router.put("/mes-restrictions", response_model=list[RestrictionRead])
def modifier_mes_restrictions(
    body: MesRestrictionsUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_sante),
):
    """Remplace les restrictions de l'utilisateur connecté par la liste fournie (id_restrictions)."""
    id_anonyme = str(current_user.id_anonyme)
    db.execute(text("DELETE FROM utilisateur_restriction WHERE id_anonyme = :id"), {"id": id_anonyme})
    for id_restriction in body.id_restrictions:
        db.execute(
            text("INSERT INTO utilisateur_restriction (id_anonyme, id_restriction) VALUES (:aid, :rid) ON CONFLICT (id_anonyme, id_restriction) DO NOTHING"),
            {"aid": id_anonyme, "rid": id_restriction},
        )
    db.commit()
    rows = db.execute(
        text("""
            SELECT r.id_restriction AS id, r.nom, r.type
            FROM ref_restriction r
            INNER JOIN utilisateur_restriction ur ON ur.id_restriction = r.id_restriction
            WHERE ur.id_anonyme = :id
        """),
        {"id": id_anonyme},
    ).fetchall()
    return [RestrictionRead.model_validate(dict(r._mapping)) for r in rows]


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
