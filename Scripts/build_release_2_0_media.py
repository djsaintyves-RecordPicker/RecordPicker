#!/usr/bin/env python3
"""Stage clean functional 2.0 screenshots and build responsive derivatives."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = (
    ROOT.parent
    / "RecordPicker"
    / "build"
    / "AppStoreSubmission"
    / "2.0-20260809-v2"
)
DESTINATION = ROOT / "assets" / "screenshots" / "v20"

APP_TO_SITE_LOCALE = {
    "ar-SA": "ar", "ca": "ca", "da": "da", "de-DE": "de", "el": "el",
    "en-AU": "en-au", "en-CA": "en-ca", "en-GB": "en-gb", "en-US": "en-us",
    "es-ES": "es-es", "es-MX": "es-mx", "fi": "fi", "fr-CA": "fr-ca",
    "fr-FR": "fr", "he": "he", "hi": "hi", "id": "id", "it": "it",
    "ja": "ja", "ko": "ko", "nl-NL": "nl", "no": "nb", "pl": "pl",
    "pt-BR": "pt-br", "pt-PT": "pt-pt", "ru": "ru", "sv": "sv",
    "th": "th", "tr": "tr", "vi": "vi", "zh-Hans": "zh-hans",
    "zh-Hant": "zh-hant",
}

MAC_OUTPUTS = {
    1: "mac-home.jpeg", 2: "mac-collection.jpeg",
    3: "mac-todays-pick.jpeg", 4: "mac-mood-pick.jpeg",
    5: "mac-random-pick.jpeg", 6: "mac-data-quality.jpeg",
}
MOBILE_OUTPUTS = {
    1: "random-pick.png", 2: "todays-pick.png",
    3: "mood-pick.png", 4: "collection.png",
}


def one_match(directory: Path, pattern: str) -> Path | None:
    matches = sorted(directory.glob(pattern))
    if len(matches) > 1:
        raise RuntimeError(f"Ambiguous screenshot source: {directory / pattern}")
    return matches[0] if matches else None


def submission_sources() -> dict[str, dict[str, tuple[Path, tuple[int, int]]]]:
    sources: dict[str, dict[str, tuple[Path, tuple[int, int]]]] = {}
    for app_locale, site_locale in APP_TO_SITE_LOCALE.items():
        localized: dict[str, tuple[Path, tuple[int, int]]] = {}
        mac_dir = SUBMISSION / "macos" / "screenshots" / app_locale
        for index, output in MAC_OUTPUTS.items():
            source = one_match(mac_dir, f"{index:02d}-*-1440x900.jpeg")
            if source:
                localized[output] = (source, (1440, 900))

        ios_dir = SUBMISSION / "ios" / "screenshots" / app_locale
        for platform, size in (("iphone", (1320, 2868)), ("ipad", (2064, 2752))):
            for index, feature in MOBILE_OUTPUTS.items():
                source = one_match(ios_dir, f"{platform}-{index:02d}-*.png")
                if source:
                    localized[f"{platform}-{feature}"] = (source, size)

        watch = SUBMISSION / "watch" / "screenshots" / app_locale / "01-record-picker-watch.png"
        if watch.is_file():
            localized["watch-random-pick.png"] = (watch, (368, 448))
        sources[site_locale] = localized
    return sources


SOURCES = submission_sources()


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
