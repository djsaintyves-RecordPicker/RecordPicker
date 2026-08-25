#!/usr/bin/env python3
"""Promote staged 2.3.1 after all Apple builds are approved and ready."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from announce_release_2_3_1 import LOCALES, ROOT, STATE_PATH, VERSION, block


def promote(path: Path, tag: str) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    upcoming = block(text, VERSION, tag)
    current = block(text, "2.3", tag)
    is_screenshot_page = path.parent.name == "screenshots"
    if is_screenshot_page and not current:
        current = re.search(r'<section\b[^>]*data-release-gallery="2\.3"[^>]*>.*?</section>', text, re.DOTALL)
    if not upcoming or not current:
        raise RuntimeError(f"Expected staged 2.3.1 and current 2.3 blocks in {path}")
    if tag == "section" and path.name == "index.html" and not is_screenshot_page:
        published = upcoming.group(0).replace("v231-preview next-release", "v231-preview current-release")
        current_status = re.search(r'<p class="kicker">(.*?)</p>', current.group(0), re.DOTALL)
        if not current_status:
            raise RuntimeError(f"Missing localized available status in {path}")
        published = re.sub(r'<p class="kicker">.*?</p>', current_status.group(0), published, count=1, flags=re.DOTALL)
        text = text[:upcoming.start()] + published + text[current.end():]
    elif tag == "article":
        current_summary = re.search(r'<p class="release-platform-summary">.*?</p>', current.group(0), re.DOTALL)
        if not current_summary:
            raise RuntimeError(f"Missing localized availability summary in {path}")
        published = upcoming.group(0).replace(" release-preview release-upcoming", "")
        published = re.sub(r'<p class="release-platform-summary">.*?</p>', current_summary.group(0), published, count=1, flags=re.DOTALL)
        historical = re.sub(r'\s*<p class="release-platform-summary">.*?</p>', "", current.group(0), count=1, flags=re.DOTALL)
        text = text[:upcoming.start()] + published + historical + text[current.end():]
    else:
        text = text[:upcoming.start()] + text[upcoming.end():]
        text = text.replace('data-release-gallery="2.3"', 'data-release-gallery="2.3.1"', 1)
        text = text.replace('<h2>Record Picker 2.3</h2>', '<h2>Record Picker 2.3.1</h2>', 1)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def update_metadata(path: Path, date: str) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    text = re.sub(r'("softwareVersion":")[^"]+', rf'\g<1>{VERSION}', text)
    text = re.sub(r'("dateModified":")[^"]+', rf'\g<1>{date}', text)
    text = re.sub(r'<span id="site-footer-version">.*?</span>', f'<span id="site-footer-version">Record Picker · {VERSION}</span>', text, flags=re.DOTALL)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def update_state() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if state.get("next_release", {}).get("version") != VERSION:
        raise RuntimeError("2.3.1 is not staged")
    state["current_release"] = {"version": VERSION, "platform_versions": {p: VERSION for p in ("iphone", "ipad", "mac", "watch")}, "platforms": {p: "available" for p in ("iphone", "ipad", "mac", "watch")}, "required_platforms_for_full_release": ["iphone", "ipad", "mac", "watch"]}
    state.pop("next_release", None)
    state["historical_releases"] = ["2.3", *[v for v in state["historical_releases"] if v != "2.3"]]
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-apple-builds-ready", action="store_true", help="Required safety gate: all four Apple builds are approved and ready")
    parser.add_argument("--publication-date", required=True, help="Release date in YYYY-MM-DD format")
    args = parser.parse_args()
    if not args.confirm_apple_builds_ready:
        raise SystemExit("Refusing to publish: pass --confirm-apple-builds-ready only after iPhone, iPad, Apple Watch and Mac builds are approved.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.publication_date):
        raise SystemExit("Invalid --publication-date; expected YYYY-MM-DD")
    changed = 0
    for directory in LOCALES:
        root = ROOT / directory if directory else ROOT
        changed += promote(root / "index.html", "section")
        changed += promote(root / "readme" / "index.html", "article")
        changed += promote(root / "screenshots" / "index.html", "section")
    changed += sum(update_metadata(path, args.publication_date) for path in ROOT.rglob("*.html"))
    for name in ("sitemap.xml", "sitemap-media.xml"):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        path.write_text(re.sub(r"<lastmod>[^<]+</lastmod>", f"<lastmod>{args.publication_date}</lastmod>", text), encoding="utf-8")
    update_state()
    print(f"Published Record Picker {VERSION} across {changed} localized pages.")


if __name__ == "__main__":
    main()
