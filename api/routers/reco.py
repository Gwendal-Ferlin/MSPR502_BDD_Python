from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from api.auth.dependencies import get_current_user
from api.db.mongo_reco import get_mongo_reco
from api.db.mongo_logs import get_mongo_logs
from api.schemas.auth import CurrentUser
from api.schemas.reco import RecommendationRead
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
