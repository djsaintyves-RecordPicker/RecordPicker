"""Keep Deezer available in the Studio music menu using its public playlist."""
from pathlib import Path
import argparse
import re

ROOT = Path(__file__).resolve().parents[1]
DEEZER = 'https://www.deezer.com/playlist/15860974261'

def normalize(text):
 def header(match):
  block = match[0]
  block = re.sub(r'\b(iOS|macOS|Windows) · Record Picker', r'Record Picker · \1', block)
  def beta_label(anchor):
   def label(span):
    text = span[1]
    if text.startswith('Record Picker ·'): return span[0]
    detail = text.replace('Android', '').strip()
    return '<span>Record Picker · Android — '+detail+'</span>'
   return re.sub(r'<span>(.*?)</span>', label, anchor[0], count=1, flags=re.S)
  block = re.sub(r'<a\b[^>]*class="store-android-beta"[^>]*>.*?</a>', beta_label, block, flags=re.S)
  if 'hub-menu' not in block or 'deezer.com/' in block: return block
  def add(link):
   spotify = link[0]
   deezer = re.sub(r'href="[^"]*"', 'href="'+DEEZER+'"', spotify, count=1)
   deezer = deezer.replace('spotify.svg', 'deezer.svg').replace('Spotify', 'Deezer').replace('"spotify"', '"deezer"')
   return spotify + deezer
  return re.sub(r'<a\b[^>]*href="https://open\.spotify\.com/[^\"]*"[^>]*>.*?</a>', add, block, count=1, flags=re.S)
 return re.sub(r'<header\b[^>]*>.*?</header>', header, text, count=1, flags=re.S)

def main():
 parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--write',action='store_true'); args=parser.parse_args()
 changed=[]
 for path in ROOT.rglob('*.html'):
  if '.git' in path.parts: continue
  before=path.read_text(); after=normalize(before)
  if after!=before:
   changed.append(str(path.relative_to(ROOT)))
   if args.write:path.write_text(after)
 if changed and not args.write:raise SystemExit('Missing Deezer music-menu link: '+', '.join(changed))
 print('OK: Deezer music menu; '+str(len(changed))+' pages updated.')

if __name__=='__main__':main()
