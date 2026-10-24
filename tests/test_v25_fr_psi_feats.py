"""Tests v25 : francisation, dés psioniques (Lame psychique), Humain / Humain variant, dons accordés par le MJ."""
import glob
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core import dice as D  # noqa: E402
from core.engine import Engine  # noqa: E402

ENGLISH = ("Soulknife", "Swashbuckler", "Mastermind", "Inquisitive", "Phantom", "(Scout)", "Wildfire", "Deep Speech",
           "Undercommon", "Homebrew", "(SCAG)", "Flourish", "(construct)")


def make(c, lvl, sub="", race="Humain"):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race(race)
    eng.ch.classes = [{"nom": c, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng.normalize()
    return eng


class FrenchTests(unittest.TestCase):
    def test_no_english_in_data(self):
        from core.data_loader import read_json
        for path in glob.glob(str(ROOT / "data" / "*.json")):
            if "monsters_db" in path:
                continue
            data, _ = read_json(Path(path))
            text = json.dumps(strip_en(data), ensure_ascii=False)      # « nom_en » : référence VO interne
            for word in ENGLISH:
                self.assertNotIn(word, text, (Path(path).name, word))

    def test_no_english_in_ui_code(self):
        for path in glob.glob(str(ROOT / "ui" / "*.py")) + [str(ROOT / "core" / "weapon_actions.py")]:
            src = Path(path).read_text(encoding="utf-8")
            for word in ("Flourish", "Soulknife", "Swashbuckler"):
                self.assertNotIn(word, src, (path, word))

    def test_subclass_names(self):
        rogue = {s["nom"] for s in DB.classes["Roublard"]["sous_classes"]}
        self.assertTrue({"Lame psychique", "Bretteur", "Conspirateur", "Éclaireur", "Enquêteur", "Fantôme"} <= rogue)
        self.assertIn("Soldat psi", {s["nom"] for s in DB.classes["Guerrier"]["sous_classes"]})

    def test_old_save_migrated(self):
        from core.character import Character
        ch = Character.from_dict({"classes": [{"nom": "Roublard", "niveau": 5,
                                               "sous_classe": "Lame psychique / Soulknife"}],
                                  "langues_liste": ["Commun", "Profonde Parler (Deep Speech)"]})
        Engine(DB, ch).normalize()
        self.assertEqual(ch.classes[0]["sous_classe"], "Lame psychique")
        self.assertIn("Profond", ch.langues_liste)

    def test_francisation_idempotent(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import francisation
        self.assertEqual(francisation.apply(write=False), {})


def strip_en(node):
    if isinstance(node, dict):
        return {k: strip_en(v) for k, v in node.items() if k not in ("nom_en", "name_en")}
    if isinstance(node, list):
        return [strip_en(v) for v in node]
    return node


class PsionicTests(unittest.TestCase):
    def test_pool_and_die(self):
        for lvl, total, die in ((3, 4, "d6"), (5, 6, "d8"), (11, 8, "d10"), (17, 12, "d12")):
            eng = make("Roublard", lvl, "Lame psychique")
            tr = {t["key"]: t for t in eng.resource_trackers("combat")}["psionique"]
            self.assertEqual((tr["total"], tr["de"]), (total, die), lvl)
        self.assertNotIn("psionique", {t["key"] for t in make("Roublard", 5, "Voleur").resource_trackers()})

    def test_actions_spend_and_lock(self):
        eng = make("Roublard", 9, "Lame psychique")
        ids = [a["id"] for a in eng.class_actions()]
        for aid in ("lame_psy", "savoir_faire", "murmures", "teleport_psy", "frappes_autoguidees", "recup_psi"):
            self.assertIn(aid, ids)
        self.assertNotIn("voile_psy", ids)                    # niveau 13
        total = {t["key"]: t for t in eng.resource_trackers()}["psionique"]["total"]
        self.assertTrue(eng.use_class_action("murmures")["ok"])                # 1re utilisation gratuite
        self.assertEqual(eng.resource_used("psionique"), 0)
        for _ in range(total):
            res = eng.use_class_action("teleport_psy")
            self.assertTrue(res["ok"])
            self.assertEqual(res["degats"].formula, "1d8")
        a = next(x for x in eng.class_actions() if x["id"] == "teleport_psy")
        self.assertFalse(a["disponible"])
        self.assertIn("épuisés", a["raison"])
        self.assertTrue(eng.use_class_action("recup_psi")["ok"])               # récupère un dé
        self.assertEqual(eng.resource_used("psionique"), total - 1)
        self.assertFalse(next(x for x in eng.class_actions() if x["id"] == "recup_psi")["disponible"])
        eng.short_rest()
        self.assertTrue(next(x for x in eng.class_actions() if x["id"] == "recup_psi")["disponible"])

    def test_spend_only_on_success_ui(self):
        import ui.combat_tab as ct
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.classes = [{"nom": "Roublard", "niveau": 3, "sous_classe": "Lame psychique", "pv_jets": []}]
        win.changed()
        saved = (ct.roll_damage_dialog, ct.ask_yes_no)
        self.addCleanup(lambda: (setattr(ct, "roll_damage_dialog", saved[0]), setattr(ct, "ask_yes_no", saved[1])))
        ct.roll_damage_dialog = lambda w, spec: D.DamageResult([(6, 4, 1)], 0, 4)
        ct.ask_yes_no = lambda *a, **k: False
        win.combat_tab._on_action("savoir_faire")
        self.assertEqual(win.engine.resource_used("psionique"), 0)            # échec : dé conservé
        ct.ask_yes_no = lambda *a, **k: True
        win.combat_tab._on_action("savoir_faire")
        self.assertEqual(win.engine.resource_used("psionique"), 1)
        self.assertIn("psionique", [w["key"] for w in win.combat_tab.res_rows])


class HumanTests(unittest.TestCase):
    def test_variant_human(self):
        eng = make("Guerrier", 1, race="Humain variant")
        rule = eng.race_rule()
        self.assertEqual((rule["fixe"], rule["libres"]), ({}, [1, 1]))
        self.assertTrue(eng.race_grants_feat())
        self.assertEqual(eng.asi_slots()[0]["id"], "race|don")
        eng.ch.bonus_libres = ["Force", "Force"]              # même caractéristique deux fois : refusé
        eng.normalize()
        self.assertEqual(eng.race_bonus()["Force"], 1)
        eng.ch.ameliorations["race|don"]["don"] = "Alerte"
        eng.normalize()
        self.assertIn("Alerte", eng.chosen_feats())
        eng.change_race("Humain")
        self.assertNotIn("race|don", [s["id"] for s in eng.asi_slots()])
        self.assertEqual({v for v in eng.race_bonus().values()}, {1})

    def test_trait_panel_reset(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.engine.change_race("Drow (Elfe noir)")
        win.changed()
        win.race_tab.refresh()
        win.engine.change_race("Humain")
        win.changed()
        win.race_tab.refresh()
        self.assertTrue(win.race_tab._traits)
        self.assertTrue(all("Drow" not in t["nom"] and "soleil" not in t["nom"].lower() for t in win.race_tab._traits))


class GmFeatTests(unittest.TestCase):
    def test_gm_feat_bonuses(self):
        eng = make("Guerrier", 1)
        feat = next(n for n, f in DB.feats.items() if f.get("effets", {}).get("initiative"))
        before = eng.feat_effect("initiative")
        self.assertTrue(eng.add_gm_feat(feat))
        self.assertFalse(eng.add_gm_feat(feat))               # pas de doublon
        self.assertIn(feat, eng.chosen_feats())
        self.assertGreater(eng.feat_effect("initiative"), before)
        eng.remove_gm_feat(feat)
        self.assertNotIn(feat, eng.chosen_feats())

    def test_gm_feat_ability_choice_and_save(self):
        from core.character import Character
        eng = make("Guerrier", 1)
        feat = next(n for n, f in DB.feats.items() if len(f.get("carac_choix", [])) == 1)
        ab = DB.feats[feat]["carac_choix"][0]
        before = eng.asi_bonus()[ab]
        eng.add_gm_feat(feat)
        self.assertEqual(eng.asi_bonus()[ab], before + 1)
        ch2 = Character.from_dict(eng.ch.to_dict())
        self.assertEqual(ch2.dons_mj, [feat])

    def test_ui_button(self):
        import ui.main_window as mw
        import ui.progression_tab as pt
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        saved = pt.ask_gm_feat
        self.addCleanup(lambda: setattr(pt, "ask_gm_feat", saved))
        pt.ask_gm_feat = lambda parent, names, pre="": "Alerte"
        win.progress_tab._on_gm_feat()
        self.assertIn("Alerte", win.ch.dons_mj)
        win.progress_tab.refresh()
        row = next(w for w in win.progress_tab._rows if w["id"] == "mj|Alerte")
        self.assertTrue(row["mj"])
        win.progress_tab._on_remove_gm("mj|Alerte")
        self.assertEqual(win.ch.dons_mj, [])


if __name__ == "__main__":
    unittest.main()
