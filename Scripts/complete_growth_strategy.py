#!/usr/bin/env python3
"""Finish the Search Console, evergreen conversion and attribution work."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://recordpicker.app"
ENGLISH_REGIONS = {"en-au", "en-ca", "en-gb"}
PUBLIC_PAGE_PATHS = {
    "",
    "support/",
    "privacy/",
    "screenshots/",
    "readme/",
    "mac-app/",
    "choose-vinyl-record/",
    "random-vinyl-record-picker/",
    "manage-vinyl-collection/",
}


def relative_url(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel == Path("index.html"):
        return "/"
    return "/" + rel.parent.as_posix().strip("/") + "/"


def canonical_for(path: Path) -> str:
    rel_url = relative_url(path)
    parts = rel_url.strip("/").split("/") if rel_url != "/" else []
    if parts and parts[0] in ENGLISH_REGIONS:
        suffix = "/".join(parts[1:])
        return f"{SITE}/en-us/{suffix + '/' if suffix else ''}"
    root_suffix = rel_url.strip("/")
    root_page_key = root_suffix + "/" if root_suffix else ""
    if root_page_key in PUBLIC_PAGE_PATHS:
        suffix = root_suffix
        french_equivalent = ROOT / "fr" / suffix / "index.html" if suffix else ROOT / "fr" / "index.html"
        if french_equivalent.exists():
            return f"{SITE}/fr/{suffix + '/' if suffix else ''}"
    return SITE + rel_url


def locale_campaign(path: Path) -> str:
    rel = path.relative_to(ROOT)
    locale = "fr" if len(rel.parts) == 1 else rel.parts[0]
    if locale in PUBLIC_PAGE_PATHS or locale.endswith(".html"):
        locale = "fr"
    return "RP20_Website_" + re.sub(r"[^A-Za-z0-9]", "_", locale).upper()


def update_structured_data(text: str, old_url: str, canonical: str) -> str:
    def replace_script(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)

        def walk(value: object, depth: int = 0) -> object:
            if isinstance(value, dict):
                result = {}
                for key, item in value.items():
                    should_replace = item == old_url and (
                        (depth == 0 and key in {"url", "@id", "mainEntityOfPage"})
                        or key in {"mainEntityOfPage", "item"}
                    )
                    result[key] = walk(canonical if should_replace else item, depth + 1)
                return result
            if isinstance(value, list):
                return [walk(item, depth + 1) for item in value]
            return value

        encoded = json.dumps(walk(data), ensure_ascii=False, separators=(",", ":"))
        return f'<script type="application/ld+json">{encoded}</script>'

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', replace_script, text, flags=re.DOTALL)


def faq_markup(french: bool, random_picker: bool) -> tuple[str, str]:
    if french and not random_picker:
        heading = "Cinq méthodes rapides pour choisir un disque"
        intro = "Utilisez la méthode qui correspond au temps et à l’envie du moment. Aucune ne vous oblige à abandonner votre propre jugement."
        methods = (
            ("1. Commencer par l’humeur", "Choisissez une ambiance — calme, énergique, nostalgique ou concentrée — puis réduisez la collection à quelques candidats."),
            ("2. Tirer au hasard", "Laissez Random Pick choisir dans toute la collection ou dans un ensemble filtré."),
            ("3. Suivre l’actualité musicale", "Le Disque du jour relie votre collection à une actualité, un anniversaire ou une réédition vérifiée."),
            ("4. Faire tourner la collection", "Favorisez les disques les moins écoutés pour redécouvrir les albums oubliés sur l’étagère."),
            ("5. Poser une seule contrainte", "Une décennie, un genre, un format ou une durée suffit souvent à rendre la décision facile."),
        )
        faqs = (
            ("Comment choisir un vinyle quand j’hésite entre plusieurs disques ?", "Commencez par une seule contrainte, comme l’ambiance, la décennie ou le genre, puis tirez au hasard parmi les résultats."),
            ("Le hasard ne risque-t-il pas de proposer un disque inadapté ?", "Un tirage filtré respecte les favoris, exclusions, genres et autres critères choisis avant la sélection."),
            ("Comment écouter davantage les disques oubliés ?", "Favorisez les albums les moins joués et consultez l’historique pour repérer ceux qui reviennent rarement."),
        )
    elif not french and not random_picker:
        heading = "Five quick ways to choose a record"
        intro = "Use the method that fits your time and mood. None of them takes the final decision away from you."
        methods = (
            ("1. Start with your mood", "Choose a feeling — calm, energetic, nostalgic or focused — and narrow the collection to a few candidates."),
            ("2. Make a random pick", "Let Random Pick choose from the whole collection or from a filtered set."),
            ("3. Follow a timely reason", "Today’s Pick connects your collection with verified music news, anniversaries and reissues."),
            ("4. Rotate the collection", "Give less-played records more weight to rediscover albums that have stayed on the shelf."),
            ("5. Set one constraint", "A decade, genre, format or listening length is often enough to make the decision easy."),
        )
        faqs = (
            ("How do I choose a vinyl record when several albums sound appealing?", "Start with one constraint, such as mood, decade or genre, then make a random pick from the results."),
            ("Can a random picker avoid unsuitable records?", "A filtered random pick can respect favourites, exclusions, genres and other criteria chosen before the selection."),
            ("How can I listen to more forgotten records?", "Give less-played albums more weight and use listening history to spot records that rarely return."),
        )
    elif french:
        heading = "Ce qui rend un tirage aléatoire vraiment utile"
        intro = "Le bon outil ne choisit pas seulement un nombre : il respecte la collection et le contexte d’écoute."
        methods = (
            ("Filtres avant le tirage", "Limitez la sélection par genre, année, format, disponibilité ou favoris."),
            ("Exclusions explicites", "Écartez un disque, un artiste ou une partie de la collection sans les supprimer."),
            ("Variété dans le temps", "Utilisez l’historique et les disques moins écoutés pour éviter les répétitions."),
            ("Résultat modifiable", "Relancez ou annulez le tirage : le hasard reste une aide, pas une obligation."),
        )
        faqs = (
            ("Peut-on tirer un vinyle au hasard sans inclure toute la collection ?", "Oui. Appliquez d’abord des filtres de genre, année, format, disponibilité ou favoris."),
            ("Comment éviter de tirer toujours le même artiste ?", "Utilisez les exclusions et l’historique, ou donnez plus de poids aux disques les moins écoutés."),
            ("Record Picker choisit-il aussi des CD ?", "Oui. La collection peut réunir des vinyles, des CD et des albums favoris."),
        )
    else:
        heading = "What makes a random record picker useful"
        intro = "A useful picker does more than generate a number: it respects the collection and the listening context."
        methods = (
            ("Filters before the pick", "Narrow the selection by genre, year, format, availability or favourites."),
            ("Explicit exclusions", "Leave out a record, artist or part of the collection without deleting it."),
            ("Variety over time", "Use listening history and less-played records to reduce repetition."),
            ("A reversible result", "Pick again or undo the choice: randomness remains a prompt, not an obligation."),
        )
        faqs = (
            ("Can I pick a random vinyl record without using my whole collection?", "Yes. Apply genre, year, format, availability or favourite filters before making the pick."),
            ("How do I avoid picking the same artist repeatedly?", "Use exclusions and listening history, or give less-played records more weight."),
            ("Does Record Picker work with CDs too?", "Yes. A collection can include vinyl records, CDs and favourite albums."),
        )

    cards = "".join(f'<article class="growth-method"><h3>{title}</h3><p>{body}</p></article>' for title, body in methods)
    questions = "".join(f'<details><summary>{question}</summary><p>{answer}</p></details>' for question, answer in faqs)
    section = (
        f'<section class="seo-section growth-answer" data-growth-answer><h2>{heading}</h2><p>{intro}</p>'
        f'<div class="growth-methods">{cards}</div><div class="seo-faq"><h2>{"Questions fréquentes" if french else "Frequently asked questions"}</h2>{questions}</div></section>'
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}}
            for question, answer in faqs
        ],
    }
    script = '<script type="application/ld+json" data-growth-faq>' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>"
    return section, script


def update_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    old_match = re.search(r'<link rel="canonical" href="([^"]+)">', text)
    if not old_match:
        return
    old_url = old_match.group(1)
    canonical = canonical_for(path)
    text = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{canonical}">', text, count=1)
    text = re.sub(r'<meta property="og:url" content="[^"]+">', f'<meta property="og:url" content="{canonical}">', text, count=1)
    text = update_structured_data(text, old_url, canonical)
    text = re.sub(
        r'("publisher":\{"@type":"Organization","name":"Record Picker","url":")[^"]+',
        r'\1https://recordpicker.app/',
        text,
    )

    campaign = locale_campaign(path)
    text = re.sub(
        r'data-app-store-link(?! data-app-store-campaign)',
        f'data-app-store-link data-app-store-campaign="{campaign}"',
        text,
    )
    text = text.replace('data-app-store-campaign="RP20_Website"', f'data-app-store-campaign="{campaign}"')
    text = re.sub(r'site\.js\?v=[^"\']+', 'site.js?v=20260813-indexnow-social', text)
    text = re.sub(r'quality\.css\?v=[^"\']+', 'quality.css?v=20260812-complete-growth', text)

    rel = relative_url(path)
    random_picker = rel.rstrip("/").endswith("random-vinyl-record-picker")
    choose = rel.rstrip("/").endswith("choose-vinyl-record")
    first = rel.strip("/").split("/")[0] if rel != "/" else "fr"
    french = first in {"fr", "fr-ca"} or rel in {"/choose-vinyl-record/", "/random-vinyl-record-picker/"}
    english = first in {"en-us", "en-gb", "en-ca", "en-au"}
    if (choose or random_picker) and (french or english):
        section, schema = faq_markup(french, random_picker)
        if 'data-growth-answer' not in text:
            text = text.replace('<section class="seo-checklist">', section + '<section class="seo-checklist">', 1)
        if 'data-growth-faq' not in text:
            text = text.replace('</head>', schema + '</head>', 1)

    path.write_text(text, encoding="utf-8")


def canonical_urls() -> set[str]:
    urls: set[str] = set()
    for path in ROOT.rglob("index.html"):
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            continue
        match = re.search(r'<link rel="canonical" href="([^"]+)">', path.read_text(encoding="utf-8"))
        if match:
            urls.add(match.group(1))
    return urls


def trim_sitemap(path: Path, allowed: set[str]) -> None:
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"\s*<url>.*?</url>", text, flags=re.DOTALL)
    kept = []
    for block in blocks:
        match = re.search(r"<loc>([^<]+)</loc>", block)
        if match and match.group(1) in allowed:
            block = re.sub(r"<lastmod>[^<]+</lastmod>", "<lastmod>2026-08-12</lastmod>", block)
            kept.append(block.rstrip())
    closing = "</urlset>"
    prefix = text[: text.find("<url>")].rstrip()
    path.write_text(prefix + "\n" + "\n".join(kept) + "\n" + closing + "\n", encoding="utf-8")


def main() -> None:
    pages = [path for path in ROOT.rglob("index.html") if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)]
    for path in pages:
        update_page(path)
    allowed = canonical_urls()
    trim_sitemap(ROOT / "sitemap.xml", allowed)
    trim_sitemap(ROOT / "sitemap-media.xml", allowed)
    print(f"Completed growth strategy across {len(pages)} pages and {len(allowed)} canonical URLs.")


if __name__ == "__main__":
    main()
