-- ==========================================
-- JEU DE DONNÉES - Microservice Santé
-- id_anonyme = mêmes UUIDs que vault_correspondance (utilisateur_db)
-- ==========================================

-- Référentiel restrictions
INSERT INTO ref_restriction (nom, type) VALUES
('Sans gluten', 'Allergie'),
('Lactose', 'Intolérance'),
('Végétarien', 'Régime'),
('Arachides', 'Allergie'),
('Vegan', 'Régime'),
('halal', 'Régime'),
('kosher', 'Régime'),
('sans lactose', 'Intolérance'),
('sans gluten', 'Allergie'),
('sans soja', 'Allergie'),
('sans arachides', 'Allergie'),
('sans fruits de mer', 'Allergie'),
('sans oeufs', 'Allergie'),
('sans mollusques', 'Allergie');

-- Référentiel exercices
INSERT INTO ref_exercice (nom, muscle_principal) VALUES
('Squat', 'Quadriceps'),
('Développé couché', 'Pectoraux'),
('Traction', 'Dos'),
('Soulevé de terre', 'Dos'),
('Fentes', 'Quadriceps'),
('Gainage', 'Abdominaux'),
('Pompes', 'Pectoraux'),
('Curl biceps', 'Biceps');

-- Référentiel matériel
INSERT INTO materiel (nom) VALUES
('Haltères'),
('Barre'),
('Kettlebell'),
('Bande élastique'),
('Poids du corps'),
('Barre de traction');

-- Exercice <-> Matériel (N-N)
INSERT INTO exercice_materiel (id_exercice, id_materiel) VALUES
(1, 2), (1, 5),   -- Squat: barre, poids du corps
(2, 2), (2, 1),   -- Développé: barre, haltères
(3, 6), (3, 5),   -- Traction: barre traction, poids du corps
(4, 2), (4, 1),   -- SDT: barre, haltères
(5, 1), (5, 5),   -- Fentes: haltères, poids du corps
(6, 5),           -- Gainage: poids du corps
(7, 5),           -- Pompes: poids du corps
(8, 1), (8, 2);   -- Curl: haltères, barre

-- Profils santé (1 par utilisateur - mêmes UUIDs que vault)
INSERT INTO profil_sante (id_anonyme, annee_naissance, sexe, taille_cm) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 1992, 'F', 165),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', 1988, 'H', 178),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', 1995, 'F', 172),
('d3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44', 1985, 'H', 182);

-- Objectifs utilisateur
INSERT INTO objectif_utilisateur (id_anonyme, type_objectif, valeur_cible, unite, date_debut, date_fin, statut) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Perte de poids', 58.0, 'kg', '2025-01-10 00:00:00+01', NULL, 'En cours'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Calories journalières', 1800.0, 'kcal', '2025-01-10 00:00:00+01', NULL, 'En cours'),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', 'Prise de masse', 78.0, 'kg', '2025-02-01 00:00:00+01', NULL, 'En cours'),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', 'Équilibre nutritionnel', NULL, NULL, '2025-01-20 00:00:00+01', NULL, 'En cours');

-- Suivi biométrique
INSERT INTO suivi_biometrique (id_anonyme, date_releve, poids_kg, score_sommeil) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2025-02-01 08:00:00+01', 61.2, 7),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2025-02-08 08:00:00+01', 60.8, 8),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', '2025-02-05 07:30:00+01', 74.5, 6),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', '2025-02-07 09:00:00+01', 65.0, 7);

-- Journal alimentaire
INSERT INTO journal_alimentaire (id_anonyme, horodatage, nom_repas, type_repas, total_calories, total_proteines, total_glucides, total_lipides) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2025-02-08 08:15:00+01', 'Petit-déj maison', 'Petit-dej', 420.0, 18.0, 52.0, 16.0),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2025-02-08 12:30:00+01', 'Salade quinoa poulet', 'Dejeuner', 580.0, 42.0, 45.0, 22.0),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2025-02-08 19:00:00+01', 'Saumon légumes vapeur', 'Diner', 520.0, 38.0, 28.0, 28.0),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', '2025-02-07 08:00:00+01', 'Oeufs toast avocat', 'Petit-dej', 550.0, 28.0, 35.0, 30.0),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', '2025-02-07 13:00:00+01', 'Pâtes bolognaise', 'Dejeuner', 720.0, 35.0, 82.0, 28.0),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', '2025-02-09 07:45:00+01', 'Smoothie bowl', 'Petit-dej', 380.0, 12.0, 62.0, 10.0);

-- Séances d'activité
INSERT INTO seance_activite (id_anonyme, horodatage, nom_seance, ressenti_effort_rpe) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2025-02-06 18:00:00+01', 'Full body maison', 6),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2025-02-08 09:00:00+01', 'Cardio 30 min', 5),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', '2025-02-07 19:00:00+01', 'Force dos / jambes', 7),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', '2025-02-08 12:00:00+01', 'HIIT', 8);

-- Détails de performance (liés aux séances 1 à 4)
INSERT INTO detail_performance (id_seance, id_exercice, series, reps, charge_kg) VALUES
(1, 1, 3, 12, 0.0),   -- Squat poids du corps
(1, 7, 3, 15, 0.0),   -- Pompes
(1, 6, 3, 45, 0.0),   -- Gainage 45s
(3, 1, 4, 8, 60.0),   -- Squat barre
(3, 4, 3, 6, 100.0),  -- SDT
(3, 3, 3, 8, 0.0),    -- Tractions
(4, 5, 4, 12, 8.0),   -- Fentes haltères
(4, 6, 3, 60, 0.0);   -- Gainage 60s

-- Utilisateur <-> Restrictions
INSERT INTO utilisateur_restriction (id_anonyme, id_restriction) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 1),  -- Marie : sans gluten
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', 3),  -- Léa : végétarien
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', 5);  -- Léa : vegan

-- Utilisateur <-> Matériel possédé
INSERT INTO utilisateur_materiel (id_anonyme, id_materiel) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 4),  -- Bande élastique, poids du corps
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 5),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', 1),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', 2),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', 6),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', 4),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', 5);
