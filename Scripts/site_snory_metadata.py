"""Describe the verified public Snory Teller app using non-executable JSON-LD."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
class Head(HTMLParser):
 def __init__(self):super().__init__();self.description='';self.canonical='';self.language=''
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.language=a.get('lang','')
  if tag=='meta' and a.get('name')=='description':self.description=a.get('content','')
  if tag=='link' and a.get('rel')=='canonical':self.canonical=a.get('href','')

def normalize(raw):
 head=Head();head.feed(raw)
 assert head.description and head.canonical and head.language
 data={'@context':'https://schema.org','@type':'SoftwareApplication','@id':'https://recordpicker.app/snory-teller/#app','name':'Snory Teller','url':head.canonical,'description':head.description,'applicationCategory':'HealthApplication','operatingSystem':'iOS 16.0 or later; watchOS 9.0 or later','softwareVersion':'1.0.2','downloadUrl':'https://apps.apple.com/app/snory-teller/id6820177689','image':'https://recordpicker.app/snory-teller/icon.png','inLanguage':head.language,'author':{'@type':'Person','name':'Yves Durand'}}
 tag='<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>'
 raw=re.sub(r'<script type="application/ld\+json">.*?</script>','',raw,flags=re.S)
 raw=raw.replace('</head>',tag+'</head>',1)
 language=head.language.split('-')[0]
 if language in ('fr','en') and 'href="/snory-teller/"' not in raw:
  label='Toutes les langues' if language=='fr' else 'All languages'
  raw=raw.replace('</footer>','<p><a href="/snory-teller/">'+label+'</a></p></footer>',1)
 return raw

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
 manifest=json.loads((ROOT/'data/snory-localization/manifest.json').read_text());changed=[]
 for loc in manifest['locales']:
  path=ROOT/'snory-teller'/loc/'index.html';before=path.read_text();after=normalize(before)
  if before!=after:
   changed.append(str(path.relative_to(ROOT)))
   if args.write:path.write_text(after)
 if changed and not args.write:raise SystemExit('Snory metadata differs: '+', '.join(changed))
 print('Snory Teller public app metadata checked on 50 localized homepages; '+str(len(changed))+' updated')

if __name__=='__main__':main()
