"""Refresh reviewed guide bodies while preserving localized navigation and SEO."""
import concurrent.futures
import html as escaping
import json
import re
from lxml import html, etree
from localize_creator_hub import DATA, ROOT, LOCALES, ROUTES, language, prefix, translate_batch
from site_social_identity import normalize as normalize_social

CONTENT=ROOT/'data/record-guide-walkthroughs.json'

def update(raw,kind,items):
 match=re.search(r'(<article\b[^>]*>\s*<h1\b[^>]*>.*?</h1>)(.*?)(<a\b[^>]*href="[^"]*/readme/".*?)(</article>)',raw,re.S)
 if not match: raise ValueError('Missing guide structure: '+kind)
 body='<section id="'+kind+'-walkthrough">'+''.join('<'+tag+'>'+escaping.escape(text)+'</'+tag+'>' for tag,text in items)+'</section>'
 raw=raw[:match.start(2)]+body+raw[match.end(2):]
 match=re.search(r'(<section id="guide-next-steps">)(.*?)(</section>)',raw,re.S)
 if not match: return raw
 inner=match.group(2); last=inner.rfind('<h2>')
 if last<0: raise ValueError('Missing related heading: '+kind)
 return raw[:match.start(2)]+inner[last:]+raw[match.end(2):]

def navigation(raw,kind,loc):
 if kind in ('discogs','backup','choose','rediscover'):
  lang=language(loc); cache=json.loads((DATA/(lang+'.json')).read_text()) if lang not in ('fr','en') else {}
  def label(en,fr): return fr if lang=='fr' else en if lang=='en' else cache[en]
  heading='<h2>'+escaping.escape(label('Continue with your collection','Pour continuer'))+'</h2>'
  doc=html.fromstring(raw); existing=doc.xpath('//section[@id="guide-next-steps"]/nav')
  if existing: nav=etree.tostring(existing[0],encoding='unicode',method='html')
  else:
   rp={'ar-SA':'ar','de-DE':'de','nl-NL':'nl','no':'nb','fr-FR':'fr','en-US':''}.get(loc,loc.lower())
   links=[]
   for route,title in [('',label('Explore Record Picker','Découvrir Record Picker')),('ios-app/',label('iPhone and iPad','iPhone et iPad')),('mac-app/','Mac'),('windows-app/','Windows')]:
    url='/'+(rp+'/' if rp else '')+route
    if not (ROOT/url.lstrip('/')/'index.html').exists(): url='/'+route
    links.append('<a href="'+url+'">'+escaping.escape(title)+'</a>')
   token='RP_Website_JP' if loc=='ja' else 'RP_Website_KR' if loc=='ko' else 'RP_Website'
   for title,url,destination in [('App Store','https://apps.apple.com/app/recordpicker/id6780422305?pt=129016722&ct='+token+'&mt=8','apple_ios'),('Microsoft Store','https://apps.microsoft.com/detail/9N2ZWRL4M3JC?cid='+token,'microsoft')]:
    links.append('<a href="'+escaping.escape(url,quote=True)+'" data-umami-event="store_click" data-umami-event-destination="'+destination+'">'+title+'</a>')
   nav='<nav aria-label="'+escaping.escape(label('App and downloads','Application et téléchargements'),quote=True)+'">'+' · '.join(links)+'</nav>'
  nav=etree.tostring(html.fromstring(nav),encoding='unicode',method='html')
  links=[]
  for target in ('discogs','backup','choose','rediscover'):
   if target==kind: continue
   url='/'+prefix(loc)+ROUTES[target]
   title=html.fromstring((ROOT/url.lstrip('/')/'index.html').read_text()).xpath('//main//h1')[0].text_content()
   links.append('<a href="'+url+'">'+escaping.escape(title)+'</a>')
  block='<section id="guide-next-steps">'+heading+'<p>'+' · '.join(links)+'</p>'+nav+'</section>'
  if '<section id="guide-next-steps">' in raw:
   return re.sub(r'<section id="guide-next-steps">.*?</section>',lambda _:block,raw,flags=re.S)
  return raw.replace('</article>',block+'</article>',1)
 if kind in ('snory-guide','physical-guide') and not html.fromstring(raw).xpath('//main//a[contains(@href,"apps.apple.com")]'):
  if kind=='snory-guide':
   app='Snory Teller'; url='/snory-teller/'+loc+'/'; store='https://apps.apple.com/app/snory-teller/id6820177689?pt=129016722&ct=ST_Website&mt=8'
  else:
   app='My Physical Routine'; url='/physical/fr/about/' if language(loc)=='fr' else '/physical/about/'; store='https://apps.apple.com/app/my-physical-routine/id6820104318?pt=129016722&ct=MPR_Website&mt=8'
  assert (ROOT/url.lstrip('/')/'index.html').exists(),url
  block='<nav aria-label="'+app+'"><a href="'+url+'">'+app+'</a> · <a href="'+escaping.escape(store,quote=True)+'" data-umami-event="store_click" data-umami-event-destination="apple_ios">App Store</a></nav>'
  return raw.replace('</article>',block+'</article>',1)
 return raw

