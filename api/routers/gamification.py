from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user, require_roles
from api.config import settings
from api.db.postgres_gamification import get_session_gamification
from api.schemas.auth import CurrentUser
from api.schemas.gamification import (
    ApiResponse,
    AddCoinsRequest,
    BuyAnimalRequest,
    BuyChromaRequest,
    SetActiveChromaRequest,
    ToggleVisibilityRequest,
)

router = APIRouter(prefix="/gamification", tags=["Gamification"])

AdminOrSuperAdmin = Annotated[CurrentUser, Depends(require_roles(["Admin", "Super-Admin"]))]


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))],
) -> CurrentUser | None:
    if not credentials or not credentials.credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        id_user = payload.get("id_user")
        email = payload.get("email")
        role = payload.get("role")
        id_anonyme = payload.get("id_anonyme")
        if id_user is None or email is None or role is None or id_anonyme is None:
            return None
        return CurrentUser(id_user=id_user, email=email, role=role, id_anonyme=id_anonyme)
    except JWTError:
        return None


def _ensure_currency_row(db: Session, user_id: UUID) -> dict[str, Any]:
    row = db.execute(
        text(
            """
            SELECT user_id, coins, total_coins_earned, total_coins_spent
            FROM gamification_user_currency
            WHERE user_id = :uid
            """
        ),
        {"uid": str(user_id)},
    ).fetchone()
    if row:
        return dict(row._mapping)
    db.execute(
        text(
            """
            INSERT INTO gamification_user_currency (user_id, coins, total_coins_earned, total_coins_spent, updated_at)
            VALUES (:uid, 500, 500, 0, now())
            """
        ),
        {"uid": str(user_id)},
    )
    row = db.execute(
        text(
            """
            SELECT user_id, coins, total_coins_earned, total_coins_spent
            FROM gamification_user_currency
            WHERE user_id = :uid
            """
        ),
        {"uid": str(user_id)},
    ).fetchone()
    return dict(row._mapping)


@router.get("/inventory", response_model=ApiResponse)
def get_inventory(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_gamification),
):
    user_id = UUID(current_user.id_anonyme)
    currency = _ensure_currency_row(db, user_id)

    animals_rows = db.execute(
        text(
            """
            SELECT animal_id, is_visible, active_chroma_id, acquired_at
            FROM gamification_user_inventory
            WHERE user_id = :uid
            ORDER BY acquired_at ASC
            """
        ),
        {"uid": str(user_id)},
    ).fetchall()

    chroma_rows = db.execute(
        text(
            """
            SELECT animal_id, chroma_id
            FROM gamification_user_chromas
            WHERE user_id = :uid
            ORDER BY animal_id, chroma_id
            """
        ),
        {"uid": str(user_id)},
    ).fetchall()

    chromas: dict[str, list[str]] = defaultdict(list)
    for r in chroma_rows:
        chromas[r._mapping["animal_id"]].append(r._mapping["chroma_id"])

    animals = []
    for r in animals_rows:
        m = r._mapping
        acquired_at = m["acquired_at"]
        if isinstance(acquired_at, datetime) and acquired_at.tzinfo is None:
            acquired_at = acquired_at.replace(tzinfo=timezone.utc)
        animals.append(
            {
                "animal_id": m["animal_id"],
                "is_visible": m["is_visible"],
                "active_chroma_id": m["active_chroma_id"],
                "acquired_at": acquired_at,
            }
        )

    return ApiResponse(
        success=True,
        data={
            "coins": currency["coins"],
            "animals": animals,
            "chromas": chromas,
        },
    )


