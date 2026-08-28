#!/usr/bin/env python3
"""Announce Record Picker 2.4 and showcase the macOS Collection Graph."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re

from announce_release_2_1 import COMING_SOON
from announce_release_2_3_1 import LOCALES, ROOT, STATE_PATH, block


VERSION = "2.4"
CURRENT_VERSION = "2.3.2"
COPY_PATH = ROOT / "data" / "release-notes" / "2.4.json"

APP_LOCALE = {
    "ar-SA": "ar", "ca": "ca", "da": "da", "de-DE": "de", "el": "el",
    "en-AU": "en-GB", "en-CA": "en-GB", "en-GB": "en-GB", "en-US": "en-GB",
    "es-ES": "es", "es-MX": "es-MX", "fi": "fi", "fr-FR": "fr",
    "fr-CA": "fr-CA", "he": "he", "hi": "hi", "id": "id", "it": "it",
    "ja": "ja", "ko": "ko", "no": "nb", "nl-NL": "nl", "pl": "pl",
    "pt-BR": "pt-BR", "pt-PT": "pt-PT", "ru": "ru", "sv": "sv",
    "th": "th", "tr": "tr", "vi": "vi", "zh-Hans": "zh-Hans",
    "zh-Hant": "zh-Hant",
}

KEYS = {
    "headline": "Compose a progression from records you already own.",
    "journey": "Record Picker builds each journey locally from records you own, linking shared genres, styles and nearby years without inventing missing metadata.",
    "listen_title": "Listen Later",
    "listen": "Add an owned record from its details to keep it ready for another listening session.",
    "graph_title": "Graphe de collection",
    "graph": "Record Picker relie les œuvres, compositeurs, interprètes, chefs, ensembles et éditions sans modifier vos données.",
    "scanner": "Use a Mac camera or an iPhone through Continuity Camera. Recognition happens locally on this Mac.",
    "today": "Your city, map center and radius stay on this device. The public global feed is filtered locally. Your collection and wishlist are never sent.",
    "privacy": "Collection status, private notes, listening history and location are never included.",
}

STRING_ENTRY = re.compile(r'^"((?:\\.|[^"\\])*)"\s*=\s*"((?:\\.|[^"\\])*)";$')


def decode_quoted(value: str) -> str:
    return json.loads(f'"{value}"')


def app_strings(app_root: Path, app_locale: str) -> dict[str, str]:
    path = app_root / "RecordPicker" / f"{app_locale}.lproj" / "Localizable.strings"
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = STRING_ENTRY.match(line.strip())
        if match:
            entries[decode_quoted(match.group(1))] = decode_quoted(match.group(2))
    return entries


def refresh_copy(app_root: Path) -> None:
    localized: dict[str, dict[str, str]] = {}
    for directory, locale in LOCALES.items():
        entries = app_strings(app_root, APP_LOCALE[locale])
        missing = [source for source in KEYS.values() if source not in entries]
        if missing:
            raise RuntimeError(f"Missing 2.4 translations for {locale}: {missing}")
        localized[directory] = {
            field: entries[source]
            for field, source in KEYS.items()
        }
    COPY_PATH.parent.mkdir(parents=True, exist_ok=True)
    COPY_PATH.write_text(
        json.dumps(localized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def screenshots(directory: str) -> tuple[str, str]:
    locale = "fr" if directory in {"fr", "fr-ca"} else "en-us"
    base = f"/assets/screenshots/v24/{locale}"
    return (
        f"{base}/collection-graph-interactive.webp",
        f"{base}/collection-graph-relationships.webp",
    )


def feature_items(copy: dict[str, str]) -> str:
    points = (
        copy["journey"],
        f'{copy["listen_title"]} — {copy["listen"]}',
        f'{copy["graph_title"]} — {copy["graph"]}',
        copy["scanner"],
        copy["today"],
        copy["privacy"],
    )
    return "".join(f"<li>{escape(point)}</li>" for point in points)


def figures(directory: str, copy: dict[str, str], *, loading: str = "lazy") -> str:
    interactive, relationships = screenshots(directory)
    title = escape(copy["graph_title"])
    return (
        '<div class="v24-graph-grid">'
        f'<figure><img src="{interactive}" alt="{title} — macOS" width="1224" height="768" loading="{loading}" decoding="async">'
        f'<figcaption class="visually-hidden">{title} · macOS</figcaption></figure>'
        f'<figure><img src="{relationships}" alt="{title} — macOS" width="1224" height="768" loading="lazy" decoding="async">'
        f'<figcaption class="visually-hidden">{title} · macOS</figcaption></figure></div>'
    )


def home(directory: str, copy: dict[str, str], status: str) -> str:
    return (
        f'<section class="section next-release v24-preview" id="versions" data-release-version="{VERSION}">'
        f'<div class="section-head"><p class="kicker">{escape(status)}</p><h2>Record Picker {VERSION}</h2>'
        f'<p class="lead">{escape(copy["headline"])}</p></div>'
        f'<div class="v24-preview-layout"><div class="v20-preview-panel"><ul>{feature_items(copy)}</ul></div>'
        f'{figures(directory, copy)}</div></section>'
    )


def history(copy: dict[str, str], status: str) -> str:
    platforms = f"{status} · iPhone · iPad · Apple Watch · Mac"
    return (
        f'<article class="release-card release-preview release-upcoming v24-release-card" data-release-version="{VERSION}">'
        f'<div class="release-head"><span class="version-pill">v{VERSION}</span><div><h3>{escape(copy["headline"])}</h3>'
        f'<p class="release-platform-summary"><strong>{escape(platforms)}</strong></p></div></div>'
        f'<ul>{feature_items(copy)}</ul></article>'
    )


def gallery(directory: str, copy: dict[str, str], status: str) -> str:
    return (
        f'<section class="media-section next-release v24-gallery" data-release-version="{VERSION}">'
        f'<div class="section-head"><p class="kicker">{escape(status)}</p><h2>Record Picker {VERSION}</h2>'
        f'<p class="lead">{escape(copy["headline"])}</p></div>{figures(directory, copy)}</section>'
    )


def mac_preview(directory: str, copy: dict[str, str], status: str) -> str:
    return (
        f'<section class="next-release v24-mac-preview" data-release-version="{VERSION}">'
        f'<div class="section-head"><p class="kicker">{escape(status)}</p><h2>Record Picker {VERSION}</h2>'
        f'<p class="lead">{escape(copy["graph"])}</p></div>'
        f'<div class="v20-preview-panel"><ul><li>{escape(copy["journey"])}</li>'
        f'<li>{escape(copy["scanner"])}</li></ul></div>{figures(directory, copy)}</section>'
    )


def stage_locale(directory: str, locale: str, copy: dict[str, str]) -> int:
    locale_root = ROOT / directory if directory else ROOT
    status = COMING_SOON[locale]
    changed = 0

    path = locale_root / "index.html"
    text = path.read_text(encoding="utf-8")
    text = text.replace("</section>></section><section", "</section><section")
    text = text.replace("</section>tion><section", "</section><section")
    if not block(text, VERSION, "section"):
        text = text.replace(
            f'id="versions" data-release-version="{CURRENT_VERSION}"',
            f'id="version-2-3-2" data-release-version="{CURRENT_VERSION}"',
            1,
        )
        current = block(text, CURRENT_VERSION, "section")
        if not current:
            raise RuntimeError(f"Missing current {CURRENT_VERSION} block in {path}")
        text = text[:current.start()] + home(directory, copy, status) + current.group(0) + text[current.end():]
        changed += 1
    path.write_text(text, encoding="utf-8")

    path = locale_root / "readme" / "index.html"
    text = path.read_text(encoding="utf-8")
    if not block(text, VERSION, "article"):
        current = block(text, CURRENT_VERSION, "article")
        if not current:
            raise RuntimeError(f"Missing current {CURRENT_VERSION} block in {path}")
        text = text[:current.start()] + history(copy, status) + current.group(0) + text[current.end():]
        changed += 1
    path.write_text(text, encoding="utf-8")

    path = locale_root / "screenshots" / "index.html"
    text = path.read_text(encoding="utf-8")
    if not block(text, VERSION, "section"):
        current = re.search(
            rf'<section\b[^>]*data-release-gallery="{re.escape(CURRENT_VERSION)}"[^>]*>.*?</section>',
            text,
            re.DOTALL,
        )
        if not current:
            raise RuntimeError(f"Missing current {CURRENT_VERSION} gallery in {path}")
        text = text[:current.start()] + gallery(directory, copy, status) + current.group(0) + text[current.end():]
        changed += 1
    path.write_text(text, encoding="utf-8")

    path = locale_root / "mac-app" / "index.html"
    text = path.read_text(encoding="utf-8")
    if not block(text, VERSION, "section"):
        marker = "</section></main>"
        if marker not in text:
            raise RuntimeError(f"Missing mac page insertion point in {path}")
        text = text.replace(marker, mac_preview(directory, copy, status) + marker, 1)
        changed += 1
    path.write_text(text, encoding="utf-8")
    return changed


def update_state() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if state["current_release"]["version"] != CURRENT_VERSION:
        raise RuntimeError(f"{CURRENT_VERSION} must remain current while {VERSION} is announced")
    state["next_release"] = {
        "version": VERSION,
        "platforms": {
            platform: "coming_soon"
            for platform in ("iphone", "ipad", "mac", "watch")
        },
    }
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-copy-from-app", type=Path)
    args = parser.parse_args()
    if args.refresh_copy_from_app:
        refresh_copy(args.refresh_copy_from_app)
    if not COPY_PATH.exists():
        raise RuntimeError(f"Missing localized release copy: {COPY_PATH}")
    copy = json.loads(COPY_PATH.read_text(encoding="utf-8"))
    if set(copy) != set(LOCALES):
        raise RuntimeError("The 2.4 copy does not cover every site locale")
    changed = sum(
        stage_locale(directory, locale, copy[directory])
        for directory, locale in LOCALES.items()
    )
    update_state()
    print(f"Announced Record Picker {VERSION} across {changed} localized pages.")


if __name__ == "__main__":
    main()
