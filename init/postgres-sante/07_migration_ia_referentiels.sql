-- Référentiels IA (exercices catalogue, ingrédients, équivalences restrictions alimentaires)
-- À appliquer sur sante_db existante ; le peuplement se fait via scripts/import_ia_referentiels_sante.py

ALTER TABLE ref_exercice
    ADD COLUMN IF NOT EXISTS niveau VARCHAR(20);

CREATE TABLE IF NOT EXISTS ref_ingredient (
    id_externe VARCHAR(64) PRIMARY KEY,
    nom TEXT NOT NULL,
    calories DOUBLE PRECISION,
    proteines DOUBLE PRECISION,
    lipides DOUBLE PRECISION,
    glucides DOUBLE PRECISION,
    budget SMALLINT NOT NULL CHECK (budget BETWEEN 1 AND 3)
);

CREATE INDEX IF NOT EXISTS idx_ref_ingredient_budget ON ref_ingredient (budget);
CREATE INDEX IF NOT EXISTS idx_ref_ingredient_nom_lower ON ref_ingredient (lower(nom));

CREATE TABLE IF NOT EXISTS ref_restriction_equivalence (
    cle_canonique VARCHAR(128) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS ref_restriction_alias (
    id_alias SERIAL PRIMARY KEY,
    cle_canonique VARCHAR(128) NOT NULL REFERENCES ref_restriction_equivalence (cle_canonique) ON DELETE CASCADE,
    alias VARCHAR(255) NOT NULL,
    UNIQUE (cle_canonique, alias)
);

CREATE INDEX IF NOT EXISTS idx_ref_restriction_alias_lower ON ref_restriction_alias (lower(alias));
