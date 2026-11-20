"""v52 : outils de confort — recherche Ctrl+F, raccourcis, journal de session, aide-mémoire, lumière, contresort."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def sheet(cls="Magicien", lvl=5, edition="2014", sub=""):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    return eng


class SearchTests(unittest.TestCase):
    def test_sheet_first_then_rules(self):
        eng = sheet("Guerrier", 3, "2014")
        res = eng.quick_search("second souffle")
        self.assertEqual(res[0]["groupe"], "fiche")
        self.assertTrue(res[0]["onglet"])
        self.assertEqual(eng.quick_search("a"), [])

    def test_edition_filter(self):
        old = [r["nom"] for r in sheet(edition="2014").quick_search("boule de feu")]
        new = [r["nom"] for r in sheet(edition="2024").quick_search("boule de feu")]
        self.assertIn("Boule de feu", old)
        self.assertNotIn("Boule de feu (2024)", old)
        self.assertIn("Boule de feu (2024)", new)
        self.assertNotIn("Boule de feu", new)

    def test_glossary_and_states(self):
        types = {r["type"] for r in sheet().quick_search("agripp")}
        self.assertIn("État", types)

    def test_dialog_opens_tab(self):
        import qt_stub
        qt_stub.install()
        from unittest import mock
        from ui.main_window import MainWindow
        from ui.search_dialog import SearchDialog
        win = MainWindow(DB)
        dlg = SearchDialog(win, "attaque")
        self.assertTrue(dlg.results)
        fiche = next(r for r in dlg.results if r["groupe"] == "fiche")
        with mock.patch.object(dlg, "current", return_value=fiche), \
                mock.patch.object(win, "open_tab", return_value=True) as op:
            dlg.open_selected()
        op.assert_called_once_with(fiche["onglet"])


if __name__ == "__main__":
    unittest.main()


class CounterTests(unittest.TestCase):
    def test_2014_auto_and_check(self):
        eng = sheet("Magicien", 5, "2014")
        info = eng.counter_info("Contresort", 3, 3)
        self.assertTrue(info["auto"])
        info = eng.counter_info("Contresort", 3, 5)
        self.assertEqual((info["dd"], info["carac"]), (15, "Intelligence"))
        spec = eng.counter_check_spec("Contresort", 15, "Intelligence")
        self.assertIn("DD 15", spec.title)
        self.assertIn("réussite", eng.counter_result("Contresort", 16, 15))
        self.assertIn("échec", eng.counter_result("Contresort", 12, 15))

    def test_2024_counterspell_save(self):
        eng = sheet("Magicien", 5, "2024")
        info = eng.counter_info("Contresort (2024)", 3, 5)
        self.assertFalse(info["auto"])
        self.assertEqual(info["dd"], 0)
        self.assertEqual(info["js_dd"], eng.casters()[0]["dc"])
        self.assertIn("Constitution", info["texte"])

    def test_dispel_both_editions(self):
        for ed, name in (("2014", "Dissipation de la magie"), ("2024", "Dissipation de la magie (2024)")):
            eng = sheet("Magicien", 5, ed)
            self.assertEqual(eng.counter_kind(name), "dissipation")
            self.assertEqual(eng.counter_info(name, 3, 4)["dd"], 14)

    def test_abjurer_bonus(self):
        eng = sheet("Magicien", 10, "2014", "École d'Abjuration")
        if not eng.has_feature("abjuration amelioree"):
            self.skipTest("aptitude absente des données")
        spec = eng.counter_check_spec("Contresort", 15, "Intelligence")
        self.assertTrue(any(t.label == "Abjuration améliorée" for t in spec.terms))


class LightTests(unittest.TestCase):
    def test_torch_and_lantern(self):
        for ed in ("2014", "2024"):
            eng = sheet("Guerrier", 3, ed)
            self.assertIn("aveuglé", eng.light_status())
            eng.ch.equipement += [{"nom": "Torche", "qte": 1}, {"nom": "Lanterne à capote", "qte": 1},
                                  {"nom": "Huile", "qte": 2}]
            self.assertIn("allumée", eng.light_source("lumiere_torche"))
            self.assertEqual(next(i for i in eng.ch.equipement if i["nom"] == "Torche")["qte"], 0)
            self.assertEqual(eng.effect_rounds("lumiere_torche"), 600)
            self.assertFalse(next(o for o in eng.light_options() if o["key"] == "lumiere_torche")["possible"])
            eng.light_source("lumiere_lanterne")
            self.assertEqual(eng.effect_rounds("lumiere_lanterne"), 3600)
            self.assertIn("Éclairé", eng.light_status())
            eng.advance_time(60)
            self.assertNotIn("lumiere_torche", eng.ch.effets_actifs)
            self.assertIn("lumiere_lanterne", eng.ch.effets_actifs)

    def test_darkvision_reminder(self):
        eng = sheet("Guerrier", 3, "2014")
        eng.ch.race = "Nain des collines"
        eng.normalize()
        if eng.darkvision()["portee"]:
            self.assertIn("vision dans le noir", eng.light_status())

    def test_tab_only_with_survival_rule(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.environment_dialog import EnvironmentDialog
        win = MainWindow(DB)
        win.settings["regle_survie"] = False
        self.assertEqual(EnvironmentDialog(win).light_btns, {})
        win.settings["regle_survie"] = True
        self.assertEqual(len(EnvironmentDialog(win).light_btns), 4)


class CheatsheetTests(unittest.TestCase):
    def test_cheatsheet_both_editions(self):
        from core.sheet_export import sheet_html
        for ed in ("2014", "2024"):
            eng = sheet("Paladin", 5, ed)
            html = sheet_html(eng, cheatsheet=True)
            self.assertIn("Aide-mémoire de combat", html)
            self.assertIn("Ressources à cocher", html)
            self.assertIn("États courants — règles {}".format(ed), html)
            self.assertNotIn("Aide-mémoire de combat", sheet_html(eng))
        self.assertIn("autre que l", sheet_html(sheet("Guerrier", 3, "2024"), True))


class ShortcutTests(unittest.TestCase):
    def test_turn_shortcuts(self):
        import qt_stub
        qt_stub.install()
        from unittest import mock
        from ui.main_window import MainWindow
        from ui import main_window as MW
        win = MainWindow(DB)
        win.action_start_turn()
        self.assertIn("Début de votre tour", win.combat_tab.turn_banner_text.text())
        win.action_end_turn()
        self.assertIn("Fin de votre tour", win.combat_tab.turn_banner_text.text())
        win.engine.record_initiative(10)
        win.action_end_combat()
        self.assertFalse(win.engine.in_combat())
        keys = [k for k, _ in win.SHORTCUTS]
        for k in ("Ctrl+F", "Ctrl+T", "Ctrl+E", "Ctrl+I", "Ctrl+A", "Ctrl+R"):
            self.assertTrue(any(k in x for x in keys), k)
        with mock.patch.object(MW, "ask_yes_no", return_value=True) as ask:
            win.action_shortcuts()
        self.assertIn("Ctrl+T", ask.call_args[0][2])


class JournalTests(unittest.TestCase):
    def test_diff_events(self):
        for ed in ("2014", "2024"):
            eng = sheet("Clerc", 3, ed)
            eng.ch.pv_actuels = eng.hp_max()
            before = eng.ch.to_dict()
            eng.take_damage(5)
            eng.add_effect("empoisonne")
            events = eng.record_diff(before)
            self.assertTrue(any(e.startswith("Dégâts : −5") for e in events), events)
            self.assertTrue(any("Empoisonné" in e for e in events))
            before = eng.ch.to_dict()
            name = "Bénédiction" if ed == "2014" else "Bénédiction (2024)"
            if not eng.db.find_spell(name):
                name = "Bénédiction"
            eng.cast_spell(name, slot_level=1, target="allie")
            events = eng.record_diff(before)
            self.assertFalse(any("Emplacement" in e for e in events))       # déjà dans « Sort lancé »
            self.assertTrue(eng.ch.journal[0]["texte"].startswith("Sort lancé") or
                            any(j["texte"].startswith("Sort lancé") for j in eng.ch.journal))
            before = eng.ch.to_dict()
            eng.do_long_rest()
            eng.record_diff(before)
            self.assertTrue(any(j["texte"] == "Repos long" for j in eng.ch.journal))
            self.assertFalse(any(j["texte"].startswith("Soins") for j in eng.ch.journal[:2]))

    def test_limit_and_text(self):
        eng = sheet()
        for i in range(520):
            eng.log("Événement {}".format(i))
        self.assertEqual(len(eng.ch.journal), 500)
        self.assertEqual(eng.ch.journal[0]["texte"], "Événement 519")
        text = eng.journal_text()
        self.assertTrue(text.splitlines()[-1].endswith("Événement 519"))

    def test_window_and_undo(self):
        import tempfile
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.history_dialog import HistoryDialog
        win = MainWindow(DB)
        win.engine.ch.pv_actuels = win.engine.hp_max()
        win.reset_history()
        win.engine.take_damage(3)
        win.changed()
        self.assertTrue(any(j["texte"].startswith("Dégâts") for j in win.engine.ch.journal))
        n = len(win.engine.ch.journal)
        win.action_undo()
        self.assertEqual(len(win.engine.ch.journal), n)                  # le journal n'est pas annulé
        dlg = HistoryDialog(win, 1)
        with tempfile.TemporaryDirectory() as d:
            path = dlg.export_journal(str(Path(d) / "j.txt"))
            self.assertIn("Dégâts", Path(path).read_text(encoding="utf-8"))
        dlg.clear_journal()
        self.assertEqual(win.engine.ch.journal, [])
