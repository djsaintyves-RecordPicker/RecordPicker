#!/usr/bin/env python3
"""Verify canonical consolidation, search answers and App Store attribution."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
pages = [path for path in ROOT.rglob("index.html") if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)]
canonicals: set[str] = set()

for path in pages:
    relative = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<link rel="canonical" href="([^"]+)">', text)
    if not match:
        errors.append(f"{relative}: missing canonical")
        continue
    canonical = match.group(1)
    canonicals.add(canonical)
    parts = relative.parts
    if parts[0] in {"en-au", "en-ca", "en-gb"}:
        suffix = "/".join(parts[1:-1])
        expected = "https://recordpicker.app/en-us/" + (suffix + "/" if suffix else "")
        if canonical != expected:
            errors.append(f"{relative}: expected consolidated canonical {expected}")
    for link in re.findall(r'<a\b[^>]*data-app-store-link[^>]*>', text):
        if 'data-app-store-campaign=' not in link:
            errors.append(f"{relative}: untracked App Store link")
    is_priority_guide = (
        len(parts) >= 2
        and parts[-2] in {"choose-vinyl-record", "random-vinyl-record-picker"}
        and (len(parts) == 2 or parts[0] in {"fr", "fr-ca", "en-au", "en-ca", "en-gb", "en-us"})
    )
    if is_priority_guide:
        if 'data-growth-answer' not in text or 'data-growth-faq' not in text:
            errors.append(f"{relative}: missing visible answer or FAQ schema")

for sitemap_name in ("sitemap.xml", "sitemap-media.xml"):
    text = (ROOT / sitemap_name).read_text(encoding="utf-8")
    urls = re.findall(r"<loc>(https://recordpicker\.app/[^<]*)</loc>", text)
    page_urls = [url for url in urls if "/assets/" not in url]
    if set(page_urls) != canonicals:
        errors.append(f"{sitemap_name}: canonical URL set differs from public pages")
    if len(page_urls) != len(set(page_urls)):
        errors.append(f"{sitemap_name}: duplicate page URL")

site_js = (ROOT / "site.js").read_text(encoding="utf-8")
if '2026-08-22T21:59:59Z' not in site_js or '.challenge-announcement, .challenge-section' not in site_js:
    errors.append("site.js: missing automatic post-contest transition")

if errors:
    raise SystemExit("\n".join(errors))
print(f"OK: {len(pages)} pages, {len(canonicals)} canonicals, tracked store links and evergreen contest transition.")
