#!/usr/bin/env python3
"""Publish the approved iOS 3.0 offer; retain other platforms' live versions."""
from html import escape, unescape
import json
from pathlib import Path
import re
from announce_release_2_3_1 import LOCALES
from announce_release_2_1 import COMING_SOON
from adapt_search_discovery_2026_10_06 import PRICES

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('index.html', 'readme/index.html', 'screenshots/index.html',
          'mac-app/index.html', 'ios-app/index.html', 'windows-app/index.html')

def main():
    copies_path = ROOT / 'data/release-notes/3.0-offer.json'
    copies = json.loads(copies_path.read_text())
    changed = 0
    for directory, locale in LOCALES.items():
        home = (ROOT / directory / 'index.html').read_text()
        old = re.search(r'<section\b[^>]*data-release-version="2\.7"[^>]*>.*?</section>', home, re.S)
        # Reuse the existing reviewed availability labels in each language.
        summary = re.search(r'<p class="release-platform-summary">.*?</p>', old.group(), re.S)
        if copies[locale].get('available_label'):
            available = copies[locale]['available_label']
        elif summary:
            available = unescape(summary.group().split(' · ')[-1].split('</p>')[0])
        else:
            available = copies[locale]['available_label']
        copies[locale]['available_label'] = available
        status = f'iPhone · iPad · Apple Watch · 3.0 — {available}. Mac · Windows · 3.0 — {COMING_SOON[locale]}.'
        if locale.startswith('en-'):
            status = '3.0 is available on iPhone, iPad and Apple Watch. Mac is under App Store review; Windows 3.0 is being submitted to Microsoft.'
        elif locale.startswith('fr-'):
            status = 'La 3.0 est disponible sur iPhone, iPad et Apple Watch. Le Mac est en examen chez Apple ; la 3.0 Windows est en cours de soumission à Microsoft.'
        copies[locale]['status'] = status
        free_title = PRICES[directory or 'en-us'].split(' · ')[0]
        copies[locale]['free_title'] = free_title
        for route in ROUTES:
            path = ROOT / directory / route
            text = path.read_text()
            tag = 'article' if route == 'readme/index.html' else 'section'
            pattern = rf'<{tag}\b[^>]*data-release-version="3\.0"[^>]*>.*?</{tag}>'
            match = re.search(pattern, text, re.S)
            if not match:
                raise RuntimeError(f'Missing 3.0 offer: {path}')
            block = match.group().replace('release-upcoming', 'release-partial').replace('next-release', 'release-partial')
            block = re.sub(r'<p class="release-free-offer"[^>]*>.*?</p>', '', block, flags=re.S)
            block = block.replace('<div class="grid two release-tier-grid">',
                '<p class="release-free-offer" data-offer="free"><strong>'+escape(free_title)+'</strong></p>'
                '<div class="grid two release-tier-grid">', 1)
            block = re.sub(r'<p class="release-platform-summary">.*?</p>',
                           lambda _: '<p class="release-platform-summary">'+escape(status)+'</p>', block, flags=re.S)
            text = re.sub(pattern, lambda _: block, text, count=1, flags=re.S)
            if route == 'index.html':
                text = re.sub(r'(<p class="hero-free-tier">).*?(</p>)',
                              lambda m: m[1]+escape(free_title+' · Light · Pro')+m[2], text, flags=re.S)
                text = re.sub(r'(<strong data-price-current>).*?(</strong>)',
                              lambda m: m[1]+escape(free_title+' · Light · Pro')+m[2], text, flags=re.S)
            text = text.replace('puis Pro à vie sans abonnement', 'puis Light ou Pro en achat unique sans abonnement')
            text = text.replace('lifetime Pro, with no subscription', 'Light or Pro, with no subscription')
            text = text.replace('with an optional one-time Pro unlock', 'with optional one-time Light or Pro upgrades')
            # The old release remains available on Mac/Windows, not on iOS.
            old_pattern = rf'<{tag}\b[^>]*data-release-version="2\.7"[^>]*>.*?</{tag}>'
            def previous(m):
                b = m.group()
                if tag == 'article':
                    return re.sub(r'<p class="release-platform-summary">.*?</p>', '', b, flags=re.S).replace(' current-release', '')
                return re.sub(r'<p class="release-platform-summary">.*?</p>',
                              lambda _: '<p class="release-platform-summary">Mac · Windows · 2.7 — '+escape(available)+'</p>', b, flags=re.S)
            text = re.sub(old_pattern, previous, text, flags=re.S)
            text = re.sub(r'quality\.css\?v=[^"\s]+', 'quality.css?v=20261008-free-light-pro', text)
            if text != path.read_text():
                path.write_text(text)
                changed += 1
    copies_path.write_text(json.dumps(copies, ensure_ascii=False, indent=2)+'\n')
    state_path = ROOT / 'data/release-state.json'
    state = json.loads(state_path.read_text())
    state['publication_phase'] = 'partial'
    state['current_release']['version'] = '3.0'
    state['current_release']['required_platforms_for_full_release'] = ['iphone', 'ipad', 'watch']
    for platform in ('iphone', 'ipad', 'watch'):
        state['current_release']['platform_versions'][platform] = '3.0'
        state['next_release']['platforms'][platform] = 'available'
    state['next_release']['platforms']['mac'] = 'in_review'
    state['next_release']['distribution']['apple'] = 'ios_available_mac_in_review'
    state['next_release']['distribution']['windows'] = 'submission_in_progress'
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n')
    for path in ROOT.rglob('*.html'):
        relative = path.relative_to(ROOT).parts
        if any(p in relative for p in ('physical','snory-teller','apps','dulpi')):
            continue
        text = path.read_text()
        if 'mac-app' not in relative and 'windows-app' not in relative:
            text = text.replace('<span id="site-footer-version">Record Picker · 2.7</span>', '<span id="site-footer-version">Record Picker · 3.0</span>')
            text = text.replace('"softwareVersion":"2.7"', '"softwareVersion":"3.0"')
        if text != path.read_text():
            path.write_text(text)
    print(f'Published approved iOS 3.0 offer on {changed} pages; Mac and Windows availability preserved.')

if __name__ == '__main__':
    main()
