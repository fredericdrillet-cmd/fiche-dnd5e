"""Tests v8 : onglet conservé, Combat épuré et réordonné, couplage ressources / états, effets sur la CA et les
dégâts, vue Caractéristiques + Compétences, performances et tri des dons, libellés d'onglets."""
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from core.rules import norm  # noqa: E402
from test_v5_features import DB, make  # noqa: E402


class EngineCouplingTests(unittest.TestCase):
    def test_rage_orb_toggles_effect_and_damage(self):
        eng = make([("Barbare", 9, "")], Force=16)
        slot = {"nom": "Hache à deux mains", "bonus": 0, "maitrise": None}
        eng.ch.armes_cac[0] = slot
        self.assertEqual(eng.weapon_stats(slot)["degats"], "1d12+3")
        eng.set_resource_used("rage", 1)
        self.assertIn("rage", eng.ch.effets_actifs)
        self.assertEqual(eng.weapon_stats(slot)["degats"], "1d12+6")         # +3 au niveau 9
        bow = {"nom": "Arc long", "bonus": 0, "maitrise": None}
        self.assertNotIn("Rage", " ".join(eng.weapon_stats(bow)["styles"]))   # pas de bonus à distance
        eng.set_resource_used("rage", 0)
        self.assertNotIn("rage", eng.ch.effets_actifs)

    def test_wild_shape_effect_follows_form(self):
        eng = make([("Druide", 2, "")])
        beast = eng.allowed_beasts()[0]["nom"]
        eng.assume_form(beast)
        self.assertIn("forme_sauvage", eng.ch.effets_actifs)
        eng.end_form()
        self.assertNotIn("forme_sauvage", eng.ch.effets_actifs)
        eng.assume_form(beast)
        eng.remove_effect("forme_sauvage")                                   # retrait depuis la barre d'états
        self.assertEqual(eng.ch.forme_active, "")

    def test_mage_armor_and_bladesong_ac(self):
        eng = make([("Magicien", 2, "")], **{"Dextérité": 14, "Intelligence": 16})
        self.assertEqual(eng.armor_class_detail()["valeur"], 12)
        eng.add_effect("armure_mage")
        self.assertEqual(eng.armor_class_detail()["valeur"], 15)
        eng.add_effect("chant_lame")
        self.assertEqual(eng.armor_class_detail()["valeur"], 18)
        eng.ch.armure["bouclier"] = True                                     # Chant de la lame : pas de bouclier
        self.assertNotIn("Chant", eng.armor_class_detail()["formule"])

    def test_hp_always_average(self):
        eng = make([("Guerrier", 3, "")])
        eng.ch.pv_mode = "jets"
        eng.normalize()
        self.assertEqual(eng.ch.pv_mode, "moyenne")


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        cls.win = mw.MainWindow(DB)

    def test_tab_bar_not_rebuilt_on_class_change(self):
        win = self.win
        items = list(win.tabs._st["items"])
        win.ch.classes = [{"nom": "Druide", "niveau": 2, "sous_classe": "", "pv_jets": []}]
        win.changed()
        self.assertEqual(win.tabs._st["items"], items)                        # aucun onglet retiré / recréé
        self.assertIn("druide", win.shown_keys())
        win.ch.classes = [{"nom": "Guerrier", "niveau": 2, "sous_classe": "", "pv_jets": []}]
        win.changed()
        self.assertEqual(win.tabs._st["items"], items)
        self.assertNotIn("druide", win.shown_keys())

    def test_merged_stats_tab_and_clean_titles(self):
        keys = [k for k, _, _ in self.win.tab_defs]
        self.assertNotIn("competences", keys)
        self.assertIs(self.win.abilities_tab, self.win.stats_tab.abilities)
        self.assertIs(self.win.skills_tab, self.win.stats_tab.skills)
        for _, _, title in self.win.tab_defs:
            self.assertNotIn("&", title.replace("&&", ""))   # « && » = « & » littéral (v36 : Ménagerie & Montures)
            self.assertNotIn("_", title)

    def test_combat_hp_controls_removed(self):
        tab = self.win.combat_tab
        self.assertNotIn("_on_roll_hp", vars(type(tab)))
        self.assertNotIn("_on_hp_mode", vars(type(tab)))
        self.assertNotIn("roll_hp", tab.__dict__)
        self.assertNotIn("hp_mode", tab.__dict__)

    def test_feats_sorted_and_progression_fast(self):
        names = self.win.progress_tab.feat_names()
        self.assertEqual(names, sorted(names, key=lambda n: (norm(n), n)))
        self.assertEqual(list(DB.feats), names)
        win = self.win
        win.ch.classes = [{"nom": "Guerrier", "niveau": 12, "sous_classe": "", "pv_jets": []}]
        win.changed()
        start = time.perf_counter()
        with win.engine.batch():
            win.progress_tab.refresh()
        self.assertLess(time.perf_counter() - start, 0.5)


if __name__ == "__main__":
    unittest.main()
