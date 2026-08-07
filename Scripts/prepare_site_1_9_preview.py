#!/usr/bin/env python3
"""Refresh site visuals and announce Record Picker 1.9 platform availability.

The script is idempotent. It presents 1.9 as available on macOS while keeping
iPhone, iPad and Apple Watch marked as coming soon, removes misleading
availability labels from historical releases, expands the 1.8 screenshot
galleries with real light-mode captures, and removes the obsolete dark Watch
gallery.
"""

from __future__ import annotations

from html import escape, unescape
from pathlib import Path
import re

from prepare_release_1_8 import (
    LOCALE_DIRECTORIES,
    PREVIEW_LABELS,
    release_copy,
    localized_visual_captions,
    visual_preview,
)
from site_translation_data import (
    ACCENT_CORRECTIONS,
    CLOSE_LABELS,
    FREE_PRO_LABELS,
    HINDI_REPLACEMENTS,
    TODAY_PICK_TRANSLATIONS,
)
from enhance_site_accessibility import main as enhance_accessibility


ROOT = Path(__file__).resolve().parents[1]
APP_LOCALIZATIONS = ROOT.parent / "RecordPicker" / "RecordPicker"
APP_RELEASE_NOTES_19 = ROOT.parent / "RecordPicker" / "AppStoreReleaseNotes" / "1.9"
PUBLICATION_DATE = "2026-08-07"
SITE_STYLES_VERSION = "20260807-quality"
V18_STYLES_VERSION = "20260807-19-macos"
MIXED_SOFTWARE_VERSION = "1.8 (iOS/iPadOS/watchOS) · 1.9 (macOS)"
MIXED_FOOTER_VERSION = "Record Picker 1.8 · macOS 1.9"

LOCALE_BY_HTML_LANGUAGE = {
    "ar": "ar", "ca": "ca", "da": "da", "de": "de", "el": "el",
    "en-AU": "en-AU", "en-CA": "en-CA", "en-GB": "en-GB", "en-US": "en",
    "es-ES": "es", "fi": "fi", "fr-CA": "fr-CA", "fr-FR": "fr",
    "he": "he", "hi": "hi", "id": "id", "it": "it", "ja": "ja",
    "ko": "ko", "nb": "nb", "nl": "nl", "pl": "pl", "pt-BR": "pt-BR",
    "pt-PT": "pt-PT", "ru": "ru", "sv": "sv", "tr": "tr",
    "zh-Hans": "zh-Hans", "zh-Hant": "zh-Hant",
}

OPEN_GRAPH_LOCALES = {
    "ar": "ar_SA", "ca": "ca_ES", "da": "da_DK", "de": "de_DE",
    "el": "el_GR", "en-AU": "en_AU", "en-CA": "en_CA", "en-GB": "en_GB",
    "en-US": "en_US", "es-ES": "es_ES", "fi": "fi_FI", "fr-CA": "fr_CA",
    "fr-FR": "fr_FR", "he": "he_IL", "hi": "hi_IN", "id": "id_ID",
    "it": "it_IT", "ja": "ja_JP", "ko": "ko_KR", "nb": "nb_NO",
    "nl": "nl_NL", "pl": "pl_PL", "pt-BR": "pt_BR", "pt-PT": "pt_PT",
    "ru": "ru_RU", "sv": "sv_SE", "tr": "tr_TR", "zh-Hans": "zh_CN",
    "zh-Hant": "zh_TW",
}

RELEASE_NOTE_FILE_BY_LANGUAGE = {
    "ar": "ar-SA.txt", "de": "de-DE.txt", "en-AU": "en-AU.txt",
    "en-CA": "en-CA.txt", "en-GB": "en-GB.txt", "en-US": "en-US.txt",
    "es-ES": "es-ES.txt", "fi": "fi.txt", "fr-FR": "fr-FR.txt",
    "it": "it.txt", "ja": "ja.txt", "ko": "ko.txt", "nb": "no.txt",
    "nl": "nl-NL.txt", "pl": "pl.txt", "pt-BR": "pt-BR.txt",
    "sv": "sv.txt", "tr": "tr.txt", "zh-Hans": "zh-Hans.txt",
    "zh-Hant": "zh-Hant.txt",
}

