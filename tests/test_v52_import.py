"""v52 (étape 2) : fusion de data/editions dans la base et filtrage des choix selon le mode d'édition."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def make(mode, classes=(("Magicien", 5),)):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": n, "niveau": lv, "sous_classe": "", "pv_jets": [], "edition": 2014} for n, lv in classes]
    ch.edition_mode = mode
    eng = Engine(DB, ch)
    eng.normalize()
    return eng


class MergeTests(unittest.TestCase):
    def test_stats(self):
        st = DB.edition_stats
        self.assertEqual(st["sous_classes"], 14)
        self.assertEqual(st["especes"], 10)
        self.assertGreater(st["sorts"], 400)
        self.assertGreater(st["dons"], 100)
        self.assertFalse([w for w in DB.warnings if "editions" in w])

    def test_missing_2014_content_added(self):
        oath = DB.subclass("Paladin", "Parjure")
        self.assertEqual(oath["edition"], 2014)
        self.assertTrue(oath["capacites"])
        self.assertIn("Chevalier de l'Écho", [s["nom"] for s in DB.subclasses("Guerrier")])
        self.assertIn("Filet", DB.weapons)
        hail = DB.find_spell("Grêle d'épines")
        self.assertEqual((hail["niveau"], hail["edition"], hail["classes"]), (1, 2014, ["Rôdeur"]))
        self.assertIsNone(DB.find_spell("Piques argentées"))          # = Barbes argentées, déjà présent

    def test_2024_content_suffixed_on_collision(self):
        fb = DB.find_spell("Boule de feu (2024)")
        self.assertEqual(fb["edition"], 2024)
        self.assertEqual(DB.find_spell("Boule de feu")["edition"], 2014)
        self.assertIn("Elfe (2024)", DB.races)
        self.assertEqual(DB.races["Elfe"]["edition"], 2014)
        self.assertEqual(DB.speeds["Goliath (2024)"], 10.5)
        acolyte = DB.backgrounds["Acolyte (2024)"]
        self.assertEqual(acolyte["caracteristiques_2024"], ["Intelligence", "Sagesse", "Charisme"])

    def test_official_feat_texts(self):
        durable = DB.feats["Dur à cuire"]                              # nom de l'app conservé (sauvegardes)
        self.assertEqual(durable["carac_choix"], ["Constitution"])
        self.assertIn("deux fois", durable["description"])
        mam = DB.feats["Maître des armures intermédiaires"]
        self.assertEqual((mam["asi_texte"], mam["carac_choix"]), ("Aucune", []))


class FilterTests(unittest.TestCase):
    def test_races_backgrounds_feats(self):
        e14, e24, lib = make("2014"), make("2024"), make("libre")
        self.assertNotIn("Elfe (2024)", e14.race_options())
        self.assertIn("Elfe (2024)", e24.race_options())
        self.assertNotIn("Elfe", e24.race_options())
        self.assertIn("Humain", e24.race_options())                   # race actuelle toujours visible
        self.assertTrue({"Elfe", "Elfe (2024)"} <= set(lib.race_options()))
        self.assertIn("Acolyte (2024)", e24.background_options())
        self.assertNotIn("Acolyte (2024)", e14.background_options())
        f24 = e24.feat_options()
        self.assertTrue(f24 and all(DB.feats[n]["edition"] == 2024 for n in f24))
        self.assertTrue(all(DB.feats[n]["edition"] == 2014 for n in e14.feat_options()))

    def test_spell_library(self):
        names14 = {s["nom"] for s in make("2014").available_spells("Magicien")}
        names24 = {s["nom"] for s in make("2024").available_spells("Magicien")}
        self.assertIn("Boule de feu", names14)
        self.assertNotIn("Boule de feu (2024)", names14)
        self.assertIn("Boule de feu (2024)", names24)
        self.assertNotIn("Boule de feu", names24)
        lib = {s["nom"] for s in make("libre").available_spells("Magicien")}
        self.assertTrue({"Boule de feu", "Boule de feu (2024)"} <= lib)

    def test_edition_tips_only_in_free_mode(self):
        items = {"Elfe (2024)": DB.races["Elfe (2024)"]}
        self.assertEqual(make("2024").edition_tips(items), {})
        self.assertTrue(make("libre").edition_tips(items)["Elfe (2024)"].startswith("Édition 2024"))


if __name__ == "__main__":
    unittest.main()
