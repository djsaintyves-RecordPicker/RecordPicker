#!/usr/bin/env python3
"""Announce Apple 2.7 while the App Store review is pending."""
from html import escape
import json
from pathlib import Path
import re

from announce_release_2_3_1 import LOCALES, COMING_SOON

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('index.html', 'readme/index.html', 'screenshots/index.html', 'mac-app/index.html')


def main():
    notes = json.loads((ROOT / 'data/release-notes/2.7.json').read_text())
    changed = 0
    for directory, locale in LOCALES.items():
        for route in ROUTES:
            path = ROOT / directory / route
            text = path.read_text()
            tag = 'article' if route == 'readme/index.html' else 'section'
            title = 'h3' if tag == 'article' else 'h2'
            css = 'release-card release-upcoming' if tag == 'article' else 'section next-release'
            status = escape(COMING_SOON[locale])
            summary = (f'<p class="release-platform-summary"><strong>'
                       f'iPhone · iPad · Apple Watch · Mac · {status}</strong></p>')
            heading = f'<{title}>Record Picker 2.7</{title}>'
            if tag == 'article':
                body = f'<div>{heading}{summary}</div><p>{escape(notes[locale])}</p>'
            else:
                body = (f'<div class="section-head"><p class="kicker">{status}</p>'
                        f'{heading}{summary}<p class="lead">{escape(notes[locale])}</p></div>')
            block = f'<{tag} class="{css}" data-release-version="2.7">{body}</{tag}>'
            pattern = rf'<{tag}\b[^>]*data-release-version="2\.7"[^>]*>.*?</{tag}>'
            if re.search(pattern, text, re.S):
                updated = re.sub(pattern, lambda m: block, text, flags=re.S)
            else:
                marker = re.search(rf'<{tag}\b[^>]*data-release-version="2\.6"[^>]*>', text)
                if not marker:
                    raise RuntimeError(f'Current release missing: {path}')
                updated = text[:marker.start()] + block + text[marker.start():]
            if updated != text:
                path.write_text(updated)
                changed += 1
    path = ROOT / 'data/release-state.json'
    state = json.loads(path.read_text())
    state['next_release'] = {
        'version': '2.7',
        'platforms': {p: 'coming_soon' for p in ('iphone', 'ipad', 'watch', 'mac')},
        'distribution': 'app_store_review_pending',
    }
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    print(f'Apple 2.7 announcement: {changed} changed pages; public Apple/Windows 2.6 preserved.')


if __name__ == '__main__':
    main()