RELEASE_19_SITE_TRANSLATIONS = {
    "ca": (
        "Record Picker 1.9 presenta el Disc del dia: un motiu actual i privat per redescobrir un disc que ja tens.",
        (
            "Les notícies musicals verificades, els aniversaris destacats i, opcionalment, els concerts propers es relacionen amb la teva col·lecció íntegrament al dispositiu.",
            "Cada suggeriment explica per què s’ha triat i cita la font amb data. Les notícies de la llista de desitjos es mantenen separades dels discos que pots escoltar.",
            "Els recordatoris privats opcionals, el retorn de rellevància i el Disc del dia a l’Apple Watch ajuden a mantenir útils els suggeriments. La col·lecció no s’envia mai al servei de notícies.",
        ),
    ),
    "da": (
        "Record Picker 1.9 introducerer Dagens plade: en aktuel og privat anledning til at genopdage en plade, du allerede ejer.",
        (
            "Bekræftede musiknyheder, mærkedage og valgfrie koncerter i nærheden matches med din samling udelukkende på din enhed.",
            "Hvert forslag forklarer, hvorfor det blev valgt, og henviser til en dateret kilde. Nyheder fra ønskelisten holdes adskilt fra plader, du kan afspille.",
            "Valgfrie private påmindelser, relevansfeedback og Dagens plade på Apple Watch hjælper med at holde forslagene nyttige. Din samling sendes aldrig til nyhedstjenesten.",
        ),
    ),
    "el": (
        "Το Record Picker 1.9 παρουσιάζει τον Δίσκο της ημέρας: μια επίκαιρη και ιδιωτική αφορμή για να ξανανακαλύψεις έναν δίσκο που ήδη έχεις.",
        (
            "Επαληθευμένες μουσικές ειδήσεις, σημαντικές επέτειοι και προαιρετικές κοντινές συναυλίες αντιστοιχίζονται με τη συλλογή σου αποκλειστικά στη συσκευή.",
            "Κάθε πρόταση εξηγεί γιατί επιλέχθηκε και παραπέμπει σε χρονολογημένη πηγή. Τα νέα της λίστας επιθυμιών παραμένουν χωριστά από τους δίσκους που μπορείς να ακούσεις.",
            "Προαιρετικές ιδιωτικές υπενθυμίσεις, σχόλια συνάφειας και ο Δίσκος της ημέρας στο Apple Watch βοηθούν τις προτάσεις να παραμένουν χρήσιμες. Η συλλογή σου δεν αποστέλλεται ποτέ στην υπηρεσία ειδήσεων.",
        ),
    ),
    "fr-CA": (
        "Record Picker 1.9 présente le Disque du jour : une raison actuelle et confidentielle de redécouvrir un disque que tu possèdes déjà.",
        (
            "Les nouvelles musicales vérifiées, les anniversaires marquants et, en option, les concerts à proximité sont rapprochés de ta collection uniquement sur ton appareil.",
            "Chaque suggestion explique son choix et cite sa source datée. Les nouvelles de la liste de souhaits restent séparées des disques disponibles à l’écoute.",
            "Des rappels privés facultatifs, le retour de pertinence et le Disque du jour sur Apple Watch entretiennent la qualité des suggestions. Ta collection n’est jamais transmise au service d’actualité.",
        ),
    ),
    "he": (
        "Record Picker 1.9 מציגה את תקליט היום: סיבה עדכנית ופרטית לגלות מחדש תקליט שכבר נמצא אצלך.",
        (
            "חדשות מוזיקה מאומתות, ימי שנה חשובים והופעות קרובות לפי בחירה מותאמים לאוסף שלך אך ורק במכשיר.",
            "כל הצעה מסבירה מדוע נבחרה ומצטטת מקור מתוארך. חדשות מרשימת המשאלות נשארות נפרדות מתקליטים שאפשר להאזין להם.",
            "תזכורות פרטיות לפי בחירה, משוב על רלוונטיות ותקליט היום ב-Apple Watch עוזרים לשמור על הצעות מועילות. האוסף שלך לעולם אינו נשלח לשירות החדשות.",
        ),
    ),
    "hi": (
        "Record Picker 1.9 में आज का रिकॉर्ड पेश है: आपके पास पहले से मौजूद रिकॉर्ड को निजी तौर पर फिर खोजने की एक सामयिक वजह।",
        (
            "सत्यापित संगीत समाचार, महत्वपूर्ण वर्षगाँठ और वैकल्पिक आस-पास के कॉन्सर्ट का मिलान आपके संग्रह से पूरी तरह इसी डिवाइस पर होता है।",
            "हर सुझाव बताता है कि उसे क्यों चुना गया और तारीख सहित स्रोत देता है। इच्छा-सूची की खबरें उन रिकॉर्ड से अलग रहती हैं जिन्हें आप सुन सकते हैं।",
            "वैकल्पिक निजी रिमाइंडर, प्रासंगिकता फ़ीडबैक और Apple Watch पर आज का रिकॉर्ड सुझावों को उपयोगी बनाए रखते हैं। आपका संग्रह समाचार सेवा को कभी नहीं भेजा जाता।",
        ),
    ),
    "id": (
        "Record Picker 1.9 memperkenalkan Piringan hari ini: alasan terkini dan privat untuk menemukan kembali piringan yang sudah Anda miliki.",
        (
            "Berita musik terverifikasi, hari jadi penting, dan konser terdekat opsional dicocokkan dengan koleksi Anda sepenuhnya di perangkat.",
            "Setiap saran menjelaskan alasan pemilihannya dan mencantumkan sumber bertanggal. Berita daftar keinginan tetap terpisah dari piringan yang dapat Anda putar.",
            "Pengingat privat opsional, umpan balik relevansi, dan Piringan hari ini di Apple Watch membantu menjaga kegunaan saran. Koleksi Anda tidak pernah dikirim ke layanan berita.",
        ),
    ),
    "pt-PT": (
        "O Record Picker 1.9 apresenta o Disco do dia: um motivo atual e privado para redescobrir um disco que já possui.",
        (
            "Notícias de música verificadas, aniversários marcantes e concertos próximos opcionais são associados à sua coleção inteiramente no dispositivo.",
            "Cada sugestão explica por que foi escolhida e cita a respetiva fonte datada. As notícias da lista de desejos permanecem separadas dos discos que pode ouvir.",
            "Lembretes privados opcionais, feedback de relevância e o Disco do dia no Apple Watch ajudam a manter as sugestões úteis. A sua coleção nunca é enviada para o serviço de notícias.",
        ),
    ),
    "ru": (
        "В Record Picker 1.9 появится «Пластинка дня» — актуальный и конфиденциальный повод заново открыть пластинку, которая уже есть в вашей коллекции.",
        (
            "Проверенные музыкальные новости, важные годовщины и, по желанию, ближайшие концерты сопоставляются с вашей коллекцией только на устройстве.",
            "Каждая рекомендация объясняет выбор и ссылается на датированный источник. Новости из списка желаний не смешиваются с пластинками, которые можно послушать.",
            "Необязательные приватные напоминания, оценка релевантности и «Пластинка дня» на Apple Watch помогают сохранять рекомендации полезными. Ваша коллекция никогда не отправляется новостному сервису.",
        ),
    ),
}

TODAY_PICK_KEYS = (
    "Today Pick",
    "A timely reason to rediscover a record you already own.",
    "Why this record today?",
    "Matching happens on this device. Your collection and wishlist are never sent to the music-news service.",
    "News and reissues related to records you want. These are never presented as records you own.",
)

