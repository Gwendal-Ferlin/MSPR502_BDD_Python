from __future__ import annotations

from typing import Any

import pandas as pd


def _difficulty_to_niveau(difficulty: Any) -> str:
	"""Convertit la difficulté numérique en niveau métier."""
	# On tente une conversion défensive depuis la source JSON.
	try:
		value = int(difficulty)
	except (TypeError, ValueError):
		# Valeur par défaut quand la difficulté est absente ou invalide.
		return "normal"

	# Règles de mapping vers la colonne cible `niveau`.
	if value <= 4:
		return "facile"
	if value <= 7:
		return "normal"
	return "intensif"


def _normalize_muscle_name(muscle_name: Any) -> str:
	"""Nettoie le muscle principal et applique une valeur de repli."""
	text = str(muscle_name or "").strip()
	if not text:
		return "Autre"

	return text


def transform_exercise_equipments(exercises: list[dict[str, Any]]) -> pd.DataFrame:
	"""Construit la liste unique des équipements pour la table materiel."""
	records: list[dict[str, str]] = []

	# Extraction des equipements depuis chaque exercice JSON, puis des noms
	# directs venant des fichiers Excel/CSV du dossier raw.
	for exercise in exercises:
		equipment_list = exercise.get("equipment") or []
		if not isinstance(equipment_list, list):
			equipment_list = [equipment_list]

		for equipment in equipment_list:
			equipment_name = str(equipment).strip().lower()
			if equipment_name:
				records.append({"nom": equipment_name})

		material_name = str(exercise.get("nom") or "").strip().lower()
		if material_name:
			records.append({"nom": material_name})

	# Schéma vide explicite si aucune donnée n'est trouvée.
	if not records:
		return pd.DataFrame(columns=["nom"])

	# Normalisation, suppression des vides et déduplication.
	dataframe = pd.DataFrame(records)
	dataframe["nom"] = dataframe["nom"].str.strip().str.lower()
	dataframe = dataframe.dropna(subset=["nom"])
	dataframe = dataframe[dataframe["nom"] != ""]
	dataframe = dataframe.drop_duplicates(subset=["nom"]).sort_values("nom").reset_index(drop=True)
	return dataframe


def transform_exercises_catalog(exercises: list[dict[str, Any]]) -> pd.DataFrame:
	"""Prépare les lignes d'exercices pour la table exercice."""
	records: list[dict[str, str]] = []

	# Construction d'un enregistrement plat pour chaque exercice valide.
	for exercise in exercises:
		name = str(exercise.get("name") or exercise.get("id") or "").strip()
		if not name:
			continue

		records.append(
			{
				"nom": name,
				"muscle_principal": _normalize_muscle_name(exercise.get("primary_muscle")),
				"niveau": _difficulty_to_niveau(exercise.get("difficulty")),
			}
		)

	# Schéma vide explicite si aucune donnée n'est trouvée.
	if not records:
		return pd.DataFrame(columns=["nom", "muscle_principal", "niveau"])

	# Nettoyage final avant export et chargement en base.
	dataframe = pd.DataFrame(records)
	dataframe["nom"] = dataframe["nom"].astype(str).str.strip()
	dataframe["muscle_principal"] = dataframe["muscle_principal"].astype(str).str.strip()
	dataframe["niveau"] = dataframe["niveau"].astype(str).str.strip().str.lower()
	dataframe = dataframe.dropna(subset=["nom", "muscle_principal", "niveau"])
	dataframe = dataframe[(dataframe["nom"] != "") & (dataframe["muscle_principal"] != "") & (dataframe["niveau"] != "")]
	dataframe = dataframe.drop_duplicates(subset=["nom"]).sort_values("nom").reset_index(drop=True)
	return dataframe

