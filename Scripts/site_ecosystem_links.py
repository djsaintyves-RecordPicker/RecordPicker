"""Keep Physical Routine destinations real across all localized creator pages."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
LEGACY='my-physical-routine.mdvnc9v49c.chatgpt.site'

def physical_destination(locale):
 language=locale.split('-')[0]
 if language=='fr': return '/physical/fr/about/'
 if language=='en': return '/physical/about/'
 return '/'+locale.lower()+'/physical-routine-guide/'

def normalize(raw,locale):
 destination=physical_destination(locale)
 assert (ROOT/destination.lstrip('/')/'index.html').is_file(),destination
 def replace(match):
  value=match.group(2);url=urlsplit(value)
  obsolete=url.netloc==LEGACY
  missing=url.netloc=='recordpicker.app' and re.fullmatch(r'/physical/(?:fr/)?about/[^/]+/',url.path)
  product=url.netloc in ('','recordpicker.app') and url.path in ('/physical/about/','/physical/fr/about/')
  if obsolete or missing or product:return match.group(1)+destination+match.group(3)
  return match.group(0)
 return re.sub(r'(<a\b[^>]*\bhref=")([^"]+)(")',replace,raw)

def pages():
 manifest=json.loads((ROOT/'data/creator-hub/manifest.json').read_text())
 for url in manifest['pages']:
  route=urlsplit(url).path
  locale=next((loc for loc in manifest['locales'] if loc!='en-US' and route.startswith('/'+('fr' if loc=='fr-FR' else loc.lower())+'/')), 'en-US')
  yield ROOT/route.lstrip('/')/'index.html',locale
 snory=json.loads((ROOT/'data/snory-localization/manifest.json').read_text())
 for url in snory['pages']:
  route=urlsplit(url).path
  yield ROOT/route.lstrip('/')/'index.html',route.split('/')[2]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
 changed=[];count=0
 for path,locale in pages():
  before=path.read_text();after=normalize(before,locale);count+=1
  if before!=after:
   changed.append(str(path.relative_to(ROOT)))
   if args.write:path.write_text(after)
 if args.write:
  path=ROOT/'data/creator-hub/templates.json';templates=json.loads(path.read_text())
  for key,raw in templates.items():templates[key]=normalize(raw,'fr-FR' if key.startswith('fr-') else 'en-US')
  path.write_text(json.dumps(templates,ensure_ascii=False,indent=2)+'\n')
  path=ROOT/'data/snory-localization/templates.json';templates=json.loads(path.read_text())
  for key,raw in templates.items():templates[key]=normalize(raw,key.split(':',1)[0])
  path.write_text(json.dumps(templates,ensure_ascii=False,indent=2)+'\n')
  for filename in ('sitemap.xml','sitemap-media.xml'):
   path=ROOT/filename;raw=path.read_text()
   for relative in changed:
    url='https://recordpicker.app/'+relative.removesuffix('index.html')
    raw=re.sub(r'(<loc>'+re.escape(url)+r'</loc>\s*<lastmod>)[^<]+',r'\g<1>2026-10-22',raw)
   path.write_text(raw)
  path=ROOT/'data/ecosystem-links-2026-10-22.json'
  previous=json.loads(path.read_text()).get('pages',[]) if path.exists() else []
  path.write_text(json.dumps({'pages':sorted(set(previous+changed)),'scope':'Retire legacy Physical Routine hosting and nonexistent language subpaths; use existing product pages or localized guides.'},ensure_ascii=False,indent=2)+'\n')
 elif changed:raise SystemExit('Obsolete ecosystem destinations: '+', '.join(changed))
 print(f'Ecosystem links checked on {count} creator pages; {len(changed)} pages '+('updated' if args.write else 'require changes'))

if __name__=='__main__':main()
