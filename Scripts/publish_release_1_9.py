#!/usr/bin/env python3
"""Validate or publish the prepared Record Picker 1.9 website.

The default mode is read-only. --apply also requires --confirm-app-store and
at least one real, non-tutorial 1.9 screenshot in assets/screenshots/v19.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LOCALE_DIRECTORIES = {
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "tr", "zh-hans",
    "zh-hant",
}

PUBLICATION_SCREENSHOTS = (
    Path("en-us/iphone-today-pick.png"),
    Path("en-us/ipad-collection-grid.png"),
    Path("en-us/mac-today-pick.png"),
)


def localized_roots() -> list[Path]:
    roots = [ROOT]
    roots.extend(
        path for path in sorted(ROOT.iterdir())
        if path.is_dir() and path.name in LOCALE_DIRECTORIES
    )
    return roots


def available_status(text: str, path: Path) -> str:
    card = re.search(
        r'<article class="release-card[^>]*data-release-version="1\.8".*?</article>',
        text,
        flags=re.DOTALL,
    )
    if card:
        status = re.search(r'<div><h3>.*?</h3><p>(.*?)</p>', card.group(0), re.DOTALL)
        if status:
            return status.group(1)

    current_mac_status = re.search(
        r'<section class="[^"]*upcoming-showcase[^"]*"[^>]*'
        r'data-release-version="1\.9".*?'
        r'<span class="is-available">(.*?)</span>',
        text,
        flags=re.DOTALL,
    )
    if current_mac_status:
        parts = re.split(r'\s*(?:&middot;|·)\s*', current_mac_status.group(1))
        if len(parts) >= 3 and parts[-1].strip():
            return parts[-1].strip()
    raise RuntimeError(f"No localized current availability label in {path}")


def remove_historical_status(text: str, version: str) -> str:
    card = re.search(
        rf'<article class="release-card[^>]*data-release-version="{re.escape(version)}".*?</article>',
        text,
        flags=re.DOTALL,
    )
    if not card:
        return text
    cleaned = re.sub(
        r'(<div><h3>.*?</h3>)<p>.*?</p>',
        r'\1',
        card.group(0),
        count=1,
        flags=re.DOTALL,
    )
    return text[:card.start()] + cleaned + text[card.end():]


def publish_release_card(text: str, path: Path, status: str) -> str:
    match = re.search(
        r'<article class="release-card release-preview release-upcoming" '
        r'data-release-version="1\.9">.*?</article>',
        text,
        flags=re.DOTALL,
    )
    if not match:
        if re.search(
            r'<article class="release-card" data-release-version="1\.9">', text
        ):
            return remove_historical_status(text, "1.8")
        raise RuntimeError(f"No prepared 1.9 release card in {path}")
    card = match.group(0).replace(
        '<article class="release-card release-preview release-upcoming" data-release-version="1.9">',
        '<article class="release-card" data-release-version="1.9">',
        1,
    )
    card, replacements = re.subn(
        r'(<div><h3>.*?</h3>)<p(?: class="[^"]*")?>.*?</p>',
        lambda match: (
            match.group(1)
            + '<p class="release-platform-summary"><strong>'
            + f'iPhone · iPad · Mac · Apple Watch · {status}'
            + '</strong></p>'
        ),
        card,
        count=1,
        flags=re.DOTALL,
    )
    if replacements != 1:
        raise RuntimeError(f"No 1.9 status in {path}")
    text = text[:match.start()] + card + text[match.end():]
    return remove_historical_status(text, "1.8")


def publish_announcement_section(
    text: str, path: Path, class_name: str, status: str
) -> str:
    section = re.search(
        rf'<section class="[^"]*{re.escape(class_name)}[^"]*"[^>]*'
        r'data-release-version="1\.9"[^>]*>.*?</section>',
        text,
        flags=re.DOTALL,
    )
    if not section:
        raise RuntimeError(f"No prepared 1.9 {class_name} section in {path}")
    updated, replacements = re.subn(
        r'<p class="kicker">.*?</p>',
        f'<p class="kicker">{status}</p>',
        section.group(0),
        count=1,
        flags=re.DOTALL,
    )
    if replacements != 1:
        raise RuntimeError(f"No 1.9 status in {path}")
    updated = re.sub(
        r'<div class="upcoming-platforms">.*?</div>',
        '<div class="upcoming-platforms"><span class="is-available">'
        f'iPhone · iPad · Mac · Apple Watch · {status}</span></div>',
        updated,
        count=1,
        flags=re.DOTALL,
    )
    return text[:section.start()] + updated + text[section.end():]


def update_current_release_facts(text: str) -> str:
    text = re.sub(
        r'"softwareVersion":"(?:1\.8|1\.8 \(iOS/iPadOS/watchOS\) · 1\.9 \(macOS\))"',
        '"softwareVersion":"1.9"',
        text,
    )
    text = text.replace('<strong>v1.8</strong>', '<strong>v1.9</strong>')
    text = text.replace(
        '<strong>iOS 1.8 · macOS 1.9</strong>',
        '<strong>v1.9</strong>',
    )
    text = re.sub(
        r'(<footer class="footer"><span id="site-footer-version">)Record Picker (?:v1\.8|1\.8 · macOS 1\.9)(</span>)',
        r'\1Record Picker v1.9\2',
        text,
    )
    text = re.sub(
        r'"screenshot":"https://recordpicker\.app/assets/screenshots/[^"]+"',
        '"screenshot":"https://recordpicker.app/assets/screenshots/v19/en-us/mac-today-pick.png"',
        text,
    )
    return text


def release_gallery(asset_prefix: str) -> str:
    base = f"{asset_prefix}assets/screenshots/v19/en-us"
    return (
        '<section class="media-section v19-screenshot-gallery" '
        'data-release-gallery="1.9">'
        '<div class="section-head"><p class="kicker">iPhone · iPad · Mac</p>'
        '<h2>Record Picker 1.9</h2></div>'
        '<div class="shot-grid v19-grid">'
        '<figure class="shot-card iphone v19-iphone">'
        f'<img loading="lazy" alt="" src="{base}/iphone-today-pick.png" '
        'width="1206" height="2622" decoding="async">'
        '<figcaption>iPhone · Record Picker 1.9</figcaption></figure>'
        '<figure class="shot-card mac v19-mac">'
        f'<img loading="lazy" alt="" src="{base}/mac-today-pick.png" '
        'width="1280" height="900" decoding="async">'
        '<figcaption>Mac · Record Picker 1.9</figcaption></figure>'
        '<figure class="shot-card ipad v19-ipad">'
        f'<img loading="lazy" alt="" src="{base}/ipad-collection-grid.png" '
        'width="1200" height="1600" decoding="async">'
        '<figcaption>iPad · Record Picker 1.9</figcaption></figure>'
        '</div></section>'
    )


def insert_release_gallery(text: str, path: Path, asset_prefix: str) -> str:
    if 'data-release-gallery="1.9"' in text:
        return text
    intro = re.search(
        r'<section class="[^"]*upcoming-gallery-intro[^"]*"[^>]*'
        r'data-release-version="1\.9"[^>]*>.*?</section>',
        text,
        flags=re.DOTALL,
    )
    if not intro:
        raise RuntimeError(f"No prepared 1.9 gallery introduction in {path}")
    return text[:intro.end()] + release_gallery(asset_prefix) + text[intro.end():]


def real_screenshots() -> list[Path]:
    root = ROOT / "assets" / "screenshots" / "v19"
    if not root.exists():
        return []
    return [
        path for path in root.rglob("*")
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        and not re.search(r'tutorial|onboarding|walkthrough', path.name, re.IGNORECASE)
    ]


def missing_publication_screenshots() -> list[Path]:
    root = ROOT / "assets" / "screenshots" / "v19"
    return [relative for relative in PUBLICATION_SCREENSHOTS if not (root / relative).is_file()]


def update_sitemap_dates() -> None:
    today = date.today().isoformat()
    for name in ("sitemap.xml", "sitemap-media.xml"):
        path = ROOT / name
        text = re.sub(
            r'<lastmod>[^<]+</lastmod>',
            f'<lastmod>{today}</lastmod>',
            path.read_text(encoding="utf-8"),
        )
        path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--confirm-app-store",
        action="store_true",
        help="confirm that Record Picker 1.9 is publicly available",
    )
    args = parser.parse_args()
    if args.apply and not args.confirm_app_store:
        parser.error("--apply requires --confirm-app-store")
    screenshots = real_screenshots()
    missing_screenshots = missing_publication_screenshots()
    if args.apply and missing_screenshots:
        parser.error(
            "missing required 1.9 publication screenshot(s): "
            + ", ".join(str(path) for path in missing_screenshots)
        )

    outputs: dict[Path, str] = {}
    for root in localized_roots():
        home = root / "index.html"
        home_text = home.read_text(encoding="utf-8")
        status = available_status(home_text, home)
        outputs[home] = publish_announcement_section(
            home_text, home, "upcoming-showcase", status
        )

        readme = root / "readme" / "index.html"
        outputs[readme] = publish_release_card(
            readme.read_text(encoding="utf-8"), readme, status
        )

        screenshots_page = root / "screenshots" / "index.html"
        screenshots_text = publish_announcement_section(
            screenshots_page.read_text(encoding="utf-8"),
            screenshots_page,
            "upcoming-gallery-intro",
            status,
        )
        asset_prefix = "../" if root == ROOT else "../../"
        outputs[screenshots_page] = insert_release_gallery(
            screenshots_text,
            screenshots_page,
            asset_prefix,
        )

    for page in ROOT.rglob("*.html"):
        text = outputs.get(page, page.read_text(encoding="utf-8"))
        outputs[page] = update_current_release_facts(text)

    if args.apply:
        for path, text in outputs.items():
            path.write_text(text, encoding="utf-8")
        update_sitemap_dates()
        print(
            f"Published Record Picker 1.9 across {len(outputs)} HTML pages "
            f"with {len(screenshots)} real 1.9 screenshots"
        )
    else:
        screenshot_status = f"{len(screenshots)} real 1.9 screenshot(s) found"
        if missing_screenshots:
            screenshot_status += (
                "; required publication files still missing: "
                + ", ".join(str(path) for path in missing_screenshots)
            )
        print(
            "Prepared: 90 localized announcement pages and all current-version "
            f"metadata can switch to 1.9; {screenshot_status}"
        )


if __name__ == "__main__":
    main()
