#!/usr/bin/env python3
"""Prepare the localized Record Picker 2.0 preview without publishing 2.0.

The App Store 2.0 release notes are the source of truth for product meaning.
The script enriches the already-public "coming soon" blocks on the home,
features and screenshots pages, while leaving the 1.9 availability metadata
and every #RecordPickerChallenge banner/section untouched.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape, unescape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
APP_NOTES = ROOT.parent / "RecordPicker" / "AppStoreReleaseNotes" / "2.0"

LOCALE_NOTE = {
    "": "fr-FR",
    "ar": "ar-SA",
    "ca": "ca",
    "da": "da",
    "de": "de-DE",
    "el": "el",
    "en-au": "en-AU",
    "en-ca": "en-CA",
    "en-gb": "en-GB",
    "en-us": "en-US",
    "es-es": "es-ES",
    "es-mx": "es-MX",
    "fi": "fi",
    "fr": "fr-FR",
    "fr-ca": "fr-CA",
    "he": "he",
    "hi": "hi",
    "id": "id",
    "it": "it",
    "ja": "ja",
    "ko": "ko",
    "nb": "no",
    "nl": "nl-NL",
    "pl": "pl",
    "pt-br": "pt-BR",
    "pt-pt": "pt-PT",
    "ru": "ru",
    "sv": "sv",
    "th": "th",
    "tr": "tr",
    "vi": "vi",
    "zh-hans": "zh-Hans",
    "zh-hant": "zh-Hant",
}

RELEASE_BLOCK = re.compile(
    r'<(?P<tag>section|article)\b(?P<attrs>[^>]*\bdata-release-version="2\.0"[^>]*)>'
    r'.*?</(?P=tag)>',
    flags=re.DOTALL,
)


@dataclass(frozen=True)
class ReleaseCopy:
    headline: str
    bullets: tuple[str, ...]
    privacy: str


FRENCH_COPY = {
    "fr-FR": ReleaseCopy(
        "Record Picker 2.0 est notre évolution la plus importante : l’expérience "
        "s’organise désormais autour de trois façons de choisir le prochain disque — "
        "Disque du jour, Mood Pick et Random Pick.",
        (
            "Disque du jour relie l’actualité musicale vérifiée — anniversaires, "
            "rééditions et, si vous l’activez, concerts à proximité — aux disques de "
            "votre collection ou de votre liste de souhaits. Chaque suggestion en "
            "explique la raison et cite sa source.",
            "Vous pouvez parcourir plusieurs suggestions adaptées au moment, puis "
            "améliorer le classement privé sur l’appareil avec Pertinent et Non pertinent.",
            "Le nouveau Graphe de collection met en relation les œuvres, les "
            "enregistrements, les interprètes et les différentes éditions, avec un "
            "intérêt particulier pour la musique classique.",
            "Une prise en main plus claire, un nouvel accueil sur Mac et une navigation "
            "plus compacte sur iPhone rendent les fonctions principales plus faciles à trouver.",
            "Les rapprochements MusicBrainz, les contrôles de qualité des données, les "
            "traductions et les performances ont été renforcés.",
        ),
        "Votre collection et votre liste de souhaits restent privées : les rapprochements "
        "et la personnalisation s’effectuent sur votre appareil.",
    ),
    "fr-CA": ReleaseCopy(
        "Record Picker 2.0 est notre évolution la plus importante : l’expérience "
        "s’organise désormais autour de trois façons de choisir le prochain disque — "
        "Disque du jour, Mood Pick et Random Pick.",
        (
            "Disque du jour relie l’actualité musicale vérifiée — anniversaires, "
            "rééditions et, si vous l’activez, concerts à proximité — aux disques de "
            "votre collection ou de votre liste de souhaits. Chaque suggestion en "
            "explique la raison et cite sa source.",
            "Vous pouvez parcourir plusieurs suggestions adaptées au moment, puis "
            "améliorer le classement privé sur l’appareil avec Pertinent et Non pertinent.",
            "Le nouveau Graphe de collection met en relation les œuvres, les "
            "enregistrements, les interprètes et les différentes éditions, avec un "
            "intérêt particulier pour la musique classique.",
            "Une prise en main plus claire, un nouvel accueil sur Mac et une navigation "
            "plus compacte sur iPhone rendent les fonctions principales plus faciles à trouver.",
            "Les rapprochements MusicBrainz, les contrôles de qualité des données, les "
            "traductions et les performances ont été renforcés.",
        ),
        "Votre collection et votre liste de souhaits restent privées : les rapprochements "
        "et la personnalisation s’effectuent sur votre appareil.",
    ),
}


def parse_note(locale: str) -> ReleaseCopy:
    if locale in FRENCH_COPY:
        return FRENCH_COPY[locale]
    path = APP_NOTES / f"{locale}.txt"
    if not path.exists():
        raise RuntimeError(f"Missing localized 2.0 source: {path}")
    paragraphs = [part.strip() for part in path.read_text(encoding="utf-8").split("\n\n") if part.strip()]
    if len(paragraphs) != 3:
        raise RuntimeError(f"Unexpected 2.0 structure in {path}")
    bullets = tuple(
        line.removeprefix("•").strip()
        for line in paragraphs[1].splitlines()
        if line.strip()
    )
    if len(bullets) != 5 or any(not line.startswith("•") for line in paragraphs[1].splitlines()):
        raise RuntimeError(f"Expected five localized 2.0 points in {path}")
    return ReleaseCopy(paragraphs[0], bullets, paragraphs[2])


def plain_html(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", value)).strip()


def preview_status(block: str, path: Path) -> str:
    patterns = (
        r'<p class="kicker">(.*?)</p>',
        r'<p class="release-platform-summary"><strong>(.*?)</strong></p>',
    )
    for pattern in patterns:
        match = re.search(pattern, block, flags=re.DOTALL)
        if match:
            status = plain_html(match.group(1))
            if status:
                return status
    raise RuntimeError(f"No localized 2.0 preview status in {path}")


def preview_section(copy: ReleaseCopy, status: str, media: bool) -> str:
    outer = "media-section" if media else "section"
    bullets = "".join(f"<li>{escape(point)}</li>" for point in copy.bullets)
    return (
        f'<section class="{outer} next-release v20-preview" id="version-2-0-preview" '
        'data-release-version="2.0">'
        '<div class="section-head">'
        f'<p class="kicker">{escape(status)}</p><h2>Record Picker 2.0</h2>'
        f'<p class="lead">{escape(copy.headline)}</p></div>'
        '<div class="v20-preview-panel">'
        f'<ul>{bullets}</ul><p class="v20-privacy-note">{escape(copy.privacy)}</p>'
        '</div></section>'
    )


def preview_card(copy: ReleaseCopy, status: str) -> str:
    bullets = "".join(f"<li>{escape(point)}</li>" for point in copy.bullets)
    return (
        '<article class="release-card release-preview release-upcoming v20-release-card" '
        'data-release-version="2.0"><div class="release-head">'
        '<span class="version-pill">v2.0</span><div>'
        f'<h3>{escape(copy.headline)}</h3>'
        f'<p class="release-platform-summary"><strong>{escape(status)}</strong></p>'
        f'</div></div><ul>{bullets}</ul>'
        f'<p class="v20-privacy-note">{escape(copy.privacy)}</p></article>'
    )


def challenge_fragments(text: str) -> tuple[str, ...]:
    fragments = re.findall(
        r'<(?:aside|section)[^>]*class="[^"]*challenge-[^"]*"[^>]*>.*?</(?:aside|section)>',
        text,
        flags=re.DOTALL,
    )
    return tuple(fragments)


def improve_french_copy(text: str) -> str:
    hero_descriptions = (
        (
            "Passez le bon disque. Redécouvrez votre collection sur iPhone, iPad, Apple Watch "
            "et Mac, avec un tirage équitable, Mood Pick, iCloud et des outils pensés pour les "
            "vrais collectionneurs."
        ),
        (
            "Passez le bon disque. Redécouvrez votre collection sur iPhone, iPad, Apple Watch "
            "et Mac grâce au tirage aléatoire personnalisable, à Mood Pick, au Disque du jour, "
            "à iCloud et aux outils conçus pour les collectionneurs."
        ),
        (
            "Cataloguez vos vinyles et vos CD, puis choisissez le prochain disque à écouter avec "
            "le tirage aléatoire personnalisable, Mood Pick ou le Disque du jour. Votre collection "
            "reste privée et peut se synchroniser via iCloud entre iPhone, iPad, Apple Watch et Mac."
        ),
    )
    new_hero_description = (
        "Cataloguez vos vinyles et vos CD, puis choisissez le prochain disque à écouter avec "
        "le tirage aléatoire personnalisable, Mood Pick ou le Disque du jour. Votre collection "
        "reste privée, peut se synchroniser via iCloud entre iPhone, iPad et Mac, et vous "
        "accompagne aussi sur Apple Watch."
    )
    for description in hero_descriptions:
        text = text.replace(description, new_hero_description)

    old_seo_description = (
        "Record Picker catalogue les vinyles, CD et albums favoris, puis propose le prochain "
        "disque à écouter selon vos filtres, vos favoris, vos exclusions et l'ambiance du moment."
    )
    new_seo_description = (
        "Cataloguez vos vinyles et CD, puis choisissez quoi écouter avec le tirage aléatoire, "
        "Mood Pick et le Disque du jour sur iPhone, iPad, Apple Watch et Mac."
    )
    text = text.replace(old_seo_description, new_seo_description)
    text = text.replace(
        old_seo_description.replace("'", "&#x27;"), new_seo_description
    )
    text = text.replace("Tirage équitable", "Tirage personnalisable")
    text = text.replace(
        "Favorisez les disques moins écoutés, filtrez par année, genre, format, vitesse "
        "ou favoris, puis balayez la pochette pour tirer ou annuler.",
        "Choisissez un tirage purement aléatoire ou favorisez les disques moins écoutés, "
        "puis appliquez vos filtres et exclusions avant de lancer ou d’annuler le tirage.",
    )
    text = text.replace(
        "Choisissez le prochain disque sans perdre le contrôle, avec un hasard qui fait "
        "mieux tourner la collection.",
        "Choisissez entre un tirage purement aléatoire et un mode pondéré facultatif qui "
        "fait davantage revenir les disques moins écoutés.",
    )
    text = text.replace(
        "Tirage pondéré qui favorise les disques moins écoutés",
        "Mode pondéré facultatif pour favoriser les disques moins écoutés",
    )
    return text


def update_page(path: Path, copy: ReleaseCopy, *, french: bool = False) -> bool:
    text = path.read_text(encoding="utf-8")
    before_challenge = challenge_fragments(text)
    match = RELEASE_BLOCK.search(text)
    if not match:
        raise RuntimeError(f"No 2.0 preview block in {path}")
    if path.parent.name == "screenshots":
        # The screenshots page is a gallery, not a second release-notes page.
        # Keep the version context in the gallery heading and do not duplicate
        # the full editorial preview already shown on the homepage.
        updated = text[:match.start()] + text[match.end():]
    else:
        status = preview_status(match.group(0), path)
        if path.parent.name == "readme":
            replacement = preview_card(copy, status)
        else:
            replacement = preview_section(copy, status, False)
        updated = text[:match.start()] + replacement + text[match.end():]
    if french:
        updated = improve_french_copy(updated)
    if challenge_fragments(updated) != before_challenge:
        raise RuntimeError(f"Contest markup changed unexpectedly in {path}")
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    if not APP_NOTES.exists():
        raise RuntimeError(f"Record Picker 2.0 sources not found: {APP_NOTES}")
    changed: list[Path] = []
    for directory, note_locale in LOCALE_NOTE.items():
        root = ROOT / directory if directory else ROOT
        copy = parse_note(note_locale)
        pages = (root / "index.html", root / "readme" / "index.html", root / "screenshots" / "index.html")
        for path in pages:
            if update_page(
                path,
                copy,
                french=note_locale in FRENCH_COPY,
            ):
                changed.append(path)
    print(f"Prepared Record Picker 2.0 preview on {len(changed)} localized pages.")
    print("Record Picker 1.9 remains the only current release; contest markup is unchanged.")


if __name__ == "__main__":
    main()
