from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    success: bool = True
    message: str | None = None
    error: str | None = None
    data: Any | None = None


class BuyAnimalRequest(BaseModel):
    animal_id: str
    price: int = Field(ge=0)


class BuyChromaRequest(BaseModel):
    animal_id: str
    chroma_id: str
    price: int = Field(ge=0)


class SetActiveChromaRequest(BaseModel):
    animal_id: str
    chroma_id: str


class ToggleVisibilityRequest(BaseModel):
    animal_id: str
    is_visible: bool


class AddCoinsRequest(BaseModel):
    user_id: UUID
    amount: int = Field(gt=0)
    reason: str | None = None
    metadata: dict[str, Any] | None = None

