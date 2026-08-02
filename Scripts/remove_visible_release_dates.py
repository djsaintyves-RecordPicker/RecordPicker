#!/usr/bin/env python3
"""Replace visible release dates with timeless localized availability labels.

The current preview keeps its existing "coming soon" wording. Every published
release reuses the localized status already present on the 1.6 card. The script
is idempotent and intentionally ignores privacy-policy and technical dates.
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
    r'(?P<prefix><div><h3>.*?</h3>)<p>.*?</p>',
    flags=re.DOTALL,
)


def localized_roots() -> list[Path]:
    roots = [ROOT]
    roots.extend(
        path for path in sorted(ROOT.iterdir())
        if path.is_dir() and path.name in LOCALE_DIRECTORIES
    )
    return roots


def release_cards(text: str) -> list[re.Match[str]]:
    return list(RELEASE_CARD_PATTERN.finditer(text))


def version_and_status(card: str, path: Path) -> tuple[str, str]:
    version_match = VERSION_PATTERN.search(card)
    status_match = STATUS_PATTERN.search(card)
    if not version_match or not status_match:
        raise RuntimeError(f"Malformed release card in {path}")
    current_status = re.search(
        r'<p>(.*?)</p>', status_match.group(0), flags=re.DOTALL
    )
    if not current_status:
        raise RuntimeError(f"Missing release status in {path}")
    return version_match.group("version"), current_status.group(1)


def published_status(text: str, path: Path) -> str:
    for card_match in release_cards(text):
        version, status = version_and_status(card_match.group(0), path)
        if version == "v1.6":
            return status
    raise RuntimeError(f"No localized published status found in {path}")


def remove_dates(text: str, path: Path) -> str:
    available_now = published_status(text, path)

    def replace_card(match: re.Match[str]) -> str:
        card = match.group(0)
        version, _ = version_and_status(card, path)
        if version == "v1.8":
            return card
        updated, replacements = STATUS_PATTERN.subn(
            rf'\g<prefix><p>{available_now}</p>',
            card,
            count=1,
        )
        if replacements != 1:
            raise RuntimeError(f"Could not update {version} in {path}")
        return updated

    return RELEASE_CARD_PATTERN.sub(replace_card, text)


def visible_release_pages() -> list[Path]:
    pages: list[Path] = []
    for root in localized_roots():
        pages.extend([root / "index.html", root / "readme" / "index.html"])
    return pages


def validate_page(text: str, path: Path) -> None:
    available_now = published_status(text, path)
    for card_match in release_cards(text):
        version, status = version_and_status(card_match.group(0), path)
        if version == "v1.8":
            continue
        if status != available_now:
            raise RuntimeError(
                f"Unexpected status for {version} in {path}: {status!r}"
            )


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
        f"Removed visible dates from {changed} page(s); "
        f"validated {len(pages)} localized release histories."
    )


if __name__ == "__main__":
    main()
