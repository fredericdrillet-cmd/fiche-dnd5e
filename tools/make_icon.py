"""Génère l'icône de l'application (assets/app_icon.ico et .png) : un d20 doré sur fond sombre.
Usage : python tools/make_icon.py"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"


def draw(size: int = 256) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c, r = size / 2, size * 0.46
    d.ellipse([c - r, c - r, c + r, c + r], fill=(28, 22, 18, 255), outline=(201, 162, 39, 255), width=size // 40)
    hexa = [(c + r * 0.82 * math.cos(math.radians(a)), c + r * 0.82 * math.sin(math.radians(a)))
            for a in range(-90, 270, 60)]
    d.polygon(hexa, fill=(120, 24, 24, 255), outline=(230, 190, 70, 255))
    tri = [hexa[0], hexa[2], hexa[4]]
    d.polygon(tri, outline=(230, 190, 70, 255))
    for p in hexa:
        d.line([p, (c, c)], fill=(230, 190, 70, 120), width=1)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(size * 0.24))
    except OSError:
        font = ImageFont.load_default()
    d.text((c, c + size * 0.03), "20", fill=(255, 236, 170, 255), font=font, anchor="mm")
    return img


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    img = draw()
    img.save(OUT / "app_icon.png")
    img.save(OUT / "app_icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Icône écrite dans", OUT)
