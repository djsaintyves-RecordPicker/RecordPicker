#!/usr/bin/env python3
"""Add the French Mac4Ever article to French-language site pages only."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_URL = (
    "https://www.mac4ever.com/audio/197509-cette-application-vous-aide-a-"
    "redecouvrir-les-vinyles-et-cd-oublies-dans-vos-etageres"
)
ARTICLE_TITLE = (
    "Cette application vous aide à redécouvrir les vinyles et CD oubliés "
    "sur vos étagères"
)
ARTICLE_QUOTE = (
    "L’idée de faire remonter les albums oubliés d’une collection est plutôt "
    "pertinente, surtout lorsque celle-ci commence à compter plusieurs "
    "centaines de références."
)
ON_MAG_URL = (
    "https://forum.on-mag.fr/threads/record-picker-une-app-sans-ia-ni-abonnement-"
    "pour-saider-%C3%A0-choisir-ses-%C3%A9coutes-vinyles-cd-dans-sa-propre-collection.960/"
)
ON_MAG_TITLE = (
    "Record Picker : une app sans IA ni abonnement pour s’aider à choisir ses "
    "écoutes vinyles & CD dans sa propre collection"
)

LOCALES = {
    "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
    "es-es", "es-mx", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja",
    "ko", "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "th", "tr", "vi",
    "zh-hans", "zh-hant",
}
FRENCH_LOCALES = {"fr", "fr-ca"}

PRESS_REVIEW_LABELS = {
    "ar": "تغطية صحفية", "ca": "Ressenyes de premsa", "da": "Presseomtale",
    "de": "Pressestimmen", "el": "Δημοσιεύματα Τύπου",
    "en-au": "Press review", "en-ca": "Press review", "en-gb": "Press review",
    "en-us": "Press review", "es-es": "Reseñas de prensa", "es-mx": "Reseñas de prensa",
    "fi": "Lehdistöarviot", "fr": "Revue de presse", "fr-ca": "Revue de presse",
    "he": "סיקור בתקשורת", "hi": "प्रेस समीक्षा", "id": "Ulasan pers",
    "it": "Rassegna stampa", "ja": "メディア掲載", "ko": "언론 보도",
    "nb": "Presseomtale", "nl": "Persrecensies", "pl": "Recenzje prasowe",
    "pt-br": "Resenhas na imprensa", "pt-pt": "Críticas na imprensa",
    "ru": "Пресса о нас", "sv": "Pressrecensioner", "th": "ข่าวจากสื่อ",
    "tr": "Basında", "vi": "Báo chí nói về Record Picker", "zh-hans": "媒体报道",
    "zh-hant": "媒體報導",
}

READ_LABELS = {
    "ar": "اقرأ المقال بالفرنسية على Mac4Ever",
    "ca": "Llegiu l’article en francès a Mac4Ever",
    "da": "Læs den franske artikel på Mac4Ever",
    "de": "Französischen Artikel bei Mac4Ever lesen",
    "el": "Διαβάστε το άρθρο στα γαλλικά στο Mac4Ever",
    "en-au": "Read the French article on Mac4Ever",
    "en-ca": "Read the French article on Mac4Ever",
    "en-gb": "Read the French article on Mac4Ever",
    "en-us": "Read the French article on Mac4Ever",
    "es-es": "Leer el artículo en francés en Mac4Ever",
    "es-mx": "Leer el artículo en francés en Mac4Ever",
    "fi": "Lue ranskankielinen artikkeli Mac4Everissä",
    "fr": "Lire l’article sur Mac4Ever",
    "fr-ca": "Lire l’article sur Mac4Ever",
    "he": "קראו את הכתבה בצרפתית ב‑Mac4Ever",
    "hi": "Mac4Ever पर फ़्रेंच लेख पढ़ें",
    "id": "Baca artikel berbahasa Prancis di Mac4Ever",
    "it": "Leggi l’articolo in francese su Mac4Ever",
    "ja": "Mac4Everでフランス語の記事を読む",
    "ko": "Mac4Ever에서 프랑스어 기사 읽기",
    "nb": "Les den franske artikkelen på Mac4Ever",
    "nl": "Lees het Franstalige artikel op Mac4Ever",
    "pl": "Przeczytaj artykuł po francusku w Mac4Ever",
    "pt-br": "Leia o artigo em francês no Mac4Ever",
    "pt-pt": "Leia o artigo em francês no Mac4Ever",
    "ru": "Прочитать статью на французском на Mac4Ever",
    "sv": "Läs den franska artikeln på Mac4Ever",
    "th": "อ่านบทความภาษาฝรั่งเศสบน Mac4Ever",
    "tr": "Mac4Ever’daki Fransızca makaleyi okuyun",
    "vi": "Đọc bài viết tiếng Pháp trên Mac4Ever",
    "zh-hans": "在 Mac4Ever 阅读法语文章",
    "zh-hant": "在 Mac4Ever 閱讀法文文章",
}


def locale_for(page: Path, text: str) -> str:
    match = re.search(r'data-page-lang="([^"]+)"', text)
    if match:
        return match.group(1)
    html_lang = re.search(r'<html\s+lang="([^"]+)"', text, flags=re.IGNORECASE)
    if html_lang:
        language = html_lang.group(1).casefold()
        if language == "fr-ca":
            return "fr-ca"
        if language.startswith("fr"):
            return "fr"
        return language
    relative = page.relative_to(ROOT)
    return relative.parts[0] if relative.parts and relative.parts[0] in LOCALES else "fr"


def review_spotlight(locale: str) -> str:
    label = PRESS_REVIEW_LABELS.get(locale, "Press review")
    read = READ_LABELS.get(locale, "Read the French article on Mac4Ever")
    visual_locale = locale if locale in LOCALES else "fr"
    visual = f"/assets/screenshots/v20/{visual_locale}/mac-mood-pick"
    return (
        '<section class="section press-review-spotlight" aria-labelledby="press-review-title">'
        '<div class="press-review-copy">'
        f'<p class="kicker">{escape(label)}</p>'
        f'<h2 id="press-review-title" lang="fr">{escape(ARTICLE_TITLE)}</h2>'
        '<p class="press-review-byline">Mac4Ever · '
        '<time datetime="2026-08-11">11 août 2026</time></p>'
        f'<blockquote lang="fr">“{escape(ARTICLE_QUOTE)}”</blockquote>'
        f'<a class="button glass" href="{ARTICLE_URL}" target="_blank" '
        f'rel="noopener external">{escape(read)} <span aria-hidden="true">↗</span></a>'
        '</div><figure class="press-review-visual">'
        f'<picture><source srcset="{visual}.avif" type="image/avif">'
        f'<source srcset="{visual}.webp" type="image/webp">'
        f'<img loading="lazy" alt="" src="{visual}.webp" '
        'width="1440" height="900" decoding="async"></picture>'
        '</figure></section>'
    )


def build_review_page() -> None:
    template = (ROOT / "press" / "index.html").read_text(encoding="utf-8")
    title = "Revue de presse - Record Picker"
    description = (
        "Les articles consacrés à Record Picker, l’app Apple qui aide à cataloguer "
        "et redécouvrir une collection de vinyles et de CD."
    )
    canonical = "https://recordpicker.app/press/reviews/"
    template = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", template, count=1)
    template = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{description}">', template, count=1,
    )
    for prop in ("og:title", "twitter:title"):
        template = re.sub(
            rf'(<meta (?:property|name)="{prop}" content=")[^"]*(">)',
            rf"\g<1>{title}\g<2>", template, count=1,
        )
    for prop in ("og:description", "twitter:description"):
        template = re.sub(
            rf'(<meta (?:property|name)="{prop}" content=")[^"]*(">)',
            rf"\g<1>{description}\g<2>", template, count=1,
        )
    template = re.sub(
        r'<meta property="og:url" content="[^"]+">',
        f'<meta property="og:url" content="{canonical}">', template, count=1,
    )
    template = re.sub(
        r'<link rel="canonical" href="[^"]+">',
        f'<link rel="canonical" href="{canonical}">', template, count=1,
    )
    template = re.sub(
        r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">', "", template,
    )
    template = template.replace(
        f'<link rel="canonical" href="{canonical}">',
        f'<link rel="canonical" href="{canonical}">'
        f'<link rel="alternate" hreflang="x-default" href="{canonical}">',
        1,
    )
    template = re.sub(
        r'<div class="header-actions">.*?</header>',
        '<div class="header-actions"><a class="store-link" '
        'href="https://apps.apple.com/fr/app/recordpicker/id6780422305" '
        'data-app-store-link>App Store</a><span class="language-trigger press-language-pill" '
        'aria-label="Français">Français</span>'
        '</div></header>',
        template,
        count=1,
        flags=re.DOTALL,
    )
    main = (
        '<main id="main-content" class="doc-shell press-review-page">'
        '<section class="doc-hero"><p class="glass-pill eyebrow">Record Picker</p>'
        '<h1>Revue de presse</h1>'
        '<p class="doc-tagline">Les médias parlent de Record Picker.</p>'
        '<div class="doc-actions"><a class="button primary" href="/press/">Dossier de presse</a>'
        '<a class="button glass" href="/fr/readme/#version-history">Versions disponibles</a></div></section>'
        '<section class="doc-content"><p class="press-kit-status" role="note">Les liens ci-dessous '
        'mènent vers des articles publiés à leurs dates respectives. Pour la version, les tarifs et '
        'les plateformes actuellement disponibles, consultez <a href="/fr/readme/#version-history">les '
        'versions de Record Picker</a>.</p><article class="press-review-entry">'
        '<div class="press-review-copy"><p class="kicker">Mac4Ever</p>'
        f'<h2 lang="fr">{escape(ARTICLE_TITLE)}</h2>'
        '<p class="press-review-byline">Laurence · '
        '<time datetime="2026-08-11">11 août 2026</time> · Audio</p>'
        '<p>Mac4Ever présente les trois façons de choisir un disque, le graphe adapté '
        'à la musique classique, les apps natives sur les quatre plateformes Apple et '
        'le modèle sans publicité, sans suivi et sans abonnement.</p>'
        f'<blockquote lang="fr">“{escape(ARTICLE_QUOTE)}”</blockquote>'
        f'<a class="button primary" href="{ARTICLE_URL}" target="_blank" '
        'rel="noopener external">Lire l’article original sur Mac4Ever '
        '<span aria-hidden="true">↗</span></a></div>'
        '<figure class="press-review-visual"><picture>'
        '<source srcset="/assets/screenshots/v301/fr/mac-mood-pick.avif" type="image/avif">'
        '<source srcset="/assets/screenshots/v301/fr/mac-mood-pick.webp" type="image/webp">'
        '<img alt="Mac · Record Picker 3.0.1 · FR" src="/assets/screenshots/v301/fr/mac-mood-pick.webp" width="1600" '
        'height="1004" decoding="async"></picture></figure></article>'
        '<article class="press-review-entry"><div class="press-review-copy"><p class="kicker">ON-mag</p>'
        f'<h2 lang="fr">{escape(ON_MAG_TITLE)}</h2>'
        '<p class="press-review-byline">Nicanor Haon · <time datetime="2026-10-07">7 octobre 2026</time> · Audio</p>'
        '<p>ON-mag revient sur Record Picker comme une app dédiée aux collections physiques : '
        'catalogue, choix d’écoute aléatoire, Mood Pick, Disque du jour et outils pour explorer sa bibliothèque.</p>'
        f'<a class="button primary" href="{ON_MAG_URL}" target="_blank" rel="noopener external">'
        'Lire l’article original sur ON-mag <span aria-hidden="true">↗</span></a></div>'
        '<figure class="press-review-visual"><picture>'
        '<source srcset="/assets/screenshots/v301/fr/mac-collection.avif" type="image/avif">'
        '<source srcset="/assets/screenshots/v301/fr/mac-collection.webp" type="image/webp">'
        '<img alt="Mac · Record Picker 3.0.1 · FR" src="/assets/screenshots/v301/fr/mac-collection.webp" '
        'width="1600" height="1004" loading="lazy" decoding="async"></picture></figure></article>'
        '</section></main>'
    )
    template = re.sub(r"<main\b.*?</main>", main, template, count=1, flags=re.DOTALL)
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage", "name": title, "url": canonical,
                "description": description,
                "about": {"@type": "SoftwareApplication", "name": "Record Picker"},
                "hasPart": [
                    {
                        "@type": "NewsArticle", "url": ARTICLE_URL,
                        "headline": ARTICLE_TITLE, "datePublished": "2026-08-11",
                        "inLanguage": "fr", "author": {"@type": "Person", "name": "Laurence"},
                        "publisher": {"@type": "Organization", "name": "Mac4Ever",
                                      "url": "https://www.mac4ever.com/"},
                    },
                    {
                        "@type": "NewsArticle", "url": ON_MAG_URL,
                        "headline": ON_MAG_TITLE, "datePublished": "2026-10-07",
                        "inLanguage": "fr", "author": {"@type": "Person", "name": "Nicanor Haon"},
                        "publisher": {"@type": "Organization", "name": "ON-mag",
                                      "url": "https://www.on-mag.fr/"},
                    },
                ],
            },
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Record Picker",
                 "item": "https://recordpicker.app/"},
                {"@type": "ListItem", "position": 2, "name": "Dossier de presse",
                 "item": "https://recordpicker.app/press/"},
                {"@type": "ListItem", "position": 3, "name": "Revue de presse",
                 "item": canonical},
            ]},
        ],
    }
    payload = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    template = re.sub(
        r'(<script type="application/ld\+json" id="page-schema">).*?(</script>)',
        rf"\g<1>{payload}\g<2>", template, count=1, flags=re.DOTALL,
    )
    # The page lives one level below the press-kit landing page. Keep all
    # inherited site navigation and shared assets rooted at the site root.
    template = template.replace('href="../', 'href="../../')
    template = template.replace('src="../', 'src="../../')
    template = template.replace('srcset="../', 'srcset="../../')
    target = ROOT / "press" / "reviews" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template, encoding="utf-8")


def update_page(page: Path) -> bool:
    text = page.read_text(encoding="utf-8")
    original = text
    locale = locale_for(page, text)
    is_french = locale in FRENCH_LOCALES
    label = PRESS_REVIEW_LABELS.get(locale, "Press review")
    if not is_french:
        text = re.sub(r'<a href="/press/reviews/">.*?</a>', "", text)
    elif 'href="/press/reviews/"' not in text:
        press_link = re.search(r'<a href="/press/">.*?</a>', text)
        if press_link:
            text = text[:press_link.start()] + (
                f'<a href="/press/reviews/">{escape(label)}</a>'
            ) + text[press_link.start():]
    relative = page.relative_to(ROOT)
    is_home = relative == Path("index.html") or (
        len(relative.parts) == 2 and relative.parts[0] in LOCALES
        and relative.parts[1] == "index.html"
    )
    if is_home:
        if not is_french:
            text = re.sub(
                r'<section class="section press-review-spotlight".*?</section>',
                "",
                text,
                count=1,
                flags=re.DOTALL,
            )
        elif 'class="section press-review-spotlight"' in text:
            spotlight = review_spotlight(locale)
            text = re.sub(
                r'<section class="section press-review-spotlight".*?</section>',
                spotlight,
                text,
                count=1,
                flags=re.DOTALL,
            )
        else:
            spotlight = review_spotlight(locale)
            text = text.replace(
                '<section class="contact-band">',
                spotlight + '<section class="contact-band">',
                1,
            )
    text = re.sub(
        r'quality\.css\?v=[^"\']+', "quality.css?v=20260811-press-review", text,
    )
    if text != original:
        page.write_text(text, encoding="utf-8")
        return True
    return False


def update_press_landing() -> None:
    page = ROOT / "press" / "index.html"
    text = page.read_text(encoding="utf-8")
    card = (
        '<article class="card press-review-card"><p class="kicker">Revue de presse</p>'
        '<h2>Mac4Ever et ON-mag parlent de Record Picker</h2>'
        '<p>Deux articles indépendants reviennent sur l’idée de redécouvrir une collection physique. '
        'Ils sont accompagnés de leur date de publication ; les informations produit actuelles restent '
        'sur ce dossier de presse.</p>'
        '<a class="button glass" href="/press/reviews/">Voir la revue de presse</a></article>'
    )
    if re.search(r'<article class="card press-review-card">.*?</article>', text, re.DOTALL):
        text = re.sub(r'<article class="card press-review-card">.*?</article>', card, text, count=1, flags=re.DOTALL)
    else:
        text = text.replace('</div><section class="official-identity"',
                            card + '</div><section class="official-identity"', 1)
    page.write_text(text, encoding="utf-8")


def add_sitemap_entry(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    url = "https://recordpicker.app/press/reviews/"
    if url not in text:
        entry = f"  <url>\n    <loc>{url}</loc>\n    <lastmod>2026-08-11</lastmod>\n  </url>\n"
        path.write_text(text.replace("</urlset>", entry + "</urlset>"), encoding="utf-8")


def main() -> None:
    build_review_page()
    update_press_landing()
    pages = sorted(ROOT.rglob("*.html"))
    changed = sum(update_page(page) for page in pages)
    add_sitemap_entry(ROOT / "sitemap.xml")
    add_sitemap_entry(ROOT / "sitemap-media.xml")
    print(f"Updated {changed} pages and added the Mac4Ever press review.")


if __name__ == "__main__":
    main()
