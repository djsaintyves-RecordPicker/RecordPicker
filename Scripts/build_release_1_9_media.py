#!/usr/bin/env python3
"""Build responsive website derivatives and the Record Picker 1.9 social card."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "assets" / "screenshots" / "v19" / "en-us"
SOCIAL = ROOT / "assets" / "social"
PUBLICATION_IMAGES = (
    SCREENSHOTS / "iphone-today-pick.png",
    SCREENSHOTS / "ipad-collection-grid.png",
    SCREENSHOTS / "mac-today-pick.png",
)


def save_derivatives(source: Path) -> None:
    image = Image.open(source)
    # Keep the rounded-window transparency from the source PNG. Flattening to
    # RGB turned transparent Mac corners black in the AVIF/WebP selected by
    # modern browsers, even though the PNG fallback was correct.
    image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
    image.save(source.with_suffix(".webp"), "WEBP", quality=84, method=6)
    image.save(source.with_suffix(".avif"), "AVIF", quality=62, speed=6)
    source_has_transparency = (
        "A" in image.getbands() and image.getchannel("A").getextrema()[0] < 255
    )
    if source_has_transparency:
        for suffix in (".webp", ".avif"):
            derivative = Image.open(source.with_suffix(suffix))
            if (
                "A" not in derivative.getbands()
                or derivative.getchannel("A").getextrema()[0] == 255
            ):
                raise RuntimeError(
                    f"{source.with_suffix(suffix).name} lost source transparency"
                )


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        Path("/System/Library/Fonts/SFNS.ttf"),
        Path("/System/Library/Fonts/SFNSDisplay.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") if bold
        else Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    )
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def cover_fit(source: Image.Image, size: tuple[int, int]) -> Image.Image:
    result = source.copy()
    result.thumbnail(size, Image.Resampling.LANCZOS)
    return result


def rounded_image(source: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, source.width, source.height), radius=radius, fill=255
    )
    result = Image.new("RGBA", source.size)
    result.paste(source.convert("RGBA"), mask=mask)
    return result


def paste_card(
    canvas: Image.Image,
    source: Image.Image,
    position: tuple[int, int],
    radius: int,
) -> None:
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_card = Image.new("RGBA", source.size, (17, 17, 20, 95))
    shadow.alpha_composite(
        rounded_image(shadow_card, radius), (position[0] + 8, position[1] + 14)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(rounded_image(source, radius), position)


def build_social_card() -> None:
    width, height = 1200, 630
    canvas = Image.new("RGBA", (width, height), "white")
    pixels = canvas.load()
    for y in range(height):
        for x in range(width):
            red_glow = max(0.0, 1.0 - ((x - 955) ** 2 + (y - 120) ** 2) ** 0.5 / 720)
            blue_glow = max(0.0, 1.0 - ((x - 860) ** 2 + (y - 590) ** 2) ** 0.5 / 800)
            pixels[x, y] = (
                255,
                int(255 - 17 * red_glow - 5 * blue_glow),
                int(255 - 10 * red_glow),
                255,
            )

    draw = ImageDraw.Draw(canvas)
    icon = Image.open(ROOT / "assets" / "brand" / "icon-512.png").convert("RGBA")
    icon.thumbnail((82, 82), Image.Resampling.LANCZOS)
    canvas.alpha_composite(rounded_image(icon, 18), (72, 68))
    draw.text((176, 76), "Record Picker", fill="#111114", font=font(42, bold=True))
    draw.rounded_rectangle((72, 196, 198, 242), radius=23, fill="#ff2d55")
    draw.text((97, 203), "v1.9", fill="white", font=font(25, bold=True))
    draw.text((72, 276), "Today Pick", fill="#111114", font=font(74, bold=True))
    draw.text((72, 374), "A timely reason to listen.", fill="#6f6f76", font=font(31))
    draw.text((72, 434), "Private by design. Native on Apple platforms.", fill="#6f6f76", font=font(25))

    mac = Image.open(SCREENSHOTS / "mac-today-pick.png").convert("RGB")
    mac = cover_fit(mac, (670, 470))
    phone = Image.open(SCREENSHOTS / "iphone-today-pick.png").convert("RGB")
    phone = cover_fit(phone, (230, 500))
    paste_card(canvas, mac, (555, 105), 24)
    paste_card(canvas, phone, (955, 72), 32)

    SOCIAL.mkdir(parents=True, exist_ok=True)
    flattened = Image.new("RGB", canvas.size, "white")
    flattened.paste(canvas, mask=canvas.getchannel("A"))
    flattened.save(SOCIAL / "social-v19.jpg", "JPEG", quality=88, optimize=True)
    flattened.save(SOCIAL / "social-v19.webp", "WEBP", quality=84, method=6)
    flattened.save(SOCIAL / "social-v19.avif", "AVIF", quality=62, speed=6)


def main() -> None:
    missing = [path for path in PUBLICATION_IMAGES if not path.is_file()]
    if missing:
        raise SystemExit("Missing source screenshot(s): " + ", ".join(map(str, missing)))
    for source in PUBLICATION_IMAGES:
        save_derivatives(source)
    build_social_card()
    print("Built responsive 1.9 screenshots and 1200 × 630 social artwork.")


if __name__ == "__main__":
    main()
