import bcrypt
from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.auth.dependencies import get_current_user, require_roles
from api.db.postgres_utilisateur import get_session_utilisateur
from api.db.postgres_gamification import get_session_gamification
from api.db.mongo_logs import get_mongo_logs
from api.schemas.auth import CurrentUser
from api.schemas.utilisateurs import (
    CompteUtilisateurRead,
    VaultRead,
    CompteUtilisateurCreate,
    CompteUtilisateurUpdate,
    SouscrireAbonnement,
)
from api.services.log_admin import log_admin_consultation_tiers, log_admin_suppression_utilisateur_tiers
from api.services import field_encryption as fe

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])

AdminOrSuperAdmin = Annotated[CurrentUser, Depends(require_roles(["Admin", "Super-Admin"]))]

SELECT_COMPTE_COLS = (
    "id_user, email, role, type_abonnement, date_consentement_rgpd, est_supprime, "
    "date_fin_periode_payee, desabonnement_a_fin_periode"
)
ABONNEMENT_DUREE_MOIS = 1


def _appliquer_fin_periode_si_necessaire(db: Session, id_user: int) -> None:
    """Si désabonnement à fin de période et date dépassée, repasse le compte en Freemium."""
    db.execute(
        text("""
            UPDATE compte_utilisateur
            SET type_abonnement = 'Freemium', date_fin_periode_payee = NULL, desabonnement_a_fin_periode = false
            WHERE id_user = :id AND desabonnement_a_fin_periode = true
              AND date_fin_periode_payee IS NOT NULL AND date_fin_periode_payee < now()
        """),
        {"id": id_user},
    )
    db.commit()


def _appliquer_fin_periode_tous(db: Session) -> None:
    """Applique la rétrogradation Freemium à tous les comptes échus (pour list_comptes)."""
    db.execute(
        text("""
            UPDATE compte_utilisateur
            SET type_abonnement = 'Freemium', date_fin_periode_payee = NULL, desabonnement_a_fin_periode = false
            WHERE desabonnement_a_fin_periode = true
              AND date_fin_periode_payee IS NOT NULL AND date_fin_periode_payee < now()
        """)
    )
    db.commit()


@router.post("", response_model=CompteUtilisateurRead, status_code=status.HTTP_201_CREATED)
def create_compte(
    body: CompteUtilisateurCreate,
    db: Session = Depends(get_session_utilisateur),
    db_gamification: Session = Depends(get_session_gamification),
):
    email = body.email.strip().lower()
    # 1. Vérifier si l'email existe déjà
    existing = db.execute(
        text(f"SELECT id_user FROM compte_utilisateur WHERE {fe.sql_email_match_clause()}"),
        fe.params_for_email_lookup(email),
    ).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    # 2. Hasher le mot de passe
    hashed_pw = bcrypt.hashpw(body.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    email_db, email_hmac, pwd_db = fe.persist_compte_email_password(email, hashed_pw)

    # 3. Créer le compte (Role: Client, Abonnement: Freemium)
    new_user_row = db.execute(
        text(f"""
            INSERT INTO compte_utilisateur (email, email_hmac, password, role, type_abonnement, date_consentement_rgpd)
            VALUES (:email, :email_hmac, :password, 'Client', 'Freemium', :rgpd)
            RETURNING {SELECT_COMPTE_COLS}
        """),
        {
            "email": email_db,
            "email_hmac": email_hmac,
            "password": pwd_db,
            "rgpd": body.date_consentement_rgpd,
        },
    ).fetchone()

    new_user = fe.decrypt_compte_row(dict(new_user_row._mapping))

    # 4. Créer l'entrée dans le vault pour le lien anonymisé
    db.execute(
        text("INSERT INTO vault_correspondance (id_user) VALUES (:id_user)"),
        {"id_user": new_user["id_user"]}
    )

    vault_row = db.execute(
        text("SELECT id_anonyme FROM vault_correspondance WHERE id_user = :id_user"),
        {"id_user": new_user["id_user"]},
    ).fetchone()
    if not vault_row:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vault non créé pour cet utilisateur",
        )
    id_anonyme = str(vault_row._mapping["id_anonyme"])

    # 5. Ligne monnaie gamification (0 pépites à la création du compte)
    try:
        db_gamification.execute(
            text(
                """
                INSERT INTO gamification_user_currency (user_id, coins, total_coins_earned, total_coins_spent, updated_at)
                VALUES (:uid, 0, 0, 0, now())
                ON CONFLICT (user_id) DO NOTHING
                """
            ),
            {"uid": id_anonyme},
        )
        db_gamification.commit()
    except Exception:
        db_gamification.rollback()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible d'initialiser la gamification pour cet utilisateur",
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        try:
            db_gamification.execute(
                text("DELETE FROM gamification_user_currency WHERE user_id = :uid"),
                {"uid": id_anonyme},
            )
            db_gamification.commit()
        except Exception:
            db_gamification.rollback()
        raise

    return CompteUtilisateurRead.model_validate(new_user)


