#!/usr/bin/env python3
"""Verify the 2.3.2 preview, platform roadmap and Android beta campaign."""

import json

from announce_release_2_1 import COMING_SOON
from announce_release_2_3_1 import LOCALES, ROOT
from announce_release_2_3_2 import VERSION, locale_html_paths


OLD_VERSION = "2.3.1"


state = json.loads((ROOT / "data/release-state.json").read_text(encoding="utf-8"))
assert state["current_release"]["version"] == "2.3"
assert state["next_release"]["version"] == VERSION

for directory, locale in LOCALES.items():
    root = ROOT / directory if directory else ROOT
    home = (root / "index.html").read_text(encoding="utf-8")
    readme = (root / "readme/index.html").read_text(encoding="utf-8")
    screenshots = (root / "screenshots/index.html").read_text(encoding="utf-8")
    for text in (home, readme, screenshots):
        assert text.count(f'data-release-version="{VERSION}"') == 1, directory
        assert OLD_VERSION not in text, directory
    assert "v232-preview next-release" in home
    assert "release-upcoming v232-release-card" in readme
    assert "v232-gallery-marker" in screenshots
    assert 'class="platform-beta-callout"' in home
    assert "android-beta-" in home
    assert "Android" in home and "Windows" in home
    assert f'<b>Windows</b><small>{COMING_SOON[locale]}</small>' in home

    for path in locale_html_paths(directory):
        text = path.read_text(encoding="utf-8")
        if "<span>Windows <small>" in text:
            assert f'<span>Windows <small>{COMING_SOON[locale]}</small></span>' in text, path

print(f"Verified staged {VERSION}, platform statuses and Android beta campaign across {len(LOCALES)} locales.")
