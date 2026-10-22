"""Apply the reviewed Discogs walkthrough without regenerating other pages."""
import concurrent.futures
import html as escape_html
import json
import re
from pathlib import Path
from lxml import html, etree
from localize_creator_hub import DATA, LOCALES, ROOT, language, prefix, translate_batch

EN = [
 ('p', 'Move your Discogs collection into Record Picker with a CSV export. Start with a small sample so you can check the destination, editions and proposed changes before importing everything.'),
 ('h2', '1. Request your Discogs export'),
 ('p', 'In your Discogs collection, open the settings menu and choose Export My Collection. On the export page, select Collection and Request Data Export. Discogs prepares the file and notifies you when it is ready. Download the CSV and keep the original unchanged.'),
 ('h2', '2. Protect your existing collection'),
 ('p', 'Before a large import, create a dated backup or export of your existing Record Picker collection and check that you can find it. Work on a copy of the Discogs CSV if you edit it. A Discogs CSV is not a complete backup of your Record Picker data.'),
 ('h2', '3. Choose the destination and review the preview'),
 ('p', 'Open CSV import in Record Picker and select your file. Choose your owned collection or your wishlist deliberately. Recognized Discogs columns can be mapped automatically; review the column mapping if the app asks you to, especially artist, title, year and format.'),
 ('p', 'Before confirming, read the preview: additions, updates, records already identical and similar editions to add. Check the proposed changes rather than assuming every row will create a new record. Similar album titles do not prove that two records are the same edition or physical copy.'),
 ('h2', '4. Check a few albums before importing the rest'),
 ('p', 'Use a small sample first, then compare the imported artists, titles, editions and destination with the original CSV. If the result is wrong, stop and review the file and preview before continuing. If all values appear in one column, check the CSV separator. Avoid repeatedly confirming the full import while investigating a mismatch.'),
 ('h2', 'After the import'),
 ('p', 'Check that your albums appear in the intended list. Keep the original CSV and your dated backup, then use the guides below to back up your collection, choose your next record or rediscover albums you have not played recently.'),
]
FR = [
 ('p', 'Transférez votre collection Discogs dans Record Picker avec un export CSV. Commencez par un petit échantillon pour vérifier la destination, les éditions et les changements proposés avant de tout importer.'),
 ('h2', '1. Demander votre export Discogs'),
 ('p', 'Dans votre collection Discogs, ouvrez le menu des paramètres et choisissez Export My Collection. Sur la page d’export, sélectionnez Collection puis Request Data Export. Discogs prépare le fichier et vous prévient lorsqu’il est prêt. Téléchargez le CSV et conservez l’original sans le modifier.'),
 ('h2', '2. Protéger votre collection existante'),
 ('p', 'Avant un import important, créez une sauvegarde ou un export daté de votre collection Record Picker et vérifiez que vous savez le retrouver. Travaillez sur une copie du CSV Discogs si vous le modifiez. Un CSV Discogs ne constitue pas une sauvegarde complète de vos données Record Picker.'),
 ('h2', '3. Choisir la destination et lire l’aperçu'),
 ('p', 'Ouvrez l’import CSV dans Record Picker et sélectionnez votre fichier. Choisissez volontairement votre collection de disques possédés ou votre liste de souhaits. Les colonnes Discogs reconnues peuvent être associées automatiquement ; vérifiez leur correspondance si l’app vous le demande, notamment artiste, titre, année et format.'),
 ('p', 'Avant de confirmer, lisez l’aperçu : ajouts, mises à jour, disques déjà identiques et éditions proches à ajouter. Contrôlez les changements proposés sans supposer que chaque ligne créera un nouveau disque. Des titres d’album semblables ne prouvent pas qu’il s’agit de la même édition ou du même exemplaire physique.'),
 ('h2', '4. Contrôler quelques albums avant d’importer le reste'),
 ('p', 'Commencez par un petit échantillon, puis comparez les artistes, titres, éditions et la destination des disques importés avec le CSV original. Si le résultat est incorrect, arrêtez-vous et relisez le fichier et l’aperçu avant de poursuivre. Si toutes les valeurs apparaissent dans une seule colonne, vérifiez le séparateur CSV. Évitez de confirmer plusieurs fois l’import complet pendant cette vérification.'),
 ('h2', 'Après l’import'),
 ('p', 'Vérifiez que vos albums figurent dans la liste prévue. Conservez le CSV original et votre sauvegarde datée, puis utilisez les guides ci-dessous pour sauvegarder votre collection, choisir votre prochain disque ou retrouver des albums peu écoutés.'),
]

