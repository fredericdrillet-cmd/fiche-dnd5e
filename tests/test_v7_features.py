"""Tests v7 : effets actifs, actions d'arme, munitions, repos interactifs, concentration, réactions, données corrigées."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests"), str(ROOT / "tools")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB, make  # noqa: E402


class EffectTests(unittest.TestCase):
    def test_effects_change_ac_and_speed(self):
        eng = make([("Guerrier", 1, "")])
        base_ac, base_speed = eng.armor_class_detail()["valeur"], eng.speed()
        self.assertTrue(eng.add_effect("hate"))
        self.assertFalse(eng.add_effect("hate"))                      # pas de doublon
        self.assertEqual(eng.armor_class_detail()["valeur"], base_ac + 2)
        self.assertEqual(eng.speed(), base_speed * 2)
        eng.add_effect("entrave")
        self.assertEqual(eng.speed(), 0)
        eng.remove_effect("entrave")
        eng.remove_effect("hate")
        self.assertEqual(eng.speed(), base_speed)

    def test_exhaustion_single_level_and_long_rest(self):
        eng = make([("Guerrier", 1, "")])
        eng.add_effect("epuisement_2")
        eng.add_effect("epuisement_3")
        self.assertEqual([k for k in eng.ch.effets_actifs if k.startswith("epuisement")], ["epuisement_3"])
        eng.do_long_rest()
        self.assertEqual([k for k in eng.ch.effets_actifs if k.startswith("epuisement")], ["epuisement_2"])


class WeaponTests(unittest.TestCase):
    def test_weapon_actions_and_dc(self):
        eng = make([("Guerrier", 1, "")], Force=16)
        slot = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        rows = eng.weapon_actions(slot)
        self.assertTrue(1 <= len(rows) <= 4)
        dcs = {r["dd"] for r in rows if r["dd"]}
        self.assertTrue(dcs <= {8 + 2 + 3})

    def test_ammo_selection_bonus_and_stock(self):
        eng = make([("Rôdeur", 5, "")], **{"Dextérité": 16})
        eng.add_magic_item("Munition +1")
        eng.ch.equipement.append({"nom": "Munitions", "qte": 2})
        slot = eng.ch.armes_distance[0]
        slot.update({"nom": "Arc long"})
        names = [a["nom"] for a in eng.ammo_options(slot)]
        self.assertEqual(names, ["Munition +1", "Munitions"])
        plain = eng.weapon_stats(slot)["attaque"]
        slot["munition"] = "Munition +1"
        self.assertEqual(eng.weapon_stats(slot)["attaque"], plain + 1)
        eng.shoot(slot)
        self.assertEqual(next(i["qte"] for i in eng.ch.equipement if i["nom"] == "Munition +1"), 9)
        self.assertEqual(eng.ammo_options({"nom": "Épée longue"}), [])


class ReactionConcentrationTests(unittest.TestCase):
    def test_reactions_by_class_and_spell(self):
        self.assertIn("Parade de projectiles", [r["nom"] for r in make([("Moine", 3, "")]).reactions()])
        self.assertIn("Esquive instinctive", [r["nom"] for r in make([("Roublard", 5, "")]).reactions()])
        eng = make([("Magicien", 3, "")])
        self.assertEqual([r["nom"] for r in eng.reactions()], ["Attaque d'opportunité"])
        eng.ch.sorts["Magicien"] = [{"nom": "Bouclier", "prepare": True}]
        self.assertIn("Bouclier", [r["nom"] for r in eng.reactions()])
        eng.use_reaction("opportunite")
        self.assertEqual(eng.ch.reaction_utilisee, "opportunite")
        eng.new_round()
        self.assertEqual(eng.ch.reaction_utilisee, "")

    def test_concentration_conflict_and_slots(self):
        eng = make([("Magicien", 5, "")])
        res = eng.cast_spell("Flou")
        self.assertTrue(res["ok"])
        self.assertEqual(eng.ch.emplacements_utilises[1], 1)
        self.assertEqual(eng.ch.concentration, "Flou")
        self.assertEqual(eng.concentration_conflict("Hâte"), "Flou")
        self.assertEqual(eng.concentration_conflict("Flou"), "")
        self.assertEqual(eng.concentration_conflict("Projectile magique"), "")
        eng.cast_spell("Hâte")
        self.assertEqual(eng.ch.concentration, "Hâte")
        eng.do_long_rest()
        self.assertEqual(eng.ch.concentration, "")


class RestTests(unittest.TestCase):
    def test_short_rest_hit_dice_and_time(self):
        eng = make([("Guerrier", 4, "")], Constitution=14)
        eng.ch.pv_actuels = 5
        res = eng.spend_hit_die("d10", roll=6)
        self.assertEqual(res["gain"], 8)
        self.assertEqual(eng.hit_dice_pool()[0]["restants"], 3)
        eng.do_short_rest()
        self.assertEqual(eng.time_text(), "Jour 1, 09:00")

    def test_long_rest_rations_and_24h_rule(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.equipement.append({"nom": "Rations", "qte": 2})
        eng.do_long_rest(eat_ration=True)
        self.assertEqual(eng.rations_available(), 1)
        self.assertTrue(eng.long_rest_warning())
        eng.advance_time(24 * 60)
        self.assertEqual(eng.long_rest_warning(), "")


class CorrectedDataTests(unittest.TestCase):
    def test_corrections_are_applied_and_idempotent(self):
        import apply_corrections as AC
        self.assertEqual(AC.apply_classes(write=False), [])
        self.assertEqual(AC.apply_races(write=False), [])

    def test_some_official_values(self):
        self.assertEqual(DB.race_ability_rule("Nain des montagnes")["fixe"], {"Constitution": 2, "Force": 2})
        life = DB.subclass("Clerc", "Domaine de la Vie")
        self.assertIn("Bénédiction", life["sorts_domaine"])
        self.assertIn("Soins", life["sorts_domaine"])


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        cls.win = mw.MainWindow(DB)
        cls.win.ch.classes = [{"nom": "Magicien", "niveau": 5, "sous_classe": "", "pv_jets": []}]
        cls.win.changed()

    def test_combat_status_bar_and_reactions(self):
        tab = self.win.combat_tab
        tab.fx_combo.addItem("Hâte", "hate")
        tab.fx_combo.setCurrentIndex(tab.fx_combo.findData("hate"))
        tab._on_add_effect()
        self.assertIn("hate", self.win.ch.effets_actifs)
        tab._on_remove_effect("hate")
        self.assertNotIn("hate", self.win.ch.effets_actifs)
        tab._on_reaction("opportunite")
        self.assertEqual(self.win.ch.reaction_utilisee, "opportunite")
        tab._on_new_round()
        self.assertEqual(self.win.ch.reaction_utilisee, "")

    def test_rest_dialog_logic(self):
        from ui.rest_dialog import RestDialog
        win = self.win
        win.ch.pv_actuels = 3
        dlg = RestDialog(win, "short")
        res = dlg._spend("d6", roll=4)
        self.assertIsNotNone(res)
        dlg.restore()                                   # « Annuler » : rien n'est consommé
        self.assertEqual(win.ch.pv_actuels, 3)
        self.assertEqual(win.ch.des_vie_utilises.get("d6", 0), 0)
        RestDialog(win, "long").apply()
        self.assertEqual(win.ch.pv_actuels, win.engine.hp_max())

    def test_magic_cast_requires_confirmation_to_break(self):
        win = self.win
        win.ch.concentration = "Flou"
        ok = win.magic_tab.cast("Hâte")                 # la fenêtre factice ne confirme pas : rien ne change
        self.assertFalse(ok)
        self.assertEqual(win.ch.concentration, "Flou")
        self.assertTrue(win.magic_tab.cast("Projectile magique"))   # pas de concentration : lancé directement


if __name__ == "__main__":
    unittest.main()


class LandCircleTests(unittest.TestCase):
    def test_terrain_choice_drives_circle_spells(self):
        eng = make([("Druide", 5, "Cercle de la Terre")])
        entry = eng.ch.classes[0]
        self.assertEqual(len(eng.land_terrains(entry)), 8)
        self.assertEqual(eng.land_terrain(entry), "Forêt")
        self.assertIn("Peau d'écorce", eng.domain_spells(entry))
        self.assertTrue(eng.set_land_terrain(0, "Arctique"))
        self.assertFalse(eng.set_land_terrain(0, "Lune"))
        self.assertEqual(eng.domain_spells(entry), ["Immobilisation de personne", "Croissance d'épines",
                                                    "Lenteur", "Tempête de neige"])
        for spells in eng.land_terrains(entry).values():
            self.assertTrue(all(DB.find_spell(n) for n in spells))
        self.assertEqual(make([("Druide", 5, "Cercle de la Lune")]).land_terrains(entry if False else
                         {"nom": "Druide", "niveau": 5, "sous_classe": "Cercle de la Lune"}), {})

    def test_terrain_selector_only_for_land_circle(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.classes = [{"nom": "Druide", "niveau": 3, "sous_classe": "Cercle de la Lune", "pv_jets": []}]
        win.changed()
        panel = win.classes_tab.panels[0]
        shown = []
        panel.terrain_row.setVisible = lambda v: shown.append(v)
        panel.refresh()
        self.assertEqual(shown[-1], False)
        win.ch.classes[0]["sous_classe"] = "Cercle de la Terre"
        panel.refresh()
        self.assertEqual(shown[-1], True)
        panel.terrain_combo.clear()
        panel.terrain_combo.addItems(["Désert"])
        panel.terrain_combo.setCurrentIndex(0)
        panel._on_terrain()
        self.assertEqual(win.ch.classes[0]["terrain"], "Désert")
