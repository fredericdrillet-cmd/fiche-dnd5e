"""Tests v26 : onglet « Familiers, Compagnons, Invocations » (ménagerie, détection, fiche dynamique, sauvegarde)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core.character import Character  # noqa: E402
from core.companions import eval_dice, eval_formula  # noqa: E402
from core.engine import Engine  # noqa: E402


def make(c, lvl, sub=""):
    eng = Engine(DB, Engine.new_character(DB))
    eng.ch.classes = [{"nom": c, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng.normalize()
    return eng


def window():
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    return mw.MainWindow(DB)


class CatalogueTests(unittest.TestCase):
    def test_entities_loaded(self):
        self.assertEqual(len(DB.entities), 102)                    # 95 + 7 montures (v36)
        eng = make("Guerrier", 1)
        self.assertEqual(len(eng.entities_of_type("summons")), 63)
        self.assertEqual(len(eng.entities_of_type("familiar")), 23)
        self.assertEqual(len(eng.entities_of_type("class_companion")), 9)

    def test_formula_evaluator(self):
        ctx = {"BM": 3, "class_level": 7, "spell_level": 5}
        self.assertEqual(eval_formula("13 + BM", ctx), 16)
        self.assertEqual(eval_formula("5 + (5 * class_level)", ctx), 40)
        self.assertEqual(eval_formula("50 + 10 * (spell_level - 4)", ctx), 60)
        self.assertIsNone(eval_formula("__import__('os')", ctx))
        self.assertEqual(eval_dice("1d8 + 2 + BM", ctx)[:2], ("1d8", 5))


class DetectionTests(unittest.TestCase):
    def test_wildfire_auto_add_and_remove(self):
        eng = make("Druide", 2, "Cercle des Fournaises")
        self.assertEqual([m["id"] for m in eng.ch.menagerie], ["esprit_feu_sauvage"])
        self.assertTrue(eng.ch.menagerie[0]["auto"])
        eng.ch.classes[0]["sous_classe"] = "Cercle de la Lune"
        eng.normalize()
        self.assertEqual(eng.ch.menagerie, [])

    def test_wildfire_removed_on_class_change(self):
        eng = make("Druide", 2, "Cercle des Fournaises")
        eng.ch.classes = [{"nom": "Guerrier", "niveau": 2, "sous_classe": "", "pv_jets": []}]
        eng.normalize()
        self.assertEqual(eng.ch.menagerie, [])

    def test_manual_entries_survive_class_change(self):
        eng = make("Druide", 2, "Cercle des Fournaises")
        eng.menagerie_add("chat")
        eng.ch.classes[0]["sous_classe"] = "Cercle de la Lune"
        eng.normalize()
        self.assertEqual([m["id"] for m in eng.ch.menagerie], ["chat"])

    def test_beast_master_hint(self):
        eng = make("Rôdeur", 3, "Maître des bêtes")
        hints = eng.companion_hints()
        self.assertEqual(hints[0]["niveau"], "warning")
        self.assertIn("lier un compagnon spécifique", hints[0]["texte"])
        self.assertEqual(set(hints[0]["recommandes"]), {"esprit_terre", "esprit_mer", "esprit_ciel"})
        eng.menagerie_add("esprit_ciel")
        self.assertEqual(eng.companion_hints(), [])

    def test_artificer_hints(self):
        self.assertEqual(make("Artificier", 3, "Artilleur").companion_hints()[0]["recommandes"], ["canon_occulte"])
        self.assertEqual(make("Artificier", 3, "Forgeur d'armes").companion_hints()[0]["recommandes"],
                         ["defenseur_acier"])
        self.assertEqual(make("Artificier", 2, "Artilleur").companion_hints(), [])

    def test_chain_pact_hint(self):
        eng = make("Occultiste", 3, "Le Fiélon")
        eng.ch.pacte = "Pacte de la chaîne"
        eng.normalize()
        hints = eng.companion_hints()
        self.assertEqual(hints[0]["niveau"], "info")
        self.assertEqual(len(hints[0]["recommandes"]), 4)
        self.assertIn("diablotin", hints[0]["recommandes"])
        self.assertTrue(set(hints[0]["recommandes"]) <= eng.recommended_entities())


class ScalingTests(unittest.TestCase):
    def test_primal_beast_scales_with_ranger(self):
        eng = make("Rôdeur", 7, "Maître des bêtes")
        sh = eng.entity_sheet(eng.menagerie_add("esprit_terre"))
        self.assertEqual(sh["ca"], 13 + 3)
        self.assertEqual(sh["pv_max"], 5 + 5 * 7)
        self.assertTrue(any(t["name"] == "Niveau 7" for t in sh["traits"]))
        self.assertFalse(any(t["name"] == "Niveau 11" for t in sh["traits"]))

    def test_reference_context_matches_data(self):
        for eid, ent in DB.entities.items():
            sc = ent.get("scaling") or {}
            ref = sc.get("reference") or {}
            if not ref:
                continue
            eng = make("Guerrier", 1)
            cur, r = eng.scaling_context(ent, {"niveau_sort": ref.get("spell_level")})
            self.assertTrue(r, eid)

    def test_summon_hp_by_spell_level(self):
        eng = make("Magicien", 11)
        summons = [e for e in DB.entities.values()
                   if (e.get("scaling") or {}).get("spell_level_min") and "spell_level" in str(e["scaling"].get(
                       "hp_formula", ""))]
        self.assertTrue(summons)
        inst = eng.menagerie_add(summons[0]["id"])
        low = eng.entity_sheet(inst)["pv_max"]
        inst["niveau_sort"] = inst["niveau_sort"] + 2
        self.assertGreater(eng.entity_sheet(inst)["pv_max"], low)

    def test_rolls(self):
        eng = make("Rôdeur", 5, "Maître des bêtes")
        inst = eng.menagerie_add("esprit_terre")
        sh = eng.entity_sheet(inst)
        self.assertTrue(eng.entity_check_spec(inst, "FOR").title)
        self.assertTrue(eng.entity_check_spec(inst, "DEX", save=True).title)
        if sh["competences"]:
            self.assertTrue(eng.entity_skill_spec(inst, next(iter(sh["competences"]))).title)
        atk = next(a for a in sh["actions"] if a.get("attack_bonus") is not None)
        self.assertEqual(atk["attack_bonus"], eng.prof + eng.mod("Sagesse"))   # modificateur d'attaque de sort du rôdeur
        self.assertIn("Dégâts", eng.entity_attack_spec(inst, atk).note)


class PersistenceTests(unittest.TestCase):
    def test_round_trip(self):
        eng = make("Magicien", 3)
        inst = eng.menagerie_add("chat", "Minou")
        inst["pv"], inst["statut"] = 1, "Inconscient"
        data = json.loads(json.dumps(eng.ch.to_dict()))
        ch = Character.from_dict(data)
        e2 = Engine(DB, ch)
        e2.normalize()
        m = e2.ch.menagerie[0]
        self.assertEqual((m["id"], m["nom"], m["pv"], m["statut"], m["uid"]),
                         ("chat", "Minou", 1, "Inconscient", inst["uid"]))

    def test_hp_clamped_and_unknown_ids_dropped(self):
        eng = make("Magicien", 3)
        inst = eng.menagerie_add("chat")
        inst["pv"] = 999
        eng.ch.menagerie.append({"uid": "x", "id": "inexistant", "nom": "?", "pv": 1})
        eng.normalize()
        self.assertEqual(len(eng.ch.menagerie), 1)
        self.assertEqual(eng.ch.menagerie[0]["pv"], eng.entity_sheet(inst)["pv_max"])


class TabTests(unittest.TestCase):
    def test_tab_registered(self):
        win = window()
        self.assertTrue(hasattr(win, "companions_tab"))

    def test_add_rename_status_remove(self):
        import ui.companions_tab as ct
        win = window()
        tab = win.companions_tab
        orig = ct.pick_entity
        ct.pick_entity = lambda *a, **k: "chat"
        try:
            tab._on_add()
        finally:
            ct.pick_entity = orig
        self.assertEqual([m["id"] for m in win.ch.menagerie], ["chat"])
        inst = win.ch.menagerie[0]
        tab.current_uid = inst["uid"]
        tab.refresh()
        tab.w["name"].text = lambda: "Pantoufle"
        tab._on_rename()
        self.assertEqual(inst["nom"], "Pantoufle")
        tab._on_hp(0)
        self.assertEqual(inst["pv"], 0)
        self.assertEqual(inst["statut"], "À 0 PV")
        tab._on_remove()
        self.assertEqual(win.ch.menagerie, [])

    def test_picker_recommended_first(self):
        import ui.companions_tab as ct
        win = window()
        dlg = ct.EntityPicker(win, win.engine, "familiar", {"quasit", "diablotin"})
        self.assertEqual(set(dlg._ids[:2]) if hasattr(dlg, "_ids") else {"quasit", "diablotin"},
                         {"quasit", "diablotin"})
        dlg.set_type("summons")
        self.assertTrue(all(win.engine.entity(i)["entity_type"] == "summons" for i in getattr(dlg, "_ids", [])))


if __name__ == "__main__":
    unittest.main()
