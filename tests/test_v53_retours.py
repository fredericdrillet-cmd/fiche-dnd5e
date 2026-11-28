"""v53 : retours d'essai — bonus au toucher (sournoise, châtiment, manœuvres, psi…), armure sur mesure,
compétences à la création (espèce comptée deux fois), onglet des dons."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def sheet(cls, lvl=1, sub="", weapon="Épée longue"):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    ch.armes_cac[0]["nom"] = weapon
    eng.normalize()
    return eng


class OnHitTests(unittest.TestCase):
    def keys(self, eng):
        return {o["key"]: o["dice"] for o in eng.on_hit_options(eng.ch.armes_cac[0])}

    def test_sneak_attack_added_to_weapon_damage(self):
        eng = sheet("Roublard", 5, weapon="Rapière")
        opts = eng.on_hit_options(eng.ch.armes_cac[0])
        self.assertEqual(eng.apply_on_hit(opts, ["sournoise"]), [("Attaque sournoise", "3d6")])

    def test_battle_master_maneuvers(self):
        eng = sheet("Guerrier", 7, "Maître de guerre")
        for i, n in enumerate(["Attaque menaçante", "Attaque précise", "Croc-en-jambe"]):
            eng.set_class_option("manoeuvres", i, n)
        keys = self.keys(eng)
        self.assertIn("man:Attaque menaçante", keys)
        self.assertNotIn("man:Attaque précise", keys)             # ajoute le dé à l'attaque, pas aux dégâts
        opts = eng.on_hit_options(eng.ch.armes_cac[0])
        added = eng.apply_on_hit(opts, ["man:Attaque menaçante", "man:Croc-en-jambe"])
        self.assertEqual(len(added), 1)                            # une seule manœuvre par coup
        self.assertEqual(eng.resource_used("superiorite"), 1)

    def test_other_riders(self):
        self.assertIn("psi_frappe", self.keys(sheet("Guerrier", 7, "Soldat psi")))
        self.assertIn("tueur_colosses", self.keys(sheet("Rôdeur", 5, "Chasseur")))
        self.assertIn("frappe_divine", self.keys(sheet("Clerc", 8, "Domaine de la Guerre")))
        zealot = sheet("Barbare", 5, "Voie du Zélote")
        zealot.ch.effets_actifs.append("rage")
        self.assertEqual(self.keys(zealot)["fureur_divine"], "1d6+2")
        ranger = sheet("Rôdeur", 5)
        ranger.ch.concentration = "Marque du chasseur"
        self.assertIn("conc:marque du chasseur", self.keys(ranger))

    def test_per_turn_riders_once(self):
        eng = sheet("Rôdeur", 5, "Chasseur")
        opts = eng.on_hit_options(eng.ch.armes_cac[0])
        eng.apply_on_hit(opts, ["tueur_colosses"])
        self.assertNotIn("tueur_colosses", self.keys(eng))


class SmiteUndeadTests(unittest.TestCase):
    def test_extra_d8_against_fiend_or_undead(self):
        from core.combat_flow import SMITE_UNDEAD
        for edition in ("2014", "2024"):
            eng = sheet("Paladin", 5)
            if edition == "2024":
                eng.set_edition_mode("2024")
                eng.normalize()
                eng.ch.armes_cac[0]["nom"] = "Épée longue"
                eng.normalize()
            opts = eng.on_hit_options(eng.ch.armes_cac[0])
            added = eng.apply_on_hit(opts, ["chatiment:1", SMITE_UNDEAD])
            self.assertEqual([d for _l, d in added], ["2d8", "1d8"], edition)
        eng = sheet("Paladin", 5)
        opts = eng.on_hit_options(eng.ch.armes_cac[0])
        self.assertEqual(eng.apply_on_hit(opts, [SMITE_UNDEAD]), [])   # sans Châtiment : rien


class CustomArmorTests(unittest.TestCase):
    def test_custom_armor_on_base(self):
        eng = sheet("Guerrier", 5)
        name = eng.add_custom_magic_item("Cotte du dragon", type_="Armure", base="Cotte de mailles", bonus=2)
        eng.normalize()
        cand = next(c for c in eng.slot_inventory("armure") if name in c["nom"])
        eng.equip_slot("armure", cand)
        eng.normalize()
        self.assertEqual(eng.armor_class()[0], 18)                 # 16 + 2
        shield = eng.add_custom_magic_item("Égide", type_="Armure", base="Bouclier", bonus=1)
        eng.normalize()
        eng.equip_slot("main_secondaire", next(c for c in eng.slot_inventory("main_secondaire") if shield in c["nom"]))
        eng.normalize()
        self.assertEqual(eng.armor_class()[0], 21)                 # + 2 + 1


class CreationSkillsTests(unittest.TestCase):
    def test_species_skill_not_counted_as_class_pick(self):
        eng = sheet("Roublard", 1)
        eng.change_race("Elfe")
        eng.normalize()
        need = eng.skills_missing()
        self.assertEqual(need, 4)
        opts = [n for n in eng.class_skill_status()["options"] if not (eng.ch.competences.get(n) or {}).get("maitrise")]
        for n in opts[:need]:
            eng.ch.competences.setdefault(n, {"maitrise": False, "expertise": False})["maitrise"] = True
        eng.normalize()
        self.assertEqual((eng.skills_missing(), eng.skill_choice_errors()), (0, []))
        self.assertEqual(eng.expertise_missing(), 2)


if __name__ == "__main__":
    unittest.main()


class ArmesMagiquesAuditTests(unittest.TestCase):
    """v53 : toute arme de base a un dessin ; armes / armures / boucliers sur mesure équipables et illustrés."""

    db = DB

    def fresh(self):
        from core.engine import Engine
        ch = Engine.new_character(self.db)
        ch.classes = [{"nom": "Guerrier", "niveau": 10, "sous_classe": "", "pv_jets": []}]
        e = Engine(self.db, ch)
        e.normalize()
        return e, ch

    def test_chaque_arme_de_base_a_un_dessin(self):
        from core.action_icons import weapon_key
        self.assertEqual([w for w in self.db.weapons if not weapon_key(w)], [])
        self.assertEqual(weapon_key("Hache du berserker (Hache à deux mains)"), "grande hache")

    def test_flechette_n_est_pas_une_munition(self):
        from core.engine import Engine
        self.assertFalse(Engine.is_ammo_item({"nom": "Fléchette +1", "type": "Arme"}))
        self.assertTrue(Engine.is_ammo_item({"nom": "Flèches +1", "type": "Arme"}))

    def test_armes_sur_mesure_equipables(self):
        from core.tile_icons import tile_icon
        for base in ("Fléchette", "Filet", "Pistolet", "Hache à deux mains", "Serpe"):
            e, ch = self.fresh()
            nom = "Mon arme " + base
            e.add_custom_magic_item(nom, "Arme", "rare", base=base, bonus=2)
            e.normalize()
            self.assertTrue(ch.objets_magiques, base)
            slot = e.gear_default_slot(ch.objets_magiques[-1])
            cand = next(c for c in e.slot_inventory(slot) if c["nom"].startswith(nom))
            e.equip_slot(slot, cand)
            e.normalize()
            tile = next(x for x in e.turn_actions() if x.get("groupe") == "attaques" and nom in x["nom"])
            self.assertEqual(tile_icon(tile)[0], "arme", base)

    def test_armure_et_bouclier_sur_mesure(self):
        for base, slot in (("Cotte de mailles", "armure"), ("Bouclier", "main_secondaire")):
            e, ch = self.fresh()
            ac0 = e.armor_class()[0]
            e.add_custom_magic_item("Pièce " + base, "Armure", "rare", base=base, bonus=2)
            e.normalize()
            self.assertEqual(e.gear_default_slot(ch.objets_magiques[-1]), slot)
            cand = next(c for c in e.slot_inventory(slot) if c["nom"].startswith("Pièce"))
            e.equip_slot(slot, cand)
            e.normalize()
            self.assertGreater(e.armor_class()[0], ac0, base)

    def test_icone_du_sac_des_armes(self):
        import qt_stub
        qt_stub.install()
        from ui.icons import named_body
        from ui.inventory_grid import item_body
        for n in ("Pistolet", "Mousquet", "Massue +1", "Maillet d’armes", "Hache du berserker (Hache à deux mains)"):
            self.assertNotEqual(item_body(n, "Arme"), named_body("objet"), n)


class HarmonisationEquipementTests(unittest.TestCase):
    """v53 : un objet qui exige l'harmonisation la prend dès qu'il est équipé ; tout l'inventaire est dans le sac."""

    LINKED = ("Anneau de protection", "Cape de protection", "Bottes ailées", "Chapeau de magicien")

    def fresh(self):
        ch = Engine.new_character(DB)
        ch.classes = [{"nom": "Magicien", "niveau": 5, "sous_classe": "", "pv_jets": []}]
        e = Engine(DB, ch)
        e.normalize()
        return e, ch

    def test_ajout_dans_le_sac_puis_equiper_harmonise(self):
        e, ch = self.fresh()
        e.add_magic_item("Anneau de protection")
        self.assertEqual((ch.objets_magiques[0]["equipe"], ch.objets_magiques[0]["harmonise"]), (False, False))
        ca = e.armor_class()[0]
        e.set_equipped(0, True)
        e.normalize()
        self.assertTrue(ch.objets_magiques[0]["harmonise"])
        self.assertEqual(e.armor_class()[0], ca + 1)
        self.assertTrue(e.paperdoll()["anneau_1"]["harmonise"])
        e.set_equipped(0, False)
        e.normalize()
        self.assertEqual((e.attuned_count(), e.armor_class()[0]), (0, ca))

    def test_limite_refuse_l_equipement(self):
        e, ch = self.fresh()
        for n in self.LINKED:
            e.add_magic_item(n)
        for i in range(3):
            e.set_equipped(i, True)
        self.assertEqual(e.attuned_count(), 3)
        self.assertIn("3 / 3", e.attune_blocked(3))
        e.set_equipped(3, True)
        self.assertFalse(ch.objets_magiques[3]["equipe"])
        cand = next(c for c in e.slot_inventory("tete") if c["nom"] == "Chapeau de magicien")
        self.assertIn("Harmonisation", e.equip_slot("tete", cand))
        e.add_magic_item("Anneau de résistance")             # même case qu'un objet harmonisé : échange permis
        cand = next(c for c in e.slot_inventory("anneau_1") if c["nom"] == "Anneau de résistance")
        e.equip_slot("anneau_1", cand)
        e.normalize()
        self.assertTrue(ch.objets_magiques[-1]["harmonise"])
        self.assertEqual(e.attuned_count(), 3)

    def test_objet_sans_harmonisation_equipe_d_office(self):
        e, ch = self.fresh()
        e.add_magic_item("Bottes elfiques")
        self.assertTrue(ch.objets_magiques[0]["equipe"])
        self.assertFalse(ch.objets_magiques[0]["harmonise"])

    def test_ancienne_sauvegarde_au_dela_de_la_limite(self):
        e, ch = self.fresh()
        for n in self.LINKED:
            e.add_magic_item(n)
            ch.objets_magiques[-1].update(equipe=True, harmonise=False)
        ch.objets_magiques.append({"nom": "Bâton de feu", "bonus": 0, "equipe": False, "harmonise": True})
        e.normalize()
        self.assertEqual(e.attuned_count(), 3)
        self.assertEqual([o["equipe"] for o in ch.objets_magiques], [True, True, True, False, False])
        self.assertFalse(ch.objets_magiques[-1]["harmonise"])           # harmonisé mais rangé : sans effet

    def test_couleurs_de_rarete(self):
        sys.path.insert(0, str(ROOT))
        from ui import theme
        self.assertEqual(theme.rarity_key("rare (+2) ou très rare (+3)"), "rare")
        self.assertEqual(theme.rarity_key("Très rare"), "tres rare")
        self.assertEqual(theme.rarity_category("légendaire"), "rarete_legendaire")
        for t in theme.THEMES.values():
            for r in ("commun", "peu commun", "rare", "très rare", "légendaire", "artefact"):
                self.assertGreaterEqual(theme.contrast_ratio(theme.rarity_color(r, t), t.panel), 4.5, (t.key, r))
                self.assertGreaterEqual(theme.contrast_ratio(theme.rarity_color(r, t, t.panel2), t.panel2), 4.5)
                c = theme.rarity_color(r, t, theme.table_bgs(t))
                self.assertGreaterEqual(min(theme.contrast_ratio(c, b) for b in theme.table_bgs(t)), 4.5, (t.key, r))
        e, ch = self.fresh()
        e.add_magic_item("Anneau de protection")
        e.set_equipped(0, True)
        self.assertEqual(e.paperdoll()["anneau_1"]["rarete"], "rare")


