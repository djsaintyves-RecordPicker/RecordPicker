"""Validate only the independent Snory Teller subsite."""
from pathlib import Path
import json
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.h1 = 0;self.canonical=None;self.alternates={};self.language=None;self.direction=None
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="html":self.language=a.get("lang");self.direction=a.get("dir")
        if tag=="link" and a.get("rel")=="canonical":self.canonical=a.get("href")
        if tag=="link" and a.get("rel")=="alternate":self.alternates[a.get("hreflang")]=a.get("href")
        if tag == "script": raise AssertionError("No scripts expected")
        if tag == "h1": self.h1 += 1
        self.links.extend(v for k, v in attrs if k in ("href", "src"))

def audit():
    pages = list((ROOT / "snory-teller").rglob("*.html"))
    manifest=json.loads((ROOT/"data/snory-localization/manifest.json").read_text())
    assert len(pages) == 201 and len(manifest["locales"])==50, "Expected 200 localized Snory Teller pages plus root"
    for path in pages:
        page = Page(); page.feed(path.read_text()); assert page.h1 == 1, path
        if path.parent != ROOT/"snory-teller":
            assert len(page.alternates)==51 and page.canonical in manifest["pages"],path
            assert page.direction==("rtl" if page.language.split("-")[0] in ("ar","he","ur") else "ltr"),path
            assert "ZXBRAND" not in path.read_text(),path
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or link.startswith("#"): continue
            target = ROOT / url.path.lstrip("/") if link.startswith("/") else path.parent / url.path
            assert target.resolve().is_relative_to((ROOT / "snory-teller").resolve()) or url.path.endswith("/apps/") or (target.is_dir() and (target/"index.html").is_file() and len(url.path.strip("/").split("/"))==1) or url.path in {"/", "/fr/", "/apps/", "/fr/apps/", "/physical/about/", "/physical/fr/about/"}, link
            if target.is_dir(): target /= "index.html"
            assert target.is_file(), (path, link)
    print("Snory Teller: 200 localized pages, root and local links validated")

if __name__ == "__main__": audit()
