"""Refresh Windows landing copy and localized navigation, preserving captures and store URLs."""
import concurrent.futures
import json
from lxml import html, etree
from localize_creator_hub import ROOT, DATA, language, prefix, translate_batch, BRANDS
from site_social_identity import normalize
BRANDS.extend(['Light','Pro','Random Pick','Mood Pick','Today’s Pick','Windows 11','Microsoft Store','x64','ARM64'])
EN={
 'title':'Record Picker for Windows — vinyl and CD collection',
 'description':'Organize vinyl and CDs on Windows 11: import a CSV, search your albums and choose your next record. Try Record Picker free with up to 100 records.',
 'deck':'Organize your vinyl and CD collection on Windows 11, on x64 or ARM64 PCs. Download Record Picker from the Microsoft Store.',
 'heading':'Your collection. Your next listen.',
 'lead':'Import a collection CSV or add your records, search your albums and choose what to play with Random Pick, Mood Pick or Today’s Pick.',
 'pricing':'Start free with up to 100 owned records. Light unlocks unlimited records and imports; Pro adds advanced tools. They are separate one-time purchases. Check the local price in Microsoft Store before buying.',
 'capture':'Authentic app capture',
 'capture_title':'Record Picker 3.0.1 on Windows 11',
 'capture_note':'The capture below shows the French interface of the released Windows app.',
 'graph_title':'A graph that follows your filters',
 'graph':'Explore documented links between records, understand the evidence behind each path and save a path as an editable Listening Journey.',
 'move_title':'Move several records together',
 'move':'Move filtered records to a physical storage location after reviewing a preview of the exact changes.',
 'insights_title':'More reliable listening insights',
 'insights':'Listening filters and Collection Stories distinguish confirmed listens from picks and playback launches.',
 'story_title':'Your collection tells its story',
 'story':'Create a private, local Collection Story and save or share it as a carefully limited PNG card.',
 'reliable_title':'Clarity and reliability',
 'reliable':'Graph performance, review cleanup, translations and several backup and recovery workflows have been improved.',
}
FR={
 'title':'Record Picker pour Windows — collection de vinyles et CD',
 'description':'Organisez vinyles et CD sur Windows 11 : import CSV, recherche et choix du prochain disque. Essayez Record Picker gratuitement jusqu’à 100 disques.',
 'deck':'Organisez votre collection de vinyles et CD sur Windows 11, sur PC x64 ou ARM64. Téléchargez Record Picker depuis le Microsoft Store.',
 'heading':'Votre collection, votre prochaine écoute.',
 'lead':'Importez un CSV de collection ou ajoutez vos disques, recherchez vos albums et choisissez quoi écouter avec Random Pick, Mood Pick ou Today’s Pick.',
 'pricing':'Commencez gratuitement jusqu’à 100 disques possédés. Light débloque les disques et imports illimités ; Pro ajoute les outils avancés. Ce sont deux achats uniques séparés. Vérifiez le prix local dans le Microsoft Store avant l’achat.',
 'capture':'Capture authentique de l’application',
 'capture_title':'Record Picker 3.0.1 sur Windows 11',
 'capture_note':'La capture ci-dessous montre l’interface française de l’application Windows publiée.',
 'graph_title':'Un graphe fidèle à vos filtres',
 'graph':'Explorez les liens documentés entre vos disques, comprenez les indices qui expliquent chaque parcours et enregistrez un chemin comme parcours d’écoute modifiable.',
 'move_title':'Déplacer plusieurs disques ensemble',
 'move':'Déplacez les disques filtrés vers un emplacement physique après avoir vérifié un aperçu exact des changements.',
 'insights_title':'Des analyses d’écoute plus fiables',
 'insights':'Les filtres d’écoute et les Histoires de la collection distinguent les écoutes confirmées des tirages et des lancements de lecture.',
 'story_title':'Votre collection raconte son histoire',
 'story':'Créez localement une Histoire de la collection privée, puis enregistrez-la ou partagez-la sous forme de carte PNG aux informations volontairement limitées.',
 'reliable_title':'Clarté et fiabilité',
 'reliable':'Les performances du graphe, le nettoyage des critiques, les traductions et plusieurs parcours de sauvegarde et de récupération ont été améliorés.',
}

