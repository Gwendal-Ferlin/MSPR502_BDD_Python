from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel


class CompteUtilisateurRead(BaseModel):
    id_user: int
    email: str
    role: str
    type_abonnement: str
    date_consentement_rgpd: datetime | None
    est_supprime: bool = False
    date_fin_periode_payee: datetime | None = None
    desabonnement_a_fin_periode: bool = False

    model_config = {"from_attributes": True}


class SouscrireAbonnement(BaseModel):
    """Body pour souscrire à Premium ou Premium+ (mock paiement)."""
    type_abonnement: Literal["Premium", "Premium+"]


class CompteUtilisateurCreate(BaseModel):
    email: str
    password: str
    date_consentement_rgpd: datetime | None = None


class CompteUtilisateurUpdate(BaseModel):
    """Champs modifiables par l'utilisateur sur son propre compte (email, mot de passe)."""
    email: str | None = None
    password: str | None = None


class VaultRead(BaseModel):
    id_anonyme: UUID
    id_user: int
    date_derniere_activite: datetime | None
    consentement_sante_actif: bool | None

    model_config = {"from_attributes": True}
