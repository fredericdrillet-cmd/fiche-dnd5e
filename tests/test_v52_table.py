"""v52 : ergonomie de table — saisie rapide des PV, historique des lancers, mode imposé, onglet En partie."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def make(cls="Guerrier", level=5):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": level, "sous_classe": "", "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    ch.pv_actuels = eng.hp_max()
    return eng


class QuickHpTests(unittest.TestCase):
    def test_damage_heal_and_temp_hp(self):
        eng = make()
        full = eng.hp_max()
        eng.ch.pv_temporaires = 3
        msg = eng.apply_hp_input("7")
        self.assertIn("3 absorbé", msg)
        self.assertEqual((eng.ch.pv_temporaires, eng.ch.pv_actuels), (0, full - 4))
        eng.apply_hp_input("-2")
        self.assertEqual(eng.ch.pv_actuels, full - 6)
        eng.apply_hp_input("+5")
        self.assertEqual(eng.ch.pv_actuels, full - 1)
        eng.apply_hp_input("4", "soins")                                  # bouton « Soins » : sens imposé
        self.assertEqual(eng.ch.pv_actuels, full)
        eng.apply_hp_input("+3", "degats")                                # bouton « Dégâts »
        self.assertEqual(eng.ch.pv_actuels, full - 3)
        self.assertEqual(eng.apply_hp_input("abc"), "")

    def test_zero_hp_and_concentration(self):
        eng = make()
        eng.ch.concentration = "Bénédiction"
        msg = eng.apply_hp_input(str(eng.hp_max() + 1))
        self.assertIn("DD", msg)
        self.assertIn("0 PV", msg)
        self.assertIn("inconscient", eng.ch.effets_actifs)
        eng.ch.mort_echecs = 2
        eng.apply_hp_input("+1")
        self.assertEqual((eng.ch.mort_echecs, "inconscient" in eng.ch.effets_actifs), (0, False))


class RollHistoryTests(unittest.TestCase):
    def test_history_capped_and_saved(self):
        eng = make()
        for i in range(55):
            eng.record_roll("Jet {}".format(i), "test", i, "d20 = {}".format(i))
        self.assertEqual(len(eng.ch.historique_jets), 50)
        self.assertEqual(eng.ch.historique_jets[0]["titre"], "Jet 54")          # le plus récent en tête
        from core.character import Character
        self.assertEqual(len(Character.from_dict(eng.ch.to_dict()).historique_jets), 50)


class TableUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        cls.win = MainWindow(DB)

    def test_tab_renamed_and_hp_entry(self):
        win = self.win
        win.engine = make()
        win.refresh_all()
        titles = [win.tabs.tabText(i) for i in range(win.tabs.count())] if hasattr(win.tabs, "tabText") else []
        tab = win.combat_tab
        tab.hp_entry.setText("-5")
        tab._quick_hp("")
        self.assertEqual(win.engine.ch.pv_actuels, win.engine.hp_max() - 5)
        win.action_hp_entry()
        self.assertIn("🎲 En partie", [t for _, (_, t) in win._tab_by_key.items()] if hasattr(win, "_tab_by_key")
                      else titles)

    def test_slot_strip_and_history_dialog(self):
        win = self.win
        win.engine = make("Magicien", 5)
        win.refresh_all()
        tab = win.combat_tab
        tab._refresh_slot_strip()
        tab._on_slot_used(0, 2)
        self.assertEqual(win.engine.ch.emplacements_utilises[0], 2)
        from ui import dice_dialog as DD
        spec = win.engine.save_spec("Dextérité")
        r = DD.roll_dice(win, spec)
        self.assertEqual(win.engine.ch.historique_jets[0]["total"], r.total)
        adv = DD.with_mode(spec, "avantage")
        self.assertEqual(adv.mode, "avantage")
        self.assertIn("Mode imposé", adv.note)
        from ui.history_dialog import HistoryDialog, history_html
        self.assertIn(spec.title, history_html(win.engine.ch.historique_jets))
        dlg = HistoryDialog(win)
        dlg.clear()
        self.assertEqual(win.engine.ch.historique_jets, [])


if __name__ == "__main__":
    unittest.main()
