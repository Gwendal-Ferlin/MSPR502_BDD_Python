from datetime import datetime
from pydantic import BaseModel


class RecommendationRead(BaseModel):
    id_anonyme: str
    type: str
    titre: str | None = None
    contenu: str | None = None
    created_at: datetime | None = None
    score: float | None = None
