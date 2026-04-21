"""Récompenses monnaie (pépites) liées à d'autres domaines (ex. repas Mongo)."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

# Pépites attribuées à chaque création de repas (reco Mongo)
COINS_PER_REPAS_CREATED = 100


def reward_coins_repas_created(
    db: Session,
    id_anonyme: str,
    *,
    repas_id: str,
    amount: int = COINS_PER_REPAS_CREATED,
) -> dict[str, Any]:
    """
    Crédite la monnaie gamification pour un utilisateur (id_anonyme = user_id).
    Insère une transaction de type 'earn'. Retourne id ligne monnaie, solde, id transaction.
    """
    uid = str(UUID(id_anonyme))
    metadata = json.dumps(
        {"source": "reco_repas", "repas_id": repas_id, "amount": amount},
        ensure_ascii=False,
    )

    try:
        db.execute(text("BEGIN"))

        row = db.execute(
            text(
                """
                SELECT id, coins, total_coins_earned, total_coins_spent
                FROM gamification_user_currency
                WHERE user_id = :uid
                FOR UPDATE
                """
            ),
            {"uid": uid},
        ).fetchone()
        if not row:
            db.execute(
                text(
                    """
                    INSERT INTO gamification_user_currency (user_id, coins, total_coins_earned, total_coins_spent, updated_at)
                    VALUES (:uid, 0, 0, 0, now())
                    """
                ),
                {"uid": uid},
            )

        db.execute(
            text(
                """
                UPDATE gamification_user_currency
                SET coins = coins + :amount,
                    total_coins_earned = total_coins_earned + :amount,
                    updated_at = now()
                WHERE user_id = :uid
                """
            ),
            {"uid": uid, "amount": amount},
        )

        tx = db.execute(
            text(
                """
                INSERT INTO gamification_transactions (user_id, transaction_type, amount, animal_id, chroma_id, created_at, metadata)
                VALUES (:uid, 'earn', :amount, NULL, NULL, now(), CAST(:metadata AS jsonb))
                RETURNING id
                """
            ),
            {"uid": uid, "amount": amount, "metadata": metadata},
        ).fetchone()

        coins_row = db.execute(
            text("SELECT id, coins FROM gamification_user_currency WHERE user_id = :uid"),
            {"uid": uid},
        ).fetchone()

        db.execute(text("COMMIT"))
    except Exception:
        db.execute(text("ROLLBACK"))
        raise

    return {
        "currency_id": str(coins_row._mapping["id"]),
        "coins_earned": amount,
        "total_coins": int(coins_row._mapping["coins"]),
        "transaction_id": str(tx._mapping["id"]),
    }
