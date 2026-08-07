#!/usr/bin/env python3
"""Exercise the complete 1.9 publication without changing the working tree."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
LOCALES = (
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "tr", "zh-hans",
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
        publish = target / "Scripts" / "publish_release_1_9.py"
        audit = target / "Scripts" / "audit_site_quality.py"
        run("python3", str(publish), "--apply", "--confirm-app-store", cwd=target)
        run("python3", str(audit), cwd=target)
        # A second pass proves that publication remains safely idempotent.
        run("python3", str(publish), "--apply", "--confirm-app-store", cwd=target)
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
            assert "v19-hero" in home and "v19-home-screens" in home
            assert ".avif" in home and ".webp" in home
            assert f'data-release-version="{following}"' in home
            assert f'data-release-version="{following}"' in readme
            assert f'data-release-version="{following}"' in screenshots
            assert f'data-release-gallery="{current}"' in screenshots
            assert "data-previous-versions" in screenshots

        css = (target / "quality.css").read_text(encoding="utf-8")
        for selector in (
            ".v19-hero-showcase",
            ".v19-home-screens",
            ".v19-grid",
            ".screenshot-archive",
            "@media (max-width: 760px)",
        ):
            assert selector in css
    print("OK: complete 1.9 publication is idempotent and responsive-ready.")


if __name__ == "__main__":
    main()
