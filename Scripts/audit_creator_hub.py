"""Validate creator navigation independently of Record Picker release marketing."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.h1 = 0
        self.in_main = False; self.main_links = []; self.descriptions = {}
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'main': self.in_main = True
        if tag == 'h1': self.h1 += 1
        self.links.extend(v for k,v in attrs if k in ('href','src'))
        if tag == 'a' and self.in_main: self.main_links.append(values.get('href',''))
        if tag == 'meta':
            key = values.get('name') or values.get('property')
            if key in ('description','og:description','twitter:description'):
                self.descriptions[key] = values.get('content','')
    def handle_endtag(self, tag):
        if tag == 'main': self.in_main = False
def audit():
    for rel in ('apps/index.html','fr/apps/index.html'):
        p=ROOT/rel; s=p.read_text(); page=Page(); page.feed(s)
        assert page.h1 == 1, rel
        for name in ('Record Picker','Physical Routine','Snory Teller','Dulpi','my_musical_update'):
            assert name in s, (rel,name)
        for link in page.links:
            u=urlsplit(link)
            if u.scheme or link.startswith('#'): continue
            target=ROOT/u.path.lstrip('/')
            if target.is_dir(): target=target/'index.html'
            assert target.is_file(), (rel,link)
    # A published release must not retain the previous review announcement.
    import json
    import re
    old = 'Coming in version 1.0.2:'
    templates = json.loads((ROOT/'data/creator-hub/templates.json').read_text())
    assert old not in templates['en-hub']
    count = 0
    for path in ROOT.glob('**/apps/index.html'):
        markup = path.read_text()
        card = re.search(r'<article[^>]*id="physical-routine"[^>]*>(.*?)</article>', markup, re.S)
        if not card: continue
        notes = re.findall(r'<p class="release-note">(.*?)</p>', card[1], re.S)
        assert len(notes) == 1 and notes[0].strip() and '1.0.4' in card[1] and '1.0.3' not in card[1], path
        assert old not in path.read_text(), path
        assert 'my-physical-routine.mdvnc9v49c.chatgpt.site' not in path.read_text(), path
        count += 1
    assert count == 50, count
    print('Creator hub: 50 current MPR release cards and maintained destinations validated')
    guides = json.loads((ROOT/'data/record-guide-walkthroughs-2026-10-22.json').read_text())['pages']
    assert len(guides) == 300
    for rel in guides:
        page = Page(); page.feed((ROOT/rel).read_text())
        assert any(urlsplit(link).netloc == 'apps.apple.com' for link in page.main_links), (rel,'Missing direct App Store link')
        descriptions = [page.descriptions.get(key,'') for key in ('description','og:description','twitter:description')]
        assert descriptions[0] and len(set(descriptions)) == 1, (rel,'Inconsistent guide descriptions')
        for link in page.main_links:
            url = urlsplit(link)
            if url.scheme or not url.path: continue
            target = ROOT/url.path.lstrip('/')
            if target.is_dir(): target = target/'index.html'
            assert target.is_file(), (rel,link)
    print('Guides: 300 direct store paths, local destinations and SEO/social descriptions validated')
    features = json.loads((ROOT/'data/feature-overview-2026-10-22.json').read_text())['pages']
    assert len(features) == 33
    for rel in features:
        raw = (ROOT/rel).read_text(); page = Page(); page.feed(raw)
        lead = re.search(r'<p class="lead">(.*?)</p>',raw,re.S)
        assert lead and all(name in lead[1] for name in ('Light','Pro')), (rel,'Missing current purchase options')
        assert any(link.endswith('/apps/') for link in page.main_links), (rel,'Missing Studio link')
        for payload in re.findall(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S):
            value = json.loads(payload)
            if value.get('@type') == 'SoftwareApplication':
                assert len(value['inLanguage']) == len(value['availableLanguage']) == 50, rel
    print('Features: 33 current purchase overviews, Studio links and 50 app localizations validated')
if __name__ == '__main__': audit()
