"""Keep shared previews attached to the page's actual app or playlist."""
import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from site_campaign_links import normalize as normalize_campaign_links

ROOT = Path(__file__).resolve().parents[1]
IMAGES = {
    'hub': ('/assets/brand/rps/icon-512.png', 'Record Picker Studio'),
    'dulpi': ('/apps/assets/dulpi-icon.png', 'Dulpi'),
    'music': ('/apps/assets/october-mess-s05e02.webp', 'My Musical Update'),
    's05e01': ('/apps/assets/september-desires-s05e01.webp', 'My Musical Update'),
    's05e02': ('/apps/assets/october-mess-s05e02.webp', 'My Musical Update'),
    'snory-guide': ('/snory-teller/icon.png', 'Snory Teller'),
    'physical-guide': ('/physical/icon.png', 'My Physical Routine'),
}
for kind in ('record-guide', 'discogs', 'backup', 'rediscover', 'choose'):
    IMAGES[kind] = ('/assets/brand/icon-512.png', 'Record Picker')

class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ''; self.in_title = False; self.meta = {}; self.canonical = ''
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title': self.in_title = True
        if tag == 'meta': self.meta[a.get('property') or a.get('name')] = a.get('content', '')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href', '')
    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
    def handle_data(self, data):
        if self.in_title: self.title += data

def normalize(raw, kind):
    head = Head(); head.feed(raw.split('</head>', 1)[0])
    assert head.title and head.canonical, kind
    image, alt = IMAGES[kind]
    values = {
        'og:type': head.meta.get('og:type', 'website'),
        'og:title': head.title, 'og:description': head.meta['description'],
        'og:url': head.canonical, 'og:site_name': 'Record Picker Studio',
        'og:image': 'https://recordpicker.app'+image, 'og:image:alt': alt,
        'twitter:card': 'summary', 'twitter:title': head.title,
        'twitter:description': head.meta['description'],
        'twitter:image': 'https://recordpicker.app'+image, 'twitter:image:alt': alt,
    }
    for key, value in values.items():
        attr = 'property' if key.startswith('og:') else 'name'
        tag = '<meta '+attr+'="'+key+'" content="'+escape(value, quote=True)+'">'
        pattern = r'<meta\b(?=[^>]*(?:property|name)="'+re.escape(key)+r'")[^>]*>'
        if re.search(pattern, raw):
            count = [0]
            def replacement(match):
                count[0] += 1
                return tag if count[0] == 1 else ''
            raw = re.sub(pattern, replacement, raw)
        else:
            raw = raw.replace('</head>', tag+'</head>', 1)
    return normalize_campaign_links(raw)

def pages():
    routes = json.loads((ROOT/'data/creator-hub/routes.json').read_text())
    manifest = json.loads((ROOT/'data/creator-hub/manifest.json').read_text())
    for url in manifest['pages']:
        route = urlsplit(url).path
        kinds = [kind for kind, suffix in routes.items() if route.endswith('/'+suffix)]
        assert len(kinds) == 1, url
        yield ROOT/route.lstrip('/')/'index.html', kinds[0]
    for path in (ROOT/'physical').rglob('*.html'):
        yield path, 'physical-guide'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    failures = []; count = 0
    for path, kind in pages():
        image, alt = IMAGES[kind]
        assert (ROOT/image.lstrip('/')).is_file(), image
        raw = path.read_text(); expected = normalize(raw, kind)
        if expected != raw:
            if args.write: path.write_text(expected)
            else: failures.append(str(path.relative_to(ROOT)))
        count += 1
    if args.write:
        path = ROOT/'data/creator-hub/templates.json'
        templates = json.loads(path.read_text())
        for key in templates:
            kind = key.split('-', 1)[1]
            templates[key] = normalize(templates[key], kind)
        path.write_text(json.dumps(templates, ensure_ascii=False, indent=2)+'\n')
    if failures: raise SystemExit('Inconsistent preview identity: '+', '.join(failures))
    print(f'Social preview identity checked on {count} pages; official assets exist')

if __name__ == '__main__': main()
