"""v52 : retours d'essai — création (compétences, styles, identité), PV (dégâts, soins, 0 PV), repos, En partie."""
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def sheet(cls="Guerrier", lvl=1, edition="2014"):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    return eng


class SkillChoiceTests(unittest.TestCase):
    def test_off_list_and_background(self):
        eng = sheet()
        eng.ch.historique = next(iter(DB.backgrounds))
        eng.apply_background()
        self.assertEqual(eng.skill_choice_errors(), [])           # l'historique ne compte pas
        eng.ch.competences["Arcanes"] = {"maitrise": True, "expertise": False}
        self.assertIn("Arcanes ne fait pas partie des compétences de Guerrier.", eng.skill_choice_errors())
        eng.ch.competences["Arcanes"]["maitrise"] = False
        for s in ("Athlétisme", "Acrobaties", "Survie"):
            eng.ch.competences[s] = {"maitrise": True, "expertise": False}
        self.assertTrue(any("Trop" in e for e in eng.skill_choice_errors()))


class HpTests(unittest.TestCase):
    def test_zero_hp_states_and_heal(self):
        for ed in ("2014", "2024"):
            eng = sheet("Guerrier", 3, ed)
            eng.ch.pv_actuels = 5
            eng.take_damage(8)
            self.assertEqual(eng.ch.pv_actuels, 0)
            self.assertIn("inconscient", eng.ch.effets_actifs)
            self.assertIn("a_terre", eng.ch.effets_actifs)
            self.assertTrue(eng.dropped_to_zero)
            eng.ch.mort_echecs = 2
            eng.receive_healing(4)
            self.assertNotIn("inconscient", eng.ch.effets_actifs)
            self.assertIn("a_terre", eng.ch.effets_actifs)
            self.assertEqual(eng.ch.mort_echecs, 0)

    def test_rest_wakes_up(self):
        for rest in ("court", "long"):
            eng = sheet("Guerrier", 3)
            eng.ch.pv_actuels = 1
            eng.take_damage(5)
            if rest == "court":
                eng.do_short_rest()
                self.assertEqual(eng.ch.pv_actuels, 1)
            else:
                eng.do_long_rest()
                self.assertEqual(eng.ch.pv_actuels, eng.hp_max())
            self.assertNotIn("inconscient", eng.ch.effets_actifs)
            self.assertNotIn("a_terre", eng.ch.effets_actifs)


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        cls.win = MainWindow(DB)

    def test_damage_heal_and_zero_message(self):
        from ui import combat_tab as CT
        tab, eng = self.win.combat_tab, self.win.engine
        eng.ch.pv_actuels = eng.hp_max()
        eng.ch.effets_actifs = []
        eng.add_effect("resist_feu")
        before = eng.ch.pv_actuels
        tab.apply_damage(10, "feu")
        self.assertEqual(eng.ch.pv_actuels, before - 5)               # résistance : moitié
        tab.apply_heal(3)
        self.assertEqual(eng.ch.pv_actuels, before - 2)
        tab.apply_heal(4, temp=True)
        self.assertEqual(eng.ch.pv_temporaires, 4)
        eng.ch.pv_temporaires = 0
        with mock.patch.object(CT, "ask_yes_no", return_value=False) as ask:
            tab.apply_damage(eng.ch.pv_actuels + 1)                   # 0 PV sans mort instantanée
        self.assertEqual(eng.ch.pv_actuels, 0)
        ask.assert_called_once()
        self.assertIn("0 PV", ask.call_args[0][1])

    def test_header_inspiration_and_init_badge(self):
        tab = self.win.combat_tab
        tab._on_inspiration(True)
        self.assertTrue(self.win.engine.ch.inspiration)
        tab.refresh()
        self.assertTrue(tab.insp_check.isChecked())
        self.assertNotIn("inspiration:recevoir", tab.turn_tiles)
        self.assertIn("❤", tab.hp_big.text())

    def test_magic_common_action_hidden(self):
        tab, eng = self.win.combat_tab, self.win.engine
        eng.set_edition_mode("2024")
        eng.normalize()
        self.win.changed()
        self.assertIn("commune:etudier", tab.turn_tiles)
        self.assertNotIn("commune:magie", tab.turn_tiles)
        eng.set_edition_mode("2014")
        eng.normalize()
        self.win.changed()


