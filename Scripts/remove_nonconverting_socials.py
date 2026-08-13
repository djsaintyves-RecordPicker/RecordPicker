#!/usr/bin/env python3
"""Temporarily keep Instagram as the site's only public social channel."""

from __future__ import annotations

from html import unescape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
INSTAGRAM = "https://www.instagram.com/recordpicker/"
REMOVED_HOSTS = ("youtube.com", "facebook.com", "threads.net", "reddit.com")


def clean_schema(value: object) -> None:
    if isinstance(value, dict):
        if "sameAs" in value and isinstance(value["sameAs"], list):
            value["sameAs"] = [url for url in value["sameAs"] if url == INSTAGRAM]
        for child in value.values():
            clean_schema(child)
    elif isinstance(value, list):
        for child in value:
            clean_schema(child)


def update_page(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'<a\b[^>]*href="https://(?:www\.)?(?:youtube\.com|facebook\.com|threads\.net|reddit\.com)/[^">]*"[^>]*>.*?</a>',
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    def replace_schema(match: re.Match[str]) -> str:
        try:
            schema = json.loads(unescape(match.group(2)))
        except json.JSONDecodeError:
            return match.group(0)
        clean_schema(schema)
        payload = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        return match.group(1) + payload + match.group(3)

    updated = re.sub(
        r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)',
        replace_schema,
        updated,
        flags=re.DOTALL,
    )
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = sum(update_page(path) for path in ROOT.rglob("*.html"))
    print(f"Kept Instagram as the only public social channel on {changed} HTML pages.")


if __name__ == "__main__":
    main()
