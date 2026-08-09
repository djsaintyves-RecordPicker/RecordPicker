#!/usr/bin/env python3
"""Replace obsolete site imagery with real, optimized Record Picker 2.0 captures."""

from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets/screenshots/v20"
CSS_VERSION = "20260809-v20-balanced-visuals"

LOCALE_ALIASES = {
    "fr-ca": "fr",
    "es-mx": "es-es",
}

DIMENSIONS = {
    "iphone": (1320, 2868),
    "ipad": (2064, 2752),
    "mac": (1440, 900),
    "watch": (368, 448),
}

GALLERY_ASSETS = {
    "iphone": (
        "iphone-random-pick.png",
        "iphone-todays-pick.png",
        "iphone-mood-pick.png",
        "iphone-collection.png",
    ),
    "ipad": (
        "ipad-random-pick.png",
        "ipad-todays-pick.png",
        "ipad-mood-pick.png",
        "ipad-collection.png",
    ),
    "mac": (
        "mac-home.jpeg",
        "mac-collection.jpeg",
        "mac-todays-pick.jpeg",
        "mac-mood-pick.jpeg",
        "mac-random-pick.jpeg",
        "mac-data-quality.jpeg",
    ),
    "watch": ("watch-random-pick.png",),
}


def page_locale(page: Path) -> str:
    relative = page.relative_to(ROOT)
    first = relative.parts[0]
    if first in {"fr", "fr-ca", "de", "es-es", "es-mx", "ja", "zh-hans"}:
        return LOCALE_ALIASES.get(first, first)
    return "fr" if first in {"index.html", "screenshots", "readme", "support", "privacy", "mac-app"} else "en-us"


def available_locale(locale: str, filename: str) -> str:
    stem = Path(filename).stem
    localized = ASSET_ROOT / locale
    return locale if any((localized / f"{stem}{suffix}").is_file() for suffix in (".avif", ".webp")) else "en-us"


def classify(old_path: str) -> tuple[str, str]:
    lowered = old_path.casefold()
    name = Path(lowered.split("?")[0]).name
    if "/mac/" in lowered or name.startswith("mac-") or "v18/mac" in lowered:
        platform = "mac"
    elif "/ipad/" in lowered or name.startswith("ipad-"):
        platform = "ipad"
    else:
        platform = "iphone"

    if "today" in name or "disque-du-jour" in name:
        feature = "todays-pick"
    elif "mood" in name:
        feature = "mood-pick"
    elif "data-quality" in name and platform == "mac":
        feature = "data-quality"
    elif any(word in name for word in ("draw", "random", "listening", "vinyl-effect")):
        feature = "random-pick"
    elif platform == "mac" and any(word in name for word in ("home", "overview")):
        feature = "home"
    else:
        feature = "collection"
    suffix = ".jpeg" if platform == "mac" else ".png"
    return platform, f"{platform}-{feature}{suffix}"


def asset_url(prefix: str, locale: str, filename: str, suffix: str = ".webp") -> str:
    selected = available_locale(locale, filename)
    return f"{prefix}assets/screenshots/v20/{selected}/{Path(filename).stem}{suffix}"


def replace_screenshot_url(match: re.Match[str], locale: str) -> str:
    prefix, old_path, query = match.group("prefix"), match.group("path"), match.group("query") or ""
    if "/v20/" in old_path:
        return match.group(0)
    _platform, filename = classify(old_path)
    old_suffix = Path(old_path).suffix.casefold()
    suffix = ".avif" if old_suffix == ".avif" else ".webp"
    return asset_url(prefix, locale, filename, suffix) + query


def picture(prefix: str, locale: str, platform: str, filename: str) -> str:
    width, height = DIMENSIONS[platform]
    avif = asset_url(prefix, locale, filename, ".avif")
    webp = asset_url(prefix, locale, filename, ".webp")
    return (
        f'<figure class="shot-card {platform}"><picture>'
        f'<source srcset="{avif}" type="image/avif">'
        f'<source srcset="{webp}" type="image/webp">'
        f'<img loading="lazy" alt="" src="{webp}" width="{width}" height="{height}" decoding="async">'
        '</picture></figure>'
    )


def home_preview(prefix: str, locale: str) -> str:
    """Return the authentic, locale-aware Mac home with the three pick cartridges."""
    filename = "mac-home.jpeg"
    avif = asset_url(prefix, locale, filename, ".avif")
    webp = asset_url(prefix, locale, filename, ".webp")
    return (
        '<figure class="v20-home-preview">'
        '<picture>'
        f'<source srcset="{avif}" type="image/avif">'
        f'<source srcset="{webp}" type="image/webp">'
        f'<img loading="lazy" alt="" src="{webp}" width="1440" height="900" decoding="async">'
        '</picture>'
        '</figure>'
    )


def gallery(prefix: str, locale: str) -> str:
    groups = []
    platform_names = {"mac": "Mac", "iphone": "iPhone", "ipad": "iPad", "watch": "Apple Watch"}
    for platform in ("mac", "iphone", "ipad", "watch"):
        cards = "".join(picture(prefix, locale, platform, name) for name in GALLERY_ASSETS[platform])
        groups.append(
            f'<div class="platform-shot-group"><h3>{platform_names[platform]} · Record Picker 2.0</h3>'
            f'<div class="shot-grid v20-shot-grid {platform}-grid">{cards}</div></div>'
        )
    return (
        '<section class="media-section v20-screenshot-gallery" data-release-gallery="2.0">'
        '<div class="section-head"><h2>Record Picker 2.0</h2></div>'
        + "".join(groups)
        + '</section>'
    )


