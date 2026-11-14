"""Tests v49 : fiche pédagogique des classes / sous-classes, recommandations de caractéristiques (badges et
infobulles), portrait et histoire dans l'assistant, inspecteur de sorts et apprentissage par bouton."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from test_v40_wizard_saves import full_spells, make  # noqa: E402
from test_v41_grimoire_combat import window  # noqa: E402
from core.class_guide import CLASS_GUIDE  # noqa: E402


class GuideTests(unittest.TestCase):
    def test_every_class_documented(self):
        eng = make("Guerrier", 1)
        for cls in DB.class_names():
            self.assertIn(cls, CLASS_GUIDE)
            g = eng.class_guide(cls)
            self.assertTrue(g["concept"] and g["mecaniques"])
            self.assertTrue(any(r == "principale" for r, _ in g["carac"].values()))
        self.assertEqual(eng.class_guide("Clerc")["niveau_sous_classe"], 1)
        self.assertEqual(eng.class_guide("Magicien")["niveau_sous_classe"], 2)
        self.assertEqual(eng.class_guide("Roublard")["niveau_sous_classe"], 3)

    def test_subclass_summary(self):
        eng = make("Roublard", 1)
        s = eng.subclass_summary("Roublard", "Arnaqueur arcanique")
        self.assertEqual(s["niveau"], 3)
        self.assertIn("🔮 Magie", s["orientation"])
        self.assertTrue(s["pouvoirs"] and s["pouvoirs"][0][0] == 3)

    def test_recommendations_follow_subclass(self):
        eng = make("Roublard", 1)
        base = eng.ability_recommendations()
        self.assertEqual(base["Dextérité"][0], "principale")
        self.assertNotIn("Intelligence", base)
        at = eng.ability_recommendations("Roublard", "Arnaqueur arcanique")
        self.assertEqual(at["Intelligence"][0], "secondaire")
        self.assertIn("Degré de Difficulté (DD)", at["Intelligence"][1])
        ek = eng.ability_recommendations("Guerrier", "Chevalier occulte")
        self.assertEqual((ek["Force"][0], ek["Dextérité"][0], ek["Intelligence"][0]),
                         ("principale", "principale", "secondaire"))

    def test_guide_panel_html(self):
        from ui.class_guide_panel import ClassGuidePanel, class_guide_html, subclass_html
        eng = make("Roublard", 1)
        text = class_guide_html(eng, "Roublard")
        for part in ("Concept", "Mécaniques clés", "Attaque sournoise", "⭐ [Principale]", "Sous-classe au niveau 3"):
            self.assertIn(part, text)
        self.assertIn("débloquée au niveau 3", subclass_html(eng, "Roublard", "Assassin"))
        panel = ClassGuidePanel()
        panel.set_class(eng, "Roublard")
        self.assertIn("Arnaqueur", panel.show_subclass("Arnaqueur arcanique"))
        self.assertEqual(panel.sub, "Arnaqueur arcanique")

    def test_ability_badges(self):
        win = window(make("Roublard", 3, "Arnaqueur arcanique"))
        win.settings["mode_libre"] = True
        tab = win.abilities_tab
        tab.refresh()
        self.assertEqual(tab.rows["Dextérité"]["badge"].text(), "⭐ [Principale]")
        self.assertEqual(tab.rows["Intelligence"]["badge"].text(), "✦ [Secondaire]")
        self.assertEqual(tab.rows["Charisme"]["badge"].text(), "")


class CreationWizardTests(unittest.TestCase):
    def wizard(self):
        from ui.creation_wizard import CreationWizard
        return CreationWizard(window(make("Guerrier", 1)))

    def test_target_subclass_changes_badges(self):
        w = self.wizard()
        w._on_class("Roublard")
        w.go(1)
        w.set_target_subclass("Arnaqueur arcanique")
        self.assertEqual(w.engine.ability_recommendations()["Intelligence"][0], "secondaire")
        w.go(3)
        self.assertEqual(w.abilities_panel.rows["Intelligence"]["badge"].text(), "✦ [Secondaire]")
        w._on_class("Clerc")
        w.set_target_subclass("Domaine de la Vie")
        self.assertEqual(w.ch.classes[0]["sous_classe"], "Domaine de la Vie")   # niveau 1 : vrai choix

    def test_spell_inspector_and_button(self):
        w = self.wizard()
        w._on_class("Magicien")
        w.go(4)
        name = next(s["nom"] for s in w.engine.level_spell_options(w.engine, "Magicien") if s["niveau"] == 0)
        text = w.inspect(name)
        for part in ("École", "Temps d'incantation", "Portée", "Composantes", "Durée", "Concentration", "Rituel"):
            self.assertIn(part, text)
        avail, _mine = w.spell_widgets["mineurs"]

        class Item:
            def data(self, _role):
                return name
        avail.currentItem = lambda: Item()
        self.assertTrue(w._learn_current("Magicien", avail))
        self.assertIn(name, [s["nom"] for s in w.ch.sorts["Magicien"]])

    def test_portrait_and_backstory(self):
        import ui.rp_tab as rp
        w = self.wizard()
        orig = rp.image_to_b64
        rp.image_to_b64 = lambda path, max_side=640: "QUJD"
        try:
            self.assertTrue(w.import_portrait("portrait.png"))
        finally:
            rp.image_to_b64 = orig
        self.assertEqual(w.ch.portrait, "QUJD")
        w._set_identity("histoire", "Née dans les marais de Cormyr.")
        w.finalize()
        from ui.creation_wizard import apply_creation
        apply_creation(w.win, w)
        self.assertEqual(w.win.engine.ch.portrait, "QUJD")
        self.assertEqual(w.win.engine.ch.histoire, "Née dans les marais de Cormyr.")
        w.win.rp_tab.refresh()                            # repris dans l'onglet Histoire, Portrait (éditable)
        self.assertIn("Cormyr", w.win.rp_tab.story.toPlainText())


class LevelUpTests(unittest.TestCase):
    def test_guide_and_inspector_in_levelup(self):
        from ui.levelup_dialog import LevelUpDialog
        eng = make("Ensorceleur", 3, "Lignée draconique")
        full_spells(eng, "Ensorceleur")
        dlg = LevelUpDialog(window(eng))
        self.assertEqual(dlg.guide.cls, "Ensorceleur")
        w = dlg.spell_widgets["Ensorceleur"]
        name = next(s["nom"] for s in dlg.engine.level_spell_options(dlg.sim, "Ensorceleur") if s["niveau"] > 0)
        self.assertIn("Portée", dlg.inspect_spell("Ensorceleur", name, "avail1"))
        dlg._learn_selected("Ensorceleur")
        self.assertIn(name, [s["nom"] for s in dlg.sim.ch.sorts["Ensorceleur"]])
        self.assertIn("Apprendre le sort", w["learn_btn"].text())


if __name__ == "__main__":
    unittest.main()
