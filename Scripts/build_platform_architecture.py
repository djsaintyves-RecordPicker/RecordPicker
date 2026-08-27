#!/usr/bin/env python3
"""Build localized platform pages and a single accessible platform navigation."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re

from announce_android_pc_development import BETA_COPY, BETA_DETAIL_12, BETA_SCOPE_COPY, COPY
from announce_release_2_1 import COMING_SOON
from announce_release_2_3_1 import COPY as RELEASE_232_COPY, LOCALES as RELEASE_LOCALES


ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-08-27"
STYLE_VERSION = "20260825-android-beta"

PLATFORM_LABELS = {
    "": "Platforms", "ar": "المنصات", "ca": "Plataformes", "da": "Platforme",
    "de": "Plattformen", "el": "Πλατφόρμες", "en-au": "Platforms",
    "en-ca": "Platforms", "en-gb": "Platforms", "en-us": "Platforms",
    "es-es": "Plataformas", "es-mx": "Plataformas", "fi": "Alustat",
    "fr": "Plateformes", "fr-ca": "Plateformes", "he": "פלטפורמות",
    "hi": "प्लेटफ़ॉर्म", "id": "Platform", "it": "Piattaforme",
    "ja": "プラットフォーム", "ko": "플랫폼", "nb": "Plattformer",
    "nl": "Platformen", "pl": "Platformy", "pt-br": "Plataformas",
    "pt-pt": "Plataformas", "ru": "Платформы", "sv": "Plattformar",
    "th": "แพลตฟอร์ม", "tr": "Platformlar", "vi": "Nền tảng",
    "zh-hans": "平台", "zh-hant": "平台",
}

REGION_NAMES = {
    "en-au": "Australia", "en-ca": "Canada",
    "en-gb": "United Kingdom", "en-us": "United States",
}

SEO_LOCALE_LABELS = {
    "": "", "ar": "العربية", "ca": "Català", "da": "Dansk",
    "de": "Deutsch", "el": "Ελληνικά", "en-au": "Australia",
    "en-ca": "Canada", "en-gb": "United Kingdom", "en-us": "United States",
    "es-es": "España", "es-mx": "México", "fi": "Suomi", "fr": "France",
    "fr-ca": "Canada français", "he": "עברית", "hi": "हिन्दी",
    "id": "Indonesia", "it": "Italiano", "ja": "日本語", "ko": "한국어",
    "nb": "Norsk", "nl": "Nederlands", "pl": "Polski", "pt-br": "Brasil",
    "pt-pt": "Portugal", "ru": "Русский", "sv": "Svenska", "th": "ไทย",
    "tr": "Türkçe", "vi": "Tiếng Việt", "zh-hans": "简体中文",
    "zh-hant": "繁體中文",
}


def locale_file(locale: str, route: str = "") -> Path:
    base = ROOT / locale if locale else ROOT
    return base / route / "index.html" if route else base / "index.html"


def match(pattern: str, text: str, label: str) -> str:
    found = re.search(pattern, text, flags=re.DOTALL)
    if not found:
        raise RuntimeError(f"Missing {label}")
    return found.group(0)


def inner(pattern: str, text: str, label: str) -> str:
    found = re.search(pattern, text, flags=re.DOTALL)
    if not found:
        raise RuntimeError(f"Missing {label}")
    return found.group(1)


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", value)).strip()


def set_meta(text: str, route: str, title: str, description: str) -> str:
    canonical = f"https://recordpicker.app/{route}/"
    text = re.sub(r"<title>.*?</title>", f"<title>{escape(title)}</title>", text, count=1)
    replacements = {
        "description": description,
        "twitter:title": title,
        "twitter:description": description,
    }
    for name, value in replacements.items():
        text = re.sub(
            rf'(<meta name="{re.escape(name)}" content=")[^"]*(")',
            rf'\g<1>{escape(value, quote=True)}\2', text, count=1,
        )
    for prop, value in {
        "og:title": title, "og:description": description, "og:url": canonical,
    }.items():
        text = re.sub(
            rf'(<meta property="{re.escape(prop)}" content=")[^"]*(")',
            rf'\g<1>{escape(value, quote=True)}\2', text, count=1,
        )
    text = re.sub(
        r'(<link rel="canonical" href=")[^"]*(")',
        rf'\g<1>{canonical}\2', text, count=1,
    )
    return text


def store_button(home: str) -> str:
    link = match(r'<a class="store-link".*?</a>', home, "App Store link")
    return link.replace('class="store-link"', 'class="button primary"')


def visual_prefix(mac_page: str) -> str:
    found = re.search(r'(\.\./)+(?:assets/screenshots/v20/)', mac_page)
    if not found:
        raise RuntimeError("Missing localized asset prefix")
    return found.group(0).split("assets/")[0]


def iphone_visual(prefix: str, locale: str) -> str:
    asset_locale = locale or "en-us"
    return (
        '<figure class="context-visual phone platform-phone-visual">'
        '<picture>'
        f'<source srcset="{prefix}assets/screenshots/v20/{asset_locale}/iphone-todays-pick.avif" type="image/avif">'
        f'<source srcset="{prefix}assets/screenshots/v20/{asset_locale}/iphone-todays-pick.webp" type="image/webp">'
        f'<img alt="Record Picker Today’s Pick on iPhone" src="{prefix}assets/screenshots/v20/{asset_locale}/iphone-todays-pick.webp" width="1320" height="2868" decoding="async">'
        '</picture></figure>'
    )


def watch_visual(prefix: str, locale: str) -> str:
    asset_locale = "fr" if locale in {"fr", "fr-ca"} else "en-us"
    if locale not in {"", "en-au", "en-ca", "en-gb", "en-us", "fr", "fr-ca"}:
        return '<div class="platform-symbol" aria-hidden="true">⌚</div>'
    return (
        '<figure class="context-visual watch platform-watch-visual"><picture>'
        f'<source srcset="{prefix}assets/screenshots/v20/{asset_locale}/watch-random-pick.avif" type="image/avif">'
        f'<source srcset="{prefix}assets/screenshots/v20/{asset_locale}/watch-random-pick.webp" type="image/webp">'
        f'<img alt="Record Picker Random Pick on Apple Watch" src="{prefix}assets/screenshots/v20/{asset_locale}/watch-random-pick.webp" width="748" height="892" decoding="async">'
        '</picture></figure>'
    )


def build_main(locale: str, route: str, home: str, mac_page: str) -> tuple[str, str, str]:
    deck = inner(r'<p class="deck">(.*?)</p>', home, "home description")
    available = plain(inner(r'<section class="section v23-preview.*?<p class="kicker">(.*?)</p>', home, "availability"))
    contact = match(r'<section class="contact-band">.*?</section>', home, "contact section")
    prefix = visual_prefix(mac_page)
    button = store_button(home)
    if route == "ios-app":
        title = "Record Picker — iPhone · iPad"
        description = plain(deck)
        app_match = re.search(
            r'<section class="section split"(?: id="app")?>.*?</section>',
            home,
            flags=re.DOTALL,
        )
        if not app_match:
            raise RuntimeError(f"Missing app section for {locale or 'en-us'}")
        app_section = app_match.group(0)
        main = (
            '<main id="main-content"><section class="hero platform-product-hero">'
            f'<div class="hero-copy"><p class="kicker">{escape(available)}</p><h1>Record Picker</h1>'
            f'<p class="tagline">iPhone · iPad</p><p class="deck">{deck}</p>'
            f'<div class="cta-row">{button}</div></div>{iphone_visual(prefix, locale)}</section>'
            f'{app_section}{contact}</main>'
        )
    elif route == "watch-app":
        title = "Record Picker — Apple Watch"
        release = match(r'<section class="section v23-preview.*?</section>', home, "watch release section")
        description = (
            plain(inner(r'<p class="lead">(.*?)</p>', release, "watch description"))
            + " " + plain(deck)
        )
        main = (
            '<main id="main-content"><section class="hero platform-product-hero">'
            f'<div class="hero-copy"><p class="kicker">{escape(available)}</p><h1>Record Picker</h1>'
            f'<p class="tagline">Apple Watch</p><p class="deck">{escape(description)}</p>'
            f'<div class="cta-row">{button}</div></div>{watch_visual(prefix, locale)}</section>'
            f'{release}{contact}</main>'
        )
    elif route == "android-app":
        kicker, _, detail = COPY[locale]
        beta_title, _, beta_button = BETA_COPY[locale]
        beta_detail = BETA_DETAIL_12[locale]
        scope = BETA_SCOPE_COPY.get(locale, "Worldwide applications welcome · Beta available in English and French")
        title = "Record Picker — Android"
        description = plain(beta_detail)
        subject = "Record%20Picker%20Android%20beta%20volunteer"
        body = "Country%20%2F%20region%3A%0AAndroid%20device%20model%3A%0APreferred%20beta%20language%3A%20English%20%2F%20French%3A%0A"
        visual = "android-beta-fr.webp" if locale in {"fr", "fr-ca"} else "android-beta-en.webp"
        main = (
            '<main id="main-content"><section class="hero platform-product-hero platform-development-hero">'
            f'<div class="hero-copy"><p class="kicker">{escape(kicker)}</p><h1>Record Picker</h1>'
            f'<p class="tagline">Android</p><p class="deck">{escape(detail)}</p></div>'
            '<div class="platform-beta-callout platform-beta-page beta-campaign-page">'
            f'<p class="beta-scope">🌍 {escape(scope)}</p>'
            f'<h2>{escape(beta_title)}</h2><p>{escape(beta_detail)}</p>'
            '<div class="cta-row compact">'
            f'<a class="button primary" href="mailto:support@recordpicker.app?subject={subject}&amp;body={body}">{escape(beta_button)}</a>'
            '</div></div>'
            f'<figure class="beta-poster"><img src="/assets/beta/{visual}" alt="{escape(beta_title)}" width="1080" height="1920" decoding="async"></figure>'
            '</section>'
            f'{contact}</main>'
        )
    else:
        note_locale = RELEASE_LOCALES[locale]
        release_copy = RELEASE_232_COPY[note_locale]
        coming_soon = COMING_SOON[note_locale]
        title = "Record Picker — Windows"
        description = release_copy.points[2]
        points = "".join(f"<li>{escape(point)}</li>" for point in release_copy.points)
        main = (
            '<main id="main-content"><section class="hero platform-product-hero platform-development-hero">'
            f'<div class="hero-copy"><p class="kicker">{escape(coming_soon)}</p><h1>Record Picker</h1>'
            f'<p class="tagline">Windows</p><p class="deck">{escape(description)}</p></div>'
            '<div class="platform-symbol windows-symbol" aria-hidden="true">⊞</div>'
            '</section><section class="section platform-expansion windows-preview">'
            f'<div class="section-head"><p class="kicker">{escape(coming_soon)}</p>'
            '<h2>Record Picker · Windows</h2>'
            f'<p class="lead">{escape(release_copy.headline)}</p></div>'
            f'<div class="v20-preview-panel"><ul>{points}</ul></div></section>'
            f'{contact}</main>'
        )
    if locale in REGION_NAMES:
        region = REGION_NAMES[locale]
        title = f"{title} — {region}"
        description = f"{description} Available in {region}."
    elif locale:
        title = f"{title} — {SEO_LOCALE_LABELS[locale]}"
    return main, title, description


def build_page(locale: str, route: str) -> Path:
    home = locale_file(locale).read_text(encoding="utf-8")
    mac_path = locale_file(locale, "mac-app")
    template = mac_path.read_text(encoding="utf-8")
    main, title, description = build_main(locale, route, home, template)
    text = re.sub(
        r'https://recordpicker\.app/((?:[a-z]{2}(?:-[a-z]{2,4})?/)?)(?:mac-app)/',
        rf'https://recordpicker.app/\1{route}/',
        template,
    )
    text = re.sub(
        r'(href="/(?:[a-z]{2}(?:-[a-z]{2,4})?/)?)(?:mac-app)/',
        rf'\g<1>{route}/',
        text,
    )
    route_path = route if not locale else f"{locale}/{route}"
    text = set_meta(text, route_path, title, description)
    text = re.sub(r'<main id="main-content"[^>]*>.*?</main>', main, text, count=1, flags=re.DOTALL)
    if route == "windows-app":
        language = inner(r'<html\s+lang="([^"]+)"', text, "page language")
        schema = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": title,
                "description": description,
                "url": f"https://recordpicker.app/{route_path}/",
                "inLanguage": language,
                "isPartOf": {
                    "@type": "WebSite",
                    "name": "Record Picker",
                    "url": "https://recordpicker.app/",
                },
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        text = re.sub(
            r'<script type="application/ld\+json">\{"@context":"https://schema\.org","@type":"SoftwareApplication".*?</script>',
            f'<script type="application/ld+json">{schema}</script>',
            text,
            count=1,
            flags=re.DOTALL,
        )
        for attribute in ('property="og:image:alt"', 'name="twitter:image:alt"'):
            text = re.sub(
                rf'(<meta {attribute} content=")[^"]*(")',
                rf'\g<1>{escape(title, quote=True)}\2',
                text,
                count=1,
            )
    else:
        text = re.sub(r'"operatingSystem":"[^"]+"', f'"operatingSystem":"{escape({"ios-app": "iOS 26 / iPadOS 26", "watch-app": "watchOS 26", "android-app": "Android"}[route])}"', text)
        text = re.sub(r'("softwareVersion":")[^"]+', r'\g<1>2.3', text)
        text = re.sub(r'("dateModified":")[^"]+', r'\g<1>2026-08-22', text)
    text = re.sub(
        r'<span id="site-footer-version">.*?</span>',
        '<span id="site-footer-version">Record Picker · 2.3</span>',
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'("position":2,"name":")[^"]+',
        rf'\g<1>{escape(title, quote=True)}',
        text,
        count=1,
    )
    path = locale_file(locale, route)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def platform_menu(locale: str, prefix: str) -> str:
    label = escape(PLATFORM_LABELS[locale])
    android_status = escape(COPY[locale][0])
    windows_status = escape(COMING_SOON[RELEASE_LOCALES[locale]])
    return (
        '<details class="platform-nav"><summary>' + label + '</summary>'
        '<div class="platform-nav-panel">'
        f'<a href="{prefix}ios-app/">iPhone · iPad</a>'
        f'<a href="{prefix}watch-app/">Apple Watch</a>'
        f'<a href="{prefix}mac-app/">Mac</a>'
        f'<a href="{prefix}android-app/">Android <small>{android_status}</small></a>'
        f'<a href="{prefix}windows-app/">Windows <small>{windows_status}</small></a>'
        '</div></details>'
    )


def update_navigation(path: Path, locale: str) -> bool:
    text = path.read_text(encoding="utf-8")
    header_match = re.search(r'<header class="site-header">.*?</header>', text, flags=re.DOTALL)
    if not header_match:
        return False
    header = header_match.group(0)
    anchor = re.search(r'<a href="([^"]*?)android-app/">.*?</a>', header, flags=re.DOTALL)
    if not anchor:
        raise RuntimeError(f"Missing Android navigation in {path}")
    prefix = anchor.group(1)
    if 'class="platform-nav"' in header:
        updated_header = re.sub(
            r'<details class="platform-nav">.*?</details>',
            platform_menu(locale, prefix),
            header,
            count=1,
            flags=re.DOTALL,
        )
    else:
        updated_header = header[:anchor.start()] + platform_menu(locale, prefix) + header[anchor.end():]
    updated = text.replace(header, updated_header, 1)
    updated = re.sub(r'quality\.css\?v=[^"\']+', f'quality.css?v={STYLE_VERSION}', updated)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def update_sitemap(path: Path, routes: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for route in routes:
        url = f"https://recordpicker.app/{route}/"
        if f"<loc>{url}</loc>" not in text:
            text = text.replace("</urlset>", f"<url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>\n</urlset>")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    routes = ("ios-app", "watch-app", "android-app", "windows-app")
    pages = [build_page(locale, route) for locale in COPY for route in routes]
    changed = 0
    for path in ROOT.rglob("*.html"):
        relative = path.relative_to(ROOT)
        locale = relative.parts[0] if relative.parts[0] in COPY and relative.parts[0] else ""
        changed += update_navigation(path, locale)
    sitemap_routes = [f"{locale}/{route}" if locale else route for locale in COPY for route in routes]
    update_sitemap(ROOT / "sitemap.xml", sitemap_routes)
    update_sitemap(ROOT / "sitemap-media.xml", sitemap_routes)
    print(f"Built {len(pages)} platform pages and updated navigation on {changed} pages.")


if __name__ == "__main__":
    main()
