"""Validate creator navigation independently of Record Picker release marketing."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.h1 = 0
    def handle_starttag(self, tag, attrs):
        if tag == 'h1': self.h1 += 1
        self.links.extend(v for k,v in attrs if k in ('href','src'))
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
    from lxml import html
    old = 'Coming in version 1.0.2:'
    templates = json.loads((ROOT/'data/creator-hub/templates.json').read_text())
    assert old not in templates['en-hub']
    count = 0
    for path in ROOT.glob('**/apps/index.html'):
        doc = html.fromstring(path.read_text())
        cards = doc.xpath('//*[@id="physical-routine"]')
        if not cards: continue
        card = cards[0]
        note = card.xpath('.//*[contains(@class,"release-note")]')
        assert len(note) == 1 and '1.0.2' in note[0].text_content(), path
        assert old not in path.read_text(), path
        assert 'my-physical-routine.mdvnc9v49c.chatgpt.site' not in path.read_text(), path
        count += 1
    assert count == 50, count
    print('Creator hub: 50 current MPR release cards and maintained destinations validated')
if __name__ == '__main__': audit()
