#!/usr/bin/env python3
"""Verify the search-conversion improvements found during the Safari review."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def meta(text: str, name: str) -> str:
    match = re.search(rf'<meta name="{re.escape(name)}" content="([^"]*)">', text)
    assert match, name
    return match.group(1)


root = read("index.html")
assert "<title>Vinyl Collection App &amp; Random Record Picker | Record Picker</title>" in root
assert "<strong>Record Picker 2.3</strong>" not in root
assert 'rel="canonical" href="https://recordpicker.app/"' in root

guide = read("choose-vinyl-record/index.html")
assert "How to Choose the Right Vinyl Record: 5 Quick Ways" in guide
assert "How to choose the right vinyl record: 5 quick ways" in guide
assert len(meta(guide, "description")) <= 160

watch = read("watch-app/index.html")
assert "Apple Watch Random Record Picker" in watch
assert "Lance un nouveau tirage" not in meta(watch, "description")
assert "Tirer un disque" not in watch
assert "Today’s Pick links reliable music news" in watch

screenshots = read("fr/screenshots/index.html")
assert "Aperçus Record Picker 2.4" in screenshots
assert "iPhone, iPad et Apple Watch" in meta(screenshots, "description")

international_screenshots = read("screenshots/index.html")
assert "Screenshots and videos" in international_screenshots
assert "Voir Record Picker" not in international_screenshots
for screenshot_path in [ROOT / "screenshots/index.html", *ROOT.glob("*/screenshots/index.html")]:
    screenshot_text = screenshot_path.read_text(encoding="utf-8")
    assert "Record Picker 2.4" in screenshot_text
    assert "iPhone · Record Picker 2.4" in screenshot_text
    assert "iPad · Record Picker 2.4" in screenshot_text
    assert "iOS 2.1.1" not in screenshot_text

android = read("fr/android-app/index.html")
assert "12 bêta-testeurs" in android
assert "15 à 20" not in meta(android, "description")
assert "Chromebook" not in meta(android, "description")

for sitemap_name in ("sitemap.xml", "sitemap-media.xml"):
    sitemap = read(sitemap_name)
    for url in (
        "https://recordpicker.app/choose-vinyl-record/",
        "https://recordpicker.app/fr/screenshots/",
        "https://recordpicker.app/fr/android-app/",
    ):
        block = re.search(rf"<url>.*?<loc>{re.escape(url)}</loc>.*?</url>", sitemap, re.DOTALL)
        assert block and "<lastmod>2026-08-31</lastmod>" in block.group(0)

print("OK: search snippets, language, release clarity and sitemap dates are coherent.")
