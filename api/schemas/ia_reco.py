"""Corps de requête aligné sur `valider_requete` dans Ia_recom_mistral_distant.py."""

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BiometrieIa(BaseModel):
    poids_kg: float = Field(..., description="Poids actuel en kg")


class IaRecommandationRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "niveau": "intensif",
                "objectif": "prise_de_masse",
                "date_debut": "2026-01-10T00:00:00",
                "date_fin": "2026-03-20T00:00:00",
                "valeur_cible": 125,
                "unite": "kg",
                "materiels": [
                    "Banc d'entraînement",
                    "Haltères",
                    "Barres",
                    "Rameur",
                    "Stepper",
                ],
                "biometrie": {"poids_kg": 115},
            }
        }
    )

    niveau: str = Field(
        ...,
        description="`facile`, `normal` ou `intensif`",
        examples=["intensif"],
    )
    objectif: str = Field(
        ...,
        description="`perte_de_poids` ou `prise_de_masse`",
        examples=["prise_de_masse"],
    )
    date_debut: str = Field(..., description="Date ISO 8601 (début de période)")
    date_fin: str = Field(..., description="Date ISO 8601 (fin de période)")
    valeur_cible: float = Field(..., description="Poids cible en kg (cohérent avec l'objectif)")
    unite: str = Field(default="kg", description="Doit être `kg`")
    materiels: list[str] = Field(
        ...,
        description="Noms de matériels (voir référentiels du script ia-reco)",
    )
    biometrie: BiometrieIa | None = Field(
        default=None,
        description="Poids actuel — **ou** `suivi_biometrique` (au moins l'un des deux)",
    )
    suivi_biometrique: BiometrieIa | None = Field(
        default=None,
        description="Synonyme de `biometrie` — **un seul** des deux suffit",
    )

    @model_validator(mode="after")
    def au_moins_une_biometrie(self):
        if self.biometrie is None and self.suivi_biometrique is None:
            raise ValueError("Fournir 'biometrie' ou 'suivi_biometrique' avec poids_kg")
        return self

    def to_engine_dict(self) -> dict:
        src = self.biometrie if self.biometrie is not None else self.suivi_biometrique
        assert src is not None
        return {
            "niveau": self.niveau,
            "objectif": self.objectif,
            "date_debut": self.date_debut,
            "date_fin": self.date_fin,
            "valeur_cible": self.valeur_cible,
            "unite": self.unite,
            "materiels": self.materiels,
            "biometrie": {"poids_kg": src.poids_kg},
        }
