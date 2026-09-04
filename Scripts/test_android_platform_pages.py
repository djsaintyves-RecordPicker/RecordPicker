#!/usr/bin/env python3
"""Verify localized Android pages expose accurate search metadata."""

from __future__ import annotations

from html import unescape
import json
import re

from announce_android_pc_development import BETA_COPY, COPY, ROOT


for directory in COPY:
    root = ROOT / directory if directory else ROOT
    page = root / "android-app/index.html"
    text = page.read_text(encoding="utf-8")
    route = f"{directory}/android-app" if directory else "android-app"

    assert f'<link rel="canonical" href="https://recordpicker.app/{route}/">' in text, directory
    assert f'<meta property="og:url" content="https://recordpicker.app/{route}/">' in text, directory
    assert BETA_COPY[directory][0] in text, directory
    assert BETA_COPY[directory][0] not in {"Coming soon", "Bientôt disponible"}, directory
    assert "14" in text, directory
    assert "lifetime Pro access" in text or "accès Pro à vie" in text, directory
    assert "Google%20Account%20email" in text, directory

    payload = re.search(
        r'<script type="application/ld\+json">(.*?)</script>', text, flags=re.DOTALL
    )
    assert payload, directory
    schema = json.loads(unescape(payload.group(1)))
    assert schema["@type"] == "WebPage", directory
    assert schema["url"] == f"https://recordpicker.app/{route}/", directory
    assert "primaryImageOfPage" not in schema, directory
    assert schema["about"]["@type"] == "SoftwareApplication", directory
    assert schema["about"]["operatingSystem"] == "Android", directory
    assert "downloadUrl" not in schema, directory
    assert "offers" not in schema, directory
    assert "downloadUrl" not in schema["about"], directory
    assert "offers" not in schema["about"], directory

print(f"Verified accurate Android search metadata across {len(COPY)} locales.")
