#!/usr/bin/env python3
"""Build and package the bilingual Record Picker 2.6 press kits."""

from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import shutil
import textwrap
import zipfile

from PIL import Image
from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf"
PRESS = ROOT / "assets/press"
TMP = ROOT / "tmp/pdfs"
DATE = "26.09.2026"
RED = HexColor("#DF2445")
INK = HexColor("#111116")
MUTED = HexColor("#64646F")
LINE = HexColor("#E6E6EA")
SOFT = HexColor("#F7F7F9")
APPLE_STORE = "https://apps.apple.com/app/id6780422305"
MICROSOFT_STORE = "https://apps.microsoft.com/detail/9N2ZWRL4M3JC"
SITE = "https://recordpicker.app/"
W, H = A4


FR = {
    "kit": "DOSSIER DE PRESSE",
    "tagline": "La bonne raison de ressortir un disque.",
    "intro": "Une app native pour cataloguer et redécouvrir une collection de vinyles et de CD.",
    "available": "Record Picker 2.6 est disponible sur iPhone, iPad, Apple Watch, Mac et Windows 11.",
    "release": "La version 2.6 améliore les sauvegardes, la restauration des pochettes et la fiabilité, tout en proposant les mêmes outils essentiels de choix et de catalogage sur PC.",
    "choose": "Trois façons de choisir",
    "random": ("Tirage aléatoire", "Un tirage classique ou pondéré, avec filtres, favoris et exclusions."),
    "mood": ("Mood Pick", "Décrivez une ambiance. Record Picker cherche un disque adapté dans votre collection."),
    "today": ("Disque du jour", "Des suggestions expliquées et sourcées, rapprochées de votre collection sur votre appareil."),
    "windows": "Record Picker 2.6 sur Windows",
    "windows_body": "Disponible dans le Microsoft Store pour Windows 11 sur PC x64 et ARM64. L'interface publique est proposée en anglais et en français.",
    "windows_note": "Capture authentique de l'app Windows 2.6, en français.",
    "collection": "Votre collection, plus claire",
    "catalog": ("Cataloguer, explorer, retrouver", "Parcourez les pochettes, retrouvez un disque, explorez le graphe de collection et préparez un parcours d'écoute. Vos données restent sous votre contrôle."),
    "backups": ("Sauvegardes et fiabilité", "La version 2.6 renforce les sauvegardes de collection et la restauration des pochettes. La synchronisation iCloud reste facultative sur les appareils Apple."),
    "demo": "Collection de démonstration presse",
    "demo_title": "335 disques pour une évaluation complète",
    "demo_body": "Le fichier presse contient 266 albums et 69 interprétations classiques reliées autour de 15 œuvres. Il permet de découvrir l'app sans utiliser sa discothèque personnelle.",
    "demo_import": "Import Apple : Réglages > Données > Importer une collection CSV.",
    "demo_note": "La capture iPhone 2.6 illustre l'interface et montre une autre collection. Tous les visuels fournis sont des captures authentiques.",
    "facts": "Les faits essentiels",
    "fact_rows": [
        ("DÉVELOPPEUR", "Yves Durand"),
        ("VERSION", "Record Picker 2.6 \"Snow Leopard\""),
        ("PLATEFORMES PUBLIQUES", "iPhone, iPad, Apple Watch, Mac, Windows 11"),
        ("EN DÉVELOPPEMENT", "Android"),
        ("PRIX", "Gratuite jusqu'à 100 disques ; achat Pro définitif, sans abonnement."),
        ("CONFIDENTIALITÉ", "Sans compte, publicité ni pistage. Collection locale ; iCloud facultatif sur Apple."),
        ("LANGUES", "32 langues et variantes sur Apple ; anglais et français sur Windows."),
    ],
    "coverage": "Presse : Mac4Ever, 11 août 2026",
    "contact": "CONTACT PRESSE - Yves Durand - djsaintyves@mac.com",
}

