-- ==========================================
-- JEU DE DONNÉES - Microservice Santé
-- id_anonyme = mêmes UUIDs que vault_correspondance (utilisateur_db)
-- ref_restriction, profil_sante, suivi_biometrique : valeurs Fernet (clé dev .env.example DATA_ENCRYPTION_KEY)
-- ==========================================

-- Référentiel restrictions (nom/type chiffrés Fernet — régénérer : scripts/emit_encrypted_sante_seed.py)
INSERT INTO ref_restriction (nom, type) VALUES
('gAAAAABp8Ga9biw6iU8UhjWuJy5G8je5yRR-TS4P1PWtIwIc25KpT8Rk_Qkfl4YMTLj3FlMouohzztutH3394RrRQG1ANcnj7A==', 'gAAAAABp8Ga9BfsePOS_FsLkn5SFFfPYycLXU-9FhuRletuwmPo-4g1w5UWsCKsM_WNsvUrLekXIiS3aE60QQRdV7MEAWG4JRg=='),
('gAAAAABp8Ga9gPWgDk7sm8DhNTgYlw34XQ1iRhml6-HKwZBct8JjET7KjUu8YGA3ecLIBZqmZ-0hSlXiT3tnNSOKGlfq7OcBFQ==', 'gAAAAABp8Ga9S-I6pp4P4tmXQU_h4QWZlHsOfeEQJ65-DpciW7Jv9ILQZF5KtQQlG2QsvRR7IiybTG6QuESVgyqoGlkfWXXtCQ=='),
('gAAAAABp8Ga99AJdDq_-EIbvF-nhZd0yq6sBhJLIngZPxwJadkjIwRRDksUnC138gngVxymKYJUQnBICWHoKRFmOlqvD-k-QVA==', 'gAAAAABp8Ga9hunZTNDO7KtWrukYjePJKV9C-8MDIIQnINfQ43FGN1pEkw1T-n_kiAbXIXsL-zJSHGpsOD7hkWqx0o17xgEzlg=='),
('gAAAAABp8Ga9fzr9f-H2100i1-RHeAC7iB5NYPtijbVHqsL5Q9uqFqnEinVvJBv0TBOp3hpUky2kKDOoohoVsp1hDUE4KFoXfA==', 'gAAAAABp8Ga9EWYe9DM1nCFlgPOKXYHRMXeuinmHljNF7eOB3RQ5DZG7_RB3Fjc0VTYfnaX3KJhEe8sjCbymy_SHND_ieWM-GA=='),
('gAAAAABp8Ga9DBS4IivBF9eDCZ_JM6SdaeziXwn1o52GbssoqjZxIuHFGcdqMGAzcXZBgjzqVRhEWQMDxzsgsNnOr05L-hVyvg==', 'gAAAAABp8Ga9wwC2oiFbjY3kiME9iSzQX_7BigpflxA5dhP8-tIsgDZnq0gJkPkE_FApGZEswbAc9dRuSdi5nmxrxjvPJHVhNQ=='),
('gAAAAABp8Ga9O9a0_NyQeuqIiqo7NbwKSLrRE0Zm8lfZeg8uvp8huIDfsE37DcL-gPZ7IxJgVaP7IP0saQ_r4XUs4U6g_5KlFA==', 'gAAAAABp8Ga9K1vxyUUmUxsIj4iI8rfMhwglfugq8TzEKHCX43mgfifgO4mumtoI58D_nWTNnGX4sSONp33BywS2wgE9eBkiJQ=='),
('gAAAAABp8Ga9AsHCBnoraAfF-xuGjBgZLpFr41aRea_YCKvCQ6CmxlsAKihp_SUjIVhdJjHP7brA05TA5sMGaxEHAmsMxc-Wpw==', 'gAAAAABp8Ga99FwzuySCM-WeKoltME2Ww4nPJ3K9xCXjlgza1pew_G0o9-YGHO0LtnAglOCEIknojYt-vt-XThUogGmdZjkfsA=='),
('gAAAAABp8Ga9iwt1jMRJ7WjUSwEgU39seAn1Gegnlil80StrgovcCRTNhuUrvrjUpGwwKeCaqSMJbPtxS1hmB6JyU0CoeCtYkw==', 'gAAAAABp8Ga9UiJiCVFNj37-y7pFKGdVd5rvqKfGR1mCQC4RTh29vplJfgPuHVh4h0FqvzuAJMD6Djs4NMNFlub3B5K-oPme9A=='),
('gAAAAABp8Ga9JoX_-l1OIGIYW7jXA18hFne5AJ9lBeQNLS54R5EjP0nd6uD4Apt3XeiTwopEjU39MEfYNOzaLbX68eDFbTD_Hg==', 'gAAAAABp8Ga9xNGkQuj8OlsHeX0yhWDpdcaTOmurhafG_HJ3qplRynk0NLk0fVHRcaK8i_wthG8roKVERr0NZ0goO6SnMyqfIg=='),
('gAAAAABp8Ga9Urylp00lHjuVvtcS_8J95DZ55ExW_26IFcM-6jHY1XFCeQe0SDR-cLHAPhH4a--BsEDRS6tEYB4ZYIw0RaSHlQ==', 'gAAAAABp8Ga9TKAGcjga5uW1AaCsBc8BgpLfsfFtf0vyv7eE4jWBJsRPvSW1O1eVsz4jaSFzZMeVatvqk2h9iXloPpXu9Js2RA=='),
('gAAAAABp8Ga9-qzZJj6IwXRdXUig82nqKGKHTC9SCup36Cx03AP0FjMaM1Gal0Wd6EKtIBDC3ls-LrnDIdESctrpfD2bRGjG9g==', 'gAAAAABp8Ga9AwHZL5fmPuw1SSI2L19YvSR_3w4CN8r9qWmTI_E83LRyMqd_7EJeY74uNXdMyf6brSj2RFkiOQKknVffmiLy5Q=='),
('gAAAAABp8Ga9C62p0yVCcONSI8M08xucW9D2YqCy7n_XI5sr2HuSgBX54P2R7_2m5SN00o-xljW6cEtDmqTvgoIY8FqfZZMKXKMjuopJuqGgDZTgnBnGgKY=', 'gAAAAABp8Ga9dN51yxrz3hZ55KZP2Da60a9-Cro7pQqgte359HdLu3RMrfG9WYtrF0rhYaprA7VFGjfANCsfNzNawrTf67XvTg=='),
('gAAAAABp8Ga9V3B3WrtBJ0RenZ9sZtu4e6s6HfCYefF-A_TvviD-7jSFQ7intFjxggyHr5Etc9_lSmw_AoGyWgriJq_S0YN5OQ==', 'gAAAAABp8Ga9Fk5Nz8TlCoUeb97aHZ7X0ooUwahs2QWmTQEDsOh9jiVP2pFMipnohN4bUbdKrHmdQCym9jh8Z-XAUriYPBJK9g=='),
('gAAAAABp8Ga9EHrF2_nEoizBro9PpsVorEjQX3ydQkZNR-xbcp-DB9PT-C4TmEFzUQuRdFtGPTFhmyI20CIA90UcQmNezoUMlg==', 'gAAAAABp8Ga9-qYXGXb_W2LXYZ_IISAeLJUTNCUx8TieA6fMbfQlRFH1Fjp7BQi1dk_ZGugsopnGQzereQtoTFtZzWCT255asA==');

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

