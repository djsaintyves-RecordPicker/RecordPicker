from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
OLD='iPhone · iPad · Apple Watch · 3.1.1 / Windows · 3.1.2 / Mac · 3.0.1'
NEW=OLD.replace('Watch · 3.1.1','Watch · 3.1.2')
p=ROOT/'data/release-state.json';d=json.loads(p.read_text())
if tuple(map(int,d['current_release']['version'].split('.'))) > (3,1,2):raise SystemExit('A newer release is already published; refusing to downgrade.')
for key in ['current_release','next_release']:
 d[key]['version']='3.1.2'
 for platform in ['iphone','ipad','watch']:d[key]['platform_versions'][platform]='3.1.2'
d['verified_public_versions']['checked_at']='2026-10-23';d['verified_public_versions']['record_picker']['ios']='3.1.2'
d['verified_public_versions']['ios_note']='Apple public lookup verified 3.1.2 in FR/US/JP/KR; release date 2026-10-22T21:04:34Z. Native Mac version not reverified; retained 3.0.1.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'data/release-notes/3.0-offer.json';d=json.loads(p.read_text())
for cp in d.values():cp['status']=cp['status'].replace(OLD,NEW)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
changed=[]
for p in ROOT.rglob('*.html'):
 if '.git' in p.parts:continue
 before=p.read_text();s=before.replace(OLD,NEW)
 if 'suite-record-picker' in s:
  s=s.replace('data-release-version="3.1.1"','data-release-version="3.1.2"').replace('data-feature-release="3.1.1"','data-feature-release="3.1.2"')
  s=s.replace('Record Picker · iOS 3.1.1','Record Picker · iOS 3.1.2')
  if p.parent.name not in ['mac-app','windows-app']:
   s=s.replace('"softwareVersion":"3.1.1"','"softwareVersion":"3.1.2"').replace('Record Picker · 3.1.1</span>','Record Picker · 3.1.2</span>')
 if p.parent.name=='apps' and 'id="record-picker"' in s:
  s=s.replace('<p class="availability windows-public-version">Windows · 3.1.2</p>','<p class="availability windows-public-version">iPhone · iPad · 3.1.2 / Windows · 3.1.2</p>')
 if s!=before:p.write_text(s);changed.append(str(p.relative_to(ROOT)))
(ROOT/'data/ios-publication-2026-10-23.json').write_text(json.dumps({'version':'3.1.2','platforms':['iPhone','iPad','Apple Watch companion'],'publicReleaseDate':'2026-10-22T21:04:34Z','verifiedCountries':['fr','us','jp','kr'],'macVersionRetained':'3.0.1','windowsVersionRetained':'3.1.2','changedPages':sorted(set(changed + (json.loads((ROOT/'data/ios-publication-2026-10-23.json').read_text()).get('changedPages',[]) if (ROOT/'data/ios-publication-2026-10-23.json').exists() else []))),'captureVersionRetained':'3.0.1'},ensure_ascii=False,indent=2)+'\n')
print('Updated',len(changed),'public pages')
