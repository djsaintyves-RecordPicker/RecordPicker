# YD : contenu et mesure — 8 octobre 2026

## État Search Console (lecture du compte connecté)

Propriété : https://recordpicker.app/.
Vue d’ensemble : 412 pages indexées, 51 non indexées.
Performances Web, 6 juillet–5 octobre 2026 : 183 clics, 10,6 k impressions,
CTR 1,7 %, position moyenne 6,7. Données affichées mises à jour il y a 30,5 heures.

Requêtes visibles : `record picker` 41 clics / 119 impressions ;
`how to choose the right vinyl record?` 0 clic / 6 145 impressions.
Ce dernier intitulé peut viser l’achat d’un vinyle, plutôt que le choix d’un album
à écouter dans sa collection. Ne pas promettre un gain de trafic sans observation.

## Mesure des parcours

Événements préparés : store_click (apple_ios, apple_mac, microsoft),
playlist_click (apple_music, spotify, deezer), beta_click (android).
Les boutons utilisent exclusivement les attributs Umami, sans second appel JS.
Les liens Apple Store portent la campagne `yd_<page>_<destination>` ; cela permet
l’attribution dans les statistiques Apple lorsqu’elles sont disponibles.
Un clic n’est ni une installation ni une écoute achevée.

Aucun compte Umami ni identifiant de site n’était disponible à la préparation.
Le compte a ensuite été créé par Yves. Site configuré en région EU, identifiant public f162dadd-7a70-47d2-ae74-ccc7b3842adb. La configuration est activée ; vérification en production à consigner après déploiement.
Pour activer : créer le compte Hobby gratuit, ajouter recordpicker.app, relever
le Website ID, renseigner apps/measurement-config.json puis publier. Vérifier un
clic de chaque catégorie dans Events puis retirer les essais des conclusions.
Les pages Snory existantes ne sont pas instrumentées, leur politique demeure intacte.

La configuration exclut query strings et fragments ; aucun formulaire, nom,
e-mail, identifiant de compte, son ou historique applicatif n’est transmis.
Respect de DNT et GPC ; pas de cookies ni localStorage dans ce module.
Avant activation, publier une notice qui nomme Umami, décrit les mesures,
le prestataire et les moyens d’opposition ; vérifier la région de stockage du compte.
Documentation : https://docs.umami.is/docs ; https://umami.is/pricing.

## Suivi à effectuer

Comparer les périodes de 28 jours, hors derniers jours incomplets.
Filtrer chaque URL de guide et d’épisode : indexation, requêtes, impressions,
clics et CTR. Éviter de conclure avec quelques visites. Croiser avec les événements
par destination, sans tenter d’identifier les visiteurs.
Aucun suivi récurrent n’est créé sans demande explicite.

## Sources des playlists

Compte @my_musical_update consulté le 8 octobre : bio « Monthly playlists ».
Aucune story active accessible pour S05E01/S05E02 lors de cette consultation.
Visuels et trois liens déjà fournis par Yves conservés. Texte factuel uniquement ;
ne pas inventer de commentaire personnel sur les morceaux.

## Opposition

Notice Umami ajoutée au pied de page. Une case permet de désactiver la mesure ; seule cette préférence est stockée localement. Les paramètres et fragments sont retirés des URL et seul le domaine du référent est conservé.
