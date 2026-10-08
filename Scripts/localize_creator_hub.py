"""Generate the creator hub and Dulpi presentation for the 50 ASC locales.

Translation refresh uses only public website copy. Cached translations make normal
regeneration offline and reproducible. FR and EN retain the authored source copy.
"""
import argparse, concurrent.futures, hashlib, json, re, time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from lxml import html, etree
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/creator-hub'
LOCALES='ar-SA bn-BD ca cs da de-DE el en-AU en-CA en-GB en-US es-ES es-MX fi fr-CA fr-FR gu-IN he hi hr hu id it ja kn-IN ko ml-IN mr-IN ms nl-NL no or-IN pa-IN pl pt-BR pt-PT ro ru sk sl-SI sv ta-IN te-IN th tr uk ur-PK vi zh-Hans zh-Hant'.split()
NAMES=['العربية','বাংলা','Català','Čeština','Dansk','Deutsch','Ελληνικά','English (Australia)','English (Canada)','English (UK)','English (US)','Español (España)','Español (México)','Suomi','Français (Canada)','Français (France)','ગુજરાતી','עברית','हिन्दी','Hrvatski','Magyar','Bahasa Indonesia','Italiano','日本語','ಕನ್ನಡ','한국어','മലയാളം','मराठी','Bahasa Melayu','Nederlands','Norsk','ଓଡ଼ିଆ','ਪੰਜਾਬੀ','Polski','Português (Brasil)','Português (Portugal)','Română','Русский','Slovenčina','Slovenščina','Svenska','தமிழ்','తెలుగు','ไทย','Türkçe','Українська','اردو','Tiếng Việt','简体中文','繁體中文']
BRANDS=['Yves Durand','Record Picker','Physical Routine','Snory Teller','Dulpi','My Musical Update','MY MUSICAL UPDATE','Apple Music','Microsoft Store','App Store','Spotify','Deezer','Instagram','Facebook','YouTube','Reddit','October Mess','September Desires','LPI']
ATTRS={'alt','aria-label','title'}
def language(locale):
 if locale.startswith('zh-'): return 'zh-CN' if locale=='zh-Hans' else 'zh-TW'
 return locale.split('-')[0]
def prefix(locale): return '' if locale=='en-US' else 'fr/' if locale=='fr-FR' else locale.lower()+'/'
def url(locale,kind): return 'https://recordpicker.app/'+prefix(locale)+'apps/'+('dulpi/' if kind=='dulpi' else '')
def strings(doc):
 for node in doc.iter():
  if not isinstance(node.tag,str): continue
  if node.tag not in ('script','style','svg','path') and not node.xpath('ancestor::script|ancestor::style|ancestor::svg'):
   if node.text and node.text.strip(): yield node,'text',node.text.strip()
   for attr in ATTRS:
    if node.get(attr): yield node,attr,node.get(attr)
   if node.tag=='meta' and (node.get('name')=='description' or node.get('property') in ('og:title','og:description','og:image:alt')): yield node,'content',node.get('content')
  if node.tail and node.tail.strip() and not node.xpath('ancestor::script|ancestor::style|ancestor::svg'): yield node,'tail',node.tail.strip()
def protect(s):
 for i,b in enumerate(BRANDS): s=s.replace(b,f'ZXBRAND{i}XZ')
 return s
def restore(s):
 for i,b in enumerate(BRANDS): s=re.sub(r'ZX\s*BRAND\s*'+str(i)+r'\s*XZ',lambda _:b,s,flags=re.I)
 return s

def translate_batch(lang,batch):
 # Separate query values preserve string boundaries, including very short labels.
 args=[('client','dict-chrome-ex'),('sl','en'),('tl',lang)]
 args.extend(('q',protect(s)) for _,s in batch)
 endpoint='https://translate.googleapis.com/translate_a/t?'+urlencode(args)
 for attempt in range(4):
  try:
   with urlopen(endpoint,timeout=45) as response: data=json.load(response)
   if len(data)!=len(batch): raise ValueError('Translation batch incomplete')
   values=[restore(s).strip() for s in data]
   if any(not s for s in values):raise ValueError('Empty translation')
   return {source:translated for (_,source),translated in zip(batch,values)}
  except Exception:
   if attempt==3:raise
   time.sleep(3*(attempt+1))

