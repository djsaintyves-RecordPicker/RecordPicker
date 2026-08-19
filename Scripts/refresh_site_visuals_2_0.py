#!/usr/bin/env python3
"""Replace obsolete site imagery with real, optimized Record Picker 2.0 captures."""

from __future__ import annotations

import json
from pathlib import Path
import re
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets/screenshots/v20"
CSS_VERSION = "20260811-press-review"

LOCALE_ALIASES = {
    "en-au": "en-us",
    "en-ca": "en-us",
    "en-gb": "en-us",
    "fr-ca": "fr",
}

SITE_LOCALES = {
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "es-mx", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja",
    "ko", "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "th", "tr", "vi",
    "zh-hans", "zh-hant",
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

COMPACT_README_INTROS = {
    "th": (
        "คอลเลกชันที่เป็นระเบียบและค้นพบได้เสมอ",
        (
            "นำเข้า CSV, สแกนบาร์โค้ด และเพิ่มข้อมูลด้วยตนเอง",
            "ค้นหาข้อมูลผ่าน MusicBrainz และ Discogs เมื่อคุณร้องขอ",
            "ตรวจสอบคุณภาพข้อมูล รายการซ้ำ และภาพปก",
            "เลือกแบบสุ่มหรือด้วย Mood Pick พร้อมตัวกรองและประวัติ",
            "ซิงค์ส่วนตัวผ่าน iCloud และสำรองข้อมูลเป็น JSON",
            "ฟรีสูงสุด 100 แผ่น ซื้อ Pro ครั้งเดียวเพื่อใช้คอลเลกชันไม่จำกัด",
        ),
    ),
    "vi": (
        "Bộ sưu tập gọn gàng, luôn dễ khám phá",
        (
            "Nhập CSV, quét mã vạch và thêm dữ liệu thủ công",
            "Tra cứu MusicBrainz và Discogs chỉ khi bạn yêu cầu",
            "Kiểm tra chất lượng dữ liệu, bản trùng lặp và ảnh bìa",
            "Chọn ngẫu nhiên hoặc Mood Pick với bộ lọc và lịch sử",
            "Đồng bộ riêng tư qua iCloud và sao lưu JSON",
            "Miễn phí tối đa 100 đĩa; mua Pro một lần để mở khóa bộ sưu tập không giới hạn",
        ),
    ),
}


def page_locale(page: Path) -> str:
    relative = page.relative_to(ROOT)
    first = relative.parts[0]
    if first in SITE_LOCALES:
        return first
    return "en-us" if first == "index.html" else ("fr" if first in {"screenshots", "readme", "support", "privacy", "mac-app"} else "en-us")


def available_locale(locale: str, filename: str) -> str:
    stem = Path(filename).stem
    localized = ASSET_ROOT / locale
    if any((localized / f"{stem}{suffix}").is_file() for suffix in (".avif", ".webp")):
        return locale
    fallback = LOCALE_ALIASES.get(locale)
    if fallback and any(
        (ASSET_ROOT / fallback / f"{stem}{suffix}").is_file()
        for suffix in (".avif", ".webp")
    ):
        return fallback
    return ""


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
    if not selected:
        return ""
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
    if not avif or not webp:
        return ""
    return (
        f'<figure class="shot-card {platform}"><picture>'
        f'<source srcset="{avif}" type="image/avif">'
        f'<source srcset="{webp}" type="image/webp">'
        f'<img loading="lazy" alt="" src="{webp}" width="{width}" height="{height}" decoding="async">'
        '</picture></figure>'
    )


def home_preview(prefix: str, locale: str) -> str:
    """Return the authentic, locale-aware hero with the three pick cartridges."""
    filename = "mac-home.jpeg"
    avif = asset_url(prefix, locale, filename, ".avif")
    webp = asset_url(prefix, locale, filename, ".webp")
    if not avif or not webp:
        raise RuntimeError(f"Missing localized Mac home screenshot for {locale}")
    return (
        '<figure class="device-frame wide-shot v20-hero">'
        '<picture>'
        f'<source srcset="{avif}" type="image/avif">'
        f'<source srcset="{webp}" type="image/webp">'
        f'<img fetchpriority="high" alt="" src="{webp}" width="1440" height="900" decoding="async">'
        '</picture>'
        '</figure>'
    )


def mac_card_preview(prefix: str, locale: str, filename: str) -> str:
    avif = asset_url(prefix, locale, filename, ".avif")
    webp = asset_url(prefix, locale, filename, ".webp")
    if not avif or not webp:
        raise RuntimeError(f"Missing localized Mac card screenshot for {locale}: {filename}")
    return (
        '<div class="mac-card-preview"><figure><picture>'
        f'<source type="image/avif" srcset="{avif}">'
        f'<img alt="" src="{webp}" width="1440" height="900" decoding="async" loading="lazy">'
        '</picture></figure></div>'
    )


def home_gallery(prefix: str, locale: str) -> str:
    """Return two valid, complementary homepage previews without captions."""
    items = (
        ("v20-home-phone", "iphone", "iphone-todays-pick.png"),
        ("v20-home-mac", "mac", "mac-collection.jpeg"),
    )
    figures = []
    for class_name, platform, filename in items:
        avif = asset_url(prefix, locale, filename, ".avif")
        webp = asset_url(prefix, locale, filename, ".webp")
        if not avif or not webp:
            raise RuntimeError(f"Missing localized homepage preview for {locale}: {filename}")
        width, height = DIMENSIONS[platform]
        figures.append(
            f'<figure class="current-screen {class_name}"><picture>'
            f'<source srcset="{avif}" type="image/avif">'
            f'<source srcset="{webp}" type="image/webp">'
            f'<img loading="lazy" alt="" src="{webp}" width="{width}" height="{height}" decoding="async">'
            '</picture></figure>'
        )
    return '<div class="screen-grid current-screens v20-home-screens">' + ''.join(figures) + '</div>'


def gallery(prefix: str, locale: str) -> str:
    groups = []
    platform_names = {"mac": "Mac", "iphone": "iPhone", "ipad": "iPad", "watch": "Apple Watch"}
    for platform in ("mac", "iphone", "ipad", "watch"):
        cards = "".join(picture(prefix, locale, platform, name) for name in GALLERY_ASSETS[platform])
        if not cards:
            continue
        platform_label = "macOS 2.2" if platform == "mac" else "iOS 2.1.1"
        groups.append(
            f'<div class="platform-shot-group"><h3>{platform_names[platform]} · {platform_label}</h3>'
            f'<div class="shot-grid v20-shot-grid {platform}-grid">{cards}</div></div>'
        )
    return (
        f'<section class="media-section v20-screenshot-gallery" data-release-gallery="{current_public_version()}">'
        '<div class="section-head"><h2>iOS 2.1.1 · macOS 2.2</h2></div>'
        + "".join(groups)
        + '</section>'
    )


def current_public_version() -> str:
    state = json.loads((ROOT / "data" / "release-state.json").read_text(encoding="utf-8"))
    return state["current_release"]["version"]


def localize_existing_v20(text: str, locale: str) -> str:
    """Localize existing v20 figures and remove unsupported foreign fallbacks."""
    text = re.sub(
        r'((?:mac-(?:home|collection|todays-pick|mood-pick|random-pick|data-quality|three-ways|search-results)|'
        r'iphone-(?:collection|todays-pick|mood-pick|random-pick)|'
        r'ipad-(?:collection|todays-pick|mood-pick|random-pick)|watch-random-pick))\.*(avif|webp)',
        r'\1.\2',
        text,
    )
    if locale.startswith("en-") or locale == "en-us":
        return text

    def localize_url(match: re.Match[str]) -> str:
        prefix, source_locale, stem, suffix = match.groups()
        if source_locale == locale:
            return match.group(0)
        selected = available_locale(locale, f"{stem}.{suffix}")
        if not selected:
            return match.group(0)
        return f"{prefix}assets/screenshots/v20/{selected}/{stem}.{suffix}"

    def localize_figure(match: re.Match[str]) -> str:
        figure = match.group(0)
        references = re.findall(
            r'assets/screenshots/v20/([^/]+)/([^/"\']+)\.(avif|webp)',
            figure,
        )
        for source_locale, stem, suffix in references:
            if source_locale != locale and not available_locale(locale, f"{stem}.{suffix}"):
                return ""
        return re.sub(
            r'((?:\.\./)*)assets/screenshots/v20/([^/]+)/([^/"\']+)\.(avif|webp)',
            localize_url,
            figure,
        )

    text = re.sub(r'<figure\b[^>]*>.*?</figure>', localize_figure, text, flags=re.DOTALL)
    text = re.sub(
        r'((?:\.\./)*|https://recordpicker\.app/)assets/screenshots/v20/([^/]+)/([^/"\']+)\.(avif|webp)',
        localize_url,
        text,
    )
    text = re.sub(r'<div class="mac-screenshot-grid">\s*</div>', '', text)
    text = re.sub(r'<section class="mac-showcase"[^>]*>\s*</section>', '', text)
    return text


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
    text = localize_existing_v20(text, locale)

    version_label = "Versions"

    def unify_version_navigation(match: re.Match[str]) -> str:
        nonlocal version_label
        nav = match.group(0)
        readme_link = re.search(r'<a href="([^"]*readme/)">', nav)
        version_link = re.search(
            r'<a href="[^"]*#(?:versions|version-history)">(.*?)</a>',
            nav,
            flags=re.DOTALL,
        )
        if not readme_link or not version_link:
            return nav
        version_label = re.sub(r'<[^>]+>', '', version_link.group(1)).strip() or version_label
        return re.sub(
            r'(<a href=")[^"]*#(?:versions|version-history)(">)',
            rf'\g<1>{readme_link.group(1)}#version-history\g<2>',
            nav,
            count=1,
        )

    text = re.sub(
        r'<nav class="nav-links".*?</nav>',
        unify_version_navigation,
        text,
        count=1,
        flags=re.DOTALL,
    )

    if relative.name == "index.html" and relative.parent.name == "readme":
        # The document hero already names the page. Remove the first content
        # heading only when it repeats that localized title verbatim.
        hero_title = re.search(r'<section class="doc-hero".*?<h1[^>]*>(.*?)</h1>', text, re.DOTALL)
        content = re.search(r'<section class="doc-content">(.*?)</section>', text, re.DOTALL)
        if hero_title and content:
            first_heading = re.search(r'<h2[^>]*>(.*?)</h2>', content.group(1), re.DOTALL)
            if first_heading:
                plain = lambda value: re.sub(r'<[^>]+>', '', value).strip().casefold()
                if plain(hero_title.group(1)) == plain(first_heading.group(1)):
                    cleaned = (
                        content.group(1)[: first_heading.start()]
                        + content.group(1)[first_heading.end() :]
                    )
                    text = text[: content.start(1)] + cleaned + text[content.end(1) :]

        # One public concept, one destination: the navigation label and the
        # complete release history use the same localized name.
        text = re.sub(
            r'<h2[^>]*>[^<]*</h2>(?=<div class="(?:timeline compact current-release-timeline|release-list)">)',
            f'<h2 id="version-history">{version_label}</h2>',
            text,
            count=1,
            flags=re.DOTALL,
        )
        text = re.sub(
            r'(<details class="release-history-archive"><summary>).*?(</summary>)',
            r'\g<1>Record Picker ≤ 1.8\g<2>',
            text,
            count=1,
            flags=re.DOTALL,
        )
        if locale in COMPACT_README_INTROS and 'class="context-pair feature-intro"' not in text:
            heading, bullets = COMPACT_README_INTROS[locale]
            items = "".join(f"<li>{item}</li>" for item in bullets)
            def compact_visual(filename: str) -> str:
                avif = asset_url(prefix, locale, filename, ".avif")
                webp = asset_url(prefix, locale, filename, ".webp")
                return (
                    '<figure class="context-visual wide"><picture>'
                    f'<source srcset="{avif}" type="image/avif">'
                    f'<source srcset="{webp}" type="image/webp">'
                    f'<img loading="lazy" alt="" src="{webp}" width="1440" height="900" decoding="async">'
                    '</picture></figure>'
                )
            intro = (
                f"<h2>{heading}</h2><ul>{items}</ul>"
                '<div class="context-pair feature-intro">'
                f'{compact_visual("mac-home.jpeg")}'
                f'{compact_visual("mac-todays-pick.jpeg")}'
                "</div>"
            )
            text = text.replace(
                f'<h2 id="version-history">{version_label}</h2>',
                intro + f'<h2 id="version-history">{version_label}</h2>',
                1,
            )

    # The middle Mac feature card demonstrates full-text search with three
    # live matches outlined in red. Keep it tied to the real localized app UI.
    def refresh_mac_feature_row(match: re.Match[str]) -> str:
        row = match.group(0)
        cards = re.findall(r'<article class="card">.*?</article>', row, flags=re.DOTALL)
        if len(cards) != 3:
            return row
        cards[1] = re.sub(
            r'<div class="mac-card-preview">.*?</div>',
            mac_card_preview(prefix, locale, "mac-search-results.jpeg"),
            cards[1],
            count=1,
            flags=re.DOTALL,
        )
        cards[2] = re.sub(
            r'<div class="mac-card-preview">.*?</div>',
            mac_card_preview(prefix, locale, "mac-mood-pick.jpeg"),
            cards[2],
            count=1,
            flags=re.DOTALL,
        )
        return '<section class="mac-feature-row">' + ''.join(cards) + '</section>'

    text = re.sub(
        r'<section class="mac-feature-row">.*?</section>',
        refresh_mac_feature_row,
        text,
        count=1,
        flags=re.DOTALL,
    )

    is_home = relative == Path("index.html") or (
        len(relative.parts) == 2
        and relative.parts[0] in SITE_LOCALES
        and relative.name == "index.html"
    )
    if is_home:
        # The three-choice screen communicates the product in one glance, so it
        # belongs in the first viewport. Do not repeat it in the release notes.
        text = re.sub(
            r'<div class="hero-showcase v20-hero-showcase">.*?</div>',
            '<div class="hero-showcase v20-hero-showcase">'
            + home_preview(prefix, locale)
            + '</div>',
            text,
            count=1,
            flags=re.DOTALL,
        )
        text = re.sub(
            r'<figure class="v20-home-preview">.*?</figure>',
            "",
            text,
            count=1,
            flags=re.DOTALL,
        )
        text = re.sub(
            r'<div class="screen-grid current-screens v20-home-screens">.*?</div>',
            home_gallery(prefix, locale),
            text,
            count=1,
            flags=re.DOTALL,
        )
        # This block is a visual gateway to the complete screenshot gallery.
        # Keep its promise literal and language-safe: the localized "Screenshots"
        # kicker, current iOS/macOS versions, then the representative app views.
        def normalize_home_gallery_heading(match: re.Match[str]) -> str:
            section = match.group(0)
            section = re.sub(r'<h2>.*?</h2>', '<h2>iOS 2.1.1 · macOS 2.2</h2>', section, count=1, flags=re.DOTALL)
            section = re.sub(r'<p class="lead">.*?</p>', '', section, count=1, flags=re.DOTALL)
            return section

        text = re.sub(
            r'<section class="section gallery".*?</section>',
            normalize_home_gallery_heading,
            text,
            count=1,
            flags=re.DOTALL,
        )

    if relative.name == "index.html" and relative.parent.name == "screenshots":
        # A screenshots page should open directly on the gallery. The full
        # 2.0 editorial summary is already present on the homepage.
        text = re.sub(
            r'<section class="media-section[^\"]*v20-preview[^\"]*"[^>]*data-release-version="2\.0"[^>]*>.*?</section>',
            "",
            text,
            count=1,
            flags=re.DOTALL,
        )
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

    if relative.name == "index.html" and relative.parent.name == "readme":
        # Artwork search combines three real providers. Keep the localized
        # sentence around the source list, but never present Cover Art Archive
        # as the only automatic source.
        feature_cards = list(
            re.finditer(r'<article class="card feature-card">.*?</article>', text, flags=re.DOTALL)
        )
        if len(feature_cards) >= 2:
            artwork_card = feature_cards[1]
            updated_card = re.sub(
                r'Cover Art Archive(?! · iTunes Search · Deezer)',
                'Cover Art Archive · iTunes Search · Deezer',
                artwork_card.group(0),
                count=1,
            )
            text = text[:artwork_card.start()] + updated_card + text[artwork_card.end():]

    url_pattern = re.compile(
        r'(?P<prefix>(?:\.\./)*)(?P<path>assets/screenshots/(?!v20/)[^"\'?# >]+)'
        r'(?P<query>\?[^"\' >]+)?'
    )
    text = url_pattern.sub(lambda match: replace_screenshot_url(match, locale), text)
    text = re.sub(r'<img\b[^>]*>', update_image_tag, text)
    # Screenshot titles already explain their images. Keep only captions that
    # are explicitly hidden for accessibility; visible legends are redundant.
    text = re.sub(
        r'<figcaption(?![^>]*class="visually-hidden")[^>]*>.*?</figcaption>',
        "",
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
        lambda match: match.group(1).replace("Record Picker 1.8", "iOS 2.1.1 · macOS 2.2"),
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
    return parts[0] if parts[0] in SITE_LOCALES else "en-us"


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
            if not selected:
                continue
            asset = f"https://recordpicker.app/assets/screenshots/v20/{selected}/{Path(filename).stem}.webp"
            entries.append(
                "\n    <image:image>\n"
                f"      <image:loc>{asset}</image:loc>\n"
                "      <image:title>Record Picker · iOS 2.1.1 · macOS 2.2 app preview</image:title>\n"
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
