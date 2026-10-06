#!/usr/bin/env python3
"""Replace development badges with the current beta-recruitment status."""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]
STATUS = {
 '':'Waiting for beta testers',
 'ar':'بانتظار مختبري النسخة التجريبية', 'ca':'Esperant provadors beta',
 'da':'Afventer betatestere', 'de':'Wartet auf Betatester',
 'el':'Αναμονή για δοκιμαστές beta',
 'en-au':'Waiting for beta testers','en-ca':'Waiting for beta testers',
 'en-gb':'Waiting for beta testers','en-us':'Waiting for beta testers',
 'es-es':'A la espera de probadores beta','es-mx':'A la espera de probadores beta',
 'fi':'Odottaa beetatestaajia','fr':'En attente de bêta-testeurs',
 'fr-ca':'En attente de bêta-testeurs','he':'ממתינים לבודקי בטא',
 'hi':'बीटा परीक्षकों की प्रतीक्षा में','id':'Menunggu penguji beta',
 'it':'In attesa di beta tester','ja':'ベータテスター募集中',
 'ko':'베타 테스터 모집 중','nb':'Venter på betatestere',
 'nl':'Wacht op bètatesters','pl':'Oczekiwanie na beta testerów',
 'pt-br':'À espera de testadores beta','pt-pt':'À espera de testadores beta',
 'ru':'Ожидание бета-тестеров','sv':'Väntar på betatestare',
 'th':'รอผู้ทดสอบเบต้า','tr':'Beta test kullanıcıları bekleniyor',
 'vi':'Đang chờ người thử nghiệm beta','zh-hans':'等待 Beta 测试者','zh-hant':'等待 Beta 測試者',
}

def main():
 from announce_android_pc_development import COPY
 changed=0
 changed_pages=set()
 for locale, label in STATUS.items():
  old=COPY[locale][0]
  old_values={old}
  # Keep this script idempotent even once the generator copy has been updated.
  from announce_cross_platform_roadmap import STATUS as roadmap
  old_values.add(roadmap.get(locale or 'en-us', ('',''))[1])
  legacy={
   '':'In development','en-au':'In development','en-ca':'In development','en-gb':'In development','en-us':'In development',
   'ar':'قيد التطوير','ca':'En desenvolupament','da':'Under udvikling','de':'In Entwicklung','el':'Υπό ανάπτυξη','es-es':'En desarrollo','es-mx':'En desarrollo','fi':'Kehitteillä','fr':'En développement','fr-ca':'En développement','he':'בפיתוח','hi':'विकासाधीन','id':'Dalam pengembangan','it':'In sviluppo','ja':'開発中','ko':'개발 중','nb':'Under utvikling','nl':'In ontwikkeling','pl':'W przygotowaniu','pt-br':'Em desenvolvimento','pt-pt':'Em desenvolvimento','ru':'В разработке','sv':'Under utveckling','th':'อยู่ระหว่างการพัฒนา','tr':'Geliştirme aşamasında','vi':'Đang phát triển','zh-hans':'开发中','zh-hant':'開發中',
  }
  old_values.add(legacy[locale])
  pages=list((ROOT/locale).rglob('*.html')) if locale else [ROOT/'index.html']+list((ROOT/'android-app').rglob('*.html'))+list((ROOT/'mac-app').rglob('*.html'))+list((ROOT/'random-vinyl-record-picker').rglob('*.html'))
  # International root routes use the same English navigation as root/index.html.
  if not locale:
   pages=[p for p in ROOT.rglob('*.html') if p.relative_to(ROOT).parts[0] not in STATUS and p.relative_to(ROOT).parts[0] not in ('tmp','snory-teller')]
  for page in pages:
   text=page.read_text();updated=text
   for old in old_values:
    if not old or old==label:continue
    updated=updated.replace('>'+escape(old)+'<','>'+escape(label)+'<')
    updated=updated.replace('Android: '+escape(old)+'"','Android: '+escape(label)+'"')
   if updated!=text:page.write_text(updated);changed+=1;changed_pages.add(page.relative_to(ROOT).as_posix())
 # Both current generators now share the exact recruitment label.
 path=ROOT/'Scripts/announce_android_pc_development.py';text=path.read_text()
 marker='from update_android_beta_status import STATUS as BETA_STATUS\nCOPY.update({locale: (BETA_STATUS[locale], row[1], row[2]) for locale, row in COPY.items()})\n\n'
 if 'STATUS as BETA_STATUS' not in text:
  pos=text.index('BETA_COPY =');text=text[:pos]+marker+text[pos:];path.write_text(text)
 path=ROOT/'Scripts/announce_cross_platform_roadmap.py';text=path.read_text()
 marker='from announce_android_pc_development import COPY as ANDROID_COPY\nSTATUS = {locale: (row[0], ANDROID_COPY[locale][0]) for locale, row in STATUS.items()}\n\n'
 if 'COPY as ANDROID_COPY' not in text:
  pos=text.index('BLOCK =');text=text[:pos]+marker+text[pos:];path.write_text(text)
 path=ROOT/'sitemap.xml';text=path.read_text()
 def touch(match):
  block=match[0];url=re.search(r'<loc>(.*?)</loc>',block)[1]
  route=url.removeprefix('https://recordpicker.app/').rstrip('/')
  file=(route+'/' if route else '')+'index.html'
  if file in changed_pages:return re.sub(r'<lastmod>.*?</lastmod>','<lastmod>2026-10-06</lastmod>',block)
  return block
 updated=re.sub(r'<url>.*?</url>',touch,text,flags=re.S)
 if updated!=text:path.write_text(updated)
 print('Android beta recruitment status updated on',changed,'pages.')

if __name__=='__main__':main()
