"""Tests v34 : flux « l'attaque touche-t-elle ? », armes ajoutées au sac, attaque d'opportunité sans réglage,
mannequin sans jeu d'armes, langues (Halfelin, cases visibles), encarts opaques de l'onglet Magie."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core import dice as D  # noqa: E402
from core.engine import Engine  # noqa: E402


def make():
    eng = Engine(DB, Engine.new_character(DB))
    eng.ch.classes = [{"nom": "Guerrier", "niveau": 3, "sous_classe": "Champion", "pv_jets": []}]
    eng.ch.armes_cac[0]["nom"] = "Épée longue"
    eng.normalize()
    return eng


def window(eng):
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    win = mw.MainWindow(DB)
    win.engine = eng
    win.refresh_all()
    return win


class FakeRoll:
    def __init__(self, natural, critical=""):
        self.natural, self.total, self.critical = natural, natural + 5, critical


class AttackFlowTests(unittest.TestCase):
    def run_flow(self, natural, critical, answer):
        import ui.combat_tab as ct
        win = window(make())
        asked, rolled = [], []
        saved = ct.roll_dice, ct.ask_yes_no, ct.roll_damage_dialog
        ct.roll_dice = lambda w, spec: FakeRoll(natural, critical)
        ct.ask_yes_no = lambda *a, **k: asked.append(a[1]) or answer
        ct.roll_damage_dialog = lambda w, spec: rolled.append(spec)
        try:
            slot = win.ch.armes_cac[0]
            win.combat_tab._attack_flow(win.engine.weapon_attack_spec(slot), win.engine.weapon_damage_spec(slot))
        finally:
            ct.roll_dice, ct.ask_yes_no, ct.roll_damage_dialog = saved
        return asked, rolled

    def test_hit_rolls_damage(self):
        asked, rolled = self.run_flow(14, "", True)
        self.assertEqual(asked, ["L'attaque touche-t-elle ?"])
        self.assertEqual(len(rolled), 1)
        self.assertTrue(rolled[0].formula.startswith("1d10"))          # v46 : épée longue à deux mains (main libre)

    def test_miss_closes(self):
        asked, rolled = self.run_flow(9, "", False)
        self.assertEqual(len(asked), 1)
        self.assertEqual(rolled, [])

    def test_critical_doubles_dice(self):
        _asked, rolled = self.run_flow(20, "succes", True)
        self.assertTrue(rolled[0].formula.startswith("2d10"))
        self.assertIn("critique", rolled[0].title)

    def test_natural_one_never_asks(self):
        asked, rolled = self.run_flow(1, "echec", True)
        self.assertEqual((asked, rolled), ([], []))

    def test_critical_formula(self):
        self.assertEqual(D.critical_formula("2d6+1d4+3"), "4d6+2d4+3")

    def test_turn_tile_returns_damage(self):
        eng = make()
        res = eng.use_turn_action("arme:armes_cac:0")
        self.assertIsNotNone(res["degats"])


class InventoryLinkTests(unittest.TestCase):
    def test_weapon_chosen_in_combat_goes_to_bag(self):
        eng = make()
        self.assertTrue(eng.ensure_in_inventory("Épée longue"))
        self.assertFalse(eng.ensure_in_inventory("Épée longue"))           # pas de doublon
        self.assertEqual(sum(1 for e in eng.ch.equipement if e["nom"] == "Épée longue"), 1)

    def test_combat_weapon_combo_adds_to_bag(self):
        win = window(make())
        tab = win.combat_tab
        w = tab.weapon_rows["armes_cac"][1]
        w["combo"].clear()
        w["combo"].addItems(["— aucune —", "Hache d'armes"])
        w["combo"].setCurrentIndex(1)
        w["magic"].addItems(["0"])
        tab._on_weapon("armes_cac", 1, True)
        self.assertIn("Hache d'armes", [e["nom"] for e in win.ch.equipement])


class ReactionTests(unittest.TestCase):
    @unittest.skip("v40 : réglages Demander / Automatique / Désactivée retirés à la demande (réactions = tuiles)")
    def test_opportunity_attack_has_no_mode(self):
        eng = make()
        self.assertFalse(eng.reaction_programmable("opportunite"))
        self.assertTrue(eng.reaction_programmable("sort:Bouclier"))


class UiCleanupTests(unittest.TestCase):
    def test_paperdoll_without_weapon_set_and_wrapping(self):
        win = window(make())
        panel = win.inventory_tab.paperdoll
        panel.refresh()
        card = panel.slot_btns["main_principale"]
        self.assertIn("Épée longue", card.text())
        src = (ROOT / "ui" / "paperdoll.py").read_text(encoding="utf-8")
        self.assertIn("setWordWrap(True)", src)
        self.assertNotIn("set_btn", src)                                  # « Jeu d'armes actif » retiré

    def test_languages(self):
        self.assertIn("Halfelin", DB.language_names())
        self.assertNotIn("Halphen", DB.language_names())
        eng = make()
        eng.ch.langues_liste = ["Commun", "Halphen"]
        eng.normalize()
        self.assertIn("Halfelin", eng.ch.langues_liste)
        win = window(make())
        win.race_tab.refresh()
        self.assertNotIn(".json", win.race_tab.lang_box.title())

    def test_no_json_in_titles(self):
        for path in ("progression_tab.py", "race_tab.py", "magic_tab.py"):
            src = (ROOT / "ui" / path).read_text(encoding="utf-8")
            for bad in ("(Dons.json)", "(Langues.json)", "(Magie-N.json)"):
                self.assertNotIn(bad, src)

    def test_granted_box_opaque(self):
        win = window(make())
        tab = win.magic_tab
        tab.refresh()
        self.assertIn("opaqueBox", tab.granted_box.styleSheet())

    def test_rp_notes_larger_than_story(self):
        src = (ROOT / "ui" / "rp_tab.py").read_text(encoding="utf-8")
        self.assertIn("right.addWidget(story, 2)", src)
        self.assertIn("right.addWidget(notes, 3)", src)

    def test_attunement_checkbox_styled(self):
        src = (ROOT / "ui" / "magic_items_panel.py").read_text(encoding="utf-8")
        self.assertIn('w["lien"].setStyleSheet(indicator_qss', src)


if __name__ == "__main__":
    unittest.main()
