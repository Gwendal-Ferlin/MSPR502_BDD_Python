"""Chiffrement symétrique des champs sensibles (Fernet) — clé DATA_ENCRYPTION_KEY dans .env."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from api.config import settings

_fernet: Fernet | None = None


def _fernet_instance() -> Fernet | None:
    global _fernet
    key = (getattr(settings, "data_encryption_key", None) or "").strip()
    if not key:
        return None
    if _fernet is None:
        _fernet = Fernet(key.encode("utf-8"))
    return _fernet


def encryption_enabled() -> bool:
    return _fernet_instance() is not None


def email_hmac(email_normalized: str) -> str:
    """Index de recherche pour l'email (connexion / unicité) sans stocker l'email en clair."""
    key = (getattr(settings, "data_encryption_key", None) or "").strip().encode("utf-8")
    if not key:
        raise RuntimeError("DATA_ENCRYPTION_KEY requis pour calculer email_hmac")
    return hmac.new(key, email_normalized.encode("utf-8"), hashlib.sha256).hexdigest()


def encrypt_str(plain: str | None) -> str | None:
    if plain is None:
        return None
    f = _fernet_instance()
    if not f:
        return plain
    return f.encrypt(plain.encode("utf-8")).decode("ascii")


def decrypt_str(stored: str | None) -> str | None:
    if stored is None:
        return None
    if isinstance(stored, (int, float)):
        stored = str(stored)
    f = _fernet_instance()
    if not f:
        return str(stored)
    try:
        return f.decrypt(str(stored).encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError):
        return str(stored)


def encrypt_int(value: int | None) -> str | None:
    if value is None:
        return None
    return encrypt_str(str(value))


def decrypt_int(stored: Any) -> int | None:
    if stored is None:
        return None
    s = decrypt_str(str(stored)) if stored is not None else None
    if s is None or s == "":
        return None
    try:
        return int(s)
    except ValueError:
        return None


def encrypt_float(value: float | None) -> str | None:
    if value is None:
        return None
    return encrypt_str(str(value))


def decrypt_float(stored: Any) -> float | None:
    if stored is None:
        return None
    s = decrypt_str(str(stored)) if stored is not None else None
    if s is None or s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def decrypt_compte_row(row: dict) -> dict:
    d = dict(row)
    if "email" in d:
        d["email"] = decrypt_str(d["email"])
    return d


def persist_compte_email_password(email_plain: str, password_bcrypt: str) -> tuple[str, str | None, str]:
    """Retourne (email_db, email_hmac_ou_none, password_db)."""
    e = email_plain.strip().lower()
    if encryption_enabled():
        return encrypt_str(e), email_hmac(e), encrypt_str(password_bcrypt)
    return e, None, password_bcrypt


def persist_email_only(email_plain: str) -> tuple[str, str | None]:
    e = email_plain.strip().lower()
    if encryption_enabled():
        return encrypt_str(e), email_hmac(e)
    return e, None


def persist_password_only(password_bcrypt: str) -> str:
    if encryption_enabled():
        return encrypt_str(password_bcrypt) or password_bcrypt
    return password_bcrypt


def sql_email_match_clause() -> str:
    """Clause WHERE pour trouver un compte par email (chiffré ou legacy)."""
    if encryption_enabled():
        return "(email_hmac = :email_hmac OR (email_hmac IS NULL AND lower(trim(email)) = :email_plain))"
    return "lower(trim(email)) = :email_plain"


def params_for_email_lookup(email_plain: str) -> dict[str, Any]:
    e = email_plain.strip().lower()
    if encryption_enabled():
        return {"email_hmac": email_hmac(e), "email_plain": e}
    return {"email_plain": e}


def decrypt_restriction_row(row: dict) -> dict:
    d = dict(row)
    if "nom" in d:
        d["nom"] = decrypt_str(d["nom"])
    if "type" in d and d["type"] is not None:
        d["type"] = decrypt_str(d["type"])
    return d


def decrypt_profil_row(row: dict) -> dict:
    d = dict(row)
    d["annee_naissance"] = decrypt_int(d.get("annee_naissance"))
    d["sexe"] = decrypt_str(d["sexe"]) if d.get("sexe") is not None else None
    d["taille_cm"] = decrypt_int(d.get("taille_cm"))
    if d.get("niveau_activite") is not None:
        d["niveau_activite"] = decrypt_str(d["niveau_activite"])
    return d


def encrypt_profil_params(params: dict) -> dict:
    out = dict(params)
    if "annee_naissance" in out and out["annee_naissance"] is not None:
        out["annee_naissance"] = encrypt_int(out["annee_naissance"])
    if "sexe" in out and out["sexe"] is not None:
        out["sexe"] = encrypt_str(out["sexe"])
    if "taille_cm" in out and out["taille_cm"] is not None:
        out["taille_cm"] = encrypt_int(out["taille_cm"])
    if "niveau_activite" in out and out["niveau_activite"] is not None:
        out["niveau_activite"] = encrypt_str(out["niveau_activite"])
    return out


def decrypt_biometrie_row(row: dict) -> dict:
    d = dict(row)
    d["poids_kg"] = decrypt_float(d.get("poids_kg"))
    d["score_sommeil"] = decrypt_int(d.get("score_sommeil"))
    return d


def encrypt_biometrie_write(poids_kg: float | None, score_sommeil: int | None) -> tuple[str | None, str | None]:
    return encrypt_float(poids_kg), encrypt_int(score_sommeil)
