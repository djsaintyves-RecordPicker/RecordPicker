#!/usr/bin/env python3
"""Publish Record Picker 2.3 on every localized site page."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "data" / "release-state.json"
PUBLICATION_DATE = "2026-08-22"
LOCALES = (
    "", "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "es-mx", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja",
    "ko", "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "th", "tr", "vi",
    "zh-hans", "zh-hant",
)


def release_block(text: str, version: str, tag: str) -> re.Match[str] | None:
    return re.search(
        rf'<{tag}\b[^>]*data-release-version="{re.escape(version)}"[^>]*>.*?</{tag}>',
        text,
        flags=re.DOTALL,
    )


def status_html(block: str) -> str:
    match = re.search(
        r'<p class="release-platform-summary">.*?</p>', block, flags=re.DOTALL
    )
    if not match:
        raise RuntimeError("Current release card has no localized availability status")
    return match.group(0)


def publish_home(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    current = release_block(text, "2.2", "section")
    upcoming = release_block(text, "2.3", "section")
    if not upcoming:
        raise RuntimeError(f"Expected 2.3 home section in {path}")
    status_source = current.group(0) if current else upcoming.group(0)
    localized_status = re.search(
        r'<p class="kicker">(.*?)</p>', status_source, flags=re.DOTALL
    )
    if not localized_status:
        raise RuntimeError(f"Expected localized availability status in {path}")
    published = upcoming.group(0)
    published = published.replace("v23-preview next-release", "v23-preview current-release")
    published = re.sub(
        r'<p class="kicker">.*?</p>',
        f'<p class="kicker">{localized_status.group(1)}</p>',
        published,
        count=1,
        flags=re.DOTALL,
    )
    text = text[:upcoming.start()] + published + text[upcoming.end():]
    current = release_block(text, "2.2", "section")
    if current:
        text = text[:current.start()] + text[current.end():]
    text = text.replace('data-release-gallery="2.2"', 'data-release-gallery="2.3"')
    text = text.replace('<h2>Record Picker 2.2</h2>', '<h2>Record Picker 2.3</h2>')
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def publish_history(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    current = release_block(text, "2.2", "article")
    upcoming = release_block(text, "2.3", "article")
    if not current or not upcoming:
        raise RuntimeError(f"Expected 2.2 and 2.3 release cards in {path}")
    try:
        current_status = status_html(upcoming.group(0))
    except RuntimeError:
        current_status = status_html(current.group(0))
    published = upcoming.group(0)
    published = published.replace(" release-preview release-upcoming", "")
    published = re.sub(
        r'<p class="release-platform-summary">.*?</p>',
        current_status,
        published,
        count=1,
        flags=re.DOTALL,
    )
    historical = re.sub(
        r'\s*<p class="release-platform-summary">.*?</p>',
        "",
        current.group(0),
        count=1,
        flags=re.DOTALL,
    ).replace(" release-preview release-upcoming", "")
    text = text[:upcoming.start()] + published + historical + text[current.end():]
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def publish_screenshots(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    marker = release_block(text, "2.3", "section")
    if marker:
        text = text[:marker.start()] + text[marker.end():]
    text = text.replace('data-release-gallery="2.2"', 'data-release-gallery="2.3"')
    text = text.replace('<h2>Record Picker 2.2</h2>', '<h2>Record Picker 2.3</h2>')
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def update_shared_metadata(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    text = re.sub(r'("softwareVersion":")[^"]+("?)', r'\g<1>2.3\2', text)
    text = re.sub(r'("dateModified":")[^"]+("?)', rf'\g<1>{PUBLICATION_DATE}\2', text)
    text = re.sub(
        r'<span id="site-footer-version">.*?</span>',
        '<span id="site-footer-version">Record Picker · 2.3</span>',
        text,
        flags=re.DOTALL,
    )
    text = text.replace("iOS 2.1.1 · macOS 2.2", "Record Picker 2.3")
    text = text.replace("Mac · macOS 2.2", "Mac · Record Picker 2.3")
    text = text.replace("macOS 2.2</p>", "Record Picker 2.3</p>")
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def update_state() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state["publication_phase"] = "full"
    state["current_release"] = {
        "version": "2.3",
        "platform_versions": {
            "iphone": "2.3", "ipad": "2.3", "mac": "2.3", "watch": "2.3",
        },
        "platforms": {
            "iphone": "available", "ipad": "available",
            "mac": "available", "watch": "available",
        },
        "required_platforms_for_full_release": ["iphone", "ipad", "mac", "watch"],
    }
    state.pop("next_release", None)
    historical = [version for version in state["historical_releases"] if version != "2.2"]
    state["historical_releases"] = ["2.2", *historical]
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_sitemaps() -> int:
    changed = 0
    for name in ("sitemap.xml", "sitemap-media.xml"):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        updated = re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{PUBLICATION_DATE}</lastmod>', text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def main() -> None:
    changed = 0
    for locale in LOCALES:
        root = ROOT / locale if locale else ROOT
        changed += publish_home(root / "index.html")
        changed += publish_history(root / "readme" / "index.html")
        changed += publish_screenshots(root / "screenshots" / "index.html")
    changed += sum(update_shared_metadata(path) for path in sorted(ROOT.rglob("*.html")))
    changed += update_sitemaps()
    update_state()
    print(f"Published Record Picker 2.3 across {changed} page and sitemap updates.")


if __name__ == "__main__":
    main()
