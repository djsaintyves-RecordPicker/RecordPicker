#!/usr/bin/env python3
"""Refresh site visuals and announce Record Picker 1.9 without publishing it.

The script is idempotent. It keeps 1.8 as the distributed software version,
removes misleading availability labels from historical releases, adds a
localized 1.9 Today Pick preview, expands the 1.8 screenshot galleries with
real light-mode captures, and removes the obsolete dark Watch gallery.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
import re

from prepare_release_1_8 import (
    DEFAULT_VISUAL_CAPTIONS,
    LOCALE_DIRECTORIES,
    PREVIEW_LABELS,
    release_copy,
)


ROOT = Path(__file__).resolve().parents[1]
APP_LOCALIZATIONS = ROOT.parent / "RecordPicker" / "RecordPicker"
PUBLICATION_DATE = "2026-08-02"

LOCALE_BY_HTML_LANGUAGE = {
    "ar": "ar", "ca": "ca", "da": "da", "de": "de", "el": "el",
    "en-AU": "en-AU", "en-CA": "en-CA", "en-GB": "en-GB", "en-US": "en",
    "es-ES": "es", "fi": "fi", "fr-CA": "fr-CA", "fr-FR": "fr",
    "he": "he", "hi": "hi", "id": "id", "it": "it", "ja": "ja",
    "ko": "ko", "nb": "nb", "nl": "nl", "pl": "pl", "pt-BR": "pt-BR",
    "pt-PT": "pt-PT", "ru": "ru", "sv": "sv", "tr": "tr",
    "zh-Hans": "zh-Hans", "zh-Hant": "zh-Hant",
}

TODAY_PICK_KEYS = (
    "Today Pick",
    "A timely reason to rediscover a record you already own.",
    "Why this record today?",
    "Matching happens on this device. Your collection and wishlist are never sent to the music-news service.",
    "News and reissues related to records you want. These are never presented as records you own.",
)

DARK_MAC_REPLACEMENTS = {
    "assets/screenshots/mac/collection-1.0-en-us.jpeg": "assets/screenshots/v18/mac/collection.png",
    "assets/screenshots/mac/collection-1.0-fr.jpeg": "assets/screenshots/v18/mac/collection.png",
    "assets/screenshots/mac/data-quality-1.0-en-us.jpeg": "assets/screenshots/v18/mac/data-quality.png",
    "assets/screenshots/mac/data-quality-1.0-fr.jpeg": "assets/screenshots/v18/mac/data-quality.png",
    "assets/screenshots/mac/mood-pick-1.0-en-us.jpeg": "assets/screenshots/mac/mood-pick-light.jpeg",
    "assets/screenshots/mac/mood-pick-1.0-fr.jpeg": "assets/screenshots/mac/mood-pick-light.jpeg",
    "assets/screenshots/mac/random-pick-1.0-en-us.jpeg": "assets/screenshots/mac/random-pick-light.png",
    "assets/screenshots/mac/record-crate-large-1.0-en-us.jpeg": "assets/screenshots/mac/record-crate-light.png",
    "assets/screenshots/mac/record-crate-small-1.0-en-us.jpeg": "assets/screenshots/mac/record-crate-light.png",
}


def localized_roots() -> list[Path]:
    roots = [ROOT]
    roots.extend(
        path for path in sorted(ROOT.iterdir())
        if path.is_dir() and path.name in LOCALE_DIRECTORIES
    )
    return roots


def html_language(text: str) -> str:
    match = re.search(r'<html lang="([^"]+)"', text)
    return match.group(1) if match else "en-US"


def app_strings(language: str) -> dict[str, str]:
    locale = LOCALE_BY_HTML_LANGUAGE.get(language, "en")
    path = APP_LOCALIZATIONS / f"{locale}.lproj" / "Localizable.strings"
    fallback = APP_LOCALIZATIONS / "en.lproj" / "Localizable.strings"
    text = (path if path.exists() else fallback).read_text(encoding="utf-8")
    values: dict[str, str] = {}
    for key in TODAY_PICK_KEYS:
        pattern = rf'^"{re.escape(key)}"\s*=\s*"((?:\\.|[^"\\])*)";'
        match = re.search(pattern, text, flags=re.MULTILINE)
        values[key] = (
            match.group(1).replace(r'\"', '"').replace(r'\n', '\n')
            if match else key
        )
    return values


def upcoming_label(language: str) -> str:
    if language.startswith("en"):
        return "Coming soon · 1.9"
    label = PREVIEW_LABELS.get(language, ("Coming in 1.8", ""))[0]
    return label.replace("1.8", "1.9")


def upcoming_card(language: str) -> str:
    strings = app_strings(language)
    title = strings["Today Pick"]
    promise = strings["A timely reason to rediscover a record you already own."]
    why = strings["Why this record today?"]
    privacy = strings[
        "Matching happens on this device. Your collection and wishlist are never sent to the music-news service."
    ]
    wishlist = strings[
        "News and reissues related to records you want. These are never presented as records you own."
    ]
    return (
        '<article class="release-card release-preview release-upcoming" '
        'data-release-version="1.9"><div class="release-head">'
        '<span class="version-pill">v1.9</span><div>'
        f'<h3>{escape(title)} — {escape(promise)}</h3>'
        f'<p>{escape(upcoming_label(language))}</p></div></div><ul>'
        f'<li>{escape(why)}</li><li>{escape(privacy)}</li>'
        f'<li>{escape(wishlist)}</li></ul></article>'
    )


def upcoming_showcase(language: str) -> str:
    strings = app_strings(language)
    title = strings["Today Pick"]
    promise = strings["A timely reason to rediscover a record you already own."]
    why = strings["Why this record today?"]
    privacy = strings[
        "Matching happens on this device. Your collection and wishlist are never sent to the music-news service."
    ]
    wishlist = strings[
        "News and reissues related to records you want. These are never presented as records you own."
    ]
    return (
        '<section class="section upcoming-showcase" data-release-version="1.9">'
        '<div class="section-head">'
        f'<p class="kicker">{escape(upcoming_label(language))}</p>'
        f'<h2>Record Picker 1.9 · {escape(title)}</h2>'
        f'<p class="lead">{escape(promise)}</p></div>'
        '<div class="upcoming-preview-panel">'
        f'<p class="upcoming-label">{escape(title)}</p><h3>{escape(why)}</h3>'
        f'<p>{escape(promise)}</p><ul><li>{escape(privacy)}</li>'
        f'<li>{escape(wishlist)}</li></ul></div></section>'
    )


def update_release_cards(text: str, path: Path) -> str:
    language = html_language(text)
    insertion = upcoming_card(language)
    current = re.search(
        r'<article class="release-card[^>]*data-release-version="1\.9".*?</article>',
        text,
        flags=re.DOTALL,
    )
    if current:
        text = text[:current.start()] + insertion + text[current.end():]
    else:
        marker = re.search(
            r'<article class="release-card[^>]*data-release-version="1\.8"', text
        )
        if not marker:
            raise RuntimeError(f"No Record Picker 1.8 card found in {path}")
        text = text[:marker.start()] + insertion + text[marker.start():]

    def historical_card(match: re.Match[str]) -> str:
        card = match.group(0)
        version = re.search(r'<span class="version-pill">v([^<]+)</span>', card)
        if not version or version.group(1) in {"1.8", "1.9"}:
            return card
        return re.sub(
            r'(<div><h3>.*?</h3>)<p>.*?</p>',
            r'\1',
            card,
            count=1,
            flags=re.DOTALL,
        )

    return re.sub(
        r'<article class="release-card[^>]*>.*?</article>',
        historical_card,
        text,
        flags=re.DOTALL,
    )


def capture_locale(language: str) -> str:
    return {"fr-FR": "fr-fr", "fr-CA": "fr-fr", "es-ES": "es-es"}.get(
        language, "en-us"
    )


def shot(asset: str, caption: str, shape: str, prefix: str) -> str:
    return (
        f'<figure class="shot-card {shape}"><img loading="lazy" '
        f'alt="{escape(caption, quote=True)}" src="{prefix}{asset}">'
        f'<figcaption>{escape(caption)}</figcaption></figure>'
    )


def expanded_gallery(language: str, prefix: str) -> str:
    intro, bullets = release_copy(language)
    captions = bullets or DEFAULT_VISUAL_CAPTIONS
    locale = capture_locale(language)
    phone_locale = "fr-fr" if locale == "fr-fr" else "en-us"
    def cap(index: int) -> str:
        return captions[index % len(captions)]

    phone_assets = [
        "collection", "collection-health", "rediscover", "freemium"
    ]
    ipad_assets = [
        "onboarding-collection.png", "onboarding-collection-health.png",
        "onboarding-freemium.png", "original-and-edition-year.png",
    ]
    mac_assets = ["collection.png", "data-quality.png", "list.png", "original-edition.png"]

    phone_figures = "".join(
        shot(f"assets/screenshots/v18/{phone_locale}/iphone-{asset}.png", cap(i), "iphone", prefix)
        for i, asset in enumerate(phone_assets)
    )
    ipad_figures = "".join(
        shot(
            f"assets/screenshots/v18/{'en-us' if asset == 'original-and-edition-year.png' else locale}/{asset}",
            cap(i), "ipad", prefix,
        )
        for i, asset in enumerate(ipad_assets)
    )
    mac_figures = "".join(
        shot(f"assets/screenshots/v18/mac/{asset}", cap(i), "ipad", prefix)
        for i, asset in enumerate(mac_assets)
    )
    return (
        '<section class="media-section v18-screenshot-gallery" data-release-version="1.8">'
        '<div class="section-head"><p class="kicker">Record Picker 1.8</p>'
        f'<h2>Record Picker 1.8</h2><p class="lead">{escape(intro)}</p></div>'
        '<div class="v18-gallery-group"><h3>iPhone · Record Picker 1.8</h3>'
        f'<div class="shot-grid phone-grid">{phone_figures}</div></div>'
        '<div class="v18-gallery-group"><h3>iPad · Record Picker 1.8</h3>'
        f'<div class="shot-grid ipad-grid">{ipad_figures}</div></div>'
        '<div class="v18-gallery-group"><h3>Mac · Record Picker 1.8</h3>'
        f'<div class="shot-grid ipad-grid">{mac_figures}</div></div></section>'
    )


def update_feature_intro(text: str, language: str, prefix: str) -> str:
    figure = re.search(
        r'<figure class="context-visual watch ">.*?</figure>', text, flags=re.DOTALL
    )
    if not figure:
        updated = text
    else:
        locale = capture_locale(language)
        replacement = (
            '<figure class="context-visual wide "><img loading="lazy" '
            'alt="Record Picker 1.8" '
            f'src="{prefix}assets/screenshots/v18/{locale}/onboarding-collection-health.png">'
            '<figcaption>Record Picker 1.8 · Collection Health</figcaption></figure>'
        )
        updated = text[:figure.start()] + replacement + text[figure.end():]

    updated = re.sub(
        r'<figure class="feature-visual watch">.*?</figure>',
        "",
        updated,
        flags=re.DOTALL,
    )
    if "assets/watch/" in updated:
        raise RuntimeError("Unexpected Watch visual remains in feature page")
    return updated


def replace_dark_mac_references(text: str) -> str:
    for old, new in DARK_MAC_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def ensure_preview_stylesheet(text: str, prefix: str) -> str:
    stylesheet = f'<link rel="stylesheet" href="{prefix}v18.css?v=20260802-19-preview">'
    text, replacements = re.subn(
        r'<link rel="stylesheet" href="[^\"]*v18\.css\?v=[^\"]+">',
        stylesheet,
        text,
        count=1,
    )
    if replacements == 0:
        text = text.replace("</head>", stylesheet + "</head>", 1)
    return text


def update_current_release_facts(text: str) -> str:
    text = text.replace('"softwareVersion":"1.6"', '"softwareVersion":"1.8"')
    text = re.sub(
        r'(<footer class="footer"><span>)(?:<span[^>]*>)?.*?</span>(?:</span>)?',
        r'\1Record Picker v1.8</span>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    heading = re.search(
        r'<section class="[^"]*release-history[^"]*".*?'
        r'<div class="section-head">.*?</div>',
        text,
        flags=re.DOTALL,
    )
    if heading:
        updated = heading.group(0).replace("1.6", "1.8").replace("1.0", "1.8")
        text = text[:heading.start()] + updated + text[heading.end():]
    return text


def sitemap_image(asset: str, title: str) -> str:
    return (
        "    <image:image>\n"
        f"      <image:loc>https://recordpicker.app/{asset}</image:loc>\n"
        f"      <image:title>{escape(title)}</image:title>\n"
        f"      <image:caption>{escape(title)}</image:caption>\n"
        "    </image:image>\n"
    )


def update_media_sitemap(roots: list[Path]) -> None:
    path = ROOT / "sitemap-media.xml"
    text = path.read_text(encoding="utf-8")
    text = replace_dark_mac_references(text)
    text = re.sub(
        r'[ \t]*<image:image>\s*<image:loc>[^<]*/assets/watch/[^<]+</image:loc>.*?'
        r'</image:image>\s*',
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'[ \t]*<image:image>\s*'
        r'<image:loc>https://recordpicker\.app/assets/screenshots/v18/[^<]+</image:loc>\s*'
        r'<image:title>Record Picker 1\.8 light screenshot [^<]+</image:title>\s*'
        r'<image:caption>.*?</image:caption>\s*</image:image>\s*',
        "",
        text,
        flags=re.DOTALL,
    )

    for root in roots:
        web_prefix = "" if root == ROOT else f"{root.name}/"
        language = html_language((root / "index.html").read_text(encoding="utf-8"))
        locale = capture_locale(language)
        phone_locale = "fr-fr" if locale == "fr-fr" else "en-us"
        assets = [
            *(f"assets/screenshots/v18/{phone_locale}/iphone-{name}.png" for name in (
                "collection", "collection-health", "rediscover", "freemium"
            )),
            *(f"assets/screenshots/v18/{locale}/{name}" for name in (
                "onboarding-collection.png", "onboarding-collection-health.png",
                "onboarding-freemium.png",
            )),
            "assets/screenshots/v18/en-us/original-and-edition-year.png",
            *(f"assets/screenshots/v18/mac/{name}" for name in (
                "collection.png", "data-quality.png", "list.png", "original-edition.png"
            )),
        ]
        images = "".join(
            sitemap_image(asset, f"Record Picker 1.8 light screenshot {index}")
            for index, asset in enumerate(assets, start=1)
        )
        for suffix in ("", "readme/", "screenshots/", "mac-app/"):
            url = f"https://recordpicker.app/{web_prefix}{suffix}"
            block_match = re.search(
                rf'  <url>\s*<loc>{re.escape(url)}</loc>.*?</url>',
                text,
                flags=re.DOTALL,
            )
            if not block_match:
                raise RuntimeError(f"No media sitemap entry for {url}")
            block = re.sub(
                r'<lastmod>[^<]+</lastmod>',
                f'<lastmod>{PUBLICATION_DATE}</lastmod>',
                block_match.group(0),
                count=1,
            )
            if suffix == "screenshots/":
                block = block.replace(
                    f'<lastmod>{PUBLICATION_DATE}</lastmod>',
                    f'<lastmod>{PUBLICATION_DATE}</lastmod>\n{images}',
                    1,
                )
            text = text[:block_match.start()] + block + text[block_match.end():]
    path.write_text(text, encoding="utf-8")


def main() -> None:
    roots = localized_roots()
    for root in roots:
        home = root / "index.html"
        home_prefix = "" if root == ROOT else "../"
        home_text = update_release_cards(home.read_text(encoding="utf-8"), home)
        language = html_language(home_text)
        showcase = upcoming_showcase(language)
        current_showcase = re.search(
            r'<section class="section upcoming-showcase".*?</section>',
            home_text,
            flags=re.DOTALL,
        )
        if current_showcase:
            home_text = (
                home_text[:current_showcase.start()] + showcase
                + home_text[current_showcase.end():]
            )
        else:
            marker = '<section class="section v18-showcase"'
            if marker not in home_text:
                raise RuntimeError(f"No 1.8 showcase found in {home}")
            home_text = home_text.replace(marker, showcase + marker, 1)
        home.write_text(ensure_preview_stylesheet(home_text, home_prefix), encoding="utf-8")

        readme = root / "readme" / "index.html"
        text = readme.read_text(encoding="utf-8")
        language = html_language(text)
        text = update_release_cards(text, readme)
        prefix = "../" if root == ROOT else "../../"
        text = update_feature_intro(text, language, prefix)
        intro = re.search(
            r'<section class="doc-content">.*?<h2>', text, flags=re.DOTALL
        )
        if intro:
            updated_intro = (
                intro.group(0)
                .replace("Record Picker v1.6 · macOS 1.0", "Record Picker 1.8")
                .replace("Record Picker v1.6 / macOS 1.0", "Record Picker 1.8")
                .replace("version 1.6", "version 1.8")
                .replace("Version 1.6", "Version 1.8")
                .replace("Mac 1.0", "Mac 1.8")
            )
            text = text[:intro.start()] + updated_intro + text[intro.end():]
        text = ensure_preview_stylesheet(text, prefix)
        readme.write_text(text, encoding="utf-8")

        screenshots = root / "screenshots" / "index.html"
        text = screenshots.read_text(encoding="utf-8")
        language = html_language(text)
        prefix = "../" if root == ROOT else "../../"
        text = ensure_preview_stylesheet(text, prefix)
        gallery = expanded_gallery(language, prefix)
        current = re.search(
            r'<section class="media-section v18-screenshot-gallery".*?</section>',
            text,
            flags=re.DOTALL,
        )
        if not current:
            raise RuntimeError(f"No 1.8 gallery in {screenshots}")
        text = text[:current.start()] + gallery + text[current.end():]
        text = re.sub(
            r'<section class="media-section watch-section">.*?</section>',
            "",
            text,
            flags=re.DOTALL,
        )
        screenshots.write_text(text, encoding="utf-8")

    for page in ROOT.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        updated = update_current_release_facts(replace_dark_mac_references(text))
        if updated != text:
            page.write_text(updated, encoding="utf-8")

    update_media_sitemap(roots)

    print(
        f"Prepared {len(roots)} locales: 1.9 preview, historical status cleanup, "
        "light visuals and expanded 1.8 galleries"
    )


if __name__ == "__main__":
    main()
