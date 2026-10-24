"""Tests v10 : lancer de d20 animé (logique du tirage, bonus / malus, critiques, fenêtre)."""
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from core import dice as D  # noqa: E402
from test_v5_features import DB, make  # noqa: E402


class FixedRng:
    def __init__(self, values):
        self.values = list(values)

    def randint(self, a, b):
        return self.values.pop(0)


class DiceLogicTests(unittest.TestCase):
    def test_modes_and_criticals(self):
        spec = D.RollSpec("Test", terms=[D.Term("Mod", 3)])
        r = D.roll_d20(spec, FixedRng([20]))
        self.assertEqual((r.natural, r.total, r.critical), (20, 23, "succes"))
        r = D.roll_d20(spec, FixedRng([1]))
        self.assertEqual((r.natural, r.critical), (1, "echec"))
        spec.mode = "avantage"
        r = D.roll_d20(spec, FixedRng([4, 15]))
        self.assertEqual((r.d20s, r.natural, r.total), ([4, 15], 15, 18))
        spec.mode = "désavantage"
        r = D.roll_d20(spec, FixedRng([4, 15]))
        self.assertEqual(r.natural, 4)

    def test_dice_terms_and_cancel(self):
        spec = D.spec_from_detail("Jet", "test", [("Mod", "+2"), ("Bénédiction", "+1d4")], ["A"], ["B"])
        self.assertEqual(spec.mode, "")                                  # avantage + désavantage s'annulent
        r = D.roll_d20(spec, FixedRng([10, 3]))
        self.assertEqual((r.term_values, r.total), ([2, 3], 15))


class SpecTests(unittest.TestCase):
    def test_skill_spec_lists_sources(self):
        eng = make([("Guerrier", 1, "")], **{"Dextérité": 14})
        eng.add_effect("passage_sans_trace")
        eng.ch.armure["nom"] = "Harnois"
        eng.normalize()
        spec = eng.skill_spec("Discrétion")
        texts = [t.text() for t in spec.terms]
        self.assertIn("+2 (Modificateur de Dextérité)", texts)
        self.assertIn("+10 (Passage sans trace)", texts)
        self.assertEqual(spec.mode, "désavantage")
        self.assertTrue(any("Harnois" in s for s in spec.desavantage))

    def test_weapon_and_spell_specs(self):
        eng = make([("Magicien", 3, "")], **{"Intelligence": 16, "Dextérité": 14})
        spec = eng.weapon_attack_spec({"nom": "Dague", "bonus": 1, "maitrise": None})
        self.assertIn("Arme magique", [t.label for t in spec.terms])
        self.assertIn("1d4", spec.note)
        spell = eng.spell_attack_spec("Trait de feu", "Magicien")
        self.assertEqual([t.text() for t in spell.terms], ["+3 (Modificateur d'Intelligence)", "+2 (Maîtrise)"])
        self.assertIsNone(eng.spell_attack_spec("Boule de feu", "Magicien"))     # JS, pas de jet d'attaque
        self.assertEqual(eng.ability_check_spec("Force").terms[0].text(), "+0 (Modificateur de Force)")


class DialogTests(unittest.TestCase):
    def test_dialog_sequence(self):
        import ui.main_window as mw
        from ui.dice_dialog import DiceRollDialog
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        spec = D.RollSpec("Athlétisme", terms=[D.Term("Modificateur de Force", 3), D.Term("Bénédiction", 0, "+1d4")])
        dlg = DiceRollDialog(win, spec, FixedRng([20, 2]))
        self.assertEqual(dlg.phase, "roll")
        self.assertIn("⏳", dlg.term_labels[0].text())                     # listés dès l'ouverture
        self.assertEqual(dlg.total.text(), "Total : …")                    # pas encore appliqués
        dlg._freeze()
        self.assertEqual(dlg.total.text(), "Total : 20")                   # d20 seul au moment où il se fige
        self.assertIn("réussite critique", dlg.crit.text())
        dlg._apply_next()
        self.assertEqual(dlg.total.text(), "Total : 23")
        dlg.finish_now()
        self.assertEqual(dlg.total.text(), "Total : 25")
        self.assertEqual(dlg.phase, "done")


if __name__ == "__main__":
    unittest.main()


class TwoDiceTests(unittest.TestCase):
    def test_advantage_and_disadvantage_show_two_dice(self):
        import ui.main_window as mw
        from ui.dice_dialog import DiceRollDialog
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        spec = D.RollSpec("Discrétion", terms=[D.Term("Modificateur de Dextérité", 2)], mode="avantage",
                          avantage=["Bottes elfiques"])
        dlg = DiceRollDialog(win, spec, FixedRng([6, 17]))
        self.assertEqual(len(dlg.dice), 2)
        dlg.finish_now()
        self.assertEqual(dlg.kept_index(), 1)                           # avantage : le meilleur (17)
        self.assertTrue(dlg.dice[1].kept and not dlg.dice[1].dimmed)
        self.assertTrue(dlg.dice[0].dimmed)
        self.assertIn("Retenu", dlg.captions[1].text())
        self.assertEqual(dlg.total.text(), "Total : 19")
        spec.mode = "désavantage"
        dlg = DiceRollDialog(win, spec, FixedRng([6, 17]))
        dlg.finish_now()
        self.assertEqual(dlg.kept_index(), 0)                           # désavantage : le moins bon (6)
        self.assertTrue(dlg.dice[1].dimmed)
        self.assertEqual(dlg.total.text(), "Total : 8")
        dlg = DiceRollDialog(win, D.RollSpec("Force"), FixedRng([11]))
        self.assertEqual(len(dlg.dice), 1)
