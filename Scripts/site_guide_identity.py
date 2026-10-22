"""Keep app guide identity and visible breadcrumbs consistent across localizations."""
import argparse
from html import escape,unescape
import json
from pathlib import Path
import re
from site_social_identity import normalize as normalize_social
ROOT=Path(__file__).resolve().parents[1]
BRANDS={'snory-guide':'Snory Teller','physical-guide':'My Physical Routine'}

def normalize(raw,kind,locale):
 if kind not in BRANDS:return raw
 brand=BRANDS[kind]
 canonical=re.search(r'<link\b(?=[^>]*rel="canonical")(?=[^>]*href="([^"]+)")[^>]*>',raw).group(1)
 current=re.search(r'<h1[^>]*>(.*?)</h1>',raw,re.S);assert current
 label=unescape(re.sub('<[^>]+>','',current.group(1))).strip()
 if label.startswith(brand+' — '):label=label[len(brand)+3:]
 title=brand+' — '+label
 raw=re.sub(r'<title>.*?</title>','<title>'+escape(title)+'</title>',raw,count=1,flags=re.S)
 raw=re.sub(r'(<h1[^>]*>).*?(</h1>)',lambda m:m.group(1)+escape(title)+m.group(2),raw,count=1,flags=re.S)
 prefix='' if locale=='en-US' else 'fr/' if locale=='fr-FR' else locale.lower()+'/'
 hub='/'+prefix+'apps/'
 product='/snory-teller/'+locale+'/' if kind=='snory-guide' else hub+'#physical-routine'
 items=[('Record Picker Studio','https://recordpicker.app'+hub),(brand,'https://recordpicker.app'+product),(label,unescape(canonical))]
 nav='<nav class="project-nav guide-breadcrumbs" aria-label="'+escape(brand,quote=True)+'"><a href="'+hub+'">Record Picker Studio</a><span aria-hidden="true">›</span><a href="'+product+'">'+escape(brand)+'</a><span aria-hidden="true">›</span><span aria-current="page">'+escape(label)+'</span></nav>'
 raw=re.sub(r'<nav class="project-nav guide-breadcrumbs".*?</nav>','',raw,flags=re.S)
 raw,count=re.subn(r'(<article class="guide detail-page">)',lambda m:m.group(1)+nav,raw,count=1)
 assert count==1,(kind,locale,'guide article missing')
 raw=re.sub(r'<script\b(?=[^>]*id="guide-breadcrumb-schema")[^>]*>.*?</script>','',raw,flags=re.S)
 schema={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':url} for i,(name,url) in enumerate(items)]}
 raw=raw.replace('</head>','<script type="application/ld+json" id="guide-breadcrumb-schema">'+json.dumps(schema,ensure_ascii=False,separators=(',',':'))+'</script></head>',1)
 return normalize_social(raw,kind)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
 locales='ar-SA bn-BD ca cs da de-DE el en-AU en-CA en-GB en-US es-ES es-MX fi fr-CA fr-FR gu-IN he hi hr hu id it ja kn-IN ko ml-IN mr-IN ms nl-NL no or-IN pa-IN pl pt-BR pt-PT ro ru sk sl-SI sv ta-IN te-IN th tr uk ur-PK vi zh-Hans zh-Hant'.split()
 pages=[];missing=[]
 for loc in locales:
  prefix='' if loc=='en-US' else 'fr/' if loc=='fr-FR' else loc.lower()+'/'
  for kind,route in [('snory-guide','snory-teller-guide/'),('physical-guide','physical-routine-guide/')]:
   relative=prefix+route+'index.html';path=ROOT/relative;before=path.read_text();after=normalize(before,kind,loc)
   if after!=before:
    if args.write:path.write_text(after)
    else:missing.append(relative)
   pages.append(relative)
 if missing:raise AssertionError('Guide identity needs update: '+', '.join(missing))
 if args.write:
  (ROOT/'data/app-guide-identity-2026-10-22.json').write_text(json.dumps({'pages':pages,'purpose':'Explicit app names and matching visible/structured breadcrumbs; existing guide content, screenshots, store URLs and canonicals preserved'},ensure_ascii=False,indent=2)+'\n')
 print('App guide identity: '+str(len(pages))+' pages '+('updated' if args.write else 'validated'))
if __name__=='__main__':main()
