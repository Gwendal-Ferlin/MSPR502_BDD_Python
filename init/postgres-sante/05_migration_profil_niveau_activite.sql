-- Migration: ajout de niveau_activite à profil_sante
-- À exécuter sur une base sante_db déjà existante

ALTER TABLE profil_sante
ADD COLUMN IF NOT EXISTS niveau_activite VARCHAR(50);

