from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

from extract import extract_exercises
from load import load_materials_to_postgres, load_records_to_postgres
from transform import transform_exercise_equipments, transform_exercises_catalog


# Chemins utilises par le pipeline ETL.
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_FILE = BASE_DIR / "data" / "processed" / "equipment_clean.csv"
EXERCISE_PROCESSED_FILE = BASE_DIR / "data" / "processed" / "exercise_clean.csv"
LOG_FILE = BASE_DIR / "logs" / "etl.log"
ENV_FILE = BASE_DIR / ".env"


def _project_relative_path(path: Path) -> str:
	"""Retourne un chemin relatif au dossier du projet quand c'est possible."""
	try:
		return str(path.relative_to(BASE_DIR))
	except ValueError:
		return str(path)


def setup_logger() -> tuple[logging.Logger, Path | None]:
	"""Configure les logs console, et fichier si le repertoire est accessible."""
	log_file = LOG_FILE

	logger = logging.getLogger("healthai_etl")
	logger.setLevel(logging.INFO)
	# Evite les doublons de handlers lors de relances successives.
	logger.handlers.clear()

	formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%d/%m/%Y %H:%M:%S")

	# Handler console pour le suivi en temps reel (toujours disponible).
	console_handler = logging.StreamHandler()
	console_handler.setFormatter(formatter)
	logger.addHandler(console_handler)

	active_log_file: Path | None = None
	try:
		log_file.parent.mkdir(parents=True, exist_ok=True)
		file_handler = logging.FileHandler(log_file, encoding="utf-8")
		file_handler.setFormatter(formatter)
		logger.addHandler(file_handler)
		active_log_file = log_file
	except OSError:
		logger.warning(
			"Impossible d'ecrire dans %s ; logs console uniquement",
			log_file.parent,
		)

	return logger, active_log_file


def main() -> None:
	"""Orchestre le flux complet: extraction, transformation, export, chargement."""
	# Charge les variables d'environnement depuis le .env du projet.
	load_dotenv(ENV_FILE)
	logger, log_file = setup_logger()
	if log_file is not None:
		logger.info("Journal fichier : %s", _project_relative_path(log_file))
	else:
		logger.info("Journal fichier : indisponible (console uniquement)")
	logger.info("=== Demarrage de l'ETL exercices et materiel ===")

	try:
		logger.info("[1/4] Extraction des sources brutes")
		# Extraction depuis toutes les sources brutes du dossier data/raw.
		exercises = extract_exercises(RAW_DIR, logger=logger)
		logger.info("Sources lues dans %s : %s enregistrements", _project_relative_path(RAW_DIR), len(exercises))

		logger.info("[2/4] Transformation des donnees")
		# Transformation des equipements pour la table materiel.
		equipments = transform_exercise_equipments(exercises)
		logger.info("Materiel unique prepare : %s lignes", len(equipments))

		# Export CSV intermediaire des equipements nettoyes.
		PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
		equipments.to_csv(PROCESSED_FILE, index=False, encoding="utf-8")
		logger.info("Export materiel nettoye : %s", _project_relative_path(PROCESSED_FILE))

		# Transformation du catalogue d'exercices.
		exercise_rows = transform_exercises_catalog(exercises)
		logger.info("Exercices prepares : %s lignes", len(exercise_rows))

		# Export CSV intermediaire des exercices nettoyes.
		EXERCISE_PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
		exercise_rows.to_csv(EXERCISE_PROCESSED_FILE, index=False, encoding="utf-8")
		logger.info("Export exercices nettoyes : %s", _project_relative_path(EXERCISE_PROCESSED_FILE))

		logger.info("[3/4] Chargement en base")
		# Chargement en base de la table materiel.
		material_inserted_count = load_materials_to_postgres(equipments, logger=logger)
		logger.info(
			"Lignes materiel inserees dans %s : %s",
			"materiel",
			material_inserted_count,
		)

		# Chargement en base de la table ref_exercice.
		exercise_inserted_count = load_records_to_postgres(
			exercise_rows,
			table_name="ref_exercice",
			value_columns=["nom", "muscle_principal", "niveau"],
			key_columns=["nom"],
			id_column="id_exercice",
			logger=logger,
		)
		logger.info(
			"Lignes exercice inserees dans %s : %s",
			"ref_exercice",
			exercise_inserted_count,
		)
		logger.info("[4/4] ETL termine avec succes")
	except Exception:
		# Conserve la stack trace dans les logs puis propage l'erreur.
		logger.exception("ETL interrompu par une erreur")
		raise
	finally:
		# Ligne vide pour separer les executions dans le fichier de log.
		if log_file is not None:
			try:
				with log_file.open("a", encoding="utf-8") as log_handle:
					log_handle.write("\n")
			except OSError:
				pass


if __name__ == "__main__":
	main()

