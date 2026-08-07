#!/usr/bin/env python3
"""Validate or publish the prepared Record Picker 1.9 website.

The default mode is read-only. --apply also requires --confirm-app-store and
at least one real, non-tutorial 1.9 screenshot in assets/screenshots/v19.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LOCALE_DIRECTORIES = {
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "tr", "zh-hans",
    "zh-hant",
}

RELEASE_STATE_PATH = ROOT / "data" / "release-state.json"
RELEASE_STATE = json.loads(RELEASE_STATE_PATH.read_text(encoding="utf-8"))
CURRENT_VERSION = RELEASE_STATE["current_release"]["version"]
NEXT_VERSION = RELEASE_STATE["next_release"]["version"]
HISTORICAL_VERSIONS = tuple(RELEASE_STATE["historical_releases"])
PUBLICATION_SCREENSHOTS = tuple(
    Path(value) for value in RELEASE_STATE["publication_assets"]["screenshots"]
)
SOCIAL_IMAGE = RELEASE_STATE["publication_assets"]["social"]


def localized_roots() -> list[Path]:
    roots = [ROOT]
    roots.extend(
        path for path in sorted(ROOT.iterdir())
        if path.is_dir() and path.name in LOCALE_DIRECTORIES
    )
    return roots


def available_status(text: str, path: Path) -> str:
    card = re.search(
        rf'<article class="release-card[^>]*data-release-version="{re.escape(HISTORICAL_VERSIONS[0])}".*?</article>',
        text,
        flags=re.DOTALL,
    )
    if card:
        status = re.search(r'<div><h3>.*?</h3><p>(.*?)</p>', card.group(0), re.DOTALL)
        if status:
            return status.group(1)

    current_mac_status = re.search(
        r'<section class="[^"]*upcoming-showcase[^"]*"[^>]*'
        rf'data-release-version="{re.escape(CURRENT_VERSION)}".*?'
        r'<span class="is-available">(.*?)</span>',
        text,
        flags=re.DOTALL,
    )
    if current_mac_status:
        parts = re.split(r'\s*(?:&middot;|·)\s*', current_mac_status.group(1))
        if len(parts) >= 3 and parts[-1].strip():
            return parts[-1].strip()
    raise RuntimeError(f"No localized current availability label in {path}")


def upcoming_status(text: str, path: Path) -> str:
    existing_next = re.search(
        rf'<section class="[^"]*next-release[^"]*"[^>]*'
        rf'data-release-version="{re.escape(NEXT_VERSION)}"[^>]*>.*?'
        r'<p class="kicker">(.*?)</p>',
        text,
        flags=re.DOTALL,
    )
    if existing_next:
        return existing_next.group(1).strip()
    section = re.search(
        r'<section class="[^"]*upcoming-showcase[^"]*"[^>]*'
        rf'data-release-version="{re.escape(CURRENT_VERSION)}".*?</section>',
        text,
        flags=re.DOTALL,
    )
    if section:
        platforms = re.search(
            r'<div class="upcoming-platforms">.*?'
            r'<span(?: class="is-available")?>.*?</span>'
            r'<span>(.*?)</span>',
            section.group(0),
            flags=re.DOTALL,
        )
        if platforms:
            prefix = re.compile(r'^iPhone\s*·\s*iPad\s*·\s*Apple Watch\s*·\s*')
            label = prefix.sub("", platforms.group(1)).strip()
            if label:
                return label.replace(CURRENT_VERSION, NEXT_VERSION)
    raise RuntimeError(f"No localized next-release label in {path}")


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
        rf'data-release-version="{re.escape(CURRENT_VERSION)}">.*?</article>',
        text,
        flags=re.DOTALL,
    )
    if not match:
        if re.search(
            rf'<article class="release-card" data-release-version="{re.escape(CURRENT_VERSION)}">', text
        ):
            return remove_historical_status(text, HISTORICAL_VERSIONS[0])
        raise RuntimeError(f"No prepared {CURRENT_VERSION} release card in {path}")
    card = match.group(0).replace(
        f'<article class="release-card release-preview release-upcoming" data-release-version="{CURRENT_VERSION}">',
        f'<article class="release-card" data-release-version="{CURRENT_VERSION}">',
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
        raise RuntimeError(f"No {CURRENT_VERSION} status in {path}")
    text = text[:match.start()] + card + text[match.end():]
    return remove_historical_status(text, HISTORICAL_VERSIONS[0])


def publish_announcement_section(
    text: str, path: Path, class_name: str, status: str
) -> str:
    section = re.search(
        rf'<section class="[^"]*{re.escape(class_name)}[^"]*"[^>]*'
        rf'data-release-version="{re.escape(CURRENT_VERSION)}"[^>]*>.*?</section>',
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
        raise RuntimeError(f"No {CURRENT_VERSION} status in {path}")
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
        f'"softwareVersion":"{CURRENT_VERSION}"',
        text,
    )
    text = text.replace('<strong>v1.8</strong>', f'<strong>v{CURRENT_VERSION}</strong>')
    text = text.replace(
        '<strong>iOS 1.8 · macOS 1.9</strong>',
        f'<strong>v{CURRENT_VERSION}</strong>',
    )
    text = text.replace(
        f'<strong>Mac · {CURRENT_VERSION}</strong>',
        f'<strong>Record Picker {CURRENT_VERSION}</strong>',
    )
    text = re.sub(
        r'(<footer class="footer"><span id="site-footer-version">)Record Picker (?:v1\.8|1\.8 · macOS 1\.9)(</span>)',
        rf'\1Record Picker v{CURRENT_VERSION}\2',
        text,
    )
    text = re.sub(
        r'"screenshot":"https://recordpicker\.app/assets/screenshots/[^"]+"',
        f'"screenshot":"https://recordpicker.app/assets/screenshots/v19/{RELEASE_STATE["publication_assets"]["hero"]}"',
        text,
    )
    social_url = f"https://recordpicker.app/{SOCIAL_IMAGE}"
    text = re.sub(
        r'(<meta property="og:image" content=")[^"]+("\s*/?>)',
        rf'\1{social_url}\2',
        text,
    )
    text = re.sub(
        r'(<meta name="twitter:image" content=")[^"]+("\s*/?>)',
        rf'\1{social_url}\2',
        text,
    )
    return text


def responsive_picture(
    base: str,
    filename: str,
    width: int,
    height: int,
    *,
    lazy: bool = True,
) -> str:
    stem = filename.rsplit(".", 1)[0]
    loading = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return (
        '<picture>'
        f'<source srcset="{base}/{stem}.avif" type="image/avif">'
        f'<source srcset="{base}/{stem}.webp" type="image/webp">'
        f'<img{loading} alt="" src="{base}/{filename}" width="{width}" '
        f'height="{height}" decoding="async">'
        '</picture>'
    )


def release_gallery(asset_prefix: str) -> str:
    base = f"{asset_prefix}assets/screenshots/v19/en-us"
    iphone = responsive_picture(base, "iphone-today-pick.png", 1206, 2622)
    mac = responsive_picture(base, "mac-today-pick.png", 1280, 900)
    ipad = responsive_picture(base, "ipad-collection-grid.png", 1200, 1600)
    return (
        '<section class="media-section v19-screenshot-gallery" '
        f'data-release-gallery="{CURRENT_VERSION}">'
        '<div class="section-head"><p class="kicker">iPhone · iPad · Mac</p>'
        f'<h2>Record Picker {CURRENT_VERSION}</h2></div>'
        '<div class="shot-grid v19-grid">'
        '<figure class="shot-card iphone v19-iphone">'
        f'{iphone}'
        f'<figcaption>iPhone · Record Picker {CURRENT_VERSION}</figcaption></figure>'
        '<figure class="shot-card mac v19-mac">'
        f'{mac}'
        f'<figcaption>Mac · Record Picker {CURRENT_VERSION}</figcaption></figure>'
        '<figure class="shot-card ipad v19-ipad">'
        f'{ipad}'
        f'<figcaption>iPad · Record Picker {CURRENT_VERSION}</figcaption></figure>'
        '</div></section>'
    )


def insert_release_gallery(text: str, path: Path, asset_prefix: str) -> str:
    if f'data-release-gallery="{CURRENT_VERSION}"' in text:
        return text
    intro = re.search(
        r'<section class="[^"]*upcoming-gallery-intro[^"]*"[^>]*'
        rf'data-release-version="{re.escape(CURRENT_VERSION)}"[^>]*>.*?</section>',
        text,
        flags=re.DOTALL,
    )
    if not intro:
        raise RuntimeError(f"No prepared 1.9 gallery introduction in {path}")
    return text[:intro.end()] + release_gallery(asset_prefix) + text[intro.end():]


def next_release_block(label: str, page_kind: str) -> str:
    if page_kind == "readme":
        return (
            '<article class="release-card release-preview release-upcoming" '
            f'data-release-version="{NEXT_VERSION}"><div class="release-head">'
            f'<span class="version-pill">v{NEXT_VERSION}</span><div>'
            f'<h3>Record Picker {NEXT_VERSION}</h3>'
            f'<p class="release-platform-summary"><strong>{label}</strong></p>'
            '</div></div></article>'
        )
    section_class = "media-section" if page_kind == "screenshots" else "section"
    return (
        f'<section class="{section_class} next-release" '
        f'data-release-version="{NEXT_VERSION}"><div class="section-head">'
        f'<p class="kicker">{label}</p><h2>Record Picker {NEXT_VERSION}</h2>'
        '</div></section>'
    )


def insert_next_release(text: str, path: Path, label: str, page_kind: str) -> str:
    if f'data-release-version="{NEXT_VERSION}"' in text:
        return text
    current_tag = re.search(
        rf'<(?:section|article) class="[^"]*"[^>]*'
        rf'data-release-version="{re.escape(CURRENT_VERSION)}"',
        text,
    )
    if not current_tag:
        raise RuntimeError(f"No {CURRENT_VERSION} insertion point in {path}")
    return text[:current_tag.start()] + next_release_block(label, page_kind) + text[current_tag.start():]


def publish_home_visuals(text: str, path: Path, asset_prefix: str) -> str:
    base = f"{asset_prefix}assets/screenshots/v19/en-us"
    hero = (
        '<div class="hero-showcase v19-hero-showcase">'
        '<figure class="device-frame wide-shot v19-hero">'
        + responsive_picture(base, "mac-today-pick.png", 1280, 900, lazy=False)
        + f'<figcaption>Mac · Record Picker {CURRENT_VERSION}</figcaption>'
        '</figure></div>'
    )
    text, hero_count = re.subn(
        r'<div class="hero-showcase">.*?</div>(?=</section><section class="facts-band">)',
        hero,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if hero_count != 1 and "v19-hero" not in text:
        raise RuntimeError(f"No homepage hero in {path}")

    current_screens = (
        '<div class="screen-grid current-screens v19-home-screens">'
        '<figure class="current-screen v19-home-phone">'
        + responsive_picture(base, "iphone-today-pick.png", 1206, 2622)
        + f'<figcaption>iPhone · Record Picker {CURRENT_VERSION}</figcaption></figure>'
        '<figure class="current-screen v19-home-mac">'
        + responsive_picture(base, "mac-today-pick.png", 1280, 900)
        + f'<figcaption>Mac · Record Picker {CURRENT_VERSION}</figcaption></figure>'
        '<figure class="current-screen v19-home-ipad">'
        + responsive_picture(base, "ipad-collection-grid.png", 1200, 1600)
        + f'<figcaption>iPad · Record Picker {CURRENT_VERSION}</figcaption></figure>'
        '</div>'
    )
    text, gallery_count = re.subn(
        r'<div class="screen-grid current-screens(?: [^"]*)?">.*?</div>'
        r'(?=</section><section class="section seo-links")',
        current_screens,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if gallery_count != 1 and "v19-home-screens" not in text:
        raise RuntimeError(f"No homepage current screenshots in {path}")
    return text


def archive_previous_media(text: str, path: Path) -> str:
    if 'data-previous-versions' in text:
        return text
    start = re.search(
        rf'<section class="media-section v18-screenshot-gallery"[^>]*'
        rf'data-release-version="{re.escape(HISTORICAL_VERSIONS[0])}"',
        text,
    )
    end = text.rfind("</main>")
    if not start or end <= start.start():
        raise RuntimeError(f"No previous-media archive boundary in {path}")
    archive = (
        '<details class="screenshot-archive" data-previous-versions>'
        f'<summary>Record Picker ≤ {HISTORICAL_VERSIONS[0]}</summary>'
        '<div class="screenshot-archive-content">'
        + text[start.start():end]
        + '</div></details>'
    )
    return text[:start.start()] + archive + text[end:]


def real_screenshots() -> list[Path]:
    root = ROOT / "assets" / "screenshots" / "v19"
    if not root.exists():
        return []
    return [
        path for path in root.rglob("*")
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}
        and not re.search(r'tutorial|onboarding|walkthrough', path.name, re.IGNORECASE)
    ]


def missing_publication_screenshots() -> list[Path]:
    root = ROOT / "assets" / "screenshots" / "v19"
    required: list[Path] = []
    for relative in PUBLICATION_SCREENSHOTS:
        required.append(root / relative)
        required.append((root / relative).with_suffix(".webp"))
        required.append((root / relative).with_suffix(".avif"))
    required.extend(
        (
            ROOT / SOCIAL_IMAGE,
            (ROOT / SOCIAL_IMAGE).with_suffix(".webp"),
            (ROOT / SOCIAL_IMAGE).with_suffix(".avif"),
        )
    )
    return [path.relative_to(ROOT) for path in required if not path.is_file()]


def mark_release_state_published() -> None:
    state = json.loads(RELEASE_STATE_PATH.read_text(encoding="utf-8"))
    state["publication_phase"] = "full"
    for platform in state["current_release"]["required_platforms_for_full_release"]:
        state["current_release"]["platforms"][platform] = "available"
    RELEASE_STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


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
        next_status = upcoming_status(home_text, home)
        asset_prefix = "" if root == ROOT else "../"
        published_home = publish_announcement_section(
            home_text, home, "upcoming-showcase", status
        )
        published_home = publish_home_visuals(
            published_home, home, asset_prefix
        )
        outputs[home] = insert_next_release(
            published_home, home, next_status, "home"
        )

        readme = root / "readme" / "index.html"
        published_readme = publish_release_card(
            readme.read_text(encoding="utf-8"), readme, status
        )
        outputs[readme] = insert_next_release(
            published_readme, readme, next_status, "readme"
        )

        screenshots_page = root / "screenshots" / "index.html"
        screenshots_text = publish_announcement_section(
            screenshots_page.read_text(encoding="utf-8"),
            screenshots_page,
            "upcoming-gallery-intro",
            status,
        )
        screenshot_asset_prefix = "../" if root == ROOT else "../../"
        screenshots_text = insert_release_gallery(
            screenshots_text,
            screenshots_page,
            screenshot_asset_prefix,
        )
        outputs[screenshots_page] = insert_next_release(
            screenshots_text,
            screenshots_page,
            next_status,
            "screenshots",
        )
        outputs[screenshots_page] = archive_previous_media(
            outputs[screenshots_page], screenshots_page
        )

    for page in ROOT.rglob("*.html"):
        text = outputs.get(page, page.read_text(encoding="utf-8"))
        outputs[page] = update_current_release_facts(text)

    if args.apply:
        for path, text in outputs.items():
            path.write_text(text, encoding="utf-8")
        mark_release_state_published()
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
