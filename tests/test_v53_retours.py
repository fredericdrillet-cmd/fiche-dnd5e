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

    def test_web_refuse_au_dela_de_la_limite(self):
        from web import service
        e, ch = self.fresh()
        for n in self.LINKED:
            e.add_magic_item(n)
        for i in range(3):
            e.set_equipped(i, True)
        res = service.apply(ch.to_dict(), [{"op": "magic_equip", "idx": 3, "value": True}])
        self.assertIn("3 / 3", json_dump(res))


def json_dump(obj) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False)
