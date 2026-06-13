# Metabase — Dashboard HealthAI Coach (MSPR 502)

Guide pour lancer Metabase, connecter les mêmes données que l’API, et construire un dashboard détaillé.

---

## 0. Guide pas à pas — tu es perdu, commence ici

Tu as déjà connecté tes bases (capture d’écran : **MSPR502 - Santé**, **User**, **Gamification**, **MongoDB Logs/Reco**). Parfait. La suite :

### Vocabulaire Metabase (3 mots à retenir)

| Mot Metabase | C’est quoi ? | Exemple |
|--------------|--------------|---------|
| **Question** | Un graphique ou un tableau (= une requête) | « Nombre de séances par mois » |
| **Dashboard** | Une page qui regroupe plusieurs questions | « Dashboard Sport HealthAI » |
| **Collection** | Un dossier pour ranger questions et dashboards | « MSPR 502 » |

**Ordre logique :** d’abord créer des **questions** une par une → puis les assembler dans un **dashboard**.

---

### Étape A — Ta première question (5 minutes)

Tu es sur l’écran **« Nouvelle question »** avec le menu **« Sélectionner une base de données »** ouvert.

#### A1. Choisir la base

Clique sur **`MSPR502 - Santé`**.

> C’est la base `sante_db` : séances, performances, nutrition, exercices.  
> Ne prends pas « Sample Database » (données de démo Metabase, sans lien avec ton projet).

#### A2. Choisir le mode SQL (recommandé pour ton projet)

En haut à droite de la zone de requête, tu vois des icônes. Clique sur **`{=}`** (requête SQL native).

Tu obtiens un éditeur de texte SQL au lieu du mode visuel « cliquer sur les tables ».

> **Pourquoi SQL ?** Ton dashboard croise `seance_activite` + `detail_performance` + `ref_exercice`. Ce croisement est plus simple en SQL qu’en mode visuel.

#### A3. Coller ta première requête

Copie-colle ceci dans l’éditeur :

```sql
SELECT
  id_anonyme,
  COUNT(*) AS nb_seances
FROM seance_activite
GROUP BY id_anonyme
ORDER BY nb_seances DESC;
```

#### A4. Lancer la requête

Clique le bouton bleu **« Visualiser »** (en bas à droite) ou appuie sur **Ctrl+Entrée**.

Tu dois voir un **tableau** avec 4 lignes (tes 4 utilisateurs) et le nombre de séances de chacun. Si c’est vide → voir section 8 (dépannage).

#### A5. Choisir le type de graphique

Sous la requête, Metabase propose des icônes de visualisation :

1. Clique l’icône **camembert** (Pie chart)
2. **Dimension** : `id_anonyme`
3. **Mesure** : `nb_seances`

Tu obtiens un camembert « qui fait le plus de séances ».

#### A6. Sauvegarder la question

1. Clique **« Sauvegarder »** (en haut à droite — devient actif après la visualisation)
2. Nom : `Séances par utilisateur`
3. Collection : crée **`MSPR 502`** si elle n’existe pas
4. Valide

**Bravo : tu as ta première question sauvegardée.**

---

### Étape B — Question la plus utile (séances + performances)

Recommence : **+ Nouveau → Question → MSPR502 - Santé → icône `{=}` SQL**.

Colle :

```sql
SELECT
  s.horodatage::date AS jour,
  s.nom_seance,
  s.ressenti_effort_rpe AS rpe,
  e.nom AS exercice,
  d.series,
  d.reps,
  d.charge_kg
FROM seance_activite s
JOIN detail_performance d ON d.id_seance = s.id_seance
JOIN ref_exercice e ON e.id_exercice = d.id_exercice
ORDER BY s.horodatage DESC
LIMIT 100;
```

- **Visualiser** → garde le type **Tableau**
- **Sauvegarder** sous le nom : `Détail séances & exercices`

C’est la même donnée que l’API pourrait exposer, mais aujourd’hui **seules les séances** sont dans l’API (`GET /api/sante/seances`), pas le détail exercice par exercice.

---

### Étape C — Créer ton premier dashboard

1. Menu **+ Nouveau → Dashboard**
2. Nom : `HealthAI Coach — Sport`
3. Tu arrives sur une page vide avec **« Ajouter un graphique »**

Pour chaque question sauvegardée :

1. Clique **« Ajouter un graphique »** (ou **« Ajouter une question existante »**)
2. Cherche `Séances par utilisateur` → Ajouter
3. Recommence pour `Détail séances & exercices`
4. **Redimensionne** les cartes en tirant les coins
5. Clique **« Sauvegarder »** en haut

Tu as un dashboard fonctionnel.

---

### Étape D — Lire les `id_anonyme` (sinon tu ne comprends rien)

Metabase affiche des UUID, pas « Marie » ou « Lucas ». Table de correspondance :

| Utilisateur | `id_anonyme` (copier-coller pour filtrer) |
|-------------|-------------------------------------------|
| Marie | `a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11` |
| Lucas | `b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22` |
| Léa | `c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33` |
| Thomas | `d3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44` |

Pour filtrer une question sur Marie, ajoute en SQL :

```sql
WHERE s.id_anonyme = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
```

Ou sur le dashboard : **icône filtre** → champ `id_anonyme` → lier aux cartes.

---

### Étape E — Mode visuel (sans SQL) : quand l’utiliser

