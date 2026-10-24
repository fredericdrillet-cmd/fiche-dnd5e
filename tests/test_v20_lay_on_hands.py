"""Tests v20 : Imposition des mains — réserve 5 × niveau de paladin en jauge, soin sur soi / allié, guérison."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core.engine import Engine  # noqa: E402


def paladin(level=4):
    eng = Engine(DB, Engine.new_character(DB))
    eng.ch.classes = [{"nom": "Paladin", "niveau": level, "sous_classe": "", "pv_jets": []}]
    eng.normalize()
    return eng


class LayOnHandsTests(unittest.TestCase):
    def test_pool_is_gauge(self):
        eng = paladin(4)
        tr = {t["key"]: t for t in eng.resource_trackers("combat")}
        self.assertEqual((tr["imposition"]["total"], tr["imposition"]["kind"]), (20, "jauge"))
        self.assertEqual(paladin(20).lay_on_hands_left(), 100)
        self.assertIn("imposition", [a["id"] for a in eng.class_actions()])

    def test_heal_self_capped(self):
        eng = paladin(4)
        eng.ch.pv_actuels = eng.hp_max() - 6
        res = eng.use_lay_on_hands(15, "soi")
        self.assertTrue(res["ok"])
        self.assertEqual(res["soin"], 6)                 # seuls les PV manquants sont pris dans la réserve
        self.assertEqual(eng.lay_on_hands_left(), 14)
        self.assertEqual(eng.ch.pv_actuels, eng.hp_max())
        self.assertFalse(eng.use_lay_on_hands(3, "soi")["ok"])     # déjà au maximum

    def test_ally_cure_and_exhaustion(self):
        eng = paladin(2)                                # réserve 10
        self.assertTrue(eng.use_lay_on_hands(4, "allie")["ok"])
        eng.add_effect("empoisonne")
        res = eng.use_lay_on_hands(0, "soi", cure=True)
        self.assertTrue(res["ok"])
        self.assertNotIn("empoisonne", eng.ch.effets_actifs)
        self.assertEqual(eng.lay_on_hands_left(), 1)
        self.assertFalse(eng.use_lay_on_hands(5, "soi", cure=True)["ok"])   # 5 points requis
        self.assertFalse(eng.use_lay_on_hands(2, "allie")["ok"])
        eng.use_lay_on_hands(1, "allie")
        a = next(x for x in eng.class_actions() if x["id"] == "imposition")
        self.assertFalse(a["disponible"])               # réserve vide : action verrouillée
        eng.short_rest()
        self.assertEqual(eng.lay_on_hands_left(), 0)    # pas de récupération au repos court
        eng.long_rest()
        self.assertEqual(eng.lay_on_hands_left(), 10)

    def test_ui_gauge_and_action(self):
        import ui.main_window as mw
        from ui.orbs import GaugeBar
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.ch.classes = [{"nom": "Paladin", "niveau": 3, "sous_classe": "", "pv_jets": []}]
        win.changed()
        ct = win.combat_tab
        row = next(w for w in ct.res_rows if w["key"] == "imposition")
        self.assertIsInstance(row["orbs"], GaugeBar)
        ct._on_orbs("imposition", 5)                    # correction manuelle depuis la jauge
        self.assertEqual(win.engine.lay_on_hands_left(), 10)
        act = next(w for w in ct.act_rows if w["id"] == "imposition")
        act["amount"].setValue(4)
        act["target"].setCurrentIndex(1)                # sur un allié
        ct._on_action("imposition")
        self.assertEqual(win.engine.lay_on_hands_left(), 6)


if __name__ == "__main__":
    unittest.main()
