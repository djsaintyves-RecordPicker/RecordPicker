#!/usr/bin/env python3
"""Present the agreed 3.0 Light/Pro offer without claiming store availability.

Localized public copy is stored in data/release-notes/3.0-offer.json. English
and French are edited manually; other translations retain their draft status.
This generator does not promote binaries, change existing store prices or
replace the provenance of actual screenshots.
"""
from html import escape
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from announce_release_2_3_1 import LOCALES

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('index.html', 'readme/index.html', 'screenshots/index.html',
          'mac-app/index.html', 'ios-app/index.html', 'windows-app/index.html')
DATE = '2026-10-07'


def main():
    copies = json.loads((ROOT / 'data/release-notes/3.0-offer.json').read_text())
    if set(copies) != set(LOCALES.values()):
        raise RuntimeError('Missing localized 3.0 offer')
    changed = 0
    urls = set()
    for directory, locale in LOCALES.items():
        copy = copies[locale]
        for route in ROUTES:
            path = ROOT / directory / route
            text = path.read_text()
            tag = 'article' if route == 'readme/index.html' else 'section'
            heading, subheading = ('h3', 'h4') if tag == 'article' else ('h2', 'h3')
            css = 'release-card release-upcoming' if tag == 'article' else 'section next-release'
            block = (
                f'<{tag} class="{css} release-30" id="upcoming-release" data-release-version="3.0">'
                f'<div><{heading}>{escape(copy["title"])}</{heading}>'
                f'<p class="release-platform-summary">{escape(copy["status"])}</p></div>'
                '<div class="grid two release-tier-grid">'
                f'<div class="card release-tier" data-offer="light"><{subheading}>{escape(copy["light_title"])}</{subheading}>'
                f'<p>{escape(copy["light"])}</p></div>'
                f'<div class="card release-tier" data-offer="pro"><{subheading}>{escape(copy["pro_title"])}</{subheading}>'
                f'<p>{escape(copy["pro"])}</p></div></div>'
                f'<p class="release-offer-terms">{escape(copy["terms"])}</p></{tag}>'
            )
            pattern = rf'<{tag}\b[^>]*id="upcoming-release"[^>]*>.*?</{tag}>'
            if len(re.findall(pattern, text, re.S)) != 1:
                raise RuntimeError(f'Expected one staged release: {path}')
            text = re.sub(pattern, lambda _: block, text, flags=re.S)
            text = re.sub(r'quality\.css\?v=[^"\s]+', 'quality.css?v=20261007-v30-offer', text)
            if text != path.read_text():
                path.write_text(text)
                changed += 1
            urls.add('https://recordpicker.app/' + (directory + '/' if directory else '')
                     + (route[:-10] if route.endswith('index.html') else route))
    state_path = ROOT / 'data/release-state.json'
    state = json.loads(state_path.read_text())
    state['next_release'] = {
        'version': '3.0',
        'platforms': {p: 'in_preparation' for p in
                      ('iphone', 'ipad', 'watch', 'mac', 'windows', 'android', 'chromeos')},
        'distribution': {'apple': 'preparing_submission', 'windows': 'validation',
                         'android': 'closed_beta_recruitment', 'chromeos': 'validation'},
        'offer': {'light': {'price_eur': '2.99', 'purchase_type': 'one_time',
                            'records_and_imports': 'unlimited',
                            'picks': ['random', 'today', 'mood']},
                  'pro': {'existing_purchases_preserved': True, 'price': 'unchanged'}},
        'announcement_routes': list(ROUTES),
    }
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    # Preserve XML formatting, canonicals and unrelated product pages.
    sitemap = ROOT / 'sitemap.xml'
    source = sitemap.read_text()
    def dated(match):
        entry = match.group()
        loc = re.search(r'<loc>(.*?)</loc>', entry)
        if loc and loc.group(1) in urls:
            entry = re.sub(r'<lastmod>.*?</lastmod>', f'<lastmod>{DATE}</lastmod>', entry)
        return entry
    source = re.sub(r'<url>.*?</url>', dated, source, flags=re.S)
    ET.fromstring(source)
    sitemap.write_text(source)
    print(f'3.0 offer staged on {changed} pages; current store availability preserved.')


if __name__ == '__main__':
    main()
