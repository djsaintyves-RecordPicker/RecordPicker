#!/usr/bin/env python3
"""Verify localized Windows pages, navigation and sitemap coverage."""

from announce_release_2_1 import COMING_SOON
from announce_release_2_3_1 import LOCALES, ROOT


for directory, locale in LOCALES.items():
    root = ROOT / directory if directory else ROOT
    home = (root / "index.html").read_text(encoding="utf-8")
    assert '<span>Windows</span><span class="future-platform"><b>Android</b>' in home, directory
    assert '<span class="future-platform"><b>Windows</b>' not in home, directory
    page = root / "windows-app/index.html"
    text = page.read_text(encoding="utf-8")
    route = f"{directory}/windows-app" if directory not in {"", "en-us"} else "windows-app"
    assert f'<link rel="canonical" href="https://recordpicker.app/{route}/">' in text, directory
    assert f'<meta property="og:url" content="https://recordpicker.app/{route}/">' in text, directory
    assert '<p class="tagline">Windows</p>' in text, directory
    assert 'data-windows-version="2.6"' in text, directory
    assert 'href="https://apps.microsoft.com/detail/9N2ZWRL4M3JC"' in text, directory
    assert 'Windows 11' in text, directory
    assert 'windows-preview' not in text, directory
    assert '"@type":"WebPage"' in text, directory
    assert f'"url":"https://recordpicker.app/{route}/"' in text, directory
    assert 'id="windows-app-schema"' in text, directory
    assert '"@type":"SoftwareApplication"' in text, directory
    assert '"softwareVersion":"2.6"' in text, directory
    assert '"operatingSystem":"Windows 11"' in text, directory
    assert '"downloadUrl":"https://apps.microsoft.com/detail/9N2ZWRL4M3JC"' in text, directory
    assert '"offers"' in text, directory
    assert "Android beta testers" not in text, directory
    assert "bêta-testeurs Android" not in text, directory

    for candidate in root.rglob("*.html"):
        content = candidate.read_text(encoding="utf-8")
        if '<details class="platform-nav">' not in content:
            continue
        assert '<a href="' in content
        assert 'windows-app/">Windows <small>' in content, candidate
        assert '<span>Windows <small>' not in content, candidate

for sitemap_name in ("sitemap.xml", "sitemap-media.xml"):
    sitemap = (ROOT / sitemap_name).read_text(encoding="utf-8")
    for directory in LOCALES:
        route = f"{directory}/windows-app" if directory not in {"", "en-us"} else "windows-app"
        assert f"<loc>https://recordpicker.app/{route}/</loc>" in sitemap, route

print(f"Verified localized Windows pages and navigation across {len(LOCALES)} locales.")
