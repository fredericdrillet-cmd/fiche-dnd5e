"""Tests v23 : illustrations de races 8 cm × 8 cm (format, recherche par nom, mise à jour, image absente)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core import race_images as RI  # noqa: E402


class ImageFilesTests(unittest.TestCase):
    def test_all_images_same_square_size(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow absent")
        files = [p for p in RI.DEFAULT_DIR.iterdir() if p.suffix.lower() in RI.IMAGE_EXTS]
        self.assertGreaterEqual(len(files), 70)
        sizes = set()
        for p in files:
            with Image.open(p) as im:
                sizes.add(im.size)
        self.assertEqual(sizes, {(512, 512)})                       # même échelle pour toutes les races
        for p in files:
            self.assertEqual(p.stem, RI.file_slug(p.stem))           # convention « nom-de-la-race »

    def test_every_race_found_except_known(self):
        missing = [r for r in DB.race_names() if RI.find_race_image(r) is None]
        self.assertEqual(missing, [])                                # v24 : « Enfant de la lune » retiré

    def test_lookup_rules(self):
        self.assertEqual(RI.find_race_image("Drow (Elfe noir)").name, "drow.jpg")
        self.assertEqual(RI.find_race_image("Genasi d'air").name, "genasi-d-air.jpg")     # « Génasi » dans le fichier
        self.assertEqual(RI.find_race_image("Halfelin Pied-léger").name, "halfelin-pied-leger.png")
        self.assertEqual(RI.find_race_image("Myconide éveillé").name, "myconide.jpg")
        self.assertEqual(RI.find_race_image("Elfe", "Elfe des bois").name, "elfe-des-bois.png")
        self.assertEqual(RI.find_race_image("Elfe", "Haut-elfe").name, "elfe.jpg")
        self.assertIsNone(RI.find_race_image(""))

    def test_extensions_and_custom_folder(self):
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        (tmp / "Génasi d'air.JPEG").write_bytes(b"x")
        (tmp / "orc.png").write_bytes(b"x")
        (tmp / "orc.jpg").write_bytes(b"x")
        self.assertEqual(RI.find_race_image("Genasi d'air", folder=tmp).name, "Génasi d'air.JPEG")
        self.assertEqual(RI.find_race_image("Orc", folder=tmp).suffix, ".png")              # PNG prioritaire


class WidgetTests(unittest.TestCase):
    def test_fixed_8cm(self):
        from ui.race_portrait import FRAME, RaceIllustration, cm_to_px
        self.assertEqual(cm_to_px(8, 96), 302)
        self.assertEqual(cm_to_px(8, 144), 454)
        w = RaceIllustration()
        self.assertEqual(w.side, 302)                                 # stub : 96 dpi
        self.assertEqual(FRAME, 16)

    def test_race_tab_updates(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        tab = win.race_tab
        win.ch.race = "Drow (Elfe noir)"
        tab.refresh()
        self.assertEqual(tab.portrait.path.name, "drow.jpg")
        win.ch.race, win.ch.sous_race = "Elfe", "Elfe des bois"
        tab.refresh()
        self.assertEqual(tab.portrait.path.name, "elfe-des-bois.png")
        win.ch.race, win.ch.sous_race = "Race inconnue", ""
        tab.refresh()
        self.assertIsNone(tab.portrait.path)                          # médaillon de remplacement
        self.assertFalse(tab.portrait.has_image())


if __name__ == "__main__":
    unittest.main()
