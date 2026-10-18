"""Replace passive creator cards on Record Picker pages with a useful studio bridge."""
from pathlib import Path
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
FR = {
    "eyebrow": "RECORD PICKER STUDIO", "title": "Trois apps, un même studio",
    "intro": "Record Picker fait partie de Record Picker Studio, avec Snory Teller et My Physical Routine. Découvrez les autres projets, puis revenez à votre collection quand vous en avez envie.",
    "rp_text": "Votre collection de vinyles et CD, pour retrouver quoi écouter.", "rp_action": "Voir Record Picker",
    "snory_text": "Un résumé estimé de vos nuits sur iPhone et Apple Watch.", "snory_action": "Découvrir Snory Teller",
    "routine_text": "Des séances de renforcement guidées, à votre rythme.", "routine_action": "Découvrir My Physical Routine",
    "all": "Explorer toutes les apps du studio",
}
EN = {
    "eyebrow": "RECORD PICKER STUDIO", "title": "Three apps, one studio",
    "intro": "Record Picker is part of Record Picker Studio, alongside Snory Teller and My Physical Routine. Explore the other projects, then return to your collection whenever you like.",
    "rp_text": "Your vinyl and CD collection, made to help you choose what to play.", "rp_action": "Explore Record Picker",
    "snory_text": "An estimated night summary on iPhone and Apple Watch.", "snory_action": "Explore Snory Teller",
    "routine_text": "Guided home strength sessions, at your own pace.", "routine_action": "Explore My Physical Routine",
    "all": "Explore every studio app",
}

def bridge(copy, french):
    apps, rp = ("/fr/apps/", "/fr/#top") if french else ("/apps/", "/#top")
    section = html.Element("section", {"class": "section studio-bridge", "data-creator-discovery": ""})
    head = etree.SubElement(section, "div", {"class": "studio-bridge-head"})
    etree.SubElement(head, "p", {"class": "kicker"}).text = copy["eyebrow"]
    etree.SubElement(head, "h2").text = copy["title"]
    etree.SubElement(head, "p", {"class": "lead"}).text = copy["intro"]
    cards = etree.SubElement(section, "div", {"class": "studio-bridge-grid"})
    entries = [
        ("Record Picker", copy["rp_text"], copy["rp_action"], rp, "/assets/brand/icon-192.png"),
        ("Snory Teller", copy["snory_text"], copy["snory_action"], f"/snory-teller/{'fr-FR' if french else 'en-US'}/", "/snory-teller/icon.png"),
        ("My Physical Routine", copy["routine_text"], copy["routine_action"], "/physical/fr/about/" if french else "/physical/about/", "/physical/icon.png"),
    ]
    for name, description, action, href, icon in entries:
        card = etree.SubElement(cards, "article", {"class": "studio-bridge-card"})
        etree.SubElement(card, "img", {"src": icon, "alt": "", "width": "88", "height": "88", "loading": "lazy"})
        body = etree.SubElement(card, "div")
        etree.SubElement(body, "h3").text = name
        etree.SubElement(body, "p").text = description
        etree.SubElement(body, "a", {"class": "button glass", "href": href}).text = action
    actions = etree.SubElement(section, "div", {"class": "studio-bridge-actions"})
    etree.SubElement(actions, "a", {"class": "button primary", "href": apps}).text = copy["all"]
    return section

for page in (ROOT / "index.html", ROOT / "fr" / "index.html"):
    raw = page.read_text()
    if "data-creator-discovery" not in raw:
        continue
    doc = html.fromstring(raw)
    old = doc.xpath('//*[@data-creator-discovery]')
    if len(old) != 1:
        raise ValueError(f"{page}: expected one creator section, found {len(old)}")
    french = page.relative_to(ROOT).parts[:1] == ("fr",)
    old[0].getparent().replace(old[0], bridge(FR if french else EN, french))
    page.write_text("<!doctype html>\n" + html.tostring(doc, encoding="unicode", method="html") + "\n")
    print(page.relative_to(ROOT))