Si tu préfères ne pas écrire de SQL :

1. **+ Nouveau → Question**
2. Base : **MSPR502 - Santé**
3. Ne clique **pas** sur `{=}` — reste en mode notebook (icône cahier)
4. Clique **« Sélectionner une table »** → choisis `seance_activite`
5. Metabase affiche un aperçu des colonnes : `id_seance`, `id_anonyme`, `horodatage`, `nom_seance`, `ressenti_effort_rpe`
6. Clique **« Synthèse »** (Summarize) → **Count of rows** → groupe par **`id_anonyme`**

C’est l’équivalent visuel de l’étape A. Limite : difficile de joindre 3 tables (`seance` + `detail` + `exercice`) sans SQL.

---

### Étape F — Ordre recommandé pour tout le dashboard

Fais les questions dans cet ordre (base **Santé** sauf mention) :

| # | Nom de la question | Type graphique | SQL / table |
|---|------------------|----------------|-------------|
| 1 | Séances par utilisateur | Camembert | Étape A |
| 2 | Détail séances & exercices | Tableau | Étape B |
| 3 | Séances par mois | Courbe | Section 5.2 |
| 4 | Top exercices | Barres horizontales | Section 5.3 |
| 5 | Calories par jour | Courbe | Section 5.4 |
| 6 | Objectifs en cours | Tableau | table `objectif_utilisateur`, filtre `statut = 'En cours'` |

Puis base **Gamification** :

| # | Nom | Type | Table |
|---|-----|------|-------|
| 7 | Transactions par type | Barres | `gamification_transactions` |

Puis **MongoDB Logs** (mode visuel sur collection `evenements`) :

| # | Nom | Type |
|---|-----|------|
| 8 | Événements par action | Barres |

Ensuite : **un dashboard** qui regroupe 1–4 (sport), un second pour 5–6 (nutrition), etc.

---

### Étape G — Lier Metabase et l’API (comprendre la différence)

```
Utilisateur Marie ouvre l'app
        │
        ▼
   API + JWT  ──►  voit SEULEMENT ses séances (filtré par id_anonyme)
        │
Toi dans Metabase
        │
        ▼
   SQL direct  ──►  vois TOUT le monde (vue admin / analyste)
```

**Test rapide API** (Swagger : `http://<IP>:18000/docs`) :

1. `POST /api/auth/login` avec `{"email":"a@a.fr","password":"password"}`
2. Copie le `access_token`
3. `GET /api/sante/seances?id_anonyme=a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11` avec header `Authorization: Bearer <token>`
4. Compare le nombre de lignes avec ta question Metabase filtrée sur le même UUID

---

### Écran « Nouvelle question » — rappel visuel

```
┌─────────────────────────────────────────────────────────────┐
│  Nouvelle question                              [Sauvegarder]│
├─────────────────────────────────────────────────────────────┤
│  [MSPR502 - Santé ▼]     ← tu choisis ça                    │
│                                                              │
│  ┌─ mode visuel ─┐  ┌─ {x} ─┐  ┌─ {=} SQL ← clique ici    │
│                                                              │
│  SELECT ...                                                  │
│                                                              │
│                              [Visualiser]  ← puis clique    │
├─────────────────────────────────────────────────────────────┤
│  (graphique ou tableau apparaît ici)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Architecture : Metabase et l’API

L’API FastAPI (**port 18000**) et Metabase (**port 13000**) lisent les **mêmes bases** :

| Source | Conteneur Docker | Port hôte | Rôle |
|--------|------------------|-----------|------|
| Postgres Utilisateur | `postgres-utilisateur` | 15432 | Comptes, vault (`id_anonyme`) |
| Postgres Santé | `postgres-sante` | 15433 | Profils, séances, nutrition, performances |
| Postgres Gamification | `postgres-gamification` | 15434 | Animaux, monnaie, transactions |
| MongoDB Logs | `mongodb-logs` | 27017 | Événements (`evenements`) |
| MongoDB Reco | `mongodb-reco` | 27018 | Recommandations, repas IA |

```
┌─────────────┐     JWT      ┌──────────────┐
│   Client    │ ──────────►  │  API :18000  │
└─────────────┘              └──────┬───────┘
                                    │ SQL / Mongo
┌─────────────┐   SQL direct        │
│  Metabase   │ ────────────────────┤
│   :13000    │                     ▼
└─────────────┘              ┌──────────────┐
                             │  Bases BDD   │
                             └──────────────┘
