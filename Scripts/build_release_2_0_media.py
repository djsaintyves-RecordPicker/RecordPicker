#!/usr/bin/env python3
"""Stage clean functional 2.0 screenshots and build responsive derivatives."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
APP_ASSETS = ROOT.parent / "RecordPicker" / "AppStoreAssets" / "2.0"
WATCH_ASSETS = ROOT.parent / "RecordPicker" / "build" / "AppStoreSubmission" / "2.0-20260809-v2" / "watch" / "screenshots"
DESTINATION = ROOT / "assets" / "screenshots" / "v20"

SOURCES = {
    "en-us": {
        "iphone-random-pick.png": (APP_ASSETS / "iOS/en-US/01-random-pick.png", (1320, 2868)),
        "iphone-todays-pick.png": (APP_ASSETS / "iOS/en-US/02-todays-pick.png", (1320, 2868)),
        "iphone-mood-pick.png": (APP_ASSETS / "iOS/en-US/03-mood-pick.png", (1320, 2868)),
        "iphone-collection.png": (APP_ASSETS / "iOS/en-US/04-collection.png", (1320, 2868)),
        "ipad-random-pick.png": (APP_ASSETS / "iPadOS/en-US/01-random-pick.png", (2064, 2752)),
        "ipad-todays-pick.png": (APP_ASSETS / "iPadOS/en-US/02-todays-pick.png", (2064, 2752)),
        "ipad-mood-pick.png": (APP_ASSETS / "iPadOS/en-US/03-mood-pick.png", (2064, 2752)),
        "ipad-collection.png": (APP_ASSETS / "iPadOS/en-US/04-collection.png", (2064, 2752)),
        "mac-home.jpeg": (APP_ASSETS / "macOS/en-US/01-record-picker-2.0-1440x900.jpeg", (1440, 900)),
        "mac-collection.jpeg": (APP_ASSETS / "macOS/en-US/02-collection-1440x900.jpeg", (1440, 900)),
        "mac-todays-pick.jpeg": (APP_ASSETS / "macOS/en-US/03-todays-pick-1440x900.jpeg", (1440, 900)),
        "mac-mood-pick.jpeg": (APP_ASSETS / "macOS/en-US/04-mood-pick-1440x900.jpeg", (1440, 900)),
        "mac-random-pick.jpeg": (APP_ASSETS / "macOS/en-US/05-random-pick-1440x900.jpeg", (1440, 900)),
        "mac-data-quality.jpeg": (APP_ASSETS / "macOS/en-US/06-data-quality-1440x900.jpeg", (1440, 900)),
        "watch-random-pick.png": (WATCH_ASSETS / "en-US/01-record-picker-watch.png", (368, 448)),
    },
    "fr": {
        "iphone-random-pick.png": (APP_ASSETS / "iOS/fr-FR/01-tirage.png", (1320, 2868)),
        "iphone-todays-pick.png": (APP_ASSETS / "iOS/fr-FR/02-disque-du-jour.png", (1320, 2868)),
        "iphone-mood-pick.png": (APP_ASSETS / "iOS/fr-FR/03-mood-pick.png", (1320, 2868)),
        "iphone-collection.png": (APP_ASSETS / "iOS/fr-FR/04-collection.png", (1320, 2868)),
        "ipad-random-pick.png": (APP_ASSETS / "iPadOS/fr-FR/01-tirage.png", (2064, 2752)),
        "ipad-todays-pick.png": (APP_ASSETS / "iPadOS/fr-FR/02-disque-du-jour.png", (2064, 2752)),
        "mac-home.jpeg": (APP_ASSETS / "macOS/fr-FR/01-record-picker-2.0-1440x900.jpeg", (1440, 900)),
        "mac-collection.jpeg": (APP_ASSETS / "macOS/fr-FR/02-collection-1440x900.jpeg", (1440, 900)),
        "mac-todays-pick.jpeg": (APP_ASSETS / "macOS/fr-FR/03-disque-du-jour-1440x900.jpeg", (1440, 900)),
    },
}

for site_locale, app_locale, stems in (
    ("de", "de-DE", ("01-zufall", "02-platte-des-tages")),
    ("es-es", "es-ES", ("01-sorteo", "02-disco-del-dia")),
    ("ja", "ja", ("01-random", "02-today")),
    ("zh-hans", "zh-Hans", ("01-random", "02-today")),
):
    SOURCES[site_locale] = {
        "iphone-random-pick.png": (APP_ASSETS / f"iOS/{app_locale}/{stems[0]}.png", (1320, 2868)),
        "iphone-todays-pick.png": (APP_ASSETS / f"iOS/{app_locale}/{stems[1]}.png", (1320, 2868)),
    }


def main() -> None:
    count = 0
    for locale, sources in SOURCES.items():
        locale_destination = DESTINATION / locale
        locale_destination.mkdir(parents=True, exist_ok=True)
        for output_name, (source, expected_size) in sources.items():
            if not source.is_file():
                raise RuntimeError(f"Missing functional 2.0 screenshot: {source}")
            if any(word in source.name.casefold() for word in ("tutorial", "onboarding", "guide")):
                raise RuntimeError(f"Tutorial imagery is forbidden on the site: {source}")
            with Image.open(source) as candidate:
                if candidate.size != expected_size:
                    raise RuntimeError(
                        f"Unexpected screenshot size for {source}: {candidate.size} != {expected_size}"
                    )
            destination = locale_destination / output_name
            with Image.open(source) as image:
                image = image.convert("RGB")
                image.save(destination.with_suffix(".webp"), "WEBP", quality=84, method=6)
                image.save(destination.with_suffix(".avif"), "AVIF", quality=62, speed=6)
            count += 1
    print(f"Staged {count} clean functional 2.0 screenshots with AVIF and WebP derivatives.")


if __name__ == "__main__":
    main()
