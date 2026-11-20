"""v52 : filet de sécurité contre les plantages (rapport, sauvegarde, application qui continue)."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core import crash_report as CR  # noqa: E402
from core.data_loader import Database  # noqa: E402

DB = Database(ROOT / "data")


def boom():
    try:
        raise ValueError("test de plantage")
    except ValueError:
        return sys.exc_info()


class CrashTests(unittest.TestCase):
    def test_report_content_and_rotation(self):
        et, ev, tb = boom()
        text = CR.format_report(et, ev, tb, {"nom": "Eolin", "portrait": "xxx", "journal": [1]})
        self.assertIn("ValueError: test de plantage", text)
        self.assertIn('"nom": "Eolin"', text)
        self.assertNotIn('"portrait"', text)
        with tempfile.TemporaryDirectory() as d:
            for _ in range(25):
                CR.write_report(text, Path(d))
            self.assertEqual(len(list(Path(d).glob("erreur_*.txt"))), CR.KEEP)

    def test_handler_saves_and_continues(self):
        import qt_stub
        qt_stub.install()
        from ui import crash_guard as G
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(CR, "reports_dir", return_value=Path(d)), \
                mock.patch.object(win, "autosave", return_value=True) as save, \
                mock.patch.object(G, "_show") as show:
            G.install(win)
            self.assertIs(sys.excepthook, G.handle_exception)
            G.handle_exception(*boom())
            save.assert_called_once()
            show.assert_called_once()
            self.assertTrue(show.call_args[0][5])                    # « fiche sauvegardée »
            files = list(Path(d).glob("erreur_*.txt"))
            self.assertEqual(len(files), 1)
            self.assertIn("test de plantage", files[0].read_text(encoding="utf-8"))
        sys.excepthook = sys.__excepthook__

    def test_handler_survives_broken_window(self):
        from ui import crash_guard as G
        broken = mock.Mock()
        broken.engine.ch.to_dict.side_effect = RuntimeError("fiche cassée")
        broken.autosave.side_effect = RuntimeError("disque plein")
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(CR, "reports_dir", return_value=Path(d)), mock.patch.object(G, "_show"):
            G.install(broken)
            G.handle_exception(*boom())                              # ne relance rien
            self.assertEqual(len(list(Path(d).glob("erreur_*.txt"))), 1)
        sys.excepthook = sys.__excepthook__


if __name__ == "__main__":
    unittest.main()
