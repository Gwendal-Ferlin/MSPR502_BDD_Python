-- ==========================================
-- ZONE SANTÉ & SUIVI (BASE B - Pseudonymisée)
-- Microservice Santé - Référence id_anonyme (VAULT dans autre base)
-- ==========================================

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================================
-- RÉFÉRENTIELS
-- ==========================================

CREATE TABLE ref_restriction (
    id_restriction SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    type VARCHAR(100)
);

CREATE TABLE ref_exercice (
    id_exercice SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    muscle_principal VARCHAR(255)
);

CREATE TABLE materiel (
    id_materiel SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL
);

-- Exercice nécessite matériel (N-N)
CREATE TABLE exercice_materiel (
    id_exercice INTEGER NOT NULL REFERENCES ref_exercice(id_exercice) ON DELETE CASCADE,
    id_materiel INTEGER NOT NULL REFERENCES materiel(id_materiel) ON DELETE CASCADE,
    PRIMARY KEY (id_exercice, id_materiel)
);

-- ==========================================
-- PROFIL SANTÉ (1-1 avec vault via id_anonyme)
-- ==========================================

CREATE TABLE profil_sante (
    id_profil SERIAL PRIMARY KEY,
    id_anonyme UUID NOT NULL UNIQUE,
    annee_naissance INTEGER,
    sexe VARCHAR(50),
    taille_cm INTEGER
);

CREATE INDEX idx_profil_sante_id_anonyme ON profil_sante(id_anonyme);

-- ==========================================
-- OBJECTIFS UTILISATEUR
-- ==========================================

CREATE TABLE objectif_utilisateur (
    id_objectif_u SERIAL PRIMARY KEY,
    id_anonyme UUID NOT NULL,
    type_objectif VARCHAR(255),
    valeur_cible DOUBLE PRECISION,
    unite VARCHAR(50),
    date_debut TIMESTAMPTZ,
    date_fin TIMESTAMPTZ,
    statut VARCHAR(100)
);

CREATE INDEX idx_objectif_id_anonyme ON objectif_utilisateur(id_anonyme);

-- ==========================================
-- SUIVI BIOMÉTRIQUE
-- ==========================================

CREATE TABLE suivi_biometrique (
    id_biometrie SERIAL PRIMARY KEY,
    id_anonyme UUID NOT NULL,
    date_releve TIMESTAMPTZ NOT NULL,
    poids_kg DOUBLE PRECISION,
    score_sommeil INTEGER
);

CREATE INDEX idx_biometrie_id_anonyme ON suivi_biometrique(id_anonyme);

-- ==========================================
-- MODULE NUTRITION - JOURNAL ALIMENTAIRE
-- ==========================================

CREATE TABLE journal_alimentaire (
    id_repas SERIAL PRIMARY KEY,
    id_anonyme UUID NOT NULL,
    horodatage TIMESTAMPTZ NOT NULL,
    nom_repas VARCHAR(255),
    type_repas VARCHAR(100),
    total_calories DOUBLE PRECISION,
    total_proteines DOUBLE PRECISION,
    total_glucides DOUBLE PRECISION,
    total_lipides DOUBLE PRECISION
);

CREATE INDEX idx_journal_id_anonyme ON journal_alimentaire(id_anonyme);

-- ==========================================
-- MODULE SPORT - SÉANCE & DÉTAILS
-- ==========================================

CREATE TABLE seance_activite (
    id_seance SERIAL PRIMARY KEY,
    id_anonyme UUID NOT NULL,
    horodatage TIMESTAMPTZ NOT NULL,
    nom_seance VARCHAR(255),
    ressenti_effort_rpe INTEGER
);

CREATE INDEX idx_seance_id_anonyme ON seance_activite(id_anonyme);

CREATE TABLE detail_performance (
    id_performance SERIAL PRIMARY KEY,
    id_seance INTEGER NOT NULL REFERENCES seance_activite(id_seance) ON DELETE CASCADE,
    id_exercice INTEGER NOT NULL REFERENCES ref_exercice(id_exercice) ON DELETE CASCADE,
    series INTEGER,
    reps INTEGER,
    charge_kg DOUBLE PRECISION
);

CREATE INDEX idx_detail_seance ON detail_performance(id_seance);
CREATE INDEX idx_detail_exercice ON detail_performance(id_exercice);

-- ==========================================
-- LIAISONS UTILISATEUR (id_anonyme) <-> RÉFÉRENTIELS
-- ==========================================

-- Utilisateur est sujet à des restrictions
CREATE TABLE utilisateur_restriction (
    id_anonyme UUID NOT NULL,
    id_restriction INTEGER NOT NULL REFERENCES ref_restriction(id_restriction) ON DELETE CASCADE,
    PRIMARY KEY (id_anonyme, id_restriction)
);

-- Utilisateur possède du matériel
CREATE TABLE utilisateur_materiel (
    id_anonyme UUID NOT NULL,
    id_materiel INTEGER NOT NULL REFERENCES materiel(id_materiel) ON DELETE CASCADE,
    PRIMARY KEY (id_anonyme, id_materiel)
);

CREATE INDEX idx_util_restriction_anonyme ON utilisateur_restriction(id_anonyme);
CREATE INDEX idx_util_materiel_anonyme ON utilisateur_materiel(id_anonyme);
