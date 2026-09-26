#!/usr/bin/env python3
"""Finish the public-site transition to Record Picker 2.6 on Apple and Windows.

Press-kit PDF and archive assets are deliberately left untouched.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[1]
MICROSOFT_STORE = "https://apps.microsoft.com/detail/9N2ZWRL4M3JC"
WINDOWS_IMAGE = "/assets/screenshots/v26/windows/windows-random-pick-fr"


def add_store_to_footer(text: str) -> str:
    match = re.search(r'(<footer class="footer">.*?<nav[^>]*>)(.*?)(</nav></footer>)', text, re.DOTALL)
    if not match or MICROSOFT_STORE in match.group(2):
        return text
    link = f'<a href="{MICROSOFT_STORE}">Microsoft Store</a>'
    return text[:match.start(3)] + link + text[match.start(3):]


def add_windows_visual(text: str, *, gallery: bool) -> str:
    marker = f'{WINDOWS_IMAGE}.webp'
    if marker in text:
        return text
    figure = (
        '<figure class="shot-card windows windows-authentic">'
        '<picture><source type="image/avif" '
        f'srcset="{WINDOWS_IMAGE}.avif">'
        f'<img src="{WINDOWS_IMAGE}.webp" '
        'alt="Record Picker 2.6 Random Pick screen on Windows 11, in French" '
        'width="1920" height="1032" loading="lazy" decoding="async"></picture>'
        '<figcaption class="screenshot-provenance">Windows 11 · Record Picker 2.6 · FR · authentic Microsoft Store capture</figcaption>'
        '</figure>'
    )
    if gallery:
        block = (
            '<section class="media-section windows-screenshot-section" data-platform-gallery="windows">'
            '<div class="section-head"><p class="kicker">Windows · Available now</p>'
            '<h2>Record Picker 2.6 on Windows 11</h2>'
            '<p class="lead">The same collection tools, Random Pick, Mood Pick and Today’s Pick, now on PC.</p></div>'
            '<div class="shot-grid windows-shot-grid">' + figure + '</div>'
            f'<div class="doc-actions"><a class="button primary" href="{MICROSOFT_STORE}">Microsoft Store</a></div>'
            '</section>'
        )
    else:
        block = (
            '<section class="section windows-screenshot-section" aria-labelledby="windows-authentic-title">'
            '<div class="section-head"><p class="kicker">Authentic app capture</p>'
            '<h2 id="windows-authentic-title">Record Picker 2.6 on Windows 11</h2>'
            '<p class="lead">Random Pick shown in the released Windows app.</p></div>'
            '<div class="shot-grid windows-shot-grid">' + figure + '</div></section>'
        )
    return text.replace('</main>', block + '</main>', 1)


def update_press_web(text: str) -> str:
    old_desc = "Téléchargez le dossier de presse officiel Record Picker, les visuels et les informations vérifiées sur l’app pour iPhone, iPad, Mac et Apple Watch."
    new_desc = "Ressources presse officielles pour Record Picker 2.6, disponible sur iPhone, iPad, Mac, Apple Watch et Windows 11."
    text = text.replace(old_desc, new_desc)
    text = text.replace("Record Picker · Août 2026", "Record Picker · Septembre 2026")
    text = text.replace(
        "Record Picker est une app Apple native pour cataloguer et redécouvrir une collection de vinyles et de CD sur iPhone, iPad, Mac et Apple Watch.",
        "Record Picker 2.6 permet de cataloguer et redécouvrir une collection de vinyles et de CD sur iPhone, iPad, Mac, Apple Watch et PC Windows 11.",
    )
    old_actions = '<div class="doc-actions"><a class="button primary" href="/assets/press/Record-Picker-Dossier-de-presse-FR.pdf">Télécharger en français</a><a class="button glass" href="/assets/press/Record-Picker-Press-Kit-EN.pdf" lang="en">Download in English</a></div>'
    new_actions = (
        '<div class="doc-actions"><a class="button primary" href="https://apps.apple.com/fr/app/recordpicker/id6780422305">App Store</a>'
        f'<a class="button primary" href="{MICROSOFT_STORE}">Microsoft Store</a>'
        '<a class="button glass" href="/assets/press/Record-Picker-Dossier-de-presse-FR.pdf">Dossier PDF français</a>'
        '<a class="button glass" href="/assets/press/Record-Picker-Press-Kit-EN.pdf" lang="en">English PDF</a></div>'
    )
    text = text.replace(old_actions, new_actions)
    notice_anchor = '<p class="lead">Record Picker 2.6 permet de cataloguer'
    if notice_anchor in text and 'press-kit-status' not in text:
        text = text.replace(
            notice_anchor,
            '<p class="press-kit-status" role="note"><strong>Mise à jour en cours :</strong> la page web reflète la version 2.6 Apple et Windows. Les dossiers PDF restent temporairement centrés sur les plateformes Apple.</p>' + notice_anchor,
            1,
        )
    return text


def update_reviews_web(text: str) -> str:
    return text.replace(
        "Les articles consacrés à Record Picker, l’app Apple qui aide à cataloguer et redécouvrir une collection de vinyles et de CD.",
        "Les articles consacrés à Record Picker, l’app Apple et Windows qui aide à cataloguer et redécouvrir une collection de vinyles et de CD.",
    )


def update_screenshot_metadata(text: str, relative: Path) -> str:
    if relative.as_posix() == "screenshots/index.html":
        text = text.replace(
            "Record Picker 2.6 Screenshots: Mac, iPhone &amp; Watch",
            "Record Picker 2.6 Screenshots: Mac, iPhone &amp; Windows",
        )
        text = re.sub(r"Record Picker 2\.6 · Mac · iPhone(?: · Windows)+", "Record Picker 2.6 · Mac · iPhone · Windows", text)
        text = text.replace(
            "See Record Picker 2.6 on Mac and iPhone, including the catalog, Random Pick, Mood Pick and Today’s Pick.",
            "See Record Picker 2.6 on Mac, iPhone and Windows, including the catalog, Random Pick, Mood Pick and Today’s Pick.",
        )
        text = text.replace("Record Picker 2.6 Screenshots: Mac, iPhone & Watch", "Record Picker 2.6 Screenshots: Mac, iPhone & Windows")
    elif relative.as_posix() == "fr/screenshots/index.html":
        text = text.replace("Captures d’écran Record Picker 2.6 : Mac, iPhone et Watch", "Captures d’écran Record Picker 2.6 : Mac, iPhone et Windows")
        text = re.sub(r"Record Picker 2\.6 · Mac · iPhone(?: · Windows)+", "Record Picker 2.6 · Mac · iPhone · Windows", text)
    return text


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        relative = path.relative_to(ROOT)
        if relative.parts and relative.parts[0] in {"snory-teller", "tmp"}:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text.replace("quality.css?v=20260828-v24-notes", "quality.css?v=20260926-v26-windows")
        updated = add_store_to_footer(updated)
        if "windows-app" in relative.parts:
            updated = add_windows_visual(updated, gallery=False)
        if relative.parts and relative.parts[-2:] == ("screenshots", "index.html"):
            updated = add_windows_visual(updated, gallery=True)
            updated = update_screenshot_metadata(updated, relative)
        if relative.as_posix() == "press/index.html":
            updated = update_press_web(updated)
        elif relative.as_posix() == "press/reviews/index.html":
            updated = update_reviews_web(updated)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    source = ROOT / "assets/screenshots/v26/windows/windows-random-pick-fr.jpg"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest_path = ROOT / "data/media-release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    provenance = {
        "version": "2.6",
        "platform": "windows",
        "language": "fr-fr",
        "kind": "screenshot",
        "source": "Record Picker Windows 2.6, authentic Microsoft Store listing capture retrieved on 2026-09-26",
        "source_sha256": digest,
        "width": 1920,
        "height": 1032,
    }
    for suffix in ("jpg", "webp", "avif"):
        manifest["assets"][f"assets/screenshots/v26/windows/windows-random-pick-fr.{suffix}"] = provenance
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for sitemap_name in ("sitemap.xml", "sitemap-media.xml"):
        sitemap_path = ROOT / sitemap_name
        sitemap = sitemap_path.read_text(encoding="utf-8")
        sitemap = re.sub(r"<lastmod>[^<]+</lastmod>", "<lastmod>2026-09-26</lastmod>", sitemap)
        sitemap_path.write_text(sitemap, encoding="utf-8")
    print(f"Refreshed {changed} public pages for Apple and Windows 2.6.")


if __name__ == "__main__":
    main()
