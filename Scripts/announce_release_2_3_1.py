#!/usr/bin/env python3
"""Stage the Record Picker 2.3.1 announcement on every localized site."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re

from announce_release_2_1 import COMING_SOON


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "data" / "release-state.json"
VERSION = "2.3.1"


@dataclass(frozen=True)
class Copy:
    headline: str
    points: tuple[str, ...]


# Site directory -> App Store locale key. The root site is English.
LOCALES = {
    "": "en-US", "ar": "ar-SA", "ca": "ca", "da": "da", "de": "de-DE",
    "el": "el", "en-au": "en-AU", "en-ca": "en-CA", "en-gb": "en-GB",
    "en-us": "en-US", "es-es": "es-ES", "es-mx": "es-MX", "fi": "fi",
    "fr": "fr-FR", "fr-ca": "fr-CA", "he": "he", "hi": "hi", "id": "id",
    "it": "it", "ja": "ja", "ko": "ko", "nb": "no", "nl": "nl-NL",
    "pl": "pl", "pt-br": "pt-BR", "pt-pt": "pt-PT", "ru": "ru",
    "sv": "sv", "th": "th", "tr": "tr", "vi": "vi",
    "zh-hans": "zh-Hans", "zh-hant": "zh-Hant",
}


EN = Copy(
    "Take your whole collection with you.",
    (
        "A new portable .recordpicker file will carry your collection, wishlist, favourites, custom artwork and pick history.",
        "Export, import and verify it on iPhone, iPad and Mac; JSON and CSV remain available.",
        "Designed independently of iCloud, ready for future transfers with Android and Windows.",
    ),
)

COPY = {
    "ar-SA": Copy("اصطحب مجموعتك كاملة معك.", ("ملف .recordpicker محمول جديد يضم مجموعتك وقائمة أمنياتك ومفضلاتك والأغلفة المخصصة وسجل الاختيارات.", "صدّره واستورده وتحقق منه على iPhone وiPad وMac، مع بقاء JSON وCSV متاحين.", "مصمم بصورة مستقلة عن iCloud استعدادًا للنقل مستقبلًا مع Android وWindows.")),
    "ca": Copy("Emporta’t tota la col·lecció.", ("Un nou fitxer portàtil .recordpicker inclourà la col·lecció, la llista de desitjos, els favorits, les portades personalitzades i l’historial de seleccions.", "Exporta’l, importa’l i verifica’l a l’iPhone, l’iPad i el Mac; JSON i CSV continuaran disponibles.", "Dissenyat independentment d’iCloud i preparat per a futures transferències amb Android i Windows.")),
    "da": Copy("Tag hele din samling med dig.", ("En ny bærbar .recordpicker-fil rummer din samling, ønskeliste, favoritter, egne omslag og valghistorik.", "Eksportér, importér og kontrollér den på iPhone, iPad og Mac; JSON og CSV er stadig tilgængelige.", "Udviklet uafhængigt af iCloud og klar til fremtidige overførsler med Android og Windows.")),
    "de-DE": Copy("Nimm deine ganze Sammlung mit.", ("Eine neue portable .recordpicker-Datei enthält deine Sammlung, Wunschliste, Favoriten, eigenen Cover und Auswahlhistorie.", "Exportiere, importiere und prüfe sie auf iPhone, iPad und Mac; JSON und CSV bleiben verfügbar.", "Unabhängig von iCloud entwickelt und bereit für künftige Übertragungen mit Android und Windows.")),
    "el": Copy("Πάρε ολόκληρη τη συλλογή σου μαζί σου.", ("Ένα νέο φορητό αρχείο .recordpicker θα περιλαμβάνει τη συλλογή, τη λίστα επιθυμιών, τα αγαπημένα, τα προσαρμοσμένα εξώφυλλα και το ιστορικό επιλογών.", "Εξαγωγή, εισαγωγή και επαλήθευση σε iPhone, iPad και Mac· τα JSON και CSV παραμένουν διαθέσιμα.", "Σχεδιασμένο ανεξάρτητα από το iCloud, έτοιμο για μελλοντικές μεταφορές με Android και Windows.")),
    "es-ES": Copy("Llévate toda tu colección contigo.", ("Un nuevo archivo portátil .recordpicker incluirá tu colección, lista de deseos, favoritos, carátulas personalizadas e historial de selecciones.", "Expórtalo, impórtalo y verifícalo en iPhone, iPad y Mac; JSON y CSV seguirán disponibles.", "Diseñado de forma independiente de iCloud y preparado para futuras transferencias con Android y Windows.")),
    "es-MX": Copy("Lleva toda tu colección contigo.", ("Un nuevo archivo portátil .recordpicker incluirá tu colección, lista de deseos, favoritos, portadas personalizadas e historial de selecciones.", "Expórtalo, impórtalo y verifícalo en iPhone, iPad y Mac; JSON y CSV seguirán disponibles.", "Diseñado de forma independiente de iCloud y listo para futuras transferencias con Android y Windows.")),
    "fi": Copy("Ota koko kokoelmasi mukaan.", ("Uusi siirrettävä .recordpicker-tiedosto sisältää kokoelman, toivelistan, suosikit, omat kansikuvat ja valintahistorian.", "Vie, tuo ja tarkista se iPhonessa, iPadissa ja Macissa; JSON ja CSV säilyvät käytettävissä.", "iCloudista riippumaton rakenne valmistautuu tuleviin Android- ja Windows-siirtoihin.")),
    "fr-FR": Copy("Emportez toute votre collection avec vous.", ("Un nouveau fichier portable .recordpicker réunira votre collection, votre liste de souhaits, vos favoris, vos pochettes personnalisées et l’historique des tirages.", "Exportez-le, importez-le et vérifiez-le sur iPhone, iPad et Mac ; JSON et CSV restent disponibles.", "Conçu indépendamment d’iCloud, il prépare les futurs transferts avec Android et Windows.")),
    "fr-CA": Copy("Emportez toute votre collection avec vous.", ("Un nouveau fichier portable .recordpicker réunira votre collection, votre liste de souhaits, vos favoris, vos pochettes personnalisées et l’historique des tirages.", "Exportez-le, importez-le et vérifiez-le sur iPhone, iPad et Mac; JSON et CSV restent disponibles.", "Conçu indépendamment d’iCloud, il prépare les futurs transferts avec Android et Windows.")),
    "he": Copy("קחו את כל האוסף איתכם.", ("קובץ .recordpicker נייד חדש יכיל את האוסף, רשימת המשאלות, המועדפים, העטיפות המותאמות והיסטוריית הבחירות.", "ניתן יהיה לייצא, לייבא ולאמת אותו ב‑iPhone, ב‑iPad וב‑Mac; ‏JSON ו‑CSV יישארו זמינים.", "עוצב ללא תלות ב‑iCloud ומוכן להעברות עתידיות עם Android ו‑Windows.")),
    "hi": Copy("अपना पूरा संग्रह अपने साथ ले जाएँ।", ("नई पोर्टेबल .recordpicker फ़ाइल में आपका संग्रह, इच्छा सूची, पसंदीदा, कस्टम कवर और चयन इतिहास शामिल होंगे।", "इसे iPhone, iPad और Mac पर निर्यात, आयात और सत्यापित करें; JSON और CSV उपलब्ध रहेंगे।", "iCloud से स्वतंत्र रूप से बनाया गया, ताकि भविष्य में Android और Windows के साथ स्थानांतरण हो सके।")),
    "id": Copy("Bawa seluruh koleksi Anda.", ("File portabel .recordpicker baru akan memuat koleksi, daftar keinginan, favorit, sampul khusus, dan riwayat pilihan Anda.", "Ekspor, impor, dan verifikasi di iPhone, iPad, dan Mac; JSON dan CSV tetap tersedia.", "Dirancang independen dari iCloud dan siap untuk transfer mendatang dengan Android dan Windows.")),
    "it": Copy("Porta con te tutta la tua collezione.", ("Un nuovo file portatile .recordpicker includerà collezione, lista dei desideri, preferiti, copertine personalizzate e cronologia delle estrazioni.", "Esportalo, importalo e verificalo su iPhone, iPad e Mac; JSON e CSV restano disponibili.", "Progettato indipendentemente da iCloud e pronto per futuri trasferimenti con Android e Windows.")),
    "ja": Copy("コレクション全体を持ち運べます。", ("新しいポータブルな .recordpicker ファイルに、コレクション、ウィッシュリスト、お気に入り、カスタムアートワーク、選択履歴をまとめます。", "iPhone、iPad、Mac で書き出し、読み込み、検証が可能。JSON と CSV も引き続き利用できます。", "iCloud に依存しない設計で、将来の Android／Windows との転送にも備えます。")),
    "ko": Copy("전체 컬렉션을 어디서나 가져가세요.", ("새로운 휴대용 .recordpicker 파일에 컬렉션, 위시리스트, 즐겨찾기, 사용자 지정 커버와 선택 기록이 담깁니다.", "iPhone, iPad, Mac에서 내보내고 가져오고 검증할 수 있으며 JSON과 CSV도 계속 지원됩니다.", "iCloud와 독립적으로 설계되어 향후 Android 및 Windows 전송을 준비합니다.")),
    "no": Copy("Ta med deg hele samlingen.", ("En ny bærbar .recordpicker-fil vil inneholde samlingen, ønskelisten, favorittene, egne omslag og valghistorikken din.", "Eksporter, importer og kontroller den på iPhone, iPad og Mac; JSON og CSV forblir tilgjengelig.", "Utformet uavhengig av iCloud og klar for fremtidige overføringer med Android og Windows.")),
    "nl-NL": Copy("Neem je hele collectie mee.", ("Een nieuw draagbaar .recordpicker-bestand bevat je collectie, verlanglijst, favorieten, eigen hoezen en keuzehistorie.", "Exporteer, importeer en controleer het op iPhone, iPad en Mac; JSON en CSV blijven beschikbaar.", "Onafhankelijk van iCloud ontworpen en klaar voor toekomstige overdrachten met Android en Windows.")),
    "pl": Copy("Zabierz całą kolekcję ze sobą.", ("Nowy przenośny plik .recordpicker pomieści kolekcję, listę życzeń, ulubione, własne okładki i historię losowań.", "Eksportuj, importuj i weryfikuj go na iPhonie, iPadzie i Macu; JSON i CSV pozostają dostępne.", "Format niezależny od iCloud, gotowy na przyszłe transfery z Androidem i Windowsem.")),
    "pt-BR": Copy("Leve toda a sua coleção com você.", ("Um novo arquivo portátil .recordpicker reunirá coleção, lista de desejos, favoritos, capas personalizadas e histórico de escolhas.", "Exporte, importe e verifique no iPhone, iPad e Mac; JSON e CSV continuarão disponíveis.", "Projetado de forma independente do iCloud e pronto para futuras transferências com Android e Windows.")),
    "pt-PT": Copy("Leve toda a sua coleção consigo.", ("Um novo ficheiro portátil .recordpicker reunirá a coleção, a lista de desejos, os favoritos, as capas personalizadas e o histórico de escolhas.", "Exporte, importe e verifique no iPhone, iPad e Mac; JSON e CSV continuarão disponíveis.", "Concebido de forma independente do iCloud e preparado para futuras transferências com Android e Windows.")),
    "ru": Copy("Берите всю коллекцию с собой.", ("Новый переносимый файл .recordpicker объединит коллекцию, список желаний, избранное, собственные обложки и историю выбора.", "Экспортируйте, импортируйте и проверяйте его на iPhone, iPad и Mac; JSON и CSV останутся доступны.", "Независимый от iCloud формат готовит будущий перенос на Android и Windows.")),
    "sv": Copy("Ta med dig hela samlingen.", ("En ny portabel .recordpicker-fil samlar din samling, önskelista, favoriter, egna omslag och valhistorik.", "Exportera, importera och verifiera den på iPhone, iPad och Mac; JSON och CSV finns kvar.", "Utformad oberoende av iCloud och redo för framtida överföringar med Android och Windows.")),
    "th": Copy("พกคอลเลกชันทั้งหมดไปกับคุณ", ("ไฟล์ .recordpicker แบบพกพาใหม่จะรวมคอลเลกชัน รายการที่อยากได้ รายการโปรด ปกที่กำหนดเอง และประวัติการสุ่มของคุณ", "ส่งออก นำเข้า และตรวจสอบบน iPhone, iPad และ Mac ได้ โดยยังคงรองรับ JSON และ CSV", "ออกแบบให้เป็นอิสระจาก iCloud และพร้อมสำหรับการถ่ายโอนกับ Android และ Windows ในอนาคต")),
    "tr": Copy("Tüm koleksiyonunuzu yanınızda taşıyın.", ("Yeni taşınabilir .recordpicker dosyası koleksiyonunuzu, istek listenizi, favorilerinizi, özel kapakları ve seçim geçmişini kapsayacak.", "iPhone, iPad ve Mac’te dışa aktarın, içe aktarın ve doğrulayın; JSON ve CSV kullanılmaya devam edecek.", "iCloud’dan bağımsız tasarlandı ve gelecekte Android ile Windows aktarımlarına hazır.")),
    "vi": Copy("Mang theo toàn bộ bộ sưu tập của bạn.", ("Tệp .recordpicker di động mới sẽ chứa bộ sưu tập, danh sách mong muốn, mục yêu thích, ảnh bìa tùy chỉnh và lịch sử lựa chọn.", "Xuất, nhập và xác minh trên iPhone, iPad và Mac; JSON và CSV vẫn được hỗ trợ.", "Được thiết kế độc lập với iCloud, sẵn sàng cho việc chuyển dữ liệu với Android và Windows trong tương lai.")),
    "zh-Hans": Copy("随身携带您的完整收藏。", ("新的便携式 .recordpicker 文件将包含收藏、愿望清单、收藏夹、自定义封面和抽选历史。", "可在 iPhone、iPad 和 Mac 上导出、导入并验证；JSON 和 CSV 仍然可用。", "独立于 iCloud 设计，为将来与 Android 和 Windows 传输做好准备。")),
    "zh-Hant": Copy("隨身攜帶您的完整收藏。", ("新的可攜式 .recordpicker 檔案將包含收藏、願望清單、喜好項目、自訂封面和抽選紀錄。", "可在 iPhone、iPad 和 Mac 上匯出、匯入並驗證；JSON 和 CSV 仍然可用。", "採用獨立於 iCloud 的設計，為未來與 Android 和 Windows 傳輸做好準備。")),
}
for locale in ("en-AU", "en-CA", "en-GB", "en-US"):
    COPY[locale] = EN


def block(text: str, version: str, tag: str) -> re.Match[str] | None:
    return re.search(rf'<{tag}\b[^>]*data-release-version="{re.escape(version)}"[^>]*>.*?</{tag}>', text, re.DOTALL)


def items(copy: Copy) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in copy.points)


def home(copy: Copy, status: str) -> str:
    return (f'<section class="section v231-preview next-release" id="versions" data-release-version="{VERSION}">'
            f'<div class="section-head"><p class="kicker">{escape(status)}</p><h2>Record Picker {VERSION}</h2>'
            f'<p class="lead">{escape(copy.headline)}</p></div><div class="v20-preview-panel"><ul>{items(copy)}</ul></div></section>')


def history(copy: Copy, status: str) -> str:
    platforms = f"{status} · iPhone · iPad · Apple Watch · Mac"
    return (f'<article class="release-card release-preview release-upcoming v231-release-card" data-release-version="{VERSION}">'
            f'<div class="release-head"><span class="version-pill">v{VERSION}</span><div><h3>{escape(copy.headline)}</h3>'
            f'<p class="release-platform-summary"><strong>{escape(platforms)}</strong></p></div></div><ul>{items(copy)}</ul></article>')


def screenshots(copy: Copy, status: str) -> str:
    return (f'<section class="media-section next-release v231-gallery-marker" data-release-version="{VERSION}">'
            f'<div class="section-head"><p class="kicker">{escape(status)}</p><h2>Record Picker {VERSION}</h2>'
            f'<p class="lead">{escape(copy.headline)}</p></div></section>')


def stage_locale(directory: str, locale: str) -> int:
    root = ROOT / directory if directory else ROOT
    copy, status = COPY[locale], COMING_SOON[locale]
    changed = 0
    for rel, tag, builder in (("index.html", "section", home), ("readme/index.html", "article", history), ("screenshots/index.html", "section", screenshots)):
        path = root / rel
        text = path.read_text(encoding="utf-8")
        if block(text, VERSION, tag):
            continue
        current = block(text, "2.3", tag)
        if rel == "screenshots/index.html" and not current:
            current = re.search(r'<section\b[^>]*data-release-gallery="2\.3"[^>]*>.*?</section>', text, re.DOTALL)
        if not current:
            raise RuntimeError(f"Missing current 2.3 block in {path}")
        if rel == "index.html":
            text = text.replace('id="versions" data-release-version="2.3"', 'id="version-2-3-preview" data-release-version="2.3"', 1)
        text = text[:current.start()] + builder(copy, status) + current.group(0) + text[current.end():]
        path.write_text(text, encoding="utf-8")
        changed += 1
    return changed


def update_state() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if state["current_release"]["version"] != "2.3":
        raise RuntimeError("2.3 must remain the current release while 2.3.1 is staged")
    state["next_release"] = {"version": VERSION, "platforms": {platform: "coming_soon" for platform in ("iphone", "ipad", "mac", "watch")}}
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    missing = set(LOCALES.values()) - set(COPY)
    if missing:
        raise RuntimeError(f"Missing localized copy: {sorted(missing)}")
    changed = sum(stage_locale(directory, locale) for directory, locale in LOCALES.items())
    update_state()
    print(f"Announced Record Picker {VERSION} across {changed} localized pages.")


if __name__ == "__main__":
    main()
