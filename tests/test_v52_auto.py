"""v52 : effets appliqués automatiquement — dons (2014 / 2024, Faveurs épiques) et aptitudes de classe."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")
MACE = {"nom": "Masse d’armes", "bonus": 0, "maitrise": None}


def sheet(cls, lvl, edition="2024", sub=""):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    return eng


def give(eng, feat, carac="", index=0):
    sid = [s["id"] for s in eng.asi_slots()][index]
    eng.ch.ameliorations[sid] = {"mode": "don", "don": feat, "don_carac": carac}


class FeatTests(unittest.TestCase):
    def test_tough_2024_and_2014_not_doubled(self):
        for ed, feat in (("2024", "Robuste (2024)"), ("2014", "Robuste")):
            eng = sheet("Guerrier", 4, ed)
            hp = eng.hp_max()
            give(eng, feat)
            self.assertEqual(eng.hp_max(), hp + 8, ed)

    def test_resilient_2024_save_and_ability(self):
        eng = sheet("Guerrier", 4)
        give(eng, "Résilient (2024)", "Sagesse")
        row = next(r for r in eng.save_rows() if r["carac"] == "Sagesse")
        self.assertTrue(row["maitrise"])
        self.assertEqual(eng.score_parts("Sagesse")["asi"], 1)

    def test_observant_proficiency_then_expertise(self):
        eng = sheet("Guerrier", 4)
        give(eng, "Observateur (2024)", "Sagesse")
        eng.set_class_option("don:observateur_2024:competence", 0, "Perception")
        row = next(r for r in eng.skill_rows() if r["nom"] == "Perception")
        self.assertEqual((row["maitrise"], row["expertise"]), (True, False))
        eng.ch.competences["Perception"] = {"maitrise": True, "expertise": False}
        row = next(r for r in eng.skill_rows() if r["nom"] == "Perception")
        self.assertTrue(row["expertise"])

    def test_skilled_tools_and_missing_choice(self):
        eng = sheet("Guerrier", 4)
        give(eng, "Doué (2024)")
        msgs = [m["message"] for m in eng.missing_choices()]
        self.assertTrue(any("Doué" in m for m in msgs))
        for i, pick in enumerate(("Discrétion", "Outils de voleur", "Histoire")):
            eng.set_class_option("don:doue_2024:maitrises", i, pick)
        self.assertIn("Outils de voleur", eng.feat_tools())
        self.assertTrue(next(r for r in eng.skill_rows() if r["nom"] == "Histoire")["maitrise"])

    def test_fey_touched_spells_free_once(self):
        eng = sheet("Magicien", 4)
        give(eng, "Affinité féérique", "Intelligence")
        key = "don:affinite_feerique:sort"
        pick = next(iter(next(s for s in eng.option_sets() if s["key"] == key)["options"]))
        eng.set_class_option(key, 0, pick)
        names = [g["nom"] for g in eng.granted_spells() if g["source"].startswith("Don")]
        self.assertEqual(len(names), 2)
        grant = next(g for g in eng.granted_spells() if g["source"].startswith("Don"))
        self.assertEqual(eng.granted_limit_left(grant["cle"]), 1)
        eng.spend_granted_limit(grant["cle"])
        self.assertEqual(eng.granted_limit_left(grant["cle"]), 0)

    def test_magic_initiate_lists(self):
        eng = sheet("Guerrier", 1)                       # don d'origine de l'historique 2024 par défaut
        if eng.origin_feat() != "Initié à la magie (2024)":
            self.skipTest("historique par défaut sans Initié à la magie")
        eng.set_class_option("don:initie_a_la_magie_2024:liste", 0, "Clerc")
        eng.set_class_option("don:initie_a_la_magie_2024:carac", 0, "Sagesse")
        keys = [s["key"] for s in eng.option_sets()]
        self.assertIn("don:initie_a_la_magie_2024:mineurs", keys)
        self.assertIn("don:initie_a_la_magie_2024:sort1", keys)

    def test_epic_boons(self):
        eng = sheet("Guerrier", 19)
        sid = [s["id"] for s in eng.asi_slots()][-1]
        eng.ch.bonus_divers = {}
        eng.ch.scores_achat["Force"] = 15
        hp = eng.hp_max()
        eng.ch.ameliorations[sid] = {"mode": "don", "don": "Faveur de vigueur", "don_carac": "Force"}
        self.assertEqual(eng.hp_max(), hp + 40)
        eng.ch.ameliorations[sid] = {"mode": "don", "don": "Faveur de vitesse", "don_carac": "Force"}
        self.assertEqual(eng.speed(), 18.0)
        eng.ch.ameliorations[sid] = {"mode": "don", "don": "Faveur de récupération", "don_carac": "Force"}
        eng.ch.pv_actuels = 5
        eng.take_damage(100)
        self.assertGreater(eng.ch.pv_actuels, 1)               # Dernier rempart
        eng.ch.pv_actuels = 5
        eng.take_damage(100)
        self.assertEqual(eng.ch.pv_actuels, 0)                 # une seule fois par repos long
        eng.ch.ameliorations[sid] = {"mode": "don", "don": "Faveur de résistance aux énergies", "don_carac": "Force"}
        eng.set_class_option("don:faveur_de_resistance_aux_energies:resistances", 0, "feu")
        self.assertIn("feu", [t for t, _ in eng.defenses()["resistances"]])

    def test_boon_raises_cap_to_30(self):
        eng = sheet("Guerrier", 19)
        eng.ch.scores_achat["Force"] = 15
        eng.ch.bonus_divers = {}
        slots = [s["id"] for s in eng.asi_slots()]
        for sid in slots[:-1]:
            eng.ch.ameliorations[sid] = {"mode": "plus2", "a1": "Force"}
        eng.ch.ameliorations[slots[-1]] = {"mode": "don", "don": "Faveur de compétence", "don_carac": "Force"}
        self.assertEqual(eng.score("Force"), 21)
        self.assertTrue(all(r["maitrise"] for r in eng.skill_rows()))

    def test_luck_and_armor_feats(self):
        eng = sheet("Magicien", 4)
        give(eng, "Protection intermédiaire (2024)", "Force")
        self.assertTrue(any("intermédiaire" in a.lower() for a in eng.armor_proficiencies()))
        eng2 = sheet("Guerrier", 4)
        eng2.ch.historique = next((n for n, b in eng2.db.backgrounds.items()
                                   if eng2.db.backgrounds[n].get("edition") == 2024), eng2.ch.historique)
        give(eng2, "Chanceux (2024)")
        tr = next(t for t in eng2.resource_trackers() if t["key"] == "don_chance")
        self.assertEqual(tr["total"], eng2.prof)


class ClassFeatureTests(unittest.TestCase):
    def test_saves(self):
        self.assertTrue(all(r["maitrise"] for r in sheet("Moine", 14, "2014").save_rows()))
        rogue = {r["carac"]: r["maitrise"] for r in sheet("Roublard", 15).save_rows()}
        self.assertTrue(rogue["Sagesse"] and rogue["Charisme"])
        rogue14 = {r["carac"]: r["maitrise"] for r in sheet("Roublard", 15, "2014").save_rows()}
        self.assertTrue(rogue14["Sagesse"])
        dex = next(r for r in sheet("Barbare", 2, "2014").save_rows() if r["carac"] == "Dextérité")
        self.assertEqual(dex["etat"], "avantage")

    def test_weapon_riders(self):
        self.assertIn("+1d8", sheet("Paladin", 11, "2014").weapon_damage_spec(MACE).formula)
        self.assertEqual(sheet("Clerc", 8, "2014", "Domaine de la Vie").weapon_damage_spec(MACE).options[-1][1], "1d8")
        cleric = sheet("Clerc", 7)
        self.assertIn("frappes_benies", [s["key"] for s in cleric.option_sets()])
        cleric.ch.options_classe = {"frappes_benies": ["Frappe divine"]}
        self.assertTrue(any(o[0].startswith("Frappe divine") for o in cleric.weapon_damage_spec(MACE).options))

    def test_ranger_monk_barbarian_sorcerer(self):
        ranger = sheet("Rôdeur", 9)
        self.assertEqual(ranger.speed(), 12.0)
        self.assertEqual(ranger.expertise_allowed(), 3)
        self.assertEqual(sheet("Moine", 20).score_parts("Dextérité")["champion"], 4)
        barb = sheet("Barbare", 15)
        barb.ch.ressources_utilisees["rage"] = 3
        barb.roll_initiative(10)
        self.assertEqual(barb.ch.ressources_utilisees["rage"], 0)
        sorc = sheet("Ensorceleur", 6)
        sorc.ch.ressources_utilisees["sorcellerie"] = 5
        sorc.short_rest()
        self.assertEqual(sorc.ch.ressources_utilisees["sorcellerie"], 2)
        sorc.ch.ressources_utilisees["sorcellerie"] = 5
        sorc.short_rest()
        self.assertEqual(sorc.ch.ressources_utilisees["sorcellerie"], 5)     # une fois par repos long


class UiSmoke(unittest.TestCase):
    def test_progression_tab_shows_feat_choices(self):
        sys.path.insert(0, str(ROOT / "tests"))
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        eng = sheet("Guerrier", 4)
        give(eng, "Doué (2024)")
        win.engine.ch.__dict__.update(eng.ch.__dict__)
        win.engine.normalize()
        win.progression_tab.refresh()
        self.assertTrue(win.progression_tab.choice_box.isVisible())
        win.combat_tab.refresh()


if __name__ == "__main__":
    unittest.main()


class DeathSaveTests(unittest.TestCase):
    def test_death_saves_applied(self):
        eng = sheet("Guerrier", 3, "2014")
        eng.ch.pv_actuels = 5
        eng.take_damage(8)
        eng.apply_death_save(12)
        self.assertEqual(eng.ch.mort_reussites, 1)
        eng.apply_death_save(1)
        self.assertEqual(eng.ch.mort_echecs, 2)
        eng.take_damage(3)                                  # dégâts à 0 PV : un échec
        self.assertEqual(eng.ch.mort_echecs, 3)
        eng.apply_death_save(20)
        self.assertEqual((eng.ch.pv_actuels, eng.ch.mort_echecs), (1, 0))
        eng.ch.pv_actuels = 5
        self.assertIn("Mort instantanée", eng.take_damage(5 + eng.hp_max()))

    def test_durable_advantage(self):
        eng = sheet("Guerrier", 4)
        self.assertEqual(eng.death_save_spec().mode, "")
        give(eng, "Gaillard", "Constitution")
        self.assertEqual(eng.death_save_spec().mode, "avantage")


class SubclassTests(unittest.TestCase):
    def test_always_prepared_2024(self):
        eng = sheet("Clerc", 5)
        eng.ch.classes[0]["sous_classe"] = "Domaine de la vie"
        eng.normalize()
        self.assertIn("Retour à la vie (2024)", eng.domain_spells(eng.ch.classes[0]))
        land = sheet("Druide", 3)
        land.ch.classes[0]["sous_classe"] = "Cercle de la terre"
        land.normalize()
        self.assertEqual(sorted(land.land_terrains(land.ch.classes[0])), ["Aride", "Polaire", "Tempérée", "Tropicale"])
        self.assertEqual(len(land.domain_spells(land.ch.classes[0])), 3)

    def test_renamed_subclasses_keep_mechanics(self):
        rogue = sheet("Roublard", 3)
        rogue.ch.classes[0]["sous_classe"] = "Âme acérée"
        rogue.normalize()
        self.assertIn("psionique", {t["key"] for t in rogue.resource_trackers()})

    def test_champion_crit_and_fiend(self):
        champ = sheet("Guerrier", 15)
        champ.ch.classes[0]["sous_classe"] = "Champion"
        champ.normalize()
        spec = champ.weapon_attack_spec({"nom": "Épée longue", "bonus": 0, "maitrise": None})
        self.assertEqual(spec.crit_min, 18)
        from core import dice as D
        class Rng:
            def randint(self, a, b):
                return 18 if b == 20 else 1
        self.assertEqual(D.roll_d20(spec, Rng()).critical, "succes")
        fiend = sheet("Occultiste", 10)
        fiend.ch.classes[0]["sous_classe"] = "Protecteur Fiélon"
        fiend.normalize()
        fiend.ch.options_classe = {"resistance_fielonne": ["feu"]}
        self.assertIn("feu", [t for t, _ in fiend.defenses()["resistances"]])

    def test_spells_2024_have_rules(self):
        self.assertEqual((DB.find_spell("Boule de feu (2024)")["test"], DB.find_spell("Boule de feu (2024)")["sup"]),
                         ("Dex", "1d6"))
        cure = DB.find_spell("Soins (2024)")
        self.assertEqual((cure["soins"], cure.get("soins_mod")), ("2d8", True))
        life = sheet("Clerc", 3)
        life.ch.classes[0]["sous_classe"] = "Domaine de la vie"
        life.normalize()
        self.assertIn("Disciple de la vie", [b[0] for b in life.spell_values("Soins (2024)")["bonus"]])