def section_markup(items):
 return '<section id="discogs-walkthrough">' + ''.join('<'+tag+'>'+escape_html.escape(text)+'</'+tag+'>' for tag,text in items) + '</section>'

def update(raw, items):
 # Preserve the page-specific title, navigation, attribution links and SEO head.
 match=re.search(r'(<article\b[^>]*>\s*<h1\b[^>]*>.*?</h1>)(.*?)(<a\b[^>]*href="[^"]*/readme/".*?)(</article>)',raw,re.S)
 if not match: raise ValueError('Missing known guide structure')
 raw=raw[:match.start(2)]+section_markup(items)+raw[match.end(2):]
 # The previous English-only explanation is superseded by the shared walkthrough.
 raw=re.sub(r'(<section id="guide-next-steps">).*?(<h2>Continue with your collection</h2>)',r'\1\2',raw,flags=re.S)
 return raw

def main():
 sources=[text for _,text in EN]
 langs=sorted({language(locale) for locale in LOCALES}-{'en','fr'})
 def translate(lang):
  path=DATA/(lang+'.json'); cache=json.loads(path.read_text())
  batch=[]; size=0
  for index,source in enumerate(sources):
   if source in cache: continue
   if size+len(source)>1800 and batch:
    cache.update(translate_batch(lang,batch)); batch=[]; size=0
   batch.append((index,source)); size+=len(source)
  if batch: cache.update(translate_batch(lang,batch))
  path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n')
  print('Cached '+lang,flush=True)
  return lang,cache
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
  caches=dict(executor.map(translate,langs))
 templates=json.loads((DATA/'templates.json').read_text())
 templates['en-discogs']=update(templates['en-discogs'],EN)
 templates['fr-discogs']=update(templates['fr-discogs'],FR)
 (DATA/'templates.json').write_text(json.dumps(templates,ensure_ascii=False,indent=2)+'\n')
 pages=[]
 for locale in LOCALES:
  lang=language(locale)
  items=FR if lang=='fr' else EN if lang=='en' else [(tag,caches[lang][source]) for tag,source in EN]
  path=ROOT/prefix(locale)/'record-picker/guides/import-discogs/index.html'
  before=path.read_text(); after=update(before,items)
  old=html.fromstring(before); new=html.fromstring(after)
  assert etree.tostring(old.find('head'))==etree.tostring(new.find('head')),path
  assert old.xpath('//nav//a/@href')==new.xpath('//nav//a/@href'),path
  path.write_text(after)
  pages.append(str(path.relative_to(ROOT)))
 for filename in ('sitemap.xml','sitemap-media.xml'):
  path=ROOT/filename
  raw=path.read_text()
  raw,count=re.subn(r'(<url><loc>https://recordpicker\.app/[^<]*record-picker/guides/import-discogs/</loc><lastmod>)[^<]+',r'\g<1>2026-10-22',raw)
  assert count==len(LOCALES),(filename,count)
  path.write_text(raw)
 (ROOT/'data/discogs-walkthrough-2026-10-22.json').write_text(json.dumps({'pages':pages,'source':'https://support.discogs.com/hc/en-us/articles/360007331534-How-Does-The-Collection-Feature-Work','scope':'CSV export, destination, preview, editions and small-sample verification; existing SEO and campaign links preserved'},ensure_ascii=False,indent=2)+'\n')
 print('Updated '+str(len(pages))+' guides')

if __name__=='__main__': main()