def main():
 entries=json.loads((ROOT/'data/guide-discovery-2026-10-22.json').read_text())['pages']
 langs=sorted({language(e['guide_locale']) for e in entries}-{'en','fr'})
 def cache_one(lang):
  p=DATA/(lang+'.json'); c=json.loads(p.read_text()); batch=[]; size=0
  for i,s in enumerate(EN.values()):
   if s in c: continue
   if size+len(s)>1700 and batch: c.update(translate_batch(lang,batch));batch=[];size=0
   batch.append((i,s)); size+=len(s)
  if batch:c.update(translate_batch(lang,batch))
  p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n'); print('Cached '+lang,flush=True);return lang,c
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:caches=dict(pool.map(cache_one,langs))
 regions=json.loads((ROOT/'data/feature-region-labels.json').read_text()); pages=[]
 for e in entries:
  loc=e['guide_locale'];lang=language(loc);cp=FR if lang=='fr' else EN if lang=='en' else {k:caches[lang][s] for k,s in EN.items()}
  path=(ROOT/e['page']).parent/'windows-app/index.html';raw=path.read_text();t=html.fromstring(raw)
  old_links=t.xpath('//link[@rel="canonical" or @rel="alternate"]/@href');images=t.xpath('//figure//img/@src');stores=t.xpath('//a[contains(@href,"apps.microsoft.com")]/@href')
  def settext(xpath,text):
   ns=t.xpath(xpath);assert len(ns)==1,(path,xpath);ns[0].text=text
  suffix=regions[str(path.relative_to(ROOT)).replace('windows-app/','readme/')]
  title=cp['title']+(' — '+suffix if suffix else '')
  settext('//title',title)
  # Keep useful descriptions already repaired; replace the old availability placeholders.
  meta=t.xpath('//meta[@name="description"]')[0]
  if len(meta.get('content',''))<120:meta.set('content',cp['description']+(' · '+suffix if suffix else ''))
  settext('//p[@class="deck"]',cp['deck'])
  sec=t.xpath('//section[contains(@class,"windows-release")]')[0];sec.set('data-windows-version',json.loads((ROOT/'data/release-state.json').read_text())['current_release']['platform_versions']['windows'])
  settext('//section[contains(@class,"windows-release")]//h2',cp['heading'])
  settext('//section[contains(@class,"windows-release")]//p[@class="lead"]',cp['lead'])
  head=sec.xpath('.//div[@class="section-head"]')[0]
  for p in head.xpath('./p[not(@class="lead")]'):head.remove(p)
  p=etree.Element('p',{'class':'windows-purchase-summary'});p.text=cp['pricing'];head.insert(2,p)
  for li,(a,b) in zip(sec.xpath('.//ul/li'),[('graph_title','graph'),('move_title','move'),('insights_title','insights'),('story_title','story'),('reliable_title','reliable')]):
   li.find('strong').text=cp[a];li.find('span').text=cp[b]
  settext('//section[contains(@class,"windows-screenshot-section")]//p[@class="kicker"]',cp['capture'])
  settext('//*[@id="windows-authentic-title"]',cp['capture_title'])
  settext('//section[contains(@class,"windows-screenshot-section")]//p[@class="lead"]',cp['capture_note'])
  cta=t.xpath('//div[@class="cta-row"]')[0];studio='/'+prefix(loc)+'apps/'
  if not cta.xpath('./a[@href="'+studio+'"]'):
   a=etree.SubElement(cta,'a',{'class':'button glass','href':studio});a.text='Record Picker Studio'
  if not t.xpath('//*[@id="priority-app-guides"]'):
   home=html.fromstring((ROOT/e['page']).read_text());guide=home.get_element_by_id('priority-app-guides');t.xpath('//main')[0].append(guide)
  raw='<!doctype html>'+html.tostring(t,encoding='unicode',method='html');raw=normalize(raw,'features');after=html.fromstring(raw)
  assert old_links==after.xpath('//link[@rel="canonical" or @rel="alternate"]/@href')
  assert images==after.xpath('//figure//img/@src')
  assert stores==after.xpath('//a[contains(@href,"apps.microsoft.com")]/@href')
  path.write_text(raw);pages.append(str(path.relative_to(ROOT)))
 (ROOT/'data/windows-discovery-2026-10-22.json').write_text(json.dumps({'pages':pages,'version':json.loads((ROOT/'data/release-state.json').read_text())['current_release']['platform_versions']['windows'],'captureVersion':'3.0.1','captureLanguage':'fr','translationReview':'Machine translations outside French/English; native review pending'},ensure_ascii=False,indent=2)+'\n')
 print('Refreshed '+str(len(pages))+' Windows pages')
if __name__=='__main__':main()
