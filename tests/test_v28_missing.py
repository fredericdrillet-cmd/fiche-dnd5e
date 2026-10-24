"""Tests v28 : choix manquants (moteur, pastilles d'onglet, voyants, titres d'encarts, rappels)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core.engine import Engine  # noqa: E402


def make(race, c, lvl, sub="", bg="Acolyte"):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race(race)
    eng.ch.historique = bg
    eng.apply_background()
    eng.ch.classes = [{"nom": c, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng.normalize()
    return eng


def msgs(eng, tab=None):
    return [m["message"] for m in eng.missing_choices() if tab is None or m["onglet"] == tab]


def window():
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    return mw.MainWindow(DB)


def complete_fighter():
    eng = make("Humain", "Guerrier", 1)
    for sk in eng.class_skill_status()["options"][:2]:
        eng.ch.competences.setdefault(sk, {})["maitrise"] = True
    eng.ch.styles_combat["Guerrier|1"] = "Défense"
    langs = [n for n in DB.language_names() if n not in eng.ch.langues_liste]
    eng.ch.langues_liste += langs[:eng.languages_missing()]
    eng.normalize()
    return eng


class EngineTests(unittest.TestCase):
    def test_complete_character_has_nothing_missing(self):
        eng = complete_fighter()
        self.assertEqual(eng.missing_choices(), [])

    def test_skills(self):
        eng = make("Humain", "Guerrier", 1)
        self.assertIn("2 compétences à choisir (classe)", msgs(eng))
        eng = make("Demi-elfe", "Guerrier", 1)                 # Polyvalence : +2 compétences au choix
        self.assertEqual(eng.skills_missing(), 4)

    def test_expertise(self):
        eng = make("Humain", "Roublard", 1)
        self.assertEqual(eng.expertise_allowed(), 2)
        self.assertIn("2 expertises à attribuer", msgs(eng))
        self.assertEqual(make("Humain", "Roublard", 6).expertise_allowed(), 4)

    def test_subclass(self):
        self.assertTrue(any("sous-classe" in m for m in msgs(make("Humain", "Guerrier", 3), "classes")))
        self.assertEqual(msgs(make("Humain", "Guerrier", 3, "Champion"), "classes"), [])
        self.assertEqual(msgs(make("Humain", "Guerrier", 2), "classes"), [])

    def test_languages(self):
        eng = make("Humain", "Guerrier", 1)                     # 1 au choix (race) + 2 au choix (Acolyte)
        self.assertEqual(eng.language_picks(), 3)
        self.assertEqual(eng.languages_missing(), 3)

    def test_asi_slot(self):
        eng = make("Humain", "Guerrier", 4, "Champion")
        self.assertTrue(any("amélioration ou don" in m for m in msgs(eng, "progression")))
        sid = eng.asi_slots()[0]["id"]
        eng.ch.ameliorations[sid] = {"mode": "plus2", "a1": "Force"}
        eng.normalize()
        self.assertEqual(msgs(eng, "progression"), [])

    def test_spells(self):
        eng = make("Elfe", "Magicien", 3, "École d'évocation")
        found = msgs(eng, "magie")
        self.assertTrue(any("sorts mineurs à choisir" in m for m in found))
        self.assertTrue(any("grimoire" in m for m in found))
        eng = make("Humain", "Occultiste", 3)
        found = msgs(eng, "magie")
        self.assertTrue(any("faveur de pacte" in m for m in found))
        self.assertTrue(any("manifestations occultes" in m for m in found))

    def test_draconic_color(self):
        eng = make("Drakéide", "Guerrier", 1)
        self.assertIn("Couleur du dragon ancestral à choisir", msgs(eng, "combat"))

    def test_excess_stays_in_warnings(self):
        eng = make("Humain", "Guerrier", 1)
        self.assertFalse(any("à choisir" in w for w in eng.warnings()))


class UiTests(unittest.TestCase):
    def test_tab_badges_and_lights(self):
        win = window()
        win.engine = Engine(DB, make("Humain", "Guerrier", 1).ch)
        win.refresh_all()
        self.assertGreater(win.tab_badges.get("caracteristiques", 0), 0)
        self.assertIn("choix à faire", win.missing_btn.text())
        win.engine = Engine(DB, complete_fighter().ch)
        win.refresh_all()
        self.assertEqual(win.tab_badges, {})
        self.assertIn("✔", win.warn_label.text())

    def test_box_titles(self):
        win = window()
        win.engine = Engine(DB, make("Humain", "Guerrier", 1).ch)
        win.refresh_all()
        win.stats_tab.skills.refresh()
        self.assertIn("2 à choisir", win.stats_tab.skills.skills_box.title())

    def test_checklist_navigates(self):
        import ui.main_window as mw
        win = window()
        win.engine = Engine(DB, make("Humain", "Guerrier", 1).ch)
        win.refresh_all()
        target = next(k for k in (m["onglet"] for m in win.engine.missing_choices()) if k == "combat")
        orig = mw.ask_choice
        mw.ask_choice = lambda w, t, m, options: next(o for o in options if "Style de combat" in o)
        went = []
        win.go_to_tab = lambda key: went.append(key)
        try:
            win.show_checklist()
        finally:
            mw.ask_choice = orig
        self.assertEqual(went, [target])

    def test_save_note(self):
        win = window()
        win.engine = Engine(DB, make("Humain", "Guerrier", 1).ch)
        self.assertIn("choix restent à faire", win.missing_note())
        win.engine = Engine(DB, complete_fighter().ch)
        self.assertEqual(win.missing_note(), "")

    def test_preparation_offered_after_long_rest(self):
        import ui.dialogs as dlg
        import ui.rest_dialog as rd
        win = window()
        win.engine = Engine(DB, make("Humain", "Clerc", 3, "Domaine de la Vie").ch)
        orig = dlg.ask_yes_no
        dlg.ask_yes_no = lambda *a, **k: True
        went = []
        win.go_to_tab = lambda key: went.append(key)
        try:
            self.assertTrue(rd.offer_preparation(win))
        finally:
            dlg.ask_yes_no = orig
        self.assertEqual(went, ["magie"])
        win.engine = Engine(DB, make("Humain", "Guerrier", 3).ch)
        self.assertFalse(rd.offer_preparation(win))


if __name__ == "__main__":
    unittest.main()
