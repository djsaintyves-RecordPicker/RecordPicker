#!/usr/bin/env python3
"""Exercise published 2.3.2 pages with the staged 2.4 announcement."""

from __future__ import annotations

import json
from pathlib import Path
import re
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
        audit = target / "Scripts" / "audit_site_quality.py"
        run("python3", str(audit), cwd=target)
        # A second pass proves that the publication audit remains repeatable.
        run("python3", str(audit), cwd=target)

        state = json.loads(
            (target / "data" / "release-state.json").read_text(encoding="utf-8")
        )
        assert state["publication_phase"] == "full"
        assert set(state["current_release"]["platforms"].values()) == {"available"}
        current = state["current_release"]["version"]
        assert current == "2.3.2"
        next_release = state.get("next_release")
        assert next_release == {
            "version": "2.4",
            "platforms": {
                "iphone": "coming_soon",
                "ipad": "coming_soon",
                "mac": "coming_soon",
                "watch": "coming_soon",
            },
        }
        assert state["current_release"]["platform_versions"] == {
            "iphone": "2.3.2", "ipad": "2.3.2", "watch": "2.3.2", "mac": "2.3.2"
        }

        roots = (target,) + tuple(target / locale for locale in LOCALES)
        for root in roots:
            home = (root / "index.html").read_text(encoding="utf-8")
            readme = (root / "readme" / "index.html").read_text(encoding="utf-8")
            screenshots = (root / "screenshots" / "index.html").read_text(encoding="utf-8")
            mac_app = (root / "mac-app" / "index.html").read_text(encoding="utf-8")
            assert "v20-hero" in home and "v20-home-screens" in home
            assert ".avif" in home and ".webp" in home
            assert f'data-release-version="{current}"' in home
            assert f'data-release-version="{current}"' in readme
            assert home.count('data-release-version="2.4"') == 1
            assert readme.count('data-release-version="2.4"') == 1
            assert screenshots.count('data-release-version="2.4"') == 1
            assert mac_app.count('data-release-version="2.4"') == 1
            for page in (home, screenshots, mac_app):
                assert "<h2>Record Picker 2.4 · Apple</h2>" in page
            assert "Apple · " in readme
            assert 'class="v24-feature-list"' in home
            assert 'class="v24-feature-list"' in readme
            assert 'class="v24-feature-list"' in mac_app
            if root.name in {"fr", "fr-ca"}:
                assert "Choisissez un nombre de disques ou une durée approximative" in home
                assert "Cette file est distincte de la liste de souhaits" in home
                assert "Sur Mac et iPad, une vue interactive révèle les liens" in home
                assert "Pour ajouter un nouveau disque sur Mac, scannez son code-barres" in home
                assert "Ajouter un nouveau disque par code-barres" in home
            assert "v24-graph-grid" in home
            assert "v24-graph-grid" in screenshots
            assert "v24-graph-grid" in mac_app
            screenshot_locale = "fr" if root.name in {"fr", "fr-ca"} else "en-us"
            expected_graph_path = f"/assets/screenshots/v24/{screenshot_locale}/collection-graph-interactive.webp"
            assert expected_graph_path in home
            assert expected_graph_path in screenshots
            assert expected_graph_path in mac_app
            assert 'data-release-version="2.2"' not in home
            assert 'data-release-version="2.3"' in readme
            assert 'data-release-version="2.3"' not in screenshots
            assert "v232-preview current-release" in home
            assert re.search(r'class="[^"]*\bplatform-expansion\b[^"]*"', home)
            assert 'class="platform-beta-callout"' in home
            assert "support@recordpicker.app?subject=Record%20Picker%20Android%20beta%20volunteer" in home
            assert "12" in home
            assert "android-beta-" in home and ".webp" in home
            assert ">Android<" in home and ">Windows<" in home
            assert home.count('class="future-platform"') == 2
            assert "release-upcoming v23-release-card" not in readme
            assert "v23-gallery-marker" not in screenshots
            assert 'data-release-version="2.3.2"' in home
            assert 'data-release-version="2.3.2"' in readme
            assert 'data-release-version="2.3.2"' not in screenshots
            assert "v232-preview current-release" in home
            assert "release-upcoming v232-release-card" not in readme
            assert "v232-gallery-marker" not in screenshots
            assert readme.count('<div class="context-pair feature-intro">') == 1
            intro = readme.split('<div class="context-pair feature-intro">', 1)[1].split('</div>', 1)[0]
            assert intro.count('<figure class="context-visual wide">') == 2
            assert '<figcaption>Record Picker 2.0</figcaption>' not in readme
            assert "Record Picker 2.0" not in home
            assert "Record Picker 2.0" not in readme
            assert "Record Picker 2.0" not in screenshots
            assert f'data-release-gallery="{current}"' in screenshots
            assert 'data-release-version="2.1.1"' not in screenshots
            assert 'class="media-section v20-preview' not in screenshots
            assert 'class="media-section current-release v20-preview' not in screenshots
            assert f'data-preview-gallery="{current}"' not in screenshots
            if root == target or root.name in {"fr", "fr-ca", "en-us", "en-au", "en-ca", "en-gb"}:
                assert "watch-random-pick" in screenshots
            assert "data-random-pick-demo" in home
            assert 'class="random-vinyl"' in home
            assert 'class="random-pick-button"' in home
            assert 'class="random-pick-title"' in home
            assert 'class="random-pick-tags"' in home
            for cover in ("sees-the-light", "in-waves", "hunky-dory", "moon-safari"):
                assert f"/assets/demo/{cover}.jpg" in home
            assert "random-record-a" not in home
            assert "random-picked-cover" not in home
            assert "data-previous-versions" not in screenshots
            assert '"softwareVersion":"2.3.2"' in mac_app
            if root != target and not root.name.startswith("en-"):
                for page in (home, readme, screenshots, mac_app):
                    assert "assets/screenshots/v20/en-us/" not in page

        css = (target / "quality.css").read_text(encoding="utf-8")
        for selector in (
            ".v20-hero-showcase",
            ".v20-home-screens",
            ".v20-shot-grid",
            ".v24-graph-grid",
            "@media (max-width: 760px)",
        ):
            assert selector in css
    print("OK: Record Picker 2.3.2 remains published and 2.4 is announced across every localized site.")


if __name__ == "__main__":
    main()
