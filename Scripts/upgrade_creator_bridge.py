"""Replace passive creator cards on Record Picker pages with a useful studio bridge."""
from pathlib import Path
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
FR = {
    "eyebrow": "RECORD PICKER STUDIO", "title": "Trois apps, un même studio",
    "intro": "Record Picker fait partie de Record Picker Studio, avec Snory Teller et My Physical Routine. Découvrez les autres projets, puis revenez à votre collection quand vous en avez envie.",
    "rp_text": "Votre collection de vinyles et CD, pour retrouver quoi écouter.", "rp_action": "Voir Record Picker",
    "snory_text": "Un résumé estimé de vos nuits sur iPhone et Apple Watch.", "snory_action": "Découvrir Snory Teller",
    "routine_text": "Des séances de renforcement guidées, à votre rythme.", "routine_action": "Découvrir My Physical Routine",
    "all": "Explorer toutes les apps du studio",
}
EN = {
    "eyebrow": "RECORD PICKER STUDIO", "title": "Three apps, one studio",
    "intro": "Record Picker is part of Record Picker Studio, alongside Snory Teller and My Physical Routine. Explore the other projects, then return to your collection whenever you like.",
    "rp_text": "Your vinyl and CD collection, made to help you choose what to play.", "rp_action": "Explore Record Picker",
    "snory_text": "An estimated night summary on iPhone and Apple Watch.", "snory_action": "Explore Snory Teller",
    "routine_text": "Guided home strength sessions, at your own pace.", "routine_action": "Explore My Physical Routine",
    "all": "Explore every studio app",
}

def bridge(copy, french):
    apps, rp = ("/fr/apps/", "/fr/#top") if french else ("/apps/", "/#top")
    section = html.Element("section", {"class": "section studio-bridge", "data-creator-discovery": ""})
    head = etree.SubElement(section, "div", {"class": "studio-bridge-head"})
    etree.SubElement(head, "p", {"class": "kicker"}).text = copy["eyebrow"]
    etree.SubElement(head, "h2").text = copy["title"]
    etree.SubElement(head, "p", {"class": "lead"}).text = copy["intro"]
    cards = etree.SubElement(section, "div", {"class": "studio-bridge-grid"})
    entries = [
        ("Record Picker", copy["rp_text"], copy["rp_action"], rp, "/assets/brand/icon-192.png"),
        ("Snory Teller", copy["snory_text"], copy["snory_action"], f"/snory-teller/{'fr-FR' if french else 'en-US'}/", "/snory-teller/icon.png"),
        ("My Physical Routine", copy["routine_text"], copy["routine_action"], "/physical/fr/about/" if french else "/physical/about/", "/physical/icon.png"),
    ]
    for name, description, action, href, icon in entries:
        card = etree.SubElement(cards, "article", {"class": "studio-bridge-card"})
        etree.SubElement(card, "img", {"src": icon, "alt": "", "width": "88", "height": "88", "loading": "lazy"})
        body = etree.SubElement(card, "div")
        etree.SubElement(body, "h3").text = name
        etree.SubElement(body, "p").text = description
        etree.SubElement(body, "a", {"class": "button glass", "href": href}).text = action
    actions = etree.SubElement(section, "div", {"class": "studio-bridge-actions"})
    etree.SubElement(actions, "a", {"class": "button primary", "href": apps}).text = copy["all"]
    return section


def main():
    import argparse
    import concurrent.futures
    import json
    import re
    import localize_creator_hub as locales
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true', help='Translate missing studio copy before publishing localized blocks')
    args = parser.parse_args()
    pages = json.loads((ROOT/'data/guide-discovery-2026-10-22.json').read_text())['pages']
    languages = {locales.language(p['guide_locale']) for p in pages} - {'en', 'fr'}
    def cache_for(lang):
        path = ROOT/'data/creator-hub'/f'{lang}.json'
        cache = json.loads(path.read_text())
        missing = list(dict.fromkeys(value for key,value in EN.items() if key != 'eyebrow' and value not in cache))
        if missing:
            if not args.refresh:
                raise ValueError(f'{lang}: missing studio translations; use --refresh')
            cache.update(locales.translate_batch(lang, list(enumerate(missing))))
            path.write_text(json.dumps(cache, ensure_ascii=False, indent=2)+'\n')
        return lang, cache
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        caches = dict(executor.map(cache_for, sorted(languages)))
    result = []
    for record in pages:
        page = ROOT/record['page']; locale = record['guide_locale']; lang = locales.language(locale)
        copy = FR if lang == 'fr' else EN if lang == 'en' else {key: value if key == 'eyebrow' else caches[lang][value] for key,value in EN.items()}
        markup = html.tostring(bridge(copy, lang == 'fr'), encoding='unicode', method='html')
        prefix = locales.prefix(locale)
        home = '/' if record['page'] == 'index.html' else '/'+str(Path(record['page']).parent)+'/'
        base = '/fr/' if lang == 'fr' else '/'
        destinations = {
            base+'apps/': '/'+prefix+'apps/',
            base+'#top': home+'#top',
            '/snory-teller/'+('fr-FR' if lang == 'fr' else 'en-US')+'/': '/snory-teller/'+locale+'/',
        }
        if lang not in ('en', 'fr'):
            destinations['/physical/about/'] = '/'+prefix+'physical-routine-guide/'
        for old,new in destinations.items():
            markup = markup.replace('href="'+old+'"', 'href="'+new+'"')
        raw = page.read_text()
        updated, count = re.subn(r'<section\b(?=[^>]*data-creator-discovery)[^>]*>.*?</section>', lambda _:markup, raw, flags=re.S)
        if count != 1:
            raise ValueError(f'{page}: expected one creator section, found {count}')
        if updated != raw: page.write_text(updated)
        result.append({'page':record['page'], 'locale':locale, 'routine_destination':destinations.get('/physical/about/', '/physical/fr/about/' if lang == 'fr' else '/physical/about/')})
    platform_pages = []
    for record in pages:
        home = Path(record['page'])
        directory = home.parent
        destination = '/'+locales.prefix(record['guide_locale'])+'apps/'
        for platform in ('ios-app', 'mac-app', 'watch-app', 'windows-app'):
            page = ROOT/directory/platform/'index.html'
            if not page.exists(): continue
            raw = page.read_text()
            if re.search(r'<meta[^>]*name="robots"[^>]*content="[^"<>]*noindex', raw): continue
            footer = re.search(r'<footer\b.*?</footer>', raw, re.S)
            if not footer: raise ValueError(f'{page}: missing footer')
            if 'href="'+destination+'"' not in footer[0]:
                content, count = re.subn(r'</nav>', '<a href="'+destination+'">Record Picker Studio</a></nav>', footer[0], count=1)
                if count != 1: raise ValueError(f'{page}: missing footer navigation')
                page.write_text(raw[:footer.start()]+content+raw[footer.end():])
            platform_pages.append(str(page.relative_to(ROOT)))
    (ROOT/'data/studio-discovery-2026-10-22.json').write_text(json.dumps({'pages':result,'platform_pages':platform_pages,'scope':'Three genuine app icons, localized copy and local studio/Snory destinations; localized MPR guide when no localized MPR product page exists.'}, ensure_ascii=False, indent=2)+'\n')
    print(f'Studio bridge checked on {len(result)} localized homepages')

if __name__ == '__main__':
    main()
