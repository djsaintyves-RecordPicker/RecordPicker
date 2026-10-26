#!/usr/bin/env python3
"""Build only the independent MOOP section from its public in-app documents."""
from pathlib import Path
from html import escape
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1]
SITE='https://recordpicker.app'
CONTACT='support@recordpicker.app'
COPY={
'fr':{'lang':'fr-FR','studio':'/fr/apps/','home':'Accueil','support':'Assistance','privacy':'Confidentialité','contact':'Écrire à l’assistance','skip':'Aller au contenu','updated':'Mise à jour : 26 octobre 2026','kicker':'MOOP · Films et séries','title':'Choisir quoi regarder, simplement.','lead':'Rassemblez vos films et séries à voir, retrouvez vos listes et laissez la bobine vous aider à décider.','status':'Informations et assistance de Moovie Picker. Aucun abonnement de visionnage n’est fourni par MOOP.','modes_title':'Trois façons de trouver votre prochain titre.','modes':[('Au hasard','Une bobine, votre bibliothèque et un cycle de tirage qui évite les répétitions.'),('Aujourd’hui','Un choix du jour à partir de vos titres et des filtres que vous avez retenus.'),('Envie','Affinez par genre, durée, type de titre ou tag, puis choisissez dans la sélection correspondante.')],'library':'Gardez vos repères.','points':['Films et séries, favoris et titres déjà vus.','Listes personnelles, tags, notes et progression des séries.','Recherche, tri et actions sur plusieurs fiches.','Illustrations personnelles, sauvegarde JSON et export CSV.'],'control':'Vos informations, sous votre contrôle.','control_copy':'La bibliothèque est enregistrée dans l’application. Vous choisissez les imports, exports et partages. La synchronisation iCloud facultative entre Mac et iPhone est désactivée par défaut et nécessite un compte Apple avec iCloud. Les fichiers JSON restent disponibles pour les transferts. La Watch utilise l’iPhone associé.','public_note':'La version publique démarre sans catalogue tiers préchargé. Les films et séries se regardent sur les services externes : leurs offres, pays et abonnements s’appliquent.','need_help':'Besoin d’un coup de main ?','help_copy':'Retrouvez les parcours d’import, de sauvegarde, de restauration et de transfert entre appareils, ou contactez Yves Durand.','studio_label':'Record Picker Studio','publisher':'Édité par Yves Durand','hosting':'Ce site est hébergé par GitHub Pages. Cette section n’ajoute pas de mesure d’audience ni de cookie publicitaire. La politique de confidentialité de GitHub s’applique au fonctionnement de l’hébergement.','host_link':'Confidentialité de GitHub','marketing_desc':'Moovie Picker : listes de films et séries, choix au hasard, du jour ou selon l’envie. Informations, assistance et confidentialité.','privacy_desc':'Confidentialité de Moovie Picker : bibliothèque locale, recherches externes, images choisies, Watch et sauvegardes.','support_desc':'Assistance Moovie Picker : organiser ses films et séries, sauvegarder, restaurer et transférer sa bibliothèque.'},
'en':{'lang':'en','studio':'/apps/','home':'Home','support':'Support','privacy':'Privacy','contact':'Email support','skip':'Skip to content','updated':'Updated: 26 October 2026','kicker':'MOOP · Movies and series','title':'Choose what to watch, simply.','lead':'Bring your movies and series together, keep your own lists, and let the film reel help you decide.','status':'Information and support for Moovie Picker. MOOP does not supply viewing subscriptions.','modes_title':'Three ways to find your next title.','modes':[('Random','A film reel, your library and a draw cycle that avoids repeats.'),('Today','A daily choice from your titles and the filters you have selected.'),('Mood','Narrow by genre, duration, title type or tag, then choose from the matching selection.')],'library':'Keep your own bearings.','points':['Movies and series, favorites and watched titles.','Personal lists, tags, ratings and series progress.','Search, sorting and actions on selected records.','Personal illustrations, JSON backups and CSV export.'],'control':'Your information, under your control.','control_copy':'The library is saved in the app. You choose imports, exports and sharing. Optional iCloud sync between Mac and iPhone is off by default and requires an Apple Account with iCloud. JSON files remain available for transfers. Apple Watch uses its paired iPhone.','public_note':'The public version starts without a preloaded third-party catalog. Movies and series play on external services, subject to their offers, countries and subscriptions.','need_help':'Need a hand?','help_copy':'Find import, backup, recovery and device-transfer instructions, or contact Yves Durand.','studio_label':'Record Picker Studio','publisher':'Published by Yves Durand','hosting':'This site is hosted by GitHub Pages. This section adds no audience analytics or advertising cookie. GitHub’s privacy policy applies to hosting operations.','host_link':'GitHub Privacy','marketing_desc':'Moovie Picker: movie and series lists, random, daily and mood-based choices. Product information, support and privacy.','privacy_desc':'Moovie Picker privacy: local library, external searches, selected images, Watch and backups.','support_desc':'Moovie Picker support: organize movies and series, back up, recover and transfer your library.'}}

