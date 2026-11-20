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
