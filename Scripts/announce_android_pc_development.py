#!/usr/bin/env python3
"""Announce the Android and PC work on every localized home page."""

from __future__ import annotations

from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

# Short, deliberately non-dated copy: the site announces active development
# without promising a release window that has not yet been set.
COPY = {
    "": ("In development", "Record Picker for Android and PC", "Release details will be announced when both versions are ready."),
    "ar": ("قيد التطوير", "Record Picker لنظام Android والكمبيوتر الشخصي", "سيتم الإعلان عن تفاصيل الإصدار عندما تصبح النسختان جاهزتين."),
    "ca": ("En desenvolupament", "Record Picker per a Android i PC", "Els detalls del llançament s’anunciaran quan totes dues versions estiguin preparades."),
    "da": ("Under udvikling", "Record Picker til Android og PC", "Udgivelsesdetaljer annonceres, når begge versioner er klar."),
    "de": ("In Entwicklung", "Record Picker für Android und PC", "Details zur Veröffentlichung folgen, sobald beide Versionen fertig sind."),
    "el": ("Υπό ανάπτυξη", "Record Picker για Android και PC", "Οι λεπτομέρειες κυκλοφορίας θα ανακοινωθούν όταν είναι έτοιμες και οι δύο εκδόσεις."),
    "en-au": ("In development", "Record Picker for Android and PC", "Release details will be announced when both versions are ready."),
    "en-ca": ("In development", "Record Picker for Android and PC", "Release details will be announced when both versions are ready."),
    "en-gb": ("In development", "Record Picker for Android and PC", "Release details will be announced when both versions are ready."),
    "en-us": ("In development", "Record Picker for Android and PC", "Release details will be announced when both versions are ready."),
    "es-es": ("En desarrollo", "Record Picker para Android y PC", "Los detalles del lanzamiento se anunciarán cuando ambas versiones estén listas."),
    "es-mx": ("En desarrollo", "Record Picker para Android y PC", "Los detalles del lanzamiento se anunciarán cuando ambas versiones estén listas."),
    "fi": ("Kehitteillä", "Record Picker Androidille ja PC:lle", "Julkaisutiedot kerrotaan, kun molemmat versiot ovat valmiita."),
    "fr": ("En développement", "Record Picker pour Android et PC", "Les informations de sortie seront annoncées lorsque les deux versions seront prêtes."),
    "fr-ca": ("En développement", "Record Picker pour Android et PC", "Les détails du lancement seront annoncés lorsque les deux versions seront prêtes."),
    "he": ("בפיתוח", "Record Picker ל-Android ולמחשב PC", "פרטי ההשקה יפורסמו כששתי הגרסאות יהיו מוכנות."),
    "hi": ("विकास जारी है", "Android और PC के लिए Record Picker", "दोनों संस्करण तैयार होने पर रिलीज़ की जानकारी घोषित की जाएगी।"),
    "id": ("Dalam pengembangan", "Record Picker untuk Android dan PC", "Detail peluncuran akan diumumkan saat kedua versi siap."),
    "it": ("In sviluppo", "Record Picker per Android e PC", "I dettagli sul lancio saranno annunciati quando entrambe le versioni saranno pronte."),
    "ja": ("開発中", "Android／PC版 Record Picker", "両バージョンの準備が整い次第、リリースの詳細をお知らせします。"),
    "ko": ("개발 중", "Android 및 PC용 Record Picker", "두 버전이 준비되면 출시 세부 정보를 안내하겠습니다."),
    "nb": ("Under utvikling", "Record Picker for Android og PC", "Lanseringsdetaljer kunngjøres når begge versjonene er klare."),
    "nl": ("In ontwikkeling", "Record Picker voor Android en pc", "De releasedetails worden bekendgemaakt zodra beide versies klaar zijn."),
    "pl": ("W trakcie tworzenia", "Record Picker na Androida i PC", "Szczegóły premiery zostaną ogłoszone, gdy obie wersje będą gotowe."),
    "pt-br": ("Em desenvolvimento", "Record Picker para Android e PC", "Os detalhes do lançamento serão anunciados quando as duas versões estiverem prontas."),
    "pt-pt": ("Em desenvolvimento", "Record Picker para Android e PC", "Os detalhes do lançamento serão anunciados quando ambas as versões estiverem prontas."),
    "ru": ("В разработке", "Record Picker для Android и ПК", "Подробности о выпуске появятся, когда обе версии будут готовы."),
    "sv": ("Under utveckling", "Record Picker för Android och PC", "Lanseringsinformation meddelas när båda versionerna är klara."),
    "th": ("อยู่ระหว่างการพัฒนา", "Record Picker สำหรับ Android และ PC", "เราจะประกาศรายละเอียดการเปิดตัวเมื่อทั้งสองเวอร์ชันพร้อมใช้งาน"),
    "tr": ("Geliştirme aşamasında", "Android ve PC için Record Picker", "Her iki sürüm de hazır olduğunda çıkış ayrıntıları duyurulacak."),
    "vi": ("Đang phát triển", "Record Picker cho Android và PC", "Thông tin phát hành sẽ được công bố khi cả hai phiên bản sẵn sàng."),
    "zh-hans": ("正在开发", "Android 和 PC 版 Record Picker", "两个版本准备就绪后将公布发布详情。"),
    "zh-hant": ("開發中", "Android 與 PC 版 Record Picker", "兩個版本準備就緒後將公布發佈詳情。"),
}

ANNOUNCEMENT = re.compile(
    r'<section class="platform-expansion"[^>]*>.*?</section>', flags=re.DOTALL
)
FACTS = re.compile(r'<section class="facts-band">.*?</section>', flags=re.DOTALL)


def announcement(locale: str) -> str:
    kicker, title, detail = COPY[locale]
    return (
        '<section class="platform-expansion" aria-labelledby="platform-expansion-title">'
        '<div class="platform-expansion-copy">'
        f'<p class="kicker">{escape(kicker)}</p>'
        f'<h2 id="platform-expansion-title">{escape(title)}</h2>'
        f'<p>{escape(detail)}</p></div>'
        f'<div class="platform-expansion-badges" aria-label="{escape(title)}">'
        '<span>Android</span><span>PC</span>'
        f'<small>{escape(kicker)}</small></div></section>'
    )


def update(locale: str) -> bool:
    path = ROOT / locale / "index.html" if locale else ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    block = announcement(locale)
    if ANNOUNCEMENT.search(text):
        updated = ANNOUNCEMENT.sub(block, text, count=1)
    else:
        facts = FACTS.search(text)
        if not facts:
            raise RuntimeError(f"Facts band not found in {path}")
        updated = text[:facts.end()] + block + text[facts.end():]
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def refresh_stylesheet_version(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'quality\.css\?v=[^"\']+',
        'quality.css?v=20260822-platform-expansion',
        text,
    )
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = sum(update(locale) for locale in COPY)
    refreshed = sum(refresh_stylesheet_version(path) for path in ROOT.rglob("*.html"))
    print(
        f"Announced Android and PC development on {changed} localized home pages "
        f"and refreshed styles on {refreshed} pages."
    )


if __name__ == "__main__":
    main()
