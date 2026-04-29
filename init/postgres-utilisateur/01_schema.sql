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
    desabonnement_a_fin_periode BOOLEAN NOT NULL DEFAULT false
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
