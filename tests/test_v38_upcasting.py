"""Tests v38 : surclassement dynamique (description, dégâts, jet de dés) et Magie des pactes de l'Occultiste."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core import dice as D  # noqa: E402
from core import rules as R  # noqa: E402
from core.engine import Engine  # noqa: E402


def make(classes, spells=None):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race("Humain")
    eng.ch.classes = [{"nom": c, "niveau": n, "sous_classe": sub, "pv_jets": []} for c, n, sub in classes]
    for cls, names in (spells or {}).items():
        eng.ch.sorts[cls] = [{"nom": n, "prepare": True} for n in names]
    eng.normalize()
    return eng


class UpcastTests(unittest.TestCase):
    def test_burning_hands_level_3(self):
        eng = make([("Magicien", 5, "")], {"Magicien": ["Mains brûlantes"]})
        self.assertEqual(eng.spell_values("Mains brûlantes", 3)["degats"], "5d6")
        self.assertEqual(eng.spell_damage_formula("Mains brûlantes", 3), "5d6")
        text, changed = eng.spell_description_at("Mains brûlantes", 3)
        self.assertIn("5d6 dégâts de feu", text)
        self.assertEqual(changed, ["5d6"])
        self.assertEqual(D.parse_damage(eng.spell_damage_formula("Mains brûlantes", 3)), ([(1, 5, 6)], 0))

    def test_base_level_by_default_for_regular_casters(self):
        eng = make([("Magicien", 5, "")], {"Magicien": ["Mains brûlantes"]})
        self.assertEqual(eng.default_slot_level("Mains brûlantes", "Magicien"), 1)
        self.assertEqual(eng.spell_values("Mains brûlantes")["degats"], "3d6")

    def test_fixed_values_and_projectiles_in_text(self):
        self.assertIn("15 PV temporaires", R.describe_at(DB.find_spell("Armure d'Agathys"), 3)[0])
        self.assertIn("5 projectiles", R.describe_at(DB.find_spell("Projectile magique"), 3)[0])
        self.assertIn("13d6 + 40", R.describe_at(DB.find_spell("Désintégration"), 7)[0])

    def test_cast_message_uses_cast_level(self):
        eng = make([("Magicien", 5, "")], {"Magicien": ["Mains brûlantes"]})
        res = eng.cast_spell("Mains brûlantes", True, slot_level=3)
        self.assertEqual(res["niveau"], 3)
        self.assertIn("Dégâts : 5d6 feu", res["message"])


class PactMagicTests(unittest.TestCase):
    def setUp(self):
        self.eng = make([("Occultiste", 5, "Le Fiélon")],
                        {"Occultiste": ["Représailles infernales", "Rayon ardent", "Décharge occulte"]})

    def test_pact_spells_upcast_automatically(self):
        eng = self.eng
        self.assertEqual(eng.pact()[1], 3)
        self.assertEqual(eng.default_slot_level("Représailles infernales"), 3)
        self.assertEqual(eng.default_slot_level("Rayon ardent", "Occultiste"), 3)
        vals = eng.spell_values("Représailles infernales")
        self.assertEqual((vals["niveau"], vals["degats"], vals["pacte"]), (3, "4d10", True))
        self.assertEqual(eng.spell_values("Rayon ardent")["degats"], "4 × 2d6")
        self.assertIn("4d10", eng.spell_description_at("Représailles infernales")[0])

    def test_turn_tile_shows_pact_level(self):
        tile = next(t for t in self.eng.turn_actions() if t["id"] == "sort:Représailles infernales")
        self.assertIn("⇒ 3", tile["origine"])
        self.assertIn("4d10", tile["description"])
        self.assertEqual(tile["ref"]["niveau_effectif"], 3)
        self.assertIn("Pacte niv. 3", tile["cout"])

    def test_cast_uses_pact_slot_at_pact_level(self):
        res = self.eng.cast_spell("Représailles infernales", True)
        self.assertEqual((res["emplacement"], res["niveau"]), ("pacte", 3))
        self.assertIn("4d10", res["message"])

    def test_attack_spec_note_uses_pact_level(self):
        spec = self.eng.spell_attack_spec("Rayon ardent", "Occultiste")
        self.assertIn("4 × 2d6", spec.note)

    def test_multiclass_keeps_base_for_other_class(self):
        eng = make([("Occultiste", 5, "Le Fiélon"), ("Magicien", 2, "")],
                   {"Occultiste": ["Représailles infernales"], "Magicien": ["Mains brûlantes"]})
        self.assertEqual(eng.default_slot_level("Mains brûlantes", "Magicien"), 1)
        self.assertEqual(eng.default_slot_level("Représailles infernales", "Occultiste"), 3)


class UiTests(unittest.TestCase):
    def test_magic_tab_shows_upcast_damage_and_rolls_it(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        eng = make([("Occultiste", 5, "Le Fiélon")], {"Occultiste": ["Représailles infernales"]})
        win = mw.MainWindow(DB)
        win.engine = eng
        win.refresh_all()
        mt = win.magic_tab
        mt.set_class = getattr(mt, "set_class", None)
        sp = DB.find_spell("Représailles infernales")
        self.assertEqual(mt._slot_level_for(mt.library, sp), eng.default_slot_level(sp["nom"], mt.current_class()))


if __name__ == "__main__":
    unittest.main()
