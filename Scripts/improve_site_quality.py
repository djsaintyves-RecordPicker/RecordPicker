#!/usr/bin/env python3
"""Apply editorial, social-metadata and structured-data improvements."""

from html import escape, unescape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOCIAL_IMAGE_BY_PAGE = {
    "mac-app/index.html": "social-mac.png",
    "screenshots/index.html": "social-screenshots.png",
    "choose-vinyl-record/index.html": "social-guides.png",
    "random-vinyl-record-picker/index.html": "social-guides.png",
    "manage-vinyl-collection/index.html": "social-guides.png",
}
GUIDE_PAGES = {
    "choose-vinyl-record/index.html",
    "random-vinyl-record-picker/index.html",
    "manage-vinyl-collection/index.html",
}


def plain(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", value)).strip()


def page_kind(path: Path) -> str:
    parts = path.relative_to(ROOT).parts
    if len(parts) >= 2 and parts[0] in {
        "ar", "ca", "da", "de", "el", "en-au", "en-ca", "en-gb", "en-us",
        "es-es", "fi", "fr", "fr-ca", "he", "hi", "id", "it", "ja", "ko",
        "nb", "nl", "pl", "pt-br", "pt-pt", "ru", "sv", "tr", "zh-hans", "zh-hant",
    }:
        return "/".join(parts[1:])
    return "/".join(parts)


def replace_meta_content(text: str, attribute: str, name: str, content: str) -> str:
    return re.sub(
        rf'(<meta {attribute}="{re.escape(name)}" content=")[^"]*(">)',
        rf'\g<1>{content}\2',
        text,
        count=1,
    )


def social_metadata(text: str, kind: str) -> str:
    image = SOCIAL_IMAGE_BY_PAGE.get(kind, "social-home.png")
    url = f"https://recordpicker.app/assets/social/{image}"
    text = replace_meta_content(text, "property", "og:image", url)
    text = replace_meta_content(text, "name", "twitter:image", url)
    text = replace_meta_content(text, "name", "twitter:card", "summary_large_image")
    text = re.sub(r'<meta property="og:image:(?:width|height|alt)"[^>]*>', "", text)
    text = re.sub(r'<meta name="twitter:image:alt"[^>]*>', "", text)
    title = re.search(r'<meta property="og:title" content="([^"]*)">', text)
    alt = escape(unescape(title.group(1)) if title else "Record Picker", quote=True)
    details = (
        '<meta property="og:image:width" content="1200">'
        '<meta property="og:image:height" content="630">'
        f'<meta property="og:image:alt" content="{alt}">'
        f'<meta name="twitter:image:alt" content="{alt}">'
    )
    text = re.sub(r'(<meta property="og:image"[^>]*>)', r'\1' + details, text, count=1)
    return text


def page_schema(text: str, kind: str) -> str:
    text = re.sub(
        r'<script type="application/ld\+json" id="page-schema">.*?</script>',
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    canonical = re.search(r'<link rel="canonical" href="([^"]+)">', text)
    title = re.search(r"<title>(.*?)</title>", text, flags=re.DOTALL)
    description = re.search(r'<meta name="description" content="([^"]*)">', text)
    language = re.search(r'<html lang="([^"]+)"', text)
    if not canonical or not title:
        return text
    canonical_url = unescape(canonical.group(1))
    title_text = plain(title.group(1))
    home_url = canonical_url.rsplit("/", 2)[0] + "/"
    graph: list[dict[str, object]] = []
    if kind != "index.html":
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Record Picker", "item": home_url},
                {"@type": "ListItem", "position": 2, "name": title_text, "item": canonical_url},
            ],
        })
    if kind in GUIDE_PAGES:
        graph.append({
            "@type": "Article",
            "headline": title_text,
            "description": unescape(description.group(1)) if description else "",
            "inLanguage": language.group(1) if language else "en",
            "mainEntityOfPage": canonical_url,
            "author": {"@type": "Organization", "name": "Record Picker"},
            "publisher": {
                "@type": "Organization",
                "name": "Record Picker",
                "logo": {"@type": "ImageObject", "url": "https://recordpicker.app/assets/brand/icon-512.png"},
            },
            "image": "https://recordpicker.app/assets/social/social-guides.png",
        })
    if not graph:
        return text
    schema = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return text.replace("</head>", f'<script type="application/ld+json" id="page-schema">{schema}</script></head>', 1)


