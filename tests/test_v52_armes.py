"""v52 : armes sur mesure et dégâts supplémentaires des armes magiques (toujours / à cocher), total par type."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core import dice as D  # noqa: E402
from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def sheet(edition="2014"):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": "Guerrier", "niveau": 5, "sous_classe": "", "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    return eng


def equip(eng, name, base=None):
    base = base or eng.magic_base_options(name)[0]
    eng.add_magic_gear(name, base)
    i = len(eng.ch.objets_magiques) - 1
    eng.equip_magic_gear(i, "main_principale")         # v53 : équipé = harmonisé
    return eng.ch.armes_cac[0]


class CustomWeaponTests(unittest.TestCase):
    def test_custom_weapon_extra_poison(self):
        for ed in ("2014", "2024"):
            eng = sheet(ed)
            base = "Épée longue" if ed == "2014" else next(n for n in eng.db.weapons if n.startswith("Épée longue"))
            name = eng.add_custom_magic_item("Lame venimeuse", "Arme", "rare", False, "", 0, 0, base, 1,
                                             [{"des": "1d4", "type": "poison", "condition": "toujours"},
                                              {"des": "2d6", "type": "radiants", "condition": "cible",
                                               "note": "morts-vivants"}])
            i = len(eng.ch.objets_magiques) - 1
            eng.equip_magic_gear(i, "main_principale")
            slot = eng.ch.armes_cac[0]
            st = eng.weapon_stats(slot)
            self.assertEqual(st["attaque"], eng.mod("Force") + eng.prof + 1, ed)
            spec = eng.weapon_damage_spec(slot)
            self.assertIn("+1d4", spec.formula)
            self.assertEqual(spec.parts[1], ("1d4", "poison"))
            self.assertTrue(any("morts-vivants" in lab and d == "2d6" for lab, d in spec.options))
            self.assertIn("1d4 poison", eng.magic_item(name)["description"])


class OfficialWeaponTests(unittest.TestCase):
    def test_always_and_conditional(self):
        eng = sheet()
        spec = eng.weapon_damage_spec(equip(eng, "Fer gelé"))
        self.assertIn("+1d6", spec.formula)
        self.assertIn(("1d6", "froid"), spec.parts)
        eng2 = sheet()
        spec = eng2.weapon_damage_spec(equip(eng2, "Épée ardente"))
        self.assertNotIn("2d6", spec.formula)
        self.assertTrue(any("feu" in lab and d == "2d6" for lab, d in spec.options))

    def test_needs_attunement(self):
        eng = sheet()
        name = "Épée ardente"
        eng.add_magic_gear(name, eng.magic_base_options(name)[0])
        i = len(eng.ch.objets_magiques) - 1
        for n in ("Anneau de protection", "Cape de protection", "Bottes ailées"):   # 3 / 3 harmonisations
            eng.add_magic_item(n)
            eng.set_attuned(len(eng.ch.objets_magiques) - 1, True)
        self.assertIn("Harmonisation : 3 / 3", eng.equip_magic_gear(i, "main_principale"))   # v53 : refusé
        self.assertEqual(eng.item_damage_riders(eng.ch.armes_cac[0]), ([], []))
        eng.set_equipped(len(eng.ch.objets_magiques) - 1, False)             # une place se libère
        eng.equip_magic_gear(i, "main_principale")
        self.assertTrue(eng.ch.objets_magiques[i]["harmonise"])
        self.assertTrue(eng.item_damage_riders(eng.ch.armes_cac[0])[1])


class TypedTotalTests(unittest.TestCase):
    def test_typed_text(self):
        class R:
            dice = [(8, 6, 1), (8, 2, 1), (4, 3, 1)]
        parts = [(D.critical_formula("1d8+3"), "tranchants"), (D.critical_formula("1d4"), "poison")]
        self.assertEqual(D.typed_text(parts, R()), "11 tranchants + 3 poison")
        self.assertEqual(D.damage_type_in("Châtiment divin"), "")
        self.assertEqual(D.damage_type_in("+2d6 feu"), "feu")


if __name__ == "__main__":
    unittest.main()


class ItemPassiveTests(unittest.TestCase):
    def attuned(self, eng, name):
        eng.add_magic_item(name)
        entry = eng.ch.objets_magiques[-1]
        eng.set_attuned(len(eng.ch.objets_magiques) - 1, True)       # v53 : équipé = harmonisé
        return entry

    def test_official_passives(self):
        for ed in ("2014", "2024"):
            eng = sheet(ed)
            ca, js = eng.armor_class()[0], eng.save_spec("Sagesse").flat
            self.attuned(eng, "Anneau de protection")
            self.assertEqual((eng.armor_class()[0], eng.save_spec("Sagesse").flat), (ca + 1, js + 1), ed)
            self.attuned(eng, "Anneau de résistance au poison")
            self.assertIn("poison", [r for r, _ in eng.defenses()["resistances"]])
            self.attuned(eng, "Amulette de protection contre le poison")
            self.assertIn("poison", [r for r, _ in eng.defenses()["immunites"]])
            self.assertIn("empoisonne", eng.condition_immunities())
            self.assertFalse(eng.add_effect("empoisonne"))

    def test_not_attuned_no_effect(self):
        eng = sheet()
        eng.add_magic_item("Anneau de protection")
        ca = eng.armor_class()[0]
        self.assertEqual(eng.armor_class()[0], ca)
        self.assertEqual(eng.item_passive_mech(eng.ch.objets_magiques[-1],
                                               eng.magic_item("Anneau de protection")), {})

    def test_no_false_positives(self):
        eng = sheet()
        for name in ("Épée vorpale", "Hache des seigneurs nains", "Anneau de contrôle des élémentaires"):
            self.assertEqual(eng.item_passive_mech({"nom": name}, eng.magic_item(name)), {}, name)
        self.assertEqual(eng.item_passive_mech({"nom": "Broche de défense"}, eng.magic_item("Broche de défense")),
                         {"resistances": ["force"]})

    def test_chosen_resistance(self):
        eng = sheet()
        entry = self.attuned(eng, "Anneau de résistance")
        self.assertNotIn("feu", [r for r, _ in eng.defenses()["resistances"]])
        entry["resistance_choisie"] = "feu"
        self.assertIn("feu", [r for r, _ in eng.defenses()["resistances"]])
        self.assertIn("(feu)", eng.magic_display_name(entry))

    def test_custom_powers_and_spell(self):
        eng = sheet()
        name = eng.add_custom_magic_item("Talisman ardent", "Objet merveilleux", "rare", True, "", 0, 0,
                                         resistances=["feu"], immunites_etats=["charme"], js_bonus=1,
                                         sort="Boule de feu", charges=3)
        entry = eng.ch.objets_magiques[-1]
        self.assertEqual(eng.magic_item_powers(), [])                 # dans le sac : pas encore harmonisé
        self.assertTrue(eng.set_attuned(len(eng.ch.objets_magiques) - 1, True))   # v53 : équipé = harmonisé
        self.assertIn("feu", [r for r, _ in eng.defenses()["resistances"]])
        self.assertIn("charme", eng.condition_immunities())
        p = eng.magic_item_powers()[0]
        self.assertEqual((p["sort"], p["charges"], p["cout"]), ("Boule de feu", 3, 1))
        self.assertIn("Boule de feu", eng.magic_item(name)["description"])
