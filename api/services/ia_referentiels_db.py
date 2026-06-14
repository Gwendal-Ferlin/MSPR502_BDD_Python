"""Charge les référentiels IA depuis postgres-sante (fallback fichiers ia-reco)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from api.db.postgres_sante import SessionSante


def count_ref_ingredients(session: Session) -> int:
    row = session.execute(text("SELECT COUNT(*) AS n FROM ref_ingredient")).fetchone()
    return int(row._mapping["n"]) if row else 0


def load_materiels_catalogue(
    session: Session | None = None,
) -> list[dict[str, Any]] | None:
    """Format moteur IA : id, nom (aligné sur materiels.txt)."""
    own = session is None
    if own:
        session = SessionSante()
    try:
        rows = session.execute(
            text("SELECT id_materiel, nom FROM materiel ORDER BY id_materiel")
        ).fetchall()
        if not rows:
            return None
        return [
            {"id": int(r._mapping["id_materiel"]), "nom": r._mapping["nom"]}
            for r in rows
        ]
    finally:
        if own:
            session.close()


def load_exercice_materiel_liaisons(
    session: Session | None = None,
) -> list[dict[str, Any]] | None:
    own = session is None
    if own:
        session = SessionSante()
    try:
        rows = session.execute(
            text(
                "SELECT id_exercice, id_materiel FROM exercice_materiel ORDER BY id_exercice, id_materiel"
            )
        ).fetchall()
        if not rows:
            return None
        return [
            {
                "id_exercice": int(r._mapping["id_exercice"]),
                "id_materiel": int(r._mapping["id_materiel"]),
            }
            for r in rows
        ]
    finally:
        if own:
            session.close()


def load_exercices_catalogue(
    session: Session | None = None,
) -> list[dict[str, Any]] | None:
    """Liste au format moteur IA : id, nom, muscle, niveau."""
    own = session is None
    if own:
        session = SessionSante()
    try:
        rows = session.execute(
            text(
                """
                SELECT id_exercice, nom, muscle_principal, niveau
                FROM ref_exercice
                WHERE niveau IS NOT NULL
                ORDER BY id_exercice
                """
            )
        ).fetchall()
        if not rows:
            return None
        return [
            {
                "id": int(r._mapping["id_exercice"]),
                "nom": r._mapping["nom"],
                "muscle": r._mapping["muscle_principal"] or "",
                "niveau": (r._mapping["niveau"] or "normal").lower().strip(),
            }
            for r in rows
        ]
    finally:
        if own:
            session.close()


def load_restriction_equivalences(
    session: Session | None = None,
) -> dict[str, list[str]] | None:
    """Dict cle_canonique -> liste d'alias (comme restrictions_equivalences.json)."""
    own = session is None
    if own:
        session = SessionSante()
    try:
        cles = session.execute(
            text(
                "SELECT cle_canonique FROM ref_restriction_equivalence ORDER BY cle_canonique"
            )
        ).fetchall()
        if not cles:
            return None
        result: dict[str, list[str]] = {}
        for row in cles:
            cle = row._mapping["cle_canonique"]
            aliases = session.execute(
                text(
                    """
                    SELECT alias FROM ref_restriction_alias
                    WHERE cle_canonique = :cle
                    ORDER BY id_alias
                    """
                ),
                {"cle": cle},
            ).fetchall()
            result[cle] = [a._mapping["alias"] for a in aliases]
        return result
    finally:
        if own:
            session.close()


def load_ingredients_by_budget(
    niveau_budget: int,
    max_items: int = 120,
    session: Session | None = None,
) -> list[dict[str, Any]] | None:
    """Même logique que charger_ingredients_par_budget (fichier), via SQL."""
    own = session is None
    if own:
        session = SessionSante()
    try:
        if count_ref_ingredients(session) == 0:
            return None
        rows = session.execute(
            text(
                """
                SELECT DISTINCT ON (lower(nom))
                    nom, budget, calories, proteines, glucides, lipides
                FROM ref_ingredient
                WHERE budget <= :budget
                ORDER BY lower(nom), nom
                LIMIT :limit
                """
            ),
            {"budget": niveau_budget, "limit": max(max_items * 3, 500)},
        ).fetchall()
        ingredients: list[dict[str, Any]] = []
        seen: set[str] = set()
        for r in rows:
            nom = r._mapping["nom"]
            cle = str(nom).strip().lower()
            if cle in seen:
                continue
            seen.add(cle)
            ingredients.append(
                {
                    "nom": nom,
                    "budget": int(r._mapping["budget"]),
                    "calories": r._mapping["calories"],
                    "proteines": r._mapping["proteines"],
                    "glucides": r._mapping["glucides"],
                    "lipides": r._mapping["lipides"],
                }
            )
            if len(ingredients) >= max_items:
                break
        return ingredients or None
    finally:
        if own:
            session.close()


def persist_new_restriction_equivalence(cle: str, aliases: list[str]) -> None:
    """Enregistre une nouvelle clé d'équivalence (best-effort, comme l'ancien JSON)."""
    cle = cle.strip().lower()
    if not cle:
        return
    with SessionSante() as session:
        session.execute(
            text(
                "INSERT INTO ref_restriction_equivalence (cle_canonique) VALUES (:cle) ON CONFLICT DO NOTHING"
            ),
            {"cle": cle},
        )
        for alias in aliases:
            a = str(alias).strip().lower()
            if not a:
                continue
            session.execute(
                text(
                    """
                    INSERT INTO ref_restriction_alias (cle_canonique, alias)
                    VALUES (:cle, :alias)
                    ON CONFLICT (cle_canonique, alias) DO NOTHING
                    """
                ),
                {"cle": cle, "alias": a},
            )
        session.commit()
