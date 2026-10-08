"""Generate the Snory Teller subsite in the creator hub's 50 ASC locales.

French/English authored text stays intact; other translations are cached public
copy, machine translated and pending native-language editorial review.
"""
import argparse,json,re,concurrent.futures
from pathlib import Path
from lxml import html,etree
import localize_creator_hub as hub
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/snory-localization'
T=json.loads((DATA/'templates.json').read_text());KINDS=['','support/','privacy/','about/']
BASE='https://recordpicker.app/snory-teller/'
def url(locale,kind):return BASE+locale+'/'+kind
def strings(d):
 yield from hub.strings(d)
 for n in d.xpath('//meta[starts-with(@name,"twitter:")]'):
  if n.get('name') in ['twitter:title','twitter:description']:yield n,'content',n.get('content')
def refresh():
 texts=list(dict.fromkeys(s for k,m in T.items() if k.startswith('en-US:') for _,_,s in strings(html.fromstring(m))))
 def one(lang):
  p=DATA/(lang+'.json');cache=json.loads(p.read_text()) if p.exists() else {}
  for s in texts:
   if s in hub.BRANDS or '@' in s or not any(x.isalpha() for x in s):cache[s]=s
  batch=[];size=0
  for s in [s for s in texts if s not in cache]+['']:
   if batch and (size+len(s)>2200 or not s):
    cache.update(hub.translate_batch(lang,[(i,t) for i,t in enumerate(batch)]));p.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n');batch=[];size=0
   if s:batch.append(s);size+=len(s)+15
  print('Translated',lang,len(texts),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:list(e.map(one,sorted({hub.language(l) for l in hub.LOCALES}-{'en','fr'})))
def generate():
 urls=[]
 for locale,name in zip(hub.LOCALES,hub.NAMES):
  lang=hub.language(locale);cache=json.loads((DATA/(lang+'.json')).read_text()) if lang not in ['en','fr'] else {}
  for kind in KINDS:
   d=html.fromstring(T[('fr-FR:' if lang=='fr' else 'en-US:')+kind]);head=d.find('head')
   for e,f,s in strings(d):
    if cache:
     v=cache[s]
     if f in ['text','tail']:
      old=getattr(e,f);setattr(e,f,re.match(r'^\s*',old).group()+v+re.search(r'\s*$',old).group())
     else:e.set(f,v)
   d.set('lang','nb' if locale=='no' else locale);d.set('dir','rtl' if lang in ['ar','he','ur'] else 'ltr')
   u=url(locale,kind);urls.append(u);head.xpath('link[@rel="canonical"]')[0].set('href',u)
   for e in head.xpath('meta[@property="og:url"]'):e.set('content',u)
   for e in head.xpath('link[@rel="alternate"]'):head.remove(e)
   for other in hub.LOCALES:etree.SubElement(head,'link',rel='alternate',hreflang='nb' if other=='no' else other,href=url(other,kind))
   etree.SubElement(head,'link',rel='alternate',hreflang='x-default',href=url('en-US',kind))
   for a in d.xpath('//*[@href]'):
    href=a.get('href')
    if href.startswith(('/snory-teller/en-US/','/snory-teller/fr-FR/')):
     parts=href.split('/');parts[2]=locale;a.set('href','/'.join(parts))
    elif href.split('#')[0] in ['/apps/','/fr/apps/']:
     _,mark,fragment=href.partition('#');a.set('href','/'+hub.prefix(locale)+'apps/'+(mark+fragment if mark else ''))
    elif href in ['/physical/about/','/physical/fr/about/']:a.set('href','https://my-physical-routine.mdvnc9v49c.chatgpt.site/'+('' if locale=='fr-FR' else locale.lower()+'/'))
    elif href in ['/','/fr/']:
     rp={'ar-SA':'ar','de-DE':'de','nl-NL':'nl','no':'nb','fr-FR':'fr','en-US':''}.get(locale,locale.lower());dest='/'+rp+'/' if rp else '/'
     if not (ROOT/dest.lstrip('/')/'index.html').is_file():dest='/'+lang+'/' if (ROOT/lang/'index.html').is_file() else '/'
     a.set('href',dest)
   header=d.find('body').find('header')
   for a in header.xpath('./a[@lang]'):header.remove(a)
   details=etree.SubElement(header,'details',{'class':'language-picker'});etree.SubElement(details,'summary').text=name+' ▾';options=etree.SubElement(details,'div',{'class':'language-options'})
   for other,oname in zip(hub.LOCALES,hub.NAMES):
    a=etree.SubElement(options,'a',href='/snory-teller/'+other+'/'+kind,lang=other,dir='auto');a.text=oname
    if other==locale:a.set('aria-current','page')
   target=ROOT/'snory-teller'/locale/kind/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text('<!doctype html>\n'+html.tostring(d,encoding='unicode')+'\n')
 ns='http://www.sitemaps.org/schemas/sitemap/0.9';r=etree.Element('{'+ns+'}urlset',nsmap={None:ns})
 for u in urls:
  n=etree.SubElement(r,'{'+ns+'}url');etree.SubElement(n,'{'+ns+'}loc').text=u
 (ROOT/'snory-teller/sitemap.xml').write_bytes(etree.tostring(r,encoding='UTF-8',xml_declaration=True,pretty_print=True))
 (DATA/'manifest.json').write_text(json.dumps({'locales':hub.LOCALES,'pages':urls,'translation':'Authored French and English; other languages machine translated, native review pending.'},ensure_ascii=False,indent=2)+'\n')
 print('Generated',len(urls),'Snory Teller pages')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');a=p.parse_args()
 if a.refresh:refresh()
 generate()
