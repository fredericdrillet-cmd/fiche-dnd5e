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
