"""Tests v33 : ajout rapide d'objets magiques (autocomplétion), objets sur mesure, badge d'harmonisation,
déplacement des traits RP hors de l'onglet Inventaire."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core.character import Character  # noqa: E402
from core.engine import Engine  # noqa: E402
from ui.magic_items_panel import quick_matches  # noqa: E402


def make():
    eng = Engine(DB, Engine.new_character(DB))
    eng.ch.classes = [{"nom": "Guerrier", "niveau": 3, "sous_classe": "Champion", "pv_jets": []}]
    eng.normalize()
    return eng


def window(eng=None):
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    win = mw.MainWindow(DB)
    if eng is not None:
        win.engine = eng
        win.refresh_all()
    return win


class QuickMatchTests(unittest.TestCase):
    def test_prefix_first_and_accent_insensitive(self):
        hits = quick_matches(DB.magic_items, "anneau de")
        self.assertTrue(hits)
        self.assertTrue(all(h.lower().startswith("anneau de") for h in hits[:5]))
        self.assertTrue(quick_matches(DB.magic_items, "epee"))              # « Épée… » sans accent
        self.assertTrue(quick_matches(DB.magic_items, "elfiques bottes"))   # mots dans le désordre
        self.assertEqual(quick_matches(DB.magic_items, ""), [])


class CustomItemTests(unittest.TestCase):
    def test_custom_item_full_record(self):
        eng = make()
        before = eng.carried_weight()
        name = eng.add_custom_magic_item("Broche du corbeau", "Objet merveilleux", "rare", True,
                                         "Vol de 3 m une fois par jour.", 0.5, 1)
        self.assertEqual(name, "Broche du corbeau")
        item = eng.magic_item(name)
        self.assertEqual((item["rarete"], item["lien"], item["ca"], item["source"]), ("rare", True, 1, "Objet sur mesure"))
        self.assertEqual(eng.ch.objets_magiques[-1]["nom"], name)
        self.assertAlmostEqual(eng.carried_weight() - before, 0.5)
        self.assertTrue(eng.set_attuned(len(eng.ch.objets_magiques) - 1, True))
        eng.normalize()
        self.assertEqual(eng.paperdoll()["amulette"]["nom"], name)           # « Broche » : case amulette

    def test_official_name_is_suffixed_and_empty_refused(self):
        eng = make()
        official = next(iter(DB.magic_items))
        self.assertEqual(eng.add_custom_magic_item(official), official + " (sur mesure)")
        self.assertEqual(eng.add_custom_magic_item("   "), "")

    def test_custom_item_saved_with_character(self):
        eng = make()
        eng.add_custom_magic_item("Anneau du héron", "Anneau", "peu commun", True)
        ch = Character.from_dict(json.loads(json.dumps(eng.ch.to_dict())))
        e2 = Engine(DB, ch)
        e2.normalize()
        self.assertEqual(e2.magic_item("Anneau du héron")["type"], "Anneau")
        self.assertIn("Anneau du héron", e2.all_magic_item_names())

    def test_attunement_limit(self):
        eng = make()
        names = [n for n, i in DB.magic_items.items() if i["lien"]][:4]
        for n in names:
            eng.add_magic_item(n)
        results = [eng.set_attuned(i, True) for i in range(4)]
        self.assertEqual(results, [True, True, True, False])


class UiTests(unittest.TestCase):
    def test_quick_add_official(self):
        win = window(make())
        panel = win.inventory_tab.magic_items
        name = quick_matches(DB.magic_items, "anneau de")[0]
        panel.quick.setText(name)
        panel._update_quick()
        self.assertIn("harmonisation", panel.quick_info.text())
        panel._on_quick_add()
        self.assertEqual(win.ch.objets_magiques[-1]["nom"], name)

    def test_quick_add_unknown_opens_custom_form(self):
        import ui.magic_items_panel as mp
        win = window(make())
        panel = win.inventory_tab.magic_items
        panel.quick.setText("Talisman de Zorg")
        orig = mp.ask_custom_item
        mp.ask_custom_item = lambda parent, name="": {"nom": name, "type_": "Objet merveilleux", "rarete": "peu commun",
                                                       "lien": False, "description": "", "poids": 0.0, "ca": 0}
        try:
            panel._on_quick_add()
        finally:
            mp.ask_custom_item = orig
        self.assertEqual(win.ch.objets_magiques[-1]["nom"], "Talisman de Zorg")

    def test_badge_label(self):
        eng = make()
        eng.add_magic_item(next(n for n, i in DB.magic_items.items() if i["lien"]))
        win = window(eng)
        panel = win.inventory_tab.magic_items
        panel.refresh()
        src = (ROOT / "ui" / "magic_items_panel.py").read_text(encoding="utf-8")
        self.assertIn("◇ Non harmonisé", src)

    def test_traits_moved_to_rp_tab(self):
        win = window(make())
        self.assertNotIn("traits", win.inventory_tab.texts)
        win.ch.traits = "Loyal envers ses amis."
        win.rp_tab.refresh()
        self.assertEqual(win.rp_tab.traits.toPlainText(), "Loyal envers ses amis.")

    def test_sources_in_french(self):
        from ui.magic_items_panel import SOURCE_FR
        self.assertEqual(SOURCE_FR["Dungeon Master's Guide"], "Guide du maître")


if __name__ == "__main__":
    unittest.main()
