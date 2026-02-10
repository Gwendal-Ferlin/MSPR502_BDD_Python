from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ProfilSanteRead(BaseModel):
    id_profil: int
    id_anonyme: UUID
    annee_naissance: int | None
    sexe: str | None
    taille_cm: int | None

    model_config = {"from_attributes": True}


class ObjectifRead(BaseModel):
    id_objectif_u: int
    id_anonyme: UUID
    type_objectif: str | None
    valeur_cible: float | None
    date_debut: datetime | None
    statut: str | None

    model_config = {"from_attributes": True}


class JournalRead(BaseModel):
    id_repas: int
    id_anonyme: UUID
    horodatage: datetime
    nom_repas: str | None
    type_repas: str | None
    total_calories: float | None
    total_proteines: float | None
    total_glucides: float | None
    total_lipides: float | None

    model_config = {"from_attributes": True}


class SeanceRead(BaseModel):
    id_seance: int
    id_anonyme: UUID
    horodatage: datetime
    nom_seance: str | None
    ressenti_effort_rpe: int | None

    model_config = {"from_attributes": True}


class RestrictionRead(BaseModel):
    id: int
    nom: str
    type: str | None = None


class ReferentielRead(BaseModel):
    id: int
    nom: str
    type: str | None = None
    muscle_principal: str | None = None
