"""Keep the French and English Studio cards concise, using verified release notes."""
from pathlib import Path
import re
from html import escape

ROOT = Path(__file__).resolve().parents[1]
COPY = {
    'fr': {
        'record-picker': ('3.1.2 · Des commandes plus faciles à suivre', 'Sur iPhone, iPad et Mac, Pro ajoute une date de livraison espérée et un accès direct au suivi du colis. La confirmation d’écoute rejoint la ligne des actions du tirage.'),
        'snory-teller': ('1.0.4 · Optimisée pour iPhone Duo', 'Cette mise à jour adapte Snory Teller aux nouvelles configurations d’écran de l’iPhone Duo et renforce la reprise de l’analyse pendant les longues nuits. Version validée par Apple ; déploiement sur l’App Store en cours.'),
        'physical-routine': ('1.0.5 · Optimisée pour iPhone Duo', 'Optimisée pour iPhone Duo'),
    },
    'en': {
        'record-picker': ('3.1.2 · Easier order tracking', 'On iPhone, iPad and Mac, Pro adds an expected delivery date and direct access to parcel tracking. Physical listening confirmation joins the pick action row.'),
        'snory-teller': ('1.0.4 · Optimized for iPhone Duo', 'This update adapts Snory Teller to new iPhone Duo display configurations and improves analysis recovery during long nights. Approved by Apple; rolling out on the App Store.'),
        'physical-routine': ('1.0.5 · Optimized for iPhone Duo', 'Optimized for iPhone Duo'),
    },
}

def update(path):
    source = path.read_text()
    locale = re.search(r'<html[^>]+lang="([^"]+)"', source)[1]
    lang = locale.split('-')[0]
    if lang not in COPY:
        return False
    original = source
    for ident, (title, note) in COPY[lang].items():
        if ident == 'snory-teller' and locale in {'en-GB', 'en-AU'}:
            title = title.replace('Optimized', 'Optimised')
        pattern = r'(<article\b[^>]*\bid="' + ident + r'"[^>]*>)(.*?)(</article>)'
        def card(match):
            body = match[2]
            news = '<details class="project-update" data-studio-current-update><summary>' + escape(title) + '</summary><p class="release-note">' + escape(note) + '</p></details>'
            old = r'<details\b[^>]*class="project-update"[^>]*>.*?</details>'
            if re.search(old, body, re.S):
                body = re.sub(old, lambda _: news, body, count=1, flags=re.S)
            else:
                body = body.replace('</div><div class="project-card-actions">', news + '</div><div class="project-card-actions">', 1)
            return match[1] + body + match[3]
        source, count = re.subn(pattern, card, source, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f'Missing {ident}: {path}')
    source = re.sub(r'(<section\b[^>]*id="ordered-records-preview"[^>]*>)(.*?)(</section>)',
                    lambda m: m[1] + m[2].replace('3.1.1', '3.1.2') + m[3], source, flags=re.S)
    if source != original:
        path.write_text(source)
        return True
    return False

if __name__ == '__main__':
    pages = list(ROOT.glob('*/apps/index.html')) + [ROOT / 'apps/index.html']
    print('Studio update pages:', sum(update(page) for page in pages))
