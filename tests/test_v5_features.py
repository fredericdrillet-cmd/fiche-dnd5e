"""Tests : compteurs à sphères (rage, ki, sorcellerie, emplacements), objets magiques et harmonisation."""
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
from core.rules import norm  # noqa: E402

DB = Database(ROOT / "data")


def make(classes, **kw):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": n, "niveau": l, "sous_classe": s, "pv_jets": []} for n, l, s in classes]
    ch.methode = "manuel"
    ch.race = "Aucune race"
    ch.scores_manuel = {a: 10 for a in R.ABILITIES}
    ch.scores_manuel.update(kw)
    eng = Engine(DB, ch)
    eng.normalize()
    return eng


class OrbRuleTests(unittest.TestCase):
    def test_click_full_spends_click_empty_recovers(self):
        self.assertEqual(R.orb_click(4, 0, 3), 1)       # 4 pleines : clic sur une pleine -> 1 dépensée
        self.assertEqual(R.orb_click(4, 1, 3), 0)       # la 4e est vide -> récupérée
        self.assertEqual(R.orb_click(4, 1, 0), 2)
        self.assertEqual(R.orb_click(4, 4, 0), 3)       # tout dépensé : clic -> récupère
        self.assertEqual(R.orb_click(4, 2, 99), 2)      # clic hors sphère : rien ne change

    def test_rage_and_ki_tables(self):
        self.assertEqual([R.rage_uses(n) for n in (1, 3, 6, 12, 17)], [2, 3, 4, 5, 6])
        self.assertIsNone(R.rage_uses(20))
        self.assertEqual((R.ki_points(1), R.ki_points(2), R.ki_points(11)), (0, 2, 11))


class ResourceTests(unittest.TestCase):
    def test_contextual_trackers(self):
        self.assertEqual(make([("Magicien", 5, "")]).resource_trackers(), [])
        self.assertEqual([t["key"] for t in make([("Guerrier", 5, "")]).resource_trackers()],
                         ["second_souffle", "sursaut"])                     # v19 : ressources du guerrier
        eng = make([("Barbare", 6, ""), ("Moine", 3, "")])
        self.assertEqual([(t["key"], t["total"], t["where"]) for t in eng.resource_trackers()],
                         [("rage", 4, "combat"), ("ki", 3, "combat")])
        self.assertEqual(make([("Moine", 1, "")]).resource_trackers(), [])          # ki dès le niveau 2
        self.assertIsNone(make([("Barbare", 20, "")]).resource_trackers()[0]["total"])

    def test_sorcery_points_only_for_sorcerer_or_metamagic_feat(self):
        self.assertEqual(make([("Magicien", 5, "")]).resource_trackers("magie"), [])
        self.assertEqual(make([("Ensorceleur", 1, "")]).resource_trackers("magie"), [])  # Source de magie : niv. 2
        self.assertEqual(make([("Ensorceleur", 6, "")]).resource_trackers("magie")[0]["total"], 6)
        feat = next((n for n in DB.feats if "metamagie" in norm(n)), None)
        if feat:
            eng = make([("Guerrier", 4, "")])
            eng.ch.ameliorations["Guerrier|4"] = {"mode": "don", "don": feat}
            self.assertEqual(eng.resource_trackers("magie")[0]["total"], 2)

    def test_spending_is_clamped_and_rests_recover(self):
        eng = make([("Barbare", 3, ""), ("Moine", 4, "")])
        eng.set_resource_used("rage", 99)
        eng.set_resource_used("ki", 2)
        self.assertEqual((eng.resource_used("rage"), eng.resource_used("ki")), (3, 2))
        eng.short_rest()
        self.assertEqual((eng.resource_used("rage"), eng.resource_used("ki")), (3, 0))   # ki : repos court
        eng.long_rest()
        self.assertEqual(eng.resource_used("rage"), 0)

    def test_spell_slot_spending_is_clamped(self):
        eng = make([("Magicien", 5, "")])
        eng.ch.emplacements_utilises[0] = 9
        eng.normalize()
        self.assertEqual(eng.ch.emplacements_utilises[0], 4)        # jamais plus que le total (4 au niveau 1)


