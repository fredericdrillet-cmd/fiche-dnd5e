"""Tests v47 : chemins compatibles PyInstaller (sys._MEIPASS), données embarquées, script de compilation."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

from core import paths  # noqa: E402


class ResourcePathTests(unittest.TestCase):
    def test_source_mode_uses_project_dir(self):
        self.assertFalse(hasattr(sys, "_MEIPASS"))
        self.assertEqual(Path(paths.get_resource_path("data")), ROOT / "data")

    def test_frozen_mode_uses_meipass(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        shutil.copytree(ROOT / "data", tmp / "data", ignore=shutil.ignore_patterns("images"))
        sys._MEIPASS = str(tmp)
        try:
            self.assertEqual(Path(paths.get_resource_path("data")), tmp / "data")
            self.assertTrue(paths.is_frozen())
            from core.data_loader import Database
            db = Database(paths.get_resource_path("data"))
            self.assertGreater(len(db.spells), 100)              # données lues depuis le dossier « extrait »
        finally:
            del sys._MEIPASS

    def test_working_copy_is_writable_and_outside_bundle(self):
        home = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, home, True)
        orig = paths.user_data_dir
        paths.user_data_dir = lambda: home
        try:
            copy = paths.working_copy("data/Langues.json")
        finally:
            paths.user_data_dir = orig
        self.assertTrue(copy.exists())
        self.assertTrue(str(copy).startswith(str(home)))
        self.assertTrue((ROOT / "data" / "Langues.json").exists())


class BuildScriptTests(unittest.TestCase):
    def test_check_file_mode(self):
        out = Path(tempfile.mkdtemp()) / "verif.txt"
        self.addCleanup(shutil.rmtree, out.parent, True)
        res = subprocess.run([sys.executable, str(ROOT / "main.py"), "--check", "--check-file", str(out)],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("sorts", out.read_text(encoding="utf-8"))

    def test_simulation_command(self):
        res = subprocess.run([sys.executable, str(ROOT / "build_executable.py"), "--simulation"],
                             capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res.returncode, 0)
        for flag in ("--onefile", "--windowed", "--add-data", "--icon", "Fiche_Personnage_DnD5E"):
            self.assertIn(flag, res.stdout)
        self.assertIn("data", res.stdout)
        self.assertIn("assets", res.stdout)

    def test_batch_file_is_windows_compatible(self):
        """Fins de ligne CRLF et texte ASCII : sinon cmd.exe découpe les lignes (« 'm' n'est pas reconnu… »)."""
        raw = (ROOT / "compiler_windows.bat").read_bytes()
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"))
        self.assertTrue(all(c < 128 for c in raw))
        self.assertIn(b"activate.bat", raw)                     # environnement Anaconda activé

    def test_icon_present(self):
        self.assertTrue((ROOT / "assets" / "app_icon.ico").exists())


if __name__ == "__main__":
    unittest.main()
