from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database
from bson import ObjectId

from api.auth.dependencies import get_current_user
from api.db.mongo_reco import get_mongo_reco
from api.db.mongo_logs import get_mongo_logs
from api.schemas.auth import CurrentUser
from api.schemas.reco import RecommendationRead, RepasCreate, RepasRead
from api.services.log_admin import log_admin_consultation_tiers

router = APIRouter(prefix="/reco", tags=["Recommandations"])


@router.get("/recommendations", response_model=list[RecommendationRead])
def list_recommendations(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    id_anonyme: str | None = Query(None),
    type_reco: str | None = Query(None, alias="type"),
    db: Database = Depends(get_mongo_reco),
    db_logs: Database = Depends(get_mongo_logs),
):
    coll = db["recommendations"]
    q = {}
    if current_user.role in ("Admin", "Super-Admin"):
        if id_anonyme:
            q["id_anonyme"] = id_anonyme
            log_admin_consultation_tiers(
                db_logs, current_user, "GET /api/reco/recommendations", id_anonyme_cible=id_anonyme
            )
    else:
        q["id_anonyme"] = current_user.id_anonyme
    if type_reco:
        q["type"] = type_reco
    cursor = coll.find(q).sort("created_at", -1).limit(50)
    out = []
    for doc in cursor:
        doc["id_anonyme"] = str(doc.get("id_anonyme", ""))
        out.append(RecommendationRead.model_validate(doc))
    return out


def _repas_doc_to_read(doc: dict) -> RepasRead:
    """Convertit un document MongoDB repas en RepasRead."""
    return RepasRead(
        id=str(doc["_id"]),
        id_anonyme=str(doc.get("id_anonyme", "")),
        nom_repas=doc.get("nom_repas", ""),
        aliments=doc.get("aliments", {}),
        total_calories=doc.get("total_calories"),
        lipides=doc.get("lipides"),
        glucides=doc.get("glucides"),
        proteines=doc.get("proteines"),
        created_at=doc.get("created_at"),
    )


@router.get("/repas", response_model=list[RepasRead])
def list_repas(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    id_anonyme: str | None = Query(None),
    db: Database = Depends(get_mongo_reco),
    db_logs: Database = Depends(get_mongo_logs),
):
    """Liste les repas (recettes) de l'utilisateur. Client : les siens ; Admin : avec id_anonyme optionnel."""
    coll = db["repas"]
    q = {}
    if current_user.role in ("Admin", "Super-Admin"):
        if id_anonyme:
            q["id_anonyme"] = id_anonyme
            log_admin_consultation_tiers(
                db_logs, current_user, "GET /api/reco/repas", id_anonyme_cible=id_anonyme
            )
    else:
        q["id_anonyme"] = current_user.id_anonyme
    cursor = coll.find(q).sort("created_at", -1).limit(100)
    return [_repas_doc_to_read(doc) for doc in cursor]


@router.get("/repas/{repas_id}", response_model=RepasRead)
def get_repas(
    repas_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Database = Depends(get_mongo_reco),
):
    """Récupère un repas par son id. Le repas doit appartenir à l'utilisateur connecté (ou Admin/Super-Admin)."""
    try:
        oid = ObjectId(repas_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repas non trouvé")
    coll = db["repas"]
    doc = coll.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repas non trouvé")
    if current_user.role not in ("Admin", "Super-Admin") and doc.get("id_anonyme") != current_user.id_anonyme:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Droits insuffisants")
    return _repas_doc_to_read(doc)


@router.post("/repas", response_model=RepasRead, status_code=status.HTTP_201_CREATED)
def create_repas(
    body: RepasCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Database = Depends(get_mongo_reco),
):
    """Crée un repas (recette) pour l'utilisateur connecté. Lié à son id_anonyme."""
    coll = db["repas"]
    now = datetime.now(timezone.utc)
    doc = {
        "id_anonyme": current_user.id_anonyme,
        "nom_repas": body.nom_repas,
        "aliments": body.aliments,
        "total_calories": body.total_calories,
        "lipides": body.lipides,
        "glucides": body.glucides,
        "proteines": body.proteines,
        "created_at": now,
    }
    result = coll.insert_one(doc)
    doc["_id"] = result.inserted_id
    doc["id"] = str(result.inserted_id)
    doc["id_anonyme"] = str(doc["id_anonyme"])
    doc["created_at"] = now
    return _repas_doc_to_read(doc)
