#!/usr/bin/env python3
"""Maintain authentic bilingual app previews in the six relevant product guides."""
from pathlib import Path
from html import escape
import json
import re
import xml.etree.ElementTree as ET
from site_guide_identity import normalize as normalize_guide_identity
from site_campaign_links import normalize as normalize_campaign_links

ROOT = Path(__file__).resolve().parents[1]
ASSETS = '/assets/videos/2026-10-22/'
DATA = ROOT / 'data/app-video-guides-2026-10-22.json'


def main():
    campaigns = json.loads((ROOT / 'data/acquisition-campaigns.json').read_text())['channels']['website']['apps']
    sitemap_ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    video_ns = 'http://www.google.com/schemas/sitemap-video/1.1'
    ET.register_namespace('',sitemap_ns)
    ET.register_namespace('video',video_ns)
    sitemap = ET.Element('{'+sitemap_ns+'}urlset')
    for app in json.loads(DATA.read_text()):
        for lang, route in app['routes'].items():
            path = ROOT / route
            text = path.read_text()
            slug = app['slug']
            title = app['title'][lang]
            description = app['description'][lang]
            section_title = 'En vidéo : ' if lang == 'fr' else 'In video: '
            label = 'Vidéo de 12 secondes, textes français et anglais.' if lang == 'fr' else '12-second video with French and English on-screen text.'
            transcript = 'Transcription' if lang == 'fr' else 'Transcript'
            store_label = 'Ouvrir la fiche App Store' if lang == 'fr' else 'Open the App Store page'
            studio_label = 'Toutes les apps du Studio' if lang == 'fr' else 'All Studio apps'
            studio_url = '/fr/apps/' if lang == 'fr' else '/apps/'
            destinations = campaigns[app['name']]
            actions = f'<p><a href="{escape(destinations["appStore"],quote=True)}">{store_label}</a>'
            if 'microsoftStore' in destinations:
                actions += f'<a href="{escape(destinations["microsoftStore"],quote=True)}">Microsoft Store</a>'
            actions += f'<a href="{studio_url}">{studio_label}</a></p>'
            tracks = ''.join(f'<track kind="captions" src="{ASSETS}{slug}-{code}.vtt" srclang="{code}" label="{name}">' for code,name in [('fr','Français'),('en','English')])
            section = f'''<section class="app-video-guide" id="app-video-preview" aria-labelledby="app-video-preview-title"><h2 id="app-video-preview-title">{escape(section_title+title)}</h2><div class="app-video-guide__content"><video controls playsinline preload="none" poster="{ASSETS}{slug}.jpg" width="1080" height="1920" aria-label="{escape(app['name']+' — '+title,quote=True)}"><source src="{ASSETS}{slug}.mp4" type="video/mp4">{tracks}<a href="{ASSETS}{slug}.mp4">{escape(title)}</a></video><div><p>{escape(label)}</p><p>{escape(description)}</p><details><summary>{transcript}</summary><p>{escape(title)} {' '.join(escape(step) for step in app['steps'][lang])}</p></details></div></div></section>'''
            section = section.replace('<details>',actions+'<details>')
            text = re.sub(r'<section class="app-video-guide".*?</section>', '', text, flags=re.S)
            assert text.count('</main>') == 1, route
            text = text.replace('</main>',section+'</main>')
            stylesheet = f'<link rel="stylesheet" href="{ASSETS}guides.css">'
            if stylesheet not in text:
                text = text.replace('</head>',stylesheet+'</head>')
            metadata = {'@context':'https://schema.org','@type':'VideoObject',
                        'name':app['name']+' — '+title,'description':description,
                        'thumbnailUrl':['https://recordpicker.app'+ASSETS+slug+'.jpg'],
                        'uploadDate':'2026-10-22T09:39:54Z','duration':'PT12S',
                        'contentUrl':'https://recordpicker.app'+ASSETS+slug+'.mp4',
                        'inLanguage':['fr','en'],
                        'transcript':title+' '+' '.join(app['steps'][lang]),
                        'publisher':{'@type':'Organization','name':'Record Picker Studio','url':'https://recordpicker.app/apps/'}}
            text = re.sub(r'<script type="application/ld\+json" id="app-video-data">.*?</script>','',text,flags=re.S)
            script = '<script type="application/ld+json" id="app-video-data">'+json.dumps(metadata,ensure_ascii=False).replace('</','<\\/')+'</script>'
            text = text.replace('</head>',script+'</head>')
            kind = {'snory-teller':'snory-guide','my-physical-routine':'physical-guide'}.get(slug)
            if kind:
                text = normalize_guide_identity(text,kind,'fr-FR' if lang=='fr' else 'en-US')
            else:
                text = normalize_campaign_links(text)
            path.write_text(text)
            entry = ET.SubElement(sitemap,'{'+sitemap_ns+'}url')
            ET.SubElement(entry,'{'+sitemap_ns+'}loc').text = 'https://recordpicker.app/'+route.removesuffix('index.html')
            video = ET.SubElement(entry,'{'+video_ns+'}video')
            values = {'thumbnail_loc':metadata['thumbnailUrl'][0],
                      'title':metadata['name'],'description':description,
                      'content_loc':metadata['contentUrl'],'duration':'12',
                      'publication_date':metadata['uploadDate']}
            for key,value in values.items():
                ET.SubElement(video,'{'+video_ns+'}'+key).text = value
            print(route)
    ET.indent(sitemap,space='  ')
    ET.ElementTree(sitemap).write(ROOT/'sitemap-videos.xml',encoding='utf-8',xml_declaration=True)
    robots = ROOT/'robots.txt'
    directive = 'Sitemap: https://recordpicker.app/sitemap-videos.xml'
    if directive not in robots.read_text():
        robots.write_text(robots.read_text().rstrip()+'\n'+directive+'\n')


if __name__ == '__main__':
    main()