DARK_MAC_REPLACEMENTS = {
    "assets/screenshots/mac/collection-1.0-en-us.jpeg": "assets/screenshots/v18/mac/collection.png",
    "assets/screenshots/mac/collection-1.0-fr.jpeg": "assets/screenshots/v18/mac/collection.png",
    "assets/screenshots/mac/data-quality-1.0-en-us.jpeg": "assets/screenshots/v18/mac/data-quality.png",
    "assets/screenshots/mac/data-quality-1.0-fr.jpeg": "assets/screenshots/v18/mac/data-quality.png",
    "assets/screenshots/mac/mood-pick-1.0-en-us.jpeg": "assets/screenshots/mac/mood-pick-light.jpeg",
    "assets/screenshots/mac/mood-pick-1.0-fr.jpeg": "assets/screenshots/mac/mood-pick-light.jpeg",
    "assets/screenshots/mac/random-pick-1.0-en-us.jpeg": "assets/screenshots/mac/random-pick-light.png",
    "assets/screenshots/mac/record-crate-large-1.0-en-us.jpeg": "assets/screenshots/mac/record-crate-light.png",
    "assets/screenshots/mac/record-crate-small-1.0-en-us.jpeg": "assets/screenshots/mac/record-crate-light.png",
}


def localized_roots() -> list[Path]:
    roots = [ROOT]
    roots.extend(
        path for path in sorted(ROOT.iterdir())
        if path.is_dir() and path.name in LOCALE_DIRECTORIES
    )
    return roots


def html_language(text: str) -> str:
    match = re.search(r'<html lang="([^"]+)"', text)
    return match.group(1) if match else "en-US"


def app_strings(language: str) -> dict[str, str]:
    if language in TODAY_PICK_TRANSLATIONS:
        return dict(zip(TODAY_PICK_KEYS, TODAY_PICK_TRANSLATIONS[language]))
    locale = LOCALE_BY_HTML_LANGUAGE.get(language, "en")
    path = APP_LOCALIZATIONS / f"{locale}.lproj" / "Localizable.strings"
    fallback = APP_LOCALIZATIONS / "en.lproj" / "Localizable.strings"
    text = (path if path.exists() else fallback).read_text(encoding="utf-8")
    values: dict[str, str] = {}
    for key in TODAY_PICK_KEYS:
        pattern = rf'^"{re.escape(key)}"\s*=\s*"((?:\\.|[^"\\])*)";'
        match = re.search(pattern, text, flags=re.MULTILINE)
        values[key] = (
            match.group(1).replace(r'\"', '"').replace(r'\n', '\n')
            if match else key
        )
    return values


def release_19_copy(language: str) -> tuple[str, tuple[str, str, str]]:
    if language in RELEASE_19_SITE_TRANSLATIONS:
        return RELEASE_19_SITE_TRANSLATIONS[language]
    filename = RELEASE_NOTE_FILE_BY_LANGUAGE.get(language)
    if not filename:
        raise RuntimeError(f"No localized Record Picker 1.9 announcement for {language}")
    path = APP_RELEASE_NOTES_19 / filename
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 4 or not all(line.startswith("•") for line in lines[1:]):
        raise RuntimeError(f"Unexpected Record Picker 1.9 release-note format in {path}")
    return lines[0], tuple(line.removeprefix("•").strip() for line in lines[1:])


def upcoming_label(language: str) -> str:
    if language.startswith("en"):
        return "Coming soon · 1.9"
    label = PREVIEW_LABELS.get(language, ("Coming in 1.8", ""))[0]
    return label.replace("1.8", "1.9")


def available_label(text: str, path: Path) -> str:
    """Return the localized "available now" label.

    Once 1.9 has been prepared, the label lives on its Mac platform summary.
    The 1.8 fallback keeps the first migration compatible with older pages.
    Historical cards must not remain the source of truth after publication.
    """
    current = re.search(
        r'<article class="release-card[^>]*data-release-version="1\.9".*?'
        r'<strong>Mac · 1\.9 · (.*?)</strong>.*?</article>',
        text,
        flags=re.DOTALL,
    )
    if current:
        return unescape(re.sub(r'<[^>]+>', '', current.group(1))).strip()

    historical = re.search(
        r'<article class="release-card[^>]*data-release-version="1\.8".*?</article>',
        text,
        flags=re.DOTALL,
    )
    if historical:
        status = re.search(
            r'<div><h3>.*?</h3><p>(.*?)</p>',
            historical.group(0),
            re.DOTALL,
        )
        if status:
            return unescape(re.sub(r'<[^>]+>', '', status.group(1))).strip()
    raise RuntimeError(f"No localized availability label in {path}")


def platform_summary(language: str, available: str) -> str:
    return (
        '<p class="release-platform-summary">'
        f'<strong>Mac · 1.9 · {escape(available)}</strong>'
        f'<span>iPhone · iPad · Apple Watch · {escape(upcoming_label(language))}</span>'
        '</p>'
    )


def platform_badges(language: str, available: str) -> str:
    return (
        '<div class="upcoming-platforms">'
        f'<span class="is-available">Mac · 1.9 · {escape(available)}</span>'
        f'<span>iPhone · iPad · Apple Watch · {escape(upcoming_label(language))}</span>'
        '</div>'
    )


def upcoming_card(language: str, available: str) -> str:
    headline, bullets = release_19_copy(language)
    return (
        '<article class="release-card release-preview release-upcoming" '
        'data-release-version="1.9"><div class="release-head">'
        '<span class="version-pill">v1.9</span><div>'
        f'<h3>{escape(headline)}</h3>'
        f'{platform_summary(language, available)}</div></div><ul>'
        + ''.join(f'<li>{escape(bullet)}</li>' for bullet in bullets)
        + '</ul></article>'
    )


