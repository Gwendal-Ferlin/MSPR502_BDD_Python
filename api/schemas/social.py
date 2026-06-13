from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AuteurPublicRead(BaseModel):
    id_anonyme: UUID
    nom_affichage: str | None = None
    photo_profil_url: str | None = None


class ProfilPublicRead(BaseModel):
    id_anonyme: UUID
    nom_affichage: str | None = None
    photo_profil_url: str | None = None


class PublicationCreate(BaseModel):
    texte: str = Field(..., min_length=1, max_length=5000)
    media_url: str | None = None


class PublicationRead(BaseModel):
    id_publication: UUID
    auteur: AuteurPublicRead
    texte: str
    media_url: str | None = None
    media_type: Literal["image", "video"] | None = None
    date_creation: datetime
    nb_likes: int
    est_like_par_moi: bool
    nb_commentaires: int


class CommentaireCreate(BaseModel):
    texte: str = Field(..., min_length=1, max_length=2000)


class CommentaireRead(BaseModel):
    id_commentaire: UUID
    auteur: AuteurPublicRead
    texte: str
    date_creation: datetime


class MediaUploadResponse(BaseModel):
    url: str
