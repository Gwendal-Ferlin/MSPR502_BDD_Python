"""Charge le moteur IA plats (Hugging Face) depuis `ia-reco/Ia_recom_mistral_plat_distant.py`."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

_IA_PLATS_MODULE: Any = None


def _resolve_script_path() -> Path:
    docker_path = Path("/app/ia-reco/Ia_recom_mistral_plat_distant.py")
    if docker_path.is_file():
        return docker_path
    local = Path(__file__).resolve().parents[2] / "ia-reco" / "Ia_recom_mistral_plat_distant.py"
    if local.is_file():
        return local
    raise FileNotFoundError(
        "Fichier ia-reco/Ia_recom_mistral_plat_distant.py introuvable. "
        "Vérifiez le build Docker (fichiers ia-reco) ou un clone complet du dépôt."
    )


def load_ia_plats_module() -> Any:
    global _IA_PLATS_MODULE
    if _IA_PLATS_MODULE is not None:
        return _IA_PLATS_MODULE
    path = _resolve_script_path()
    spec = importlib.util.spec_from_file_location("ia_recom_mistral_plat_distant", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Impossible de charger le module depuis {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _IA_PLATS_MODULE = mod
    return mod


def generer_plats(data: dict[str, Any]) -> dict[str, Any]:
    """Délègue au mock local ou au script distant."""
    from api.config import settings
    from api.services import ia_mock

    if settings.ia_mock_mode:
        return ia_mock.generer_plats(data)

    from api.services.ia_referentiels_db import (
        load_ingredients_by_budget,
        load_restriction_equivalences,
        persist_new_restriction_equivalence,
    )

    mod = load_ia_plats_module()
    payload = dict(data)

    equiv = load_restriction_equivalences()
    if equiv:
        payload["_restriction_equivalences"] = equiv
        payload["_persist_restrictions"] = persist_new_restriction_equivalence

    try:
        niveau_budget, _ = mod.normaliser_budget(payload.get("budget"))
    except Exception:
        niveau_budget = 2
    ingredients = load_ingredients_by_budget(niveau_budget)
    if ingredients is not None:
        payload["_ingredients_catalogue"] = ingredients

    return mod.generer_recommandations_plats(payload)