class GlisserDeposerTests(unittest.TestCase):
    """v53 : sac -> mannequin par glisser-déposer (clé fiable) ; tuiles « En partie » réagençables."""

    def test_equiper_depuis_le_sac(self):
        ch = Engine.new_character(DB)
        ch.classes = [{"nom": "Guerrier", "niveau": 8, "sous_classe": "", "pv_jets": []}]
        e = Engine(DB, ch)
        e.normalize()
        e.add_magic_item("Anneau de protection")
        name = "Hache du berserker"
        e.add_magic_gear(name, e.magic_base_options(name)[0])
        e.add_magic_item("Baguette de boules de feu")
        ch.equipement.append({"nom": "Cotte de mailles", "qte": 1})
        e.normalize()
        self.assertTrue(e.equip_from_bag(e.bag_key(1), "main_principale")[0])
        self.assertEqual(ch.armes_cac[0]["nom"], e.magic_base_options(name)[0])
        ok, msg = e.equip_from_bag(e.bag_key(0), "tete")       # mauvaise case -> sa case naturelle
        self.assertTrue(ok, msg)
        self.assertEqual(ch.objets_magiques[0]["emplacement"], "anneau_1")
        self.assertTrue(e.equip_from_bag(e.bag_key(2))[0])      # baguette : portée sans case
        self.assertTrue(ch.objets_magiques[2]["equipe"])
        self.assertTrue(e.equip_from_bag("Cotte de mailles", "armure")[0])
        self.assertEqual(ch.armure["nom"], "Cotte de mailles")
        self.assertFalse(e.equip_from_bag("#mg:99")[0])

    def test_ordre_des_tuiles(self):
        sys.path.insert(0, str(ROOT))
        from ui.tile_button import apply_order, reorder
        shown = ["a", "b", "c", "d"]
        self.assertEqual(reorder([], shown, "d", "a", False), ["d", "a", "b", "c"])
        self.assertEqual(reorder([], shown, "a", "c", True), ["b", "c", "a", "d"])
        saved = ["x", "a", "y", "b", "c", "d"]                 # x, y masquées par un filtre : gardent leur place
        self.assertEqual(reorder(saved, shown, "d", "a", False), ["x", "d", "y", "a", "b", "c"])
        ids = ["c", "new", "a", "b"]
        self.assertEqual([ids[k] for k in apply_order(ids, ["a", "b", "c"])], ["a", "b", "c", "new"])

    def test_ordre_sauvegarde(self):
        import json
        from core.character import Character
        ch = Engine.new_character(DB)
        ch.ordre_tuiles = ["reaction:opportunite", "arme:mains_nues"]
        self.assertEqual(Character.from_dict(json.loads(json.dumps(ch.to_dict()))).ordre_tuiles,
                         ["reaction:opportunite", "arme:mains_nues"])