```

**Différence clé :**

- **API** : données filtrées par utilisateur (JWT), champs chiffrés déchiffrés, pas d’endpoint pour `detail_performance` aujourd’hui.
- **Metabase** : accès SQL direct (vue admin/analyste), idéal pour croiser séances + performances + nutrition + logs.

Utilise les deux : l’API pour valider ce que voit un client ; Metabase pour l’analyse globale.

---

## 2. Démarrer Metabase

### Lancer le service

```bash
docker compose up -d metabase
```

Vérifier :

```bash
docker compose ps metabase
docker logs metabase --tail 30
```

### Accès

- Local : **http://localhost:13000**
- TrueNAS : **http://<IP-TRUENAS>:13000**

### Configuration initiale (première visite)

1. Langue : Français
2. Créer le compte admin Metabase (email + mot de passe **Metabase**, distinct des comptes API)
3. **Ajouter vos données** → on configure les bases à l’étape 3
4. Préférences → ignorer ou configurer plus tard

### Variable d’environnement (TrueNAS)

Dans le `.env` à la racine du projet :

```env
METABASE_SITE_URL=http://192.168.1.150:13000
```

Puis :

```bash
docker compose up -d metabase
```

---

## 3. Connecter les bases de données

Dans Metabase : **⚙️ Admin → Bases de données → Ajouter une base de données**.

Depuis le réseau Docker, utilise les **noms de conteneurs** (pas `localhost`).

### 3.1 Postgres Santé (prioritaire)

| Champ | Valeur |
|-------|--------|
| Type | PostgreSQL |
| Nom affiché | `MSPR502 - Santé` |
| Hôte | `postgres-sante` |
| Port | `5432` |
| Base | `sante_db` |
| Utilisateur | `sante_user` |
| Mot de passe | `sante_password` |

Tables utiles : `seance_activite`, `detail_performance`, `ref_exercice`, `journal_alimentaire`, `suivi_biometrique`, `objectif_utilisateur`, `profil_sante`, `materiel`.

### 3.2 Postgres Utilisateur

| Champ | Valeur |
|-------|--------|
| Hôte | `postgres-utilisateur` |
| Base | `utilisateur_db` |
| Utilisateur | `utilisateur_user` |
| Mot de passe | `utilisateur_password` |

Tables : `compte_utilisateur`, `vault_correspondance`.

> Les emails / profils chiffrés (Fernet) apparaissent **chiffrés** dans Metabase. Pour l’analyse, joins via `vault_correspondance.id_anonyme`.

### 3.3 Postgres Gamification

| Champ | Valeur |
|-------|--------|
| Hôte | `postgres-gamification` |
| Base | `gamification_db` |
| Utilisateur | `gamification_user` |
| Mot de passe | `gamification_password` |

Tables : `gamification_user_currency`, `gamification_transactions`, `gamification_user_inventory`.

### 3.4 MongoDB Logs

| Champ | Valeur |
|-------|--------|
| Type | MongoDB |
| Hôte | `mongodb-logs` |
| Port | `27017` |
| Base | `logs_config` |
| Auth | aucune (compose dev) |

Collection : `evenements`.

### 3.5 MongoDB Reco

| Champ | Valeur |
|-------|--------|
| Hôte | `mongodb-reco` |
| Port | `27017` |
| Base | `reco` |

Collections : `recommendations`, `repas`.

---

## 4. Correspondance API ↔ tables Metabase

| Endpoint API | Méthode | Table / collection Metabase | Notes |
|--------------|---------|----------------------------|-------|
| `/api/auth/login` | POST | — | Obtenir un JWT pour tester l’API |
| `/api/sante/seances` | GET | `seance_activite` | API = 1 utilisateur ; Metabase = tous |
| `/api/sante/journal` | GET | `journal_alimentaire` | Idem |
| `/api/sante/suivi-biometrique` | GET | `suivi_biometrique` | Poids chiffré en base si `DATA_ENCRYPTION_KEY` actif |
| `/api/sante/objectifs` | GET | `objectif_utilisateur` | |
| `/api/sante/profils` | GET | `profil_sante` | |
| `/api/sante/referentiels/exercices` | GET | `ref_exercice` | |
| `/api/journal` (POST) | POST | `journal_alimentaire` | Écriture via API uniquement |
| `/api/logs/evenements` | GET | `logs_config.evenements` | |
| `/api/reco/recommendations` | GET | `reco.recommendations` | |
| *(pas d’endpoint)* | — | `detail_performance` | **Metabase uniquement** pour l’instant |

### Comptes de test API (mot de passe : `password`)

| Email | Rôle | `id_anonyme` |
|-------|------|----------------|
| `marie.dupont@email.fr` | Client | `a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11` |
| `c@c.fr` | Client | `b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22` |
| `a@a.fr` | Admin | `c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33` |
| `sa@sa.fr` | Super-Admin | `d3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44` |

### Vérifier l’API vs Metabase

```bash
# 1) Login
curl -s -X POST http://localhost:18000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"a@a.fr","password":"password"}' | jq .

# 2) Séances Marie (admin)
TOKEN="<access_token>"
curl -s "http://localhost:18000/api/sante/seances?id_anonyme=a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

Compare le nombre de lignes avec une question Metabase SQL sur `seance_activite` filtrée par le même `id_anonyme`.

---

## 5. Créer des questions (SQL)

Metabase : **+ Nouveau → Question SQL**.

### 5.1 Vue séances + performances (cœur du dashboard sport)

```sql
SELECT
  s.id_seance,
  s.id_anonyme,
  s.horodatage::date AS jour,
  s.nom_seance,
  s.ressenti_effort_rpe AS rpe,
  e.nom AS exercice,
  e.muscle_principal,
  d.series,
  d.reps,
  d.charge_kg,
  (d.series * d.reps * COALESCE(d.charge_kg, 0)) AS volume_kg
FROM seance_activite s
JOIN detail_performance d ON d.id_seance = s.id_seance
JOIN ref_exercice e ON e.id_exercice = d.id_exercice
ORDER BY s.horodatage DESC;
```

Enregistrer sous : **« Détail séances & performances »**.

### 5.2 Séances par utilisateur et par mois

> Pour une **courbe** ou un **tableau** — pas pour une jauge (trop de lignes).

