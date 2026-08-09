# Préparation du site Record Picker 2.0

Record Picker 1.9 reste la seule version annoncée comme disponible tant que la
2.0 n’est pas effectivement distribuée sur toutes les plateformes publiques.
La 2.0 est présentée comme « à venir » avec un contenu traduit, mais ses
métadonnées structurées ne remplacent pas celles de la 1.9.

## Source éditoriale

- Les notes App Store 2.0 de l’app constituent la source de vérité pour les
  fonctions et leur sens dans les 32 localisations.
- La formulation française du site est réécrite éditorialement, car une
  traduction littérale de « fair draws » pouvait laisser entendre que le
  tirage était toujours pondéré ou qu’il garantissait une forme d’équité.
- Le Graphe de collection doit être présenté comme une fonction d’analyse sur
  Mac et iPad. Ne pas laisser entendre qu’il est proposé sur iPhone.
- Ne jamais annoncer de transfert de collection : rapprochements et
  personnalisation restent effectués sur l’appareil.

## Préparation de l’aperçu

```sh
python3 Scripts/prepare_site_2_0_preview.py
python3 Scripts/build_release_2_0_media.py
python3 Scripts/add_official_identity_and_press.py
python3 Scripts/audit_release_2_0_semantics.py
python3 Scripts/audit_site_quality.py
```

Le script enrichit les blocs 2.0 des 33 accueils, 33 pages Fonctionnalités et
33 pages Captures. Il vérifie également que les bandeaux et cartouches du
`#RecordPickerChallenge` ne sont pas modifiés.

## Règles avant publication

- Conserver `data/release-state.json` avec `1.9` comme version courante et
  `2.0` comme prochaine version jusqu’à confirmation App Store.
- Ne pas utiliser de capture de tutoriel ou d’onboarding.
- Trois captures fonctionnelles 2.0 anglaises sont prévalidées et préparées
  dans `assets/screenshots/v20/en-us/` : Disque du jour sur iPhone et iPad,
  puis l’accueil Mac présentant les trois modes de sélection. Elles ne doivent
  être rendues publiques sur une page localisée qu’avec une légende traduite et
  après décision explicite sur l’emploi de captures anglaises hors pages anglaises.
- N’ajouter que des captures fonctionnelles réelles de la candidate 2.0,
  détourées et vérifiées aux formats desktop, tablette et mobile.
- Ne pas publier le Graphe de collection avec une collection vide ou des
  relations artificielles.
- Conserver les bandeaux du concours pendant toute sa période officielle.
- Conserver le lien vers le dossier de presse ainsi que les profils officiels
  Instagram, YouTube et Facebook dans le pied de page et dans le balisage
  structuré `sameAs`.
- Avant le basculement, choisir explicitement la version suivante à annoncer ;
  ne jamais inventer automatiquement `2.1` ou `2.0.1`.

## Basculement futur

Le futur script de publication devra refuser de basculer sans les trois preuves
suivantes : disponibilité publique confirmée, captures fonctionnelles 2.0
validées et version suivante explicitement définie. Après le basculement, seule
la 2.0 portera le libellé « disponible maintenant » ; la 1.9 et les versions
antérieures n’auront plus aucun statut ni date visible.
