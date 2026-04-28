-- Migration : colonnes TEXT pour chiffrement applicatif (Fernet côté API)
-- À exécuter une fois si les tables existent avec les anciens types.

ALTER TABLE ref_restriction ALTER COLUMN nom TYPE TEXT;
ALTER TABLE ref_restriction ALTER COLUMN type TYPE TEXT;

ALTER TABLE profil_sante ALTER COLUMN annee_naissance TYPE TEXT USING annee_naissance::text;
ALTER TABLE profil_sante ALTER COLUMN sexe TYPE TEXT;
ALTER TABLE profil_sante ALTER COLUMN taille_cm TYPE TEXT USING taille_cm::text;
ALTER TABLE profil_sante ALTER COLUMN niveau_activite TYPE TEXT;

ALTER TABLE suivi_biometrique ALTER COLUMN poids_kg TYPE TEXT USING poids_kg::text;
ALTER TABLE suivi_biometrique ALTER COLUMN score_sommeil TYPE TEXT USING score_sommeil::text;
