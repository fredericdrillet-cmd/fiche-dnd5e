"""Tests v12 : Forme sauvage complète (substitution des statistiques, PV tampon et excédent, attaques de la bête,
sorts indisponibles, concentration maintenue, soins du Cercle de la Lune, fin au repos)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB, make  # noqa: E402


def moon(**kw):
    eng = make([("Druide", 6, "Cercle de la Lune")], Force=8, Constitution=14, Sagesse=16, **kw)
    eng.ch.pv_actuels = 30
    return eng


class WildShapeTests(unittest.TestCase):
    def test_substitution_and_restore(self):
        eng = moon()
        ac, speed = eng.armor_class_detail()["valeur"], eng.speed()
        self.assertTrue(eng.assume_form("Ours brun"))
        self.assertEqual((eng.score("Force"), eng.score("Constitution")), (19, 16))
        self.assertEqual(eng.score("Sagesse"), 16)                       # mentales conservées
        self.assertEqual(eng.armor_class_detail()["valeur"], 11)
        self.assertEqual(eng.speed(), 12)
        self.assertEqual(eng.ch.forme_pv, 34)
        eng.end_form()
        self.assertEqual((eng.score("Force"), eng.armor_class_detail()["valeur"], eng.speed()), (8, ac, speed))
        self.assertEqual(eng.ch.pv_actuels, 30)

    def test_buffer_and_overflow(self):
        eng = moon()
        eng.assume_form("Ours brun")
        eng.damage_form(20)
        self.assertEqual((eng.ch.forme_pv, eng.ch.pv_actuels), (14, 30))
        eng.damage_form(19)                                              # 5 de trop
        self.assertEqual(eng.ch.forme_active, "")
        self.assertEqual(eng.ch.pv_actuels, 25)

    def test_beast_attacks_use_creature_modifiers(self):
        eng = moon()
        eng.assume_form("Ours brun")
        attacks = {a["nom"]: a for a in eng.beast_attacks()}
        self.assertEqual((attacks["Griffes"]["attaque"], attacks["Griffes"]["degats"]), (6, "2d6+4"))
        spec = eng.beast_attack_spec(attacks["Morsure"])
        self.assertEqual([t.value for t in spec.terms], [4, 2])           # FOR de l'ours +4, maîtrise FP 1 +2

    def test_spells_blocked_concentration_kept(self):
        eng = moon()
        eng.cast_spell("Appel de la foudre")
        eng.assume_form("Ours brun")
        self.assertEqual(eng.ch.concentration, "Appel de la foudre")
        self.assertTrue(eng.spells_blocked())
        self.assertFalse(eng.cast_spell("Soins")["ok"])

    def test_moon_heal_and_rest(self):
        eng = moon()
        eng.assume_form("Ours brun")
        eng.damage_form(25)
        res = eng.moon_heal(2, rolls=[5, 6])
        self.assertEqual((res["total"], eng.ch.forme_pv), (11, 20))
        self.assertEqual(eng.ch.emplacements_utilises[1], 1)
        self.assertIsNone(make([("Druide", 6, "")]).moon_heal(1))         # hors Cercle de la Lune
        eng.do_short_rest()
        self.assertEqual(eng.ch.forme_active, "")
        self.assertNotIn("forme_sauvage", eng.active_effect_keys())

    def test_ui_banner_and_combat_switch(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.classes = [{"nom": "Druide", "niveau": 6, "sous_classe": "Cercle de la Lune", "pv_jets": []}]
        win.changed()
        win.engine.assume_form("Ours brun")
        win.changed()
        self.assertIn("Ours brun", win.form_label.text())
        self.assertIsNotNone(win.combat_tab._beast_key)
        win.combat_tab.form_dmg.setValue(40)
        win.combat_tab._on_form_damage()
        self.assertEqual(win.ch.forme_active, "")


if __name__ == "__main__":
    unittest.main()
