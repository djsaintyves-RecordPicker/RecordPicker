#!/usr/bin/env python3
"""Exercise the published Record Picker 2.7 on Apple with Windows 2.7 preserved."""

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

        campaign_pages = {
            "help-record-picker/index.html": (
                'lang="en-GB"',
                'href="https://recordpicker.app/help-record-picker/"',
                'href="/fr/aidez-record-picker/"',
                "#HelpRecordPicker",
                "No reward, no script and no five-star request",
            ),
            "fr/aidez-record-picker/index.html": (
                'lang="fr-FR"',
                'href="https://recordpicker.app/fr/aidez-record-picker/"',
                'href="/help-record-picker/"',
                "#HelpRecordPicker",
                "pas de demande de cinq étoiles",
            ),
        }
        for relative, required_fragments in campaign_pages.items():
            campaign = (target / relative).read_text(encoding="utf-8")
            assert all(fragment in campaign for fragment in required_fragments)
            assert "/assets/campaign/basile-records.jpeg" in campaign
            assert "https://apps.apple.com/" in campaign
            assert "https://apps.microsoft.com/detail/9N2ZWRL4M3JC" in campaign

        state = json.loads(
            (target / "data" / "release-state.json").read_text(encoding="utf-8")
        )
        assert state["publication_phase"] == "full"
        assert set(state["current_release"]["platforms"].values()) == {"available"}
        current = state["current_release"]["version"]
        assert current == "2.7"
        assert state["next_release"]["version"] == "2.7.1"
        notes = json.loads((target / 'data/release-notes/2.7.json').read_text())
        from html import unescape
        for root in (target, *(target / locale for locale in LOCALES)):
            for route in ('index.html', 'readme/index.html', 'screenshots/index.html', 'mac-app/index.html'):
                page = (root / route).read_text()
                match = re.search(r'<(section|article)\b[^>]*data-release-version="2\.7"[^>]*>.*?</\1>', page, re.S)
                assert match, (root, route)
                assert 'current-release' in match.group()
                assert 'Windows 2.7' in match.group()
                assert 'release-upcoming' not in match.group() and 'next-release' not in match.group()
                assert any(note in unescape(match.group()) for note in notes.values())
        upcoming_notes = json.loads((target / 'data/release-notes/2.7.1.json').read_text())
        from announce_release_2_3_1 import LOCALES as ANNOUNCEMENT_LOCALES, COMING_SOON
        for directory, locale in ANNOUNCEMENT_LOCALES.items():
            for route in state['next_release']['announcement_routes']:
                page = (target / directory / route).read_text()
                upcoming = re.search(r'<(section|article)\b[^>]*data-release-version="2\.7\.1"[^>]*>.*?</\1>', page, re.S)
                assert upcoming, (directory, route)
                assert COMING_SOON[locale] in unescape(upcoming.group())
                assert 'current-release' not in upcoming.group()
                assert all(note in unescape(upcoming.group()) for note in upcoming_notes[locale])
        before = {p: p.read_bytes() for p in target.rglob('*.html')}
        before[target / 'data/release-state.json'] = (target / 'data/release-state.json').read_bytes()
        run('python3', 'Scripts/publish_release_2_7_apple.py', cwd=target)
        run('python3', 'Scripts/announce_release_2_7.py', cwd=target)
        run('python3', 'Scripts/announce_release_2_7_1.py', cwd=target)
        assert all(p.read_bytes() == content for p, content in before.items())
        assert state["current_release"]["platform_versions"] == {
            "iphone": "2.7", "ipad": "2.7", "watch": "2.7", "mac": "2.7", "windows": "2.7"
        }

        roots = (target,) + tuple(target / locale for locale in LOCALES)
        for root in roots:
            home = (root / "index.html").read_text(encoding="utf-8")
            readme = (root / "readme" / "index.html").read_text(encoding="utf-8")
            screenshots = (root / "screenshots" / "index.html").read_text(encoding="utf-8")
            mac_app = (root / "mac-app" / "index.html").read_text(encoding="utf-8")
            for page in (home, readme, screenshots, mac_app):
                assert page.count('data-release-version="2.6"') == (1 if page == readme else 0)
                assert '<h3>Record Picker 2.7</h3>' in page or '<h2>Record Picker 2.7</h2>' in page
            assert "v20-hero" in home and "v20-home-screens" in home
            assert ".avif" in home and ".webp" in home
            assert f'data-release-version="{current}"' in home
            assert f'data-release-version="{current}"' in readme
            assert home.count('data-release-version="2.5"') == 0
            assert readme.count('data-release-version="2.5"') == 1
            assert screenshots.count('data-release-version="2.5"') == 0
            assert mac_app.count('data-release-version="2.5"') == 0
            assert 'data-release-version="2.4.1"' not in home
            assert 'data-release-version="2.4.1"' not in readme
            assert 'data-release-version="2.4.1"' not in screenshots
            assert 'data-release-version="2.4.1"' not in mac_app
            for page in (home, screenshots, mac_app):
                assert '<h2>Record Picker 2.7</h2>' in page
            assert "Windows 2.5 · " not in home
            assert "Windows 2.7 · " in home
            assert "iPhone · iPad · Apple Watch · Mac · " in home
            assert 'class="v24-feature-list"' in home
            assert 'class="v24-feature-list"' in readme
            assert 'class="v24-feature-list"' in mac_app
            for page in (home, readme):
                assert "Partager un choix ou un parcours" not in page
                assert "Share a pick or listening journey" not in page
                assert "sharing a pick or journey" not in page
            if root.name in {"fr", "fr-ca"}:
                assert "Un graphe fidèle à vos filtres" in home
                assert "Déplacer plusieurs disques ensemble" in home
                assert "Des analyses d’écoute plus fiables" in home
                assert "Votre collection raconte son histoire" in home
            assert "v24-graph-grid" in screenshots
            assert "v24-graph-grid" in mac_app
            screenshot_locale = "en-us"
            expected_graph_path = f"/assets/screenshots/v26/{screenshot_locale}/mac-collection-graph.webp"
            assert expected_graph_path in screenshots
            assert expected_graph_path in mac_app
            assert 'data-release-version="2.2"' not in home
            assert 'data-release-version="2.3"' in readme
            assert 'data-release-version="2.3"' not in screenshots
            assert 'class="section current-release" id="versions" data-release-version="2.7"' in home
            assert re.search(r'class="[^"]*\bplatform-expansion\b[^"]*"', home)
            assert 'class="platform-beta-callout"' in home
            assert home.count('class="beta-site-banner"') == 1
            assert 'data-weekend-campaign' not in home
            assert "support@recordpicker.app?subject=Record%20Picker%20Android%20beta%20volunteer" in home
            assert "12" in home
            assert "android-collection.webp" in home
            assert ">Android<" in home and ">Windows<" in home
            assert home.count('class="future-platform"') == 1
            assert '<span>Windows</span>' in home
            assert "release-upcoming v23-release-card" not in readme
            assert "v23-gallery-marker" not in screenshots
            assert 'data-release-version="2.3.2"' not in home
            assert 'data-release-version="2.3.2"' in readme
            assert 'data-release-version="2.3.2"' not in screenshots
            assert 'class="section current-release" id="versions" data-release-version="2.7"' in home
            assert "release-upcoming v232-release-card" not in readme
            assert "v232-gallery-marker" not in screenshots
            assert readme.count('<div class="context-pair feature-intro">') == 1
            intro = readme.split('<div class="context-pair feature-intro">', 1)[1].split('</div>', 1)[0]
            assert intro.count('<figure class="context-visual wide">') == 2
            assert '<figcaption>Record Picker 2.0</figcaption>' not in readme
            assert "Record Picker 2.0" not in home
            assert "Record Picker 2.0" not in readme
            assert "Record Picker 2.0" not in screenshots
            assert 'data-release-gallery="2.6"' in screenshots
            assert 'data-release-version="2.1.1"' not in screenshots
            assert 'class="media-section v20-preview' not in screenshots
            assert 'class="media-section current-release v20-preview' not in screenshots
            assert f'data-preview-gallery="{current}"' not in screenshots
            if root == target or root.name in {"fr", "fr-ca", "en-us", "en-au", "en-ca", "en-gb"}:
                assert "watch-random-pick" not in screenshots
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
            assert '"softwareVersion":"2.7"' in mac_app
            if root != target and not root.name.startswith("en-"):
                for page in (home, readme, screenshots, mac_app):
                    assert "assets/screenshots/v20/en-us/" not in page

        for root in roots:
            windows = (root / "windows-app/index.html").read_text()
            assert 'data-windows-version="2.7"' in windows
            assert 'Record Picker · 2.7</span>' in windows
            assert 'id="windows-app-schema"' in windows
            for route in ('ios-app/index.html', 'watch-app/index.html', 'mac-app/index.html'):
                apple = (root / route).read_text()
                assert '\"softwareVersion\":\"2.7\"' in apple
                assert 'Record Picker · 2.7</span>' in apple
        css = (target / "quality.css").read_text(encoding="utf-8")
        for selector in (
            ".v20-hero-showcase",
            ".v20-home-screens",
            ".v20-shot-grid",
            ".v24-graph-grid",
            "@media (max-width: 760px)",
        ):
            assert selector in css
    print("OK: Apple 2.7 is published in every locale; Windows 2.7 and screenshot provenance are preserved.")


if __name__ == "__main__":
    main()
