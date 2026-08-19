#!/usr/bin/env python3
"""Keep public version labels aligned with the versions distributed by Apple."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
CURRENT_LABEL = "iOS 2.1.1 · macOS 2.2"

RELEASE_20_CARD = re.compile(
    r'<article class="release-card[^>]*data-release-version="2\.0"[^>]*>.*?</article>',
    flags=re.DOTALL,
)


def normalize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = RELEASE_20_CARD.sub("", text)

    platform_labels = {
        "Mac · Record Picker 2.0": "Mac · Record Picker 2.1",
        "iPhone · Record Picker 2.0": "iPhone · Record Picker 2.1.1",
        "iPad · Record Picker 2.0": "iPad · Record Picker 2.1.1",
        "Apple Watch · Record Picker 2.0": "Apple Watch · Record Picker 2.1.1",
        "Mac · Record Picker 2.1": "Mac · macOS 2.2",
        "Mac · macOS 2.1": "Mac · macOS 2.2",
        "iPhone · Record Picker 2.1.1": "iPhone · iOS 2.1.1",
        "iPad · Record Picker 2.1.1": "iPad · iOS 2.1.1",
        "Apple Watch · Record Picker 2.1.1": "Apple Watch · iOS 2.1.1",
    }
    for old, new in platform_labels.items():
        updated = updated.replace(old, new)

    updated = updated.replace("<h2>Record Picker 2.0</h2>", f"<h2>{CURRENT_LABEL}</h2>")
    updated = updated.replace("<h2>Record Picker 2.1</h2>", f"<h2>{CURRENT_LABEL}</h2>")
    updated = updated.replace("<strong>Record Picker 2.0</strong>", f"<strong>{CURRENT_LABEL}</strong>")
    updated = updated.replace("macOS 2.0", "macOS 2.2")
    updated = updated.replace("iOS 2.1.1 · macOS 2.1", CURRENT_LABEL)
    updated = updated.replace("Record Picker v2.0", "Record Picker")
    updated = updated.replace("Record Picker 2.0", "Record Picker")
    updated = updated.replace(
        '<span class="version-pill">v2.1.1</span>',
        f'<span class="version-pill">{CURRENT_LABEL}</span>',
    )
    updated = updated.replace("Record Picker 2.1.1", "iOS 2.1.1")
    updated = re.sub(r"Record Picker 2\.1(?!\.1)", "Record Picker", updated)
    updated = updated.replace(
        '<span id="site-footer-version">Record Picker v2.1.1</span>',
        f'<span id="site-footer-version">Record Picker · {CURRENT_LABEL}</span>',
    )

    if path.name == "index.html" and path.parent.name == "mac-app":
        updated = re.sub(r'"softwareVersion":"[^"]+"', '"softwareVersion":"2.2"', updated)

    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = sum(normalize(path) for path in ROOT.rglob("*.html"))
    print(f"Normalized public version labels on {changed} HTML pages.")


if __name__ == "__main__":
    main()