class FiltresDuSacTests(unittest.TestCase):
    def test_familles(self):
        sys.path.insert(0, str(ROOT / "tests"))
        import qt_stub
        qt_stub.install()
        from ui.inventory_grid import item_family
        cases = {("Épée longue", "Arme", False): "armes", ("Flèches", "Équipement", False): "armes",
                 ("Flèches +1", "", False): "armes", ("Cotte de mailles", "Armure", False): "armures",
                 ("Bouclier", "Bouclier", False): "armures", ("Potion de soins", "Équipement", False): "consommables",
                 ("Parchemin de sort", "Parchemin", True): "consommables",
                 ("Potion de force de géant des collines", "Potion", True): "consommables",
                 ("Anneau de protection", "Anneau", True): "magiques", ("Épée vorpale", "Arme", True): "armes",
                 ("Outils de forgeron", "Outil", False): "outils", ("Corde en chanvre (15 m)", "Équipement", False): "divers"}
        for (n, c, m), want in cases.items():
            self.assertEqual(item_family(n, c, m), want, n)

    def test_potion_rangee_dans_le_sac(self):
        ch = Engine.new_character(DB)
        e = Engine(DB, ch)
        e.add_magic_item("Potion de force de géant des collines")
        e.add_magic_item("Bottes elfiques")
        self.assertEqual([o["equipe"] for o in ch.objets_magiques], [False, True])


class EmplacementsRapidesTests(unittest.TestCase):
    """v53 : potions / huiles / parchemins sous la main -> tuiles « En partie »."""

    def fresh(self, edition="2014"):
        ch = Engine.new_character(DB)
        ch.classes = [{"nom": "Magicien", "niveau": 5, "sous_classe": "", "pv_jets": []}]
        e = Engine(DB, ch)
        e.normalize()
        ch.equipement.append({"nom": "Potion de guérison", "qte": 2})
        e.add_magic_item("Parchemin de sort (niveau 1)")
        e.add_magic_item("Anneau de protection")
        return e, ch

    def test_placer_et_tuiles(self):
        e, ch = self.fresh()
        self.assertTrue(e.set_quick_slot(0, "Potion de guérison")[0])
        self.assertTrue(e.set_quick_slot(1, e.bag_key(0))[0])
        self.assertFalse(e.set_quick_slot(2, e.bag_key(1))[0])           # un anneau ne va pas là
        self.assertTrue(e.set_quick_slot(3, "Potion de guérison")[0])    # déplacé : un seul emplacement
        self.assertEqual(ch.emplacements_rapides, ["", "Parchemin de sort (niveau 1)", "", "Potion de guérison"])
        tiles = {t["id"]: t for t in e.turn_actions() if t["id"].startswith("rapide:")}
        self.assertEqual(set(tiles), {"rapide:1", "rapide:3"})
        self.assertEqual(tiles["rapide:3"]["groupe"], "objets")
        self.assertEqual(tiles["rapide:3"]["type"], "Action")            # 2014 sans la règle de la table
        ch.regles_optionnelles["potion_action_bonus"] = True
        self.assertEqual(e.quick_slots()[3]["type"], "Action bonus")

    def test_utiliser_puis_vider_quand_epuise(self):
        e, ch = self.fresh()
        e.set_quick_slot(0, "Potion de guérison")
        res = e.use_turn_action("rapide:0")
        self.assertTrue(res["ok"] and ch.tour_action)
        e.use_consumable(res["rapide"]["source"], res["rapide"]["index"])
        e.use_consumable("equipement", 0)
        e.normalize()
        self.assertEqual(ch.emplacements_rapides[0], "")

    def test_parchemin(self):
        e, ch = self.fresh()
        self.assertEqual(e.scroll_level("Parchemin de sort (niveau 3)"), 3)
        self.assertEqual(e.scroll_level("Parchemin de sort (sort mineur)"), 0)
        self.assertIsNone(e.scroll_level("Parchemin de protection"))
        self.assertIn("Projectile magique", e.scroll_spells("Parchemin de sort (niveau 1)"))
        e.consume_one("objet", 0)
        self.assertEqual([o["nom"] for o in ch.objets_magiques], ["Anneau de protection"])

    def test_noms_potion_de_soins(self):
        from core import mechanics as M
        self.assertEqual(M.potion_action("Potion de soins"), ("soin", "2d4+2"))
        self.assertEqual(M.potion_action("Potion de soins supérieurs"), ("soin", "8d4+8"))

    def test_sauvegarde(self):
        import json
        from core.character import Character
        e, ch = self.fresh()
        e.set_quick_slot(2, "Potion de guérison")
        again = Character.from_dict(json.loads(json.dumps(ch.to_dict())))
        self.assertEqual(again.emplacements_rapides[2], "Potion de guérison")
        self.assertEqual(Character.from_dict({}).emplacements_rapides, ["", "", "", ""])


