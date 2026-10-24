"""Tests des bibliothèques pures core.weapon_actions et core.effects (aucune dépendance Qt)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import effects as FX  # noqa: E402
from core import weapon_actions as WA  # noqa: E402
from core.data_loader import Database  # noqa: E402

WEAPONS = Database(ROOT / "data").weapons
WEAPON_LIST = list(WEAPONS.values()) if isinstance(WEAPONS, dict) else list(WEAPONS)


class TestWeaponActions(unittest.TestCase):
    def test_every_weapon_has_1_to_4_actions(self):
        self.assertGreaterEqual(len(WEAPON_LIST), 30)
        for w in WEAPON_LIST:
            keys = WA.actions_for_weapon(w)
            self.assertTrue(1 <= len(keys) <= 4, (w["nom"], keys))
            self.assertEqual(len(keys), len(set(keys)), w["nom"])
            for k in keys:
                self.assertIn(k, WA.ACTIONS, (w["nom"], k))

    def test_botte_first(self):
        for w in WEAPON_LIST:
            if w.get("botte"):
                keys = WA.actions_for_weapon(w)
                self.assertTrue(keys[0].startswith("botte_"), (w["nom"], keys))
                self.assertEqual(WA.ACTIONS[keys[0]]["action"], "Passive")

    def test_action_fields(self):
        for k, a in WA.ACTIONS.items():
            for f in ("nom", "icone", "action", "recharge", "sauvegarde", "condition_dd",
                      "succes", "echec", "description", "source"):
                self.assertIn(f, a, (k, f))
            if a["condition_dd"]:
                self.assertIsNotNone(a["sauvegarde"], k)

    def test_dd_formula(self):
        w = WEAPONS["Bâton de combat"]
        rows = WA.weapon_action_rows(w, attack_mod=3, prof=2)
        self.assertTrue(rows)
        for r in rows:
            self.assertIn("cle", r)
            if r["condition_dd"]:
                self.assertEqual(r["dd"], 8 + 2 + 3)
            else:
                self.assertIsNone(r["dd"])
        self.assertTrue(any(r["dd"] == 13 for r in rows))

    def test_typographic_apostrophe(self):
        keys = WA.actions_for_weapon({"nom": "Hache d'armes", "botte": "Renversement",
                                      "type": "cac", "type_degats": "tranchant", "proprietes": []})
        self.assertIn("laceration", keys)

    def test_unknown_weapon_fallback(self):
        keys = WA.actions_for_weapon({"nom": "Faux de guerre", "type": "cac", "type_degats": "tranchant",
                                      "proprietes": ["Lourde", "Deux mains"], "botte": "Enchaînement"})
        self.assertEqual(keys[0], "botte_enchainement")
        self.assertTrue(1 <= len(keys) <= 4)

    def test_tooltip(self):
        row = WA.weapon_action_rows(WEAPONS["Épée longue"], 4, 3)[1]
        html = WA.tooltip_html(row, "#ff0000")
        self.assertIn(row["nom"], html)
        if row["dd"] is not None:
            self.assertIn(f"DD {row['dd']}", html)


class TestEffects(unittest.TestCase):
    def test_count_and_fields(self):
        self.assertGreaterEqual(len(FX.EFFECTS), 90)
        for k, e in FX.EFFECTS.items():
            self.assertIn(e["categorie"], FX.CATEGORIES, k)
            for f in ("nom", "icone", "source", "duree", "concentration", "description", "mods"):
                self.assertIn(f, e, (k, f))

    def test_phb_conditions_and_exhaustion(self):
        for k in ("a_terre", "agrippe", "assourdi", "aveugle", "charme", "effraye", "empoisonne",
                  "entrave", "etourdi", "neutralise", "inconscient", "invisible", "paralyse", "petrifie"):
            self.assertIn(k, FX.EFFECTS)
        for i in range(1, 7):
            self.assertIn(f"epuisement_{i}", FX.EFFECTS)
        self.assertEqual(FX.EFFECTS["epuisement_2"]["mods"]["vitesse_mult"], 0.5)

    def test_summary_mods(self):
        s = FX.summary_mods(["bouclier_foi", "hate"])
        self.assertEqual(s["ca"], 4)
        self.assertEqual(s["vitesse_mult"], 2.0)
        s = FX.summary_mods(["entrave", "hate"])
        self.assertEqual(s["vitesse_mult"], 0)
        self.assertEqual(s["ca"], 2)
        self.assertTrue(any("Entravé" in a for a in s["attaque"]))
        s = FX.summary_mods(["benediction", "grande_foulee", "rage", "inconnu"])
        self.assertIn("+1d4 (Bénédiction)", s["attaque"])
        self.assertEqual(s["vitesse_bonus"], 3.0)
        self.assertTrue(any(r.startswith("contondant") for r in s["resistances"]))

    def test_search_without_accents(self):
        res = FX.search("etourdi")
        self.assertIn("etourdi", res)
        self.assertEqual(FX.search("ÉTOURDI"), res)
        self.assertIn("benediction", FX.search("benediction"))
        etats = FX.search(categorie="État")
        self.assertTrue(etats and all(FX.EFFECTS[k]["categorie"] == "État" for k in etats))
        all_keys = FX.search()
        self.assertEqual(len(all_keys), len(FX.EFFECTS))
        cats = [FX.CATEGORIES.index(FX.EFFECTS[k]["categorie"]) for k in all_keys]
        self.assertEqual(cats, sorted(cats))

    def test_tooltip(self):
        for k in ("hate", "a_terre", "aura_protection"):
            self.assertIn(FX.EFFECTS[k]["nom"], FX.tooltip_html(k))
        self.assertEqual(FX.tooltip_html("nope"), "")


if __name__ == "__main__":
    unittest.main()
