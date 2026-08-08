#!/usr/bin/env python3
"""Stage clean functional 2.0 screenshots and build responsive derivatives."""

from __future__ import annotations

from pathlib import Path
import shutil

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
APP_ASSETS = ROOT.parent / "RecordPicker" / "AppStoreAssets" / "2.0"
DESTINATION = ROOT / "assets" / "screenshots" / "v20" / "en-us"

SOURCES = {
    "iphone-todays-pick.png": (
        APP_ASSETS / "iOS" / "en-US" / "02-todays-pick.png",
        (1320, 2868),
    ),
    "ipad-todays-pick.png": (
        APP_ASSETS / "iPadOS" / "en-US" / "02-todays-pick.png",
        (2064, 2752),
    ),
    "mac-three-ways.jpeg": (
        APP_ASSETS / "macOS" / "en-US" / "01-record-picker-2.0-1440x900.jpeg",
        (1440, 900),
    ),
}


def main() -> None:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for output_name, (source, expected_size) in SOURCES.items():
        if not source.is_file():
            raise RuntimeError(f"Missing functional 2.0 screenshot: {source}")
        if any(word in source.name.casefold() for word in ("tutorial", "onboarding", "guide")):
            raise RuntimeError(f"Tutorial imagery is forbidden on the site: {source}")
        with Image.open(source) as candidate:
            if candidate.size != expected_size:
                raise RuntimeError(
                    f"Unexpected screenshot size for {source}: {candidate.size} != {expected_size}"
                )
        destination = DESTINATION / output_name
        shutil.copy2(source, destination)
        with Image.open(destination) as image:
            image = image.convert("RGB")
            image.save(destination.with_suffix(".webp"), "WEBP", quality=84, method=6)
            image.save(destination.with_suffix(".avif"), "AVIF", quality=62, speed=6)
    print("Staged three clean functional 2.0 screenshots with AVIF and WebP derivatives.")


if __name__ == "__main__":
    main()
