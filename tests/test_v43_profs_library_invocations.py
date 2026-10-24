"""Tests v43 : maîtrises (multiclassage, sous-classes), équipement non maîtrisé (avertissements, désavantage,
sorts bloqués), arme non maîtrisée sans bonus de maîtrise, bibliothèque ajout / retrait, manifestations occultes
dans l'assistant de niveau."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from test_v40_wizard_saves import full_spells, make  # noqa: E402
from test_v41_grimoire_combat import window  # noqa: E402
from core.engine import Engine  # noqa: E402
from core.proficiencies import ARMOR_WARNING, CAST_BLOCKED, WEAPON_WARNING  # noqa: E402


def multi(*classes):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race("Humain")
    eng.ch.classes = [{"nom": c, "niveau": n, "sous_classe": sub, "pv_jets": []} for c, n, sub in classes]
    eng.normalize()
    return eng


class ProficiencyTests(unittest.TestCase):
    def test_multiclass_profs_are_limited(self):
        eng = multi(("Magicien", 3, ""), ("Guerrier", 1, ""))
        summ = eng.proficiency_summary()
        self.assertIn("Armures intermédiaires", summ["armures"])
        self.assertNotIn("Armures lourdes", summ["armures"])         # pas de lourde en multiclassage Guerrier
        self.assertNotIn("Toutes les armures", summ["armures"])
        modes = {s["mode"] for s in summ["sources"]}
        self.assertEqual(modes >= {"depart", "multiclassage"}, True)

    def test_subclass_profs(self):
        eng = multi(("Clerc", 1, "Domaine de la Guerre"))
        summ = eng.proficiency_summary()
        self.assertIn("Armures lourdes", summ["armures"])
        self.assertIn("Armes de guerre", summ["armes"])

    def test_unproficient_armor_blocks_spells(self):
        eng = make("Magicien", 3, spells={"Magicien": ["Trait de feu", "Projectile magique"]})
        eng.ch.armure["nom"] = next(n for n, a in DB.armors.items() if a.get("categorie") == "intermédiaire")
        eng.normalize()
        gear = eng.unproficient_gear()
        self.assertEqual(gear[0]["message"], ARMOR_WARNING)
        self.assertEqual(eng.spell_block_reason(), ("armure", CAST_BLOCKED))
        self.assertFalse(eng.cast_spell("Projectile magique")["ok"])
        tile = next(t for t in eng.turn_actions() if t["id"] == "sort:Trait de feu")
        self.assertFalse(tile["disponible"])
        self.assertEqual(tile["raison"], CAST_BLOCKED)
        self.assertIn("Armure non maîtrisée", " ".join(eng.attack_mods()["desavantage"]))
        self.assertTrue(eng.save_mods("Dextérité")["desavantage"])
        self.assertEqual(eng.item_proficiency_warning(eng.ch.armure["nom"]), ARMOR_WARNING)

    def test_unproficient_shield(self):
        eng = make("Magicien", 3)
        eng.ch.armure["bouclier"] = True
        eng.normalize()
        self.assertEqual(eng.unproficient_gear()[0]["type"], "bouclier")
        self.assertTrue(eng.spells_blocked())

    def test_unproficient_weapon_no_proficiency_bonus(self):
        eng = make("Magicien", 3)
        eng.ch.armes_cac[0] = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        eng.normalize()
        st = eng.weapon_stats(eng.ch.armes_cac[0])
        self.assertFalse(st["maitrise"])
        self.assertEqual(st["attaque"], eng.mod(st["carac"]))
        self.assertEqual(eng.item_proficiency_warning("Épée longue"), WEAPON_WARNING)
        tile = next(t for t in eng.turn_actions() if t["id"] == "arme:armes_cac:0")
        self.assertTrue(tile["nom"].startswith("⚠"))
        self.assertIn("bonus de maîtrise ne s'applique pas", tile["description"])


class LibraryAndWizardTests(unittest.TestCase):
    def test_library_toggle_add_remove(self):
        eng = make("Magicien", 3)
        win = window(eng)
        mt = win.magic_tab
        mt._lib_rows = [{"nom": "Trait de feu", "sort": DB.find_spell("Trait de feu")}]
        mt._selected_spell = lambda table, rows: (rows[0] if rows and table is mt.library else None)
        mt.all_chk.isChecked = lambda: True
        mt._on_add()
        self.assertTrue(any(s["nom"] == "Trait de feu" for s in eng.ch.sorts["Magicien"]))
        mt._on_add()
        self.assertFalse(any(s["nom"] == "Trait de feu" for s in eng.ch.sorts.get("Magicien", [])))

    def test_wizard_invocations(self):
        from ui.levelup_dialog import LevelUpDialog
        eng = make("Occultiste", 1, "Le Fiélon")
        full_spells(eng, "Occultiste")
        d = LevelUpDialog(window(eng))
        kinds = [m["kind"] for m in d.pending()]
        self.assertIn("manifestations", kinds)
        self.assertEqual(d._inv_slots(), 2)
        opts = [m["nom"] for m in eng.level_invocation_options(d.sim)]
        self.assertNotIn("Lame assoiffée", opts)                   # pacte et niveau 5 requis
        self.assertIn("Vision du diable", opts)
        self.assertIn("Prérequis", d.invocation_tip("Vision du diable"))
        d._set_invocation(0, "Armure d'ombres")
        d._set_invocation(1, "Armure d'ombres")                    # doublon refusé
        self.assertEqual(d.sim.ch.manifestations, ["Armure d'ombres"])
        d._set_invocation(1, "Vision du diable")
        self.assertNotIn("manifestations", [m["kind"] for m in d.pending()])


if __name__ == "__main__":
    unittest.main()
