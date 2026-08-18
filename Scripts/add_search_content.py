#!/usr/bin/env python3
"""Build the x-default homepage and focused English/French search guides."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://recordpicker.app"

GUIDES = {
    "catalog-vinyl-collection-app": {
        "en": ("Vinyl Collection Catalogue App", "Build a useful vinyl catalogue on iPhone, iPad and Mac", "Record artist, album, pressing, format, location and listening history in one private catalogue. Import a Discogs CSV or add records manually, then search the collection before buying.", ["Catalogue vinyl and CDs in the same collection", "Keep pressing details, notes and shelf location", "Search quickly at home or in a record shop"]),
        "fr": ("Application pour cataloguer une collection de vinyles", "Créez un catalogue utile sur iPhone, iPad et Mac", "Conservez artiste, album, pressage, format, emplacement et historique d’écoute dans un catalogue privé. Importez un CSV Discogs ou ajoutez les disques manuellement, puis retrouvez-les avant un achat.", ["Cataloguez vinyles et CD ensemble", "Conservez pressage, notes et emplacement", "Recherchez rapidement chez vous ou en disquaire"]),
    },
    "import-discogs-csv": {
        "en": ("Import a Discogs CSV into a Record Collection App", "Move your Discogs collection without starting again", "Export your collection from Discogs as CSV, import it into Record Picker and review the matched records. Your catalogue stays useful even when you want a calmer, private app for everyday listening.", ["Start from an existing Discogs export", "Review imported releases and cover art", "Keep a fresh backup before major changes"]),
        "fr": ("Importer un CSV Discogs dans une app de collection", "Reprenez votre collection Discogs sans repartir de zéro", "Exportez votre collection Discogs en CSV, importez-la dans Record Picker et vérifiez les disques reconnus. Votre catalogue reste pratique dans une app privée pensée pour l’écoute quotidienne.", ["Partez d’un export Discogs existant", "Vérifiez les éditions et les pochettes importées", "Gardez une sauvegarde avant toute modification importante"]),
    },
    "vinyl-duplicate-checker": {
        "en": ("Vinyl Duplicate Checker for Record Shops", "Check your catalogue before buying the same record twice", "Search by artist, album or barcode while browsing a shop or record fair. A clear catalogue helps distinguish a true duplicate from another pressing you intentionally want.", ["Search the collection in seconds", "Compare format and pressing details", "Avoid accidental duplicates without blocking variants"]),
        "fr": ("Vérifier les doublons de vinyles avant un achat", "Consultez votre catalogue avant de racheter le même disque", "Recherchez un artiste, un album ou un code-barres chez un disquaire ou dans une convention. Un catalogue précis distingue un vrai doublon d’un autre pressage voulu.", ["Recherchez la collection en quelques secondes", "Comparez format et détails de pressage", "Évitez les doublons accidentels sans exclure les variantes"]),
    },
    "cd-collection-app": {
        "en": ("CD Collection Catalogue App", "Catalogue CDs and vinyl together", "Record Picker is not limited to vinyl. Keep CDs, box sets and records in one searchable collection, with formats, notes, favourites, listening history and private iCloud sync.", ["Manage CDs, vinyl and box sets", "Use one search across every format", "Choose forgotten albums with Random Pick"]),
        "fr": ("Application pour cataloguer une collection de CD", "Cataloguez CD et vinyles dans la même collection", "Record Picker ne se limite pas au vinyle. Regroupez CD, coffrets et disques dans une collection consultable, avec formats, notes, favoris, historique d’écoute et synchronisation iCloud privée.", ["Gérez CD, vinyles et coffrets", "Utilisez une seule recherche pour tous les formats", "Retrouvez des albums oubliés avec Random Pick"]),
    },
    "classical-music-catalogue-app": {
        "en": ("Classical Music Collection Catalogue App", "Keep works, performers and editions findable", "Classical collections need more than an album title. Use detailed notes and searchable metadata to keep composers, conductors, orchestras, soloists, labels and formats easy to retrieve.", ["Describe composer, work and performers", "Differentiate conductors, orchestras and editions", "Keep box sets and multi-disc releases organised"]),
        "fr": ("Application de catalogage pour la musique classique", "Retrouvez facilement œuvres, interprètes et éditions", "Une collection classique demande plus qu’un titre d’album. Les notes détaillées et métadonnées consultables permettent de retrouver compositeurs, chefs, orchestres, solistes, labels et formats.", ["Décrivez compositeur, œuvre et interprètes", "Distinguez chefs, orchestres et éditions", "Organisez coffrets et parutions multidisques"]),
    },
    "discogs-companion-app": {
        "en": ("A Private Companion App for Discogs Collectors", "Use Discogs data in a calmer listening workflow", "Keep Discogs as a powerful release database and marketplace, while using Record Picker to browse, enrich and actually listen to your collection. Import by CSV and keep your catalogue private.", ["Import the collection you already built", "Add personal notes and listening history", "Choose what to play without a marketplace feed"]),
        "fr": ("Une app complémentaire à Discogs pour les collectionneurs", "Utilisez les données Discogs dans un parcours centré sur l’écoute", "Gardez Discogs pour sa base d’éditions et sa marketplace, et utilisez Record Picker pour parcourir, enrichir et écouter réellement votre collection. Importez par CSV et conservez un catalogue privé.", ["Importez la collection déjà constituée", "Ajoutez notes personnelles et historique d’écoute", "Choisissez quoi écouter sans fil de marketplace"]),
    },
}


def replace_metadata(text: str, title: str, description: str, canonical: str) -> str:
    for pattern, replacement in (
        (r"<title>.*?</title>", f"<title>{escape(title)}</title>"),
        (r'(<meta name="description" content=")[^"]*(">)', rf"\g<1>{escape(description, quote=True)}\g<2>"),
        (r'(<meta property="og:title" content=")[^"]*(">)', rf"\g<1>{escape(title, quote=True)}\g<2>"),
        (r'(<meta property="og:description" content=")[^"]*(">)', rf"\g<1>{escape(description, quote=True)}\g<2>"),
        (r'(<meta name="twitter:title" content=")[^"]*(">)', rf"\g<1>{escape(title, quote=True)}\g<2>"),
        (r'(<meta name="twitter:description" content=")[^"]*(">)', rf"\g<1>{escape(description, quote=True)}\g<2>"),
        (r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{canonical}">'),
        (r'<meta property="og:url" content="[^"]+">', f'<meta property="og:url" content="{canonical}">'),
    ):
        text = re.sub(pattern, replacement, text, count=1, flags=re.DOTALL)
    return text


def international_home() -> None:
    text = (ROOT / "en-us" / "index.html").read_text(encoding="utf-8")
    text = text.replace('<html lang="en-US">', '<html lang="en">')
    text = text.replace(' data-lang="en-us" data-page-lang="en-us" data-static-locale', ' data-lang="en-us" data-page-lang="x-default"')
    text = text.replace("https://recordpicker.app/en-us/", "https://recordpicker.app/")
    text = text.replace('href="../', 'href="').replace('src="../', 'src="')
    text = text.replace('../assets/', 'assets/')
    text = text.replace('/en-us/#recordpicker-challenge', '/#recordpicker-challenge')
    text = replace_metadata(text, "Record Picker — Catalogue, Choose and Rediscover Your Records", "Catalogue vinyl records and CDs, check duplicates before buying, import a Discogs CSV and choose what to play. Private, ad-free and available in 32 localizations.", SITE + "/")
    text = re.sub(r'<meta property="og:locale" content="[^"]+">', '<meta property="og:locale" content="en_US">', text, count=1)
    (ROOT / "index.html").write_text(text, encoding="utf-8")


def guide_main(lang: str, slug: str, data: tuple[str, str, str, list[str]]) -> str:
    title, heading, intro, bullets = data
    back = "Aller à Record Picker" if lang == "fr" else "Open Record Picker"
    why = "Ce que ce parcours apporte" if lang == "fr" else "What this workflow gives you"
    related = "Guides associés" if lang == "fr" else "Related guides"
    links = []
    for other_slug, other in GUIDES.items():
        if other_slug != slug:
            links.append(f'<a class="seo-link-card" href="../{other_slug}/"><strong>{escape(other[lang][0])}</strong></a>')
    items = "".join(f"<li>{escape(item)}</li>" for item in bullets)
    return f'''<main id="main-content" class="doc-page"><section class="doc-hero"><p class="eyebrow">Record Picker</p><h1>{escape(title)}</h1><p class="lead">{escape(heading)}</p><p>{escape(intro)}</p><div class="hero-actions"><a class="button primary" href="../#download" data-app-store-link>{back}</a></div></section><section class="doc-content"><h2>{why}</h2><ul>{items}</ul><p>{escape(intro)}</p></section><section class="seo-section"><h2>{related}</h2><div class="seo-links">{"".join(links)}</div></section></main>'''


def build_guides() -> None:
    for locale, lang in (("en-us", "en"), ("fr", "fr")):
        source = (ROOT / locale / "manage-vinyl-collection" / "index.html").read_text(encoding="utf-8")
        source_url = SITE + f"/{locale}/manage-vinyl-collection/"
        for slug, translations in GUIDES.items():
            title, _heading, intro, _bullets = translations[lang]
            canonical = SITE + f"/{locale}/{slug}/"
            text = source.replace(source_url, canonical)
            text = replace_metadata(text, title + " — Record Picker", intro, canonical)
            text = re.sub(r'<main\b.*?</main>', guide_main(lang, slug, translations[lang]), text, count=1, flags=re.DOTALL)
            alternates = (f'<link rel="alternate" hreflang="en-US" href="{SITE}/en-us/{slug}/">'
                          f'<link rel="alternate" hreflang="fr-FR" href="{SITE}/fr/{slug}/">'
                          f'<link rel="alternate" hreflang="x-default" href="{SITE}/en-us/{slug}/">')
            text = re.sub(r'(?:<link rel="alternate" hreflang="[^"]+" href="[^"]+">)+', alternates, text, count=1)
            # Keep the template schema useful, but identify the new guide accurately.
            text = text.replace('"headline":"Gérer une collection de vinyles avec Record Picker"', f'"headline":{json.dumps(title, ensure_ascii=False)}')
            text = text.replace('"headline":"Manage a Vinyl Record Collection with Record Picker"', f'"headline":{json.dumps(title, ensure_ascii=False)}')
            destination = ROOT / locale / slug / "index.html"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text, encoding="utf-8")


def main() -> None:
    international_home()
    build_guides()
    print("Built one x-default homepage and 12 focused search guides.")


if __name__ == "__main__":
    main()
