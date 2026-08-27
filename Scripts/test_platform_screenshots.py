#!/usr/bin/env python3
"""Verify temporary Android and Windows screenshots are not published."""

from announce_android_pc_development import COPY, ROOT


for directory in COPY:
    root = ROOT / directory if directory else ROOT
    android = (root / "android-app/index.html").read_text(encoding="utf-8")
    android_hero = android.split('</section>', 1)[0]
    assert '<p class="tagline">Android</p>' in android_hero, directory
    assert '<p class="deck">' not in android_hero, directory
    assert "platform-screenshot" not in android, directory
    assert "/assets/screenshots/multiplatform/" not in android, directory

    windows = (root / "windows-app/index.html").read_text(encoding="utf-8")
    assert "platform-screenshot" not in windows, directory
    assert "/assets/screenshots/multiplatform/" not in windows, directory

assert not (ROOT / "assets/screenshots/multiplatform").exists()

print(f"Verified temporary platform screenshots are absent across {len(COPY)} locales.")
