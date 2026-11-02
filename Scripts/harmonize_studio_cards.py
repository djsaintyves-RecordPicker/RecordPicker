"""Use the same semantic regions for every released app card."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
import re
ROOT=Path(__file__).resolve().parents[1]
class Node:
 def __init__(self,tag='',attrs=(),text=None):self.tag=tag;self.attrs=dict(attrs);self.children=[];self.text=text
 def html(self):
  if self.text is not None:return self.text
  a=''.join(' '+k+('="'+escape(v,quote=True)+'"' if v is not None else '') for k,v in self.attrs.items())
  return '<'+self.tag+a+'>'+('' if self.tag in {'img','br','hr','input','source'} else ''.join(x.html() for x in self.children)+'</'+self.tag+'>')
 def has(self,c):return c in self.attrs.get('class','').split()
class Tree(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=False);self.root=Node('root');self.stack=[self.root]
 def handle_starttag(self,t,a):
  n=Node(t,a);self.stack[-1].children.append(n)
  if t not in {'img','br','hr','input','source','meta','link'}:self.stack.append(n)
 def handle_endtag(self,t):
  if self.stack[-1].tag==t:self.stack.pop()
 def handle_data(self,d):self.stack[-1].children.append(Node(text=d))
 def handle_entityref(self,n):self.handle_data('&'+n+';')
 def handle_charref(self,n):self.handle_data('&#'+n+';')
def normalize(match):
 raw=match[0]
 if 'data-unified-card' in raw:return raw
 t=Tree();t.feed(raw);card=t.root.children[0]
 if card.attrs.get('id') not in ['record-picker','snory-teller','physical-routine','meal-picker','moovie-picker','book-picker']:return raw
 regions={};summary=[];media=[];meta=[]
 for n in card.children:
  if n.has('project-card-head'):regions['head']=n.html()
  elif n.has('project-card-actions'):regions['actions']=n.html()
  elif n.has('project-card-body'):
   for x in n.children:
    if x.tag=='p' and not x.has('availability') and not any(k.startswith('data-') for k in x.attrs):summary.append(x.html())
    elif x.tag in ['img','figure'] or x.has('routine-art') or x.has('app-preview') or x.has('presentation-shot'):media.append(x.html())
    else:meta.append(x.html())
  elif n.text is None:media.append(n.html())
 if 'head' not in regions or 'actions' not in regions:return raw
 card.attrs['data-unified-card']=''
 card.children=[]
 content=regions['head']+'<div class="project-card-body unified-summary">'+''.join(summary)+'</div><div class="unified-media">'+''.join(media)+'</div><div class="unified-meta">'+''.join(meta)+'</div>'+regions['actions']
 card.children=[Node(text=content)]
 return card.html()
def update(s):return re.sub(r'<article\b[^>]*class="card project-card".*?</article>',normalize,s,flags=re.S)
if __name__=='__main__':
 for p in [ROOT/'apps/index.html',*ROOT.glob('*/apps/index.html')]:p.write_text(update(p.read_text()))