```sql
SELECT
  id_anonyme,
  date_trunc('month', horodatage) AS mois,
  COUNT(*) AS nb_seances,
  ROUND(AVG(ressenti_effort_rpe)::numeric, 1) AS rpe_moyen
FROM seance_activite
GROUP BY id_anonyme, date_trunc('month', horodatage)
ORDER BY mois DESC, COUNT(*) DESC
```

Graphique : **courbe** — X = `mois`, Y = `nb_seances` (ou tableau).

### 5.2b RPE moyen global (jauge — 1 seul chiffre)

> **Erreur « La visualisation par jauge nécessite un nombre » ?**  
> La requête 5.2 renvoie **plusieurs lignes**. Pour une jauge, il faut **une question séparée** qui ne renvoie **qu’un seul nombre**.

Base **`MSPR502 - Santé`**, mode `{=}` SQL :

```sql
SELECT ROUND(AVG(ressenti_effort_rpe)::numeric, 1) AS rpe_moyen
FROM seance_activite
```

1. **Visualiser** → type **Jauge** (gauge)
2. Metabase prend la colonne **`rpe_moyen`** automatiquement
3. Options jauge (panneau gauche) — exemple :
   - Min : **1**, Max : **10**
   - Vert : 1 → 3 (Facile)
   - Bleu : 4 → 5
   - Jaune : 6 → 7 (Modéré)
   - Orange : 8 → 9
   - Rouge : 10 → 10 (Maximal)
4. **Sauvegarder** → `RPE moyen global`

**RPE moyen pour un seul utilisateur** (avec filtre dashboard sur `id_anonyme`) :

```sql
SELECT ROUND(AVG(ressenti_effort_rpe)::numeric, 1) AS rpe_moyen
FROM seance_activite
WHERE id_anonyme = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
```

Ou ajoute un **filtre dashboard** sur la question globale : champ `id_anonyme` lié à la carte jauge.

### 5.3 Top exercices (volume total)

> **Metabase :** ne mets **pas** de `;` à la fin de la requête. Utilise `ORDER BY` sur l’expression, pas sur l’alias.

```sql
SELECT
  e.nom AS exercice,
  e.muscle_principal,
  COUNT(*) AS nb_series_enregistrees,
  SUM(d.series * d.reps) AS reps_totales,
  ROUND(AVG(d.charge_kg)::numeric, 1) AS charge_moyenne_kg
FROM detail_performance d
JOIN ref_exercice e ON e.id_exercice = d.id_exercice
GROUP BY e.id_exercice, e.nom, e.muscle_principal
ORDER BY SUM(d.series * d.reps) DESC
LIMIT 15
```

### 5.4 Nutrition — calories par jour

> **Courbe (onglet 2.1)** : trie par date **croissante** et une **série par utilisateur**, sinon Metabase relie les points dans le mauvais ordre (ligne diagonale) ou additionne mal.

```sql
SELECT
  CASE id_anonyme::text
    WHEN 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' THEN 'Marie'
    WHEN 'b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22' THEN 'Lucas'
    WHEN 'c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33' THEN 'Lea'
    WHEN 'd3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44' THEN 'Thomas'
    ELSE id_anonyme::text
  END AS utilisateur,
  horodatage::date AS jour,
  SUM(total_calories) AS calories_jour
FROM journal_alimentaire
GROUP BY id_anonyme, horodatage::date
ORDER BY jour ASC
```

**Visualisation Metabase :**

1. Type **Courbe** (line chart)
2. **Axe X** : `jour`
3. **Axe Y** : `calories_jour`
4. **Série / Répartition** : `utilisateur` (1 ligne par personne)

**Données seed** : seulement quelques repas en **fév. 2025** → courbe **creuse** avec 2–3 points, c’est normal. Pas de données tous les jours.

**Une seule personne** (ex. Marie, ~1520 kcal/jour max au 8 fév.) :

```sql
SELECT
  horodatage::date AS jour,
  SUM(total_calories) AS calories_jour
FROM journal_alimentaire
WHERE id_anonyme = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
GROUP BY horodatage::date
ORDER BY jour ASC
```

**Icône ⚠️ en haut à droite** : clique dessus — souvent « limite de lignes » ou agrégation en double. Vérifie qu’il n’y a pas **Sum of calories_jour** en plus du SUM SQL.

### 5.5 Séances par utilisateur (avec noms lisibles)

> **Erreur `seance_activite does not exist` ?**  
> Tu es sur la mauvaise base Metabase. `seance_activite` est **uniquement** dans **`MSPR502 - Santé`**.  
> `vault_correspondance` est **uniquement** dans **`MSPR502 - User`**.  
> Vérifie le nom affiché en haut à gauche de la question **avant** de cliquer Visualiser.

**Test rapide (base Santé obligatoire) :**

```sql
SELECT COUNT(*) AS nb FROM seance_activite
```

Si ça échoue → mauvaise base sélectionnée, ou schéma pas initialisé (`01_schema.sql`).

---

**Question A — choisir la base `MSPR502 - Santé` en haut à gauche**

