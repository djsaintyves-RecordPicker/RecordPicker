"""Publish verified iOS 3.2.2 without advancing Mac/Windows or screenshot provenance."""
from pathlib import Path
import json
import re
from html import escape
ROOT = Path(__file__).resolve().parents[1]
PUBLICATION = ROOT / 'data/rp-3.2.2-publication-2026-10-27.json'
OLD = 'iPhone · iPad · Mac · Apple Watch · Windows · 3.2.1'
NEW = 'iPhone · iPad · Apple Watch · 3.2.2 / Mac · Windows · 3.2.1'

def normalize(source, route=''):
    source = source.replace(OLD, NEW).replace('Record Picker · iOS 3.2.1 · Mac 3.2.1 · Windows 3.2.1', 'Record Picker · iOS 3.2.2 · Mac 3.2.1 · Windows 3.2.1')
    source = re.sub(r'(<article\b[^>]*class="[^"]*current-release[^"]*"[^>]*data-release-version=")3\.2\.1(")', r'\g<1>3.2.2\2', source)
    if route not in {'mac-app', 'windows-app'}:

        source = re.sub(r'("softwareVersion"\s*:\s*")3\.2\.1(")', r'\g<1>3.2.2\2', source)
        source = source.replace('Record Picker · 3.2.1</span>', 'Record Picker · 3.2.2</span>')
    if (route == 'ios-app' or 'rps-acquisition' in source) and 'data-rp-ios-update="3.2.2"' not in source and '<p class="release-platform-summary">' in source:
        lang = re.search(r'<html[^>]*lang="([^"]+)"', source)[1]
        aliases = {'nb':'no','fr':'fr-FR','en':'en-US','de':'de-DE','nl':'nl-NL','ar':'ar-SA','es':'es-ES'}
        note = json.loads(PUBLICATION.read_text())['releaseNotes'][aliases.get(lang,lang)]
        source = source.replace('<p class="release-platform-summary">', '<p class="release-note" data-rp-ios-update="3.2.2">iOS 3.2.2 · '+escape(note)+'</p><p class="release-platform-summary">', 1)
    if 'id="record-picker"' in source:
        lang = re.search(r'<html[^>]*lang="([^"]+)"', source)[1]
        publication = json.loads(PUBLICATION.read_text())
        aliases = {'nb':'no','fr':'fr-FR','en':'en-US','de':'de-DE','nl':'nl-NL','ar':'ar-SA','es':'es-ES'}
        note = publication['releaseNotes'][aliases.get(lang,lang)]
        def card(match):
            body = match[0]
            news = '<details class="project-update" data-rp-ios-update="3.2.2"><summary>3.2.2 · iPhone / iPad</summary><p class="release-note"><strong>Record Picker 3.2.2</strong> · '+escape(note)+'</p></details>'
            body = re.sub(r'<details\b[^>]*class="project-update"[^>]*>.*?</details>',lambda _:news,body,count=1,flags=re.S)
            body = re.sub(r'(<p class="availability windows-public-version">).*?(</p>)',r'\g<1>iOS · 3.2.2 / Mac · 3.2.1 / Windows · 3.2.1\2',body,flags=re.S)
            return body
        source = re.sub(r'<article\b[^>]*id="record-picker"[^>]*>.*?</article>',card,source,flags=re.S)
    return source

def main():
    notes = json.loads((ROOT/'data/mpr-publication-2026-10-27.json').read_text())['releaseNotes']
    pub = {'version':'3.2.2','platforms':['iPhone','iPad','embedded Apple Watch companion'],'checkedAt':'2026-10-27','publicReleaseDate':'2026-10-27T16:36:54Z','publicIOSFrance':'3.2.2','source':'Apple public lookup and ASC Ready for Distribution observed; publisher confirmation','macVersionRetained':'3.2.1','windowsVersionRetained':'3.2.1','releaseNotes':notes,'screenshotVersionRetained':'3.0.1'}
    PUBLICATION.write_text(json.dumps(pub,ensure_ascii=False,indent=2)+'\n')
    p=ROOT/'data/release-state.json'; state=json.loads(p.read_text())
    if tuple(map(int,state['current_release']['version'].split('.')))>(3,2,2): raise SystemExit('Refusing to downgrade')
    for name in ['current_release','next_release']:
        state[name]['version']='3.2.2'
        for platform in ['iphone','ipad','watch']: state[name]['platform_versions'][platform]='3.2.2'
    state['historical_releases']=list(dict.fromkeys(['3.2.1']+state['historical_releases']))
    verified=state['verified_public_versions']; verified['checked_at']='2026-10-27'; verified['record_picker']['ios']='3.2.2'; verified['ios_note']='ASC Ready for Distribution; Apple public France lookup 3.2.2 released 2026-10-27T16:36:54Z. Optimized for iPhone Duo. Mac/Windows retained at 3.2.1; no Android public release.'
    p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    p=ROOT/'data/release-notes/3.0-offer.json'; offer=json.loads(p.read_text())
    for value in offer.values(): value['status']=value['status'].replace(OLD,NEW)
    p.write_text(json.dumps(offer,ensure_ascii=False,indent=2)+'\n')
    changed=[]
    for p in ROOT.rglob('*.html'):
        if '.git' in p.parts: continue
        before=p.read_text(); after=normalize(before,p.parent.name)
        if before!=after: p.write_text(after); changed.append(str(p.relative_to(ROOT)))
    pub['changedPages']=changed; PUBLICATION.write_text(json.dumps(pub,ensure_ascii=False,indent=2)+'\n')
    print('Updated',len(changed),'pages; Mac/Windows versions preserved')
if __name__=='__main__': main()
