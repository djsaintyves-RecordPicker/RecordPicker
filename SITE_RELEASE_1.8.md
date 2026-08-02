# Publication du site Record Picker 1.8

Le site est préparé pour annoncer la version 1.8 sans la présenter prématurément comme disponible. Les pages d’accueil et les pages Fonctionnalités de chaque langue affichent donc une carte « à venir » 1.8, tandis que les métadonnées publiques restent alignées sur la version réellement disponible dans l’App Store.

## Avant la mise en ligne de l’app

- Conserver `softwareVersion` à `1.6` dans les données structurées.
- Conserver les libellés « disponible » et le pied de page sur la version publiée.
- Vérifier que les quatre visuels 1.8 correspondent encore à la build candidate.
- Exécuter `python3 Scripts/prepare_release_1_8.py` puis l’audit du site.

## Dès que la version 1.8 est disponible

- Passer `softwareVersion` et les textes de disponibilité à `1.8`.
- Transformer la carte 1.8 de préversion en version disponible et ajouter la date de publication.
- Mettre à jour le pied de page et les introductions des pages Fonctionnalités.
- Vérifier les liens App Store locaux, les titres, les descriptions Open Graph et les captures.
- Relancer l’audit intégral avant publication.

Commande d’audit depuis le dépôt de l’app :

```sh
python3 /Users/yvesdurand/Developper/RecordPicker/Scripts/audit_site.py /Users/yvesdurand/Developper/RecordPicker-site
```

