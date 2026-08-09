#!/usr/bin/env python3
"""Promote the prepared Record Picker 2.0 content to the public current release."""

from __future__ import annotations

import json
from pathlib import Path
import re

from refresh_site_visuals_2_0 import asset_url, page_locale


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "data/release-state.json"
CSS_VERSION = "20260809-v20-pick-reveal"
JS_VERSION = "20260809-v20-pick-reveal"
LOCALE_DIRS = {
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "es-mx", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja",
    "ko", "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "th", "tr", "vi",
    "zh-hans", "zh-hant",
}


RANDOM_PICK_DEMO = (
    '<figure class="random-pick-demo" data-random-pick-demo>'
    '<button class="random-pick-button" type="button" aria-label="Random Pick">'
    '<span class="random-pick-stage" aria-hidden="true">'
    '<span class="random-record random-record-a"><i></i></span>'
    '<span class="random-record random-record-b"><i></i></span>'
    '<span class="random-record random-record-c"><i></i></span>'
    '<span class="random-pick-marker">?</span>'
    '</span>'
    '<span class="random-pick-control"><strong>Random Pick</strong><span>♪&nbsp; ↻</span></span>'
    '</button><figcaption class="visually-hidden">Random Pick</figcaption>'
    '</figure>'
)


def release_block(text: str, version: str, tag: str = "section") -> re.Match[str] | None:
    return re.search(
        rf'<{tag}\b[^>]*data-release-version="{re.escape(version)}"[^>]*>.*?</{tag}>',
        text,
        flags=re.DOTALL,
    )


def kicker(block: str) -> str:
    match = re.search(r'<p class="kicker">(.*?)</p>', block, flags=re.DOTALL)
    if not match:
        raise RuntimeError("Current localized release status is missing")
    return match.group(1)


def promote_home(text: str, prefix: str, locale: str) -> str:
    old = release_block(text, "1.9")
    current = release_block(text, "2.0")
    if not current:
        raise RuntimeError("Expected localized 1.9 and 2.0 home release blocks")
    if old:
        available = kicker(old.group(0))
        promoted = current.group(0).replace("section next-release v20-preview", "section v20-preview current-release")
        promoted = re.sub(r'<p class="kicker">.*?</p>', f'<p class="kicker">{available}</p>', promoted, count=1)
        text = text[:current.start()] + promoted + text[current.end():]
        old = release_block(text, "1.9")
        if old:
            text = text[:old.start()] + text[old.end():]
    text = text.replace("<strong>Record Picker 1.9</strong>", "<strong>Record Picker 2.0</strong>")
    text = text.replace('id="version-2-0-preview"', 'id="versions"')
    if 'data-random-pick-demo' not in text:
        text = re.sub(
            r'<figure class="context-visual wide inline-context">.*?</figure>',
            RANDOM_PICK_DEMO,
            text,
            count=1,
            flags=re.DOTALL,
        )
    if 'data-random-pick-demo' not in text:
        text = re.sub(
            r'(<section class="section split"[^>]*>.*?)(</section>)',
            lambda match: match.group(1) + RANDOM_PICK_DEMO + match.group(2),
            text,
            count=1,
            flags=re.DOTALL,
        )
    text = re.sub(
        r'(<figure class="current-screen v20-home-mac">.*?</figure>)',
        lambda match: match.group(1).replace("mac-todays-pick", "mac-random-pick"),
        text,
        count=1,
        flags=re.DOTALL,
    )
    for suffix in (".avif", ".webp"):
        text = re.sub(
            rf'(?:\.\./)*assets/screenshots/v20/[^/]+/mac-random-pick{re.escape(suffix)}',
            asset_url(prefix, locale, "mac-random-pick.jpeg", suffix),
            text,
        )
    return text


def preview_figure(prefix: str, locale: str, filename: str) -> str:
    avif = asset_url(prefix, locale, filename, ".avif")
    webp = asset_url(prefix, locale, filename, ".webp")
    return (
        '<figure class="context-visual wide">'
        f'<picture><source srcset="{avif}" type="image/avif">'
        f'<source srcset="{webp}" type="image/webp">'
        f'<img loading="lazy" alt="" src="{webp}" width="1440" height="900" decoding="async">'
        '</picture><figcaption>Record Picker 2.0</figcaption></figure>'
    )


def promote_readme(text: str, prefix: str, locale: str) -> str:
    old = release_block(text, "1.9", "article")
    current = release_block(text, "2.0", "article")
    if not old or not current:
        raise RuntimeError("Expected localized 1.9 and 2.0 release cards")
    status = re.search(
        r'<p class="release-platform-summary">.*?</p>', old.group(0), flags=re.DOTALL
    )
    if status:
        promoted = current.group(0)
        promoted = promoted.replace("release-card release-preview release-upcoming v20-release-card", "release-card v20-release-card")
        promoted = re.sub(
            r'<p class="release-platform-summary">.*?</p>', status.group(0), promoted, count=1, flags=re.DOTALL
        )
        historical = re.sub(
            r'<p class="release-platform-summary">.*?</p>', "", old.group(0), count=1, flags=re.DOTALL
        )
        text = text[:current.start()] + promoted + text[current.end():]
        old = release_block(text, "1.9", "article")
        if old:
            text = text[:old.start()] + historical + text[old.end():]
    text = re.sub(
        r'(<div class="context-pair feature-intro">.*?</div>)<p>',
        r'\1<p class="feature-summary">',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<p class="feature-summary">.*?Record Picker )1\.9(.*?</p>)',
        r'\g<1>2.0\2',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'<div class="context-pair feature-intro">.*?</div>',
        '<div class="context-pair feature-intro">'
        + preview_figure(prefix, locale, "mac-home.jpeg")
        + preview_figure(prefix, locale, "mac-todays-pick.jpeg")
        + '</div>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    return text


