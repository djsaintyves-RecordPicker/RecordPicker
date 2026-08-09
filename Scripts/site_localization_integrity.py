#!/usr/bin/env python3
"""Require explicit acceptance for changes to public localized copy."""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "localization-integrity.json"
SPACE = re.compile(r"\s+")
PAGE_LOCALE = re.compile(r'data-page-lang="([^"]+)"')
HEAD_META = {"description", "og:title", "og:description", "twitter:title", "twitter:description"}


class PublicCopyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.copy: list[str] = []
        self.in_main = 0
        self.in_title = 0
        self.ignored = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag in {"script", "style", "svg"}:
            self.ignored += 1
            return
        if tag == "main":
            self.in_main += 1
        if tag == "title":
            self.in_title += 1
        if tag == "meta":
            identity = attributes.get("name") or attributes.get("property")
            if identity in HEAD_META and attributes.get("content"):
                self.add(f"meta:{identity}:{attributes['content']}")
        if self.in_main:
            for attribute in ("alt", "aria-label", "title"):
                if attributes.get(attribute):
                    self.add(f"{attribute}:{attributes[attribute]}")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag in {"script", "style", "svg"}:
            self.ignored -= 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "svg"}:
            self.ignored = max(0, self.ignored - 1)
            return
        if tag == "title":
            self.in_title = max(0, self.in_title - 1)
        if tag == "main":
            self.in_main = max(0, self.in_main - 1)

    def handle_data(self, data: str) -> None:
        if not self.ignored and (self.in_main or self.in_title):
            self.add(data)

    def add(self, value: str) -> None:
        normalized = SPACE.sub(" ", value).strip()
        if normalized:
            self.copy.append(normalized)


def page_digest(path: Path) -> tuple[str, str] | None:
    text = path.read_text(encoding="utf-8")
    if "<main" not in text:
        return None
    parser = PublicCopyParser()
    parser.feed(text)
    locale_match = PAGE_LOCALE.search(text)
    locale = locale_match.group(1) if locale_match else "shared"
    payload = json.dumps(parser.copy, ensure_ascii=False, separators=(",", ":"))
    return locale, hashlib.sha256(payload.encode("utf-8")).hexdigest()


def current_groups() -> tuple[int, dict[str, str]]:
    groups: dict[str, list[tuple[str, str]]] = {}
    page_count = 0
    for path in sorted(ROOT.rglob("*.html")):
        result = page_digest(path)
        if result is None:
            continue
        locale, digest = result
        page_count += 1
        groups.setdefault(locale, []).append((str(path.relative_to(ROOT)), digest))
    group_hashes = {
        locale: hashlib.sha256(
            json.dumps(entries, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        for locale, entries in sorted(groups.items())
    }
    return page_count, group_hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accept", action="store_true")
    parser.add_argument("--reason")
    arguments = parser.parse_args()
    page_count, groups = current_groups()
    if arguments.accept:
        if not arguments.reason or not arguments.reason.strip():
            print("--accept requires a non-empty --reason", file=sys.stderr)
            return 2
        payload = {
            "schema": 1,
            "page_count": page_count,
            "locale_group_count": len(groups),
            "review_reason": arguments.reason.strip(),
            "groups": groups,
        }
        MANIFEST.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"OK: accepted localized public copy for {page_count} pages.")
        return 0
    try:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"site localization integrity failed: {error}", file=sys.stderr)
        return 1
    if (
        payload.get("schema") != 1
        or payload.get("page_count") != page_count
        or payload.get("locale_group_count") != len(groups)
        or payload.get("groups") != groups
    ):
        print("site localization integrity failed: public copy changed", file=sys.stderr)
        print(
            "Review the generated pages, then accept them with "
            "--accept --reason '…'.",
            file=sys.stderr,
        )
        return 1
    print(
        f"OK: {page_count} pages in {len(groups)} locale groups match the accepted copy baseline."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
