"""Tests v6 : compétences cliquables, sorts raciaux, encombrement, forme sauvage, formules, onglets déplaçables,
objets à paliers, libellés d'amélioration, textes de classe et audit."""
import importlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests"), str(ROOT / "tools")]
import qt_stub  # noqa: E402

qt_stub.install()

from core import rules as R  # noqa: E402
from core.formulas import FormulaContext, annotate  # noqa: E402
from test_v5_features import DB, make  # noqa: E402


class DataTests(unittest.TestCase):
    def test_asi_label_renamed_everywhere(self):
        for f in (ROOT / "data").glob("*.json"):
            try:
                raw = json.loads(f.read_text(encoding="utf-8-sig"))
            except ValueError:                                  # fichiers « tolérés » (réparés au chargement)
                continue
            if not isinstance(raw, dict) or "classe" not in raw:
                continue
            names = [x["nom"] for x in raw["classe"]["capacites_classe"] if R.is_asi_feature(x["nom"])]
            self.assertTrue(names, f.name)
            self.assertEqual(set(names), {"Amélioration de caractéristique ou choix d'un don"}, f.name)
        eng = make([("Guerrier", 8, "")])
        self.assertEqual(len(eng.asi_slots()), 3)                # 4, 6, 8 : toujours détectés

    def test_class_texts_match_data(self):
        apply = importlib.import_module("apply_class_texts")
        for mod in apply.modules([]):
            self.assertEqual(apply.apply(mod, write=False), [], mod.CLASSE)

    def test_tiered_items_split(self):
        names = {o["nom"] for o in DB.magic_items.values()} if isinstance(DB.magic_items, dict) else set()
        for n in ("Potion de guérison", "Potion de guérison suprême", "Ceinturon de force de géant des tempêtes",
                  "Parchemin de sort (niveau 9)", "Arme +3"):
            self.assertIn(n, names)
        self.assertFalse(any("+1, +2 ou +3" in n for n in names))

    def test_audit_modules_wellformed(self):
        for mod in importlib.import_module("apply_class_texts").modules([]):
            for entry in mod.AUDIT:
                self.assertEqual(len(entry), 4)
                self.assertIn(entry[0], ("majeur", "mineur", "info"))
        for mod in importlib.import_module("apply_corrections").iter_modules("race_fixes"):
            self.assertTrue(mod.FIXES)
            for entry in mod.AUDIT + mod.CORRIGE:
                self.assertIn(entry[0], ("majeur", "mineur", "info"))


class FormulaTests(unittest.TestCase):
    ctx = FormulaContext(mods={"Constitution": 3, "Sagesse": 2, "Force": -1}, prof=3,
                         levels={"Guerrier": 5, "Magicien": 5}, current_class="Guerrier")

    def test_chain_with_dice(self):
        self.assertEqual(annotate("1d10 + votre modificateur de Constitution", self.ctx),
                         "1d10 + 3 (mod. Constitution)")

    def test_chain_total_and_negative(self):
        self.assertIn("= 14", annotate("DD = 8 + votre bonus de maîtrise + votre modificateur de Constitution", self.ctx))
        self.assertIn("1d8 - 1 (mod. Force)", annotate("1d8 + votre modificateur de Force", self.ctx))

    def test_isolated_and_half_levels(self):
        self.assertIn("(+2)", annotate("égal à votre modificateur de Sagesse.", self.ctx))
        self.assertIn("(2)", annotate("la moitié de votre niveau de guerrier.", self.ctx))
        self.assertIn("(3)", annotate("la moitié (arrondie au supérieur) de votre niveau de magicien.", self.ctx))

    def test_unknown_class_left_untouched(self):
        self.assertEqual(annotate("votre niveau de paladin", self.ctx), "votre niveau de paladin")


class EngineTests(unittest.TestCase):
    def test_racial_spells_for_non_caster(self):
        eng = make([("Guerrier", 3, "")])
        eng.ch.race = "Tieffelin"
        eng.normalize()
        spells = {s["nom"]: s for s in eng.racial_spells()}
        self.assertIn("Thaumaturgie", spells)
        self.assertEqual(spells["Thaumaturgie"]["carac"], "Charisme")
        self.assertIn("Thaumaturgie", eng.available_cantrips())
        self.assertNotIn("Boule de feu", eng.available_cantrips())

    def test_encumbrance_and_bag(self):
        eng = make([("Guerrier", 1, "")], Force=10)
        enc = eng.encumbrance()
        self.assertEqual(enc["capacite"], 75.0)
        eng.ch.sac_sans_fond = True
        eng.normalize()
        self.assertEqual(eng.encumbrance()["etat"], "sac")

    def test_wild_shape_rules(self):
        self.assertFalse(R.wild_shape_limits(1, False)["actif"])
        w2, w4, w8 = (R.wild_shape_limits(n, False) for n in (2, 4, 8))
        self.assertEqual((w2["fp_max"], w2["nage"], w2["vol"]), (0.25, False, False))
        self.assertEqual((w4["fp_max"], w4["nage"], w4["vol"]), (0.5, True, False))
        self.assertEqual((w8["fp_max"], w8["vol"]), (1, True))
        self.assertEqual(R.wild_shape_limits(2, True)["fp_max"], 1)
        self.assertEqual(R.wild_shape_limits(9, True)["fp_max"], 3)
        eng = make([("Druide", 2, "")])
        allowed = eng.allowed_beasts()
        self.assertTrue(allowed)
        self.assertTrue(all(b["fp"] <= 0.25 and not b["vol"] and not b["nage"] for b in allowed))
        self.assertTrue(eng.assume_form(allowed[0]["nom"]))
        self.assertEqual(eng.resource_used("forme"), 1)

    def test_pancratiaste_unarmed_and_guard(self):
        eng = make([("Guerrier", 3, "Pancratiaste")])
        self.assertEqual(eng.unarmed_die()[0], 6)
        eng = make([("Guerrier", 10, "Pancratiaste")], Constitution=16, **{"Dextérité": 14})
        self.assertEqual(eng.unarmed_die()[0], 8)
        ac = eng.armor_class_detail()
        self.assertEqual((ac["valeur"], ac["note"]), (15, "Garde de pugiliste"))


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ui.main_window as mw
        mw.save_settings = lambda data: None                   # pas d'écriture dans le dossier utilisateur
        cls.win = mw.MainWindow(DB)

    def test_skill_row_click_toggles(self):
        win = self.win
        name = DB.skill_names[0]
        before = win.ch.competences.get(name, {}).get("maitrise", False)
        win.skills_tab._on_skill_click(0, 2)                   # clic sur le nom / la carac : bascule la maîtrise
        self.assertNotEqual(win.ch.competences[name]["maitrise"], before)

    def test_druid_tab_only_for_druids_and_order_saved(self):
        win = self.win
        win.ch.classes = [{"nom": "Guerrier", "niveau": 1, "sous_classe": "", "pv_jets": []}]
        win.changed()
        self.assertNotIn("druide", win.shown_keys())
        win.ch.classes = [{"nom": "Druide", "niveau": 4, "sous_classe": "", "pv_jets": []}]
        win.changed()
        self.assertIn("druide", win.shown_keys())
        win.druid_tab.refresh()
        win._on_tab_moved()
        self.assertEqual([k for k in win.settings["ordre_onglets"] if k in win._current_keys()], win._current_keys())
        win.reset_tab_order()
        self.assertEqual(win.settings["ordre_onglets"], [])


if __name__ == "__main__":
    unittest.main()
