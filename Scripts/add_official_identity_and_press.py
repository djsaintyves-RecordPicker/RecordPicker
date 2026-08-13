#!/usr/bin/env python3
"""Publish Record Picker's official identity links and press-kit entry point."""

from __future__ import annotations

from html import unescape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://recordpicker.app/"
LOGO_URL = SITE_URL + "assets/brand/icon-512.png"
SOCIALS = [
    "https://www.instagram.com/recordpicker/",
]

PRESS_LABELS = {
    "ar": "الملف الصحفي",
    "ca": "Dossier de premsa",
    "da": "Pressemateriale",
    "de": "Pressemappe",
    "el": "Υλικό Τύπου",
    "es-es": "Kit de prensa",
    "es-mx": "Kit de prensa",
    "fi": "Lehdistöaineisto",
    "fr": "Dossier de presse",
    "fr-ca": "Dossier de presse",
    "he": "ערכת עיתונות",
    "hi": "प्रेस किट",
    "id": "Kit pers",
    "it": "Cartella stampa",
    "ja": "プレスキット",
    "ko": "프레스 키트",
    "nb": "Pressepakke",
    "nl": "Persmap",
    "pl": "Materiały prasowe",
    "pt-br": "Kit de imprensa",
    "pt-pt": "Kit de imprensa",
    "ru": "Пресс-кит",
    "sv": "Pressmaterial",
    "th": "ชุดสื่อมวลชน",
    "tr": "Basın kiti",
    "vi": "Bộ tài liệu báo chí",
    "zh-hans": "媒体资料包",
    "zh-hant": "媒體資料包",
}


def locale_for(page: Path, text: str) -> str:
    match = re.search(r'data-page-lang="([^"]+)"', text)
    return match.group(1) if match else "fr"


def normalize_schema(value: object) -> None:
    if isinstance(value, dict):
        if value.get("@type") == "SoftwareApplication":
            value["name"] = "Record Picker"
            value["image"] = LOGO_URL
            value["sameAs"] = SOCIALS
            value["publisher"] = {
                "@type": "Organization",
                "name": "Record Picker",
                "url": SITE_URL,
                "logo": {"@type": "ImageObject", "url": LOGO_URL},
                "sameAs": SOCIALS,
            }
        elif value.get("@type") == "Organization":
            value["name"] = "Record Picker"
            value["url"] = SITE_URL
            value["logo"] = {"@type": "ImageObject", "url": LOGO_URL}
            value["sameAs"] = SOCIALS
        for child in value.values():
            normalize_schema(child)
    elif isinstance(value, list):
        for child in value:
            normalize_schema(child)


def update_schemas(text: str) -> str:
    pattern = re.compile(
        r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)',
        flags=re.DOTALL,
    )

    def replacement(match: re.Match[str]) -> str:
        schema = json.loads(unescape(match.group(2)))
        normalize_schema(schema)
        payload = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        return match.group(1) + payload + match.group(3)

    return pattern.sub(replacement, text)


def update_footer(text: str, locale: str) -> str:
    # Keep a single, canonical URL for each official profile.
    text = re.sub(
        r'https://(?:www\.)?instagram\.com/recordpicker/?', SOCIALS[0], text
    )
    missing: list[str] = []
    if 'href="/press/"' not in text:
        label = PRESS_LABELS.get(locale, "Press kit")
        missing.append(f'<a href="/press/">{label}</a>')
    for url, label in zip(SOCIALS, ("Instagram",)):
        if f'href="{url}" rel="me"' not in text:
            missing.append(f'<a href="{url}" rel="me">{label}</a>')
    if missing:
        text = text.replace("</nav></footer>", "".join(missing) + "</nav></footer>", 1)
    return text


