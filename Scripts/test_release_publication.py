#!/usr/bin/env python3
"""Exercise the published 1.9 / preview 2.0 site without changing the working tree."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
LOCALES = (
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "es-mx", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "th", "tr", "vi", "zh-hans",
    "zh-hant",
)


def run(*arguments: str, cwd: Path) -> None:
    subprocess.run(arguments, cwd=cwd, check=True)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="recordpicker-site-publication-") as directory:
        target = Path(directory) / "site"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        refresh = target / "Scripts" / "refresh_site_visuals_2_0.py"
        audit = target / "Scripts" / "audit_site_quality.py"
        run("python3", str(refresh), cwd=target)
        run("python3", str(audit), cwd=target)
        # A second pass proves that the visual refresh remains safely idempotent.
        run("python3", str(refresh), cwd=target)
        run("python3", str(audit), cwd=target)

        state = json.loads(
            (target / "data" / "release-state.json").read_text(encoding="utf-8")
        )
        assert state["publication_phase"] == "full"
        assert set(state["current_release"]["platforms"].values()) == {"available"}
        current = state["current_release"]["version"]
        following = state["next_release"]["version"]

        roots = (target,) + tuple(target / locale for locale in LOCALES)
        for root in roots:
            home = (root / "index.html").read_text(encoding="utf-8")
            readme = (root / "readme" / "index.html").read_text(encoding="utf-8")
            screenshots = (root / "screenshots" / "index.html").read_text(encoding="utf-8")
            assert "v20-hero" in home and "v20-home-screens" in home
            assert ".avif" in home and ".webp" in home
            assert f'data-release-version="{following}"' in home
            assert f'data-release-version="{following}"' in readme
            assert f'data-release-version="{following}"' in screenshots
            assert f'data-release-gallery="{current}"' not in screenshots
            assert 'data-preview-gallery="2.0"' in screenshots
            assert "data-previous-versions" not in screenshots

        css = (target / "quality.css").read_text(encoding="utf-8")
        for selector in (
            ".v20-hero-showcase",
            ".v20-home-screens",
            ".v20-shot-grid",
            "@media (max-width: 760px)",
        ):
            assert selector in css
    print("OK: published 1.9 state and 2.0 visual preview are idempotent and responsive-ready.")


if __name__ == "__main__":
    main()
