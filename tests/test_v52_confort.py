"""v52 : règles et confort — épuisement selon l'édition (compteur, JS d'épuisement, Frénésie 2014)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402
from core import effects as FX  # noqa: E402

DB = Database(ROOT / "data")


def sheet(cls, lvl, edition="2024", sub=""):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    return eng


class ExhaustionTests(unittest.TestCase):
    def test_2014_table(self):
        eng = sheet("Guerrier", 3, "2014")
        speed = eng.speed() if hasattr(eng, "speed") else None
        eng.set_exhaustion(1)
        self.assertIn("Épuisement 1", eng.check_mods("Force")["desavantage"])
        self.assertFalse(eng.save_spec("Force").desavantage)
        eng.set_exhaustion(3)
        self.assertTrue(eng.save_spec("Force").desavantage)
        self.assertIn("vitesse divisée", eng.exhaustion_text())
        self.assertEqual(eng.exhaustion_level(), 3)
        del speed

    def test_2024_minus_two_per_level(self):
        eng = sheet("Guerrier", 3)
        base = eng.save_spec("Force").flat
        eng.set_exhaustion(2)
        self.assertEqual(eng.save_spec("Force").flat, base - 4)
        self.assertFalse(eng.check_mods("Force")["desavantage"])
        self.assertIn("−4", eng.exhaustion_text())
        self.assertIn("3 m", eng.exhaustion_text())
        self.assertEqual(eng.speed(), 6.0)

    def test_counter_bounds_and_long_rest(self):
        for ed in ("2014", "2024"):
            eng = sheet("Guerrier", 3, ed)
            eng.set_exhaustion(9)
            self.assertEqual(eng.exhaustion_level(), 6)
            self.assertIn("meurt", eng.exhaustion_text())
            eng.set_exhaustion(2)
            eng.do_long_rest()
            self.assertEqual(eng.exhaustion_level(), 1, ed)
            eng.set_exhaustion(-1)
            self.assertEqual(eng.exhaustion_level(), 0)
            self.assertEqual([k for k in eng.ch.effets_actifs if k.startswith("epuisement")], [])

    def test_exhaustion_save(self):
        eng = sheet("Guerrier", 3)
        self.assertEqual(eng.exhaustion_dc("marche", 3), 13)
        self.assertEqual(eng.exhaustion_dc("chaleur", 1), 5)
        self.assertEqual(eng.exhaustion_dc("autre", dc=17), 17)
        spec = eng.exhaustion_save_spec("froid", 10)
        self.assertIn("Constitution DD 10", spec.title)
        self.assertIn("réussi", eng.apply_exhaustion_save(12, 10))
        self.assertEqual(eng.exhaustion_level(), 0)
        self.assertIn("raté", eng.apply_exhaustion_save(4, 10))
        self.assertEqual(eng.exhaustion_level(), 1)

    def test_berserker_2014_frenzy(self):
        eng = sheet("Barbare", 3, "2014", "Voie du berserker")
        eng.use_class_action("rage")
        eng.add_effect("frenesie")
        r = eng.use_class_action("rage")              # fin de la rage
        self.assertIn("épuisement", r["message"])
        self.assertEqual(eng.exhaustion_level(), 1)
        self.assertNotIn("frenesie", eng.ch.effets_actifs)
        eng.use_class_action("rage")
        eng.use_class_action("rage")                  # sans frénésie : rien
        self.assertEqual(eng.exhaustion_level(), 1)


if __name__ == "__main__":
    unittest.main()


class DurationTests(unittest.TestCase):
    def test_parse(self):
        from core.durations import parse_rounds, rounds_text
        self.assertEqual(parse_rounds("1 minute"), 10)
        self.assertEqual(parse_rounds("Concentration, jusqu'à 10 minutes"), 100)
        self.assertEqual(parse_rounds("1 heure"), 600)
        self.assertIsNone(parse_rounds("1 heure par verre au-delà du mod. de Con"))
        self.assertIsNone(parse_rounds("Variable"))
        self.assertEqual(rounds_text(7), "7 rounds")
        self.assertEqual(rounds_text(600), "60 min")

    def test_countdown_on_turn_start(self):
        for ed in ("2014", "2024"):
            eng = sheet("Clerc", 3, ed)
            eng.add_effect("benediction")
            self.assertEqual(eng.effect_rounds("benediction"), 10)
            for _ in range(3):
                eng.start_turn()
            self.assertEqual(eng.effect_rounds("benediction"), 7)
            self.assertIn("7 rounds", eng.effect_rounds_text("benediction"))
            self.assertIn("remise", eng.extend_effect("benediction"))
            self.assertEqual(eng.effect_rounds("benediction"), 10)
            msgs = []
            for _ in range(10):
                msgs += eng.start_turn()["appliques"]
            self.assertNotIn("benediction", eng.ch.effets_actifs, ed)
            self.assertTrue(any("Bénédiction" in m for m in msgs))

    def test_time_and_concentration(self):
        eng = sheet("Clerc", 3, "2014")
        r = eng.cast_spell("Bénédiction", slot_level=1, target="allie")
        if not r["ok"]:
            self.skipTest(r["message"])
        self.assertEqual(eng.effect_rounds("concentration"), 10)
        eng.advance_time(1)
        self.assertEqual(eng.ch.concentration, "")
        self.assertIsNone(eng.effect_rounds("concentration"))

    def test_hour_effect_survives_minutes(self):
        eng = sheet("Guerrier", 3, "2024")
        key = next(k for k, e in FX.EFFECTS.items() if e["duree"] == "1 heure")
        eng.add_effect(key)
        eng.advance_time(10)
        self.assertEqual(eng.effect_rounds(key), 500)
        eng.advance_time(50)
        self.assertNotIn(key, eng.ch.effets_actifs)


class CommonActionTests(unittest.TestCase):
    def names(self, eng):
        return {t["id"].split(":", 1)[1]: t for t in eng.turn_actions() if t["id"].startswith("commune:")}

    def test_lists_per_edition(self):
        old, new = self.names(sheet("Guerrier", 5, "2014")), self.names(sheet("Guerrier", 5, "2024"))
        for cid in ("pret", "cacher", "saisir", "bousculer", "chercher"):
            self.assertIn(cid, old)
            self.assertIn(cid, new)
        for cid in ("etudier", "influencer", "magie"):
            self.assertNotIn(cid, old)
            self.assertIn(cid, new)
        self.assertIn("Perception passive", old["cacher"]["description"])
        self.assertIn("DD 15", new["cacher"]["description"])

    def test_grapple_2024_dc_and_attack_count(self):
        eng = sheet("Guerrier", 5, "2024")
        dc = eng.grapple_dc()
        self.assertEqual(dc, 8 + eng.mod("Force") + eng.prof)
        self.assertIn("DD {}".format(dc), self.names(eng)["saisir"]["description"])
        r = eng.use_turn_action("commune:saisir")
        self.assertIn("JS de Force ou de Dextérité DD {}".format(dc), r["message"])
        self.assertEqual(eng.ch.tour_attaques, 1)
        self.assertFalse(r.get("tests"))

    def test_grapple_2014_contest(self):
        eng = sheet("Guerrier", 5, "2014")
        r = eng.use_turn_action("commune:bousculer")
        self.assertEqual(r["tests"], ["Athlétisme"])

    def test_hide(self):
        eng = sheet("Roublard", 3, "2024")
        r = eng.use_turn_action("commune:cacher")
        self.assertEqual((r["tests"], r["dd"]), (["Discrétion"], 15))
        self.assertIn("visible", eng.resolve_common_test("cacher", "Discrétion", 12, 15))
        self.assertNotIn("cache", eng.ch.effets_actifs)
        self.assertIn("DD 17 pour vous trouver", eng.resolve_common_test("cacher", "Discrétion", 17, 15))
        self.assertIn("cache", eng.ch.effets_actifs)
        eng14 = sheet("Roublard", 3, "2014")
        r = eng14.use_turn_action("commune:cacher")
        self.assertEqual(r["dd"], 0)
        self.assertIn("Perception passive", eng14.resolve_common_test("cacher", "Discrétion", 12))

    def test_search_skills(self):
        self.assertIn("Médecine", sheet("Clerc", 3, "2024").use_turn_action("commune:chercher")["tests"])
        self.assertIn("Investigation", sheet("Clerc", 3, "2014").use_turn_action("commune:chercher")["tests"])


class ExhaustionUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        cls.win = MainWindow(DB)

    def test_counter_buttons(self):
        tab = self.win.combat_tab
        self.win.engine.set_exhaustion(0)
        tab.refresh()
        tab._on_exhaustion(1)
        tab._on_exhaustion(1)
        tab.refresh()
        self.assertEqual(self.win.engine.exhaustion_level(), 2)
        self.assertIn("◆◆◇◇◇◇", tab.exh_label.text())
        tab._on_exhaustion(-1)
        self.assertEqual(self.win.engine.exhaustion_level(), 1)

    def test_dialog_without_roll(self):
        from ui.exhaustion_dialog import ExhaustionDialog
        self.win.engine.set_exhaustion(0)
        dlg = ExhaustionDialog(self.win, "chaleur")
        self.assertEqual(dlg.cause_id(), "chaleur")
        self.assertEqual(dlg.dc.value(), 5)
        dlg._on_fail()
        self.assertEqual(self.win.engine.exhaustion_level(), 1)
        self.assertIn("Chaleur extrême", dlg.result_text)


class DurationUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        cls.win = MainWindow(DB)

    def test_badge_timer_and_extend(self):
        tab = self.win.combat_tab
        eng = self.win.engine
        eng.add_effect("benediction")
        eng.start_turn()
        tab.refresh()
        self.assertEqual(eng.effect_rounds("benediction"), 9)
        tab._on_extend_effect("benediction")
        self.assertEqual(eng.effect_rounds("benediction"), 10)
        eng.remove_effect("benediction")
