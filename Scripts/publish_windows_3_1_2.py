"""Publish verified Windows 3.1.2 labels, preserving Apple versions and capture provenance."""
from pathlib import Path
import json
import re
from lxml import html
from html import escape
ROOT=Path(__file__).resolve().parents[1]
OLD='iPhone · iPad · Apple Watch · Windows · 3.1.1 / Mac · 3.0.1'
NEW='iPhone · iPad · Apple Watch · 3.1.1 / Windows · 3.1.2 / Mac · 3.0.1'
def normalize(s,windows=False,studio=False):
 s=s.replace(OLD,NEW).replace('Windows 3.1.1','Windows 3.1.2')
 if windows:
  s=s.replace("quality.css?v=20261008-free-light-pro","quality.css?v=20261022-windows312")
  doc=html.fromstring(s)
  store=doc.xpath('//a[contains(@href,"apps.microsoft.com/detail/9N2ZWRL4M3JC")]/@href')
  if store:
   header=re.search(r"<header\b.*?</header>",s,re.S)
   if header:
    updated=re.sub(r'<a\b[^>]*class="store-link"[^>]*>.*?</a>',lambda _: '<a class="store-link" href="'+escape(store[0],quote=True)+'" data-umami-event="store_click" data-umami-event-app="record_picker" data-umami-event-destination="microsoft">Microsoft Store</a>',header[0],count=1,flags=re.S)
    s=s[:header.start()]+updated+s[header.end():]
  s=s.replace('data-windows-version="3.1.1"','data-windows-version="3.1.2"')
  s=re.sub(r'("softwareVersion"\s*:\s*")3\.1\.1(")',r'\g<1>3.1.2\2',s)
  s=s.replace('<span id="site-footer-version">Record Picker · 3.1.1</span>','<span id="site-footer-version">Record Picker · 3.1.2</span>')
  s=re.sub(r'(<p class="kicker windows-release-version">Windows · 3.1.2</p>)(?:\1)+',r'\1',s)
  if 'windows-release-version"' not in s:
   s=re.sub(r'(<section\b[^>]*class="[^"]*windows-release[^"]*"[^>]*>\s*<div class="section-head">)',r'\1<p class="kicker windows-release-version">Windows · 3.1.2</p>',s,count=1)
 if studio:
  def card(m):
   text=m[0]
   if 'class="availability windows-public-version"' not in text:
    text=text.replace('<div class="project-card-body">','<div class="project-card-body"><p class="availability windows-public-version">Windows · 3.1.2</p>',1)
   node=html.fromstring(text)
   version=node.xpath('.//p[@class="availability windows-public-version"]')[0]
   body=version.getparent();body.remove(version);body.append(version)
   return html.tostring(node,encoding="unicode",with_tail=False)
  s=re.sub(r'<article\b[^>]*id="record-picker"[^>]*>.*?</article>',card,s,flags=re.S)
 return s

def main():
 p=ROOT/'data/release-state.json';d=json.loads(p.read_text());assert d['current_release']['platform_versions']['iphone']=='3.1.1';assert d['current_release']['platform_versions']['mac']=='3.0.1'
 d['current_release']['platform_versions']['windows']='3.1.2';d['next_release']['platform_versions']['windows']='3.1.2'
 v=d['verified_public_versions'];v['record_picker']['windows']='3.1.2';v['windows_note']='Partner Center submission 10 confirmed published on 2026-10-22; marketing 3.1.2, x64 package 3.1.4.0, ARM64 package 3.1.5.0.';v['sources']['windows']='https://apps.microsoft.com/detail/9N2ZWRL4M3JC';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 changed=[]
 for p in ROOT.rglob('*.html'):
  if '.git' in p.parts:continue
  before=p.read_text();after=normalize(before,p.parent.name=='windows-app',p.parent.name=='apps')
  if before!=after:p.write_text(after);changed.append(str(p.relative_to(ROOT)))
 p=ROOT/'data/release-notes/3.0-offer.json';d=json.loads(p.read_text())
 for v in d.values():v['status']=v['status'].replace(OLD,NEW)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/windows-publication-2026-10-22.json').write_text(json.dumps({'marketingVersion':'3.1.2','submission':10,'changedPages':sorted(set(changed + (json.loads((ROOT/'data/windows-publication-2026-10-22.json').read_text()).get('changedPages',[]) if (ROOT/'data/windows-publication-2026-10-22.json').exists() else []))),'applePublicVersions':{'ios':'3.1.1','mac':'3.0.1'},'captureVersion':'3.0.1','noNewScreenshots':True},ensure_ascii=False,indent=2)+'\n')
 print('Updated',len(changed),'pages; Apple versions and screenshot labels preserved.')
if __name__=='__main__':main()
