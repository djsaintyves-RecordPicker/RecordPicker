#!/usr/bin/env python3
"""Apply the August 2026 Google and Bing SEO corrections."""

from __future__ import annotations

from html import escape, unescape
from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://recordpicker.app"
TODAY = "2026-08-23"
LOCALE_LABELS = {
    "": "International", "ar": "العربية", "ca": "Català", "da": "Dansk",
    "de": "Deutsch", "el": "Ελληνικά", "en-au": "Australia",
    "en-ca": "Canada", "en-gb": "United Kingdom", "en-us": "United States",
    "es-es": "España", "es-mx": "México", "fi": "Suomi", "fr": "France",
    "fr-ca": "Canada français", "he": "עברית", "hi": "हिन्दी",
    "id": "Indonesia", "it": "Italiano", "ja": "日本語", "ko": "한국어",
    "nb": "Norsk", "nl": "Nederlands", "pl": "Polski", "pt-br": "Brasil",
    "pt-pt": "Portugal", "ru": "Русский", "sv": "Svenska", "th": "ไทย",
    "tr": "Türkçe", "vi": "Tiếng Việt", "zh-hans": "简体中文",
    "zh-hant": "繁體中文",
}
ENGLISH_MARKETS = {
    "en-au": ("Australia", "Australian English", "Australian App Store"),
    "en-ca": ("Canada", "Canadian English", "Canadian App Store"),
    "en-gb": ("the United Kingdom", "British English", "UK App Store"),
}


