"""Tests v27 : actions de race (encart Combat), styles de combat passifs, vision dans le noir, mini-fiche des entités."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core import race_actions as RA  # noqa: E402
from core.engine import Engine  # noqa: E402


def make(race, c="Guerrier", lvl=5, sub=""):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race(race)
    eng.ch.classes = [{"nom": c, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng.normalize()
    return eng


def race_acts(eng):
    return {a["nom"]: a for a in eng.class_actions() if a.get("origine") == "race"}


def window():
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    return mw.MainWindow(DB)


class RaceActionTests(unittest.TestCase):
    def test_goblin_fury(self):
        eng = make("Gobelin")
        acts = race_acts(eng)
        fury = acts["Fureur des petits"]
        self.assertEqual(fury["formule"], str(eng.prof))
        tr = next(t for t in eng.resource_trackers("combat") if t["key"] == fury["id"])
        self.assertEqual((tr["total"], tr["recover"]), (eng.prof, "repos long"))
        self.assertIn("Fuite agile", acts)
        self.assertEqual(acts["Fuite agile"]["type"], "Action bonus")

    def test_spend_lock_and_rest(self):
        eng = make("Gobelin")
        aid = race_acts(eng)["Fureur des petits"]["id"]
        for _ in range(eng.prof):
            self.assertTrue(eng.use_class_action(aid)["ok"])
        self.assertFalse(race_acts(eng)["Fureur des petits"]["disponible"])
        self.assertFalse(eng.use_class_action(aid)["ok"])
        eng.short_rest()
        self.assertFalse(race_acts(eng)["Fureur des petits"]["disponible"])      # repos long requis
        eng.long_rest()
        self.assertTrue(race_acts(eng)["Fureur des petits"]["disponible"])

    def test_reset_on_race_change(self):
        eng = make("Gobelin")
        aid = race_acts(eng)["Fureur des petits"]["id"]
        eng.use_class_action(aid)
        eng.change_race("Humain")
        self.assertEqual(race_acts(eng), {})
        self.assertNotIn(aid, eng.ch.ressources_utilisees)
        eng.change_race("Gobelin")
        self.assertTrue(race_acts(eng)["Fureur des petits"]["disponible"])
        self.assertEqual(eng.resource_used(aid), 0)

    def test_reaction_trait_consumes_reaction(self):
        eng = make("Goliath")
        a = race_acts(eng)["Endurance de pierre"]
        self.assertEqual(a["type"], "Réaction")
        self.assertEqual(a["formule"], "1d12{:+d}".format(eng.mod("Constitution")).replace("+0", ""))
        self.assertIn("Endurance de pierre", [r["nom"] for r in eng.reactions()])
        res = eng.use_class_action(a["id"])
        self.assertTrue(res["ok"])
        self.assertTrue(eng.ch.reaction_utilisee)
        self.assertFalse(eng.use_class_action(a["id"])["ok"])

    def test_breath_is_short_rest_action(self):
        eng = make("Drakéide")
        a = race_acts(eng)["Souffle"]
        self.assertEqual((a["id"], a["type"], a["formule"]), ("souffle", "Action", "2d6"))
        eng.use_class_action("souffle")
        self.assertFalse(race_acts(eng)["Souffle"]["disponible"])
        eng.short_rest()
        self.assertTrue(race_acts(eng)["Souffle"]["disponible"])

    def test_level_gate_and_first_trigger(self):
        self.assertNotIn("Âme radieuse", race_acts(make("Aasimar protecteur", lvl=2)))
        a = race_acts(make("Aasimar protecteur", lvl=3))["Âme radieuse"]
        self.assertEqual(a["type"], "Action")                  # « y mettre fin par une action bonus » ignoré

    def test_spell_and_rest_traits_excluded(self):
        self.assertEqual(race_acts(make("Tieffelin")), {})       # Héritage infernal : onglet Magie
        self.assertEqual(race_acts(make("Elfe")), {})            # Transe
        self.assertEqual(race_acts(make("Humain")), {})
        self.assertTrue(RA.is_spell_trait("Sorts : *Thaumaturgie* (sort mineur)"))

    def test_heal_trait(self):
        eng = make("Aasimar protecteur")
        a = race_acts(eng)["Mains guérisseuses"]
        self.assertTrue(a["soin"])
        self.assertEqual(a["formule"], str(eng.total_level))


class FightingStyleTests(unittest.TestCase):
    def _with_style(self, style, cls="Guerrier"):
        eng = make("Humain", cls, 5)
        slot = next(s for s in eng.fighting_style_slots() if s["kind"] == "style" and s["debloque"])
        eng.ch.styles_combat[slot["id"]] = style
        eng.normalize()
        return eng

    def test_passive_style_not_in_reactions(self):
        for style in ("Duel", "Défense", "Armes à deux mains", "Archerie"):
            eng = self._with_style(style)
            names = [r["nom"] for r in eng.reactions()]
            self.assertNotIn("Style de combat", names, style)
            self.assertNotIn(style, names)
            self.assertIn("Style de combat : " + style, [p["nom"] for p in eng.class_passives()])

    def test_reaction_styles_stay_reactions(self):
        for style in ("Protection", "Interception"):
            eng = self._with_style(style)
            self.assertIn(style, [r["nom"] for r in eng.reactions()])
            self.assertNotIn("Style de combat : " + style, [p["nom"] for p in eng.class_passives()])

    def test_paladin_style(self):
        eng = self._with_style("Défense", "Paladin")
        self.assertIn("Style de combat : Défense", [p["nom"] for p in eng.class_passives()])


class VisionTests(unittest.TestCase):
    def test_darkvision_ranges(self):
        self.assertEqual(make("Gobelin").darkvision()["portee"], 18)
        dv = make("Drow (Elfe noir)").darkvision()
        self.assertEqual(dv["portee"], 36)
        self.assertTrue(dv["superieure"])
        self.assertEqual(make("Humain").darkvision()["portee"], 0)

    def test_darkvision_spell(self):
        eng = make("Humain")
        eng.ch.effets_actifs.append("vision_noir") if isinstance(eng.ch.effets_actifs, list) else \
            eng.ch.effets_actifs.__setitem__("vision_noir", {})
        self.assertEqual(eng.darkvision()["portee"], 18)


class UiTests(unittest.TestCase):
    def test_actions_box_title(self):
        win = window()
        win.engine.change_race("Gobelin")
        win.changed()
        self.assertEqual(win.combat_tab.res_box.title(), "⚔ Actions, capacités de classe et de race")
        win.engine.change_race("Humain")
        win.ch.classes = [{"nom": "Guerrier", "niveau": 3, "sous_classe": "", "pv_jets": []}]
        win.engine.normalize()
        win.changed()
        self.assertEqual(win.combat_tab.res_box.title(), "⚔ Actions, capacités de classe")

    def test_vision_box(self):
        win = window()
        win.engine.change_race("Gobelin")
        win.changed()
        self.assertIn("18 m", win.combat_tab.stat_labels["vision"].text())
        self.assertEqual(win.combat_tab.stat_boxes["vision"].title(), "Vision dans le noir")
        win.engine.change_race("Humain")
        win.changed()
        self.assertIn("Normale", win.combat_tab.stat_labels["vision"].text())

    def test_companion_gauge_black_text(self):
        win = window()
        inst = win.engine.menagerie_add("chat")
        tab = win.companions_tab
        tab.current_uid = inst["uid"]
        tab.refresh()
        self.assertEqual(tab.w["gauge"].text_color, "#000000")


if __name__ == "__main__":
    unittest.main()
