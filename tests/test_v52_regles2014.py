"""v52 : corrections de règles 2014 relevées par AUDIT_CONFORMITE_5E2014.md (§3.2, §3.3, §6.1, §9.1)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import race_images as RI  # noqa: E402
from core import rules as R  # noqa: E402
from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


class ClassSkillsTests(unittest.TestCase):
    def test_stealth_only_for_classes_that_have_it(self):
        for cls in ("Barbare", "Guerrier", "Paladin", "Ensorceleur", "Occultiste", "Clerc"):
            self.assertNotIn("Discrétion", DB.start_info(cls)["competences"], cls)
        for cls in ("Moine", "Rôdeur", "Roublard", "Barde"):
            self.assertIn("Discrétion", DB.start_info(cls)["competences"], cls)

    def test_official_lists_complete(self):
        self.assertEqual(sorted(DB.start_info("Guerrier")["competences"]),
                         sorted(["Acrobaties", "Athlétisme", "Histoire", "Intimidation", "Perception", "Survie",
                                 "Dressage", "Perspicacité"]))
        self.assertEqual(sorted(DB.start_info("Occultiste")["competences"]),
                         sorted(["Arcanes", "Histoire", "Investigation", "Nature", "Religion", "Intimidation",
                                 "Tromperie"]))


class DruidWeaponsTests(unittest.TestCase):
    def test_sickle_not_light_crossbow(self):
        profs = DB.start_info("Druide")["armes"]
        self.assertTrue(R.weapon_proficient("Serpe", "courante", profs))
        self.assertFalse(R.weapon_proficient("Arbalète légère", "courante", profs))


class WeaponValuesTests(unittest.TestCase):
    def test_phb_values(self):
        w = DB.weapons
        self.assertEqual(w["Lance d’arçon"]["degats"], "1d12")
        self.assertNotIn("Lourde", w["Lance d’arçon"]["proprietes"])
        self.assertEqual((w["Trident"]["degats"], w["Trident"]["polyvalent"]), ("1d6", "1d8"))
        self.assertEqual(w["Javeline"]["prix"], "5 pa")
        self.assertEqual(w["Serpe"]["prix"], "1 po")
        self.assertEqual(w["Marteau de guerre"]["poids"], "1 kg")


class HalfOrcTests(unittest.TestCase):
    def test_half_orc(self):
        ch = Engine.new_character(DB)
        eng = Engine(DB, ch)
        eng.change_race("Demi-orque")
        eng.normalize()
        self.assertEqual({k: v for k, v in eng.race_bonus().items() if v}, {"Force": 2, "Constitution": 1})
        self.assertTrue(ch.competences["Intimidation"]["maitrise"])
        self.assertIn("Orc", ch.langues_liste)
        self.assertIn("race:demi-orque:endurance-implacable", [t["key"] for t in eng.resource_trackers()])
        self.assertEqual(RI.find_race_image("Demi-orque").name, "demi-orc.jpg")
        self.assertIn("Demi-orque", eng.race_options())


if __name__ == "__main__":
    unittest.main()
