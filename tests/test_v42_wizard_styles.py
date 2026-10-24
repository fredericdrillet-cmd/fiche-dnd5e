"""Tests v42 : fenêtre « Niveau supérieur » redimensionnée et styles de combat expliqués (survol + sélection)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from test_v40_wizard_saves import make  # noqa: E402
from test_v41_grimoire_combat import window  # noqa: E402
from core.fighting_styles import APPLIED, STYLES  # noqa: E402


class StyleTextTests(unittest.TestCase):
    def test_full_texts_for_every_data_style(self):
        names = {n for d in DB.styles_by_class.values() for n in d}
        missing = sorted(n for n in names if n not in STYLES)
        self.assertEqual(missing, [])
        self.assertIn("réaction", DB.style_description("Guerrier", "Protection"))
        self.assertIn("bouclier", DB.style_description("Guerrier", "Protection"))
        self.assertIn("1d10 + votre bonus de maîtrise", DB.style_description("Guerrier", "Interception"))
        self.assertTrue(set(APPLIED) <= set(STYLES))


class WizardStyleTests(unittest.TestCase):
    def test_style_card_tooltips_and_summary(self):
        from ui.levelup_dialog import LevelUpDialog
        eng = make("Paladin", 1, "")
        d = LevelUpDialog(window(eng))
        slot = d._new_style_slots()[0]
        self.assertIn("style:" + slot["id"], d.choice_widgets)
        self.assertIn(slot["id"], d.style_labels)
        tip = d.style_tip(slot["classe"], "Défense")
        self.assertIn("+1 à la CA", tip)
        self.assertIn("Sur la fiche", tip)
        d._set_style(slot["id"], "Défense")
        self.assertEqual(d.sim.ch.styles_combat[slot["id"]], "Défense")
        self.assertIn("Style choisi", d._style_html(slot["classe"], "Défense", "✔ Style choisi :"))

    def test_dialog_has_resize_and_scroll_pages(self):
        src = (ROOT / "ui" / "levelup_dialog.py").read_text(encoding="utf-8")
        self.assertIn("QSizeGrip(card)", src)
        self.assertIn("_fit_to_screen", src)
        self.assertGreaterEqual(src.count("self._scroll_page("), 4)     # pages 1, 2, 4 et 5 défilantes


if __name__ == "__main__":
    unittest.main()
