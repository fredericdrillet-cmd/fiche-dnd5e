"""Tests v46 : décomposition des modificateurs de dégâts, prise automatique des armes polyvalentes, quantités
centrées dans l'inventaire."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v40_wizard_saves import make  # noqa: E402
from test_v41_grimoire_combat import window  # noqa: E402
from core import dice as D  # noqa: E402
from core.engine import damage_calc  # noqa: E402


def weak_fighter():
    eng = make("Guerrier", 3)
    for ab in ("Force", "Dextérité"):
        eng.ch.bonus_divers[ab] = 0
    eng.normalize()
    # Force et Dextérité à 8 : -1
    eng.ch.bonus_divers["Force"] = 8 - eng.score("Force")
    eng.ch.bonus_divers["Dextérité"] = 8 - eng.score("Dextérité")
    eng.normalize()
    return eng


class DamageBreakdownTests(unittest.TestCase):
    def test_example_longsword_plus_three(self):
        eng = weak_fighter()
        self.assertEqual(eng.mod("Force"), -1)
        eng.add_magic_gear("Arme +3", "Épée longue")
        eng.ch.armure["bouclier"], eng.ch.armure["bouclier_nom"] = True, "Bouclier"   # à une main : 1d8
        eng.equip_magic_gear(len(eng.ch.objets_magiques) - 1)
        eng.normalize()
        st = eng.weapon_stats(eng.ch.armes_cac[0])
        self.assertEqual(st["degats"], "1d8+2")
        self.assertEqual(st["calcul"], "1d8 - 1 (Mod. FOR) + 3 (Objet magique : Épée longue +3) = 1d8 + 2")
        spec = eng.weapon_damage_spec(eng.ch.armes_cac[0])
        self.assertEqual(spec.calcul, st["calcul"])
        self.assertEqual(D.flat_breakdown(spec.flat_labels, 2),
                         "-1 (Mod. FOR) + 3 (Objet magique : Épée longue +3) = +2")
        tile = next(t for t in eng.turn_actions() if t["id"] == "arme:armes_cac:0")
        self.assertIn("Calcul des dégâts : " + st["calcul"], tile["description"])

    def test_duel_and_rage_terms(self):
        eng = make("Guerrier", 3)
        eng.ch.styles_combat["Guerrier|1"] = "Duel"
        eng.ch.armes_cac[0] = {"nom": "Rapière", "bonus": 0, "maitrise": None}
        eng.normalize()
        st = eng.weapon_stats(eng.ch.armes_cac[0])
        self.assertIn("(Style de combat : Duel)", st["calcul"])
        self.assertTrue(st["calcul"].startswith("1d8 ") and " = 1d8" in st["calcul"])

    def test_damage_calc_helper(self):
        self.assertEqual(damage_calc("1d6", [("Mod. DEX", 3)], "1d6+3"), "1d6 + 3 (Mod. DEX) = 1d6 + 3")
        self.assertEqual(damage_calc("1d6", [], "1d6"), "1d6")

    def test_dialog_flat_text(self):
        from ui.dice_dialog import flat_text
        spec = D.DamageSpec("Dégâts", "1d8+2", "tranchant", flat_labels=[("Mod. FOR", -1), ("Objet magique : X +3", 3)],
                            calcul="1d8 - 1 (Mod. FOR) + 3 (Objet magique : X +3) = 1d8 + 2")
        text = flat_text(spec, 2)
        self.assertIn("Bonus fixe : -1 (Mod. FOR) + 3 (Objet magique : X +3) = +2", text)
        self.assertIn("Calcul : 1d8 - 1", text)
        self.assertNotIn("Bonus fixe : +2\n", text)


class VersatileTests(unittest.TestCase):
    def test_offhand_free_two_hands(self):
        eng = make("Guerrier", 3)
        eng.ch.armes_cac[0] = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        eng.normalize()
        st = eng.weapon_stats(eng.ch.armes_cac[0])
        self.assertTrue(st["degats"].startswith("1d10"))
        self.assertEqual(st["prise"], "à deux mains")
        self.assertIn("Attaque — Épée longue (à deux mains) (main principale)", [t["nom"] for t in eng.turn_actions()])

    def test_shield_or_second_weapon_one_hand(self):
        eng = make("Guerrier", 3)
        eng.ch.armes_cac[0] = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        eng.ch.armure["bouclier"], eng.ch.armure["bouclier_nom"] = True, "Bouclier"
        eng.normalize()
        self.assertTrue(eng.weapon_stats(eng.ch.armes_cac[0])["degats"].startswith("1d8"))
        self.assertIn("Attaque — Épée longue (à une main) (main principale)", [t["nom"] for t in eng.turn_actions()])
        eng.unequip_slot("main_secondaire")                     # bouclier ôté : retour immédiat à deux mains
        eng.normalize()
        self.assertTrue(eng.weapon_stats(eng.ch.armes_cac[0])["degats"].startswith("1d10"))
        eng.equip_slot("main_secondaire", {"nom": "Dague", "kind": "objet"})   # seconde arme : une main
        eng.normalize()
        st = eng.weapon_stats(eng.ch.armes_cac[0])
        self.assertEqual(st["prise"], "à une main")
        self.assertTrue(st["degats"].startswith("1d8"))
        off = eng.weapon_stats(eng.ch.armes_cac[1], offhand=True)
        self.assertFalse(off.get("deux_mains"))

    def test_offhand_versatile_weapon_is_one_handed(self):
        eng = make("Guerrier", 3)
        eng.ch.armes_cac[0] = {"nom": "Épée courte", "bonus": 0, "maitrise": None}
        eng.ch.armes_cac[1] = {"nom": "Bâton de combat", "bonus": 0, "maitrise": None}
        eng.normalize()
        self.assertEqual(eng.weapon_stats(eng.ch.armes_cac[1])["prise"], "à une main")

    def test_combat_tab_indicator_and_spec(self):
        import ui.combat_tab as ct
        eng = make("Guerrier", 3)
        eng.ch.armes_cac[0] = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        eng.normalize()
        win = window(eng)
        w = win.combat_tab.weapon_rows["armes_cac"][0]
        self.assertEqual(w["hands"].text(), "🙌 À deux mains")
        got = []
        orig = ct.roll_damage_dialog
        self.addCleanup(lambda: setattr(ct, "roll_damage_dialog", orig))
        ct.roll_damage_dialog = lambda win_, spec: got.append(spec)
        win.combat_tab._roll_weapon_damage("armes_cac", 0)
        self.assertIn("(à deux mains)", got[0].title)
        self.assertTrue(got[0].calcul.startswith("1d10"))
        win.engine.ch.armure["bouclier"] = True
        win.changed()
        self.assertEqual(w["hands"].text(), "✋ À une main")


class InventoryAlignmentTests(unittest.TestCase):
    def test_quantity_spin_centered(self):
        src = (ROOT / "ui" / "inventory_tab.py").read_text(encoding="utf-8")
        self.assertIn("spin.setAlignment(Qt.AlignmentFlag.AlignCenter)", src)


if __name__ == "__main__":
    unittest.main()
