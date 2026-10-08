# Suivi de l’indexation Yves Durand et Dulpi

Contrôle du 8 octobre 2026 dans Google Search Console et Bing Webmaster Tools,
propriété https://recordpicker.app/. Les pages YD française et anglaise sont
indexées par Google. Dulpi attend l’exploration. Bing connaît la page YD française
sans l’avoir explorée. Les 100 pages localisées sont présentes dans les sitemaps ;
cela ne confirme pas leur indexation.

## État vérifié

| URL | Google | Bing |
| --- | --- | --- |
| https://recordpicker.app/fr/apps/ | Indexée ; dernière exploration 8 octobre 11:58:22, Googlebot smartphone ; récupération réussie, indexation autorisée, canonique inspectée retenue | Découverte le 8 octobre, non explorée ; demande d’indexation confirmée |
| https://recordpicker.app/apps/ | Indexée | À inspecter lors du suivi |
| https://recordpicker.app/fr/apps/dulpi/ | URL inconnue ; demande d’indexation confirmée, ajoutée à la file prioritaire | Découverte le 8 octobre, non explorée ; demande d’indexation confirmée |
| https://recordpicker.app/apps/dulpi/ | URL inconnue ; demande d’indexation confirmée, ajoutée à la file prioritaire | À inspecter lors du suivi |

Le rapport global Google affiche 412 pages indexées et 51 non indexées pour
l’ensemble du domaine. Ces totaux ne mesurent pas la couverture des 100 nouvelles
pages de la page YD et de Dulpi.

## Sitemaps et soumissions

Google affiche ses trois sitemaps en succès avant la relance. Sa dernière lecture
du sitemap principal date du 1er octobre, avec 432 pages découvertes. Le sitemap
principal a été soumis à nouveau le 8 octobre et Google a confirmé « Sitemap
envoyé ». La prise en compte du nouvel inventaire reste à vérifier au suivi.

Bing affiche trois sitemaps connus, zéro erreur et zéro avertissement.
Le sitemap principal a été soumis à nouveau le 8 octobre ; son état est
Processing, sa précédente exploration date du 6 octobre et son ancien inventaire
contient 432 URL. Le sitemap média compte 241 URL et celui de Snory Teller 8 URL,
tous deux en succès. Les 681 URL découvertes ne sont pas un compteur de pages
indexées et peuvent provenir de sitemaps qui se recoupent.

Le déploiement transmet aussi les URL publiques à IndexNow. Une réponse HTTP 200
confirme la réception, pas l’exploration ou l’indexation.

## Prochain contrôle

Suivi Codex quotidien à 9 h 30, heure de Paris, dans cette conversation.
Automation : suivre-l-indexation-de-la-page-yves-durand.
Vérifier les quatre pages prioritaires, le traitement des sitemaps et un
échantillon tournant des autres langues du manifeste. Documenter chaque résultat
avec sa date et sa source. Ne pas resoumettre quotidiennement les mêmes pages.
Une recherche site: sert uniquement de signal secondaire.
Notifier seulement un progrès concret, un problème important ou une intervention
nécessaire ; rester silencieux sur un état inchangé. Arrêter le suivi une fois
les quatre pages prioritaires indexées dans les deux moteurs et les sitemaps
traités sans erreur.

## Publication des corrections

Commit 04aeceb30 publié le 8 octobre. Validation du site, déploiement GitHub Pages
et build Pages terminés avec succès. Les corrections allemandes ont été relues
sur la réponse HTML publique après déploiement.
