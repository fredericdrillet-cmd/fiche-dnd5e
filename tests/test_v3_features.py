"""Tests : Point Buy (+ réinitialisation), formule de CA, styles de combat, onglet RP / portrait."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core import rules as R  # noqa: E402
from core.character import Character  # noqa: E402
from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def make(classes, dex=10, **scores):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": n, "niveau": l, "sous_classe": s, "pv_jets": []} for n, l, s in classes]
    ch.methode = "manuel"
    ch.race = "Aucune race"          # pas de bonus racial : les modificateurs sont ceux de la saisie manuelle
    ch.scores_manuel = {a: 10 for a in R.ABILITIES}
    ch.scores_manuel["Dextérité"] = dex
    ch.scores_manuel.update(scores)
    eng = Engine(DB, ch)
    eng.normalize()
    return eng


class PointBuyTests(unittest.TestCase):
    def test_official_costs(self):
        self.assertEqual([R.POINT_BUY_COST[v] for v in range(8, 16)], [0, 1, 2, 3, 4, 5, 7, 9])
        self.assertEqual(R.POINT_BUY_TOTAL, 27)

    def test_standard_array_is_27_points(self):
        arr = dict(zip(R.ABILITIES, [15, 14, 13, 12, 10, 8]))
        self.assertEqual(R.point_buy_total(arr), 27)
        self.assertEqual(R.point_buy_remaining(arr), 0)

    def test_stepping_up_to_the_budget_without_blocking(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.methode = "achat"
        eng.reset_scores()
        self.assertEqual(R.point_buy_remaining(eng.ch.scores_achat), 27)
        for ab in ("Force", "Dextérité", "Constitution"):          # 3 × 9 points = 27
            for _ in range(7):
                self.assertTrue(eng.buy_step(ab, +1))
        self.assertEqual(R.point_buy_remaining(eng.ch.scores_achat), 0)
        self.assertFalse(eng.buy_step("Sagesse", +1))              # plus de budget : refusé proprement
        self.assertTrue(eng.buy_step("Constitution", -1))          # baisser rend des points
        self.assertEqual(R.point_buy_remaining(eng.ch.scores_achat), 2)
        self.assertTrue(eng.buy_step("Sagesse", +1))

    def test_bounds(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.methode = "achat"
        eng.reset_scores()
        self.assertFalse(eng.buy_step("Force", -1))                # jamais sous 8
        for _ in range(7):
            eng.buy_step("Force", +1)
        self.assertFalse(eng.buy_step("Force", +1))                # jamais au-dessus de 15
        self.assertEqual(eng.ch.scores_achat["Force"], 15)

    def test_step_cost_changes_at_14(self):
        sc = {a: 8 for a in R.ABILITIES}
        sc["Force"] = 13
        sc["Dextérité"] = 15
        sc["Constitution"] = 15      # 5 + 9 + 9 = 23, reste 4
        self.assertTrue(R.can_raise(sc, "Force"))                   # 13 -> 14 coûte 2
        sc["Intelligence"] = 12      # +4 = 27
        self.assertFalse(R.can_raise(sc, "Force"))

    def test_reset_button_logic(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.methode = "achat"
        for ab in ("Force", "Charisme"):
            for _ in range(4):
                eng.buy_step(ab, +1)
        self.assertLess(R.point_buy_remaining(eng.ch.scores_achat), 27)
        eng.reset_scores()
        self.assertEqual(set(eng.ch.scores_achat.values()), {8})
        self.assertEqual(R.point_buy_remaining(eng.ch.scores_achat), 27)
        eng.ch.methode = "manuel"
        eng.ch.scores_manuel["Force"] = 18
        eng.reset_scores()
        self.assertEqual(set(eng.ch.scores_manuel.values()), {10})

    def test_corrupted_save_is_repaired(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.methode = "achat"
        eng.ch.scores_achat = {a: 15 for a in R.ABILITIES}          # 54 points : invalide
        eng.normalize()
        self.assertLessEqual(R.point_buy_total(eng.ch.scores_achat), 27)
        self.assertTrue(R.point_buy_valid(eng.ch.scores_achat)[0])


class ArmorClassDisplayTests(unittest.TestCase):
    def _ac(self, armor, shield=False, dex=16, bonus=0):
        eng = make([("Guerrier", 1, "")], dex=dex)
        eng.ch.armure.update({"nom": armor, "bouclier": shield, "bouclier_nom": "Bouclier" if shield else "",
                              "bonus": bonus})
        return eng.armor_class_detail()

    def test_light_armor(self):
        d = self._ac("Armure matelassée")
        self.assertEqual((d["formule"], d["valeur"]), ("11 + Dex", 14))
        self.assertEqual(d["chiffres"], "11 + 3 = 14")

    def test_medium_armor_dex_cap(self):
        d = self._ac("Chemise de mailles")
        self.assertEqual((d["formule"], d["valeur"]), ("13 + Dex (max 2)", 15))

    def test_heavy_armor_fixed(self):
        d = self._ac("Harnois")
        self.assertEqual((d["formule"], d["valeur"], d["variable"]), ("18", 18, False))

    def test_armor_shield_and_magic(self):
        d = self._ac("Demi-plate", shield=True, bonus=1)
        self.assertEqual(d["formule"], "15 + Dex (max 2) + 2 (bouclier) + 1 (bonus magique)")
        self.assertEqual(d["valeur"], 15 + 2 + 2 + 1)

    def test_negative_dex_in_numbers(self):
        d = self._ac("Armure de cuir", dex=8)
        self.assertEqual(d["chiffres"], "11 - 1 = 10")

    def test_unarmored_variants(self):
        eng = make([("Barbare", 1, "")], dex=14, Constitution=16)
        d = eng.armor_class_detail()
        self.assertEqual(d["formule"], "10 + Dex + Con")
        self.assertIn("barbare", d["note"])
        self.assertEqual(d["valeur"], 15)

    def test_armor_class_tuple_is_formula_not_name(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.armure["nom"] = "Armure matelassée"
        value, label = eng.armor_class()
        self.assertNotIn("matelass", label)
        self.assertIn("11", label)


class FightingStyleTests(unittest.TestCase):
    def test_slots_follow_class_levels(self):
        eng = make([("Guerrier", 1, "")])
        self.assertEqual([(s["classe"], s["niveau_requis"], s["debloque"]) for s in eng.fighting_style_slots()],
                         [("Guerrier", 1, True)])
        eng = make([("Paladin", 1, "")])
        self.assertEqual([(s["niveau_requis"], s["debloque"]) for s in eng.fighting_style_slots()], [(2, False)])
        eng = make([("Paladin", 2, "")])
        self.assertTrue(eng.fighting_style_slots()[0]["debloque"])
        self.assertEqual(make([("Rôdeur", 2, "")]).fighting_style_slots()[0]["niveau_requis"], 2)
        self.assertEqual(make([("Magicien", 5, "")]).fighting_style_slots(), [])

    def test_champion_gets_a_second_style_at_10(self):
        eng = make([("Guerrier", 9, "Champion")])
        self.assertFalse(eng.fighting_style_slots()[1]["debloque"])
        eng = make([("Guerrier", 10, "Champion")])
        self.assertEqual(len(eng.fighting_style_slots()), 2)
        self.assertTrue(all(s["debloque"] for s in eng.fighting_style_slots()))

    def test_options_per_class_and_no_duplicates(self):
        eng = make([("Guerrier", 10, "Champion")])
        first, second = (s["id"] for s in eng.fighting_style_slots())
        self.assertIn("Archerie", eng.style_options(first))
        self.assertNotIn("Archerie", make([("Paladin", 2, "")]).style_options("Paladin|1"))   # style de Guerrier/Rôdeur uniquement
        eng.ch.styles_combat[first] = "Archerie"
        self.assertNotIn("Archerie", eng.style_options(second))

    def test_locked_style_has_no_effect(self):
        eng = make([("Paladin", 1, "")])
        eng.ch.styles_combat["Paladin|1"] = "Défense"
        eng.normalize()
        self.assertFalse(eng.style_active("Défense"))

    def test_defense_style_needs_armor(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.styles_combat["Guerrier|1"] = "Défense"
        base = eng.armor_class_detail()["valeur"]
        eng.ch.armure["nom"] = "Cotte de mailles"
        self.assertEqual(eng.armor_class_detail()["valeur"], 17)
        self.assertIn("style Défense", eng.armor_class_detail()["formule"])
        eng.ch.armure["nom"] = "Aucune armure"
        self.assertEqual(eng.armor_class_detail()["valeur"], base)

    def test_archery_and_duelist(self):
        eng = make([("Guerrier", 1, "")], Force=16, dex=14)
        bow = {"nom": "Arc long", "bonus": 0, "maitrise": None}
        before = eng.weapon_stats(bow)["attaque"]
        eng.ch.styles_combat["Guerrier|1"] = "Archerie"
        self.assertEqual(eng.weapon_stats(bow)["attaque"], before + 2)
        eng.ch.styles_combat["Guerrier|1"] = "Duel"
        sword = eng.weapon_stats({"nom": "Rapière", "bonus": 0, "maitrise": None})
        self.assertEqual(sword["degats"], "1d8+5")                  # Force 16 (+3) + 2
        great = eng.weapon_stats({"nom": "Épée à deux mains", "bonus": 0, "maitrise": None})
        self.assertEqual(great["degats"], "2d6+3")                  # arme à deux mains : pas de +2

    def test_missing_choice_warns(self):
        eng = make([("Guerrier", 1, "")])
        # v28 : un style non choisi est un OUBLI (missing_choices), plus une incohérence (warnings)
        self.assertTrue(any("Style de combat" in m["message"] for m in eng.missing_choices()))
        eng.ch.styles_combat["Guerrier|1"] = "Défense"
        self.assertFalse(any("Style de combat" in m["message"] for m in eng.missing_choices()))


class RPTests(unittest.TestCase):
    def test_roleplay_fields_roundtrip(self):
        ch = Engine.new_character(DB)
        ch.histoire, ch.notes, ch.portrait = "Il était une fois…", "PNJ : Mira", "QUJD"
        again = Character.from_dict(ch.to_dict())
        self.assertEqual((again.histoire, again.notes, again.portrait), ("Il était une fois…", "PNJ : Mira", "QUJD"))

    def test_old_save_without_rp_fields_loads(self):
        data = Engine.new_character(DB).to_dict()
        for k in ("histoire", "portrait", "styles_combat"):
            data.pop(k)
        again = Character.from_dict(data)
        self.assertEqual((again.histoire, again.portrait, again.styles_combat), ("", "", {}))


class UiSmokeV3(unittest.TestCase):
    def test_new_screens(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        eng = win.engine
        self.assertIn(win.rp_tab, [w for w, _ in win.tab_list])
        eng.ch.classes = [{"nom": "Guerrier", "niveau": 10, "sous_classe": "Champion", "pv_jets": []}]
        win.changed()
        self.assertEqual(len(win.combat_tab.style_rows), 2)
        sid = win.combat_tab.style_rows[0]["id"]
        win.combat_tab.style_rows[0]["combo"]._st["items"] = ["— choisir —", "Archerie"]
        win.combat_tab.style_rows[0]["combo"]._st["idx"] = 1
        win.combat_tab._on_style(sid)
        self.assertEqual(eng.ch.styles_combat[sid], "Archerie")
        eng.ch.classes = [{"nom": "Magicien", "niveau": 1, "sous_classe": "", "pv_jets": []}]
        win.changed()
        self.assertEqual(win.combat_tab.style_rows, [])               # aucun style pour un magicien
        win.rp_tab._on_text("histoire", win.rp_tab.story)
        win.rp_tab._on_clear()
        win.abilities_tab._on_buy("Force", +1)
        win.abilities_tab._on_reset()
        self.assertEqual(set(eng.ch.scores_achat.values()), {8})


if __name__ == "__main__":
    unittest.main()
