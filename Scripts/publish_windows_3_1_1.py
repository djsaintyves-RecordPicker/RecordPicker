"""Record the verified Windows 3.1.1 publication without relabelling captures."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = '3.1.1'
OLD_STATUS = 'iPhone · iPad · Apple Watch · 3.1.1 / Mac · Windows · 3.0.1'
NEW_STATUS = 'iPhone · iPad · Apple Watch · Windows · 3.1.1 / Mac · 3.0.1'

def normalize(raw, windows=False):
    raw = raw.replace(OLD_STATUS, NEW_STATUS)
    raw = re.sub(r'(<span id="site-footer-version">)(.*?)(</span>)',
        lambda m: m[1] + (('Record Picker · ' + VERSION) if windows else m[2].replace('Windows 3.0.1', 'Windows '+VERSION)) + m[3], raw)
    if windows:
        raw = raw.replace('data-windows-version="3.0.1"', 'data-windows-version="'+VERSION+'"')
        raw = re.sub(r'("softwareVersion"\s*:\s*")3\.0\.1(")',r'\g<1>'+VERSION+r'\2',raw)
    return raw

def main():
    p=ROOT/'data/release-state.json';state=json.loads(p.read_text())
    if tuple(map(int,state['current_release']['platform_versions']['windows'].split('.'))) > tuple(map(int,VERSION.split('.'))):
        print('Newer verified Windows release retained.'); return
    assert state['current_release']['version']==VERSION
    state['current_release']['platform_versions']['windows']=VERSION
    required=state['current_release']['required_platforms_for_full_release']
    if 'windows' not in required:required.append('windows')
    p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    paths=[]
    for p in ROOT.rglob('*.html'):
        if '.git' in p.parts:continue
        before=p.read_text();after=normalize(before,p.parent.name=='windows-app')
        if before!=after:p.write_text(after);paths.append(str(p.relative_to(ROOT)))
    p=ROOT/'data/release-notes/3.0-offer.json';data=json.loads(p.read_text())
    for value in data.values():value['status']=value['status'].replace(OLD_STATUS,NEW_STATUS)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('Windows 3.1.1 aligned on',len(paths),'HTML pages; screenshot versions retained.')

if __name__=='__main__':main()
