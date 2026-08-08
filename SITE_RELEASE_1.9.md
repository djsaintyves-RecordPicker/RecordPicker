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
- La carte 1.9 est la seule à porter des statuts : macOS « disponible
  maintenant », iPhone/iPad/Apple Watch « coming soon ».
- La carte 1.8 et toutes les versions antérieures conservent leur contenu
  historique, sans libellé de disponibilité ni date de publication visible.

## Contenu et vérifications permanentes

- Considérer `data/release-state.json` comme l’unique source de vérité pour la
  version courante, la version suivante, les plateformes et la phase de
  publication. Ne jamais modifier les statuts directement dans les 297 pages.
- Exécuter `python3 Scripts/prepare_site_1_9_preview.py`.
- Exécuter `python3 Scripts/remove_visible_release_dates.py` et vérifier que les
  30 historiques localisés respectent la règle « version courante + suivante ».
- Vérifier les 33 variantes régionales des pages Accueil, Fonctionnalités et
  Captures. La disponibilité par plateforme doit toujours rester explicite.
- Présenter Today Pick avec les quatre promesses publiques validées : actualité
  musicale vérifiée et anniversaires, rapprochement local, source datée et
  séparation de la liste de souhaits, puis rappels/pertinence/Apple Watch.
- Ne jamais employer de capture de tutoriel, d’onboarding ou de walkthrough.
  Utiliser exclusivement les captures fonctionnelles validées de la build 1.9.
- Générer les formats web et l’image sociale avec
  `python3 Scripts/build_release_1_9_media.py`.
- Lancer `python3 Scripts/publish_release_1_9.py` en lecture seule, puis
  `python3 Scripts/test_release_publication.py`. Le second script effectue deux
  publications successives dans une copie temporaire, audite les deux états et
  garantit que le basculement est complet et idempotent.

## Captures requises avant publication

- Placer uniquement des captures fonctionnelles claires dans
  `assets/screenshots/v19/`.
- Le jeu de publication est constitué de
  `en-us/iphone-today-pick.png`, `en-us/ipad-collection-grid.png` et
  `en-us/mac-today-pick.png`, avec leurs variantes AVIF et WebP. Les PNG restent
  les images de repli et de référence.
- Montrer Today Pick avec la raison du choix et la source datée. Les autres
  captures fonctionnelles 1.9 peuvent compléter la galerie, mais aucune image
  de tutoriel, d’onboarding ou de walkthrough ne doit être utilisée.
- Vérifier qu’aucun nom, emplacement ou élément personnel ne doit être masqué.
- Le script ajoute les captures validées à la galerie 1.9 des 30 pages Captures,
  remplace les visuels courants des 33 accueils et replie l’ancienne galerie
  dans une archive accessible.

## Basculement quand la 1.9 est réellement disponible

1. Confirmer la disponibilité publique de la 1.9 sur iPhone, iPad et Apple Watch
   dans App Store Connect et sur les fiches App Store publiques. macOS est déjà
   confirmé depuis le 7 août 2026.
2. Régénérer et vérifier les médias :

   ```sh
   python3 Scripts/build_release_1_9_media.py
   ```

3. Lancer la simulation complète :

   ```sh
   python3 Scripts/publish_release_1_9.py
   python3 Scripts/test_release_publication.py
   ```

4. Effectuer le basculement protégé :

   ```sh
   python3 Scripts/publish_release_1_9.py --apply --confirm-app-store
   ```

5. Vérifier que la 1.9 devient la version structurée et le pied de page courants,
   que son statut est « disponible », que la 1.10 est annoncée « coming soon »
   sans date ni fonctionnalité inventée, et que la 1.8 ne porte plus de libellé
   « disponible maintenant » dans l’historique.
6. Relancer l’audit intégral, les tests responsive et la vérification des deux
   sitemaps avant commit, push et déploiement.

## Règle permanente pour les versions suivantes

- Une seule version peut être signalée comme « disponible maintenant » : la
  dernière version effectivement distribuée sur la plateforme indiquée.
- La version suivante définie dans le manifeste doit être annoncée avec le
  statut localisé « coming soon » dès que la version courante est intégralement
  distribuée. Elle ne reçoit ni date ni promesse fonctionnelle non confirmée.
- Toutes les versions antérieures restent documentées sans date de publication
  et sans statut « disponible maintenant ».
- Toute évolution du manifeste de versions doit être suivie du générateur, du
  contrôle de toutes les langues et variantes régionales de l’app — notamment
  es-MX, thaï et vietnamien — et de l’audit automatisé avant publication.

Commande d’audit :

```sh
python3 Scripts/audit_site_quality.py
python3 Scripts/test_release_publication.py
```
