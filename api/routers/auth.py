import logging
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
import bcrypt
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.config import settings
from api.db.postgres_utilisateur import get_session_utilisateur
from api.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

_log = logging.getLogger(__name__)


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    db: Session = Depends(get_session_utilisateur),
):
    try:
        row = db.execute(
            text(
                "SELECT id_user, email, password, role FROM compte_utilisateur WHERE email = :email AND COALESCE(est_supprime, false) = false"
            ),
            {"email": body.email.strip().lower()},
        ).fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
            )
        user = dict(row._mapping)
        stored_hash = user["password"]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")
        try:
            if not bcrypt.checkpw(body.password.encode("utf-8"), stored_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email ou mot de passe incorrect",
                )
        except (ValueError, TypeError):
            # Hash en base invalide (ex. ancien placeholder)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
            )
        vault = db.execute(
            text(
                "SELECT id_anonyme FROM vault_correspondance WHERE id_user = :id_user"
            ),
            {"id_user": user["id_user"]},
        ).fetchone()
        if not vault:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Vault manquant pour cet utilisateur",
            )
        id_anonyme = str(vault._mapping["id_anonyme"])
        expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
        # python-jose exige un NumericDate (secondes UTC), pas un datetime — sinon erreur 500 à l'encodage.
        payload = {
            "sub": str(user["id_user"]),
            "id_user": user["id_user"],
            "email": user["email"],
            "role": user["role"],
            "id_anonyme": id_anonyme,
            "exp": int(expire_at.timestamp()),
        }
        access_token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_expire_minutes * 60,
        )
    except HTTPException:
        raise
    except SQLAlchemyError:
        _log.exception("Login : erreur SQL base utilisateur (connexion, schéma ou table manquante)")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Base utilisateur indisponible. En pré-prod / TrueNAS : exécuter les scripts "
                "init/postgres-utilisateur (01_schema.sql puis 02_seed.sql) sur postgres-utilisateur(-preprod), "
                "et vérifier que POSTGRES_UTILISATEUR_* dans l'API correspond au conteneur Postgres."
            ),
        ) from None
