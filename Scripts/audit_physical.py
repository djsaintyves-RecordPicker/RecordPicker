"""Verify all 50 MPR locales without dependencies on the publication runner."""
from pathlib import Path
from urllib.parse import urlsplit
from html.parser import HTMLParser
import json
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.attributes={};self.canonicals=[];self.alternates=[];self.links=[];self.scripts=[];self.schemas=[];self.metadata=None;self.h1=0;self.main=False;self.controls=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.attributes=a
  if tag=='h1':self.h1+=1
  if tag=='main' and a.get('id')=='main':self.main=True
  if tag=='select' or (tag=='nav' and a.get('aria-label')=='Languages') or 'language-nav' in a.get('class','').split():self.controls+=1
  if tag=='link' and a.get('rel')=='canonical':self.canonicals.append(a.get('href'))
  if tag=='link' and a.get('rel')=='alternate':self.alternates.append(a.get('href'))
  if tag=='script':
   if a.get('src'):self.scripts.append(a['src'])
   else:
    assert a.get('type')=='application/ld+json','Unexpected inline script'
    self.metadata=''
  self.links.extend(v for k,v in attrs if k in ('href','src'))
 def handle_data(self,data):
  if self.metadata is not None:self.metadata+=data
 def handle_endtag(self,tag):
  if tag=='script' and self.metadata is not None:self.schemas.append(json.loads(self.metadata));self.metadata=None

def audit():
 manifest=json.loads((ROOT/'data/physical-localization/manifest.json').read_text());locales=manifest['locales']
 assert len(locales)==50 and len(manifest['pages'])==150
 pages=sorted((ROOT/'physical').rglob('*.html'));assert len(pages)==150
 for path in pages:
  page=Page();page.feed(path.read_text());attrs=page.attributes;route='/'+str(path.relative_to(ROOT).parent)+'/'
  assert page.canonicals==['https://recordpicker.app'+route],path
  assert attrs.get('data-physical-locale') in locales,path
  assert attrs.get('dir')==('rtl' if attrs.get('lang').split('-')[0] in ('ar','he','ur') else 'ltr'),path
  assert page.h1==1 and page.main and page.controls==0,path
  assert len(page.alternates)==51,path
  assert set(page.alternates)=={u for u in manifest['pages'] if u.endswith('/'+path.parent.name+'/')},path
  assert any(x.startswith('/physical/locale.js?v=') for x in page.scripts),path
  assert all(urlsplit(x).path in ('/physical/locale.js','/assets/js/suite-experience.js') for x in page.scripts),path
  for obj in page.schemas:
   assert obj['@type']=='SoftwareApplication' and obj['name']=='My Physical Routine' and obj['inLanguage']==attrs['lang'],path
  for href in page.links:
   u=urlsplit(href)
   if u.netloc and u.netloc!='recordpicker.app':continue
   if u.scheme not in ('','http','https') or not u.path:continue
   target=ROOT/u.path.lstrip('/') if u.path.startswith('/') else path.parent/u.path
   if target.is_dir():target/='index.html'
   assert target.is_file(),(path,href)
 print('Physical: 150 pages, 50 locales, no selectors, RTL, reciprocal language links and local assets validated')
if __name__=='__main__':audit()
