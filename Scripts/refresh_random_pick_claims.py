"""Keep current marketing aligned with Random Pick eligibility and favorites."""
from html import escape
import json
import re
from lxml import html
from refresh_feature_overview import EN,FR
from localize_creator_hub import ROOT,DATA,language

ANSWERS={
 'en':[
  'Review the current draw cycle and available exclusions. A proposed record is not necessarily a record you have listened to.',
  'If other artists are eligible, use the option to avoid consecutive picks by the same artist where available. You can also exclude an artist temporarily. Draw history records proposals, not confirmed listening.'
 ],
 'fr':[
  'Consultez le cycle de tirage en cours et les exclusions disponibles. Un disque proposé n’est pas nécessairement un disque que vous avez écouté.',
  'Si des disques d’autres artistes sont éligibles, utilisez l’option qui évite les tirages consécutifs du même artiste lorsqu’elle est disponible. Vous pouvez aussi exclure temporairement un artiste. L’historique des tirages conserve les propositions, pas des écoutes confirmées.'
 ]}
OLD={
 'en':['Use listening history and less-played records to reduce repetition.','Use exclusions and listening history, or give less-played records more weight.'],
 'fr':['Utilisez l’historique et les disques moins écoutés pour éviter les répétitions.','Utilisez les exclusions et l’historique, ou donnez plus de poids aux disques les moins écoutés.']}

def main():
 entries=json.loads((ROOT/'data/guide-discovery-2026-10-22.json').read_text())['pages'];changed=[]
 for entry in entries:
  lang=language(entry['guide_locale']);cache=json.loads((DATA/(lang+'.json')).read_text()) if lang not in ('en','fr') else {}
  text=FR['random'] if lang=='fr' else EN['random'] if lang=='en' else cache[EN['random']]
  parent=(ROOT/entry['page']).parent
  for path in [ROOT/entry['page'],parent/'ios-app/index.html']:
   raw=path.read_text();before=raw
   section=re.search(r'<section\b(?=[^>]*id="app")[^>]*>.*?</section>',raw,re.S)
   if section:
    block,count=re.subn(r'(<article class="card">\s*<h3>.*?</h3>\s*<p>).*?(</p>)',lambda m:m.group(1)+escape(text)+m.group(2),section.group(0),count=1,flags=re.S)
    if count:raw=raw[:section.start()]+block+raw[section.end():]
   if before!=raw:path.write_text(raw);changed.append(str(path.relative_to(ROOT)))
  if lang not in ANSWERS:continue
  path=parent/'random-vinyl-record-picker/index.html';raw=path.read_text();before=raw;doc=html.fromstring(raw)
  methods=doc.xpath('//main//article[@class="growth-method"]')
  if not methods:continue
  old1=methods[2].find('p').text_content()
  questions=doc.xpath('//main//details');assert len(questions)==3,path
  old2=questions[1].find('p').text_content()
  replacements=dict(zip((old1,old2),ANSWERS[lang]))
  for old,new in replacements.items():
   raw,count=re.subn(r'(<p>)'+re.escape(escape(old,quote=False))+r'(</p>)',lambda m:m.group(1)+escape(new)+m.group(2),raw)
   assert count>=1,(path,old)
  structured_replacements={**replacements,**dict(zip(OLD[lang],ANSWERS[lang]))}
  def structured(match):
   value=json.loads(match.group(2))
   def walk(item):
    if isinstance(item,dict):return {key:walk(val) for key,val in item.items()}
    if isinstance(item,list):return [walk(val) for val in item]
    return structured_replacements.get(item,item) if isinstance(item,str) else item
   return match.group(1)+json.dumps(walk(value),ensure_ascii=False,separators=(',',':'))+match.group(3)
  raw=re.sub(r'(<script\b(?=[^>]*type="application/ld\+json")[^>]*>)(.*?)(</script>)',structured,raw,flags=re.S)
  if before!=raw:path.write_text(raw);changed.append(str(path.relative_to(ROOT)))
 path=ROOT/'data/random-pick-claims-2026-10-22.json'
 previous=json.loads(path.read_text()).get('pages',[]) if path.exists() else []
 path.write_text(json.dumps({'pages':sorted(set(previous+changed)),'scope':'Current home/iOS feature cards and FR/EN search-page answers. Historical release notes are preserved.'},ensure_ascii=False,indent=2)+'\n')
 print(str(len(changed))+' current Random Pick marketing pages aligned')

if __name__=='__main__':main()
