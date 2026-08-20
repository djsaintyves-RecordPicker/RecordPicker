#!/usr/bin/env python3
"""Publish Record Picker 2.2 and announce the reviewed 2.3 direction."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re

from announce_release_2_1 import COMING_SOON, LOCALE_NOTE


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT.parent / "RecordPicker"
APP_NOTES = APP_ROOT / "AppStoreReleaseNotes" / "2.2"
STATE_PATH = ROOT / "data" / "release-state.json"
PUBLICATION_DATE = "2026-08-20"

APP_LOCALE = {
    "ar-SA": "ar", "ca": "ca", "da": "da", "de-DE": "de", "el": "el",
    "en-AU": "en-AU", "en-CA": "en-CA", "en-GB": "en-GB", "en-US": "en",
    "es-ES": "es", "es-MX": "es-MX", "fi": "fi", "fr-FR": "fr",
    "fr-CA": "fr-CA", "he": "he", "hi": "hi", "id": "id", "it": "it",
    "ja": "ja", "ko": "ko", "no": "nb", "nl-NL": "nl", "pl": "pl",
    "pt-BR": "pt-BR", "pt-PT": "pt-PT", "ru": "ru", "sv": "sv",
    "th": "th", "tr": "tr", "vi": "vi", "zh-Hans": "zh-Hans",
    "zh-Hant": "zh-Hant",
}

STRINGS_ENTRY = re.compile(r'^"((?:\\.|[^"\\])*)"\s*=\s*"((?:\\.|[^"\\])*)";$')


@dataclass(frozen=True)
class ReleaseCopy:
    headline: str
    bullets: tuple[str, ...]


def decode_quoted(value: str) -> str:
    return json.loads(f'"{value}"')


def app_strings(note_locale: str) -> dict[str, str]:
    locale = APP_LOCALE[note_locale]
    path = APP_ROOT / "RecordPicker" / f"{locale}.lproj" / "Localizable.strings"
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = STRINGS_ENTRY.match(line.strip())
        if match:
            entries[decode_quoted(match.group(1))] = decode_quoted(match.group(2))
    return entries


def release_2_2_copy(note_locale: str) -> ReleaseCopy:
    path = APP_NOTES / f"{note_locale}.txt"
    paragraphs = [part.strip() for part in path.read_text(encoding="utf-8").split("\n\n") if part.strip()]
    if len(paragraphs) < 2:
        raise RuntimeError(f"Unexpected 2.2 release note structure: {path}")
    bullets = tuple(
        line.removeprefix("•").strip()
        for line in paragraphs[1].splitlines()
        if line.strip().startswith("•")
    )
    if len(bullets) != 5:
        raise RuntimeError(f"Expected five 2.2 release points in {path}")
    return ReleaseCopy(paragraphs[0], bullets)


def release_2_3_copy(note_locale: str) -> ReleaseCopy:
    strings = app_strings(note_locale)

    def localized(key: str) -> str:
        value = strings.get(key)
        if not value:
            raise RuntimeError(f"Missing 2.3 app localization for {note_locale}: {key}")
        return value

    return ReleaseCopy(
        localized("Lance un nouveau tirage dans Record Picker sur l’Apple Watch."),
        (
            " · ".join((localized("Tirer un disque"), "Random Pick", localized("Favoris"))),
            " · ".join((
                localized("Rarement écoutés"), localized("Ajouts récents"),
                localized("Classique"), localized("Soirée calme"), localized("Énergique"),
            )),
            " · ".join((
                localized("Hors ligne"), localized("Synchronisation différée"),
                localized("Synchronisation en cours"), localized("À jour"),
            )),
            " · ".join((
                localized("Lecture sur l’Apple Watch"), localized("Lecture lancée"),
                localized("Écouté"),
            )),
            localized(
                "Today’s Pick links reliable music news to a record you own and explains why it matters today."
            ),
        ),
    )


def release_block(text: str, version: str, tag: str) -> re.Match[str] | None:
    return re.search(
        rf'<{tag}\b[^>]*data-release-version="{re.escape(version)}"[^>]*>.*?</{tag}>',
        text,
        flags=re.DOTALL,
    )


def bullets(copy: ReleaseCopy) -> str:
    return "".join(f"<li>{escape(point)}</li>" for point in copy.bullets)


def home_section(version: str, copy: ReleaseCopy, status: str, current: bool) -> str:
    classes = f"section v{version.replace('.', '')}-preview"
    if current:
        classes += " current-release"
    else:
        classes += " next-release"
    section_id = f'version-{version.replace(".", "-")}-preview' if current else "versions"
    return (
        f'<section class="{classes}" id="{section_id}" '
        f'data-release-version="{version}"><div class="section-head">'
        f'<p class="kicker">{escape(status)}</p><h2>Record Picker {version}</h2>'
        f'<p class="lead">{escape(copy.headline)}</p></div>'
        f'<div class="v20-preview-panel"><ul>{bullets(copy)}</ul></div></section>'
    )


def history_card(
    version: str,
    copy: ReleaseCopy,
    status_html: str | None,
    upcoming: bool,
) -> str:
    classes = "release-card"
    if upcoming:
        classes += " release-preview release-upcoming"
    classes += f" v{version.replace('.', '')}-release-card"
    status = status_html or ""
    return (
        f'<article class="{classes}" data-release-version="{version}">'
        f'<div class="release-head"><span class="version-pill">v{version}</span><div>'
        f'<h3>{escape(copy.headline)}</h3>{status}</div></div>'
        f'<ul>{bullets(copy)}</ul></article>'
    )


def screenshot_marker(copy: ReleaseCopy, status: str) -> str:
    return (
        '<section class="media-section next-release v23-gallery-marker" '
        'data-release-version="2.3"><div class="section-head">'
        f'<p class="kicker">{escape(status)}</p><h2>Record Picker 2.3</h2>'
        f'<p class="lead">{escape(copy.headline)}</p></div></section>'
    )


def promote_gallery(text: str) -> str:
    gallery = re.search(
        r'<section\b[^>]*data-release-gallery="2\.0"[^>]*>.*?</section>',
        text,
        flags=re.DOTALL,
    )
    if not gallery:
        return text
    promoted = gallery.group(0).replace('data-release-gallery="2.0"', 'data-release-gallery="2.2"')
    promoted = promoted.replace("<h2>Record Picker 2.0</h2>", "<h2>Record Picker 2.2</h2>")
    return text[:gallery.start()] + promoted + text[gallery.end():]


def update_release_pages(root: Path, note_locale: str) -> int:
    changed = 0
    copy_22 = release_2_2_copy(note_locale)
    copy_23 = release_2_3_copy(note_locale)
    status_23 = COMING_SOON[note_locale]

    home_path = root / "index.html"
    text = home_path.read_text(encoding="utf-8")
    original = text
    if not (release_block(text, "2.2", "section") and release_block(text, "2.3", "section")):
        previous_next = release_block(text, "2.1", "section")
        previous_current = release_block(text, "2.0", "section")
        if not previous_next or not previous_current:
            raise RuntimeError(f"Expected 2.1 and 2.0 home blocks in {home_path}")
        status_match = re.search(r'<p class="kicker">(.*?)</p>', previous_current.group(0), re.DOTALL)
        if not status_match:
            raise RuntimeError(f"Missing current-release status in {home_path}")
        text = text[:previous_next.start()] + home_section("2.3", copy_23, status_23, False) + text[previous_next.end():]
        previous_current = release_block(text, "2.0", "section")
        assert previous_current
        text = text[:previous_current.start()] + home_section("2.2", copy_22, status_match.group(1), True) + text[previous_current.end():]
    text = text.replace('id="version-2-3-preview"', 'id="versions"')
    text = text.replace("<strong>Record Picker 2.0</strong>", "<strong>Record Picker 2.2</strong>")
    text = text.replace("<h2>Record Picker 2.0</h2>", "<h2>Record Picker 2.2</h2>")
    if text != original:
        home_path.write_text(text, encoding="utf-8")
        changed += 1

    history_path = root / "readme" / "index.html"
    text = history_path.read_text(encoding="utf-8")
    original = text
    if not (release_block(text, "2.2", "article") and release_block(text, "2.3", "article")):
        old_21 = release_block(text, "2.1", "article")
        current_20 = release_block(text, "2.0", "article")
        if not old_21 or not current_20:
            raise RuntimeError(f"Expected 2.1 and 2.0 history cards in {history_path}")
        status_match = re.search(
            r'<p class="release-platform-summary">.*?</p>', current_20.group(0), re.DOTALL
        )
        if not status_match:
            raise RuntimeError(f"Missing platform summary in {history_path}")
        historical_21 = re.sub(
            r'\s*<p class="release-platform-summary">.*?</p>', "", old_21.group(0),
            count=1, flags=re.DOTALL,
        ).replace(" release-preview release-upcoming", "")
        replacement = (
            history_card("2.3", copy_23, f'<p class="release-platform-summary"><strong>{escape(status_23)}</strong></p>', True)
            + history_card("2.2", copy_22, status_match.group(0), False)
            + historical_21
        )
        text = text[:old_21.start()] + replacement + text[old_21.end():]
    for historical_version in ("2.1", "2.0"):
        historical = release_block(text, historical_version, "article")
        if historical:
            cleaned = re.sub(
                r'\s*<p class="release-platform-summary">.*?</p>', "", historical.group(0),
                count=1, flags=re.DOTALL,
            ).replace(" release-preview release-upcoming", "")
            text = text[:historical.start()] + cleaned + text[historical.end():]
    if text != original:
        history_path.write_text(text, encoding="utf-8")
        changed += 1

    screenshots_path = root / "screenshots" / "index.html"
    text = screenshots_path.read_text(encoding="utf-8")
    original = text
    if not release_block(text, "2.3", "section"):
        old_marker = release_block(text, "2.1", "section")
        if not old_marker:
            raise RuntimeError(f"Expected 2.1 screenshot marker in {screenshots_path}")
        text = text[:old_marker.start()] + screenshot_marker(copy_23, status_23) + text[old_marker.end():]
    text = promote_gallery(text)
    if text != original:
        screenshots_path.write_text(text, encoding="utf-8")
        changed += 1

    return changed


def update_shared_metadata(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    text = re.sub(r'("softwareVersion":")2\.[01](")', r'\g<1>2.2\2', text)
    text = re.sub(r'("dateModified":")[^"]+(")', rf'\g<1>{PUBLICATION_DATE}\2', text)
    text = text.replace("Record Picker v2.0</span>", "Record Picker v2.2</span>")
    text = re.sub(
        r'(<p class="doc-meta">.*?)Record Picker v?2\.0(.*?</p>)',
        r'\1Record Picker v2.2\2', text, flags=re.DOTALL,
    )
    text = re.sub(
        r'(<p class="glass-pill eyebrow">.*?)macOS 2\.0(.*?</p>)',
        r'\1macOS 2.2\2', text, flags=re.DOTALL,
    )
    text = re.sub(
        r'(<p class="eyebrow">.*?)Record Picker 2\.0(.*?</p>)',
        r'\1Record Picker 2.2\2', text, flags=re.DOTALL,
    )
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def update_state() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state["publication_phase"] = "full"
    state["current_release"] = {
        "version": "2.2",
        "platforms": {
            "iphone": "available", "ipad": "available",
            "mac": "available", "watch": "available",
        },
        "required_platforms_for_full_release": ["iphone", "ipad", "mac", "watch"],
    }
    state["next_release"] = {
        "version": "2.3",
        "platforms": {
            "iphone": "coming_soon", "ipad": "coming_soon",
            "mac": "coming_soon", "watch": "coming_soon",
        },
    }
    state["historical_releases"] = [
        "2.1", "2.0", "1.9", "1.8", "1.6", "1.5", "1.4", "1.3", "1.2", "1.1"
    ]
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if not APP_NOTES.is_dir():
        raise RuntimeError(f"Reviewed 2.2 release notes not found: {APP_NOTES}")
    changed = 0
    for directory, note_locale in LOCALE_NOTE.items():
        root = ROOT / directory if directory else ROOT
        changed += update_release_pages(root, note_locale)
    changed += sum(update_shared_metadata(path) for path in sorted(ROOT.rglob("*.html")))
    update_state()
    print(f"Published Record Picker 2.2 and announced 2.3 across {changed} page updates.")


if __name__ == "__main__":
    main()