@router.get("", response_model=list[CompteUtilisateurRead])
def list_comptes(
    current_user: AdminOrSuperAdmin,
    db: Session = Depends(get_session_utilisateur),
    db_logs: Database = Depends(get_mongo_logs),
):
    log_admin_consultation_tiers(
        db_logs, current_user, "GET /api/utilisateurs", details_extra={"liste_complete": True}
    )
    _appliquer_fin_periode_tous(db)
    rows = db.execute(
        text(f"SELECT {SELECT_COMPTE_COLS} FROM compte_utilisateur WHERE COALESCE(est_supprime, false) = false")
    ).fetchall()
    return [CompteUtilisateurRead.model_validate(fe.decrypt_compte_row(dict(r._mapping))) for r in rows]


@router.get("/me", response_model=CompteUtilisateurRead)
def get_mon_compte(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    """Retourne le compte de l'utilisateur connecté."""
    _appliquer_fin_periode_si_necessaire(db, current_user.id_user)
    row = db.execute(
        text(f"SELECT {SELECT_COMPTE_COLS} FROM compte_utilisateur WHERE id_user = :id AND COALESCE(est_supprime, false) = false"),
        {"id": current_user.id_user},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte non trouvé")
    return CompteUtilisateurRead.model_validate(fe.decrypt_compte_row(dict(row._mapping)))


@router.patch("/me", response_model=CompteUtilisateurRead)
def modifier_mon_compte(
    body: CompteUtilisateurUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    """Permet à l'utilisateur connecté de modifier son email et/ou son mot de passe."""
    id_user = current_user.id_user
    updates = []
    params = {"id": id_user}

    if body.email is not None:
        email = body.email.strip().lower()
        existing = db.execute(
            text(
                f"SELECT id_user FROM compte_utilisateur WHERE {fe.sql_email_match_clause()} AND id_user != :id"
            ),
            {**fe.params_for_email_lookup(email), "id": id_user},
        ).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
        em_db, hmac_v = fe.persist_email_only(email)
        updates.append("email = :email")
        updates.append("email_hmac = :email_hmac")
        params["email"] = em_db
        params["email_hmac"] = hmac_v

    if body.password is not None:
        hashed_pw = bcrypt.hashpw(body.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        updates.append("password = :password")
        params["password"] = fe.persist_password_only(hashed_pw)

    if not updates:
        _appliquer_fin_periode_si_necessaire(db, id_user)
        row = db.execute(
            text(f"SELECT {SELECT_COMPTE_COLS} FROM compte_utilisateur WHERE id_user = :id"),
            {"id": id_user},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte non trouvé")
        return CompteUtilisateurRead.model_validate(fe.decrypt_compte_row(dict(row._mapping)))

    set_clause = ", ".join(updates)
    db.execute(
        text(f"UPDATE compte_utilisateur SET {set_clause} WHERE id_user = :id"),
        params,
    )
    db.commit()
    _appliquer_fin_periode_si_necessaire(db, id_user)
    row = db.execute(
        text(f"SELECT {SELECT_COMPTE_COLS} FROM compte_utilisateur WHERE id_user = :id"),
        {"id": id_user},
    ).fetchone()
    return CompteUtilisateurRead.model_validate(fe.decrypt_compte_row(dict(row._mapping)))


@router.post("/me/abonnement/souscrire", response_model=CompteUtilisateurRead)
def souscrire_abonnement(
    body: SouscrireAbonnement,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    """Souscrit à Premium ou Premium+ (mock paiement : pas de vrai paiement, période fixe 1 mois)."""
    id_user = current_user.id_user
    row = db.execute(
        text(f"SELECT id_user FROM compte_utilisateur WHERE id_user = :id AND COALESCE(est_supprime, false) = false"),
        {"id": id_user},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte non trouvé")
    date_fin = datetime.now(timezone.utc) + timedelta(days=30 * ABONNEMENT_DUREE_MOIS)
    db.execute(
        text("""
            UPDATE compte_utilisateur
            SET type_abonnement = :type_abonnement, date_fin_periode_payee = :date_fin, desabonnement_a_fin_periode = false
            WHERE id_user = :id
        """),
        {"id": id_user, "type_abonnement": body.type_abonnement, "date_fin": date_fin},
    )
    db.commit()
    row = db.execute(
        text(f"SELECT {SELECT_COMPTE_COLS} FROM compte_utilisateur WHERE id_user = :id"),
        {"id": id_user},
    ).fetchone()
    return CompteUtilisateurRead.model_validate(fe.decrypt_compte_row(dict(row._mapping)))


@router.post("/me/abonnement/desabonner", response_model=CompteUtilisateurRead)
def desabonner(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
):
    """Demande à ne pas renouveler : l'abonnement reste actif jusqu'à date_fin_periode_payee."""
    id_user = current_user.id_user
    row = db.execute(
        text(f"SELECT type_abonnement, desabonnement_a_fin_periode FROM compte_utilisateur WHERE id_user = :id AND COALESCE(est_supprime, false) = false"),
        {"id": id_user},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte non trouvé")
    if row.type_abonnement == "Freemium":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Compte déjà en Freemium")
    if row.desabonnement_a_fin_periode:
        # Idempotent : déjà désabonné à fin de période
        r = db.execute(
            text(f"SELECT {SELECT_COMPTE_COLS} FROM compte_utilisateur WHERE id_user = :id"),
            {"id": id_user},
        ).fetchone()
        return CompteUtilisateurRead.model_validate(fe.decrypt_compte_row(dict(r._mapping)))
    db.execute(
        text("UPDATE compte_utilisateur SET desabonnement_a_fin_periode = true WHERE id_user = :id"),
        {"id": id_user},
    )
    db.commit()
    _appliquer_fin_periode_si_necessaire(db, id_user)
    r = db.execute(
        text(f"SELECT {SELECT_COMPTE_COLS} FROM compte_utilisateur WHERE id_user = :id"),
        {"id": id_user},
    ).fetchone()
    return CompteUtilisateurRead.model_validate(fe.decrypt_compte_row(dict(r._mapping)))


@router.delete("/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_compte(
    id_user: int,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_utilisateur),
    db_logs: Database = Depends(get_mongo_logs),
):
    """Suppression logique (est_supprime=true). Le client peut se supprimer lui-même ; un Admin/Super-Admin peut supprimer tout compte. Les suppressions par un admin sur un tiers sont loguées."""
    if current_user.role not in ("Admin", "Super-Admin") and current_user.id_user != id_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Droits insuffisants")

    row = db.execute(
        text("SELECT id_user FROM compte_utilisateur WHERE id_user = :id AND COALESCE(est_supprime, false) = false"),
        {"id": id_user},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte non trouvé")

    if current_user.role in ("Admin", "Super-Admin") and current_user.id_user != id_user:
        log_admin_suppression_utilisateur_tiers(
            db_logs, current_user, "DELETE /api/utilisateurs/{id_user}", id_user_cible=id_user
        )

    db.execute(
        text("UPDATE compte_utilisateur SET est_supprime = true WHERE id_user = :id"),
        {"id": id_user},
    )
    db.commit()
    return None


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
    _appliquer_fin_periode_si_necessaire(db, id_user)
    row = db.execute(
        text(f"SELECT {SELECT_COMPTE_COLS} FROM compte_utilisateur WHERE id_user = :id AND COALESCE(est_supprime, false) = false"),
        {"id": id_user},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Compte non trouvé")
    return CompteUtilisateurRead.model_validate(fe.decrypt_compte_row(dict(row._mapping)))


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
