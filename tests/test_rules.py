"""Tests unitaires de la logique métier (aucune dépendance Qt).  Lancer : python -m unittest discover tests"""
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import rules as R  # noqa: E402
from core.character import Character  # noqa: E402
from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def make(classes, **scores):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": n, "niveau": l, "sous_classe": s, "pv_jets": []} for n, l, s in classes]
    ch.methode = "manuel"
    ch.scores_manuel = {a: 10 for a in R.ABILITIES}
    for k, v in scores.items():
        ch.scores_manuel[k] = v
    eng = Engine(DB, ch)
    eng.normalize()
    return eng


class RulesTests(unittest.TestCase):
    def test_modifiers_and_proficiency(self):
        self.assertEqual([R.ability_modifier(x) for x in (1, 8, 10, 11, 15, 20)], [-5, -1, 0, 0, 2, 5])
        self.assertEqual([R.proficiency_bonus(l) for l in (1, 4, 5, 9, 13, 17, 20)], [2, 2, 3, 4, 5, 6, 6])

    def test_point_buy(self):
        ok, _ = R.point_buy_valid({a: 8 for a in R.ABILITIES})
        self.assertTrue(ok)
        std = dict(zip(R.ABILITIES, [15, 14, 13, 12, 10, 8]))
        self.assertEqual(R.point_buy_total(std), 27)
        self.assertTrue(R.point_buy_valid(std)[0])
        self.assertFalse(R.point_buy_valid({**std, "Charisme": 15})[0])
        self.assertFalse(R.point_buy_valid({**std, "Force": 16})[0])

    def test_4d6(self):
        rng = random.Random(1)
        for _ in range(200):
            total, dice = R.roll_4d6_drop_lowest(rng)
            self.assertEqual(total, sum(dice) - min(dice))
            self.assertTrue(3 <= total <= 18)

    def test_slots(self):
        self.assertEqual(R.spell_slots([("full", 5)])[:3], [4, 3, 2])
        self.assertEqual(R.spell_slots([("half", 1)]), [0] * 9)
        self.assertEqual(R.spell_slots([("half", 5)])[:2], [4, 2])          # paladin 5
        self.assertEqual(R.spell_slots([("artificer", 1)])[0], 2)
        self.assertEqual(R.spell_slots([("third", 3)])[0], 2)               # chevalier occulte 3
        # multiclasse : magicien 4 + paladin 4 -> niveau d'incantateur 6
        self.assertEqual(R.spell_slots([("full", 4), ("half", 4)])[:3], [4, 3, 3])
        self.assertEqual(R.pact_slots(5), (2, 3))

    def test_dice_and_cantrips(self):
        self.assertEqual(R.scale_dice("1d10", R.cantrip_multiplier(5)), "2d10")
        self.assertEqual(R.add_flat("1d8", 3), "1d8+3")
        self.assertEqual(R.add_flat("1d8", -1), "1d8-1")
        self.assertEqual(R.cantrip_multiplier(17), 4)

    def test_skill_bonus(self):
        self.assertEqual(R.skill_bonus(3, 2, False, False), 3)
        self.assertEqual(R.skill_bonus(3, 2, True, False), 5)
        self.assertEqual(R.skill_bonus(3, 2, True, True), 7)
        self.assertEqual(R.skill_bonus(3, 3, False, False, half_prof=True), 4)

    def test_weapon_proficiency(self):
        mage = ["Dagues", "Dard", "Frondes", "Bâtons", "Arbalètes légères"]
        self.assertTrue(R.weapon_proficient("Dague", "courante", mage))
        self.assertTrue(R.weapon_proficient("Bâton de combat", "courante", mage))
        self.assertTrue(R.weapon_proficient("Arbalète légère", "courante", mage))
        self.assertFalse(R.weapon_proficient("Masse d'armes", "courante", mage))
        self.assertTrue(R.weapon_proficient("Épée longue", "guerre", ["Armes courantes", "Épées longues"]))
        self.assertTrue(R.weapon_proficient("Épée longue", "guerre", ["Armes de guerre"]))


