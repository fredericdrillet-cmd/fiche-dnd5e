"""v53 : icônes — un dessin unique par sort, catégories de couleur, fichiers à jour, palette par thème."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.data_loader import Database  # noqa: E402
from core import icon_art as A  # noqa: E402
from core import spell_icons as SI  # noqa: E402
from ui import theme  # noqa: E402

DB = Database(ROOT / "data")


class SpellIconTests(unittest.TestCase):
    def test_every_spell_has_a_unique_icon(self):
        icons = SI.all_spell_icons(DB.spells)
        bases = {SI.base_name(n) for n in DB.spells}
        self.assertEqual(set(icons), bases)
        self.assertEqual(len(set(icons.values())), len(icons))
        self.assertEqual(SI.spell_icon(DB.spells, "Boule de feu (2024)"), SI.spell_icon(DB.spells, "Boule de feu"))

    def test_hand_drawn_spells_exist(self):
        bases = {SI.base_name(n) for n in DB.spells}
        self.assertFalse([n for n in A.SPELL_ART if n not in bases])
        self.assertGreaterEqual(len(A.SPELL_ART), 80)

    def test_healing_spells_are_green(self):
        for name in ("Soins", "Mot de guérison", "Prière de guérison", "Guérison", "Retour à la vie"):
            self.assertTrue(SI.is_healing(DB.spells[name]), name)
        self.assertFalse(SI.is_healing(DB.spells["Boule de feu"]))


class IconFilesTests(unittest.TestCase):
    def test_svg_files_up_to_date(self):
        out = subprocess.run([sys.executable, str(ROOT / "tools" / "build_icons.py"), "--check"],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout)


class PaletteTests(unittest.TestCase):
    def test_categories_for_every_theme(self):
        for t in theme.THEMES.values():
            pal = theme.icon_palette(t)
            self.assertTrue({"attaque", "magie", "soins", "commune", "capacite", "objet", "reaction"} <= set(pal))
            self.assertEqual(len([k for k in pal if k.startswith("ecole_")]), 8)
            self.assertEqual(len({p["haut"] for p in pal.values()}), len(pal), t.key)


if __name__ == "__main__":
    unittest.main()


class TileIconTests(unittest.TestCase):
    def test_every_turn_tile_has_a_known_icon(self):
        from core.engine import Engine
        from core.tile_icons import tile_icon
        for edition in ("2014", "2024"):
            for cls, sub in (("Guerrier", "Maître de guerre"), ("Moine", ""), ("Paladin", ""), ("Magicien", "")):
                ch = Engine.new_character(DB)
                ch.classes = [{"nom": cls, "niveau": 6, "sous_classe": "", "pv_jets": []}]
                eng = Engine(DB, ch)
                eng.normalize()
                if edition == "2024":
                    eng.set_edition_mode("2024")
                    eng.normalize()
                for x in eng.turn_actions():
                    kind, name, cat = tile_icon(x)
                    if kind == "icone":
                        self.assertIn(name, A.ICONS, (edition, cls, x["nom"]))
                        self.assertIn(cat, ("attaque", "soins", "commune", "capacite", "objet", "reaction"))
        self.assertEqual(tile_icon({"id": "generique:foncer", "nom": "Foncer", "groupe": "generiques"}),
                         ("icone", "foncer", "commune"))
        self.assertEqual(tile_icon({"id": "classe:second_souffle", "nom": "Second souffle", "groupe": "capacites",
                                    "type": "Action bonus"})[2], "soins")
