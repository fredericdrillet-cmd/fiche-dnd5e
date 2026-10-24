"""Tests v13 : sort Métamorphose sur soi (moteur de la Forme sauvage, 6 caractéristiques remplacées,
concentration, PV tampon, sélecteur de bêtes partagé)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB, make  # noqa: E402


def wizard():
    eng = make([("Magicien", 9, "")], Intelligence=18, Sagesse=12)
    eng.ch.pv_actuels = 40
    return eng


class PolymorphTests(unittest.TestCase):
    def test_all_six_scores_replaced_and_restored(self):
        eng = wizard()
        res = eng.cast_polymorph("Ours brun")
        self.assertTrue(res["ok"])
        self.assertEqual(eng.ch.forme_type, "metamorphose")
        self.assertEqual((eng.score("Force"), eng.score("Intelligence"), eng.score("Charisme")), (19, 2, 7))
        self.assertEqual(eng.ch.forme_pv, 34)
        self.assertIn("metamorphose", eng.active_effect_keys())
        self.assertEqual(eng.ch.emplacements_utilises[3], 1)               # emplacement de niveau 4
        self.assertTrue(eng.spells_blocked())
        self.assertFalse(any(r["maitrise"] for r in eng.save_rows()))
        eng.end_form()
        self.assertEqual(eng.score("Intelligence"), 18)
        self.assertEqual(eng.ch.concentration, "")                         # fin de forme = fin du sort

    def test_concentration_rules(self):
        eng = wizard()
        eng.cast_spell("Flou")
        eng.cast_polymorph("Loup")
        self.assertEqual(eng.ch.concentration, "Métamorphose")             # Flou est rompu
        self.assertIn("JS de Constitution DD 10", eng.damage_form(4))
        eng.break_concentration()                                          # concentration perdue -> forme perdue
        self.assertEqual(eng.ch.forme_active, "")

    def test_overflow_and_limits(self):
        eng = wizard()
        for b in DB.beasts.values():                                        # FP > niveau : interdit
            if b["fp"] > eng.total_level:
                self.assertFalse(eng.polymorph_status(b["nom"])[0])
        eng.cast_polymorph("Loup")                                         # 11 PV
        msg = eng.damage_form(15)
        self.assertIn("Métamorphose prend fin", msg)
        self.assertEqual(eng.ch.pv_actuels, 36)
        self.assertEqual(eng.ch.forme_active, "")

    def test_wild_shape_unchanged(self):
        eng = make([("Druide", 4, "")], Sagesse=16)
        eng.assume_form("Loup")
        self.assertEqual(eng.ch.forme_type, "sauvage")
        self.assertEqual(eng.score("Sagesse"), 16)                         # druide : mentales conservées

    def test_picker_dialog_and_banner(self):
        import ui.main_window as mw
        from ui.druid_tab import BeastPickerDialog
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.classes = [{"nom": "Magicien", "niveau": 9, "sous_classe": "", "pv_jets": []}]
        win.changed()
        dlg = BeastPickerDialog(win, "Métamorphose", win.engine.polymorph_status)
        self.assertTrue(dlg._rows)
        win.engine.cast_polymorph("Ours brun")
        win.changed()
        self.assertIn("Métamorphose (Ours brun)", win.form_label.text())


if __name__ == "__main__":
    unittest.main()
