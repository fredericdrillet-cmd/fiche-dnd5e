"""Tests v51 : multiclassage sans blocage (« Choix du niveau » calculé pour la classe montée), en-tête épuré,
encarts de combat de même hauteur, onglet Caractéristiques & Compétences compact."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v40_wizard_saves import full_spells, make  # noqa: E402
from test_v41_grimoire_combat import window  # noqa: E402


def warlock(cha=6, force=0):
    eng = make("Occultiste", 1)
    eng.ch.bonus_divers["Charisme"] = cha
    eng.ch.bonus_divers["Force"] = force
    full_spells(eng, "Occultiste")
    eng.normalize()
    return eng


def dialog(eng, free=False, cls="Paladin"):
    from ui.levelup_dialog import LevelUpDialog
    win = window(eng)
    win.settings["mode_libre"] = free
    dlg = LevelUpDialog(win)
    idx = next((i for i, o in enumerate(dlg.options) if o["classe"] == cls), None)
    if idx is not None:
        dlg.class_combo.setCurrentIndex(idx)
        dlg._on_class(idx)
    return dlg, idx


class MulticlassBugTests(unittest.TestCase):
    def test_warlock_to_paladin_no_phantom_choice(self):
        dlg, idx = dialog(warlock(cha=6, force=6))               # prérequis remplis
        self.assertIsNotNone(idx)
        self.assertEqual(dlg.pending(), [])
        dlg._refresh_steps()
        items = dlg.step_list._st["items"]
        self.assertEqual(items[3], "✔ 4. Choix du niveau")         # compteur à 0, pas de « (1) »

    def test_unmet_prereq_not_offered_in_guided_mode(self):
        dlg, idx = dialog(warlock(cha=6, force=0))               # Force 13 manquante
        self.assertIsNone(idx)
        self.assertIn("Paladin", dlg.locked_label.text())
        self.assertFalse(any(m.get("kind") == "prerequis" for m in dlg.pending()))

    def test_free_mode_allows_with_warning(self):
        dlg, idx = dialog(warlock(cha=6, force=0), free=True)
        self.assertIsNotNone(idx)
        self.assertEqual(dlg.pending(), [])
        self.assertIn("Prérequis", dlg.prereq.text())

    def test_choices_counted_for_raised_class_only(self):
        eng = warlock(cha=6, force=6)
        self.assertTrue(eng._concerns_class({"kind": "style", "message": "Style de combat à choisir (Guerrier)"},
                                            "Guerrier"))
        self.assertFalse(eng._concerns_class({"kind": "style", "message": "Style de combat à choisir (Guerrier)"},
                                             "Paladin"))
        self.assertFalse(eng._concerns_class({"kind": "sorts", "message": "Occultiste : 1 sort connu à choisir"},
                                             "Paladin"))
        self.assertTrue(eng._concerns_class({"kind": "sorts", "message": "Paladin : 2 sorts…"}, "Paladin"))
        self.assertFalse(eng._concerns_class({"kind": "pacte", "message": "Pacte à choisir"}, "Paladin"))
        dlg, _ = dialog(warlock(cha=6), cls="Occultiste")        # Occultiste 2 : manifestations comptées
        self.assertTrue(any(m.get("kind") == "manifestations" for m in dlg.pending()))


class LayoutTests(unittest.TestCase):
    def test_header_without_speed_and_proficiency(self):
        win = window(make("Guerrier", 1))
        self.assertEqual(set(win.badges), {"pv", "ca", "init"})

    def test_combat_stat_boxes_same_height(self):
        src = (ROOT / "ui" / "combat_tab.py").read_text(encoding="utf-8")
        self.assertIn("box.setFixedHeight(self.STAT_BOX_HEIGHT)", src)
        win = window(make("Guerrier", 1))
        self.assertEqual(set(win.combat_tab.stat_boxes), {"init", "vit", "prof", "perc", "vision"})

    def test_stats_tab_compact(self):
        stats = (ROOT / "ui" / "stats_tab.py").read_text(encoding="utf-8")
        self.assertNotIn("Valeurs choisies dans l'assistant de création ; les améliorations passent \"\n", stats)
        self.assertNotIn("summary_note", stats)
        skills = (ROOT / "ui" / "skills_tab.py").read_text(encoding="utf-8")
        self.assertIn("row_h=26 if compact else 32", skills)


if __name__ == "__main__":
    unittest.main()
