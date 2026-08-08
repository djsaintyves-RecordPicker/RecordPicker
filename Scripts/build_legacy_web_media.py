#!/usr/bin/env python3
"""Build lightweight WebP derivatives for legacy screenshots still used by the site."""

from __future__ import annotations

from pathlib import Path
import re

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "assets" / "screenshots"
SOURCE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def referenced_sources() -> set[Path]:
    sources: set[Path] = set()
    pattern = re.compile(
        r'(?:\.\./)*assets/screenshots/([^"\'?#]+\.(?:png|jpe?g|webp))',
        flags=re.IGNORECASE,
    )
    for page in ROOT.rglob("*.html"):
        for relative in pattern.findall(page.read_text(encoding="utf-8")):
            referenced = SCREENSHOTS / relative
            if "v19" in referenced.parts:
                continue
            if referenced.suffix.lower() in SOURCE_SUFFIXES:
                sources.add(referenced)
                continue
            for suffix in (".png", ".jpg", ".jpeg"):
                source = referenced.with_suffix(suffix)
                if source.is_file():
                    sources.add(source)
                    break
    return sources


def convert(source: Path) -> tuple[int, int]:
    target = source.with_suffix(".webp")
    before = source.stat().st_size
    with Image.open(source) as image:
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        image.save(target, "WEBP", quality=84, method=6, exact=True)
    return before, target.stat().st_size


def main() -> None:
    count = 0
    original_bytes = 0
    webp_bytes = 0
    missing: list[Path] = []
    for source in sorted(referenced_sources()):
        if not source.is_file():
            missing.append(source)
            continue
        before, after = convert(source)
        count += 1
        original_bytes += before
        webp_bytes += after
    if missing:
        raise SystemExit("Missing referenced screenshots:\n" + "\n".join(map(str, missing)))
    saving = 100 * (1 - webp_bytes / original_bytes) if original_bytes else 0
    print(
        f"Built {count} WebP screenshots: {original_bytes / 1_000_000:.1f} MB -> "
        f"{webp_bytes / 1_000_000:.1f} MB ({saving:.1f}% smaller)."
    )


if __name__ == "__main__":
    main()
