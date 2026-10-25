"""Keep the approved Studio presentation in generated pages, not only in output."""
import re
from lxml import html, etree
from site_music_menu import normalize as music_menu
from site_campaign_links import normalize as campaign_links

CSS = (
    '<link rel="stylesheet" href="/assets/css/studio-suite.css?v=20261025-restored">'
    '<link rel="stylesheet" href="/assets/css/suite-experience.css?v=20261025-white">'
)
JS = '<script src="/assets/js/suite-experience.js?v=20261023-language" defer></script>'


def normalize(source):
    if not re.search(r'<link[^>]+href="/apps/styles\.css', source):
        return source
    def body(match):
        tag = match[0]
        old = re.search(r'class="([^"]*)"', tag)
        names = list(dict.fromkeys((old[1].split() if old else []) +
                                  ['rps-suite', 'suite-studio', 'suite-experience']))
        attr = 'class="' + ' '.join(names) + '"'
        return tag[:old.start()] + attr + tag[old.end():] if old else tag[:-1] + ' ' + attr + '>'
    source = re.sub(r'<body\b[^>]*>', body, source, count=1)
    source = re.sub(r'<link[^>]+href="/assets/css/(?:studio-suite|studio-shadow-study|suite-experience)\.css[^"]*"[^>]*>', '', source)
    source = re.sub(r'<script[^>]+src="/assets/js/(?:studio-motion-study|suite-experience)\.js[^"]*"[^>]*>\s*</script>', '', source)
    source = source.replace('</head>', CSS + '</head>', 1).replace('</body>', JS + '</body>', 1)

    def intro(match):
        block = match[0]
        if 'studio-brand-composition' in block:
            return block
        image = re.search(r'<img\b[^>]*src="/assets/brand/rps/logo.webp"[^>]*>', block)
        if not image:
            return block
        pieces = '<span class="studio-brand-composition" aria-hidden="true">' + ''.join(
            '<img class="brand-piece brand-piece-' + part + '" src="/assets/brand/rps/logo.webp" alt="" width="1846" height="763"' +
            (' fetchpriority="high"' if part == 'symbol' else '') + '>'
            for part in ['symbol', 'name', 'studio']) + '</span>'
        return '<div class="studio-introduction">' + block.replace(image[0], pieces, 1) + '</div>'
    if 'studio-brand-composition' not in source:
        source = re.sub(r'<h1 class="studio-brand">.*?</h1>\s*<p class="intro">.*?</p>', intro, source, count=1, flags=re.S)

    def card(match):
        node = html.fromstring(match[0])
        ident = node.get('id')
        lang = re.search(r'<html[^>]*lang="([^"]*)"', source)
        language = lang[1].split('-')[0] if lang else 'en'
        actions = node.find("div[@class='project-card-actions']")
        content = node.find("div[@class='project-card-body']")
        if actions is None or content is None:
            return match[0]
        # A release regeneration puts the buttons back inside prose; the sequence
        # and consistent two-line geometry require the shared actions grid.
        stores = node.xpath('.//a[contains(concat(" ",@class," ")," store-button ")]')
        if stores and actions.find("div[@class='project-store-grid']") is None:
            grid = etree.Element('div', {'class': 'project-store-grid'})
            actions.insert(0, grid)
            for link in stores:
                link.getparent().remove(link)
                grid.append(link)
        for empty in content.xpath('./div[@class="app-actions"][not(*)]'):
            content.remove(empty)
        for link in list(content.xpath('.//a')):
            link.getparent().remove(link)
            link.set('class', (link.get('class', '') + ' project-text-link').strip())
            actions.append(link)
        for empty in content.xpath('./div[@class="app-actions"][not(*)]'):
            content.remove(empty)
        for link in stores:
            if link.find("span[@class='store-label']") is not None:
                continue
            old_label = link.text_content().strip()
            for span in link.findall('span'):
                link.remove(span)
            label = etree.SubElement(link, 'span', {'class': 'store-label'})
            classes = link.get('class', '')
            if 'store-appstore' in classes:
                name = 'App Store'
                platform = 'Mac' if 'platform=mac' in link.get('href', '') else ('iPhone & Apple Watch' if ident == 'snory-teller' else 'iPhone' if ident == 'physical-routine' else 'iPhone & iPad')
            elif 'store-microsoftstore' in classes:
                name, platform = 'Microsoft Store', 'Windows'
            else:
                name = 'Android'
                platform = 'Bêta privée' if language == 'fr' else 'Private beta' if language == 'en' else old_label
                link.set('aria-label', old_label)
            etree.SubElement(label, 'strong').text = name
            etree.SubElement(label, 'small').text = platform
        for note in list(content.xpath('./p[@class="release-note"]|./p[@class="release-32-summary"]|./div[@class="release-note"]')):
            version = re.search(r'(?<!\d)\d+\.\d+(?:\.\d+)?(?![\d.])', note.text_content())
            content.remove(note)
            details = etree.SubElement(content, 'details', {'class': 'project-update'})
            prefix = 'Nouveautés · ' if language == 'fr' else 'What’s new · ' if language == 'en' else ''
            etree.SubElement(details, 'summary').text = prefix + (version[0] if version else 'Info')
            details.append(note)
        for details in content.xpath('./details[@class="project-update"]'):
            summary = details.find('summary')
            notes = ''.join(child.text_content() for child in details if child.tag != 'summary')
            version = re.search(r'(?<!\d)\d+\.\d+(?:\.\d+)?(?![\d.])', notes)
            if summary is not None and version and re.fullmatch(r'(?:Nouveautés · |What’s new · )?\d+\.\d+(?:\.\d+)?', summary.text or ''):
                summary.text = re.sub(r'\d+\.\d+(?:\.\d+)?', version[0], summary.text)
        for image in node.xpath('.//img[contains(concat(" ",@class," ")," app-icon ")]'):
            image.set('src', image.get('src', '').rstrip('\\'))
        return html.tostring(node, encoding='unicode', with_tail=False)
    source = re.sub(r'<article\b[^>]*class="[^"]*project-card[^"]*"[^>]*>.*?</article>', card, source, flags=re.S)
    return campaign_links(music_menu(source))


if __name__ == '__main__':
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    changed = 0
    for path in root.rglob('apps/**/*.html'):
        if '.git' in path.parts:
            continue
        before = path.read_text()
        after = normalize(before)
        if after != before:
            path.write_text(after)
            changed += 1
    print('Studio presentation restored:', changed, 'pages')