-- Profils santé (champs sensibles Fernet)
INSERT INTO profil_sante (id_anonyme, annee_naissance, sexe, taille_cm, niveau_activite) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'gAAAAABp8Ga9dUPYG5KNr-LRG1rFhI5VKffclfrow78bxusMX3U1GHK7FuVL3_vhFaEJ__ryyV_t9Od7-qGxsDSArXNvUdK2EQ==', 'gAAAAABp8Ga9OLZYV8KESXfh-vQniQ7s23jcu2zv88WS8fPWYNbzGDo7TBpEHITn4NclpJJe5in_yBayf7Md5NF-6ZOAeJb8OA==', 'gAAAAABp8Ga9iI1ri1jgpR1JCEvf-JSjJq5wBzTz1NLMr7_D_bhjgjCsUJmseXPI1Pysvh_hBarzYuFl5teNjy9EDsyWTlsVTg==', 'gAAAAABp8Ga9IXvZkxuiVz2xTSFTDbcF7Z1tDKbXt46F24gh6lHkLfH19CCTRMVfTcW5dG-nl8xociPd8urepcKhQuNKujvbig=='),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', 'gAAAAABp8Ga9MyUMd8dX8pC6BQUVgSdmfca0UWQ9mrMaHscgiW0BL0wff9fntNZjcpV28wkxYSfnxtoDuz_q6aUr_9OO0MzT-g==', 'gAAAAABp8Ga9ALrzBol0sBpBJmVnusUxoZqFrSOo4BkFhcJXxN4Ho1a-Sa2rKH5a1-mw5wtsGb6HKNBRQugCuaRAZnKrrxpxDg==', 'gAAAAABp8Ga9UjJ-iF955rM9SQO_G96_VBklDKDJh68CTvXpGtExNBddJe0o27-6zyMNRM4qQFJi5haBGihZYRaOs6fa6IMpfg==', 'gAAAAABp8Ga9LVbyZ4mUay3r-Skjbl9gz-urMcpre4fahDs2YoM6FV81_v3b3dyngnjfCbX0LfG5jN80rG8wmqQ017JtYJRyyA=='),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', 'gAAAAABp8Ga90chihITi6gdpmsIRVIxWCpgYPdW-paelQSSs3mtgWc-vb3C-J-zjWt8uU-MpVF8VCS-ePBlJ38up2bixXGviYg==', 'gAAAAABp8Ga9nnOP9ejI3ZBdHGTSn7KQ75So6S8x-SDNVDiA2C9h_azEK7Ti2p8RCM_12Gbn7AsTjEy2HB4E0bz5HBw8nGr1Kg==', 'gAAAAABp8Ga9bVKlhUBa2C4RBLkur15uxZ4FUD5euEH6gimtUsEyjyX0KL4up4U49bzwdFurUvo7GIvsWo1B1HJ5swkbGebt3A==', 'gAAAAABp8Ga9GZVkGsShHj5EFiR-fwtOmxswOBdeklS6wlbQ_3FKAQP2bCB_a_bGZp8JhPRz7p6zMQjhT51JDPutnW4mQkWdNQ=='),
('d3bbee22-cf3e-4f01-ee90-9ee2ef6b3d44', 'gAAAAABp8Ga9S0-NZ7P0U-x-_PZh7tFZ3XfbtzzKsJaXJyZRZmFdVX3ZaEa-yPJ0lNxK3RpsDCsM8Jdj2o03zeMtt8jdPctv_w==', 'gAAAAABp8Ga9grVuHT4Emhw-1W4UZ1KV10nsDufcpN3ZO7CBp4fqIr47HidTdeorFjpdgovLyAou-Wa8XNmTsaIQ8AzbAi0ZpA==', 'gAAAAABp8Ga9qTwPmdfmk338kG7BVZbsg-lypxZDKQzYA0wfxyGpv73f28D593f4kiQU90N_srBP9biCWaX1cxUaey3N5C2PjA==', 'gAAAAABp8Ga9E-7Yc-Kh9jnBP9tNeqUehe6OOwYzoc2G11VPjPB5L6PUrp0vJxMyRJ-rK7X0XjfCUixLsU-2zgq4pjc-PEUhiQ==');

