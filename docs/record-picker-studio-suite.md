# Record Picker Studio — charte de suite

Référence visuelle — 22 octobre 2026.

## Direction

Les quatre apps et leurs sites doivent être reconnaissables comme une même suite. Meal Picker et Record Picker sont les références graphiques ; les autres s’alignent sur leurs composants et leur niveau de finition. Ne pas dégrader MP ou RP pour les ramener vers les autres.

## Identités conservées

- Record Picker : rouge.
- Meal Picker : British Racing Green #004225, papier chaud et neutres culinaires existants.
- My Physical Routine : bleu et rose.
- Snory Teller : ses deux bleus.
- Record Picker Studio : socle neutre commun ; les accents des quatre apps servent à identifier chaque produit, pas à recolorer toute l’interface en rouge.

Les valeurs existantes des palettes sont conservées ; aucun nouveau bleu ou rose arbitraire. Les couleurs fonctionnelles d’état restent distinctes des couleurs de marque, avec un libellé ou un symbole, jamais la couleur seule.

## Grammaire commune

- Typographie système, hiérarchie de titres cohérente et lisible, tailles adaptées à la plateforme et aux préférences d’accessibilité.
- Même rythme d’espacement, alignements précis, largeurs de lecture maîtrisées ; éviter les titres démesurés et les vides inutiles.
- Composants apparentés : navigation, recherche, filtres, cartes, listes, boutons, réglages, états vides, confirmations et accès à l’aide.
- Fond clair chaleureux, surfaces légèrement surélevées, ombres courtes et douces, reflet fin sur les contours. Couleurs franches pour les actions et les identités. Éviter les effets plastiques, les dégradés décoratifs et les halos.
- Icônes et commandes natives cohérentes ; les contrôles et cibles tactiles restent propres à iOS/macOS. Cohérence ne signifie pas reproduire une interface mobile sur ordinateur.
- Une action principale nette par contexte, actions secondaires plus discrètes ; pas de slogans ou d’urgence artificielle.
- Captures et démonstrations authentiques, légendes honnêtes sur langue et version ; aucune interface générée présentée comme réelle.

## Sites et pages produit

Même grille, même typographie et mêmes conventions de boutons, de captures, de pied de page et de liens Studio ↔ app. Chaque page produit utilise sa palette, sans perdre l’identité commune du Studio. Les pages RP restent rouges ; les pages MP vertes, MPR bleues/roses, ST dans leurs deux bleus.

Conserver le contenu utile, les canoniques, hreflang, liens de campagne et événements de mesure. Contrôler les mises en page téléphone/ordinateur, contrastes, navigation clavier et grands caractères. Ne pas uniformiser aveuglément les styles des sous-sites : vérifier leurs parcours et composants avant d’appliquer le socle.

## Ordre d’alignement

1. Formaliser les composants MP/RP existants et la présentation des pages RP/RPS en cours.
2. Aligner les surfaces web MPR/ST et les pages MP sur cette grammaire, en gardant leurs palettes.
3. Aligner les composants natifs MPR/ST sur les modèles MP/RP, écran par écran, après audit de leurs sources et tests.

Cette charte fixe une direction. Elle ne prétend pas que les quatre interfaces natives ont déjà été refaites.


## Composants web

Surfaces de lecture en papier chaud ; texte foncé, contrastes lisibles et largeurs maîtrisées. Commandes principales de 52 px minimum, rayon de 14 px ; commandes compactes de navigation de 44 px minimum. Les cartes partagent un rayon de 16 à 18 px et une ombre contenue. Snory Teller conserve son ambiance nocturne et ses deux bleus. Les captures restent authentiques et leur version est indiquée.

## Relief et mouvement — déploiement web

La version commune utilise `assets/css/suite-experience.css` et `assets/js/suite-experience.js`. Les anciennes feuilles d’essai de l’accueil français ne sont plus chargées. Les cartes restent sans bordure ; les ombres portent vers le bas et la droite, avec un soulèvement de 4 px au survol des cartes et de 2 px sur les commandes. Les captures flottent directement au-dessus du fond, sans cadre crème. Snory Teller adapte les ombres à son fond nocturne.

Les boutons apparaissent dans l’ordre de lecture. Les pochettes, captures et commandes rejouent leur entrée après une sortie complète de l’écran. Le symbole RPS, « Record Picker » et « Studio » apparaissent en trois temps dans les accueils localisés du Studio. Le réglage de réduction des mouvements désactive ces animations ; sans JavaScript les contenus restent visibles et les liens fonctionnent. Aucun texte de lecture ou de confidentialité n’est masqué par défaut.

Une impulsion tactile de 8 ms est demandée uniquement après une activation tactile réelle et sur les navigateurs compatibles. Safari iOS ne fournit pas cette API ; aucun contournement n’est ajouté. Le script ne transmet aucune donnée et ne modifie pas les destinations des liens.

Après une régénération de pages, exécuter `python3 Scripts/rollout_suite_experience.py` avant les audits. Le script est idempotent, exclut les alias de redirection et les fichiers de vérification des moteurs, et conserve l’attribution statique des sous-sites qui ne chargeaient pas le script de campagne. Les pages légales restent sobres ; aucun avis de disponibilité ou de prix n’est changé par ce traitement.