def upcoming_showcase(language: str, available: str) -> str:
    strings = app_strings(language)
    title = strings["Today Pick"]
    promise = strings["A timely reason to rediscover a record you already own."]
    why = strings["Why this record today?"]
    headline, bullets = release_19_copy(language)
    return (
        '<section class="section upcoming-showcase" data-release-version="1.9">'
        '<div class="section-head">'
        f'<p class="kicker">Mac · 1.9 · {escape(available)}</p>'
        f'<h2>Record Picker 1.9 · {escape(title)}</h2>'
        f'<p class="lead">{escape(promise)}</p></div>'
        '<div class="upcoming-preview-panel">'
        f'<p class="upcoming-label">{escape(title)}</p><h3>{escape(why)}</h3>'
        f'<p>{escape(headline)}</p><ul>'
        + ''.join(f'<li>{escape(bullet)}</li>' for bullet in bullets)
        + '</ul>' + platform_badges(language, available) + '</div></section>'
    )


def upcoming_gallery_intro(language: str, available: str) -> str:
    strings = app_strings(language)
    title = strings["Today Pick"]
    promise = strings["A timely reason to rediscover a record you already own."]
    headline, bullets = release_19_copy(language)
    return (
        '<section class="media-section upcoming-gallery-intro" data-release-version="1.9">'
        '<div class="section-head">'
        f'<p class="kicker">Mac · 1.9 · {escape(available)}</p>'
        f'<h2>Record Picker 1.9 · {escape(title)}</h2>'
        f'<p class="lead">{escape(headline)}</p></div>'
        '<div class="upcoming-gallery-summary"><p>' + escape(promise) + '</p><ul>'
        + ''.join(f'<li>{escape(bullet)}</li>' for bullet in bullets)
        + '</ul>' + platform_badges(language, available) + '</div></section>'
    )


def update_release_cards(text: str, path: Path, available: str) -> str:
    language = html_language(text)
    insertion = upcoming_card(language, available)
    current = re.search(
        r'<article class="release-card[^>]*data-release-version="1\.9".*?</article>',
        text,
        flags=re.DOTALL,
    )
    if current:
        text = text[:current.start()] + insertion + text[current.end():]
    else:
        marker = re.search(
            r'<article class="release-card[^>]*data-release-version="1\.8"', text
        )
        if not marker:
            raise RuntimeError(f"No Record Picker 1.8 card found in {path}")
        text = text[:marker.start()] + insertion + text[marker.start():]

    def historical_card(match: re.Match[str]) -> str:
        card = match.group(0)
        version = re.search(r'<span class="version-pill">v([^<]+)</span>', card)
        if not version or version.group(1) == "1.9":
            return card
        return re.sub(
            r'(<div><h3>.*?</h3>)<p>.*?</p>',
            r'\1',
            card,
            count=1,
            flags=re.DOTALL,
        )

    text = re.sub(
        r'<article class="release-card[^>]*>.*?</article>',
        historical_card,
        text,
        flags=re.DOTALL,
    )
    _, bullets = release_copy(language)
    v18 = re.search(
        r'<article class="release-card[^>]*data-release-version="1\.8".*?</article>',
        text,
        flags=re.DOTALL,
    )
    if v18:
        card = re.sub(
            r'<li(?: class="v18-highlight"| data-v18-added)>.*?</li>',
            "",
            v18.group(0),
            flags=re.DOTALL,
        )
        highlights = "".join(
            f'<li data-v18-added>{escape(bullet)}</li>' for bullet in bullets
        )
        card = card.replace("</ul>", highlights + "</ul>", 1)
        text = text[:v18.start()] + card + text[v18.end():]
    return text


def shot(asset: str, caption: str, shape: str, prefix: str) -> str:
    return (
        f'<figure class="shot-card {shape}"><img loading="lazy" '
        f'alt="{escape(caption, quote=True)}" src="{prefix}{asset}">'
        f'<figcaption>{escape(caption)}</figcaption></figure>'
    )


def expanded_gallery(language: str, prefix: str, captions: list[str]) -> str:
    intro, _ = release_copy(language)
    def cap(index: int) -> str:
        return captions[index % len(captions)]

    phone_assets = [
        "data-quality.jpeg", "final-draw.jpeg", "history.jpeg", "manual-entry.jpeg"
    ]
    ipad_assets = [
        "ipad/data-quality.png", "ipad/bin-filters.png", "ipad/manual-edit.png",
        "v18/en-us/original-and-edition-year.png",
    ]
    mac_assets = ["collection.png", "data-quality.png", "list.png", "original-edition.png"]

    phone_figures = "".join(
        shot(f"assets/screenshots/iphone/{asset}", cap(caption_index), "iphone", prefix)
        for asset, caption_index in zip(phone_assets, (0, 1, 2, 2))
    )
    ipad_figures = "".join(
        shot(f"assets/screenshots/{asset}", cap(caption_index), "ipad", prefix)
        for asset, caption_index in zip(ipad_assets, (0, 1, 0, 2))
    )
    mac_figures = "".join(
        shot(f"assets/screenshots/v18/mac/{asset}", cap(caption_index), "ipad", prefix)
        for asset, caption_index in zip(mac_assets, (3, 0, 1, 2))
    )
    return (
        '<section class="media-section v18-screenshot-gallery" data-release-version="1.8">'
        '<div class="section-head"><p class="kicker">Record Picker 1.8</p>'
        f'<h2>Record Picker 1.8</h2><p class="lead">{escape(intro)}</p></div>'
        '<div class="v18-gallery-group"><h3>iPhone · Record Picker 1.8</h3>'
        f'<div class="shot-grid phone-grid">{phone_figures}</div></div>'
        '<div class="v18-gallery-group"><h3>iPad · Record Picker 1.8</h3>'
        f'<div class="shot-grid ipad-grid">{ipad_figures}</div></div>'
        '<div class="v18-gallery-group"><h3>Mac · Record Picker 1.8</h3>'
        f'<div class="shot-grid ipad-grid">{mac_figures}</div></div></section>'
    )


