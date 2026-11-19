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


def sub24(cls, lvl, sub):
    eng = sheet(cls, lvl)
    eng.ch.classes[0]["sous_classe"] = sub
    eng.normalize()
    return eng


class Subclass2024OnlyTests(unittest.TestCase):
    def test_world_tree(self):
        eng = sub24("Barbare", 6, "Voie de l'Arbre-Monde")
        eng.use_class_action("rage")
        self.assertEqual(eng.ch.pv_temporaires, 6)                 # Vitalité de l'arbre
        acts = {a["id"]: a for a in eng.class_actions()}
        self.assertEqual(acts["cap:force_vivifiante"]["formule"], "2d6")
        self.assertIn("cap:branches_arbre", acts)

    def test_wild_heart_bear_and_owl(self):
        eng = sub24("Barbare", 6, "Voie du Cœur sauvage")
        eng.ch.options_classe = {"coeur_sauvage_rage": ["Ours"], "coeur_sauvage_aspect": ["Chouette"]}
        self.assertEqual(eng.defenses()["resistances"], [])
        eng.use_class_action("rage")
        self.assertIn("contondant", [t for t, _ in eng.defenses()["resistances"]])
        self.assertEqual(eng.darkvision()["portee"], 18.0)

    def test_dance_land_sea_elements(self):
        dance = sub24("Barde", 6, "Collège de la Danse")
        self.assertEqual(dance.unarmed_die()[0], 8)
        self.assertIn("cap:pirouettes_coordonnees", {a["id"] for a in dance.class_actions()})
        land = sub24("Druide", 10, "Cercle de la terre")
        self.assertEqual(next(a for a in land.class_actions() if a["id"] == "cap:aval_terre")["formule"], "3d6")
        self.assertIn(("feu", "Protégé de dame Nature"), land.defenses()["resistances"])
        sea = sub24("Druide", 10, "Cercle des Mers")
        self.assertEqual(sea.defenses()["resistances"], [])         # seulement pendant Courroux des mers
        sea.use_class_action("cap:courroux_mers")
        self.assertEqual(len(sea.defenses()["resistances"]), 3)
        monk = sub24("Moine", 6, "Credo des Éléments")
        self.assertIn("cap:decharge_elementaire", {a["id"] for a in monk.class_actions()})
        self.assertNotIn("cap:aval_terre", {a["id"] for a in sheet("Druide", 10, "2014").class_actions()})

    def test_channel_divinity_2024_options(self):
        self.assertEqual([o["nom"] for o in sub24("Clerc", 3, "Domaine de la vie").channel_options("Clerc")],
                         ["Préservation de la vie"])
        self.assertIn("Arme sacrée", [o["nom"] for o in sub24("Paladin", 3, "Serment de dévotion")
                                      .channel_options("Paladin")])

    def test_champion_turn_start_and_assassin(self):
        champ = sub24("Guerrier", 18, "Champion")
        champ.ch.inspiration = False
        champ.ch.pv_actuels = 10
        champ.new_round()
        self.assertTrue(champ.ch.inspiration)
        self.assertEqual(champ.ch.pv_actuels, 10 + 5 + champ.mod("Constitution"))
        champ.ch.pv_actuels = 0
        champ.apply_death_save(18)
        self.assertEqual(champ.ch.pv_actuels, 1)                     # 18-20 compte comme un 20
        assassin = sub24("Roublard", 3, "Assassin")
        self.assertIn("Matériel d’empoisonneur", assassin.granted_tools())
        self.assertIn("Assassinat", assassin.initiative_detail()["avantage"])


class _Rng:
    def __init__(self, value):
        self.value = value

    def randint(self, a, b):
        return self.value if b in (20, 4) else 1


def both(cls, lvl, sub14="", sub24_=""):
    """Même personnage en 2014 et en 2024."""
    out = []
    for ed, sub in (("2014", sub14), ("2024", sub24_)):
        eng = sheet(cls, lvl, ed)
        eng.ch.classes[0]["sous_classe"] = sub
        eng.normalize()
        out.append(eng)
    return out


