#!/usr/bin/env python3
"""Prepare every localized home page for the Record Picker 1.8 preview.

The published version remains untouched in App Store facts and structured
metadata. This script only replaces the skipped 1.7 preview and adds the 1.8
visual preview. It is safe to run more than once.
"""

from __future__ import annotations

from html import escape, unescape
from pathlib import Path
import re

from site_translation_data import RELEASE_18_OVERRIDES


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT.parent / "RecordPicker"
NOTES_ROOT = APP_ROOT / "AppStoreReleaseNotes" / "1.8"

LOCALE_DIRECTORIES = {
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "tr", "zh-hans",
    "zh-hant",
}

NOTE_LOCALE_BY_HTML_LANGUAGE = {
    "ar": "ar-SA", "de": "de-DE", "en-AU": "en-AU", "en-CA": "en-CA",
    "en-GB": "en-GB", "en-US": "en-US", "es-ES": "es-ES", "fi": "fi",
    "fr-FR": "fr-FR", "it": "it", "ja": "ja", "ko": "ko", "nb": "no",
    "nl": "nl-NL", "pl": "pl", "pt-BR": "pt-BR", "sv": "sv", "th": "th",
    "tr": "tr", "vi": "vi", "zh-Hans": "zh-Hans", "zh-Hant": "zh-Hant",
}

PREVIEW_LABELS = {
    "ar": ("قريبًا في الإصدار 1.8", "صحة المجموعة تصبح قابلة للتنفيذ"),
    "ca": ("Properament a la versió 1.8", "La salut de la col·lecció esdevé realment útil"),
    "da": ("Kommer i 1.8", "Samlingsstatus bliver konkret og handlingsklar"),
    "fr-FR": ("À venir en 1.8", "La qualité de la collection devient actionnable"),
    "fr-CA": ("À venir dans la 1.8", "La qualité de la collection devient actionnable"),
    "es-ES": ("Próximamente en la 1.8", "El estado de la colección pasa a la acción"),
    "el": ("Έρχεται στην 1.8", "Η υγεία της συλλογής γίνεται πραγματικά αξιοποιήσιμη"),
    "de": ("Demnächst in 1.8", "Sammlungsqualität, die wirklich weiterhilft"),
    "fi": ("Tulossa versiossa 1.8", "Kokoelman kunto muuttuu käytännön toimiksi"),
    "he": ("בקרוב בגרסה 1.8", "מצב האוסף הופך לתוכנית פעולה"),
    "hi": ("1.8 में जल्द आ रहा है", "कलेक्शन की स्थिति अब उपयोगी कार्रवाइयों में बदलेगी"),
    "id": ("Segera hadir di 1.8", "Kesehatan koleksi menjadi langkah nyata"),
    "it": ("In arrivo con la 1.8", "La qualità della collezione diventa operativa"),
    "nb": ("Kommer i 1.8", "Samlingsstatus blir konkret og handlingsklar"),
    "nl": ("Binnenkort in 1.8", "Collectiegezondheid wordt echt bruikbaar"),
    "pl": ("Już wkrótce w 1.8", "Stan kolekcji przekłada się na konkretne działania"),
    "pt-BR": ("Em breve na 1.8", "A qualidade da coleção se torna prática"),
    "pt-PT": ("Brevemente na 1.8", "A qualidade da coleção torna-se prática"),
    "ru": ("Скоро в версии 1.8", "Состояние коллекции становится планом действий"),
    "sv": ("Kommer i 1.8", "Samlingshälsa blir konkret och användbar"),
    "tr": ("1.8 ile yakında", "Koleksiyon sağlığı somut eylemlere dönüşüyor"),
    "zh-Hans": ("1.8 即将推出", "让收藏健康状况真正可操作"),
    "zh-Hant": ("1.8 即將推出", "讓收藏健康狀況真正可操作"),
    "ja": ("1.8で登場", "コレクションの状態を具体的な改善へ"),
    "ko": ("1.8에서 제공", "컬렉션 상태를 실제 개선으로"),
}

