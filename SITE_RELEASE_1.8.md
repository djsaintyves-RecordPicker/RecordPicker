# Publication du site Record Picker 1.8

Le site est préparé pour annoncer la version 1.8 sans la présenter prématurément comme disponible. Les pages d’accueil et les pages Fonctionnalités de chaque langue affichent donc une carte « à venir » 1.8, tandis que les métadonnées publiques restent alignées sur la version réellement disponible dans l’App Store.

## Avant la mise en ligne de l’app

- Conserver `softwareVersion` à `1.6` dans les données structurées.
- Conserver les libellés « disponible » et le pied de page sur la version publiée.
- Les quatre visuels proviennent de la build 1.8 (12) : parcours d’accueil,
  qualité de collection, double année originale/édition et présentation Free/Pro.
- Les parcours d’accueil sont localisés en français et en espagnol ; les autres
  langues utilisent les captures en-US pour éviter tout visuel partiellement traduit.
- Les 30 galeries de captures comportent désormais une section 1.8 placée avant
  les aperçus historiques, avec les notes de version localisées disponibles.
- Vérifier avant publication que ces captures correspondent toujours à la build candidate.
- Exécuter `python3 Scripts/prepare_release_1_8.py` puis l’audit du site.

## Dès que la version 1.8 est disponible

- Lancer d’abord `python3 Scripts/publish_release_1_8.py` : ce contrôle en lecture
  seule vérifie les 90 pages préparées et les libellés localisés.
- Après vérification de la présence de la 1.8 sur l’App Store, lancer
  `python3 Scripts/publish_release_1_8.py --apply` pour passer `softwareVersion`,
  les statuts, les cartes de version, les pieds de page et les galeries à
  « disponible ».
- Ajouter la date publique de la version dans l’historique.
- Vérifier les liens App Store locaux, les titres, les descriptions Open Graph et les captures.
- Relancer l’audit intégral avant publication.

Commande d’audit depuis le dépôt de l’app :

```sh
python3 /Users/yvesdurand/Developper/RecordPicker/Scripts/audit_site.py /Users/yvesdurand/Developper/RecordPicker-site
```
