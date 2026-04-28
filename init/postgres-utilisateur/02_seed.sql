-- ==========================================
-- JEU DE DONNÉES - Microservice Utilisateur
-- UUIDs fixes pour cohérence avec sante_db et MongoDB
-- ==========================================

-- Mots de passe de test : tous "password" (hash bcrypt, généré avec bcrypt.hashpw)
INSERT INTO compte_utilisateur (email, email_hmac, password, role, type_abonnement, date_consentement_rgpd) VALUES
('marie.dupont@email.fr', NULL, '$2b$12$/9KuH9SbyAZAZXhVRRzJOuO7gcMW/5PPgVlQe8bVzRZOx4EZucEdu', 'Client', 'Premium', '2024-01-15 10:00:00+01'),
('c@c.fr', NULL, '$2b$12$/9KuH9SbyAZAZXhVRRzJOuO7gcMW/5PPgVlQe8bVzRZOx4EZucEdu', 'Client', 'Freemium', '2024-02-20 14:30:00+01'),
('a@a.fr', NULL, '$2b$12$/9KuH9SbyAZAZXhVRRzJOuO7gcMW/5PPgVlQe8bVzRZOx4EZucEdu', 'Admin', 'Premium+', '2024-03-01 09:00:00+01'),
('sa@sa.fr', NULL, '$2b$12$/9KuH9SbyAZAZXhVRRzJOuO7gcMW/5PPgVlQe8bVzRZOx4EZucEdu', 'Super-Admin', 'Premium+', '2023-06-01 00:00:00+01');

-- Vault : même ordre que compte_utilisateur (id_user 1->4)
-- Ces UUIDs sont réutilisés dans sante_db et MongoDB
INSERT INTO vault_correspondance (id_anonyme, id_user, date_derniere_activite, consentement_sante_actif) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 1, '2025-02-08 18:45:00+01', true),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', 2, '2025-02-07 20:00:00+01', true),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', 3, '2025-02-09 08:30:00+01', true),
('d3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44', 4, '2025-02-09 12:00:00+01', true);
