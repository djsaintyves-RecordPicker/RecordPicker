#!/usr/bin/env python3
"""Repair the international English canonicals and current search snippets."""

from __future__ import annotations

from html import escape, unescape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://recordpicker.app"
LASTMOD = "2026-09-21"
RELEASE_SCHEMA_DATE = "2026-09-17"

INTERNATIONAL_PAGES = {
    "readme": (
        "Record Picker Features: Vinyl & CD Collection Tools",
        "Explore Record Picker’s vinyl and CD cataloguing, Discogs import, duplicate checks, Random Pick, Mood Pick, Today’s Pick, backup and export tools.",
    ),
    "support": (
        "Record Picker Support: Import, Sync, Backup & Pro",
        "Get help with Record Picker imports, backups, iCloud sync, Apple Watch, purchases, Pro access and managing a private vinyl or CD collection.",
    ),
    "privacy": (
        "Record Picker Privacy: Local, Private and Ad-Free",
        "Learn how Record Picker keeps your vinyl and CD catalogue private, with local storage, private iCloud sync, no advertising and no data selling.",
    ),
    "random-vinyl-record-picker": (
        "Random Vinyl Record Picker: Smart, Filtered Picks",
        "Pick a vinyl record at random while respecting genres, favourites, exclusions and less-played albums. Try Record Picker free with up to 100 records.",
    ),
    "manage-vinyl-collection": (
        "How to Manage and Rediscover a Vinyl Collection",
        "Learn how to catalogue vinyl and CDs, prevent duplicate purchases, preserve pressing details, back up your data and rediscover overlooked records.",
    ),
}

PRIORITY_METADATA = {
    "choose-vinyl-record/index.html": (
        "How to Choose the Right Vinyl Record to Play (5 Ways)",
        "Choosing a vinyl record? Use mood, genre, listening time, collection rotation or a random picker to find the right album to play in seconds.",
    ),
    "ar/windows-app/index.html": (
        None,
        "نزّل Record Picker 2.5 من Microsoft Store لنظام Windows 11 على أجهزة x64 وARM64، ونظّم مجموعة الأسطوانات والأقراص المدمجة واختر ما ستستمع إليه ومن دون إعلانات.",
    ),
    "ca/windows-app/index.html": (
        None,
        "Descarrega Record Picker 2.5 des de Microsoft Store per a Windows 11 en PC x64 i ARM64, cataloga vinils i CD i tria fàcilment què vols escoltar, sense anuncis.",
    ),
    "zh-hant/windows-app/index.html": (
        None,
        "從 Microsoft Store 下載適用於 Windows 11 x64 與 ARM64 電腦的 Record Picker 2.5，整理黑膠唱片與 CD 收藏，搜尋專輯、檢查重複項目，並透過隨機選擇快速決定下一張要播放的專輯。收藏保留在你的裝置上，介面清楚且無廣告，也可安心匯入、編輯與瀏覽完整的實體音樂收藏資料。",
    ),
    "fi/windows-app/index.html": (
        None,
        "Lataa Record Picker 2.5 Microsoft Storesta Windows 11 -tietokoneille (x64 ja ARM64), luetteloi vinyylit ja CD:t ja valitse seuraava levy ilman mainoksia.",
    ),
    "he/windows-app/index.html": (
        None,
        "הורידו את Record Picker 2.5 מ-Microsoft Store למחשבי Windows 11 מסוג x64 ו-ARM64, קטלגו תקליטים ותקליטורים ובחרו בקלות מה לשמוע עכשיו, ללא פרסומות ובפרטיות.",
    ),
    "fr/windows-app/index.html": (
        None,
        "Téléchargez Record Picker 2.5 sur Microsoft Store pour Windows 11, sur PC x64 et ARM64, puis cataloguez vos vinyles et choisissez quoi écouter, sans publicité.",
    ),
    "ko/windows-app/index.html": (
        None,
        "Microsoft Store에서 Windows 11 x64 및 ARM64 PC용 Record Picker 2.5를 다운로드하세요. 바이닐과 CD를 정리하고 중복 항목을 확인하며 무작위 선택으로 다음 음반을 고르세요. 또한 컬렉션은 기기에 안전하게 보관되며 광고가 없습니다.",
    ),
    "ru/windows-app/index.html": (
        None,
        "Скачайте Record Picker 2.5 из Microsoft Store для Windows 11 на ПК x64 и ARM64, каталогизируйте винил и CD и легко выбирайте следующий альбом без рекламы.",
    ),
    "ru/privacy/index.html": (
        None,
        "Record Picker хранит каталог винила и CD локально на устройстве, не продаёт данные и не показывает рекламу. Синхронизация iCloud всегда остаётся приватной.",
    ),
    "en-us/support/index.html": (
        None,
        "Get Record Picker help for Discogs and CSV imports, backups, iCloud sync, Apple Watch, purchases, Pro access and managing a private vinyl or CD collection.",
    ),
    "zh-hant/manage-vinyl-collection/index.html": (
        None,
        "學習如何使用 Record Picker 整理黑膠唱片與 CD、避免重複購買、保存版本與壓片資料、補充封面與收藏資訊、建立可恢復的備份，並透過播放紀錄與隨機選擇重新發現長時間沒有播放的專輯。這份實用指南適合想讓實體音樂收藏保持清楚、完整且容易瀏覽的收藏者，也能協助你規劃聆聽、匯出資料並長期維護每張唱片的準確資訊。",
    ),
    "windows-app/index.html": (
        None,
        "Download Record Picker 2.5 from Microsoft Store for Windows 11 on x64 or ARM64 PCs. Catalog vinyl and CDs, search your collection and choose what to play without ads.",
    ),
    "en-us/windows-app/index.html": (
        None,
        "Download Record Picker 2.5 in the US from Microsoft Store for Windows 11 on x64 or ARM64 PCs. Catalog vinyl and CDs and choose what to play without ads.",
    ),
    "en-au/windows-app/index.html": (
        None,
        "Download Record Picker 2.5 in Australia from Microsoft Store for Windows 11 on x64 or ARM64 PCs. Catalogue vinyl and CDs and choose what to play without ads.",
    ),
    "en-ca/windows-app/index.html": (
        None,
        "Download Record Picker 2.5 in Canada from Microsoft Store for Windows 11 on x64 or ARM64 PCs. Catalogue vinyl and CDs and choose what to play without ads.",
    ),
    "en-gb/windows-app/index.html": (
        None,
        "Download Record Picker 2.5 in the UK from Microsoft Store for Windows 11 on x64 or ARM64 PCs. Catalogue vinyl and CDs and choose what to play without ads.",
    ),
}