class ObjetsImportesEtTatouagesTests(unittest.TestCase):
    """v53 : objets magiques de la référence importés (Tasha, Xanathar, Eberron…), tatouages, bonus de sorts."""

    def fresh(self, cls="Guerrier", lvl=5):
        ch = Engine.new_character(DB)
        ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
        e = Engine(DB, ch)
        e.normalize()
        return e, ch

    def wear(self, e, name, **extra):
        e.add_magic_item(name)
        e.ch.objets_magiques[-1].update(extra)
        e.normalize()
        ok, msg = e.equip_from_bag(e.bag_key(len(e.ch.objets_magiques) - 1))
        e.normalize()
        self.assertTrue(ok, msg)
        return e.ch.objets_magiques[-1]

    def test_import(self):
        imported = [n for n, i in DB.magic_items.items() if i.get("importe")]
        self.assertGreater(len(imported), 300)
        self.assertEqual(len([n for n in imported if n.startswith("Tatouage")]), 11)
        self.assertNotIn("Armure +1, +2 ou +3", DB.magic_items)          # déjà découpée en paliers

    def test_tatouages_dans_leurs_cases(self):
        e, ch = self.fresh()
        for n in ("Tatouage de Gisombre", "Tatouage mascarade", "Tatouage de l'enlumineur"):
            entry = self.wear(e, n)
            self.assertTrue(entry["emplacement"].startswith("tatouage_"))
            self.assertTrue(entry["harmonise"])
        e.add_magic_item("Tatouage barrière")                              # 4e tatouage : 3 / 3 harmonisations
        self.assertIn("3 / 3", e.attune_blocked(len(ch.objets_magiques) - 1))

    def test_barriere_et_griffe(self):
        e, ch = self.fresh()
        ch.armure["nom"] = "Aucune armure"
        e.normalize()
        dex = e.mod("Dextérité")
        self.wear(e, "Tatouage barrière", palier="Rare")
        self.assertEqual(e.armor_class()[0], 15 + min(dex, 2))
        unarmed = e.weapon_stats(e.unarmed_slot())["attaque"]
        self.wear(e, "Tatouage de la griffe occulte")
        self.assertEqual(e.weapon_stats(e.unarmed_slot())["attaque"], unarmed + 1)

    def test_fontaine_de_vie(self):
        e, ch = self.fresh()
        self.wear(e, "Tatouage de fontaine de vie")
        self.assertIn("nécrotique", [r for r, _ in e.defenses()["resistances"]])
        ch.pv_actuels = 4
        e.take_damage(10)
        self.assertEqual(ch.pv_actuels, 1)
        e.take_damage(10)
        self.assertEqual(ch.pv_actuels, 0)
        e.long_rest()
        self.assertNotIn("charges_utilisees", ch.objets_magiques[0])

    def test_fureur_et_foulee(self):
        e, ch = self.fresh()
        self.wear(e, "Tatouage de fureur sanglante")
        opts = e.on_hit_options(ch.armes_cac[0])
        self.assertIn("tatouage:fureur", [o["key"] for o in opts])
        e.apply_on_hit(opts, ["tatouage:fureur"])
        self.assertEqual(ch.objets_magiques[0]["charges_utilisees"], 1)
        e2, ch2 = self.fresh()
        self.wear(e2, "Tatouage de foulée spectrale")
        self.assertEqual(e2.defenses()["resistances"], [])                 # seulement pendant la forme
        p = e2.magic_item_powers()[0]
        e2.use_item_power(p["id"])
        self.assertIn("forme_fantomatique", ch2.effets_actifs)

    def test_sortilege(self):
        e, ch = self.fresh()
        self.wear(e, "Tatouage sortilège", sort_tatouage="Rayon de givre")
        p = e.magic_item_powers()[0]
        out = e.use_item_power(p["id"])
        self.assertEqual(out["stats"]["attaque"], 5)
        self.assertEqual(ch.objets_magiques, [])                            # le tatouage disparaît
        e.item_spell_override = out["stats"]
        spec = e.spell_attack_spec("Rayon de givre")
        e.item_spell_override = None
        self.assertEqual(sum(t.value for t in spec.terms), 5)

    def test_gisombre(self):
        e, ch = self.fresh()
        self.wear(e, "Tatouage de Gisombre")
        self.assertEqual(e.darkvision()["portee"], 18.0)

    def test_bonus_de_sorts(self):
        e, ch = self.fresh("Magicien")
        dc, atk = e.caster("Magicien")["dc"], e.caster("Magicien")["attaque"]
        self.wear(e, "Grimoire des arcanes", palier="Très rare")
        self.assertEqual((e.caster("Magicien")["dc"], e.caster("Magicien")["attaque"]), (dc + 3, atk + 3))
        self.wear(e, "Fiole sanguine", palier="Rare")                       # sorts d'ensorceleur : sans effet
        self.assertEqual(e.caster("Magicien")["dc"], dc + 3)

    def test_fonctionne_comme(self):
        e, ch = self.fresh()
        ca = e.armor_class()[0]
        entry = self.wear(e, "Anneau de protection d'Obo'laka")
        self.assertTrue(entry["emplacement"].startswith("anneau"))
        self.assertEqual(e.armor_class()[0], ca + 1)

    def test_ceinturon_et_parchemin(self):
        e, ch = self.fresh()
        self.wear(e, "Ceinturon de force de géant (givre ou pierres)")
        self.assertEqual(e.score("Force"), 23)
        self.assertEqual(e.scroll_level("Parchemin de sort (tour de magie)"), 0)

    def test_reglage_tatouages_enregistre(self):
        from core import settings as S
        self.assertIn("tatouages_visibles", S.DEFAULTS)
        self.assertIn("icones_noms", S.DEFAULTS)


class DonneesReferenceCompleteesTests(unittest.TestCase):
    """v53 : races 2014, paquetages 2024, listes de sorts 2014, dons accordés par le MJ (data/editions)."""

    def sheet(self, race="Humain", cls="Guerrier", lvl=5):
        ch = Engine.new_character(DB)
        ch.race = race
        ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
        e = Engine(DB, ch)
        e.normalize()
        return e, ch

    def test_races_2014(self):
        for n in ("Drakéide chromatique", "Drakéide métallique", "Drakéide diamantin", "Drakéide ravenite",
                  "Nain (Marque de garde)", "Humain (Marque du passage)", "Elfe pâle", "Halfelin spectral",
                  "Aasimar fléau", "Demi-elfe (Marque de la tempête)"):
            self.assertIn(n, DB.races, n)
            e, ch = self.sheet(n)
            self.assertIn(n, e.race_options())
        self.assertEqual(DB.races["Nain (Marque de garde)"]["caracteristiques"], "Con +2, Int +1")
        self.assertEqual(DB.races["Aasimar fléau"]["caracteristiques"], "Cha +2, Con +1")
        self.assertNotIn("Résistance aux dégâts", [c["nom"] for c in DB.races["Drakéide ravenite"]["capacites"]])
        self.assertNotIn("Haut-elfe", DB.races)                            # déjà une sous-race d'Elfe
        e, ch = self.sheet()
        e.set_edition_mode("2024")
        e.normalize()
        self.assertNotIn("Elfe pâle", e.race_options())

    def test_drakeides_de_fizban(self):
        e, ch = self.sheet("Drakéide diamantin")
        ch.ascendance_raciale = "Améthyste"
        e.normalize()
        b = e.breath_weapon()
        self.assertEqual((b["type"], b["zone"], b["degats"], b["utilisations"]), ("force", "cône de 4,50 m", "2d10", 3))
        self.assertIn("resist_force", e.innate_effects())
        sets = [s for s in e.option_sets() if s["key"] == "ascendance_raciale"]
        self.assertIn("Topaze", sets[0]["options"])

    def test_paquetages_2024(self):
        self.assertEqual(DB.catalog["Sac d'explorateur"]["categorie"], "Paquetage")
        e, ch = self.sheet()
        self.assertGreater(e.add_pack("Sac d'explorateur"), 5)
        self.assertIn("Torche", [i["nom"] for i in ch.equipement])

    def test_listes_de_sorts(self):
        self.assertIn("Occultiste", DB.spells["Gelure"]["classes"])
        self.assertIn("Artificier", DB.spells["Verrou magique"]["classes"])
        self.assertIn("Barde", DB.spells["Mot de pouvoir mortel"]["classes"])
        self.assertNotIn("Magicien", DB.spells["Piqûre sapeuse"].get("classes", []))   # dunamancie : restreinte
        self.assertIn("Glace entravante de Rime", DB.spells)

    def test_dons_du_mj(self):
        e, ch = self.sheet(lvl=4)
        self.assertNotIn("Charme de vision dans le noir", e.feat_options())
        self.assertIn("Charme de vision dans le noir", e.feat_options(gm=True))
        self.assertTrue(e.add_gm_feat("Faveur de vigueur" if "Faveur de vigueur" in DB.feats else
                                      "Charme de vision dans le noir"))
        self.assertTrue(ch.dons_mj)


