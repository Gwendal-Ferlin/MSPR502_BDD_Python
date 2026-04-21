# Déploiement sur serveur (MSPR 502)

Ce document décrit les **principes généraux** pour exécuter l’application sur un **serveur** (machine Linux, VM cloud, NAS, etc.) avec **Docker Compose**. Il ne dépend pas d’un fournisseur ou d’un matériel précis.

## Prérequis communs

- **Docker** et **Docker Compose** (plugin `docker compose` ou binaire `docker-compose` selon l’environnement).
- Fichier **`.env`** à la racine du projet (mots de passe bases, `JWT_SECRET`, etc.) — voir `.env.example`.
- **Ports** exposés non déjà utilisés sur l’hôte (par défaut : API 8000, Postgres 5432/5433/5434, MongoDB 27017/27018 — ajuster le YAML si besoin).
- Espace disque pour les **volumes** nommés (données Postgres / MongoDB).
- Pour un accès HTTPS public : **reverse proxy** (Traefik, Caddy, nginx) et certificats — hors périmètre du dépôt, à configurer côté infra.

## Déploiement standard (SSH, VM ou serveur dédié)

1. **Récupérer le code** sur le serveur (clone Git, archive, CI/CD).
2. **Configurer** `.env` (ne pas commiter les secrets).
3. Depuis la racine du projet :  
   `docker compose up -d --build`
4. Vérifier les services : `docker compose ps`, logs des conteneurs, `GET /health` sur l’URL exposée.
5. **Initialisation des bases** : en local, les scripts sous `init/` sont souvent montés automatiquement. Sur certains serveurs (stockage réseau, permissions strictes), il peut être nécessaire d’utiliser un fichier Compose **sans** montage d’init et d’exécuter les scripts SQL/JS **à la main** une fois les conteneurs démarrés — procédure détaillée dans le `README.md` (section initialisation des bases).

Les chemins dans `docker-compose.yml` sont souvent **relatifs** (`./init/...`). Sur le serveur, le répertoire de travail doit être **la racine du projet** pour que ces montages restent valides. Si l’outil de déploiement impose un autre répertoire courant, **remplacer** les chemins relatifs par des **chemins absolus** cohérents avec l’emplacement réel des fichiers sur la machine.

## Variables d’environnement

Le Compose charge en général un fichier `.env` à côté du YAML. Si l’environnement d’exécution **ne charge pas** automatiquement ce fichier :

- définir les variables dans l’interface d’administration du serveur / de l’orchestrateur, ou  
- les reporter dans la section `environment` des services dans le YAML (en **évitant** de committer des secrets en clair : préférer des secrets managés ou des variables injectées par la CI).

## Build de l’image API

Le service `api` est défini avec `build: { context: . }`. Il faut que le **contexte de build** contienne le `Dockerfile` et le code. Si le serveur ne peut pas builder (pas d’accès réseau pour les images de base, politique interne), une alternative est de **construire l’image ailleurs**, la **pousser** vers un registry (Docker Hub, GitLab Container Registry, registry privé), puis remplacer dans le Compose `build:` par `image: <registry>/<nom>:<tag>`.

## Déploiement via interface graphique (NAS, PaaS « Docker Compose »)

Certains équipements (NAS, appliances) proposent une installation d’applications à partir d’un **fichier Compose YAML** sans passer par SSH. Les contraintes sont souvent les mêmes :

- chemins d’**init** : remplacer `./init/...` par des chemins **absolus** sur le système de fichiers du serveur ;
- **secrets** : même problématique que ci-dessus pour `.env` ;
- **ports** : vérifier l’absence de conflit avec d’autres services sur la même machine.

La documentation du constructeur (ports par défaut, emplacement des volumes) reste la référence pour ce type de plateforme.

## Fichier `docker-compose.truenas.yml`

Le dépôt peut inclure un fichier Compose **alternatif** (ex. `docker-compose.truenas.yml`) adapté à des environnements où les montages d’initialisation automatique posent problème (permissions, FS réseau). Ce n’est **pas** obligatoire : sur un serveur Linux classique avec stockage local, le `docker-compose.yml` principal suffit en général. Consulter les commentaires en tête du fichier alternatif et le `README.md` pour les ports et l’init manuelle éventuelle.

## Vérification après déploiement

- `GET /health` → `{"status":"ok"}`
- Documentation API : `/docs`
- Sauvegardes : planifier des sauvegardes des **volumes Docker** ou dumps BDD selon la politique du projet.

Pour un **rebuild forcé** de l’image API après changement de code :  
`docker compose build --no-cache api` puis redémarrage du service `api`.