def replace_metadata(text: str, title: str | None, description: str) -> str:
    if title:
        encoded_title = escape(title, quote=True)
        text = re.sub(r"<title>.*?</title>", f"<title>{encoded_title}</title>", text, count=1, flags=re.DOTALL)
        for attribute in ("og:title", "og:image:alt", "twitter:title", "twitter:image:alt"):
            kind = "property" if attribute.startswith("og:") else "name"
            text = re.sub(
                rf'(<meta {kind}="{re.escape(attribute)}" content=")[^"]*(")',
                rf'\g<1>{encoded_title}\2',
                text,
                count=1,
            )

    encoded_description = escape(description, quote=True)
    for attribute in ("description", "og:description", "twitter:description"):
        kind = "property" if attribute.startswith("og:") else "name"
        text = re.sub(
            rf'(<meta {kind}="{re.escape(attribute)}" content=")[^"]*(")',
            rf'\g<1>{encoded_description}\2',
            text,
            count=1,
        )
    return text


def rewrite_schema_metadata(text: str, canonical: str, title: str | None, description: str) -> str:
    def update(match: re.Match[str]) -> str:
        try:
            payload = json.loads(unescape(match.group(2)))
        except json.JSONDecodeError:
            return match.group(0)

        def visit(value: object) -> None:
            if isinstance(value, dict):
                same_page = value.get("url") == canonical or value.get("@id") == canonical
                if same_page:
                    if title and "name" in value:
                        value["name"] = title
                    if "description" in value:
                        value["description"] = description
                    if value.get("@type") == "SoftwareApplication" and "dateModified" in value:
                        value["dateModified"] = RELEASE_SCHEMA_DATE
                if value.get("@type") == "BreadcrumbList" and title:
                    for item in value.get("itemListElement", []):
                        if isinstance(item, dict) and item.get("position") == 2:
                            item["name"] = title
                for nested in value.values():
                    visit(nested)
            elif isinstance(value, list):
                for nested in value:
                    visit(nested)

        visit(payload)
        return match.group(1) + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "</script>"

    return re.sub(
        r'(<script type="application/ld\+json"[^>]*>)(.*?)</script>',
        update,
        text,
        flags=re.DOTALL,
    )


def neutralize_international_page(route: str, title: str, description: str) -> Path:
    source = ROOT / "en-us" / route / "index.html"
    target = ROOT / route / "index.html"
    text = source.read_text(encoding="utf-8").replace("../../", "../")
    canonical = f"{SITE}/{route}/"
    source_url = f"{SITE}/en-us/{route}/"
    text = text.replace(source_url, canonical)
    text = replace_metadata(text, title, description)
    text = rewrite_schema_metadata(text, canonical, title, description)
    target.write_text(text, encoding="utf-8")
    return target


def root_counterpart(href: str) -> str | None:
    if href == "/en-us/":
        return "/" if (ROOT / "index.html").exists() else None
    prefix = "/en-us/"
    if not href.startswith(prefix):
        return None
    route = href[len(prefix):].strip("/")
    target = ROOT / route / "index.html"
    return f"/{route}/" if target.exists() else None


