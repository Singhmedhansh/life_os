from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Pillow is required. Install with: pip install pillow")


def make_icon(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    size = (256, 256)
    img = Image.new("RGBA", size, (10, 132, 255, 255))
    draw = ImageDraw.Draw(img)

    # Subtle diagonal accent
    draw.rectangle([(0, 0), (256, 256)], fill=(10, 132, 255, 255))
    draw.polygon([(0, 200), (0, 256), (256, 56), (256, 0)], fill=(255, 255, 255, 40))

    # Text overlay
    try:
        font = ImageFont.truetype("arial.ttf", 96)
    except Exception:
        font = ImageFont.load_default()

    text = "LO"
    # textbbox works across Pillow versions
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pos = ((size[0] - tw) / 2, (size[1] - th) / 2 - 8)
    draw.text(pos, text, fill=(255, 255, 255, 240), font=font)

    # Save multi-size ICO
    img.save(output, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])


def main() -> None:
    out = Path("assets/life_os.ico").resolve()
    make_icon(out)
    print(f"Icon written to {out}")


if __name__ == "__main__":
    main()
