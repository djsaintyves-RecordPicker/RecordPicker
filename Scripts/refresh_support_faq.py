"""Publish generalized support answers; private source correspondence stays outside this repo."""
import concurrent.futures
import json
from lxml import html, etree
from localize_creator_hub import ROOT, DATA, language, prefix, translate_batch, BRANDS
from site_social_identity import normalize
BRANDS.extend(['Light','Pro','TERA','CSV','Discogs','Apple Watch','iOS','Android','.recordpicker'])
EN={
 'heading':'Frequently asked questions',
 'intro':'Practical answers about import, playback and backups. Instructions depend on your device and installed version.',
 'q1':'Does a Discogs CSV need a Genres column?',
 'a1':'No. Current Record Picker imports accept a Discogs collection CSV without a Genres column. Keep the original export and review the import preview before applying changes. If an older version rejects the file, update the app first; do not add a dummy column just to reproduce an old workaround.',
 'q2':'Is a collection backup the same as a synchronization file?',
 'a2':'No. A .recordpicker backup, a collection CSV and a synchronization file serve different purposes. Use the matching import or restore action. In the Android beta, use “Import my collection” for a .recordpicker backup, not the Optional Sync screen. Keep the original backup; if the destination already contains records, check the available merge or replacement options before proceeding.',
 'q3':'How do I confirm that I actually listened to a record?',
 'a3':'On iPhone and iPad with Record Picker 3.1.2 and Pro, use the disc-shaped “Listened” button at the right end of the Random Pick action row. The Apple Watch companion also has a listening confirmation action. These controls depend on the platform and installed version; do not expect the same button in Mac 3.0.1. Drawing a record, opening a streaming service and confirming a listen are different events.',
 'q4':'Does excluding a record mark it as listened?',
 'a4':'No. Exclusion keeps the record in your collection and removes it from eligible draws until you remove the exclusion. It does not create a confirmed listening session. Use the listening confirmation control when it is available in your version.',
 'q5':'Does opening Apple Music or another streaming app guarantee playback?',
 'a5':'No. A listening link can open a search or a destination in an external music service. Check the selected album and start playback there if needed. Availability, account access and any required music subscription depend on that service. Opening the service is not proof that you listened to the record.',
 'q6':'Can I use a TERA barcode scanner on Mac?',
 'a6':'Compatibility with every TERA model has not been physically verified. Keyboard/HID mode can enter barcode digits, but this alone does not certify the complete Record Picker workflow. Before relying on a scanner, check its exact model and input mode with support. Include your operating system and app version; do not send pairing codes or your full collection backup.',
 'guides':'Import and backup guides',
 'discogs':'Import a Discogs collection',
 'backup':'Back up and restore your collection',
}
FR={
 'heading':'Questions fréquentes',
 'intro':'Des réponses pratiques sur l’import, la lecture et les sauvegardes. Les manipulations dépendent de votre appareil et de la version installée.',
 'q1':'Un CSV Discogs doit-il contenir une colonne Genres ?',
 'a1':'Non. Les imports actuels de Record Picker acceptent un CSV de collection Discogs sans colonne Genres. Conservez l’export original et vérifiez l’aperçu avant d’appliquer les changements. Si une ancienne version refuse le fichier, mettez d’abord l’application à jour ; inutile d’ajouter une colonne artificielle pour reproduire un ancien contournement.',
 'q2':'Une sauvegarde de collection est-elle un fichier de synchronisation ?',
 'a2':'Non. Une sauvegarde .recordpicker, un CSV de collection et un fichier de synchronisation ont des rôles différents. Utilisez l’action d’import ou de restauration correspondante. Dans la bêta Android, utilisez « Import my collection » pour une sauvegarde .recordpicker, et non l’écran Optional Sync. Gardez la sauvegarde originale ; si la destination contient déjà des disques, vérifiez les options de fusion ou de remplacement disponibles avant de continuer.',
 'q3':'Comment confirmer que j’ai réellement écouté un disque ?',
 'a3':'Sur iPhone et iPad avec Record Picker 3.1.2 et Pro, utilisez le bouton « Écouté », en forme de disque, à droite dans la ligne des actions de Random Pick. L’app compagnon Apple Watch propose aussi une action de confirmation d’écoute. Ces commandes dépendent de la plateforme et de la version installée ; ne cherchez pas le même bouton dans Mac 3.0.1. Tirer un disque, ouvrir un service musical et confirmer une écoute sont trois événements différents.',
 'q4':'Exclure un disque le marque-t-il comme écouté ?',
 'a4':'Non. L’exclusion conserve le disque dans votre collection et le retire des tirages éligibles jusqu’à ce que vous leviez l’exclusion. Elle ne crée pas de session d’écoute confirmée. Utilisez la commande de confirmation d’écoute lorsqu’elle est disponible dans votre version.',
 'q5':'Ouvrir Apple Music ou un autre service garantit-il la lecture ?',
 'a5':'Non. Un lien d’écoute peut ouvrir une recherche ou une destination dans un service musical externe. Vérifiez l’album sélectionné et lancez sa lecture dans ce service si nécessaire. La disponibilité, l’accès au compte et un éventuel abonnement musical dépendent du service. Son ouverture ne prouve pas que vous avez écouté le disque.',
 'q6':'Puis-je utiliser un scanner de codes-barres TERA sur Mac ?',
 'a6':'La compatibilité de tous les modèles TERA n’a pas été vérifiée par un test matériel. Le mode clavier/HID peut saisir les chiffres d’un code-barres, mais cela ne certifie pas tout le parcours dans Record Picker. Avant de compter sur un scanner, vérifiez son modèle exact et son mode de saisie avec l’assistance. Indiquez votre système et la version de l’app ; n’envoyez ni code d’appairage ni sauvegarde complète de votre collection.',
 'guides':'Guides d’import et de sauvegarde',
 'discogs':'Importer une collection Discogs',
 'backup':'Sauvegarder et restaurer votre collection',
}

