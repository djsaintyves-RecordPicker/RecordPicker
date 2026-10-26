"""Align current RP version markers after the publisher confirms Windows 3.2.1.

Keep historical feature copy and actual screenshot provenance unchanged.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = '3.2.1'


def normalize(source):
    source = re.sub(r'(Windows(?: ·)? )3\.2(?![\d.])', r'\g<1>' + VERSION, source)
    source = re.sub(r'(iOS |Mac )3\.2(?![\d.])', r'\g<1>' + VERSION, source)
    source = re.sub(r'(<span id="site-footer-version">Record Picker · )3\.2(</span>)', r'\g<1>' + VERSION + r'\2', source)
    source = re.sub(r'("softwareVersion"\s*:\s*")3\.2(")', r'\g<1>' + VERSION + r'\2', source)
    source = source.replace('Windows · 3.2 —', 'Windows · 3.2.1 —')
    for attr in ('data-release-version', 'data-windows-version'):
        source = source.replace(attr + '="3.2"', attr + '="' + VERSION + '"')
    # All Studio locales show the same current version, without translating
    # existing 3.2 feature descriptions into unverified Windows patch notes.
    def studio_card(match):
        card = match[0]
        card = re.sub(r'(<summary>[^<]*?)3\.2(?![\d.])', r'\g<1>' + VERSION, card)
        card = card.replace('3.2.1 · iOS / Mac</summary>', '3.2.1 · iOS / Mac / Windows</summary>')
        return card
    return re.sub(r'<article\b[^>]*id="record-picker"[^>]*>.*?</article>', studio_card, source, flags=re.S)


def main():
    state_path = ROOT / 'data/release-state.json'
    state = json.loads(state_path.read_text())
    if tuple(map(int, state['current_release']['version'].split('.'))) > (3, 2, 1):
        raise SystemExit('A newer release is published; refusing to downgrade.')
    for key in ('current_release', 'next_release'):
        state[key]['version'] = VERSION
        state[key]['platform_versions'] = {platform: VERSION for platform in state[key]['platform_versions']}
    state['historical_releases'] = list(dict.fromkeys(['3.2'] + state['historical_releases']))
    verified = state['verified_public_versions']
    verified['record_picker']['windows'] = VERSION
    verified['checked_at'] = '2026-10-26'
    verified['windows_note'] = 'Publisher confirms Microsoft Partner Center approval of marketing version 3.2.1 on 2026-10-26. No new package build number inferred.'
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    publication_path = ROOT / 'data/rp-3.2.1-publication-2026-10-26.json'
    publication = json.loads(publication_path.read_text())
    publication.pop('windowsMarketingVersionRetained', None)
    publication['windowsMarketingVersion'] = VERSION
    publication['windowsConfirmation'] = {'date': '2026-10-26', 'source': 'Publisher confirmation: RP 3.2.1 approved by Microsoft Partner Center'}
    publication['scope'] = 'Current platform version markers across all localized pages; concise Studio news; screenshot provenance preserved'
    publication_path.write_text(json.dumps(publication, ensure_ascii=False, indent=2) + '\n')
    offer_path = ROOT / 'data/release-notes/3.0-offer.json'
    offer = json.loads(offer_path.read_text())
    for value in offer.values():
        value['status'] = value['status'].replace('Windows · 3.2 —', 'Windows · 3.2.1 —')
    offer_path.write_text(json.dumps(offer, ensure_ascii=False, indent=2) + '\n')
    changed = []
    for path in ROOT.rglob('*.html'):
        if '.git' in path.parts:
            continue
        before = path.read_text()
        after = normalize(before)
        if after != before:
            path.write_text(after)
            changed.append(str(path.relative_to(ROOT)))
    print(f'Updated {len(changed)} pages')


if __name__ == '__main__':
    main()
