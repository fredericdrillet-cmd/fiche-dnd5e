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
