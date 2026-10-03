#!/usr/bin/env python3
"""Publish Apple 2.7, preserving Windows 2.6 and screenshot capture labels."""
import json
import re
from announce_release_2_7 import ROOT, ROUTES, LOCALES


def main():
    for directory in LOCALES:
        for route in ROUTES:
            path = ROOT / directory / route
            text = path.read_text()
            tag = 'article' if route == 'readme/index.html' else 'section'
            pattern = lambda version: rf'<{tag}\b[^>]*data-release-version="{version}"[^>]*>.*?</{tag}>'
            candidate = re.search(pattern(r'2\.7'), text, re.S)
            if not candidate:
                raise RuntimeError(f'Missing 2.7 release: {path}')
            if 'current-release' in candidate.group().split('>', 1)[0]:
                continue
            previous = re.search(pattern(r'2\.6'), text, re.S)
            if not previous:
                raise RuntimeError(f'Missing previous release: {path}')
            old_summary = re.search(r'<p class="release-platform-summary">.*?</p>', previous.group(), re.S).group()
            available = old_summary.split(' · ')[-1].split('</strong>')[0]
            summary = (f'<p class="release-platform-summary"><strong>iPhone · iPad · Apple Watch · Mac · {available}</strong>'
                       f'<br>Windows 2.6 · {available}</p>')
            promoted = candidate.group().replace('release-upcoming', 'current-release').replace('next-release', 'current-release')
            promoted = re.sub(r'<p class="release-platform-summary">.*?</p>', lambda m: summary, promoted, flags=re.S)
            promoted = re.sub(r'<p class="kicker">.*?</p>', lambda m: f'<p class="kicker">Apple · {available}</p>', promoted, flags=re.S)
            if tag == 'article':
                historical = previous.group().replace(' current-release', '', 1)
                historical = re.sub(r'<p class="release-platform-summary">.*?</p>', '', historical, flags=re.S)
            else:
                # Preserve the existing panels and photographs with their actual version labels.
                tail = previous.group().split('</div>', 1)[1].rsplit('</section>', 1)[0]
                promoted = promoted.rsplit('</section>', 1)[0] + tail + '</section>'
                if 'id="versions"' in previous.group().split('>', 1)[0]:
                    promoted = promoted.replace('data-release-version="2.7"', 'id="versions" data-release-version="2.7"', 1)
                historical = ''
            text = text[:previous.start()] + historical + text[previous.end():]
            text = re.sub(pattern(r'2\.7'), lambda m: promoted, text, count=1, flags=re.S)
            path.write_text(text)
    for path in ROOT.rglob('*.html'):
        if 'snory-teller' in path.relative_to(ROOT).parts or 'windows-app' in path.relative_to(ROOT).parts:
            continue
        text = path.read_text()
        updated = text.replace('<span id="site-footer-version">Record Picker · 2.6</span>', '<span id="site-footer-version">Record Picker · 2.7</span>')
        updated = updated.replace('"softwareVersion":"2.6"', '"softwareVersion":"2.7"')
        if updated != text:
            updated = re.sub(r'("dateModified":")[^"]+', r'\g<1>2026-10-03', updated)
            path.write_text(updated)
    path = ROOT / 'data/release-state.json'
    state = json.loads(path.read_text())
    state['publication_assets']['screenshot_version'] = '2.6'
    state['current_release']['version'] = '2.7'
    for platform in ('iphone', 'ipad', 'watch', 'mac'):
        state['current_release']['platform_versions'][platform] = '2.7'
    state['current_release']['required_platforms_for_full_release'] = ['iphone', 'ipad', 'watch', 'mac']
    state['historical_releases'] = ['2.6'] + [v for v in state['historical_releases'] if v != '2.6']
    state.pop('next_release', None)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    print('Published approved Apple 2.7 in 33 site variants; Windows stays 2.6.')


if __name__ == '__main__':
    main()
