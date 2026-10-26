#!/usr/bin/env python3
"""Validate independent MOOP support/privacy routes without RP release assumptions."""
from html import unescape
from html.parser import HTMLParser
import json,re
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
SITE='https://recordpicker.app'
ROUTES=['/moop/']+[f'/moop/{locale}/{kind}' for locale in ['fr','en'] for kind in ['', 'privacy/', 'support/']]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.title='';self.in_title=False;self.lang='';self.h1=0;self.canonical=[];self.alternates={};self.links=[];self.assets=[];self.ids=set();self.skip=False;self.scripts=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang','')
  if tag=='title':self.in_title=True
  if tag=='h1':self.h1+=1
  if a.get('id'):self.ids.add(a['id'])
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href',''))
  if tag=='link' and a.get('rel')=='alternate':self.alternates[a.get('hreflang')]=a.get('href')
  if tag=='a':self.links.append(a.get('href',''));self.skip=self.skip or a.get('href')=='#main'
  if tag in ['img','script'] and a.get('src'):self.assets.append(a['src'])
  if tag=='link' and a.get('rel') in ['stylesheet','icon']:self.assets.append(a.get('href',''))
  if tag=='script':self.scripts.append(a.get('type',''))
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
 def handle_data(self,data):
  if self.in_title:self.title+=data

def main():
 for route in ROUTES:
  path=ROOT/route.lstrip('/')/'index.html';assert path.is_file(),route
  raw=path.read_text();p=Page();p.feed(raw)
  assert p.title and p.h1==1 and p.lang and p.skip and 'main' in p.ids,route
  assert p.canonical==[SITE+route],(route,p.canonical)
  assert set(p.alternates)=={'fr-FR','en','x-default'},route
  assert '<meta name="description"' in raw and 'support@recordpicker.app' in raw,route
  assert not any(word in raw.lower() for word in ['example.com','lorem ipsum','todo','à renseigner','placeholder','app-store-badge']),route
  assert all(kind=='application/ld+json' for kind in p.scripts),route
  assert all(not urlsplit(value).scheme and value.startswith('/moop/') for value in p.assets),route
  for value in p.links+p.assets:
   url=urlsplit(unescape(value))
   if url.scheme in ['mailto','tel'] or (url.scheme and url.netloc!='recordpicker.app') or not url.path:continue
   target=ROOT/url.path.lstrip('/') if url.path.startswith('/') else path.parent/url.path
   if target.is_dir():target=target/'index.html'
   assert target.is_file(),(route,value)
  for payload in re.findall(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S):assert json.loads(payload)['@type']=='WebPage'
 for name in ['sitemap.xml','sitemap-media.xml']:
  text=(ROOT/name).read_text()
  for route in ROUTES:assert text.count('<loc>'+SITE+route+'</loc>')==1,(name,route)
 for locale in ['fr','en']:
  for kind in ['privacy','support']:
   text=(ROOT/f'moop/content/{kind}-{locale}.md').read_text()
   assert text.strip(),(locale,kind)
   raw=(ROOT/f'moop/{locale}/{kind}/index.html').read_text()
   for block in re.split(r'\n\s*\n',text.strip()):
    assert unescape(block.strip().lstrip('# ')) in unescape(re.sub('<[^>]*>','',raw)),(locale,kind,block[:60])
 print('MOOP: 7 real pages; FR/EN privacy+support, exact resource content, contact, local links/assets, metadata, accessibility landmarks and both sitemaps validated. No publishing performed.')
if __name__=='__main__':main()
