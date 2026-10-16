#!/usr/bin/env python3
"""Publish the approved Apple 3.0 offer, preserving verified desktop availability."""
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
    if json.loads((ROOT / "data/release-state.json").read_text())["current_release"]["version"] == "3.0.1":
        from publish_release_3_0_1 import main as publish_patch
        publish_patch()
        return
    copies_path = ROOT / 'data/release-notes/3.0-offer.json'
    copies = json.loads(copies_path.read_text())
    mac_available = json.loads((ROOT / "data/release-state.json").read_text())["current_release"]["platform_versions"].get("mac") == "3.0"
    windows_available = json.loads((ROOT / "data/release-state.json").read_text())["current_release"]["platform_versions"].get("windows") in ("3.0", "3.0.1")
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
        if mac_available:
            status = f'iPhone · iPad · Apple Watch · Mac · 3.0 — {available}. Windows · 3.0 — {COMING_SOON[locale]}.'
            if locale.startswith('en-'):
                status = '3.0 is available on iPhone, iPad, Apple Watch and Mac. Windows 3.0 is being prepared separately.'
            elif locale.startswith('fr-'):
                status = 'La 3.0 est disponible sur iPhone, iPad, Apple Watch et Mac. La version 3.0 Windows est préparée séparément.'
        if windows_available:
            status = f'iPhone · iPad · Apple Watch · Mac · Windows · 3.0 — {available}.'
        if windows_available and json.loads((ROOT / 'data/release-state.json').read_text())['current_release']['platform_versions']['windows'] == '3.0.1':
            status = f'iPhone · iPad · Apple Watch · Mac · 3.0 — {available} Windows · 3.0.1 — {available}'
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
            if windows_available:
                block = block.replace('release-partial', 'current-release')
            block = re.sub(r'<p class="release-free-offer"[^>]*>.*?</p>', '', block, flags=re.S)
            block = block.replace('<div class="grid two release-tier-grid">',
                '<p class="release-free-offer" data-offer="free"><strong>'+escape(free_title)+'</strong></p>'
                '<div class="grid two release-tier-grid">', 1)
            block = re.sub(r'<p class="release-platform-summary">.*?</p>',
                           lambda _: '<p class="release-platform-summary">'+escape(status)+'</p>', block, flags=re.S)
            for tier in ('light', 'pro'):
                block = re.sub(r'(<div class="card release-tier" data-offer="'+tier+r'"><h[34]>).*?(</h[34]>)',
                               lambda m: m[1]+escape(copies[locale][tier+'_title'])+m[2], block, count=1, flags=re.S)
            text = re.sub(pattern, lambda _: block, text, count=1, flags=re.S)
            if route == 'index.html':
                text = re.sub(r'(<p class="hero-free-tier">).*?(</p>)',
                              lambda m: m[1]+escape(free_title+' · Light · Pro')+m[2], text, flags=re.S)
                text = re.sub(r'(<strong data-price-current>).*?(</strong>)',
                              lambda m: m[1]+escape(free_title+' · Light · Pro')+m[2], text, flags=re.S)
            text = text.replace('puis Pro à vie sans abonnement', 'puis Light ou Pro en achat unique sans abonnement')
            text = text.replace('lifetime Pro, with no subscription', 'Light or Pro, with no subscription')
            text = text.replace('with an optional one-time Pro unlock', 'with optional one-time Light or Pro upgrades')
            # Preserve older platform availability only where 3.0 is not released.
            old_pattern = rf'<{tag}\b[^>]*data-release-version="2\.7"[^>]*>.*?</{tag}>'
            def previous(m):
                b = m.group()
                if windows_available or tag == 'article':
                    return re.sub(r'<p class="release-platform-summary">.*?</p>', '', b, flags=re.S).replace(' current-release', '')
                return re.sub(r'<p class="release-platform-summary">.*?</p>',
                              lambda _: '<p class="release-platform-summary">'+('Windows' if mac_available else 'Mac · Windows')+' · 2.7 — '+escape(available)+'</p>', b, flags=re.S)
            text = re.sub(old_pattern, previous, text, flags=re.S)
            text = re.sub(r'site\.js\?v=[^"\s]+', 'site.js?v=20261008-free-light-pro', text)
            text = re.sub(r'quality\.css\?v=[^"\s]+', 'quality.css?v=20261008-free-light-pro', text)
            if text != path.read_text():
                path.write_text(text)
                changed += 1
    copies_path.write_text(json.dumps(copies, ensure_ascii=False, indent=2)+'\n')
    state_path = ROOT / 'data/release-state.json'
    state = json.loads(state_path.read_text())
    state['publication_phase'] = 'full' if windows_available else 'partial'
    state['current_release']['version'] = '3.0'
    state['current_release']['required_platforms_for_full_release'] = ['iphone', 'ipad', 'watch'] + (['mac'] if mac_available else []) + (['windows'] if windows_available else [])
    for platform in ('iphone', 'ipad', 'watch'):
        state['current_release']['platform_versions'][platform] = '3.0'
        state['next_release']['platforms'][platform] = 'available'
    state['next_release']['platforms']['mac'] = 'available' if mac_available else 'in_review'
    state['next_release']['distribution']['apple'] = 'available' if mac_available else 'ios_available_mac_in_review'
    if windows_available:
        state['next_release']['platforms']['windows'] = 'available'
        if '2.7' not in state['historical_releases']:
            state['historical_releases'].insert(0, '2.7')
    state['next_release']['distribution']['windows'] = 'available' if windows_available else 'submission_in_progress'
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n')
    for path in ROOT.rglob('*.html'):
        relative = path.relative_to(ROOT).parts
        if any(p in relative for p in ('physical','snory-teller','apps','dulpi')):
            continue
        text = path.read_text()
        if (windows_available or 'windows-app' not in relative) and (mac_available or 'mac-app' not in relative):
            text = text.replace('<span id="site-footer-version">Record Picker · 2.7</span>', '<span id="site-footer-version">Record Picker · 3.0</span>')
            text = text.replace('"softwareVersion":"2.7"', '"softwareVersion":"3.0"')
        if windows_available and 'windows-app' in relative:
            text = text.replace('Record Picker 2.7', 'Record Picker 3.0')
        if text != path.read_text():
            path.write_text(text)
    if windows_available and json.loads(state_path.read_text())['current_release']['platform_versions']['windows'] == '3.0.1':
        from publish_windows_3_0_1 import refresh_windows_pages
        refresh_windows_pages(ROOT)
    print(f'Published verified 3.0 offer on {changed} pages; platform availability preserved.')

if __name__ == '__main__':
    main()
