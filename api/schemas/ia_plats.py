"""Corps de requête aligné sur `valider_requete` dans Ia_recom_mistral_plat_distant.py."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

MealType = Literal["dejeuner", "diner", "souper"]


class IaPlatsRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "objectif_alimentaire": "perte_de_poids",
                "repas_par_jour": 2,
                "repas_types": ["dejeuner", "souper"],
                "budget": 2,
                "restrictions": ["arachides", "porc"],
            }
        }
    )

    objectif_alimentaire: Literal["perte_de_poids", "prise_de_masse"] = Field(
        ...,
        description="Objectif nutritionnel",
    )
    repas_par_jour: int = Field(..., ge=1, le=3, description="Nombre de repas (1 à 3)")
    budget: int | str | None = Field(
        default=None,
        description="1=économique, 2=standard, 3=premium (ou libellé). Défaut : standard",
    )
    restrictions: list[str] = Field(
        default_factory=list,
        description="Restrictions alimentaires (liste, peut être vide)",
    )
    repas_types: list[MealType] | None = Field(
        default=None,
        description="Types de repas — même longueur que repas_par_jour si fourni ; sinon ordre par défaut du moteur",
    )

    @model_validator(mode="after")
    def repas_types_match_count(self):
        if self.repas_types is not None and len(self.repas_types) != self.repas_par_jour:
            raise ValueError("repas_types doit avoir la même longueur que repas_par_jour")
        return self

    def to_engine_dict(self) -> dict:
        out: dict = {
            "objectif_alimentaire": self.objectif_alimentaire,
            "repas_par_jour": self.repas_par_jour,
            "restrictions": self.restrictions,
        }
        if self.budget is not None:
            out["budget"] = self.budget
        if self.repas_types is not None:
            out["repas_types"] = self.repas_types
        return out
