"""Réponses IA statiques pour les profils offline / performance (sans Hugging Face)."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def generer_programme(data: dict[str, Any]) -> dict[str, Any]:
    niveau = data.get("niveau", "normal")
    objectif = data.get("objectif", "perte_de_poids")
    date_debut = data.get("date_debut", "2026-01-01T00:00:00")
    date_fin = data.get("date_fin", "2026-02-01T00:00:00")

    try:
        debut = datetime.fromisoformat(str(date_debut).replace("Z", "+00:00"))
        fin = datetime.fromisoformat(str(date_fin).replace("Z", "+00:00"))
        jours = max((fin - debut).days, 7)
        nombre_semaines = max(1, jours // 7)
    except (TypeError, ValueError):
        nombre_semaines = 4

    series = 4 if niveau == "intensif" else 3 if niveau == "normal" else 2
    reps = 12 if objectif == "prise_de_masse" else 15

    return {
        "niveau": niveau,
        "objectif": objectif,
        "programme": [
            {"exercice": "Squat (Quadriceps)", "series": series, "repetitions": reps, "temps_de_repos": 90},
            {"exercice": "Pompes (Pectoraux)", "series": series, "repetitions": reps, "temps_de_repos": 60},
            {"exercice": "Rowing haltères (Dos)", "series": series, "repetitions": reps, "temps_de_repos": 75},
            {"exercice": "Planche (Abdominaux)", "series": series, "repetitions": 1, "temps_de_repos": 45},
        ],
        "progression": {"nombre_semaines": nombre_semaines},
        "_mock": True,
    }


def generer_plats(data: dict[str, Any]) -> dict[str, Any]:
    objectif = data.get("objectif_alimentaire", "perte_de_poids")
    repas_par_jour = int(data.get("repas_par_jour", 2))
    repas_types = data.get("repas_types")
    if not repas_types:
        defaults: list[str] = ["dejeuner", "diner", "souper"]
        repas_types = defaults[:repas_par_jour]

    repas_mock = {
        "dejeuner": {
            "type": "dejeuner",
            "plats": [
                {
                    "nom": "Bol protéiné mock",
                    "ingredients": ["Poulet", "Riz", "Brocoli"],
                    "calories": 520,
                }
            ],
        },
        "diner": {
            "type": "diner",
            "plats": [
                {
                    "nom": "Salade complète mock",
                    "ingredients": ["Saumon", "Quinoa", "Épinards"],
                    "calories": 480,
                }
            ],
        },
        "souper": {
            "type": "souper",
            "plats": [
                {
                    "nom": "Omelette légère mock",
                    "ingredients": ["Œufs", "Tomates", "Fromage"],
                    "calories": 350,
                }
            ],
        },
    }

    repas = [repas_mock[t] for t in repas_types if t in repas_mock]

    return {
        "objectif_alimentaire": objectif,
        "repas_par_jour": repas_par_jour,
        "plan_repas": [{"repas": repas}],
        "liste_courses": [
            {"ingredient": "Poulet", "quantite": "400 g", "categorie": "protéines"},
            {"ingredient": "Riz", "quantite": "300 g", "categorie": "féculents"},
            {"ingredient": "Brocoli", "quantite": "200 g", "categorie": "légumes"},
        ],
        "budget": {"niveau": 2, "libelle": "standard", "ingredients_reference_count": 3},
        "_mock": True,
    }
