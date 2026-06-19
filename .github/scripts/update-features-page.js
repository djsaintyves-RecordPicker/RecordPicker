const fs = require('fs');

const workflow = '.github/workflows/update-features-page.yml';
const script = '.github/scripts/update-features-page.js';
const appName = 'Record Picker';
const appStoreUrl = 'https://apps.apple.com/fr/app/recordpicker/id6780422305';
const contactEmail = 'djsaintyves@mac.com';

const replaceAll = (value, from, to) => value.split(from).join(to);
const esc = (value) => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;');
const languagePair = (fr, en) => `<span class="lang-fr">${fr}</span><span class="lang-en">${en}</span>`;

const featureGroups = [
  {
    titleFr: 'Catalogue musical complet',
    titleEn: 'Complete music catalog',
    bodyFr: 'Construisez une collection exploitable, même si vos données de départ sont incomplètes.',
    bodyEn: 'Build a usable collection, even when the data you start from is incomplete.',
    items: [
      ['Import de collection CSV', 'CSV collection import'],
      ['Ajout manuel de vinyles, CD et albums', 'Manual vinyl, CD, and album entry'],
      ["Scan de codes-barres avec l'appareil photo", 'Barcode scanning with the camera'],
      ['Recherche de métadonnées avec MusicBrainz et Discogs', 'Metadata lookup with MusicBrainz and Discogs'],
      ['Fiches disque éditables pour compléter les informations', 'Editable record detail sheets for completing information'],
    ],
  },
  {
    titleFr: 'Pochettes et données visuelles',
    titleEn: 'Artwork and visual data',
    bodyFr: 'Gardez une collection agréable à parcourir, avec des pochettes récupérées ou choisies par vous.',
    bodyEn: 'Keep the collection pleasant to browse with artwork you retrieve or choose yourself.',
    items: [
      ['Recherche de pochettes via Cover Art Archive', 'Artwork lookup through Cover Art Archive'],
      ['Import manuel depuis Photos ou Fichiers', 'Manual import from Photos or Files'],
      ['Recherche Internet quand une illustration manque', 'Web lookup when artwork is missing'],
      ["Restauration de l'illustration d'origine", 'Restore original artwork'],
      ['Contrôles de qualité pour les pochettes et données manquantes', 'Quality checks for missing artwork and data'],
    ],
  },
  {
    titleFr: 'Tirage intelligent',
    titleEn: 'Smart picking',
    bodyFr: 'Choisissez le prochain disque sans perdre le contrôle sur ce qui peut sortir du bac.',
    bodyEn: 'Choose the next record without losing control over what can be drawn from the bin.',
    items: [
      ['Tirage aléatoire animé', 'Animated random draw'],
      ['Filtrage par années, genres, styles, favoris et disponibilité', 'Filtering by years, genres, styles, favorites, and availability'],
      ['Exclusion du même artiste', 'Same-artist exclusion'],
      ['Favoriser les favoris ou limiter le tirage aux favoris', 'Favor favorites or limit picks to favorites'],
      ['Exclusions temporaires de disques, artistes ou critères', 'Temporary exclusions for records, artists, or criteria'],
    ],
  },
  {
    titleFr: 'Ambiances et écoute',
    titleEn: 'Moods and playback',
    bodyFr: "Record Picker peut orienter le choix selon l'humeur du moment et garder une trace de ce que vous écoutez.",
    bodyEn: 'Record Picker can steer choices by mood and keep a trail of what you play.',
    items: [
      ['Choix par ambiance avec modèles Apple locaux quand ils sont disponibles', 'Mood-based picking with local Apple models when available'],
      ['Calcul local à partir des métadonnées quand les modèles ne sont pas disponibles', 'Local metadata-based matching when models are unavailable'],
      ['Historique récent des disques tirés ou écoutés', 'Recent history of drawn or played records'],
      ['Lecture via Apple Music quand elle est disponible', 'Playback through Apple Music when available'],
      ['Liste de souhaits pour garder les envies à portée de main', 'Wishlist for keeping wanted records close at hand'],
    ],
  },
  {
    titleFr: 'Navigation et analyse de collection',
    titleEn: 'Browsing and collection insight',
    bodyFr: "Parcourez, vérifiez et comprenez votre collection sans quitter l'app.",
    bodyEn: 'Browse, check, and understand your collection without leaving the app.',
    items: [
      ['Bac à disques avec recherche, tri et filtres', 'Record bin with search, sorting, and filters'],
      ['Vues adaptées iPhone et iPad', 'Views adapted for iPhone and iPad'],
      ['Grandes pochettes et listes rapides', 'Large covers and fast lists'],
      ['Statistiques de collection, tirages, favoris et exclusions', 'Collection, draw, favorite, and exclusion statistics'],
      ['Détection des pistes, formats, labels, dates et données manquantes', 'Detection of missing tracks, formats, labels, dates, and data'],
    ],
  },
  {
    titleFr: 'Sauvegarde, automatisation et confidentialité',
    titleEn: 'Backup, automation, and privacy',
    bodyFr: 'Les outils avancés restent sous votre contrôle, avec une collection stockée localement.',
    bodyEn: 'Advanced tools stay under your control, with the collection stored locally.',
    items: [
      ['Sauvegarde et restauration de collection', 'Collection backup and restore'],
      ['Exports CSV et JSON lisibles', 'Readable CSV and JSON exports'],
      ['Raccourcis Siri et actions système', 'Siri Shortcuts and system actions'],
      ['Compagnon Apple Watch', 'Apple Watch companion'],
      ['Aucun compte utilisateur, aucune publicité, pas de serveur Record Picker pour stocker votre collection', 'No user account, no advertising, and no Record Picker server storing your collection'],
    ],
  },
];

