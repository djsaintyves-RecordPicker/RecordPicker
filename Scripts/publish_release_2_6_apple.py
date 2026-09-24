#!/usr/bin/env python3
"""Publish Apple 2.6, preserving Windows 2.5 and its upcoming 2.6 status."""
from html import escape
import json
import re
from announce_release_2_3_1 import ROOT, LOCALES, COMING_SOON


def main():
    notes = json.loads((ROOT / 'data/release-notes/2.6.json').read_text())
    for directory, locale in LOCALES.items():
        for route in ('index.html', 'readme/index.html', 'screenshots/index.html', 'mac-app/index.html'):
            path = ROOT / directory / route
            text = path.read_text()
            tag = 'article' if route == 'readme/index.html' else 'section'
            pattern = rf'<{tag}\b[^>]*data-release-version="2\.5".*?</{tag}>'
            old = re.search(pattern, text, re.S)
            # Already published: leave the current release and history unchanged.
            if not old or 'current-release' not in old.group().split('>', 1)[0]:
                continue
            previous = old.group()
            status = re.search(r'(?:Apple · Windows · |Mac · Windows · )([^<]+)', previous)
            if status:
                available = status.group(1)
            else:
                available = re.search(r'Mac · Windows · (.*?)</strong>', previous).group(1)
            summary = (f'<p class="release-platform-summary"><strong>iPhone · iPad · Apple Watch · Mac · {available}</strong>'
                       f'<br>Windows 2.5 · {available} · Windows 2.6 · {escape(COMING_SOON[locale])}</p>')
            if tag == 'article':
                historical = previous.replace(' current-release', '', 1)
                historical = re.sub(r'<p class="release-platform-summary">.*?</p>', '', historical, flags=re.S)
                replacement = (f'<article class="release-card current-release" data-release-version="2.6">'
                               f'<div class="release-head"><span class="version-pill">v2.6</span><div>'
                               f'<h3>Record Picker 2.6 “Snow Leopard”</h3>{summary}</div></div>'
                               f'<p>{escape(notes[locale])}</p></article>' + historical)
            else:
                replacement = previous.replace('data-release-version="2.5"', 'data-release-version="2.6"')
                replacement = replacement.replace('v25-preview', 'v26-preview')
                replacement = re.sub(r'<p class="kicker">.*?</p>', f'<p class="kicker">Apple · {available}</p>', replacement, count=1, flags=re.S)
                replacement = replacement.replace('<h2>Record Picker 2.5</h2>', '<h2>Record Picker 2.6 “Snow Leopard”</h2>')
                replacement = re.sub(r'<p class="lead">.*?</p>', lambda m: f'<p class="lead">{escape(notes[locale])}</p>{summary}', replacement, count=1, flags=re.S)
            text = text[:old.start()] + replacement + text[old.end():]
            text = re.sub(rf'<{tag} class="[^"]*(?:next-release|release-upcoming)[^"]*" data-release-version="2\.6">.*?</{tag}>', '', text, flags=re.S)
            path.write_text(text)
    for path in ROOT.rglob('*.html'):
        text = path.read_text()
        windows = 'windows-app' in path.parts
        updated = text.replace('<span id="site-footer-version">Record Picker · 2.5</span>', '<span id="site-footer-version">Record Picker · '+('2.5' if windows else '2.6')+'</span>')
        if not windows:
            updated = updated.replace('"softwareVersion":"2.5"', '"softwareVersion":"2.6"')
            updated = re.sub(r'("dateModified":")[^"]+', r'\g<1>2026-09-24', updated)
        if 'readme' not in path.parts and not windows:
            # Current gallery/labels only; do not rewrite the historical release notes.
            updated = updated.replace('data-release-gallery="2.5"', 'data-release-gallery="2.6"')
            updated = updated.replace('Record Picker 2.5', 'Record Picker 2.6')
        if updated != text:
            path.write_text(updated)
    path = ROOT / 'data/release-state.json'
    state = json.loads(path.read_text())
    state['current_release']['version'] = '2.6'
    for platform in ('iphone','ipad','watch','mac'):
        state['current_release']['platform_versions'][platform] = '2.6'
    state['current_release']['required_platforms_for_full_release'] = ['iphone','ipad','watch','mac']
    state['historical_releases'] = ['2.5'] + [v for v in state['historical_releases'] if v != '2.5']
    state['next_release'] = {'version':'2.6', 'platforms':{'windows':'coming_soon'}}
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n')
    print('Published Apple 2.6 in 33 site variants; Windows remains 2.5.')

if __name__ == '__main__':
    main()
