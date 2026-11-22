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
                    self.assertIn(kind, ("sort", "icone", "action", "arme"))
                    if kind == "icone":
                        self.assertIn(name, A.ICONS, (edition, cls, x["nom"]))
                    if kind != "sort":
                        self.assertIn(cat, ("attaque", "soins", "commune", "capacite", "objet", "reaction"))
        self.assertEqual(tile_icon({"id": "generique:foncer", "nom": "Foncer", "groupe": "generiques"}),
                         ("icone", "foncer", "commune"))
        self.assertEqual(tile_icon({"id": "classe:second_souffle", "nom": "Second souffle", "groupe": "capacites",
                                    "type": "Action bonus"})[2], "soins")


class InventoryUiTests(unittest.TestCase):
    def test_grid_and_drop_on_paperdoll(self):
        sys.path.insert(0, str(ROOT / "tests"))
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.inventory_grid import item_icon_name
        win = MainWindow(DB)
        ch = win.engine.ch
        ch.equipement.append({"nom": "Cotte de mailles", "qte": 1})
        ch.equipement.append({"nom": "Torche", "qte": 3})
        win.engine.normalize()
        win.refresh_all()
        self.assertTrue(win.inventory_tab.paperdoll.drop_on_slot("armure", "Cotte de mailles"))
        self.assertEqual(ch.armure["nom"], "Cotte de mailles")
        self.assertFalse(win.inventory_tab.paperdoll.drop_on_slot("armure", "Torche"))
        self.assertEqual(item_icon_name("Potion de soins"), "objet_potion")
        self.assertEqual(item_icon_name("Épée longue"), "arme_epee")


class ActionIconTests(unittest.TestCase):
    """Chaque action du jeu (registre data/action_icons.json, tools/build_action_icons.py) a un dessin unique."""

    def test_every_action_has_a_unique_drawing(self):
        import json
        from core import action_icons as AI
        reg = json.loads((ROOT / "data" / "action_icons.json").read_text(encoding="utf-8"))
        self.assertGreater(len(reg["actions"]), 350)
        by_body = {}
        for n in reg["actions"]:
            by_body.setdefault(AI.action_body(n), set()).add(AI.canonical(n))
        shared = {b: c for b, c in by_body.items() if len(c) > 1}
        self.assertFalse(shared, list(shared.values())[:5])
        named = {fn() for fn in A.ICONS.values()}
        self.assertFalse([n for n in reg["actions"] if AI.action_body(n) in named])

    def test_families_are_distinct(self):
        from core import action_icons as AI
        for family in (["Attaque menaçante", "Attaque précise", "Croc-en-jambe", "Désarmement", "Riposte", "Parade"],
                       ["Frappe malicieuse : Poison", "Frappe malicieuse : Repli", "Frappe malicieuse : Aveugler"],
                       ["Métamagie : Sort prudent", "Métamagie : Sort distant", "Métamagie : Sort accéléré"],
                       ["Déluge de coups", "Défense patiente", "Pas du vent", "Coup étourdissant"],
                       ["Bond psi", "Frappe psionique", "Champ protecteur", "Mouvement télékinétique"]):
            bodies = [AI.action_body(n) for n in family]
            self.assertEqual(len(set(bodies)), len(bodies), family)

    def test_each_weapon_has_its_drawing(self):
        from core import action_icons as AI
        bodies = {k: f() for k, f in AI.WEAPON_ART.items()}
        self.assertEqual(len(set(bodies.values())), len(bodies))
        self.assertNotEqual(AI.weapon_body("Rapière"), AI.weapon_body("Épée longue"))