def main():
 content=json.loads(CONTENT.read_text())
 sources=list(dict.fromkeys([text for spec in content.values() for _,text in spec.get('en',[])]+[spec['description']['en'] for spec in content.values()]))
 langs=sorted({language(loc) for loc in LOCALES}-{'en','fr'})
 def one(lang):
  path=DATA/(lang+'.json'); cache=json.loads(path.read_text()); batch=[]; size=0
  for i,source in enumerate(sources):
   if source in cache: continue
   if size+len(source)>1800 and batch:
    cache.update(translate_batch(lang,batch)); batch=[]; size=0
   batch.append((i,source)); size+=len(source)
  if batch: cache.update(translate_batch(lang,batch))
  path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n'); print('Cached '+lang,flush=True)
  return lang,cache
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: caches=dict(pool.map(one,langs))
 templates=json.loads((DATA/'templates.json').read_text()); pages=[]; body_pages=[]
 def edit(raw,kind,spec,lang,cache):
  if 'en' in spec:
   items=spec[lang] if lang in ('en','fr') else [(tag,cache[source]) for tag,source in spec['en']]
   raw=update(raw,kind,items)
  description=spec['description'][lang] if lang in ('en','fr') else cache[spec['description']['en']]
  raw,count=re.subn(r'(<meta\b[^>]*name="description"[^>]*content=")[^"]*',lambda m:m.group(1)+escaping.escape(description,quote=True),raw)
  if count!=1: raise ValueError('Missing description: '+kind)
  return normalize_social(raw,kind)
 for kind,spec in content.items():
  for lang in ('en','fr'):
   loc='fr-FR' if lang=='fr' else 'en-US'
   templates[lang+'-'+kind]=navigation(edit(templates[lang+'-'+kind],kind,spec,lang,{}),kind,loc)
  for loc in LOCALES:
   lang=language(loc)
   path=ROOT/prefix(loc)/ROUTES[kind]/'index.html'; before=path.read_text(); after=navigation(edit(before,kind,spec,lang,caches.get(lang,{})),kind,loc)
   old=html.fromstring(before); new=html.fromstring(after)
   assert old.xpath('//link[@rel="canonical" or @rel="alternate"]/@href')==new.xpath('//link[@rel="canonical" or @rel="alternate"]/@href'),path
   assert set(old.xpath('//nav//a/@href')).issubset(new.xpath('//nav//a/@href')),path
   if 'en' in spec:
    assert 'ZXBRAND' not in new.get_element_by_id(kind+'-walkthrough').text_content(),path
    body_pages.append(str(path.relative_to(ROOT)))
   path.write_text(after); pages.append(str(path.relative_to(ROOT)))
 (DATA/'templates.json').write_text(json.dumps(templates,ensure_ascii=False,indent=2)+'\n')
 for filename in ('sitemap.xml','sitemap-media.xml'):
  path=ROOT/filename; routes='|'.join(re.escape(ROUTES[kind]) for kind in content)
  raw,count=re.subn(r'(<url><loc>https://recordpicker\.app/(?:[^<]*/)?(?:'+routes+r')</loc><lastmod>)[^<]+',r'\g<1>2026-10-22',path.read_text())
  assert count==len(pages),(filename,count)
  path.write_text(raw)
 (ROOT/'data/record-guide-walkthroughs-2026-10-22.json').write_text(json.dumps({'pages':pages,'bodyPages':body_pages,'review':'Complete backup versus readable export; eligibility and draw cycle; proposals versus actual listening; no automatic least-played preference promised; specific descriptions for six guides'},ensure_ascii=False,indent=2)+'\n')
 print('Updated '+str(len(pages))+' guides')

if __name__=='__main__': main()
