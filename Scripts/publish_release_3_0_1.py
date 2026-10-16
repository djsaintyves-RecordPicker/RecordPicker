#!/usr/bin/env python3
"""Publish the verified Apple and Windows 3.0.1 release without changing pricing."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def main():
    state_path=ROOT/'data/release-state.json'
    state=json.loads(state_path.read_text())
    state['current_release']['version']='3.0.1'
    state['current_release']['platform_versions']={p:'3.0.1' for p in state['current_release']['platform_versions']}
    state['next_release']['version']='3.0.1'
    state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    copies_path=ROOT/'data/release-notes/3.0-offer.json'
    copies=json.loads(copies_path.read_text())
    for copy in copies.values():
        copy['status']=f"iPhone · iPad · Apple Watch · Mac · Windows · 3.0.1 — {copy['available_label']}"
        copy['title']=re.sub(r'3\.0(?![.\d])','3.0.1',copy['title'])
    copies_path.write_text(json.dumps(copies,ensure_ascii=False,indent=2)+'\n')
    from announce_release_2_3_1 import LOCALES
    from html import escape
    for directory,locale in LOCALES.items():
        base=ROOT/directory
        for page in base.rglob('*.html'):
            if any(x in page.relative_to(base).parts for x in ('apps','physical','snory-teller','dulpi')):continue
            if not directory and page.relative_to(base).parts[0] in LOCALES:continue
            text=page.read_text()
            text=text.replace('data-release-version="3.0"','data-release-version="3.0.1"')
            parts=re.split(r'(<figure\b.*?</figure>)',text,flags=re.S)
            text=''.join(part if part.startswith('<figure') else re.sub(r'Record Picker 3\.0(?![.\d])','Record Picker 3.0.1',part) for part in parts)
            text=text.replace('Record Picker · 3.0</span>','Record Picker · 3.0.1</span>')
            text=text.replace('"softwareVersion":"3.0"','"softwareVersion":"3.0.1"')
            text=re.sub(r'"dateModified":"[0-9-]+"','"dateModified":"2026-10-16"',text)
            pattern=r'(<(?:section|article)\b[^>]*data-release-version="3\.0\.1"[^>]*>.*?<p class="release-platform-summary">).*?(</p>)'
            text=re.sub(pattern,lambda m:m[1]+escape(copies[locale]['status'])+m[2],text,flags=re.S)
            # Retain still-relevant feature descriptions without presenting 2.7 as current.
            def current_features(match):
                block = match[0].replace('data-release-version="2.7"', 'data-feature-release="3.0.1"')
                block = block.replace('Record Picker 2.7', 'Record Picker 3.0.1')
                return re.sub(r'(<p class="kicker">).*?(</p>)',
                              lambda m: m[1] + escape(copies[locale]['status']) + m[2], block)
            text = re.sub(r'<section\b[^>]*(?:data-release-version="2\.7"|data-feature-release="3\.0\.1")[^>]*>.*?</section>',
                          current_features, text, flags=re.S)
            if text!=page.read_text():page.write_text(text)
if __name__=='__main__':main()
