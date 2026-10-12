#!/usr/bin/env python3
"""Notify IndexNow participants after a successful public deployment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
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


def changed_urls(since: str, root: Path = ROOT) -> list[str]:
    """Notify changed public HTML only, including removed URLs and old canonicals."""
    if not since or set(since) == {"0"}:
        return []  # No reliable baseline: never fall back to submitting the entire site.
    def git(*args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=root, text=True)
    git("rev-parse", "--verify", since + "^{commit}")
    paths = git("diff", "--name-only", "-z", "--no-renames", since, "HEAD", "--").split("\0")
    urls = set()
    pattern = re.compile(r'<link\b(?=[^>]*\brel=[\"\']canonical[\"\'])[^>]*\bhref=[\"\']([^\"\']+)', re.I)
    for path in paths:
        if not path.endswith(".html") or any(part.startswith(".") for part in Path(path).parts):
            continue
        for revision in (since, "HEAD"):
            result = subprocess.run(["git", "show", f"{revision}:{path}"], cwd=root,
                                    capture_output=True, text=True)
            if result.returncode:
                continue  # File added or deleted in this revision.
            match = pattern.search(result.stdout)
            if match and match.group(1).startswith(SITE + "/"):
                urls.add(match.group(1))
    return sorted(urls)


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
    parser.add_argument("--since", help="Git baseline before the deployed push; only changed HTML URLs are notified")
    args = parser.parse_args()
    validate_key_file()
    if not args.dry_run and args.since is None:
        parser.error("--since is required for live notifications; full-site resubmission is disabled")
    urls = changed_urls(args.since) if args.since is not None else sitemap_urls()
    if args.dry_run:
        print(f"OK: IndexNow batch contains {len(urls)} canonical URLs; key at {KEY_LOCATION}.")
        return
    if not urls:
        print("OK: no changed public HTML URLs; no IndexNow request sent.")
        return
    status = submit(urls)
    print(f"OK: IndexNow accepted {len(urls)} canonical URLs (HTTP {status}).")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
