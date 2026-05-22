#!/usr/bin/env python3
"""
Importe dans postgres-sante (sante_db) :
  - ia-reco/exercices.txt          -> ref_exercice (+ colonne niveau)
  - ia-reco/restrictions_equivalences.json -> ref_restriction_equivalence + ref_restriction_alias
  - ia-reco/materiels.txt                  -> materiel (IDs 1..n, ordre du fichier)
  - ia-reco/exercice_materiel.txt          -> exercice_materiel (liaisons IA)
  - ia-reco/final_ingredients_list.json    -> ref_ingredient (JSONL, ~300k lignes)

Usage (racine du dépôt, .env configuré) :
  python scripts/import_ia_referentiels_sante.py

Docker :
  docker compose exec api python scripts/import_ia_referentiels_sante.py
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.db.postgres_sante import SessionSante  # noqa: E402

# Noms invalides type « by Marque » (sans produit) dans le JSON source
SQL_DELETE_INGREDIENTS_JUNK = (
    "DELETE FROM ref_ingredient WHERE lower(btrim(nom)) LIKE 'by %'"
)

IA_RECO = ROOT / "ia-reco"
EXERCICES_FILE = IA_RECO / "exercices.txt"
RESTRICTIONS_FILE = IA_RECO / "restrictions_equivalences.json"
INGREDIENTS_FILE = IA_RECO / "final_ingredients_list.json"
MATERIELS_FILE = IA_RECO / "materiels.txt"
EXERCICE_MATERIEL_FILE = IA_RECO / "exercice_materiel.txt"

BATCH_SIZE = 2000
LIAISON_PATTERN = re.compile(r"\((\d+),\s*(\d+)\)")
EXERCICE_PATTERN = re.compile(
    r"\((\d+),\s*'([^']+)',\s*'([^']+)'(?:,\s*'([^']+)')?\)"
)


def parse_exercices(path: Path) -> list[tuple[int, str, str, str]]:
    rows: list[tuple[int, str, str, str]] = []
    text_content = path.read_text(encoding="utf-8")
    for line in text_content.splitlines():
        line = line.strip().rstrip(",")
        if not line.startswith("("):
            continue
        try:
            t = ast.literal_eval(line)
        except (SyntaxError, ValueError):
            continue
        if len(t) < 3:
            continue
        rows.append(
            (
                int(t[0]),
                str(t[1]),
                str(t[2]),
                str(t[3]).lower().strip() if len(t) > 3 and t[3] else "normal",
            )
        )
    if rows:
        return rows
    for match in EXERCICE_PATTERN.finditer(text_content):
        ex_id, nom, muscle, niveau = match.groups()
        rows.append(
            (
                int(ex_id),
                nom,
                muscle,
                (niveau or "normal").lower().strip(),
            )
        )
    return rows


def import_exercices(session) -> int:
    if not EXERCICES_FILE.is_file():
        raise FileNotFoundError(EXERCICES_FILE)
    rows = parse_exercices(EXERCICES_FILE)
    if not rows:
        raise RuntimeError("Aucun exercice parsé depuis exercices.txt")

    session.execute(text("TRUNCATE detail_performance"))
    session.execute(text("DELETE FROM ref_exercice"))
    session.execute(
        text(
            """
            INSERT INTO ref_exercice (id_exercice, nom, muscle_principal, niveau)
            VALUES (:id, :nom, :muscle, :niveau)
            """
        ),
        [
            {"id": i, "nom": n, "muscle": m, "niveau": nv}
            for i, n, m, nv in rows
        ],
    )
    session.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('ref_exercice', 'id_exercice'), "
            "(SELECT COALESCE(MAX(id_exercice), 1) FROM ref_exercice))"
        )
    )
    return len(rows)


def parse_materiels(path: Path) -> list[tuple[int, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    rows: list[tuple[int, str]] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        nom = line.strip()
        if nom:
            rows.append((idx + 1, nom))
    return rows


def parse_exercice_materiel(path: Path) -> list[tuple[int, int]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    rows: list[tuple[int, int]] = []
    content = path.read_text(encoding="utf-8")
    for line in content.splitlines():
        line = line.strip().rstrip(",;")
        if not line.startswith("("):
            continue
        try:
            t = ast.literal_eval(line if line.startswith("(") else f"({line}")
            if not isinstance(t, tuple) or len(t) < 2:
                continue
            rows.append((int(t[0]), int(t[1])))
        except (SyntaxError, ValueError):
            continue
    if rows:
        return rows
    for ex_id, mat_id in LIAISON_PATTERN.findall(content):
        rows.append((int(ex_id), int(mat_id)))
    return rows


def import_materiels(session) -> tuple[int, int]:
    """Réimporte le catalogue matériel IA + liaisons exercice_materiel."""
    materiels = parse_materiels(MATERIELS_FILE)
    if not materiels:
        raise RuntimeError("Aucun matériel parsé depuis materiels.txt")

    session.execute(text("TRUNCATE utilisateur_materiel"))
    session.execute(text("TRUNCATE exercice_materiel"))
    session.execute(text("DELETE FROM materiel"))
    session.execute(
        text("INSERT INTO materiel (id_materiel, nom) VALUES (:id, :nom)"),
        [{"id": i, "nom": n} for i, n in materiels],
    )
    session.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('materiel', 'id_materiel'), "
            "(SELECT COALESCE(MAX(id_materiel), 1) FROM materiel))"
        )
    )

    liaisons = parse_exercice_materiel(EXERCICE_MATERIEL_FILE)
    if liaisons:
        session.execute(
            text(
                """
                INSERT INTO exercice_materiel (id_exercice, id_materiel)
                VALUES (:id_exercice, :id_materiel)
                ON CONFLICT DO NOTHING
                """
            ),
            [{"id_exercice": a, "id_materiel": b} for a, b in liaisons],
        )
    return len(materiels), len(liaisons)


def import_restrictions(session) -> tuple[int, int]:
    if not RESTRICTIONS_FILE.is_file():
        raise FileNotFoundError(RESTRICTIONS_FILE)
    data = json.loads(RESTRICTIONS_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("restrictions_equivalences.json doit être un objet JSON")

    session.execute(text("TRUNCATE ref_restriction_alias, ref_restriction_equivalence RESTART IDENTITY CASCADE"))

    cles = 0
    alias_count = 0
    for key, values in data.items():
        cle = str(key).strip().lower()
        if not cle:
            continue
        session.execute(
            text("INSERT INTO ref_restriction_equivalence (cle_canonique) VALUES (:cle) ON CONFLICT DO NOTHING"),
            {"cle": cle},
        )
        cles += 1
        aliases = [cle]
        if isinstance(values, list):
            aliases.extend(str(v).strip().lower() for v in values if str(v).strip())
        seen: set[str] = set()
        batch = []
        for a in aliases:
            if a and a not in seen:
                seen.add(a)
                batch.append({"cle": cle, "alias": a})
        if batch:
            session.execute(
                text(
                    """
                    INSERT INTO ref_restriction_alias (cle_canonique, alias)
                    VALUES (:cle, :alias)
                    ON CONFLICT (cle_canonique, alias) DO NOTHING
                    """
                ),
                batch,
            )
            alias_count += len(batch)
    return cles, alias_count


def import_ingredients(session) -> int:
    if not INGREDIENTS_FILE.is_file():
        raise FileNotFoundError(INGREDIENTS_FILE)

    session.execute(text("TRUNCATE ref_ingredient"))
    total = 0
    batch: list[dict] = []

    with INGREDIENTS_FILE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            ext_id = item.get("id")
            nom = item.get("nom")
            budget = item.get("budget")
            if not ext_id or not nom or budget is None:
                continue
            try:
                budget_i = int(budget)
            except (TypeError, ValueError):
                continue
            if budget_i < 1 or budget_i > 3:
                continue
            batch.append(
                {
                    "id_externe": str(ext_id),
                    "nom": str(nom),
                    "calories": item.get("calories"),
                    "proteines": item.get("proteines"),
                    "lipides": item.get("lipides"),
                    "glucides": item.get("glucides"),
                    "budget": budget_i,
                }
            )
            if len(batch) >= BATCH_SIZE:
                session.execute(
                    text(
                        """
                        INSERT INTO ref_ingredient (
                            id_externe, nom, calories, proteines, lipides, glucides, budget
                        ) VALUES (
                            :id_externe, :nom, :calories, :proteines, :lipides, :glucides, :budget
                        )
                        ON CONFLICT (id_externe) DO UPDATE SET
                            nom = EXCLUDED.nom,
                            calories = EXCLUDED.calories,
                            proteines = EXCLUDED.proteines,
                            lipides = EXCLUDED.lipides,
                            glucides = EXCLUDED.glucides,
                            budget = EXCLUDED.budget
                        """
                    ),
                    batch,
                )
                total += len(batch)
                batch.clear()
                if total % 20000 == 0:
                    session.commit()
                    print(f"  … {total} ingrédients importés", flush=True)

    if batch:
        session.execute(
            text(
                """
                INSERT INTO ref_ingredient (
                    id_externe, nom, calories, proteines, lipides, glucides, budget
                ) VALUES (
                    :id_externe, :nom, :calories, :proteines, :lipides, :glucides, :budget
                )
                ON CONFLICT (id_externe) DO UPDATE SET
                    nom = EXCLUDED.nom,
                    calories = EXCLUDED.calories,
                    proteines = EXCLUDED.proteines,
                    lipides = EXCLUDED.lipides,
                    glucides = EXCLUDED.glucides,
                    budget = EXCLUDED.budget
                """
            ),
            batch,
        )
        total += len(batch)

    deleted = session.execute(text(SQL_DELETE_INGREDIENTS_JUNK)).rowcount or 0
    if deleted:
        print(f"  … {deleted} lignes « by … » supprimées (SQL)", flush=True)

    return total


def main() -> None:
    print("Import référentiels IA -> postgres-sante (sante_db)")
    with SessionSante() as session:
        print("1/4 Exercices (ref_exercice)…")
        n_ex = import_exercices(session)
        session.commit()
        print(f"    {n_ex} exercices")

        print("2/4 Matériel (materiels.txt + exercice_materiel.txt)…")
        n_mat, n_lia = import_materiels(session)
        session.commit()
        print(f"    {n_mat} matériels, {n_lia} liaisons")

        print("3/4 Équivalences restrictions…")
        n_cle, n_alias = import_restrictions(session)
        session.commit()
        print(f"    {n_cle} clés, {n_alias} alias")

        print("4/4 Ingrédients (ref_ingredient)…")
        n_ing = import_ingredients(session)
        session.commit()
        print(f"    {n_ing} ingrédients")

    print("Terminé.")


if __name__ == "__main__":
    main()
