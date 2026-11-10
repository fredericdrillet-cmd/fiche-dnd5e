"""Tests v48 : assistant de création niveau 1 (BG3), magie raciale pour toutes les classes, paquetage / boutique,
Mode guidé / Mode libre, résumé de la race, sauvegarde automatique et réouverture."""
import random
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from test_v40_wizard_saves import make  # noqa: E402
from test_v41_grimoire_combat import window  # noqa: E402
from core.creation import CLASS_KITS, parse_price, split_coins  # noqa: E402
from core.engine import Engine  # noqa: E402


def fresh(race="Humain", cls="Guerrier", sub=""):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race(race)
    eng.ch.sous_race = sub
    if cls != "Guerrier":
        eng.change_class(0, cls)
    eng.normalize()
    return eng


class RacialMagicTests(unittest.TestCase):
    def test_tiefling_fighter_racial_spell_tile(self):
        eng = fresh("Tieffelin", "Guerrier")
        self.assertIsNone(eng.caster("Guerrier"))
        tiles = [t for t in eng.turn_actions() if t["id"].startswith("sort:")]
        self.assertTrue(tiles)
        self.assertTrue(all("[Sort Racial]" in t["origine"] and t["groupe"] == "magie" for t in tiles))

    def test_high_elf_cantrip_choice(self):
        eng = fresh("Elfe", "Guerrier", "Haut-elfe")
        slots = eng.racial_choice_slots()
        self.assertEqual(slots[0]["liste"], "Magicien")
        self.assertIn("1 sort mineur racial à choisir", [m["message"] for m in eng.missing_choices()])
        name = eng.racial_choice_options(slots[0]["cle"])[0]["nom"]
        self.assertFalse(eng.set_racial_choice(slots[0]["cle"], "Boule de feu"))      # pas un tour du magicien
        self.assertTrue(eng.set_racial_choice(slots[0]["cle"], name))
        self.assertIn(name, [r["nom"] for r in eng.racial_spells()])
        self.assertNotIn("1 sort mineur racial à choisir", [m["message"] for m in eng.missing_choices()])
        self.assertTrue(any(t["nom"] == name and "[Sort Racial]" in t["origine"] for t in eng.turn_actions()))

    def test_rp_race_summary(self):
        win = window(fresh("Tieffelin", "Guerrier"))
        html = win.rp_tab.race_summary_html()
        self.assertIn("Tieffelin", html)
        self.assertIn("[Sort Racial]", html)
        self.assertIn("Traits raciaux", html)


class EquipmentTests(unittest.TestCase):
    def test_prices_and_coins(self):
        self.assertEqual(parse_price("15 po"), 15.0)
        self.assertAlmostEqual(parse_price("2 pa"), 0.2)
        self.assertAlmostEqual(parse_price("5 pc"), 0.05)
        self.assertEqual(parse_price("—"), 0.0)
        self.assertEqual(split_coins(15.37), {"po": 15, "pa": 3, "pc": 7})

    def test_every_class_has_kit_and_gold(self):
        for cls in DB.class_names():
            eng = fresh(cls=cls)
            self.assertIn(cls, CLASS_KITS)
            self.assertGreater(eng.starting_gold()["moyenne"], 0)
            res = eng.apply_starting_equipment("paquetage")
            self.assertTrue(res["ajouts"])
            self.assertEqual(eng.ch.pieces["po"], eng.background_gold())

    def test_fighter_kit_equipped(self):
        eng = fresh()
        eng.apply_starting_equipment("paquetage")
        self.assertEqual(eng.ch.armure["nom"], "Cotte de mailles")
        self.assertTrue(eng.ch.armure["bouclier"])
        self.assertEqual(eng.ch.armes_cac[0]["nom"], "Épée longue")
        self.assertEqual(eng.armor_class()[0], 18)

    def test_shop_budget(self):
        eng = fresh()
        budget = 125 + eng.background_gold()
        res = eng.apply_starting_equipment("boutique", 125, {"Épée longue": 1, "Corde": 2})
        spent = 15 + 2 * parse_price(DB.catalog["Corde"]["prix"])
        self.assertAlmostEqual(res["depense"], spent)
        self.assertEqual(eng.ch.pieces, split_coins(budget - spent))
        self.assertIn("Épée longue", [e["nom"] for e in eng.ch.equipement])
        bg_first = eng.background_items()[0][1]
        self.assertIn(bg_first, [e["nom"] for e in eng.ch.equipement])          # équipement d'historique offert
        with self.assertRaises(ValueError):
            eng.apply_starting_equipment("boutique", 0, {"Cotte de mailles": 1})


