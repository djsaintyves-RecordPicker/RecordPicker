"""Build all 50 MPR product/support/privacy locales with automatic browser language.

FR/EN are authored. Other public copy is cached machine translation; refresh is
explicit, never performed by CI. Existing App Store support URLs remain valid.
"""
from pathlib import Path
from urllib.parse import urlsplit
import argparse,concurrent.futures,hashlib,json,re
from lxml import html,etree
import localize_creator_hub as hub
from site_campaign_links import normalize as normalize_campaign_links
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/physical-localization'
KINDS=('about','support','privacy');LOCALES=hub.LOCALES

def route(locale,kind):
 prefix='' if locale=='en-US' else 'fr/' if locale=='fr-FR' else locale.lower()+'/'
 return '/physical/'+prefix+kind+'/'

def templates():return json.loads((DATA/'templates.json').read_text())
def refresh():
 T=templates();texts=list(dict.fromkeys(s for kind in KINDS for _,_,s in hub.strings(html.fromstring(T['en:'+kind]))))
 def one(lang):
  p=DATA/(lang+'.json');cache=json.loads(p.read_text()) if p.exists() else {}
  for s in texts:
   if s in hub.BRANDS or '@' in s or not any(c.isalpha() for c in s):cache[s]=s
  pending=[s for s in texts if s not in cache];batch=[];size=0
  for s in pending+['']:
   if batch and (size+len(s)>2200 or not s):
    cache.update(hub.translate_batch(lang,list(enumerate(batch))));p.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n');batch=[];size=0
   if s:batch.append(s);size+=len(s)+15
  print('Translated',lang,len(texts),'public strings',flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(one,sorted({hub.language(l) for l in LOCALES}-{'en','fr'})))

def generate():
 T=templates();urls=[];script='/physical/locale.js?v='+hashlib.sha256((ROOT/'physical/locale.js').read_bytes()).hexdigest()[:12]
 for locale in LOCALES:
  lang=hub.language(locale);cache=json.loads((DATA/(lang+'.json')).read_text()) if lang not in ('en','fr') else {}
  for kind in KINDS:
   d=html.fromstring(T[('fr:' if lang=='fr' else 'en:')+kind]);head=d.find('head')
   for node in d.xpath('//nav[@aria-label="Languages"]|//*[@class="language-nav"]|//select[@aria-label="Language"]'):node.getparent().remove(node)
   for node,field,source in hub.strings(d):
    if cache:
     translated=cache[source]
     if field in ('text','tail'):
      old=getattr(node,field);setattr(node,field,re.match(r'^\s*',old)[0]+translated+re.search(r'\s*$',old)[0])
     else:node.set(field,translated)
   d.set('lang','nb' if locale=='no' else locale);d.set('dir','rtl' if lang in ('ar','he','ur') else 'ltr');d.set('data-physical-locale',locale)
   for link in head.xpath('link[@rel="alternate"]'):head.remove(link)
   canonical='https://recordpicker.app'+route(locale,kind);urls.append(canonical)
   head.xpath('link[@rel="canonical"]')[0].set('href',canonical)
   for node in head.xpath('meta[@property="og:url"]'):node.set('content',canonical)
   for other in LOCALES:etree.SubElement(head,'link',rel='alternate',hreflang='nb' if other=='no' else other,href='https://recordpicker.app'+route(other,kind))
   etree.SubElement(head,'link',rel='alternate',hreflang='x-default',href='https://recordpicker.app'+route('en-US',kind))
   for node in head.xpath('script[starts-with(@src,"/physical/locale.js")]'):head.remove(node)
   head.insert(2,etree.Element('script',src=script))
   for node in d.xpath('//a[@href]'):
    href=node.get('href');parts=urlsplit(href)
    if parts.netloc not in ('','recordpicker.app'):continue
    match=re.fullmatch(r'/physical/(?:fr/)?(about|support|privacy)/',parts.path)
    if match:node.set('href',route(locale,match[1])+('?' + parts.query if parts.query else '')+('#'+parts.fragment if parts.fragment else ''))
    elif parts.path in ('/apps/','/fr/apps/'):
     node.set('href','/'+hub.prefix(locale)+'apps/'+('#'+parts.fragment if parts.fragment else ''))
    elif parts.path in ('/physical-routine-guide/','/fr/physical-routine-guide/'):
     node.set('href','/'+hub.prefix(locale)+'physical-routine-guide/')
   for node in d.xpath('//script[@type="application/ld+json"]'):
    obj=json.loads(node.text);obj['url']=canonical;obj['inLanguage']='nb' if locale=='no' else locale
    if isinstance(obj.get('description'),str) and obj['description'] in cache:obj['description']=cache[obj['description']]
    node.text=json.dumps(obj,ensure_ascii=False,separators=(',',':'))
   target=ROOT/route(locale,kind).lstrip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(normalize_campaign_links('<!doctype html>\n'+html.tostring(d,encoding='unicode',with_tail=False)+'\n'))
 # The MPR getting-started guide follows the same browser language, too.
 for guide in ROOT.glob('**/physical-routine-guide/index.html'):
  raw=guide.read_text();raw=re.sub(r'<script src="/physical/locale.js[^"]*"[^>]*></script>','',raw)
  raw=raw.replace('</head>','<script src="'+script+'"></script></head>',1);guide.write_text(normalize_campaign_links(raw))
 source=ROOT/'data/creator-hub/templates.json';hub_templates=json.loads(source.read_text())
 for key in ('en-physical-guide','fr-physical-guide'):
  raw=hub_templates[key];raw=re.sub(r'<script src="/physical/locale.js[^"]*"[^>]*></script>','',raw)
  hub_templates[key]=normalize_campaign_links(raw.replace('</head>','<script src="'+script+'"></script></head>',1))
 source.write_text(json.dumps(hub_templates,ensure_ascii=False,indent=2)+'\n')
 (DATA/'manifest.json').write_text(json.dumps({'locales':LOCALES,'pages':urls,'languagePolicy':'Browser preferences on every MPR route; no visible selector; English fallback.','translation':'French and English authored; other public copy machine translated; native review pending.'},ensure_ascii=False,indent=2)+'\n')
 ns='http://www.sitemaps.org/schemas/sitemap/0.9';sitemap=etree.Element('{'+ns+'}urlset',nsmap={None:ns})
 for u in urls:
  n=etree.SubElement(sitemap,'{'+ns+'}url');etree.SubElement(n,'{'+ns+'}loc').text=u;etree.SubElement(n,'{'+ns+'}lastmod').text='2026-10-23'
 (ROOT/'physical/sitemap.xml').write_bytes(etree.tostring(sitemap,xml_declaration=True,encoding='UTF-8',pretty_print=True))
 # The shared SEO audit requires every canonical in both root sitemaps as well.
 for filename in ('sitemap.xml','sitemap-media.xml'):
  path=ROOT/filename;raw=path.read_text();existing=set(re.findall(r'<loc>([^<]+)</loc>',raw))
  missing=[u for u in urls if u not in existing]
  if missing:
   additions='\n'.join('<url><loc>'+u+'</loc><lastmod>2026-10-23</lastmod></url>' for u in missing)
   path.write_text(raw.replace('</urlset>',additions+'\n</urlset>'))
 print('Generated 150 MPR pages in 50 locales',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');args=p.parse_args()
 if args.refresh:refresh()
 generate()
