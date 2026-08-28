#!/usr/bin/env python3
"""Normalize internal URLs and refine metadata highlighted by Bing."""

from __future__ import annotations

from html import escape, unescape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

TITLE_OVERRIDES = {
    "screenshots/index.html": "Record Picker 2.3.2 Screenshots: Mac, iPhone & Watch",
    "fr/screenshots/index.html": "Aperçus Record Picker 2.3.2 : Mac, iPhone et Watch",
    "en-us/index.html": "Vinyl Collection App & Random Record Picker | Record Picker — US",
    "en-us/choose-vinyl-record/index.html": "How to Choose the Right Vinyl Record: 5 Quick Ways — US",
    "en-us/screenshots/index.html": "Record Picker 2.3.2 Screenshots: Mac, iPhone & Watch — US",
    "en-us/watch-app/index.html": "Apple Watch Random Record Picker | Record Picker — US",
}

DESCRIPTION_OVERRIDES = {
    "screenshots/index.html": (
        "See Record Picker 2.3.2 on Mac, iPhone, iPad and Apple Watch, including the catalog, Random Pick, "
        "Mood Pick and Today’s Pick."
    ),
    "fr/screenshots/index.html": (
        "Découvrez Record Picker 2.3.2 sur Mac, iPhone, iPad et Apple Watch : catalogue, tirage aléatoire, "
        "Mood Pick et Disque du jour."
    ),
    "en-us/index.html": (
        "Catalog vinyl records and CDs in the US, import Discogs, check duplicates, and use Random Pick, "
        "Mood Pick or Today’s Pick. Private, ad-free, and native."
    ),
    "en-us/choose-vinyl-record/index.html": (
        "Can’t decide what vinyl to play? Try five quick methods for US collectors, based on mood, a random "
        "pick, music news, collection rotation or one simple rule."
    ),
    "en-us/screenshots/index.html": (
        "See the US edition of Record Picker 2.3.2 on Mac, iPhone, iPad and Apple Watch, including "
        "the catalog, Random Pick, Mood Pick and Today’s Pick."
    ),
    "en-us/watch-app/index.html": (
        "US collectors can pick another record from their wrist with Random Pick, favorites and listening "
        "modes. Record Picker keeps vinyl and CD collections private and in sync."
    ),
    "es-mx/ios-app/index.html": (
        "Cataloga tus vinilos y CD en México y elige el próximo disco con una selección aleatoria "
        "personalizable, Mood Pick o el Disco del día. Tu colección permanece privada y sincronizada."
    ),
    "es-mx/watch-app/index.html": (
        "Elige otro álbum desde tu Apple Watch en México con Random Pick, favoritos y modos de escucha. "
        "Record Picker mantiene privada y sincronizada tu colección de vinilos y CD."
    ),
    "fr-ca/ios-app/index.html": (
        "Cataloguez vos vinyles et CD au Canada, puis choisissez le prochain disque avec le tirage aléatoire "
        "personnalisable, Mood Pick ou le Disque du jour. Collection privée et synchronisée."
    ),
    "fr-ca/watch-app/index.html": (
        "Au Canada, lancez un nouveau tirage Record Picker depuis l’Apple Watch avec vos favoris et modes "
        "d’écoute. Votre collection de vinyles et de CD reste privée et synchronisée."
    ),
    "fr-ca/windows-app/index.html": (
        "La future version Windows de Record Picker pour le Canada francophone est conçue indépendamment "
        "d’iCloud afin de préparer les transferts avec Android et les appareils Apple."
    ),
    "zh-hans/index.html": (
        "整理黑胶唱片与 CD，从 Discogs 导入收藏、检查重复项目并完善封面和资料，再通过可自定义的随机选择、Mood Pick 和今日唱片决定下一张听什么。"
        "Record Picker 原生支持 iPhone、iPad、Apple Watch 与 Mac，收藏保持私密、无广告，最多可免费管理 100 张唱片。"
    ),
    "zh-hant/index.html": (
        "整理黑膠唱片與 CD，從 Discogs 匯入收藏、檢查重複項目並完善封面與資料，再透過可自訂的隨機選擇、Mood Pick 和今日唱片決定下一張聽什麼。"
        "Record Picker 原生支援 iPhone、iPad、Apple Watch 與 Mac，收藏保持私密、無廣告，最多可免費管理 100 張唱片。"
    ),
    "ja/index.html": (
        "レコードとCDを整理し、Discogsからコレクションを読み込み、重複やジャケット情報を確認できます。カスタマイズ可能なランダム選択、Mood Pick、今日の一枚で、次に聴く作品を迷わず決定。"
        "iPhone、iPad、Apple Watch、Macに対応し、コレクションは非公開・広告なしで管理できます。"
    ),
    "ko/index.html": (
        "바이닐과 CD를 정리하고 Discogs에서 컬렉션을 가져오며 중복 항목과 커버 정보를 확인하세요. 맞춤 설정 가능한 무작위 선택, Mood Pick, 오늘의 음반으로 다음에 들을 앨범을 고를 수 있습니다. "
        "iPhone, iPad, Apple Watch, Mac에서 컬렉션을 비공개로 광고 없이 관리할 수 있습니다."
    ),
    "zh-hans/readme/index.html": (
        "了解 Record Picker 的全部功能：可自定义随机选择、Mood Pick、Discogs 导入、丰富编目、封面编辑、重复项目管理、iCloud 同步、CSV 导出与备份。"
        "应用原生支持 iPhone、iPad、Apple Watch 和 Mac，提供 32 种语言，最多可免费管理 100 张唱片。"
    ),
    "ko/support/index.html": (
        "Record Picker 사용 중 도움이 필요하신가요? Discogs 및 CSV 가져오기, iCloud 동기화, 백업과 복원, 중복 항목, 커버 이미지, Apple Watch, 구매 및 Pro 라이선스 문제에 대한 지원을 받으세요. "
        "문의는 support@recordpicker.app으로 보내 주세요."
    ),
    "ko/mac-app/index.html": (
        "Mac용 Record Picker로 바이닐과 CD 컬렉션을 정리하고 Discogs에서 가져오며 중복 항목과 커버를 관리하세요. Random Pick, Mood Pick, 오늘의 음반으로 오늘 밤 들을 앨범을 고를 수 있습니다. "
        "컬렉션은 비공개로 유지되며 Apple 기기와 iCloud로 동기화됩니다."
    ),
    "id/choose-vinyl-record/index.html": (
        "Panduan praktis untuk memilih piringan vinyl berikutnya tanpa terlalu lama menatap rak. Gunakan "
        "suasana hati, pilihan acak, berita musik, rotasi koleksi, atau satu batasan sederhana agar album "
        "yang jarang diputar kembali mendapat giliran."
    ),
}


