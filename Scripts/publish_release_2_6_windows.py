#!/usr/bin/env python3
"""Publish Windows 2.6 consistently without modifying press-kit files."""

from __future__ import annotations

from html import unescape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MICROSOFT_STORE = "https://apps.microsoft.com/detail/9N2ZWRL4M3JC"
RELEASE_DATE = "2026-09-24"
PLATFORM_ROUTES = {"ios-app", "watch-app", "mac-app", "android-app", "windows-app"}
SITE_LANGUAGES = [
    "ar", "de", "en-AU", "en-CA", "en-US", "en-GB", "ca", "ko", "zh-Hans",
    "zh-Hant", "da", "es-ES", "fi", "fr-CA", "fr-FR", "el", "he", "hi",
    "id", "it", "ja", "nl", "nb", "pl", "pt-BR", "pt-PT", "ru", "sv",
    "tr", "fr-CH", "de-CH", "it-CH", "en-CH", "es-MX", "th", "vi",
]
SITE_REGIONS = [
    "SA", "DE", "AU", "CA", "US", "GB", "ES", "KR", "CN", "TW", "DK",
    "FI", "FR", "GR", "IL", "IN", "ID", "IT", "JP", "NL", "NO", "PL",
    "BR", "PT", "RU", "SE", "TR", "CH", "MX", "TH", "VN",
]
OFFICIAL_SOCIALS = ["https://www.instagram.com/recordpicker/"]


def replace_json_ld(text: str, relative: Path) -> str:
    is_windows_page = "windows-app" in relative.parts
    is_cross_platform_page = not PLATFORM_ROUTES.intersection(relative.parts)

    def update(match: re.Match[str]) -> str:
        attributes, payload = match.groups()
        try:
            data = json.loads(unescape(payload))
        except json.JSONDecodeError:
            return match.group(0)

        def visit(item: object) -> None:
            if isinstance(item, list):
                for value in item:
                    visit(value)
                return
            if not isinstance(item, dict):
                return
            for value in item.values():
                visit(value)
            if item.get("@type") != "SoftwareApplication":
                return
            if is_windows_page:
                item["sameAs"] = OFFICIAL_SOCIALS
                item["inLanguage"] = SITE_LANGUAGES
                item["areaServed"] = SITE_REGIONS
                item["publisher"] = {
                    "@type": "Organization",
                    "name": "Record Picker",
                    "url": "https://recordpicker.app/",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://recordpicker.app/assets/brand/icon-512.png",
                    },
                    "sameAs": OFFICIAL_SOCIALS,
                }
            if is_cross_platform_page:
                systems = str(item.get("operatingSystem", ""))
                if "Windows 11" not in systems:
                    item["operatingSystem"] = f"{systems} / Windows 11".strip(" /")
                download = item.get("downloadUrl")
                if isinstance(download, str) and download != MICROSOFT_STORE:
                    item["downloadUrl"] = [download, MICROSOFT_STORE]
                elif isinstance(download, list) and MICROSOFT_STORE not in download:
                    download.append(MICROSOFT_STORE)
                item["dateModified"] = RELEASE_DATE

        visit(data)
        return f'<script type="application/ld+json"{attributes}>' + json.dumps(
            data, ensure_ascii=False, separators=(",", ":")
        ) + "</script>"

    text = re.sub(
        r'<script type="application/ld\+json"([^>]*)>(.*?)</script>',
        update,
        text,
        flags=re.DOTALL,
    )

    if is_windows_page and 'id="windows-app-schema"' not in text:
        language = re.search(r'<html\s+lang="([^"]+)"', text)
        description = re.search(r'<meta name="description" content="([^"]*)"', text)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        schema = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "Record Picker",
            "applicationCategory": "MultimediaApplication",
            "operatingSystem": "Windows 11",
            "softwareVersion": "2.6",
            "url": canonical.group(1),
            "downloadUrl": MICROSOFT_STORE,
            "image": "https://recordpicker.app/assets/brand/icon-512.png",
            "description": unescape(description.group(1)),
            "inLanguage": language.group(1),
            "dateModified": RELEASE_DATE,
            "offers": {
                "@type": "Offer",
                "price": 0,
                "availability": "https://schema.org/InStock",
                "url": MICROSOFT_STORE,
            },
            "publisher": {
                "@type": "Organization",
                "name": "Record Picker",
                "url": "https://recordpicker.app/",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://recordpicker.app/assets/brand/icon-512.png",
                },
                "sameAs": OFFICIAL_SOCIALS,
            },
            "sameAs": OFFICIAL_SOCIALS,
            "inLanguage": SITE_LANGUAGES,
            "areaServed": SITE_REGIONS,
        }
        tag = '<script type="application/ld+json" id="windows-app-schema">' + json.dumps(
            schema, ensure_ascii=False, separators=(",", ":")
        ) + "</script>"
        text = text.replace("</head>", tag + "</head>", 1)
    return text


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        relative = path.relative_to(ROOT)
        if relative.parts and relative.parts[0] == "snory-teller":
            continue
        text = path.read_text(encoding="utf-8")
        updated = re.sub(
            r'<p class="release-platform-summary"><strong>'
            r'iPhone · iPad · Apple Watch · Mac · ([^<]+)</strong><br>'
            r'Windows 2\.5 · [^<]+ · Windows 2\.6 · [^<]+</p>',
            r'<p class="release-platform-summary"><strong>'
            r'iPhone · iPad · Apple Watch · Mac · Windows · \1</strong></p>',
            text,
        )
        if "windows-app" in relative.parts:
            updated = updated.replace('data-windows-version="2.5"', 'data-windows-version="2.6"')
            updated = updated.replace("Record Picker 2.5", "Record Picker 2.6")
            updated = updated.replace(
                '<span id="site-footer-version">Record Picker · 2.5</span>',
                '<span id="site-footer-version">Record Picker · 2.6</span>',
            )
            updated = re.sub(
                r'("dateModified":")[^"]+', r'\g<1>' + RELEASE_DATE, updated
            )
        updated = replace_json_ld(updated, relative)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    state_path = ROOT / "data/release-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["current_release"]["platform_versions"]["windows"] = "2.6"
    required = state["current_release"]["required_platforms_for_full_release"]
    if "windows" not in required:
        required.append("windows")
    state["next_release"] = None
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Published Windows 2.6 metadata and status across {changed} pages.")


if __name__ == "__main__":
    main()