class AutomatisationAjoutsTests(unittest.TestCase):
    """v53 : traits des races importées et dons du MJ réellement appliqués."""

    def sheet(self, race="Humain", cls="Guerrier", lvl=5):
        ch = Engine.new_character(DB)
        ch.race = race
        ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
        e = Engine(DB, ch)
        e.normalize()
        return e, ch

    def test_traits_des_races_importees(self):
        e, _ = self.sheet("Elfe (Marque de l'ombre)")
        self.assertEqual([(s["nom"], s["niveau_requis"]) for s in e.racial_spells()],
                         [("Illusion mineure", 1), ("Invisibilité", 3)])
        self.assertIn("+1d4", e.imported_race_modifiers()[0][1]["competences"]["Discrétion"])
        e, _ = self.sheet("Humain (Marque du passage)")
        self.assertEqual(e.speed(), 10.5)
        e, _ = self.sheet("Nain (Marque de garde)")
        self.assertIn("hache d'armes", e.racial_weapon_proficiencies())
        e, _ = self.sheet("Demi-elfe (Marque de détection)")
        self.assertIn("Détection du poison et des maladies", [s["nom"] for s in e.racial_spells()])
        e, ch = self.sheet("Humain (Marque du passage)", "Magicien")
        self.assertTrue(any(s["nom"] == "Repli expéditif" for s in e.available_spells("Magicien")))
        e, ch = self.sheet("Drakéide métallique")
        ch.ascendance_raciale = "Or"
        e.normalize()
        second = next(a for a in e.race_actions() if a["nom"] == "Arme de souffle métallique")
        self.assertEqual((second["utilisations"], second["niveau"]), (1, 5))

    def test_rafale_de_vent_tour_de_magie(self):
        self.assertEqual(DB.spells["Rafale de vent"]["niveau"], 0)
        self.assertEqual(DB.spells["Bourrasque"]["niveau"], 2)

    def test_dons_du_mj_appliques(self):
        e, ch = self.sheet(lvl=20)
        hp, speed = e.hp_max(), e.speed()
        e.add_gm_feat("Faveur de vigueur (2014)")
        e.add_gm_feat("Faveur de vitesse (2014)")
        self.assertEqual((e.hp_max(), e.speed()), (hp + 40, speed + 9))
        e.add_gm_feat("Faveur de l'âme ardente")
        self.assertIn("feu", [t for t, _ in e.defenses()["immunites"]])
        self.assertIn("Mains brûlantes", [s["nom"] for s in e.feat_spells()])
        e.add_gm_feat("Faveur de chance")
        tr = next(t for t in e.resource_trackers() if t["key"] == "don_mj_faveur_de_chance")
        self.assertEqual((tr["total"], tr["recover"]), (1, "repos court"))
        e.add_gm_feat("Bénédiction de santé")
        self.assertEqual(e.feat_ability_cap("Constitution"), 22)
        ch.pv_actuels = 1
        e.add_gm_feat("Faveur de récupération (2014)")
        res = e.use_class_action("don_mj_faveur_de_recuperation_2014")
        self.assertTrue(res["ok"])
        self.assertGreater(ch.pv_actuels, 1)

    def test_charme_et_haute_magie(self):
        e, ch = self.sheet(cls="Magicien", lvl=20)
        nine = e.spell_slots()[8]
        e.add_gm_feat("Faveur de haute magie")
        self.assertEqual(e.spell_slots()[8], nine + 1)
        e.add_gm_feat("Charme de vision dans le noir")
        tr = next(t for t in e.resource_trackers() if t["key"] == "don_mj_charme_de_vision_dans_le_noir")
        self.assertEqual((tr["total"], tr["recover"]), (3, "jamais"))

    def test_rappel_des_dons_narratifs(self):
        e, ch = self.sheet()
        e.add_gm_feat("Disciple de Mogis")
        self.assertTrue(any("charmé ou effrayé" in x for x in e.remember_list().get("En défense", [])))


class InfobullesCompletesTests(unittest.TestCase):
    """v53 : les infobulles des tuiles donnent la règle complète (sorts et capacités)."""

    def test_texte_complet(self):
        self.assertGreater(len(DB.spells["Boule de feu"].get("description_complete", "")), 400)
        ch = Engine.new_character(DB)
        ch.classes = [{"nom": "Roublard", "niveau": 6, "sous_classe": "Assassin", "pv_jets": []}]
        e = Engine(DB, ch)
        e.normalize()
        tile = next(t for t in e.turn_actions() if t["id"] == "classe:sournoise")
        self.assertIn("coup critique", tile["regle_complete"])
        ch2 = Engine.new_character(DB)
        ch2.classes = [{"nom": "Magicien", "niveau": 5, "sous_classe": "", "pv_jets": []}]
        ch2.sorts["Magicien"] = [{"nom": "Boule de feu", "prepare": True}, {"nom": "Trait de feu", "prepare": True}]
        e2 = Engine(DB, ch2)
        e2.normalize()
        tiles = {t["id"]: t for t in e2.turn_actions()}
        self.assertIn("contourne les angles", tiles["sort:Boule de feu"]["description"])
        self.assertIn("Dégâts : 8d6", tiles["sort:Boule de feu"]["description"])
        self.assertIn("inflammable", tiles["sort:Trait de feu"]["description"])


class RetoursCreationEtPartieTests(unittest.TestCase):
    """v53 : familles d'espèces, icônes d'historique, actions d'arme décomptées, noms courts des tuiles."""

    def test_familles(self):
        from core.race_families import families
        e = Engine(DB, Engine.new_character(DB))
        e.normalize()
        groups = dict(families(e.race_options()))
        for n in ("Elfe des mers", "Elfe pâle", "Elfe astral", "Drow (Elfe noir)"):
            self.assertIn(n, groups["Elfe"])
        self.assertIn("Duergar", groups["Nain"])

    def test_icones_historiques_uniques(self):
        import collections
        sys.path.insert(0, str(ROOT / "tests"))
        import qt_stub
        qt_stub.install()
        from ui.card_picker import background_glyphs
        seen = collections.defaultdict(set)
        for n in DB.backgrounds:
            seen[background_glyphs(n)].add(n.replace(" (2024)", ""))
        self.assertEqual({k: v for k, v in seen.items() if len(v) > 1}, {})
        self.assertEqual(background_glyphs("Idiot du village"), ("cerveau", "spirale"))

    def test_actions_d_arme_decomptees(self):
        ch = Engine.new_character(DB)
        ch.classes = [{"nom": "Guerrier", "niveau": 3, "sous_classe": "", "pv_jets": []}]
        e = Engine(DB, ch)
        e.normalize()
        row = {"nom": "Frappe du pommeau", "action": "Action bonus", "recharge": "Repos court"}
        self.assertTrue(e.use_weapon_action(row)["ok"])
        self.assertTrue(ch.tour_bonus)
        self.assertFalse(e.use_weapon_action(row)["ok"])                 # plus de « spam »
        ch.tour_bonus = False
        self.assertFalse(e.weapon_action_state(row)[0])                  # 1 fois par repos court
        e.short_rest()
        self.assertTrue(e.weapon_action_state(row)[0])

    def test_noms_courts(self):
        sys.path.insert(0, str(ROOT / "tests"))
        import qt_stub
        qt_stub.install()
        from ui.combat_tab import CombatTab
        self.assertEqual(CombatTab.short_label("Attaque — Épée longue"), "Épée longue")
        self.assertEqual(CombatTab.short_label("Conduit divin : Renvoi des morts-vivants"), "Renvoi des\nmorts-vivants")


