#!/usr/bin/env python3
"""Add the temporary 3 Picks Challenge callout and rules link idempotently."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LOCALES = (
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "es-mx", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "th", "tr", "vi", "zh-hans",
    "zh-hant",
)

CALLOUT = (
    '<section class="section contest-callout" data-campaign="three-picks-2026" '
    'aria-labelledby="three-picks-title"><div><p class="kicker">Instagram · 9–22 August 2026</p>'
    '<h2 id="three-picks-title">70 Record Picker Pro codes to win</h2>'
    '<p class="lead">Take the 3 Picks Challenge. Five winners every day.</p></div>'
    '<a class="button primary" href="/contest/">Play and read the official rules</a></section>'
)

FOOTER_LINK = '<a href="/contest/" data-campaign-link="three-picks-2026">3 Picks Challenge rules</a>'


def add_home_callout(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    if 'data-campaign="three-picks-2026"' not in html:
        html, count = re.subn(
            r'(<section class="facts-band">.*?</section>)',
            r'\1' + CALLOUT,
            html,
            count=1,
            flags=re.DOTALL,
        )
        if count != 1:
            raise RuntimeError(f"facts band not found in {path}")
        path.write_text(html, encoding="utf-8")


def add_footer_link(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    relative = path.relative_to(ROOT)
    is_home = relative == Path("index.html") or (
        len(relative.parts) == 2
        and relative.parts[0] in LOCALES
        and relative.parts[1] == "index.html"
    )
    if not is_home and "contest-page" not in html:
        html = html.replace(FOOTER_LINK, "")
        html = html.replace(
            "quality.css?v=20260808-contest1",
            "quality.css?v=20260808-finish2",
        )
        path.write_text(html, encoding="utf-8")
        return
    html = html.replace("quality.css?v=20260808-finish2", "quality.css?v=20260808-contest1")
    if 'data-campaign-link="three-picks-2026"' in html or "contest-page" in html:
        path.write_text(html, encoding="utf-8")
        return
    marker = "</nav></footer>"
    if marker not in html:
        path.write_text(html, encoding="utf-8")
        return
    head, tail = html.rsplit(marker, 1)
    path.write_text(head + FOOTER_LINK + marker + tail, encoding="utf-8")


def main() -> None:
    add_home_callout(ROOT / "index.html")
    for locale in LOCALES:
        add_home_callout(ROOT / locale / "index.html")
    for path in ROOT.rglob("*.html"):
        add_footer_link(path)
    print("OK: 3 Picks Challenge callout and rules links added.")


if __name__ == "__main__":
    main()
