"""Tests v9 : modificateurs structurés (compétences, JS, caractéristiques, avantages), traits innés, potions,
objets équipés, purge des effets au repos, filtre des sorts préparés, infobulles de calcul."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from core import effects as FX  # noqa: E402
from core import mechanics as M  # noqa: E402
from test_v5_features import DB, make  # noqa: E402


def skill(eng, name):
    return next(r for r in eng.skill_rows() if r["nom"] == name)


class ModifierTests(unittest.TestCase):
    def test_pass_without_trace_and_heavy_armor(self):
        eng = make([("Guerrier", 1, "")], **{"Dextérité": 14})
        base = skill(eng, "Discrétion")["bonus"]
        eng.add_effect("passage_sans_trace")
        self.assertEqual(skill(eng, "Discrétion")["bonus"], base + 10)
        self.assertIn(("Passage sans trace", "+10"), skill(eng, "Discrétion")["detail"])
        eng.ch.armure["nom"] = "Harnois"
        eng.normalize()
        self.assertEqual(skill(eng, "Discrétion")["etat"], "désavantage")
        eng.remove_effect("passage_sans_trace")
        self.assertEqual(skill(eng, "Discrétion")["bonus"], base)

    def test_enlarge_bless_and_conditions(self):
        eng = make([("Guerrier", 1, "")])
        eng.add_effect("agrandissement")
        self.assertEqual(skill(eng, "Athlétisme")["etat"], "avantage")
        self.assertEqual(eng.save_rows()[0]["etat"], "avantage")
        eng.add_effect("benediction")
        self.assertEqual(eng.save_rows()[2]["des"], ["+1d4"])
        eng.add_effect("paralyse")
        self.assertEqual(eng.save_rows()[1]["etat"], "échec")
        eng.add_effect("empoisonne")                                    # désavantage aux tests
        self.assertEqual(skill(eng, "Perception")["etat"], "désavantage")
        eng.add_effect("hate")
        self.assertEqual(M.adv_state(eng.save_mods("Dextérité")), "échec")

    def test_advantage_and_disadvantage_cancel(self):
        eng = make([("Guerrier", 1, "")])
        eng.add_effect("agrandissement")
        eng.add_effect("malade")
        self.assertEqual(skill(eng, "Athlétisme")["etat"], "")

    def test_aid_and_exhaustion_hp(self):
        eng = make([("Guerrier", 4, "")])
        hp = eng.hp_max()
        eng.add_effect("aide")
        self.assertEqual(eng.hp_max(), hp + 5)
        eng.remove_effect("aide")
        eng.add_effect("epuisement_4")
        self.assertEqual(eng.hp_max(), hp // 2)

    def test_equipped_items(self):
        eng = make([("Guerrier", 3, "")], Force=14)
        eng.add_magic_item("Ceinturon de force de géant du givre")
        self.assertEqual(eng.score("Force"), 14)                          # harmonisation requise
        eng.ch.objets_magiques[-1]["harmonise"] = True
        eng.normalize()
        self.assertEqual(eng.score("Force"), 23)
        eng.add_magic_item("Bottes elfiques")
        self.assertEqual(skill(eng, "Discrétion")["etat"], "avantage")


class InnateTests(unittest.TestCase):
    def test_racial_resistances_are_permanent(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.race = "Tieffelin"
        eng.normalize()
        self.assertIn("resist_feu", eng.active_effect_keys())
        self.assertTrue(eng.innate_source("resist_feu").startswith("Trait racial"))
        self.assertIn(("feu", "Résistance (feu)"), eng.defenses()["resistances"])
        eng.clear_temporary_effects()
        self.assertIn("resist_feu", eng.active_effect_keys())
        eng.do_long_rest()
        self.assertIn("resist_feu", eng.active_effect_keys())
        eng.remove_effect("resist_feu")
        self.assertNotIn("resist_feu", eng.active_effect_keys())
        eng.add_effect("resist_feu")                                      # rétabli depuis le sélecteur
        self.assertIn("resist_feu", eng.active_effect_keys())

    def test_dwarf_and_monk(self):
        eng = make([("Moine", 10, "")])
        eng.ch.race = "Nain des collines"
        eng.normalize()
        keys = eng.active_effect_keys()
        for k in ("resist_poison", "avantage_js_poison", "immun_poison"):
            self.assertIn(k, keys)

    def test_all_damage_types_exist(self):
        for k in M.DAMAGE_TYPES:
            self.assertIn("resist_" + k, FX.EFFECTS)
            self.assertIn("immun_" + k, FX.EFFECTS)


class PotionAndRestTests(unittest.TestCase):
    def test_healing_strength_speed_vitality(self):
        eng = make([("Guerrier", 5, "")], Force=12)
        eng.ch.pv_actuels = 5
        for name in ("Potion de guérison", "Potion de force de géant du feu", "Potion de vitesse",
                     "Potion de vitalité"):
            eng.ch.equipement.append({"nom": name, "qte": 1})
        idx = next(c["index"] for c in eng.consumables() if c["nom"] == "Potion de guérison")
        eng.use_consumable("equipement", idx, roll=7)
        self.assertEqual(eng.ch.pv_actuels, 12)
        idx = next(c["index"] for c in eng.consumables() if "force" in c["nom"])
        eng.use_consumable("equipement", idx)
        self.assertEqual(eng.score("Force"), 25)
        self.assertEqual(skill(eng, "Athlétisme")["bonus"], 7 + eng.prof * skill(eng, "Athlétisme")["maitrise"])
        idx = next(c["index"] for c in eng.consumables() if "vitesse" in c["nom"])
        speed = eng.speed()
        eng.use_consumable("equipement", idx)
        self.assertEqual(eng.speed(), speed * 2)
        eng.add_effect("empoisonne")
        idx = next(c["index"] for c in eng.consumables() if "vitalit" in c["nom"])
        eng.use_consumable("equipement", idx)
        self.assertNotIn("empoisonne", eng.active_effect_keys())
        self.assertEqual(eng.consumables(), [])                           # tout a été consommé

    def test_resistance_potion_and_rest_purge(self):
        eng = make([("Barbare", 3, "")])
        eng.ch.equipement.append({"nom": "Potion de résistance", "qte": 1})
        eng.use_consumable("equipement", 0, choice="froid")
        self.assertIn("resist_froid", eng.active_effect_keys())
        eng.add_effect("armure_mage")
        eng.set_resource_used("rage", 1)
        eng.do_short_rest()
        keys = eng.active_effect_keys()
        self.assertNotIn("rage", keys)
        self.assertNotIn("resist_froid", keys)                            # potion : 1 heure
        self.assertIn("armure_mage", keys)                                # 8 heures : survit au repos court
        eng.do_long_rest()
        self.assertNotIn("armure_mage", eng.active_effect_keys())


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        cls.win = mw.MainWindow(DB)

    def test_innate_removal_needs_confirmation(self):
        win = self.win
        win.ch.race = "Tieffelin"
        win.changed()
        win.combat_tab._on_remove_effect("resist_feu")                   # fenêtre factice : « Non »
        self.assertIn("resist_feu", win.engine.active_effect_keys())
        win.ch.effets_actifs = ["hate"]
        win.combat_tab._on_clear_effects()
        self.assertEqual(win.ch.effets_actifs, [])
        self.assertIn("resist_feu", win.engine.active_effect_keys())

    def test_prepared_filter(self):
        win = self.win
        win.ch.classes = [{"nom": "Clerc", "niveau": 3, "sous_classe": "Domaine de la Vie", "pv_jets": []}]
        win.ch.sorts["Clerc"] = [{"nom": "Bénédiction", "prepare": True}, {"nom": "Soins", "prepare": False}]
        win.changed()
        win.magic_tab.select_class("Clerc")
        all_rows = [r["nom"] for r in win.magic_tab._chosen_rows]
        win.magic_tab.prepared_only.setChecked(True)
        win.magic_tab.refresh()
        filtered = [r["nom"] for r in win.magic_tab._chosen_rows]
        self.assertIn("Soins", all_rows)
        self.assertLess(len(filtered), len(all_rows) + 1)
        self.assertTrue(all(not (r["nom"] == "Soins" and not r["domaine"]) for r in win.magic_tab._chosen_rows))

    def test_inventory_use_button(self):
        win = self.win
        win.ch.equipement = [{"nom": "Potion de guérison", "qte": 2}]
        win.ch.pv_actuels = 1
        win.changed()
        win.inventory_tab.table._st["row"] = 0
        win.inventory_tab._on_use_item()
        self.assertEqual(win.ch.equipement[0]["qte"], 1)
        self.assertGreater(win.ch.pv_actuels, 1)


if __name__ == "__main__":
    unittest.main()
