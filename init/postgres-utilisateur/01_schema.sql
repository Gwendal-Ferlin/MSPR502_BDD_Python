-- ==========================================
-- ZONE IDENTITÉ (BASE A - PII)
-- Microservice Utilisateur
-- ==========================================

CREATE TABLE compte_utilisateur (
    id_user SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Admin', 'Super-Admin', 'Client')),
    type_abonnement VARCHAR(50) NOT NULL CHECK (type_abonnement IN ('Freemium', 'Premium', 'Premium+')),
    date_consentement_rgpd TIMESTAMPTZ,
    est_supprime BOOLEAN NOT NULL DEFAULT false,
    date_fin_periode_payee TIMESTAMPTZ,
    desabonnement_a_fin_periode BOOLEAN NOT NULL DEFAULT false
);

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
