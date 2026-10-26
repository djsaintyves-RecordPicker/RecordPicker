"""Add the announced projects and proposed suite offer without implying App Store availability."""
import json,re
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]

def normalize(source):
    if '/apps/styles.css' not in source or 'id="meal-picker"' not in source:
        return source
    data=json.loads((ROOT/'data/studio-upcoming-apps-2026-10-26.json').read_text())
    match=re.search(r'<html[^>]*lang="([^"]+)"',source)
    language=(match[1] if match else 'en').split('-')[0]
    if match and match[1].startswith('zh-'):
        language='zh-CN' if match[1]=='zh-Hans' else 'zh-TW'
    if language=='nb':language='no'
    c=data['copy'].get(language,data['copy']['en'])
    for ident in ('moovie-picker','book-picker','bundle-rps'):
        source=re.sub(r'<article\b[^>]*id="'+ident+r'".*?</article>','',source,flags=re.S)
    cards=[]
    for ident,name,tag,title,body in [('moovie-picker','Moovie Picker','movies','movieTitle','movieBody'),('book-picker','Book Picker','books','bookTitle','bookBody')]:
        cards.append('<article class="card project-card" id="'+ident+'"><div class="project-card-head"><p class="tag">'+escape(c[tag])+'</p><img class="app-icon" src="/apps/assets/'+ident+'-icon.png?v=20261026" alt="" width="64" height="64" loading="lazy"><h2>'+name+'</h2></div><div class="project-card-body"><p><strong>'+escape(c[title])+'</strong></p><p>'+escape(c[body])+'</p><p class="availability">'+escape(c['status'])+'</p></div><div class="project-card-actions"></div></article>')
    source=re.sub(r'(?=<article\b[^>]*id="dulpi")',lambda _:''.join(cards),source,count=1)
    source=re.sub(r'(<article\b[^>]*id="dulpi".*?<p class="tag">)\d{2}',r'\g<1>08',source,count=1,flags=re.S)
    bundle = '<article class="card project-card" id="bundle-rps"><div class="project-card-head"><p class="tag">'+escape(c['bundleTag'])+'</p><img class="app-icon" src="/assets/brand/rps/icon-192.png" alt="" width="64" height="64" loading="lazy"><h2>Suite Record Picker Studio</h2></div><div class="project-card-body"><p><strong>'+escape(c['bundleTitle'])+'</strong></p><p>'+escape(c['bundleBody'])+'</p><p class="availability">'+escape(c['bundleStatus'])+'</p></div><div class="project-card-actions"></div></article>'
    source=re.sub(r'(<article\b[^>]*id="dulpi".*?</article>)',lambda match:bundle+match[0],source,count=1,flags=re.S)
    return source

if __name__=='__main__':
    count=0
    for path in ROOT.glob('**/apps/index.html'):
        source=path.read_text();updated=normalize(source)
        if updated!=source:path.write_text(updated);count+=1
    print('Studio upcoming app cards updated:',count)
