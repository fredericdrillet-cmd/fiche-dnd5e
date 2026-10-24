"""Tests v19 : actions de classe + sphères (ki, rage, dés de supériorité, conduit…), dés de dégâts animés
(d4 → d12, multi-dés), restriction de la bibliothèque au niveau du personnage (sauf mode MJ)."""
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core import dice as D  # noqa: E402
from core.engine import Engine  # noqa: E402


def make(classes):
    eng = Engine(DB, Engine.new_character(DB))
    eng.ch.classes = [{"nom": n, "niveau": lvl, "sous_classe": sub, "pv_jets": []} for n, lvl, sub in classes]
    eng.normalize()
    return eng


class DamageDiceTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(D.parse_damage("2d6+3"), ([(1, 2, 6)], 3))
        self.assertEqual(D.parse_damage("1d8 + 1d4 - 1"), ([(1, 1, 8), (1, 1, 4)], -1))
        self.assertEqual(D.parse_damage("36 m"), ([], 0))
        self.assertFalse(D.has_dice("—"))

    def test_roll_total(self):
        spec = D.DamageSpec("Test", "3d8+2", "feu")
        r = D.roll_damage(spec, random.Random(4))
        self.assertEqual(len(r.dice), 3)
        self.assertTrue(all(s == 8 and 1 <= v <= 8 for s, v, _ in r.dice))
        self.assertEqual(r.total, r.dice_sum + 2)

    def test_dialog_multi_dice(self):
        from ui.dice_dialog import DamageRollDialog, die_outline
        dlg = DamageRollDialog(None, D.DamageSpec("Boule de feu", "8d6", "feu"), random.Random(1))
        self.assertEqual(len(dlg.dice), 8)
        self.assertTrue(all(w.sides == 6 for w in dlg.dice))
        dlg.finish_now()
        self.assertEqual(dlg.phase, "done")
        self.assertIn(str(dlg.result.total), dlg.total.text())
        mixed = DamageRollDialog(None, D.DamageSpec("Mixte", "1d4+1d6+1d8+1d10+1d12"), random.Random(2))
        self.assertEqual([w.sides for w in mixed.dice], [4, 6, 8, 10, 12])
        self.assertTrue(callable(die_outline))          # géométrie réelle vérifiée hors stub (voir README)


class ClassActionTests(unittest.TestCase):
    def test_superiority_dice(self):
        eng = make([("Guerrier", 3, "Maître de guerre")])
        tr = {t["key"]: t for t in eng.resource_trackers("combat")}
        self.assertEqual((tr["superiorite"]["total"], tr["superiorite"]["de"]), (4, "d8"))
        eng = make([("Guerrier", 10, "Maître de guerre")])
        tr = {t["key"]: t for t in eng.resource_trackers("combat")}
        self.assertEqual((tr["superiorite"]["total"], tr["superiorite"]["de"]), (5, "d10"))
        self.assertNotIn("superiorite", {t["key"] for t in make([("Guerrier", 10, "Champion")]).resource_trackers()})

    def test_ki_spend_and_lock(self):
        eng = make([("Moine", 2, "")])
        ids = [a["id"] for a in eng.class_actions()]
        self.assertIn("deluge_coups", ids)
        self.assertNotIn("coup_etourdissant", ids)                 # niveau 5
        for _ in range(2):
            res = eng.use_class_action("deluge_coups")
            self.assertTrue(res["ok"])
            self.assertIsNotNone(res["attaque"])
        self.assertEqual(eng.resource_used("ki"), 2)
        a = next(x for x in eng.class_actions() if x["id"] == "deluge_coups")
        self.assertFalse(a["disponible"])
        self.assertIn("épuisé", a["raison"])
        self.assertFalse(eng.use_class_action("defense_patiente")["ok"])
        eng.short_rest()
        self.assertTrue(next(x for x in eng.class_actions() if x["id"] == "deluge_coups")["disponible"])

    def test_rage_action(self):
        eng = make([("Barbare", 3, "")])
        self.assertTrue(eng.use_class_action("rage")["ok"])
        self.assertIn("rage", eng.ch.effets_actifs)
        self.assertEqual(eng.resource_used("rage"), 1)
        self.assertTrue(next(x for x in eng.class_actions() if x["id"] == "rage")["actif"])   # v21 : bascule
        self.assertTrue(eng.use_class_action("rage")["ok"])                  # mettre fin : sans coût
        self.assertNotIn("rage", eng.ch.effets_actifs)
        self.assertEqual(eng.resource_used("rage"), 1)

    def test_smite_uses_slot(self):
        eng = make([("Paladin", 5, "")])
        before = list(eng.ch.emplacements_utilises)
        a = next(x for x in eng.class_actions() if x["id"] == "chatiment")
        self.assertEqual(a["formule"], "2d8")
        res = eng.use_class_action("chatiment", 2)
        self.assertTrue(res["ok"])
        self.assertEqual(res["degats"].formula, "3d8")
        self.assertEqual(eng.ch.emplacements_utilises[1], before[1] + 1)

    def test_maneuver_and_sneak(self):
        eng = make([("Guerrier", 3, "Maître de guerre")])
        res = eng.use_class_action("manoeuvre", choice="Riposte")
        self.assertEqual(res["degats"].formula, "1d8")
        self.assertIn("DD", res["degats"].note)
        eng = make([("Roublard", 7, "")])
        self.assertEqual(next(x for x in eng.class_actions() if x["id"] == "sournoise")["formule"], "4d6")

    def test_second_wind_heals_via_ui(self):
        import ui.combat_tab as ct
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.classes = [{"nom": "Guerrier", "niveau": 4, "sous_classe": "", "pv_jets": []}]
        win.changed()
        win.ch.pv_actuels = 5
        orig = ct.roll_damage_dialog
        self.addCleanup(lambda: setattr(ct, "roll_damage_dialog", orig))
        ct.roll_damage_dialog = lambda w, spec: D.DamageResult([(10, 6, 1)], 4, 10)
        self.assertIn("second_souffle", [w["id"] for w in win.combat_tab.act_rows])
        win.combat_tab._on_action("second_souffle")
        self.assertEqual(win.ch.pv_actuels, 15)
        self.assertEqual(win.engine.resource_used("second_souffle"), 1)
        win.combat_tab._on_action("second_souffle")                  # épuisé : aucun soin
        self.assertEqual(win.ch.pv_actuels, 15)

    def test_no_actions_for_wizard(self):
        self.assertEqual(make([("Magicien", 5, "")]).class_actions(), [])