class IconesDeClasseTests(unittest.TestCase):
    """v53 : chaque classe a son icône composée (épée, masse, serpe et feuille, hache à deux mains…)."""

    def test_toutes_les_classes_ont_leur_icone(self):
        import qt_stub
        qt_stub.install()
        from core.action_icons import G, layered_body
        from core.rules import norm
        from ui.card_picker import CLASS_LAYERS
        for name in DB.class_names():
            key = norm(name.split(" (")[0])
            self.assertIn(key, CLASS_LAYERS, name)
            for part in CLASS_LAYERS[key]:
                self.assertIn(part[0], G, (name, part[0]))
            self.assertIn("<", layered_body(CLASS_LAYERS[key]))
        self.assertEqual([p[0] for p in CLASS_LAYERS["druide"]], ["serpe", "feuille"])
        self.assertEqual([p[0] for p in CLASS_LAYERS["roublard"]], ["dague", "masque", "cle"])
        self.assertEqual([p[0] for p in CLASS_LAYERS["artificier"]], ["marteau", "cle_plate", "fiole"])

    def test_dessins_de_classe_fournis(self):
        """Chaque classe a son dessin (data/images/classes) et sa couleur de pierre."""
        import qt_stub
        qt_stub.install()
        from core.rules import norm
        from ui.card_picker import CLASS_COLORS, class_icon_path
        for name in DB.class_names():
            self.assertIsNotNone(class_icon_path(name), name)
            self.assertIn(norm(name.split(" (")[0]), CLASS_COLORS, name)
        self.assertIsNone(class_icon_path("Classe inconnue"))


class IconesSoigneesTests(unittest.TestCase):
    """v53 : dessins soignés des armes, actions d'arme, manœuvres et sorts courants ; symboles des caractéristiques."""

    def test_dessins_branches(self):
        from core import action_icons as AI, art_armes as AA, art_sorts as AS, spell_icons as SI
        from core.rules import norm
        for k in AI.WEAPON_ART:                          # chaque arme connue a son dessin soigné
            self.assertIn(k, AI._drawn_weapons(), k)
        self.assertIn("TAILLE_FIXE", AI.weapon_body("Épée à deux mains"))
        self.assertNotIn("TAILLE_FIXE", AI.weapon_body("Hache d'armes"))
        self.assertEqual(AI.action_body("Parade"), AA.MANEUVERS["Parade"]())
        self.assertEqual(AI.action_body("Écorchure"), AA.ACTIONS["Écorchure"]())
        self.assertEqual(SI.spell_icon(DB.spells, "Boule de feu"), AS.SPELLS["Boule de feu"]())
        for fn in list(AA.WEAPONS.values()) + list(AA.ACTIONS.values()) + list(AA.MANEUVERS.values()) + \
                list(AS.SPELLS.values()):
            self.assertTrue(fn().startswith("<"))
        for n in DB.maneuvers:                           # chaque manœuvre a son dessin
            self.assertIn(norm(n), AI._drawn_actions(), n)

    def test_symboles_des_caracteristiques(self):
        import qt_stub
        qt_stub.install()
        from core.rules import ABILITIES
        from ui.ability_icons import icon_path
        for ab in ABILITIES:
            self.assertIsNotNone(icon_path(ab), ab)

    def test_actions_communes_et_capacites(self):
        from core import action_icons as AI, art_actions as AC, tile_icons as T
        for _key, name in T.COMMON:                      # chaque action commune a son dessin soigné
            self.assertIn(name, AC.COMMON, name)
        self.assertEqual(AI.action_body("Second souffle"), AC.FEATURES["Second souffle"]())
        self.assertEqual(AI.action_body("Forme sauvage (2024)"), AC.FEATURES["Forme sauvage"]())

    def test_sorts_dessines_existent(self):
        from core import art_sorts as AS, spell_icons as SI
        for name, fn in AS.SPELLS.items():               # chaque dessin correspond à un vrai sort de la base
            self.assertIn(name, DB.spells, name)
            self.assertEqual(SI.spell_icon(DB.spells, name), fn())
        self.assertGreaterEqual(len(AS.SPELLS), 100)

    def test_objets_et_motifs(self):
        import qt_stub
        qt_stub.install()
        from core import action_icons as AI, art_motifs as AM, art_objets as AO
        from core.tile_icons import ITEMS
        for _k, icon in ITEMS:                           # chaque icône d'objet a son dessin soigné
            self.assertIn(icon, AO.OBJECTS, icon)
        self.assertIs(AI.G["flamme"], AM.MOTIFS["flamme"])
        self.assertNotIn("<circle cx=\"49\" cy=\"49\"", AI.action_body("Pas du vent (2024)"))   # plus de médaillon

    def test_chaque_effet_a_son_dessin(self):
        from core import art_etats as AE, effects as FX
        for key, e in FX.EFFECTS.items():
            self.assertTrue(AE.effect_body(key, e["nom"]), key)

    def test_toutes_les_capacites_dessinees(self):
        import json
        from core import action_icons as AI
        reg = json.loads((ROOT / "data" / "action_icons.json").read_text(encoding="utf-8"))["actions"]
        for n in reg:                                    # plus aucune capacité composée automatiquement
            base = n.replace(" (2024)", "")
            self.assertNotEqual(AI.action_body(n), AI.compose(base, int(AI._registry().get("variantes", {}).get(base, 0))), n)


class CompatibiliteWindowsTests(unittest.TestCase):
    """v53 : aucun fichier du projet ne porte un nom réservé sous Windows (CON, PRN, AUX, NUL, COM1…, LPT1…) — sinon
    le dépôt ne s'extrait plus et la compilation de l'exécutable échoue."""

    def test_noms_de_fichiers(self):
        import os
        import re
        bad = re.compile(r"^(con|prn|aux|nul|com[0-9]|lpt[0-9])(\..*)?$", re.I)
        found = []
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "venv", ".venv", "build", "dist")]
            found += [os.path.join(base, n) for n in dirs + files if bad.match(n) or n.endswith((".", " "))]
        self.assertEqual(found, [])


def _race_sheet(race, cls="Guerrier", lvl=5, edition=""):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
    ch.race = race
    eng = Engine(DB, ch)
    if edition:
        eng.set_edition_mode(edition)
    eng.normalize()
    return eng


