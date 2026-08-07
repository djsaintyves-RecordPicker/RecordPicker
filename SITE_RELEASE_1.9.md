# Publication du site Record Picker 1.9

Depuis le 7 août 2026, Record Picker 1.9 est distribué sur macOS. La version 1.8
reste la version distribuée sur iPhone, iPad et Apple Watch jusqu’à confirmation
de leur publication App Store en 1.9.

## Disponibilité mixte actuelle

- Exécuter `python3 Scripts/prepare_site_1_9_preview.py`.
- Présenter `Mac · 1.9` avec le statut localisé « disponible maintenant ».
- Conserver iPhone, iPad et Apple Watch avec le statut localisé « coming soon ».
- Utiliser `1.8 (iOS/iPadOS/watchOS) · 1.9 (macOS)` dans les métadonnées
  structurées et `Record Picker 1.8 · macOS 1.9` dans le pied de page.
- Ne pas retirer le statut disponible de la carte 1.8 : elle reste actuelle sur
  les plateformes mobiles.

## Contenu et vérifications permanentes

- Exécuter `python3 Scripts/prepare_site_1_9_preview.py`.
- Vérifier les 30 variantes linguistiques des pages Accueil, Fonctionnalités et
  Captures. La disponibilité par plateforme doit toujours rester explicite.
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

1. Confirmer la disponibilité publique de la 1.9 sur iPhone, iPad et Apple Watch
   dans App Store Connect et sur les fiches App Store publiques. macOS est déjà
   confirmé depuis le 7 août 2026.
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
