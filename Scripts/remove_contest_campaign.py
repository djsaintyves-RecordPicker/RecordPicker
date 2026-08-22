#!/usr/bin/env python3
"""Remove the finished 2026 contest campaign from the public website."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

BLOCKS = (
    re.compile(r'<aside class="challenge-announcement".*?</aside>', re.DOTALL),
    re.compile(r'<section class="challenge-section".*?</section>', re.DOTALL),
    re.compile(r'<section class="section contest-callout".*?</section>', re.DOTALL),
)
CONTEST_LINK = re.compile(r'<a href="/contest/"[^>]*>.*?</a>', re.DOTALL)
CONTEST_URL = re.compile(
    r'\s*<url>\s*<loc>https://recordpicker\.app/contest/</loc>.*?</url>',
    re.DOTALL,
)
CAMPAIGN_CSS = re.compile(
    r'\n/\* #RecordPickerChallenge campaign.*?(?=/\* App screenshots)',
    re.DOTALL,
)


def update_html(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original
    for pattern in BLOCKS:
        text = pattern.sub("", text)
    text = CONTEST_LINK.sub("", text)
    text = re.sub(
        r'quality\.css\?v=[^"\']+',
        'quality.css?v=20260822-no-contest',
        text,
    )
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def update_sitemap(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = CONTEST_URL.sub("", original)
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def update_css() -> bool:
    path = ROOT / "quality.css"
    original = path.read_text(encoding="utf-8")
    text = CAMPAIGN_CSS.sub("\n", original)
    text = text.replace("h2,\n.challenge-section h2 {", "h2 {")
    text = text.replace("  .challenge-lead,\n", "")
    text = text.replace(
        ":where(.challenge-legal, .challenge-media figcaption, .seo-link-card .kicker)",
        ":where(.seo-link-card .kicker)",
    )
    for selector in (
        "  .challenge-media figcaption,\n",
        "  .challenge-kicker,\n",
        "  .challenge-legal,\n",
    ):
        text = text.replace(selector, "")
    text = re.sub(
        r'html\[dir="rtl"\] \.challenge-steps.*?\n@media \(max-width: 820px\) \{.*?\n\}\n',
        "",
        text,
        flags=re.DOTALL,
    )
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    pages = sum(update_html(path) for path in ROOT.rglob("*.html"))
    maps = sum(update_sitemap(ROOT / name) for name in ("sitemap.xml", "sitemap-media.xml"))
    css = update_css()
    print(
        f"Removed the contest campaign from {pages} pages and {maps} sitemaps"
        f"; stylesheet updated: {css}."
    )


if __name__ == "__main__":
    main()
