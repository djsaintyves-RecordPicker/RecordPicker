"""Verify all 50 MPR product/support/privacy locales and automatic-language assets."""
from pathlib import Path
from urllib.parse import urlsplit
import json
from lxml import html
ROOT=Path(__file__).resolve().parents[1]
def audit():
 manifest=json.loads((ROOT/'data/physical-localization/manifest.json').read_text());locales=manifest['locales']
 assert len(locales)==50 and len(manifest['pages'])==150
 pages=sorted((ROOT/'physical').rglob('*.html'));assert len(pages)==150
 for page in pages:
  text=page.read_text();d=html.fromstring(text);route='/'+str(page.relative_to(ROOT).parent)+'/'
  assert d.xpath('//link[@rel="canonical"]/@href')==['https://recordpicker.app'+route],page
  assert d.get('data-physical-locale') in locales and d.get('dir') in ('ltr','rtl'),page
  assert d.get('dir')==('rtl' if d.get('lang').split('-')[0] in ('ar','he','ur') else 'ltr'),page
  assert len(d.xpath('//h1'))==1 and d.xpath('//main[@id="main"]'),page
  assert not d.xpath('//select|//nav[@aria-label="Languages"]|//*[@class="language-nav"]'),page
  assert len(d.xpath('//link[@rel="alternate"]'))==51,page
  alternates=d.xpath('//link[@rel="alternate"]/@href')
  assert set(alternates)=={u for u in manifest['pages'] if u.endswith('/'+page.parent.name+'/')},page
  scripts=d.xpath('//script[@src]/@src');assert any(x.startswith('/physical/locale.js?v=') for x in scripts),page
  assert all(urlsplit(x).path in ('/physical/locale.js','/assets/js/suite-experience.js') for x in scripts),page
  assert not d.xpath('//script[not(@src) and not(@type="application/ld+json")]'),page
  for s in d.xpath('//script[@type="application/ld+json"]/text()'):
   obj=json.loads(s);assert obj['@type']=='SoftwareApplication' and obj['name']=='My Physical Routine' and obj['inLanguage']==d.get('lang'),page
  for href in d.xpath('//*[@href]/@href|//*[@src]/@src'):
   u=urlsplit(href)
   if u.netloc and u.netloc!='recordpicker.app':continue
   if u.scheme not in ('','http','https'):continue
   if not u.path:continue
   target=ROOT/u.path.lstrip('/') if u.path.startswith('/') else page.parent/u.path
   if target.is_dir():target/='index.html'
   assert target.is_file(),(page,href)
 print('Physical: 150 pages, 50 locales, no selectors, RTL, reciprocal language links and local assets validated')
if __name__=='__main__':audit()
