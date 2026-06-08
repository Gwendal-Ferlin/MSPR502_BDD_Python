### MSPR501 - ETL Exercices et Materiel

## A quoi sert ce projet

Ce projet sert a charger des donnees d'exercices sportives depuis un fichier JSON, les nettoyer, puis les envoyer dans une base PostgreSQL.

Le pipeline fait deux choses:

- extraire et charger les equipements dans la table materiel
- extraire et charger les exercices dans la table exercice

## Source des donnees

Le fichier source est:

- [data/raw/exercises.json](data/raw/exercises.json)

## Fichiers principaux

- [main.py](main.py): point d'entré du pipeline ETL
- [extract.py](extract.py): lecture du JSON source
- [transform.py](transform.py): nettoyage et transformation des données
- [load.py](load.py): insertion des données dans PostgreSQL

## Sorties générées

- [data/processed/equipment_clean.csv](data/processed/equipment_clean.csv)
- [data/processed/exercise_clean.csv](data/processed/exercise_clean.csv)
- [logs/etl.log](logs/etl.log)

## Configuration

Copier le modele [.env.example](.env.example) en fichier `.env` et renseigner la connexion PostgreSQL vers **sante_db** (tables `materiel` et `ref_exercice`) :

- `DB_HOST` — `localhost` en local, `postgres-sante` dans Docker
- `DB_PORT` — `15433` en local (port mappe du compose), `5432` dans Docker
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` — voir `docker-compose.yml` (service `postgres-sante`)

## Lancer le projet

### Option A — Local (Windows)

```powershell
cd etl
.\setup.ps1
.\.venv\Scripts\python.exe main.py
```

### Option B — Local (pip manuel)

```bash
cd etl
python -m venv .venv
# Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # puis adapter si besoin
python main.py
```

### Option C — Docker (recommande si les BDD tournent deja via compose)

```bash
# Depuis la racine du depot, apres init de postgres-sante
mkdir -p etl/logs   # obligatoire sur TrueNAS si le dossier n'existe pas encore
docker compose --profile etl build etl
docker compose --profile etl run --rm etl
```

Les logs sont ecrits dans **`etl/logs/etl.log`** (local et Docker).

Les CSV restent dans le conteneur (ephemeres avec `--rm`). Pour les recuperer, relancer sans `--rm` puis `docker cp etl:/app/data/processed/. ./processed/`.

## Resultat attendu

A la fin:

- les CSV nettoyés sont générés dans data/processed (dans le conteneur Docker, ou en local)
- les nouvélles lignes sont insérées dans les tables materiel et ref_exercice
- les logs d'exécution dans `etl/logs/etl.log` (et dans le terminal)
