#!/usr/bin/env python3
"""Regression checks for the September 2026 Google/Bing remediation."""

from __future__ import annotations

from html import unescape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
INTERNATIONAL_ROUTES = (
    "choose-vinyl-record",
    "readme",
    "support",
    "privacy",
    "random-vinyl-record-picker",
    "manage-vinyl-collection",
)
BING_SHORT_DESCRIPTION_PAGES = (
    "ko/index.html",
    "ar/windows-app/index.html",
    "ca/windows-app/index.html",
    "zh-hant/windows-app/index.html",
    "tr/index.html",
    "zh-hant/index.html",
    "fi/windows-app/index.html",
    "he/windows-app/index.html",
    "en-au/index.html",
    "ru/index.html",
    "zh-hans/index.html",
    "fr/windows-app/index.html",
    "ko/windows-app/index.html",
    "el/index.html",
    "he/readme/index.html",
    "ja/index.html",
    "da/index.html",
    "ru/windows-app/index.html",
    "ru/privacy/index.html",
    "en-us/support/index.html",
    "zh-hant/manage-vinyl-collection/index.html",
    "windows-app/index.html",
    "en-us/windows-app/index.html",
    "en-au/windows-app/index.html",
    "en-ca/windows-app/index.html",
    "en-gb/windows-app/index.html",
)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def match(pattern: str, text: str) -> str:
    result = re.search(pattern, text, flags=re.DOTALL)
    assert result, pattern
    return unescape(result.group(1))


for route in INTERNATIONAL_ROUTES:
    relative = f"{route}/index.html"
    text = read(relative)
    assert match(r'<html[^>]+lang="([^"]+)"', text) in {"en", "en-US"}, relative
    assert match(r'<link rel="canonical" href="([^"]+)"', text) == f"https://recordpicker.app/{route}/"
    assert f'hreflang="en-US" href="https://recordpicker.app/{route}/"' in text
    assert f'hreflang="x-default" href="https://recordpicker.app/{route}/"' in text
    assert 'data-lang="en-us"' in text
    assert f"https://recordpicker.app/en-us/{route}/" not in text

guide = read("choose-vinyl-record/index.html")
assert "How to Choose the Right Vinyl Record to Play (5 Ways)" in guide
assert "find the right album to play in seconds" in match(r'<meta name="description" content="([^"]*)">', guide)

for relative in BING_SHORT_DESCRIPTION_PAGES:
    description = match(r'<meta name="description" content="([^"]*)">', read(relative))
    assert len(description) >= 150, (relative, len(description), description)

for path in ROOT.rglob("*.html"):
    if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
        continue
    text = path.read_text(encoding="utf-8")
    for href in re.findall(r'href="(/en-us/(?:[^"]*)?)"', text):
        route = href.removeprefix("/en-us/").strip("/")
        counterpart = ROOT / route / "index.html" if route else ROOT / "index.html"
        assert not counterpart.exists(), (path.relative_to(ROOT), href)

for path in (ROOT / "en-us").rglob("index.html"):
    route = path.relative_to(ROOT / "en-us").parent.as_posix()
    counterpart = ROOT / route / "index.html" if route != "." else ROOT / "index.html"
    if not counterpart.exists():
        continue
    canonical = f"https://recordpicker.app/{route}/" if route != "." else "https://recordpicker.app/"
    text = path.read_text(encoding="utf-8")
    assert match(r'<link rel="canonical" href="([^"]+)"', text) == canonical, path
    assert match(r'<meta property="og:url" content="([^"]+)"', text) == canonical, path

for sitemap_name in ("sitemap.xml", "sitemap-media.xml"):
    sitemap = read(sitemap_name)
    for path in (ROOT / "en-us").rglob("index.html"):
        route = path.relative_to(ROOT / "en-us").parent.as_posix()
        counterpart = ROOT / route / "index.html" if route != "." else ROOT / "index.html"
        if counterpart.exists():
            duplicate = f"https://recordpicker.app/en-us/{route}/" if route != "." else "https://recordpicker.app/en-us/"
            assert f"<loc>{duplicate}</loc>" not in sitemap, (sitemap_name, duplicate)
    for route in INTERNATIONAL_ROUTES:
        url = f"https://recordpicker.app/{route}/"
        block = re.search(rf"<url>.*?<loc>{re.escape(url)}</loc>.*?</url>", sitemap, re.DOTALL)
        assert block, (sitemap_name, url)
        assert "<lastmod>2026-09-26</lastmod>" in block.group(0), (sitemap_name, url)

print("OK: international English content, Bing descriptions, canonical menus and sitemap dates are coherent.")
