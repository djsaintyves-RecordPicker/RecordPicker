"""Maintain the neutral language entry page for the released Snory Teller app."""
from html import escape
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def markup():
 from localize_creator_hub import LOCALES,NAMES
 links=''.join('<a href="/snory-teller/'+locale+'/" lang="'+locale+'" dir="auto">'+escape(name)+'</a>' for locale,name in zip(LOCALES,NAMES))
 return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Snory Teller — Languages / Langues</title><meta name="description" content="Snory Teller for iPhone and Apple Watch. Choose one of 50 localizations to explore the app, night reports, optional alerts, support and privacy information."><link rel="stylesheet" href="/snory-teller/styles.css"><link rel="canonical" href="https://recordpicker.app/snory-teller/"><meta property="og:title" content="Snory Teller — Languages / Langues"><meta property="og:description" content="Choose your language · Choisissez votre langue"><meta property="og:image" content="https://recordpicker.app/snory-teller/icon.png"><meta property="og:url" content="https://recordpicker.app/snory-teller/"></head><body class="landing"><a class="skip" href="#content">Skip to content / Aller au contenu</a><header><img class="icon" src="/snory-teller/icon.png" alt="Snory Teller" width="64" height="64"><span class="brand">Snory Teller</span><nav aria-label="Record Picker Studio"><a href="/fr/apps/" lang="fr">Studio · Français</a><a href="/apps/" lang="en">Studio · English</a></nav></header><main id="content"><h1>Snory Teller</h1><p class="status">1.0.2 · iPhone · Apple Watch</p><p lang="fr">Suivez les sons de vos nuits, consultez les ronflements estimés et vos bilans. Choisissez votre langue pour découvrir le fonctionnement, les conditions d’utilisation et les limites de l’app.</p><p lang="en">Explore estimated snoring and night reports. Choose your language to read how the app works, its terms and its limitations.</p><p><a class="cta" href="https://apps.apple.com/app/snory-teller/id6820177689?pt=129016722&amp;ct=ST_Website&amp;mt=8">App Store</a></p><section class="offer"><h2>Choose your language / Choisissez votre langue</h2><nav aria-label="Languages / Langues">'''+links+'''</nav></section></main><footer>© 2026 Yves Durand · Record Picker Studio</footer></body></html>
'''

def main():
 (ROOT/'snory-teller/index.html').write_text(markup())
 print('Snory Teller language portal updated: released app and 50 choices')

if __name__=='__main__':main()
