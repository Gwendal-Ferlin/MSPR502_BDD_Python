from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from api.auth.dependencies import get_current_user
from api.schemas.auth import CurrentUser
from api.schemas.ia_plats import IaPlatsRequest
from api.schemas.ia_reco import IaRecommandationRequest
from api.services.ia_plats import generer_plats as ia_generer_plats
from api.services.ia_recommendations import generer_programme as ia_generer_programme

router = APIRouter(prefix="/ia", tags=["IA"])


def _http_status_for_result(result: dict[str, Any]) -> int | None:
    """Interprète le dict renvoyé par le moteur IA (erreurs métier vs HF)."""
    err = result.get("error")
    if err is None:
        return None
    err_s = str(err).lower()
    if "hf" in err_s or "request failed" in err_s or "token" in err_s:
        return status.HTTP_502_BAD_GATEWAY
    return status.HTTP_400_BAD_REQUEST


@router.post("/recommandations")
def post_recommandations(
    body: IaRecommandationRequest,
    _: Annotated[CurrentUser, Depends(get_current_user)],
):
    """
    Génère un programme d'exercices (JSON) via le modèle distant Hugging Face
    (`ia-reco/Ia_recom_mistral_distant.py`). Nécessite `HF_API_TOKEN` dans l'environnement
    (fichier `.env` à la racine du projet ou variables du conteneur `api`).

    Le corps doit inclure **soit** `biometrie`, **soit** `suivi_biometrique` (poids actuel en kg) ;
    l'exemple Swagger montre uniquement `biometrie`.
    """
    try:
        payload = body.to_engine_dict()
        result = ia_generer_programme(payload)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur moteur IA: {e!s}",
        ) from e

    code = _http_status_for_result(result)
    if code is not None:
        raise HTTPException(status_code=code, detail=result)
    return result


@router.post("/plats")
def post_plats(
    body: IaPlatsRequest,
    _: Annotated[CurrentUser, Depends(get_current_user)],
):
    """
    Génère un plan de repas (JSON) via `ia-reco/Ia_recom_mistral_plat_distant.py` (Hugging Face).
    Nécessite `HF_API_TOKEN` et les fichiers `final_ingredients_list.json` / `restrictions_equivalences.json`
    dans `ia-reco/` (inclus dans l’image Docker API).
    """
    try:
        result = ia_generer_plats(body.to_engine_dict())
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur moteur IA plats: {e!s}",
        ) from e

    code = _http_status_for_result(result)
    if code is not None:
        raise HTTPException(status_code=code, detail=result)
    return result
