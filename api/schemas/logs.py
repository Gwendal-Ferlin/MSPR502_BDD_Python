from datetime import datetime
from pydantic import BaseModel
from typing import Any


class EvenementCreate(BaseModel):
    id_anonyme: str
    action: str
    details_techniques: dict[str, Any] | None = None


class EvenementRead(BaseModel):
    id_log: str | None
    timestamp: datetime
    id_anonyme: str
    action: str
    details_techniques: dict[str, Any] | None = None


class ConfigRead(BaseModel):
    cle: str
    valeur: Any
    description: str | None = None
