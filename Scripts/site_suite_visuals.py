"""Apply shared suite presentation without rewriting copy, palettes or canonical URLs."""
from pathlib import Path
import re
from site_campaign_links import normalize as campaign_links
ROOT=Path(__file__).resolve().parents[1]
STYLE='<link rel="stylesheet" href="/assets/css/studio-suite.css?v=20261022">'
pages={}
for path in ROOT.rglob('apps/index.html'):
 if '.git' not in path.parts:pages[path]='suite-studio'
for path in (ROOT/'snory-teller').rglob('index.html'):pages[path]='suite-snory'
for path in (ROOT/'physical').rglob('index.html'):pages[path]='suite-physical'
for path in pages:
 text=path.read_text();family=pages[path]
 def body(m):
  tag=m[0]
  if 'rps-suite' in tag:return tag
  classes='rps-suite '+family
  return re.sub(r'class="([^"]*)"',lambda x:'class="'+x[1]+' '+classes+'"',tag,count=1) if 'class="' in tag else tag[:-1]+' class="'+classes+'">'
 text=re.sub(r'<body\b[^>]*>',body,text,count=1)
 if 'studio-suite.css' not in text:text=text.replace('</head>',STYLE+'</head>',1)
 path.write_text(campaign_links(text))
print('Suite presentation:',len(pages),'pages')
