"""Tests v31 : mannequin d'équipement (12 cases, un objet par case), jeux d'armes, comparaison d'objets."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core.character import Character  # noqa: E402
from core.engine import Engine  # noqa: E402
from core.equipment import SLOTS, item_slot_kind  # noqa: E402


def of_kind(kind, n=1):
    return [name for name, it in DB.magic_items.items() if item_slot_kind(it, name) == kind][:n]


def make():
    eng = Engine(DB, Engine.new_character(DB))
    eng.ch.classes = [{"nom": "Guerrier", "niveau": 3, "sous_classe": "Champion", "pv_jets": []}]
    eng.ch.armure["nom"] = "Cotte de mailles"
    eng.ch.armes_cac[0]["nom"] = "Épée longue"
    eng.ch.armes_distance[0]["nom"] = "Arc long"
    eng.normalize()
    return eng


def window(eng):
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    win = mw.MainWindow(DB)
    win.engine = eng
    win.refresh_all()
    return win


class EngineTests(unittest.TestCase):
    def test_twelve_slots_and_kinds(self):
        self.assertEqual(len(SLOTS), 12)
        self.assertEqual(item_slot_kind(DB.magic_items.get("Bottes elfiques"), "Bottes elfiques"), "bottes")
        self.assertEqual(item_slot_kind(DB.magic_items.get("Cape elfique"), "Cape elfique"), "cape")
        self.assertEqual(item_slot_kind({"type": "Baguette"}, "Baguette de projectiles magiques"), "")
        self.assertEqual(item_slot_kind({"type": "Anneau"}, "Anneau de protection"), "anneau")
        self.assertEqual(item_slot_kind({"type": "Potion"}, "Potion de soins"), "")

    def test_paperdoll_mirrors_combat_choices(self):
        doll = make().paperdoll()
        self.assertEqual(doll["armure"]["nom"], "Cotte de mailles")
        self.assertEqual(doll["main_principale"]["nom"], "Épée longue")
        self.assertEqual(doll["distance"]["nom"], "Arc long")
        self.assertNotIn("tete", doll)

    def test_one_item_per_slot(self):
        eng = make()
        boots = of_kind("bottes", 2)
        for b in boots:
            eng.add_magic_item(b)
        eng.normalize()
        self.assertEqual(eng.paperdoll()["bottes"]["nom"], boots[0])
        self.assertIn("2 objets « bottes » équipés pour 1 emplacement.", eng.warnings())
        replaced = eng.equip_magic_item(1, "bottes")
        self.assertEqual(replaced, boots[0])
        self.assertEqual(eng.paperdoll()["bottes"]["nom"], boots[1])
        self.assertFalse(eng.ch.objets_magiques[0]["equipe"])
        self.assertEqual(eng.equipment_warnings(), [])

    def test_two_rings(self):
        eng = make()
        rings = of_kind("anneau", 3)
        for r in rings:
            eng.add_magic_item(r)
        eng.normalize()
        doll = eng.paperdoll()
        self.assertEqual((doll["anneau_1"]["nom"], doll["anneau_2"]["nom"]), (rings[0], rings[1]))
        self.assertIn("3 anneaux équipés pour 2 emplacements.", eng.warnings())
        eng.unequip_slot("anneau_1")
        eng.set_equipped(2, True)
        self.assertEqual(eng.paperdoll()["anneau_1"]["nom"], rings[2])
        self.assertEqual(eng.equipment_warnings(), [])

    def test_unequipped_item_frees_slot(self):
        eng = make()
        cape = of_kind("cape")[0]
        eng.add_magic_item(cape)
        eng.normalize()
        eng.set_equipped(0, False)
        self.assertNotIn("cape", eng.paperdoll())
        self.assertEqual(eng.ch.objets_magiques[0]["emplacement"], "")

    def test_compare(self):
        eng = make()
        c = eng.compare_armor("Harnois")
        self.assertEqual(c["delta"], c["ca_apres"] - c["ca_avant"])
        self.assertGreater(c["delta"], 0)
        self.assertTrue(c["discretion"])
        w = eng.compare_weapon("Épée à deux mains")
        self.assertEqual(w["actuelle"], "Épée longue")
        self.assertGreater(w["delta_moy"], 0)

    def test_persistence(self):
        eng = make()
        eng.add_magic_item(of_kind("cape")[0])
        eng.normalize()
        ch = Character.from_dict(json.loads(json.dumps(eng.ch.to_dict())))
        e2 = Engine(DB, ch)
        e2.normalize()
        self.assertEqual(e2.ch.objets_magiques[0]["emplacement"], "cape")


class UiTests(unittest.TestCase):
    def test_panel_and_slot_choice(self):
        import ui.paperdoll as pd
        eng = make()
        rings = of_kind("anneau", 2)
        for r in rings:
            eng.add_magic_item(r)
            eng.set_equipped(len(eng.ch.objets_magiques) - 1, False)
        win = window(eng)
        panel = win.inventory_tab.paperdoll
        panel.refresh()
        self.assertIn("2 objets disponibles", panel.slot_btns["anneau_1"].text())
        orig = pd.ask_choice
        pd.ask_choice = lambda w, t, m, options: options[1]
        try:
            panel._on_slot("anneau_1")
        finally:
            pd.ask_choice = orig
        self.assertEqual(win.engine.paperdoll()["anneau_1"]["nom"], rings[1])
        self.assertIn(rings[1], panel.slot_btns["anneau_1"].text())

    def test_gear_slots_use_inventory_by_role(self):
        import ui.paperdoll as pd
        eng = make()
        eng.ch.equipement = [{"nom": n, "qte": 1} for n in ("Harnois", "Épée à deux mains", "Bouclier", "Arc court",
                                                             "Dague", "Corde en chanvre (15 m)")]
        eng.normalize()
        self.assertEqual([c["nom"] for c in eng.slot_inventory("armure")], ["Harnois"])
        self.assertEqual([c["nom"] for c in eng.slot_inventory("main_principale")], ["Épée à deux mains", "Dague"])
        self.assertEqual([c["nom"] for c in eng.slot_inventory("main_secondaire")], ["Bouclier", "Dague"])
        self.assertEqual([c["nom"] for c in eng.slot_inventory("distance")], ["Arc court"])
        win = window(eng)
        panel = win.inventory_tab.paperdoll
        orig = pd.ask_choice
        try:
            pd.ask_choice = lambda w, t, m, options: next(o for o in options if o.startswith("Harnois"))
            panel._on_slot("armure")
            self.assertEqual(win.ch.armure["nom"], "Harnois")          # même armure que l'onglet Combat
            pd.ask_choice = lambda w, t, m, options: next(o for o in options if o.startswith("Bouclier"))
            panel._on_slot("main_secondaire")
            self.assertTrue(win.ch.armure["bouclier"])
            pd.ask_choice = lambda w, t, m, options: next(o for o in options if o.startswith("Épée à deux mains"))
            panel._on_slot("main_principale")
            self.assertEqual(win.ch.armes_cac[0]["nom"], "Épée à deux mains")
            self.assertFalse(win.ch.armure["bouclier"])                # arme à deux mains : bouclier rangé
            pd.ask_choice = lambda w, t, m, options: options[-1]       # « Vider la case »
            panel._on_slot("distance")
        finally:
            pd.ask_choice = orig
        self.assertEqual(win.ch.armes_distance[0]["nom"], "")

    def test_offhand_blocked_by_two_handed(self):
        eng = make()
        eng.ch.armes_cac[0]["nom"] = "Épée à deux mains"
        msg = eng.equip_slot("main_secondaire", {"nom": "Bouclier", "kind": "objet"})
        self.assertIn("deux mains", msg)
        self.assertFalse(eng.ch.armure["bouclier"])

    def test_character_portrait_in_center(self):
        win = window(make())
        panel = win.inventory_tab.paperdoll
        panel.refresh()
        self.assertIn("Aucun portrait", panel.portrait.text())
        went = []
        win.go_to_tab = lambda k: went.append(k)
        panel._on_portrait()
        self.assertEqual(went, ["rp"])

    def test_compare_text(self):
        win = window(make())
        tab = win.inventory_tab
        txt = tab.compare_text("Harnois", DB.catalog.get("Harnois"))
        self.assertIn("CA", txt)
        txt = tab.compare_text("Épée à deux mains", DB.catalog.get("Épée à deux mains"))
        self.assertIn("en moyenne", txt)


if __name__ == "__main__":
    unittest.main()
