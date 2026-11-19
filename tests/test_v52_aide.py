"""v52 : aides de jeu — lexique des règles (survol, F1, option « Aides pour débuter »)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402

DB = Database(ROOT / "data")


class GlossaryTests(unittest.TestCase):
    def test_data_loaded(self):
        g = DB.glossary
        self.assertGreaterEqual(len(g.terms), 60)
        self.assertFalse(any("Lexique" in w for w in DB.warnings))
        self.assertIn("combat", g.tab_help)
        self.assertIn("Classe", g.step_help)
        self.assertIs(DB.view_2024().glossary, g)

    def test_find_whole_words_longest_first(self):
        g = DB.glossary
        found = [t["terme"] for t in g.find("Par une action bonus, JS de Sagesse DD 13 ; charmé. Charme-personne.", 10)]
        self.assertEqual(found, ["Action bonus", "Jet de sauvegarde", "DD", "Charmé"])
        self.assertEqual(g.find("Esquive instinctive"), [])            # « Esquiver » n'est pas une variante

    def test_definition_by_edition(self):
        g = DB.glossary
        rest = g.get("Repos long")
        self.assertIn("moitié", g.definition(rest, 2014))
        self.assertNotIn("moitié", g.definition(rest, 2024))
        self.assertIn("2014 :", g.definition(rest, 0))
        self.assertTrue(g.search("concentration"))


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        cls.win = MainWindow(DB)

    def test_rich_tip_has_definitions(self):
        from ui import common
        tip = common.rich_tip("Bouclier", "Réaction : +5 à la CA jusqu'au début de votre prochain tour.")
        self.assertIn("Lexique", tip)
        self.assertIn("Réaction", tip)
        self.assertNotIn("Lexique", common.rich_tip("Avantage", "Lancez deux dés."))   # le titre lui-même exclu

    def test_beginner_option(self):
        from ui import common
        win = self.win
        win.settings["aides_debutant"] = False
        win.refresh_help_banner()
        self.assertEqual(win.help_banner.text(), "")
        self.assertNotIn("<u>", common.make_label("Une action bonus", wrap=True).text())
        win.settings["aides_debutant"] = True
        win.tabs.currentWidget = lambda: win.combat_tab          # faux Qt : onglet courant imposé
        win.refresh_help_banner()
        self.assertIn("tuile", win.help_banner.text())
        self.assertIn("<u>action bonus</u>", common.make_label("Une action bonus", wrap=True).text())
        win.settings["aides_debutant"] = False

    def test_glossary_dialog(self):
        from ui.glossary_dialog import GlossaryDialog, term_html
        dlg = GlossaryDialog(self.win, DB.glossary, 2024, "concentration")
        self.assertTrue(dlg._shown)
        self.assertIn("(votre fiche)", term_html(DB.glossary, DB.glossary.get("Repos long"), 2024))

    def test_wizard_step_help(self):
        from ui.creation_wizard import CreationWizard
        self.win.settings["aides_debutant"] = True
        wiz = CreationWizard(self.win)
        wiz.go(2)
        self.assertIn("métier", wiz.step_help.text())
        self.win.settings["aides_debutant"] = False
        wiz.go(1)
        self.assertEqual(wiz.step_help.text(), "")


if __name__ == "__main__":
    unittest.main()
