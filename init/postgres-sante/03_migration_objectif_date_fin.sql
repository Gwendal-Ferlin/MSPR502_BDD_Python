-- Migration: ajout de date_fin à objectif_utilisateur
-- À exécuter sur une base sante_db déjà existante

ALTER TABLE objectif_utilisateur
ADD COLUMN IF NOT EXISTS date_fin TIMESTAMPTZ;