COPY['fr']['release_status']='Version App Store en préparation.'
COPY['en']['release_status']='App Store release in preparation.'
COPY['fr']['purchase_title']='Un seul achat pour iPhone et Mac.'
COPY['fr']['purchase_copy']='Téléchargement gratuit. Démarrez explicitement un essai gratuit facultatif de 7 jours, sans facturation automatique. Ensuite, un achat définitif unique débloque MOOP sur iPhone et Mac avec le même compte Apple. Prix de base : 1,99 € ; le prix local est affiché dans la fenêtre d’achat Apple. Aucun abonnement. Vous pouvez restaurer les achats ; cela ne synchronise pas votre bibliothèque.'
COPY['en']['purchase_title']='One purchase for iPhone and Mac.'
COPY['en']['purchase_copy']='Free download. Explicitly start an optional 7-day free trial, with no automatic charge. Afterwards, one permanent purchase unlocks MOOP on iPhone and Mac with the same Apple Account. Base price: €1.99; Apple’s purchase sheet displays the local price. No subscription. Purchases can be restored; this does not synchronise your library.'

def route(locale,kind='home'):
 return '/moop/'+locale+'/'+('' if kind=='home' else kind+'/')
def head(locale,kind,url,title,description):
 c=COPY[locale]
 alternates=''.join(f'<link rel="alternate" hreflang="{COPY[l]["lang"]}" href="{SITE+route(l,kind)}">' for l in ['fr','en'])
 alternates+=f'<link rel="alternate" hreflang="x-default" href="{SITE+("/moop/" if kind=="home" else route("fr",kind))}">'
 schema={'@context':'https://schema.org','@type':'WebPage','name':title,'url':SITE+url,'inLanguage':c['lang'],'description':description,'publisher':{'@type':'Person','name':'Yves Durand'}}
 return f'''<!doctype html>
<html lang="{c['lang']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{escape(title)}</title><meta name="description" content="{escape(description,quote=True)}"><link rel="canonical" href="{SITE+url}">{alternates}<meta property="og:type" content="website"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:url" content="{SITE+url}"><meta property="og:site_name" content="Moovie Picker"><link rel="icon" href="/moop/assets/reel.svg" type="image/svg+xml"><link rel="stylesheet" href="/moop/assets/moop.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script></head><body><a class="skip" href="#main">{c['skip']}</a>'''
def navigation(locale,kind):
 c=COPY[locale];other='en' if locale=='fr' else 'fr'
 links=''.join(f'<a href="{route(locale,k)}"'+(' aria-current="page"' if kind==k else '')+f'>{c[k]}</a>' for k in ['home','support','privacy'])
 links+=f'<a href="{route(other,kind)}" lang="{COPY[other]["lang"]}" hreflang="{COPY[other]["lang"]}">{"English" if locale=="fr" else "Français"}</a>'
 return f'<header class="site-header"><div class="container"><a class="brand" href="{route(locale)}"><img src="/moop/assets/reel.svg" width="40" height="40" alt=""><span>Moovie Picker</span></a><nav class="site-nav" aria-label="Navigation">{links}</nav></div></header>'
def footer(locale):
 c=COPY[locale]
 return f'<footer class="site-footer"><div class="container"><span>© 2026 Yves Durand · MOOP</span><nav aria-label="{"Liens utiles" if locale=="fr" else "Useful links"}"><a href="mailto:{CONTACT}">{CONTACT}</a><a href="{c["studio"]}">{c["studio_label"]}</a></nav></div></footer></body></html>\n'
def paragraphs(text):
 blocks=[];section_open=False
 for block in re.split(r'\n\s*\n',text.strip()):
  block=block.strip()
  if not block:continue
  if block.startswith('# '):
   blocks.append('<p class="eyebrow">'+escape(block[2:])+'</p>')
  elif ('\n' not in block and len(block)<100 and not block.endswith(('.',':','?','!'))) or block.startswith('## '):
   if section_open:blocks.append('</section>')
   blocks.append('<section><h2>'+escape(block.lstrip('# '))+'</h2>');section_open=True
  else:blocks.append('<p>'+escape(block)+'</p>')
 if section_open:blocks.append('</section>')
 return '\n'.join(blocks)

def document(locale,kind,content):
 c=COPY[locale];title=c[kind]+' — Moovie Picker';url=route(locale,kind)
 body=f'<main id="main" class="document"><h1>{c[kind]}</h1><p class="meta">{c["updated"]} · {c["publisher"]}</p><p class="contact-line"><a href="mailto:{CONTACT}">{CONTACT}</a></p>'+paragraphs(content)
 if kind=='privacy':body+=f'<section><h2>{"Ce site" if locale=="fr" else "This website"}</h2><p>{c["hosting"]}</p><p><a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">{c["host_link"]}</a></p></section>'
 return head(locale,kind,url,title,c[kind+'_desc'])+navigation(locale,kind)+body+'</main>'+footer(locale)
