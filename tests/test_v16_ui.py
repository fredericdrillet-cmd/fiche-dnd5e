"""Tests v16 : tableau de bord Magie (liste hiérarchisée par niveau, statuts), formes sauvages sans mention
« valeurs estimées », note de sous-classe, cartes de caractéristiques."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402


class V16Tests(unittest.TestCase):
    def setUp(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        self.win = mw.MainWindow(DB)

    def _cleric(self):
        win = self.win
        win.ch.classes = [{"nom": "Clerc", "niveau": 3, "sous_classe": "Domaine de la Vie", "pv_jets": []}]
        win.ch.sorts["Clerc"] = [{"nom": "Bénédiction", "prepare": True}, {"nom": "Soins", "prepare": False},
                                 {"nom": "Flamme sacrée", "prepare": True}]
        win.changed()
        win.magic_tab.select_class("Clerc")
        return win.magic_tab

    def test_grouped_by_level_with_separators(self):
        tab = self._cleric()
        rows = tab._chosen_rows
        seps = [r for r in rows if r.get("separator")]
        self.assertTrue(seps)
        self.assertTrue(rows[0].get("separator"))
        levels = [r["niveau"] for r in seps]
        self.assertEqual(levels, sorted(set(levels)))
        # chaque sort est précédé de la ligne-titre de son niveau
        current = None
        for r in rows:
            if r.get("separator"):
                current = r["niveau"]
            else:
                self.assertEqual(r["niveau"], current)

    def test_separator_not_selectable(self):
        tab = self._cleric()
        tab.chosen.setCurrentRow(0)
        self.assertIsNone(tab._selected_spell(tab.chosen, tab._chosen_rows))
        idx = next(i for i, r in enumerate(tab._chosen_rows) if not r.get("separator"))
        tab.chosen.setCurrentRow(idx)
        self.assertIsNotNone(tab._selected_spell(tab.chosen, tab._chosen_rows))
        tab._on_chosen_click(0, 2)            # clic sur un titre : aucune erreur, rien ne change

    def test_cantrip_counter(self):
        tab = self._cleric()
        self.assertTrue(tab.cantrip_count.text().startswith("Sorts mineurs :"))
        self.assertIn("à volonté", tab.cantrip_count.text())

    def test_spell_status(self):
        from ui.magic_tab import spell_status
        row = {"nom": "Bénédiction", "sort": {"concentration": True}, "niveau": 1, "prepare": True, "domaine": False}
        st = spell_status(row, "", False)
        self.assertIn("Ⓒ Concentration", st["texte"])
        self.assertIn("✔ Préparé", st["texte"])
        self.assertFalse(st["actif"])
        st = spell_status(row, "Bénédiction", False)
        self.assertIn("🧠 Concentration active", st["texte"])
        self.assertTrue(st["actif"])
        st = spell_status(row, "", True)
        self.assertIn("🔒 Indisponible", st["texte"])
        self.assertNotIn("Préparé", st["texte"])
        row["prepare"] = False
        self.assertIn("Non préparé", spell_status(row, "", False)["texte"])

    def test_no_estimated_mention(self):
        eng = self.win.engine
        self.win.ch.classes = [{"nom": "Druide", "niveau": 8, "sous_classe": "Cercle de la Lune", "pv_jets": []}]
        self.win.changed()
        checked = 0
        for name in list(DB.beasts)[:80]:
            self.win.ch.forme_active = name
            for a in eng.beast_attacks():
                self.assertNotIn("estim", eng.beast_attack_spec(a).note)
                checked += 1
        self.win.ch.forme_active = ""
        self.assertGreater(checked, 0)
        src = (ROOT / "ui" / "combat_tab.py").read_text(encoding="utf-8")
        self.assertNotIn("statblock incomplet", src)
        self.assertNotIn("valeurs estimées", (ROOT / "core" / "engine_extras.py").read_text(encoding="utf-8"))

    def test_subclass_note(self):
        win = self.win
        win.ch.classes = [{"nom": "Guerrier", "niveau": 1, "sous_classe": "", "pv_jets": []}]
        win.changed()
        panel = win.classes_tab.panels[0] if hasattr(win.classes_tab, "panels") else None
        if panel is not None:
            self.assertIn("choix au niveau", panel.sub_note.text())
            win.ch.classes[0]["niveau"] = 3
            win.changed()
            self.assertEqual(panel.sub_note.text(), "○ à choisir")       # v28 : sous-classe à choisir signalée
            win.ch.classes[0]["sous_classe"] = "Champion"
            win.changed()
            self.assertEqual(panel.sub_note.text(), "")

    def test_ability_cards(self):
        tab = self.win.abilities_tab
        for ab, w in tab.rows.items():
            self.assertIn("card", w)
            self.assertIn("d20", w)
        self.win.ch.methode = "achat"
        self.win.changed()
        self.assertTrue(tab.rows["Force"]["cost"].text().startswith("Coût :"))
        self.win.ch.methode = "manuel"
        self.win.changed()
        self.assertEqual(tab.rows["Force"]["cost"].text(), "")


if __name__ == "__main__":
    unittest.main()
