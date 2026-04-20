-- Schéma Gamification (PostgreSQL)
--
-- Note importante :
-- Une contrainte FK directe vers une table "utilisateurs" située dans une AUTRE base PostgreSQL
-- n'est pas supportée (les clés étrangères ne traversent pas les bases).
-- Dans cette base, on stocke donc user_id en UUID comme référence logique.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE gamification_user_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    animal_id VARCHAR(50) NOT NULL, -- 'fox', 'cat', 'red_panda', 'snake', 'bat', 'ferret', 'chicken', 'deer'
    is_visible BOOLEAN DEFAULT true, -- Permet de "cacher" un animal
    active_chroma_id VARCHAR(50) DEFAULT 'default', -- Couleur active de l'animal
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, animal_id), -- Un utilisateur ne peut avoir qu'un exemplaire d'un animal
    CHECK (animal_id IN ('fox', 'cat', 'red_panda', 'snake', 'bat', 'ferret', 'chicken', 'deer'))
);

CREATE INDEX idx_gamification_inventory_user ON gamification_user_inventory(user_id);
CREATE INDEX idx_gamification_inventory_active_chromas ON gamification_user_inventory(user_id, active_chroma_id);

CREATE TABLE gamification_user_chromas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    animal_id VARCHAR(50) NOT NULL,
    chroma_id VARCHAR(50) NOT NULL, -- 'default', 'crimson', 'sunset', etc.
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, animal_id, chroma_id),
    FOREIGN KEY (user_id, animal_id) REFERENCES gamification_user_inventory(user_id, animal_id) ON DELETE CASCADE
);

CREATE INDEX idx_gamification_chromas_user ON gamification_user_chromas(user_id);
CREATE INDEX idx_gamification_chromas_animal ON gamification_user_chromas(user_id, animal_id);

CREATE TABLE gamification_user_currency (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    coins BIGINT DEFAULT 500, -- Au démarrage
    total_coins_earned BIGINT DEFAULT 500, -- Statistique totale
    total_coins_spent BIGINT DEFAULT 0, -- Statistique totale
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (coins >= 0)
);

CREATE INDEX idx_gamification_currency_user ON gamification_user_currency(user_id);

CREATE TABLE gamification_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- 'animal_purchase', 'chroma_purchase', 'boost_purchase', 'earn'
    amount BIGINT NOT NULL,
    animal_id VARCHAR(50), -- Nullable si transaction != animal/chroma
    chroma_id VARCHAR(50), -- Nullable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB, -- Pour les boosts ou infos supplémentaires

    CHECK (transaction_type IN ('animal_purchase', 'chroma_purchase', 'boost_purchase', 'earn'))
);

CREATE INDEX idx_gamification_transactions_user ON gamification_transactions(user_id);
CREATE INDEX idx_gamification_transactions_type ON gamification_transactions(transaction_type);

CREATE TABLE gamification_animals_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    emoji VARCHAR(10) NOT NULL,
    price BIGINT NOT NULL,
    rarity VARCHAR(20) NOT NULL, -- 'common', 'rare', 'epic', 'legendary'
    description TEXT,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (rarity IN ('common', 'rare', 'epic', 'legendary'))
);

CREATE TABLE gamification_chromas_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id VARCHAR(50) NOT NULL,
    chroma_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price BIGINT NOT NULL DEFAULT 0,
    row_y INT NOT NULL, -- Pour le sprite sheet
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(animal_id, chroma_id),
    FOREIGN KEY (animal_id) REFERENCES gamification_animals_config(animal_id) ON DELETE CASCADE
);

