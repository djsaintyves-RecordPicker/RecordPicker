#!/usr/bin/env python3
"""Publish Record Picker 2.4 and stage the localized 2.4.1 announcement."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re

from announce_release_2_1 import COMING_SOON
from announce_release_2_3_1 import LOCALES, ROOT, STATE_PATH, block
from announce_release_2_4 import APP_LOCALE, app_strings


CURRENT_VERSION = "2.4"
PREVIOUS_VERSION = "2.3.2"
NEXT_VERSION = "2.4.1"
COPY_PATH = ROOT / "data" / "release-notes" / f"{NEXT_VERSION}.json"

SOURCE = {
    "headline": "Keep Mac, iPhone, iPad, Windows and Android aligned through a shared folder you choose. Record Picker encrypts the collection on this device before the storage provider receives it.",
    "sync_title": "Encrypted cross-platform synchronization",
    "sync": "Cross-platform sync uses a folder you choose and encrypts every collection file before it reaches the storage provider.",
    "account_title": "No Record Picker account is required.",
    "account": "The provider stores encrypted files, not a readable collection.",
    "recovery_title": "Privacy and recovery",
    "recovery": "The association code is the only way to decrypt the shared collection. Record Picker cannot recover it if it is lost.",
}

EDITORIAL = {
    "fr": {
        "headline": "La version 2.4.1 prépare une synchronisation privée et chiffrée entre Mac, iPhone, iPad, Windows et Android, à partir d’un dossier partagé de votre choix.",
        "sync_title": "Une collection synchronisée entre plateformes",
        "sync": "La collection, les pochettes, la liste À écouter plus tard et les brouillons de parcours d’écoute pourront rester cohérents sur vos appareils, même lorsque vous travaillez hors ligne.",
        "account_title": "Aucun compte Record Picker à créer",
        "account": "Les fichiers sont chiffrés sur l’appareil avant d’arriver chez le fournisseur de stockage. Celui-ci ne reçoit jamais une collection lisible.",
        "recovery_title": "Une clé qui reste entre vos mains",
        "recovery": "Un code d’association relie les appareils autorisés. Il faudra le conserver précieusement : Record Picker ne pourra pas récupérer une clé perdue.",
    },
    "en": {
        "headline": "Record Picker 2.4.1 prepares private, encrypted synchronization between Mac, iPhone, iPad, Windows and Android through a shared folder you choose.",
        "sync_title": "One collection across platforms",
        "sync": "Your collection, artwork, Listen Later queue and Listening Journey drafts can stay aligned across devices, even while you work offline.",
        "account_title": "No Record Picker account required",
        "account": "Files are encrypted on your device before they reach the storage provider, which never receives a readable collection.",
        "recovery_title": "A key that stays in your hands",
        "recovery": "An association code connects authorized devices. Keep it safe: Record Picker cannot recover a lost key.",
    },
}


def refresh_copy(app_root: Path) -> None:
    localized: dict[str, dict[str, str]] = {}
    for directory, locale in LOCALES.items():
        entries = app_strings(app_root, APP_LOCALE[locale])
        localized[directory] = {
            field: entries.get(source, source) for field, source in SOURCE.items()
        }
        if directory in {"fr", "fr-ca"}:
            localized[directory].update(EDITORIAL["fr"])
        elif directory in {"", "en-au", "en-ca", "en-gb", "en-us"}:
            localized[directory].update(EDITORIAL["en"])
    COPY_PATH.parent.mkdir(parents=True, exist_ok=True)
    COPY_PATH.write_text(
        json.dumps(localized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def feature_list(copy: dict[str, str]) -> str:
    return "".join(
        f"<li><strong>{escape(copy[title])}</strong><span>{escape(copy[text])}</span></li>"
        for title, text in (
            ("sync_title", "sync"),
            ("account_title", "account"),
            ("recovery_title", "recovery"),
        )
    )


def next_home(copy: dict[str, str], status: str) -> str:
    return (
        f'<section class="section next-release v241-preview" id="versions" data-release-version="{NEXT_VERSION}">'
        f'<div class="section-head"><p class="kicker">Apple · {escape(status)}</p>'
        f'<h2>Record Picker {NEXT_VERSION} · Apple</h2><p class="lead">{escape(copy["headline"])}</p></div>'
        f'<div class="v20-preview-panel"><ul class="v24-feature-list">{feature_list(copy)}</ul></div></section>'
    )


def next_history(copy: dict[str, str], status: str) -> str:
    return (
        f'<article class="release-card release-preview release-upcoming v241-release-card" data-release-version="{NEXT_VERSION}">'
        f'<div class="release-head"><span class="version-pill">v{NEXT_VERSION}</span><div>'
        f'<h3>{escape(copy["headline"])}</h3><p class="release-platform-summary"><strong>'
        f'Apple · {escape(status)} · iPhone · iPad · Apple Watch · Mac</strong></p></div></div>'
        f'<ul class="v24-feature-list">{feature_list(copy)}</ul></article>'
    )


def next_marker(copy: dict[str, str], status: str, *, mac: bool = False) -> str:
    classes = "next-release v241-mac-preview" if mac else "media-section next-release v241-gallery-marker"
    return (
        f'<section class="{classes}" data-release-version="{NEXT_VERSION}"><div class="section-head">'
        f'<p class="kicker">Apple · {escape(status)}</p><h2>Record Picker {NEXT_VERSION} · Apple</h2>'
        f'<p class="lead">{escape(copy["headline"])}</p></div></section>'
    )


def status_text(release_block: str, pattern: str) -> str:
    match = re.search(pattern, release_block, re.DOTALL)
    if not match:
        raise RuntimeError("Missing localized current-release status")
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def publish_locale(directory: str, locale: str, copy: dict[str, str]) -> int:
    locale_root = ROOT / directory if directory else ROOT
    coming_soon = COMING_SOON[locale]
    changed = 0

    path = locale_root / "index.html"
    text = path.read_text(encoding="utf-8")
    current = block(text, PREVIOUS_VERSION, "section")
    candidate = block(text, CURRENT_VERSION, "section")
    if not current or not candidate:
        raise RuntimeError(f"Expected {PREVIOUS_VERSION} and {CURRENT_VERSION} home blocks in {path}")
    available = status_text(current.group(0), r'<p class="kicker">(.*?)</p>')
    published = re.sub(r'class="[^"]*\bv24-preview\b[^"]*"', 'class="section current-release v24-preview"', candidate.group(0), count=1)
    published = published.replace('id="versions"', 'id="version-2-4"', 1)
    published = re.sub(r'<p class="kicker">.*?</p>', f'<p class="kicker">Apple · {escape(available)}</p>', published, count=1, flags=re.DOTALL)
    updated = text[:candidate.start()] + next_home(copy, coming_soon) + published + text[candidate.end():current.start()] + text[current.end():]
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed += 1

    path = locale_root / "readme" / "index.html"
    text = path.read_text(encoding="utf-8")
    current = block(text, PREVIOUS_VERSION, "article")
    candidate = block(text, CURRENT_VERSION, "article")
    if not current or not candidate:
        raise RuntimeError(f"Expected release cards in {path}")
    summary = re.search(r'<p class="release-platform-summary">.*?</p>', current.group(0), re.DOTALL)
    if not summary:
        raise RuntimeError(f"Missing current platform summary in {path}")
    published = re.sub(r'class="[^"]*\bv24-release-card\b[^"]*"', 'class="release-card current-release v24-release-card"', candidate.group(0), count=1)
    published = re.sub(r'<p class="release-platform-summary">.*?</p>', summary.group(0), published, count=1, flags=re.DOTALL)
    historical = re.sub(r'\s*<p class="release-platform-summary">.*?</p>', '', current.group(0), count=1, flags=re.DOTALL)
    historical = re.sub(r'class="[^"]*\bv232-release-card\b[^"]*"', 'class="release-card v232-release-card"', historical, count=1)
    updated = text[:candidate.start()] + next_history(copy, coming_soon) + published + text[candidate.end():current.start()] + historical + text[current.end():]
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed += 1

    path = locale_root / "screenshots" / "index.html"
    text = path.read_text(encoding="utf-8")
    candidate = block(text, CURRENT_VERSION, "section")
    gallery = re.search(rf'<section\b[^>]*data-release-gallery="{re.escape(PREVIOUS_VERSION)}"[^>]*>.*?</section>', text, re.DOTALL)
    if not candidate or not gallery:
        raise RuntimeError(f"Expected release gallery blocks in {path}")
    published = re.sub(r'class="[^"]*\bv24-gallery\b[^"]*"', 'class="media-section current-release v24-gallery"', candidate.group(0), count=1)
    published = re.sub(r'<p class="kicker">.*?</p>', f'<p class="kicker">Apple · {escape(available)}</p>', published, count=1, flags=re.DOTALL)
    current_gallery = gallery.group(0).replace(f'data-release-gallery="{PREVIOUS_VERSION}"', f'data-release-gallery="{CURRENT_VERSION}"', 1)
    current_gallery = current_gallery.replace(f"Record Picker {PREVIOUS_VERSION}", f"Record Picker {CURRENT_VERSION}")
    updated = text[:candidate.start()] + next_marker(copy, coming_soon) + published + text[candidate.end():gallery.start()] + current_gallery + text[gallery.end():]
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed += 1

    path = locale_root / "mac-app" / "index.html"
    text = path.read_text(encoding="utf-8")
    candidate = block(text, CURRENT_VERSION, "section")
    if not candidate:
        raise RuntimeError(f"Expected {CURRENT_VERSION} Mac block in {path}")
    published = re.sub(r'class="[^"]*\bv24-mac-preview\b[^"]*"', 'class="current-release v24-mac-preview"', candidate.group(0), count=1)
    published = re.sub(r'<p class="kicker">.*?</p>', f'<p class="kicker">Apple · {escape(available)}</p>', published, count=1, flags=re.DOTALL)
    updated = text[:candidate.start()] + next_marker(copy, coming_soon, mac=True) + published + text[candidate.end():]
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed += 1
    return changed


def update_metadata(publication_date: str) -> int:
    changed = 0
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        updated = re.sub(r'("softwareVersion":")[^"]+', rf'\g<1>{CURRENT_VERSION}', text)
        updated = re.sub(r'("dateModified":")[^"]+', rf'\g<1>{publication_date}', updated)
        updated = re.sub(r'<span id="site-footer-version">.*?</span>', f'<span id="site-footer-version">Record Picker · {CURRENT_VERSION}</span>', updated, flags=re.DOTALL)
        if "readme" not in path.parts:
            updated = updated.replace(
                f"Record Picker {PREVIOUS_VERSION}",
                f"Record Picker {CURRENT_VERSION}",
            )
        if path.name == "index.html" and path.parent.name not in {
            "android-app", "windows-app", "ios-app", "watch-app", "mac-app",
            "readme", "screenshots", "support", "privacy", "press",
            "choose-vinyl-record", "random-vinyl-record-picker",
            "manage-vinyl-collection", "catalog-vinyl-collection-app",
            "cd-collection-app", "music-collection-app", "vinyl-collection-app",
        }:
            updated = re.sub(
                r'(<section class="section gallery".*?<h2>)Record Picker [^<]+(</h2>)',
                rf'\g<1>Record Picker {CURRENT_VERSION}\g<2>',
                updated,
                count=1,
                flags=re.DOTALL,
            )
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    for name in ("sitemap.xml", "sitemap-media.xml"):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        path.write_text(re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{publication_date}</lastmod>', text), encoding="utf-8")
    return changed


def update_state() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if state.get("next_release", {}).get("version") != CURRENT_VERSION:
        raise RuntimeError(f"{CURRENT_VERSION} must be staged before publication")
    state["current_release"] = {
        "version": CURRENT_VERSION,
        "platform_versions": {p: CURRENT_VERSION for p in ("iphone", "ipad", "mac", "watch")},
        "platforms": {p: "available" for p in ("iphone", "ipad", "mac", "watch")},
        "required_platforms_for_full_release": ["iphone", "ipad", "mac", "watch"],
    }
    state["historical_releases"] = [PREVIOUS_VERSION, *[v for v in state["historical_releases"] if v != PREVIOUS_VERSION]]
    state["next_release"] = {
        "version": NEXT_VERSION,
        "platforms": {p: "coming_soon" for p in ("iphone", "ipad", "mac", "watch")},
    }
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-root", type=Path, required=True)
    parser.add_argument("--publication-date", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.publication_date):
        raise SystemExit("Invalid publication date")
    refresh_copy(args.app_root)
    copy = json.loads(COPY_PATH.read_text(encoding="utf-8"))
    changed = sum(publish_locale(directory, locale, copy[directory]) for directory, locale in LOCALES.items())
    changed += update_metadata(args.publication_date)
    update_state()
    print(f"Published {CURRENT_VERSION} and announced {NEXT_VERSION} across {changed} localized pages.")


if __name__ == "__main__":
    main()
