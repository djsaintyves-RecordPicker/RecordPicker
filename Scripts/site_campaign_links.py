"""Keep store campaign links complete, including when JavaScript is disabled."""
from __future__ import annotations

import argparse
from html import escape, unescape
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
APP_PREFIXES = {'6780422305': 'RP', '6820177689': 'ST', '6820104318': 'MPR'}
SCRIPT = '<script defer src="/apps/campaign-links.js?v=20261018"></script>'
ANCHOR = re.compile(r'<a\b[^>]*>', re.I)
HREF = re.compile(r'\bhref=("[^"]*"|\x27[^\x27]*\x27)', re.I)


def decorate(href: str) -> str:
    url = urlsplit(href)
    if url.scheme != 'https':
        return href
    query = dict(parse_qsl(url.query, keep_blank_values=True))
    match = re.search(r'/id(\d+)(?:/|$)', url.path)
    prefix = APP_PREFIXES.get(match[1]) if match else None
    if url.hostname == 'apps.apple.com' and prefix:
        query.update(pt='129016722', ct=prefix + '_Website', mt='8')
    elif url.hostname == 'apps.microsoft.com' and re.search(r'/9N2ZWRL4M3JC/?$', url.path, re.I):
        query['cid'] = 'RP_Website'
    else:
        return href
    return urlunsplit(url._replace(query=urlencode(query)))


def market_token(text: str) -> str | None:
    language = re.search(r'<html\b[^>]*\blang=["\x27](ja|ko)["\x27]', text, re.I)
    if language is None:
        return None
    return {"ja": "JP", "ko": "KR"}[language.group(1).lower()]


def normalize(text: str) -> str:
    def anchor(match):
        tag = match[0]
        href = HREF.search(tag)
        if not href:
            return tag
        original = unescape(href[1][1:-1])
        updated = decorate(original)
        if updated == original:
            return tag
        return tag[:href.start(1)] + '"' + escape(updated, quote=True) + '"' + tag[href.end(1):]
    text = ANCHOR.sub(anchor, text)
    text = text.replace('site.js?v=20261008-free-light-pro', 'site.js?v=20261018-campaigns')
    text = text.replace('site.js?v=20261018-campaigns"', 'site.js?v=20261018-campaigns-2"')
    # Independent support/product subsites keep static website attribution.
    # A local visual enhancement alone must not add the campaign runtime.
    text = text.replace(SCRIPT, '')
    executable = re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>', '', text, flags=re.I | re.S)
    executable = re.sub(r'''<script\b[^>]*src=["']/assets/js/suite-experience\.js(?:\?[^"']*)?["'][^>]*>\s*</script>''', '', executable, flags=re.I | re.S)
    # Language-only MPR routing does not require the campaign runtime.
    executable = re.sub(r'''<script\b[^>]*src=["']/physical/locale\.js(?:\?[^"']*)?["'][^>]*>\s*</script>''', '', executable, flags=re.I | re.S)
    if re.search(r'<script\b', executable, re.I):
        text = text.replace('</head>', SCRIPT + '</head>', 1)
    market = market_token(text)
    if market:
        text = text.replace('ct=RP_Website', f'ct=RP_Website_{market}')
        text = text.replace('cid=RP_Website', f'cid=RP_Website_{market}')
    return text


def pages(root=ROOT):
    for page in root.rglob('*.html'):
        if any(part.startswith('.') or part in {'Archives', 'node_modules', 'outputs'} for part in page.relative_to(root).parts):
            continue
        if '<head' in page.read_text(encoding='utf-8'):
            yield page


def audit(root=ROOT):
    return [f'{p.relative_to(root)}: missing or inconsistent store campaign links'
            for p in pages(root) if normalize(p.read_text(encoding='utf-8')) != p.read_text(encoding='utf-8')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    changed = 0
    if args.write:
        for page in pages():
            before = page.read_text(encoding='utf-8')
            after = normalize(before)
            if after != before:
                page.write_text(after, encoding='utf-8')
                changed += 1
    errors = audit()
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'OK: campaign links for three Apple apps and Record Picker Windows; {changed} pages updated.')


if __name__ == '__main__':
    main()
