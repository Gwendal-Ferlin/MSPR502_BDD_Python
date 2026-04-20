# Compte rendu – Environnement d’exécution (MSPR 502)

Ce document synthétise l’évaluation de l’environnement technique du projet MSPR 502 selon trois axes : **reproductibilité**, **robustesse au démarrage** et **documentation opérationnelle**. Il est rédigé pour être intégré tel quel dans un compte rendu de projet.

---

### 1) Reproductibilité de l’environnement

#### Constat
L’environnement est **reproductible** sur une autre machine de développement, car l’exécution repose sur **Docker Compose** avec des images standard (PostgreSQL, MongoDB) et une configuration centralisée via un fichier `.env`.

#### Points forts
- **Standardisation** : orchestration via `docker-compose.yml`, images officielles, réseau dédié, volumes persistants.
- **Paramétrage externalisé** : secrets et variables (utilisateurs, mots de passe, secret JWT, etc.) isolés dans `.env`, avec un modèle `.env.example`.
- **Initialisation “local” automatisée** : en environnement local, les scripts d’initialisation SQL sont montés et exécutés au premier démarrage des conteneurs PostgreSQL.

#### Limites / risques identifiés
- **Pré-requis “.env”** : un minimum d’ajustement est requis (copie de `.env.example` et saisie de secrets). Cela reste une bonne pratique, mais ce n’est pas un “zéro configuration”.
- **Cas TrueNAS / serveur** : l’initialisation automatique est volontairement désactivée (bases démarrent vides), ce qui impose des étapes manuelles d’amorçage (schémas + seed) après déploiement.

#### Recommandations (priorisées)
- **R1 (court terme)** : expliciter dès la section “Démarrage” la différence *Local* vs *TrueNAS* (init automatique vs init manuelle) pour éviter les incompréhensions.
- **R2 (court terme)** : ajouter un récapitulatif des ports exposés (notamment les décalages hôte/containeur) dans la doc d’exploitation.
- **R3 (moyen terme)** : fournir un script d’amorçage (ex. `make init` / script shell) pour enchaîner les étapes d’initialisation serveur de manière homogène et limiter les erreurs humaines.

---

### 2) Robustesse du démarrage (dépendances et santé des services)

#### Constat
Le démarrage est **robuste** grâce à une stratégie explicite :
- chaque base de données dispose d’un **healthcheck** ;
- l’API déclare des **dépendances** conditionnées à l’état “healthy” des bases.

Cela répond au besoin métier/technique : **l’API ne se lance pas si les bases ne sont pas prêtes**.

#### Points forts
- **Healthchecks présents** :
  - PostgreSQL : vérification de disponibilité via `pg_isready` sur la base cible ;
  - MongoDB : ping de l’instance via `mongosh` et `db.adminCommand('ping')`.
- **Orchestration des dépendances** : le service API attend explicitement que Postgres (2) et Mongo (2) soient “healthy” avant d’être démarré.
- **Lisibilité** : la documentation annonce clairement l’ordre de démarrage attendu.

#### Limites / risques identifiés
- **Robustesse “après démarrage”** : l’orchestration Compose sécurise l’ordre de démarrage initial, mais ne garantit pas à elle seule la continuité si une base devient indisponible après coup (redémarrage d’un conteneur DB, latence, etc.). La résilience dépend alors du comportement applicatif (retries, timeouts, reconnexion) et/ou d’une stratégie de supervision.

#### Recommandations (priorisées)
- **R4 (court terme)** : documenter une procédure de diagnostic “API down / DB up/down” (commandes à exécuter, signaux à vérifier, logs).
- **R5 (moyen terme)** : ajouter une notion de “readiness” applicative (au niveau API) qui reflète réellement la disponibilité des dépendances, afin d’améliorer l’exploitation et la supervision.

---

### 3) Documentation opérationnelle (prise en main par un développeur externe)

#### Constat
La documentation actuelle est **opérationnelle et exploitable** : elle couvre le démarrage, la configuration, l’initialisation des bases (y compris en serveur/TrueNAS) et propose une description extensive des endpoints API (via Swagger et inventaire).

#### Points forts
- **Parcours de démarrage clair** : prérequis → configuration `.env` → commande de lancement → URLs utiles (API + Swagger).
- **Procédures serveur** : l’initialisation manuelle des bases est décrite étape par étape (PostgreSQL et MongoDB).
- **Documentation API riche** : endpoints listés, règles d’authentification, comportements spécifiques (ex. logging admin).

#### Axes d’amélioration concrets
- **A1** : ajouter une section “Dépannage” (symptôme → cause probable → vérification → action corrective).
- **A2** : ajouter une section “Données / persistance” expliquant le rôle des volumes et les impacts d’un redémarrage, d’un `down`, ou d’une réinitialisation.
- **A3** : regrouper dans un tableau “Local vs TrueNAS” :
  - init automatique (oui/non),
  - ports exposés,
  - gestion du `.env`,
  - commandes d’amorçage.

---

### Conclusion

L’environnement MSPR 502 présente un niveau de maturité **solide** pour un contexte projet/équipe :
- **Reproductibilité** : bonne en local via Docker Compose et `.env`, avec une variante serveur maîtrisée mais plus manuelle.
- **Robustesse au démarrage** : bonne, grâce aux healthchecks et au démarrage conditionnel de l’API.
- **Documentation opérationnelle** : déjà complète sur les aspects démarrage + init + API, avec quelques améliorations possibles orientées exploitation et dépannage.

