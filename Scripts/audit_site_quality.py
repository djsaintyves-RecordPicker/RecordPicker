#!/usr/bin/env python3
"""Fail when the generated public site violates release or quality invariants."""

from __future__ import annotations

from html import unescape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from refine_homepage_descriptions import audit as audit_homepage_descriptions
from refine_remaining_localized_copy import audit as audit_remaining_localized_copy


ROOT = Path(__file__).resolve().parents[1]
RELEASE_STATE = json.loads(
    (ROOT / "data" / "release-state.json").read_text(encoding="utf-8")
)
PUBLICATION_PHASE = RELEASE_STATE["publication_phase"]
CURRENT_VERSION = RELEASE_STATE["current_release"]["version"]
NEXT_RELEASE = RELEASE_STATE.get("next_release")
NEXT_VERSION = NEXT_RELEASE["version"] if NEXT_RELEASE else None
NEXT_RELEASE_DATE = "2026-08-12"
HISTORICAL_VERSIONS = set(RELEASE_STATE["historical_releases"])
SOCIAL_IMAGE_URL = (
    "https://recordpicker.app/" + RELEASE_STATE["publication_assets"]["social"]
)
OFFICIAL_SOCIALS = {
    "https://www.instagram.com/recordpicker/",
    "https://www.youtube.com/@recordpicker",
    "https://www.facebook.com/profile.php?id=61591096987226",
    "https://www.threads.net/@recordpicker",
}
LOCALES = {
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "es-mx", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "th", "tr", "vi", "zh-hans", "zh-hant",
}
RELEASE_CARD = re.compile(
    r'<article class="release-card[^>]*data-release-version="([^"]+)".*?</article>',
    flags=re.DOTALL,
)
STATUS = re.compile(
    r'<div><h3>.*?</h3><p(?: class="[^"]*")?>.*?</p>',
    flags=re.DOTALL,
)


def local_target(page: Path, value: str) -> Path | None:
    value = unescape(value)
    if not value or value.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    target = ROOT / parsed.path.lstrip("/") if parsed.path.startswith("/") else page.parent / parsed.path
    if parsed.path.endswith("/"):
        target = target / "index.html"
    elif target.is_dir():
        target = target / "index.html"
    return target.resolve()


def page_language(relative: Path, text: str) -> str:
    if relative.parts and relative.parts[0] in LOCALES:
        return relative.parts[0]
    match = re.search(r'<html\s+lang="([^"]+)"', text, flags=re.IGNORECASE)
    if not match:
        return ""
    language = match.group(1).casefold()
    if language == "fr-ca":
        return "fr-ca"
    if language.startswith("fr"):
        return "fr"
    return language


