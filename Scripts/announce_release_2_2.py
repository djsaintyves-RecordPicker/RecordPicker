#!/usr/bin/env python3
"""Publish Record Picker 2.2 on Mac while keeping iPhone and iPad upcoming."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "data" / "release-notes" / "2.2"
ANNOUNCEMENT_DATE = "2026-08-19"

LOCALE_NOTE = {
    "ar": "ar-SA", "ca": "ca", "da": "da", "de": "de-DE",
    "el": "el", "en-au": "en-AU", "en-ca": "en-CA", "en-gb": "en-GB",
    "en-us": "en-US", "es-es": "es-ES", "es-mx": "es-MX", "fi": "fi",
    "fr": "fr-FR", "fr-ca": "fr-CA", "he": "he", "hi": "hi", "id": "id",
    "it": "it", "ja": "ja", "ko": "ko", "nb": "no", "nl": "nl-NL",
    "pl": "pl", "pt-br": "pt-BR", "pt-pt": "pt-PT", "ru": "ru",
    "sv": "sv", "th": "th", "tr": "tr", "vi": "vi",
    "zh-hans": "zh-Hans", "zh-hant": "zh-Hant",
}

HTML_LANG_NOTE = {
    "ar": "ar-SA", "ca": "ca", "da": "da", "de-DE": "de-DE",
    "el": "el", "en": "en-US", "en-AU": "en-AU", "en-CA": "en-CA",
    "en-GB": "en-GB", "en-US": "en-US", "es-ES": "es-ES",
    "es-MX": "es-MX", "fi": "fi", "fr-FR": "fr-FR", "fr-CA": "fr-CA",
    "he": "he", "hi": "hi", "id": "id", "it": "it", "ja": "ja",
    "ko": "ko", "nb": "no", "nl-NL": "nl-NL", "pl": "pl",
    "pt-BR": "pt-BR", "pt-PT": "pt-PT", "ru": "ru", "sv": "sv",
    "th": "th", "tr": "tr", "vi": "vi", "zh-Hans": "zh-Hans",
    "zh-Hant": "zh-Hant",
}

PARTIAL_STATUS = {
    "ar-SA": "متوفر الآن على Mac · قريبًا على iPhone وiPad",
    "ca": "Disponible ara al Mac · Properament a l’iPhone i l’iPad",
    "da": "Tilgængelig nu på Mac · Kommer snart til iPhone og iPad",
    "de-DE": "Jetzt auf dem Mac verfügbar · Demnächst auf iPhone und iPad",
    "el": "Διαθέσιμο τώρα σε Mac · Σύντομα σε iPhone και iPad",
    "en-AU": "Available now on Mac · Coming soon on iPhone and iPad",
    "en-CA": "Available now on Mac · Coming soon on iPhone and iPad",
    "en-GB": "Available now on Mac · Coming soon on iPhone and iPad",
    "en-US": "Available now on Mac · Coming soon on iPhone and iPad",
    "es-ES": "Disponible ya en Mac · Próximamente en iPhone y iPad",
    "es-MX": "Disponible ya en Mac · Próximamente en iPhone y iPad",
    "fi": "Nyt saatavilla Macille · Tulossa pian iPhonelle ja iPadille",
    "fr-FR": "Disponible dès maintenant sur Mac · Bientôt sur iPhone et iPad",
    "fr-CA": "Disponible dès maintenant sur Mac · Bientôt sur iPhone et iPad",
    "he": "זמין כעת ב‑Mac · בקרוב ב‑iPhone וב‑iPad",
    "hi": "Mac पर अभी उपलब्ध · iPhone और iPad पर जल्द आ रहा है",
    "id": "Tersedia sekarang di Mac · Segera hadir di iPhone dan iPad",
    "it": "Ora disponibile su Mac · Prossimamente su iPhone e iPad",
    "ja": "Macで配信中 · iPhoneとiPadは近日公開",
    "ko": "Mac에서 지금 이용 가능 · iPhone 및 iPad 출시 예정",
    "no": "Tilgjengelig nå på Mac · Kommer snart til iPhone og iPad",
    "nl-NL": "Nu beschikbaar op Mac · Binnenkort op iPhone en iPad",
    "pl": "Dostępna teraz na Macu · Wkrótce na iPhonie i iPadzie",
    "pt-BR": "Já disponível no Mac · Em breve no iPhone e iPad",
    "pt-PT": "Já disponível no Mac · Em breve no iPhone e no iPad",
    "ru": "Уже доступно на Mac · Скоро на iPhone и iPad",
    "sv": "Tillgänglig nu på Mac · Kommer snart till iPhone och iPad",
    "th": "พร้อมใช้งานแล้วบน Mac · เร็ว ๆ นี้บน iPhone และ iPad",
    "tr": "Şimdi Mac’te · Yakında iPhone ve iPad’de",
    "vi": "Hiện đã có trên Mac · Sắp ra mắt trên iPhone và iPad",
    "zh-Hans": "Mac 版现已推出 · iPhone 和 iPad 版即将推出",
    "zh-Hant": "Mac 版現已推出 · iPhone 和 iPad 版即將推出",
}

BLOCK = re.compile(
    r'<(?P<tag>section|article)\b(?P<attrs>[^>]*\bdata-release-version="2\.2"[^>]*)>'
    r'.*?</(?P=tag)>',
    flags=re.DOTALL,
)


@dataclass(frozen=True)
class ReleaseCopy:
    headline: str
    bullets: tuple[str, ...]


def parse_note(locale: str) -> ReleaseCopy:
    path = NOTES / f"{locale}.txt"
    if not path.exists():
        raise RuntimeError(f"Missing reviewed 2.2 release note: {path}")
    paragraphs = [part.strip() for part in path.read_text(encoding="utf-8").split("\n\n") if part.strip()]
    if len(paragraphs) != 2:
        raise RuntimeError(f"Unexpected 2.2 note structure: {path}")
    lines = [line.strip() for line in paragraphs[1].splitlines() if line.strip()]
    if len(lines) != 5 or any(not line.startswith("•") for line in lines):
        raise RuntimeError(f"Expected five 2.2 points in {path}")
    return ReleaseCopy(
        headline=paragraphs[0],
        bullets=tuple(line.removeprefix("•").strip() for line in lines),
    )


def page_locale(path: Path, fallback: str) -> str:
    if path.parent == ROOT or path.parent.parent == ROOT:
        text = path.read_text(encoding="utf-8")
        match = re.search(r'<html\s+lang="([^"]+)"', text)
        if match and match.group(1) in HTML_LANG_NOTE:
            return HTML_LANG_NOTE[match.group(1)]
    return fallback


def home_section(copy: ReleaseCopy, status: str) -> str:
    bullets = "".join(f"<li>{escape(point)}</li>" for point in copy.bullets)
    return (
        '<section class="section next-release v22-preview" id="version-2-2-preview" '
        'data-release-version="2.2"><div class="section-head">'
        f'<p class="kicker">{escape(status)}</p><h2>Record Picker 2.2</h2>'
        f'<p class="lead">{escape(copy.headline)}</p></div>'
        f'<div class="v20-preview-panel"><ul>{bullets}</ul></div></section>'
    )


def history_card(copy: ReleaseCopy, status: str) -> str:
    bullets = "".join(f"<li>{escape(point)}</li>" for point in copy.bullets)
    return (
        '<article class="release-card release-preview release-partial v22-release-card" '
        'data-release-version="2.2"><div class="release-head">'
        '<span class="version-pill">v2.2</span><div>'
        f'<h3>{escape(copy.headline)}</h3>'
        f'<p class="release-platform-summary"><strong>{escape(status)}</strong></p>'
        f'</div></div><ul>{bullets}</ul></article>'
    )


def screenshot_marker(copy: ReleaseCopy, status: str) -> str:
    return (
        '<section class="media-section next-release v22-gallery-marker" '
        'data-release-version="2.2"><div class="section-head">'
        f'<p class="kicker">{escape(status)}</p><h2>Record Picker 2.2</h2>'
        f'<p class="lead">{escape(copy.headline)}</p></div></section>'
    )


def insert_or_replace(text: str, block: str, anchor: str, path: Path) -> str:
    if BLOCK.search(text):
        return BLOCK.sub(block, text, count=1)
    position = text.find(anchor)
    if position < 0:
        raise RuntimeError(f"Could not find current-release anchor in {path}")
    return text[:position] + block + text[position:]


def update_page(path: Path, block: str, anchor: str) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = insert_or_replace(text, block, anchor, path)
    if 'data-release-version="2.2"' in updated:
        updated = re.sub(
            r'("dateModified":")[^"]+(\")',
            rf'\g<1>{ANNOUNCEMENT_DATE}\g<2>',
            updated,
        )
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def update_release_state() -> None:
    path = ROOT / "data" / "release-state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["next_release"] = {
        "version": "2.2",
        "platforms": {
            "iphone": "coming_soon",
            "ipad": "coming_soon",
            "mac": "available",
        },
    }
    state["current_release"]["platform_versions"]["mac"] = "2.2"
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_sitemaps() -> None:
    for name in ("sitemap.xml", "sitemap-media.xml"):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        updated = re.sub(
            r"<lastmod>[^<]+</lastmod>",
            f"<lastmod>{ANNOUNCEMENT_DATE}</lastmod>",
            text,
        )
        path.write_text(updated, encoding="utf-8")


def main() -> None:
    changed = 0
    for directory, fallback_locale in {"": "en-US", **LOCALE_NOTE}.items():
        root = ROOT / directory if directory else ROOT
        pages = (
            (root / "index.html", home_section, '<section class="section v21-preview current-release"'),
            (root / "readme" / "index.html", history_card, '<article class="release-card v21-release-card"'),
            (root / "screenshots" / "index.html", screenshot_marker, '<section class="media-section v20-screenshot-gallery"'),
        )
        for path, renderer, anchor in pages:
            locale = page_locale(path, fallback_locale)
            changed += update_page(path, renderer(parse_note(locale), PARTIAL_STATUS[locale]), anchor)
    update_release_state()
    update_sitemaps()
    print(f"Announced Record Picker 2.2 on {changed} localized pages.")
    print("Record Picker 2.2 is available on Mac; iPhone and iPad remain coming soon.")


if __name__ == "__main__":
    main()
