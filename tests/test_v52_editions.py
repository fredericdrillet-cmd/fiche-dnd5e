"""v52 : éditions 2014 / 2024 / libre, catalogue data/editions, multiclassage inter-éditions, règles de la table."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import editions as E  # noqa: E402
from core import house_rules as HR  # noqa: E402
from core.character import Character  # noqa: E402
from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def make(classes, mode="2014", rules=None):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": n, "niveau": lv, "sous_classe": "", "pv_jets": [], "edition": ed} for n, lv, ed in classes]
    ch.edition_mode = mode
    ch.regles_optionnelles = dict(rules or {})
    eng = Engine(DB, ch)
    eng.normalize()
    return eng


class ModeTests(unittest.TestCase):
    def test_normalize_and_editions(self):
        self.assertEqual(E.normalize_mode("hybride"), "libre")
        self.assertEqual(E.normalize_mode(2024), "2024")
        self.assertEqual(E.normalize_mode(None), "2014")
        self.assertEqual(E.editions_of_mode("libre"), frozenset({2014, 2024}))
        self.assertEqual(E.item_edition({}), 2014)                 # anciennes données sans champ : 2014
        self.assertEqual(E.item_edition({"edition": "2024"}), 2024)

    def test_filter_and_badge(self):
        items = [{"nom": "A", "edition": 2014}, {"nom": "B", "edition": 2024},
                 {"nom": "B bis", "edition": 2024, "doublon_de": "x"}, {"nom": "Ancien"}]
        self.assertEqual([i["nom"] for i in E.filter_items(items, "2014")], ["A", "Ancien"])
        self.assertEqual([i["nom"] for i in E.filter_items(items, "2024")], ["B"])
        self.assertEqual(len(E.filter_items(items, "libre")), 3)
        self.assertEqual(len(E.filter_items(items, "libre", dedupe=False)), 4)
        self.assertEqual(E.badge(items[1], "libre"), "2024")
        self.assertEqual(E.badge(items[1], "2024"), "")
        self.assertEqual(E.label("Guerrier", items[1], "libre"), "Guerrier [2024]")


class CatalogTests(unittest.TestCase):
    def test_counts_match_files(self):
        cat = DB.editions
        self.assertTrue(cat.available())
        counts = cat.counts()
        self.assertEqual(counts["sorts"], {2014: 561, 2024: 391})
        self.assertEqual(counts["classes"], {2014: 14, 2024: 12})
        self.assertEqual(sum(counts["dons"].values()), 296)

    def test_list_filters_by_mode(self):
        cat = DB.editions
        spells = cat.list("sorts", "2024")
        self.assertTrue(spells and all(s["edition"] == 2024 for s in spells))
        self.assertFalse(any(s.get("doublon_de") for s in spells))
        self.assertEqual(len(cat.subclasses_of("Guerrier", "2024")), 4)
        self.assertTrue(all(s["edition"] == 2014 for s in cat.subclasses_of("Guerrier", "2014")))
        fighter = cat.find("classes", "Guerrier", 2024)
        self.assertEqual(fighter["id"], "classe-fighter-2024-phb24")
        self.assertIs(cat.get("classe-fighter-2024-phb24"), fighter)
        wiz = cat.spells_for_class("classe-wizard-2024-phb24", "2024")
        self.assertTrue(wiz and all(s["edition"] == 2024 for s in wiz))
        masteries = [p["nom"] for p in cat.list("proprietes_des_armes", "2024")]
        self.assertIn("Sape", masteries)


class MulticlassTests(unittest.TestCase):
    def test_half_caster_rounding_per_edition(self):
        self.assertEqual(E.spell_slots([("half", 5, 2014), ("full", 3, 2014)])[:3], [4, 3, 2])   # 2 + 3 = 5
        self.assertEqual(E.spell_slots([("half", 5, 2024), ("full", 3, 2014)])[:3], [4, 3, 3])   # 3 + 3 = 6
        self.assertEqual(E.spell_slots([("half", 1, 2024)])[:1], [2])          # 2024 : sorts dès le niveau 1
        self.assertEqual(E.spell_slots([("half", 1, 2014)]), [0] * 9)
        self.assertEqual(E.spell_slots([("full", 5)]), E.spell_slots([("full", 5, 2014)]))

    def test_engine_mixed_classes(self):
        eng = make([("Paladin", 5, 2024), ("Magicien", 3, 2014)], mode="libre")
        self.assertEqual(eng.spell_slots()[:3], [4, 3, 3])
        self.assertEqual(eng.edition_problems(), [])
        eng14 = make([("Paladin", 5, 2014), ("Magicien", 3, 2014)])
        self.assertEqual(eng14.spell_slots()[:3], [4, 3, 2])
        self.assertTrue(make([("Paladin", 1, 2024)], mode="libre").spell_slots()[0] == 2)

    def test_validation_messages(self):
        # une fiche 2014 ou 2024 aligne toutes ses classes sur son édition ; seul le mode libre (masqué) les mélange
        eng = make([("Guerrier", 3, 2024), ("Roublard", 2, 2014)], mode="2014")
        self.assertEqual([c["edition"] for c in eng.ch.classes], [2014, 2014])
        self.assertEqual(eng.edition_problems(), [])
        mixed = [{"nom": "Guerrier", "edition": 2024}, {"nom": "Roublard", "edition": 2014}]
        self.assertEqual(len(E.validate_classes(mixed, "2014")), 1)
        self.assertEqual(E.validate_classes(mixed, "libre"), [])
        both = E.validate_classes([{"nom": "Guerrier", "edition": 2014}, {"nom": "Guerrier", "edition": 2024}], "libre")
        self.assertEqual(len(both), 1)


class HouseRuleTests(unittest.TestCase):
    def test_defaults_and_resolve(self):
        self.assertFalse(HR.defaults_for("2014")["potion_action_bonus"])
        self.assertTrue(HR.defaults_for("2024")["potion_action_bonus"])
        self.assertTrue(HR.defaults_for("libre")["inspiration_heroique"])
        r = HR.resolve({"potion_action_bonus": True, "inconnue": True}, "2014")
        self.assertTrue(r["potion_action_bonus"])
        self.assertNotIn("inconnue", r)

    def test_save_migration(self):
        old = Character.from_dict({"classes": [{"nom": "Guerrier", "niveau": 2, "sous_classe": "", "pv_jets": []}]})
        self.assertEqual(old.edition_mode, "2014")
        self.assertEqual(old.regles_optionnelles, HR.LEGACY)       # comportement des versions précédentes conservé
        self.assertEqual(old.classes[0]["edition"], 2014)
        new = Character.from_dict({"classes": [], "edition_mode": "libre", "regles_optionnelles": {"x": 1}})
        self.assertEqual((new.edition_mode, new.regles_optionnelles), ("libre", {}))
        back = Character.from_dict(make([("Guerrier", 1, 2024)], mode="libre").ch.to_dict())
        self.assertEqual((back.edition_mode, back.classes[0]["edition"]), ("libre", 2024))

    def test_potion_tile_follows_rule(self):
        eng = make([("Guerrier", 3, 2014)])
        eng.ch.equipement.append({"nom": "Potion de guérison", "qte": 1})
        self.assertFalse(any(t["id"] == "potion:boire" for t in eng.turn_actions()))
        eng.set_house_rule("potion_action_bonus", True)
        tile = next(t for t in eng.turn_actions() if t["id"] == "potion:boire")
        self.assertEqual((tile["type"], tile["disponible"]), ("Action bonus", True))

    def test_inspiration_tiles(self):
        eng = make([("Guerrier", 3, 2014)])
        ids = {t["id"]: t for t in eng.turn_actions()}
        self.assertIn("avantage", ids["inspiration:recevoir"]["description"])          # règle 2014
        eng.use_turn_action("inspiration:recevoir")
        self.assertTrue(eng.ch.inspiration)
        eng.set_house_rule("inspiration_heroique", True)
        tile = next(t for t in eng.turn_actions() if t["id"] == "inspiration:utiliser")
        self.assertIn("relancez", tile["description"])
        eng.use_turn_action("inspiration:utiliser")
        self.assertFalse(eng.ch.inspiration)

    def test_weapon_mastery_and_bg3_actions(self):
        eng = make([("Guerrier", 3, 2014)])
        slot = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        keys = [r["cle"] for r in eng.weapon_actions(slot)]
        self.assertFalse(any(k.startswith("botte_") for k in keys))
        self.assertEqual(eng.weapon_stats(slot)["botte"], "")
        eng.set_house_rule("maitrises_armes_2014", True)
        self.assertEqual(eng.weapon_actions(slot)[0]["cle"], "botte_sape")
        eng.set_house_rule("actions_arme_bg3", False)
        self.assertEqual([r["cle"] for r in eng.weapon_actions(slot)], ["botte_sape"])
        wiz = make([("Magicien", 3, 2014)], rules={"maitrises_armes_2014": True})        # arme non maîtrisée
        self.assertFalse(any(r["cle"].startswith("botte_") for r in wiz.weapon_actions(slot)))


class UnofficialSubclassTests(unittest.TestCase):
    def test_community_subclasses_marked_discreetly(self):
        tips = DB.subclass_tips("Barbare")
        self.assertIn("Voie du Météore", tips)
        self.assertNotIn("Voie du Berserker", tips)
        eng = make([("Barbare", 3, 2014)])
        summ = eng.subclass_summary("Barbare", "Voie du Météore")
        self.assertTrue(summ["non_officielle"])
        self.assertIn("non officielle", summ["source"])
        self.assertFalse(eng.subclass_summary("Barbare", "Voie du Berserker")["non_officielle"])
        # proposées dans tous les modes (aucun filtrage par édition)
        self.assertGreaterEqual(len(DB.subclasses("Barbare")), 13)


class RulesDialogSmoke(unittest.TestCase):
    def test_dialog_applies_mode_and_rules(self):
        sys.path.insert(0, str(ROOT / "tests"))
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.rules_dialog import RulesDialog, apply_table_defaults
        win = MainWindow(DB)
        dlg = RulesDialog(win)
        dlg._current_mode = lambda: "libre"
        dlg.checks["potion_action_bonus"].setChecked(True)
        dlg.accept()
        self.assertEqual(win.engine.ch.edition_mode, "libre")
        self.assertTrue(win.engine.rule_active("potion_action_bonus"))
        ch = Character()
        apply_table_defaults(ch, {"edition_defaut": "2024", "regles_defaut": {"actions_arme_bg3": False}})
        self.assertEqual((ch.edition_mode, ch.regles_optionnelles), ("2024", {"actions_arme_bg3": False}))


if __name__ == "__main__":
    unittest.main()
