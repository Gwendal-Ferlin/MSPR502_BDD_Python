from datetime import datetime, timezone
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from api.auth.dependencies import get_current_user
from api.db.mongo_logs import get_mongo_logs
from api.schemas.auth import CurrentUser
from api.schemas.logs import EvenementCreate, EvenementRead, ConfigRead
from api.services.log_admin import log_admin_consultation_tiers

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/evenements", response_model=list[EvenementRead])
def list_evenements(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    id_anonyme: str | None = Query(None),
    action: str | None = Query(None),
    db: Database = Depends(get_mongo_logs),
):
    coll = db["evenements"]
    q = {}
    if current_user.role in ("Admin", "Super-Admin"):
        if id_anonyme:
            q["id_anonyme"] = id_anonyme
            log_admin_consultation_tiers(
                db, current_user, "GET /api/logs/evenements", id_anonyme_cible=id_anonyme
            )
    else:
        q["id_anonyme"] = current_user.id_anonyme
    if action:
        q["action"] = action
    cursor = coll.find(q).sort("timestamp", -1).limit(100)
    out = []
    for doc in cursor:
        doc["id_log"] = doc.get("id_log") or str(doc.get("_id", ""))
        if not doc.get("timestamp") and hasattr(doc.get("_id"), "generation_time"):
            doc["timestamp"] = doc["_id"].generation_time
        if "id_anonyme" in doc and not isinstance(doc["id_anonyme"], str):
            doc["id_anonyme"] = str(doc["id_anonyme"])
        out.append(EvenementRead.model_validate(doc))
    return out


@router.post("/evenements", status_code=201)
def create_evenement(
    body: EvenementCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Database = Depends(get_mongo_logs),
):
    coll = db["evenements"]
    id_anonyme = body.id_anonyme
    if current_user.role not in ("Admin", "Super-Admin"):
        id_anonyme = current_user.id_anonyme
    doc = {
        "id_log": f"log-{uuid.uuid4().hex[:12]}",
        "timestamp": datetime.now(timezone.utc),
        "id_anonyme": id_anonyme,
        "action": body.action,
        "details_techniques": body.details_techniques or {},
    }
    coll.insert_one(doc)
    return {"id_log": doc["id_log"], "message": "Événement enregistré"}


@router.get("/config", response_model=list[ConfigRead])
def list_config(db: Database = Depends(get_mongo_logs)):
    coll = db["config"]
    out = []
    for doc in coll.find():
        out.append(ConfigRead(cle=doc.get("cle", ""), valeur=doc.get("valeur"), description=doc.get("description")))
    return out


@router.get("/config/{cle}")
def get_config(cle: str, db: Database = Depends(get_mongo_logs)):
    doc = db["config"].find_one({"cle": cle})
    if not doc:
        return None
    return {"cle": doc["cle"], "valeur": doc.get("valeur"), "description": doc.get("description")}
