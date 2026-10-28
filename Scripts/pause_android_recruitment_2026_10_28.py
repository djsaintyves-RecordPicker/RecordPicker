#!/usr/bin/env python3
"""Pause public Android recruitment while retaining localized URLs and Git history."""
from pathlib import Path
import html
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAUSED = {
 '': 'Android project paused', 'en-us': 'Android project paused', 'en-gb': 'Android project paused', 'en-ca': 'Android project paused', 'en-au': 'Android project paused',
 'fr': 'Projet Android en pause', 'fr-ca': 'Projet Android en pause', 'de': 'Android-Projekt pausiert', 'nl': 'Android-project gepauzeerd',
 'es-es': 'Proyecto Android en pausa', 'es-mx': 'Proyecto Android en pausa', 'pt-br': 'Projeto Android pausado', 'pt-pt': 'Projeto Android em pausa',
 'it': 'Progetto Android in pausa', 'ca': 'Projecte Android en pausa', 'da': 'Android-projekt sat på pause', 'sv': 'Android-projektet är pausat',
 'nb': 'Android-prosjektet er satt på pause', 'fi': 'Android-projekti on tauolla', 'pl': 'Projekt Android wstrzymany', 'tr': 'Android projesi duraklatıldı',
 'ru': 'Проект Android приостановлен', 'uk': 'Проєкт Android призупинено', 'el': 'Το έργο Android έχει τεθεί σε παύση',
 'ar': 'مشروع Android متوقف مؤقتًا', 'he': 'פרויקט Android מושהה', 'hi': 'Android परियोजना फिलहाल रुकी हुई है',
 'id': 'Proyek Android dijeda', 'ja': 'Androidプロジェクトは一時停止中です', 'ko': 'Android 프로젝트가 일시 중단되었습니다',
 'th': 'โครงการ Android หยุดชั่วคราว', 'vi': 'Dự án Android đang tạm dừng', 'zh-hans': 'Android 项目已暂停', 'zh-hant': 'Android 專案已暫停',
}

sys.path.insert(0, str(ROOT / 'Scripts'))
from update_android_beta_status import STATUS

ANCHOR = re.compile(r'<a\b[^>]*>.*?</a\s*>', re.I | re.S)
BANNER = re.compile(r'<section\b[^>]*class="[^"]*\bbeta-campaign\b[^"]*"[^>]*>.*?</section\s*>', re.I | re.S)
SITE_BANNER = re.compile(r'<aside\b[^>]*\bdata-beta-recruitment\b[^>]*>.*?</aside\s*>', re.I | re.S)
MAIN = re.compile(r'<main\b[^>]*>.*?</main\s*>', re.I | re.S)
SCHEMA = re.compile(r'(<script\b[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)', re.I | re.S)

def replace_meta(text, name, content):
    pattern = re.compile(r'(<meta\b[^>]*(?:name|property)="' + re.escape(name) + r'"[^>]*\bcontent=")[^"]*("[^>]*>)', re.I)
    return pattern.sub(lambda m: m.group(1) + html.escape(content, quote=True) + m.group(2), text)

def main():
    changed = []
    for path in ROOT.rglob('*.html'):
        if '.git' in path.parts or 'tmp' in path.parts:
            continue
        relative = path.relative_to(ROOT)
        locale = relative.parts[0] if relative.parts[0] in PAUSED else ''
        message = PAUSED[locale]
        old = path.read_text(encoding='utf-8')
        text = SITE_BANNER.sub('', BANNER.sub('', old))

        def remove_recruitment(m):
            a = m.group()
            opening = a[:a.find('>') + 1]
            if 'language-option' in opening or 'hreflang=' in opening:
                return a
            if re.search(r'(?:android-app/|android[_%\-]beta|record-picker-android-beta|data-umami-event="beta_click")', opening, re.I):
                return ''
            return a
        text = ANCHOR.sub(remove_recruitment, text)

        previous = STATUS.get(locale, STATUS[''])
        text = text.replace('>' + html.escape(previous) + '<', '>' + html.escape(message) + '<')
        text = text.replace('Android: ' + html.escape(previous) + '"', 'Android: ' + html.escape(message) + '"')

        if relative.parts[-2:] == ('android-app', 'index.html'):
            assert len(MAIN.findall(text)) == 1, relative
            title = 'Record Picker — ' + message
            content = '<main id="main-content" class="container"><section class="section"><h1>' + html.escape(title) + '</h1></section></main>'
            text = MAIN.sub(lambda _: content, text)
            text = re.sub(r'<title>.*?</title>', lambda _: '<title>' + html.escape(title) + '</title>', text, count=1, flags=re.I | re.S)
            for key in ('description', 'og:title', 'og:description', 'twitter:title', 'twitter:description', 'og:image:alt', 'twitter:image:alt'):
                text = replace_meta(text, key, title)
            def update_schema(m):
                try:
                    obj = json.loads(m.group(2))
                except ValueError:
                    return m.group()
                def walk(node):
                    if isinstance(node, dict):
                        for key, val in node.items():
                            if key in ('name', 'description') and isinstance(val, str) and re.search(r'android|beta|bêta|beta-tester', val, re.I):
                                node[key] = title
                            else:
                                walk(val)
                    elif isinstance(node, list):
                        for val in node: walk(val)
                walk(obj)
                return m.group(1) + json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + m.group(3)
            text = SCHEMA.sub(update_schema, text)
        if text != old:
            path.write_text(text, encoding='utf-8')
            changed.append(str(relative))
    print('Updated', len(changed), 'pages; Android landing pages:', sum('/android-app/' in '/' + p for p in changed))

if __name__ == '__main__':
    main()
