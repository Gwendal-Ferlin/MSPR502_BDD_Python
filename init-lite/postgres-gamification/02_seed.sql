-- Seed Gamification (données de configuration)
-- Idempotent : en cas de relance, on ne duplique pas.

INSERT INTO gamification_animals_config (animal_id, name, emoji, price, rarity, description)
VALUES
    ('fox', 'Renard', '🦊', 0, 'common', 'Malin et agile, le renard est votre premier compagnon.'),
    ('cat', 'Chat', '🐱', 100, 'common', 'Indépendant et curieux.'),
    ('red_panda', 'Panda Roux', '🔴', 150, 'rare', 'Adorable et rare.'),
    ('snake', 'Serpent', '🐍', 200, 'rare', 'Mystérieux et élégant.'),
    ('bat', 'Chauve-souris', '🦇', 300, 'epic', 'Nocturne et mystique.'),
    ('ferret', 'Furet', '🟡', 250, 'epic', 'Joueur et espiègle.'),
    ('chicken', 'Poussin', '🐥', 120, 'common', 'Petit et mignon.'),
    ('deer', 'Mini Cerf', '🦌', 180, 'rare', 'Gracieux et rapide.')
ON CONFLICT (animal_id) DO NOTHING;

INSERT INTO gamification_chromas_config (animal_id, chroma_id, name, price, row_y)
VALUES
    ('chicken', 'default', 'Original', 0, 0),
    ('chicken', 'crimson', 'Cramoisi', 50, 32),
    ('chicken', 'sunset', 'Coucher de soleil', 75, 64)
ON CONFLICT (animal_id, chroma_id) DO NOTHING;

