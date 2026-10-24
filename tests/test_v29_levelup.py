"""Tests v29 : assistant « Niveau supérieur » (copie de travail, choix bloquants, récapitulatif) et frise 1 → 20."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core.engine import Engine  # noqa: E402
from core.levelup import roadmap_icons  # noqa: E402


def make(c, lvl, sub="", multi=False):
    eng = Engine(DB, Engine.new_character(DB))
    eng.ch.classes = [{"nom": c, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng.ch.multiclassage = multi
    eng.normalize()
    return eng


def window(eng=None):
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    win = mw.MainWindow(DB)
    if eng is not None:
        win.engine = eng
        win.refresh_all()
    return win


class EngineTests(unittest.TestCase):
    def test_options(self):
        eng = make("Guerrier", 3, "Champion")
        self.assertEqual([o["classe"] for o in eng.level_up_options()], ["Guerrier"])
        eng.ch.multiclassage = True
        opts = eng.level_up_options()
        self.assertGreater(len(opts), 1)
        self.assertTrue(all(o["nouvelle"] for o in opts[1:]))
        self.assertEqual(make("Guerrier", 20, "Champion").level_up_options(), [])

    def test_simulation_leaves_original_untouched(self):
        eng = make("Guerrier", 3, "Champion")
        sim = eng.simulate_level_up("Guerrier")
        self.assertEqual(sim.ch.find_class("Guerrier")["niveau"], 4)
        self.assertEqual(eng.ch.find_class("Guerrier")["niveau"], 3)
        self.assertIsNot(sim.ch, eng.ch)

    def test_report_inline_choices(self):
        eng = make("Guerrier", 3, "Champion")
        eng.ch.styles_combat["Guerrier|1"] = "Défense"
        rep = eng.level_up_report(eng.simulate_level_up("Guerrier"), "Guerrier")
        self.assertEqual([m["kind"] for m in rep["dans_assistant"]], ["amelioration"])
        self.assertTrue(any("Amélioration" in f["nom"] for f in rep["aptitudes"]))
        labels = [r[0] for r in rep["recap"]]
        self.assertIn("Points de vie maximum", labels)
        rep = eng.level_up_report(make("Guerrier", 2).simulate_level_up("Guerrier"), "Guerrier")
        self.assertIn("sous_classe", [m["kind"] for m in rep["dans_assistant"]])

    def test_prior_gaps_do_not_block(self):
        eng = make("Guerrier", 1)                        # style de combat jamais choisi : oubli ANTÉRIEUR
        rep = eng.level_up_report(eng.simulate_level_up("Guerrier"), "Guerrier")
        self.assertEqual(rep["dans_assistant"], [])

    def test_multiclass_prereq_and_later_choices(self):
        eng = make("Guerrier", 3, "Champion", multi=True)
        self.assertIn("Magicien demande Intelligence 13", eng.multiclass_prereq("Magicien"))
        rep = eng.level_up_report(eng.simulate_level_up("Magicien"), "Magicien")
        # v40 : le grimoire se remplit DANS l'assistant (étape « Nouveaux sorts »)
        self.assertTrue(any("grimoire" in m["message"] for m in rep["dans_assistant"] if m["kind"] == "sorts"))
        self.assertIn("Emplacements de sorts", [r[0] for r in rep["recap"]])

    def test_hp_info(self):
        eng = make("Guerrier", 3, "Champion")
        sim = eng.simulate_level_up("Guerrier")
        info = sim.level_hp_info("Guerrier")
        self.assertEqual((info["de"], info["moyenne"]), ("d10", 6))
        self.assertEqual(sim.hp_max() - eng.hp_max(), info["gain"])

    def test_roadmap(self):
        eng = make("Magicien", 5)
        road = eng.class_roadmap(eng.ch.classes[0])
        self.assertEqual(len(road), 20)
        self.assertIn("▲", roadmap_icons(road[3]))          # niveau 4 : amélioration ou don
        self.assertIn("◆", roadmap_icons(road[1]))          # niveau 2 : sous-classe du magicien
        self.assertIn("✧", roadmap_icons(road[2]))          # niveau 3 : sorts de niveau 2
        self.assertTrue(road[4]["actuel"])
        self.assertFalse(road[5]["atteint"])


class DialogTests(unittest.TestCase):
    def test_confirm_locked_until_choice_then_applied(self):
        from ui.levelup_dialog import LevelUpDialog, apply_level_up
        eng = make("Guerrier", 3, "Champion")
        eng.ch.styles_combat["Guerrier|1"] = "Défense"
        eng.normalize()
        win = window(eng)
        dlg = LevelUpDialog(win)
        self.assertEqual(len(dlg.pending()), 1)
        sid = dlg._new_asi_slots()[0]["id"]
        dlg.sim.ch.ameliorations[sid] = {"mode": "plus2", "a1": "Force"}
        dlg._changed()
        self.assertEqual(dlg.pending(), [])
        self.assertEqual(win.ch.find_class("Guerrier")["niveau"], 3)      # rien d'appliqué avant confirmation
        dlg._on_confirm()
        apply_level_up(win, dlg.sim, dlg.cls)
        self.assertEqual(win.ch.find_class("Guerrier")["niveau"], 4)
        self.assertEqual(win.ch.ameliorations[sid]["a1"], "Force")
        self.assertTrue(win._dirty)

    def test_subclass_choice_in_wizard(self):
        from ui.levelup_dialog import LevelUpDialog
        win = window(make("Guerrier", 2))
        dlg = LevelUpDialog(win)
        self.assertIn("sous_classe", [m["kind"] for m in dlg.pending()])
        dlg._set_sub("Champion")
        self.assertNotIn("sous_classe", [m["kind"] for m in dlg.pending()])
        self.assertEqual(win.ch.find_class("Guerrier")["sous_classe"], "")

    def test_class_switch_rebuilds_copy(self):
        from ui.levelup_dialog import LevelUpDialog
        win = window(make("Guerrier", 3, "Champion", multi=True))
        dlg = LevelUpDialog(win)
        idx = next(i for i, o in enumerate(dlg.options) if o["classe"] == "Magicien")
        dlg.class_combo.setCurrentIndex(idx)
        dlg._on_class(idx)
        self.assertEqual(dlg.cls, "Magicien")
        self.assertIsNotNone(dlg.sim.ch.find_class("Magicien"))
        self.assertIsNone(win.ch.find_class("Magicien"))

    def test_roadmap_in_classes_tab(self):
        win = window(make("Magicien", 5))
        win.classes_tab.refresh()
        panel = win.classes_tab.panels[0]
        self.assertIn("▲", panel.roadmap.cells[3].text())


if __name__ == "__main__":
    unittest.main()