def update_feature_intro(text: str, language: str, prefix: str, caption: str) -> str:
    figure = re.search(
        r'<figure class="context-visual (?:watch|wide) ">(?:(?!</figure>).)*'
        r'(?:onboarding-|iphone-(?:collection|collection-health|rediscover|freemium)|'
        r'assets/screenshots/ipad/data-quality\.png)'
        r'.*?</figure>',
        text,
        flags=re.DOTALL,
    )
    if not figure:
        figure = re.search(
            r'<figure class="context-visual watch ">.*?</figure>',
            text,
            flags=re.DOTALL,
        )
    if not figure:
        updated = text
    else:
        replacement = (
            '<figure class="context-visual wide "><img loading="lazy" '
            f'alt="{escape(caption, quote=True)}" '
            f'src="{prefix}assets/screenshots/ipad/data-quality.png">'
            f'<figcaption>{escape(caption)}</figcaption></figure>'
        )
        updated = text[:figure.start()] + replacement + text[figure.end():]

    updated = re.sub(
        r'<figure class="feature-visual watch">.*?</figure>',
        "",
        updated,
        flags=re.DOTALL,
    )
    if "assets/watch/" in updated:
        raise RuntimeError("Unexpected Watch visual remains in feature page")
    if re.search(
        r'onboarding-|iphone-(?:collection|collection-health|rediscover|freemium)',
        updated,
    ):
        raise RuntimeError("Unexpected tutorial visual remains in feature page")
    return updated


def replace_dark_mac_references(text: str) -> str:
    for old, new in DARK_MAC_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def replace_words(text: str, replacements: dict[str, str]) -> str:
    for old in sorted(replacements, key=len, reverse=True):
        new = replacements[old]
        text = re.sub(
            rf'(?<![\w-]){re.escape(old)}(?![\w-])',
            lambda match, value=new: (
                value[0].upper() + value[1:]
                if match.group(0)[:1].isupper() and value[:1].islower()
                else value
            ),
            text,
            flags=re.IGNORECASE,
        )
    return text


def localize_accessibility(text: str, language: str) -> str:
    text = re.sub(
        r'<span(?: id="site-brand-name")?>Record Picker</span></a>'
        r'<nav class="nav-links"(?: aria-(?:label|labelledby)="[^"]+")?>',
        '<span id="site-brand-name">Record Picker</span></a>'
        '<nav class="nav-links" aria-labelledby="site-brand-name">',
        text,
    )
    text = re.sub(
        r'<footer class="footer"><span(?: id="site-footer-version")?>'
        r'(Record Picker v1\.8)</span><nav(?: aria-(?:label|labelledby)="[^"]+")?>',
        r'<footer class="footer"><span id="site-footer-version">\1</span>'
        r'<nav aria-labelledby="site-footer-version">',
        text,
    )
    text = re.sub(
        r'<span class="visually-hidden"(?: id="language-label")?>(.*?)</span>',
        r'<span class="visually-hidden" id="language-label">\1</span>',
        text,
        count=1,
    )
    text = re.sub(
        r'role="listbox" aria-(?:label|labelledby)="[^"]+"',
        'role="listbox" aria-labelledby="language-label"',
        text,
        count=1,
    )
    for label in ("App Store details", "Record Picker screenshots", "Record Picker for Mac"):
        text = text.replace(f' aria-label="{label}"', "")

    def figure_alt(match: re.Match[str]) -> str:
        figure = match.group(0)
        caption_match = re.search(r'<figcaption>(.*?)</figcaption>', figure, flags=re.DOTALL)
        if not caption_match:
            return figure
        caption = unescape(re.sub(r'<[^>]+>', '', caption_match.group(1))).strip()
        if not caption:
            return figure
        return re.sub(
            r'(<img\b[^>]*\balt=")[^"]*(")',
            lambda image: image.group(1) + escape(caption, quote=True) + image.group(2),
            figure,
            count=1,
        )

    text = re.sub(r'<figure\b.*?</figure>', figure_alt, text, flags=re.DOTALL)

    def video_label(match: re.Match[str]) -> str:
        button = match.group(0)
        title = re.search(r'\btitle="([^"]+)"', button)
        if not title:
            return button
        return re.sub(
            r'\baria-label="[^"]*"',
            f'aria-label="{escape(unescape(title.group(1)), quote=True)}"',
            button,
            count=1,
        )

    text = re.sub(r'<button class="video-(?:thumb|preview)"[^>]*>', video_label, text)
    close = CLOSE_LABELS.get(language, "Close")
    text = re.sub(
        r'(data-video-close[^>]*aria-label=")[^"]*(")',
        rf'\1{escape(close, quote=True)}\2',
        text,
    )
    return text


def restore_support_privacy_link(text: str) -> str:
    section = re.search(r'<section class="doc-content">.*?</section>', text, flags=re.DOTALL)
    if not section or 'href="../privacy/"' in section.group(0):
        return text
    label = re.search(r'<a href="../privacy/">([^<]+)</a>', text)
    if not label:
        return text
    block = section.group(0)
    paragraphs = list(re.finditer(r'<p>.*?</p>', block, flags=re.DOTALL))
    if not paragraphs:
        return text
    last = paragraphs[-1]
    paragraph = last.group(0).replace(
        '</p>', f' <a href="../privacy/">{label.group(1)}</a>.</p>', 1
    )
    block = block[:last.start()] + paragraph + block[last.end():]
    return text[:section.start()] + block + text[section.end():]


IMAGE_DIMENSION_CACHE: dict[Path, tuple[int, int]] = {}


