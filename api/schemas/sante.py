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


class ProfilSanteUpdate(BaseModel):
    annee_naissance: int | None = None
    sexe: str | None = None
    taille_cm: int | None = None


class ObjectifRead(BaseModel):
    id_objectif_u: int
    id_anonyme: UUID
    type_objectif: str | None
    valeur_cible: float | None
    date_debut: datetime | None
    statut: str | None

    model_config = {"from_attributes": True}


class ObjectifUpdate(BaseModel):
    type_objectif: str | None = None
    valeur_cible: float | None = None
    date_debut: datetime | None = None
    statut: str | None = None


class SuiviBiometriqueRead(BaseModel):
    id_biometrie: int
    id_anonyme: UUID
    date_releve: datetime
    poids_kg: float | None
    score_sommeil: int | None

    model_config = {"from_attributes": True}


class SuiviBiometriqueUpdate(BaseModel):
    date_releve: datetime | None = None
    poids_kg: float | None = None
    score_sommeil: int | None = None


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


class JournalCreate(BaseModel):
    horodatage: datetime
    nom_repas: str | None = None
    type_repas: str | None = None
    total_calories: float | None = None
    total_proteines: float | None = None
    total_glucides: float | None = None
    total_lipides: float | None = None


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


class MesRestrictionsUpdate(BaseModel):
    """Liste des id_restriction à associer à l'utilisateur (remplace les restrictions actuelles)."""
    id_restrictions: list[int]


class ReferentielRead(BaseModel):
    id: int
    nom: str
    type: str | None = None
    muscle_principal: str | None = None
