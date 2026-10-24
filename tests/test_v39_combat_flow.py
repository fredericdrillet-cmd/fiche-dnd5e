"""Tests v39 : main principale / secondaire, mains nues, manœuvres, Attaque sournoise, Action astucieuse,
tuiles d'aptitudes de classe / sous-classe, ressources décomptées, résolution des sorts (attaque, JS, soins)."""
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


def make(cls, lvl, sub="", spells=None, **bonus):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race("Humain")
    eng.ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    for ab, v in bonus.items():
        eng.ch.bonus_divers[ab] = v
    for c, names in (spells or {}).items():
        eng.ch.sorts[c] = [{"nom": n, "prepare": True} for n in names]
    eng.normalize()
    return eng


def tiles(eng):
    return {t["id"]: t for t in eng.turn_actions()}


def weapons(eng, main="", off="", ranged=""):
    eng.ch.armes_cac[0] = {"nom": main, "bonus": 0, "maitrise": None}
    eng.ch.armes_cac[1] = {"nom": off, "bonus": 0, "maitrise": None}
    eng.ch.armes_distance[0] = {"nom": ranged, "bonus": 0, "maitrise": None}
    eng.normalize()


class TwoWeaponTests(unittest.TestCase):
    def test_offhand_needs_attack_then_no_modifier(self):
        eng = make("Guerrier", 1, Dextérité=4)
        weapons(eng, "Épée courte", "Dague")
        t = tiles(eng)
        self.assertFalse(t["arme:main_secondaire"]["disponible"])
        self.assertEqual(t["arme:main_secondaire"]["type"], "Action bonus")
        eng.use_turn_action("arme:armes_cac:0")
        self.assertTrue(tiles(eng)["arme:main_secondaire"]["disponible"])
        res = eng.use_turn_action("arme:main_secondaire")
        self.assertEqual(res["degats"].formula, "1d4")              # pas de modificateur positif
        self.assertTrue(eng.ch.tour_bonus)

    def test_two_weapon_fighting_style_adds_modifier(self):
        eng = make("Guerrier", 1, Dextérité=4)
        eng.ch.styles_combat["Guerrier|1"] = "Combat à deux armes"
        weapons(eng, "Épée courte", "Dague")
        st = eng.weapon_stats(eng.off_hand_slot(), offhand=True)
        self.assertEqual(st["degats"], "1d4+{}".format(eng.mod("Dextérité")))

    def test_negative_modifier_kept_offhand(self):
        eng = make("Guerrier", 1, Force=-4, Dextérité=-4)
        weapons(eng, "Hachette", "Hachette")
        self.assertIn("-", eng.weapon_stats(eng.off_hand_slot(), offhand=True)["degats"])

    def test_heavy_weapon_blocks_offhand(self):
        eng = make("Guerrier", 1)
        weapons(eng, "Épée longue", "Dague")
        eng.use_turn_action("arme:armes_cac:0")
        ok, why = eng.offhand_status()
        self.assertFalse(ok)
        self.assertIn("Légère", why)

    def test_unarmed_when_main_hand_empty(self):
        eng = make("Guerrier", 1)
        weapons(eng)
        self.assertIn("arme:mains_nues", tiles(eng))
        self.assertTrue(eng.use_turn_action("arme:mains_nues")["ok"])