```sql
SELECT
  CASE id_anonyme::text
    WHEN 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' THEN 'Marie'
    WHEN 'b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22' THEN 'Lucas'
    WHEN 'c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33' THEN 'Lea'
    WHEN 'd3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44' THEN 'Thomas'
    ELSE id_anonyme::text
  END AS utilisateur,
  COUNT(*) AS nb_seances,
  ROUND(AVG(ressenti_effort_rpe)::numeric, 1) AS rpe_moyen
FROM seance_activite
GROUP BY id_anonyme
ORDER BY nb_seances DESC
```

Graphique : **barres** — Y = `utilisateur`, X = `nb_seances`.

---

**Question B — nouvelle question, base `MSPR502 - User` en haut à gauche**

```sql
SELECT
  v.id_anonyme,
  c.email,
  c.role,
  c.type_abonnement
FROM vault_correspondance v
JOIN compte_utilisateur c ON c.id_user = v.id_user
ORDER BY c.email
```

> Ne mélange **pas** les deux requêtes dans la même question. Deux questions séparées, deux bases différentes.

### 5.6 Logs admin (MongoDB)

Ici c’est **MongoDB**, pas du SQL Postgres. Pas d’icône `{=}` SQL : tu restes en **mode visuel** (icône cahier).

#### Question A — Événements par type d’action (graphique barres)

1. **+ Nouveau → Question**
2. En haut à gauche : **`MongoDB Logs`** (pas Santé, pas User)
3. **Ne clique pas** sur `{=}` — reste en mode notebook
4. Clique **« Pick a collection »** / **« Choisir une collection »** → **`evenements`**
5. Tu vois un aperçu : colonnes `id_log`, `timestamp`, `id_anonyme`, `action`, `details_techniques`
6. Clique **« Synthèse »** / **Summarize** (en haut au centre)
7. **Métrique** : `Nombre de lignes` / **Count of rows**
8. **Grouper par** : **`action`**
9. **Visualiser** → choisis **Barres** (bar chart)
   - Axe X : `action`
   - Y : count
10. **Sauvegarder** → nom : `Logs — événements par action`

Tu devrais voir des barres comme `connexion`, `consultation_journal`, `ajout_seance`, etc. (données du seed `init/mongodb-logs/init.js`).

#### Question B — Tableau des derniers logs

1. Nouvelle question → **`MongoDB Logs`** → collection **`evenements`**
2. Ne fais **pas** de synthèse — garde la vue **Tableau** / raw
3. Trie par **`timestamp`** décroissant (clic sur l’en-tête de colonne ou option Trier)
4. **Sauvegarder** → nom : `Logs — derniers événements`

#### Question C — Filtre « consultations admin » (optionnel)

L’API enregistre `consultation_donnees_tiers` quand un **Admin** consulte les données d’un autre user.  
Le seed de démo n’en contient **pas** encore : le graphique sera vide tant qu’un admin n’a pas appelé l’API (ex. `GET /api/sante/seances?id_anonyme=...` avec un token admin).

Pour filtrer quand même :

1. Sur la question A ou B, clique **Filtrer** / **Filter**
2. Colonne **`action`**
3. Opérateur **est égal à** → `consultation_donnees_tiers`
4. Sauvegarder sous : `Logs — consultations admin`

Pour **générer** des logs de test : connecte-toi en admin sur Swagger (`a@a.fr` / `password`) et consulte les séances d’un autre utilisateur.

#### Lien avec l’API

| Ce que tu vois dans Metabase | Endpoint API équivalent |
|------------------------------|-------------------------|
| Collection `evenements` | `GET /api/logs/evenements` |
| Champ `action` | même champ dans la réponse JSON |
| `consultation_donnees_tiers` | log auto quand admin consulte un tiers |

#### Si la collection est vide

```bash
docker cp init/mongodb-logs/init.js mongodb-logs:/tmp/
docker exec mongodb-logs mongosh logs_config --file /tmp/init.js
```

Puis dans Metabase : **⚙️ Admin → Bases de données → MongoDB Logs → Sync database schema now**.

### 5.7 Gamification — économie

```sql
SELECT
  transaction_type,
  COUNT(*) AS nb,
  SUM(amount) AS montant_total
FROM gamification_transactions
GROUP BY transaction_type
ORDER BY SUM(amount) DESC
```

---

## 6. Construire le dashboard détaillé

**+ Nouveau → Dashboard** → nom : **« HealthAI Coach — Vue globale »**.

### Onglet 1 — Activité physique

| Carte | Type | Source |
|-------|------|--------|
| Séances ce mois | Nombre | **Section 6.1.1** |
| RPE moyen | Jauge 1–10 | **Question 5.2b** (pas 5.2) |
| Évolution séances / mois | Courbe | Question 5.2 |
| Répartition par utilisateur | Camembert | **Section 6.1.4** (ou question « Séances par utilisateur ») |
| Détail dernières séances | Table | Question 5.1, limite 50 lignes |
| Top exercices | Barres horizontales | Question 5.3 |

**Filtre dashboard** : ajoute un filtre **« id_anonyme »** (champ texte ou liste) lié aux cartes sport.

#### 6.1.1 Nombre — séances ce mois

> Carte **Nombre** = **1 seul chiffre** (comme la jauge RPE). Ne pas utiliser la requête 5.2 telle quelle (plusieurs lignes).

1. **+ Nouveau → Question**
2. Base **`MSPR502 - Santé`** → **`{=}`** SQL
3. Colle (sans `;`) :

