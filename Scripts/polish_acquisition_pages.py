"""Present the reviewed acquisition copy with a shared, restrained visual layout."""
from pathlib import Path
import re
from site_campaign_links import normalize as normalize_campaign_links
ROOT=Path(__file__).resolve().parents[1]
EN=['','en-us/','en-gb/','en-ca/','en-au/']
PAGES=['index.html','fr/index.html','mac-app/index.html','fr/mac-app/index.html','random-vinyl-record-picker/index.html','fr/random-vinyl-record-picker/index.html']+[p+'choose-vinyl-record/index.html' for p in EN]+['fr/choose-vinyl-record/index.html']
GUIDES=['record-picker/guides/import-discogs/index.html','fr/record-picker/guides/import-discogs/index.html','record-picker/guides/choose/index.html','fr/record-picker/guides/choose/index.html']
for relative in PAGES+GUIDES:
 p=ROOT/relative;s=p.read_text();guide=relative in GUIDES;fr=relative.startswith('fr/')
 def body(m):
  t=m[0]
  if 'rps-acquisition' in t:return t
  classes='rps-acquisition'+(' rps-walkthrough' if guide else '')
  return re.sub(r'class="([^"]*)"',lambda x:'class="'+x[1]+' '+classes+'"',t,count=1) if 'class="' in t else t[:-1]+' class="'+classes+'">'
 s=re.sub(r'<body\b[^>]*>',body,s,count=1)
 if 'acquisition-editorial.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/assets/css/acquisition-editorial.css?v=20261022"></head>',1)
 if not guide and 'rps-visual-hero' not in s:
  figure=re.search(r'<figure class="(?:context-visual wide|mac-hero-visual)">.*?</figure>',s,re.S)
  hero=re.search(r'<(header|section) class="doc-hero ([^"]*)">(.*?)</\1>',s,re.S)
  if figure and hero:
   updated='<'+hero[1]+' class="doc-hero '+hero[2]+' rps-visual-hero"><div class="rps-hero-copy">'+hero[3]+'</div>'+figure[0]+'</'+hero[1]+'>'
   s=s.replace(figure[0],'',1).replace(hero[0],updated,1)
 if guide and 'rps-studio-brand' not in s:
  prefix='/fr' if fr else ''
  brand='<a class="rps-studio-brand" href="'+prefix+'/apps/"><img src="/assets/brand/rps/icon-48.png" width="32" height="32" alt=""><span>Record Picker Studio</span></a>'
  s=re.sub(r'<header\b[^>]*>',lambda m:m[0]+brand,s,count=1)
 if guide and 'rps-guide-masthead' not in s:
  h=re.search(r'<h1>.*?</h1>',s,re.S);intro=re.search(r'(<section id="(?:discogs|choose)-walkthrough">)(<p>.*?</p>)',s,re.S);assert h and intro,relative
  pick='/choose/' in relative;image='mac-random-pick' if pick else 'mac-collection'
  label='Record Picker · Guide pratique' if fr else 'Record Picker · Practical guide'
  caption='Record Picker sur Mac · capture en français' if fr else 'Record Picker on Mac · screenshot in French'
  figure='<figure><img src="/assets/screenshots/v301/fr/'+image+'.webp" width="1600" height="1004" alt="'+caption+'" decoding="async"><figcaption>'+caption+'</figcaption></figure>'
  masthead='<div class="rps-guide-masthead"><div><p class="rps-guide-kicker">'+label+'</p>'+h[0]+intro[2]+'</div>'+figure+'</div>'
  s=s.replace(intro[0],intro[1],1).replace(h[0],masthead,1)
 p.write_text(normalize_campaign_links(s))
print('Editorial layout applied to',len(PAGES+GUIDES),'pages')
