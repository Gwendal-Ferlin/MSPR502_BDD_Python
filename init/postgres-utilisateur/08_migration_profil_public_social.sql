-- Profil public (affichage communauté) + publications / likes / commentaires

ALTER TABLE compte_utilisateur
    ADD COLUMN IF NOT EXISTS nom_affichage VARCHAR(100),
    ADD COLUMN IF NOT EXISTS photo_profil_url TEXT;

CREATE TABLE IF NOT EXISTS publication (
    id_publication UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_anonyme UUID NOT NULL,
    texte TEXT NOT NULL,
    media_url TEXT,
    media_type VARCHAR(20) CHECK (media_type IS NULL OR media_type IN ('image', 'video')),
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    est_supprime BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_publication_date ON publication (date_creation DESC);
CREATE INDEX IF NOT EXISTS idx_publication_auteur ON publication (id_anonyme);

CREATE TABLE IF NOT EXISTS publication_like (
    id_publication UUID NOT NULL REFERENCES publication (id_publication) ON DELETE CASCADE,
    id_anonyme UUID NOT NULL,
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id_publication, id_anonyme)
);

CREATE TABLE IF NOT EXISTS publication_commentaire (
    id_commentaire UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_publication UUID NOT NULL REFERENCES publication (id_publication) ON DELETE CASCADE,
    id_anonyme UUID NOT NULL,
    texte TEXT NOT NULL,
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    est_supprime BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_commentaire_publication ON publication_commentaire (id_publication);
