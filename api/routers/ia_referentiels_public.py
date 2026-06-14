"""Référentiels IA (exercices, ingrédients, équivalences restrictions) — accès public."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.db.postgres_sante import get_session_sante
from api.schemas.ia_referentiels import (
    ExerciceCatalogueRead,
    ExerciceMaterielLiaisonRead,
    IngredientListResponse,
    IngredientRead,
    MaterielCatalogueRead,
    RestrictionEquivalenceListResponse,
    RestrictionEquivalenceRead,
)

router = APIRouter(prefix="/sante/referentiels/ia", tags=["Santé - Référentiels IA"])


@router.get("/exercices", response_model=list[ExerciceCatalogueRead])
def list_exercices_catalogue(
    db: Session = Depends(get_session_sante),
    niveau: str | None = Query(
        None, description="Filtrer par niveau : facile, normal, intensif"
    ),
):
    """Catalogue exercices IA (`exercices.txt` → `ref_exercice`). Public, sans authentification."""
    sql = """
        SELECT id_exercice, nom, muscle_principal, niveau
        FROM ref_exercice
        WHERE niveau IS NOT NULL
    """
    params: dict = {}
    if niveau:
        sql += " AND lower(niveau) = lower(:niveau)"
        params["niveau"] = niveau.strip()
    sql += " ORDER BY id_exercice"
    rows = db.execute(text(sql), params).fetchall()
    return [ExerciceCatalogueRead.model_validate(dict(r._mapping)) for r in rows]


@router.get("/materiel", response_model=list[MaterielCatalogueRead])
def list_materiel_catalogue(
    db: Session = Depends(get_session_sante),
):
    """Catalogue matériel IA (`materiels.txt` → `materiel`). Public, sans authentification."""
    rows = db.execute(
        text("SELECT id_materiel, nom FROM materiel ORDER BY id_materiel")
    ).fetchall()
    return [MaterielCatalogueRead.model_validate(dict(r._mapping)) for r in rows]


@router.get("/exercice-materiel", response_model=list[ExerciceMaterielLiaisonRead])
def list_exercice_materiel_liaisons(
    db: Session = Depends(get_session_sante),
    id_exercice: int | None = Query(None, description="Filtrer par id_exercice"),
    id_materiel: int | None = Query(None, description="Filtrer par id_materiel"),
):
    """Liaisons exercice ↔ matériel IA (`exercice_materiel.txt` → `exercice_materiel`). Public."""
    sql = "SELECT id_exercice, id_materiel FROM exercice_materiel WHERE 1=1"
    params: dict = {}
    if id_exercice is not None:
        sql += " AND id_exercice = :id_exercice"
        params["id_exercice"] = id_exercice
    if id_materiel is not None:
        sql += " AND id_materiel = :id_materiel"
        params["id_materiel"] = id_materiel
    sql += " ORDER BY id_exercice, id_materiel"
    rows = db.execute(text(sql), params).fetchall()
    return [ExerciceMaterielLiaisonRead.model_validate(dict(r._mapping)) for r in rows]


@router.get("/ingredients", response_model=IngredientListResponse)
@router.get("/plats", response_model=IngredientListResponse, include_in_schema=True)
def list_ingredients_catalogue(
    db: Session = Depends(get_session_sante),
    budget_max: int | None = Query(
        None,
        ge=1,
        le=3,
        description="Ingrédients avec budget <= cette valeur (1=économique … 3=premium)",
    ),
    q: str | None = Query(
        None, description="Recherche partielle sur le nom (insensible à la casse)"
    ),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Catalogue ingrédients IA (`final_ingredients_list.json` → `ref_ingredient`). Public, paginé."""
    where = ["1=1"]
    params: dict = {"limit": limit, "offset": offset}
    if budget_max is not None:
        where.append("budget <= :budget_max")
        params["budget_max"] = budget_max
    if q and q.strip():
        where.append("lower(nom) LIKE lower(:q)")
        params["q"] = f"%{q.strip()}%"

    where_sql = " AND ".join(where)
    total_row = db.execute(
        text(f"SELECT COUNT(*) AS n FROM ref_ingredient WHERE {where_sql}"),
        {k: v for k, v in params.items() if k not in ("limit", "offset")},
    ).fetchone()
    total = int(total_row._mapping["n"]) if total_row else 0

    rows = db.execute(
        text(
            f"""
            SELECT id_externe, nom, calories, proteines, lipides, glucides, budget
            FROM ref_ingredient
            WHERE {where_sql}
            ORDER BY nom
            LIMIT :limit OFFSET :offset
            """
        ),
        params,
    ).fetchall()

    return IngredientListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[IngredientRead.model_validate(dict(r._mapping)) for r in rows],
    )


@router.get(
    "/restrictions-equivalences", response_model=RestrictionEquivalenceListResponse
)
def list_restrictions_equivalences(
    db: Session = Depends(get_session_sante),
):
    """Équivalences FR/EN pour l’IA plats (`restrictions_equivalences.json` → tables dédiées). Public."""
    cles = db.execute(
        text(
            "SELECT cle_canonique FROM ref_restriction_equivalence ORDER BY cle_canonique"
        )
    ).fetchall()
    items: list[RestrictionEquivalenceRead] = []
    for row in cles:
        cle = row._mapping["cle_canonique"]
        aliases = db.execute(
            text(
                """
                SELECT alias FROM ref_restriction_alias
                WHERE cle_canonique = :cle
                ORDER BY id_alias
                """
            ),
            {"cle": cle},
        ).fetchall()
        items.append(
            RestrictionEquivalenceRead(
                cle_canonique=cle,
                aliases=[a._mapping["alias"] for a in aliases],
            )
        )
    return RestrictionEquivalenceListResponse(items=items)
