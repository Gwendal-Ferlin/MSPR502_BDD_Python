# HealthAI Coach API – Liste des endpoints

Base URL : `http://localhost:8000` (ou l’URL de ton déploiement).

**Authentification** : toutes les routes sauf celles marquées "Public" exigent le header :
```http
Authorization: Bearer <access_token>
```
Token obtenu via **POST /api/auth/login**.

**Logging admin** : lorsqu’un Admin ou Super-Admin consulte des données personnelles qui ne sont pas les siennes, une entrée est enregistrée en base (collection `evenements`, action `consultation_donnees_tiers`). Les routes concernées sont indiquées par la colonne **Logué** (oui/non).

---

## Racine et santé

| Méthode | Chemin | Auth | Logué | Description |
|--------|--------|------|-------|-------------|
| GET | `/` | Public | Non | Message d’accueil et lien vers la doc. |
| GET | `/health` | Public | Non | Healthcheck (retourne `{"status": "ok"}`). |

---

## Auth

| Méthode | Chemin | Auth | Logué | Description |
|--------|--------|------|-------|-------------|
| POST | `/api/auth/login` | Public | Non | Connexion avec email et mot de passe. Vérifie les identifiants, récupère l’`id_anonyme` (vault), renvoie un JWT. **Body** : `{"email": "...", "password": "..."}`. **Réponse** : `access_token`, `token_type`, `expires_in`. |

---

## Utilisateurs

Toutes les routes ci‑dessous exigent un token valide.

| Méthode | Chemin | Rôle | Logué | Description |
|--------|--------|------|-------|-------------|
| GET | `/api/utilisateurs` | Admin, Super-Admin | **Oui** | Liste tous les comptes (id_user, email, role, type_abonnement, date_consentement_rgpd). Pas de mot de passe. Consultation liste complète = logué. |
| GET | `/api/utilisateurs/{id_user}` | Tous | **Oui** si admin consulte un autre `id_user` | Détail d’un compte par `id_user`. Un **Client** ne peut accéder qu’à son propre `id_user`, sinon 403. |
| GET | `/api/utilisateurs/{id_user}/vault` | Tous | **Oui** si admin consulte un autre `id_user` | Récupère la ligne vault (id_anonyme, date_derniere_activite, consentement_sante_actif) pour l’utilisateur donné. Même règle d’accès : Client = uniquement son compte. |
| GET | `/api/utilisateurs/vault/{id_anonyme}` | Tous | **Oui** si admin consulte un autre `id_anonyme` | Récupère la ligne vault par UUID `id_anonyme`. Client = uniquement son propre `id_anonyme`. |

---

## Santé

Toutes les routes exigent un token. Pour un **Client**, les données sont limitées à son `id_anonyme` (celui du token). **Admin / Super-Admin** peuvent interroger n’importe quel `id_anonyme` via les query params quand c’est proposé.

| Méthode | Chemin | Query params | Logué | Description |
|--------|--------|--------------|-------|-------------|
| GET | `/api/sante/profils` | `id_anonyme` (optionnel, UUID) | **Oui** si admin consulte un tiers ou liste complète | Liste les profils santé. Sans paramètre (Admin) = tous ; avec `id_anonyme` ou implicite (Client) = filtré. |
| GET | `/api/sante/objectifs` | `id_anonyme` (optionnel, UUID) | **Oui** si admin consulte un tiers ou liste complète | Liste les objectifs utilisateur. Même logique de filtrage. |
| GET | `/api/sante/journal` | `id_anonyme` (optionnel, UUID) | **Oui** si admin consulte un autre `id_anonyme` | Liste le journal alimentaire (repas) pour un `id_anonyme`. Client = forcément le sien. Tri par date décroissante. |
| GET | `/api/sante/seances` | `id_anonyme` (optionnel, UUID) | **Oui** si admin consulte un autre `id_anonyme` | Liste les séances d’activité. Même règle. Tri par date décroissante. |
| GET | `/api/sante/referentiels/restrictions` | — | Non | Liste le référentiel des restrictions (nom, type). |
| GET | `/api/sante/referentiels/exercices` | — | Non | Liste le référentiel des exercices (nom, muscle_principal). |
| GET | `/api/sante/referentiels/materiel` | — | Non | Liste le référentiel du matériel. |

---

## Logs

| Méthode | Chemin | Auth | Logué | Description |
|--------|--------|------|-------|-------------|
| GET | `/api/logs/evenements` | Oui | **Oui** si admin filtre par un `id_anonyme` tiers | Liste les événements (logs). **Client** : uniquement ses événements (`id_anonyme` du token). **Admin/Super-Admin** : tous, avec filtre optionnel. **Query** : `id_anonyme` (optionnel), `action` (optionnel). Limite 100, tri par timestamp décroissant. |
| POST | `/api/logs/evenements` | Oui | Non | Crée un événement. **Body** : `id_anonyme`, `action`, `details_techniques` (optionnel). Pour un **Client**, `id_anonyme` est ignoré et remplacé par celui du token. **Réponse** : 201 + `id_log`, message. |
| GET | `/api/logs/config` | Public | Non | Liste toutes les entrées de config globale (cle, valeur, description). |
| GET | `/api/logs/config/{cle}` | Public | Non | Récupère une entrée de config par sa clé. 200 ou valeur nulle si absent. |

---

## Recommandations

| Méthode | Chemin | Auth | Logué | Description |
|--------|--------|------|-------|-------------|
| GET | `/api/reco/recommendations` | Oui | **Oui** si admin filtre par un `id_anonyme` tiers | Liste les recommandations. **Client** : uniquement les siennes. **Admin/Super-Admin** : tous, avec filtre optionnel. **Query** : `id_anonyme` (optionnel), `type` (optionnel, ex. "nutrition", "activite"). Limite 50, tri par `created_at` décroissant. |

---

## Récapitulatif par préfixe

- **/** : racine, health (publics).
- **/api/auth** : login (public).
- **/api/utilisateurs** : comptes et vault (token + règles par rôle).
- **/api/sante** : profils, objectifs, journal, séances, référentiels (token + id_anonyme selon rôle).
- **/api/logs** : evenements (token + id_anonyme selon rôle), config (public).
- **/api/reco** : recommendations (token + id_anonyme selon rôle).

Documentation interactive (Swagger) : **GET** `/docs`.

---

## Détail du logging admin

Quand une route est **Logué = Oui** et qu’un Admin/Super-Admin consulte des données qui ne sont pas les siennes, un événement est enregistré dans la collection **evenements** (MongoDB, base `logs_config`) avec :

- **action** : `consultation_donnees_tiers`
- **id_anonyme** : celui de l’admin qui consulte
- **details_techniques** : `endpoint`, `role_acteur`, `id_user_acteur`, et selon le cas `id_anonyme_cible`, `id_user_cible` ou `liste_complete`

La consultation par un admin de **ses propres** données (même `id_user` ou `id_anonyme`) n’est pas loguée.
