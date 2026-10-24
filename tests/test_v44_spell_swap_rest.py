"""Tests v44 : échange d'un sort connu à la montée de niveau (1 au maximum, écoles imposées du Chevalier occulte /
de l'Arnaqueur arcanique, emplacement libre), préparation des sorts et échange de tour de magie au repos long."""
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
from core.spell_swap import SWAP_CLASSES  # noqa: E402

KNIGHT = ("Abjuration", "Évocation")


def ready(cls, lvl, sub=""):
    eng = make(cls, lvl, sub)
    full_spells(eng, cls)
    return eng, eng.simulate_level_up(cls)


class LevelSwapTests(unittest.TestCase):
    def test_known_casters_only(self):
        self.assertEqual(set(SWAP_CLASSES), {"Barde", "Ensorceleur", "Occultiste", "Rôdeur", "Guerrier", "Roublard"})
        eng, sim = ready("Barde", 3, "Collège du Savoir")
        self.assertTrue(eng.level_swap_allowed(sim, "Barde"))
        mage = make("Magicien", 3)
        self.assertFalse(mage.level_swap_allowed(mage.simulate_level_up("Magicien"), "Magicien"))
        cleric = make("Clerc", 3, "Domaine de la Vie")
        self.assertFalse(cleric.level_swap_allowed(cleric.simulate_level_up("Clerc"), "Clerc"))

    def test_forget_then_replace_one_max(self):
        eng, sim = ready("Ensorceleur", 4, "Lignée draconique")
        cands = [s["nom"] for s in eng.level_swap_candidates(sim, "Ensorceleur")]
        self.assertTrue(cands)
        self.assertEqual(eng.level_swap_options(sim, "Ensorceleur"), [])          # étape 2 verrouillée
        count = sim.spell_counts("Ensorceleur")["sorts"]
        self.assertTrue(eng.level_swap_forget(sim, "Ensorceleur", cands[0]))
        self.assertNotIn(cands[0], [s["nom"] for s in sim.ch.sorts["Ensorceleur"]])
        self.assertEqual(sim.spell_counts("Ensorceleur")["sorts"], count)       # la place reste réservée
        pending = [m for m in eng.level_up_report(sim, "Ensorceleur")["dans_assistant"] if m.get("echange")]
        self.assertEqual(len(pending), 1)                                       # « Confirmer » bloqué
        opts = eng.level_swap_options(sim, "Ensorceleur")
        self.assertTrue(opts and all(o["niveau"] > 0 and o["nom"] != cands[0] for o in opts))
        self.assertTrue(eng.level_swap_choose(sim, "Ensorceleur", opts[0]["nom"]))
        self.assertFalse([m for m in eng.level_up_report(sim, "Ensorceleur")["dans_assistant"] if m.get("echange")])
        self.assertEqual(eng.level_swap_options(sim, "Ensorceleur"), [])          # un seul échange par niveau
        self.assertTrue(eng.level_swap_forget(sim, "Ensorceleur", cands[1]))     # autre choix : 1er échange annulé
        names = [s["nom"] for s in sim.ch.sorts["Ensorceleur"]]
        self.assertIn(cands[0], names)
        self.assertNotIn(opts[0]["nom"], names)
        self.assertNotIn(cands[1], names)
        self.assertTrue(eng.level_swap_cancel(sim, "Ensorceleur"))
        self.assertIn(cands[1], [s["nom"] for s in sim.ch.sorts["Ensorceleur"]])

    def test_new_spells_of_this_level_cannot_be_forgotten(self):
        eng, sim = ready("Barde", 3, "Collège du Savoir")
        new = next(s["nom"] for s in eng.level_spell_options(sim, "Barde") if s["niveau"] > 0)
        eng.level_learn_spell(sim, "Barde", new)
        self.assertNotIn(new, [s["nom"] for s in eng.level_swap_candidates(sim, "Barde")])

    def test_eldritch_knight_schools(self):
        eng, sim = ready("Guerrier", 4, "Chevalier occulte")
        cands = eng.level_swap_candidates(sim, "Guerrier")
        inside = next(s["nom"] for s in cands if s.get("ecole") in KNIGHT)
        eng.level_swap_forget(sim, "Guerrier", inside)
        self.assertEqual({o["ecole"] for o in eng.level_swap_options(sim, "Guerrier")} - set(KNIGHT), set())
        self.assertFalse(eng.level_swap_state(sim, "Guerrier")["libre"])
        off = next(s["nom"] for s in cands if s.get("ecole") not in KNIGHT)      # sort de l'emplacement libre
        eng.level_swap_forget(sim, "Guerrier", off)
        self.assertTrue(eng.level_swap_state(sim, "Guerrier")["libre"])
        self.assertTrue({o["ecole"] for o in eng.level_swap_options(sim, "Guerrier")} - set(KNIGHT))
        self.assertIn("Abjuration", eng.level_swap_rule(sim, "Guerrier").replace("abjuration", "Abjuration"))

    def test_arcane_trickster_schools(self):
        eng, sim = ready("Roublard", 4, "Arnaqueur arcanique")
        cands = eng.level_swap_candidates(sim, "Roublard")
        self.assertNotIn("Main de mage", [s["nom"] for s in cands])               # sort mineur accordé
        inside = next(s["nom"] for s in cands if s.get("ecole") in ("Enchantement", "Illusion"))
        eng.level_swap_forget(sim, "Roublard", inside)
        self.assertEqual({o["ecole"] for o in eng.level_swap_options(sim, "Roublard")}, {"Enchantement", "Illusion"})

    def test_wizard_dialog_swap_card(self):
        from ui.levelup_dialog import LevelUpDialog
        win = window(ready("Barde", 3, "Collège du Savoir")[0])
        dlg = LevelUpDialog(win)
        self.assertIn("Barde", dlg.swap_widgets)
        old = dlg.swap_widgets["Barde"]["names"][0]
        self.assertTrue(dlg.swap_forget("Barde", old))
        self.assertTrue(any(m.get("echange") for m in dlg.pending()))
        self.assertIn("⚠", dlg.swap_widgets["Barde"]["summary"].text())
        new = dlg.engine.level_swap_options(dlg.sim, "Barde")[0]["nom"]
        self.assertTrue(dlg.swap_choose("Barde", new))
        self.assertIn("✔ Échange : {} → {}".format(old, new), dlg.swap_widgets["Barde"]["summary"].text())
        self.assertFalse(any(m.get("echange") for m in dlg.pending()))
        self.assertTrue(dlg.swap_cancel("Barde"))
        self.assertIn(old, [s["nom"] for s in dlg.sim.ch.sorts["Barde"]])


