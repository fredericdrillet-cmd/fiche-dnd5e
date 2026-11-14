"""Tests v50 : fenêtres maximisables, modale « Création de personnage incomplète », cases à cocher visibles,
multiclassage sans interrupteur (prérequis appliqués), en-têtes statiques en Mode guidé / sélecteurs en Mode libre."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v40_wizard_saves import make  # noqa: E402
from test_v41_grimoire_combat import window  # noqa: E402


def src(name: str) -> str:
    return (ROOT / "ui" / name).read_text(encoding="utf-8")


class WindowTests(unittest.TestCase):
    def test_wizards_are_maximizable(self):
        for name in ("creation_wizard.py", "levelup_dialog.py"):
            text = src(name)
            self.assertIn("WindowMinMaxButtonsHint", text)
            self.assertNotIn("FramelessWindowHint", text)
        self.assertIn("setMinimumSize(1024, 640)", src("main_window.py"))

    def test_fullscreen_toggle(self):
        from ui.creation_wizard import CreationWizard
        w = CreationWizard(window(make("Guerrier", 1)))
        calls = []
        w.isMaximized = lambda: False
        w.showMaximized = lambda: calls.append("max")
        w.toggle_maximized()
        self.assertEqual(calls, ["max"])
        self.assertEqual(w.full_btn.text(), "🗗 Taille normale")


class IncompleteTests(unittest.TestCase):
    def test_confirmation_modal(self):
        import ui.dialogs as dlg
        from ui.creation_wizard import CreationWizard
        w = CreationWizard(window(make("Guerrier", 1)))
        self.assertTrue(w.incomplete_items())               # compétences, style, langues, nom…
        asked = []
        orig = dlg.ask_yes_no

        def fake(parent, title, message, yes="Oui", no="Non", default_no=True):
            asked.append((title, message, yes, no))
            return False                                   # « Poursuivre la création »
        dlg.ask_yes_no = fake
        try:
            accepted = []
            w.accept = lambda: accepted.append(True)
            w.go(6)
            w._on_create()
            self.assertEqual(accepted, [])
            title, message, yes, no = asked[0]
            self.assertEqual(title, "Création de personnage incomplète")
            self.assertIn("Souhaitez-vous tout de même générer ce personnage en l'état ?", message)
            self.assertEqual((yes, no), ("Valider malgré tout", "Poursuivre la création"))
            self.assertEqual(w.step, w.first_incomplete_step())
            self.assertLess(w.step, 6)                     # retour à la première étape incomplète
            dlg.ask_yes_no = lambda *a, **k: True            # « Valider malgré tout »
            w._on_create()
            self.assertEqual(accepted, [True])
        finally:
            dlg.ask_yes_no = orig


class CheckboxTests(unittest.TestCase):
    def test_bag_and_options_checkboxes(self):
        inv = src("inventory_tab.py")
        self.assertIn("self.bag.setStyleSheet(indicator_qss(t))", inv)
        self.assertIn("page_scroll.setWidget(page)", inv)
        opt = src("options_dialog.py")
        self.assertIn("for box in (self.survival, self.free_mode)", opt)
        self.assertIn("scroll.setWidget(inner)", opt)


class MulticlassTests(unittest.TestCase):
    def test_always_offered_with_prereqs(self):
        eng = make("Guerrier", 3, "Champion")
        eng.ch.multiclassage = False
        opts = eng.level_up_options()
        self.assertGreater(len(opts), 1)
        self.assertTrue(any(o["prerequis"] for o in opts[1:]))     # Force / Dex… à 10 : prérequis non remplis

    def test_guided_mode_hides_unmet_prereq(self):
        """v51 : la classe aux prérequis non remplis n'est plus proposée (elle bloquait « Confirmer » sans choix
        visible) ; elle est listée « 🔒 » avec la raison. En Mode libre, elle reste proposée avec un avertissement."""
        from ui.levelup_dialog import LevelUpDialog
        win = window(make("Guerrier", 3, "Champion"))
        win.settings["mode_libre"] = False
        dlg = LevelUpDialog(win)
        self.assertTrue(dlg.locked_options)
        self.assertFalse(any(o["prerequis"] for o in dlg.options))
        self.assertIn("🔒 Multiclassage indisponible", dlg.locked_label.text())
        win.settings["mode_libre"] = True
        dlg = LevelUpDialog(win)
        self.assertTrue(any(o["prerequis"] for o in dlg.options))
        self.assertEqual(dlg.locked_options, [])

    def test_toggle_hidden(self):
        self.assertIn("self.multi_chk.setVisible(False)", src("classes_tab.py"))


class HeaderModeTests(unittest.TestCase):
    def test_static_vs_dropdowns(self):
        win = window(make("Guerrier", 3, "Champion"))
        win.settings["mode_libre"] = False
        win.refresh_all()
        self.assertIn("Guerrier", win.class_badge.text())
        self.assertIn("Champion", win.class_badge.text())
        win.classes_tab.refresh()
        panel = win.classes_tab.panels[0]
        self.assertIn("Lecture seule", panel.static_head.text())
        self.assertIn("Niveau 3", panel.static_head.text())


if __name__ == "__main__":
    unittest.main()
