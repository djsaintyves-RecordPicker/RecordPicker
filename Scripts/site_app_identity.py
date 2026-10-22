"""Keep real product names in SoftwareApplication entities across the ecosystem."""
import argparse
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
PRODUCTS={'6780422305':'Record Picker','6820177689':'Snory Teller','6820104318':'My Physical Routine'}

def normalize(raw):
 def replace(match):
  before=json.loads(match.group(2));changed=[False]
  def walk(value):
   if isinstance(value,dict):
    if value.get('@type')=='SoftwareApplication':
     encoded=json.dumps([value.get('downloadUrl'),value.get('installUrl')],ensure_ascii=False)
     for identifier,name in PRODUCTS.items():
      if identifier in encoded and value.get('name')!=name:value['name']=name;changed[0]=True;break
    for item in value.values():walk(item)
   elif isinstance(value,list):
    for item in value:walk(item)
  walk(before)
  if not changed[0]:return match.group(0)
  return match.group(1)+json.dumps(before,ensure_ascii=False,separators=(',',':'))+match.group(3)
 return re.sub(r'(<script\b(?=[^>]*type="application/ld\+json")[^>]*>)(.*?)(</script>)',replace,raw,flags=re.S)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args();changed=[];count=0
 for path in ROOT.rglob('*.html'):
  if any(part in ('.git','node_modules','work','outputs') for part in path.relative_to(ROOT).parts):continue
  before=path.read_text()
  if 'rel="canonical" href="https://recordpicker.app/' not in before:continue
  count+=1;after=normalize(before)
  if after!=before:
   changed.append(str(path.relative_to(ROOT)))
   if args.write:path.write_text(after)
 if changed and not args.write:raise SystemExit('Application identity differs: '+', '.join(changed))
 if args.write:
  path=ROOT/'data/app-identity-2026-10-22.json';previous=json.loads(path.read_text()).get('pages',[]) if path.exists() else []
  path.write_text(json.dumps({'pages':sorted(set(previous+changed)),'policy':'SoftwareApplication.name is the app name; page titles remain distinct metadata.'},ensure_ascii=False,indent=2)+'\n')
 print(f'Application identity checked on {count} public pages; {len(changed)} updated')

if __name__=='__main__':main()
