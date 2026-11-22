"""v53 : retours d'essai — bonus au toucher (sournoise, châtiment, manœuvres, psi…), armure sur mesure,
compétences à la création (espèce comptée deux fois), onglet des dons."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def sheet(cls, lvl=1, sub="", weapon="Épée longue"):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    ch.armes_cac[0]["nom"] = weapon
    eng.normalize()
    return eng


class OnHitTests(unittest.TestCase):
    def keys(self, eng):
        return {o["key"]: o["dice"] for o in eng.on_hit_options(eng.ch.armes_cac[0])}

    def test_sneak_attack_added_to_weapon_damage(self):
        eng = sheet("Roublard", 5, weapon="Rapière")
        opts = eng.on_hit_options(eng.ch.armes_cac[0])
        self.assertEqual(eng.apply_on_hit(opts, ["sournoise"]), [("Attaque sournoise", "3d6")])

    def test_battle_master_maneuvers(self):
        eng = sheet("Guerrier", 7, "Maître de guerre")
        for i, n in enumerate(["Attaque menaçante", "Attaque précise", "Croc-en-jambe"]):
            eng.set_class_option("manoeuvres", i, n)
        keys = self.keys(eng)
        self.assertIn("man:Attaque menaçante", keys)
        self.assertNotIn("man:Attaque précise", keys)             # ajoute le dé à l'attaque, pas aux dégâts
        opts = eng.on_hit_options(eng.ch.armes_cac[0])
        added = eng.apply_on_hit(opts, ["man:Attaque menaçante", "man:Croc-en-jambe"])
        self.assertEqual(len(added), 1)                            # une seule manœuvre par coup
        self.assertEqual(eng.resource_used("superiorite"), 1)

    def test_other_riders(self):
        self.assertIn("psi_frappe", self.keys(sheet("Guerrier", 7, "Soldat psi")))
        self.assertIn("tueur_colosses", self.keys(sheet("Rôdeur", 5, "Chasseur")))
        self.assertIn("frappe_divine", self.keys(sheet("Clerc", 8, "Domaine de la Guerre")))
        zealot = sheet("Barbare", 5, "Voie du Zélote")
        zealot.ch.effets_actifs.append("rage")
        self.assertEqual(self.keys(zealot)["fureur_divine"], "1d6+2")
        ranger = sheet("Rôdeur", 5)
        ranger.ch.concentration = "Marque du chasseur"
        self.assertIn("conc:marque du chasseur", self.keys(ranger))

    def test_per_turn_riders_once(self):
        eng = sheet("Rôdeur", 5, "Chasseur")
        opts = eng.on_hit_options(eng.ch.armes_cac[0])
        eng.apply_on_hit(opts, ["tueur_colosses"])
        self.assertNotIn("tueur_colosses", self.keys(eng))


class CustomArmorTests(unittest.TestCase):
    def test_custom_armor_on_base(self):
        eng = sheet("Guerrier", 5)
        name = eng.add_custom_magic_item("Cotte du dragon", type_="Armure", base="Cotte de mailles", bonus=2)
        eng.normalize()
        cand = next(c for c in eng.slot_inventory("armure") if name in c["nom"])
        eng.equip_slot("armure", cand)
        eng.normalize()
        self.assertEqual(eng.armor_class()[0], 18)                 # 16 + 2
        shield = eng.add_custom_magic_item("Égide", type_="Armure", base="Bouclier", bonus=1)
        eng.normalize()
        eng.equip_slot("main_secondaire", next(c for c in eng.slot_inventory("main_secondaire") if shield in c["nom"]))
        eng.normalize()
        self.assertEqual(eng.armor_class()[0], 21)                 # + 2 + 1


class CreationSkillsTests(unittest.TestCase):
    def test_species_skill_not_counted_as_class_pick(self):
        eng = sheet("Roublard", 1)
        eng.change_race("Elfe")
        eng.normalize()
        need = eng.skills_missing()
        self.assertEqual(need, 4)
        opts = [n for n in eng.class_skill_status()["options"] if not (eng.ch.competences.get(n) or {}).get("maitrise")]
        for n in opts[:need]:
            eng.ch.competences.setdefault(n, {"maitrise": False, "expertise": False})["maitrise"] = True
        eng.normalize()
        self.assertEqual((eng.skills_missing(), eng.skill_choice_errors()), (0, []))
        self.assertEqual(eng.expertise_missing(), 2)


if __name__ == "__main__":
    unittest.main()
