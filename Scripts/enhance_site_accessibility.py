#!/usr/bin/env python3
"""Add stable keyboard landmarks and refresh shared-asset cache keys."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKIP_LABELS = {
    "ar": "الانتقال إلى المحتوى", "ca": "Ves al contingut", "da": "Gå til indhold",
    "de": "Zum Inhalt springen", "el": "Μετάβαση στο περιεχόμενο",
    "es-ES": "Saltar al contenido", "fi": "Siirry sisältöön", "fr-CA": "Aller au contenu",
    "fr-FR": "Aller au contenu", "he": "דילוג לתוכן", "hi": "सामग्री पर जाएँ",
    "id": "Lewati ke konten", "it": "Vai al contenuto", "ja": "コンテンツへ移動",
    "ko": "콘텐츠로 건너뛰기", "nb": "Gå til innhold", "nl": "Naar inhoud",
    "pl": "Przejdź do treści", "pt-BR": "Ir para o conteúdo", "pt-PT": "Ir para o conteúdo",
    "ru": "Перейти к содержимому", "sv": "Gå till innehållet", "tr": "İçeriğe geç",
    "zh-Hans": "跳到内容", "zh-Hant": "跳至內容",
}


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        original = path.read_text(encoding="utf-8")
        text = original
        if "<body" not in text or "<main" not in text:
            continue
        language_match = re.search(r'<html lang="([^"]+)"', text)
        language = language_match.group(1) if language_match else "en"
        label = SKIP_LABELS.get(language, "Skip to content")
        text = re.sub(r'<a class="skip-link".*?</a>', "", text, count=1)
        text = re.sub(
            r'(<body[^>]*>)',
            rf'\1<a class="skip-link" href="#main-content">{label}</a>',
            text,
            count=1,
        )
        text = re.sub(r'<main(?: id="main-content")?', '<main id="main-content"', text, count=1)
        text = re.sub(r'(styles\.css\?v=)[^"]+', r'\g<1>20260807-quality', text)
        text = re.sub(r'(site\.js\?v=)[^"]+', r'\g<1>20260807-quality', text)
        quality_href = "quality.css" if path.parent == ROOT else "../" * len(path.relative_to(ROOT).parent.parts) + "quality.css"
        quality_link = f'<link rel="stylesheet" href="{quality_href}?v=20260807-quality">'
        text = re.sub(r'<link rel="stylesheet" href="[^"]*quality\.css[^>]*>', "", text, count=1)
        text = text.replace("</head>", quality_link + "</head>", 1)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    print(f"Enhanced keyboard access on {changed} HTML pages.")


if __name__ == "__main__":
    main()
