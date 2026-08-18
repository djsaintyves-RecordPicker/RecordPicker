#!/usr/bin/env python3
"""Publish the approved iOS 2.1.1 / macOS 2.1 release on the website."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "data" / "release-state.json"
PUBLIC_VERSION = "2.1.1"
RELEASE_DATE = "2026-08-18"


def release_block(text: str, version: str, tag: str) -> re.Match[str] | None:
    return re.search(
        rf'<{tag}\b[^>]*data-release-version="{re.escape(version)}"[^>]*>.*?</{tag}>',
        text,
        flags=re.DOTALL,
    )


def home_status(block: str) -> str:
    match = re.search(r'<p class="kicker">(.*?)</p>', block, flags=re.DOTALL)
    if not match:
        raise RuntimeError("Current release status is missing from the homepage")
    return match.group(1)


def readme_status(block: str) -> str:
    match = re.search(
        r'<p class="release-platform-summary">.*?</p>', block, flags=re.DOTALL
    )
    if not match:
        raise RuntimeError("Current platform status is missing from version history")
    return match.group(0)


def promote_home(text: str) -> str:
    previous = release_block(text, "2.0", "section")
    candidate = release_block(text, "2.1", "section")
    published = release_block(text, PUBLIC_VERSION, "section")
    if published and "current-release" in published.group(0):
        return text
    if not previous or not candidate:
        raise RuntimeError("Expected 2.0 and 2.1 homepage release blocks")

    promoted = candidate.group(0)
    promoted = promoted.replace(
        "section next-release v21-preview", "section v21-preview current-release"
    )
    promoted = promoted.replace('data-release-version="2.1"', f'data-release-version="{PUBLIC_VERSION}"')
    promoted = promoted.replace('id="version-2-1-preview"', 'id="versions"')
    promoted = re.sub(
        r'<p class="kicker">.*?</p>',
        f'<p class="kicker">{home_status(previous.group(0))}</p>',
        promoted,
        count=1,
        flags=re.DOTALL,
    )
    text = text[: candidate.start()] + promoted + text[candidate.end() :]
    previous = release_block(text, "2.0", "section")
    if previous:
        text = text[: previous.start()] + text[previous.end() :]
    return text


def promote_readme(text: str) -> str:
    previous = release_block(text, "2.0", "article")
    candidate = release_block(text, "2.1", "article")
    published = release_block(text, PUBLIC_VERSION, "article")
    if published and "release-upcoming" not in published.group(0):
        return text
    if not previous or not candidate:
        raise RuntimeError("Expected 2.0 and 2.1 version-history cards")

    status = readme_status(previous.group(0))
    promoted = candidate.group(0).replace(
        "release-card release-preview release-upcoming v21-release-card",
        "release-card v21-release-card",
    )
    promoted = promoted.replace('data-release-version="2.1"', f'data-release-version="{PUBLIC_VERSION}"')
    promoted = promoted.replace('<span class="version-pill">v2.1</span>', '<span class="version-pill">v2.1.1</span>')
    promoted = re.sub(
        r'<p class="release-platform-summary">.*?</p>',
        status,
        promoted,
        count=1,
        flags=re.DOTALL,
    )
    historical = re.sub(
        r'<p class="release-platform-summary">.*?</p>',
        "",
        previous.group(0),
        count=1,
        flags=re.DOTALL,
    )
    text = text[: candidate.start()] + promoted + text[candidate.end() :]
    previous = release_block(text, "2.0", "article")
    if previous:
        text = text[: previous.start()] + historical + text[previous.end() :]
    return text


def remove_screenshot_announcement(text: str) -> str:
    candidate = release_block(text, "2.1", "section")
    if candidate:
        text = text[: candidate.start()] + text[candidate.end() :]
    text = text.replace('data-release-gallery="2.0"', f'data-release-gallery="{PUBLIC_VERSION}"')
    return text


def update_page(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    relative = path.relative_to(ROOT)
    kind = "/".join(relative.parts[-2:])

    if relative.name == "index.html" and relative.parent.name not in {
        "readme", "screenshots", "support", "privacy", "mac-app",
        "random-vinyl-record-picker", "choose-vinyl-record",
        "manage-vinyl-collection", "contest", "press",
    } and ('data-release-version="2.1"' in text or f'data-release-version="{PUBLIC_VERSION}"' in text):
        text = promote_home(text)
    elif kind == "readme/index.html" and ('data-release-version="2.1"' in text or f'data-release-version="{PUBLIC_VERSION}"' in text):
        text = promote_readme(text)
    elif kind == "screenshots/index.html":
        text = remove_screenshot_announcement(text)

    text = re.sub(r'"softwareVersion":"[^"]+"', f'"softwareVersion":"{PUBLIC_VERSION}"', text)
    text = re.sub(r'"dateModified":"[^"]+"', f'"dateModified":"{RELEASE_DATE}"', text)
    text = re.sub(r'Record Picker v2\.0</span>', f'Record Picker v{PUBLIC_VERSION}</span>', text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def update_state() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state["current_release"] = {
        "version": PUBLIC_VERSION,
        "platform_versions": {
            "iphone": "2.1.1",
            "ipad": "2.1.1",
            "watch": "2.1.1",
            "mac": "2.1",
        },
        "platforms": {
            "iphone": "available",
            "ipad": "available",
            "watch": "available",
            "mac": "available",
        },
        "required_platforms_for_full_release": ["iphone", "ipad", "mac", "watch"],
    }
    state["next_release"] = None
    releases = state.setdefault("historical_releases", [])
    if "2.0" not in releases:
        releases.insert(0, "2.0")
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    update_state()
    changed = sum(update_page(path) for path in sorted(ROOT.rglob("*.html")))
    print(f"Published Record Picker {PUBLIC_VERSION} state on {changed} HTML pages.")


if __name__ == "__main__":
    main()
