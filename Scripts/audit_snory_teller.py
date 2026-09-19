"""Validate only the independent Snory Teller subsite."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.h1 = 0
    def handle_starttag(self, tag, attrs):
        if tag == "script": raise AssertionError("No scripts expected")
        if tag == "h1": self.h1 += 1
        self.links.extend(v for k, v in attrs if k in ("href", "src"))

def audit():
    pages = list((ROOT / "snory-teller").rglob("*.html"))
    assert len(pages) == 9, "Expected nine Snory Teller pages"
    for path in pages:
        page = Page(); page.feed(path.read_text()); assert page.h1 == 1, path
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or link.startswith("#"): continue
            target = ROOT / url.path.lstrip("/") if link.startswith("/") else path.parent / url.path
            assert target.resolve().is_relative_to((ROOT / "snory-teller").resolve()), link
            if target.is_dir(): target /= "index.html"
            assert target.is_file(), (path, link)
    print("Snory Teller: nine standalone pages and local links validated")

if __name__ == "__main__": audit()
