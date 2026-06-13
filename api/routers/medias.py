from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from api.db.postgres_utilisateur import get_session_utilisateur
from api.schemas.auth import CurrentUser
from api.schemas.social import MediaUploadResponse
from api.services.minio_storage import upload_media

router = APIRouter(prefix="/medias", tags=["Médias"])


@router.post("/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_fichier(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    fichier: UploadFile = File(...),
):
    """Téléverse une image ou une vidéo vers MinIO et retourne l'URL publique."""
    content_type = fichier.content_type or "application/octet-stream"
    content = await fichier.read()
    url = upload_media(content, content_type)
    return MediaUploadResponse(url=url)