function featureCards() {
  return featureGroups.map((group) => {
    const items = group.items.map(([fr, en]) => `<li>${languagePair(esc(fr), esc(en))}</li>`).join('');
    return `<article class="card feature-card"><h3>${languagePair(esc(group.titleFr), esc(group.titleEn))}</h3><p>${languagePair(esc(group.bodyFr), esc(group.bodyEn))}</p><ul class="feature-list">${items}</ul></article>`;
  }).join('');
}

function updateSharedLabels(html) {
  html = replaceAll(html, '<span class="lang-fr">Guide</span><span class="lang-en">Guide</span>', '<span class="lang-fr">Fonctionnalités</span><span class="lang-en">Features</span>');
  html = replaceAll(html, 'Guide - Record Picker', 'Fonctionnalités / Features - Record Picker');
  html = replaceAll(html, 'Record Picker Guide', 'Features - Record Picker');
  html = replaceAll(html, 'Record Picker guide and feature overview.', 'Record Picker features and app overview.');
  return html;
}

const htmlFiles = ['index.html', 'support/index.html', 'privacy/index.html', 'screenshots/index.html'];
for (const file of htmlFiles) {
  if (!fs.existsSync(file)) continue;
  fs.writeFileSync(file, updateSharedLabels(fs.readFileSync(file, 'utf8')));
}

let readmeHtml = fs.readFileSync('readme/index.html', 'utf8');
readmeHtml = updateSharedLabels(readmeHtml);
readmeHtml = replaceAll(readmeHtml, '<title>Fonctionnalités / Features - Record Picker</title>', '<title>Fonctionnalités / Features - Record Picker</title>');
readmeHtml = replaceAll(readmeHtml, 'content="Fonctionnalités / Features - Record Picker"', 'content="Fonctionnalités / Features - Record Picker"');
readmeHtml = replaceAll(readmeHtml, '<h1><span class="lang-fr">Fonctionnalités / Features - Record Picker</span><span class="lang-en">Features - Record Picker</span></h1>', '<h1><span class="lang-fr">Fonctionnalités - Record Picker</span><span class="lang-en">Features - Record Picker</span></h1>');
readmeHtml = replaceAll(readmeHtml, '<h1><span class="lang-fr">Guide - Record Picker</span><span class="lang-en">Features - Record Picker</span></h1>', '<h1><span class="lang-fr">Fonctionnalités - Record Picker</span><span class="lang-en">Features - Record Picker</span></h1>');
readmeHtml = replaceAll(readmeHtml, '<h1><span class="lang-fr">Guide - Record Picker</span><span class="lang-en">Record Picker Guide</span></h1>', '<h1><span class="lang-fr">Fonctionnalités - Record Picker</span><span class="lang-en">Features - Record Picker</span></h1>');
readmeHtml = readmeHtml.replace(/<p class="doc-tagline">.*?<\/p>/, `<p class="doc-tagline">${languagePair('Tout ce que Record Picker sait faire pour votre collection.', 'Everything Record Picker can do for your collection.')}</p>`);

