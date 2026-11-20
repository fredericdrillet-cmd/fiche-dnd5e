"""v52 : versions de sauvegarde (10 dernières), restauration."""
import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core import versions as V  # noqa: E402
from core.data_loader import Database  # noqa: E402

DB = Database(ROOT / "data")


class VersionTests(unittest.TestCase):
    def test_keep_ten_and_list(self):
        with tempfile.TemporaryDirectory() as d:
            root, save = Path(d) / "versions", Path(d) / "eolin.json"
            for i in range(12):
                save.write_text('{"nom": "Eolin", "classes": [{"nom": "Rôdeur", "niveau": %d}], "pv_actuels": 9}'
                                % (i + 1), encoding="utf-8")
                V.save_version(save, root, now=dt.datetime(2026, 11, 20, 10, 0, i))
            files = sorted((root / "eolin").glob("*.json"))
            self.assertEqual(len(files), 10)
            infos = V.list_versions(save, root)
            self.assertEqual(infos[0]["niveau"], 12)
            self.assertEqual(infos[-1]["niveau"], 3)
            self.assertIn("20/11/2026 10:00", V.version_label(infos[0]))
            V.save_version(save, root, now=dt.datetime(2026, 11, 20, 10, 0, 11))   # même seconde
            self.assertEqual(len(list((root / "eolin").glob("*.json"))), 10)

    def test_window_save_and_restore(self):
        import qt_stub
        qt_stub.install()
        from ui import main_window as MW
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "versions"
            with mock.patch.object(V, "versions_root", return_value=root), \
                    mock.patch.object(MW, "save_settings", lambda _s: None):
                win = MW.MainWindow(DB)
                path = Path(d) / "perso.json"
                win.ch.nom = "Avant"
                win._write(path)
                win.ch.nom = "Après"
                win._write(path)
                self.assertEqual(len(V.list_versions(path)), 2)
                win.ch.nom = "Modifié"
                oldest = V.version_label(V.list_versions(path)[-1])
                with mock.patch.object(MW, "ask_choice", return_value=oldest):
                    self.assertTrue(win.action_restore_version())
                self.assertEqual(win.ch.nom, "Avant")
                self.assertEqual(len(V.list_versions(path)), 3)          # l'état « Modifié » est gardé
                self.assertIn("Après", path.read_text(encoding="utf-8"))  # le fichier n'est pas écrasé


if __name__ == "__main__":
    unittest.main()
