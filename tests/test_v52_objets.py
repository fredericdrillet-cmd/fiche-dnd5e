"""v52 : objets magiques — recharge selon la formule, charges multiples, destruction, éléments comptés."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def sheet(cls="Magicien", lvl=7, edition="2014"):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    return eng


class SeqRng:
    def __init__(self, seq):
        self.seq = list(seq)

    def randint(self, a, b):
        return self.seq.pop(0)


def power(eng, frag):
    return next(p for p in eng.magic_item_powers() if frag in p["id"])


class ItemTests(unittest.TestCase):
    def test_wand_multi_charges_and_recharge(self):
        for ed in ("2014", "2024"):
            eng = sheet(edition=ed)
            eng.add_magic_item("Baguette de projectiles magiques")
            p = power(eng, "Projectile")
            self.assertEqual(eng.item_count_choice(p["id"])["max"], 7)
            r = eng.use_item_power(p["id"], 3)
            self.assertEqual(r["niveau"], 3)
            entry = eng.ch.objets_magiques[0]
            self.assertEqual(entry["charges_utilisees"], 3)
            self.assertEqual(eng.pending_recharges()[0][2], "1d6+1")
            msgs = eng.recharge_magic_items(rng=SeqRng([1]))        # 1d6+1 = 2
            self.assertEqual(entry["charges_utilisees"], 1)
            self.assertTrue(msgs)
            eng.do_long_rest(recharge_rolls={0: 7})
            self.assertNotIn("charges_utilisees", entry)

    def test_last_charge_destruction(self):
        eng = sheet()
        eng.add_magic_item("Baguette de projectiles magiques")
        p = power(eng, "Projectile")
        r = eng.use_item_power(p["id"], 7)
        self.assertTrue(r["destruction"])
        self.assertIn("tient bon", eng.resolve_item_destruction(0, 12))
        self.assertIn("détruit", eng.resolve_item_destruction(0, 1))
        entry = eng.ch.objets_magiques[0]
        self.assertTrue(entry["detruit"])
        self.assertEqual(eng.item_state_label(entry), "💥 Détruit")
        self.assertFalse(eng.magic_item_powers())
        self.assertEqual(eng.pending_recharges(), [])

    def test_transform_is_not_destroyed(self):
        eng = sheet()
        eng.add_magic_item("Baguette du jovial")
        self.assertIn("grincheux", eng.resolve_item_destruction(0, 1))
        self.assertFalse(eng.ch.objets_magiques[0].get("detruit"))

    def test_necklace_beads(self):
        for ed in ("2014", "2024"):
            eng = sheet(edition=ed)
            eng.add_magic_item("Collier de boules de feu")
            entry = eng.ch.objets_magiques[0]
            self.assertTrue(4 <= entry["elements"] <= 9)
            eng.set_item_elements(0, 5)
            p = power(eng, "Boule de feu")
            self.assertEqual(p["niveau"], 3)
            choice = eng.item_count_choice(p["id"])
            self.assertEqual((choice["max"], choice["nom"]), (5, "perles"))
            r = eng.use_item_power(p["id"], 3)
            self.assertEqual(r["niveau"], 5)
            self.assertIn("perles : 2 / 5", r["message"])
            eng.do_long_rest()                                      # les perles ne reviennent pas
            self.assertEqual(entry["charges_utilisees"], 3)
            r = eng.use_item_power(p["id"], 2)
            self.assertTrue(entry["epuise"])
            self.assertIn("épuisé", r["message"])
            self.assertEqual(eng.item_state_label(entry), "Épuisé")
            self.assertFalse(eng.magic_item_powers())

    def test_plain_item_full_recharge(self):
        eng = sheet()
        eng.add_magic_item("Baguette du jovial")
        eng.ch.objets_magiques[0]["charges_utilisees"] = 3
        eng.recharge_magic_items()
        self.assertNotIn("charges_utilisees", eng.ch.objets_magiques[0])

    def test_ui_tile_asks_count(self):
        import qt_stub
        qt_stub.install()
        from unittest import mock
        from ui.main_window import MainWindow
        from ui import combat_tab as CT
        win = MainWindow(DB)
        eng = win.engine
        eng.add_magic_item("Baguette de projectiles magiques")
        pid = power(eng, "Projectile")["id"]
        with mock.patch.object(CT, "ask_int", return_value=2) as ask, \
                mock.patch.object(CT.CombatTab, "_use_item_power", lambda self, res: None):
            win.combat_tab._on_turn_tile(pid)
        ask.assert_called_once()
        self.assertEqual(eng.ch.objets_magiques[0]["charges_utilisees"], 2)


if __name__ == "__main__":
    unittest.main()