def build_press_page() -> None:
    template = (ROOT / "support" / "index.html").read_text(encoding="utf-8")
    title = "Dossier de presse / Press kit - Record Picker"
    description = (
        "Téléchargez le dossier de presse officiel Record Picker, les visuels et "
        "les informations vérifiées sur l’app pour iPhone, iPad, Mac et Apple Watch."
    )
    template = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", template, count=1)
    template = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{description}">',
        template,
        count=1,
    )
    for prop in ("og:title", "twitter:title"):
        template = re.sub(
            rf'(<meta (?:property|name)="{prop}" content=")[^"]*(">)',
            rf"\g<1>{title}\g<2>",
            template,
            count=1,
        )
    for prop in ("og:description", "twitter:description"):
        template = re.sub(
            rf'(<meta (?:property|name)="{prop}" content=")[^"]*(">)',
            rf"\g<1>{description}\g<2>",
            template,
            count=1,
        )
    template = template.replace(
        '<meta property="og:url" content="https://recordpicker.app/support/">',
        '<meta property="og:url" content="https://recordpicker.app/press/">',
    )
    template = template.replace(
        '<link rel="canonical" href="https://recordpicker.app/support/">',
        '<link rel="canonical" href="https://recordpicker.app/press/">',
    )
    template = template.replace(
        '"url":"https://recordpicker.app/support/"',
        '"url":"https://recordpicker.app/press/"',
        1,
    )
    template = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">', "", template)
    canonical = "https://recordpicker.app/press/"
    template = template.replace(
        '<link rel="canonical" href="https://recordpicker.app/press/">',
        '<link rel="canonical" href="https://recordpicker.app/press/">'
        f'<link rel="alternate" hreflang="x-default" href="{canonical}">',
    )

    main = '''<main id="main-content" class="doc-shell press-page"><section class="doc-hero"><p class="glass-pill eyebrow">Record Picker</p><h1>Dossier de presse <span lang="en">/ Press kit</span></h1><p class="doc-tagline">Informations officielles, documents prêts à l’emploi et visuels haute définition.</p><div class="doc-actions"><a class="button primary" href="/assets/press/Record-Picker-Dossier-de-presse-FR.pdf">Télécharger en français</a><a class="button glass" href="/assets/press/Record-Picker-Press-Kit-EN.pdf" lang="en">Download in English</a></div></section><section class="doc-content"><p class="doc-meta">Record Picker · Août 2026</p><p class="lead">Record Picker est une app Apple native pour cataloguer et redécouvrir une collection de vinyles et de CD sur iPhone, iPad, Mac et Apple Watch.</p><div class="press-download-grid"><article class="card"><h2>Dossier de presse français</h2><p>Présentation, fonctions principales, confidentialité, modèle économique et fiche technique.</p><a class="button glass" href="/assets/press/Record-Picker-Dossier-de-presse-FR.pdf">PDF · 5 pages</a></article><article class="card" lang="en"><h2>English press kit</h2><p>Official overview, key features, privacy, business model, and essential product facts.</p><a class="button glass" href="/assets/press/Record-Picker-Press-Kit-EN.pdf">PDF · 5 pages</a></article><article class="card"><h2>Archive complète</h2><p>Les deux dossiers, les textes de présentation et huit visuels de presse prêts à télécharger.</p><a class="button glass" href="/assets/press/Record-Picker-Press-Kit.zip">ZIP · PDF, textes et visuels</a></article></div><section class="official-identity" aria-labelledby="official-identity-title"><img src="/assets/brand/icon-512.png" width="160" height="160" alt="Logo officiel Record Picker"><div><p class="kicker">Identité officielle</p><h2 id="official-identity-title">Record Picker</h2><p><a href="https://recordpicker.app/">recordpicker.app</a></p><nav class="official-social-links" aria-label="Profil officiel Record Picker"><a href="https://www.instagram.com/recordpicker/" rel="me">Instagram · @recordpicker</a></nav></div></section><h2>Contact presse</h2><p>Yves Durand · <a href="mailto:djsaintyves@mac.com">djsaintyves@mac.com</a></p><p>Pour l’assistance produit : <a href="mailto:support@recordpicker.app">support@recordpicker.app</a>.</p></section></main>'''
    template = re.sub(r"<main\b.*?</main>", main, template, count=1, flags=re.DOTALL)

    page_schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": title,
                "url": canonical,
                "description": description,
                "about": {
                    "@type": "Organization",
                    "name": "Record Picker",
                    "url": SITE_URL,
                    "logo": {"@type": "ImageObject", "url": LOGO_URL},
                    "sameAs": SOCIALS,
                },
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Record Picker", "item": SITE_URL},
                    {"@type": "ListItem", "position": 2, "name": "Press kit", "item": canonical},
                ],
            },
        ],
    }
    payload = json.dumps(page_schema, ensure_ascii=False, separators=(",", ":"))
    template = re.sub(
        r'(<script type="application/ld\+json" id="page-schema">).*?(</script>)',
        rf"\g<1>{payload}\g<2>",
        template,
        count=1,
        flags=re.DOTALL,
    )
    target = ROOT / "press" / "index.html"
    target.parent.mkdir(exist_ok=True)
    target.write_text(template, encoding="utf-8")


def add_sitemap_entry(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "https://recordpicker.app/press/" in text:
        return
    entry = "  <url>\n    <loc>https://recordpicker.app/press/</loc>\n    <lastmod>2026-08-09</lastmod>\n  </url>\n"
    path.write_text(text.replace("</urlset>", entry + "</urlset>"), encoding="utf-8")


def main() -> None:
    build_press_page()
    pages = sorted(ROOT.rglob("*.html"))
    for page in pages:
        text = page.read_text(encoding="utf-8")
        text = re.sub(
            r"quality\.css\?v=[^\"']+",
            "quality.css?v=20260809-identity",
            text,
        )
        text = update_schemas(text)
        text = update_footer(text, locale_for(page, text))
        page.write_text(text, encoding="utf-8")
    add_sitemap_entry(ROOT / "sitemap.xml")
    add_sitemap_entry(ROOT / "sitemap-media.xml")
    print(f"Updated {len(pages)} pages with official identity and press links.")


if __name__ == "__main__":
    main()