```sql
SELECT COUNT(*) AS nb_seances_ce_mois
FROM seance_activite
WHERE horodatage >= date_trunc('month', CURRENT_DATE)
  AND horodatage < date_trunc('month', CURRENT_DATE) + INTERVAL '1 month'
```

4. **Visualiser** → type **Nombre** (icône « 123 » / Number / Scalar)
5. Metabase affiche la colonne **`nb_seances_ce_mois`**
6. Options (panneau gauche) :
   - **Style** : nombre simple
   - **Libellé** (optionnel) : `Séances ce mois`
7. **Sauvegarder** → `Séances ce mois`
8. Dashboard → **Ajouter une question existante**

**Tous les utilisateurs confondus** — c’est le total global du mois en cours.

**Un seul utilisateur** (ex. Marie) :

```sql
SELECT COUNT(*) AS nb_seances_ce_mois
FROM seance_activite
WHERE horodatage >= date_trunc('month', CURRENT_DATE)
  AND horodatage < date_trunc('month', CURRENT_DATE) + INTERVAL '1 month'
  AND id_anonyme = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
```

**Avec filtre dashboard** : garde la première requête (sans `WHERE id_anonyme`), puis sur le dashboard → **icône filtre** → ajoute un filtre **`id_anonyme`** → lie-le à cette carte.

**Si le nombre affiche 0** : normal si aucune séance n’a été enregistrée **ce mois-ci** (juin 2026). Les seeds datent surtout de 2024–2025. Pour tester, remplace temporairement le filtre date par :

```sql
SELECT COUNT(*) AS nb_seances_ce_mois
FROM seance_activite
WHERE horodatage >= date_trunc('month', TIMESTAMP '2024-07-01')
  AND horodatage < date_trunc('month', TIMESTAMP '2024-07-01') + INTERVAL '1 month'
```

Tu devrais voir un chiffre > 0 en juillet 2024.

#### 6.1.4 Camembert — répartition des séances par utilisateur

1. **+ Nouveau → Question**
2. Base **`MSPR502 - Santé`** → icône **`{=}`** SQL
3. Colle (sans `;` à la fin) :

```sql
SELECT
  CASE id_anonyme::text
    WHEN 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' THEN 'Marie'
    WHEN 'b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22' THEN 'Lucas'
    WHEN 'c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33' THEN 'Lea'
    WHEN 'd3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44' THEN 'Thomas'
    ELSE id_anonyme::text
  END AS utilisateur,
  COUNT(*) AS nb_seances
FROM seance_activite
GROUP BY id_anonyme
ORDER BY COUNT(*) DESC
```

4. **Visualiser**
5. Clique l’icône **Camembert** (pie chart) sous le graphique
6. **Dimension** (tranche) : **`utilisateur`**
7. **Mesure** (taille) : **`nb_seances`**
8. **Sauvegarder** → `Camembert — séances par utilisateur`
9. Sur le dashboard : **Ajouter une question existante** → choisis cette question

> Si tu as déjà la question **« Séances par utilisateur »** (étape A) avec les UUID, tu peux la réutiliser : camembert, dimension = `id_anonyme`, mesure = `nb_seances`. Les prénoms (requête ci-dessus) sont plus lisibles sur le dashboard.

### Onglet 2 — Nutrition

| Carte | Type | Source |
|-------|------|--------|
| Calories / jour | Courbe | Question 5.4 |
| Macros moyennes | Barres empilées | `journal_alimentaire` |
| Repas récents | Table | **Section 6.2.3** |

#### 6.2.3 Table — repas récents

1. **+ Nouveau → Question**
2. Base **`MSPR502 - Santé`** → **`{=}`** SQL
3. Colle (sans `;`) :

```sql
SELECT
  CASE id_anonyme::text
    WHEN 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' THEN 'Marie'
    WHEN 'b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22' THEN 'Lucas'
    WHEN 'c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33' THEN 'Lea'
    WHEN 'd3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44' THEN 'Thomas'
    ELSE id_anonyme::text
  END AS utilisateur,
  horodatage,
  nom_repas,
  type_repas,
  total_calories,
  total_proteines,
  total_glucides,
  total_lipides
FROM journal_alimentaire
ORDER BY horodatage DESC
LIMIT 50
```

4. **Visualiser** → type **Table** (icône grille — 1re option)
5. **Sauvegarder** → `Repas récents`
6. Dashboard nutrition → **Ajouter une question existante**

Équivalent API : `GET /api/sante/journal` (même table, filtré par JWT côté API).

**Filtrer un utilisateur** sur le dashboard : filtre **`utilisateur`** ou **`id_anonyme`**.


**Validation API** : pour un client, `GET /api/sante/journal` doit correspondre au filtre Metabase sur son `id_anonyme`.

### Onglet 3 — Suivi & objectifs

| Carte | Type | Source |
|-------|------|--------|
| Objectifs actifs | Table | **Section 6.3.1** |
| Relevés biométriques | Courbe ou Table | **Section 6.3.2** |

#### 6.3.1 Table — objectifs actifs

Base **`MSPR502 - Santé`**, SQL (sans `;`) :

```sql
SELECT
  CASE id_anonyme::text
    WHEN 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' THEN 'Marie'
    WHEN 'b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22' THEN 'Lucas'
    WHEN 'c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33' THEN 'Lea'
    WHEN 'd3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44' THEN 'Thomas'
    ELSE id_anonyme::text
  END AS utilisateur,
  type_objectif,
  valeur_cible,
  unite,
  date_debut,
  date_fin,
  statut
FROM objectif_utilisateur
WHERE statut = 'En cours'
ORDER BY date_debut DESC
```

