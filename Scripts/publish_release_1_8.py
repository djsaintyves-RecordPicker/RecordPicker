#!/usr/bin/env python3
"""Validate or publish the prepared Record Picker 1.8 website.

Without --apply, the script only verifies that every localized page is ready.
With --apply, it changes the prepared 1.8 preview to the public release while
preserving each page's existing localized "available now" wording.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LOCALE_DIRECTORIES = {
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "tr", "zh-hans",
    "zh-hant",
}


def localized_roots() -> list[Path]:
    roots = [ROOT]
    roots.extend(
        path for path in sorted(ROOT.iterdir())
        if path.is_dir() and path.name in LOCALE_DIRECTORIES
    )
    return roots


def available_status(text: str, path: Path) -> str:
    match = re.search(
        r'<span class="version-pill">v1\.6</span>.*?<h3>.*?</h3><p>(.*?)</p>',
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise RuntimeError(f"No localized 1.6 availability label in {path}")
    return match.group(1)


def publish_release_card(text: str, path: Path, status: str) -> str:
    match = re.search(
        r'<article class="release-card release-preview" '
        r'data-release-version="1\.8">.*?</article>',
        text,
        flags=re.DOTALL,
    )
    if not match:
        if '<span class="version-pill">v1.8</span>' in text:
            return text
        raise RuntimeError(f"No prepared 1.8 release card in {path}")
    card = match.group(0)
    card = card.replace(
        '<article class="release-card release-preview" data-release-version="1.8">',
        '<article class="release-card" data-release-version="1.8">',
        1,
    )
    card, replacements = re.subn(
        r'(<div><h3>.*?</h3>)<p>.*?</p>',
        rf'\1<p>{status}</p>',
        card,
        count=1,
        flags=re.DOTALL,
    )
    if replacements != 1:
        raise RuntimeError(f"No 1.8 availability label in {path}")
    return text[:match.start()] + card + text[match.end():]


def publish_home(text: str, path: Path, status: str) -> str:
    text = publish_release_card(text, path, status)
    text = text.replace('"softwareVersion":"1.6"', '"softwareVersion":"1.8"')
    text = text.replace('<strong>v1.6</strong>', '<strong>v1.8</strong>', 1)
    showcase = re.search(
        r'<section class="section v18-showcase".*?</section>',
        text,
        flags=re.DOTALL,
    )
    if not showcase:
        raise RuntimeError(f"No 1.8 showcase in {path}")
    section = re.sub(
        r'<p class="kicker">.*?</p>',
        f'<p class="kicker">{status}</p>',
        showcase.group(0),
        count=1,
    )
    text = text[:showcase.start()] + section + text[showcase.end():]
    text = re.sub(
        r'(<footer class="footer"><span>).*?(</span>)',
        r'\1Record Picker v1.8\2',
        text,
        count=1,
    )
    return text


def publish_screenshot_gallery(text: str, path: Path, status: str) -> str:
    gallery = re.search(
        r'<section class="media-section v18-screenshot-gallery".*?</section>',
        text,
        flags=re.DOTALL,
    )
    if not gallery:
        raise RuntimeError(f"No prepared 1.8 screenshot gallery in {path}")
    section = re.sub(
        r'<p class="kicker">.*?</p>',
        f'<p class="kicker">{status}</p>',
        gallery.group(0),
        count=1,
    )
    return text[:gallery.start()] + section + text[gallery.end():]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="replace the prepared preview with the public 1.8 release",
    )
    args = parser.parse_args()

    outputs: dict[Path, str] = {}
    for root in localized_roots():
        home = root / "index.html"
        home_text = home.read_text(encoding="utf-8")
        status = available_status(home_text, home)
        outputs[home] = publish_home(home_text, home, status)

        readme = root / "readme" / "index.html"
        readme_text = readme.read_text(encoding="utf-8")
        outputs[readme] = publish_release_card(readme_text, readme, status)

        screenshots = root / "screenshots" / "index.html"
        screenshot_text = screenshots.read_text(encoding="utf-8")
        outputs[screenshots] = publish_screenshot_gallery(
            screenshot_text, screenshots, status
        )

    if args.apply:
        for path, text in outputs.items():
            path.write_text(text, encoding="utf-8")
        print(f"Published Record Picker 1.8 across {len(outputs)} localized pages")
    else:
        print(
            f"Ready: {len(outputs)} localized pages can switch to Record Picker 1.8; "
            "run again with --apply only after App Store publication"
        )


if __name__ == "__main__":
    main()
