#!/usr/bin/env python3
"""Apply shared editorial and layout refinements to generated site pages."""

from __future__ import annotations

from pathlib import Path
from html import escape, unescape
import json
import re


ROOT = Path(__file__).resolve().parents[1]
DOC_KINDS = {"privacy", "readme", "support"}
ADDITIONAL_SCHEMA_LOCALES = (
    ("es-MX", "Español (México)", "MX", "MXN", "mx"),
    ("th", "ไทย", "TH", "THB", "th"),
    ("vi", "Tiếng Việt", "VN", "VND", "vn"),
)


def page_kind(path: Path) -> str:
    relative = path.relative_to(ROOT)
    return relative.parent.name if relative.name == "index.html" else ""


def deduplicate_feature_lists(text: str) -> str:
    def clean(match: re.Match[str]) -> str:
        items = re.findall(r"<li>.*?</li>", match.group(1), flags=re.DOTALL)
        unique: list[str] = []
        seen: set[str] = set()
        for item in items:
            key = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", item)).strip()
            if key and key not in seen:
                unique.append(item)
                seen.add(key)
        return '<ul class="feature-list">' + "".join(unique) + "</ul>"

    return re.sub(
        r'<ul class="feature-list">(.*?)</ul>', clean, text, flags=re.DOTALL
    )


def deduplicate_plain_lists(text: str) -> str:
    def clean(match: re.Match[str]) -> str:
        items = re.findall(r"<li(?: [^>]*)?>.*?</li>", match.group(1), flags=re.DOTALL)
        unique: list[str] = []
        seen: set[str] = set()
        for item in items:
            key = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", item)).strip()
            if key and key not in seen:
                unique.append(item)
                seen.add(key)
        return "<ul>" + "".join(unique) + "</ul>"

    return re.sub(r"<ul>(.*?)</ul>", clean, text, flags=re.DOTALL)


def improve_document_description(text: str, kind: str) -> str:
    """Use the page's own localized editorial copy as its search description."""
    body = re.search(r'<section class="doc-content">(.*?)</section>', text, re.DOTALL)
    if not body:
        return text
    candidates = re.findall(r'<p(?: class="([^"]*)")?>(.*?)</p>', body.group(1), re.DOTALL)
    description = ""
    for css_class, markup in candidates:
        if "doc-meta" in css_class:
            continue
        value = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", markup)).strip()
        value = unescape(value)
        if len(value) >= 45 or kind in {"privacy", "support"}:
            description = value
            break
    if not description:
        return text
    encoded = escape(description, quote=True)
    for name in ("description", "twitter:description"):
        text = re.sub(
            rf'(<meta name="{re.escape(name)}" content=")[^"]*(")',
            rf"\g<1>{encoded}\2",
            text,
            count=1,
        )
    text = re.sub(
        r'(<meta property="og:description" content=")[^"]*(")',
        rf"\g<1>{encoded}\2",
        text,
        count=1,
    )
    return text


def clean_feature_cards(text: str) -> str:
    def plain(value: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", value)).strip()

    def clean_card(match: re.Match[str]) -> str:
        card = match.group(0)
        heading = re.search(r"<h3>(.*?)</h3>", card, flags=re.DOTALL)
        paragraph = re.search(r"<p>(.*?)</p>", card, flags=re.DOTALL)
        reserved = {
            plain(value.group(1))
            for value in (heading, paragraph)
            if value and plain(value.group(1))
        }

        def clean_list(list_match: re.Match[str]) -> str:
            kept: list[str] = []
            seen = set(reserved)
            for item in re.findall(
                r"<li>.*?</li>", list_match.group(1), flags=re.DOTALL
            ):
                key = plain(item)
                if key and key not in seen:
                    kept.append(item)
                    seen.add(key)
            return '<ul class="feature-list">' + "".join(kept) + "</ul>"

        card = re.sub(
            r'<ul class="feature-list">(.*?)</ul>',
            clean_list,
            card,
            flags=re.DOTALL,
        )
        if heading and "32" in plain(heading.group(1)):
            card = re.sub(
                r'<figure class="feature-visual[^"]*">.*?</figure>',
                "",
                card,
                count=1,
                flags=re.DOTALL,
            )
        return card

    return re.sub(
        r'<article class="card feature-card">.*?</article>',
        clean_card,
        text,
        flags=re.DOTALL,
    )


def archive_release_history(text: str) -> str:
    marker = '<div class="timeline compact">'
    start = text.find(marker)
    if start < 0:
        return text
    end_marker = "</div></section></main>"
    end = text.find(end_marker, start)
    if end < 0:
        return text
    inner = text[start + len(marker) : end]
    cards = re.findall(
        r'<article class="release-card.*?</article>', inner, flags=re.DOTALL
    )
    if len(cards) < 3:
        return text
    current = [
        card
        for card in cards
        if 'data-release-version="2.0"' in card
        or 'data-release-version="1.9"' in card
    ]
    historical = [card for card in cards if card not in current]
    if not current or not historical:
        return text
    version_link = re.search(
        r'<a href="(?:\.\./)?index\.html#versions">([^<]+)</a>', text
    )
    summary = version_link.group(1) if version_link else "Previous versions"
    replacement = (
        '<div class="timeline compact current-release-timeline">'
        + "".join(current)
        + "</div>"
        + '<details class="release-history-archive">'
        + f"<summary>{summary}</summary>"
        + '<div class="timeline compact">'
        + "".join(historical)
        + "</div></details>"
    )
    return text[:start] + replacement + text[end + len("</div>") :]


def update_software_schema(text: str) -> str:
    def update(match: re.Match[str]) -> str:
        payload = json.loads(unescape(match.group(1)))
        if payload.get("@type") != "SoftwareApplication":
            return match.group(0)
        languages = payload.setdefault("inLanguage", [])
        language_names = payload.setdefault("availableLanguage", [])
        regions = payload.setdefault("areaServed", [])
        offers = payload.setdefault("offers", [])
        offered_regions = {
            offer.get("eligibleRegion") for offer in offers if isinstance(offer, dict)
        }
        for code, name, region, currency, storefront in ADDITIONAL_SCHEMA_LOCALES:
            if code not in languages:
                languages.append(code)
            if name not in language_names:
                language_names.append(name)
            if region not in regions:
                regions.append(region)
            if region not in offered_regions:
                offers.append(
                    {
                        "@type": "Offer",
                        "price": 0,
                        "priceCurrency": currency,
                        "availability": "https://schema.org/InStock",
                        "url": (
                            f"https://apps.apple.com/{storefront}/app/recordpicker/"
                            "id6780422305"
                        ),
                        "eligibleRegion": region,
                    }
                )
        payload["dateModified"] = "2026-08-08"
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        return match.group(0).replace(match.group(1), encoded)

    return re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        update,
        text,
        flags=re.DOTALL,
    )