def image_dimensions(path: Path) -> tuple[int, int] | None:
    if path in IMAGE_DIMENSION_CACHE:
        return IMAGE_DIMENSION_CACHE[path]
    if not path.exists():
        return None
    data = path.read_bytes()
    dimensions = None
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        dimensions = (
            int.from_bytes(data[16:20], "big"),
            int.from_bytes(data[20:24], "big"),
        )
    elif data.startswith(b"\xff\xd8"):
        offset = 2
        start_of_frame = {
            0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
        }
        while offset + 8 < len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            marker = data[offset + 1]
            offset += 2
            if marker in {0x01, *range(0xD0, 0xDA)}:
                continue
            if offset + 2 > len(data):
                break
            length = int.from_bytes(data[offset:offset + 2], "big")
            if marker in start_of_frame and offset + 7 <= len(data):
                dimensions = (
                    int.from_bytes(data[offset + 5:offset + 7], "big"),
                    int.from_bytes(data[offset + 3:offset + 5], "big"),
                )
                break
            if length < 2:
                break
            offset += length
    if dimensions:
        IMAGE_DIMENSION_CACHE[path] = dimensions
    return dimensions


def add_intrinsic_image_dimensions(text: str, page: Path) -> str:
    def update(match: re.Match[str]) -> str:
        tag = match.group(0)
        source = re.search(r'\bsrc="([^"]+)"', tag)
        if not source or source.group(1).startswith(("data:", "http://", "https://")):
            return tag
        raw_source = unescape(source.group(1)).split("?", 1)[0]
        asset = (
            ROOT / raw_source.lstrip("/")
            if raw_source.startswith("/")
            else (page.parent / raw_source).resolve()
        )
        dimensions = image_dimensions(asset)
        if not dimensions:
            return tag
        additions = ""
        if not re.search(r'\bwidth="', tag):
            additions += f' width="{dimensions[0]}"'
        if not re.search(r'\bheight="', tag):
            additions += f' height="{dimensions[1]}"'
        return tag[:-1] + additions + ">" if additions else tag
    return re.sub(r'<img\b[^>]*>', update, text)


def optimize_image_loading(text: str) -> str:
    def defaults(match: re.Match[str]) -> str:
        tag = match.group(0)
        if not re.search(r'\bdecoding="', tag):
            tag = tag[:-1] + ' decoding="async">'
        if 'src="/assets/brand/favicon-96.png"' not in tag and not re.search(r'\bloading="', tag):
            tag = tag[:-1] + ' loading="lazy">'
        return tag

    text = re.sub(r'<img\b[^>]*>', defaults, text)
    hero = re.search(r'<div class="hero-showcase".*?</div>', text, flags=re.DOTALL)
    if hero:
        block = re.sub(
            r'<img\b[^>]*>',
            lambda match: re.sub(r'\sloading="lazy"', '', match.group(0))[:-1]
            + (' fetchpriority="high">' if 'fetchpriority=' not in match.group(0) else '>'),
            hero.group(0),
            count=1,
        )
        text = text[:hero.start()] + block + text[hero.end():]
    return text


def ensure_mac_feature_previews(text: str) -> str:
    row = re.search(r'<section class="mac-feature-row">.*?</section>', text, flags=re.DOTALL)
    if not row:
        return text
    prefix_match = re.search(
        r'src="([^\"]*)assets/screenshots/mac/record-crate-light\.png"',
        row.group(0),
    )
    prefix = prefix_match.group(1) if prefix_match else "../"
    assets = (
        "assets/screenshots/mac/record-crate-light.png",
        "assets/screenshots/v18/mac/list.png",
        "assets/screenshots/mac/mood-pick-light.jpeg",
    )
    cards = re.findall(r'<article class="card">.*?</article>', row.group(0), flags=re.DOTALL)
    if len(cards) != len(assets):
        return text
    updated_cards = []
    for card, asset in zip(cards, assets):
        card = re.sub(
            r'<div class="mac-card-preview[^\"]*">.*?</div>',
            "",
            card,
            flags=re.DOTALL,
        )
        heading = re.search(r'<h2>(.*?)</h2>', card, flags=re.DOTALL)
        alt = escape(unescape(re.sub(r'<[^>]+>', '', heading.group(1))).strip(), quote=True)
        preview = (
            '<div class="mac-card-preview"><figure>'
            f'<img alt="{alt}" src="{prefix}{asset}">'
            '</figure></div>'
        )
        updated_cards.append(card.replace("</article>", preview + "</article>", 1))
    block = row.group(0)
    for original, updated in zip(cards, updated_cards):
        block = block.replace(original, updated, 1)
    return text[:row.start()] + block + text[row.end():]


def ensure_social_metadata(text: str, language: str) -> str:
    title_match = re.search(r'<title>(.*?)</title>', text, flags=re.DOTALL)
    description_match = re.search(
        r'<meta name="description" content="([^"]*)">', text
    )
    image_match = re.search(
        r'<meta property="og:image" content="([^"]*)">', text
    )
    if not title_match or not description_match or not image_match:
        return text
    title = unescape(re.sub(r'<[^>]+>', '', title_match.group(1))).strip()
    description = unescape(description_match.group(1)).strip()
    image = unescape(image_match.group(1)).strip()
    for key in ("robots", "twitter:card", "twitter:title", "twitter:description", "twitter:image"):
        text = re.sub(rf'<meta name="{re.escape(key)}" content="[^"]*">', "", text)
    for key in ("og:type", "og:site_name", "og:locale"):
        text = re.sub(rf'<meta property="{re.escape(key)}" content="[^"]*">', "", text)
    metadata = (
        '<meta name="robots" content="index,follow,max-image-preview:large">'
        '<meta property="og:type" content="website">'
        '<meta property="og:site_name" content="Record Picker">'
        f'<meta property="og:locale" content="{OPEN_GRAPH_LOCALES.get(language, "en_US")}">'
        '<meta name="twitter:card" content="summary">'
        f'<meta name="twitter:title" content="{escape(title, quote=True)}">'
        f'<meta name="twitter:description" content="{escape(description, quote=True)}">'
        f'<meta name="twitter:image" content="{escape(image, quote=True)}">'
    )
    canonical = re.search(r'<link rel="canonical"', text)
    if not canonical:
        return text
    return text[:canonical.start()] + metadata + text[canonical.start():]


