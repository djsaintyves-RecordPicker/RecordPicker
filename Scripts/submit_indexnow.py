#!/usr/bin/env python3
"""Notify IndexNow participants after a successful public deployment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
HOST = "recordpicker.app"
SITE = f"https://{HOST}"
KEY = "8f4a6c2e91d7430ba5f8c1e6a9d2b407"
KEY_LOCATION = f"{SITE}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"


def sitemap_urls() -> list[str]:
    text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    urls = re.findall(r"<loc>(https://recordpicker\.app/[^<]*)</loc>", text)
    unique = list(dict.fromkeys(urls))
    if not unique:
        raise RuntimeError("sitemap.xml contains no Record Picker URL")
    if len(unique) != len(urls):
        raise RuntimeError("sitemap.xml contains duplicate URLs")
    return unique


def validate_key_file() -> None:
    path = ROOT / f"{KEY}.txt"
    if path.read_text(encoding="utf-8").strip() != KEY:
        raise RuntimeError(f"invalid IndexNow key file: {path.name}")


def payload(urls: list[str]) -> bytes:
    return json.dumps(
        {
            "host": HOST,
            "key": KEY,
            "keyLocation": KEY_LOCATION,
            "urlList": urls,
        },
        separators=(",", ":"),
    ).encode("utf-8")


def submit(urls: list[str]) -> int:
    body = payload(urls)
    request = Request(
        ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "RecordPicker-IndexNow/1.0",
        },
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urlopen(request, timeout=30) as response:
                status = response.status
            if status in {200, 202}:
                return status
            last_error = RuntimeError(f"unexpected IndexNow HTTP status {status}")
        except (HTTPError, URLError, TimeoutError) as error:
            last_error = error
        if attempt < 3:
            time.sleep(attempt * 2)
    raise RuntimeError(f"IndexNow submission failed after 3 attempts: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and print the batch without contacting IndexNow",
    )
    args = parser.parse_args()
    validate_key_file()
    urls = sitemap_urls()
    if args.dry_run:
        print(f"OK: IndexNow batch contains {len(urls)} canonical URLs; key at {KEY_LOCATION}.")
        return
    status = submit(urls)
    print(f"OK: IndexNow accepted {len(urls)} canonical URLs (HTTP {status}).")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