def main() -> None:
    audit_homepage_descriptions()
    audit_remaining_localized_copy()
    pages = sorted(ROOT.rglob("*.html"))
    errors: list[str] = []
    content_pages = 0
    release_pages = 0
    homes = 0
    next_release_pages = 0
    current_gallery_pages = 0
    current_metadata_pages = 0
    current_social_pages = 0
    optimized_picture_pages = 0
    archived_gallery_pages = 0
    if PUBLICATION_PHASE not in {"partial", "full"}:
        errors.append(f"unknown publication phase {PUBLICATION_PHASE}")
    platform_states = RELEASE_STATE["current_release"]["platforms"]
    required_platforms = set(
        RELEASE_STATE["current_release"]["required_platforms_for_full_release"]
    )
    if set(platform_states) != required_platforms:
        errors.append("release-state platform list does not match the publication gate")
    if PUBLICATION_PHASE == "full" and set(platform_states.values()) != {"available"}:
        errors.append("full publication still has a platform that is not available")
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for value in re.findall(r'(?:href|src|srcset)="([^"]+)"', text):
            target = local_target(page, value)
            if target and not target.exists():
                errors.append(f"{page.relative_to(ROOT)}: missing {target.relative_to(ROOT)}")
        for payload in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', text, flags=re.DOTALL):
            try:
                schema = json.loads(unescape(payload))
                if schema.get("@type") == "SoftwareApplication":
                    if NEXT_VERSION and f'data-release-version="{NEXT_VERSION}"' in text:
                        if schema.get("dateModified") != NEXT_RELEASE_DATE:
                            errors.append(
                                f"{page.relative_to(ROOT)}: stale structured-data modification date"
                            )
                    if set(schema.get("sameAs", [])) != OFFICIAL_SOCIALS:
                        errors.append(
                            f"{page.relative_to(ROOT)}: official sameAs profiles incomplete"
                        )
                    publisher = schema.get("publisher", {})
                    if (
                        publisher.get("name") != "Record Picker"
                        or publisher.get("url") != "https://recordpicker.app/"
                        or publisher.get("logo", {}).get("url")
                        != "https://recordpicker.app/assets/brand/icon-512.png"
                    ):
                        errors.append(
                            f"{page.relative_to(ROOT)}: official publisher identity incomplete"
                        )
                    languages = set(schema.get("inLanguage", []))
                    if not {"es-MX", "th", "vi"}.issubset(languages):
                        errors.append(
                            f"{page.relative_to(ROOT)}: structured locale coverage incomplete"
                        )
                    regions = set(schema.get("areaServed", []))
                    if not {"MX", "TH", "VN"}.issubset(regions):
                        errors.append(
                            f"{page.relative_to(ROOT)}: structured market coverage incomplete"
                        )
            except json.JSONDecodeError as error:
                errors.append(f"{page.relative_to(ROOT)}: invalid JSON-LD: {error}")
        if "<main" not in text:
            continue
        content_pages += 1
        relative = page.relative_to(ROOT)
        if relative in {
            Path("mac-app/index.html"),
            Path("fr/mac-app/index.html"),
            Path("fr-ca/mac-app/index.html"),
        } and "façon calme" in text.casefold():
            errors.append(f"{relative}: vague French Mac tagline remains")
        if re.search(r"Record Picker[^<\n]{0,120}\b(?:25\+?|29)\b", text):
            errors.append(f"{relative}: obsolete localization count remains")
        if relative.parts[0] in {"en-au", "en-ca", "en-gb", "en-us"}:
            if "Today Pick" in text:
                errors.append(f"{relative}: stale Today Pick product name")
        if re.search(r'assets/screenshots/(?:v1[0-9]/|iphone/|ipad/|mac/)', text):
            errors.append(f"{relative}: obsolete screenshot remains")
        for forbidden_visual in (
            "assets/screenshots/iphone/import.jpeg",
            "assets/screenshots/ipad/manual-edit.png",
        ):
            if forbidden_visual in text:
                errors.append(f"{relative}: tutorial visual remains")
        if re.search(
            r'assets/screenshots/(?!v19/)[^"\'?#]+\.(?:png|jpe?g)(?:\?[^"\']*)?["\']',
            text,
            flags=re.IGNORECASE,
        ):
            errors.append(f"{relative}: unoptimized legacy screenshot reference")
        if relative.parts and relative.parts[0] in LOCALES:
            expected_page_locale = relative.parts[0]
            if f'data-page-lang="{expected_page_locale}"' not in text:
                errors.append(
                    f"{relative}: data-page-lang does not match its locale directory"
                )
            if not expected_page_locale.startswith("en-") and re.search(
                r'assets/screenshots/v20/en-us/', text, flags=re.IGNORECASE
            ):
                errors.append(
                    f"{relative}: English screenshot fallback on a non-English page"
                )
        relative_parts = relative.parts[1:] if relative.parts and relative.parts[0] in LOCALES else relative.parts
        kind = "/".join(relative_parts)
        page_locale = page_language(relative, text)
        is_french_page = page_locale in {"fr", "fr-ca"}
        if is_french_page and 'href="/press/reviews/"' not in text:
            errors.append(f"{relative}: French press-review entry point missing")
        if not is_french_page and 'href="/press/reviews/"' in text:
            errors.append(f"{relative}: French press-review exposed on non-French page")
        if relative == Path("press/reviews/index.html"):
            if (
                '"@type":"NewsArticle"' not in text
                or "https://www.mac4ever.com/audio/197509-" not in text
            ):
                errors.append(f"{relative}: Mac4Ever article metadata missing")
        nav = re.search(r'<nav class="nav-links".*?</nav>', text, flags=re.DOTALL)
        if not nav or not re.search(
            r'href="[^"]*readme/#version-history"',
            nav.group(0),
        ):
            errors.append(f"{relative}: Versions navigation does not open the full history")
        if kind == "readme/index.html":
            if text.count('id="version-history"') != 1:
                errors.append(f"{relative}: unique version history destination missing")
            if '<details class="release-history-archive">' in text and (
                '<summary>Record Picker ≤ 1.8</summary>' not in text
            ):
                errors.append(f"{relative}: previous-version archive label is ambiguous")
            hero_title = re.search(
                r'<section class="doc-hero".*?<h1[^>]*>(.*?)</h1>',
                text,
                flags=re.DOTALL,
            )
            content = re.search(
                r'<section class="doc-content">(.*?)</section>',
                text,
                flags=re.DOTALL,
            )
            if hero_title and content:
                first_heading = re.search(
                    r'<h2[^>]*>(.*?)</h2>',
                    content.group(1),
                    flags=re.DOTALL,
                )
                if first_heading:
                    plain = lambda value: re.sub(r'<[^>]+>', '', value).strip().casefold()
                    if plain(hero_title.group(1)) == plain(first_heading.group(1)):
                        errors.append(
                            f"{relative}: page title duplicated as first Features heading"
                        )
        if kind == "mac-app/index.html":
            if 'class="mac-icon-card"' in text:
                errors.append(f"{relative}: redundant Mac app icon card remains")
            visual_locale = (
                relative.parts[0]
                if relative.parts and relative.parts[0] in LOCALES
                else "fr"
            )
            expected_visual = (
                f"assets/screenshots/v20/{visual_locale}/mac-home.webp"
            )
            if expected_visual not in text:
                errors.append(
                    f"{relative}: localized Mac 2.0 home visual missing"
                )
            if 'class="mac-intro"' in text:
                hero_visual = re.search(
                    r'<figure class="mac-hero-visual">(.*?)</figure>',
                    text,
                    flags=re.DOTALL,
                )
                if not hero_visual or "<figcaption" in hero_visual.group(1):
                    errors.append(
                        f"{relative}: Mac hero visual missing or still captioned"
                    )
            feature_row = re.search(
                r'<section class="mac-feature-row">(.*?)</section>',
                text,
                flags=re.DOTALL,
            )
            if feature_row:
                feature_cards = re.findall(
                    r'<article class="card">.*?</article>',
                    feature_row.group(1),
                    flags=re.DOTALL,
                )
                expected_search = (
                    f"assets/screenshots/v20/{visual_locale}/mac-search-results.webp"
                )
                expected_mood = (
                    f"assets/screenshots/v20/{visual_locale}/mac-mood-pick.webp"
                )
                if len(feature_cards) != 3 or expected_search not in feature_cards[1]:
                    errors.append(
                        f"{relative}: localized Mac search-result illustration missing from middle card"
                    )
                elif "<figcaption" in feature_cards[1]:
                    errors.append(
                        f"{relative}: redundant caption remains on Mac search-result illustration"
                    )
                if len(feature_cards) == 3 and "mac-collection.webp" in feature_cards[1]:
                    errors.append(
                        f"{relative}: collection visual duplicated in Mac search card"
                    )
                if len(feature_cards) != 3 or expected_mood not in feature_cards[2]:
                    errors.append(
                        f"{relative}: localized Mood Pick illustration missing from third card"
                    )
                elif "<figcaption" in feature_cards[2]:
                    errors.append(
                        f"{relative}: redundant caption remains on Mood Pick illustration"
                    )
                if len(feature_cards) == 3:
                    for index, card in enumerate(feature_cards, start=1):
                        if '<div class="mac-card-preview"></div>' in card:
                            errors.append(
                                f"{relative}: empty Mac feature illustration in card {index}"
                            )
        if kind in {"privacy/index.html", "readme/index.html", "support/index.html"}:
            if "support@recordpicker.app" not in text:
                errors.append(f"{relative}: public support contact missing")
        for requirement in (
            'class="skip-link"',
            'id="main-content"',
            'href="/press/"',
            'href="https://www.instagram.com/recordpicker/" rel="me"',
            'href="https://www.youtube.com/@recordpicker" rel="me"',
            'href="https://www.facebook.com/profile.php?id=61591096987226" rel="me"',
            'href="https://www.threads.net/@recordpicker" rel="me"',
        ):
            if requirement not in text:
                errors.append(f"{relative}: missing {requirement}")
        if not any(version in text for version in (
            "site.js?v=20260809-v20-pick-carousel",
            "site.js?v=20260812-growth-funnel",
            "site.js?v=20260812-complete-growth",
            "site.js?v=20260812-final-funnel",
            "site.js?v=20260813-indexnow-social",
        )):
            errors.append(f"{relative}: missing versioned site.js")
        if not any(version in text for version in (
            "quality.css?v=20260811-press-review",
            "quality.css?v=20260812-growth-funnel",
            "quality.css?v=20260812-complete-growth",
            "quality.css?v=20260812-final-funnel",
        )):
            errors.append(f"{relative}: missing versioned quality.css")
        if kind == "readme/index.html":
            intro = re.search(
                r'<div class="context-pair feature-intro">(.*?)</div>',
                text,
                flags=re.DOTALL,
            )
            if not intro or intro.group(1).count('<figure class="context-visual wide">') != 2:
                errors.append(f"{relative}: balanced two-visual feature intro missing")
            if '<figcaption>Record Picker 2.0</figcaption>' in text:
                errors.append(f"{relative}: redundant generic screenshot caption")
            feature_cards = re.findall(
                r'<article class="card feature-card">.*?</article>',
                text,
                flags=re.DOTALL,
            )
            if feature_cards and (
                len(feature_cards) < 2
                or not all(
                    source in feature_cards[1]
                    for source in ("Cover Art Archive", "iTunes Search", "Deezer")
                )
            ):
                errors.append(f"{relative}: artwork providers are incomplete")
        if '<h2>Catalogue, en beauté</h2>' in text:
            errors.append(f"{relative}: Mac feature title is not phrased as an infinitive")
        if kind == "index.html":
            press_review = re.search(
                r'<section class="section press-review-spotlight".*?</section>',
                text,
                flags=re.DOTALL,
            )
            review_locale = (
                relative.parts[0]
                if relative.parts and relative.parts[0] in LOCALES
                else "fr"
            )
            if review_locale in {"fr", "fr-ca"}:
                if (
                    not press_review
                    or "https://www.mac4ever.com/audio/197509-" not in press_review.group(0)
                    or f"assets/screenshots/v20/{review_locale}/mac-mood-pick" not in press_review.group(0)
                ):
                    errors.append(f"{relative}: French Mac4Ever press spotlight incomplete")
            elif press_review:
                errors.append(f"{relative}: French Mac4Ever spotlight on non-French home")
            hero_showcase = re.search(
                r'<div class="hero-showcase v20-hero-showcase">(.*?)</div>',
                text,
                flags=re.DOTALL,
            )
            if (
                not hero_showcase
                or "mac-home.avif" not in hero_showcase.group(1)
                or "mac-home.webp" not in hero_showcase.group(1)
            ):
                errors.append(f"{relative}: localized three-choice screen missing from hero")
            elif "<figcaption" in hero_showcase.group(1):
                errors.append(f"{relative}: redundant homepage hero caption remains")
            if 'class="v20-home-preview"' in text:
                errors.append(f"{relative}: three-choice screen is duplicated below the hero")
            home_gallery = re.search(
                r'<div class="screen-grid current-screens v20-home-screens">(.*?)</div>',
                text,
                flags=re.DOTALL,
            )
            if (
                not home_gallery
                or "iphone-todays-pick.webp" not in home_gallery.group(1)
                or "mac-collection.webp" not in home_gallery.group(1)
            ):
                errors.append(f"{relative}: complete localized homepage gallery missing")
            gallery_section = re.search(
                r'<section class="section gallery".*?</section>',
                text,
                flags=re.DOTALL,
            )
            if not gallery_section or "<h2>Record Picker 2.0</h2>" not in gallery_section.group(0):
                errors.append(f"{relative}: homepage gallery heading does not match its visuals")
            elif '<p class="lead">' in gallery_section.group(0):
                errors.append(f"{relative}: redundant homepage gallery promise remains")
            expected_home_locale = relative.parts[0] if relative.parts and relative.parts[0] in {"fr", "fr-ca"} else None
            if relative == Path("index.html"):
                expected_home_locale = "fr"
            if expected_home_locale and f"assets/screenshots/v20/{expected_home_locale}/mac-home" not in text:
                errors.append(f"{relative}: French Mac home preview missing")
        selected_languages = re.findall(
            r'<a class="language-option"[^>]*aria-selected="true"', text
        )
        global_bilingual_page = relative == Path("press/reviews/index.html")
        if not global_bilingual_page and len(selected_languages) != 1:
            errors.append(
                f"{relative}: expected one selected language, found {len(selected_languages)}"
            )
        if re.search(r'<img[^>]+src="[^"]*(?:tutorial|onboarding|walkthrough)', text, flags=re.IGNORECASE):
            errors.append(f"{relative}: forbidden tutorial image")
        if re.search(r'<(?:img\b[^>]*\bsrc|source\b[^>]*\bsrcset)="(?:"|\?)', text):
            errors.append(f"{relative}: empty or query-only image source")
        if re.search(r'<figcaption(?![^>]*class="visually-hidden")', text):
            errors.append(f"{relative}: visible figure caption remains")
        for image_tag in re.findall(r'<img\b[^>]*>', text):
            for attribute in ("alt", "width", "height"):
                if not re.search(rf'\b{attribute}="[^"]*"', image_tag):
                    errors.append(f"{relative}: image missing {attribute}")
                    break
        functional_images = [
            re.sub(r'\.(?:avif|webp|png|jpe?g)(?:\?[^"\']*)?$', '', source, flags=re.IGNORECASE)
            for source in re.findall(
                r'<img\b[^>]*src="([^"]*assets/screenshots/v20/[^"]+)"', text, flags=re.IGNORECASE
            )
        ]
        repeated_images = {source for source in functional_images if functional_images.count(source) > 1}
        if repeated_images:
            errors.append(f"{relative}: repeated functional screenshot(s): {sorted(repeated_images)}")
        if kind == "index.html":
            for requirement in (
                'data-random-pick-demo',
                'class="random-vinyl"',
                'class="random-pick-button"',
                'class="random-pick-title"',
                'class="random-pick-tags"',
                '/assets/demo/sees-the-light.jpg',
                '/assets/demo/in-waves.jpg',
                '/assets/demo/hunky-dory.jpg',
                '/assets/demo/moon-safari.jpg',
            ):
                if requirement not in text:
                    errors.append(f"{relative}: incomplete Random Pick reveal ({requirement})")
            if "random-record-a" in text or "random-pick-marker" in text or "random-picked-cover" in text:
                errors.append(f"{relative}: obsolete abstract Random Pick illustration remains")
        if kind == "screenshots/index.html":
            directory_locale = relative.parts[0] if relative.parts and relative.parts[0] in LOCALES else "fr"
            watch_locales = {"fr", "fr-ca", "en-us", "en-au", "en-ca", "en-gb"}
            if directory_locale in watch_locales and "watch-random-pick" not in text:
                errors.append(f"{relative}: localized watchOS 2.0 preview missing")
            if re.search(
                r'<section class="media-section[^\"]*v20-preview[^\"]*"',
                text,
            ):
                errors.append(
                    f"{relative}: redundant 2.0 release summary remains above screenshot gallery"
                )
        if kind in {"privacy/index.html", "mac-app/index.html"} and re.search(r'Record Picker v?1\.9|macOS 1\.9', text):
            errors.append(f"{relative}: stale current-version label")
        if 'content="https://recordpicker.app/assets/brand/icon-512.png"' in text:
            errors.append(f"{relative}: generic icon still used as social image")
        if '<meta name="twitter:card" content="summary_large_image">' not in text:
            errors.append(f"{relative}: Twitter large card missing")
        if kind != "index.html" and '"@type":"BreadcrumbList"' not in text:
            errors.append(f"{relative}: breadcrumb schema missing")
        if kind in {"choose-vinyl-record/index.html", "random-vinyl-record-picker/index.html", "manage-vinyl-collection/index.html"}:
            if '"@type":"Article"' not in text:
                errors.append(f"{relative}: Article schema missing")
        for card_match in RELEASE_CARD.finditer(text):
            version = card_match.group(1)
            card = card_match.group(0)
            release_pages += 1
            status = STATUS.search(card)
            if version == CURRENT_VERSION:
                if not status or "release-platform-summary" not in status.group(0):
                    errors.append(f"{relative}: current {CURRENT_VERSION} status missing")
            elif NEXT_VERSION and version == NEXT_VERSION:
                if PUBLICATION_PHASE != "full":
                    errors.append(f"{relative}: next release announced before full publication")
                if not status or "release-platform-summary" not in status.group(0):
                    errors.append(f"{relative}: next {NEXT_VERSION} status missing")
            elif version in HISTORICAL_VERSIONS and status:
                errors.append(f"{relative}: historical {version} still has a status")
        if NEXT_VERSION and f'data-release-version="{NEXT_VERSION}"' in text:
            next_release_pages += 1
            next_block = re.search(
                rf'<(?:section|article)\b[^>]*data-release-version="{re.escape(NEXT_VERSION)}"[^>]*>',
                text,
            )
            if not next_block or not re.search(
                r'class="[^"]*(?:next-release|release-upcoming)[^"]*"',
                next_block.group(0),
            ):
                errors.append(f"{relative}: next {NEXT_VERSION} is not marked as upcoming")
            if next_block and "current-release" in next_block.group(0):
                errors.append(f"{relative}: next {NEXT_VERSION} is incorrectly marked current")
        if f'data-release-gallery="{CURRENT_VERSION}"' in text:
            current_gallery_pages += 1
        if f'"softwareVersion":"{CURRENT_VERSION}"' in text:
            current_metadata_pages += 1
        if SOCIAL_IMAGE_URL in text:
            current_social_pages += 1
        if "<picture>" in text and ".avif" in text and ".webp" in text:
            optimized_picture_pages += 1
        if "data-previous-versions" in text:
            archived_gallery_pages += 1
        if kind == "index.html":
            homes += 1
            for forbidden in ("v18-showcase", "release-history", "support-band"):
                if forbidden in text:
                    errors.append(f"{relative}: verbose home section {forbidden} remains")
            for required in ("privacy-compact", "current-screens", 'id="versions"'):
                if required not in text:
                    errors.append(f"{relative}: compact home element {required} missing")
            if PUBLICATION_PHASE == "full":
                for required in ("v20-hero", "v20-home-screens"):
                    if required not in text:
                        errors.append(f"{relative}: published home missing {required}")
        if kind == "mac-app/index.html" and "macOS 1.8" in text:
            errors.append(f"{relative}: stale macOS 1.8 label")

    media_sitemap = (ROOT / "sitemap-media.xml").read_text(encoding="utf-8")
    if re.search(r"assets/screenshots/(?:v1[0-9]/|iphone/|ipad/|mac/)", media_sitemap):
        errors.append("sitemap-media.xml: obsolete screenshot remains")
    for forbidden_visual in (
        "assets/screenshots/iphone/import.jpeg",
        "assets/screenshots/ipad/manual-edit.png",
    ):
        if forbidden_visual in media_sitemap:
            errors.append(f"sitemap-media.xml: tutorial visual remains: {forbidden_visual}")
    for value in re.findall(r"<image:loc>(.*?)</image:loc>", media_sitemap):
        parsed = urlsplit(unescape(value))
        target = ROOT / parsed.path.lstrip("/")
        if not target.exists():
            errors.append(f"sitemap-media.xml: missing {target.relative_to(ROOT)}")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    canonical_urls = {
        unescape(value)
        for page in pages
        if "<main" in page.read_text(encoding="utf-8")
        for value in re.findall(
            r'<link rel="canonical" href="([^"]+)">',
            page.read_text(encoding="utf-8"),
        )
    }
    sitemap_urls = set(re.findall(r"<loc>(https://recordpicker\.app/[^<]*)</loc>", sitemap))
    media_page_urls = set(re.findall(r"<loc>(https://recordpicker\.app/[^<]*)</loc>", media_sitemap))
    missing_sitemap = canonical_urls - sitemap_urls
    missing_media_sitemap = canonical_urls - media_page_urls
    if missing_sitemap:
        errors.append(f"sitemap.xml misses {len(missing_sitemap)} canonical page(s)")
    if missing_media_sitemap:
        errors.append(
            f"sitemap-media.xml misses {len(missing_media_sitemap)} canonical page(s)"
        )

    if len(pages) < 278:
        errors.append(f"only {len(pages)} HTML pages found")
    expected_locales = len(LOCALES) + 1
    expected_content_pages = expected_locales * 9 + 3
    if content_pages != expected_content_pages:
        errors.append(
            f"expected {expected_content_pages} content pages, found {content_pages}"
        )
    if homes != expected_locales:
        errors.append(f"expected {expected_locales} home pages, found {homes}")
    versions_per_history = (3 if PUBLICATION_PHASE == "full" else 2) + (1 if NEXT_VERSION else 0)
    expected_release_cards = expected_locales * versions_per_history
    if release_pages != expected_release_cards:
        errors.append(
            f"expected {expected_release_cards} versioned release cards, "
            f"found {release_pages}"
        )
    expected_next_pages = expected_locales * 3 if PUBLICATION_PHASE == "full" and NEXT_VERSION else 0
    if next_release_pages != expected_next_pages:
        errors.append(
            f"expected {expected_next_pages} next-release pages, found {next_release_pages}"
        )
    expected_gallery_pages = expected_locales
    if current_gallery_pages != expected_gallery_pages:
        errors.append(
            f"expected {expected_gallery_pages} current galleries, "
            f"found {current_gallery_pages}"
        )
    if PUBLICATION_PHASE == "full":
        if current_metadata_pages != content_pages:
            errors.append(
                f"only {current_metadata_pages}/{content_pages} pages expose "
                f"softwareVersion {CURRENT_VERSION}"
            )
        if current_social_pages != content_pages:
            errors.append(
                f"only {current_social_pages}/{content_pages} pages use the current social image"
            )
        if optimized_picture_pages < expected_locales * 2:
            errors.append(
                f"expected responsive AVIF/WebP pictures on at least {expected_locales * 2} pages, "
                f"found {optimized_picture_pages}"
            )
        if archived_gallery_pages != 0:
            errors.append(
                "obsolete screenshot archives should not be visible; "
                f"found {archived_gallery_pages}"
            )
        preview_galleries = sum(
            'data-preview-gallery="2.0"' in page.read_text(encoding="utf-8")
            for page in pages
        )
        if preview_galleries != 0:
            errors.append(
                f"expected no 2.0 preview galleries after publication, found {preview_galleries}"
            )
    if (ROOT / "assets/screenshots/mac/record-crate-search.png").exists():
        errors.append("unused 4.5 MB record-crate-search.png still exists")
    for relative in (
        "assets/press/Record-Picker-Dossier-de-presse-FR.pdf",
        "assets/press/Record-Picker-Press-Kit-EN.pdf",
        "assets/press/Record-Picker-Press-Kit.zip",
    ):
        if not (ROOT / relative).is_file():
            errors.append(f"missing press asset {relative}")
    for image in (ROOT / "assets/social").glob("*.png"):
        if image.stat().st_size > 600_000:
            errors.append(f"{image.relative_to(ROOT)} exceeds 600 KB")
    for relative in RELEASE_STATE["publication_assets"]["screenshots"]:
        source = ROOT / "assets" / "screenshots" / "v20" / relative
        for suffix, maximum in ((".webp", 300_000), (".avif", 250_000)):
            derivative = source.with_suffix(suffix)
            if not derivative.is_file():
                errors.append(f"missing optimized asset {derivative.relative_to(ROOT)}")
            elif derivative.stat().st_size > maximum:
                errors.append(f"{derivative.relative_to(ROOT)} exceeds {maximum} bytes")
    for language in ("ar", "he"):
        for page in (ROOT / language).rglob("*.html"):
            if '<html lang=' in page.read_text(encoding="utf-8") and 'dir="rtl"' not in page.read_text(encoding="utf-8"):
                errors.append(f"{page.relative_to(ROOT)}: RTL direction missing")
    if errors:
        print("\n".join(errors[:100]))
        raise SystemExit(f"Quality audit failed with {len(errors)} error(s).")
    print(
        f"OK: {len(pages)} HTML pages, {content_pages} content pages, "
        f"{homes} compact localized homes, {release_pages} versioned cards, "
        f"release phase {PUBLICATION_PHASE}."
    )


if __name__ == "__main__":
    main()
