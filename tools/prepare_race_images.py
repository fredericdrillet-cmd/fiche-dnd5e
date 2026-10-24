#!/usr/bin/env python3
"""
Prépare les illustrations de races pour l'onglet Race (cadre carré 8 cm × 8 cm).

Chaque image est :
    - redressée selon son orientation EXIF ;
    - recadrée au CENTRE en carré parfait (aucune déformation : équivalent « object-fit: cover ») ;
    - mise à l'échelle commune SIZE × SIZE (512 px par défaut : net à 8 cm sur écran 96 dpi comme en 150 %) ;
    - enregistrée en PNG si elle a un fond transparent (détourage conservé), sinon en JPEG qualité 90 ;
    - renommée selon la convention « nom-de-la-race.ext » (minuscules, sans accents, tirets).

    python tools/prepare_race_images.py <dossier_source> [data/images/races] [--size 512]

L'application retrouve ensuite l'image d'après le nom de la race (voir core/race_images.py) ; elle accepte aussi
des fichiers non préparés (.png, .jpg, .jpeg, .webp) et les recadre à l'affichage.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.race_images import IMAGE_EXTS, file_slug  # noqa: E402

# noms de fichiers source -> nom cible (sous-espèces, variantes d'orthographe)
RENAME = {"elfe-sylvestre": "elfe-des-bois"}


def prepare(src: Path, dst: Path, size: int = 512) -> list[str]:
    from PIL import Image, ImageOps
    dst.mkdir(parents=True, exist_ok=True)
    report = []
    for path in sorted(src.iterdir()):
        if path.suffix.lower() not in IMAGE_EXTS:
            continue
        im = ImageOps.exif_transpose(Image.open(path))
        w, h = im.size
        side = min(w, h)
        im = im.crop(((w - side) // 2, (h - side) // 2, (w - side) // 2 + side, (h - side) // 2 + side))
        im = im.resize((size, size), Image.Resampling.LANCZOS)
        alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        if alpha:
            im = im.convert("RGBA")
            alpha = im.getchannel("A").getextrema()[0] < 250          # vraie transparence (détourage)
        name = RENAME.get(file_slug(path.stem), file_slug(path.stem))
        for old in dst.glob(name + ".*"):
            old.unlink()
        if alpha:
            out = dst / (name + ".png")
            im.save(out, optimize=True)
        else:
            out = dst / (name + ".jpg")
            im.convert("RGB").save(out, quality=90, optimize=True, progressive=True)
        note = " (agrandie depuis {} px : un peu moins nette)".format(side) if side < size else ""
        report.append("{} -> {} ({}×{}){}".format(path.name, out.name, size, size, note))
    return report


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 1
    size = int(argv[argv.index("--size") + 1]) if "--size" in argv else 512
    src = Path(args[0])
    dst = Path(args[1]) if len(args) > 1 else ROOT / "data" / "images" / "races"
    for line in prepare(src, dst, size):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
