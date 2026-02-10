from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from api.config import settings
from api.schemas.auth import CurrentUser

# HTTPBearer exige le header Authorization: Bearer <token> sur chaque requête
security = HTTPBearer(auto_error=True)

oauth2_scheme = security  # alias pour compatibilité


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> CurrentUser:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        id_user: int = payload.get("id_user")
        email: str = payload.get("email")
        role: str = payload.get("role")
        id_anonyme: str = payload.get("id_anonyme")
        if id_user is None or email is None or role is None or id_anonyme is None:
            raise credentials_exception
        return CurrentUser(
            id_user=id_user,
            email=email,
            role=role,
            id_anonyme=id_anonyme,
        )
    except JWTError:
        raise credentials_exception


def require_roles(
    allowed_roles: list[str],
) -> callable:
    def _check(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Droits insuffisants",
            )
        return current_user

    return _check
