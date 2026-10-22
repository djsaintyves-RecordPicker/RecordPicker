"""Check that structured FAQ answers agree with the published paragraphs."""
from html.parser import HTMLParser
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class Page(HTMLParser):
 def __init__(self):super().__init__();self.paragraph=None;self.paragraphs=[];self.metadata=None;self.schemas=[]
 def handle_starttag(self,tag,attrs):
  if tag=='p':self.paragraph=''
  if tag=='script' and dict(attrs).get('type')=='application/ld+json':self.metadata=''
 def handle_data(self,data):
  if self.paragraph is not None:self.paragraph+=data
  if self.metadata is not None:self.metadata+=data
 def handle_endtag(self,tag):
  if tag=='p' and self.paragraph is not None:self.paragraphs.append(self.paragraph.strip());self.paragraph=None
  if tag=='script' and self.metadata is not None:self.schemas.append(json.loads(self.metadata));self.metadata=None

def audit():
 manifest=json.loads((ROOT/'data/random-pick-claims-2026-10-22.json').read_text());count=0
 for relative in manifest['pages']:
  page=Page();page.feed((ROOT/relative).read_text())
  def walk(item):
   nonlocal count
   if isinstance(item,dict):
    if item.get('@type')=='Question':
     assert item['acceptedAnswer']['text'].strip() in page.paragraphs,(relative,item['name'])
     count+=1
    for value in item.values():walk(value)
   elif isinstance(item,list):
    for value in item:walk(value)
  for schema in page.schemas:walk(schema)
 assert count==21,count
 print('FAQ: 21 structured answers agree with visible text on seven search pages')

if __name__=='__main__':audit()
