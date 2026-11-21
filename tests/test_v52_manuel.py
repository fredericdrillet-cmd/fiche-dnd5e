"""v52 : manuel d'utilisation (data/Manuel.json) — chapitres, recherche, fenêtre, export PDF."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402

DB = Database(ROOT / "data")


class ManualTests(unittest.TestCase):
    def test_chapters_cover_every_tab(self):
        m = DB.manual
        self.assertTrue(m)
        for key in ("classes", "caracteristiques", "race", "rp", "combat", "magie", "druide", "menagerie",
                    "progression", "inventaire"):
            self.assertIsNotNone(m.chapter_for_tab(key), key)
        ids = [c["id"] for c in m.chapters]
        for cid in ("demarrer", "repos", "fichiers", "raccourcis"):
            self.assertIn(cid, ids)

    def test_search_and_html(self):
        m = DB.manual
        hits = m.search("munitions")
        self.assertTrue(any(cid == "combat" for cid, _, _ in hits))
        self.assertEqual(m.search("x"), [])
        self.assertIn("<u>", m.chapter_html("combat", "munitions"))
        self.assertIn("Manuel d'utilisation", m.print_html())

    def test_shortcuts_mentioned(self):
        text = " ".join(s["texte"] for c in DB.manual.chapters for s in c["sections"])
        for k in ("Ctrl+F", "Ctrl+T", "Ctrl+E", "Ctrl+H", "F2"):
            self.assertIn(k, text)

    def test_dialog(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.manual_dialog import ManualDialog
        win = MainWindow(DB)
        dlg = ManualDialog(win, "magie")
        self.assertEqual(dlg.current_id, "magie")
        with mock.patch.object(win, "open_tab", return_value=True) as op:
            self.assertTrue(dlg.open_tab())
        op.assert_called_once_with("magie")
        dlg.show_chapter("raccourcis")
        self.assertFalse(dlg.open_tab())
        with mock.patch("ui.manual_dialog.ManualDialog.exec", return_value=0) as ex:
            win.action_manual()
        ex.assert_called_once()

    def test_banner_link(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        win.settings["aides_debutant"] = True
        win.refresh_help_banner()
        if win.help_banner.text():
            self.assertIn("Voir le manuel", win.help_banner.text())



if __name__ == "__main__":
    unittest.main()
