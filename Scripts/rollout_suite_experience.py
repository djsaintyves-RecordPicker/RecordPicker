"""Apply the approved RPS web experience to content pages, preserving content/SEO."""
from pathlib import Path
import re
from lxml import html
from site_campaign_links import normalize
from site_snory_metadata import normalize as snory_metadata
from site_guide_identity import normalize as guide_identity
ROOT=Path(__file__).resolve().parents[1]
CSS='<link rel="stylesheet" href="/assets/css/suite-experience.css?v=20261022-all-pages">'
JS='<script src="/assets/js/suite-experience.js?v=20261022-smooth" defer></script>'
def classes(raw,items):
 def update(m):
  tag=m[0];old=re.search(r'class="([^"]*)"',tag);current=old[1].split() if old else []
  current=list(dict.fromkeys(current+items));value='class="'+' '.join(current)+'"'
  return tag[:old.start()]+value+tag[old.end():] if old else tag[:-1]+' '+value+'>'
 return re.sub(r'<body\b[^>]*>',update,raw,count=1)
def brand(raw):
 def transform(m):
  block=m[0]
  if 'studio-brand-composition' in block:return block
  image=re.search(r'<img\b[^>]*src="/assets/brand/rps/logo.webp"[^>]*>',block)
  if not image:return block
  pieces='<span class="studio-brand-composition" aria-hidden="true">'+''.join('<img class="brand-piece brand-piece-'+part+'" src="/assets/brand/rps/logo.webp" alt="" width="1846" height="763"'+(' fetchpriority="high"' if part=='symbol' else '')+'>' for part in ['symbol','name','studio'])+'</span>'
  return '<div class="studio-introduction">'+block.replace(image[0],pieces,1)+'</div>'
 return re.sub(r'<h1 class="studio-brand">.*?</h1>\s*<p class="intro">.*?</p>',transform,raw,count=1,flags=re.S)
changed=[];counts={}
for p in ROOT.rglob('*.html'):
 if '.git' in p.parts:continue
 before=p.read_text();s=before
 if '<body' not in s or '<main' not in s:continue
 d=html.fromstring(s)
 if d.xpath('//meta[translate(@http-equiv,"REFSH","refsh")="refresh"]'):continue
 existing=(d.xpath('//body/@class') or [''])[0].split();rel=str(p.relative_to(ROOT))
 kind=next((x for x in ['suite-studio','suite-record-picker','suite-snory','suite-physical'] if x in existing),None)
 if not kind:
  if rel.startswith('meal-picker/'):kind='suite-meal'
  elif '/record-picker/guides/' in '/'+rel:kind='suite-guide-record'
  elif '/snory-teller-guide/' in '/'+rel:kind='suite-guide-snory'
  elif '/physical-routine-guide/' in '/'+rel:kind='suite-guide-physical'
  else:continue
 s=classes(s,['rps-suite','suite-experience',kind])
 s=re.sub(r'<link[^>]*href="/assets/css/(?:studio-shadow-study|suite-experience)\.css[^\"]*"[^>]*>','',s)
 s=re.sub(r'<script[^>]*src="/assets/js/(?:studio-motion-study|suite-experience)\.js[^\"]*"[^>]*>\s*</script>','',s)
 if kind=='suite-studio':s=brand(s)
 s=s.replace('</head>',CSS+'</head>',1).replace('</body>',JS+'</body>',1)
 s=normalize(s) if "campaign-links.js" in before else s
 if kind in {"suite-guide-snory","suite-guide-physical"}:s=guide_identity(s,"snory-guide" if kind=="suite-guide-snory" else "physical-guide","no" if rel.startswith("no/") else d.get("lang"))
 if kind=="suite-snory" and p.name=="index.html" and p.parent.parent==ROOT/"snory-teller":s=snory_metadata(s)
 counts[kind]=counts.get(kind,0)+1
 if s!=before:p.write_text(s);changed.append(rel)
print('Suite rollout:',len(changed),'changed;',counts)