class LibraryRestrictionTests(unittest.TestCase):
    def test_level_restriction_and_gm(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.classes = [{"nom": "Magicien", "niveau": 3, "sous_classe": "", "pv_jets": []}]
        win.changed()
        tab = win.magic_tab
        tab.select_class("Magicien")
        tab._on_level_chip(0)
        self.assertTrue(all(r["sort"]["niveau"] <= 2 for r in tab._lib_rows))
        # ajout forcé d'un sort trop haut : refusé hors mode MJ
        tab._lib_rows = [{"nom": "Boule de feu", "sort": DB.spells["Boule de feu"]}]
        tab.library.setCurrentRow(0)
        tab._on_add()
        self.assertNotIn("Boule de feu", [s["nom"] for s in win.ch.sorts.get("Magicien", [])])
        tab.all_chk.setChecked(True)
        tab._fill_library(force=True)
        self.assertTrue(any(r["sort"]["niveau"] >= 3 for r in tab._lib_rows))
        tab._lib_rows = [{"nom": "Boule de feu", "sort": DB.spells["Boule de feu"]}]
        tab.library.setCurrentRow(0)
        tab._on_add()
        self.assertIn("Boule de feu", [s["nom"] for s in win.ch.sorts["Magicien"]])
        tab.all_chk.setChecked(False)

    def test_detail_damage_only_in_grimoire(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.classes = [{"nom": "Magicien", "niveau": 5, "sous_classe": "", "pv_jets": []}]
        win.ch.sorts["Magicien"] = [{"nom": "Boule de feu", "prepare": True}]
        win.changed()
        tab = win.magic_tab
        tab.select_class("Magicien")
        idx = next(i for i, r in enumerate(tab._chosen_rows) if r["nom"] == "Boule de feu")
        tab._show_from(tab.chosen, idx)
        self.assertEqual(tab._detail_damage.formula, "8d6")
        lib = next(i for i, r in enumerate(tab._lib_rows) if r["nom"] == "Boule de feu") \
            if any(r["nom"] == "Boule de feu" for r in tab._lib_rows) else None
        if lib is not None:
            tab._show_from(tab.library, lib)
            self.assertIsNone(tab._detail_damage)


class PersistenceV19(unittest.TestCase):
    def test_new_resources_saved(self):
        from core.character import Character
        eng = make([("Guerrier", 5, "Maître de guerre")])
        eng.use_class_action("manoeuvre", choice="Riposte")
        eng.use_class_action("second_souffle")
        data = eng.ch.to_dict()
        ch2 = Character.from_dict(data)
        eng2 = Engine(DB, ch2)
        eng2.normalize()
        self.assertEqual(eng2.resource_used("superiorite"), 1)
        self.assertEqual(eng2.resource_used("second_souffle"), 1)


if __name__ == "__main__":
    unittest.main()
