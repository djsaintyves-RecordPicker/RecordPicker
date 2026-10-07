"""Validate the separate Physical support subsite."""
from pathlib import Path
import re
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]
def audit():
    pages = sorted((ROOT / "physical").rglob("*.html"))
    assert len(pages) == 6, "Physical needs three pages in two languages"
    for page in pages:
        text = page.read_text()
        route = "/" + str(page.relative_to(ROOT).parent) + "/"
        assert f'<link rel="canonical" href="https://recordpicker.app{route}">' in text
        assert 'mailto:support@recordpicker.app?subject=Physical' in text
        assert '<meta name="viewport"' in text and 'prefers-color-scheme' in (ROOT / "physical/styles.css").read_text()
        assert '<main id="main">' in text and '<h1>' in text
        assert 'hreflang="fr"' in text and 'hreflang="en"' in text
        assert '<script' not in text and 'Brouillon' not in text
        for url in re.findall(r'(?:href|src)="([^"]+)"', text):
            parsed = urlsplit(url)
            if parsed.scheme or not parsed.path: continue
            path = ROOT / parsed.path.lstrip("/")
            if parsed.path.endswith("/"): path = path / "index.html"
            assert path.exists(), f"Missing link: {url}"
    print("Physical: six bilingual pages and local links verified")
if __name__ == "__main__": audit()