def update_image_tag(match: re.Match[str]) -> str:
    tag = match.group(0)
    if "assets/screenshots/v20/" not in tag:
        return tag
    asset = re.search(r'assets/screenshots/v20/[^"?]+/(iphone|ipad|mac)-[^"?]+', tag)
    if not asset:
        return tag
    width, height = DIMENSIONS[asset.group(1)]
    tag = re.sub(r'\balt="[^"]*"', 'alt=""', tag)
    tag = re.sub(r'\bwidth="[^"]*"', f'width="{width}"', tag)
    tag = re.sub(r'\bheight="[^"]*"', f'height="{height}"', tag)
    return tag


def update_page(page: Path) -> bool:
    text = page.read_text(encoding="utf-8")
    original = text
    locale = page_locale(page)
    relative = page.relative_to(ROOT)
    depth = len(relative.parts) - 1
    prefix = "../" * depth

    # The 2.0 preview belongs on localized home pages only. Keep this
    # idempotent so a later media refresh can safely replace the illustration.
    if 'class="section next-release v20-preview"' in text:
        def refresh_home_preview(match: re.Match[str]) -> str:
            section = re.sub(
                r'<figure class="v20-home-preview">.*?</figure>',
                "",
                match.group(0),
                flags=re.DOTALL,
            )
            return section.replace("</section>", home_preview(prefix, locale) + "</section>")

        text = re.sub(
            r'<section class="section next-release v20-preview".*?</section>',
            refresh_home_preview,
            text,
            count=1,
            flags=re.DOTALL,
        )

    if relative.name == "index.html" and relative.parent.name == "screenshots":
        text = re.sub(
            r'<section class="media-section v(?:19|20)-screenshot-gallery".*?</section>',
            gallery(prefix, locale),
            text,
            count=1,
            flags=re.DOTALL,
        )
        text = re.sub(
            r'<details class="screenshot-archive" data-previous-versions>.*?</details>',
            "",
            text,
            count=1,
            flags=re.DOTALL,
        )

    url_pattern = re.compile(
        r'(?P<prefix>(?:\.\./)*)(?P<path>assets/screenshots/(?!v20/)[^"\'?# >]+)'
        r'(?P<query>\?[^"\' >]+)?'
    )
    text = url_pattern.sub(lambda match: replace_screenshot_url(match, locale), text)
    text = re.sub(r'<img\b[^>]*>', update_image_tag, text)
    text = re.sub(
        r'(<figure\b[^>]*>.*?assets/screenshots/v20/.*?<figcaption>).*?(</figcaption>)',
        r'\1Record Picker 2.0\2',
        text,
        flags=re.DOTALL,
    )
    text = text.replace("v19-hero-showcase", "v20-hero-showcase")
    text = text.replace("v19-hero", "v20-hero")
    text = text.replace("v19-home-screens", "v20-home-screens")
    text = text.replace("v19-home-phone", "v20-home-phone")
    text = text.replace("v19-home-mac", "v20-home-mac")
    text = text.replace("v19-home-ipad", "v20-home-ipad")
    text = re.sub(
        r'(<section class="section gallery".*?</section>)',
        lambda match: match.group(1).replace("Record Picker 1.8", "Record Picker 2.0"),
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(r'quality\.css\?v=[^"\']+', f'quality.css?v={CSS_VERSION}', text)
    text = text.replace(
        "https://recordpicker.app/assets/screenshots/v19/en-us/mac-today-pick.png",
        "https://recordpicker.app/assets/screenshots/v20/en-us/mac-home.webp",
    )
    if text != original:
        page.write_text(text, encoding="utf-8")
        return True
    return False


def sitemap_locale(url: str) -> str:
    parts = [part for part in urlsplit(url).path.split("/") if part]
    if not parts:
        return "fr"
    return LOCALE_ALIASES.get(parts[0], parts[0]) if parts[0] in {
        "fr", "fr-ca", "de", "es-es", "es-mx", "ja", "zh-hans"
    } else "en-us"


def sitemap_images(url: str) -> tuple[str, ...]:
    path = urlsplit(url).path
    parts = [part for part in path.split("/") if part]
    if path.endswith("/screenshots/"):
        return tuple(name for names in GALLERY_ASSETS.values() for name in names)
    if path == "/" or len(parts) == 1 or path.endswith(("/readme/", "/mac-app/")):
        return ("mac-todays-pick.jpeg", "iphone-todays-pick.png", "ipad-collection.png")
    return ("mac-home.jpeg",)


def update_media_sitemap() -> None:
    path = ROOT / "sitemap-media.xml"
    text = path.read_text(encoding="utf-8")

    def update_url(match: re.Match[str]) -> str:
        block = match.group(0)
        location = re.search(r"<loc>([^<]+)</loc>", block)
        if not location:
            return block
        url = location.group(1)
        locale = sitemap_locale(url)
        block = re.sub(r"\s*<image:image>.*?</image:image>", "", block, flags=re.DOTALL)
        block = re.sub(r"\s*<video:video>.*?</video:video>", "", block, flags=re.DOTALL)
        entries = []
        for filename in sitemap_images(url):
            selected = available_locale(locale, filename)
            asset = f"https://recordpicker.app/assets/screenshots/v20/{selected}/{Path(filename).stem}.webp"
            entries.append(
                "\n    <image:image>\n"
                f"      <image:loc>{asset}</image:loc>\n"
                "      <image:title>Record Picker 2.0 app preview</image:title>\n"
                "    </image:image>"
            )
        return block.replace("</url>", "".join(entries) + "\n  </url>")

    text = re.sub(r"<url>.*?</url>", update_url, text, flags=re.DOTALL)
    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    changed = sum(update_page(page) for page in sorted(ROOT.rglob("*.html")))
    update_media_sitemap()
    print(f"Updated {changed} HTML pages with current 2.0 visuals.")


if __name__ == "__main__":
    main()