class ClassTilesTests(unittest.TestCase):
    def test_battle_master_maneuvers_spend_superiority(self):
        eng = make("Guerrier", 3, "Maître de guerre", Force=4)
        weapons(eng, "Épée longue")
        eng.ch.options_classe = {"manoeuvres": ["Attaque menaçante", "Parade", "Attaque précise"]}
        eng.normalize()
        res = eng.use_turn_action("classe:manoeuvre:attaque-menacante")
        self.assertTrue(res["ok"])
        self.assertIn("1d8", res["degats"].formula)
        self.assertIn("1d8", res["degats"].formula.split("+", 1)[1])   # dé de supériorité ajouté à l'arme
        self.assertEqual(eng.resource_used("superiorite"), 1)
        self.assertEqual(eng.ch.tour_attaques, 1)
        eng.ch.ressources_utilisees["superiorite"] = 4
        self.assertFalse(tiles(eng)["classe:manoeuvre:parade"]["disponible"])

    def test_maneuver_choice_is_a_missing_choice(self):
        eng = make("Guerrier", 3, "Maître de guerre")
        self.assertTrue(any("Manœuvres" in m["message"] for m in eng.missing_choices()))

    def test_sneak_attack_once_per_turn_with_finesse(self):
        eng = make("Roublard", 5, Dextérité=4)
        weapons(eng, "Massue")
        self.assertFalse(tiles(eng)["classe:sournoise"]["disponible"])
        weapons(eng, "Rapière")
        res = eng.use_turn_action("classe:sournoise")
        self.assertTrue(res["degats"].formula.endswith("3d6"))
        eng.ch.tour_action = False
        self.assertFalse(tiles(eng)["classe:sournoise"]["disponible"])
        eng.new_round()
        self.assertTrue(tiles(eng)["classe:sournoise"]["disponible"])

    def test_cunning_action_tiles(self):
        t = tiles(make("Roublard", 2))
        for cid in ("classe:ruse_foncer", "classe:ruse_desengager", "classe:ruse_cacher"):
            self.assertEqual(t[cid]["type"], "Action bonus")

    def test_rage_spends_and_frenzy_requires_rage(self):
        eng = make("Barbare", 3, "Voie du Berserker")
        weapons(eng, "Hache à deux mains")
        self.assertFalse(tiles(eng)["classe:cap:frenesie"]["disponible"])
        eng.use_turn_action("classe:rage")
        self.assertEqual(eng.resource_used("rage"), 1)
        eng.new_round()
        self.assertTrue(tiles(eng)["classe:cap:frenesie"]["disponible"])

    def test_monk_ki_tiles(self):
        eng = make("Moine", 5)
        eng.use_turn_action("classe:deluge_coups")
        self.assertEqual(eng.resource_used("ki"), 1)
        self.assertIn("classe:coup_etourdissant", tiles(eng))

    def test_subclass_uses_trackers(self):
        eng = make("Occultiste", 6, "Le Fiélon")
        self.assertEqual(eng.class_action_state(next(a for a in eng.class_actions()
                                                      if a["id"] == "cap:chance_tenebres"))["cout_txt"],
                         "1 utilisation")
        eng.use_class_action("cap:chance_tenebres")
        self.assertFalse(next(a for a in eng.class_actions() if a["id"] == "cap:chance_tenebres")["disponible"])
        eng.short_rest()
        self.assertTrue(next(a for a in eng.class_actions() if a["id"] == "cap:chance_tenebres")["disponible"])

    def test_metamagic_option_tiles(self):
        eng = make("Ensorceleur", 3)
        eng.ch.options_classe = {"metamagie": ["Sort accéléré", "Sort jumeau"]}
        eng.normalize()
        a = next(a for a in eng.class_actions() if a["nom"] == "Métamagie : Sort accéléré")
        self.assertEqual(a["cout_txt"], "2 points de sorcellerie")

    def test_beast_natural_weapon(self):
        eng = make("Barbare", 3, "Voie de la Bête", Force=4)
        eng.use_turn_action("classe:rage")
        eng.new_round()
        res = eng.use_turn_action("classe:cap:morsure_bete")
        self.assertTrue(res["ok"])
        self.assertTrue(res["degats"].formula.startswith("1d8"))


class SpellResolutionTests(unittest.TestCase):
    def test_save_spell_shows_dc_and_scales(self):
        eng = make("Magicien", 5, spells={"Magicien": ["Mains brûlantes"]})
        res = eng.spell_resolution("Mains brûlantes", 3)
        self.assertEqual(res["mode"], "sauvegarde")
        self.assertEqual(res["carac"], "Dextérité")
        self.assertEqual(res["dd"], eng.caster("Magicien")["dc"])
        self.assertEqual(res["degats"].formula, "5d6")
        self.assertTrue(res["reussite"].startswith("Moitié des dégâts"))

    def test_attack_spell_and_rays(self):
        eng = make("Occultiste", 11, "Le Fiélon", spells={"Occultiste": ["Décharge occulte"]})
        res = eng.spell_resolution("Décharge occulte")
        self.assertEqual((res["mode"], res["rayons"]), ("attaque", 3))
        self.assertEqual(res["rayon_degats"].formula, "1d10")

    def test_heal_spell(self):
        eng = make("Clerc", 5, spells={"Clerc": ["Soins"]})
        res = eng.spell_resolution("Soins", 2)
        self.assertEqual(res["mode"], "soins")
        self.assertTrue(res["soins"].formula.startswith("2d8"))

    def test_slot_choices_dialog_lists_levels(self):
        from ui.spell_flow import slot_choices
        eng = make("Magicien", 5, spells={"Magicien": ["Mains brûlantes"]})
        choices = slot_choices(eng, DB.find_spell("Mains brûlantes"))
        self.assertEqual([lvl for lvl, _ in choices], [1, 2, 3])
        self.assertIn("5d6", choices[2][1])
        warlock = make("Occultiste", 5, "Le Fiélon", spells={"Occultiste": ["Représailles infernales"]})
        self.assertEqual([lvl for lvl, _ in slot_choices(warlock, DB.find_spell("Représailles infernales"))], [3])

    def test_conditional_rider_from_hunters_mark(self):
        eng = make("Rôdeur", 2)
        weapons(eng, "Épée courte")
        eng.add_effect("marque_chasseur_lanceur")
        spec = eng.weapon_damage_spec(eng.main_hand_slot())
        self.assertEqual(spec.options, [("Marque du chasseur (vous marquez)", "1d6")])


if __name__ == "__main__":
    unittest.main()
