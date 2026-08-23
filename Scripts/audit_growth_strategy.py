#!/usr/bin/env python3
"""Verify self-canonicals, regional search metadata and App Store attribution."""

from __future__ import annotations

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
CURRENT_VERSION = json.loads(
    (ROOT / "data" / "release-state.json").read_text(encoding="utf-8")
)["current_release"]["version"]
errors: list[str] = []
pages = [path for path in ROOT.rglob("index.html") if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)]
canonicals: set[str] = set()
regional_titles: dict[str, list[Path]] = {}
regional_descriptions: dict[str, list[Path]] = {}

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
    expected_path = "/" if relative == Path("index.html") else "/" + relative.parent.as_posix().strip("/") + "/"
    if expected_path == "/en-us/":
        expected_path = "/"
    elif expected_path.startswith("/en-us/"):
        root_path = expected_path.removeprefix("/en-us")
        counterpart = ROOT / root_path.strip("/") / "index.html"
        if counterpart.exists():
            expected_path = root_path
    expected = "https://recordpicker.app" + expected_path
    if canonical != expected:
        errors.append(f"{relative}: expected canonical {expected}")
    og_url = re.search(r'<meta property="og:url" content="([^"]+)">', text)
    if not og_url or og_url.group(1) != expected:
        errors.append(f"{relative}: og:url does not match self-canonical")
    if parts[0] in {"en-au", "en-ca", "en-gb", "en-us"}:
        title = re.search(r"<title>(.*?)</title>", text, flags=re.DOTALL)
        description = re.search(r'<meta name="description" content="([^"]*)">', text)
        if not title or not description:
            errors.append(f"{relative}: missing regional title or description")
        else:
            regional_titles.setdefault(title.group(1), []).append(relative)
            regional_descriptions.setdefault(description.group(1), []).append(relative)
            if len(description.group(1)) < 120:
                errors.append(f"{relative}: regional description is too short")
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

for value, relatives in regional_titles.items():
    if len(relatives) > 1:
        errors.append(f"duplicate regional title on {', '.join(map(str, relatives))}: {value}")
for value, relatives in regional_descriptions.items():
    if len(relatives) > 1:
        errors.append(f"duplicate regional description on {', '.join(map(str, relatives))}")

for sitemap_name in ("sitemap.xml", "sitemap-media.xml"):
    text = (ROOT / sitemap_name).read_text(encoding="utf-8")
    urls = re.findall(r"<loc>(https://recordpicker\.app/[^<]*)</loc>", text)
    page_urls = [url for url in urls if "/assets/" not in url]
    if set(page_urls) != canonicals:
        errors.append(f"{sitemap_name}: canonical URL set differs from public pages")
    if len(page_urls) != len(set(page_urls)):
        errors.append(f"{sitemap_name}: duplicate page URL")

for home in [ROOT / "index.html", ROOT / "fr" / "index.html", ROOT / "fr-ca" / "index.html"]:
    text = home.read_text(encoding="utf-8")
    positions = [
        text.find(
            f'class="section v{CURRENT_VERSION.replace(".", "")}-preview current-release"'
        ),
        text.find('class="section split" id="app"'),
        text.find('class="section privacy-compact"'),
    ]
    if home != ROOT / "index.html":
        positions.insert(2, text.find('class="section press-review-spotlight"'))
    if -1 in positions or positions != sorted(positions):
        errors.append(f"{home.relative_to(ROOT)}: product-first homepage hierarchy is incomplete")
    if home != ROOT / "index.html" and 'data-app-store-campaign="RP20_InstagramMac4Ever"' not in text:
        errors.append(f"{home.relative_to(ROOT)}: Mac4Ever conversion CTA missing")

if errors:
    raise SystemExit("\n".join(errors))
print(f"OK: {len(pages)} canonical pages, unique regional metadata and tracked store links.")
