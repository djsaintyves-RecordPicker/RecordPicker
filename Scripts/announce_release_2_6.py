#!/usr/bin/env python3
"""Announce 2.6 without changing the available 2.5 release or download links."""
from pathlib import Path
from html import escape
import json,re
from announce_release_2_3_1 import LOCALES, COMING_SOON
ROOT=Path(__file__).resolve().parents[1]
def main():
 count=0
 for directory,locale in LOCALES.items():
  for rel in ('index.html','readme/index.html','screenshots/index.html','mac-app/index.html'):
   path=ROOT/directory/rel
   text=path.read_text()
   tag='article' if rel=='readme/index.html' else 'section'
   title='h3' if tag=='article' else 'h2'
   css='release-card release-upcoming' if tag=='article' else 'section next-release'
   status=escape(COMING_SOON[locale])
   block=(f'<{tag} class="{css}" data-release-version="2.6">'
          f'<div class="section-head"><p class="kicker">{status}</p>'
          f'<{title}>Record Picker 2.6 “Snow Leopard”</{title}>'
          f'<p class="release-platform-summary"><strong>iPhone · iPad · Apple Watch · Mac · Windows · {status}</strong></p></div></{tag}>')
   if tag=='article':
    block=block.replace(f'<div class="section-head"><p class="kicker">{status}</p>', '<div>')
   pattern=r'<'+tag+r'\b[^>]*data-release-version="2\.6"[^>]*>.*?</'+tag+'>'
   if re.search(pattern,text,re.S): new=re.sub(pattern,lambda m:block,text,flags=re.S)
   else:
    marker=re.search(r'<'+tag+r'\b[^>]*data-release-version="2\.5"[^>]*>',text)
    if not marker:raise RuntimeError(str(path))
    new=text[:marker.start()]+block+text[marker.start():]
   if new!=text:path.write_text(new);count+=1
 statepath=ROOT/'data/release-state.json';state=json.loads(statepath.read_text())
 state['next_release']={'version':'2.6','platforms':{p:'coming_soon' for p in ('iphone','ipad','watch','mac','windows')}}
 statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
 print(f'Updated {count} pages; 2.5 remains available.')
if __name__=='__main__':main()