def use_optimized_legacy_media(text: str) -> str:
    """Serve generated WebP derivatives for legacy screenshot images."""
    return re.sub(
        r'((?:\.\./)*assets/screenshots/(?!v19/)[^"\'?#]+)\.(?:png|jpe?g)(?=\?[^"\']*|["\'])',
        r"\1.webp",
        text,
        flags=re.IGNORECASE,
    )


def refine(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original
    kind = page_kind(path)

    text = re.sub(
        r"(<h1>)(.*?)(?: - Record Picker)(</h1>)",
        r"\1\2\3",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = text.replace(
        '<p class="doc-meta">Record Picker 1.8</p>',
        '<p class="doc-meta">Record Picker 1.9</p>',
    )
    text = text.replace(
        '<p class="doc-meta">Record Picker v1.8',
        '<p class="doc-meta">Record Picker v1.9',
    )

    if kind in {"privacy", "support"}:
        text = re.sub(
            r'<p class="doc-tagline">.*?</p>', "", text, count=1, flags=re.DOTALL
        )
    if kind == "support":
        text = re.sub(
            r'<div class="context-pair">.*?</div>',
            "",
            text,
            count=1,
            flags=re.DOTALL,
        )
    if kind == "readme":
        text = text.replace("29", "32")
        text = text.replace(
            "assets/screenshots/iphone/import.jpeg",
            "assets/screenshots/iphone/tools-menu.jpeg",
        )
        text = deduplicate_feature_lists(text)
        text = clean_feature_cards(text)
        text = deduplicate_plain_lists(text)
        text = re.sub(
            r'<p>(?=[^<]*(?:1\.6))(?=[^<]*(?:1\.8))[^<]*</p>',
            "",
            text,
            flags=re.DOTALL,
        )
        text = archive_release_history(text)

    text = re.sub(
        r'<figure[^>]*>(?:(?!</figure>).)*src="[^"]*assets/screenshots/(?:iphone/import\.jpeg|ipad/manual-edit\.png)"(?:(?!</figure>).)*</figure>',
        "",
        text,
        flags=re.DOTALL,
    )

    text = re.sub(
        r'(quality\.css\?v=)[^"\']+', r'\g<1>20260808-finish2', text
    )
    text = update_software_schema(text)
    text = use_optimized_legacy_media(text)
    text = improve_document_description(text, kind)
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if page_kind(path) not in DOC_KINDS:
            text = path.read_text(encoding="utf-8")
            updated = re.sub(
                r'(quality\.css\?v=)[^"\']+',
                r'\g<1>20260808-finish2',
                text,
            )
            updated = re.sub(
                r'<figure[^>]*>(?:(?!</figure>).)*src="[^"]*assets/screenshots/(?:iphone/import\.jpeg|ipad/manual-edit\.png)"(?:(?!</figure>).)*</figure>',
                "",
                updated,
                flags=re.DOTALL,
            )
            updated = update_software_schema(updated)
            updated = use_optimized_legacy_media(updated)
            if updated != text:
                path.write_text(updated, encoding="utf-8")
                changed += 1
            continue
        changed += refine(path)
    media_sitemap = ROOT / "sitemap-media.xml"
    sitemap = media_sitemap.read_text(encoding="utf-8")
    sitemap = re.sub(
        r'\s*<image:image>(?:(?!</image:image>).)*(?:iphone/import\.jpeg|ipad/manual-edit\.png)(?:(?!</image:image>).)*</image:image>',
        "",
        sitemap,
        flags=re.DOTALL,
    )
    sitemap = re.sub(
        r'(<video:thumbnail_loc>https://recordpicker\.app/assets/screenshots/)(?:iphone/import\.jpeg|ipad/manual-edit\.png)(</video:thumbnail_loc>)',
        r'\1iphone/mood-pick-1.6-en-us.jpeg\2',
        sitemap,
    )
    media_sitemap.write_text(sitemap, encoding="utf-8")
    print(f"Refined {changed} HTML pages.")


if __name__ == "__main__":
    main()
