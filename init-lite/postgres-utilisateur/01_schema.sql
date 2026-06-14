-- ==========================================
-- ZONE IDENTITÉ (BASE A - PII)
-- Microservice Utilisateur
-- ==========================================

CREATE TABLE compte_utilisateur (
    id_user SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    email_hmac VARCHAR(64),
    password TEXT NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Admin', 'Super-Admin', 'Client')),
    type_abonnement VARCHAR(50) NOT NULL CHECK (type_abonnement IN ('Freemium', 'Premium', 'Premium+')),
    date_consentement_rgpd TIMESTAMPTZ,
    est_supprime BOOLEAN NOT NULL DEFAULT false,
    date_suppression TIMESTAMPTZ,
    date_fin_periode_payee TIMESTAMPTZ,
    desabonnement_a_fin_periode BOOLEAN NOT NULL DEFAULT false,
    nom_affichage VARCHAR(100),
    photo_profil_url TEXT
);

CREATE UNIQUE INDEX idx_compte_email_hmac ON compte_utilisateur(email_hmac) WHERE email_hmac IS NOT NULL;
CREATE UNIQUE INDEX ux_compte_email_plain ON compte_utilisateur (lower(trim(email))) WHERE email_hmac IS NULL;

-- ==========================================
-- ZONE PIVOT (Lien anonymisé - RGPD)
-- ==========================================

CREATE TABLE vault_correspondance (
    id_anonyme UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user INTEGER NOT NULL UNIQUE REFERENCES compte_utilisateur(id_user) ON DELETE CASCADE,
    date_derniere_activite TIMESTAMPTZ,
    consentement_sante_actif BOOLEAN DEFAULT true
);

CREATE INDEX idx_vault_id_user ON vault_correspondance(id_user);

-- ==========================================
-- COMMUNAUTÉ (publications, likes, commentaires)
-- ==========================================

CREATE TABLE publication (
    id_publication UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_anonyme UUID NOT NULL,
    texte TEXT NOT NULL,
    media_url TEXT,
    media_type VARCHAR(20) CHECK (media_type IS NULL OR media_type IN ('image', 'video')),
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    est_supprime BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX idx_publication_date ON publication (date_creation DESC);
CREATE INDEX idx_publication_auteur ON publication (id_anonyme);

CREATE TABLE publication_like (
    id_publication UUID NOT NULL REFERENCES publication (id_publication) ON DELETE CASCADE,
    id_anonyme UUID NOT NULL,
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id_publication, id_anonyme)
);

CREATE TABLE publication_commentaire (
    id_commentaire UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_publication UUID NOT NULL REFERENCES publication (id_publication) ON DELETE CASCADE,
    id_anonyme UUID NOT NULL,
    texte TEXT NOT NULL,
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    est_supprime BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX idx_commentaire_publication ON publication_commentaire (id_publication);
