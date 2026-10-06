#!/usr/bin/env python3
"""Make existing discovery pages clearer without changing public release status."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PRICES = {
 'ar':'مجاني حتى 100 أسطوانة · Pro مدى الحياة',
 'ca':'Gratis fins a 100 discos · Pro de per vida',
 'da':'Gratis op til 100 plader · Pro for livet',
 'de':'Kostenlos bis zu 100 Tonträger · Pro auf Lebenszeit',
 'el':'Δωρεάν έως 100 δίσκους · Pro εφ’ όρου ζωής',
 'en-au':'Free for up to 100 records · Lifetime Pro',
 'en-ca':'Free for up to 100 records · Lifetime Pro',
 'en-gb':'Free for up to 100 records · Lifetime Pro',
 'en-us':'Free for up to 100 records · Lifetime Pro',
 'es-es':'Gratis hasta 100 discos · Pro de por vida',
 'es-mx':'Gratis hasta 100 discos · Pro de por vida',
 'fi':'Ilmainen 100 levyyn asti · Elinikäinen Pro',
 'fr':'Gratuit jusqu’à 100 disques · Pro à vie',
 'fr-ca':'Gratuit jusqu’à 100 disques · Pro à vie',
 'he':'חינם עד 100 תקליטים · Pro לכל החיים',
 'hi':'100 रिकॉर्ड तक मुफ़्त · आजीवन Pro',
 'id':'Gratis hingga 100 rekaman · Pro seumur hidup',
 'it':'Gratis fino a 100 dischi · Pro a vita',
 'ja':'100枚まで無料 · Proは買い切り',
 'ko':'음반 100장까지 무료 · 평생 Pro',
 'nb':'Gratis opptil 100 plater · Pro for livet',
 'nl':'Gratis tot 100 platen · Levenslang Pro',
 'pl':'Bezpłatnie do 100 płyt · Pro na zawsze',
 'pt-br':'Grátis até 100 discos · Pro vitalício',
 'pt-pt':'Grátis até 100 discos · Pro vitalício',
 'ru':'Бесплатно до 100 пластинок · Pro навсегда',
 'sv':'Gratis upp till 100 skivor · Pro för livet',
 'th':'ฟรีสูงสุด 100 แผ่น · Pro ตลอดชีพ',
 'tr':'100 plağa kadar ücretsiz · Ömür boyu Pro',
 'vi':'Miễn phí đến 100 đĩa · Pro trọn đời',
 'zh-hans':'100 张唱片以内免费 · 终身 Pro',
 'zh-hant':'100 張唱片以內免費 · 終身 Pro',
}
# Title, visible promise, two useful destinations, and short search description.
FOCUS = {
 '': ('Vinyl & CD Collection App and Random Record Picker | Record Picker', 'Catalogue your vinyl and CDs. Choose what to play.', 'Organise vinyl and CDs', 'Choose a record to play', 'Catalogue your vinyl records and CDs, import a Discogs CSV and rediscover albums with Random Pick. Free for up to 100 records; lifetime Pro, with no subscription.'),
 'fr': ('Collection vinyles et CD et tirage aléatoire | Record Picker', 'Cataloguez vos vinyles et CD. Choisissez quoi écouter.', 'Gérer mes vinyles et CD', 'Choisir quoi écouter', 'Cataloguez vos vinyles et CD, importez un CSV Discogs et retrouvez quoi écouter avec Random Pick. Gratuit jusqu’à 100 disques, puis Pro à vie sans abonnement.'),
 'it': ('App per collezioni di vinili e CD | Record Picker', 'Cataloga vinili e CD. Scegli cosa ascoltare.', 'Organizza vinili e CD', 'Scegli un disco da ascoltare', 'Cataloga vinili e CD, importa un CSV Discogs e riscopri gli album con una selezione casuale personalizzabile. Gratis fino a 100 dischi; Pro a vita senza abbonamento.'),
 'pt-br': ('App para coleção de vinis e CDs | Record Picker Brasil', 'Organize seus vinis e CDs. Escolha o que ouvir.', 'Organizar vinis e CDs', 'Escolher um disco para ouvir', 'Organize sua coleção de vinis e CDs, importe um CSV do Discogs e redescubra álbuns com um sorteio personalizável. Grátis até 100 discos; Pro vitalício sem assinatura.'),
 'pt-pt': ('App para coleção de vinis e CD | Record Picker Portugal', 'Organize os seus vinis e CD. Escolha o que ouvir.', 'Organizar vinis e CD', 'Escolher um disco para ouvir', 'Organize a sua coleção de vinis e CD, importe um CSV do Discogs e redescubra álbuns com uma seleção aleatória personalizável. Grátis até 100 discos; Pro vitalício sem subscrição.'),
}
FOCUS['fr-ca'] = FOCUS['fr']
for locale in ('en-us','en-gb','en-au','en-ca'):
 FOCUS[locale] = FOCUS['']
FOCUS['en-us'] = (FOCUS[''][0], 'Catalog your vinyl and CDs. Choose what to play.', 'Organize vinyl and CDs', FOCUS[''][3], FOCUS[''][4].replace('Catalogue','Catalog'))


MARKETS = {'en-us': 'United States', 'en-gb': 'United Kingdom', 'en-au': 'Australia', 'en-ca': 'Canada', 'fr-ca': 'Canada'}
for locale, market in MARKETS.items():
 title, tagline, collect, listen, description = FOCUS[locale]
 suffix = ' Découvrez l’app au Canada.' if locale == 'fr-ca' else ' Discover Record Picker in '+('the ' if locale in ('en-us', 'en-gb') else '')+market+'.'
 FOCUS[locale] = (title+' — '+market, tagline, collect, listen, description+suffix)

PORTUGUESE = {
 'A graph that follows your filters':'Um grafo que respeita os seus filtros',
 'Explore documented links between records, understand the evidence behind each path and save a path as an editable Listening Journey.':'Explore ligações documentadas entre discos, compreenda os indícios de cada percurso e guarde um percurso de escuta editável.',
 'Move several records together':'Mover vários discos de uma vez',
 'Move filtered records to a physical storage location after reviewing a preview of the exact changes.':'Mova os discos filtrados para um local físico depois de conferir as alterações na pré-visualização.',
 'More reliable listening insights':'Análises de escuta mais fiáveis',
 'Listening filters and Collection Stories distinguish confirmed listens from picks and playback launches.':'Os filtros de escuta e as Histórias da coleção distinguem escutas confirmadas de seleções e inícios de reprodução.',
 'Your collection tells its story':'A sua coleção conta a sua história',
 'Create a private, local Collection Story and save or share it as a carefully limited PNG card.':'Crie uma História da coleção privada neste dispositivo e guarde-a ou partilhe-a como um cartão PNG com informações limitadas.',
 'Clarity and reliability':'Clareza e fiabilidade',
 'Graph performance, review cleanup, translations and several backup and recovery workflows have been improved.':'Melhorias no desempenho do grafo, nas críticas, nas traduções e em vários processos de cópia de segurança e recuperação.',
 '🌍 Worldwide applications welcome · Beta available in English and French':'🌍 Candidaturas de todo o mundo · Bêta disponível em inglês e francês',
 'The 12 testers who complete the 14 days and send useful feedback will receive lifetime Pro access.':'Os 12 participantes que completarem os 14 dias e enviarem comentários úteis receberão acesso Pro vitalício.',
}
CHANGED = set()
def write(path, text):
 if path.read_text() != text:
  path.write_text(text); CHANGED.add(path.relative_to(ROOT).as_posix())
def metadata(text, title, description):
 text = re.sub(r'<title>.*?</title>', '<title>'+escape(title)+'</title>', text, count=1, flags=re.S)
 for attr,key,value in [('name','description',description),('property','og:title',title),('property','og:description',description),('name','twitter:title',title),('name','twitter:description',description)]:
  text = re.sub(r'(<meta '+attr+'="'+re.escape(key)+r'" content=")[^"]*(")', lambda m:m[1]+escape(value,quote=True)+m[2], text)
 return text

def apply():
 for locale in [''] + list(PRICES):
  base = ROOT / locale
  path = base/'index.html'; text = path.read_text()
  price = PRICES[locale or 'en-us']
  text = re.sub(r'(<strong data-price-current>).*?(</strong>)', lambda m:m[1]+escape(price)+m[2], text, flags=re.S)
  if locale in FOCUS:
   title,tagline,collect,listen,description = FOCUS[locale]
   text = metadata(text,title,description)
   text = re.sub(r'(<p class="tagline">).*?(</p>)',lambda m:m[1]+escape(tagline)+m[2],text,count=1,flags=re.S)
   prefix = '/' if locale in ('','en-us') else '/'+locale+'/'
   collection_route = 'cd-collection-app' if locale == 'fr' else 'manage-vinyl-collection'
   nav = f'<div class="collection-intents" data-collection-intents><a href="{prefix}{collection_route}/">{escape(collect)}</a><a href="{prefix}random-vinyl-record-picker/">{escape(listen)}</a></div>'
   if 'data-collection-intents' in text:
    text = re.sub(r'<div class="collection-intents" data-collection-intents>.*?</div>',lambda _:nav,text,count=1,flags=re.S)
   else:
    text = text.replace('<div class="badge-row">',nav+'<div class="badge-row">',1)
  if locale in FOCUS:
   text = re.sub(r'<p class="hero-free-tier">.*?</p>', '', text, count=1, flags=re.S)
   cta = re.search(r'<div class="cta-row">.*?</div>',text,re.S)
   if cta:
    text=text[:cta.start()]+text[cta.end():]
    text=text.replace('<div class="collection-intents"',cta[0]+'<div class="collection-intents"',1)
   tier='<p class="hero-free-tier">'+escape(price)+'</p>'
   if 'class="hero-free-tier"' not in text:
    text=text.replace('<div class="collection-intents"',tier+'<div class="collection-intents"',1)
  # Only the first showcase image is the above-the-fold hero. Real capture labels stay intact.
  match = re.search(r'<div class="hero-showcase v20-hero-showcase">.*?</div>',text,re.S)
  if match:
   hero = re.sub(r'(<img\b[^>]*?)loading="lazy"',r'\1loading="eager" fetchpriority="high"',match[0],count=1)
   text = text[:match.start()]+hero+text[match.end():]
  write(path,text)
  path=base/'mac-app/index.html';text=path.read_text()
  text = re.sub(r'(<p class="glass-pill eyebrow">)(.*?)(</p>)',lambda m:m[1]+m[2].replace(' · Record Picker 2.6',' · Record Picker')+m[3],text,count=1,flags=re.S)
  if locale=='it':
   text = metadata(text,'App Mac per catalogare vinili e CD | Record Picker','Cataloga vinili e CD sul Mac, importa un CSV Discogs e scegli cosa ascoltare. App nativa, sincronizzazione iCloud opzionale; gratis fino a 100 dischi e Pro a vita.')
   text=text.replace('Il modo calmo e nativo per catalogare i tuoi vinili e decidere cosa ascoltare stasera.','Cataloga vinili e CD sul Mac e scegli il prossimo disco da ascoltare.')
   text=text.replace('100 record.','100 dischi.')
  write(path,text)
 for locale in ('pt-br','pt-pt'):
  for path in (ROOT/locale).rglob('*.html'):
   text=path.read_text()
   for old,new in PORTUGUESE.items():
    if locale=='pt-br':
     new=new.replace('os seus filtros','seus filtros').replace('ligações','conexões').replace('compreenda','entenda').replace('guarde','salve').replace('fiáveis','confiáveis').replace('fiabilidade','confiabilidade').replace('a sua coleção','sua coleção').replace('A sua coleção','Sua coleção').replace('partilhe','compartilhe').replace('cópia de segurança','backup').replace('Bêta','Beta')
    text=text.replace(escape(old,quote=False),escape(new,quote=False)).replace(old,new)
   write(path,text)
 # Enrich the existing French CD page; make the free limit and next action explicit.
 path=ROOT/'fr/cd-collection-app/index.html';text=path.read_text()
 text=metadata(text,'Application pour classer ses CD : gratuit jusqu’à 100 disques | Record Picker','Classez vos CD et vinyles, importez un CSV Discogs et retrouvez quoi écouter. Gratuit jusqu’à 100 disques, puis achat Pro à vie sans abonnement. iPhone, iPad, Mac et Windows.')
 text=text.replace('<h1>Application pour cataloguer une collection de CD</h1>','<h1>Classez vos CD et retrouvez quoi écouter</h1>')
 text=text.replace('<p class="lead">Cataloguez CD et vinyles dans la même collection</p>','<p class="lead">CD et vinyles dans la même collection. Gratuit jusqu’à 100 disques.</p>')
 text=text.replace('href="../#download"','href="https://apps.apple.com/fr/app/recordpicker/id6780422305"').replace('>Aller à Record Picker</a>','>Essayer sur iPhone, iPad ou Mac</a>')
 if 'data-cd-guide' not in text:
  block='''<section class="seo-checklist" data-cd-guide><h2>Commencez avec votre collection</h2><ol><li>Importez votre CSV Discogs ou ajoutez un disque manuellement.</li><li>Vérifiez les éditions, les formats et les doublons avant de valider l’import.</li><li>Retrouvez un album par artiste, titre ou format, puis choisissez votre prochaine écoute avec Random Pick.</li></ol><h2>Est-ce vraiment gratuit ?</h2><p>Record Picker est gratuit jusqu’à 100 disques. Un achat Pro à vie débloque une collection illimitée, sans abonnement. Il n’est pas nécessaire de créer un compte Record Picker.</p><h2>Puis-je mélanger CD et vinyles ?</h2><p>Oui. Les formats restent distincts dans la même collection. Les éditions différentes d’un album peuvent être conservées séparément.</p><p><a class="button glass" href="https://apps.microsoft.com/detail/9N2ZWRL4M3JC">Voir la version Windows sur Microsoft Store</a></p></section>'''
  text=text.replace('<section class="seo-section">',block+'<section class="seo-section">',1)
 write(path,text)
 for locale in ('','en-us','en-gb','en-au','en-ca'):
  path=ROOT/locale/'random-vinyl-record-picker/index.html';text=path.read_text()
  title = 'Random Record Picker for Your Vinyl Collection | Record Picker'
  description = 'Can’t decide which record to play? Pick from your own vinyl and CD collection with genre filters, favourites and exclusions. Free for up to 100 records; lifetime Pro.'
  if locale in MARKETS:
   title += ' — '+MARKETS[locale]
   description += ' Discover Record Picker in '+MARKETS[locale]+'.'
  if locale == 'en-us': description = description.replace('favourites','favorites')
  text=metadata(text,title,description)
  text=text.replace('Random choice becomes useful when it understands a little about your collection.','Choose the next record from the vinyl and CDs you already own.')
  if 'data-picker-start' not in text:
   block='<section class="seo-checklist" data-picker-start><h2>Start with your own records</h2><p>Import a Discogs CSV or add records manually. Set your filters, then use Random Pick to rediscover an album from your collection.</p><p>Free for up to 100 records. A one-time lifetime Pro purchase unlocks an unlimited collection, with no subscription.</p></section>'
   text=text.replace('<section class="seo-checklist">',block+'<section class="seo-checklist">',1) if '<section class="seo-checklist">' in text else text.replace('</main>',block+'</main>',1)
  write(path,text)
 # Runtime storefront updates must preserve the same translated free limit as static HTML.
 path=ROOT/'site.js';text=path.read_text()
 block='  var freeTierCopy = '+json.dumps(PRICES,ensure_ascii=False,separators=(',',':'))+';\n  Object.keys(freeTierCopy).forEach(function (locale) { if (storefronts[locale]) storefronts[locale].price = freeTierCopy[locale]; });\n'
 if 'var freeTierCopy' not in text:
  pos=text.index('  var localeIndexes')
  text=text[:pos]+block+text[pos:]
 write(path,text)
 # Keep the existing homepage audit source in sync with these intentional snippet edits.
 path=ROOT/'Scripts/refine_homepage_descriptions.py';text=path.read_text()
 block='SEARCH_DESCRIPTION_OVERRIDES = '+repr({k:v[4] for k,v in FOCUS.items()})+'\nCOPY.update({locale: (description, COPY[locale][1]) for locale, description in SEARCH_DESCRIPTION_OVERRIDES.items()})\n\n'
 if 'SEARCH_DESCRIPTION_OVERRIDES' in text:
  start=text.index('SEARCH_DESCRIPTION_OVERRIDES')
  end=text.index('RANDOM_TERMS',start)
  text=text[:start]+block+text[end:]
 else:
  pos=text.index('RANDOM_TERMS')
  text=text[:pos]+block+text[pos:]
 write(path,text)
 # Only touched URLs get a new website lastmod; app release dates remain unchanged.
 path=ROOT/'sitemap.xml';text=path.read_text()
 def touch(m):
  block=m[0];url=re.search(r'<loc>(.*?)</loc>',block)[1]
  rel=url.removeprefix('https://recordpicker.app/').rstrip('/')
  file=(rel+'/' if rel else '')+'index.html'
  return re.sub(r'<lastmod>.*?</lastmod>','<lastmod>2026-10-06</lastmod>',block) if file in CHANGED else block
 text=re.sub(r'<url>.*?</url>',touch,text,flags=re.S);write(path,text)
 print('Updated',len(CHANGED),'files; public release state and real screenshot labels preserved.')

if __name__=='__main__': apply()
