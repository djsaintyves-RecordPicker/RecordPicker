from pathlib import Path
from lxml import html, etree
import re
root=Path(__file__).resolve().parents[1]
for p in root.rglob('apps/index.html'):
 s=p.read_text(); doc=html.fromstring(s); lang=doc.get('lang','en'); fr=lang.startswith('fr'); en=lang.startswith('en');
 for card in doc.cssselect('article.project-card') if False else doc.xpath('//article[contains(concat(" ",@class," ")," project-card ")]'):
  ident=card.get('id'); old=re.search(r'<article\b[^>]*id="'+re.escape(ident)+r'"[^>]*>.*?</article>',s,re.S)
  if not old: continue
  body=card.find("div[@class='project-card-body']"); actions=card.find("div[@class='project-card-actions']")
  if body is None or actions is None:continue
  stores=[]; links=[]
  for a in list(card.xpath('.//a')):
   if 'store-button' in a.get('class',''):stores.append(a)
   else:links.append(a)
   a.getparent().remove(a)
  for div in list(body.xpath('./div[@class="app-actions"]|./div[@class="routine-art"]')):body.remove(div)
  for note in list(body.xpath('./p[@class="release-note"]')):
   body.remove(note)
   details=etree.SubElement(body,'details',{'class':'project-update'})
   etree.SubElement(details,'summary').text='Nouveautés · 1.0.2' if fr else ('What’s new · 1.0.2' if en else '1.0.2')
   details.append(note)
  for a in list(actions):actions.remove(a)
  grid=etree.SubElement(actions,'div',{'class':'project-store-grid'}) if stores else None
  for a in stores:
   cls=a.get('class',''); span=a.find('span'); oldlabel=''.join(span.itertext()) if span is not None else ''.join(a.itertext())
   if span is not None:a.remove(span)
   label=etree.SubElement(a,'span',{'class':'store-label'})
   if 'store-appstore' in cls:
    etree.SubElement(label,'strong').text='App Store'
    devices='Mac' if 'platform=mac' in a.get('href','') else ('iPhone & Apple Watch' if ident=='snory-teller' else 'iPhone & iPad')
    etree.SubElement(label,'small').text=devices
   elif 'store-microsoftstore' in cls:
    etree.SubElement(label,'strong').text='Microsoft Store';etree.SubElement(label,'small').text='Windows'
   else:
    etree.SubElement(label,'strong').text='Android';etree.SubElement(label,'small').text='Bêta privée' if fr else ('Private beta' if en else ('ベータ版' if lang.startswith('ja') else ('베타' if lang.startswith('ko') else ('测试版' if lang.startswith('zh') else 'Beta'))))
   if 'store-microsoftstore' in cls or 'store-android-beta' in cls:
    for img in a.findall('img'):img.set('class','store-logo store-logo-native')
   grid.append(a)
  for a in sorted(links,key=lambda a:'press-review-link' in a.get('class','')):
   a.set('class',(a.get('class','')+' project-text-link').strip())
   if ident=='physical-routine':a.text=('Découvrir My Physical Routine →' if fr else 'Explore My Physical Routine →') if (fr or en) else a.text
   actions.append(a)
  if fr or en:
   if ident=='snory-teller':
    paras=body.xpath('./p[not(@class)]')
    if len(paras)>1:paras[1].text=('Des bilans nocturnes et des vibrations discrètes sur Apple Watch pour inviter à changer de position lorsque des ronflements sont détectés.' if fr else 'Nightly reports and discreet Apple Watch vibrations that prompt a change of position when snoring is detected.')
   if ident=='meal-picker':
    paras=body.xpath('./p[not(@class)]')
    if len(paras)>2:
     paras[1].text=('Retrouve tes recettes, choisis le repas du jour avec la roue et organise tes menus et ta liste de courses.' if fr else 'Keep your recipes together, pick today’s meal with the wheel and organise your menus and shopping list.')
     for a in paras[2:]:body.remove(a)
   if ident=='record-picker':
    for a in body.xpath('./p[not(@class)]'):
     if a.find('strong') is None:a.text=('Importe ta collection Discogs, organise tes vinyles et CD et tire le prochain album à écouter.' if fr else 'Import your Discogs collection, organise your vinyl and CDs and pick the next album to play.')
   # Same French editorial voice across all four products.
   first=body.find('p/strong')
   if fr and first is not None:
    if ident=='record-picker':first.text='Retrouve le plaisir de choisir un disque.'
    if ident=='snory-teller':first.text='Comprends les sons de ta nuit.'
   if ident=='meal-picker' and fr:card.find('div/p').text='04 · CUISINE'
  # Fix malformed RP icon cache suffix inherited from earlier markup.
  for img in card.xpath('.//img[@class="app-icon"]'):img.set('src',img.get('src','').rstrip('\\'))
  new=html.tostring(card,encoding='unicode',with_tail=False)
  s=s[:old.start()]+new+s[old.end():]
 s=s.replace('studio-suite.css?v=20261022-spacing','studio-suite.css?v=20261022-refined')
 p.write_text(s)
p=root/'Scripts/site_suite_visuals.py';p.write_text(p.read_text().replace('20261022-spacing','20261022-refined'))
