#!/usr/bin/env python3
"""Publish Record Picker 2.5 across the localized Apple and Windows site."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re

from announce_release_2_3_1 import LOCALES, ROOT, STATE_PATH, block


VERSION = "2.5"
APPLE_PREVIOUS = "2.4"
WINDOWS_PREVIOUS = "2.4.3"
COPY_PATH = ROOT / "data" / "release-notes" / f"{VERSION}.json"

EN = {
    "headline": "Record Picker 2.5 makes exploring, organizing and understanding your collection clearer and more reliable on Apple devices and Windows.",
    "graph_title": "A graph that follows your filters",
    "graph": "Explore documented links between records, understand the evidence behind each path and save a path as an editable Listening Journey.",
    "move_title": "Move several records together",
    "move": "Move filtered records to a physical storage location after reviewing a preview of the exact changes.",
    "listen_title": "More reliable listening insights",
    "listen": "Listening filters and Collection Stories distinguish confirmed listens from picks and playback launches.",
    "story_title": "Your collection tells its story",
    "story": "Create a private, local Collection Story and save or share it as a carefully limited PNG card.",
    "quality_title": "Clarity and reliability",
    "quality": "Graph performance, review cleanup, translations and several backup and recovery workflows have been improved.",
}

FR = {
    "headline": "Record Picker 2.5 rend l’exploration, le rangement et la compréhension de votre collection plus clairs et plus fiables sur les appareils Apple et Windows.",
    "graph_title": "Un graphe fidèle à vos filtres",
    "graph": "Explorez les liens documentés entre vos disques, comprenez les indices qui expliquent chaque parcours et enregistrez un chemin comme parcours d’écoute modifiable.",
    "move_title": "Déplacer plusieurs disques ensemble",
    "move": "Déplacez les disques filtrés vers un emplacement physique après avoir vérifié un aperçu exact des changements.",
    "listen_title": "Des analyses d’écoute plus fiables",
    "listen": "Les filtres d’écoute et les Histoires de la collection distinguent les écoutes confirmées des tirages et des lancements de lecture.",
    "story_title": "Votre collection raconte son histoire",
    "story": "Créez localement une Histoire de la collection privée, puis enregistrez-la ou partagez-la sous forme de carte PNG aux informations volontairement limitées.",
    "quality_title": "Clarté et fiabilité",
    "quality": "Les performances du graphe, le nettoyage des critiques, les traductions et plusieurs parcours de sauvegarde et de récupération ont été améliorés.",
}


def copy_for(directory: str) -> dict[str, str]:
    return FR if directory in {"fr", "fr-ca"} else EN


def feature_list(copy: dict[str, str]) -> str:
    return "".join(
        f"<li><strong>{escape(copy[title])}</strong><span>{escape(copy[text])}</span></li>"
        for title, text in (
            ("graph_title", "graph"),
            ("move_title", "move"),
            ("listen_title", "listen"),
            ("story_title", "story"),
            ("quality_title", "quality"),
        )
    )


def available_status(current: str) -> str:
    match = re.search(r'<p class="kicker">(?:Apple · )?(.*?)</p>', current, re.DOTALL)
    return re.sub(r"<[^>]+>", "", match.group(1)).strip() if match else "Available now"


def current_home(copy: dict[str, str], status: str) -> str:
    return (
        f'<section class="section current-release v25-preview" id="versions" data-release-version="{VERSION}">'
        f'<div class="section-head"><p class="kicker">Apple · Windows · {escape(status)}</p>'
        f'<h2>Record Picker {VERSION}</h2><p class="lead">{escape(copy["headline"])}</p></div>'
        f'<div class="v20-preview-panel"><ul class="v24-feature-list">{feature_list(copy)}</ul></div></section>'
    )


def current_history(copy: dict[str, str], status: str) -> str:
    return (
        f'<article class="release-card current-release v25-release-card" data-release-version="{VERSION}">'
        f'<div class="release-head"><span class="version-pill">v{VERSION}</span><div>'
        f'<h3>{escape(copy["headline"])}</h3><p class="release-platform-summary"><strong>'
        f'iPhone · iPad · Apple Watch · Mac · Windows · {escape(status)}</strong></p></div></div>'
        f'<ul class="v24-feature-list">{feature_list(copy)}</ul></article>'
    )


def replace_release_blocks(path: Path, kind: str, copy: dict[str, str]) -> bool:
    text = path.read_text(encoding="utf-8")
    upcoming = block(text, "2.4.1", "article" if kind == "readme" else "section")
    current = block(text, APPLE_PREVIOUS, "article" if kind == "readme" else "section")
    if not upcoming or not current:
        raise RuntimeError(f"Expected 2.4.1 and 2.4 blocks in {path}")
    status = available_status(current.group(0))
    if copy is FR:
        status = "Disponible dès maintenant"

    if kind == "home":
        replacement = current_home(copy, status)
    elif kind == "readme":
        historical = re.sub(r'\s*<p class="release-platform-summary">.*?</p>', "", current.group(0), count=1, flags=re.DOTALL)
        historical = historical.replace("release-card current-release v24-release-card", "release-card v24-release-card", 1)
        replacement = current_history(copy, status) + historical
    else:
        replacement = current.group(0)
        replacement = re.sub(r'class="[^"]*(?:current-release|next-release)[^"]*"', 'class="current-release v25-preview"', replacement, count=1)
        replacement = replacement.replace('data-release-version="2.4"', 'data-release-version="2.5"', 1)
        replacement = re.sub(r'<p class="kicker">.*?</p>', f'<p class="kicker">Apple · Windows · {escape(status)}</p>', replacement, count=1, flags=re.DOTALL)
        replacement = re.sub(r'<h2>.*?</h2>', f'<h2>Record Picker {VERSION}</h2>', replacement, count=1, flags=re.DOTALL)
        replacement = re.sub(r'<p class="lead">.*?</p>', f'<p class="lead">{escape(copy["headline"])}</p>', replacement, count=1, flags=re.DOTALL)

    start = min(upcoming.start(), current.start())
    end = max(upcoming.end(), current.end())
    updated = text[:start] + replacement + text[end:]
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def publish_locales() -> int:
    changed = 0
    release_copy: dict[str, dict[str, str]] = {}
    for directory in LOCALES:
        copy = copy_for(directory)
        release_copy[directory] = copy
        root = ROOT / directory if directory else ROOT
        for route, kind in (("index.html", "home"), ("readme/index.html", "readme"), ("screenshots/index.html", "screenshots"), ("mac-app/index.html", "mac")):
            changed += replace_release_blocks(root / route, kind, copy)
    COPY_PATH.write_text(json.dumps(release_copy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def update_windows(path: Path, copy: dict[str, str]) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"Record Picker {WINDOWS_PREVIOUS}", f"Record Picker {VERSION}")
    updated = updated.replace(f'data-windows-version="{WINDOWS_PREVIOUS}"', f'data-windows-version="{VERSION}"')
    updated = updated.replace(f"Record Picker · Windows {WINDOWS_PREVIOUS}", f"Record Picker · {VERSION}")
    section = re.search(r'<section class="section platform-expansion windows-release".*?</section>', updated, re.DOTALL)
    if not section:
        raise RuntimeError(f"Missing Windows release section in {path}")
    original = section.group(0)
    heading = re.search(r'<h2>.*?</h2>', original, re.DOTALL)
    lead = re.search(r'<p class="lead">.*?</p>', original, re.DOTALL)
    price = re.search(r'<p>(?!<).*?</p>', original, re.DOTALL)
    rebuilt = (
        f'<section class="section platform-expansion windows-release" data-windows-version="{VERSION}"><div class="section-head">'
        f'{heading.group(0) if heading else ""}{lead.group(0) if lead else ""}{price.group(0) if price else ""}'
        f'<ul class="v24-feature-list">{feature_list(copy)}</ul></div></section>'
    )
    updated = updated[:section.start()] + rebuilt + updated[section.end():]
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def update_metadata(publication_date: str) -> int:
    changed = 0
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        updated = re.sub(r'("softwareVersion":")[^"]+', rf'\g<1>{VERSION}', text)
        updated = re.sub(r'("dateModified":")[^"]+', rf'\g<1>{publication_date}', updated)
        updated = re.sub(r'<span id="site-footer-version">.*?</span>', f'<span id="site-footer-version">Record Picker · {VERSION}</span>', updated, flags=re.DOTALL)
        updated = updated.replace(f'data-release-gallery="{APPLE_PREVIOUS}"', f'data-release-gallery="{VERSION}"')
        if path.parts and any(part in {"fr", "fr-ca"} for part in path.parts):
            updated = updated.replace("iPhone · iPad · Apple Watch · Mac · Windows · Available now", "iPhone · iPad · Apple Watch · Mac · Windows · Disponible dès maintenant")
        if "readme" not in path.parts:
            updated = re.sub(r'Record Picker 2\.4(?!\.)', f'Record Picker {VERSION}', updated)
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
    platforms = ("iphone", "ipad", "watch", "mac", "windows")
    state["current_release"] = {
        "version": VERSION,
        "platform_versions": {platform: VERSION for platform in platforms},
        "platforms": {platform: "available" for platform in platforms},
        "required_platforms_for_full_release": list(platforms),
    }
    history = state.get("historical_releases", [])
    state["historical_releases"] = [APPLE_PREVIOUS, WINDOWS_PREVIOUS, *[v for v in history if v not in {APPLE_PREVIOUS, WINDOWS_PREVIOUS}]]
    state["next_release"] = None
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_readme() -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace(f"Windows {WINDOWS_PREVIOUS}", f"Windows {VERSION}")
    text = text.replace(f"Windows: {WINDOWS_PREVIOUS}", f"Windows: {VERSION}")
    text = re.sub(r"The current Apple release is .*?\.", "The current Apple release is 2.5 for iPhone, iPad, Apple Watch and Mac.", text)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication-date", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.publication_date):
        raise SystemExit("Invalid publication date")
    changed = publish_locales()
    for directory in LOCALES:
        root = ROOT / directory if directory else ROOT
        changed += update_windows(root / "windows-app/index.html", copy_for(directory))
    changed += update_metadata(args.publication_date)
    update_state()
    update_readme()
    print(f"Published Record Picker {VERSION} across {changed} localized pages.")


if __name__ == "__main__":
    main()
