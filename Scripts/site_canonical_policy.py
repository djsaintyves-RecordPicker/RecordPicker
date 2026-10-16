#!/usr/bin/env python3
"""Keep regional duplicate signals consistent without removing localized pages."""
from __future__ import annotations

import argparse
from datetime import date
from html import escape, unescape
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://recordpicker.app'
LOCALES = {
    'ar': 'ar', 'ca': 'ca', 'da': 'da', 'de': 'de', 'el': 'el',
    'en-au': 'en-AU', 'en-ca': 'en-CA', 'en-gb': 'en-GB', 'en-us': 'en-US',
    'es-es': 'es-ES', 'es-mx': 'es-MX', 'fi': 'fi', 'fr': 'fr-FR',
    'fr-ca': 'fr-CA', 'he': 'he', 'hi': 'hi', 'id': 'id', 'it': 'it',
    'ja': 'ja', 'ko': 'ko', 'nb': 'nb', 'nl': 'nl', 'pl': 'pl',
    'pt-br': 'pt-BR', 'pt-pt': 'pt-PT', 'ru': 'ru', 'sv': 'sv',
    'th': 'th', 'tr': 'tr', 'vi': 'vi', 'zh-hans': 'zh-Hans', 'zh-hant': 'zh-Hant',
}
STANDARD_ROUTES = {
    '', 'choose-vinyl-record', 'random-vinyl-record-picker', 'manage-vinyl-collection',
    'support', 'privacy', 'readme', 'screenshots', 'mac-app', 'ios-app',
    'watch-app', 'android-app', 'windows-app',
}
# These informational pages have substantially the same content in each region.
# Market homepages and distinct English Mac/Watch pages keep their own canonical.
DUPLICATE_INFORMATION_ROUTES = {
    'choose-vinyl-record', 'random-vinyl-record-picker', 'manage-vinyl-collection',
    'support', 'privacy', 'readme', 'screenshots',
}
CANONICAL = re.compile(r'<link rel="canonical" href="([^"]+)">')
ALTERNATE = re.compile(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">')
ANCHOR_HREF = re.compile(r'(<a\b[^>]*?\shref\s*=\s*)([\"\'])(.*?)(\2)', re.I)
MAC_ALIAS_PATHS = {'/en-us/mac-app', '/en-us/mac-app/', '/en-us/mac-app/index.html'}
MAC_REDIRECT = ('<meta http-equiv="refresh" content="0;url=/mac-app/">'
                '<script data-canonical-mac-redirect>'
                'window.location.replace("/mac-app/" + window.location.search + window.location.hash);'
                '</script>')


def normalize_mac_links(text: str, page_url: str) -> str:
    """Resolve relative navigation before consolidating the US Mac alias."""
    def replace(match: re.Match[str]) -> str:
        href = unescape(match.group(3))
        # In-page navigation, especially the accessibility skip link, stays local.
        if href.startswith('#'):
            return match.group(0)
        target = urlsplit(urljoin(page_url, href))
        if target.scheme not in {'http', 'https'} or target.netloc != 'recordpicker.app' or target.path not in MAC_ALIAS_PATHS:
            return match.group(0)
        canonical = urlunsplit(('', '', '/mac-app/', target.query, target.fragment))
        return match.group(1) + match.group(2) + escape(canonical, quote=True) + match.group(4)
    return ANCHOR_HREF.sub(replace, text)


def identity(path: Path, root: Path = ROOT) -> tuple[str, str]:
    parts = path.relative_to(root).parts[:-1]
    locale = parts[0] if parts and parts[0] in LOCALES else ''
    route = '/'.join(parts[1:] if locale else parts)
    return locale, route


def public_url(locale: str, route: str) -> str:
    return SITE + '/' + '/'.join(part for part in (locale, route) if part) + ('/' if locale or route else '')


def canonical_for(path: Path, root: Path = ROOT) -> str:
    locale, route = identity(path, root)
    counterpart_locale = locale
    if locale == 'en-us' or (locale in {'en-au', 'en-ca', 'en-gb'} and route in DUPLICATE_INFORMATION_ROUTES):
        counterpart_locale = ''
    elif locale == 'fr-ca' and route in DUPLICATE_INFORMATION_ROUTES | {'mac-app'}:
        counterpart_locale = 'fr'
    counterpart = root / counterpart_locale / route / 'index.html'
    if not counterpart.exists():
        counterpart_locale = locale
    return public_url(counterpart_locale, route)


def alternate_urls(route: str, root: Path = ROOT) -> dict[str, str]:
    # Canonical consolidation and regional hreflang work together (Google's
    # multi-regional guidance). Keep regional destinations and reciprocal links.
    result = {language: public_url('' if locale == 'en-us' else locale, route)
              for locale, language in LOCALES.items()
              if (root / locale / route / 'index.html').exists()}
    for language, locale in {'fr-CH': 'fr', 'de-CH': 'de', 'it-CH': 'it', 'en-CH': 'en-gb'}.items():
        if (root / locale / route / 'index.html').exists():
            result[language] = public_url(locale, route)
    if (root / route / 'index.html').exists():
        result['x-default'] = public_url('', route)
    return result


def normalize_page(path: Path, root: Path = ROOT) -> str:
    text = path.read_text(encoding='utf-8')
    found = CANONICAL.search(text)
    if not found:
        return text
    old = found.group(1)
    canonical = canonical_for(path, root)
    text = CANONICAL.sub(f'<link rel="canonical" href="{canonical}">', text, count=1)
    text = re.sub(r'<meta property="og:url" content="[^"]+">',
                  f'<meta property="og:url" content="{canonical}">', text, count=1)
    if old != canonical:
        def structured(match: re.Match[str]) -> str:
            payload = json.loads(match.group(1))
            def walk(value):
                if isinstance(value, dict):
                    return {key: (canonical + item[len(old):]
                                  if key in {'url', '@id', 'mainEntityOfPage', 'item'}
                                  and isinstance(item, str) and (item == old or item.startswith(old + '#'))
                                  else walk(item)) for key, item in value.items()}
                if isinstance(value, list):
                    return [walk(item) for item in value]
                return value
            updated = walk(payload)
            return match.group(0) if updated == payload else '<script type="application/ld+json">' + json.dumps(updated, ensure_ascii=False, separators=(',', ':')) + '</script>'
        text = re.sub(r'<script type="application/ld\+json">(.*?)</script>', structured, text, flags=re.S)
    locale, route = identity(path, root)
    text = normalize_mac_links(text, public_url(locale, route))
    if (locale, route) == ('en-us', 'mac-app') and MAC_REDIRECT not in text:
        # GitHub Pages has no per-route HTTP redirect configuration. An instant
        # refresh supplies a permanent consolidation signal even without JS;
        # location.replace also preserves campaign parameters and deep links.
        canonical_tag = f'<link rel="canonical" href="{canonical}">'
        text = text.replace(canonical_tag, canonical_tag + MAC_REDIRECT, 1)
    if route in STANDARD_ROUTES:
        expected = alternate_urls(route, root)
        actual = dict(ALTERNATE.findall(text))
        if actual != expected or len(ALTERNATE.findall(text)) != len(expected):
            # Preserve the established order while adding any missing language.
            ordered = dict.fromkeys([*actual, *expected])
            links = ''.join(f'<link rel="alternate" hreflang="{lang}" href="{expected[lang]}">' for lang in ordered if lang in expected)
            text = ALTERNATE.sub('', text)
            text = text.replace('</head>', links + '</head>', 1)
    return text


def public_pages(root: Path = ROOT) -> list[Path]:
    return sorted(path for path in root.rglob('index.html')
                  if not any(part.startswith('.') for part in path.relative_to(root).parts)
                  and '<main' in path.read_text(encoding='utf-8')
                  and CANONICAL.search(path.read_text(encoding='utf-8'))
                  and 'snory-teller' not in path.relative_to(root).parts)


def normalize_sitemap(path: Path, allowed: set[str], changed: set[str], modified: str) -> str:
    text = path.read_text(encoding='utf-8')
    blocks = re.findall(r'<url>.*?</url>', text, re.S)
    retained = []
    seen = set()
    for block in blocks:
        found = re.search(r'<loc>([^<]+)</loc>', block)
        if not found:
            raise ValueError(f'{path}: URL block without loc')
        url = found.group(1)
        if url not in allowed or url in seen:
            continue
        seen.add(url)
        if url in changed:
            block = re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{modified}</lastmod>', block)
        retained.append(block)
    missing = allowed - seen
    if missing:
        raise ValueError(f'{path}: missing canonical entries: {sorted(missing)}')
    return text[:text.index('<url>')].rstrip() + '\n' + '\n'.join(retained) + '\n</urlset>\n'


def audit(root: Path = ROOT) -> list[str]:
    errors = []
    canonical_urls = set()
    for path in public_pages(root):
        text = path.read_text(encoding='utf-8')
        if normalize_page(path, root) != text:
            errors.append(f'{path.relative_to(root)}: inconsistent canonical, og:url, or reciprocal hreflang')
        url = CANONICAL.search(text).group(1)
        canonical_urls.add(url)
        target = root / url.removeprefix(SITE + '/') / 'index.html'
        target_canonical = CANONICAL.search(target.read_text(encoding='utf-8')) if target.exists() else None
        if not target_canonical or target_canonical.group(1) != url:
            errors.append(f'{path.relative_to(root)}: missing or non-self-canonical target {url}')
    for name in ('sitemap.xml', 'sitemap-media.xml'):
        urls = re.findall(r'<loc>([^<]+)</loc>', (root / name).read_text(encoding='utf-8'))
        if set(urls) != canonical_urls or len(urls) != len(set(urls)):
            errors.append(f'{name}: must contain each canonical exactly once, without duplicate regional aliases')
    return errors


def write(root: Path = ROOT) -> tuple[int, int]:
    # Prepare and validate all output before changing any file.
    updates = {path: normalize_page(path, root) for path in public_pages(root)}
    changed = {CANONICAL.search(after).group(1) for path, after in updates.items()
               if path.read_text(encoding='utf-8') != after
               and public_url(*identity(path, root)) == CANONICAL.search(after).group(1)}
    allowed = {CANONICAL.search(after).group(1) for after in updates.values()}
    count = sum(path.read_text(encoding='utf-8') != after for path, after in updates.items())
    for name in ('sitemap.xml', 'sitemap-media.xml'):
        path = root / name
        updates[path] = normalize_sitemap(path, allowed, changed, date.today().isoformat())
    for path, after in updates.items():
        if path.read_text(encoding='utf-8') != after:
            path.write_text(after, encoding='utf-8')
    return count, len(allowed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Apply metadata and sitemap corrections')
    args = parser.parse_args()
    if args.write:
        count, canonical_count = write()
        print(f'Updated {count} pages; {canonical_count} canonical URLs in each sitemap.')
    errors = audit()
    if errors:
        raise SystemExit('\n'.join(errors))
    print('OK: canonical targets, reciprocal regional hreflang, and both sitemaps agree.')


if __name__ == '__main__':
    main()
