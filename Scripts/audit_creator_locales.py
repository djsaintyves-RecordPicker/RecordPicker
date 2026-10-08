"""Check complete static locale pages and reciprocal navigation offline."""
import json,re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.alternates={};self.lang=None;self.direction=None;self.h1=0;self.canonical=None;self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang');self.direction=a.get('dir')
  if tag=='h1':self.h1+=1
  if a.get('id'):self.ids.append(a['id'])
  if tag=='link' and a.get('rel')=='alternate':self.alternates[a.get('hreflang')]=a.get('href')
  if tag=='link' and a.get('rel')=='canonical':self.canonical=a.get('href')
  for key in ('href','src'):
   if a.get(key):self.links.append(a[key])
def audit():
 manifest=json.loads((ROOT/'data/creator-hub/manifest.json').read_text());assert len(manifest['locales'])==50
 for url in manifest['pages']:
  path=ROOT/urlsplit(url).path.lstrip('/')/'index.html';text=path.read_text();page=Page();page.feed(text)
  assert page.h1==1 and page.canonical==url,(url,'heading or canonical')
  assert len(page.alternates)==51,(url,'alternates')
  assert 'ZXBRAND' not in text and 'XZ' not in text,(url,'unrestored brand')
  assert page.direction==('rtl' if page.lang.split('-')[0] in ('ar','he','ur') else 'ltr'),url
  for alt,dest in page.alternates.items():
   peer=Page();peer.feed((ROOT/urlsplit(dest).path.lstrip('/')/'index.html').read_text());assert url in peer.alternates.values(),(url,'non-reciprocal',dest)
  for link in page.links:
   u=urlsplit(link)
   if u.scheme or link.startswith('#'):continue
   target=ROOT/u.path.lstrip('/')
   if target.is_dir():target=target/'index.html'
   assert target.is_file(),(url,link)
  for payload in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):json.loads(payload)
  if not url.endswith('/dulpi/'):
   assert page.ids.index('community')<page.ids.index('guide-snory'),url
   for service in ('music.apple.com/fr/playlist/','open.spotify.com/playlist/','deezer.com/fr/playlist/'):assert text.count(service)>=2,(url,service)
   assert 'apps.apple.com/app/recordpicker/id6780422305' in text
   assert 'apps.microsoft.com/detail/9N2ZWRL4M3JC' in text
  else:assert 'https://dulpi.recordpicker.app' not in text,(url,'restricted tool exposed')
 print('Creator localization: 100 pages, 50 locales, reciprocal SEO, assets and store/playlist links validated')
if __name__=='__main__':audit()
