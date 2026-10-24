"""Tests v30 : barre du tour (actions par coût), suivi du tour, réactions programmables, surclassement direct."""
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
from core.turn import spell_economy  # noqa: E402


def make(c="Guerrier", lvl=5, sub="Champion", race="Humain"):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race(race)
    eng.ch.classes = [{"nom": c, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng.ch.armes_cac[0]["nom"] = "Épée longue"
    eng.normalize()
    return eng


def tiles(eng, kind=None):
    return {t["nom"]: t for t in eng.turn_actions() if kind is None or t["type"] == kind}


def window(eng):
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    win = mw.MainWindow(DB)
    win.engine = eng
    win.refresh_all()
    return win


class EngineTests(unittest.TestCase):
    def test_tiles_cover_every_source(self):
        eng = make("Magicien", 3, "", race="Gobelin")
        eng.ch.sorts["Magicien"] = [{"nom": "Bouclier", "prepare": True}, {"nom": "Projectile magique", "prepare": True}]
        eng.normalize()
        all_tiles = tiles(eng)
        # v43 : un magicien ne maîtrise pas l'épée longue -> tuile marquée ⚠
        self.assertEqual(all_tiles["⚠ Attaque — Épée longue (à deux mains) (main principale)"]["type"], "Action")
        self.assertEqual(all_tiles["Projectile magique"]["type"], "Action")
        self.assertEqual(all_tiles["Bouclier"]["type"], "Réaction")
        self.assertEqual(all_tiles["Fuite agile"]["type"], "Action bonus")          # race
        self.assertEqual(all_tiles["Attaque d'opportunité"]["type"], "Réaction")
        for name in ("Foncer", "Se désengager", "Esquiver", "Aider", "Se cacher", "Saisir", "Interagir"):
            self.assertIn(name, all_tiles)
        self.assertEqual(all_tiles["Interagir"]["type"], "Gratuit")

    def test_spell_economy(self):
        self.assertEqual(spell_economy({"temps": "1 action bonus"}), "Action bonus")
        self.assertEqual(spell_economy({"temps": "1 réaction, que vous prenez quand…"}), "Réaction")
        self.assertEqual(spell_economy({"temps": "1 action"}), "Action")
        self.assertEqual(spell_economy({"temps": "10 minutes"}), "")

    def test_action_spent_locks_actions_not_bonus(self):
        eng = make()
        res = eng.use_turn_action("commune:esquiver")
        self.assertTrue(res["ok"])
        self.assertIn("esquive", eng.ch.effets_actifs)
        acts = tiles(eng, "Action")
        self.assertFalse(acts["Foncer"]["disponible"])
        self.assertIn("déjà utilisée", acts["Foncer"]["raison"])
        self.assertTrue(tiles(eng, "Gratuit")["Interagir"]["disponible"])
        self.assertTrue(tiles(eng, "Action bonus")["Second souffle"]["disponible"])

    def test_extra_attack(self):
        eng = make("Guerrier", 11)
        self.assertEqual(eng.attacks_per_action(), 3)
        for i in range(3):
            self.assertTrue(eng.use_turn_action("arme:armes_cac:0")["ok"], i)
        self.assertFalse(eng.use_turn_action("arme:armes_cac:0")["ok"])
        self.assertEqual(make("Paladin", 5, "").attacks_per_action(), 2)
        self.assertEqual(make("Magicien", 5, "").attacks_per_action(), 1)

    def test_attack_after_spell_is_locked(self):
        eng = make()
        eng.use_turn_action("commune:foncer")
        self.assertFalse(tiles(eng)["Attaque — Épée longue (à deux mains) (main principale)"]["disponible"])

    def test_spell_without_slot_locked(self):
        eng = make("Magicien", 1, "")
        eng.ch.sorts["Magicien"] = [{"nom": "Projectile magique", "prepare": True}]
        eng.ch.emplacements_utilises[0] = 2
        eng.normalize()
        t = tiles(eng)["Projectile magique"]
        self.assertFalse(t["disponible"])
        self.assertIn("emplacement", t["raison"])

    def test_new_round(self):
        eng = make()
        eng.use_turn_action("arme:armes_cac:0")
        eng.use_turn_action("classe:second_souffle")
        eng.use_turn_action("reaction:opportunite")
        eng.set_movement(6)
        st = eng.turn_state()
        self.assertTrue(st["Action"] and st["Action bonus"] and st["Réaction"])
        eng.new_round()
        st = eng.turn_state()
        self.assertFalse(st["Action"] or st["Action bonus"] or st["Réaction"])
        self.assertEqual((st["deplacement"], eng.ch.tour_attaques), (0.0, 0))

    @unittest.skip("v40 : réglages Demander / Automatique / Désactivée retirés à la demande (réactions = tuiles)")
    def test_reaction_modes(self):
        eng = make()
        eng.ch.styles_combat["Guerrier|1"] = "Protection"
        eng.normalize()
        eng.set_reaction_mode("style:Protection", "off")
        self.assertNotIn("Protection", tiles(eng))
        eng.set_reaction_mode("style:Protection", "auto")
        first = eng.turn_actions()[0]
        self.assertEqual(first["nom"], "★ Protection")
        self.assertTrue(eng.use_auto_reaction()["ok"])
        self.assertFalse(eng.use_auto_reaction()["ok"])            # déjà utilisée ce round
        eng.set_reaction_mode("style:Protection", "demander")
        self.assertEqual(eng.ch.modes_reactions, {})

    def test_opportunity_attack_not_programmable(self):
        eng = make()                                              # v34 : jouée à la table, aucun réglage
        eng.set_reaction_mode("opportunite", "off")
        eng.set_reaction_mode("opportunite", "auto")
        self.assertEqual(eng.reaction_mode("opportunite"), "demander")
        self.assertEqual(eng.ch.modes_reactions, {})
        self.assertIn("Attaque d'opportunité", tiles(eng))

    @unittest.skip("v40 : réglages Demander / Automatique / Désactivée retirés à la demande (réactions = tuiles)")
    def test_single_auto_reaction(self):
        eng = make()
        eng.ch.styles_combat["Guerrier|1"] = "Protection"
        eng.normalize()
        eng.set_reaction_mode("sort:Bouclier", "auto")
        eng.set_reaction_mode("style:Protection", "auto")
        self.assertEqual(eng.ch.modes_reactions, {"style:Protection": "auto"})

    def test_persistence(self):
        eng = make()
        eng.use_turn_action("arme:armes_cac:0")              # v40 : plus de modes de réaction à sauvegarder
        ch = Character.from_dict(json.loads(json.dumps(eng.ch.to_dict())))
        self.assertTrue(ch.tour_action)


class UiTests(unittest.TestCase):
    def test_filter_and_tiles(self):
        win = window(make())
        tab = win.combat_tab
        tab._refresh_turn()
        all_count = len(tab.turn_tiles)
        tab._on_turn_filter("Action bonus")
        self.assertLess(len(tab.turn_tiles), all_count)
        self.assertIn("classe:second_souffle", tab.turn_tiles)
        self.assertIn("Tout (", tab.turn_filter_btns["Tout"].text())

    def test_weapon_tile_rolls_and_spends(self):
        import ui.combat_tab as ct
        win = window(make())
        rolled = []
        orig = ct.roll_dice
        ct.roll_dice = lambda w, spec: rolled.append(spec)
        try:
            win.combat_tab._on_turn_tile("arme:armes_cac:0")
        finally:
            ct.roll_dice = orig
        self.assertEqual(len(rolled), 1)
        self.assertTrue(win.ch.tour_action)
        self.assertIn("●", win.combat_tab.turn_lights["Action"].text())

    def test_cancelled_spell_refunds_action(self):
        eng = make("Magicien", 3, "")
        eng.ch.sorts["Magicien"] = [{"nom": "Projectile magique", "prepare": True}]
        eng.normalize()
        win = window(eng)
        win.magic_tab.cast = lambda name, use_slot=True, slot_level=0, **kw: False
        win.combat_tab._on_turn_tile("sort:Projectile magique")
        self.assertFalse(win.ch.tour_action)

    @unittest.skip("v40 : réglages Demander / Automatique / Désactivée retirés à la demande (réactions = tuiles)")
    def test_reaction_mode_from_panel(self):
        eng = make()
        eng.ch.styles_combat["Guerrier|1"] = "Protection"
        eng.normalize()
        win = window(eng)
        win.combat_tab._on_reaction_mode("style:Protection", "off")
        self.assertEqual(win.engine.reaction_mode("style:Protection"), "off")
        self.assertNotIn("reaction:style:Protection", win.combat_tab.turn_tiles)

    def test_inline_upcast(self):
        eng = make("Magicien", 5, "")
        eng.ch.sorts["Magicien"] = [{"nom": "Projectile magique", "prepare": True}]
        eng.normalize()
        win = window(eng)
        calls = []
        win.engine.cast_spell = lambda name, use_slot=True, target="", effect="", slot_level=0: (
            calls.append(slot_level) or {"ok": True, "message": "ok", "emplacement": "slot:3"})
        win.magic_tab.cast("Projectile magique", True, 3)
        self.assertEqual(calls, [3])


if __name__ == "__main__":
    unittest.main()
