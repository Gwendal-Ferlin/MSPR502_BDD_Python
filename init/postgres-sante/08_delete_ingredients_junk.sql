-- Supprime les noms invalides « by Marque » (sans libellé produit) dans ref_ingredient
DELETE FROM ref_ingredient WHERE lower(btrim(nom)) LIKE 'by %';
