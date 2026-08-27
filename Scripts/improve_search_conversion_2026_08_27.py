#!/usr/bin/env python3
"""Improve high-impression search snippets and release clarity after the SEO review."""

from __future__ import annotations

from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-08-27"
CURRENT_APP_RELEASE_DATE = "2026-08-22"
SITE = "https://recordpicker.app"


def replace_metadata(path: Path, title: str, description: str) -> None:
    text = path.read_text(encoding="utf-8")
    escaped_title = escape(title, quote=True)
    escaped_description = escape(description, quote=True)
    text = re.sub(
        r"<title>.*?</title>",
        f"<title>{escaped_title}</title>",
        text,
        count=1,
        flags=re.DOTALL,
    )
    replacements = {
        ("name", "description"): escaped_description,
        ("property", "og:title"): escaped_title,
        ("property", "og:description"): escaped_description,
        ("property", "og:image:alt"): escaped_title,
        ("name", "twitter:title"): escaped_title,
        ("name", "twitter:description"): escaped_description,
        ("name", "twitter:image:alt"): escaped_title,
    }
    for (attribute, key), value in replacements.items():
        text = re.sub(
            rf'(<meta {attribute}="{re.escape(key)}" content=")[^"]*(")',
            rf"\g<1>{value}\2",
            text,
            count=1,
        )
    text = re.sub(
        r'("dateModified":")[^"]+',
        rf"\g<1>{CURRENT_APP_RELEASE_DATE}",
        text,
    )
    path.write_text(text, encoding="utf-8")


def clarify_home_release(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        '<section class="facts-band"><div><strong>Record Picker 2.3</strong>',
        '<section class="facts-band"><div><strong>Record Picker</strong>',
        1,
    )
    path.write_text(text, encoding="utf-8")


def refresh_screenshot_version_labels(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    replacements = {
        "Mac · Record Picker 2.3": "Mac · Record Picker 2.3.2",
        "iPhone · iOS 2.1.1": "iPhone · Record Picker 2.3",
        "iPad · iOS 2.1.1": "iPad · Record Picker 2.3",
        "Apple Watch · iOS 2.1.1": "Apple Watch · Record Picker 2.3",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def improve_guide_copy(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"<h1>.*?</h1>",
        "<h1>How to choose the right vinyl record: 5 quick ways</h1>",
        text,
        count=1,
        flags=re.DOTALL,
    )
    path.write_text(text, encoding="utf-8")
    replace_metadata(
        path,
        "How to Choose the Right Vinyl Record: 5 Quick Ways",
        "Can’t decide what vinyl to play? Try five quick methods based on mood, a random pick, music news, collection rotation or one simple constraint.",
    )


def sync_root_route_from_en_us(route: str) -> None:
    source = (ROOT / "en-us" / route / "index.html").read_text(encoding="utf-8")
    text = source.replace("../../", "../")
    text = text.replace(
        f"https://recordpicker.app/en-us/{route}/",
        f"https://recordpicker.app/{route}/",
    )
    (ROOT / route / "index.html").write_text(text, encoding="utf-8")


def touch_sitemap_urls(path: Path, urls: set[str]) -> None:
    text = path.read_text(encoding="utf-8")

    def update(match: re.Match[str]) -> str:
        block = match.group(0)
        location = re.search(r"<loc>([^<]+)</loc>", block)
        if not location or location.group(1) not in urls:
            return block
        return re.sub(
            r"<lastmod>[^<]+</lastmod>",
            f"<lastmod>{TODAY}</lastmod>",
            block,
            count=1,
        )

    updated = re.sub(r"<url>.*?</url>", update, text, flags=re.DOTALL)
    path.write_text(updated, encoding="utf-8")


def main() -> None:
    homepage_title = "Vinyl Collection App & Random Record Picker | Record Picker"
    homepage_description = (
        "Catalog vinyl records and CDs, import Discogs, check duplicates and use "
        "Random Pick, Mood Pick or Today’s Pick to choose what to play. Private and ad-free."
    )
    replace_metadata(ROOT / "index.html", homepage_title, homepage_description)
    replace_metadata(ROOT / "en-us/index.html", homepage_title, homepage_description)

    improve_guide_copy(ROOT / "choose-vinyl-record/index.html")
    improve_guide_copy(ROOT / "en-us/choose-vinyl-record/index.html")

    sync_root_route_from_en_us("watch-app")
    sync_root_route_from_en_us("screenshots")
    for path in (ROOT / "watch-app/index.html", ROOT / "en-us/watch-app/index.html"):
        replace_metadata(
            path,
            "Apple Watch Random Record Picker | Record Picker",
            "Pick another record from your wrist with Random Pick, favorites and listening modes. Record Picker keeps your vinyl and CD collection private and in sync.",
        )
    for path in (ROOT / "screenshots/index.html", ROOT / "en-us/screenshots/index.html"):
        replace_metadata(
            path,
            "Record Picker Screenshots: Mac 2.3.2, iPhone & Watch",
            "See Record Picker 2.3.2 on Mac and 2.3 on iPhone, iPad and Apple Watch, including the catalog, Random Pick, Mood Pick and Today’s Pick.",
        )
    replace_metadata(
        ROOT / "fr/screenshots/index.html",
        "Aperçus Record Picker : Mac 2.3.2, iPhone et Watch",
        "Découvrez Record Picker 2.3.2 sur Mac et 2.3 sur iPhone, iPad et Apple Watch : catalogue, tirage aléatoire, Mood Pick et Disque du jour.",
    )
    replace_metadata(
        ROOT / "android-app/index.html",
        "Record Picker Android Beta: 12 Testers Wanted",
        "Join the 14-day Record Picker closed Android beta. We need 12 testers with a Google Account and a compatible Android phone or tablet.",
    )
    replace_metadata(
        ROOT / "fr/android-app/index.html",
        "Bêta Android Record Picker : 12 testeurs recherchés",
        "Participez pendant 14 jours au test fermé de Record Picker sur Android. Nous recherchons 12 testeurs avec un compte Google et un appareil compatible.",
    )

    home_paths = [ROOT / "index.html"]
    home_paths.extend(
        path
        for path in ROOT.glob("*/index.html")
        if path.parent.name not in {"assets", "press"}
    )
    for path in home_paths:
        clarify_home_release(path)

    screenshot_paths = [ROOT / "screenshots/index.html"]
    screenshot_paths.extend(ROOT.glob("*/screenshots/index.html"))
    for path in screenshot_paths:
        refresh_screenshot_version_labels(path)

    changed_urls = {
        SITE + "/",
        SITE + "/choose-vinyl-record/",
        SITE + "/watch-app/",
        SITE + "/screenshots/",
        SITE + "/fr/screenshots/",
        SITE + "/android-app/",
        SITE + "/fr/android-app/",
    }
    for name in ("sitemap.xml", "sitemap-media.xml"):
        touch_sitemap_urls(ROOT / name, changed_urls)

    print(
        "Improved the high-impression English pages, refreshed French snippets, "
        f"and clarified release labels on {len(home_paths)} homepages."
    )


if __name__ == "__main__":
    main()