class LongRestSpellTests(unittest.TestCase):
    def test_prepare_info_and_quota(self):
        eng = make("Clerc", 5, "Domaine de la Vie")
        info = eng.rest_prepare_info("Clerc")
        self.assertEqual(info["maximum"], eng.caster("Clerc")["prepares_max"])
        self.assertIn("niveau de Clerc", info["formule"])
        self.assertTrue(info["toujours"])                                        # sorts de domaine hors quota
        self.assertFalse(set(info["toujours"]) & {sp["nom"] for sp in info["candidats"]})
        names = [sp["nom"] for sp in info["candidats"]]
        too_many = names[:info["maximum"] + 1]
        self.assertFalse(eng.rest_set_prepared("Clerc", too_many)[0])
        ok, _msg = eng.rest_set_prepared("Clerc", names[:info["maximum"]])
        self.assertTrue(ok)
        self.assertEqual(sorted(eng.rest_prepare_info("Clerc")["prepares"]), sorted(names[:info["maximum"]]))
        eng.rest_set_prepared("Clerc", names[:1])                                 # changement le lendemain
        self.assertEqual(eng.rest_prepare_info("Clerc")["prepares"], names[:1])

    def test_classes_with_buttons(self):
        self.assertEqual(make("Druide", 2).rest_prepare_classes(), ["Druide"])
        self.assertEqual(make("Paladin", 2).rest_prepare_classes(), ["Paladin"])
        self.assertEqual(make("Barde", 2).rest_prepare_classes(), [])
        self.assertEqual(make("Paladin", 1).rest_prepare_classes(), [])           # pas encore de sorts

    def test_wizard_prepares_from_spellbook(self):
        eng = make("Magicien", 3, "", {"Magicien": ["Lumière", "Main de mage", "Trait de feu",
                                                    "Projectile magique", "Bouclier", "Armure de mage"]})
        info = eng.rest_prepare_info("Magicien")
        self.assertEqual({sp["nom"] for sp in info["candidats"]}, {"Projectile magique", "Bouclier", "Armure de mage"})

    def test_wizard_cantrip_formulas(self):
        eng = make("Magicien", 3, "", {"Magicien": ["Lumière", "Main de mage", "Trait de feu"]})
        self.assertTrue(eng.cantrip_swap_available())
        opts = [sp["nom"] for sp in eng.cantrip_swap_options()]
        self.assertNotIn("Lumière", opts)
        self.assertFalse(eng.swap_cantrip("Lumière", "Lumière")[0])
        ok, msg = eng.swap_cantrip("Lumière", opts[0])
        self.assertTrue(ok)
        names = [s["nom"] for s in eng.ch.sorts["Magicien"]]
        self.assertIn(opts[0], names)
        self.assertNotIn("Lumière", names)
        self.assertFalse(make("Clerc", 3).cantrip_swap_available())

    def test_rest_dialog_buttons_apply_on_rest(self):
        from ui.rest_dialog import RestDialog
        win = window(make("Clerc", 3, "Domaine de la Vie"))
        dlg = RestDialog(win, "long")
        self.assertIn("Clerc", dlg.prep_labels)
        info = win.engine.rest_prepare_info("Clerc")
        pick = [sp["nom"] for sp in info["candidats"]][:info["maximum"]]
        self.assertFalse(dlg.set_prepared_choice("Clerc", pick + ["x"] * 10))
        self.assertTrue(dlg.set_prepared_choice("Clerc", pick))
        self.assertIn("modifié", dlg.prep_labels["Clerc"].text())
        self.assertEqual(win.engine.rest_prepare_info("Clerc")["prepares"], [])   # rien avant « Se reposer »
        dlg.apply()
        self.assertEqual(sorted(win.engine.rest_prepare_info("Clerc")["prepares"]), sorted(pick))

    def test_rest_dialog_cantrip(self):
        from ui.rest_dialog import RestDialog
        win = window(make("Magicien", 3, "", {"Magicien": ["Lumière", "Main de mage", "Trait de feu"]}))
        dlg = RestDialog(win, "long")
        self.assertIsNotNone(dlg.cantrip_label)
        new = win.engine.cantrip_swap_options()[0]["nom"]
        self.assertTrue(dlg.set_cantrip_choice("Lumière", new))
        dlg.apply()
        self.assertIn(new, [s["nom"] for s in win.engine.ch.sorts["Magicien"]])
        fighter = window(make("Guerrier", 3))
        plain = RestDialog(fighter, "long")
        self.assertEqual(plain.prep_labels, {})
        self.assertIsNone(plain.cantrip_label)

    def test_prepare_modal_limits(self):
        from ui.spell_rest_dialogs import CantripSwapDialog, PrepareSpellsDialog
        eng = make("Clerc", 3, "Domaine de la Vie")
        info = eng.rest_prepare_info("Clerc")
        dlg = PrepareSpellsDialog(None, info, [])
        names = [sp["nom"] for sp in info["candidats"]]
        for n in names[:info["maximum"]]:
            self.assertTrue(dlg.toggle(n, True))
        self.assertFalse(dlg.toggle(names[info["maximum"]], True))               # quota atteint
        self.assertIn("Limite atteinte", dlg.warn.text())
        self.assertTrue(dlg.toggle(names[0], False))
        self.assertEqual(len(dlg.selected), info["maximum"] - 1)
        self.assertIn("Préparés : {} / {}".format(info["maximum"] - 1, info["maximum"]), dlg.count.text())
        w = make("Magicien", 3, "", {"Magicien": ["Lumière", "Main de mage", "Trait de feu"]})
        c = CantripSwapDialog(None, w.cantrip_swap_known(), w.cantrip_swap_options())
        self.assertIsNone(c.choice())
        self.assertTrue(c.set_old("Lumière"))
        self.assertFalse(c.set_new("Lumière"))                                   # déjà connu
        new = w.cantrip_swap_options()[0]["nom"]
        self.assertTrue(c.set_new(new))
        self.assertEqual(c.choice(), ("Lumière", new))


if __name__ == "__main__":
    unittest.main()
