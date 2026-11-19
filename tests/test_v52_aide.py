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


from core.engine import Engine  # noqa: E402


def _sheet(cls, lvl, edition="2014", sub=""):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    eng.ch.classes[0]["sous_classe"] = sub
    eng.normalize()
    return eng


class TurnReminderTests(unittest.TestCase):
    def test_start_turn_resets_and_reminds(self):
        for ed in ("2014", "2024"):
            eng = _sheet("Barbare", 5, ed)
            eng.use_class_action("rage")
            eng.ch.tour_action = eng.ch.tour_bonus = True
            eng.ch.concentration = "Bénédiction"
            res = eng.start_turn()
            self.assertFalse(eng.ch.tour_action or eng.ch.tour_bonus)
            self.assertTrue(any(r.startswith("Rage") for r in res["rappels"]), ed)
            self.assertTrue(any("Concentration" in r for r in res["rappels"]))
        dying = _sheet("Guerrier", 3)
        dying.ch.pv_actuels = 0
        self.assertTrue(any("jet contre la mort" in r for r in dying.start_turn()["rappels"]))

    def test_text_triggers_both_editions(self):
        tree = _sheet("Barbare", 3, "2024", "Voie de l'Arbre-Monde")
        tree.use_class_action("rage")
        self.assertTrue(any(r.startswith("Vitalité de l'arbre") for r in tree.start_turn()["rappels"]))
        champ = _sheet("Guerrier", 18, "2024", "Champion")
        champ.ch.inspiration = False
        res = champ.start_turn()
        self.assertIn("Héros du champ d'honneur : Inspiration héroïque", res["appliques"])
        self.assertFalse(any(r.startswith("Survivant") for r in res["rappels"]))        # déjà appliqué
        for ed in ("2014", "2024"):
            barb = _sheet("Barbare", 7, ed)
            barb.roll_initiative(10)
            self.assertEqual([r for r in barb.initiative_reminders() if r.startswith("Instinct")], [])   # appliqué
        dance = _sheet("Barde", 6, "2024", "Collège de la Danse")
        dance.roll_initiative(10)
        self.assertTrue(any(r.startswith("Pirouettes coordonnées") for r in dance.initiative_reminders()))

    def test_end_turn_unused(self):
        for ed in ("2014", "2024"):
            eng = _sheet("Guerrier", 3, ed)
            msgs = eng.end_turn()
            self.assertTrue(any(m.startswith("Action non utilisée") for m in msgs))
            self.assertTrue(any("Second souffle" in m for m in msgs), ed)
            eng.ch.tour_action = eng.ch.tour_bonus = True
            self.assertEqual([m for m in eng.end_turn() if "non utilisée" in m], [])
        barb = _sheet("Barbare", 5, "2014")
        barb.use_class_action("rage")
        self.assertFalse(any("Entrer en rage" in m for m in barb.end_turn()))           # déjà en rage

    def test_ui_buttons(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        tab = win.combat_tab
        tab._on_new_round()
        self.assertIn("Début de votre tour", tab.turn_banner_text.text())
        tab._on_end_turn()
        self.assertIn("Fin de votre tour", tab.turn_banner_text.text())
        tab.show_turn_banner("", [])
        self.assertEqual(tab.turn_banner_text.text(), "")