@router.post("/animals/buy", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def buy_animal(
    body: BuyAnimalRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_gamification),
):
    user_id = UUID(current_user.id_anonyme)
    animal_id = body.animal_id.strip()

    cfg = db.execute(
        text(
            """
            SELECT animal_id, price, is_available
            FROM gamification_animals_config
            WHERE animal_id = :animal_id
            """
        ),
        {"animal_id": animal_id},
    ).fetchone()
    if not cfg or not cfg._mapping["is_available"]:
        raise HTTPException(status_code=400, detail="Animal indisponible")
    cfg_price = int(cfg._mapping["price"])
    if int(body.price) != cfg_price:
        raise HTTPException(status_code=400, detail="Prix invalide")

    try:
        db.execute(text("BEGIN"))

        currency = db.execute(
            text(
                """
                SELECT coins, total_coins_earned, total_coins_spent
                FROM gamification_user_currency
                WHERE user_id = :uid
                FOR UPDATE
                """
            ),
            {"uid": str(user_id)},
        ).fetchone()
        if not currency:
            db.execute(
                text(
                    """
                    INSERT INTO gamification_user_currency (user_id, coins, total_coins_earned, total_coins_spent, updated_at)
                    VALUES (:uid, 500, 500, 0, now())
                    """
                ),
                {"uid": str(user_id)},
            )
            currency = db.execute(
                text(
                    """
                    SELECT coins, total_coins_earned, total_coins_spent
                    FROM gamification_user_currency
                    WHERE user_id = :uid
                    FOR UPDATE
                    """
                ),
                {"uid": str(user_id)},
            ).fetchone()

        coins = int(currency._mapping["coins"])
        if coins < cfg_price:
            db.execute(text("ROLLBACK"))
            return ApiResponse(
                success=False,
                error="insufficient_funds",
                message="Vous n'avez pas assez de pépites",
            )

        existing = db.execute(
            text(
                """
                SELECT 1
                FROM gamification_user_inventory
                WHERE user_id = :uid AND animal_id = :animal_id
                """
            ),
            {"uid": str(user_id), "animal_id": animal_id},
        ).fetchone()
        if existing:
            db.execute(text("ROLLBACK"))
            return ApiResponse(
                success=False,
                error="already_owned",
                message="Vous possédez déjà cet animal",
            )

        db.execute(
            text(
                """
                INSERT INTO gamification_user_inventory (user_id, animal_id, is_visible, active_chroma_id, acquired_at, updated_at)
                VALUES (:uid, :animal_id, true, 'default', now(), now())
                """
            ),
            {"uid": str(user_id), "animal_id": animal_id},
        )

        # Le chroma "default" est offert à l'achat de l'animal.
        db.execute(
            text(
                """
                INSERT INTO gamification_user_chromas (user_id, animal_id, chroma_id, purchased_at)
                VALUES (:uid, :animal_id, 'default', now())
                ON CONFLICT (user_id, animal_id, chroma_id) DO NOTHING
                """
            ),
            {"uid": str(user_id), "animal_id": animal_id},
        )

        db.execute(
            text(
                """
                UPDATE gamification_user_currency
                SET coins = coins - :price,
                    total_coins_spent = total_coins_spent + :price,
                    updated_at = now()
                WHERE user_id = :uid
                """
            ),
            {"uid": str(user_id), "price": cfg_price},
        )

        tx = db.execute(
            text(
                """
                INSERT INTO gamification_transactions (user_id, transaction_type, amount, animal_id, chroma_id, created_at, metadata)
                VALUES (:uid, 'animal_purchase', :amount, :animal_id, NULL, now(), NULL)
                RETURNING id
                """
            ),
            {"uid": str(user_id), "amount": cfg_price, "animal_id": animal_id},
        ).fetchone()

        remaining = db.execute(
            text("SELECT coins FROM gamification_user_currency WHERE user_id = :uid"),
            {"uid": str(user_id)},
        ).fetchone()
        db.execute(text("COMMIT"))

        return ApiResponse(
            success=True,
            message="Animal acheté avec succès",
            data={
                "animal_id": animal_id,
                "remaining_coins": int(remaining._mapping["coins"]),
                "transaction_id": str(tx._mapping["id"]),
            },
        )
    except Exception:
        db.execute(text("ROLLBACK"))
        raise


