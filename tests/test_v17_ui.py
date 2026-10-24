"""Tests v17 : Magie compacte (pas de boutons de repos), encarts de combat adaptatifs, filtres rapides et quota de la
bibliothèque, catalogue des dons sans colonne Source."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402


class V17Tests(unittest.TestCase):
    def setUp(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        self.win = mw.MainWindow(DB)
        win = self.win
        win.ch.classes = [{"nom": "Magicien", "niveau": 3, "sous_classe": "", "pv_jets": []}]
        win.changed()
        win.magic_tab.select_class("Magicien")

    def test_no_rest_buttons_in_magic(self):
        self.assertNotIn("short_btn", vars(self.win.magic_tab))
        self.assertNotIn("long_btn", vars(self.win.magic_tab))
        self.assertIn("short_btn", vars(self.win.combat_tab))        # toujours disponibles ailleurs
        self.assertEqual(self.win.magic_tab.slot_rows[0]["orbs"].orb, 22)      # v22 : sphères agrandies

    def test_library_filters(self):
        tab = self.win.magic_tab
        tab._on_level_chip(1)                                             # sorts mineurs
        self.assertTrue(tab._lib_rows)
        self.assertTrue(all(r["sort"]["niveau"] == 0 for r in tab._lib_rows))
        tab._on_level_chip(0)
        total = len(tab._lib_rows)
        school = tab._lib_rows[0]["sort"]["ecole"]
        tab.school_filter.setCurrentIndex(tab.school_filter.findText(school))
        tab._fill_library()
        self.assertTrue(all(r["sort"]["ecole"] == school for r in tab._lib_rows))
        self.assertLessEqual(len(tab._lib_rows), total)
        tab.school_filter.setCurrentIndex(0)
        name = tab._lib_rows[0]["nom"]
        # recherche sans accents ni majuscules
        import unicodedata
        plain = "".join(ch for ch in unicodedata.normalize("NFD", name) if unicodedata.category(ch) != "Mn").upper()
        tab.search.setText(plain)
        tab._fill_library()
        self.assertIn(name, [r["nom"] for r in tab._lib_rows])
        tab.search.setText("")

    def test_hide_owned(self):
        tab, win = self.win.magic_tab, self.win
        tab._on_level_chip(0)
        name = tab._lib_rows[0]["nom"]
        win.ch.sorts["Magicien"] = [{"nom": name, "prepare": True}]
        win.changed()
        tab.unknown_only.setChecked(True)
        tab._fill_library()
        self.assertNotIn(name, [r["nom"] for r in tab._lib_rows])
        tab.unknown_only.setChecked(False)

    def test_quota(self):
        from ui.magic_tab import spell_quota
        text, over = spell_quota({"mineurs": 1, "sorts": 2, "prepares": 2},
                                 {"mineurs_max": 3, "connus_max": 4, "prepares_max": None})
        self.assertIn("Sorts mineurs : 1 / 3 (reste 2)", text)
        self.assertIn("Sorts connus : 2 / 4 (reste 2)", text)
        self.assertFalse(over)
        text, over = spell_quota({"mineurs": 4, "sorts": 6, "prepares": 6},
                                 {"mineurs_max": 3, "connus_max": None, "prepares_max": 5})
        self.assertTrue(over)
        self.assertIn("Sorts préparés : 6 / 5", text)
        self.assertIn("Sorts", self.win.magic_tab.lib_quota.text())

    def test_combat_boxes_adapt(self):
        ct, win = self.win.combat_tab, self.win
        for sl in win.ch.armes_cac:
            sl["nom"] = ""
        win.changed()
        row0 = ct.weapon_rows["armes_cac"][0]
        self.assertEqual(len(ct._box_heads["armes_cac"]), len(row0["_order"]))   # un en-tête par colonne
        self.assertIn("cantrips", ct._box_heads)
        weapon = next(n for n, w in DB.weapons.items() if w["type"] == "cac")
        win.ch.armes_cac[0]["nom"] = weapon
        win.changed()
        self.assertIn("combo", row0["_order"])

    def test_feats_no_source_column(self):
        src = (ROOT / "ui" / "progression_tab.py").read_text(encoding="utf-8")
        self.assertIn('["Don", "Prérequis", "Augmentation", "État"]', src)


if __name__ == "__main__":
    unittest.main()
