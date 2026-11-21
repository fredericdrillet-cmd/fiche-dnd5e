"""v52 : retours d'essai de l'onglet En partie — épuisement, couleurs du thème, options de classe, Sommeil, dés."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402
from ui import theme  # noqa: E402

DB = Database(ROOT / "data")


def sheet(cls="Magicien", lvl=3, sub="", edition="2014"):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    return eng


class TilePaletteTests(unittest.TestCase):
    def test_every_theme_readable_and_distinct(self):
        for t in theme.THEMES.values():
            p = theme.tile_palette(t)
            self.assertEqual(set(p), {"attaque", "capacite", "magie", "objet", "reaction", "commune"})
            self.assertEqual(len(set(p.values())), 6, t.key)
            for cat, col in p.items():
                self.assertGreaterEqual(theme.contrast_ratio(col, t.panel), 3, (t.key, cat))


class HpPoolTests(unittest.TestCase):
    def test_sleep_2014_scales_with_slot(self):
        eng = sheet()
        self.assertEqual([eng.spell_resolution("Sommeil", n)["reserve"].formula for n in (1, 2, 3)],
                         ["5d8", "7d8", "9d8"])
        self.assertEqual(eng.spell_resolution("Sommeil", 1)["mode"], "reserve")
        self.assertEqual(eng.spell_resolution("Couleurs dansantes", 2)["reserve"].formula, "8d10")

    def test_sleep_2024_is_a_save(self):
        eng = sheet(edition="2024")
        self.assertEqual(eng.spell_resolution("Sommeil (2024)", 1)["mode"], "sauvegarde")


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        cls.win = MainWindow(DB)

    def test_class_options_moved_to_classes_tab(self):
        eng = self.win.engine
        eng.ch.classes = [{"nom": "Guerrier", "niveau": 3, "sous_classe": "Maître de guerre", "pv_jets": []}]
        eng.normalize()
        self.win.changed()
        self.win.classes_tab.refresh()
        self.assertNotIn("options_box", vars(self.win.combat_tab))
        tab = self.win.classes_tab
        self.assertIn("Rappels", tab.options_box.title())
        self.assertIn("3 à choisir", tab.options_label.text())    # rappel en bas, pas de liste à choisir

    def test_short_common_labels(self):
        from ui.combat_tab import CombatTab
        self.assertEqual(CombatTab.SHORT_COMMON["Utiliser un objet"], "Objet")

    def test_no_dice_in_wizard(self):
        from ui.dice_dialog import roll_damage_dialog, roll_dice
        from core import dice as D

        class Host:
            no_dice = True
        self.assertIsNone(roll_dice(Host(), self.win.engine.skill_spec("Acrobaties")))
        self.assertIsNone(roll_damage_dialog(Host(), D.DamageSpec("x", "1d6")))


class LevelUpChoiceTests(unittest.TestCase):
    def test_maneuvers_chosen_in_level_up(self):
        eng = sheet("Guerrier", 2)
        sim = eng.simulate_level_up("Guerrier")
        sim.ch.find_class("Guerrier")["sous_classe"] = "Maître de guerre"
        sim.normalize()
        self.assertEqual(eng.level_option_keys(sim), {"manoeuvres"})
        rep = eng.level_up_report(sim, "Guerrier")
        self.assertIn("options", {m["kind"] for m in rep["dans_assistant"]})     # bloque « Confirmer »
        for i, n in enumerate(list(DB.maneuvers)[:3]):
            sim.set_class_option("manoeuvres", i, n)
        self.assertNotIn("options", {m["kind"] for m in eng.level_up_report(sim, "Guerrier")["dans_assistant"]})

    def test_more_maneuvers_at_level_7(self):
        eng = sheet("Guerrier", 6, "Maître de guerre")
        for i, n in enumerate(list(DB.maneuvers)[:3]):
            eng.set_class_option("manoeuvres", i, n)
        sim = eng.simulate_level_up("Guerrier")
        self.assertEqual(eng.level_option_keys(sim), {"manoeuvres"})

    def test_superior_technique_is_a_class_choice(self):
        eng = sheet("Guerrier", 3, "Champion")
        eng.ch.styles_combat = {s["id"]: "Technique supérieure" for s in eng.fighting_style_slots()}
        eng.normalize()
        st = next(s for s in eng.option_sets() if s["key"] == "technique_superieure")
        self.assertEqual((st["total"], st["chosen"]), (1, []))
        name = next(iter(DB.maneuvers))
        eng.set_class_option("technique_superieure", 0, name)
        self.assertEqual(eng.ch.technique_manoeuvre, name)
        self.assertIsNotNone(eng.superior_technique_action())


class LevelUpSkillsLanguagesFeatsTests(unittest.TestCase):
    def test_rogue_expertise_in_level_up(self):
        eng = sheet("Roublard", 5)
        sim = eng.simulate_level_up("Roublard")                     # niveau 6 : deux expertises
        rep = eng.level_up_report(sim, "Roublard")
        self.assertIn("competences", {m["kind"] for m in rep["dans_assistant"]})
        prof = [n for n, s in sim.ch.competences.items() if s.get("maitrise") and not s.get("expertise")]
        if len(prof) < 2:                                           # fiche nue : deux maîtrises pour le test
            for n in DB.skill_names[:2]:
                sim.ch.competences[n] = {"maitrise": True, "expertise": False}
            prof = DB.skill_names[:2]
        missing = sim.expertise_missing()
        for n in prof[:missing]:
            self.assertTrue(eng.level_set_skill(sim, n, "expertise", True))
        self.assertFalse(eng.level_set_skill(sim, prof[-1] if len(prof) > missing else "Arcanes", "expertise", True))
        self.assertNotIn("competences", {m["kind"] for m in eng.level_up_report(sim, "Roublard")["dans_assistant"]})

    def test_feat_choices_and_languages(self):
        eng = sheet("Guerrier", 3)
        sim = eng.simulate_level_up("Guerrier")
        sid = sim.asi_slots()[-1]["id"]
        sim.ch.ameliorations[sid] = {"mode": "don", "don": "Linguiste"}
        sim.normalize()
        kinds = {m["kind"] for m in eng.level_up_report(sim, "Guerrier")["dans_assistant"]}
        self.assertIn("langues", kinds)
        for name in eng.level_language_options(sim):
            if sim.languages_missing() <= 0:
                self.assertFalse(eng.level_set_language(sim, name, True))      # pas au-delà de ce qui est accordé
                break
            eng.level_set_language(sim, name, True)
        self.assertNotIn("langues", {m["kind"] for m in eng.level_up_report(sim, "Guerrier")["dans_assistant"]})
        sim.ch.ameliorations[sid] = {"mode": "don", "don": "Doué"}
        sim.normalize()
        self.assertTrue(any(k.startswith("don:") for k in eng.level_feat_keys(sim)))
        self.assertIn("dons", {m["kind"] for m in eng.level_up_report(sim, "Guerrier")["dans_assistant"]})


class LevelUpSummaryTests(unittest.TestCase):
    def test_summary_lists_every_difference(self):
        eng = sheet("Roublard", 5, "Voleur")
        for n in ("Discrétion", "Acrobaties", "Perception", "Tromperie"):
            eng.ch.competences[n] = {"maitrise": True, "expertise": n in ("Discrétion", "Acrobaties")}
        eng.normalize()
        sim = eng.simulate_level_up("Roublard")
        eng.level_set_skill(sim, "Perception", "expertise", True)
        changes = dict(eng.level_up_changes(sim, "Roublard"))
        self.assertEqual(changes["Classe"], ["Roublard : niveau 5 → 6"])
        self.assertIn("Expertise : Perception", changes["Compétences"])
        self.assertIn("Aptitudes gagnées", changes)

    def test_summary_spells_and_feat(self):
        eng = sheet("Magicien", 3)
        sim = eng.simulate_level_up("Magicien")
        name = next(o["nom"] for o in eng.level_spell_options(sim, "Magicien") if o.get("niveau"))
        self.assertTrue(eng.level_learn_spell(sim, "Magicien", name))
        sim.ch.ameliorations[sim.asi_slots()[-1]["id"]] = {"mode": "plus2", "a1": "Intelligence"}
        sim.normalize()
        changes = dict(eng.level_up_changes(sim, "Magicien"))
        self.assertIn("{} (Magicien)".format(name), changes["Sorts appris"])
        self.assertEqual(changes["Amélioration de caractéristiques ou don"], ["+2 en Intelligence"])


class RealQtDiceTests(unittest.TestCase):
    """Fenêtres de dés construites avec le VRAI PyQt6 (le faux Qt des autres tests ne voit pas ces erreurs)."""

    def test_dice_dialogs_build(self):
        import os
        import subprocess
        code = ("import sys; sys.path.insert(0, '.')\n"
                "from PyQt6.QtWidgets import QApplication; app = QApplication([])\n"
                "from core.data_loader import Database; from core.engine import Engine; from core import dice as D\n"
                "from ui.dice_dialog import DiceRollDialog, DamageRollDialog\n"
                "db = Database('data'); eng = Engine(db, Engine.new_character(db)); eng.normalize()\n"
                "DiceRollDialog(None, eng.skill_spec('Acrobaties'))\n"
                "d = DamageRollDialog(None, D.DamageSpec('Épée', '1d8+2d6+3', 'tranchant')); d.finish_now()\n"
                "print('OK')\n")
        env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
        out = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), env=env, capture_output=True, text=True,
                             timeout=120)
        if "No module named 'PyQt6'" in out.stderr:     # le faux Qt des autres tests ne compte pas ici
            self.skipTest("PyQt6 absent")
        self.assertIn("OK", out.stdout, out.stderr[-1500:])


if __name__ == "__main__":
    unittest.main()
