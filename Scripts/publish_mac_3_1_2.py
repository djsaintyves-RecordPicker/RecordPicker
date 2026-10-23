"""Align current Mac 3.1.2 release labels; preserve historical capture provenance."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
OLD='iPhone · iPad · Apple Watch · 3.1.2 / Windows · 3.1.2 / Mac · 3.0.1'
NEW='iPhone · iPad · Mac · Apple Watch · Windows · 3.1.2'
changed=[]
for p in ROOT.rglob('*.html'):
    before=p.read_text();s=before.replace(OLD,NEW).replace('Record Picker · iOS 3.1.2 · Mac 3.0.1 · Windows 3.1.2','Record Picker · iOS 3.1.2 · Mac 3.1.2 · Windows 3.1.2')
    if p.parent.name=='mac-app':
        s=re.sub(r'("softwareVersion"\s*:\s*")3\.0\.1(")',r'\g<1>3.1.2\2',s)
        s=s.replace('Record Picker · 3.0.1</span>','Record Picker · 3.1.2</span>')
    if p.parent.name=='apps':
        s=s.replace('iPhone · iPad · 3.1.2 / Windows · 3.1.2','iPhone · iPad · Mac · Apple Watch · Windows · 3.1.2')
        s=s.replace('Sur iPhone et iPad, Pro ajoute','Sur iPhone, iPad et Mac, Pro ajoute')
        s=s.replace('On iPhone and iPad, Pro adds','On iPhone, iPad and Mac, Pro adds')
    if s!=before:p.write_text(s);changed.append(str(p.relative_to(ROOT)))
p=ROOT/'data/release-state.json';d=json.loads(p.read_text())
for key in ('current_release','next_release'):
    d[key]['platform_versions']['mac']='3.1.2'
if 'mac' not in d['current_release']['required_platforms_for_full_release']:d['current_release']['required_platforms_for_full_release'].append('mac')
d['verified_public_versions']['record_picker']['mac']='3.1.2'
d['verified_public_versions']['mac_note']='macOS 3.1.2 approval confirmed by publisher on 2026-10-23; same version as iOS and Windows. Capture provenance remains 3.0.1.'
d['verified_public_versions']['ios_note']='Apple public lookup verified iOS 3.1.2; release date 2026-10-22T21:04:34Z.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'data/release-notes/3.0-offer.json';d=json.loads(p.read_text())
for v in d.values():v['status']=v['status'].replace(OLD,NEW)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'data/studio-news-2026-10-23.json';d=json.loads(p.read_text());d['versions']['recordPickerMac']='3.1.2 approved by Apple, publisher confirmation';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'Scripts/studio_current_updates.py';s=p.read_text().replace('Sur iPhone et iPad, Pro ajoute','Sur iPhone, iPad et Mac, Pro ajoute').replace('On iPhone and iPad, Pro adds','On iPhone, iPad and Mac, Pro adds');p.write_text(s)
(ROOT/'data/mac-publication-2026-10-23.json').write_text(json.dumps({'version':'3.1.2','platform':'macOS','approvalEvidence':'Explicit publisher confirmation on 2026-10-23','changedPages':sorted(set(changed + (json.loads((ROOT/'data/mac-publication-2026-10-23.json').read_text()).get('changedPages',[]) if (ROOT/'data/mac-publication-2026-10-23.json').exists() else []))),'captureVersionRetained':'3.0.1','release32Published':False},ensure_ascii=False,indent=2)+'\n')
print('Updated',len(changed),'pages')