class EngineTests(unittest.TestCase):
    def test_hp_first_level_and_average(self):
        eng = make([("Guerrier", 3, "")], Constitution=14)          # d10 : 10+2, puis 2 × (6+2)
        self.assertEqual(eng.hp_max(), 12 + 8 + 8)
        eng = make([("Guerrier", 1, ""), ("Magicien", 2, "")], Constitution=14)
        self.assertEqual(eng.hp_max(), 12 + 2 * (4 + 2))

    def test_unarmored_defense(self):
        eng = make([("Barbare", 1, "")], Dextérité=14, Constitution=16)
        self.assertEqual(eng.armor_class()[0], 10 + 2 + 3)
        eng = make([("Moine", 1, "")], Dextérité=16, Sagesse=14)
        self.assertEqual(eng.armor_class()[0], 10 + 3 + 2)

    def test_armor_and_shield(self):
        eng = make([("Guerrier", 1, "")], Dextérité=18)
        eng.ch.armure.update({"nom": "Cuirasse", "bouclier": True})
        self.assertEqual(eng.armor_class()[0], 14 + 2 + 2)           # Dex plafonnée à +2
        eng.ch.armure.update({"nom": "Cotte de mailles", "bouclier": False, "bonus": 1})
        self.assertEqual(eng.armor_class()[0], 17)

    def test_multiclass_levels(self):
        eng = make([("Guerrier", 4, ""), ("Magicien", 3, "")])
        eng.set_total_level(10, 1)
        self.assertEqual(eng.total_level, 10)
        eng.set_total_level(2, 0)
        self.assertEqual(sorted(c["niveau"] for c in eng.ch.classes), [1, 1])
        self.assertTrue(eng.add_class("Clerc"))
        self.assertFalse(eng.add_class("Clerc"))
        self.assertFalse(eng.remove_class(99))

    def test_casters_and_slots(self):
        eng = make([("Magicien", 5, ""), ("Occultiste", 2, "")], Intelligence=16, Charisme=14)
        self.assertEqual(eng.spell_slots()[:3], [4, 3, 2])
        self.assertEqual(eng.pact(), (2, 1))
        mag = eng.caster("Magicien")
        self.assertEqual(mag["dc"], 8 + 3 + 3)
        self.assertEqual(mag["prepares_max"], 3 + 5)
        self.assertEqual(eng.caster("Occultiste")["connus_max"], 3)
        self.assertTrue(all("Magicien" in s["classes"] for s in eng.available_spells("Magicien")))

    def test_third_caster_subclass(self):
        eng = make([("Guerrier", 3, "Chevalier occulte")], Intelligence=14)
        self.assertEqual(eng.caster("Guerrier")["liste"], "Magicien")
        self.assertEqual(eng.spell_slots()[0], 2)
        eng = make([("Guerrier", 3, "Champion")])
        self.assertIsNone(eng.caster("Guerrier"))

    def test_skills_and_expertise(self):
        eng = make([("Roublard", 1, "")], Dextérité=16)
        eng.ch.competences["Discrétion"] = {"maitrise": True, "expertise": True}
        eng.ch.competences["Acrobaties"] = {"maitrise": True, "expertise": False}
        self.assertEqual(eng.skill_bonus("Discrétion"), 3 + 4)
        self.assertEqual(eng.skill_bonus("Acrobaties"), 3 + 2)
        eng.ch.competences["Arcanes"] = {"maitrise": False, "expertise": True}   # sans maîtrise : ignoré
        eng.normalize()
        self.assertFalse(eng.ch.competences["Arcanes"]["expertise"])

    def test_bard_jack_of_all_trades(self):
        eng = make([("Barde", 2, "")], Dextérité=14)
        self.assertEqual(eng.skill_bonus("Acrobaties"), 2 + 1)

    def test_background_skills(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.historique = "Acolyte"
        eng.apply_background()
        self.assertTrue(eng.ch.competences["Perspicacité"]["maitrise"])
        eng.ch.historique = "Artisan"
        eng.apply_background()
        self.assertFalse(eng.ch.competences["Religion"]["maitrise"])

    def test_race_bonus_and_asi(self):
        eng = make([("Guerrier", 4, "")])
        eng.ch.race = "Nain des montagnes"                           # « Con +2, For +2 » (PHB)
        self.assertEqual(eng.race_bonus()["Constitution"], 2)
        self.assertEqual(eng.race_bonus()["Force"], 2)
        eng.ch.ameliorations["Guerrier|4"] = {"mode": "plus2", "a1": "Force"}
        self.assertEqual(eng.score("Force"), 10 + 2 + 2)
        eng.ch.race = "Humain variant"                               # « +1, +1 » : deux bonus libres
        eng.ch.bonus_libres = ["Sagesse", "Charisme"]
        self.assertEqual((eng.race_bonus()["Sagesse"], eng.race_bonus()["Charisme"]), (1, 1))

    def test_weapons(self):
        eng = make([("Guerrier", 1, "")], Force=16, Dextérité=14)
        st = eng.weapon_stats({"nom": "Épée longue", "bonus": 2, "maitrise": None})
        self.assertEqual((st["attaque"], st["degats"]), (3 + 2 + 2, "1d10+5"))   # v46 : à deux mains (main libre)
        st = eng.weapon_stats({"nom": "Rapière", "bonus": 0, "maitrise": None})
        self.assertEqual(st["carac"], "Force")                       # finesse : meilleure des deux
        eng = make([("Magicien", 1, "")], Force=16)
        st = eng.weapon_stats({"nom": "Épée longue", "bonus": 0, "maitrise": None})
        self.assertFalse(st["maitrise"])

    def test_cantrip_scaling(self):
        eng = make([("Magicien", 5, "")], Intelligence=16)
        st = eng.cantrip_stats("Trait de feu")
        self.assertEqual(st["degats"], "2d10")
        self.assertIn("Attaque +6", st["test"])

    def test_save_load_roundtrip(self):
        eng = make([("Paladin", 6, "Serment de Dévotion"), ("Barde", 2, "")], Force=15)
        eng.ch.nom = "Test"
        eng.ch.sorts["Barde"] = [{"nom": "Lumière", "prepare": True}]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            eng.ch.save(path)
            again = Character.load(path)
        self.assertEqual(again.to_dict(), eng.ch.to_dict())

    def test_warnings(self):
        eng = make([("Guerrier", 1, ""), ("Magicien", 1, "")], Force=14, Intelligence=8)
        self.assertTrue(any("Magicien demande" in w for w in eng.warnings()))

    def test_long_rest(self):
        eng = make([("Magicien", 3, "")])
        eng.ch.emplacements_utilises[0] = 2
        eng.ch.pv_actuels = 1
        eng.long_rest()
        self.assertEqual(eng.ch.emplacements_utilises[0], 0)
        self.assertEqual(eng.ch.pv_actuels, eng.hp_max())


if __name__ == "__main__":
    unittest.main()
