from pydantic import BaseModel, Field


class ExerciceCatalogueRead(BaseModel):
    id_exercice: int
    nom: str
    muscle_principal: str | None = None
    niveau: str | None = None

    model_config = {"from_attributes": True}


class MaterielCatalogueRead(BaseModel):
    id_materiel: int
    nom: str

    model_config = {"from_attributes": True}


class ExerciceMaterielLiaisonRead(BaseModel):
    id_exercice: int
    id_materiel: int

    model_config = {"from_attributes": True}


class IngredientRead(BaseModel):
    id_externe: str
    nom: str
    calories: float | None = None
    proteines: float | None = None
    lipides: float | None = None
    glucides: float | None = None
    budget: int = Field(ge=1, le=3)


class IngredientListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[IngredientRead]


class RestrictionEquivalenceRead(BaseModel):
    cle_canonique: str
    aliases: list[str]


class RestrictionEquivalenceListResponse(BaseModel):
    items: list[RestrictionEquivalenceRead]