def repair_translations(text: str, language: str, relative_path: Path, page: Path) -> str:
    text = re.sub(
        r'(styles\.css\?v=)[^"]+',
        rf'\g<1>{SITE_STYLES_VERSION}',
        text,
    )
    if language in FREE_PRO_LABELS:
        text = text.replace("Free · Lifetime Pro", FREE_PRO_LABELS[language])
    if language == "hi":
        text = replace_words(text, HINDI_REPLACEMENTS)
    if language in ACCENT_CORRECTIONS:
        text = replace_words(text, ACCENT_CORRECTIONS[language])
    if language in {"en-AU", "en-CA", "en-GB"}:
        text = replace_words(
            text,
            {"Favorite": "Favourite", "favorite": "favourite", "Catalog": "Catalogue", "catalog": "catalogue"},
        )
    text = localize_accessibility(text, language)
    if relative_path.as_posix() == "support/index.html":
        text = restore_support_privacy_link(text)
    if relative_path.as_posix() == "privacy/index.html":
        text = re.sub(
            r'(<p class="doc-meta">Record Picker )v1\.6',
            r'\1v1.8',
            text,
            count=1,
        )
        text = text.replace("<h3>", "<h2>").replace("</h3>", "</h2>")
    if relative_path.as_posix() == "mac-app/index.html":
        text = text.replace("macOS 1.0", "macOS 1.9")
        text = text.replace("macOS 1.8", "macOS 1.9")
        text = ensure_mac_feature_previews(text)
    text = add_intrinsic_image_dimensions(text, page)
    text = optimize_image_loading(text)
    text = ensure_social_metadata(text, language)
    return text


def ensure_preview_stylesheet(text: str, prefix: str) -> str:
    stylesheet = f'<link rel="stylesheet" href="{prefix}v18.css?v={V18_STYLES_VERSION}">'
    text = re.sub(
        r'<link rel="stylesheet" href="[^\"]*v18\.css\?v=[^\"]+">',
        "",
        text,
    )
    return text.replace("</head>", stylesheet + "</head>", 1)


def update_current_release_facts(text: str) -> str:
    text = re.sub(
        r'"softwareVersion":"(?:1\.0|1\.6|1\.8|1\.8 \(iOS/iPadOS/watchOS\) · 1\.9 \(macOS\))"',
        f'"softwareVersion":"{MIXED_SOFTWARE_VERSION}"',
        text,
    )
    text = text.replace(
        '<strong>v1.8</strong>',
        '<strong>Mac · 1.9</strong>',
    )
    text = text.replace(
        '<strong>iOS 1.8 · macOS 1.9</strong>',
        '<strong>Mac · 1.9</strong>',
    )
    text = re.sub(
        r'(<footer class="footer"><span(?: id="site-footer-version")?>).*?</span>',
        rf'\1{MIXED_FOOTER_VERSION}</span>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    heading = re.search(
        r'<section class="[^"]*release-history[^"]*".*?'
        r'<div class="section-head">.*?</div>',
        text,
        flags=re.DOTALL,
    )
    if heading:
        updated = heading.group(0).replace("1.6", "1.8").replace("1.0", "1.8")
        text = text[:heading.start()] + updated + text[heading.end():]
    return text


def sitemap_image(asset: str, title: str) -> str:
    return (
        "    <image:image>\n"
        f"      <image:loc>https://recordpicker.app/{asset}</image:loc>\n"
        f"      <image:title>{escape(title)}</image:title>\n"
        f"      <image:caption>{escape(title)}</image:caption>\n"
        "    </image:image>\n"
    )


def update_media_sitemap(roots: list[Path]) -> None:
    path = ROOT / "sitemap-media.xml"
    text = path.read_text(encoding="utf-8")
    text = replace_dark_mac_references(text)
    text = re.sub(
        r'[ \t]*<image:image>\s*<image:loc>[^<]*/assets/watch/[^<]+</image:loc>.*?'
        r'</image:image>\s*',
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'[ \t]*<image:image>\s*'
        r'<image:loc>https://recordpicker\.app/assets/screenshots/[^<]+</image:loc>\s*'
        r'<image:title>Record Picker 1\.8 light screenshot [^<]+</image:title>\s*'
        r'<image:caption>.*?</image:caption>\s*</image:image>\s*',
        "",
        text,
        flags=re.DOTALL,
    )

    for root in roots:
        web_prefix = "" if root == ROOT else f"{root.name}/"
        language = html_language((root / "index.html").read_text(encoding="utf-8"))
        assets = [
            *(f"assets/screenshots/iphone/{name}" for name in (
                "data-quality.jpeg", "final-draw.jpeg", "history.jpeg", "manual-entry.jpeg"
            )),
            *(f"assets/screenshots/ipad/{name}" for name in (
                "data-quality.png", "bin-filters.png", "manual-edit.png",
            )),
            "assets/screenshots/v18/en-us/original-and-edition-year.png",
            *(f"assets/screenshots/v18/mac/{name}" for name in (
                "collection.png", "data-quality.png", "list.png", "original-edition.png"
            )),
        ]
        images = "".join(
            sitemap_image(asset, f"Record Picker 1.8 light screenshot {index}")
            for index, asset in enumerate(assets, start=1)
        )
        for suffix in ("", "readme/", "screenshots/", "mac-app/"):
            url = f"https://recordpicker.app/{web_prefix}{suffix}"
            block_match = re.search(
                rf'  <url>\s*<loc>{re.escape(url)}</loc>.*?</url>',
                text,
                flags=re.DOTALL,
            )
            if not block_match:
                raise RuntimeError(f"No media sitemap entry for {url}")
            block = re.sub(
                r'<lastmod>[^<]+</lastmod>',
                f'<lastmod>{PUBLICATION_DATE}</lastmod>',
                block_match.group(0),
                count=1,
            )
            if suffix == "screenshots/":
                block = block.replace(
                    f'<lastmod>{PUBLICATION_DATE}</lastmod>',
                    f'<lastmod>{PUBLICATION_DATE}</lastmod>\n{images}',
                    1,
                )
            text = text[:block_match.start()] + block + text[block_match.end():]
    text = re.sub(
        r'<lastmod>[^<]+</lastmod>',
        f'<lastmod>{PUBLICATION_DATE}</lastmod>',
        text,
    )
    path.write_text(text, encoding="utf-8")


