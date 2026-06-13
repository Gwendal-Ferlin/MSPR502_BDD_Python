import uuid
from io import BytesIO

from fastapi import HTTPException, status
from minio import Minio
from minio.error import S3Error

from api.config import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}
ALLOWED_CONTENT_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES

EXTENSION_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/webm": ".webm",
}

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 Mo

_client: Minio | None = None
_bucket_ready = False


def _get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
    return _client


def _ensure_bucket() -> None:
    global _bucket_ready
    if _bucket_ready:
        return
    client = _get_client()
    bucket = settings.minio_bucket
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        policy = (
            f'{{"Version":"2012-10-17","Statement":[{{"Effect":"Allow","Principal":{{"AWS":["*"]}},'
            f'"Action":["s3:GetObject"],"Resource":["arn:aws:s3:::{bucket}/*"]}}]}}'
        )
        client.set_bucket_policy(bucket, policy)
    except S3Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Stockage média indisponible : {exc}",
        ) from exc
    _bucket_ready = True


def upload_media(content: bytes, content_type: str) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type de fichier non autorisé (image ou vidéo uniquement)",
        )
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Fichier trop volumineux (max 50 Mo)",
        )

    _ensure_bucket()
    ext = EXTENSION_BY_CONTENT_TYPE[content_type]
    object_name = f"{uuid.uuid4()}{ext}"
    client = _get_client()
    try:
        client.put_object(
            settings.minio_bucket,
            object_name,
            BytesIO(content),
            length=len(content),
            content_type=content_type,
        )
    except S3Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Échec de l'upload : {exc}",
        ) from exc

    base = settings.minio_public_url.rstrip("/")
    return f"{base}/{settings.minio_bucket}/{object_name}"


def infer_media_type_from_url(url: str | None) -> str | None:
    if not url:
        return None
    ext = url.rsplit(".", 1)[-1].lower().split("?")[0]
    if ext in ("jpg", "jpeg", "png", "gif", "webp", "bmp"):
        return "image"
    if ext in ("mp4", "mov", "webm", "avi", "mkv"):
        return "video"
    return None
