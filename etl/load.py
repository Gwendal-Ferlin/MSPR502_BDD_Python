from __future__ import annotations

import logging
import os
from collections.abc import Sequence

import pandas as pd


def load_records_to_postgres(
	dataframe: pd.DataFrame,
	table_name: str,
	value_columns: Sequence[str],
	logger: logging.Logger | None = None,
	key_columns: Sequence[str] | None = None,
	id_column: str = "id",
) -> int:
	"""Insere des lignes nettoyees en PostgreSQL avec attribution sequentielle des ids."""
	logger = logger or logging.getLogger("healthai_etl")
	# Journalise la cible de connexion pour faciliter le diagnostic.
	logger.info(
		"Connexion PostgreSQL vers %s:%s/%s",
		os.environ.get("DB_HOST", "localhost"),
		os.environ.get("DB_PORT", "5432"),
		os.environ.get("DB_NAME"),
	)

	# Import dynamique pour eviter un echec au chargement du module.
	try:
		import psycopg2
		from psycopg2 import sql
		from psycopg2.extras import execute_values
	except Exception as exc:  # pragma: no cover - runtime dependency
		logger.error("psycopg2 manquant ; chargement PostgreSQL impossible")
		raise RuntimeError(
			"psycopg2 is required to load into PostgreSQL; run 'pip install psycopg2-binary'"
		) from exc

	host = os.environ.get("DB_HOST", "localhost")
	port = int(os.environ.get("DB_PORT", "5432"))
	database = os.environ.get("DB_NAME")
	user = os.environ.get("DB_USER")
	password = os.environ.get("DB_PASSWORD")

	# Les identifiants DB sont obligatoires pour lancer le chargement.
	if not database or not user or password is None:
		logger.error("Identifiants PostgreSQL manquants dans .env")
		raise ValueError("DB_NAME, DB_USER and DB_PASSWORD must be defined in .env")

	# Rien a inserer si le DataFrame est vide.
	if dataframe is None or dataframe.empty:
		logger.warning("Aucune ligne a inserer dans %s", table_name)
		return 0

	# Controle des colonnes attendues avant nettoyage.
	missing_columns = [column_name for column_name in value_columns if column_name not in dataframe.columns]
	if missing_columns:
		raise ValueError(f"Colonnes requises manquantes pour {table_name}: {', '.join(missing_columns)}")

	# Normalisation des champs et suppression des lignes invalides.
	clean_dataframe = dataframe.loc[:, list(value_columns)].copy()
	for column_name in value_columns:
		clean_dataframe[column_name] = clean_dataframe[column_name].astype(str).str.strip()
	clean_dataframe = clean_dataframe.replace({"": pd.NA}).dropna(subset=list(value_columns))
	clean_dataframe = clean_dataframe.drop_duplicates(subset=list(value_columns)).reset_index(drop=True)

	# Arret propre si le nettoyage retire toutes les lignes.
	if clean_dataframe.empty:
		logger.warning("Aucune ligne valide apres nettoyage pour %s", table_name)
		return 0

	if key_columns is None:
		key_columns = value_columns

	inserted_count = 0
	logger.info("Lignes nettoyees pour %s : %s", table_name, len(clean_dataframe))
	# Une seule connexion pour toute l'operation.
	conn = psycopg2.connect(host=host, port=port, dbname=database, user=user, password=password)
	try:
		with conn:
			with conn.cursor() as cur:
				logger.info("Connexion etablie sur la table %s", table_name)
				# Lecture des cles existantes pour eviter les doublons.
				select_columns = [sql.Identifier(column_name) for column_name in key_columns]
				cur.execute(sql.SQL("SELECT {} FROM {}").format(sql.SQL(", ").join(select_columns), sql.Identifier(table_name)))
				existing_rows = {
					tuple(str(value).strip().lower() for value in row)
					for row in cur.fetchall()
					if row and all(value is not None and str(value).strip() for value in row)
				}

				# Filtrage des nouvelles lignes seulement.
				new_rows = []
				for _, row in clean_dataframe.iterrows():
					row_key = tuple(str(row[column_name]).strip().lower() for column_name in key_columns)
					if row_key not in existing_rows:
						new_rows.append(row)

				if not new_rows:
					logger.error("Aucune nouvelle valeur a inserer dans %s ; tout existe deja", table_name)
					return 0

				logger.info("%s deja presentes, %s nouvelles lignes detectees", len(existing_rows), len(new_rows))

				# Calcul du prochain id de depart a partir du max existant.
				cur.execute(sql.SQL("SELECT COALESCE(MAX({}), 0) FROM {}").format(sql.Identifier(id_column), sql.Identifier(table_name)))
				start_id = int(cur.fetchone()[0])

				# Preparation du payload d'insertion: id + colonnes metier.
				values = []
				for index, row in enumerate(new_rows, start=1):
					values.append((start_id + index, *[row[column_name] for column_name in value_columns]))

				# Insertion par lots pour limiter les aller-retours SQL.
				column_list = sql.SQL(", ").join([sql.Identifier(id_column)] + [sql.Identifier(column_name) for column_name in value_columns])
				query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(sql.Identifier(table_name), column_list)
				execute_values(cur, query.as_string(conn), values, page_size=100)
				inserted_count = len(values)
				logger.info("Insertion effectuee : %s nouvelles lignes a partir de l'id %s", inserted_count, start_id + 1)
	finally:
		# Fermeture systematique de la connexion meme en cas d'erreur.
		conn.close()
		logger.info("Connexion PostgreSQL fermee")

	return inserted_count


def load_materials_to_postgres(dataframe: pd.DataFrame, logger: logging.Logger | None = None) -> int:
	"""Wrapper de chargement pour la table materiel."""
	return load_records_to_postgres(
		dataframe,
		table_name="materiel",
		value_columns=["nom"],
		key_columns=["nom"],
		id_column="id_materiel",
		logger=logger,
	)

