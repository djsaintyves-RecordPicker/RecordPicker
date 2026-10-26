# Section publique MOOP

Pages statiques indépendantes : `/moop/`, `/moop/fr/`, `/moop/en/` et les pages `privacy/` et `support/` dans chaque langue. Contact : support@recordpicker.app. Aucun lien de téléchargement n'est annoncé avant disponibilité de l'application.

Les quatre textes approuvés sont versionnés dans `moop/content/`. Après modification, lancer `python3 Scripts/build_moop_section.py`, puis `python3 Scripts/audit_moop_site.py`. Le générateur conserve les autres sections du site et ajoute les URL aux deux sitemaps.

Validation : audit MOOP, politique canonique, liens internes, vérification visuelle Safari. L'audit de localisation RP exclut cette section indépendante ; aucune baseline RP ne doit être régénérée pour une modification MOOP.

Déploiement existant : un push sur `main` déclenche `.github/workflows/pages.yml` et publie le dépôt statique avec GitHub Pages sur recordpicker.app. Les workflows qualité restent indépendants : contrôler leur résultat avant publication. Vérifier ensuite les sept URL publiques, notamment les quatre adresses privacy/support configurées dans l'application.

L'illustration de bobine SVG est originale. Ces pages n'embarquent ni affiche, logo de plateforme, catalogue tiers, script actif, mesure d'audience ni police distante. L'hébergement est soumis à la politique de GitHub, rappelée dans chaque page de confidentialité.
