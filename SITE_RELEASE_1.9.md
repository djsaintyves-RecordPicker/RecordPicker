# Publication du site Record Picker 1.9

Le site peut annoncer Record Picker 1.9 avant sa sortie, mais la version 1.8
reste la seule version présentée comme disponible jusqu’à confirmation de la
publication App Store sur iPhone, iPad, Apple Watch et Mac.

## Annonce avant publication

- Exécuter `python3 Scripts/prepare_site_1_9_preview.py`.
- Vérifier les 30 variantes linguistiques des pages Accueil, Fonctionnalités et
  Captures. La 1.9 doit toujours porter le statut localisé « coming soon ».
- Conserver `softwareVersion` à `1.8`, le pied de page sur `Record Picker v1.8`
  et les liens App Store actuels.
- Présenter Today Pick avec les quatre promesses publiques validées : actualité
  musicale vérifiée et anniversaires, rapprochement local, source datée et
  séparation de la liste de souhaits, puis rappels/pertinence/Apple Watch.
- Ne jamais employer de capture de tutoriel, d’onboarding ou de walkthrough.
  Tant qu’aucune vraie capture fonctionnelle Today Pick n’est validée, conserver
  l’illustration éditoriale en HTML/CSS.
- Lancer `python3 Scripts/publish_release_1_9.py` en lecture seule. Le script
  doit annoncer que 90 pages localisées sont prêtes et signaler séparément si
  les captures 1.9 réelles manquent encore.

## Captures requises avant publication

- Placer uniquement des captures fonctionnelles claires dans
  `assets/screenshots/v19/`.
- Montrer au minimum Today Pick sur iPhone ou iPad, avec la raison du choix et
  la source datée. Ajouter Mac et Apple Watch si les builds finales le permettent.
- Vérifier qu’aucun nom, emplacement ou élément personnel ne doit être masqué.
- Ajouter les captures validées à la galerie 1.9 des 30 pages Captures.

## Basculement quand la 1.9 est réellement disponible

1. Confirmer la disponibilité publique de la 1.9 sur toutes les plateformes
   annoncées dans App Store Connect et sur les fiches App Store publiques.
2. Ajouter et vérifier les captures fonctionnelles finales sous
   `assets/screenshots/v19/`.
3. Lancer la simulation :

   ```sh
   python3 Scripts/publish_release_1_9.py
   ```

4. Effectuer le basculement protégé :

   ```sh
   python3 Scripts/publish_release_1_9.py --apply --confirm-app-store
   ```

5. Vérifier que la 1.9 devient la version structurée et le pied de page courants,
   que son statut est « disponible », et que la 1.8 ne porte plus de libellé
   « disponible maintenant » dans l’historique.
6. Relancer l’audit intégral, les tests responsive et la vérification des deux
   sitemaps avant commit, push et déploiement.

Commande d’audit :

```sh
python3 /Users/yvesdurand/Developper/RecordPicker/Scripts/audit_site.py /Users/yvesdurand/Developper/RecordPicker-site
```
