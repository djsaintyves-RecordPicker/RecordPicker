#!/usr/bin/env python3
"""Publish Record Picker 2.3.2 on Mac while other Apple builds remain upcoming."""

from __future__ import annotations

import json
from pathlib import Path
import re

from announce_release_2_1 import COMING_SOON
from announce_release_2_3_1 import LOCALES, ROOT, block


VERSION = "2.3.2"
PUBLICATION_DATE = "2026-08-27"
STATE_PATH = ROOT / "data" / "release-state.json"


def kicker(release_block: str) -> str:
    match = re.search(r'<p class="kicker">(.*?)</p>', release_block, re.DOTALL)
    if not match:
        raise RuntimeError("Release status is missing")
    return match.group(1)


def partial_status(available: str, coming_soon: str) -> str:
    return f"{available} · Mac · {coming_soon} · iPhone · iPad · Apple Watch"


def update_release_pages(directory: str, locale: str) -> int:
    root = ROOT / directory if directory else ROOT
    home_path = root / "index.html"
    history_path = root / "readme/index.html"
    screenshots_path = root / "screenshots/index.html"

    home = home_path.read_text(encoding="utf-8")
    current = block(home, "2.3", "section")
    candidate = block(home, VERSION, "section")
    if not current or not candidate:
        raise RuntimeError(f"Expected 2.3 and {VERSION} home blocks in {home_path}")
    status = partial_status(kicker(current.group(0)), COMING_SOON[locale])

    changed = 0
    promoted = candidate.group(0)
    promoted = re.sub(
        r"section v232-preview next-release(?: release-partial)*",
        "section v232-preview next-release release-partial",
        promoted,
        count=1,
    )
    promoted = re.sub(
        r'<p class="kicker">.*?</p>',
        f'<p class="kicker">{status}</p>',
        promoted,
        count=1,
        flags=re.DOTALL,
    )
    updated = home[:candidate.start()] + promoted + home[candidate.end():]
    if updated != home:
        home_path.write_text(updated, encoding="utf-8")
        changed += 1

    history = history_path.read_text(encoding="utf-8")
    candidate = block(history, VERSION, "article")
    if not candidate:
        raise RuntimeError(f"Expected {VERSION} history card in {history_path}")
    promoted = candidate.group(0).replace("release-upcoming", "release-partial")
    promoted = re.sub(
        r'<p class="release-platform-summary">.*?</p>',
        f'<p class="release-platform-summary"><strong>{status}</strong></p>',
        promoted,
        count=1,
        flags=re.DOTALL,
    )
    updated = history[:candidate.start()] + promoted + history[candidate.end():]
    if updated != history:
        history_path.write_text(updated, encoding="utf-8")
        changed += 1

    screenshots = screenshots_path.read_text(encoding="utf-8")
    candidate = block(screenshots, VERSION, "section")
    if not candidate:
        raise RuntimeError(f"Expected {VERSION} screenshot marker in {screenshots_path}")
    promoted = candidate.group(0).replace(
        "media-section next-release v232-gallery-marker",
        "media-section next-release release-partial v232-gallery-marker",
    )
    promoted = re.sub(
        r'<p class="kicker">.*?</p>',
        f'<p class="kicker">{status}</p>',
        promoted,
        count=1,
        flags=re.DOTALL,
    )
    updated = screenshots[:candidate.start()] + promoted + screenshots[candidate.end():]
    if updated != screenshots:
        screenshots_path.write_text(updated, encoding="utf-8")
        changed += 1

    return changed


def update_mac_page(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r'("softwareVersion":")[^"]+', rf'\g<1>{VERSION}', text)
    updated = re.sub(
        r'("dateModified":")[^"]+',
        rf'\g<1>{PUBLICATION_DATE}',
        updated,
    )
    updated = re.sub(
        r'(<p class="(?:glass-pill )?eyebrow">.*?)Record Picker 2\.3(?:\.2)*(.*?</p>)',
        rf'\g<1>Record Picker {VERSION}\g<2>',
        updated,
        count=1,
        flags=re.DOTALL,
    )
    updated = re.sub(
        r'<span id="site-footer-version">.*?</span>',
        f'<span id="site-footer-version">Record Picker · {VERSION}</span>',
        updated,
        flags=re.DOTALL,
    )
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def update_state() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    next_release = state.get("next_release")
    if not next_release or next_release.get("version") != VERSION:
        raise RuntimeError(f"{VERSION} must be staged before publishing the Mac build")
    next_release["platforms"] = {
        "iphone": "coming_soon",
        "ipad": "coming_soon",
        "mac": "available",
        "watch": "coming_soon",
    }
    state["current_release"]["platform_versions"]["mac"] = VERSION
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def update_sitemaps() -> int:
    changed = 0
    for name in ("sitemap.xml", "sitemap-media.xml"):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        updated = re.sub(
            r'<lastmod>[^<]+</lastmod>',
            f'<lastmod>{PUBLICATION_DATE}</lastmod>',
            text,
        )
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def main() -> None:
    changed = sum(
        update_release_pages(directory, locale)
        for directory, locale in LOCALES.items()
    )
    changed += sum(
        update_mac_page((ROOT / directory if directory else ROOT) / "mac-app/index.html")
        for directory in LOCALES
    )
    changed += update_sitemaps()
    update_state()
    print(
        f"Published Record Picker {VERSION} on Mac across {changed} pages and sitemaps; "
        "iPhone, iPad and Apple Watch remain coming soon."
    )


if __name__ == "__main__":
    main()
