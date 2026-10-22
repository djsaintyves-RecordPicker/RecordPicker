"""Audit root-relative, relative and absolute same-site hyperlinks alike."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]

class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.canonical='';self.links=[];self.anchors=set()
 def handle_starttag(self,tag,attrs):
  values=dict(attrs)
  if tag=='link' and values.get('rel')=='canonical':self.canonical=values.get('href','')
  if tag=='a' and values.get('href'):self.links.append(values['href'])
  for key in ('id','name'):
   if values.get(key):self.anchors.add(values[key])

def audit():
 failures=[];count=0;pages={};fragments=0
 for path in ROOT.rglob('*.html'):
  if any(part in ('.git','node_modules','work','outputs') for part in path.relative_to(ROOT).parts):continue
  page=Page();page.feed(path.read_text())
  if not page.canonical.startswith('https://recordpicker.app/'):continue
  pages[path.resolve()]=page
  count+=1
  for href in page.links:
   url=urlsplit(href)
   if url.netloc=='my-physical-routine.mdvnc9v49c.chatgpt.site':
    failures.append((str(path.relative_to(ROOT)),href,'obsolete hosting'));continue
   if url.scheme and url.netloc!='recordpicker.app':continue
   if url.netloc and url.netloc!='recordpicker.app':continue
   if not url.path:continue
   target=ROOT/unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent/unquote(url.path)
   if target.is_dir():target=target/'index.html'
   if not target.is_file():failures.append((str(path.relative_to(ROOT)),href,'missing destination'))
 for path,page in pages.items():
  for href in page.links:
   url=urlsplit(href)
   if not url.fragment or url.scheme not in ('','https','http') or (url.netloc and url.netloc!='recordpicker.app') or url.fragment.startswith(':~:'):continue
   target=(ROOT/unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent/unquote(url.path)) if url.path else path
   if target.is_dir():target=target/'index.html'
   destination=pages.get(target.resolve())
   if destination is None:continue
   fragments+=1
   if unquote(url.fragment) not in destination.anchors:failures.append((str(path.relative_to(ROOT)),href,'missing fragment target'))
 if failures:raise AssertionError(json.dumps(failures,ensure_ascii=False,indent=2))
 print(f'Internal links: {count} public HTML pages and {fragments} fragment links; relative and absolute same-site destinations exist; legacy hosting absent')

if __name__=='__main__':audit()
