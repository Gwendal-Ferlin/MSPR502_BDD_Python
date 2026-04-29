#!/usr/bin/env python3
"""
Effacement définitif des comptes en suppression logique depuis plus de N jours (RGPD).

Usage (depuis la racine du dépôt, avec le même .env que l’API) :
  python scripts/purge_comptes_rgpd.py
  python scripts/purge_comptes_rgpd.py --dry-run

Planifier en production (ex. mensuel) : cron / systemd timer / tâche TrueNAS.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

# Racine du dépôt = parent de scripts/
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pymongo import MongoClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.config import settings
from api.db.postgres_gamification import SessionGamification
from api.db.postgres_sante import SessionSante
from api.db.postgres_utilisateur import SessionUtilisateur


def _eligible_users(db_u: Session, cutoff: datetime) -> list[tuple[int, UUID]]:
    rows = db_u.execute(
        text(
            """
            SELECT cu.id_user, v.id_anonyme
            FROM compte_utilisateur cu
            INNER JOIN vault_correspondance v ON v.id_user = cu.id_user
            WHERE cu.est_supprime = true
              AND cu.date_suppression IS NOT NULL
              AND cu.date_suppression <= :cutoff
            """
        ),
        {"cutoff": cutoff},
    ).fetchall()
    out: list[tuple[int, UUID]] = []
    for r in rows:
        out.append((r.id_user, r.id_anonyme))
    return out


def _purge_auxiliary_data(db_s: Session, db_g: Session, id_anonyme: UUID) -> None:
    deletes_sante = [
        "DELETE FROM utilisateur_restriction WHERE id_anonyme = :aid",
        "DELETE FROM utilisateur_materiel WHERE id_anonyme = :aid",
        "DELETE FROM journal_alimentaire WHERE id_anonyme = :aid",
        "DELETE FROM objectif_utilisateur WHERE id_anonyme = :aid",
        "DELETE FROM suivi_biometrique WHERE id_anonyme = :aid",
        "DELETE FROM seance_activite WHERE id_anonyme = :aid",
        "DELETE FROM profil_sante WHERE id_anonyme = :aid",
    ]
    for q in deletes_sante:
        db_s.execute(text(q), {"aid": id_anonyme})
    deletes_g = [
        "DELETE FROM gamification_transactions WHERE user_id = :aid",
        "DELETE FROM gamification_user_currency WHERE user_id = :aid",
        "DELETE FROM gamification_user_inventory WHERE user_id = :aid",
    ]
    for q in deletes_g:
        db_g.execute(text(q), {"aid": id_anonyme})


def _purge_mongo(
    mongo_logs_db,
    mongo_reco_db,
    id_anonyme: UUID,
    id_user: int,
) -> None:
    uid_str = str(id_anonyme)
    mongo_logs_db["evenements"].delete_many({"id_anonyme": uid_str})
    mongo_logs_db["evenements"].delete_many({"details_techniques.id_user_cible": id_user})
    names = mongo_reco_db.list_collection_names()
    if "repas" in names:
        mongo_reco_db["repas"].delete_many({"id_anonyme": uid_str})
    if "recommendations" in names:
        mongo_reco_db["recommendations"].delete_many({"id_anonyme": uid_str})


def _purge_one(
    db_u: Session,
    db_s: Session,
    db_g: Session,
    mongo_logs_db,
    mongo_reco_db,
    id_user: int,
    id_anonyme: UUID,
    *,
    dry_run: bool,
) -> None:
    if dry_run:
        print(f"[dry-run] purgerait id_user={id_user} id_anonyme={id_anonyme}")
        return
    _purge_auxiliary_data(db_s, db_g, id_anonyme)
    db_s.commit()
    db_g.commit()
    _purge_mongo(mongo_logs_db, mongo_reco_db, id_anonyme, id_user)
    db_u.execute(
        text("DELETE FROM compte_utilisateur WHERE id_user = :id"),
        {"id": id_user},
    )
    db_u.commit()
    print(f"OK suppression définitive id_user={id_user}")


def main() -> None:
    p = argparse.ArgumentParser(description="Purge RGPD des comptes soft-deletes expirés.")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Lister les comptes éligibles sans rien effacer.",
    )
    args = p.parse_args()
    retention = settings.rgpd_soft_delete_retention_days
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention)
    print(f"Rétention = {retention} j ; seuil date_suppression <= {cutoff.isoformat()}")

    db_u = SessionUtilisateur()
    db_s = SessionSante()
    db_g = SessionGamification()
    mongo_logs = MongoClient(settings.mongodb_logs_url)[settings.mongodb_logs_db]
    mongo_reco = MongoClient(settings.mongodb_reco_url)[settings.mongodb_reco_db]
    try:
        candidates = _eligible_users(db_u, cutoff)
        if not candidates:
            print("Aucun compte éligible.")
            return
        print(f"{len(candidates)} compte(s) éligible(s).")
        for id_user, id_anonyme in candidates:
            try:
                _purge_one(
                    db_u,
                    db_s,
                    db_g,
                    mongo_logs,
                    mongo_reco,
                    id_user,
                    id_anonyme,
                    dry_run=args.dry_run,
                )
            except Exception as e:
                db_s.rollback()
                db_g.rollback()
                db_u.rollback()
                print(f"ERREUR id_user={id_user}: {e}", file=sys.stderr)
    finally:
        db_u.close()
        db_s.close()
        db_g.close()


if __name__ == "__main__":
    main()