def point_english_menu_to_canonical(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        replacement = root_counterpart(match.group(1))
        return f'href="{replacement}"' if replacement else match.group(0)

    return re.sub(r'href="(/en-us/(?:[^"]*)?)"', replace, text)


def canonicalize_en_us_duplicates() -> set[Path]:
    changed: set[Path] = set()
    for path in (ROOT / "en-us").rglob("index.html"):
        route = path.relative_to(ROOT / "en-us").parent.as_posix()
        counterpart = ROOT / route / "index.html" if route != "." else ROOT / "index.html"
        if not counterpart.exists():
            continue
        canonical = SITE + (f"/{route}/" if route != "." else "/")
        text = path.read_text(encoding="utf-8")
        old_match = re.search(r'<link rel="canonical" href="([^"]+)">', text)
        old = old_match.group(1) if old_match else None
        updated = re.sub(
            r'<link rel="canonical" href="[^"]+">',
            f'<link rel="canonical" href="{canonical}">',
            text,
            count=1,
        )
        updated = re.sub(
            r'<meta property="og:url" content="[^"]+">',
            f'<meta property="og:url" content="{canonical}">',
            updated,
            count=1,
        )
        updated = re.sub(
            r'<link rel="alternate" hreflang="en-US" href="[^"]+">',
            f'<link rel="alternate" hreflang="en-US" href="{canonical}">',
            updated,
            count=1,
        )
        updated = re.sub(
            r'<link rel="alternate" hreflang="x-default" href="[^"]+">',
            f'<link rel="alternate" hreflang="x-default" href="{canonical}">',
            updated,
            count=1,
        )
        if old and old != canonical:
            def replace_schema(match: re.Match[str]) -> str:
                try:
                    payload = json.loads(unescape(match.group(2)))
                except json.JSONDecodeError:
                    return match.group(0)

                def visit(value: object) -> None:
                    if isinstance(value, dict):
                        for key, item in tuple(value.items()):
                            if key in {"url", "@id", "mainEntityOfPage", "item"} and item == old:
                                value[key] = canonical
                            else:
                                visit(item)
                    elif isinstance(value, list):
                        for item in value:
                            visit(item)

                visit(payload)
                return match.group(1) + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "</script>"

            updated = re.sub(
                r'(<script type="application/ld\+json"[^>]*>)(.*?)</script>',
                replace_schema,
                updated,
                flags=re.DOTALL,
            )
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.add(path)
    return changed


def remove_duplicate_en_us_sitemap_entries(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    def keep_or_remove(match: re.Match[str]) -> str:
        block = match.group(0)
        loc = re.search(r'<loc>([^<]+)</loc>', block)
        if not loc or "/en-us/" not in loc.group(1):
            return block
        route = loc.group(1).split("/en-us/", 1)[1].strip("/")
        counterpart = ROOT / route / "index.html" if route else ROOT / "index.html"
        return "" if counterpart.exists() else block

    updated = re.sub(r'\s*<url>.*?</url>', keep_or_remove, text, flags=re.DOTALL)
    path.write_text(updated.replace("</url><url>", "</url>\n<url>"), encoding="utf-8")


def update_sitemap_lastmod(path: Path, urls: set[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for url in urls:
        text = re.sub(
            rf'(<url>.*?<loc>{re.escape(url)}</loc>.*?<lastmod>)[^<]+(</lastmod>)',
            rf'\g<1>{LASTMOD}\2',
            text,
            count=1,
            flags=re.DOTALL,
        )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    content_changed: set[Path] = set()
    for route, (title, description) in INTERNATIONAL_PAGES.items():
        content_changed.add(neutralize_international_page(route, title, description))

    for relative, (title, description) in PRIORITY_METADATA.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        canonical = re.search(r'<link rel="canonical" href="([^"]+)">', text)
        updated = replace_metadata(text, title, description)
        if canonical:
            updated = rewrite_schema_metadata(updated, canonical.group(1), title, description)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            content_changed.add(path)

    content_changed.update(canonicalize_en_us_duplicates())

    menu_changed = 0
    for path in ROOT.rglob("*.html"):
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            continue
        text = path.read_text(encoding="utf-8")
        updated = point_english_menu_to_canonical(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            menu_changed += 1

    changed_urls = set()
    for path in content_changed:
        text = path.read_text(encoding="utf-8")
        canonical = re.search(r'<link rel="canonical" href="([^"]+)">', text)
        if canonical:
            changed_urls.add(canonical.group(1))
    for sitemap in (ROOT / "sitemap.xml", ROOT / "sitemap-media.xml"):
        remove_duplicate_en_us_sitemap_entries(sitemap)
        update_sitemap_lastmod(sitemap, changed_urls)

    print(
        f"Updated {len(content_changed)} SEO content pages, canonicalised English menu links "
        f"on {menu_changed} HTML files, and touched {len(changed_urls)} sitemap URLs."
    )


if __name__ == "__main__":
    main()
