# Déploiement HealthAI Coach (MSPR 502)

## Option retenue : TrueNAS Scale — Install via YAML (Docker Compose)

Sur **TrueNAS Scale 24.10 (Electric Eel)** ou plus récent, l’interface supporte nativement le **Docker Compose** via **Apps → Custom → Install via YAML**. Le champ **Custom Config** attend un fichier YAML au format Docker Compose (pas du Kubernetes).

**Référence :** [TrueNAS Docs – Custom App Screens (24.10)](https://www.truenas.com/docs/scale/24.10/scaleuireference/apps/installcustomappscreens/) — section « Add Custom App Screen ».

### Étapes

1. **Préparer le projet sur TrueNAS**  
   Copier le dépôt (ou les fichiers nécessaires) sur un dataset accessible, par ex. `/mnt/pool/apps/mspr502/`, pour que les chemins d’init et le build de l’API soient cohérents.

2. **Variables d’environnement**  
   Le `docker-compose.yml` actuel utilise un fichier `.env`. Si TrueNAS ne charge pas de `.env` à côté du Custom Config :
   - soit renseigner les variables dans l’interface (si l’écran le permet),
   - soit les mettre en dur dans la section `environment` du service `api` (et des Postgres) dans le YAML collé (en évitant les secrets en clair en prod).

3. **Chemins d’init (bind mounts)**  
   Les services utilisent `./init/postgres-utilisateur`, `./init/postgres-sante`, `./init/mongodb-logs`, `./init/mongodb-reco`. Dans le YAML collé, remplacer `./init/...` par le chemin absolu sur TrueNAS, par ex. `/mnt/pool/apps/mspr502/init/postgres-utilisateur`, etc.

4. **Build de l’API**  
   Le service `api` est défini avec `build: context: .`. Si l’éditeur Custom Config exécute le compose depuis le répertoire du projet (après avoir pointé ou copié les fichiers), garder `context: .` et s’assurer que le `Dockerfile` et le code sont bien dans ce contexte. Sinon, builder l’image en local, la pousser vers un registry (Docker Hub, registry privé) et remplacer par `image: votre-registry/mspr502-api:tag`.

5. **Ports**  
   Vérifier que les ports 5432, 5433, 27017, 27018, 8000 ne sont pas déjà utilisés par d’autres apps TrueNAS (voir [Default Ports](https://www.truenas.com/docs/references/defaultports/) si besoin).

6. **Déploiement**  
   - Apps → Discover → **Custom** → **Install via YAML**.  
   - **Name** : par ex. `healthai-coach`.  
   - **Custom Config** : coller le contenu de `docker-compose.yml` (après adaptations ci-dessus).  
   - Enregistrer pour lancer le déploiement.

---

## Alternative : VM Linux + Docker Compose

Si tu préfères tout gérer dans une VM (SSH, `docker compose up`, logs, sauvegardes manuelles), installer une VM sous TrueNAS puis à l’intérieur utiliser le même `docker-compose.yml` et `.env` qu’en local. Aucune conversion Kubernetes nécessaire.



docker compose build --no-cache api