def refresh(templates):
 texts=list(dict.fromkeys(s for key,markup in templates.items() if key.startswith('en-') for _,_,s in strings(html.fromstring(markup))))
 batches=[]; batch=[]; size=0
 for i,s in enumerate(texts):
  if size+len(s)>2200 and batch: batches.append(batch); batch=[]; size=0
  batch.append((i,s)); size+=len(s)+12
 if batch:batches.append(batch)
 langs=sorted({language(l) for l in LOCALES}-{'en','fr'})
 def one(lang):
  path=DATA/(lang+'.json'); cache=json.loads(path.read_text()) if path.exists() else {}
  for s in texts:
   if s in BRANDS or not any(c.isalpha() for c in s) or s.startswith(('©','S05E','MY MUSICAL UPDATE ·')) or '@' in s: cache[s]=s
  for batch in batches:
   missing=[(i,s) for i,s in batch if s not in cache]
   if missing:cache.update(translate_batch(lang,missing)); path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n')
  print(f'Translated {lang}: {len(texts)} strings',flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
  list(executor.map(one,langs))

def generate(templates):
 csshash=hashlib.sha256((ROOT/'apps/styles.css').read_bytes()).hexdigest()[:12]
 for locale,name in zip(LOCALES,NAMES):
  lang=language(locale); cache=json.loads((DATA/(lang+'.json')).read_text()) if lang not in ('en','fr') else {}
  for kind in ('hub','dulpi'):
   doc=html.fromstring(templates[('fr' if lang=='fr' else 'en')+'-'+kind]); head=doc.find('head')
   if cache:
    for node,field,s in strings(doc):
     translated=cache[s]
     if field in ('text','tail'):
      original=getattr(node,field)
      leading=re.match(r'^\s*',original).group(0); trailing=re.search(r'\s*$',original).group(0)
      setattr(node,field,leading+translated+trailing)
     else:node.set(field,translated)
   for button in doc.xpath("//*[contains(@class,'playlist-actions') or contains(@class,'platforms')]/a"):
    for part in button.iter():
     if part.text:part.text=part.text.replace(' ↗','').replace('↗','')
     if part.tail:part.tail=part.tail.replace(' ↗','').replace('↗','')
    if button.get('aria-label'):button.set('aria-label',button.get('aria-label').replace(' ↗','').replace('↗',''))
   doc.set('lang',locale if locale!='no' else 'nb'); doc.set('dir','rtl' if lang in ('ar','he','ur') else 'ltr')
   pageurl=url(locale,kind)
   head.xpath('link[@rel="canonical"]')[0].set('href',pageurl)
   for node in head.xpath('link[@rel="alternate"]'):head.remove(node)
   for other in LOCALES:
    etree.SubElement(head,'link',rel='alternate',hreflang='nb' if other=='no' else other,href=url(other,kind))
   etree.SubElement(head,'link',rel='alternate',hreflang='x-default',href=url('en-US',kind))
   for node in head.xpath('meta[@property="og:url"]'):node.set('content',pageurl)
   for node in head.xpath('link[@rel="stylesheet"]'):node.set('href','/apps/styles.css?v='+csshash)
   # Localize only hub/presentation links. Other project URLs remain genuine destinations.
   rp_locale={'ar-SA':'ar','de-DE':'de','nl-NL':'nl','no':'nb','fr-FR':'fr','en-US':''}.get(locale,locale.lower())
   for node in doc.xpath('//*[@href]'):
    href=node.get('href')
    if href in ('/apps/','/fr/apps/'):node.set('href','/'+prefix(locale)+'apps/')
    elif href.startswith(('/snory-teller/en-US/','/snory-teller/fr-FR/')):
     parts=href.split('/');parts[2]=locale;node.set('href','/'.join(parts))
    elif href in ('/apps/dulpi/','/fr/apps/dulpi/'):node.set('href','/'+prefix(locale)+'apps/dulpi/')
    elif href in ('/','/manage-vinyl-collection/','/choose-vinyl-record/') and rp_locale:
     candidate='/'+rp_locale+href
     if (ROOT/candidate.lstrip('/')/'index.html').is_file():node.set('href',candidate)
   for primary in doc.xpath('//*[@id="record-picker"]/*[@class="app-actions"]/a[not(contains(@class,"store-button"))]'):
    destination='/'+rp_locale+'/' if rp_locale else '/'
    if not (ROOT/destination.lstrip('/')/'index.html').is_file():
     base=language(locale); destination='/'+base+'/' if (ROOT/base/'index.html').is_file() else '/'
    primary.set('href',destination)
   if kind=='hub':
    for edition in ('v26','v20'):
     shot='/assets/screenshots/'+edition+'/'+(rp_locale or 'en-us')+'/mac-collection.webp'
     if (ROOT/shot.lstrip('/')).is_file():
      for image in doc.xpath('//*[@id="record-picker"]//figure//img'):image.set('src',shot)
      for image_link in doc.xpath('//*[@id="record-picker"]//figure/a'):image_link.set('href',shot)
      break
   if kind=='dulpi':
    for old in doc.xpath('//header/a')[1:]:old.getparent().remove(old)
   navs=doc.xpath('//header/nav')
   if navs:
    nav=navs[-1]; nav.clear(); nav.set('class','language-nav')
   else:nav=etree.SubElement(doc.find('body').find('header'),'nav',{'class':'language-nav'})
   details=etree.SubElement(nav,'details',{'class':'language-picker'})
   etree.SubElement(details,'summary').text=name+' ▾'
   links=etree.SubElement(details,'div',{'class':'language-options'})
   for other,othername in zip(LOCALES,NAMES):
    a=etree.SubElement(links,'a',href='/'+prefix(other)+'apps/'+('dulpi/' if kind=='dulpi' else ''),hreflang=other,lang=other,dir='auto')
    a.text=othername
    if other==locale:a.set('aria-current','page')
   for primary in doc.xpath('//*[@id="physical-routine"]/a'):
    primary.set('href','https://my-physical-routine.mdvnc9v49c.chatgpt.site/'+('' if locale=='fr-FR' else locale.lower()+'/'))
   for script in doc.xpath('//script[@type="application/ld+json"]'):
    data=json.loads(script.text)
    def fix(value):
     if isinstance(value,dict):
      for key,item in list(value.items()):
       if key=='inLanguage':value[key]=doc.get('lang')
       elif key in ('name','description','jobTitle') and isinstance(item,str):value[key]=cache.get(item,item)
       elif isinstance(item,str) and item.startswith(('https://recordpicker.app/apps/','https://recordpicker.app/fr/apps/')) and not item.startswith('https://recordpicker.app/apps/assets/') and not item.endswith('#yves-durand'):
        for base in ('https://recordpicker.app/fr/apps/','https://recordpicker.app/apps/'):
         if item.startswith(base):value[key]=url(locale,'hub')+item[len(base):];break
       else:fix(item)
     elif isinstance(value,list):
      for item in value:fix(item)
    fix(data);script.text=json.dumps(data,ensure_ascii=False)
   path=ROOT/(prefix(locale)+'apps/'+('dulpi/' if kind=='dulpi' else '')+'index.html');path.parent.mkdir(parents=True,exist_ok=True)
   path.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html')+'\n')
 manifest={'locales':LOCALES,'pages':[url(l,k) for l in LOCALES for k in ('hub','dulpi')],'translation':'Google Translate machine translation; authored French and English retained; human review pending for additional languages.'}
 (DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 for filename in ('sitemap.xml','sitemap-media.xml'):
  path=ROOT/filename;tree=etree.parse(str(path));ns='http://www.sitemaps.org/schemas/sitemap/0.9';known={x.text for x in tree.findall('.//{'+ns+'}loc')}
  for entry in manifest['pages']:
   if entry not in known:
    node=etree.SubElement(tree.getroot(),'{'+ns+'}url');etree.SubElement(node,'{'+ns+'}loc').text=entry;etree.SubElement(node,'{'+ns+'}lastmod').text='2026-10-08'
  path.write_bytes(etree.tostring(tree,encoding='UTF-8',xml_declaration=True,pretty_print=True))
 print('Generated 100 pages across 50 ASC locales')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');args=p.parse_args()
 templates=json.loads((DATA/'templates.json').read_text())
 if args.refresh:refresh(templates)
 generate(templates)