-- Objectifs utilisateur
INSERT INTO objectif_utilisateur (id_anonyme, type_objectif, valeur_cible, unite, date_debut, date_fin, statut) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Perte de poids', 58.0, 'kg', '2025-01-10 00:00:00+01', NULL, 'En cours'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Calories journalières', 1800.0, 'kcal', '2025-01-10 00:00:00+01', NULL, 'En cours'),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', 'Prise de masse', 78.0, 'kg', '2025-02-01 00:00:00+01', NULL, 'En cours'),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', 'Équilibre nutritionnel', NULL, NULL, '2025-01-20 00:00:00+01', NULL, 'En cours');

-- Suivi biométrique (poids_kg / score_sommeil Fernet)
INSERT INTO suivi_biometrique (id_anonyme, date_releve, poids_kg, score_sommeil) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2025-02-01 08:00:00+01', 'gAAAAABp8Ga9vEahjS85QlnkmNsCfOzQCs0-MYZDg6rNmZGjfmrkV_NdKegT_Id-RQxtMe41lYQchukKkLb_x6yGbZOaw-9TKg==', 'gAAAAABp8Ga9r0gTQAjJRdAvb41ahw9tuldAQoy9DMHBC_pmOGq23X9ql28_cPmwG0vTbJoIsleof6u0XhevJiyrDgCZ9GJSKQ=='),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2025-02-08 08:00:00+01', 'gAAAAABp8Ga9ve00-lJWUTMaAvwBAB4_yO4VpCFSX1-i0PpbMEy9lVhBXx-B-TRaYX-2-CmUgdGGHwCY2MqcQlhhn6G0yKy4oQ==', 'gAAAAABp8Ga9i80GYH6zuueOo3g_bYq_2RPuGoVVGfq7QrLhmKzPckL77ZsKAASOit3Vzb5JUMOYahbtqHJm2p9rCQU0umy3SQ=='),
('b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22', '2025-02-05 07:30:00+01', 'gAAAAABp8Ga9cXLwdFwcbqJbdgD5NEdXglsQmp9OwZWnlmeidVT6Ziyp7Z7yxp3-Wct1V_YmMBj9CdWkVfP0AhyvuA-eJwk_SQ==', 'gAAAAABp8Ga9QslYGzRK2JEqDQrbriGisLCLBL_dki9WgUosY3HUsrQyvk-YvuWU4TVQlduSnbPeNbKZQXlwn2boOWhUGSI_TQ=='),
('c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33', '2025-02-07 09:00:00+01', 'gAAAAABp8Ga9Sv1xdztinZXufjxFbTx4eU4nKh8cnOkPqgfcfxzdjxXo5X4rf4r3QK-Yasa8GFh0mqC4Hc8NksM_mGmxIHKVJg==', 'gAAAAABp8Ga9sj5_XI8BCfqFRes_RsQjvkivxpKZJh44EhENwVNbDuWeGkHfUUEa5G4cPs9X73lf2RlS2kq4SaIkXoCqn2VXhw==');

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