class TableRulesTests(unittest.TestCase):
    def test_typed_damage_and_heavy_armor_master(self):
        for eng, feat, red in zip(both("Guerrier", 8), ("Maître des armures lourdes", "Maître des armures lourdes (2024)"),
                                  (3, 3)):
            eng.ch.armure["nom"] = next(n for n, a in eng.db.armors.items() if a.get("categorie") == "lourde")
            give(eng, feat, "Force")
            eng.ch.pv_actuels = 50
            eng.apply_hp_input("10", "degats", "tranchant")
            self.assertEqual(eng.ch.pv_actuels, 50 - (10 - red), feat)
            eng.add_effect("resist_feu")
            eng.apply_hp_input("11", "degats", "feu")
            self.assertEqual(eng.ch.pv_actuels, 50 - 7 - 5)
            eng.apply_hp_input("4", "degats", "")               # sans type : inchangé
            self.assertEqual(eng.ch.pv_actuels, 34)
        e14, e24 = both("Guerrier", 8)
        for eng, feat in ((e14, "Maître des armures lourdes"), (e24, "Maître des armures lourdes (2024)")):
            eng.ch.armure["nom"] = next(n for n, a in eng.db.armors.items() if a.get("categorie") == "lourde")
            give(eng, feat, "Force")
            eng.ch.pv_actuels = 50
            eng.apply_hp_input("10", "degats", "tranchant", True)
        self.assertEqual(e14.ch.pv_actuels, 40)                  # 2014 : attaques non magiques seulement
        self.assertEqual(e24.ch.pv_actuels, 43)

    def test_reliable_talent_and_indomitable_might(self):
        from core import dice as D
        for eng in both("Roublard", 11):
            eng.ch.competences["Discrétion"] = {"maitrise": True, "expertise": False}
            r = D.roll_d20(eng.skill_spec("Discrétion"), _Rng(3))
            self.assertIn("Talent fiable", r.adjust)
            self.assertEqual(r.total, 10 + eng.skill_bonus("Discrétion"))
            self.assertEqual(D.roll_d20(eng.skill_spec("Histoire"), _Rng(3)).adjust, "")   # non maîtrisée
        self.assertEqual(D.roll_d20(sheet("Roublard", 7, "2014").skill_spec("Discrétion"), _Rng(3)).adjust, "")
        b14, b24 = both("Barbare", 18)
        for eng in (b14, b24):
            self.assertEqual(D.roll_d20(eng.ability_check_spec("Force"), _Rng(1)).total, eng.score("Force"))
        self.assertEqual(D.roll_d20(b14.save_spec("Force"), _Rng(1)).adjust, "")          # 2014 : tests seulement
        self.assertIn("Puissance", D.roll_d20(b24.save_spec("Force"), _Rng(1)).adjust)

    def test_evasion_notes(self):
        for eng in both("Moine", 7) + both("Roublard", 7):
            self.assertIn("aucun dégât", eng.save_spec("Dextérité").note)
        self.assertNotIn("aucun dégât", sheet("Moine", 6).save_spec("Dextérité").note)

    def test_spell_recall_boon(self):
        eng = sheet("Magicien", 19)
        sid = [s["id"] for s in eng.asi_slots()][-1]
        eng.ch.ameliorations[sid] = {"mode": "don", "don": "Faveur de mémoire des sorts", "don_carac": "Intelligence"}
        spell = next(s["nom"] for s in eng.db.spells.values() if s.get("niveau") == 1 and s.get("edition") == 2024)
        eng.cast_spell(spell, slot_level=1, rng=_Rng(1))
        self.assertEqual(eng.ch.emplacements_utilises[0], 0)       # 1d4 = 1 = niveau : emplacement conservé
        eng.cast_spell(spell, slot_level=1, rng=_Rng(3))
        self.assertEqual(eng.ch.emplacements_utilises[0], 1)

    def test_condition_immunities(self):
        for eng in both("Paladin", 10, "Serment de Dévotion", "Serment de dévotion"):
            self.assertFalse(eng.add_effect("charme"))
            self.assertFalse(eng.add_effect("effraye"))
            self.assertTrue(eng.add_effect("empoisonne"))
        m14, m24 = both("Moine", 10)
        self.assertFalse(m14.add_effect("empoisonne"))             # Pureté du corps (2014)
        self.assertTrue(m24.add_effect("empoisonne"))              # 2024 : Restauration de soi n'immunise pas
        for eng in both("Barbare", 6, "Voie du Berserker", "Voie du berserker"):
            eng.add_effect("charme")
            eng.use_class_action("rage")
            self.assertNotIn("charme", eng.ch.effets_actifs)       # Rage aveugle

    def test_2024_texts_on_renamed_subclasses(self):
        fey = sub24("Occultiste", 3, "Protecteur Archifée")
        self.assertIn("Foulée des fées", [a["nom"] for a in fey.class_actions()])
        self.assertNotIn("Présence féerique", [a["nom"] for a in fey.class_actions()])
        self.assertIn("Présence féerique", [a["nom"] for a in sheet_sub("Occultiste", 3, "2014", "L'Archifée")
                                            .class_actions()])
        bers = sub24("Barbare", 3, "Voie du berserker")
        self.assertNotIn("cap:frenesie", {a["id"] for a in bers.class_actions()})
        bers.use_class_action("rage")
        self.assertTrue(any(o[0].startswith("Frénésie") for o in bers.weapon_damage_spec(MACE).options))