EN = {
    "kit": "PRESS KIT",
    "tagline": "A good reason to pull a record off the shelf.",
    "intro": "A native app for cataloguing and rediscovering a vinyl and CD collection.",
    "available": "Record Picker 2.6 is available on iPhone, iPad, Apple Watch, Mac and Windows 11.",
    "release": "Version 2.6 improves backups, cover artwork restoration and reliability, while bringing the same essential picking and cataloguing tools to PC.",
    "choose": "Three ways to choose",
    "random": ("Random Pick", "A standard or weighted draw, with filters, favourites and exclusions."),
    "mood": ("Mood Pick", "Describe a mood. Record Picker finds a fitting record in your own collection."),
    "today": ("Today's Pick", "Explained, sourced suggestions matched to your collection on your device."),
    "windows": "Record Picker 2.6 on Windows",
    "windows_body": "Available from the Microsoft Store for Windows 11 on x64 and ARM64 PCs. The public interface is available in English and French.",
    "windows_note": "Authentic Record Picker 2.6 Windows capture, shown in French.",
    "collection": "A clearer view of your collection",
    "catalog": ("Catalogue, explore, rediscover", "Browse covers, find a record, explore the Collection Graph and prepare a Listening Journey. Your data stays under your control."),
    "backups": ("Backups and reliability", "Version 2.6 improves collection backups and cover artwork restoration. iCloud synchronisation remains optional on Apple devices."),
    "demo": "Press demonstration collection",
    "demo_title": "335 records for a complete review",
    "demo_body": "The press file contains 266 albums and 69 classical interpretations connected through 15 works. It lets reviewers explore the app without using their personal music library.",
    "demo_import": "Apple import: Settings > Data > Import collection CSV.",
    "demo_note": "The iPhone 2.6 capture illustrates the interface and shows a different collection. Every supplied visual is an authentic app capture.",
    "facts": "Essential facts",
    "fact_rows": [
        ("DEVELOPER", "Yves Durand"),
        ("VERSION", "Record Picker 2.6 \"Snow Leopard\""),
        ("PUBLIC PLATFORMS", "iPhone, iPad, Apple Watch, Mac, Windows 11"),
        ("IN DEVELOPMENT", "Android"),
        ("PRICING", "Free for up to 100 records; one-time Pro purchase, no subscription."),
        ("PRIVACY", "No account, advertising or tracking. Local collection; optional iCloud on Apple."),
        ("LANGUAGES", "32 languages and variants on Apple; English and French on Windows."),
    ],
    "coverage": "Coverage: Mac4Ever, 11 August 2026",
    "contact": "PRESS CONTACT - Yves Durand - djsaintyves@mac.com",
}


