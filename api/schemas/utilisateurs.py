from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class CompteUtilisateurRead(BaseModel):
    id_user: int
    email: str
    role: str
    type_abonnement: str
    date_consentement_rgpd: datetime | None

    model_config = {"from_attributes": True}


class VaultRead(BaseModel):
    id_anonyme: UUID
    id_user: int
    date_derniere_activite: datetime | None
    consentement_sante_actif: bool | None

    model_config = {"from_attributes": True}
