#!/usr/bin/env python3
"""Verify that every localized 2.0 preview preserves the approved meaning."""

from __future__ import annotations

from html import escape
from pathlib import Path
import json

from prepare_site_2_0_preview import LOCALE_NOTE, ROOT, parse_note


def main() -> None:
    state = json.loads((ROOT / "data" / "release-state.json").read_text(encoding="utf-8"))
    assert state["current_release"]["version"] == "1.9"
    assert state["next_release"] == {
        "announce_after_full_release": True,
        "status": "coming_soon",
        "version": "2.0",
    }

    checked = 0
    for directory, note_locale in LOCALE_NOTE.items():
        root = ROOT / directory if directory else ROOT
        copy = parse_note(note_locale)
        assert "Record Picker 2.0" in copy.headline
        assert "Mood Pick" in copy.headline and "Random Pick" in copy.headline
        assert len(copy.bullets) == 5
        assert any("MusicBrainz" in point for point in copy.bullets)

        for path in (
            root / "index.html",
            root / "readme" / "index.html",
            root / "screenshots" / "index.html",
        ):
            text = path.read_text(encoding="utf-8")
            assert 'data-release-version="2.0"' in text, path
            assert escape(copy.headline) in text, path
            assert escape(copy.privacy) in text, path
            for point in copy.bullets:
                assert escape(point) in text, (path, point)
            assert 'data-release-version="1.9"' in text, path
            checked += 1

        home = (root / "index.html").read_text(encoding="utf-8")
        assert 'class="challenge-announcement"' in home
        assert 'id="recordpicker-challenge"' in home

    for french_root in (ROOT, ROOT / "fr", ROOT / "fr-ca"):
        for relative in ("index.html", "readme/index.html", "screenshots/index.html"):
            french = (french_root / relative).read_text(encoding="utf-8")
            assert "tirage équitable" not in french.casefold(), french_root / relative
        assert "Tirage personnalisable" in (french_root / "index.html").read_text(encoding="utf-8")
        french_home = (french_root / "index.html").read_text(encoding="utf-8")
        assert "Cataloguez vos vinyles et vos CD" in french_home
        assert "Votre collection reste privée" in french_home
        assert "vrais collectionneurs" not in french_home.casefold()
    print(
        f"OK: {checked} localized 2.0 previews preserve five approved product facts, "
        "privacy meaning, 1.9 availability and the contest campaign."
    )


if __name__ == "__main__":
    main()
