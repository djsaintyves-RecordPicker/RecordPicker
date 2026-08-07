#!/usr/bin/env python3
"""Enforce the public release-status rule across every localized history.

Only the newest release card may display availability. In the current mixed
rollout, 1.9 says that macOS is available and that iPhone, iPad and Apple Watch
are coming soon. Historical releases display no availability or release date.
The script is idempotent and intentionally ignores policy and technical dates.
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LOCALE_DIRECTORIES = {
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "tr", "zh-hans",
    "zh-hant",
}

RELEASE_CARD_PATTERN = re.compile(
    r'<article class="release-card(?P<classes>[^"]*)"(?P<attributes>[^>]*)>'
    r'(?P<body>.*?)</article>',
    flags=re.DOTALL,
)
VERSION_PATTERN = re.compile(
    r'<span class="version-pill">(?P<version>v[^<]+)</span>'
)
STATUS_PATTERN = re.compile(
    r'(?P<prefix><div><h3>.*?</h3>)<p(?: class="[^"]*")?>.*?</p>',
    flags=re.DOTALL,
)
CURRENT_VERSION = "v1.9"


def localized_roots() -> list[Path]:
    roots = [ROOT]
    roots.extend(
        path for path in sorted(ROOT.iterdir())
        if path.is_dir() and path.name in LOCALE_DIRECTORIES
    )
    return roots


def release_cards(text: str) -> list[re.Match[str]]:
    return list(RELEASE_CARD_PATTERN.finditer(text))


def card_version(card: str, path: Path) -> str:
    version_match = VERSION_PATTERN.search(card)
    if not version_match:
        raise RuntimeError(f"Malformed release card in {path}")
    return version_match.group("version")


def remove_dates(text: str, path: Path) -> str:
    def replace_card(match: re.Match[str]) -> str:
        card = match.group(0)
        version = card_version(card, path)
        if version == CURRENT_VERSION:
            return card
        return STATUS_PATTERN.sub(r'\g<prefix>', card, count=1)

    return RELEASE_CARD_PATTERN.sub(replace_card, text)


def visible_release_pages() -> list[Path]:
    return [root / "readme" / "index.html" for root in localized_roots()]


def validate_page(text: str, path: Path) -> None:
    found_current = False
    for card_match in release_cards(text):
        card = card_match.group(0)
        version = card_version(card, path)
        status = STATUS_PATTERN.search(card)
        if version == CURRENT_VERSION:
            found_current = True
            if not status or 'release-platform-summary' not in status.group(0):
                raise RuntimeError(f"Missing 1.9 platform status in {path}")
        elif status:
            raise RuntimeError(
                f"Historical release {version} still has a status in {path}"
            )
    if not found_current:
        raise RuntimeError(f"No {CURRENT_VERSION} release card in {path}")


def main() -> None:
    pages = visible_release_pages()
    changed = 0
    for page in pages:
        text = page.read_text(encoding="utf-8")
        updated = remove_dates(text, page)
        validate_page(updated, page)
        if updated != text:
            page.write_text(updated, encoding="utf-8")
            changed += 1

    print(
        f"Normalized release status on {changed} page(s); "
        f"validated {len(pages)} localized histories."
    )


if __name__ == "__main__":
    main()