def clean_index_links(text: str) -> str:
    return re.sub(
        r'href="((?:\.\./)*)index\.html(#[^"]*)?"',
        lambda found: f'href="{found.group(1) or "./"}{found.group(2) or ""}"',
        text,
    )


def replace_meta(text: str, relative: str) -> str:
    title = TITLE_OVERRIDES.get(relative)
    description = DESCRIPTION_OVERRIDES.get(relative)
    if not title and not description:
        return text

    if title:
        escaped_title = escape(title, quote=True)
        text = re.sub(r"<title>.*?</title>", f"<title>{escaped_title}</title>", text, count=1)
        for attribute in ('property="og:title"', 'name="twitter:title"', 'property="og:image:alt"', 'name="twitter:image:alt"'):
            text = re.sub(
                rf'(<meta {attribute} content=")[^"]*(")',
                rf'\g<1>{escaped_title}\2',
                text,
                count=1,
            )
    if description:
        escaped_description = escape(description, quote=True)
        for attribute in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
            text = re.sub(
                rf'(<meta {attribute} content=")[^"]*(")',
                rf'\g<1>{escaped_description}\2',
                text,
                count=1,
            )

    canonical_match = re.search(r'<link rel="canonical" href="([^"]+)"', text)
    canonical = canonical_match.group(1) if canonical_match else None

    def update_json(match: re.Match[str]) -> str:
        try:
            payload = json.loads(unescape(match.group(2)))
        except json.JSONDecodeError:
            return match.group(0)
        if canonical and payload.get("url") == canonical:
            if title and "name" in payload:
                payload["name"] = title
            if description and "description" in payload:
                payload["description"] = description
        for item in payload.get("@graph", []):
            if item.get("@type") == "BreadcrumbList" and title:
                for entry in item.get("itemListElement", []):
                    if entry.get("position") == 2:
                        entry["name"] = title
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        return f'{match.group(1)}{encoded}</script>'

    return re.sub(
        r'(<script type="application/ld\+json"[^>]*>)(.*?)</script>',
        update_json,
        text,
        flags=re.DOTALL,
    )


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        updated = replace_meta(clean_index_links(text), relative)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"Optimized Bing metadata and clean internal URLs on {changed} pages.")


if __name__ == "__main__":
    main()
