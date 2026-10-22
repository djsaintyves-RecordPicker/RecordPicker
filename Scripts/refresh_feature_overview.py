"""Refresh current feature copy without rewriting screenshots or release history."""
import concurrent.futures
import html as escaping
import json
import re
from lxml import html, etree
from localize_creator_hub import ROOT, DATA, LOCALES, NAMES, BRANDS, language, prefix, translate_batch
from site_social_identity import normalize
BRANDS.extend(['Light', 'Pro'])

EN={
 'title':'Record Picker features — Discogs import, collection and album picks',
 'description':'Organize vinyl and CDs with Record Picker: Discogs CSV import, album picks and backups. Free up to 100 records; Light and Pro are separate one-time purchases.',
 'lead':'Organize your vinyl and CD collection, import a Discogs CSV and choose your next album with Random Pick or Mood Pick. Start free with up to 100 records. Light unlocks unlimited records and imports; Pro adds advanced tools. They are separate one-time purchases, without a subscription. Available features depend on your device and installed version.',
 'summary':'Explore collection management, album selection, import, export, backup and privacy below. For the current Free, Light and Pro options, see the pricing section. The version history is kept separately for reference.',
 'random':'Random Pick proposes a record from the eligible collection. Use the selection and exclusion controls available in your version to adapt the draw to the moment.',
 'weight':'Optional preference for favorites where available; drawing a record is separate from actually listening to it.',
 'watch':'Choose a record from your wrist with the actions supported by your installed Apple Watch version.',
 'localizations':'50 localizations',
 'localization_detail':'Record Picker is localized for 50 languages and regional variants, including Japanese, Korean, Simplified Chinese and Traditional Chinese.',
 'variants':'Language and regional variants are distinct localizations, not 50 different languages.'
}
FR={
 'title':'Fonctionnalités Record Picker — Import Discogs, collection et choix d’albums',
 'description':'Organisez vinyles et CD avec Record Picker : import CSV Discogs, choix d’albums et sauvegardes. Gratuit jusqu’à 100 disques ; achats uniques Light et Pro séparés.',
 'lead':'Organisez votre collection de vinyles et CD, importez un CSV Discogs et choisissez votre prochain album avec Random Pick ou Mood Pick. Commencez gratuitement jusqu’à 100 disques. Light débloque les disques et imports illimités ; Pro ajoute les outils avancés. Ce sont deux achats uniques séparés, sans abonnement. Les fonctions disponibles dépendent de votre appareil et de la version installée.',
 'summary':'Découvrez ci-dessous la gestion de collection, le choix d’albums, l’import, l’export, la sauvegarde et la confidentialité. Consultez la section tarifaire pour les offres actuelles Free, Light et Pro. L’historique des versions est conservé à part pour référence.',
 'random':'Random Pick propose un disque parmi les éléments éligibles de la collection. Utilisez les réglages de sélection et d’exclusion disponibles dans votre version pour adapter le tirage au moment.',
 'weight':'Préférence facultative pour les favoris lorsqu’elle est disponible ; tirer un disque est distinct de son écoute réelle.',
 'watch':'Choisissez un disque au poignet avec les actions prises en charge par votre version Apple Watch installée.',
 'localizations':'50 localisations',
 'localization_detail':'Record Picker est localisé dans 50 langues et variantes régionales, notamment en japonais, coréen, chinois simplifié et chinois traditionnel.',
 'variants':'Les langues et variantes régionales constituent des localisations distinctes, et non 50 langues différentes.'
}

def replace_text(raw,pattern,text):
 raw,count=re.subn(pattern,lambda m:m.group(1)+escaping.escape(text)+m.group(2),raw,count=1,flags=re.S)
 assert count==1,pattern
 return raw