VISUAL_CAPTIONS = {
    "fr-FR": [
        "Qualité des données rassemble les corrections et les décisions qui demandent votre attention.",
        "Le bac permet de parcourir, filtrer et retrouver rapidement chaque disque de la collection.",
        "L’année de sortie originale reste prioritaire, sans perdre l’année de l’édition possédée.",
        "Sur Mac, la collection profite d’un grand écran clair pour la parcourir et la gérer.",
    ],
    "fr-CA": [
        "Qualité des données rassemble les corrections et les décisions qui demandent votre attention.",
        "Le bac permet de parcourir, filtrer et retrouver rapidement chaque disque de la collection.",
        "L’année de sortie originale reste prioritaire, sans perdre l’année de l’édition possédée.",
        "Sur Mac, la collection profite d’un grand écran clair pour la parcourir et la gérer.",
    ],
    "es-ES": [
        "Calidad de los datos reúne las correcciones y las decisiones que requieren tu atención.",
        "La caja permite explorar, filtrar y encontrar rápidamente cada disco de la colección.",
        "El año de lanzamiento original tiene prioridad sin perder el año de la edición que posees.",
        "En Mac, una vista amplia y clara facilita explorar y gestionar la colección.",
    ],
}

DEFAULT_VISUAL_CAPTIONS = [
    "Collection Health brings together fixes and decisions that need your attention.",
    "The record crate makes it easy to browse, filter and find every record.",
    "The original release year stays prominent without losing the year of your exact edition.",
    "On Mac, a clear large-screen view makes the collection easier to browse and manage.",
]

FALLBACK_INTRO = (
    "Record Picker 1.8 makes Collection Health proactive and actionable, "
    "while keeping every ambiguous decision under your control."
)

FALLBACK_BULLETS = [
    "Separates reliable automatic fixes from choices that need your decision, with source and confidence for every suggestion.",
    "Compares MusicBrainz and Discogs conflicts side by side, with a resumable repair queue, CSV report and undo.",
    "Adds a four-step guide to imports, data quality, Random Pick, Mood Pick and Free/Pro.",
    "Shows the original release year first while preserving the exact edition year.",
]


def release_copy(language: str) -> tuple[str, list[str]]:
    if language in RELEASE_18_OVERRIDES:
        return RELEASE_18_OVERRIDES[language]
    note_locale = NOTE_LOCALE_BY_HTML_LANGUAGE.get(language, "en-US")
    note_path = NOTES_ROOT / f"{note_locale}.txt"
    if not note_path.exists():
        note_path = NOTES_ROOT / "en-US.txt"
    if not note_path.exists():
        return FALLBACK_INTRO, FALLBACK_BULLETS
    lines = [line.strip() for line in note_path.read_text(encoding="utf-8").splitlines()]
    intro = next((line for line in lines if line and not line.startswith("•")), FALLBACK_INTRO)
    bullets = [line.removeprefix("•").strip() for line in lines if line.startswith("•")]
    return intro, bullets or FALLBACK_BULLETS


def update_preview_card(text: str, path: Path, bullets: list[str]) -> str:
    card_match = re.search(
        r'<article class="release-card[^"]*"[^>]*data-release-version="1\.8".*?</article>',
        text,
        flags=re.DOTALL,
    )
    if not card_match:
        card_match = re.search(
            r'<article class="release-card release-preview">.*?</article>',
            text,
            flags=re.DOTALL,
        )
    if not card_match:
        raise RuntimeError(f"No release preview found in {path}")
    card = card_match.group(0)
    card = card.replace("v1.7", "v1.8").replace(" 1.7", " 1.8")
    if 'data-release-version="1.8"' not in card:
        card = card.replace(
            '<article class="release-card release-preview">',
            '<article class="release-card release-preview" data-release-version="1.8">',
            1,
        )
    card = re.sub(
        r'<li class="v18-highlight">.*?</li>', "", card, flags=re.DOTALL
    )
    additions = "".join(
        f'<li class="v18-highlight">{escape(bullet)}</li>' for bullet in bullets
    )
    card = card.replace("</ul>", additions + "</ul>", 1)
    return text[:card_match.start()] + card + text[card_match.end():]


