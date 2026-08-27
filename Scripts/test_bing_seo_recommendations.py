#!/usr/bin/env python3
"""Verify the technical Bing recommendation fixes remain in place."""

from __future__ import annotations

from collections import defaultdict
from html import unescape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TARGETED_DESCRIPTIONS = {
    "zh-hans/index.html",
    "zh-hant/index.html",
    "ja/index.html",
    "ko/index.html",
    "zh-hans/readme/index.html",
    "ko/support/index.html",
    "ko/mac-app/index.html",
    "id/choose-vinyl-record/index.html",
}

titles: dict[str, list[str]] = defaultdict(list)
descriptions: dict[str, list[str]] = defaultdict(list)
pages = 0

for path in sorted(ROOT.rglob("*.html")):
    text = path.read_text(encoding="utf-8")
    relative = path.relative_to(ROOT).as_posix()
    assert not re.search(r'href="(?:\.\./)*index\.html(?:#[^"]*)?"', text), relative

    title_match = re.search(r"<title>(.*?)</title>", text, flags=re.DOTALL)
    description_match = re.search(
        r'<meta name="description" content="([^"]*)"', text, flags=re.DOTALL
    )
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
    if not (title_match and description_match and canonical):
        continue
    title = unescape(title_match.group(1)).strip()
    description = unescape(description_match.group(1)).strip()
    titles[title].append(relative)
    descriptions[description].append(relative)
    if relative in TARGETED_DESCRIPTIONS:
        assert len(description) >= 140, (relative, len(description))
    pages += 1

assert not {value: paths for value, paths in titles.items() if len(paths) > 1}
assert not {value: paths for value, paths in descriptions.items() if len(paths) > 1}

print(f"Verified clean URLs and unique Bing metadata across {pages} indexable pages.")
