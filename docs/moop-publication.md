# Section publique MOOP

Pages statiques indépendantes : `/moop/`, `/moop/fr/`, `/moop/en/` et les pages `privacy/` et `support/` dans chaque langue. Contact : support@recordpicker.app. Aucun lien de téléchargement n'est annoncé avant disponibilité de l'application.

Les quatre textes approuvés sont versionnés dans `moop/content/`. Après modification, lancer `python3 Scripts/build_moop_section.py`, puis `python3 Scripts/audit_moop_site.py`. Le générateur conserve les autres sections du site et ajoute les URL aux deux sitemaps.

Validation : audit MOOP, politique canonique, liens internes, vérification visuelle Safari. L'audit de localisation RP exclut cette section indépendante ; aucune baseline RP ne doit être régénérée pour une modification MOOP.

Déploiement existant : un push sur `main` déclenche `.github/workflows/pages.yml` et publie le dépôt statique avec GitHub Pages sur recordpicker.app. Les workflows qualité restent indépendants : contrôler leur résultat avant publication. Vérifier ensuite les sept URL publiques, notamment les quatre adresses privacy/support configurées dans l'application.

L'illustration de bobine SVG est originale. Ces pages n'embarquent ni affiche, logo de plateforme, catalogue tiers, script actif, mesure d'audience ni police distante. L'hébergement est soumis à la politique de GitHub, rappelée dans chaque page de confidentialité.

## Lancement iOS du 29 octobre 2026

L’API publique Apple Lookup pour 6826992764 (boutique France) confirme Moovie Picker 1.0.0, disponible sur iPhone et iPad. La version Mac reste en attente de validation, selon la confirmation d’Yves ; aucun bouton Mac n’est ajouté. Les 50 pages Studio utilisent les 44 traductions de `movieStatus`, sans modifier le statut de Book Picker ou Meal Picker. Le générateur et les templates conservent ces liens après régénération. Les pages MOOP FR/EN, le bouton App Store et l’aperçu social reflètent ce lancement iOS uniquement.

Visuel social : `moop/assets/launch-ios-1.0.0.png`, composition AppKit avec l’icône existante, sans affiche de film tierce ni capture d’interface simulée. Facebook, Instagram et TikTok : annonce bilingue FR/EN. YouTube n’est pas utilisé pour une publication d’image.
