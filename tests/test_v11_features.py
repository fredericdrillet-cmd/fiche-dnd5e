"""Tests v11 : concentration (badge, purge au repos, rupture), ascendance draconique et souffle, encart racial,
sorts accordés par le MJ."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB, make  # noqa: E402


class ConcentrationTests(unittest.TestCase):
    def test_badge_rest_and_manual_break(self):
        eng = make([("Magicien", 5, "")])
        eng.cast_spell("Flou")
        self.assertIn("concentration", eng.active_effect_keys())
        self.assertIn("Concentration : Flou", eng.effects_ending(False))
        eng.do_short_rest()
        self.assertEqual(eng.ch.concentration, "")
        self.assertNotIn("concentration", eng.active_effect_keys())
        eng.cast_spell("Hâte")
        eng.remove_effect("concentration")                               # clic sur l'icône = rupture volontaire
        self.assertEqual(eng.ch.concentration, "")


class DraconicTests(unittest.TestCase):
    def test_breath_by_color(self):
        eng = make([("Guerrier", 6, "")], Constitution=14)
        eng.ch.race = "Drakéide"
        eng.normalize()
        self.assertEqual(eng.breath_weapon()["type"], "")
        eng.ch.ascendance_raciale = "Bleu"
        eng.normalize()
        b = eng.breath_weapon()
        self.assertEqual((b["type"], b["js"], b["dd"], b["degats"]), ("foudre", "Dextérité", 13, "3d6"))
        self.assertIn("ligne", b["zone"])
        self.assertIn("resist_foudre", eng.active_effect_keys())
        eng.ch.ascendance_raciale = "Blanc"
        eng.normalize()
        b = eng.breath_weapon()
        self.assertEqual((b["type"], b["js"]), ("froid", "Constitution"))
        self.assertIn("cône", b["zone"])
        self.assertIn("resist_froid", eng.active_effect_keys())
        self.assertNotIn("resist_foudre", eng.active_effect_keys())
        eng.set_resource_used("souffle", 1)
        self.assertTrue(eng.breath_weapon()["utilise"])
        eng.do_short_rest()
        self.assertFalse(eng.breath_weapon()["utilise"])

    def test_racial_combat_traits_and_sorcerer(self):
        self.assertEqual(make([("Guerrier", 1, "")]).racial_combat_traits(), [])
        eng = make([("Ensorceleur", 6, "Lignée draconique")], Charisme=16)
        eng.ch.race = "Minotaure"
        eng.ch.ascendance_ensorceleur = "Rouge"
        eng.normalize()
        self.assertIn("Cornes", [t["nom"] for t in eng.racial_combat_traits()])
        lin = eng.sorcerer_lineage()
        self.assertEqual((lin["type"], lin["bonus_degats"]), ("feu", 3))


class GmSpellTests(unittest.TestCase):
    def test_gm_spells_in_granted_list(self):
        eng = make([("Guerrier", 3, "")])
        self.assertTrue(eng.add_gm_spell("Bouclier", "1 fois par repos long", "Relique d'Helm"))
        self.assertFalse(eng.add_gm_spell("Bouclier"))
        g = [x for x in eng.granted_spells() if x.get("mj")]
        self.assertEqual(g[0]["categorie"], "Accordés par le MJ")
        self.assertIn("Relique d'Helm", g[0]["source"])
        self.assertIn("Bouclier", [r["nom"] for r in eng.reactions()])
        eng.remove_gm_spell("Bouclier")
        self.assertEqual(eng.ch.sorts_mj, [])

    def test_ui_racial_box_and_granted_filter(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.race = "Drakéide"
        win.ch.ascendance_raciale = "Rouge"
        win.engine.add_gm_spell("Bénédiction", "À volonté")
        win.changed()
        self.assertTrue(win.combat_tab._racial_key is not None)
        win.magic_tab.refresh()
        self.assertIn("Accordés par le MJ", win.magic_tab.granted_filter._st["items"])
        self.assertTrue(any(r["mj"] for r in win.magic_tab._granted_rows))


if __name__ == "__main__":
    unittest.main()
