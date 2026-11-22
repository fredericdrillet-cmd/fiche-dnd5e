"""v52 : aptitudes 2024 calculées — Sorcellerie innée, Ordre divin, Ordre primitif, prérequis des dons 2024."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def sheet(cls, lvl, edition="2024"):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    return eng


class InnateSorceryTests(unittest.TestCase):
    def test_tracker_tiles_and_effect(self):
        eng = sheet("Ensorceleur", 7)
        tracker = next(t for t in eng.resource_trackers() if t["key"] == "sorcellerie_innee")
        self.assertEqual(tracker["total"], 2)
        ids = {a["id"] for a in eng.class_actions()}
        self.assertTrue({"sorcellerie_innee", "sorcellerie_incarnee"} <= ids)
        dc = eng.casters()[0]["dc"]
        self.assertTrue(eng.use_class_action("sorcellerie_innee")["ok"])
        self.assertTrue(eng.innate_sorcery_active())
        self.assertEqual(eng.casters()[0]["dc"], dc + 1)
        spec = eng.spell_attack_spec("Trait de feu", "Ensorceleur")
        self.assertEqual(spec.mode, "avantage")
        self.assertIn("Sorcellerie innée", spec.avantage)
        eng.use_class_action("sorcellerie_innee")          # bascule : seconde activation = fin de l'effet
        self.assertFalse(eng.innate_sorcery_active())
        self.assertEqual(eng.casters()[0]["dc"], dc)

    def test_low_level_and_2014(self):
        self.assertNotIn("sorcellerie_incarnee", {a["id"] for a in sheet("Ensorceleur", 3).class_actions()})
        old = sheet("Ensorceleur", 7, edition="2014")
        self.assertFalse(any(a["id"].startswith("sorcellerie_in") for a in old.class_actions()))
        self.assertFalse(any(t["key"] == "sorcellerie_innee" for t in old.resource_trackers()))


class OrderTests(unittest.TestCase):
    def test_divine_order(self):
        eng = sheet("Clerc", 1)
        self.assertIn("ordre_divin", [o["key"] for o in eng.option_sets()])
        cantrips = eng.casters()[0]["mineurs_max"]
        eng.ch.options_classe = {"ordre_divin": ["Protecteur"]}
        src = eng.proficiency_sources()[-1]
        self.assertEqual((src["armures"], src["armes"]), (["Armures lourdes"], ["Armes de guerre"]))
        self.assertTrue(any("lourde" in a.lower() for a in eng.armor_proficiencies()))
        eng.ch.options_classe = {"ordre_divin": ["Thaumaturge"]}
        self.assertEqual(eng.casters()[0]["mineurs_max"], cantrips + 1)
        rows = {r["nom"]: r for r in eng.skill_rows()}
        self.assertIn(("Ordre divin : Thaumaturge", "+1"), rows["Religion"]["detail"])   # Sagesse, minimum +1
        self.assertNotIn("Ordre divin : Thaumaturge", [d[0] for d in rows["Nature"]["detail"]])

    def test_primal_order_and_2014(self):
        eng = sheet("Druide", 1)
        eng.ch.options_classe = {"ordre_primitif": ["Gardien"]}
        self.assertEqual(eng.proficiency_sources()[-1]["armures"], ["Armures intermédiaires"])
        eng.ch.options_classe = {"ordre_primitif": ["Magicien"]}
        self.assertIn("Ordre primitif : Magicien", [d[0] for d in {r["nom"]: r for r in eng.skill_rows()}["Nature"]["detail"]])
        old = sheet("Clerc", 1, edition="2014")
        old.ch.options_classe = {"ordre_divin": ["Protecteur"]}
        self.assertNotIn("ordre_divin", [o["key"] for o in old.option_sets()])
        self.assertEqual(old.order_proficiency_sources(), [])


class FeatPrereq2024Tests(unittest.TestCase):
    def test_epic_boons_need_level_19(self):
        self.assertEqual(sheet("Guerrier", 4).feat_status("Faveur de compétence")[0], "ko")
        self.assertEqual(sheet("Guerrier", 19).feat_status("Faveur de compétence")[0], "ok")

    def test_no_unknown_prereq_in_2024(self):
        eng = sheet("Guerrier", 4)
        self.assertEqual([n for n in eng.feat_options() if eng.feat_status(n)[0] == "?"], [])


if __name__ == "__main__":
    unittest.main()
