from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import uuid
from pymongo.database import Database

from api.schemas.auth import CurrentUser


def log_admin_consultation_tiers(
    db_logs: Database,
    current_user: CurrentUser,
    endpoint: str,
    *,
    id_anonyme_cible: str | None = None,
    id_user_cible: int | None = None,
    details_extra: dict[str, Any] | None = None,
) -> None:
    """Enregistre en base (logs) quand un Admin/Super-Admin consulte des données qui ne sont pas les siennes."""
    if current_user.role not in ("Admin", "Super-Admin"):
        return
    if id_anonyme_cible is not None and id_anonyme_cible == current_user.id_anonyme:
        return
    if id_user_cible is not None and id_user_cible == current_user.id_user:
        return

    details = {
        "endpoint": endpoint,
        "role_acteur": current_user.role,
        "id_user_acteur": current_user.id_user,
    }
    if id_anonyme_cible is not None:
        details["id_anonyme_cible"] = id_anonyme_cible
    if id_user_cible is not None:
        details["id_user_cible"] = id_user_cible
    if details_extra:
        details.update(details_extra)

    coll = db_logs["evenements"]
    coll.insert_one({
        "id_log": f"log-{uuid.uuid4().hex[:12]}",
        "timestamp": datetime.now(ZoneInfo("Europe/Paris")),
        "id_anonyme": current_user.id_anonyme,
        "action": "consultation_donnees_tiers",
        "details_techniques": details,
    })