def update_standard_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'<lastmod>[^<]+</lastmod>',
        f'<lastmod>{PUBLICATION_DATE}</lastmod>',
        text,
    )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    roots = localized_roots()
    for root in roots:
        home = root / "index.html"
        home_prefix = "" if root == ROOT else "../"
        source_home_text = home.read_text(encoding="utf-8")
        current_availability = available_label(source_home_text, home)
        home_text = update_release_cards(source_home_text, home, current_availability)
        language = html_language(home_text)
        release_intro, release_bullets = release_copy(language)
        visual_captions = localized_visual_captions(root, release_bullets)
        release_card = re.search(
            r'<article class="release-card[^>]*data-release-version="1\.8".*?</article>',
            home_text,
            flags=re.DOTALL,
        )
        release_status = None
        if release_card:
            status = re.search(r'<div><h3>.*?</h3><p>(.*?)</p>', release_card.group(0), re.DOTALL)
            if status:
                release_status = unescape(re.sub(r'<[^>]+>', '', status.group(1))).strip()
        current_v18 = re.search(
            r'<section class="section v18-showcase".*?</section>',
            home_text,
            flags=re.DOTALL,
        )
        functional_v18 = visual_preview(
            language, release_intro, release_bullets, home_prefix, visual_captions,
            release_status,
        )
        if not current_v18:
            raise RuntimeError(f"No 1.8 visual showcase found in {home}")
        home_text = (
            home_text[:current_v18.start()] + functional_v18
            + home_text[current_v18.end():]
        )
        showcase = upcoming_showcase(language, current_availability)
        current_showcase = re.search(
            r'<section class="section upcoming-showcase".*?</section>',
            home_text,
            flags=re.DOTALL,
        )
        if current_showcase:
            home_text = (
                home_text[:current_showcase.start()] + showcase
                + home_text[current_showcase.end():]
            )
        else:
            marker = '<section class="section v18-showcase"'
            if marker not in home_text:
                raise RuntimeError(f"No 1.8 showcase found in {home}")
            home_text = home_text.replace(marker, showcase + marker, 1)
        home.write_text(ensure_preview_stylesheet(home_text, home_prefix), encoding="utf-8")

        readme = root / "readme" / "index.html"
        text = readme.read_text(encoding="utf-8")
        language = html_language(text)
        text = update_release_cards(text, readme, current_availability)
        prefix = "../" if root == ROOT else "../../"
        text = update_feature_intro(text, language, prefix, visual_captions[0])
        intro = re.search(
            r'<section class="doc-content">.*?<h2>', text, flags=re.DOTALL
        )
        if intro:
            updated_intro = (
                intro.group(0)
                .replace("Record Picker v1.6 · macOS 1.0", "Record Picker 1.8")
                .replace("Record Picker v1.6 / macOS 1.0", "Record Picker 1.8")
                .replace("version 1.6", "version 1.8")
                .replace("Version 1.6", "Version 1.8")
                .replace("Mac 1.0", "Mac 1.8")
            )
            text = text[:intro.start()] + updated_intro + text[intro.end():]
        text = ensure_preview_stylesheet(text, prefix)
        readme.write_text(text, encoding="utf-8")

        screenshots = root / "screenshots" / "index.html"
        text = screenshots.read_text(encoding="utf-8")
        language = html_language(text)
        prefix = "../" if root == ROOT else "../../"
        text = ensure_preview_stylesheet(text, prefix)
        announcement = upcoming_gallery_intro(language, current_availability)
        current_announcement = re.search(
            r'<section class="media-section upcoming-gallery-intro".*?</section>',
            text,
            flags=re.DOTALL,
        )
        if current_announcement:
            text = (
                text[:current_announcement.start()] + announcement
                + text[current_announcement.end():]
            )
        else:
            marker = '<section class="media-section v18-screenshot-gallery"'
            if marker not in text:
                raise RuntimeError(f"No 1.8 gallery in {screenshots}")
            text = text.replace(marker, announcement + marker, 1)
        gallery = expanded_gallery(language, prefix, visual_captions)
        current = re.search(
            r'<section class="media-section v18-screenshot-gallery".*?</section>',
            text,
            flags=re.DOTALL,
        )
        if not current:
            raise RuntimeError(f"No 1.8 gallery in {screenshots}")
        text = text[:current.start()] + gallery + text[current.end():]
        text = re.sub(
            r'<section class="media-section watch-section">.*?</section>',
            "",
            text,
            flags=re.DOTALL,
        )
        screenshots.write_text(text, encoding="utf-8")

    for page in ROOT.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        updated = update_current_release_facts(replace_dark_mac_references(text))
        if updated != text:
            page.write_text(updated, encoding="utf-8")

    sections = (
        "support", "screenshots", "privacy", "manage-vinyl-collection",
        "readme", "mac-app", "choose-vinyl-record", "random-vinyl-record-picker",
    )
    for root in roots:
        pages = [root / "index.html"] + [root / section / "index.html" for section in sections]
        for page in pages:
            text = page.read_text(encoding="utf-8")
            language = html_language(text)
            relative_path = page.relative_to(root)
            page.write_text(
                repair_translations(text, language, relative_path, page),
                encoding="utf-8",
            )

    update_media_sitemap(roots)
    update_standard_sitemap()
    enhance_accessibility()

    print(
        f"Prepared {len(roots)} locales: macOS 1.9 available, other platforms "
        "coming soon, light visuals and expanded 1.8 galleries"
    )


if __name__ == "__main__":
    main()