**Visualiser** → **Table** → **Sauvegarder** → `Objectifs actifs`

Équivalent API : `GET /api/sante/objectifs`

Tu devrais voir **4 objectifs** (Marie ×2, Lucas, Léa).

---

#### 6.3.2 Relevés biométriques

> **Attention :** `poids_kg` et `score_sommeil` sont **chiffrés** (Fernet) en base. Metabase affiche des chaînes illisibles — pas une courbe de poids exploitable. L’API les déchiffre (`GET /api/sante/suivi-biometrique`).

**Option A — Table des dates** (utile pour voir *quand* un relevé a été fait) :

```sql
SELECT
  CASE id_anonyme::text
    WHEN 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' THEN 'Marie'
    WHEN 'b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22' THEN 'Lucas'
    WHEN 'c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33' THEN 'Lea'
    WHEN 'd3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44' THEN 'Thomas'
    ELSE id_anonyme::text
  END AS utilisateur,
  date_releve
FROM suivi_biometrique
ORDER BY date_releve DESC
```

**Table** → `Relevés biométriques — dates`

**Option B — Courbe « nombre de relevés »** (graphique qui a du sens dans Metabase) :

```sql
SELECT
  CASE id_anonyme::text
    WHEN 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' THEN 'Marie'
    WHEN 'b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22' THEN 'Lucas'
    WHEN 'c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33' THEN 'Lea'
    WHEN 'd3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44' THEN 'Thomas'
    ELSE id_anonyme::text
  END AS utilisateur,
  date_releve::date AS jour,
  COUNT(*) AS nb_releves
FROM suivi_biometrique
GROUP BY id_anonyme, date_releve::date
ORDER BY jour ASC
```

**Courbe** : X = `jour`, Y = `nb_releves`, Série = `utilisateur`

**Option C — Vérifier les vraies valeurs via l’API** (Swagger) :

1. Login admin → token  
2. `GET /api/sante/suivi-biometrique?id_anonyme=a0eebc99-...`  
3. Compare avec Metabase (dates OK, valeurs poids/sommeil seulement via API)

### Onglet 4 — Logs & conformité

Base **`MongoDB Logs`** uniquement — **pas de SQL** `{=}`.

| Carte | Type | Source |
|-------|------|--------|
| Événements par action | Histogramme | **Section 6.4.1** |
| Consultations admin (RGPD) | Table | **Section 6.4.2** |

#### 6.4.1 Histogramme — événements par action

1. **+ Nouveau → Question**
2. Base **`MongoDB Logs`** (en haut à gauche)
3. Mode **visuel** (icône cahier — **pas** `{=}`)
4. Collection **`evenements`**
5. **Résumer** (Summarize) :
   - Métrique : **Nombre de lignes**
   - Grouper par : **`action`**
6. **Visualiser** → **Histogramme** (barres verticales chez toi)
   - X : `action`
   - Y : count
7. **Sauvegarder** → `Logs — événements par action`

Résultat seed (~6 lignes) :

| action | nb |
|--------|-----|
| connexion | 3 |
| consultation_journal | 1 |
| ajout_seance | 1 |
| consultation_recommandations | 1 |

API : `GET /api/logs/evenements`

#### 6.4.2 Table — consultations admin (RGPD)

Les logs `consultation_donnees_tiers` n’existent **pas** dans le seed. Il faut d’abord en **générer** :

1. Swagger : http://`<IP>`:18000/docs  
2. `POST /api/auth/login` → `{"email":"a@a.fr","password":"password"}`  
3. Copie le `access_token`  
4. `GET /api/sante/seances?id_anonyme=a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11`  
   Header : `Authorization: Bearer <token>`

Puis dans Metabase :

1. **+ Nouveau → Question** → **`MongoDB Logs`** → **`evenements`**
2. **Filtrer** → `action` **est égal à** `consultation_donnees_tiers`
3. Garde la vue **Table** (grille)
4. Colonnes utiles : `timestamp`, `id_anonyme`, `action`, `details_techniques`
5. **Trier** par `timestamp` décroissant
6. **Sauvegarder** → `Logs — consultations admin`

Si la table est **vide** → refais l’étape Swagger ci-dessus, puis rafraîchis la question.

**Alternative** : duplique la question **6.4.1** et ajoute le filtre `action = consultation_donnees_tiers` → sauvegarde séparément.

#### Dashboard onglet 4

**+ Nouveau → Dashboard** (ou ajoute à un dashboard existant) → nom : `HealthAI — Logs`  
→ Ajoute **6.4.1** + **6.4.2** → **Sauvegarder**

### Onglet 5 — Gamification

Base **`MSPR502 - Gamification`** pour toutes les cartes (`gamification_db`).

| Carte | Type | Source |
|-------|------|--------|
| Pépites en circulation | Numérique | **Section 6.5.1** |
| Transactions par type | Histogramme | **Section 6.5.2** |
| Animaux possédés | Table | **Section 6.5.3** |

> Le seed (`02_seed.sql`) ne remplit que le **catalogue** (animaux/chromas config). Inventaire, pépites et transactions se créent via l’**API** (`/api/gamification/...`, achats, `POST /api/reco/repas`, etc.). Tables vides = normal tant qu’aucun user n’a joué.

