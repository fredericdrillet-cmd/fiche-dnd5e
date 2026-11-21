"""v52 : tous les choix de construction à la création ou à la montée de niveau — bottes d'arme, Mode guidé,
remplacements d'un choix, sorts 2024 (listes, tours de magie), échanges du repos long, grimoire du Magicien."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def sheet(cls, lvl=1, sub="", edition="2014"):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    if sub:
        ch.classes[0]["sous_classe"] = next(s["nom"] for s in eng.db.subclasses(cls) if sub in s["nom"])
        eng.normalize()
    return eng


class MasteryTests(unittest.TestCase):
    def test_masteries_are_a_tracked_choice(self):
        eng = sheet("Guerrier", 1, edition="2024")
        st = next(s for s in eng.option_sets() if s["key"] == "bottes")
        self.assertEqual(st["total"], 3)
        self.assertIn(("classes", "Options de classe"), {(m["onglet"], m["encart"]) for m in eng.missing_choices()})
        for i, n in enumerate(list(st["options"])[:3]):
            eng.set_class_option("bottes", i, n)
        self.assertEqual(len(eng.ch.bottes_choisies), 3)
        self.assertEqual(eng.level_option_keys(eng.simulate_level_up("Guerrier")) & {"bottes"}, set())
        sim = eng.simulate_level_up("Guerrier")
        for _ in range(2):                                         # niveau 4 : une botte de plus
            sim.ch.classes[0]["niveau"] += 1
        sim.normalize()
        self.assertIn("bottes", eng.level_option_keys(sim))

    def test_rest_swaps_one_mastery(self):
        eng = sheet("Guerrier", 1, edition="2024")
        st = next(s for s in eng.option_sets() if s["key"] == "bottes")
        for i, n in enumerate(list(st["options"])[:3]):
            eng.set_class_option("bottes", i, n)
        sw = next(x for x in eng.rest_option_swaps() if x["key"] == "bottes")
        old = sw["set"]["chosen"][0]
        new = next(n for n in sw["set"]["options"] if n not in sw["set"]["chosen"])
        self.assertTrue(eng.rest_swap_option("bottes", old, new)[0])
        self.assertIn(new, eng.ch.bottes_choisies)
        self.assertNotIn(old, eng.ch.bottes_choisies)
        self.assertFalse(eng.rest_swap_option("bottes", "Inexistante", new)[0])


class ReplaceOneChoiceTests(unittest.TestCase):
    def _bm(self, edition):
        eng = sheet("Guerrier", 3, "guerre", edition)
        names = list(next(s for s in eng.option_sets() if s["key"] == "manoeuvres")["options"])
        for i, n in enumerate(names[:3]):
            eng.set_class_option("manoeuvres", i, n)
        return eng, names

    def test_battle_master_2014_only_when_learning(self):
        eng, names = self._bm("2014")
        sim = eng.simulate_level_up("Guerrier")                     # niveau 4 : pas de nouvelle manœuvre
        self.assertFalse(eng.level_replace_allowed(sim, "manoeuvres", "Guerrier"))

    def test_battle_master_2024_one_per_level(self):
        eng, names = self._bm("2024")
        sim = eng.simulate_level_up("Guerrier")
        self.assertTrue(eng.level_replace_option(sim, "manoeuvres", names[0], names[5]))
        self.assertTrue(eng.level_replace_option(sim, "manoeuvres", names[1], names[6]))   # annule le premier
        chosen = eng._level_chosen(sim, "manoeuvres")
        self.assertIn(names[0], chosen)
        self.assertNotIn(names[1], chosen)
        self.assertIn("(remplace", " ".join(dict(eng.level_up_changes(sim, "Guerrier"))["Choix de classe"]))


class Spells2024Tests(unittest.TestCase):
    def test_list_casters_2024_swap_one_spell(self):
        for cls in ("Barde", "Ensorceleur", "Occultiste"):
            eng = sheet(cls, 3, edition="2024")
            for n in [o["nom"] for o in eng.level_spell_options(eng, cls) if o.get("niveau")][:2]:
                eng.level_learn_spell(eng, cls, n)
            self.assertTrue(eng.level_swap_allowed(eng.simulate_level_up(cls), cls), cls)
            self.assertFalse(eng.free_prep_class(cls))
        self.assertTrue(sheet("Clerc", 3, edition="2024").free_prep_class("Clerc"))
        self.assertFalse(sheet("Paladin", 3, edition="2024").free_prep_class("Paladin"))
        self.assertTrue(sheet("Paladin", 3).free_prep_class("Paladin"))

    def test_cantrip_swap_at_level_up(self):
        eng = sheet("Clerc", 1, edition="2024")
        for n in [o["nom"] for o in eng.level_spell_options(eng, "Clerc") if not o.get("niveau")][:3]:
            eng.level_learn_spell(eng, "Clerc", n)
        sim = eng.simulate_level_up("Clerc")
        old, new = eng._cantrips_of(eng, "Clerc")[0], eng.level_cantrip_options(sim, "Clerc")[0]
        self.assertTrue(eng.level_cantrip_swap(sim, "Clerc", old, new))
        self.assertIn(new, eng._cantrips_of(sim, "Clerc"))
        wiz = sheet("Magicien", 1, edition="2024")                  # Magicien 2024 : au repos long
        self.assertFalse(wiz.level_cantrip_swap_allowed(wiz.simulate_level_up("Magicien"), "Magicien"))

    def test_wizard_scribes_found_spell(self):
        eng = sheet("Magicien", 3)
        eng.ch.pieces["po"] = 120
        name = next(sp["nom"] for sp in eng.available_spells("Magicien") if sp["niveau"] == 2
                    and not any(s["nom"] == sp["nom"] for s in eng.ch.sorts.get("Magicien", [])))
        t0 = eng.ch.temps_minutes
        ok, msg = eng.scribe_spell(name)
        self.assertTrue(ok, msg)
        self.assertEqual(eng.ch.pieces["po"], 20)
        self.assertEqual(eng.ch.temps_minutes - t0, 240)
        other = next(sp["nom"] for sp in eng.available_spells("Magicien") if sp["niveau"] == 1
                     and not any(s["nom"] == sp["nom"] for s in eng.ch.sorts.get("Magicien", [])))
        self.assertFalse(eng.scribe_spell(other)[0])                # 20 po < 50 po
        eng.ch.pieces["po"] = 9999
        high = next(sp["nom"] for sp in DB.spells.values() if sp.get("niveau") == 9
                    and "Magicien" in sp.get("classes", []))
        self.assertFalse(eng.scribe_spell(high)[0])                 # pas d'emplacement de niveau 9 au niveau 3


class GuidedAbilitiesTests(unittest.TestCase):
    def test_no_reroll_in_guided_mode(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        win.settings["mode_libre"] = False
        win.engine.ch.methode = "des"
        win.engine.ch.des_tirages = [{"total": 12, "des": [4, 4, 4, 1]}] * 6
        win.engine.normalize()
        enabled = {}
        win.abilities_tab.roll_btn.setEnabled = lambda on: enabled.__setitem__("roll", on)
        win.abilities_tab._apply_guided_locks()
        self.assertFalse(enabled["roll"])


class GuidedLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        cls.win = MainWindow(DB)

    def setUp(self):
        self.win.settings["mode_libre"] = False
        eng = self.win.engine
        eng.ch.classes = [{"nom": "Roublard", "niveau": 1, "sous_classe": "", "pv_jets": []}]
        eng.normalize()

    def tearDown(self):
        self.win.settings["mode_libre"] = False

    def test_skills_locked_except_missing(self):
        tab = self.win.skills_tab
        names = DB.skill_names
        ch = self.win.engine.ch
        missing = self.win.engine.skills_missing()
        free = [i for i, n in enumerate(names) if not (ch.competences.get(n) or {}).get("maitrise")]
        tab._on_skill_click(free[0], 0)                            # compléter un choix manquant : permis
        self.assertEqual(bool(ch.competences[names[free[0]]]["maitrise"]), missing > 0)
        if missing > 0:
            tab._on_skill_click(free[0], 0)                        # retirer : refusé en Mode guidé
            self.assertTrue(ch.competences[names[free[0]]]["maitrise"])
        self.win.settings["mode_libre"] = True
        tab._on_skill_click(free[0], 0)
        self.assertEqual(bool(ch.competences[names[free[0]]]["maitrise"]), not missing > 0)


if __name__ == "__main__":
    unittest.main()