def image_box(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(SOFT)
    c.roundRect(x, y, w, h, 10, fill=1, stroke=0)
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min((w - 12) / iw, (h - 12) / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(str(path), x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, preserveAspectRatio=True, mask="auto")


def wrap(c: canvas.Canvas, text: str, x: float, y: float, width: float, size: float = 11, leading: float = 15, color=INK, font="Helvetica") -> float:
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = (line + " " + word).strip()
        if stringWidth(candidate, font, size) <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def header(c: canvas.Canvas, d: dict, page: int, title: str) -> None:
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(0, H - 8, W, 8, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(38, H - 34, f"RECORD PICKER 2.6  /  {d['kit']}")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 25)
    c.drawString(38, H - 76, title)
    c.setStrokeColor(LINE)
    c.line(38, H - 92, W - 38, H - 92)
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawString(38, 24, f"recordpicker.app  |  {DATE}")
    c.drawRightString(W - 38, 24, str(page))


def pill(c: canvas.Canvas, text: str, x: float, y: float) -> float:
    size = 9
    width = stringWidth(text, "Helvetica-Bold", size) + 22
    c.setFillColor(white)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, width, 25, 12, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", size)
    c.drawCentredString(x + width / 2, y + 8, text)
    return x + width + 7


def build_pdf(path: Path, d: dict, lang: str) -> None:
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    c.setTitle(f"Record Picker 2.6 - {d['kit'].title()}")
    c.setAuthor("Record Picker")

    header(c, d, 1, d["tagline"])
    y = H - 125
    y = wrap(c, d["intro"], 38, y, W - 76, 15, 20, INK, "Helvetica-Bold") - 6
    x = 38
    for name in ("iPhone", "iPad", "Apple Watch", "Mac", "Windows"):
        x = pill(c, name, x, y - 18)
    image_box(c, ROOT / "assets/screenshots/v26/en-us/mac-home.webp", 38, 270, W - 76, 310)
    y = 242
    y = wrap(c, d["available"], 38, y, W - 76, 12, 17, INK, "Helvetica-Bold") - 5
    wrap(c, d["release"], 38, y, W - 76, 10.5, 15, MUTED)
    c.showPage()

    header(c, d, 2, d["choose"])
    cards = [
        ("mac-random-pick.webp", d["random"]),
        ("mac-mood-pick.webp", d["mood"]),
        ("mac-todays-pick.webp", d["today"]),
    ]
    cw = (W - 92) / 3
    for idx, (filename, copy) in enumerate(cards):
        x = 38 + idx * (cw + 8)
        image_box(c, ROOT / "assets/screenshots/v26/en-us" / filename, x, 430, cw, 245)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, 403, copy[0])
        wrap(c, copy[1], x, 382, cw, 10, 14, MUTED)
    c.showPage()

    header(c, d, 3, d["windows"])
    image_box(c, ROOT / "assets/screenshots/v26/windows/windows-random-pick-fr.webp", 38, 335, W - 76, 360)
    y = 305
    y = wrap(c, d["windows_body"], 38, y, W - 76, 12, 17, INK, "Helvetica-Bold") - 6
    wrap(c, d["windows_note"], 38, y, W - 76, 9.5, 14, MUTED)
    c.setFillColor(RED)
    c.roundRect(38, 116, 190, 38, 19, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(133, 130, "Microsoft Store")
    c.linkURL(MICROSOFT_STORE, (38, 116, 228, 154), relative=0)
    c.showPage()

    header(c, d, 4, d["collection"])
    image_box(c, ROOT / "assets/screenshots/v26/en-us/mac-collection.webp", 38, 393, W - 76, 300)
    y = 360
    for title, body in (d["catalog"], d["backups"]):
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(38, y, title)
        y = wrap(c, body, 38, y - 20, W - 76, 10.5, 15, MUTED) - 16
    c.showPage()

    header(c, d, 5, d["demo"])
    image_box(c, ROOT / "assets/screenshots/v26/en-us/iphone-collection.webp", 38, 150, 190, 545)
    x = 255
    y = 660
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 16)
    y = wrap(c, d["demo_title"], x, y, W - x - 38, 16, 20, INK, "Helvetica-Bold") - 15
    y = wrap(c, d["demo_body"], x, y, W - x - 38, 10.5, 15, MUTED) - 15
    y = wrap(c, d["demo_import"], x, y, W - x - 38, 10.5, 15, INK, "Helvetica-Bold") - 15
    wrap(c, d["demo_note"], x, y, W - x - 38, 10, 14, MUTED)
    c.showPage()

    header(c, d, 6, d["facts"])
    y = 700
    for label, value in d["fact_rows"]:
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(38, y, label)
        y = wrap(c, value, 38, y - 17, W - 76, 11.5, 16, INK, "Helvetica-Bold") - 13
        c.setStrokeColor(LINE)
        c.line(38, y + 5, W - 38, y + 5)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(38, 118, "App Store")
    c.linkURL(APPLE_STORE, (38, 104, 118, 128), relative=0)
    c.drawString(145, 118, "Microsoft Store")
    c.linkURL(MICROSOFT_STORE, (145, 104, 255, 128), relative=0)
    c.drawString(285, 118, "recordpicker.app")
    c.linkURL(SITE, (285, 104, 390, 128), relative=0)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(38, 86, d["coverage"])
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(38, 63, d["contact"])
    c.save()


def build_archive(fr_pdf: Path, en_pdf: Path) -> None:
    old_zip = PRESS / "Record-Picker-Press-Kit.zip"
    demo = TMP / "Record-Picker-Press-Demo-Library.zip"
    if old_zip.exists():
        with zipfile.ZipFile(old_zip) as archive:
            demo.write_bytes(archive.read("Record-Picker-Press-Demo-Library.zip"))
    readme_fr = """RECORD PICKER 2.6 - DOSSIER DE PRESSE\n\nRecord Picker est disponible sur iPhone, iPad, Apple Watch, Mac et Windows 11.\nAndroid reste en développement.\n\nApp Store : https://apps.apple.com/app/id6780422305\nMicrosoft Store : https://apps.microsoft.com/detail/9N2ZWRL4M3JC\nSite : https://recordpicker.app/\nContact presse : Yves Durand - djsaintyves@mac.com\n"""
    readme_en = """RECORD PICKER 2.6 - PRESS KIT\n\nRecord Picker is available on iPhone, iPad, Apple Watch, Mac and Windows 11.\nAndroid remains in development.\n\nApp Store: https://apps.apple.com/app/id6780422305\nMicrosoft Store: https://apps.microsoft.com/detail/9N2ZWRL4M3JC\nWebsite: https://recordpicker.app/\nPress contact: Yves Durand - djsaintyves@mac.com\n"""
    visuals = [
        ROOT / "assets/screenshots/v26/en-us/mac-home.webp",
        ROOT / "assets/screenshots/v26/en-us/mac-random-pick.webp",
        ROOT / "assets/screenshots/v26/en-us/mac-mood-pick.webp",
        ROOT / "assets/screenshots/v26/en-us/mac-todays-pick.webp",
        ROOT / "assets/screenshots/v26/en-us/mac-collection.webp",
        ROOT / "assets/screenshots/v26/en-us/mac-collection-graph.webp",
        ROOT / "assets/screenshots/v26/en-us/mac-graph-relationships.webp",
        ROOT / "assets/screenshots/v26/en-us/mac-data-quality.webp",
        ROOT / "assets/screenshots/v26/en-us/iphone-collection.webp",
        ROOT / "assets/screenshots/v26/fr/iphone-collection.webp",
        ROOT / "assets/screenshots/v26/windows/windows-random-pick-fr.webp",
    ]
    provenance = json.loads((ROOT / "data/media-release-manifest.json").read_text(encoding="utf-8"))
    with zipfile.ZipFile(PRESS / "Record-Picker-Press-Kit.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(en_pdf, en_pdf.name)
        archive.write(fr_pdf, fr_pdf.name)
        if demo.exists():
            archive.write(demo, demo.name)
        archive.writestr("LISEZ-MOI.txt", readme_fr)
        archive.writestr("README.txt", readme_en)
        for visual in visuals:
            locale = "windows" if "windows" in visual.parts else visual.parent.name
            archive.write(visual, f"Visuals/{locale}/{visual.name}")
        archive.writestr("Visuals/provenance.json", json.dumps(provenance, ensure_ascii=False, indent=2))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    fr = OUT / "Record-Picker-Dossier-de-presse-FR.pdf"
    en = OUT / "Record-Picker-Press-Kit-EN.pdf"
    build_pdf(fr, FR, "fr")
    build_pdf(en, EN, "en-GB")
    shutil.copy2(fr, PRESS / fr.name)
    shutil.copy2(en, PRESS / en.name)
    build_archive(PRESS / fr.name, PRESS / en.name)
    print(f"Built {fr}, {en}, and the press archive.")


if __name__ == "__main__":
    main()