const historyStart = readmeHtml.indexOf('<h2><span class="lang-fr">Historique App Store');
const historyEnd = readmeHtml.indexOf('</section></main>', historyStart);
const historyHtml = historyStart >= 0 && historyEnd >= 0 ? readmeHtml.slice(historyStart, historyEnd) : '';
const mainStart = readmeHtml.indexOf('<main class="doc-shell">');
const mainEnd = readmeHtml.indexOf('</main>', mainStart) + '</main>'.length;
const newMain = `<main class="doc-shell"><section class="doc-hero"><p class="glass-pill eyebrow">${appName}</p><h1>${languagePair('Fonctionnalités - Record Picker', 'Features - Record Picker')}</h1><p class="doc-tagline">${languagePair('Tout ce que Record Picker sait faire pour votre collection.', 'Everything Record Picker can do for your collection.')}</p><div class="doc-actions"><a class="button primary" href="${appStoreUrl}">App Store</a><a class="button glass" href="mailto:${contactEmail}">${languagePair("Contacter l'assistance", 'Contact support')}</a></div></section><section class="doc-content"><p class="doc-meta">Record Picker v1.2</p><p class="lead">${languagePair('Record Picker réunit catalogue, tirage intelligent, enrichissement des données, statistiques, sauvegardes et compagnons système pour redonner vie à votre collection musicale.', 'Record Picker brings together cataloging, smart picking, data enrichment, statistics, backups, and system companions to bring your music collection back to life.')}</p><p>${languagePair("La page ci-dessous présente les fonctionnalités principales de la version 1.2, de l'import initial jusqu'au choix du disque, en passant par les pochettes, les filtres, les contrôles de qualité et les outils d'export.", 'The page below presents the main features in version 1.2, from the first import to the next record pick, including artwork, filters, data quality checks, and export tools.')}</p><h2>${languagePair('Fonctionnalités', 'Features')}</h2><div class="doc-grid feature-grid">${featureCards()}</div>${historyHtml}</section></main>`;
if (mainStart >= 0 && mainEnd > mainStart) {
  readmeHtml = readmeHtml.slice(0, mainStart) + newMain + readmeHtml.slice(mainEnd);
}
readmeHtml = updateSharedLabels(readmeHtml);
fs.writeFileSync('readme/index.html', readmeHtml);

if (fs.existsSync('readme.html')) {
  let redirect = fs.readFileSync('readme.html', 'utf8');
  redirect = updateSharedLabels(redirect);
  redirect = replaceAll(redirect, 'Guide - Record Picker', 'Fonctionnalités / Features - Record Picker');
  fs.writeFileSync('readme.html', redirect);
}

if (fs.existsSync('README.md')) {
  let readme = fs.readFileSync('README.md', 'utf8');
  readme = replaceAll(readme, 'guide pages', 'features pages');
  readme = replaceAll(readme, 'Guide page: ./readme/', 'Features page: ./readme/');
  fs.writeFileSync('README.md', readme);
}

if (fs.existsSync('styles.css')) {
  let css = fs.readFileSync('styles.css', 'utf8');
  if (!css.includes('recordpicker-feature-grid')) {
    css += '\n/* recordpicker-feature-grid */.feature-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.feature-card p{margin-top:12px}@media (max-width:1040px){.feature-grid{grid-template-columns:1fr}}\n';
    fs.writeFileSync('styles.css', css);
  }
}

if (fs.existsSync(workflow)) fs.unlinkSync(workflow);
if (fs.existsSync(script)) fs.unlinkSync(script);
