"""Align localized Mac search snippets without altering app content or routing."""
import concurrent.futures
from html import escape
import json
import re
from localize_creator_hub import ROOT,DATA,language,translate_batch
from site_social_identity import normalize

EN={'title':'Record Picker for Mac — Vinyl and CD collection','description':'Manage your vinyl and CD collection on your Mac, import a Discogs CSV, back up your catalogue and choose your next album with Record Picker.'}
FR={'title':'Record Picker pour Mac — Collection de vinyles et CD','description':'Gérez votre collection de vinyles et CD sur Mac, importez un CSV Discogs, sauvegardez votre catalogue et choisissez votre prochain album avec Record Picker.'}

def main():
 entries=json.loads((ROOT/'data/guide-discovery-2026-10-22.json').read_text())['pages']
 regions=json.loads((ROOT/'data/feature-region-labels.json').read_text())
 def one(lang):
  path=DATA/(lang+'.json');cache=json.loads(path.read_text());missing=[(i,text) for i,text in enumerate(EN.values()) if text not in cache]
  if missing:cache.update(translate_batch(lang,missing));path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n')
  return lang,cache
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:caches=dict(pool.map(one,sorted({language(e['guide_locale']) for e in entries}-{'en','fr'})))
 pages=[]
 for entry in entries:
  loc=entry['guide_locale'];lang=language(loc);copy=FR if lang=='fr' else EN if lang=='en' else {key:caches[lang][text] for key,text in EN.items()}
  parent=(ROOT/entry['page']).parent;path=parent/'mac-app/index.html';raw=path.read_text()
  body=raw.split('<body',1)[1]
  suffix=regions[str((parent/'readme/index.html').relative_to(ROOT))]
  title=copy['title']+(' — '+suffix if suffix else '')
  description=copy['description']+(' · '+suffix if suffix else '')
  raw,count=re.subn(r'<title>.*?</title>','<title>'+escape(title)+'</title>',raw,count=1,flags=re.S);assert count==1,path
  raw,count=re.subn(r'(<meta\b[^>]*name="description"[^>]*content=")[^"]*',lambda m:m.group(1)+escape(description,quote=True),raw,count=1);assert count==1,path
  raw=normalize(raw,'features')
  assert raw.split('<body',1)[1]==body,path
  path.write_text(raw);pages.append(str(path.relative_to(ROOT)))
 (ROOT/'data/mac-search-metadata-2026-10-22.json').write_text(json.dumps({'pages':pages,'preserved':['visible body','canonical and hreflang','Mac App Store platform parameter and campaign attribution']},ensure_ascii=False,indent=2)+'\n')
 print('Mac search metadata aligned on '+str(len(pages))+' pages')

if __name__=='__main__':main()