class WizardTests(unittest.TestCase):
    def test_skills_step_and_identity(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.creation_wizard import CreationWizard, STEPS
        win = MainWindow(DB)
        w = CreationWizard(win)
        self.assertEqual(STEPS[3], "Compétences")
        w._on_class("Guerrier")
        w.go(3)
        w.ch.competences["Arcanes"] = {"maitrise": True, "expertise": False}
        w.refresh()
        self.assertIn("Arcanes", w.skill_errors.text())
        self.assertFalse(w.step_done()[3])
        w.ch.competences["Arcanes"]["maitrise"] = False
        w.refresh()
        w._set_identity("nom", "Aldric")
        self.assertFalse(w.step_done()[7])
        w._set_identity("joueur", "Fred")
        w.set_portrait("iVBORw0KGgo=")
        self.assertTrue(w.step_done()[7])

    def test_style_description_shown(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.creation_wizard import CreationWizard
        w = CreationWizard(MainWindow(DB))
        w._on_class("Guerrier")
        w.go(2)
        self.assertIn("style de combat", w.style_desc.text().lower())
        sid = next(s["id"] for s in w.engine.fighting_style_slots())
        w.set_style(sid, "Défense")
        w.go(2)
        self.assertIn("Défense", w.style_desc.text())


if __name__ == "__main__":
    unittest.main()


class FormTilesTests(unittest.TestCase):
    def test_wild_shape_and_polymorph_tiles(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        eng = win.engine
        eng.ch.classes = [{"nom": "Druide", "niveau": 4, "sous_classe": "", "pv_jets": []}]
        eng.normalize()
        self.assertTrue(eng.assume_form("Loup"))
        win.changed()
        tab = win.combat_tab
        self.assertIn("bete:0", tab.turn_tiles)
        self.assertIn("vos PV", tab.hp_big.text())               # PV de la bête en tête
        eng.end_form()
        eng.ch.classes = [{"nom": "Magicien", "niveau": 7, "sous_classe": "", "pv_jets": []}]
        eng.ch.sorts = {"Magicien": [{"nom": "Métamorphose", "prepare": True}]}
        eng.normalize()
        self.assertTrue(eng.cast_polymorph("Ours brun", True)["ok"])
        win.changed()
        self.assertIn("bete:1", tab.turn_tiles)
        self.assertIn("vos PV", tab.hp_big.text())


class FormEndTests(unittest.TestCase):
    def test_beast_drops_to_zero(self):
        eng = sheet("Druide", 4)
        eng.ch.pv_actuels = 20
        eng.assume_form("Loup")
        eng.take_damage(eng.ch.forme_pv + 4)
        self.assertEqual(eng.ch.forme_active, "")
        self.assertEqual(eng.ch.pv_actuels, 16)
        self.assertIn("forme normale", eng.form_ended_message)
        self.assertIn("16 / ", eng.form_ended_message)

    def test_polymorph_overflow_knocks_out(self):
        eng = sheet("Magicien", 7)
        eng.ch.sorts = {"Magicien": [{"nom": "Métamorphose", "prepare": True}]}
        eng.ch.pv_actuels = 10
        eng.cast_polymorph("Loup", True)
        eng.take_damage(eng.ch.forme_pv + 12)
        self.assertEqual((eng.ch.forme_active, eng.ch.pv_actuels, eng.ch.concentration), ("", 0, ""))
        self.assertIn("inconscient", eng.ch.effets_actifs)
        self.assertTrue(eng.dropped_to_zero)
        self.assertIn("Métamorphose prend fin", eng.form_ended_message)

    def test_ui_message_then_zero(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui import combat_tab as CT
        win = MainWindow(DB)
        eng = win.engine
        eng.ch.classes = [{"nom": "Druide", "niveau": 4, "sous_classe": "", "pv_jets": []}]
        eng.normalize()
        eng.ch.pv_actuels = 3
        eng.assume_form("Loup")
        win.changed()
        with mock.patch.object(CT, "ask_yes_no", return_value=False) as ask:
            win.combat_tab.apply_damage(eng.ch.forme_pv + 5)
        titles = [c[0][1] for c in ask.call_args_list]
        self.assertEqual(titles[0], "Fin de la transformation")
        self.assertIn("0 PV — inconscient", titles)
        self.assertFalse(win.combat_tab.form_box.isVisibleTo(win.combat_tab) and eng.ch.forme_active)


class InventoryTests(unittest.TestCase):
    def test_weapon_settings_and_actions_tiles(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        eng = win.engine
        eng.ch.equipement += [{"nom": "Épée longue", "qte": 1}]
        eng.ch.armes_cac[0] = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        win.changed()
        inv = win.inventory_tab
        inv._set_weapon("armes_cac", 0, "bonus", 2)
        self.assertEqual(eng.ch.armes_cac[0]["bonus"], 2)
        inv._set_weapon("armes_cac", 0, "maitrise", False)
        self.assertFalse(eng.weapon_stats(eng.ch.armes_cac[0])["maitrise"])
        rows = win.combat_tab._weapon_action_rows()
        win.combat_tab.refresh()
        for key, i, row, _w in rows:
            self.assertIn("arme_action:{}:{}:{}".format(key, i, row["cle"]), win.combat_tab.turn_tiles)

    def test_magic_library_not_rebuilt(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        panel = win.inventory_tab.magic_items
        panel._fill_library(force=True)
        key = panel._lib_key
        with mock.patch.object(panel.library, "setRowCount") as rc:
            panel._fill_library()
        rc.assert_not_called()
        self.assertEqual(panel._lib_key, key)
