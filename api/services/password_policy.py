"""Politique de mot de passe pour la création et le changement de mot de passe.

Alignée sur l’article 32 du RGPD (mesures techniques et organisationnelles appropriées)
et les recommandations de la CNIL sur l’authentification par mot de passe (longueur,
complexité, mots de passe trop courants), compte tenu du traitement de données
personnelles et de santé par l’application.
"""

from __future__ import annotations

import re
import string

# Données sensibles : exigence renforcée par rapport au strict minimum CNIL (souvent 8 caractères).
MIN_LENGTH = 12
MAX_LENGTH = 128

_SPECIAL = set(string.punctuation)

# Mots / motifs trop prévisibles (non exhaustif ; compléter côté prod si besoin).
_DENY_SUBSTRINGS = frozenset(
    (
        "password",
        "motdepasse",
        "azerty",
        "qwerty",
        "letmein",
        "welcome",
        "admin",
        "123456789",
        "87654321",
        "00000000",
        "abcdef",
    )
)


def validate_password_rgpd(password: str, email: str | None = None) -> list[str]:
    """
    Retourne une liste de messages d’erreur en français (vide si le mot de passe est acceptable).
    `email` sert à éviter un mot de passe dérivé trop trivialement de l’adresse (partie locale).
    """
    errors: list[str] = []

    if password is None or (isinstance(password, str) and not password.strip()):
        return ["Le mot de passe est obligatoire."]

    if len(password) > MAX_LENGTH:
        errors.append(f"Le mot de passe ne doit pas dépasser {MAX_LENGTH} caractères.")

    if len(password) < MIN_LENGTH:
        errors.append(
            f"Le mot de passe doit contenir au moins {MIN_LENGTH} caractères "
            "(exigence renforcée pour la protection des données personnelles)."
        )

    if not re.search(r"[A-Z]", password):
        errors.append("Le mot de passe doit contenir au moins une lettre majuscule.")

    if not re.search(r"[a-z]", password):
        errors.append("Le mot de passe doit contenir au moins une lettre minuscule.")

    if not re.search(r"\d", password):
        errors.append("Le mot de passe doit contenir au moins un chiffre.")

    if not any(c in _SPECIAL for c in password):
        errors.append(
            "Le mot de passe doit contenir au moins un caractère spécial "
            f"({string.punctuation})."
        )

    lowered = password.lower()
    for fragment in _DENY_SUBSTRINGS:
        if fragment in lowered:
            errors.append(
                "Le mot de passe est trop courant ou trop prévisible ; choisissez une phrase ou une combinaison plus personnelle."
            )
            break

    if email:
        local = email.strip().lower().split("@", 1)[0]
        if len(local) >= 3 and local in lowered:
            errors.append(
                "Le mot de passe ne doit pas contenir la partie locale de votre adresse e-mail."
            )

    return errors
