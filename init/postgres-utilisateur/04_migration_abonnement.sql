-- Migration pour BDD existantes : ajout des colonnes abonnement (période payée, désabonnement à fin de période).
-- À exécuter une fois si la table compte_utilisateur existe déjà sans ces colonnes.

ALTER TABLE compte_utilisateur
ADD COLUMN IF NOT EXISTS date_fin_periode_payee TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS desabonnement_a_fin_periode BOOLEAN NOT NULL DEFAULT false;
