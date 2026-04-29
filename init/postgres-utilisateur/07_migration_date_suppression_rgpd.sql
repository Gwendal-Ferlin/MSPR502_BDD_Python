-- Date de suppression logique : nécessaire pour effacer définitivement après la durée RGPD configurée (ex. 2 ans).
ALTER TABLE compte_utilisateur ADD COLUMN IF NOT EXISTS date_suppression TIMESTAMPTZ;

COMMENT ON COLUMN compte_utilisateur.date_suppression IS
    'Horodatage de la suppression logique ; effacement physique après rgpd_soft_delete_retention_days.';

-- Comptes déjà en est_supprime=true sans date : valeur rétroactive pour déclencher l’effacement au plus vite
-- après déploiement (sinon ils resteraient indéfiniment car la date est inconnue). Ajuster au besoin.
UPDATE compte_utilisateur
SET date_suppression = now() - INTERVAL '731 days'
WHERE COALESCE(est_supprime, false) = true AND date_suppression IS NULL;
