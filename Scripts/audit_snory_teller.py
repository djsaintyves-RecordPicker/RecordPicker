"""Validate only the independent Snory Teller subsite."""
from pathlib import Path
import json
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.h1 = 0;self.canonical=None;self.alternates={};self.language=None;self.direction=None;self.metadata=None;self.schemas=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="html":self.language=a.get("lang");self.direction=a.get("dir")
        if tag=="link" and a.get("rel")=="canonical":self.canonical=a.get("href")
        if tag=="link" and a.get("rel")=="alternate":self.alternates[a.get("hreflang")]=a.get("href")
        if tag == "script":
            assert a.get('type') == 'application/ld+json' and not a.get('src'), 'Executable scripts are not allowed'
            self.metadata=''
        if tag == "h1": self.h1 += 1
        self.links.extend(v for k, v in attrs if k in ("href", "src"))
    def handle_data(self,data):
        if self.metadata is not None:self.metadata+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.metadata is not None:
            value=json.loads(self.metadata)
            assert value.get('@type')=='SoftwareApplication' and value.get('name')=='Snory Teller'
            self.schemas.append(value);self.metadata=None

def audit():
    pages = list((ROOT / "snory-teller").rglob("*.html"))
    manifest=json.loads((ROOT/"data/snory-localization/manifest.json").read_text())
    assert len(pages) == 201 and len(manifest["locales"])==50, "Expected 200 localized Snory Teller pages plus root"
    root_text=(ROOT/'snory-teller/index.html').read_text()
    root_page=Page();root_page.feed(root_text)
    assert all('/snory-teller/'+locale+'/' in root_page.links for locale in manifest['locales'])
    assert 'En développement' not in root_text and 'In development' not in root_text
    for path in pages:
        page = Page(); page.feed(path.read_text()); assert page.h1 == 1, path
        if path.parent != ROOT/"snory-teller":
            assert len(page.alternates)==51 and page.canonical in manifest["pages"],path
            assert page.direction==("rtl" if page.language.split("-")[0] in ("ar","he","ur") else "ltr"),path
            assert "ZXBRAND" not in path.read_text(),path
            if path.parent.parent == ROOT/'snory-teller':
                assert len(page.schemas)==1,path
                assert page.schemas[0]['url']==page.canonical and page.schemas[0]['inLanguage']==page.language,path
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or link.startswith("#"): continue
            target = ROOT / url.path.lstrip("/") if link.startswith("/") else path.parent / url.path
            assert target.resolve().is_relative_to((ROOT / "snory-teller").resolve()) or url.path.endswith(("/snory-teller-guide/", "/physical-routine-guide/")) or url.path == "/apps/assets/appstore.svg" or url.path.endswith("/apps/") or (target.is_dir() and (target/"index.html").is_file() and len(url.path.strip("/").split("/"))==1) or url.path in {"/", "/fr/", "/apps/", "/fr/apps/", "/physical/about/", "/physical/fr/about/"}, link
            if target.is_dir(): target /= "index.html"
            assert target.is_file(), (path, link)
    print("Snory Teller: 200 localized pages, root and local links validated")

if __name__ == "__main__": audit()
