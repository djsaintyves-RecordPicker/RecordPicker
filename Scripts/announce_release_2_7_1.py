#!/usr/bin/env python3
"""Announce submitted 2.7.1 while keeping the available 2.7 release distinct."""
from html import escape
import json
from pathlib import Path
import re

from announce_release_2_3_1 import LOCALES, COMING_SOON

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('index.html', 'readme/index.html', 'screenshots/index.html',
          'mac-app/index.html', 'ios-app/index.html', 'windows-app/index.html')


def main():
    notes = json.loads((ROOT / 'data/release-notes/2.7.1.json').read_text())
    if set(notes) != set(LOCALES.values()):
        raise RuntimeError('Missing localized 2.7.1 notes')
    changed = 0
    for directory, locale in LOCALES.items():
        for route in ROUTES:
            path = ROOT / directory / route
            text = path.read_text()
            # Screenshot labels must continue to describe their actual capture.
            if route == 'windows-app/index.html':
                captures = []
                def protect(match):
                    captures.append(match.group())
                    return f'<!--windows-capture-{len(captures)-1}-->'
                text = re.sub(r'<section\b[^>]*aria-labelledby="windows-authentic-title"[^>]*>.*?</section>', protect, text, flags=re.S)
                text = text.replace('Record Picker 2.6', 'Record Picker 2.7')
                text = text.replace('data-windows-version="2.6"', 'data-windows-version="2.7"')
                text = text.replace('"softwareVersion":"2.6"', '"softwareVersion":"2.7"')
                text = text.replace('Record Picker · 2.6</span>', 'Record Picker · 2.7</span>')
                for index, capture in enumerate(captures):
                    text = text.replace(f'<!--windows-capture-{index}-->', capture)
            text = re.sub(r'(<p class="release-platform-summary"><strong>iPhone · iPad · Apple Watch · Mac · [^<]+</strong><br>)Windows 2\.6', r'\1Windows 2.7', text)
            tag = 'article' if route == 'readme/index.html' else 'section'
            heading = 'h3' if tag == 'article' else 'h2'
            css = 'release-card release-upcoming release-271' if tag == 'article' else 'section next-release release-271'
            platforms = ('Windows' if route == 'windows-app/index.html' else
                         'iPhone · iPad' if route == 'ios-app/index.html' else
                         'Mac' if route == 'mac-app/index.html' else
                         'iPhone · iPad · Apple Watch · Mac · Windows')
            summary = f'<p class="release-platform-summary"><strong>{platforms} · {escape(COMING_SOON[locale])}</strong></p>'
            block = (f'<{tag} class="{css}" id="upcoming-release" data-release-version="2.7.1">'
                     f'<div><{heading}>Record Picker 2.7.1</{heading}>{summary}</div>'
                     '<ul>' + ''.join(f'<li>{escape(note)}</li>' for note in notes[locale]) + f'</ul></{tag}>')
            pattern = rf'<{tag}\b[^>]*data-release-version="2\.7\.1"[^>]*>.*?</{tag}>'
            if re.search(pattern, text, re.S):
                text = re.sub(pattern, lambda _: block, text, flags=re.S)
            elif route in ('ios-app/index.html', 'windows-app/index.html'):
                text = text.replace('</main>', block + '</main>', 1)
            else:
                marker = re.search(rf'<{tag}\b[^>]*data-release-version="2\.7"[^>]*>', text)
                if not marker:
                    raise RuntimeError(f'Missing current 2.7 release: {path}')
                text = text[:marker.start()] + block + text[marker.start():]
            text = re.sub(r'("dateModified":")[^"]+', r'\g<1>2026-10-03', text)
            text = re.sub(r'quality\.css\?v=[^"\s]+', 'quality.css?v=20261003-v271', text)
            if text != path.read_text():
                path.write_text(text)
                changed += 1
    path = ROOT / 'data/release-state.json'
    state = json.loads(path.read_text())
    state['current_release']['platform_versions']['windows'] = '2.7'
    state['current_release']['required_platforms_for_full_release'] = ['iphone', 'ipad', 'watch', 'mac', 'windows']
    state['next_release'] = {
        'version': '2.7.1',
        'platforms': {platform: 'coming_soon' for platform in ('iphone', 'ipad', 'watch', 'mac', 'windows')},
        'distribution': {'apple': 'app_store_review_pending', 'windows': 'microsoft_store_certification_pending'},
        'announcement_routes': list(ROUTES),
    }
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    print(f'Announced 2.7.1 across {changed} pages; Apple and Windows 2.7 remain available.')


if __name__ == '__main__':
    main()
