"""Tests v22 : sphères d'emplacements agrandies, référentiel des espèces (retraits, Demi-elfe, Drow, Elfe et
sous-espèces), maîtrises d'armes et compétences raciales, ascendance féerique."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core.engine import Engine  # noqa: E402


def make(race, sub="", cls="Guerrier", lvl=5):
    eng = Engine(DB, Engine.new_character(DB))
    eng.ch.race, eng.ch.sous_race = race, sub
    eng.ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
    eng.normalize()
    return eng


def proficient(eng, weapon):
    return eng.weapon_stats({"nom": weapon, "bonus": 0, "maitrise": None})["maitrise"]


class RaceListTests(unittest.TestCase):
    def test_removed_and_added(self):
        names = set(DB.races)
        for gone in ("Changeling ténébreux", "Demi-dragon", "Golem miniature", "Harengon", "Naïade", "Orc cendré",
                     "Mort-vivant", "Elfe sylvestre"):
            self.assertNotIn(gone, names)
        for kept in ("Conil", "Revenant"):
            self.assertIn(kept, names)
        for new in ("Demi-elfe", "Drow (Elfe noir)", "Elfe"):
            self.assertIn(new, names)
        self.assertEqual([s["nom"] for s in DB.subraces_of("Elfe")], ["Haut-elfe", "Elfe des bois"])

    def test_corrections_idempotent(self):
        import importlib
        sys.path.insert(0, str(ROOT / "tools"))
        AC = importlib.import_module("apply_corrections")
        self.assertEqual(AC.apply_races(write=False), [])


class MigrationTests(unittest.TestCase):
    def test_old_wood_elf_save(self):
        from core.character import Character
        ch = Character.from_dict({"classes": [{"nom": "Rôdeur", "niveau": 3}], "race": "Elfe sylvestre"})
        eng = Engine(DB, ch)
        eng.normalize()
        self.assertEqual((ch.race, ch.sous_race), ("Elfe", "Elfe des bois"))
        self.assertEqual(eng.speed(), 10.5)
        ch2 = Character.from_dict({"classes": [{"nom": "Guerrier", "niveau": 1}], "race": "Harengon"})
        Engine(DB, ch2).normalize()
        self.assertEqual(ch2.race, "Conil")


class ElfTests(unittest.TestCase):
    def test_high_elf(self):
        eng = make("Elfe", "Haut-elfe")
        bonus = {k: v for k, v in eng.race_bonus().items() if v}
        self.assertEqual(bonus, {"Dextérité": 2, "Intelligence": 1})
        self.assertEqual(eng.speed(), 9.0)
        self.assertTrue(proficient(eng, "Arc long"))
        self.assertTrue(any("Haut-elfe" in t["nom"] for t in eng.race_traits()))
        self.assertIn("ascendance_feerique", eng.innate_effects())

    def test_wood_elf(self):
        eng = make("Elfe", "Elfe des bois")
        self.assertEqual({k: v for k, v in eng.race_bonus().items() if v}, {"Dextérité": 2, "Sagesse": 1})
        self.assertEqual(eng.speed(), 10.5)

    def test_tasha_rule_replaces_subrace_bonus(self):
        eng = make("Elfe", "Haut-elfe")
        eng.ch.regle_libre = True
        eng.ch.bonus_libres = ["Force", "Constitution"]
        eng.normalize()
        self.assertEqual({k: v for k, v in eng.race_bonus().items() if v}, {"Force": 2, "Constitution": 1})

    def test_perception_from_keen_senses(self):
        eng = make("Elfe", "Elfe des bois")
        eng.ch.competences["Perception"] = {"maitrise": False, "expertise": False}
        self.assertIn("Perception", eng.apply_race_skills())
        self.assertTrue(eng.ch.competences["Perception"]["maitrise"])


class DrowTests(unittest.TestCase):
    def test_drow(self):
        eng = make("Drow (Elfe noir)", cls="Guerrier", lvl=5)
        self.assertEqual({k: v for k, v in eng.race_bonus().items() if v}, {"Dextérité": 2, "Charisme": 1})
        spells = {s["nom"]: s for s in eng.racial_spells()}
        self.assertEqual(spells["Lumières dansantes"]["usage"], "À volonté")
        self.assertEqual(spells["Lueurs féeriques"]["niveau_requis"], 3)
        self.assertEqual(spells["Ténèbres"]["niveau_requis"], 5)
        self.assertTrue(all(s["carac"] == "Charisme" for s in spells.values()))
        for w in ("Rapière", "Épée courte", "Arbalète de poing"):
            if w in DB.weapons:
                self.assertTrue(proficient(make("Drow (Elfe noir)", cls="Magicien"), w), w)
        self.assertTrue(any("soleil" in t["nom"].lower() for t in eng.race_traits()))
        self.assertFalse(make("Drow (Elfe noir)", cls="Guerrier", lvl=2).racial_spells()[1]["debloque"])


class HalfElfTests(unittest.TestCase):
    def test_half_elf_bonus_and_free_picks(self):
        eng = make("Demi-elfe")
        rule = eng.race_rule()
        self.assertEqual((rule["fixe"], rule["libres"]), ({"Charisme": 2}, [1, 1]))
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.race = "Demi-elfe"
        win.changed()
        combo = win.abilities_tab.free_combos[0]
        items = [combo.itemText(i) for i in range(combo.count())]
        self.assertNotIn("Charisme", items)                  # +1 sur deux AUTRES caractéristiques
        self.assertIn("Force", items)


class MagicOrbTests(unittest.TestCase):
    def test_bigger_slot_orbs(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        self.assertGreaterEqual(win.magic_tab.slot_rows[0]["orbs"].orb, 22)
        self.assertGreaterEqual(win.magic_tab.pact_row["orbs"].orb, 22)


if __name__ == "__main__":
    unittest.main()
