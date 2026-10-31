"""Maintain bilingual discovery metadata for Meal Picker's public help pages."""
import argparse
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://recordpicker.app'
DESCRIPTIONS = {
 ('support', 'fr-FR'): 'Aide Meal Picker pour iPhone, iPad et Mac : recettes, menus, liste de courses, partage de fiches, synchronisation iCloud et contact assistance.',
 ('support', 'en-GB'): 'Meal Picker help for iPhone, iPad and Mac: recipes, menus, shopping lists, recipe sharing, iCloud synchronisation and support contact details.',
 ('privacy', 'fr-FR'): 'Confidentialité Meal Picker : stockage des recettes, synchronisation iCloud, autorisations, partage de fiches et gestion de vos données personnelles.',
 ('privacy', 'en-GB'): 'Meal Picker privacy information: recipe storage, iCloud synchronisation, permissions, recipe sharing and management of your personal data.',
}

def expected(kind, locale):
 fr = locale == 'fr-FR'
 url = f'{SITE}/meal-picker/{kind}-{locale}.html'
 title = ('Assistance et recettes' if kind == 'support' else 'Confidentialité et données') if fr else ('Help and recipes' if kind == 'support' else 'Privacy and data')
 title += ' — Meal Picker'
 desc = DESCRIPTIONS[kind, locale]
 links = ''.join(f'<link rel="alternate" hreflang="{lang}" href="{SITE}/meal-picker/{kind}-{lang}.html">' for lang in ('fr-FR', 'en-GB'))
 links += f'<link rel="alternate" hreflang="x-default" href="{SITE}/meal-picker/{kind}-en-GB.html">'
 payload = {'@context': 'https://schema.org', '@type': 'WebPage', '@id': url, 'url': url, 'name': title, 'description': desc, 'inLanguage': locale, 'isPartOf': {'@type': 'WebSite', 'name': 'Record Picker Studio', 'url': SITE + ('/fr/apps/' if fr else '/apps/')}}
 tags = f'<meta name="description" content="{escape(desc, quote=True)}"><link rel="canonical" href="{url}">' + links
 for prop, value in [('og:type','website'), ('og:title',title), ('og:description',desc), ('og:url',url), ('og:site_name','Record Picker Studio'), ('og:image',SITE+'/apps/assets/meal-picker-icon.png')]:
  tags += f'<meta property="{prop}" content="{escape(value, quote=True)}">'
 tags += '<meta name="twitter:card" content="summary">'
 tags += '<script type="application/ld+json" data-meal-discovery>'+json.dumps(payload, ensure_ascii=False, separators=(',', ':'))+'</script>'
 return title, '<!-- meal-discovery:start -->'+tags+'<!-- meal-discovery:end -->'

def main():
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--write', action='store_true')
 args = parser.parse_args()
 errors = []
 for kind, locale in DESCRIPTIONS:
  path = ROOT / 'meal-picker' / f'{kind}-{locale}.html'
  before = path.read_text(); after = before
  title, metadata = expected(kind, locale)
  after = re.sub(r'<title>.*?</title>', '<title>'+title+'</title>', after, count=1)
  after = re.sub(r'<!-- meal-discovery:start -->.*?<!-- meal-discovery:end -->', '', after, flags=re.S)
  common_css = re.search(r'<link[^>]*href="/assets/css/suite-experience\.css[^"]*"[^>]*>', after)
  if common_css:
   after = after[:common_css.start()] + metadata + after[common_css.start():]
  else:
   after = after.replace('</head>', metadata+'</head>', 1)
  studio = '/fr/apps/#meal-picker' if locale == 'fr-FR' else '/apps/#meal-picker'
  link = f'<a data-meal-studio href="{studio}">Record Picker Studio</a>'
  after = re.sub(r'<a data-meal-studio[^>]*>.*?</a>', '', after)
  after = after.replace('</nav>', link+'</nav>', 1)
  if after != before:
   if args.write: path.write_text(after)
   else: errors.append(str(path.relative_to(ROOT)))
 for rel, locale, label in [('fr/apps/index.html','fr-FR','Assistance et informations de confidentialité'), ('apps/index.html','en-GB','Help and privacy information')]:
  path = ROOT/rel; before = path.read_text()
  link = f'<a class="project-detail-link" data-meal-help href="/meal-picker/support-{locale}.html">{label} →</a>'
  existing = re.search(r'<a[^>]*data-meal-help[^>]*>.*?</a>', before, re.S)
  if existing:
   # Preserve the store button's position when refreshing the help link.
   after = before[:existing.start()] + link + before[existing.end():]
  else:
   after, count = re.subn(r'(<article[^>]*id="meal-picker".*?<div class="project-card-actions">)', lambda m: m[1]+link, before, count=1, flags=re.S)
   if count != 1: raise SystemExit('Meal Picker card missing: '+rel)
  if after != before:
   if args.write: path.write_text(after)
   else: errors.append(rel)
 sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{SITE}/meal-picker/{kind}-{locale}.html</loc></url>\n' for kind, locale in DESCRIPTIONS)+'</urlset>\n'
 target = ROOT/'sitemap-meal-picker.xml'
 if not target.exists() or target.read_text() != sitemap:
  if args.write: target.write_text(sitemap)
  else: errors.append(target.name)
 robots = ROOT/'robots.txt'; before = robots.read_text(); line = f'Sitemap: {SITE}/sitemap-meal-picker.xml'
 if line not in before:
  if args.write: robots.write_text(before.rstrip()+'\n'+line+'\n')
  else: errors.append('robots.txt')
 if errors: raise SystemExit('Meal Picker discovery metadata differs: '+', '.join(errors))
 print('OK: four bilingual Meal Picker help pages, canonical/language metadata and sitemap.')

if __name__ == '__main__': main()
