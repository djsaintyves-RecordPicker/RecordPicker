#!/usr/bin/env python3
"""Verify platform-language alternates stay on the equivalent platform route."""

from pathlib import Path
import re

from announce_android_pc_development import COPY, ROOT


routes = ("ios-app", "watch-app", "android-app", "windows-app")
checked = 0
for directory in COPY:
    locale_root = ROOT / directory if directory else ROOT
    for route in routes:
        page = locale_root / route / "index.html"
        text = page.read_text(encoding="utf-8")
        alternates = re.findall(
            r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', text
        )
        assert alternates, page
        for hreflang, href in alternates:
            if hreflang != "x-default":
                assert href.endswith(f"/{route}/"), (page, hreflang, href)
        language_options = re.findall(
            r'<a class="language-option" href="([^"]+)" hreflang="([^"]+)"', text
        )
        assert language_options, page
        for href, hreflang in language_options:
            assert href.endswith(f"/{route}/"), (page, hreflang, href)
        checked += 1

print(f"Verified platform hreflang routes on {checked} localized pages.")
