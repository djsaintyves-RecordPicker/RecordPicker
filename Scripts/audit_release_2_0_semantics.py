#!/usr/bin/env python3
"""Verify the localized Record Picker 2.0 publication semantics."""

from __future__ import annotations

import json

from prepare_site_2_0_preview import LOCALE_NOTE, ROOT


def current_block(text: str) -> str:
    marker = 'data-release-version="2.0"'
    position = text.index(marker)
    return text[max(0, position - 180):position + 1800]


def main() -> None:
    state = json.loads((ROOT / "data" / "release-state.json").read_text(encoding="utf-8"))
    assert state["current_release"]["version"] == "2.0"
    assert state["next_release"] is None

    checked = 0
    for directory in LOCALE_NOTE:
        root = ROOT / directory if directory else ROOT
        home = (root / "index.html").read_text(encoding="utf-8")
        readme = (root / "readme" / "index.html").read_text(encoding="utf-8")
        screenshots = (root / "screenshots" / "index.html").read_text(encoding="utf-8")
        for text in (home, readme, screenshots):
            block = current_block(text)
            assert "next-release" not in block
            assert "Mood Pick" in text and "Random Pick" in text
            assert "MusicBrainz" in text
            checked += 1
        assert 'data-random-pick-demo' in home
        assert 'class="challenge-announcement"' in home
        assert 'id="recordpicker-challenge"' in home
        assert 'data-release-gallery="2.0"' in screenshots
        assert "watch-random-pick" in screenshots
        assert 'data-preview-gallery="2.0"' not in screenshots

    for french_root in (ROOT, ROOT / "fr", ROOT / "fr-ca"):
        for relative in ("index.html", "readme/index.html", "screenshots/index.html"):
            french = (french_root / relative).read_text(encoding="utf-8")
            assert "tirage équitable" not in french.casefold(), french_root / relative
        french_home = (french_root / "index.html").read_text(encoding="utf-8")
        assert "Tirage personnalisable" in french_home
        assert "iPhone en mode paysage" in french_home
        assert "Cataloguez vos vinyles et vos CD" in french_home
        assert "Votre collection reste privée" in french_home
        assert "vrais collectionneurs" not in french_home.casefold()
    print(
        f"OK: {checked} localized 2.0 release surfaces preserve product meaning, "
        "Random Pick prominence, watchOS previews and the contest campaign."
    )


if __name__ == "__main__":
    main()
