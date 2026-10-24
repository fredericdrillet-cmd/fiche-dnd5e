"""Test de fumée de l'interface avec un faux PyQt6 (voir qt_stub.py)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import qt_stub  # noqa: E402

qt_stub.install()

from core.data_loader import Database  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402


class UiSmoke(unittest.TestCase):
    def test_full_cycle(self):
        db = Database(ROOT / "data")
        win = MainWindow(db)
        eng = win.engine
        # ajout de classes, niveaux, sous-classes
        eng.add_class("Magicien"); eng.add_class("Occultiste")
        win.changed()
        panel = win.classes_tab.panels[0]
        panel._on_level(5)
        win._on_level(9)
        eng.ch.classes[1]["sous_classe"] = "École d'Évocation"
        eng.ch.classes[1]["niveau"] = 3
        win.changed()
        # ajout de sorts
        win.magic_tab.select_class("Magicien")
        win.magic_tab._lib_rows = [{"nom": "Projectile magique", "sort": db.spells["Projectile magique"]}]
        win.magic_tab.library.setCurrentRow(0) if False else None
        win.magic_tab.library._st["row"] = 0
        win.magic_tab._on_add()
        self.assertTrue(any(s["nom"] == "Projectile magique" for s in eng.ch.sorts["Magicien"]))
        # onglets spécifiques
        win.abilities_tab._on_roll()
        win.abilities_tab._on_buy("Force", 15)
        win.race_tab._on_race()
        win.combat_tab._on_armor()
        win.skills_tab.refresh(); win.combat_tab.refresh(); win.progress_tab.refresh(); win.inventory_tab.refresh()
        win.action_about if False else None
        # sauvegarde / chargement
        import tempfile, os
        path = os.path.join(tempfile.mkdtemp(), "p.json")
        eng.ch.save(path)
        from core.character import Character
        again = Character.load(path)
        self.assertEqual(again.niveau_total, eng.ch.niveau_total)


if __name__ == "__main__":
    unittest.main()
