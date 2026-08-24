#!/usr/bin/env python3
"""Add the reviewed Windows and Android roadmap status to every homepage."""

from __future__ import annotations

from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
STRUCTURED_RELEASE_DATE = "2026-08-22"

STATUS = {
    "ar": ("قريبًا", "قيد التطوير"),
    "ca": ("Properament", "En desenvolupament"),
    "da": ("Kommer snart", "Under udvikling"),
    "de": ("Demnächst", "In Entwicklung"),
    "el": ("Σύντομα διαθέσιμο", "Υπό ανάπτυξη"),
    "en-au": ("Coming soon", "In development"),
    "en-ca": ("Coming soon", "In development"),
    "en-gb": ("Coming soon", "In development"),
    "en-us": ("Coming soon", "In development"),
    "es-es": ("Próximamente", "En desarrollo"),
    "es-mx": ("Próximamente", "En desarrollo"),
    "fi": ("Tulossa pian", "Kehitteillä"),
    "fr": ("Bientôt disponible", "En développement"),
    "fr-ca": ("Bientôt disponible", "En développement"),
    "he": ("בקרוב", "בפיתוח"),
    "hi": ("जल्द आ रहा है", "विकासाधीन"),
    "id": ("Segera hadir", "Dalam pengembangan"),
    "it": ("Prossimamente", "In sviluppo"),
    "ja": ("近日公開", "開発中"),
    "ko": ("출시 예정", "개발 중"),
    "nb": ("Kommer snart", "Under utvikling"),
    "nl": ("Binnenkort", "In ontwikkeling"),
    "pl": ("Wkrótce", "W przygotowaniu"),
    "pt-br": ("Em breve", "Em desenvolvimento"),
    "pt-pt": ("Em breve", "Em desenvolvimento"),
    "ru": ("Скоро", "В разработке"),
    "sv": ("Kommer snart", "Under utveckling"),
    "th": ("เร็ว ๆ นี้", "อยู่ระหว่างการพัฒนา"),
    "tr": ("Yakında", "Geliştirme aşamasında"),
    "vi": ("Sắp ra mắt", "Đang phát triển"),
    "zh-hans": ("即将推出", "开发中"),
    "zh-hant": ("即將推出", "開發中"),
}

BLOCK = re.compile(
    r'<section class="platform-roadmap" aria-label="[^"]*" data-platform-roadmap>.*?</section>',
    flags=re.DOTALL,
)
FACTS = re.compile(r'(<section class="facts-band">.*?</section>)', flags=re.DOTALL)


def roadmap_block(coming_soon: str, in_development: str) -> str:
    label = f"Windows: {coming_soon}; Android: {in_development}"
    return (
        f'<section class="platform-roadmap" aria-label="{escape(label)}" data-platform-roadmap>'
        '<div><strong>Windows</strong>'
        f'<span class="platform-status coming-soon">{escape(coming_soon)}</span></div>'
        '<div><strong>Android</strong>'
        f'<span class="platform-status in-development">{escape(in_development)}</span></div>'
        '</section>'
    )


def update_home(path: Path, locale: str) -> bool:
    text = path.read_text(encoding="utf-8")
    stylesheet = "platform-roadmap.css" if path.parent == ROOT else "../platform-roadmap.css"
    stylesheet_link = f'<link rel="stylesheet" href="{stylesheet}?v=20260824-platforms">'
    if stylesheet_link not in text:
        text = text.replace("</head>", stylesheet_link + "</head>", 1)
    block = roadmap_block(*STATUS[locale])
    if BLOCK.search(text):
        updated = BLOCK.sub(block, text, count=1)
    else:
        match = FACTS.search(text)
        if not match:
            raise RuntimeError(f"Missing facts band in {path}")
        updated = text[:match.end()] + block + text[match.end():]
    updated = re.sub(
        r'("dateModified":")[^"]+(\")',
        rf'\g<1>{STRUCTURED_RELEASE_DATE}\g<2>',
        updated,
    )
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = update_home(ROOT / "index.html", "en-us")
    for locale in STATUS:
        changed += update_home(ROOT / locale / "index.html", locale)
    print(f"Updated {changed} homepages with Windows and Android roadmap status.")


if __name__ == "__main__":
    main()