def image_figure(figure: str) -> str:
    image = re.search(r"<img .*?>", figure, flags=re.DOTALL)
    caption = re.search(r"<figcaption>.*?</figcaption>", figure, flags=re.DOTALL)
    if not image or not caption:
        return ""
    return f'<figure class="current-screen">{image.group(0)}{caption.group(0)}</figure>'


def improve_home(text: str) -> str:
    v18 = re.search(r'<section class="section v18-showcase".*?</section>', text, flags=re.DOTALL)
    current_figures: list[str] = []
    current_heading = ""
    current_lead = ""
    if v18:
        figures = re.findall(r"<figure.*?</figure>", v18.group(0), flags=re.DOTALL)
        current_figures = [image_figure(figures[index]) for index in (0, 2, 3) if index < len(figures)]
        heading = re.search(r"<h2[^>]*>(.*?)</h2>", v18.group(0), flags=re.DOTALL)
        lead = re.search(r'<p class="lead">.*?</p>', v18.group(0), flags=re.DOTALL)
        current_heading = f"<h2>{heading.group(1)}</h2>" if heading else ""
        current_lead = lead.group(0) if lead else ""
        text = text[:v18.start()] + text[v18.end():]

    text = re.sub(r'<section class="section release-history".*?</section>', "", text, count=1, flags=re.DOTALL)
    text = re.sub(r'<section class="section support-band".*?</section>', "", text, count=1, flags=re.DOTALL)
    text = text.replace('<section class="section upcoming-showcase"', '<section class="section upcoming-showcase" id="versions"', 1)
    text = text.replace('id="versions" id="versions"', 'id="versions"')

    privacy = re.search(r'<section class="section split" id="privacy">.*?</section>', text, flags=re.DOTALL)
    if privacy:
        heading = re.search(r"<h2>.*?</h2>", privacy.group(0), flags=re.DOTALL)
        lead = re.search(r'<p class="lead">.*?</p>', privacy.group(0), flags=re.DOTALL)
        actions = re.search(r'<div class="cta-row compact">.*?</div>', privacy.group(0), flags=re.DOTALL)
        if heading and lead and actions:
            compact = (
                '<section class="section privacy-compact" id="privacy"><div>'
                + heading.group(0) + lead.group(0) + actions.group(0)
                + '</div></section>'
            )
            text = text[:privacy.start()] + compact + text[privacy.end():]

    gallery = re.search(r'<section class="section gallery".*?</section>', text, flags=re.DOTALL)
    if gallery and current_figures:
        updated_gallery = gallery.group(0)
        if current_heading:
            updated_gallery = re.sub(r"<h2>.*?</h2>", current_heading, updated_gallery, count=1, flags=re.DOTALL)
        if current_lead:
            updated_gallery = re.sub(r'<p class="lead">.*?</p>', current_lead, updated_gallery, count=1, flags=re.DOTALL)
        grid = re.search(r'<div class="screen-grid[^>]*>.*?</div>', gallery.group(0), flags=re.DOTALL)
        if grid:
            replacement = '<div class="screen-grid current-screens">' + "".join(current_figures) + "</div>"
            updated_grid = re.search(r'<div class="screen-grid[^>]*>.*?</div>', updated_gallery, flags=re.DOTALL)
            if updated_grid:
                updated_gallery = updated_gallery[:updated_grid.start()] + replacement + updated_gallery[updated_grid.end():]
            text = text[:gallery.start()] + updated_gallery + text[gallery.end():]

    teaser = re.search(r'<section class="section mac-teaser">.*?(<a class="button glass".*?</a>).*?</section>', text, flags=re.DOTALL)
    hero_actions = re.search(r'<div class="cta-row">.*?</div>', text, flags=re.DOTALL)
    if teaser and hero_actions and "mac-app/" not in hero_actions.group(0):
        updated_actions = hero_actions.group(0).replace("</div>", teaser.group(1) + "</div>", 1)
        text = text[:hero_actions.start()] + updated_actions + text[hero_actions.end():]
    return text


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        original = path.read_text(encoding="utf-8")
        if "<main" not in original:
            continue
        kind = page_kind(path)
        text = improve_home(original) if kind == "index.html" else original
        text = social_metadata(text, kind)
        text = page_schema(text, kind)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    print(f"Applied editorial and SEO improvements to {changed} HTML pages.")


if __name__ == "__main__":
    main()