def sheet_sub(cls, lvl, ed, frag):
    eng = sheet(cls, lvl, ed)
    subs = [s if isinstance(s, str) else s.get("nom") for s in eng.db.subclasses(cls)]
    eng.ch.classes[0]["sous_classe"] = next(s for s in subs if frag.split("'")[-1].lower() in s.lower())
    eng.normalize()
    return eng


class RenamedTileLevelTests(unittest.TestCase):
    def test_level_follows_2024_feature(self):
        e24 = sub24("Barbare", 10, "Voie du berserker")
        self.assertIn("Représailles", [a["nom"] for a in e24.class_actions()])      # niveau 10 en 2024
        e14 = sheet_sub("Barbare", 10, "2014", "Berserker")
        self.assertNotIn("Représailles", [a["nom"] for a in e14.class_actions()])   # niveau 14 en 2014


class TashaOptionsTests(unittest.TestCase):
    def test_additive_options_applied_on_2014(self):
        monk = sheet("Moine", 5, "2014")
        ids = {a["id"] for a in monk.class_actions()}
        self.assertTrue({"cap:guerison_acceleree", "cap:visee_concentree"} <= ids)
        heal = next(a for a in monk.class_actions() if a["id"] == "cap:guerison_acceleree")
        self.assertEqual(heal["formule"], "1d6+3")
        self.assertIn("arme_dediee", [s["key"] for s in monk.option_sets()])
        monk.ch.options_classe = {"arme_dediee": ["Lance"]}
        self.assertEqual(monk.dedicated_weapon(), "Lance")
        druid = sheet("Druide", 3, "2014")
        self.assertIn("Augure", [s["nom"] for s in druid.available_spells("Druide")])
        barb = sheet("Barbare", 10, "2014")
        self.assertEqual(next(s for s in barb.option_sets() if s["key"] == "connaissance_primitive")["total"], 2)
        self.assertIn("Bond instinctif", barb.use_class_action("rage")["message"])

    def test_harness_divine_power(self):
        pal = sheet("Paladin", 5, "2014")
        pal.ch.emplacements_utilises[0] = 2
        pal.use_class_action("cap:exploitation_divine")
        self.assertEqual(pal.ch.emplacements_utilises[0], 1)
        self.assertIn("cap:canalisation_divine", {a["id"] for a in sheet("Clerc", 2, "2014").class_actions()})

    def test_replacing_options_never_applied(self):
        ranger = sheet("Rôdeur", 10, "2014")
        self.assertEqual(ranger.speed(), 9.0)                         # Vagabond (Explorateur expert) non appliqué
        self.assertFalse(ranger.feature_allowed("Voile de la nature (option Tasha)"))
        self.assertFalse(ranger.feature_allowed("Ennemi favori (option Tasha)"))
        cleric = sheet("Clerc", 8, "2014", "Domaine de la Vie")
        self.assertNotIn("Frappes bénies", " ".join(o[0] for o in cleric.weapon_damage_spec(MACE).options))

    def test_rule_toggle_and_2024(self):
        pal = sheet("Paladin", 5, "2014")
        pal.set_house_rule("options_tasha", False)
        self.assertNotIn("cap:exploitation_divine", {a["id"] for a in pal.class_actions()})
        for cls, lvl in (("Moine", 5), ("Paladin", 5), ("Druide", 3)):
            eng = sheet(cls, lvl, "2024")
            self.assertFalse(eng.tasha_on())
            self.assertFalse(any(a["id"] in ("cap:guerison_acceleree", "cap:exploitation_divine",
                                             "cap:compagnon_sauvage") for a in eng.class_actions()))
        self.assertIn("cap:visee_stable_2024", {a["id"] for a in sheet("Roublard", 3, "2024").class_actions()})