def visual_preview(
    language: str,
    intro: str,
    bullets: list[str],
    prefix: str,
    localized_captions: list[str] | None = None,
) -> str:
    kicker, title = PREVIEW_LABELS.get(
        language,
        ("Coming in 1.8", "Collection Health becomes truly actionable"),
    )
    captions = localized_captions or VISUAL_CAPTIONS.get(language, DEFAULT_VISUAL_CAPTIONS)
    assets = [
        ("assets/screenshots/ipad/data-quality.png", "wide"),
        ("assets/screenshots/ipad/bin-filters.png", "wide"),
        ("assets/screenshots/v18/en-us/original-and-edition-year.png", "portrait"),
        ("assets/screenshots/v18/mac/collection.png", "wide"),
    ]
    figures = []
    for index, (asset, shape) in enumerate(assets):
        caption = captions[index] if index < len(captions) else title
        figures.append(
            f'<figure class="v18-visual {shape}"><img loading="lazy" '
            f'alt="{escape(caption, quote=True)}" src="{prefix}{asset}">'
            f'<figcaption>{escape(caption)}</figcaption></figure>'
        )
    return (
        '<section class="section v18-showcase" aria-labelledby="v18-preview-title">'
        '<div class="section-head">'
        f'<p class="kicker">{escape(kicker)}</p>'
        f'<h2 id="v18-preview-title">{escape(title)}</h2>'
        f'<p class="lead">{escape(intro)}</p>'
        '</div><div class="v18-visual-grid">'
        + "".join(figures)
        + '</div></section>'
    )


def screenshot_gallery(
    language: str,
    intro: str,
    bullets: list[str],
    prefix: str,
    localized_captions: list[str] | None = None,
) -> str:
    kicker, _ = PREVIEW_LABELS.get(language, ("Coming in 1.8", "Record Picker 1.8"))
    fallback = localized_captions or DEFAULT_VISUAL_CAPTIONS
    captions = [fallback[0], fallback[1], fallback[2]]
    assets = [
        "assets/screenshots/ipad/data-quality.png",
        "assets/screenshots/ipad/bin-filters.png",
        "assets/screenshots/v18/en-us/original-and-edition-year.png",
    ]
    figures = []
    for asset, caption in zip(assets, captions):
        figures.append(
            '<figure class="shot-card ipad">'
            f'<img loading="lazy" alt="{escape(caption, quote=True)}" '
            f'src="{prefix}{asset}">'
            f'<figcaption>{escape(caption)}</figcaption></figure>'
        )
    return (
        '<section class="media-section v18-screenshot-gallery" '
        'data-release-version="1.8"><div class="section-head">'
        f'<p class="kicker">{escape(kicker)}</p>'
        '<h2>Record Picker 1.8</h2>'
        f'<p class="lead">{escape(intro)}</p>'
        '</div><div class="shot-grid ipad-grid">'
        + ''.join(figures)
        + '</div></section>'
    )


def localized_visual_captions(locale_root: Path, bullets: list[str]) -> list[str]:
    def caption_from(page: Path, asset: str, fallback: str) -> str:
        if not page.exists():
            return fallback
        text = page.read_text(encoding="utf-8")
        matches = re.findall(
            rf'<figure[^>]*>(?:(?!</figure>).)*<img[^>]+{re.escape(asset)}[^>]*>'
            rf'(?:(?!</figure>).)*<figcaption>(.*?)</figcaption>.*?</figure>',
            text,
            flags=re.DOTALL,
        )
        usable = [
            unescape(re.sub(r'<[^>]+>', '', value)).strip()
            for value in matches
            if unescape(re.sub(r'<[^>]+>', '', value)).strip()
            not in DEFAULT_VISUAL_CAPTIONS
        ]
        return usable[-1] if usable else fallback

    screenshot_page = locale_root / "screenshots" / "index.html"
    mac_page = locale_root / "mac-app" / "index.html"
    original_year = bullets[3] if len(bullets) > 3 else DEFAULT_VISUAL_CAPTIONS[2]
    return [
        caption_from(screenshot_page, "assets/screenshots/ipad/data-quality.png", DEFAULT_VISUAL_CAPTIONS[0]),
        caption_from(screenshot_page, "assets/screenshots/ipad/bin-filters.png", DEFAULT_VISUAL_CAPTIONS[1]),
        original_year,
        caption_from(mac_page, "assets/screenshots/v18/mac/collection.png", DEFAULT_VISUAL_CAPTIONS[3]),
    ]


