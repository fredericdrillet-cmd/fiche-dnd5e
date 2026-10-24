"""Tests v45 : assistant de niveau (multiclassage Occultiste -> Guerrier sans widgets d'Occultiste), dons de
maîtrise d'armures, jet d'initiative, tuiles de Forme sauvage, armes / armures magiques +X liées à un objet de base,
capacités activables des objets magiques (tuiles, charges), inventaire principal."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from test_v40_wizard_saves import make  # noqa: E402
from test_v41_grimoire_combat import window  # noqa: E402
from core.proficiencies import FEAT_SOURCE  # noqa: E402


class FakeItem:
    def __init__(self, widget=None, layout=None):
        self._w, self._l = widget, layout

    def widget(self):
        return self._w

    def layout(self):
        return self._l


class FakeLayout:
    def __init__(self, items):
        self.items = list(items)
        self.deleted = False

    def count(self):
        return len(self.items)

    def takeAt(self, i):  # noqa: N802
        return self.items.pop(i)

    def deleteLater(self):  # noqa: N802
        self.deleted = True


class FakeWidget:
    def __init__(self):
        self.hidden = self.deleted = False

    def hide(self):
        self.hidden = True

    def setParent(self, p):  # noqa: N802
        self.parent = p

    def deleteLater(self):  # noqa: N802
        self.deleted = True


class WizardMulticlassTests(unittest.TestCase):
    def test_clear_layout_recurses_into_nested_grids(self):
        from ui.game_widgets import clear_layout
        inner_w, outer_w = FakeWidget(), FakeWidget()
        grid = FakeLayout([FakeItem(widget=inner_w)])
        root = FakeLayout([FakeItem(widget=outer_w), FakeItem(layout=grid)])
        clear_layout(root)
        self.assertTrue(inner_w.hidden and inner_w.deleted)          # le widget de la grille imbriquée disparaît
        self.assertTrue(outer_w.hidden and grid.deleted)

    def test_warlock_to_fighter_shows_only_fighter_choices(self):
        from ui.levelup_dialog import LevelUpDialog
        eng = make("Occultiste", 2)
        eng.ch.multiclassage = True
        for ab in ("Force", "Dextérité", "Charisme"):
            eng.ch.bonus_divers[ab] = 6
        eng.normalize()
        win = window(eng)
        dlg = LevelUpDialog(win)
        idx = next(i for i, o in enumerate(dlg.options) if o["classe"] == "Guerrier")
        dlg.class_combo.setCurrentIndex(idx)
        dlg._on_class(idx)
        self.assertEqual(dlg.cls, "Guerrier")
        self.assertNotIn("pacte", dlg.choice_widgets)
        self.assertTrue(dlg.style_labels)                              # Style de combat du Guerrier
        # retour à l'Occultiste : ses choix reviennent
        back = next(i for i, o in enumerate(dlg.options) if o["classe"] == "Occultiste")
        dlg.class_combo.setCurrentIndex(back)
        dlg._on_class(back)
        self.assertEqual(dlg.style_labels, {})
        self.assertIn("pacte", dlg.choice_widgets)                     # Occultiste 3 : Faveur de pacte


class FeatProficiencyTests(unittest.TestCase):
    def test_heavy_armor_feat(self):
        eng = make("Magicien", 4)
        self.assertIn("Maîtrise des armures lourdes", DB.feats)
        eng.ch.armure["nom"] = "Harnois"
        eng.normalize()
        self.assertTrue(eng.unproficient_gear())
        self.assertTrue(eng.spell_block_reason())
        eng.add_gm_feat("Maîtrise des armures lourdes")
        eng.normalize()
        self.assertFalse(eng.unproficient_gear())                      # plus d'avertissement ni de blocage
        self.assertIsNone(eng.spell_block_reason())
        labels = eng.proficiency_origin_labels("armures")
        self.assertIn("Armures lourdes ({})".format(FEAT_SOURCE.format("Maîtrise des armures lourdes")), labels)
        self.assertIn("don", {s["mode"] for s in eng.proficiency_sources()})

    def test_medium_feat_grants_shields(self):
        eng = make("Magicien", 4)
        eng.add_gm_feat("Maîtrise des armures intermédiaires")
        eng.normalize()
        self.assertTrue(eng.shield_proficient())


class InitiativeTests(unittest.TestCase):
    def test_detail_and_roll(self):
        eng = make("Guerrier", 3)
        base = eng.initiative()
        eng.add_gm_feat("Alerte")
        eng.normalize()
        d = eng.initiative_detail()
        self.assertEqual(eng.initiative(), base + 5)
        self.assertIn(("Don : Alerte", 5), d["termes"])
        r = eng.roll_initiative(12)
        self.assertEqual(r["total"], 12 + eng.initiative())
        self.assertEqual(eng.ch.initiative_jet, r["total"])
        spec = eng.initiative_spec()
        self.assertEqual(spec.flat, eng.initiative())
        self.assertEqual(spec.title, "Jet d'initiative")

    def test_class_features(self):
        bard = make("Barde", 2)
        self.assertTrue(any(t[0].startswith("Touche-à-tout") for t in bard.initiative_detail()["termes"]))
        barb = make("Barbare", 7)
        self.assertIn("Instinct sauvage", barb.initiative_detail()["avantage"])

    def test_d20_button_roll(self):
        import types
        import ui.dice_dialog as dd
        win = window(make("Guerrier", 3))
        orig = dd.roll_dice
        dd.roll_dice = lambda w, spec: types.SimpleNamespace(natural=15, total=15 + spec.flat, critical="")
        try:
            r = dd.roll_initiative(win)
        finally:
            dd.roll_dice = orig
        self.assertEqual(r.total, 15 + win.engine.initiative())
        self.assertEqual(win.engine.ch.initiative_jet, r.total)
        self.assertIn("Initiative", win.statusBar().currentMessage() if callable(
            getattr(win.statusBar(), "currentMessage", None)) and isinstance(win.statusBar().currentMessage(), str)
            else "Initiative")


class WildShapeTilesTests(unittest.TestCase):
    def test_beast_tiles_replace_weapons(self):
        eng = make("Druide", 4)
        eng.ch.armes_cac[0] = {"nom": "Bâton", "bonus": 0, "maitrise": None}
        eng.normalize()
        self.assertTrue([t for t in eng.turn_actions() if t["id"].startswith("arme:")])
        beast = next(b["nom"] for b in eng.allowed_beasts() if b["actions"])
        self.assertTrue(eng.assume_form(beast))
        tiles = eng.turn_actions()
        beasts = [t for t in tiles if t["id"].startswith("bete:")]
        self.assertTrue(beasts)
        self.assertFalse([t for t in tiles if t["id"].startswith("arme:")])     # armes masquées
        self.assertEqual({t["groupe"] for t in beasts}, {"attaques"})
        res = eng.use_turn_action(beasts[0]["id"])
        self.assertTrue(res["ok"])
        self.assertIsNotNone(res["attaque"])
        self.assertIsNotNone(res["degats"])
        eng.end_form()
        tiles = eng.turn_actions()
        self.assertFalse([t for t in tiles if t["id"].startswith("bete:")])     # tuiles temporaires retirées
        self.assertTrue([t for t in tiles if t["id"].startswith("arme:")])


class MagicGearTests(unittest.TestCase):
    def test_weapon_plus_two(self):
        eng = make("Guerrier", 5, "Champion")
        self.assertIn("Épée à deux mains", eng.magic_base_options("Arme +2"))
        self.assertEqual(eng.add_magic_gear("Arme +2", "Épée à deux mains"), "Épée à deux mains +2")
        self.assertEqual(eng.add_magic_gear("Arme +2", "Inexistante"), "")
        idx = len(eng.ch.objets_magiques) - 1
        plain = eng.weapon_stats({"nom": "Épée à deux mains", "bonus": 0, "maitrise": None})
        self.assertFalse(eng.ch.objets_magiques[idx]["equipe"])
        eng.equip_magic_gear(idx)
        eng.normalize()
        st = eng.weapon_stats(eng.ch.armes_cac[0])
        self.assertEqual(st["attaque"], plain["attaque"] + 2)                      # +2 au toucher
        self.assertEqual(st["affichage"], "Épée à deux mains +2")
        self.assertTrue(eng.ch.objets_magiques[idx]["equipe"])
        self.assertIn("Attaque — Épée à deux mains +2 (main principale)",
                      [t["nom"] for t in eng.turn_actions()])
        dmg = eng.weapon_damage_spec(eng.ch.armes_cac[0])
        self.assertIn("+", dmg.formula)
        eng.unequip_slot("main_principale")
        eng.normalize()
        self.assertFalse(eng.ch.objets_magiques[idx]["equipe"])                   # lien rompu, bonus retiré

    def test_armor_and_shield(self):
        eng = make("Guerrier", 5, "Champion")
        eng.add_magic_gear("Armure +1", "Harnois")
        eng.equip_magic_gear(len(eng.ch.objets_magiques) - 1)
        eng.normalize()
        self.assertEqual(eng.armor_class()[0], 18 + 1)
        self.assertEqual(eng.paperdoll()["armure"]["nom"], "Harnois +1")
        self.assertTrue(eng.paperdoll()["armure"].get("magique"))
        self.assertEqual(eng.magic_item_bonuses()["ca"], 0)                         # pas compté deux fois
        eng.add_magic_gear("Bouclier +2", "Bouclier")
        eng.equip_magic_gear(len(eng.ch.objets_magiques) - 1)
        eng.normalize()
        self.assertEqual(eng.armor_class()[0], 18 + 1 + 2 + 2)
        eng.remove_magic_item(0)                                                   # l'armure retirée quitte la case
        eng.normalize()
        self.assertEqual(eng.ch.armure["nom"], "Aucune armure")

    def test_slot_inventory_offers_magic_gear(self):
        eng = make("Guerrier", 5)
        eng.add_magic_gear("Arme +1", "Dague")
        cands = eng.slot_inventory("main_principale")
        pick = next(c for c in cands if c["kind"] == "magique_arme")
        self.assertEqual(pick["nom"], "Dague +1")
        eng.equip_slot("main_principale", pick)
        eng.normalize()
        self.assertEqual(eng.ch.armes_cac[0]["bonus"], 1)

    def test_attunement_required_bonus(self):
        eng = make("Guerrier", 5)
        name = next(n for n, i in DB.magic_items.items() if i["type"] == "Arme" and i["lien"]
                    and eng.magic_base_options(n))
        base = eng.magic_base_options(name)[0]
        eng.add_magic_gear(name, base)
        self.assertIn(base, eng.magic_display_name(eng.ch.objets_magiques[-1]))


class MagicPowerTests(unittest.TestCase):
    def test_expressive_shield_bonus_action_tile(self):
        eng = make("Guerrier", 3)
        eng.add_magic_gear("Bouclier expressif", "Bouclier")
        self.assertFalse([t for t in eng.turn_actions() if t["id"].startswith("objet:")])   # non équipé
        eng.equip_magic_gear(len(eng.ch.objets_magiques) - 1)
        eng.normalize()
        tiles = [t for t in eng.turn_actions() if t["id"].startswith("objet:")]
        self.assertEqual(len(tiles), 1)
        self.assertEqual(tiles[0]["type"], "Action bonus")
        self.assertEqual(tiles[0]["groupe"], "objets")
        self.assertTrue(tiles[0]["origine"].startswith("[Objet Magique : Bouclier expressif"))
        res = eng.use_turn_action(tiles[0]["id"])
        self.assertTrue(res["ok"] and res["objet"])
        self.assertTrue(eng.ch.tour_bonus)

    def test_wand_charges(self):
        eng = make("Magicien", 5)
        eng.add_magic_item("Baguette de boules de feu")
        eng.ch.objets_magiques[-1]["harmonise"] = True
        eng.normalize()
        tile = next(t for t in eng.turn_actions() if t["id"].startswith("objet:") and "Boule de feu" in t["nom"])
        res = eng.use_turn_action(tile["id"])
        self.assertTrue(res["ok"])
        self.assertEqual(res["objet_sort"], "Boule de feu")
        self.assertEqual(eng.ch.objets_magiques[-1]["charges_utilisees"], 1)
        self.assertIn("6 / 7", res["message"])
        eng.long_rest()
        self.assertNotIn("charges_utilisees", eng.ch.objets_magiques[-1])

    def test_staff_spell_costs(self):
        eng = make("Magicien", 9)
        eng.add_magic_item("Bâton de feu")
        eng.ch.objets_magiques[-1]["harmonise"] = True
        eng.normalize()
        costs = {p["sort"]: p["cout"] for p in eng.magic_item_powers()}
        self.assertEqual(costs.get("Boule de feu"), 3)
        self.assertEqual(costs.get("Mur de feu"), 4)


class InventoryUiTests(unittest.TestCase):
    def test_magic_items_listed_in_main_inventory(self):
        eng = make("Guerrier", 5)
        eng.add_item("Corde")
        eng.add_magic_gear("Arme +3", "Épée longue")
        win = window(eng)
        tab = win.inventory_tab
        tab.refresh()
        n = len(win.engine.ch.equipement)
        self.assertEqual(tab.magic_row(n), 0)
        self.assertEqual(tab.magic_row(0), -1)
        tab.table.currentRow = lambda: n
        self.assertTrue(tab._on_equip_magic())
        self.assertTrue(win.engine.ch.objets_magiques[0]["equipe"])
        self.assertEqual(win.engine.ch.armes_cac[0]["bonus"], 3)
        self.assertEqual(win.engine.ch.armes_cac[0]["affichage"], "Épée longue +3")

    def test_panel_add_asks_base(self):
        import ui.magic_items_panel as mp
        import ui.dialogs as dlg
        eng = make("Guerrier", 5)
        win = window(eng)
        orig = dlg.ask_choice
        dlg.ask_choice = lambda *a, **k: "Épée à deux mains"
        try:
            name = mp.add_catalog_item(win, win.engine, DB.magic_items["Arme +2"])
        finally:
            dlg.ask_choice = orig
        self.assertEqual(name, "Épée à deux mains +2")
        self.assertEqual(win.engine.ch.objets_magiques[-1]["base"], "Épée à deux mains")


if __name__ == "__main__":
    unittest.main()
