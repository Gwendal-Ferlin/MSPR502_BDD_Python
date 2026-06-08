from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


SUPPORTED_RAW_EXTENSIONS = {".csv", ".json", ".xls", ".xlsx"}
EXPECTED_RAW_COLUMNS = {"equipment", "name", "id", "primary_muscle", "difficulty", "nom"}


def _read_raw_file(raw_path: Path, logger: Any | None = None) -> list[dict[str, Any]]:
	"""Lit un fichier brut supporte et retourne une liste d'enregistrements."""
	if raw_path.suffix.lower() == ".json":
		# Les fichiers JSON du projet contiennent une liste d'exercices.
		with raw_path.open("r", encoding="utf-8") as file_handle:
			data = json.load(file_handle)

		if not isinstance(data, list):
			raise ValueError(f"The raw exercises file must contain a JSON array: {raw_path}")

		if logger is not None:
			json_keys = {str(key) for row in data if isinstance(row, dict) for key in row.keys()}
			if not (json_keys & EXPECTED_RAW_COLUMNS):
				logger.error("Aucune valeur exploitable dans %s: colonnes non reconnues", raw_path.name)

		return data

	if raw_path.suffix.lower() in {".xls", ".xlsx"}:
		# Chaque ligne Excel est convertie en dictionnaire pour reutiliser le pipeline.
		dataframe = pd.read_excel(raw_path)
		dataframe = dataframe.dropna(how="all")
		if logger is not None:
			column_names = {str(column_name).strip().lower() for column_name in dataframe.columns}
			if not (column_names & EXPECTED_RAW_COLUMNS):
				logger.error("Aucune valeur exploitable dans %s: colonnes non reconnues", raw_path.name)
		return dataframe.to_dict(orient="records")

	if raw_path.suffix.lower() == ".csv":
		# Les fichiers CSV sont lus comme tableaux plats.
		dataframe = pd.read_csv(raw_path)
		dataframe = dataframe.dropna(how="all")
		if logger is not None:
			column_names = {str(column_name).strip().lower() for column_name in dataframe.columns}
			if not (column_names & EXPECTED_RAW_COLUMNS):
				logger.error("Aucune valeur exploitable dans %s: colonnes non reconnues", raw_path.name)
		return dataframe.to_dict(orient="records")

	raise ValueError(f"Unsupported raw file format: {raw_path.suffix}")


def _discover_raw_files(raw_source: Path) -> list[Path]:
	"""Retourne la liste des fichiers bruts a traiter dans le dossier source."""
	if raw_source.is_file():
		return [raw_source]

	if not raw_source.exists():
		raise FileNotFoundError(f"Raw source not found: {raw_source}")

	# On conserve uniquement les fichiers d'entree supportes.
	return sorted(
		path
		for path in raw_source.iterdir()
		if path.is_file() and path.suffix.lower() in SUPPORTED_RAW_EXTENSIONS
	)

def extract_exercises(raw_file: str | Path, logger: Any | None = None) -> list[dict[str, Any]]:
	"""Lit un fichier ou un dossier brut et retourne la liste des exercices."""
	# Conversion en objet Path pour supporter str et Path.
	source_path = Path(raw_file)
	# Recherche de tous les fichiers d'entree supportes quand un dossier est fourni.
	raw_files = _discover_raw_files(source_path)

	if not raw_files:
		raise FileNotFoundError(f"No supported raw files found in: {source_path}")

	# Fusion de toutes les lignes/exercices provenant des sources brutes.
	merged_records: list[dict[str, Any]] = []
	for raw_path in raw_files:
		merged_records.extend(_read_raw_file(raw_path, logger=logger))

	return merged_records