def page_locale(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return rel.parts[0] if len(rel.parts) > 1 and rel.parts[0] in LOCALE_LABELS else ""


def page_route(path: Path) -> str:
    rel = path.relative_to(ROOT)
    locale = page_locale(path)
    parts = rel.parts[1:] if locale else rel.parts
    if parts == ("index.html",):
        return ""
    return "/".join(parts[:-1]) + "/"


def public_url(path: Path) -> str:
    locale = page_locale(path)
    route = page_route(path)
    if locale == "en-us":
        counterpart = ROOT / route / "index.html" if route else ROOT / "index.html"
        if counterpart.exists():
            return SITE + "/" + route
    prefix = f"{locale}/" if locale else ""
    return SITE + "/" + prefix + route


def text_only(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def replace_metadata(text: str, title: str, description: str) -> str:
    values = {
        "title": title,
        "description": description,
        "og:title": title,
        "og:description": description,
        "og:image:alt": title,
        "twitter:title": title,
        "twitter:description": description,
        "twitter:image:alt": title,
    }
    text = re.sub(r"<title>.*?</title>", f"<title>{escape(title)}</title>", text, count=1, flags=re.DOTALL)
    for key, value in values.items():
        if key == "title":
            continue
        attr = "property" if key.startswith("og:") else "name"
        text = re.sub(
            rf'(<meta {attr}="{re.escape(key)}" content=")[^"]*(")',
            rf'\g<1>{escape(value, quote=True)}\2', text, count=1,
        )
    return text


def sync_international_guide() -> None:
    source = (ROOT / "en-us" / "choose-vinyl-record" / "index.html").read_text(encoding="utf-8")
    text = source.replace("../../", "../")
    text = text.replace(
        "https://recordpicker.app/en-us/choose-vinyl-record/",
        "https://recordpicker.app/choose-vinyl-record/",
    )
    text = replace_metadata(
        text,
        "How to Choose the Right Vinyl Record to Play",
        "Not sure which vinyl record to play? Use mood, chance, music news, collection rotation or one simple constraint to choose the right album in seconds.",
    )
    text = re.sub(
        r"<h1>.*?</h1>",
        "<h1>How to choose the right vinyl record to play</h1>",
        text, count=1, flags=re.DOTALL,
    )
    text = re.sub(
        r'(<p class="lead">).*?(</p>)',
        r"\1The right vinyl record depends on the moment, not on a perfect formula. Start with one useful constraint and turn a crowded shelf into an easy choice.\2",
        text, count=1, flags=re.DOTALL,
    )
    (ROOT / "choose-vinyl-record" / "index.html").write_text(text, encoding="utf-8")


def update_structured_urls(text: str, old: str, new: str) -> str:
    def rewrite(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)

        def walk(value: object) -> object:
            if isinstance(value, dict):
                return {key: walk(new if item == old and key in {"url", "@id", "mainEntityOfPage", "item"} else item) for key, item in value.items()}
            if isinstance(value, list):
                return [walk(item) for item in value]
            return value

        return '<script type="application/ld+json">' + json.dumps(walk(data), ensure_ascii=False, separators=(",", ":")) + "</script>"

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', rewrite, text, flags=re.DOTALL)


def regional_context(path: Path, text: str) -> str:
    locale = page_locale(path)
    if 'data-search-market' in text:
        return text
    route = page_route(path).strip("/") or "home"
    topics = {
        "home": "Record Picker overview", "support": "support page",
        "privacy": "privacy page", "screenshots": "screenshots page",
        "readme": "features page", "mac-app": "Mac app page",
        "ios-app": "iPhone and iPad app page", "watch-app": "Apple Watch app page",
        "android-app": "Android development page",
        "choose-vinyl-record": "vinyl choosing guide",
        "random-vinyl-record-picker": "random record picker guide",
        "manage-vinyl-collection": "collection management guide",
    }
    topic = topics.get(route, "Record Picker page")
    if locale in ENGLISH_MARKETS:
        market, spelling, store = ENGLISH_MARKETS[locale]
        section = (
            f'<section class="seo-section regional-search-context" data-search-market="{locale}">'
            f'<h2>Record Picker in {market}</h2>'
            f'<p>This {topic} uses {spelling} and links collectors to the {store}. '
            'Record Picker is free for collections of up to 100 records, with an optional one-time Pro unlock.</p></section>'
        )
    elif locale == "fr-ca":
        section = (
            '<section class="seo-section regional-search-context" data-search-market="fr-ca">'
            '<h2>Record Picker au Canada</h2>'
            f'<p>Cette page consacrée à {topic} utilise le français canadien et renvoie vers l’App Store canadien. '
            'Record Picker est gratuit jusqu’à 100 disques, avec un déverrouillage Pro facultatif et définitif.</p></section>'
        )
    else:
        return text
    return text.replace('</main>', section + '</main>', 1)


def image_description(src: str) -> str:
    name = Path(src.split("?", 1)[0]).stem.lower()
    descriptions = (
        ("iphone-todays-pick", "Today’s Pick on iPhone"),
        ("mac-todays-pick", "Today’s Pick on Mac"),
        ("watch-random-pick", "Random Pick on Apple Watch"),
        ("iphone-random", "Random Pick on iPhone"),
        ("mac-random", "Random Pick on Mac"),
        ("mood", "Mood Pick result"),
        ("barcode", "barcode record entry"),
        ("collection", "record collection catalogue"),
        ("mac-home", "Record Picker home screen on Mac"),
        ("iphone", "Record Picker on iPhone"),
        ("ipad", "Record Picker on iPad"),
        ("mac", "Record Picker on Mac"),
        ("watch", "Record Picker on Apple Watch"),
        ("icon", "Record Picker app icon"),
    )
    for marker, description in descriptions:
        if marker in name:
            return description
    return "Record Picker app interface"


def describe_images(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        before, after = match.group(1), match.group(2)
        attributes = before + after
        src = re.search(r'\bsrc="([^"]+)"', attributes)
        alt = image_description(src.group(1) if src else "")
        return f'<img{before} alt="{escape(alt, quote=True)}"{after}>'
    return re.sub(r'<img([^>]*?)\s+alt=""([^>]*)>', replace, text)


def extend_description(text: str, description: str, locale: str) -> str:
    if len(description) >= 110 or locale in {"ar", "he", "hi", "ja", "ko", "th", "zh-hans", "zh-hant"}:
        return description
    candidates = re.findall(r'<p(?: class="(?:deck|lead)")?[^>]*>(.*?)</p>', text, flags=re.DOTALL)
    for candidate in candidates:
        addition = text_only(candidate)
        if addition and addition.lower() not in description.lower():
            combined = (description.rstrip(" .") + ". " + addition).strip()
            return combined[:157].rsplit(" ", 1)[0].rstrip(" ,;:") + "."
    return description


def shorten_title(title: str, locale: str) -> str:
    if len(title) <= 60:
        return title
    suffix = " — " + (locale or "Record Picker")
    base = re.sub(r"\s+[—|-]\s+(?:Record Picker|[^—|]{2,20})$", "", title).strip()
    room = 60 - len(suffix)
    head = base[:room].rsplit(" ", 1)[0].rstrip(" —|-:,.?")
    return head + suffix


def update_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    locale = page_locale(path)
    old_canonical_match = re.search(r'<link rel="canonical" href="([^"]+)">', text)
    if not old_canonical_match:
        return
    old_canonical = old_canonical_match.group(1)
    canonical = public_url(path)
    text = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{canonical}">', text, count=1)
    text = re.sub(r'<meta property="og:url" content="[^"]+">', f'<meta property="og:url" content="{canonical}">', text, count=1)
    text = update_structured_urls(text, old_canonical, canonical)

    route = page_route(path)
    counterpart = ROOT / route / "index.html" if route else ROOT / "index.html"
    root_route = SITE + "/" + route if counterpart.exists() else public_url(path)
    text = re.sub(
        r'<link rel="alternate" hreflang="en-US" href="[^"]+">',
        f'<link rel="alternate" hreflang="en-US" href="{root_route}">', text, count=1,
    )
    text = re.sub(
        r'<link rel="alternate" hreflang="x-default" href="[^"]+">',
        f'<link rel="alternate" hreflang="x-default" href="{root_route}">', text, count=1,
    )

    title_match = re.search(r'<title>(.*?)</title>', text, flags=re.DOTALL)
    desc_match = re.search(r'<meta name="description" content="([^"]*)">', text)
    if title_match and desc_match:
        title = text_only(title_match.group(1))
        description = unescape(desc_match.group(1))
        route = page_route(path).strip("/")
        if route in {"ios-app", "watch-app", "android-app"} and locale not in {"", "en-us"}:
            label = LOCALE_LABELS[locale]
            title = re.sub(r"(?: — " + re.escape(label) + r")+$", "", title) + " — " + label
        title = shorten_title(title, locale)
        description = extend_description(text, description, locale)
        text = replace_metadata(text, title, description)

    text = regional_context(path, text)
    text = describe_images(text)
    path.write_text(text, encoding="utf-8")


def deduplicate_descriptions(paths: list[Path]) -> None:
    groups: dict[str, list[Path]] = {}
    for path in paths:
        if page_locale(path) == "en-us":
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r'<meta name="description" content="([^"]*)">', text)
        if match:
            groups.setdefault(unescape(match.group(1)), []).append(path)
    for description, members in groups.items():
        if len(members) < 2:
            continue
        for path in members:
            text = path.read_text(encoding="utf-8")
            title = text_only(re.search(r'<title>(.*?)</title>', text, flags=re.DOTALL).group(1))
            label = LOCALE_LABELS[page_locale(path)]
            qualifier = f" {label}."
            adjusted = description.rstrip(" .")
            if len(adjusted) + len(qualifier) > 160:
                adjusted = adjusted[: 160 - len(qualifier)].rsplit(" ", 1)[0]
            path.write_text(replace_metadata(text, title, adjusted + qualifier), encoding="utf-8")


def deduplicate_titles(paths: list[Path]) -> None:
    groups: dict[str, list[Path]] = {}
    for path in paths:
        if page_locale(path) == "en-us" and public_url(path) != SITE + "/en-us/" + page_route(path):
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r'<title>(.*?)</title>', text, flags=re.DOTALL)
        if match:
            groups.setdefault(text_only(match.group(1)), []).append(path)
    for _, members in groups.items():
        if len(members) < 2:
            continue
        for path in members:
            text = path.read_text(encoding="utf-8")
            heading = re.search(r'<h1[^>]*>(.*?)</h1>', text, flags=re.DOTALL)
            description = unescape(re.search(r'<meta name="description" content="([^"]*)">', text).group(1))
            route = page_route(path).strip("/").replace("-", " ")
            title = text_only(heading.group(1)) if heading else route.title()
            if len(title) > 60:
                title = shorten_title(title, page_locale(path))
            path.write_text(replace_metadata(text, title, description), encoding="utf-8")


def trim_sitemap(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r'\s*<url>.*?</url>', text, flags=re.DOTALL)
    kept = []
    for block in blocks:
        loc = re.search(r'<loc>([^<]+)</loc>', block)
        if not loc:
            continue
        url = loc.group(1)
        if "/en-us/" in url:
            route = url.split("/en-us/", 1)[1]
            counterpart = ROOT / route / "index.html" if route else ROOT / "index.html"
            if counterpart.exists():
                continue
        block = re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{TODAY}</lastmod>', block)
        kept.append(re.sub(r'\n\s*\n+', '\n', block.strip()))
    present = {
        match.group(1)
        for block in kept
        if (match := re.search(r'<loc>([^<]+)</loc>', block))
    }
    canonicals = set()
    for page in ROOT.rglob("index.html"):
        if any(part.startswith(".") for part in page.relative_to(ROOT).parts):
            continue
        match = re.search(r'<link rel="canonical" href="([^"]+)">', page.read_text(encoding="utf-8"))
        if match:
            canonicals.add(match.group(1))
    for url in sorted(canonicals - present):
        kept.append(f'<url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>')
    prefix = re.sub(r'\n\s*\n+', '\n', text[: text.find("<url>")].rstrip())
    path.write_text(prefix + "\n" + "\n".join(kept) + "\n</urlset>\n", encoding="utf-8")


def main() -> None:
    sync_international_guide()
    paths = [path for path in ROOT.rglob("index.html") if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)]
    for path in paths:
        update_page(path)
    deduplicate_descriptions(paths)
    deduplicate_titles(paths)
    for name in ("sitemap.xml", "sitemap-media.xml"):
        trim_sitemap(ROOT / name)
    print(f"Applied search-engine improvements to {len(paths)} pages.")


if __name__ == "__main__":
    main()
