#!/usr/bin/env python3
"""Apply the August 2026 search and conversion audit to the public site."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
FRENCH_HOMES = (ROOT / "index.html", ROOT / "fr" / "index.html", ROOT / "fr-ca" / "index.html")
ENGLISH_HOMES = tuple(ROOT / locale / "index.html" for locale in ("en-au", "en-ca", "en-gb", "en-us"))


def replace_meta(text: str, title: str, description: str) -> str:
    replacements = (
        (r"<title>.*?</title>", f"<title>{title}</title>"),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{description}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">'),
        (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{description}">'),
        (r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{title}">'),
        (r'<meta name="twitter:image:alt" content="[^"]*">', f'<meta name="twitter:image:alt" content="{title}">'),
        (r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{title}">'),
        (r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{description}">'),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, count=1)
    return text


def track_store_links(text: str) -> str:
    text = re.sub(
        r'data-app-store-link(?! data-app-store-campaign)',
        'data-app-store-link data-app-store-campaign="RP20_Website"',
        text,
    )
    text = re.sub(r'site\.js\?v=[^"\']+', 'site.js?v=20260812-growth-funnel', text)
    text = re.sub(r'quality\.css\?v=[^"\']+', 'quality.css?v=20260812-growth-funnel', text)
    return text


def challenge_copy(french: bool, figure: str) -> str:
    if french:
        kicker = '<bdi dir="ltr">#RecordPickerChallenge</bdi> · jusqu’au 22 août · 70 codes Pro à gagner'
        title = "Télécharge. Fais trois choix. Partage ton favori."
        lead = "Record Picker est gratuit jusqu’à 100 disques. Cinq participants gagnent Pro à vie chaque jour."
        steps = (
            "Ajoute au moins cinq disques",
            "Commence par Random Pick, puis essaie Disque du jour et Mood Pick",
            'Termine en partageant ton favori avec <bdi dir="ltr">#RecordPickerChallenge</bdi>',
        )
        download = "Télécharge gratuitement et participe"
        instagram = "Voir le challenge sur Instagram"
        rules = "Règlement officiel"
        legal = "Aucun achat, aucune note et aucun avis App Store ne sont requis. Consulte le règlement pour les conditions d’éligibilité et de sélection."
    else:
        kicker = '<bdi dir="ltr">#RecordPickerChallenge</bdi> · until 22 August · 70 Pro codes to win'
        title = "Download. Make three picks. Share your favourite."
        lead = "Record Picker is free for collections of up to 100 records. Five participants win Lifetime Pro every day."
        steps = (
            "Add at least five records",
            "Start with Random Pick, then try Today’s Pick and Mood Pick",
            'Finish by sharing your favourite with <bdi dir="ltr">#RecordPickerChallenge</bdi>',
        )
        download = "Download free and take part"
        instagram = "See the challenge on Instagram"
        rules = "Official rules"
        legal = "No purchase, App Store rating or review is required. Read the rules for eligibility and selection details."
    items = "".join(f'<li><span>{index}</span><strong>{label}</strong></li>' for index, label in enumerate(steps, 1))
    return (
        '<section class="challenge-section" id="recordpicker-challenge" aria-labelledby="challenge-title">'
        f'<div class="challenge-copy"><p class="challenge-kicker">{kicker}</p>'
        f'<h2 id="challenge-title">{title}</h2><p class="challenge-lead">{lead}</p>'
        f'<ol class="challenge-steps">{items}</ol><div class="challenge-actions">'
        f'<a class="button challenge-button" href="https://apps.apple.com/app/recordpicker/id6780422305" data-app-store-link data-app-store-campaign="RP20_InstagramContest">{download}</a>'
        f'<a class="button challenge-rules-button" href="https://www.instagram.com/recordpicker/" rel="me">{instagram}</a>'
        f'<a class="challenge-rules-link" href="/contest/">{rules}</a></div>'
        f'<p class="challenge-legal">{legal}</p></div>{figure}</section>'
    )


def update_home(path: Path, french: bool) -> None:
    text = path.read_text(encoding="utf-8")
    if french:
        title = "Quel vinyle écouter ? Choisissez avec Record Picker"
        description = "Choisissez quel vinyle ou CD écouter avec Random Pick, Mood Pick ou le Disque du jour. Gratuit jusqu’à 100 disques, sans publicité ni abonnement."
        text = text.replace("Gratuit · Pro à vie", "Gratuit jusqu’à 100 disques · Pro à vie")
    else:
        title = "Choose What Vinyl Record to Play — Record Picker"
        description = "Choose the next vinyl record or CD with Random Pick, Mood Pick or Today’s Pick. Free for up to 100 records, with no ads or subscription."
        text = text.replace("Free · Lifetime Pro", "Free for up to 100 records · Lifetime Pro")
    text = replace_meta(text, title, description)
    text = track_store_links(text)
    match = re.search(r'<section class="challenge-section".*?(<figure class="challenge-media">.*?</figure>)</section>', text, re.DOTALL)
    if not match:
        raise RuntimeError(f"Challenge section not found in {path}")
    text = text[: match.start()] + challenge_copy(french, match.group(1)) + text[match.end() :]
    if french:
        press = re.search(r'<section class="section press-review-spotlight".*?</section>', text, re.DOTALL)
        challenge = re.search(r'<section class="challenge-section".*?</section>', text, re.DOTALL)
        if press and challenge and press.start() > challenge.start():
            press_html = press.group(0)
            text = text[: press.start()] + text[press.end() :]
            challenge = re.search(r'<section class="challenge-section".*?</section>', text, re.DOTALL)
            text = text[: challenge.start()] + press_html + text[challenge.start() :]
    path.write_text(text, encoding="utf-8")


def update_guide(path: Path, title: str, description: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_meta(text, title, description)
    text = track_store_links(text)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for path in FRENCH_HOMES:
        update_home(path, True)
    for path in ENGLISH_HOMES:
        update_home(path, False)

    french_guides = {
        "choose-vinyl-record": (
            "Quel vinyle écouter ? 5 méthodes simples | Record Picker",
            "Cinq méthodes concrètes pour choisir le prochain vinyle à écouter, éviter l’indécision et redécouvrir sa collection avec Record Picker.",
        ),
        "random-vinyl-record-picker": (
            "Tirage aléatoire de vinyles personnalisé | Record Picker",
            "Tirez un vinyle au hasard tout en respectant vos filtres, favoris, exclusions et disques moins écoutés. Essayez Record Picker gratuitement.",
        ),
    }
    english_guides = {
        "choose-vinyl-record": (
            "How to Choose the Right Vinyl Record to Play | Record Picker",
            "Five practical ways to choose the next vinyl record to play, avoid decision fatigue and rediscover your collection with Record Picker.",
        ),
        "random-vinyl-record-picker": (
            "Random Vinyl Record Picker App | Record Picker",
            "Pick a random vinyl record while respecting filters, favourites, exclusions and less-played albums. Try Record Picker free.",
        ),
    }
    for locale in ("", "fr", "fr-ca"):
        base = ROOT / locale if locale else ROOT
        for slug, metadata in french_guides.items():
            update_guide(base / slug / "index.html", *metadata)
    for locale in ("en-au", "en-ca", "en-gb", "en-us"):
        for slug, metadata in english_guides.items():
            update_guide(ROOT / locale / slug / "index.html", *metadata)

    print("Growth funnel updates applied to priority home and search pages.")


if __name__ == "__main__":
    main()
