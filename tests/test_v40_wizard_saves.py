"""Tests v40 : assistant de niveau (nouveaux sorts, infobulles des dons, +1 à deux caractéristiques différentes),
demi-dégâts des sorts à jet de sauvegarde, réactions sans réglage, potion en action bonus."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core.data_loader import save_success_text  # noqa: E402
from core.engine import Engine  # noqa: E402


def make(cls, lvl, sub="", spells=None):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race("Humain")
    eng.ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    for c, names in (spells or {}).items():
        eng.ch.sorts[c] = [{"nom": n, "prepare": True} for n in names]
    eng.normalize()
    return eng


def full_spells(eng, cls):
    """Remplit les quotas actuels pour isoler les choix du niveau suivant."""
    plan = eng.level_spell_plan(eng, cls)
    while plan and plan["mineurs"][0] < plan["mineurs"][1]:
        eng.level_learn_spell(eng, cls, next(s["nom"] for s in eng.level_spell_options(eng, cls) if s["niveau"] == 0))
        plan = eng.level_spell_plan(eng, cls)
    quota = plan and (plan["connus"] or plan["grimoire"])
    while quota and quota[0] < quota[1]:
        eng.level_learn_spell(eng, cls, next(s["nom"] for s in eng.level_spell_options(eng, cls) if s["niveau"] > 0))
        plan = eng.level_spell_plan(eng, cls)
        quota = plan["connus"] or plan["grimoire"]


class WizardSpellTests(unittest.TestCase):
    def test_new_spells_are_wizard_choices(self):
        eng = make("Ensorceleur", 3, "Lignée draconique")
        full_spells(eng, "Ensorceleur")
        sim = eng.simulate_level_up("Ensorceleur")
        rep = eng.level_up_report(sim, "Ensorceleur")
        spells = [m for m in rep["dans_assistant"] if m["kind"] == "sorts"]
        self.assertEqual(sorted(m["message"] for m in spells),
                         ["Ensorceleur : 1 sort connu à choisir", "Ensorceleur : 1 sort mineur à choisir"])
        plan = eng.level_spell_plan(sim, "Ensorceleur")
        self.assertEqual((plan["gain_mineurs"], plan["gain_sorts"]), (1, 1))
        opts = eng.level_spell_options(sim, "Ensorceleur")
        self.assertTrue(all(s["niveau"] <= plan["niveau_max"] for s in opts))
        self.assertTrue(eng.level_learn_spell(sim, "Ensorceleur", next(s["nom"] for s in opts if s["niveau"] == 0)))
        self.assertTrue(eng.level_learn_spell(sim, "Ensorceleur", next(
            s["nom"] for s in eng.level_spell_options(sim, "Ensorceleur") if s["niveau"] > 0)))
        rep = eng.level_up_report(sim, "Ensorceleur")
        self.assertFalse([m for m in rep["dans_assistant"] if m["kind"] == "sorts"])
        self.assertFalse(eng.level_spell_options(sim, "Ensorceleur"))       # quotas atteints

    def test_wizard_spellbook_plus_two(self):
        eng = make("Magicien", 2, "École d'Évocation")
        full_spells(eng, "Magicien")
        sim = eng.simulate_level_up("Magicien")
        self.assertEqual(eng.level_spell_plan(sim, "Magicien")["grimoire"][1] -
                         eng.level_spell_plan(sim, "Magicien")["grimoire"][0], 2)

    def test_preparation_stays_in_magic_tab(self):
        eng = make("Clerc", 1, "Domaine de la Vie")
        full_spells(eng, "Clerc")
        rep = eng.level_up_report(eng.simulate_level_up("Clerc"), "Clerc")
        self.assertFalse(any("préparer" in m["message"] for m in rep["dans_assistant"]))

    def test_plus_one_two_needs_different_abilities(self):
        eng = make("Guerrier", 3, "Champion")
        sim = eng.simulate_level_up("Guerrier")
        sid = [s for s in sim.asi_slots() if s["id"] not in {x["id"] for x in eng.asi_slots()}][0]["id"]
        sim.ch.ameliorations[sid] = {"mode": "plus1x2", "a1": "Force", "a2": "Force"}
        self.assertTrue(any(m["kind"] == "amelioration" for m in eng.level_up_report(sim, "Guerrier")["dans_assistant"]))
        sim.ch.ameliorations[sid] = {"mode": "plus1x2", "a1": "Force", "a2": "Constitution"}
        self.assertFalse(any(m["kind"] == "amelioration" for m in eng.level_up_report(sim, "Guerrier")["dans_assistant"]))

    def test_dialog_steps_feat_tooltips_and_spells(self):
        import ui.main_window as mw
        from ui.levelup_dialog import STEPS, LevelUpDialog
        mw.save_settings = lambda data: None
        eng = make("Ensorceleur", 3, "Lignée draconique")
        full_spells(eng, "Ensorceleur")
        win = mw.MainWindow(DB)
        win.engine = eng
        win.refresh_all()
        d = LevelUpDialog(win)
        self.assertIn("Nouveaux sorts", STEPS)
        self.assertIn("Ensorceleur", d.spell_widgets)
        tip = d.feat_tip(next(iter(DB.feats)))
        self.assertTrue(tip)
        opt = next(s["nom"] for s in eng.level_spell_options(d.sim, "Ensorceleur") if s["niveau"] == 0)
        d._learn("Ensorceleur", opt)
        self.assertEqual(d.spell_added["Ensorceleur"], [opt])
        d._unlearn("Ensorceleur", opt)
        self.assertFalse(d.spell_added["Ensorceleur"])


class SaveSpellTests(unittest.TestCase):
    def test_half_damage_rules(self):
        for name in ("Boule de feu", "Mains brûlantes", "Éclair", "Cône de froid"):
            self.assertEqual(save_success_text(DB.find_spell(name)), "Succès = 1/2 dégâts", name)
        for name in ("Flamme sacrée", "Gelure", "Désintégration", "Catapulte"):
            self.assertEqual(save_success_text(DB.find_spell(name)), "Succès = 0 dégât", name)
        self.assertIn("Dégâts même en cas de succès", save_success_text(DB.find_spell("Châtiment courroucé")))

    def test_resolution_line_and_tile(self):
        eng = make("Magicien", 5, spells={"Magicien": ["Boule de feu"]})
        res = eng.spell_resolution("Boule de feu", 3, "Magicien")
        self.assertEqual(res["ligne_js"], "Jet de sauvegarde de Dextérité : DD {}".format(eng.caster("Magicien")["dc"]))
        self.assertEqual(res["succes"], "moitie")
        tile = next(t for t in eng.turn_actions() if t["id"] == "sort:Boule de feu")
        self.assertIn("Succès = 1/2 dégâts", tile["description"])
        self.assertIn("Jet de sauvegarde de Dextérité", tile["description"])


class ReactionAndPotionTests(unittest.TestCase):
    def test_reactions_are_plain_tiles(self):
        eng = make("Magicien", 3, spells={"Magicien": ["Bouclier"]})
        self.assertFalse(eng.reaction_programmable("sort:Bouclier"))
        eng.set_reaction_mode("sort:Bouclier", "off")
        self.assertEqual(eng.reaction_mode("sort:Bouclier"), "demander")
        self.assertIsNone(eng.auto_reaction())
        tile = next(t for t in eng.turn_actions() if t["id"] == "sort:Bouclier")
        self.assertEqual(tile["type"], "Réaction")

    def test_potion_bonus_action(self):
        eng = make("Guerrier", 3)
        tile = next(t for t in eng.turn_actions() if t["id"] == "potion:boire")
        self.assertFalse(tile["disponible"])
        eng.ch.equipement.append({"nom": "Potion de guérison", "qte": 2})
        tile = next(t for t in eng.turn_actions() if t["id"] == "potion:boire")
        self.assertEqual((tile["type"], tile["disponible"]), ("Action bonus", True))
        res = eng.use_turn_action("potion:boire")
        self.assertTrue(res["potion"] and eng.ch.tour_bonus)
        self.assertFalse(eng.ch.tour_action)
        objet = next(t for t in eng.turn_actions() if t["id"] == "commune:objet")
        self.assertEqual(objet["type"], "Action")
        self.assertIn("allié", objet["description"])


if __name__ == "__main__":
    unittest.main()