def main():
 manifest=json.loads((ROOT/'data/guide-discovery-2026-10-22.json').read_text())['pages']
 region_labels=json.loads((ROOT/'data/feature-region-labels.json').read_text())
 languages=sorted({language(p['guide_locale']) for p in manifest}-{'en','fr'})
 def one(lang):
  path=DATA/(lang+'.json');cache=json.loads(path.read_text()); batch=[];size=0
  for i,text in enumerate(EN.values()):
   if text in cache:continue
   if size+len(text)>1800 and batch:cache.update(translate_batch(lang,batch));batch=[];size=0
   batch.append((i,text));size+=len(text)
  if batch:cache.update(translate_batch(lang,batch))
  path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n'); print('Cached '+lang,flush=True)
  return lang,cache
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:caches=dict(pool.map(one,languages))
 pages=[]; indexable=set()
 for entry in manifest:
  loc=entry['guide_locale']; lang=language(loc); copy=FR if lang=='fr' else EN if lang=='en' else {k:caches[lang][v] for k,v in EN.items()}
  parent=(ROOT/entry['page']).parent;path=parent/'readme/index.html';raw=path.read_text();before=html.fromstring(raw)
  copy=dict(copy);suffix=region_labels[str(path.relative_to(ROOT))]
  if suffix:
   copy['title']+=' — '+suffix
   copy['description']+=' · '+suffix
  raw=replace_text(raw,r'(<title>).*?(</title>)',copy['title'])
  raw=re.sub(r'(<meta\b[^>]*name="description"[^>]*content=")[^"]*',lambda m:m.group(1)+escaping.escape(copy['description'],quote=True),raw,count=1)
  if '<p class="lead">' in raw:raw=replace_text(raw,r'(<p class="lead">).*?(</p>)',copy['lead'])
  else:raw=raw.replace('<section class="doc-content">','<section class="doc-content"><p class="lead">'+escaping.escape(copy['lead'])+'</p>',1)
  if '<p class="feature-summary">' in raw:raw=replace_text(raw,r'(<p class="feature-summary">).*?(</p>)',copy['summary'])
  else:
   marker='<div class="doc-grid feature-grid">' if '<div class="doc-grid feature-grid">' in raw else '<h2 id="version-history">'
   raw=raw.replace(marker,'<p class="feature-summary">'+escaping.escape(copy['summary'])+'</p>'+marker,1)
  cards=list(re.finditer(r'<article class="card feature-card">.*?</article>',raw,re.S));assert len(cards) in (0,9),path
  for index in ((8,5,3) if cards else ()):
   match=cards[index];card=match.group(0)
   if index==3:
    card=replace_text(card,r'(<p>).*?(</p>)',copy['random'])
    card=replace_text(card,r'(<li>).*?(</li>)',copy['weight'])
   elif index==5:card=replace_text(card,r'(<p>).*?(</p>)',copy['watch'])
   else:card='<article class="card feature-card"><h3>'+escaping.escape(copy['localizations'])+'</h3><p>'+escaping.escape(copy['localization_detail'])+'</p><p>'+escaping.escape(copy['variants'])+'</p></article>'
   raw=raw[:match.start()]+card+raw[match.end():]
  studio='/'+prefix(loc)+'apps/'
  if not before.xpath('//div[@class="doc-actions"]/a[@href="'+studio+'"]'):
   button='<a class="button glass" href="'+studio+'">Record Picker Studio</a>'
   if '<div class="doc-actions">' in raw:
    raw=re.sub(r'(<div class="doc-actions">.*?)(</div>)',lambda m:m.group(1)+button+m.group(2),raw,count=1,flags=re.S)
   else:
    raw,count=re.subn(r'(<section class="doc-hero">.*?)(</section>)',lambda m:m.group(1)+'<div class="doc-actions">'+button+'</div>'+m.group(2),raw,count=1,flags=re.S)
    assert count==1,path
  raw=raw.replace('<section id="priority-app-guides" class="guide">','<section id="priority-app-guides" class="section">')
  if 'id="priority-app-guides"' not in raw:
   home=(ROOT/entry['page']).read_text()
   guides=re.search(r'<section id="priority-app-guides"[^>]*>.*?</section>',home,re.S)
   assert guides,entry['page']
   raw=raw.replace('</main>',guides.group(0)+'</main>',1)
  def schema(match):
   data=json.loads(match.group(2))
   if data.get('@type')=='SoftwareApplication':
    data['inLanguage']=LOCALES;data['availableLanguage']=NAMES
    return match.group(1)+json.dumps(data,ensure_ascii=False,separators=(',',':'))+match.group(3)
   return match.group(0)
  raw=re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)',schema,raw,flags=re.S)
  raw=normalize(raw,'features');after=html.fromstring(raw)
  assert all(name in after.xpath('//p[@class="lead"]')[0].text_content() for name in ('Light','Pro')),path
  assert before.xpath('//link[@rel="canonical" or @rel="alternate"]/@href')==after.xpath('//link[@rel="canonical" or @rel="alternate"]/@href'),path
  assert before.xpath('//figure//img/@src')==after.xpath('//figure//img/@src'),path
  # Everything after the current feature grid is the historical release record.
  old_history=before.get_element_by_id('version-history')
  new_history=after.get_element_by_id('version-history')
  assert etree.tostring(old_history)==etree.tostring(new_history),path
  assert [etree.tostring(node) for node in old_history.itersiblings()]==[etree.tostring(node) for node in new_history.itersiblings()],path
  relative=str(path.relative_to(ROOT));url='https://recordpicker.app/'+relative.removesuffix('index.html')
  if after.xpath('//link[@rel="canonical"]/@href')==[url] and not any('noindex' in value for value in after.xpath('//meta[@name="robots"]/@content')):indexable.add(url)
  path.write_text(raw);pages.append(relative)
 for filename in ('sitemap.xml','sitemap-media.xml'):
  path=ROOT/filename;raw,count=re.subn(r'(<loc>https://recordpicker\.app/[^<]*readme/</loc>\s*<lastmod>)[^<]+',r'\g<1>2026-10-22',path.read_text());assert count==len(indexable),(filename,count,len(indexable));path.write_text(raw)
 (ROOT/'data/feature-overview-2026-10-22.json').write_text(json.dumps({'pages':pages,'source':'Current feature overview corrected; historical version notes and screenshots preserved','locales':50},ensure_ascii=False,indent=2)+'\n')
 print('Updated '+str(len(pages))+' feature pages')

if __name__=='__main__':main()
