#!/usr/bin/env python3
"""Verify the 2.3.1 coming-soon state without publishing it."""

import json
from pathlib import Path

from announce_release_2_3_1 import LOCALES, ROOT, VERSION


state = json.loads((ROOT / "data/release-state.json").read_text(encoding="utf-8"))
assert state["current_release"]["version"] == "2.3"
assert state["next_release"]["version"] == VERSION
assert set(state["next_release"]["platforms"].values()) == {"coming_soon"}

for directory in LOCALES:
    root = ROOT / directory if directory else ROOT
    home = (root / "index.html").read_text(encoding="utf-8")
    readme = (root / "readme/index.html").read_text(encoding="utf-8")
    shots = (root / "screenshots/index.html").read_text(encoding="utf-8")
    for text in (home, readme, shots):
        assert text.count(f'data-release-version="{VERSION}"') == 1, directory
    assert 'data-release-version="2.3"' in home
    assert 'data-release-version="2.3"' in readme
    assert 'data-release-gallery="2.3"' in shots
    assert "v231-preview next-release" in home
    assert "release-upcoming v231-release-card" in readme
    assert "v231-gallery-marker" in shots
    assert "iPhone · iPad · Apple Watch · Mac" in readme

print(f"Verified staged {VERSION} announcement across {len(LOCALES)} locales.")