class RestRecoveryAuditTests(unittest.TestCase):
    def test_short_rest_partial_2024(self):
        for cls, key in (("Barbare", "rage"), ("Clerc", "conduit"), ("Druide", "forme"), ("Guerrier", "second_souffle")):
            e14, e24 = sheet(cls, 6, "2014"), sheet(cls, 6, "2024")
            for eng in (e14, e24):
                eng.ch.ressources_utilisees[key] = 2
                eng.short_rest()
            self.assertEqual(e24.ch.ressources_utilisees.get(key, 0), 1, cls)        # 2024 : une utilisation
            self.assertEqual(e14.ch.ressources_utilisees.get(key, 0), 2 if key == "rage" else 0, cls)

    def test_long_rest_hit_dice(self):
        for ed, left in (("2014", 3), ("2024", 0)):
            eng = sheet("Guerrier", 6, ed)
            eng.ch.des_vie_utilises = {"d10": 6}
            eng.long_rest()
            self.assertEqual(eng.ch.des_vie_utilises["d10"], left, ed)

    def test_uncanny_metabolism_and_magical_cunning(self):
        monk = sheet("Moine", 5, "2024")
        monk.ch.ressources_utilisees["ki"] = 4
        monk.roll_initiative(10)
        self.assertEqual(monk.ch.ressources_utilisees["ki"], 0)
        monk.ch.ressources_utilisees["ki"] = 4
        monk.roll_initiative(10)
        self.assertEqual(monk.ch.ressources_utilisees["ki"], 4)                     # une fois par repos long
        lock = sheet("Occultiste", 5, "2024")
        lock.ch.pacte_utilises = 2
        lock.use_class_action("cap:ruse_magique")
        self.assertEqual(lock.ch.pacte_utilises, 1)
        self.assertNotIn("cap:ruse_magique", {a["id"] for a in sheet("Occultiste", 5, "2014").class_actions()})


class CombatFeatTests(unittest.TestCase):
    def _fighter(self, ed, feats):
        eng = sheet("Guerrier", 8, ed)
        for sid, f in zip([s["id"] for s in eng.asi_slots()], feats):
            eng.ch.ameliorations[sid] = {"mode": "don", "don": f, "don_carac": "Force"}
        return eng

    def test_power_attack_2014(self):
        eng = self._fighter("2014", ["Tireur d'élite", "Briseur d'armes lourdes"])
        bow = {"nom": "Arc long", "bonus": 0, "maitrise": None}
        sword = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        before = eng.weapon_stats(bow)["attaque"]
        self.assertTrue(eng.weapon_stats(bow)["puissance_possible"])
        self.assertFalse(eng.weapon_stats(sword)["puissance_possible"])            # ni lourde ni à distance
        eng.use_class_action("don_puissance")
        self.assertEqual(eng.weapon_stats(bow)["attaque"], before - 5)
        self.assertIn("+", eng.weapon_stats(bow)["degats"])
        self.assertIn("Attaque puissante (−5 / +10)", [t.label for t in eng.weapon_attack_spec(bow).terms])
        eng.use_class_action("don_puissance")
        self.assertEqual(eng.weapon_stats(bow)["attaque"], before)

    def test_bonus_attack_tiles(self):
        e14 = self._fighter("2014", ["Maître des armes d'hast", "Expert en arbalètes", "Briseur d'armes lourdes"])
        ids = {a["id"] for a in e14.class_actions()}
        self.assertTrue({"don_pommeau", "don_arbalete", "don_fauchage", "don_puissance"} <= ids)
        e24 = self._fighter("2024", ["Maître d'hast", "Cogneur lourd"])
        ids = {a["id"] for a in e24.class_actions()}
        self.assertTrue({"don_pommeau", "don_fauchage"} <= ids)
        self.assertNotIn("don_puissance", ids)                                     # pas de −5/+10 en 2024
        res = e24.use_class_action("don_pommeau")
        self.assertTrue(res["degats"].formula.startswith("1d4"))


