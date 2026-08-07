#!/usr/bin/env python3
"""Fail when the generated public site violates release or quality invariants."""

from __future__ import annotations

from html import unescape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
LOCALES = {
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "tr", "zh-hans", "zh-hant",
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
    pages = sorted(ROOT.rglob("*.html"))
    errors: list[str] = []
    content_pages = 0
    release_pages = 0
    homes = 0
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for value in re.findall(r'(?:href|src)="([^"]+)"', text):
            target = local_target(page, value)
            if target and not target.exists():
                errors.append(f"{page.relative_to(ROOT)}: missing {target.relative_to(ROOT)}")
        for payload in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', text, flags=re.DOTALL):
            try:
                json.loads(unescape(payload))
            except json.JSONDecodeError as error:
                errors.append(f"{page.relative_to(ROOT)}: invalid JSON-LD: {error}")
        if "<main" not in text:
            continue
        content_pages += 1
        relative = page.relative_to(ROOT)
        relative_parts = relative.parts[1:] if relative.parts and relative.parts[0] in LOCALES else relative.parts
        kind = "/".join(relative_parts)
        for requirement in ('class="skip-link"', 'id="main-content"', "quality.css?v=20260807-quality"):
            if requirement not in text:
                errors.append(f"{relative}: missing {requirement}")
        if re.search(r'<img[^>]+src="[^"]*(?:tutorial|onboarding|walkthrough)', text, flags=re.IGNORECASE):
            errors.append(f"{relative}: forbidden tutorial image")
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
            if version == "1.9":
                if not status or "release-platform-summary" not in status.group(0):
                    errors.append(f"{relative}: current 1.9 status missing")
            elif status:
                errors.append(f"{relative}: historical {version} still has a status")
        if kind == "index.html":
            homes += 1
            for forbidden in ("v18-showcase", "release-history", "support-band"):
                if forbidden in text:
                    errors.append(f"{relative}: verbose home section {forbidden} remains")
            for required in ("privacy-compact", "current-screens", 'id="versions"'):
                if required not in text:
                    errors.append(f"{relative}: compact home element {required} missing")
        if kind == "mac-app/index.html" and "macOS 1.8" in text:
            errors.append(f"{relative}: stale macOS 1.8 label")

    media_sitemap = (ROOT / "sitemap-media.xml").read_text(encoding="utf-8")
    for value in re.findall(r"<image:loc>(.*?)</image:loc>", media_sitemap):
        parsed = urlsplit(unescape(value))
        target = ROOT / parsed.path.lstrip("/")
        if not target.exists():
            errors.append(f"sitemap-media.xml: missing {target.relative_to(ROOT)}")

    if len(pages) < 278:
        errors.append(f"only {len(pages)} HTML pages found")
    if content_pages != 270:
        errors.append(f"expected 270 content pages, found {content_pages}")
    if homes != 30:
        errors.append(f"expected 30 home pages, found {homes}")
    if release_pages != 60:
        errors.append(f"expected 60 versioned release cards, found {release_pages}")
    if (ROOT / "assets/screenshots/mac/record-crate-search.png").exists():
        errors.append("unused 4.5 MB record-crate-search.png still exists")
    for image in (ROOT / "assets/social").glob("*.png"):
        if image.stat().st_size > 600_000:
            errors.append(f"{image.relative_to(ROOT)} exceeds 600 KB")
    if errors:
        print("\n".join(errors[:100]))
        raise SystemExit(f"Quality audit failed with {len(errors)} error(s).")
    print(
        f"OK: {len(pages)} HTML pages, {content_pages} content pages, "
        f"{homes} compact localized homes, {release_pages} versioned cards."
    )


if __name__ == "__main__":
    main()
