#!/usr/bin/env python3
"""Verify localized Android and Windows screenshot galleries."""

from announce_android_pc_development import COPY, ROOT


for directory in COPY:
    root = ROOT / directory if directory else ROOT
    asset_locale = "fr-fr" if directory in {"fr", "fr-ca"} else "en-us"

    android = (root / "android-app/index.html").read_text(encoding="utf-8")
    assert 'class="platform-screenshot-grid android-screenshot-grid"' in android, directory
    assert android.count(f'<img src="/assets/screenshots/multiplatform/{asset_locale}/android-') == 3, directory
    assert f'/assets/screenshots/multiplatform/{asset_locale}/android-home.webp' in android, directory
    assert ('Android · fr-FR' in android) == (asset_locale == "fr-fr"), directory
    assert ('Android · en-US' in android) == (asset_locale == "en-us"), directory

    windows = (root / "windows-app/index.html").read_text(encoding="utf-8")
    assert 'class="platform-screenshot-grid windows-screenshot-grid"' in windows, directory
    assert windows.count(f'<img src="/assets/screenshots/multiplatform/{asset_locale}/windows-') == 2, directory
    assert f'/assets/screenshots/multiplatform/{asset_locale}/windows-home.webp' in windows, directory
    assert ('Windows · fr-FR' in windows) == (asset_locale == "fr-fr"), directory
    assert ('Windows · en-US' in windows) == (asset_locale == "en-us"), directory

for locale in ("en-us", "fr-fr"):
    expected = (
        "android-home.webp",
        "android-collection.webp",
        "android-random-pick.webp",
        "windows-home.webp",
        "windows-collection.webp",
    )
    for filename in expected:
        path = ROOT / "assets/screenshots/multiplatform" / locale / filename
        assert path.is_file() and path.stat().st_size > 20_000, path

print(f"Verified Android and Windows screenshot galleries across {len(COPY)} locales.")
