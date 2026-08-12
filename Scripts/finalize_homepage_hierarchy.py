#!/usr/bin/env python3
"""Put durable product value before the temporary contest on every homepage."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def extract(text: str, pattern: str) -> tuple[str, str]:
    match = re.search(pattern, text, flags=re.DOTALL)
    if not match:
        return text, ""
    return text[: match.start()] + text[match.end() :], match.group(0)


def update_home(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    original = text
    blocks: dict[str, str] = {}
    patterns = {
        "release": r'<section class="section v20-preview current-release".*?</section>',
        "product": r'<section class="section split" id="app".*?</section>',
        "press": r'<section class="section press-review-spotlight".*?</section>',
        "privacy": r'<section class="section privacy-compact".*?</section>',
        "challenge": r'<section class="challenge-section".*?</section>',
    }
    for name, pattern in patterns.items():
        text, blocks[name] = extract(text, pattern)

    if not all(blocks[name] for name in ("release", "product", "privacy", "challenge")):
        return

    if blocks["press"] and 'RP20_InstagramMac4Ever' not in blocks["press"]:
        french = path == ROOT / "index.html" or path.parts[-2] in {"fr", "fr-ca"}
        label = "Essayer gratuitement" if french else "Try Record Picker free"
        app_url = "https://apps.apple.com/app/recordpicker/id6780422305"
        button = (
            f'<a class="button primary press-review-app-button" href="{app_url}" '
            f'data-app-store-link data-app-store-campaign="RP20_InstagramMac4Ever">{label}</a>'
        )
        article_link = re.search(r'<a class="button glass".*?</a>', blocks["press"], flags=re.DOTALL)
        if article_link:
            actions = '<div class="press-review-actions">' + article_link.group(0) + button + "</div>"
            blocks["press"] = (
                blocks["press"][: article_link.start()]
                + actions
                + blocks["press"][article_link.end() :]
            )

    facts_end = text.find("</section>", text.find('<section class="facts-band">'))
    if facts_end < 0:
        raise RuntimeError(f"Facts band missing in {path}")
    facts_end += len("</section>")
    hierarchy = (
        blocks["release"]
        + blocks["product"]
        + blocks["press"]
        + blocks["privacy"]
        + blocks["challenge"]
    )
    text = text[:facts_end] + hierarchy + text[facts_end:]
    text = re.sub(r'site\.js\?v=[^"\']+', 'site.js?v=20260812-final-funnel', text)
    text = re.sub(r'quality\.css\?v=[^"\']+', 'quality.css?v=20260812-final-funnel', text)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    homes = [ROOT / "index.html"] + sorted(
        path for path in ROOT.glob("*/index.html") if path.parent.name not in {
            "contest", "press", "privacy", "support", "screenshots", "readme", "mac-app",
            "choose-vinyl-record", "random-vinyl-record-picker", "manage-vinyl-collection",
        }
    )
    updated = 0
    for path in homes:
        before = path.read_text(encoding="utf-8")
        update_home(path)
        updated += path.read_text(encoding="utf-8") != before
    print(f"Finalized product-first hierarchy on {updated} homepages.")


if __name__ == "__main__":
    main()
