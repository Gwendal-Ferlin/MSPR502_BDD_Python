"""Rate limiting (SlowAPI) — clé par IP, compatible reverse-proxy (X-Forwarded-For)."""

from __future__ import annotations

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.config import settings


def rate_limit_key(request: Request) -> str:
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return get_remote_address(request)


_default_limits = (
    [settings.rate_limit_default] if settings.rate_limit_enabled else []
)

limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=_default_limits,
)


def apply_login_rate_limit(handler):
    """Applique une limite stricte sur POST /login si RATE_LIMIT_ENABLED est vrai."""
    if not settings.rate_limit_enabled:
        return handler
    return limiter.limit(settings.rate_limit_login)(handler)
