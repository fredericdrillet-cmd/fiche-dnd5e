"""v52 : retours d'essai de l'onglet En partie — épuisement, couleurs du thème, options de classe, Sommeil, dés."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402
from ui import theme  # noqa: E402

DB = Database(ROOT / "data")


def sheet(cls="Magicien", lvl=3, sub="", edition="2014"):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    return eng


class TilePaletteTests(unittest.TestCase):
    def test_every_theme_readable_and_distinct(self):
        for t in theme.THEMES.values():
            p = theme.tile_palette(t)
            self.assertEqual(set(p), {"attaque", "capacite", "magie", "objet", "reaction", "commune"})
            self.assertEqual(len(set(p.values())), 6, t.key)
            for cat, col in p.items():
                self.assertGreaterEqual(theme.contrast_ratio(col, t.panel), 3, (t.key, cat))


class HpPoolTests(unittest.TestCase):
    def test_sleep_2014_scales_with_slot(self):
        eng = sheet()
        self.assertEqual([eng.spell_resolution("Sommeil", n)["reserve"].formula for n in (1, 2, 3)],
                         ["5d8", "7d8", "9d8"])
        self.assertEqual(eng.spell_resolution("Sommeil", 1)["mode"], "reserve")
        self.assertEqual(eng.spell_resolution("Couleurs dansantes", 2)["reserve"].formula, "8d10")

    def test_sleep_2024_is_a_save(self):
        eng = sheet(edition="2024")
        self.assertEqual(eng.spell_resolution("Sommeil (2024)", 1)["mode"], "sauvegarde")


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        cls.win = MainWindow(DB)

    def test_class_options_moved_to_classes_tab(self):
        eng = self.win.engine
        eng.ch.classes = [{"nom": "Guerrier", "niveau": 3, "sous_classe": "Maître de guerre", "pv_jets": []}]
        eng.normalize()
        self.win.changed()
        self.win.classes_tab.refresh()
        self.assertNotIn("options_box", vars(self.win.combat_tab))
        self.assertIn("Options de classe", self.win.classes_tab.options_box.title())
        self.assertIsNotNone(self.win.classes_tab._options_key)

    def test_short_common_labels(self):
        from ui.combat_tab import CombatTab
        self.assertEqual(CombatTab.SHORT_COMMON["Utiliser un objet"], "Objet")

    def test_no_dice_in_wizard(self):
        from ui.dice_dialog import roll_damage_dialog, roll_dice
        from core import dice as D

        class Host:
            no_dice = True
        self.assertIsNone(roll_dice(Host(), self.win.engine.skill_spec("Acrobaties")))
        self.assertIsNone(roll_damage_dialog(Host(), D.DamageSpec("x", "1d6")))


if __name__ == "__main__":
    unittest.main()