class MagicItemTests(unittest.TestCase):
    def test_catalog_loaded_with_attunement(self):
        self.assertGreater(len(DB.magic_items), 300)
        ring = DB.magic_items["Anneau de protection"]
        self.assertTrue(ring["lien"])
        self.assertEqual((ring["ca"], ring["js"]), (1, 1))
        self.assertEqual(DB.magic_items["Armure +2"]["ca"], 2)                 # paliers séparés

    def test_bonuses_need_equipped_and_attuned(self):
        eng = make([("Guerrier", 1, "")])
        eng.add_magic_item("Anneau de protection")
        self.assertEqual(eng.magic_item_bonuses(), {"ca": 0, "js": 0})       # pas encore harmonisé
        self.assertTrue(eng.set_attuned(0, True))
        self.assertEqual(eng.magic_item_bonuses(), {"ca": 1, "js": 1})
        self.assertIn("objets magiques", eng.armor_class_detail()["formule"])
        eng.set_equipped(0, False)
        self.assertEqual(eng.magic_item_bonuses()["ca"], 0)                   # retiré : plus d'effet

    def test_variable_bonus_items(self):
        eng = make([("Guerrier", 1, "")])
        eng.add_magic_item("Bouclier +2")
        self.assertEqual(eng.ch.objets_magiques[0]["nom"], "Bouclier +2")
        self.assertEqual(eng.magic_item_bonuses()["ca"], 2)                   # pas d'harmonisation requise
        # ancienne sauvegarde « Bouclier +1, +2 ou +3 » + bonus 3 -> migrée vers « Bouclier +3 »
        eng.ch.objets_magiques = [{"nom": "Bouclier +1, +2 ou +3", "bonus": 3, "equipe": True, "harmonise": False}]
        eng.normalize()
        self.assertEqual(eng.ch.objets_magiques[0]["nom"], "Bouclier +3")
        self.assertEqual(eng.magic_item_bonuses()["ca"], 3)

    def test_attunement_limit_three_then_artificer(self):
        eng = make([("Guerrier", 1, "")])
        for _ in range(4):
            eng.add_magic_item("Anneau de protection")
        self.assertEqual([eng.set_attuned(i, True) for i in range(4)], [True, True, True, False])
        self.assertEqual(eng.attuned_count(), 3)
        self.assertEqual(make([("Artificier", 10, "")]).attunement_limit(), 4)
        self.assertEqual(make([("Artificier", 18, "")]).attunement_limit(), 6)

    def test_item_without_attunement_cannot_be_attuned(self):
        eng = make([("Guerrier", 1, "")])
        eng.add_magic_item("Bouclier +1")
        self.assertFalse(eng.set_attuned(0, True))

    def test_attunement_prerequisites(self):
        self.assertEqual(make([("Guerrier", 1, "")]).attune_status("Bâton de feu")[0], "ko")
        self.assertEqual(make([("Magicien", 1, "")]).attune_status("Bâton de feu")[0], "ok")
        self.assertEqual(make([("Artificier", 14, "")]).attune_status("Bâton de feu")[0], "ok")   # Érudit des objets

    def test_save_roundtrip(self):
        eng = make([("Barbare", 3, "")])
        eng.add_magic_item("Anneau de protection")
        eng.set_attuned(0, True)
        eng.set_resource_used("rage", 1)
        again = Character.from_dict(eng.ch.to_dict())
        self.assertEqual(again.objets_magiques, eng.ch.objets_magiques)
        self.assertEqual(again.ressources_utilisees, {"rage": 1})


class UiSmokeV5(unittest.TestCase):
    def test_new_widgets(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        eng = win.engine
        eng.ch.classes = [{"nom": "Barbare", "niveau": 5, "sous_classe": "", "pv_jets": []},
                          {"nom": "Ensorceleur", "niveau": 4, "sous_classe": "", "pv_jets": []}]
        win.changed()
        self.assertEqual([w["key"] for w in win.combat_tab.res_rows], ["rage"])
        win.combat_tab._on_orbs("rage", 2)
        self.assertEqual(eng.resource_used("rage"), 2)
        win.magic_tab._on_sorcery(3)
        self.assertEqual(eng.resource_used("sorcellerie"), 3)
        win.magic_tab._on_used(0, 1)
        panel = win.inventory_tab.magic_items
        panel._lib_rows = ["Anneau de protection"]
        panel.library._st["row"] = 0
        panel._on_add()
        panel._toggle_attune(0, True)
        self.assertTrue(eng.ch.objets_magiques[0]["harmonise"])
        panel._toggle_equipped(0, False)
        panel.table._st["row"] = 0
        panel._on_remove()
        self.assertEqual(eng.ch.objets_magiques, [])


if __name__ == "__main__":
    unittest.main()