#### 6.5.1 Numérique — pépites en circulation

Base **`MSPR502 - Gamification`**, `{=}` SQL (sans `;`) :

```sql
SELECT COALESCE(SUM(coins), 0) AS pepites_en_circulation
FROM gamification_user_currency
```

**Visualiser** → **Numérique** (icône « 12 ») → **Sauvegarder** → `Pépites en circulation`

Si **0** : aucun user n’a encore de ligne monnaie. Test API : login `c@c.fr` → `GET /api/gamification/inventory`.

**Détail par user** (table bonus) :

```sql
SELECT
  CASE user_id::text
    WHEN 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' THEN 'Marie'
    WHEN 'b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22' THEN 'Lucas'
    WHEN 'c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33' THEN 'Lea'
    WHEN 'd3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44' THEN 'Thomas'
    ELSE user_id::text
  END AS utilisateur,
  coins,
  total_coins_earned,
  total_coins_spent
FROM gamification_user_currency
ORDER BY coins DESC
```

#### 6.5.2 Histogramme — transactions par type

```sql
SELECT
  transaction_type,
  COUNT(*) AS nb,
  SUM(amount) AS montant_total
FROM gamification_transactions
GROUP BY transaction_type
ORDER BY SUM(amount) DESC
```

**Visualiser** → **Histogramme** :
- X : `transaction_type`
- Y : `nb` ou `montant_total`

Types possibles : `animal_purchase`, `chroma_purchase`, `boost_purchase`, `earn`.

**Sauvegarder** → `Transactions gamification par type`

Si vide → acheter un animal via Swagger : `POST /api/gamification/animals/buy` avec token client.

#### 6.5.3 Table — animaux possédés

```sql
SELECT
  CASE i.user_id::text
    WHEN 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' THEN 'Marie'
    WHEN 'b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22' THEN 'Lucas'
    WHEN 'c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33' THEN 'Lea'
    WHEN 'd3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44' THEN 'Thomas'
    ELSE i.user_id::text
  END AS utilisateur,
  c.emoji,
  c.name AS animal,
  i.animal_id,
  i.active_chroma_id,
  i.is_visible,
  i.acquired_at
FROM gamification_user_inventory i
LEFT JOIN gamification_animals_config c ON c.animal_id = i.animal_id
ORDER BY i.acquired_at DESC
```

**Table** → **Sauvegarder** → `Animaux possédés`

**Si inventaire vide** — catalogue disponible (seed) :

```sql
SELECT animal_id, emoji, name, price, rarity, description
FROM gamification_animals_config
WHERE is_available = true
ORDER BY price
```

→ Table `Catalogue animaux` (8 animaux du seed).

#### Dashboard onglet 5

Ajoute **6.5.1** + **6.5.2** + **6.5.3** (ou catalogue si vide) → **Sauvegarder**.

API : `GET /api/gamification/stats`, `GET /api/gamification/inventory`.

### Paramètres dashboard

- **Auto-refresh** : 5 ou 10 min (optionnel)
- **Date relative** : filtres « 30 derniers jours » sur `horodatage`
- **Liens** : texte en en-tête avec URL API Swagger `http://<IP>:18000/docs`

---

## 7. Bonnes pratiques avec l’API

1. **Ne pas exposer Metabase publiquement** sans authentification forte (VPN ou reverse proxy + TLS).
2. **RGPD** : Metabase voit les `id_anonyme` et emails ; restreindre les comptes Metabase (groupe « Analyste » vs « Admin »).
3. **Cohérence** : après un run ETL ou un seed SQL, rafraîchir le schéma Metabase (**Admin → Bases → Sync database schema**).
4. **Champs chiffrés** : `profil_sante`, `suivi_biometrique`, `ref_restriction` peuvent être illisibles dans Metabase ; privilégier les tables non chiffrées (`seance_activite`, `detail_performance`, `journal_alimentaire`).
5. **Performances** : indexer déjà en place (`idx_seance_id_anonyme`, `idx_detail_seance`) — les requêtes 5.1–5.3 restent rapides.

---

## 8. Dépannage TrueNAS

| Problème | Solution |
|----------|----------|
| Metabase ne démarre pas | `docker logs metabase` — attendre 1–2 min au premier lancement |
| Connexion Postgres refusée | Vérifier le nom d’hôte `postgres-sante` (pas `localhost`) depuis le conteneur Metabase |
| Dashboard vide | BDD initialisée ? (`02_seed.sql`, `09_seed_seances_performance.sql`) |
| Port 13000 inaccessible | Ouvrir le port ou accéder via IP LAN |
| Schéma obsolète | Admin Metabase → synchroniser la base |

### Commandes utiles

```bash
# Santé Metabase
curl -s http://localhost:13000/api/health

# Compter les données côté Postgres (comparaison API)
docker exec postgres-sante psql -U sante_user -d sante_db -c \
  "SELECT COUNT(*) FROM seance_activite; SELECT COUNT(*) FROM detail_performance;"
```

---

## 9. Récapitulatif des URLs

| Service | URL |
|---------|-----|
| Metabase | http://localhost:13000 |
| API Swagger | http://localhost:18000/docs |
| API Health | http://localhost:18000/health |

Sur TrueNAS, remplace `localhost` par l’IP du NAS (ex. `192.168.1.150`).