def promote_screenshots(text: str) -> str:
    old = release_block(text, "1.9")
    current = release_block(text, "2.0")
    if not current:
        raise RuntimeError("Expected localized 1.9 and 2.0 screenshot introductions")
    if old:
        available = kicker(old.group(0))
        promoted = current.group(0).replace("media-section next-release v20-preview", "media-section v20-preview current-release")
        promoted = re.sub(r'<p class="kicker">.*?</p>', f'<p class="kicker">{available}</p>', promoted, count=1)
        text = text[:current.start()] + promoted + text[current.end():]
        old = release_block(text, "1.9")
        if old:
            text = text[:old.start()] + text[old.end():]
    return text.replace('data-preview-gallery="2.0"', 'data-release-gallery="2.0"')


def remove_duplicate_visuals(text: str) -> str:
    """Keep each functional 2.0 screenshot at most once on a page."""
    seen: set[str] = set()

    def unique_figure(match: re.Match[str]) -> str:
        figure = match.group(0)
        source = re.search(r'<img\b[^>]*src="([^"]*assets/screenshots/v20/[^"]+)"', figure)
        if not source:
            return figure
        identity = re.sub(r'\.(?:avif|webp|png|jpe?g)(?:\?[^"\']*)?$', '', source.group(1), flags=re.IGNORECASE)
        if identity in seen:
            return ""
        seen.add(identity)
        return figure

    return re.sub(r'<figure\b[^>]*>.*?</figure>', unique_figure, text, flags=re.DOTALL)


def update_page(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    relative = path.relative_to(ROOT)
    depth = len(relative.parts) - 1
    prefix = "../" * depth
    locale = page_locale(path)
    localized_parts = relative.parts[1:] if relative.parts and relative.parts[0] in LOCALE_DIRS else relative.parts
    kind = "/".join(localized_parts)
    if kind == "index.html" and 'data-release-version="2.0"' in text:
        text = promote_home(text, prefix, locale)
    elif kind == "readme/index.html":
        text = promote_readme(text, prefix, locale)
    elif kind == "screenshots/index.html":
        text = promote_screenshots(text)
    text = text.replace('"softwareVersion":"1.9"', '"softwareVersion":"2.0"')
    text = text.replace('"dateModified":"2026-08-08"', '"dateModified":"2026-08-09"')
    text = text.replace("Record Picker v1.9</span>", "Record Picker v2.0</span>")
    text = re.sub(
        r'(<p class="doc-meta">.*?)Record Picker v?1\.9(.*?</p>)',
        r'\1Record Picker v2.0\2',
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<p class="glass-pill eyebrow">.*?)Record Picker 1\.9(.*?</p>)',
        r'\1Record Picker 2.0\2',
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<p class="glass-pill eyebrow">.*?)macOS 1\.9(.*?</p>)',
        r'\1macOS 2.0\2',
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<p class="eyebrow">.*?)Record Picker 1\.9(.*?</p>)',
        r'\1Record Picker 2.0\2',
        text,
        flags=re.DOTALL,
    )
    if relative == Path("index.html") or (relative.parts and relative.parts[0] in {"fr", "fr-ca"}):
        text = text.replace("iPhone paysage", "iPhone en mode paysage")
    text = re.sub(
        r'https://recordpicker\.app/assets/social/social-v19\.jpg\?v=[^"\']+',
        'https://recordpicker.app/assets/social/social-home.png?v=20260809-v20',
        text,
    )
    text = re.sub(r'quality\.css\?v=[^"\']+', f'quality.css?v={CSS_VERSION}', text)
    text = re.sub(r'site\.js\?v=[^"\']+', f'site.js?v={JS_VERSION}', text)
    text = remove_duplicate_visuals(text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def update_state() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state["current_release"] = {
        "version": "2.0",
        "platforms": {"iphone": "available", "ipad": "available", "mac": "available", "watch": "available"},
        "required_platforms_for_full_release": ["iphone", "ipad", "mac", "watch"],
    }
    state["next_release"] = None
    state["historical_releases"] = ["1.9", "1.8", "1.6", "1.5", "1.4", "1.3", "1.2", "1.1"]
    state["publication_assets"] = {
        "hero": "en-us/mac-home.jpeg",
        "screenshots": [
            "en-us/iphone-random-pick.png",
            "en-us/ipad-random-pick.png",
            "en-us/mac-home.jpeg",
        ],
        "social": "assets/social/social-home.png",
    }
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    update_state()
    changed = sum(update_page(path) for path in sorted(ROOT.rglob("*.html")))
    print(f"Published Record Picker 2.0 state on {changed} HTML pages.")


if __name__ == "__main__":
    main()
