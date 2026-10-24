"""Tests v14 : sorts de buff (cible soi / allié, repli sur un emplacement supérieur, concentration)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB, make  # noqa: E402


class EngineBuffTests(unittest.TestCase):
    def test_self_buff_applies_and_ends_with_concentration(self):
        eng = make([("Magicien", 5, "")], **{"Dextérité": 14})
        ac, speed = eng.armor_class_detail()["valeur"], eng.speed()
        eng.cast_spell("Hâte", target="soi", effect="hate")
        self.assertEqual(eng.armor_class_detail()["valeur"], ac + 2)
        self.assertEqual(eng.speed(), speed * 2)
        self.assertEqual(eng.save_rows()[1]["etat"], "avantage")
        eng.break_concentration()
        self.assertNotIn("hate", eng.active_effect_keys())
        self.assertIn("lethargie", eng.active_effect_keys())               # fin de Hâte (PHB)

    def test_ally_buff_tracks_concentration_only(self):
        eng = make([("Clerc", 3, "")])
        res = eng.cast_spell("Bénédiction", target="allie", effect="benediction")
        self.assertTrue(res["ok"])
        self.assertEqual((eng.ch.concentration, eng.ch.concentration_cible), ("Bénédiction", "allie"))
        self.assertNotIn("benediction", eng.active_effect_keys())
        self.assertEqual(eng.save_rows()[0]["des"], [])
        self.assertEqual(eng.ch.emplacements_utilises[0], 1)

    def test_upcast_fallback(self):
        eng = make([("Clerc", 3, "")])
        eng.ch.emplacements_utilises[0] = eng.spell_slots()[0]             # plus de niveau 1
        plan = eng.slot_plan(1)
        self.assertEqual((plan["niveau"], plan["exact"]), (2, False))
        res = eng.cast_spell("Bénédiction", target="soi", effect="benediction")
        self.assertIn("niveau supérieur", res["message"])
        self.assertEqual(eng.ch.emplacements_utilises[1], 1)
        self.assertIn("benediction", eng.active_effect_keys())

    def test_buff_catalogue(self):
        eng = make([("Magicien", 5, "")])
        self.assertTrue(eng.spell_is_personal("Passage sans trace"))
        self.assertTrue(eng.spell_is_personal("Bouclier"))
        self.assertFalse(eng.spell_is_personal("Hâte"))
        self.assertEqual(len(eng.buff_options("Amélioration de caractéristique")), 6)
        self.assertEqual(eng.buff_options("Boule de feu"), [])


class UiBuffTests(unittest.TestCase):
    def test_double_click_flow(self):
        import ui.magic_tab as mt
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.classes = [{"nom": "Magicien", "niveau": 5, "sous_classe": "", "pv_jets": []}]
        win.changed()
        answers = ["Sur un allié / autre"]
        saved = (mt.ask_choice, mt.ask_yes_no)
        self.addCleanup(lambda: (setattr(mt, "ask_choice", saved[0]), setattr(mt, "ask_yes_no", saved[1])))
        mt.ask_choice = lambda *a, **k: answers.pop(0)
        self.assertTrue(win.magic_tab.cast("Hâte"))
        self.assertEqual(win.ch.concentration_cible, "allie")
        self.assertNotIn("hate", win.engine.active_effect_keys())
        win.engine.break_concentration()
        answers.append("Sur soi")
        mt.ask_yes_no = lambda *a, **k: True
        self.assertTrue(win.magic_tab.cast("Hâte"))
        self.assertIn("hate", win.engine.active_effect_keys())
        self.assertTrue(win.magic_tab.cast("Passage sans trace"))          # personnel : pas de question
        self.assertIn("passage_sans_trace", win.engine.active_effect_keys())


if __name__ == "__main__":
    unittest.main()