def main():
 entries=json.loads((ROOT/'data/guide-discovery-2026-10-22.json').read_text())['pages']
 langs=sorted({language(e['guide_locale']) for e in entries}-{'en','fr'})
 def one(lang):
  path=DATA/(lang+'.json');cache=json.loads(path.read_text());batch=[];size=0
  for i,s in enumerate(EN.values()):
   if s in cache:continue
   if size+len(s)>1600 and batch:cache.update(translate_batch(lang,batch));batch=[];size=0
   batch.append((i,s));size+=len(s)
  if batch:cache.update(translate_batch(lang,batch))
  path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n');print('FAQ cached '+lang,flush=True);return lang,cache
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:caches=dict(pool.map(one,langs))
 pages=[]
 for e in entries:
  loc=e['guide_locale'];lang=language(loc);cp=FR if lang=='fr' else EN if lang=='en' else {k:caches[lang][v] for k,v in EN.items()}
  path=(ROOT/e['page']).parent/'support/index.html';raw=path.read_text();t=html.fromstring(raw)
  for n in t.xpath('//*[@id="support-faq" or @id="support-faq-schema"]'):n.getparent().remove(n)
  sec=etree.Element('section',{'class':'doc-content seo-faq','id':'support-faq'});etree.SubElement(sec,'h2').text=cp['heading'];etree.SubElement(sec,'p').text=cp['intro']
  qs=[]
  for i in range(1,7):
   d=etree.SubElement(sec,'details');etree.SubElement(d,'summary').text=cp['q'+str(i)];etree.SubElement(d,'p').text=cp['a'+str(i)]
   qs.append({'@type':'Question','name':cp['q'+str(i)],'acceptedAnswer':{'@type':'Answer','text':cp['a'+str(i)]}})
  etree.SubElement(sec,'h3').text=cp['guides'];nav=etree.SubElement(sec,'p')
  for route,label in [('import-discogs',cp['discogs']),('backup',cp['backup'])]:
   a=etree.SubElement(nav,'a',{'href':'/'+prefix(loc)+'record-picker/guides/'+route+'/'});a.text=label;a.tail=' · '
  a=etree.SubElement(nav,'a',{'href':'/'+prefix(loc)+'apps/'});a.text='Record Picker Studio'
  t.xpath('//main')[0].append(sec)
  script=etree.SubElement(t.xpath('//head')[0],'script',{'type':'application/ld+json','id':'support-faq-schema'})
  script.text=json.dumps({'@context':'https://schema.org','@type':'FAQPage','mainEntity':qs},ensure_ascii=False,separators=(',',':'))
  raw='<!doctype html>'+html.tostring(t,encoding='unicode',method='html');raw=normalize(raw,'features');path.write_text(raw);pages.append(str(path.relative_to(ROOT)))
 (ROOT/'data/support-faq-2026-10-22.json').write_text(json.dumps({'pages':pages,'questionsPerPage':6,'translationReview':'French and English authored; other translations need native review'},ensure_ascii=False,indent=2)+'\n')
 print('Added six support questions on '+str(len(pages))+' pages')
if __name__=='__main__':main()