class ReglesRetours53Tests(unittest.TestCase):
    """v53 : Poussée d'adrénaline (PV temporaires), avantages des objets portés (Armure du zéphyr…), effets d'un
    20 naturel des armes magiques (Épée voleuse de vie…), Agrandissement / Rapetissement en deux tuiles."""

    def test_poussee_d_adrenaline_donne_des_pv_temporaires(self):
        for race, ed in (("Orc", ""), ("Orc (2024)", "2024")):
            eng = _race_sheet(race, edition=ed)
            act = next(a for a in eng.race_actions() if "adrenaline" in a["id"])
            self.assertEqual(act["pv_temp"], eng.prof, race)
            res = eng.use_class_action(act["id"])
            self.assertTrue(res["ok"])
            self.assertEqual(eng.ch.pv_temporaires, eng.prof)
            self.assertIn("PV temporaires", res["message"])

    def test_pv_temporaires_conditionnels_non_appliques(self):
        eng = _race_sheet("Homme lézard")
        act = next(a for a in eng.race_actions() if "machoires" in a["id"])
        self.assertFalse(act["pv_temp"])                 # « si elle touche » : à la main

    def _wear(self, eng, name):
        eng.ch.objets_magiques.append({"nom": name, "equipe": True, "harmonise": True})
        return Engine(DB, eng.ch)

    def test_armure_du_zephyr_avantage_acrobaties_et_js_dex(self):
        eng = self._wear(_race_sheet("Humain"), "Armure du zéphyr")
        self.assertIn("Objet : Armure du zéphyr", eng.check_mods("Dextérité", "Acrobaties")["avantage"])
        self.assertIn("Objet : Armure du zéphyr", eng.save_mods("Dextérité")["avantage"])
        self.assertFalse(eng.check_mods("Dextérité", "Discrétion")["avantage"])

    def test_bouclier_sentinelle_initiative_et_perception(self):
        eng = self._wear(_race_sheet("Humain"), "Bouclier sentinelle")
        self.assertIn("Objet : Bouclier sentinelle", eng.initiative_detail()["avantage"])
        self.assertIn("Objet : Bouclier sentinelle", eng.check_mods("Sagesse", "Perception")["avantage"])

    def test_avantage_restreint_non_applique(self):
        eng = self._wear(_race_sheet("Humain"), "Visière de Danoth")     # « qui reposent sur la vue »
        self.assertFalse(eng.check_mods("Sagesse", "Perception")["avantage"])

    def _sword(self, name, base="Épée longue"):
        eng = _race_sheet("Humain")
        self.assertTrue(eng.add_magic_gear(name, base))
        eng.ch.objets_magiques[-1]["harmonise"] = True
        eng.equip_magic_gear(len(eng.ch.objets_magiques) - 1)
        return eng, eng.ch.armes_cac[0]

    def test_epee_voleuse_de_vie_sur_un_20(self):
        eng, slot = self._sword("Épée voleuse de vie")
        self.assertFalse([o for o in eng.on_hit_options(slot, [], False) if o["key"].startswith("crit")])
        opts = eng.on_hit_options(slot, [], True)
        crit = [o for o in opts if o["key"].startswith("crit")]
        self.assertEqual(len(crit), 1)
        self.assertTrue(crit[0]["coche"])
        added = eng.apply_on_hit(opts, [o["key"] for o in crit])
        self.assertEqual(added, [("Épée voleuse de vie", "10")])
        self.assertEqual(eng.ch.pv_temporaires, 10)

    def test_autres_armes_sur_un_20(self):
        eng, slot = self._sword("Épée acérée")
        self.assertEqual([o["dice"] for o in eng.on_hit_options(slot, [], True) if o["key"].startswith("crit")], ["14"])
        eng, slot = self._sword("Cri du faucheur")
        opts = eng.on_hit_options(slot, [], True)
        self.assertEqual(eng.apply_on_hit(opts, [o["key"] for o in opts if o["key"].startswith("crit")]), [])
        self.assertEqual(eng.ch.pv_temporaires, 10)
        eng, slot = self._sword("Lamelune")
        self.assertEqual(eng.weapon_attack_spec(slot).crit_min, 19)

    def test_agrandissement_rapetissement_deux_tuiles(self):
        eng = _race_sheet("Humain", "Magicien", 3)
        eng.ch.sorts["Magicien"] = [{"nom": "Agrandissement/Rapetissement", "prepare": True}]
        eng = Engine(DB, eng.ch)
        tiles = {t["nom"]: t for t in eng.turn_actions() if t["id"].startswith("sort:Agrandissement")}
        self.assertEqual(set(tiles), {"Agrandissement", "Rapetissement"})
        res = eng.use_turn_action(tiles["Rapetissement"]["id"])
        self.assertEqual(res["effet"], "rapetissement")
        from core import tile_icons as TI
        from core.art_finitions import SPELL_VARIANTS
        kind, name, _ = TI.tile_icon(tiles["Agrandissement"])
        self.assertEqual((kind, name.split("#")[1]), ("sort", "agrandissement"))
        self.assertNotEqual(SPELL_VARIANTS["agrandissement"](), SPELL_VARIANTS["rapetissement"]())


