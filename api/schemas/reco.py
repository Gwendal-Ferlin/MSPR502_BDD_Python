from datetime import datetime
from pydantic import BaseModel


class RecommendationRead(BaseModel):
    id_anonyme: str
    type: str
    titre: str | None = None
    contenu: str | None = None
    created_at: datetime | None = None
    score: float | None = None


# Repas (recette) — collection repas MongoDB reco
# aliments : clé = nom aliment, valeur = dosage avec unité (ex: "150 g", "2 unités")
class RepasCreate(BaseModel):
    nom_repas: str
    aliments: dict[str, str] = {}  # nom_aliment -> "quantité unité"
    total_calories: float | None = None
    lipides: float | None = None
    glucides: float | None = None
    proteines: float | None = None


class RepasRead(BaseModel):
    id: str
    id_anonyme: str
    nom_repas: str
    aliments: dict[str, str] = {}
    total_calories: float | None = None
    lipides: float | None = None
    glucides: float | None = None
    proteines: float | None = None
    created_at: datetime | None = None