def landing(locale,url=None):
 c=COPY[locale];url=url or route(locale)
 modes=''.join(f'<article><span class="mode-index">0{i+1}</span><h3>{escape(name)}</h3><p>{escape(copy)}</p></article>' for i,(name,copy) in enumerate(c['modes']))
 points=''.join('<li>'+escape(p)+'</li>' for p in c['points'])
 body=f'''<main id="main"><div class="container"><section class="hero"><div><p class="eyebrow">{c['kicker']}</p><h1>{c['title']}</h1><p class="lead">{c['lead']}</p><p class="note">{c['release_status']}</p><div class="actions"><a class="button primary" href="{route(locale,'support')}">{c['support']}</a><a class="button" href="{route(locale,'privacy')}">{c['privacy']}</a></div></div><div class="reel-stage"><img src="/moop/assets/reel.svg" width="400" height="400" alt=""></div></section><section class="section"><h2>{c['modes_title']}</h2><div class="modes">{modes}</div></section><section class="section split"><div><h2>{c['library']}</h2><ul class="points">{points}</ul></div><div><h2>{c['control']}</h2><p>{c['control_copy']}</p><p class="note">{c['public_note']}</p></div></section><section class="section"><h2>{c['purchase_title']}</h2><p>{c['purchase_copy']}</p></section><section class="section"><div class="contact"><h2>{c['need_help']}</h2><p>{c['help_copy']}</p><a class="button primary" href="mailto:{CONTACT}">{c['contact']}</a></div></section><p class="note">{c['status']}</p></div></main>'''
 return head(locale,'home',url,'Moovie Picker — '+('Films, séries et listes à voir' if locale=='fr' else 'Movies, series and watchlists'),c['marketing_desc'])+navigation(locale,'home')+body+footer(locale)
def gateway():
 c=COPY['fr'];url='/moop/'
 title='Moovie Picker — Informations et assistance / Support'
 description='Moovie Picker (MOOP) : choisissez la langue des informations, de l’assistance et de la confidentialité. Français / English.'
 body=f'''<main id="main"><div class="container"><section class="hero"><div><p class="eyebrow">Moovie Picker · MOOP</p><h1>Films. Séries.<br>Votre prochain choix.</h1><p class="lead">Informations et assistance en français.<br><span lang="en">Product information and support in English.</span></p><div class="actions"><a class="button primary" href="/moop/fr/" lang="fr-FR" hreflang="fr-FR">Français</a><a class="button" href="/moop/en/" lang="en" hreflang="en">English</a></div></div><div class="reel-stage"><img src="/moop/assets/reel.svg" width="400" height="400" alt=""></div></section><section class="section split"><div><h2>Assistance</h2><p>Organiser, choisir, sauvegarder et retrouver vos titres.</p><a href="/moop/fr/support/">Lire l’assistance</a></div><div lang="en"><h2>Support</h2><p>Organize, choose, back up and recover your titles.</p><a href="/moop/en/support/">Read support</a></div></section></div></main>'''
 return head('fr','home',url,title,description)+navigation('fr','home')+body+footer('fr')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source-dir',type=Path);args=parser.parse_args()
 contentdir=ROOT/'moop'/'content';contentdir.mkdir(parents=True,exist_ok=True)
 if args.source_dir:
  for locale in ['fr','en']:
   for kind in ['privacy','support']:
    source=args.source_dir/f'{kind}-{locale}.md'
    if not source.is_file():raise SystemExit('Missing public policy resource: '+str(source))
    (contentdir/source.name).write_text(source.read_text())
 for locale in ['fr','en']:
  path=ROOT/route(locale).lstrip('/')/'index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(landing(locale))
  for kind in ['privacy','support']:
   path=ROOT/route(locale,kind).lstrip('/')/'index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(document(locale,kind,(contentdir/f'{kind}-{locale}.md').read_text()))
 (ROOT/'moop/index.html').write_text(gateway())
 urls=[SITE+'/moop/']+[SITE+route(locale,kind) for locale in ['fr','en'] for kind in ['home','privacy','support']]
 for name in ['sitemap.xml','sitemap-media.xml']:
  path=ROOT/name;text=path.read_text()
  for url in urls:
   if '<loc>'+url+'</loc>' not in text:text=text.replace('</urlset>',f'<url><loc>{url}</loc><lastmod>2026-10-26</lastmod></url>\n</urlset>')
  path.write_text(text)
 print('Prepared 7 MOOP HTML pages, public document copies and sitemap entries. No deployment.')
if __name__=='__main__':main()