def update_home_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    language_match = re.search(r'<html lang="([^"]+)"', text)
    language = language_match.group(1) if language_match else "en-US"
    intro, new_bullets = release_copy(language)

    text = update_preview_card(text, path, new_bullets)

    prefix = "" if path.parent == ROOT else "../"
    stylesheet = f'<link rel="stylesheet" href="{prefix}v18.css?v=20260802">'
    if stylesheet not in text:
        text = text.replace("</head>", stylesheet + "</head>", 1)

    insertion = visual_preview(
        language, intro, new_bullets, prefix, localized_visual_captions(path.parent, new_bullets)
    )
    existing_showcase = re.search(
        r'<section class="section v18-showcase".*?</section>',
        text,
        flags=re.DOTALL,
    )
    if existing_showcase:
        text = text[:existing_showcase.start()] + insertion + text[existing_showcase.end():]
    else:
        marker = '<section class="section mac-teaser"'
        if marker not in text:
            raise RuntimeError(f"No Mac teaser insertion point found in {path}")
        text = text.replace(marker, insertion + marker, 1)

    path.write_text(text, encoding="utf-8")


def update_readme_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    language_match = re.search(r'<html lang="([^"]+)"', text)
    language = language_match.group(1) if language_match else "en-US"
    _, bullets = release_copy(language)
    text = update_preview_card(text, path, bullets)
    path.write_text(text, encoding="utf-8")


def update_screenshot_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    language_match = re.search(r'<html lang="([^"]+)"', text)
    language = language_match.group(1) if language_match else "en-US"
    intro, bullets = release_copy(language)
    prefix = "../" if path.parent.parent == ROOT else "../../"
    locale_root = path.parent.parent
    insertion = screenshot_gallery(
        language, intro, bullets, prefix, localized_visual_captions(locale_root, bullets)
    )
    existing_gallery = re.search(
        r'<section class="media-section v18-screenshot-gallery".*?</section>',
        text,
        flags=re.DOTALL,
    )
    if existing_gallery:
        text = text[:existing_gallery.start()] + insertion + text[existing_gallery.end():]
    else:
        hero = re.search(r'<section class="screens-hero">.*?</section>', text, flags=re.DOTALL)
        if not hero:
            raise RuntimeError(f"No screenshot hero found in {path}")
        text = text[:hero.end()] + insertion + text[hero.end():]
    path.write_text(text, encoding="utf-8")


def main() -> None:
    home_pages = [ROOT / "index.html"]
    home_pages.extend(
        path / "index.html"
        for path in sorted(ROOT.iterdir())
        if path.is_dir() and path.name in LOCALE_DIRECTORIES
    )
    for page in home_pages:
        update_home_page(page)
    readme_pages = [ROOT / "readme" / "index.html"]
    readme_pages.extend(
        path / "readme" / "index.html"
        for path in sorted(ROOT.iterdir())
        if path.is_dir() and path.name in LOCALE_DIRECTORIES
    )
    for page in readme_pages:
        update_readme_page(page)
    screenshot_pages = [ROOT / "screenshots" / "index.html"]
    screenshot_pages.extend(
        path / "screenshots" / "index.html"
        for path in sorted(ROOT.iterdir())
        if path.is_dir() and path.name in LOCALE_DIRECTORIES
    )
    for page in screenshot_pages:
        update_screenshot_page(page)
    print(
        f"Prepared {len(home_pages)} localized home pages and "
        f"{len(readme_pages)} feature pages and {len(screenshot_pages)} "
        "screenshot galleries for Record Picker 1.8"
    )


if __name__ == "__main__":
    main()
