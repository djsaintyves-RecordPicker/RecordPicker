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
NEXT_VERSION = RELEASE_STATE["next_release"]["version"]
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
        if re.search(r"Record Picker[^<\n]{0,120}\b(?:25\+?|29)\b", text):
            errors.append(f"{relative}: obsolete localization count remains")
        if relative.parts[0] in {"en-au", "en-ca", "en-gb", "en-us"}:
            if "Today Pick" in text:
                errors.append(f"{relative}: stale Today Pick product name")
        if re.search(
            r'assets/screenshots/v19/en-us/[^\"]+\.(?:avif|webp)\"', text
        ):
            errors.append(f"{relative}: unversioned optimized 1.9 screenshot")
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
        relative_parts = relative.parts[1:] if relative.parts and relative.parts[0] in LOCALES else relative.parts
        kind = "/".join(relative_parts)
        if kind in {"privacy/index.html", "readme/index.html", "support/index.html"}:
            if "support@recordpicker.app" not in text:
                errors.append(f"{relative}: public support contact missing")
        for requirement in (
            'class="skip-link"',
            'id="main-content"',
            "site.js?v=20260808-v19-locales",
            'href="/press/"',
            'href="https://www.instagram.com/recordpicker/" rel="me"',
            'href="https://www.youtube.com/@recordpicker" rel="me"',
            'href="https://www.facebook.com/profile.php?id=61591096987226" rel="me"',
            'href="https://www.threads.net/@recordpicker" rel="me"',
        ):
            if requirement not in text:
                errors.append(f"{relative}: missing {requirement}")
        if "quality.css?v=20260809-identity" not in text:
            errors.append(f"{relative}: missing versioned quality.css")
        selected_languages = re.findall(
            r'<a class="language-option"[^>]*aria-selected="true"', text
        )
        if len(selected_languages) != 1:
            errors.append(
                f"{relative}: expected one selected language, found {len(selected_languages)}"
            )
        if re.search(r'<img[^>]+src="[^"]*(?:tutorial|onboarding|walkthrough)', text, flags=re.IGNORECASE):
            errors.append(f"{relative}: forbidden tutorial image")
        for image_tag in re.findall(r'<img\b[^>]*>', text):
            for attribute in ("alt", "width", "height"):
                if not re.search(rf'\b{attribute}="[^"]*"', image_tag):
                    errors.append(f"{relative}: image missing {attribute}")
                    break
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
            elif version == NEXT_VERSION:
                if PUBLICATION_PHASE != "full":
                    errors.append(f"{relative}: next release announced before full publication")
                if not status or "release-platform-summary" not in status.group(0):
                    errors.append(f"{relative}: next {NEXT_VERSION} status missing")
            elif version in HISTORICAL_VERSIONS and status:
                errors.append(f"{relative}: historical {version} still has a status")
        if f'data-release-version="{NEXT_VERSION}"' in text:
            next_release_pages += 1
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
                for required in ("v19-hero", "v19-home-screens"):
                    if required not in text:
                        errors.append(f"{relative}: published home missing {required}")
        if kind == "mac-app/index.html" and "macOS 1.8" in text:
            errors.append(f"{relative}: stale macOS 1.8 label")

    media_sitemap = (ROOT / "sitemap-media.xml").read_text(encoding="utf-8")
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
    expected_content_pages = expected_locales * 9 + 2
    if content_pages != expected_content_pages:
        errors.append(
            f"expected {expected_content_pages} content pages, found {content_pages}"
        )
    if homes != expected_locales:
        errors.append(f"expected {expected_locales} home pages, found {homes}")
    expected_release_cards = expected_locales * (3 if PUBLICATION_PHASE == "full" else 2)
    if release_pages != expected_release_cards:
        errors.append(
            f"expected {expected_release_cards} versioned release cards, "
            f"found {release_pages}"
        )
    expected_next_pages = expected_locales * 3 if PUBLICATION_PHASE == "full" else 0
    if next_release_pages != expected_next_pages:
        errors.append(
            f"expected {expected_next_pages} next-release pages, found {next_release_pages}"
        )
    expected_gallery_pages = expected_locales if PUBLICATION_PHASE == "full" else 0
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
        if archived_gallery_pages != expected_locales:
            errors.append(
                f"expected {expected_locales} archived historical galleries, "
                f"found {archived_gallery_pages}"
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
        source = ROOT / "assets" / "screenshots" / "v19" / relative
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
