"""Apply the 22 October search audit to the measured FR/EN acquisition paths."""
from pathlib import Path
import re
from html import escape, unescape
from urllib.parse import urlsplit, parse_qs, parse_qsl, urlencode, urlunsplit
from site_campaign_links import normalize as normalize_campaign_links
ROOT=Path(__file__).resolve().parents[1]
EN=['','en-us/','en-gb/','en-ca/','en-au/']
PAGES=['index.html','fr/index.html','mac-app/index.html','fr/mac-app/index.html','random-vinyl-record-picker/index.html','fr/random-vinyl-record-picker/index.html']+[p+'choose-vinyl-record/index.html' for p in EN]+['fr/choose-vinyl-record/index.html']
GUIDES=['record-picker/guides/import-discogs/index.html','fr/record-picker/guides/import-discogs/index.html','record-picker/guides/choose/index.html','fr/record-picker/guides/choose/index.html']

def store_attrs(match):
 tag=match.group(0); href=re.search(r'href="([^"]+)"',tag)
 if not href:return tag
 u=urlsplit(unescape(href.group(1))); app=None;dest=None
 if u.netloc=='apps.apple.com':
  app=next((name for ident,name in [('6780422305','record_picker'),('6820177689','snory_teller'),('6820104318','my_physical_routine')] if ident in u.path),None)
  dest='apple_mac' if parse_qs(u.query).get('platform')==['mac'] else 'apple_ios'
 elif u.netloc=='apps.microsoft.com' and '9N2ZWRL4M3JC' in u.path:app='record_picker';dest='microsoft'
 if not app:return tag
 if app=='record_picker' and relative.endswith('mac-app/index.html') and u.netloc=='apps.apple.com':
  query=dict(parse_qsl(u.query));query['platform']='mac'
  updated=urlunsplit(u._replace(query=urlencode(query)))
  tag=tag[:href.start(1)]+escape(updated,quote=True)+tag[href.end(1):];dest='apple_mac'
  tag=re.sub(r'data-umami-event-destination="[^"]*"','data-umami-event-destination="apple_mac"',tag)
 elif relative in PAGES and u.netloc=='apps.apple.com' and not parse_qs(u.query).get('platform'):
  dest='apple_app_store'
  tag=re.sub(r'data-umami-event-destination="[^"]*"','data-umami-event-destination="apple_app_store"',tag)
 if 'data-umami-event=' not in tag:tag=tag[:-1]+' data-umami-event="store_click" data-umami-event-destination="'+dest+'">'
 if 'data-umami-event-app=' not in tag:tag=tag[:-1]+' data-umami-event-app="'+app+'">'
 return tag

for relative in PAGES+GUIDES:
 path=ROOT/relative;t=path.read_text();fr=relative.startswith('fr/')
 if relative.endswith('choose-vinyl-record/index.html') and not fr:
  title='What Vinyl Should I Play Next? Pick from Your Collection'
  if relative.startswith('en-'):title+=' — '+{'en-us':'US','en-gb':'UK','en-ca':'Canada','en-au':'Australia'}[relative.split('/')[0]]
  desc='Choose a vinyl record to listen to from your own collection: five practical methods, random picks, and a Discogs-to-Mac walkthrough with Record Picker.'
  if relative.startswith('en-'):desc+=' For listeners in '+{'en-us':'the United States','en-gb':'the United Kingdom','en-ca':'Canada','en-au':'Australia'}[relative.split('/')[0]]+'.'
  t=re.sub(r'<title>.*?</title>','<title>'+title+'</title>',t,count=1)
  for attr,key,value in [('name','description',desc),('property','og:title',title),('property','og:description',desc),('name','twitter:title',title),('name','twitter:description',desc)]:
   t=re.sub(r'<meta '+attr+'="'+key+r'" content="[^"]*">','<meta '+attr+'="'+key+'" content="'+escape(value,quote=True)+'">',t,count=1)
  block='''<section class="seo-section" id="collection-to-listening"><h2>Already use Discogs? Go from your collection to tonight’s record</h2><ol><li><strong>Export your collection.</strong> Download the collection CSV from Discogs; a wantlist is a different export.</li><li><strong>Import it into Record Picker.</strong> Follow the CSV guide and check the imported records before editing your collection.</li><li><strong>Pick something to play.</strong> Open Random Pick and draw from your own albums. Start free with up to 100 records; the store shows any optional Light or Pro purchase before you buy.</li></ol><div class="doc-actions"><a class="button primary" href="/record-picker/guides/import-discogs/">Import your Discogs collection step by step</a><a class="button glass" href="/mac-app/">Explore the Mac app and screenshots</a></div><p>Looking to buy your first vinyl record? This guide is about choosing what to play from records you already own.</p></section>'''
  if 'id="collection-to-listening"' not in t:t=t.replace('<section class="seo-related">',block+'<section class="seo-related">',1)
 if relative in ['index.html','fr/index.html','random-vinyl-record-picker/index.html','fr/random-vinyl-record-picker/index.html','mac-app/index.html','fr/mac-app/index.html']:
  prefix='/fr' if fr else ''
  block=('<section class="doc-shell seo-shell" data-search-store-path><h2>'+('De votre collection Discogs à votre prochaine écoute' if fr else 'From your Discogs collection to your next listen')+'</h2><p>'+('Importez votre fichier CSV, retrouvez vos albums sur Mac et choisissez un disque à écouter. Commencez gratuitement jusqu’à 100 disques.' if fr else 'Import your collection CSV, find your albums on Mac, and choose a record to play. Start free with up to 100 records.')+'</p><div class="doc-actions"><a class="button primary" href="'+prefix+'/record-picker/guides/import-discogs/">'+('Importer ma collection Discogs' if fr else 'Import my Discogs collection')+'</a><a class="button glass" href="'+prefix+'/mac-app/">'+('Découvrir Record Picker sur Mac' if fr else 'Explore Record Picker for Mac')+'</a></div></section>')
  # No redundant self-link on the Mac landing page.
  if relative.endswith('mac-app/index.html'):
   block=re.sub(r'<a class="button glass".*?</a>','',block)
  if 'data-search-store-path' not in t:t=t.replace('</main>',block+'</main>',1)
 t=re.sub(r'<a\b[^>]*>',store_attrs,t)
 if relative in PAGES:
  if '/apps/measurement.js' not in t:t=t.replace('</head>','<script defer src="/apps/measurement.js?v=20261022-store-paths"></script></head>',1)
  # Restrict external requests to the existing EU analytics service and its collection endpoint.
  t=t.replace("script-src 'self' 'unsafe-inline';", "script-src 'self' 'unsafe-inline' https://cloud.umami.is;")
  t=t.replace("connect-src 'none';", "connect-src 'self' https://cloud.umami.is https://gateway.umami.is;")
  notice=('<aside class="doc-shell measurement-notice" data-store-measurement-notice><p>'+('Statistiques de pages et de clics via Umami Cloud (région Europe), sans cookies publicitaires. Aucun contenu de vos applications n’est envoyé. ' if fr else 'Page and click statistics via Umami Cloud (Europe region), without advertising cookies. No app content is sent. ')+'<a href="https://umami.is/privacy">'+('Confidentialité Umami' if fr else 'Umami privacy')+'</a>.</p><label><input type="checkbox" data-measurement-optout> '+('Désactiver la mesure sur ce navigateur' if fr else 'Disable measurement in this browser')+'</label></aside>')
  if 'data-store-measurement-notice' not in t:t=t.replace('</body>',notice+'</body>',1)
 path.write_text(normalize_campaign_links(t))
print('Updated',len(PAGES+GUIDES),'FR/EN search and store paths')