class WizardTests(unittest.TestCase):
    def test_full_flow(self):
        from ui.creation_wizard import STEPS, CreationWizard, apply_creation
        win = window(make("Guerrier", 3))
        w = CreationWizard(win)
        self.assertEqual(STEPS, ["Race / Sous-race", "Classe", "Historique", "Caractéristiques",
                                 "Sorts et tours de magie", "Équipement", "Identité"])
        for i in range(len(STEPS)):
            w.go(i)
        self.assertEqual(w.engine.total_level, 1)
        self.assertIsNot(w.engine, win.engine)                                   # copie : la fiche est intacte
        w.engine.change_race("Elfe")
        w.ch.sous_race = "Haut-elfe"
        w.host.changed()
        w._on_class("Magicien")
        w.go(4)
        self.assertIn("mineurs", w.spell_widgets)
        cantrip = next(s["nom"] for s in w.engine.level_spell_options(w.engine, "Magicien") if s["niveau"] == 0)
        self.assertTrue(w.learn("Magicien", cantrip))
        w.set_racial("Sort mineur", w.engine.racial_choice_options("Sort mineur")[1]["nom"])
        w.set_equip_mode("boutique")
        self.assertEqual(w.budget(), 100 + w.engine.background_gold())
        self.assertTrue(w.buy("Dague"))
        self.assertFalse(w.buy("Harnois"))                                       # au-delà du budget
        rolled = w.roll_gold(random.Random(3))
        self.assertTrue(40 <= rolled <= 160)
        w._set_identity("nom", "Elara")
        w._set_identity("joueur", "Fred")
        self.assertIn("Elara", w.summary_html())
        self.assertIn("Haut-elfe", w.summary_html())
        w.finalize()
        apply_creation(win, w)
        ch = win.engine.ch
        self.assertEqual((ch.nom, ch.joueur, ch.race, ch.classes[0]["nom"]), ("Elara", "Fred", "Elfe", "Magicien"))
        self.assertIn("Dague", [e["nom"] for e in ch.equipement])
        self.assertIn(cantrip, [s["nom"] for s in ch.sorts["Magicien"]])
        self.assertTrue(win._dirty)
        self.assertIsNone(win.path)

    def test_nameless_defaults(self):
        from ui.creation_wizard import CreationWizard
        w = CreationWizard(window(make("Guerrier", 1)))
        w.finalize()
        self.assertEqual(w.ch.nom, "Sans nom")
        self.assertEqual(w.ch.armes_cac[0]["nom"], "Épée longue")                # paquetage par défaut


class ModeTests(unittest.TestCase):
    def test_guided_mode_hides_race_tab_and_raw_scores(self):
        eng = make("Guerrier", 1)
        eng.ch.langues_liste = [x["nom"] for x in DB.languages][:6]                # aucun choix de langue en attente
        eng.normalize()
        win = window(eng)
        win.settings["mode_libre"] = False
        win.refresh_all()
        if not any(m["onglet"] == "race" for m in win.engine.missing_choices()):
            self.assertNotIn("race", win.shown_keys())
        self.assertFalse(win.stats_tab.editors_visible() and not any(
            m["onglet"] == "caracteristiques" and m["encart"] != "Compétences" for m in win.engine.missing_choices()))
        win.settings["mode_libre"] = True
        win.refresh_all()
        self.assertIn("race", win.shown_keys())
        self.assertTrue(win.stats_tab.editors_visible())

    def test_guided_classes_tab_read_only(self):
        win = window(make("Guerrier", 3))
        win.settings["mode_libre"] = False
        state = {}
        tab = win.classes_tab
        tab.add_btn.setVisible = lambda v: state.__setitem__("visible", v)
        tab.ch.multiclassage = True
        tab.refresh()
        self.assertFalse(state["visible"])
        self.assertFalse(win.free_mode)
        src = (ROOT / "ui" / "options_dialog.py").read_text(encoding="utf-8")
        self.assertIn("Activer le Mode libre", src)

    def test_header_has_no_alignment(self):
        win = window(make("Guerrier", 1))
        src = (ROOT / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertNotIn('make_label("Alignement")', src)


class AutosaveTests(unittest.TestCase):
    def test_autosave_and_restore(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        win = window(make("Roublard", 2))
        win.ch.nom = "Vex"
        win._dirty = True
        auto = tmp / "auto.json"
        self.assertTrue(win.autosave(auto))
        other = window(make("Guerrier", 1))
        self.assertEqual(other.restore_last_session(auto), "auto")
        self.assertEqual(other.ch.nom, "Vex")
        self.assertTrue(other._dirty)

    def test_reopen_last_saved_file(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        win = window(make("Clerc", 1))
        win.ch.nom = "Aldric"
        path = tmp / "aldric.json"
        win._write(path)
        self.assertEqual(win.settings["dernier_fichier"], str(path))
        other = window(make("Guerrier", 1))
        other.settings["dernier_fichier"] = str(path)
        self.assertEqual(other.restore_last_session(tmp / "absent.json"), "fichier")
        self.assertEqual(other.ch.nom, "Aldric")
        self.assertEqual(other.path, path)


if __name__ == "__main__":
    unittest.main()
