"""Charge le moteur IA distant (Hugging Face) depuis `ia-reco/Ia_recom_mistral_distant.py`."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

_IA_MODULE: Any = None


def _resolve_script_path() -> Path:
    """Docker : `/app/ia-reco/` ; local : racine du dépôt `ia-reco/`."""
    docker_path = Path("/app/ia-reco/Ia_recom_mistral_distant.py")
    if docker_path.is_file():
        return docker_path
    # api/services/ia_recommendations.py -> parents[2] = racine du projet
    local = (
        Path(__file__).resolve().parents[2] / "ia-reco" / "Ia_recom_mistral_distant.py"
    )
    if local.is_file():
        return local
    raise FileNotFoundError(
        "Fichier ia-reco/Ia_recom_mistral_distant.py introuvable. "
        "Vérifiez que le dossier ia-reco est présent (build Docker ou clone complet)."
    )


def load_ia_module() -> Any:
    global _IA_MODULE
    if _IA_MODULE is not None:
        return _IA_MODULE
    path = _resolve_script_path()
    spec = importlib.util.spec_from_file_location("ia_recom_mistral_distant", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Impossible de charger le module depuis {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _IA_MODULE = mod
    return mod


def generer_programme(data: dict[str, Any]) -> dict[str, Any]:
    """Délègue au mock local ou au script Mistral distant (appel HF Router)."""
    from api.config import settings
    from api.services import ia_mock

    if settings.ia_mock_mode:
        return ia_mock.generer_programme(data)

    from api.services.ia_referentiels_db import (
        load_exercice_materiel_liaisons,
        load_exercices_catalogue,
        load_materiels_catalogue,
    )

    mod = load_ia_module()
    payload = dict(data)
    exercices = load_exercices_catalogue()
    if exercices:
        payload["_exercices_catalogue"] = exercices
    materiels = load_materiels_catalogue()
    if materiels:
        payload["_materiels_catalogue"] = materiels
    liaisons = load_exercice_materiel_liaisons()
    if liaisons:
        payload["_exercice_materiel_liaisons"] = liaisons
    return mod.generer_programme(payload)