@router.post("/chromas/buy", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def buy_chroma(
    body: BuyChromaRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_gamification),
):
    user_id = UUID(current_user.id_anonyme)
    animal_id = body.animal_id.strip()
    chroma_id = body.chroma_id.strip()

    # Le chroma doit exister dans le catalogue.
    cfg = db.execute(
        text(
            """
            SELECT price, is_available
            FROM gamification_chromas_config
            WHERE animal_id = :animal_id AND chroma_id = :chroma_id
            """
        ),
        {"animal_id": animal_id, "chroma_id": chroma_id},
    ).fetchone()
    if not cfg or not cfg._mapping["is_available"]:
        raise HTTPException(status_code=400, detail="Chroma indisponible")
    cfg_price = int(cfg._mapping["price"])
    if int(body.price) != cfg_price:
        raise HTTPException(status_code=400, detail="Prix invalide")

    owned_animal = db.execute(
        text(
            "SELECT 1 FROM gamification_user_inventory WHERE user_id = :uid AND animal_id = :animal_id"
        ),
        {"uid": str(user_id), "animal_id": animal_id},
    ).fetchone()
    if not owned_animal:
        raise HTTPException(status_code=400, detail="Animal non possédé")

    try:
        db.execute(text("BEGIN"))
        currency = db.execute(
            text(
                """
                SELECT coins
                FROM gamification_user_currency
                WHERE user_id = :uid
                FOR UPDATE
                """
            ),
            {"uid": str(user_id)},
        ).fetchone()
        if not currency:
            db.execute(
                text(
                    """
                    INSERT INTO gamification_user_currency (user_id, coins, total_coins_earned, total_coins_spent, updated_at)
                    VALUES (:uid, 500, 500, 0, now())
                    """
                ),
                {"uid": str(user_id)},
            )
            currency = db.execute(
                text(
                    "SELECT coins FROM gamification_user_currency WHERE user_id = :uid FOR UPDATE"
                ),
                {"uid": str(user_id)},
            ).fetchone()

        coins = int(currency._mapping["coins"])
        if coins < cfg_price:
            db.execute(text("ROLLBACK"))
            return ApiResponse(
                success=False,
                error="insufficient_funds",
                message="Vous n'avez pas assez de pépites",
            )

        already = db.execute(
            text(
                """
                SELECT 1
                FROM gamification_user_chromas
                WHERE user_id = :uid AND animal_id = :animal_id AND chroma_id = :chroma_id
                """
            ),
            {"uid": str(user_id), "animal_id": animal_id, "chroma_id": chroma_id},
        ).fetchone()
        if already:
            db.execute(text("ROLLBACK"))
            return ApiResponse(
                success=False,
                error="already_owned",
                message="Vous possédez déjà cette couleur",
            )

        db.execute(
            text(
                """
                INSERT INTO gamification_user_chromas (user_id, animal_id, chroma_id, purchased_at)
                VALUES (:uid, :animal_id, :chroma_id, now())
                """
            ),
            {"uid": str(user_id), "animal_id": animal_id, "chroma_id": chroma_id},
        )

        db.execute(
            text(
                """
                UPDATE gamification_user_currency
                SET coins = coins - :price,
                    total_coins_spent = total_coins_spent + :price,
                    updated_at = now()
                WHERE user_id = :uid
                """
            ),
            {"uid": str(user_id), "price": cfg_price},
        )

        tx = db.execute(
            text(
                """
                INSERT INTO gamification_transactions (user_id, transaction_type, amount, animal_id, chroma_id, created_at, metadata)
                VALUES (:uid, 'chroma_purchase', :amount, :animal_id, :chroma_id, now(), NULL)
                RETURNING id
                """
            ),
            {"uid": str(user_id), "amount": cfg_price, "animal_id": animal_id, "chroma_id": chroma_id},
        ).fetchone()

        remaining = db.execute(
            text("SELECT coins FROM gamification_user_currency WHERE user_id = :uid"),
            {"uid": str(user_id)},
        ).fetchone()
        db.execute(text("COMMIT"))

        return ApiResponse(
            success=True,
            message="Couleur achetée",
            data={
                "animal_id": animal_id,
                "chroma_id": chroma_id,
                "remaining_coins": int(remaining._mapping["coins"]),
                "transaction_id": str(tx._mapping["id"]),
            },
        )
    except Exception:
        db.execute(text("ROLLBACK"))
        raise


