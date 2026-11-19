"""v52 : règles de jeu — états selon l'édition, Se libérer, Chanceux, Fin du combat, environnement, composantes,
abri."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

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


class ConditionTests(unittest.TestCase):
    def test_stunned_speed_per_edition(self):
        for ed, speed in (("2014", 0.0), ("2024", 9.0)):
            eng = sheet("Guerrier", 3, ed)
            eng.add_effect("etourdi")
            self.assertEqual(eng.speed(), speed, ed)
            self.assertTrue(eng.save_spec("Force").echec, ed)

    def test_grappled_2024_text_and_no_attack_malus(self):
        eng = sheet("Guerrier", 3, "2024")
        eng.add_effect("agrippe")
        self.assertIn("autre que l&#x27;agrippeur", eng.effect_tooltip("agrippe"))
        self.assertNotIn("(ou JS)", eng.effect_tooltip("agrippe"))
        self.assertIn("règle 2024", eng.effect_tooltip("agrippe"))
        self.assertEqual(eng.speed(), 0.0)
        old = sheet("Guerrier", 3, "2014")
        self.assertNotIn("règle 2024", old.effect_tooltip("agrippe"))

    def test_initiative_2024(self):
        eng = sheet("Guerrier", 3, "2024")
        eng.add_effect("invisible")
        self.assertIn("Invisible", eng.initiative_detail()["avantage"])
        eng.remove_effect("invisible")
        eng.add_effect("neutralise")
        self.assertTrue(eng.initiative_detail()["desavantage"])
        old = sheet("Guerrier", 3, "2014")
        old.add_effect("invisible")
        self.assertNotIn("Invisible", old.initiative_detail()["avantage"])

    def test_incapacitated_breaks_concentration_both(self):
        for ed in ("2014", "2024"):
            eng = sheet("Clerc", 3, ed)
            r = eng.cast_spell("Bénédiction", slot_level=1, target="allie")
            self.assertTrue(r["ok"], r)
            eng.add_effect("paralyse")
            self.assertEqual(eng.ch.concentration, "", ed)
            self.assertIn("Concentration rompue", eng.last_effect_message)
            eng.remove_effect("paralyse")
            eng.add_effect("a_terre")
            self.assertEqual(eng.last_effect_message, "")

    def test_hidden_ends_on_spell(self):
        eng = sheet("Clerc", 3, "2024")
        eng.add_effect("cache")
        r = eng.cast_spell("Bénédiction", slot_level=1, target="allie")
        self.assertIn("plus caché", r["message"])
        self.assertNotIn("cache", eng.ch.effets_actifs)
        eng.add_effect("cache")
        self.assertTrue(eng.reveal_after_attack())
        self.assertFalse(eng.reveal_after_attack())


class EscapeTests(unittest.TestCase):
    def tiles(self, eng):
        return [t["id"] for t in eng.turn_actions()]

    def test_tile_only_when_grappled(self):
        for ed in ("2014", "2024"):
            eng = sheet("Guerrier", 3, ed)
            self.assertNotIn("commune:liberer", self.tiles(eng))
            eng.add_effect("agrippe")
            self.assertIn("commune:liberer", self.tiles(eng))

    def test_escape_flow(self):
        eng = sheet("Guerrier", 3, "2024")
        eng.add_effect("entrave")
        r = eng.use_turn_action("commune:liberer")
        self.assertEqual((r["liberer"], r["dd"]), (["entrave"], 15))
        self.assertIn(r["competence"], ("Athlétisme", "Acrobaties"))
        self.assertIn("Toujours", eng.resolve_escape("entrave", False, 10, 15))
        self.assertIn("Libéré (16 contre DD 15)", eng.resolve_escape("entrave", True, 16, 15))
        self.assertNotIn("entrave", eng.ch.effets_actifs)
        old = sheet("Guerrier", 3, "2014")
        old.add_effect("agrippe")
        self.assertEqual(old.use_turn_action("commune:liberer")["dd"], 0)
        self.assertIn("Libéré", old.resolve_escape("agrippe", True, 14))


if __name__ == "__main__":
    unittest.main()


class ConditionUiTests(unittest.TestCase):
    def test_escape_2014_asks_result(self):
        import qt_stub
        qt_stub.install()
        from unittest import mock
        from ui.main_window import MainWindow
        from ui import combat_tab as CT
        win = MainWindow(DB)
        eng = win.engine
        eng.add_effect("agrippe")
        res = eng.use_turn_action("commune:liberer")
        fake = mock.Mock(total=14)
        with mock.patch.object(CT, "roll_dice", return_value=fake), \
                mock.patch.object(CT, "ask_yes_no", return_value=True) as ask:
            win.combat_tab._escape(res)
        ask.assert_called_once()
        self.assertNotIn("agrippe", eng.ch.effets_actifs)

    def test_paralysis_message(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        eng = win.engine
        eng.ch.concentration = "Bénédiction"
        self.assertTrue(eng.add_effect("etourdi"))
        self.assertIn("Concentration rompue", eng.last_effect_message)


class SeqRng:
    def __init__(self, seq):
        self.seq = list(seq)

    def randint(self, a, b):
        return self.seq.pop(0)


class LuckTests(unittest.TestCase):
    def test_halfling_rerolls_ones(self):
        from core import dice as D
        for ed, race in (("2014", "Halfelin Pied-léger"), ("2024", "Halfelin")):
            eng = sheet("Guerrier", 3, ed)
            eng.ch.race = race
            eng.normalize()
            self.assertTrue(eng.halfling_lucky(), ed)
            spec = eng.prepare_d20_spec(eng.save_spec("Force"))
            r = D.roll_d20(spec, SeqRng([1, 14]))
            self.assertEqual(r.natural, 14)
            self.assertIn("1 relancé", r.adjust)
        self.assertFalse(sheet("Guerrier", 3, "2014").halfling_lucky())

    def test_lucky_feat_2014_extra_die(self):
        from core import dice as D
        spec = D.RollSpec("t", mode="désavantage", luck_dice=[2, 17])
        self.assertEqual(D.roll_d20(spec, SeqRng([9])).natural, 17)

    def test_lucky_points_and_defense(self):
        eng = sheet("Guerrier", 4, "2024")
        sid = [x["id"] for x in eng.asi_slots()][0]
        eng.ch.ameliorations[sid] = {"mode": "don", "don": "Chanceux (2024)", "don_carac": ""}
        if not eng.luck_tracker():
            eng.ch.ameliorations[sid]["don"] = "Chanceux"
        self.assertEqual(eng.luck_left(), eng.prof)
        opt = next(o for o in eng.defense_options("attaque") if o["key"] == "chance")
        eng.ch.reaction_utilisee = "autre"
        self.assertTrue(any(o["key"] == "chance" for o in eng.defense_options("attaque")))
        r = eng.use_defense(opt)
        self.assertTrue(r["desavantage"])
        self.assertEqual(eng.luck_left(), eng.prof - 1)
        self.assertEqual(eng.ch.reaction_utilisee, "autre")

    def test_dice_dialog_luck_button(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.dice_dialog import DiceRollDialog
        win = MainWindow(DB)
        self.assertIsNone(DiceRollDialog(win, win.engine.skill_spec("Athlétisme")).luck_btn)


class CombatEndTests(unittest.TestCase):
    def archer(self, ed):
        eng = sheet("Rôdeur", 3, ed)
        eng.ch.armes_distance[0] = {"nom": "Arc long", "bonus": 0, "maitrise": None}
        eng.ch.equipement.append({"nom": "Flèches", "qte": 20})
        return eng

    def test_ammo_and_summary(self):
        for ed in ("2014", "2024"):
            eng = self.archer(ed)
            eng.record_initiative(15)
            self.assertTrue(eng.in_combat())
            for _ in range(5):
                self.assertIn("tiré", eng.fire_ammo(eng.ch.armes_distance[0]))
            self.assertEqual(eng.ch.munitions_tirees, {"Flèches": 5})
            arrows = next(i for i in eng.ch.equipement if i["nom"] == "Flèches")
            self.assertEqual(arrows["qte"], 15)
            eng.start_turn()
            eng.start_turn()
            eng.ch.pv_actuels = max(1, eng.ch.pv_actuels - 4)
            eng.add_effect("esquive")
            eng.add_effect("benediction")
            lines = eng.end_combat()
            self.assertEqual(arrows["qte"], 17, ed)
            text = "\n".join(lines)
            self.assertIn("2 récupérée(s) sur 5", text)
            self.assertIn("Durée : 2 round(s)", text)
            self.assertIn("PV perdus : 4", text)
            self.assertIn("Esquive", text)
            self.assertNotIn("esquive", eng.ch.effets_actifs)
            self.assertIn("benediction", eng.ch.effets_actifs)       # les sorts gardent leur durée
            self.assertFalse(eng.in_combat())
            self.assertEqual(eng.ch.munitions_tirees, {})

    def test_melee_weapon_uses_no_ammo(self):
        eng = sheet("Guerrier", 3, "2024")
        self.assertEqual(eng.fire_ammo({"nom": "Épée longue"}), "")

    def test_rage_and_frenzy_end(self):
        eng = sheet("Barbare", 3, "2014", "Voie du berserker")
        eng.use_class_action("rage")
        eng.add_effect("frenesie")
        eng.end_combat()
        self.assertNotIn("rage", eng.ch.effets_actifs)
        self.assertEqual(eng.exhaustion_level(), 1)

    def test_ui_button(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        win.engine.record_initiative(12)
        win.combat_tab._on_end_combat()
        self.assertIn("Fin du combat", win.combat_tab.turn_banner_text.text())
        self.assertFalse(win.engine.in_combat())


class EnvironmentTests(unittest.TestCase):
    def test_fall(self):
        eng = sheet("Guerrier", 5, "2024")
        self.assertEqual(eng.fall_formula(2), "")
        self.assertEqual(eng.fall_formula(10), "3d6")
        self.assertEqual(eng.fall_formula(200), "20d6")
        hp = eng.ch.pv_actuels = eng.hp_max()
        msg = eng.apply_fall(7, 10)
        self.assertEqual(eng.ch.pv_actuels, hp - 7)
        self.assertIn("a_terre", eng.ch.effets_actifs)
        self.assertIn("À terre", msg)
        self.assertIn("aucun dégât", eng.apply_fall(0, 10, feather=True))

    def test_slow_fall_monk(self):
        eng = sheet("Moine", 4, "2014")
        self.assertEqual(eng.slow_fall_reduction(), 20)
        hp = eng.ch.pv_actuels = eng.hp_max()
        msg = eng.apply_fall(15, 12, slow_fall=True)
        self.assertEqual(eng.ch.pv_actuels, hp)
        self.assertNotIn("a_terre", eng.ch.effets_actifs)
        self.assertIn("Chute ralentie", msg)
        self.assertEqual(eng.slow_fall_reduction(), 0)            # réaction dépensée

    def test_suffocation_2014(self):
        eng = sheet("Guerrier", 3, "2014")
        eng.ch.pv_actuels = eng.hp_max()
        eng.hold_breath()
        self.assertEqual(eng.effect_rounds("apnee"), eng.breath_rounds())
        msgs = eng.tick_effects(eng.breath_rounds())
        self.assertIn("suffoque", eng.ch.effets_actifs)
        self.assertTrue(any("suffoquez" in m for m in msgs))
        msgs = eng.tick_effects(eng.suffocation_rounds_2014())
        self.assertEqual(eng.ch.pv_actuels, 0)
        self.assertTrue(any("0 PV" in m for m in msgs))

    def test_suffocation_2024(self):
        eng = sheet("Guerrier", 3, "2024")
        eng.start_suffocating()
        eng.end_turn()
        eng.end_turn()
        self.assertEqual(eng.exhaustion_level(), 2)
        self.assertIn("2 niveau", eng.breathe_again())
        self.assertEqual(eng.exhaustion_level(), 0)
        eng.set_exhaustion(1)
        eng.start_suffocating()
        eng.end_turn()
        eng.remove_effect("suffoque")
        self.assertEqual(eng.exhaustion_level(), 1)

    def test_dialog(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.environment_dialog import EnvironmentDialog
        win = MainWindow(DB)
        dlg = EnvironmentDialog(win)
        dlg.height.setValue(9)
        dlg._refresh_fall()
        self.assertEqual(dlg.fall_formula.text(), "3d6")
        dlg._done(win.engine.hold_breath())
        self.assertIn("apnee", win.engine.ch.effets_actifs)
