"""Extend the approved suite design while preserving copy, store attribution and metadata."""
from pathlib import Path
import re,copy
from lxml import html,etree
from site_campaign_links import normalize as campaigns
ROOT=Path(__file__).resolve().parents[1]
STYLE='<link rel="stylesheet" href="/assets/css/suite-product.css?v=20261022-tactile">'
STUDIO='<link rel="stylesheet" href="/assets/css/studio-suite.css?v=20261022-tactile">'
def body_class(raw,classes):
 def change(m):
  tag=m[0]
  for cls in classes.split():
   if re.search(r'\b'+re.escape(cls)+r'\b',tag):continue
   tag=re.sub(r'class="([^"]*)"',lambda x:'class="'+x[1].strip()+' '+cls+'"',tag,count=1) if 'class="' in tag else tag[:-1]+' class="'+cls+'">'
  return tag
 return re.sub(r'<body\b[^>]*>',change,raw,count=1)
def promote_windows_capture(raw):
 d=html.fromstring(raw);old=d.xpath('//section[contains(@class,"windows-screenshot-section")]');hero=d.xpath('//figure[@class="platform-capture-hero"]')
 if not old or not hero:return raw
 sec=old[0];details=etree.Element('details',{'class':'windows-capture-details'});heading=sec.xpath('.//h2')[0];summary=etree.SubElement(details,'summary',{'id':heading.get('id','windows-authentic-title')});summary.text=heading.text_content()
 for para in sec.xpath('.//p'):details.append(copy.deepcopy(para))
 fig=re.search(r'<figure class="platform-capture-hero".*?</figure>',raw,re.S)
 new=fig[0].replace('</figure>',html.tostring(details,encoding='unicode')+'</figure>');raw=raw[:fig.start()]+new+raw[fig.end():]
 return re.sub(r'<section\b[^>]*class="[^"]*windows-screenshot-section[^"]*"[^>]*>.*?</section>','',raw,count=1,flags=re.S)
changed=[]
for p in ROOT.rglob('*.html'):
 if '.git' in p.parts:continue
 before=p.read_text();s=before
 if re.search(r'<link[^>]*href="[^"]*quality\.css\?',s):
  s=body_class(s,'rps-suite suite-record-picker')
  if 'suite-product.css' not in s:s=s.replace('</head>',STYLE+'</head>',1)
  if p.parent.name=='windows-app' and 'platform-symbol windows-symbol' in s:
   d=html.fromstring(s);fig=d.xpath('//section[contains(@class,"windows-screenshot-section")]//figure')
   if fig:
    f=copy.deepcopy(fig[0]);f.set('class','platform-capture-hero')
    for image in f.xpath('.//img'):image.set('loading','eager')
    s=re.sub(r'<div class="platform-symbol windows-symbol"[^>]*>.*?</div>',lambda _:html.tostring(f,encoding='unicode'),s,count=1,flags=re.S)
 if '/apps/' in '/'+str(p.relative_to(ROOT)) and '/apps/assets/' not in '/'+str(p.relative_to(ROOT)):
  s=body_class(s,'rps-suite suite-studio')
  if 'studio-suite.css' not in s:s=s.replace('</head>',STUDIO+'</head>',1)
 s=re.sub(r'<link rel="stylesheet" href="/assets/css/studio-suite\.css\?v=[^"]*">',STUDIO,s)
 if p.parent.name=='windows-app':s=promote_windows_capture(s)
 if before!=s:p.write_text(campaigns(s));changed.append(str(p.relative_to(ROOT)))
# Windows capture promotion is maintained in the published markup; avoid duplicating figures on reruns.
print('Shared suite surfaces:',len(changed),'pages')
