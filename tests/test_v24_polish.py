"""Tests v24 : interrupteurs de maîtrise / multiclassage, prise 1 main / 2 mains, purge des acquis raciaux,
Transe elfique (repos long de 4 h), retrait d'« Enfant de la lune », thèmes (police Skyrim, BG3 intact)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core import dice as D  # noqa: E402
from core.engine import Engine  # noqa: E402


def window():
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    return mw.MainWindow(DB)


class ToggleTests(unittest.TestCase):
    def test_weapon_prof_toggle(self):
        win = window()
        win.ch.armes_cac[0]["nom"] = "Épée longue"
        win.changed()
        w = win.combat_tab.weapon_rows["armes_cac"][0]
        self.assertTrue(w["prof"].text().startswith("✦") or w["prof"].text().startswith("○"))
        w["prof"].setChecked(False)
        win.combat_tab._on_weapon_prof("armes_cac", 0)
        self.assertFalse(win.engine.weapon_stats(win.ch.armes_cac[0])["maitrise"])
        self.assertEqual(w["prof"].text(), "○ Non maîtrisée")

    def test_multiclass_toggle_text(self):
        win = window()
        tab = win.classes_tab
        tab.refresh()
        self.assertIn("désactivé", tab.multi_chk.text())
        tab._on_multiclass(True)
        tab.refresh()
        self.assertIn("activé", tab.multi_chk.text())
        self.assertNotIn("désactivé", tab.multi_chk.text())


class VersatileTests(unittest.TestCase):
    def test_engine_grip(self):
        eng = Engine(DB, Engine.new_character(DB))
        eng.ch.scores_achat["Force"] = 15
        eng.normalize()
        slot = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        st = eng.weapon_stats(slot)                            # v46 : main secondaire libre -> à deux mains
        self.assertEqual((st["degats"], st["polyvalent"], st["prise"]), ("1d10+3", "1d8+3", "à deux mains"))
        eng.ch.armure["bouclier"] = True                       # bouclier : prise à une main automatique
        self.assertEqual(eng.weapon_stats(slot)["degats"], "1d8+3")
        self.assertEqual(eng.weapon_stats(slot)["prise"], "à une main")
        self.assertFalse(eng.weapon_stats(slot)["deux_mains_possible"])

    def test_ui_switch_and_roll(self):
        import ui.combat_tab as ct
        win = window()
        win.ch.armes_cac[0]["nom"] = "Bâton de combat"
        win.changed()
        w = win.combat_tab.weapon_rows["armes_cac"][0]
        self.assertEqual(w["hands"].text(), "🙌 À deux mains")      # v46 : prise automatique (main libre)
        self.assertTrue(win.combat_tab.weapon_rows["armes_cac"][0]["dmg"].formula.startswith("1d8"))
        got = []
        orig = ct.roll_damage_dialog
        self.addCleanup(lambda: setattr(ct, "roll_damage_dialog", orig))
        ct.roll_damage_dialog = lambda win_, spec: got.append(spec)
        win.combat_tab._roll_weapon_damage("armes_cac", 0)
        self.assertTrue(got[0].formula.startswith("1d8"))
        self.assertIn("deux mains", got[0].title)

    def test_grip_saved(self):
        from core.character import Character
        ch = Character()
        ch.armes_cac[0] = {"nom": "Trident", "bonus": 0, "maitrise": None, "deux_mains": True}
        self.assertTrue(Character.from_dict(ch.to_dict()).armes_cac[0]["deux_mains"])


class RaceTests(unittest.TestCase):
    def test_moonchild_removed(self):
        from core.character import Character
        self.assertNotIn("Enfant de la lune", DB.races)
        ch = Character.from_dict({"classes": [{"nom": "Guerrier", "niveau": 1}], "race": "Enfant de la lune"})
        Engine(DB, ch).normalize()
        self.assertEqual(ch.race, "Féral")

    def test_race_change_purges_grants(self):
        eng = Engine(DB, Engine.new_character(DB))
        eng.change_race("Elfe")
        self.assertIn("Elfique", eng.ch.langues_liste)
        self.assertTrue(eng.ch.competences["Perception"]["maitrise"])
        eng.change_race("Nain des collines")
        self.assertNotIn("Elfique", eng.ch.langues_liste)
        self.assertIn("Nain", eng.ch.langues_liste)
        self.assertIn("Commun", eng.ch.langues_liste)          # langue de base conservée
        self.assertFalse(eng.ch.competences["Perception"]["maitrise"])

    def test_purge_keeps_background_and_manual_skills(self):
        eng = Engine(DB, Engine.new_character(DB))
        eng.ch.competences["Perception"] = {"maitrise": True, "expertise": False}   # déjà maîtrisée avant
        eng.change_race("Elfe")
        eng.change_race("Humain")
        self.assertTrue(eng.ch.competences["Perception"]["maitrise"])          # pas accordée par la race

    def test_trance_long_rest(self):
        eng = Engine(DB, Engine.new_character(DB))
        eng.change_race("Elfe")
        self.assertEqual(eng.long_rest_minutes(), 240)
        t0 = eng.ch.temps_minutes
        eng.do_long_rest()
        self.assertEqual(eng.ch.temps_minutes - t0, 240)
        eng.change_race("Drow (Elfe noir)")
        self.assertEqual(eng.long_rest_minutes(), 240)
        eng.change_race("Humain")
        self.assertEqual(eng.long_rest_minutes(), 480)


class ThemeTests(unittest.TestCase):
    def test_skyrim_uses_bg3_font(self):
        from ui import theme
        bg3, sky = theme.THEMES["bg3"], theme.THEMES["skyrim"]
        self.assertEqual((sky.font, sky.font_title), (bg3.font, bg3.font))

    def test_bg3_untouched_and_others_polished(self):
        from ui import theme
        bg3 = theme.THEMES["bg3"]
        self.assertEqual((bg3.bg, bg3.panel, bg3.accent_text, bg3.button_bg, bg3.glow),
                         ("#181514", "#24201D", "#C5A059", "#7C2424", ""))
        self.assertEqual(theme.polish_stylesheet(bg3), "")
        for key, t in theme.THEMES.items():
            if key != "bg3":
                self.assertTrue(t.glow, key)
                self.assertIn(t.glow, theme.build_stylesheet(t), key)
            self.assertEqual(t.audit(), [], key)                 # contrastes WCAG AA, interrupteurs compris


if __name__ == "__main__":
    unittest.main()
