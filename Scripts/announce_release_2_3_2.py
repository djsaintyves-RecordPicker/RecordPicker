#!/usr/bin/env python3
"""Advance the staged release to 2.3.2 and align platform statuses."""

from __future__ import annotations

import json
from pathlib import Path
import re

from announce_release_2_1 import COMING_SOON
from announce_release_2_3_1 import LOCALES, ROOT


OLD_VERSION = "2.3.1"
VERSION = "2.3.2"
STATE_PATH = ROOT / "data" / "release-state.json"


def locale_root(directory: str) -> Path:
    return ROOT / directory if directory else ROOT


def locale_html_paths(directory: str) -> list[Path]:
    root = locale_root(directory)
    paths = list(root.rglob("*.html"))
    if directory:
        return paths
    localized_directories = {name for name in LOCALES if name}
    return [
        path for path in paths
        if path.relative_to(ROOT).parts[0] not in localized_directories
    ]


def advance_release_blocks() -> int:
    changed = 0
    for directory in LOCALES:
        root = locale_root(directory)
        for relative in ("index.html", "readme/index.html", "screenshots/index.html"):
            path = root / relative
            text = path.read_text(encoding="utf-8")
            updated = text.replace(OLD_VERSION, VERSION).replace("v231-", "v232-")
            if updated != text:
                path.write_text(updated, encoding="utf-8")
                changed += 1
    return changed


def align_platform_statuses() -> int:
    changed = 0
    for directory, locale in LOCALES.items():
        coming_soon = COMING_SOON[locale]
        for path in locale_html_paths(directory):
            text = path.read_text(encoding="utf-8")
            updated = re.sub(
                r'(<span>Windows <small>).*?(</small></span>)',
                rf'\g<1>{coming_soon}\g<2>',
                text,
            )
            # The homepage badges repeat the same roadmap outside the menu.
            updated = re.sub(
                r'(<span class="future-platform"><b>Windows</b><small>).*?(</small></span>)',
                rf'\g<1>{coming_soon}\g<2>',
                updated,
            )
            if updated != text:
                path.write_text(updated, encoding="utf-8")
                changed += 1
    return changed


def update_state() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if state["current_release"]["version"] != "2.3":
        raise RuntimeError("2.3 must remain current while 2.3.2 is staged")
    state["next_release"] = {
        "version": VERSION,
        "platforms": {
            platform: "coming_soon"
            for platform in ("iphone", "ipad", "mac", "watch")
        },
    }
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    release_pages = advance_release_blocks()
    platform_pages = align_platform_statuses()
    update_state()
    print(
        f"Announced Record Picker {VERSION} on {release_pages} localized release pages; "
        f"aligned platform statuses on {platform_pages} pages."
    )


if __name__ == "__main__":
    main()
