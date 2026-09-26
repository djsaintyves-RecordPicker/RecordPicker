#!/usr/bin/env python3
"""Verify only authenticated platform screenshots are published."""

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
    assert "/assets/screenshots/v26/windows/windows-random-pick-fr.webp" in windows, directory
    assert "authentic Microsoft Store capture" in windows, directory
    assert "/assets/screenshots/multiplatform/" not in windows, directory

    screenshots = (root / "screenshots/index.html").read_text(encoding="utf-8")
    assert "/assets/screenshots/v26/windows/windows-random-pick-fr.webp" in screenshots, directory
    assert "https://apps.microsoft.com/detail/9N2ZWRL4M3JC" in screenshots, directory

assert not (ROOT / "assets/screenshots/multiplatform").exists()

print(f"Verified authentic Windows screenshots and absent temporary assets across {len(COPY)} locales.")