class TashaReplacementTests(unittest.TestCase):
    def test_ranger_replacements(self):
        r = sheet("Rôdeur", 10, "2014")
        self.assertEqual([o["cle"] for o in r.tasha_replacement_options("Rôdeur")],
                         ["ennemi favori", "explorateur expert", "conscience primordiale", "voile de la nature"])
        ids = {a["id"] for a in r.class_actions()}
        self.assertFalse(ids & {"cap:ennemi_jure", "cap:voile_nature", "cap:infatigable"})   # rien d'office
        speed, exp = r.speed(), r.expertise_allowed()
        for cle in ("ennemi favori", "explorateur expert", "conscience primordiale", "voile de la nature"):
            r.set_tasha_replacement(cle, True)
        ids = {a["id"] for a in r.class_actions()}
        self.assertTrue({"cap:ennemi_jure", "cap:voile_nature", "cap:infatigable"} <= ids)
        self.assertEqual(r.speed(), speed + 1.5)                                   # Vagabond
        self.assertEqual(r.expertise_allowed(), exp + 1)
        self.assertIn("Communication avec les animaux", [g["nom"] for g in r.granted_spells()])
        self.assertFalse(r.has_feature("camouflage"))                              # aptitude remplacée
        r.use_class_action("cap:ennemi_jure")
        self.assertEqual(r.ch.concentration, "Ennemi favori")
        self.assertTrue(any(o[0].startswith("Ennemi favori") for o in
                            r.weapon_damage_spec({"nom": "Arc long", "bonus": 0, "maitrise": None}).options))
        r.ch.pv_temporaires = 0
        r.use_class_action("cap:infatigable")
        self.assertGreater(r.ch.pv_temporaires, 0)

    def test_blessed_strikes_replaces_divine_strike(self):
        c = sheet("Clerc", 8, "2014", "Domaine de la Vie")
        self.assertTrue(any(o[0].startswith("Frappe divine") for o in c.weapon_damage_spec(MACE).options))
        c.set_tasha_replacement("frappes benies", True)
        opts = [o[0] for o in c.weapon_damage_spec(MACE).options]
        self.assertTrue(any(o.startswith("Frappes bénies") for o in opts))
        self.assertFalse(any(o.startswith("Frappe divine") for o in opts))

    def test_not_on_2024_or_without_rule(self):
        self.assertEqual(sheet("Rôdeur", 10, "2024").tasha_replacement_options("Rôdeur"), [])
        r = sheet("Rôdeur", 10, "2014")
        r.set_house_rule("options_tasha", False)
        self.assertEqual(r.tasha_replacement_options("Rôdeur"), [])


class WildShape2024Tests(unittest.TestCase):
    def test_rules_and_known_forms(self):
        d14, d24 = sheet("Druide", 4, "2014"), sheet("Druide", 4, "2024")
        self.assertIsNone(d14.known_forms_option_set())
        s = d24.known_forms_option_set()
        self.assertEqual(s["total"], 6)
        self.assertEqual(d24.allowed_beasts(), [])                       # aucune forme connue choisie
        pick = list(s["options"])[0]
        d24.set_class_option("formes_connues", 0, pick)
        self.assertEqual([b["nom"] for b in d24.allowed_beasts()], [pick])
        self.assertTrue(d24.wild_shape()["nage"])                        # 2024 : nage dès le niveau 2
        self.assertEqual(sheet("Druide", 8, "2024").wild_shape()["formes_connues"], 8)

    def test_hp_temp_and_damage(self):
        d24 = sheet("Druide", 4, "2024")
        pick = list(d24.known_forms_option_set()["options"])[0]
        d24.set_class_option("formes_connues", 0, pick)
        d24.ch.pv_actuels = 20
        self.assertTrue(d24.assume_form(pick))
        self.assertEqual(d24.ch.pv_temporaires, 4)                      # niveau de druide
        d24.take_damage(6)
        self.assertEqual((d24.ch.pv_actuels, d24.ch.forme_active), (18, pick))
        d24.take_damage(30)
        self.assertEqual(d24.ch.forme_active, "")                        # 0 PV : la forme prend fin
        self.assertEqual([a["type"] for a in d24.class_actions() if a["id"] == "cap:forme_sauvage"],
                         ["Action bonus"])

    def test_moon_2024(self):
        moon = sheet("Druide", 6, "2024")
        moon.ch.classes[0]["sous_classe"] = "Cercle de la lune"
        moon.normalize()
        ws = moon.wild_shape()
        self.assertEqual((ws["fp_max"], ws["pv_temp"]), (2.0, 18))
        beast = next(iter(moon.db.beasts.values()))
        self.assertGreaterEqual(moon.beast_ac(beast), 13 + moon.mod("Sagesse"))
