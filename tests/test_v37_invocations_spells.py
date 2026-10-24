"""Tests v37 : manifestations occultes (prérequis, Décharge occulte, sorts accordés, Livre des secrets anciens,
actions et passifs) et règles chiffrées des sorts (durées, rituels, surclassement, modificateurs)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core import dice as D  # noqa: E402
from core import rules as R  # noqa: E402
from core.engine import Engine  # noqa: E402


def warlock(lvl=5, cha=18, pact="", invocations=(), blast=True, sub="Le Fiélon"):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race("Humain")
    eng.ch.classes = [{"nom": "Occultiste", "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng.ch.bonus_divers["Charisme"] = cha - eng.score("Charisme")
    eng.ch.pacte = pact
    if blast:
        eng.ch.sorts["Occultiste"] = [{"nom": "Décharge occulte", "prepare": True}]
    eng.ch.manifestations = list(invocations)
    eng.normalize()
    return eng


class EldritchBlastTests(unittest.TestCase):
    def test_agonizing_adds_charisma_per_ray(self):
        eng = warlock(11, 18, invocations=["Décharge déchirante"])
        st = eng.cantrip_stats("Décharge occulte")
        self.assertEqual(st["degats"], "3 × 1d10+4")            # niveau 11 : 3 rayons, CHA 18 -> +4 par rayon
        self.assertEqual(st["degats_rayon"], "1d10+4")
        self.assertEqual(D.parse_damage(st["degats"]), ([(1, 3, 10)], 12))

    def test_rays_scale_with_character_level(self):
        for lvl, rays in ((1, 1), (5, 2), (11, 3), (17, 4)):
            self.assertEqual(warlock(lvl).cantrip_stats("Décharge occulte")["rayons"], rays)

    def test_spear_grasp_lethargy_repelling_on_tile(self):
        eng = warlock(5, invocations=["Lance occulte", "Étreinte de Hadar", "Lance de léthargie", "Décharge répulsive"])
        st = eng.cantrip_stats("Décharge occulte")
        self.assertEqual(st["portee"], "90 m")
        text = " ".join(st["effets"])
        for frag in ("repousse la cible de 3 m", "attire la cible de 3 m", "vitesse de la cible −3 m"):
            self.assertIn(frag, text)
        tile = next(t for t in eng.turn_actions() if t["id"] == "sort:Décharge occulte")
        self.assertIn("2 rayons", tile["description"])
        self.assertIn("90 m", tile["description"])

    def test_blast_invocations_require_the_cantrip(self):
        eng = warlock(5, blast=False, invocations=["Décharge déchirante"])
        self.assertEqual(eng.manifestation_status("Décharge déchirante"),
                         ("ko", "requiert le sort mineur Décharge occulte"))

    def test_old_save_name_migrated(self):
        eng = warlock(5, invocations=["Etreinte de Hadar"])
        self.assertEqual(eng.ch.manifestations, ["Étreinte de Hadar"])


class InvocationSheetTests(unittest.TestCase):
    def test_data_has_54_official_invocations_with_sources(self):
        self.assertEqual(len(DB.manifestations), 54)
        self.assertTrue(all(m["source"] in ("PHB", "XGtE", "TCoE") for m in DB.manifestations.values()))
        self.assertEqual(DB.manifestations["Attaque occulte"]["niveau"], 5)
        self.assertEqual(DB.manifestations["Voleur des cinq destinées"]["sorts"][0]["sort"], "Fléau")

    def test_devils_sight_in_vision_box(self):
        dv = warlock(2, invocations=["Vision du diable"]).darkvision()
        self.assertEqual(dv["portee"], 36.0)
        self.assertTrue(dv["magique"])

    def test_beguiling_influence_skills(self):
        rows = {r["nom"]: r for r in warlock(2, invocations=["Présence captivante"]).skill_rows()}
        self.assertTrue(rows["Tromperie"]["maitrise"] and rows["Persuasion"]["maitrise"])

    def test_armor_of_shadows_at_will_without_slot(self):
        eng = warlock(2, invocations=["Armure d'ombres"])
        g = eng.granted_spells()[0]
        self.assertEqual((g["nom"], g["emplacement"], g["cle"]), ("Armure de mage", False, ""))
        tile = next(t for t in eng.turn_actions() if t["id"] == "sort:Armure de mage")
        self.assertFalse(tile["ref"]["emplacement"])
        before = eng.armor_class()[0]
        res = eng.cast_spell("Armure de mage", False, "soi", "armure_mage")
        self.assertTrue(res["ok"])
        self.assertEqual(eng.armor_class()[0], 13 + eng.mod("Dextérité"))
        self.assertGreaterEqual(eng.armor_class()[0], before)

    def test_once_per_long_rest_grants(self):
        eng = warlock(7, invocations=["Sculpteur de chair", "Fuite de l'escamoteur"])
        grants = {g["nom"]: g for g in eng.granted_spells()}
        self.assertTrue(grants["Métamorphose"]["emplacement"])                # emplacement d'occultiste
        self.assertFalse(grants["Liberté de mouvement"]["emplacement"])       # gratuit, 1 fois
        key = grants["Liberté de mouvement"]["cle"]
        self.assertEqual(eng.granted_limit_left(key), 1)
        eng.spend_granted_limit(key)
        tile = next(t for t in eng.turn_actions() if t["id"] == "sort:Liberté de mouvement")
        self.assertFalse(tile["disponible"])
        eng.long_rest()
        self.assertEqual(eng.granted_limit_left(key), 1)

    def test_chains_of_carceri_at_will(self):
        eng = warlock(15, pact="Pacte de la chaîne", invocations=["Chaîne des carcères"])
        g = eng.granted_spells()[0]
        self.assertEqual(g["nom"], "Immobilisation de monstre")
        self.assertTrue(g["usage"].startswith("À volonté"))
        self.assertEqual(g["cle"], "")

    def test_thirsting_blade_and_lifedrinker(self):
        eng = warlock(12, pact="Pacte de la lame", invocations=["Lame assoiffée", "Buveuse de vie"])
        self.assertEqual(eng.attacks_per_action(), 2)
        self.assertTrue(any("+4 dégâts nécrotiques" in p["description"] for p in eng.class_passives()))

    def test_eldritch_smite_uses_pact_slot(self):
        eng = warlock(5, pact="Pacte de la lame", invocations=["Attaque occulte"])
        a = next(a for a in eng.class_actions() if a["id"] == "inv:attaque_occulte")
        self.assertEqual(a["formule"], "4d8")                    # pacte niveau 3 : 1d8 + 3d8
        eng.use_class_action("inv:attaque_occulte")
        self.assertEqual(eng.ch.pacte_utilises, 1)

    def test_tomb_of_levistus_temp_hp_and_short_rest(self):
        eng = warlock(6, invocations=["Tombe de Levistus"])
        eng.use_class_action("inv:tombe_levistus")
        self.assertEqual(eng.ch.pv_temporaires, 60)
        self.assertFalse(next(a for a in eng.class_actions() if a["id"] == "inv:tombe_levistus")["disponible"])
        self.assertEqual(eng.resource_used("inv:tombe_levistus"), 1)
        eng.short_rest()
        self.assertEqual(eng.resource_used("inv:tombe_levistus"), 0)

    def test_maddening_hex_needs_hex_and_uses_charisma(self):
        eng = warlock(5, invocations=["Maléfice accablant"])
        self.assertEqual(eng.manifestation_status("Maléfice accablant")[0], "ko")
        eng.ch.sorts["Occultiste"].append({"nom": "Maléfice", "prepare": True})
        a = next(a for a in eng.class_actions() if a["id"] == "inv:malefice_accablant")
        self.assertIn("4 dégâts psychiques", a["description"])
        hexblade = warlock(5, invocations=["Maléfice accablant"], sub="La Lame maudite")
        self.assertEqual(hexblade.manifestation_status("Maléfice accablant")[0], "ok")

    def test_talisman_uses_equal_proficiency_bonus(self):
        eng = warlock(12, pact="Pacte du talisman", invocations=["Protection du talisman", "Lien du talisman"])
        totals = {t["key"]: t["total"] for t in eng.resource_trackers()}
        self.assertEqual(totals["inv:protection_talisman"], eng.prof)
        self.assertEqual(totals["inv:lien_talisman"], eng.prof)

    def test_book_of_ancient_secrets(self):
        eng = warlock(5, pact="Pacte du grimoire", invocations=["Livre des secrets anciens"])
        self.assertEqual(eng.ritual_book_missing(), 2)
        self.assertTrue(any("Livre des secrets anciens" in m["message"] for m in eng.missing_choices()))
        self.assertFalse(eng.ritual_book_can_add("Bouclier")[0])          # pas un rituel
        self.assertFalse(eng.ritual_book_can_add("Augure")[0])            # niveau 2 avant les deux niveau 1
        self.assertTrue(eng.add_ritual("Alarme") and eng.add_ritual("Appel de familier"))
        self.assertEqual(eng.ritual_book_missing(), 0)
        self.assertTrue(eng.add_ritual("Augure"))                          # niveau ≤ 3 (moitié de 5, arrondie)
        self.assertFalse(eng.ritual_book_can_add("Fusion dans la pierre")[0] and eng.ritual_book_max_level() < 3)
        names = [g["nom"] for g in eng.granted_spells()]
        self.assertIn("Alarme", names)
        self.assertNotIn("sort:Alarme", [t["id"] for t in eng.turn_actions()])   # rituel : hors combat

    def test_gift_of_depths_swim_speed(self):
        eng = warlock(5, invocations=["Don des profondeurs"])
        self.assertEqual(eng.swim_speed(), eng.speed())
        self.assertEqual([g["nom"] for g in eng.granted_spells()], ["Respiration aquatique"])


class SpellRuleTests(unittest.TestCase):
    def test_ritual_flags_fixed(self):
        self.assertFalse(DB.find_spell("Rappel à la vie")["rituel"])
        self.assertFalse(DB.find_spell("Réincarnation")["rituel"])
        self.assertTrue(DB.find_spell("Alarme")["rituel"])

    def test_durations(self):
        self.assertEqual(DB.find_spell("Boule de feu")["duree"], "Instantanée")
        self.assertEqual(DB.find_spell("Hâte")["duree"], "Concentration, jusqu'à 1 minute")
        self.assertEqual(DB.find_spell("Armure de mage")["duree"], "8 heures")
        missing = [n for n, s in DB.spells.items() if not s["duree"] and not s.get("hors_corpus")]
        self.assertEqual(missing, [])

    def test_upcasting(self):
        sc = R.spell_scaling(DB.find_spell("Boule de feu"), 5)
        self.assertEqual(sc["degats"], "10d6")
        self.assertEqual(R.spell_scaling(DB.find_spell("Désintégration"), 7)["degats"], "13d6+40")
        self.assertEqual(R.spell_scaling(DB.find_spell("Arme spirituelle"), 4)["degats"], "2d8")
        self.assertEqual(R.spell_scaling(DB.find_spell("Arme spirituelle"), 3)["degats"], "1d8")
        self.assertEqual(R.spell_scaling(DB.find_spell("Lame d'ombres"), 5)["degats"], "4d8")
        self.assertEqual(R.spell_scaling(DB.find_spell("Projectile magique"), 4)["projectiles"], 6)
        self.assertEqual(R.spell_scaling(DB.find_spell("Soins"), 3)["soins"], "3d8")
        self.assertEqual(R.spell_scaling(DB.find_spell("Châtiment tonitruant"), 3)["degats"], "2d6")  # sans surclassement

    def test_modifier_only_when_rule_says_so(self):
        eng = warlock(5)
        self.assertEqual(eng.spell_values("Boule de feu")["degats"], "8d6")
        self.assertEqual(eng.spell_values("Soins", 1)["soins"], "1d8+4")
        self.assertEqual(eng.spell_values("Arme spirituelle", 2)["degats"], "1d8+4")
        self.assertEqual(eng.cantrip_stats("Pierre magique")["degats"], "1d6+4")     # pas d'échelle de niveau
        self.assertEqual(eng.cantrip_stats("Trait de feu")["degats"], "2d10")         # pas de modificateur

    def test_evocation_and_potent_spellcasting(self):
        wiz = Engine(DB, Engine.new_character(DB))
        wiz.ch.classes = [{"nom": "Magicien", "niveau": 10, "sous_classe": "École d'Évocation", "pv_jets": []}]
        wiz.normalize()
        vals = wiz.spell_values("Boule de feu")
        if any(n.startswith("evocation renforcee") for n in wiz.unlocked_feature_names()):
            self.assertTrue(vals["bonus"])

    def test_magic_missile_formula(self):
        vals = warlock(5).spell_values("Projectile magique", 2)
        self.assertEqual(vals["degats"], "4 × (1d4+1)")
        self.assertEqual(D.parse_damage(vals["degats"]), ([(1, 4, 4)], 4))


class UiTests(unittest.TestCase):
    def test_window_refresh_with_invocations(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        eng = warlock(9, pact="Pacte du grimoire", invocations=["Livre des secrets anciens", "Vision du diable",
                                                                 "Décharge déchirante", "Armure d'ombres",
                                                                 "Présent des sauveurs"])
        eng.add_ritual("Alarme")
        win = mw.MainWindow(DB)
        win.engine = eng
        win.refresh_all()
        panel = win.magic_tab.manif
        panel.refresh()
        self.assertIn("1 à choisir", panel.book.title())
        self.assertEqual(panel._book_rows, ["Alarme"])
        self.assertIn("36", win.combat_tab.stat_labels["vision"].text())


if __name__ == "__main__":
    unittest.main()