class EnPartieRetours53Tests(unittest.TestCase):
    def setUp(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        self.win = MainWindow(DB)

    def test_bouton_pv_temporaires_et_encart_js(self):
        tab = self.win.combat_tab
        self.assertTrue(hasattr(tab, "temp_open_btn"))
        self.assertTrue(tab.apply_heal(5, True))
        self.assertEqual(self.win.ch.pv_temporaires, 5)
        from ui.hp_dialogs import HealDialog
        self.assertEqual(HealDialog(self.win, temp=True).values()[1], True)
        self.assertEqual(HealDialog(self.win).values()[1], False)

    def test_icones_de_caracteristiques_cliquables(self):
        tab = self.win.stats_tab
        self.assertTrue(hasattr(tab, "_roll_check"))


class ObjetSurMesureAvantagesTests(unittest.TestCase):
    """v53 : avantage / désavantage choisis dans le créateur d'objets ; ils s'annulent avec ceux de l'armure."""

    def test_avantage_annule_le_desavantage_d_armure_lourde(self):
        eng = _race_sheet("Humain")
        name = eng.add_custom_magic_item("Harnois du silence", "Armure", base="Harnois", bonus=1,
                                         avantages=["comp:Discrétion", "init"], desavantages=["comp:Persuasion"])
        eng.equip_magic_gear(len(eng.ch.objets_magiques) - 1)
        eng = Engine(DB, eng.ch)
        row = next(r for r in eng.skill_rows() if r["nom"] == "Discrétion")
        self.assertTrue(row["avantage"] and row["desavantage"])
        self.assertEqual(eng.skill_spec("Discrétion").mode, "")          # ni avantage ni désavantage
        self.assertEqual(eng.skill_spec("Persuasion").mode, "désavantage")
        self.assertEqual(eng.initiative_spec().mode, "avantage")
        self.assertIn("avantage : Discrétion", eng.ch.objets_perso[name]["description"])

    def test_objet_merveilleux_js(self):
        eng = _race_sheet("Humain")
        name = eng.add_custom_magic_item("Broche du roc", avantages=["js:Constitution"], js_bonus=1)
        eng.ch.objets_magiques[-1]["equipe"] = True
        eng = Engine(DB, eng.ch)
        fx = eng.save_mods("Constitution")
        self.assertIn("Objet : " + name, fx["avantage"])
        self.assertEqual(fx["bonus"], 1)


class AvantagesSousConditionTests(unittest.TestCase):
    """v53 : avantages sous condition proposés avant le d20, seulement si le personnage en possède un."""

    def test_rien_pour_un_personnage_ordinaire(self):
        eng = _race_sheet("Humain")
        for spec in (eng.skill_spec("Perception"), eng.save_spec("Sagesse"), eng.ability_check_spec("Force"),
                     eng.death_save_spec()):
            self.assertEqual(eng.situational_options(spec), [])

    def test_yeux_de_lynx_seulement_en_perception(self):
        eng = _race_sheet("Humain")
        eng.ch.objets_magiques.append({"nom": "Yeux de lynx", "equipe": True, "harmonise": True})
        eng = Engine(DB, eng.ch)
        opts = eng.situational_options(eng.skill_spec("Perception"))
        self.assertEqual([o["source"] for o in opts], ["Yeux de lynx"])
        self.assertIn("vue", opts[0]["label"])
        self.assertEqual(eng.situational_options(eng.skill_spec("Athlétisme")), [])
        spec = eng.apply_situational(eng.skill_spec("Perception"), ["Yeux de lynx"])
        self.assertEqual(spec.mode, "avantage")
        self.assertEqual(eng.apply_situational(eng.skill_spec("Perception"), []).mode, "")

    def test_annule_par_un_desavantage(self):
        eng = _race_sheet("Humain")
        eng.ch.objets_magiques.append({"nom": "Yeux de lynx", "equipe": True, "harmonise": True})
        eng = Engine(DB, eng.ch)
        spec = eng.skill_spec("Perception")
        spec.desavantage = ["Aveuglé"]
        self.assertEqual(eng.apply_situational(spec, ["Yeux de lynx"]).mode, "")

    def test_trait_racial_sur_les_jets_de_sauvegarde(self):
        eng = _race_sheet("Nain des collines")
        self.assertTrue(any("poison" in o["label"] for o in eng.situational_options(eng.save_spec("Constitution"))))
        self.assertEqual(eng.situational_options(eng.death_save_spec()), [])
        self.assertEqual(eng.situational_options(eng.skill_spec("Discrétion")), [])

    def test_objet_non_equipe_ignore(self):
        eng = _race_sheet("Humain")
        eng.ch.objets_magiques.append({"nom": "Yeux de lynx", "equipe": False, "harmonise": True})
        eng = Engine(DB, eng.ch)
        self.assertEqual(eng.situational_options(eng.skill_spec("Perception")), [])

    def test_machoires_affamees_pv_temp_si_touche(self):
        eng = _race_sheet("Homme lézard")
        act = next(a for a in eng.race_actions() if "machoires" in a["id"])
        self.assertEqual(act["pv_temp_si_touche"], eng.prof)
        self.assertEqual(eng.use_class_action(act["id"])["pv_temp_si_touche"], eng.prof)
        self.assertEqual(eng.ch.pv_temporaires, 0)        # pas appliqués avant la réponse « touché »


class AutomatisationVisibleTests(unittest.TestCase):
    """v53 : « appliqué automatiquement / proposé au jet / à gérer à la main » sur objets, traits, capacités, dons."""

    def test_objets(self):
        eng = _race_sheet("Humain")
        rep = eng.item_automation("Armure du zéphyr")
        self.assertTrue(any("Acrobaties" in x for x in rep["auto"]))
        rep = eng.item_automation("Yeux de lynx")
        self.assertTrue(any("vue" in x for x in rep["jet"]))
        rep = eng.item_automation("Cape de déplacement")
        self.assertFalse(rep["auto"])
        self.assertTrue(rep["main"])                     # illusion : à gérer soi-même
        rep = eng.item_automation("Baguette de boules de feu")
        self.assertTrue(any("Boule de feu" in x for x in rep["auto"]))
        self.assertEqual(rep["main"], [])

    def test_traits_raciaux(self):
        eng = _race_sheet("Homme lézard")
        traits = {c["nom"]: c["description"] for c in eng._race_trait_list()}
        rep = eng.text_automation("Mâchoires affamées", traits["Mâchoires affamées"], "race")
        self.assertTrue(any("tuile" in x for x in rep["auto"]))
        self.assertEqual(rep["main"], [])
        rep = eng.text_automation("Apnée", traits["Apnée"], "race")
        self.assertTrue(rep["main"])

    def test_rapport_html(self):
        from core.automation import report_html
        html = report_html({"auto": ["a"], "jet": [], "main": []})
        self.assertIn("Appliqué automatiquement", html)
        self.assertIn("rien", html)
        self.assertEqual(report_html({"auto": [], "jet": [], "main": []}), "")


class SurMesureEtModeLibreTests(unittest.TestCase):
    def test_description_objet_sur_mesure(self):
        eng = _race_sheet("Humain")
        n = eng.add_custom_magic_item("Harnois du silence", "Armure", base="Harnois", bonus=1,
                                      avantages=["comp:Discrétion"], resistances=["feu"])
        self.assertEqual(eng.ch.objets_perso[n]["description"],
                         "Harnois +1 (CA 19) — résistance : feu ; avantage : Discrétion.")
        n = eng.add_custom_magic_item("Cuir runique", "Armure", base="Armure de cuir", bonus=1,
                                      description="Gravée de runes naines.")
        self.assertEqual(eng.ch.objets_perso[n]["description"],
                         "Gravée de runes naines.\n\nArmure de cuir +1 (CA 12 + Dex).")
        n = eng.add_custom_magic_item("Lame ardente", "Arme", base="Épée longue", bonus=1,
                                      degats_sup=[{"des": "1d6", "type": "feu", "condition": "toujours"}])
        self.assertTrue(eng.ch.objets_perso[n]["description"].startswith("Épée longue +1 (1d8+1"))

    def test_bonus_raciaux_replies_en_mode_libre_seulement(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        self.assertTrue(win.stats_tab.abilities.compact_racial)
        from ui.abilities_tab import AbilitiesTab
        self.assertFalse(AbilitiesTab(win).compact_racial)   # assistant de création : inchangé


class PassifsSansConditionTests(unittest.TestCase):
    """v53 : effets passifs lus et appliqués (CA naturelle, vitesses, initiative, charge, sens, objets…)."""

    def sheet(self, race="Humain", cls="Guerrier", sub="", items=(), lvl=5):
        ch = Engine.new_character(DB)
        ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
        ch.race = race
        eng = Engine(DB, ch)
        eng.normalize()
        for it in items:
            ch.objets_magiques.append({"nom": it, "equipe": True, "harmonise": True})
        return Engine(DB, ch)

    def test_armure_naturelle(self):
        base = self.sheet().armor_class()[0]
        self.assertEqual(self.sheet("Homme lézard").armor_class()[0], base + 3)       # 13 + Dex au lieu de 10 + Dex
        self.assertEqual(self.sheet("Tortle").armor_class()[0], 17)
        self.assertEqual(self.sheet("Forgelier").armor_class()[0], base + 1)

    def test_vitesses_speciales_et_charge(self):
        self.assertIn("vol", self.sheet("Aarakocra").other_speeds())
        self.assertIn("nage", self.sheet("Triton").other_speeds())
        self.assertEqual(self.sheet().other_speeds(), {})
        self.assertEqual(self.sheet("Goliath").carry_multiplier(), 2)
        self.assertEqual(self.sheet(items=["Anneau de nage"]).other_speeds()["nage"], 12)

    def test_initiative_conil(self):
        eng = self.sheet("Conil")
        self.assertEqual(eng.initiative_detail()["total"], self.sheet().initiative_detail()["total"] + eng.prof)

    def test_objets(self):
        base = self.sheet()
        self.assertEqual(self.sheet(items=["Bottes du bourlingueur"]).speed(), base.speed() + 3)
        self.assertEqual(self.sheet(items=["Bracelets de défense"]).armor_class()[0], base.armor_class()[0] + 2)
        row = next(r for r in self.sheet(items=["Gants de chapardeur"]).skill_rows() if r["nom"] == "Escamotage")
        self.assertIn("+5", str(row["detail"]))
        self.assertEqual(self.sheet(items=["Lunettes de nuit"]).darkvision()["portee"], 18)
        st = self.sheet("Humain", "Magicien", items=["Bracelets d'archer"]).weapon_stats({"nom": "Arc long"})
        self.assertTrue(st["maitrise"])
        self.assertIn("Vision aveugle", self.sheet(items=["Sens draconiques"]).darkvision()["detail"])
        self.assertTrue(self.sheet(items=["Grovelthrash"]).item_languages())

    def test_armes_naturelles(self):
        st = self.sheet("Tabaxi").weapon_stats({"nom": "Mains nues"})
        self.assertTrue(st["degats"].startswith("1d6"))
        self.assertEqual(st["type_degats"], "tranchant")

    def test_ame_de_la_forge(self):
        eng = self.sheet(cls="Clerc", sub="Domaine de la Forge", lvl=6)
        eng.ch.armure["nom"] = "Harnois"
        forge = Engine(DB, eng.ch).armor_class()[0]
        plain = self.sheet(cls="Clerc", lvl=6)
        plain.ch.armure["nom"] = "Harnois"
        self.assertEqual(forge, Engine(DB, plain.ch).armor_class()[0] + 1)

    def test_rapport_reconnait_les_passifs(self):
        eng = self.sheet("Homme lézard")
        traits = {c["nom"]: c["description"] for c in eng._race_trait_list()}
        rep = eng.text_automation("Armure naturelle", traits["Armure naturelle"], "race")
        self.assertTrue(any("CA sans armure" in x for x in rep["auto"]))
