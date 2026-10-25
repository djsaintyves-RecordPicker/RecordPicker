"""Publish Record Picker 3.2; preserve other apps and screenshot provenance."""
from pathlib import Path
import json,re
from html import escape
ROOT=Path(__file__).resolve().parents[1]
NOTES=json.loads((ROOT/'data/release-notes/3.2.json').read_text())
changed=[]
for p in ROOT.rglob('*.html'):
 s=p.read_text();before=s
 # 3.1.2 is the current RP release throughout the existing public pages.
 s=s.replace('3.1.2','3.2')
 lang=re.search(r'<html[^>]*lang="([^"]+)"',s,re.I)
 key=(lang.group(1) if lang else 'en').lower()
 aliases={'en-us':'en','fr-fr':'fr','ar-sa':'ar','es-es':'es'}
 key=aliases.get(key,key)
 notes=NOTES.get(key,NOTES['en'])
 summary='<p class="release-32-summary">'+escape(notes)+'</p>'
 s=re.sub(r'(<(?:section|article)[^>]*data-release-version="3\.2"[^>]*>.*?</h2>)(?!<p class="release-32-summary">)',lambda m:m[1]+summary,s,flags=re.S)
 if 'id="record-picker"' in s:
  s=re.sub(r'(<article[^>]*id="record-picker".*?<div class="project-card-body">)(?!<p class="release-32-summary">)',lambda m:m[1]+'<p class="release-32-summary"><strong>Record Picker 3.2</strong> · '+escape(notes)+'</p>',s,flags=re.S)
 if s!=before:p.write_text(s);changed.append(str(p.relative_to(ROOT)))
p=ROOT/'data/release-state.json';d=json.loads(p.read_text())
for key in ('current_release','next_release'):
 d[key]['version']='3.2'
 d[key]['platform_versions']={k:'3.2' for k in d[key]['platform_versions']}
d['next_release']['platforms'].update(android='closed_beta',chromeos='closed_beta')
d['next_release']['distribution'].update(android='closed_beta',chromeos='closed_beta')
d['historical_releases']=list(dict.fromkeys(['3.1.2']+d['historical_releases']))
v=d['verified_public_versions'];v['checked_at']='2026-10-25';v['record_picker']={k:'3.2' for k in v['record_picker']}
v['ios_note']='Apple public listing version3.2; release2026-10-23T23:20:02Z; publisher confirms all Apple platforms.'
v['mac_note']='Publisher confirms macOS3.2 distributed. Actual screenshot provenance remains3.0.1.'
v['windows_note']='Partner Center submission11 published, x64/ARM64 bundles3.2.0.0/3.2.1.0. Marketing3.2.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'data/release-notes/3.0-offer.json';d=json.loads(p.read_text())
for v in d.values():v['status']=v['status'].replace('3.1.2','3.2')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Updated',len(changed),'pages')
