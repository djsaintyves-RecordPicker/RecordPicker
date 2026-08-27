#!/usr/bin/env python3
"""Verify the partial Record Picker 2.3.2 Mac publication."""

import json

from announce_release_2_1 import COMING_SOON
from announce_release_2_3_1 import LOCALES, ROOT, block
from publish_release_2_3_2_mac import PUBLICATION_DATE, VERSION, kicker, partial_status


state = json.loads((ROOT / "data/release-state.json").read_text(encoding="utf-8"))
assert state["current_release"]["version"] == "2.3"
assert state["current_release"]["platform_versions"]["mac"] == VERSION
assert state["next_release"]["version"] == VERSION
assert state["next_release"]["platforms"] == {
    "iphone": "coming_soon",
    "ipad": "coming_soon",
    "mac": "available",
    "watch": "coming_soon",
}

for directory, locale in LOCALES.items():
    root = ROOT / directory if directory else ROOT
    home = (root / "index.html").read_text(encoding="utf-8")
    current = block(home, "2.3", "section")
    candidate = block(home, VERSION, "section")
    assert current and candidate, directory
    status = partial_status(kicker(current.group(0)), COMING_SOON[locale])
    assert status in candidate.group(0), directory
    assert "release-partial" in candidate.group(0), directory

    history = (root / "readme/index.html").read_text(encoding="utf-8")
    candidate = block(history, VERSION, "article")
    assert candidate and "release-partial" in candidate.group(0), directory
    assert status in candidate.group(0), directory

    screenshots = (root / "screenshots/index.html").read_text(encoding="utf-8")
    candidate = block(screenshots, VERSION, "section")
    assert candidate and "release-partial" in candidate.group(0), directory
    assert status in candidate.group(0), directory

    mac = (root / "mac-app/index.html").read_text(encoding="utf-8")
    assert f'"softwareVersion":"{VERSION}"' in mac, directory
    assert f'"dateModified":"{PUBLICATION_DATE}"' in mac, directory
    assert f"Record Picker {VERSION}</p>" in mac, directory
    assert f'<span id="site-footer-version">Record Picker · {VERSION}</span>' in mac, directory

print(f"Verified the {VERSION} Mac publication across {len(LOCALES)} locales.")
