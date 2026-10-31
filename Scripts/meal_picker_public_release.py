# -*- coding: utf-8 -*-
"""Publish verified Meal Picker iOS availability, preserving the other Studio cards."""
from pathlib import Path
from html import escape
import re,json
ROOT=Path(__file__).resolve().parents[1]
URL='https://apps.apple.com/app/meal-picker/id6823270770'
PENDING={
'en':'Mac: awaiting Apple approval',
'fr':'Mac : en attente de validation Apple',
'de':'Mac: wartet auf die Freigabe von Apple',
'es':'Mac: pendiente de aprobación de Apple',
'pt':'Mac: aguardando aprovação da Apple',
'it':'Mac: in attesa di approvazione Apple',
'nl':'Mac: wacht op goedkeuring van Apple',
'da':'Mac: afventer Apples godkendelse',
'no':'Mac: venter på godkjenning fra Apple',
'sv':'Mac: inväntar Apples godkännande',
'fi':'Mac: odottaa Applen hyväksyntää',
'pl':'Mac: oczekuje na zatwierdzenie przez Apple',
'cs':'Mac: čeká na schválení společností Apple',
'sk':'Mac: čaká na schválenie spoločnosťou Apple',
'hu':'Mac: az Apple jóváhagyására vár',
'ro':'Mac: în așteptarea aprobării Apple',
'hr':'Mac: čeka odobrenje Applea',
'sl':'Mac: čaka na odobritev družbe Apple',
'el':'Mac: αναμένεται έγκριση από την Apple',
'ru':'Mac: ожидает одобрения Apple',
'uk':'Mac: очікує схвалення Apple',
'tr':'Mac: Apple onayı bekleniyor',
'ca':'Mac: pendent d’aprovació d’Apple',
'ar':'Mac: بانتظار موافقة Apple',
'he':'Mac: ממתין לאישור Apple',
'hi':'Mac: Apple की मंज़ूरी की प्रतीक्षा में',
'bn':'Mac: Apple-এর অনুমোদনের অপেক্ষায়',
'gu':'Mac: Appleની મંજૂરીની રાહમાં',
'kn':'Mac: Apple ಅನುಮೋದನೆಗಾಗಿ ಕಾಯುತ್ತಿದೆ',
'ml':'Mac: Apple അംഗീകാരത്തിനായി കാത്തിരിക്കുന്നു',
'mr':'Mac: Apple च्या मंजुरीच्या प्रतीक्षेत',
'or':'Mac: Apple ଅନୁମୋଦନ ଅପେକ୍ଷାରେ',
'pa':'Mac: Apple ਦੀ ਮਨਜ਼ੂਰੀ ਦੀ ਉਡੀਕ ਵਿੱਚ',
'ta':'Mac: Apple ஒப்புதலுக்காகக் காத்திருக்கிறது',
'te':'Mac: Apple ఆమోదం కోసం వేచి ఉంది',
'ur':'Mac: Apple کی منظوری کا انتظار ہے',
'id':'Mac: menunggu persetujuan Apple',
'ms':'Mac: menunggu kelulusan Apple',
'vi':'Mac: đang chờ Apple phê duyệt',
'th':'Mac: รอการอนุมัติจาก Apple',
'ja':'Mac：Appleの承認待ち',
'ko':'Mac: Apple 승인 대기 중',
'zh':'Mac：等待 Apple 审核通过'}
def update(source):
 lang=re.search(r'<html[^>]*lang="([^"]+)"',source)[1].split('-')[0]
 if lang=='nb':lang='no'
 assert lang in PENDING,lang
 pattern=r'<article\b[^>]*id="meal-picker".*?</article>'
 old=re.search(pattern,source,re.S)
 if not old:return source
 card=old[0]
 status='iPhone · iPad — App Store · '+PENDING[lang]
 card=re.sub(r'<p class="availability">.*?</p>',
'<p class="availability">'+escape(status)+'</p>',card,count=1,flags=re.S)
 price={'fr':'Téléchargement gratuit · Essai de 7 jours · Achat unique à 6,99 € en France, sans abonnement ni débit automatique. Prix local dans l’app.',
'en':'Free download · 7-day trial · One-time unlock: €6.99 in France, with no subscription or automatic charge. Local price shown in the app.'}.get(lang)
 if price and 'data-meal-price' not in card:card=card.replace('<p class="availability">',
'<p data-meal-price>'+escape(price)+'</p><p class="availability">',1)
 button='<div class="project-store-grid" data-meal-store><a class="store-button store-appstore" href="'+URL+'" data-umami-event="store_click" data-umami-event-destination="apple_ios"><img src="/apps/assets/appstore.svg" alt="" width="26" height="26" class="store-logo"><span class="store-label"><strong>App Store</strong><small>iPhone · iPad</small></span></a></div>'
 if 'data-meal-store' not in card:card=card.replace('<div class="project-card-actions">',
'<div class="project-card-actions">'+button,1)
 source=source[:old.start()]+card+source[old.end():]
 # The download menu must point to iOS, never to the pending Mac release.
 if 'data-meal-download' not in source:
  source=re.sub(r'(<details[^>]*class="hub-menu-group"[^>]*>\s*<summary>.*?</summary>\s*<div class="hub-menu-panel">)(.*?)(</div></details>)',lambda m:m[1]+m[2]+('<a data-meal-download href="'+URL+'" data-umami-event="store_click" data-umami-event-destination="apple_ios">Meal Picker · iPhone · iPad</a>' if 'data-umami-event-destination="apple_ios"' in m[2] and 'store-appstore' in m[2] else '')+m[3],source,flags=re.S)
 return source
if __name__=='__main__':
 count=0
 for p in [ROOT/'apps/index.html',*ROOT.glob('*/apps/index.html')]:
  s=p.read_text();n=update(s)
  if s!=n:p.write_text(n);count+=1
 print('Studio pages updated:',count)
