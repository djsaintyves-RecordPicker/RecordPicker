"""Complete verified Book Picker iOS release discovery without changing other apps."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
URL='https://apps.apple.com/app/id6826948524'
def studio(s):
 lang=re.search(r'<html[^>]*lang="([^"]+)"',s)[1];fr=lang.startswith('fr');base='/book-picker/'+('fr' if fr else 'en')+'/'
 if 'data-book-project' not in s:
  s=re.sub(r'(<a[^>]*href="[^"]*/apps/dulpi/"[^>]*>)', '<a data-book-project href="#book-picker">06 · Book Picker</a>'+r'\1',s,count=1)
 if 'data-book-download' not in s:
  s=re.sub(r'(<a[^>]*data-meal-download[^>]*>.*?</a>)',r'\1'+'<a data-book-download href="'+URL+'" data-umami-event="store_click" data-umami-event-destination="apple_ios">Book Picker · iPhone · iPad</a>',s,count=1,flags=re.S)
 def card(m):
  c=m[0]
  if 'data-book-release' not in c:
   line='1.0.0 · Disponible sur iPhone et iPad' if fr else '1.0.0 · iPhone · iPad · App Store'
   c=c.replace('<p class="availability">','<p data-book-release>'+line+'</p><p class="availability">',1)
  return c
 return re.sub(r'<article\b[^>]*id="book-picker".*?</article>',card,s,flags=re.S)
def product(s,fr):
 if 'data-book-details' in s:return s
 s=s.replace('/moop/assets/moop.css','/book-picker/assets/book-picker.css')
 s=s.replace('<main id="main">','<a class="skip" href="#main">'+('Aller au contenu' if fr else 'Skip to content')+'</a><main id="main">')
 s=s.replace('<nav class="site-nav">','<nav class="site-nav" aria-label="Navigation">')
 title='Une bibliothèque qui vous ressemble.' if fr else 'A library that feels like yours.'
 body='Ajoutez un livre par scan ISBN, recherche ISBN, saisie manuelle ou import CSV BookBuddy. Retrouvez vos livres en liste, petites ou grandes couvertures et triez notamment par titre, nom de famille de l’auteur ou date d’ajout.' if fr else 'Add a book by ISBN scan, ISBN lookup, manual entry or BookBuddy CSV import. Browse a list, small covers or large covers, and sort by title, author surname or date added.'
 title2='Choisissez votre prochaine lecture.' if fr else 'Choose your next read.'
 body2='Gardez vos favoris et vos listes de lecture, affinez les filtres par statut, genre ou tag et lancez un choix au hasard. Les fiches rassemblent vos informations, notes et couvertures personnalisées.' if fr else 'Keep favorites and reading lists, narrow your selection by reading status, genre or tag, then make a random pick. Book details bring together your information, notes and custom covers.'
 title3='Pour commencer' if fr else 'Getting started'
 steps=['Ajoutez votre premier livre ou importez votre bibliothèque.','Choisissez la présentation et les filtres qui vous conviennent.','Retrouvez une lecture ou laissez le hasard vous surprendre.'] if fr else ['Add your first book or import your library.','Choose your preferred layout and filters.','Find a read or let a random pick surprise you.']
 lang='fr' if fr else 'en'
 extra=f'<section class="section split" data-book-details><div><h2>{title}</h2><p>{body}</p></div><div><h2>{title2}</h2><p>{body2}</p></div></section><section class="section"><h2>{title3}</h2><ol>'+''.join('<li>'+x+'</li>' for x in steps)+f'</ol><div class="actions"><a class="button primary" href="{URL}">'+('Télécharger sur l’App Store' if fr else 'Download on the App Store')+f'</a><a class="button" href="/book-picker/support-{lang}.html">'+('Lire l’aide' if fr else 'Read the guide')+'</a></div></section>'
 s=s.replace('</div></main>',extra+'</div></main>')
 s=s.replace('</head>','<meta property="og:type" content="website"><meta property="og:url" content="https://recordpicker.app/book-picker/'+lang+'/"><meta name="twitter:card" content="summary"><script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@type':'SoftwareApplication','name':'Book Picker','operatingSystem':'iOS, iPadOS','applicationCategory':'LifestyleApplication','softwareVersion':'1.0.0','url':'https://recordpicker.app/book-picker/'+lang+'/','downloadUrl':URL},ensure_ascii=False)+'</script></head>')
 return s
if __name__=='__main__':
 for p in [ROOT/'apps/index.html',*ROOT.glob('*/apps/index.html')]:p.write_text(studio(p.read_text()))
 for lang in ['fr','en']:
  p=ROOT/'book-picker'/lang/'index.html';p.write_text(product(p.read_text(),lang=='fr'))
 css=ROOT/'book-picker/assets/book-picker.css';css.parent.mkdir(exist_ok=True)
 css.write_text((ROOT/'moop/assets/moop.css').read_text()+'\n/* Book Picker identity */\n.button.primary{background:#593151;border-color:#593151}.reel-stage{background:transparent;box-shadow:none;border-radius:0}.reel-stage img{width:min(100%,280px);height:auto;border-radius:24%}a:focus-visible{outline-color:#593151}.eyebrow{color:#593151}footer{padding-block:30px}ol li{padding-block:8px}\n')
