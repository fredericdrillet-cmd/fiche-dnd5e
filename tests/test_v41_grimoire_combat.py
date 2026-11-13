"""Tests v41 : assistant de niveau (tours de magie / sorts séparés, filtres, préparation), tuiles du Combat en
groupes, déplacement en cases, encart Réactions retiré, Mains nues hors inventaire."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from test_v40_wizard_saves import full_spells, make  # noqa: E402
from core.levelup import SCHOOLS, filter_spells  # noqa: E402


def window(eng):
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    win = mw.MainWindow(DB)
    win.engine = eng
    win.refresh_all()
    return win


class GrimoireFilterTests(unittest.TestCase):
    def test_filters(self):
        spells = DB.all_spells()
        self.assertTrue(all(s["niveau"] == 2 for s in filter_spells(spells, 2)))
        evo = filter_spells(spells, None, "Évocation")
        self.assertTrue(evo and all(s["ecole"] == "Évocation" for s in evo))
        self.assertTrue(all(s["rituel"] for s in filter_spells(spells, rituel=True)))
        both = filter_spells(spells, rituel=True, concentration=True)
        self.assertTrue(all(s["rituel"] and s["concentration"] for s in both))
        self.assertEqual([s["nom"] for s in filter_spells(spells, texte="boule de feu")][:1], ["Boule de feu"])
        self.assertEqual(len(SCHOOLS), 8)

    def test_wizard_preparation_gauge(self):
        eng = make("Magicien", 3, "École d'Évocation")
        full_spells(eng, "Magicien")
        sim = eng.simulate_level_up("Magicien")
        info = eng.level_prepare_info(sim, "Magicien")
        self.assertFalse(info["toujours"])
        self.assertEqual(info["maximum"], sim.caster("Magicien")["prepares_max"])
        name = next(s["nom"] for s in sim.ch.sorts["Magicien"] if (DB.find_spell(s["nom"]) or {}).get("niveau"))
        was = next(s for s in sim.ch.sorts["Magicien"] if s["nom"] == name)["prepare"]
        self.assertTrue(eng.level_set_prepared(sim, "Magicien", name, not was))
        for s in sim.ch.sorts["Magicien"]:                 # au maximum : refus de préparer un sort de plus
            if (DB.find_spell(s["nom"]) or {}).get("niveau"):
                s["prepare"] = True
        extra = next((s["nom"] for s in sim.ch.sorts["Magicien"] if not s["prepare"]), None)
        if extra:
            self.assertFalse(eng.level_set_prepared(sim, "Magicien", extra, True))

    def test_cleric_prepares_from_list(self):
        eng = make("Clerc", 2, "Domaine de la Vie")
        sim = eng.simulate_level_up("Clerc")
        plan = eng.level_spell_plan(sim, "Clerc")
        self.assertTrue(eng.prepares_from_list(plan))
        opt = next(s["nom"] for s in eng.level_spell_options(sim, "Clerc") if s["niveau"] > 0)
        self.assertTrue(eng.level_learn_spell(sim, "Clerc", opt))
        self.assertEqual(eng.level_prepare_info(sim, "Clerc")["prepares"], 1)

    def test_known_casters_always_prepared(self):
        eng = make("Ensorceleur", 3, "Lignée draconique")
        full_spells(eng, "Ensorceleur")
        self.assertTrue(eng.level_prepare_info(eng.simulate_level_up("Ensorceleur"), "Ensorceleur")["toujours"])

    def test_dialog_tabs_and_filters(self):
        from ui.levelup_dialog import LevelUpDialog
        eng = make("Magicien", 3, "École d'Évocation")
        full_spells(eng, "Magicien")
        d = LevelUpDialog(window(eng))
        w = d.spell_widgets["Magicien"]
        for key in ("cnt0", "cnt1", "school1", "ritual", "conc", "lvl_btns", "prep_bar", "mine1"):
            self.assertIn(key, w)
        self.assertIn(2, w["lvl_btns"])                     # niveau 4 de magicien : sorts de niveau 1 et 2
        d._on_spell_level("Magicien", 2)
        self.assertEqual(w["filtre_niveau"], 2)


class CombatLayoutTests(unittest.TestCase):
    def test_tile_groups(self):
        eng = make("Roublard", 3, spells={})
        eng.ch.armes_cac[0] = {"nom": "Rapière", "bonus": 0, "maitrise": None}
        eng.ch.equipement.append({"nom": "Potion de guérison", "qte": 1})
        eng.ch.regles_optionnelles["potion_action_bonus"] = True       # v52 : règle de la table
        eng.normalize()
        g = {t["id"]: t["groupe"] for t in eng.turn_actions()}
        self.assertEqual(g["arme:armes_cac:0"], "attaques")
        self.assertEqual(g["classe:sournoise"], "attaques")
        self.assertEqual(g["reaction:opportunite"], "reactions")
        self.assertEqual(g["commune:foncer"], "generiques")
        self.assertEqual(g["potion:boire"], "generiques")
        self.assertEqual(g["classe:ruse_cacher"], "generiques")
        wiz = make("Magicien", 3, spells={"Magicien": ["Trait de feu", "Bouclier", "Boule de feu"]})
        g = {t["id"]: t["groupe"] for t in wiz.turn_actions()}
        self.assertEqual(g["sort:Trait de feu"], "magie")
        self.assertEqual(g["sort:Bouclier"], "reactions")

    def test_window_groups_cases_and_no_reaction_box(self):
        from ui.combat_tab import cases_text
        self.assertEqual(cases_text(9), "6 cases (9 m)")
        self.assertEqual(cases_text(1.5), "1 case (1,5 m)")
        eng = make("Guerrier", 3)
        win = window(eng)
        tab = win.combat_tab
        self.assertEqual(list(tab.turn_groups), ["attaques", "magie", "reactions", "generiques", "capacites", "objets"])
        src = (ROOT / "ui" / "combat_tab.py").read_text(encoding="utf-8")
        self.assertNotIn("react_grid", src)                 # encart « Réactions » retiré (stub : hasattr toujours vrai)
        self.assertIn("case", tab.turn_move_left.text())
        tab._on_turn_tile("reaction:opportunite")
        self.assertEqual(eng.ch.reaction_utilisee, "opportunite")

    def test_unarmed_not_in_inventory(self):
        eng = make("Moine", 3)
        eng.ch.armes_cac[0] = {"nom": "Mains nues", "bonus": 0, "maitrise": None}
        eng.ch.equipement.append({"nom": "Mains nues", "qte": 1})
        self.assertFalse(eng.ensure_in_inventory("Mains nues"))
        eng.normalize()
        self.assertFalse(any(e["nom"] == "Mains nues" for e in eng.ch.equipement))
        self.assertEqual(eng.ch.armes_cac[0]["nom"], "Mains nues")


if __name__ == "__main__":
    unittest.main()