@router.put("/chromas/set-active", response_model=ApiResponse)
def set_active_chroma(
    body: SetActiveChromaRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_gamification),
):
    user_id = UUID(current_user.id_anonyme)
    animal_id = body.animal_id.strip()
    chroma_id = body.chroma_id.strip()

    owned = db.execute(
        text(
            """
            SELECT 1
            FROM gamification_user_chromas
            WHERE user_id = :uid AND animal_id = :animal_id AND chroma_id = :chroma_id
            """
        ),
        {"uid": str(user_id), "animal_id": animal_id, "chroma_id": chroma_id},
    ).fetchone()
    if not owned:
        raise HTTPException(status_code=400, detail="Chroma non possédé")

    updated = db.execute(
        text(
            """
            UPDATE gamification_user_inventory
            SET active_chroma_id = :chroma_id, updated_at = now()
            WHERE user_id = :uid AND animal_id = :animal_id
            RETURNING animal_id, active_chroma_id
            """
        ),
        {"uid": str(user_id), "animal_id": animal_id, "chroma_id": chroma_id},
    ).fetchone()
    if not updated:
        raise HTTPException(status_code=400, detail="Animal non possédé")
    db.commit()
    return ApiResponse(
        success=True,
        message="Couleur activée",
        data=dict(updated._mapping),
    )


@router.put("/animals/toggle-visibility", response_model=ApiResponse)
def toggle_visibility(
    body: ToggleVisibilityRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_gamification),
):
    user_id = UUID(current_user.id_anonyme)
    animal_id = body.animal_id.strip()
    updated = db.execute(
        text(
            """
            UPDATE gamification_user_inventory
            SET is_visible = :is_visible, updated_at = now()
            WHERE user_id = :uid AND animal_id = :animal_id
            RETURNING animal_id, is_visible
            """
        ),
        {"uid": str(user_id), "animal_id": animal_id, "is_visible": body.is_visible},
    ).fetchone()
    if not updated:
        raise HTTPException(status_code=400, detail="Animal non possédé")
    db.commit()
    return ApiResponse(success=True, data=dict(updated._mapping))


@router.post("/coins/add", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def add_coins(
    body: AddCoinsRequest,
    _: AdminOrSuperAdmin,
    db: Session = Depends(get_session_gamification),
):
    user_id = body.user_id
    amount = int(body.amount)

    try:
        db.execute(text("BEGIN"))

        row = db.execute(
            text(
                """
                SELECT coins, total_coins_earned, total_coins_spent
                FROM gamification_user_currency
                WHERE user_id = :uid
                FOR UPDATE
                """
            ),
            {"uid": str(user_id)},
        ).fetchone()
        if not row:
            db.execute(
                text(
                    """
                    INSERT INTO gamification_user_currency (user_id, coins, total_coins_earned, total_coins_spent, updated_at)
                    VALUES (:uid, 500, 500, 0, now())
                    """
                ),
                {"uid": str(user_id)},
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
            {"uid": str(user_id), "amount": amount},
        )

        metadata: dict[str, Any] | None = body.metadata
        if body.reason:
            metadata = {**(metadata or {}), "reason": body.reason}

        tx = db.execute(
            text(
                """
                INSERT INTO gamification_transactions (user_id, transaction_type, amount, animal_id, chroma_id, created_at, metadata)
                VALUES (:uid, 'earn', :amount, NULL, NULL, now(), CAST(:metadata AS jsonb))
                RETURNING id
                """
            ),
            {"uid": str(user_id), "amount": amount, "metadata": None if metadata is None else str(metadata).replace("'", '"')},
        ).fetchone()

        coins_row = db.execute(
            text("SELECT coins FROM gamification_user_currency WHERE user_id = :uid"),
            {"uid": str(user_id)},
        ).fetchone()

        db.execute(text("COMMIT"))
        return ApiResponse(
            success=True,
            data={
                "coins": int(coins_row._mapping["coins"]),
                "transaction_id": str(tx._mapping["id"]),
            },
        )
    except Exception:
        db.execute(text("ROLLBACK"))
        raise


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_gamification),
):
    user_id = UUID(current_user.id_anonyme)
    currency = _ensure_currency_row(db, user_id)

    total_animals = db.execute(
        text("SELECT COUNT(*) AS c FROM gamification_user_inventory WHERE user_id = :uid"),
        {"uid": str(user_id)},
    ).fetchone()._mapping["c"]

    rare_or_better = db.execute(
        text(
            """
            SELECT COUNT(*) AS c
            FROM gamification_user_inventory i
            JOIN gamification_animals_config a ON a.animal_id = i.animal_id
            WHERE i.user_id = :uid
              AND a.rarity IN ('rare', 'epic', 'legendary')
            """
        ),
        {"uid": str(user_id)},
    ).fetchone()._mapping["c"]

    available_total = db.execute(
        text("SELECT COUNT(*) AS c FROM gamification_animals_config WHERE is_available = true"),
    ).fetchone()._mapping["c"]

    completion = 0.0
    if int(available_total) > 0:
        completion = (float(total_animals) / float(available_total)) * 100.0

    return ApiResponse(
        success=True,
        data={
            "total_animals": int(total_animals),
            "rare_or_better": int(rare_or_better),
            "completion_percentage": completion,
            "total_coins_earned": int(currency["total_coins_earned"]),
            "total_coins_spent": int(currency["total_coins_spent"]),
            "current_coins": int(currency["coins"]),
        },
    )


