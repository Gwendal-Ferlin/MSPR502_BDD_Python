-- Migration : chiffrement applicatif (colonnes TEXT + email_hmac)
-- À exécuter une fois si la base existe déjà avec l'ancien schéma (sans email_hmac).

ALTER TABLE compte_utilisateur DROP CONSTRAINT IF EXISTS compte_utilisateur_email_key;

ALTER TABLE compte_utilisateur ADD COLUMN IF NOT EXISTS email_hmac VARCHAR(64);

ALTER TABLE compte_utilisateur ALTER COLUMN email TYPE TEXT;
ALTER TABLE compte_utilisateur ALTER COLUMN password TYPE TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_compte_email_hmac ON compte_utilisateur(email_hmac) WHERE email_hmac IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ux_compte_email_plain ON compte_utilisateur (lower(trim(email))) WHERE email_hmac IS NULL;
