"""Tests v15 : affichage strict des transformations (badges PV/CA de la bête, icône animale, verrou de la magie,
restauration complète)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402


class FormUiTests(unittest.TestCase):
    def setUp(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        self.win = mw.MainWindow(DB)
        self.win.ch.classes = [{"nom": "Druide", "niveau": 6, "sous_classe": "Cercle de la Lune", "pv_jets": []}]
        self.win.ch.scores_manuel = {a: 10 for a in self.win.ch.scores_manuel}
        self.win.ch.methode = "manuel"
        self.win.changed()
        self.win.ch.pv_actuels = 30
        self.win.changed()

    def test_swap_and_restore(self):
        win, eng = self.win, self.win.engine
        druid_ca = eng.armor_class()[0]
        eng.assume_form("Ours brun")
        win.changed()
        self.assertEqual(win.badges["pv"].text(), "🐺 PV 34/34")
        self.assertEqual(win.badges["ca"].text(), "🐺 CA 11")
        self.assertIn("État actif : Forme Sauvage - Ours brun", win.badges["pv"].toolTip()
                      if hasattr(win.badges["pv"], "toolTip") and isinstance(win.badges["pv"].toolTip(), str) else
                      eng.form_status()["libelle"])
        self.assertEqual(win.combat_tab.hp_max.text(), "🐺 34")
        self.assertTrue(win.abilities_tab.rows["Force"]["total"].text().endswith("🐺"))
        self.assertFalse(win.abilities_tab.rows["Sagesse"]["total"].text().endswith("🐺"))
        self.assertIn("Magie indisponible sous cette forme", win.magic_tab.lock_label.text())
        win.combat_tab._on_hp_cur(20)                                     # le champ PV agit sur la bête
        self.assertEqual((win.ch.forme_pv, win.ch.pv_actuels), (20, 30))
        win._on_end_form()                                                # annulation : tout redevient comme avant
        self.assertEqual(win.badges["pv"].text(), "PV 30/{}".format(eng.hp_max()))
        self.assertEqual(win.badges["ca"].text(), "CA {}".format(druid_ca))
        self.assertFalse(win.abilities_tab.rows["Force"]["total"].text().endswith("🐺"))

    def test_polymorph_label(self):
        eng = self.win.engine
        self.win.ch.classes = [{"nom": "Magicien", "niveau": 9, "sous_classe": "", "pv_jets": []}]
        self.win.changed()
        eng.cast_polymorph("Loup")
        self.win.changed()
        self.assertEqual(eng.form_status()["libelle"], "État actif : Métamorphose - Loup")
        self.assertTrue(self.win.badges["pv"].text().startswith("🦋"))


if __name__ == "__main__":
    unittest.main()