@router.get("/animals/catalog", response_model=ApiResponse)
def animals_catalog(
    current_user: Annotated[CurrentUser | None, Depends(_optional_current_user)],
    db: Session = Depends(get_session_gamification),
):
    user_uuid: UUID | None = UUID(current_user.id_anonyme) if current_user else None

    animals_cfg = db.execute(
        text(
            """
            SELECT animal_id, name, emoji, price, rarity, description, is_available
            FROM gamification_animals_config
            WHERE is_available = true
            ORDER BY price ASC, animal_id ASC
            """
        )
    ).fetchall()

    inv_by_animal: dict[str, dict[str, Any]] = {}
    owned_chromas: dict[str, set[str]] = defaultdict(set)
    if user_uuid:
        inv_rows = db.execute(
            text(
                """
                SELECT animal_id, active_chroma_id
                FROM gamification_user_inventory
                WHERE user_id = :uid
                """
            ),
            {"uid": str(user_uuid)},
        ).fetchall()
        inv_by_animal = {r._mapping["animal_id"]: dict(r._mapping) for r in inv_rows}

        chroma_rows = db.execute(
            text(
                """
                SELECT animal_id, chroma_id
                FROM gamification_user_chromas
                WHERE user_id = :uid
                """
            ),
            {"uid": str(user_uuid)},
        ).fetchall()
        for r in chroma_rows:
            owned_chromas[r._mapping["animal_id"]].add(r._mapping["chroma_id"])

    chromas_cfg = db.execute(
        text(
            """
            SELECT animal_id, chroma_id, name, price, row_y, is_available
            FROM gamification_chromas_config
            WHERE is_available = true
            ORDER BY animal_id, price ASC, chroma_id ASC
            """
        )
    ).fetchall()
    chromas_by_animal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in chromas_cfg:
        chromas_by_animal[r._mapping["animal_id"]].append(dict(r._mapping))

    out_animals = []
    for r in animals_cfg:
        a = dict(r._mapping)
        animal_id = a["animal_id"]
        owned = animal_id in inv_by_animal
        active = inv_by_animal.get(animal_id, {}).get("active_chroma_id", "default") if owned else None

        owned_list = sorted(list(owned_chromas.get(animal_id, set())))
        if owned and "default" not in owned_chromas.get(animal_id, set()):
            # Compat : l'achat d'un animal offre toujours "default"
            owned_list = ["default"] + owned_list

        available = chromas_by_animal.get(animal_id, [])
        # S'assurer que "default" est visible dans le catalogue même si absent du seed.
        if not any(c["chroma_id"] == "default" for c in available):
            available = [
                {
                    "animal_id": animal_id,
                    "chroma_id": "default",
                    "name": "Original",
                    "price": 0,
                    "row_y": 0,
                    "is_available": True,
                },
                *available,
            ]

        available_view = []
        for c in available:
            cid = c["chroma_id"]
            available_view.append(
                {
                    "chroma_id": cid,
                    "name": c["name"],
                    "price": int(c["price"]),
                    "owned": owned and (cid in owned_chromas.get(animal_id, set()) or cid == "default"),
                    "active": owned and active == cid,
                }
            )

        out_animals.append(
            {
                "animal_id": animal_id,
                "name": a["name"],
                "emoji": a["emoji"],
                "price": int(a["price"]),
                "rarity": a["rarity"],
                "description": a.get("description"),
                "owned": owned,
                "active_chroma": active if owned else None,
                "owned_chromas": owned_list if owned else [],
                "available_chromas": available_view,
            }
        )

    return ApiResponse(success=True, data={"animals": out_animals})

