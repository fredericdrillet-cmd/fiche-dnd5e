"""v52 (étape 2) : fusion de data/editions dans la base et filtrage des choix selon le mode d'édition."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def make(mode, classes=(("Magicien", 5),)):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": n, "niveau": lv, "sous_classe": "", "pv_jets": [], "edition": 2014} for n, lv in classes]
    ch.edition_mode = mode
    eng = Engine(DB, ch)
    eng.normalize()
    return eng


class MergeTests(unittest.TestCase):
    def test_stats(self):
        st = DB.edition_stats
        self.assertEqual(st["sous_classes"], 14)
        self.assertEqual(st["especes"], 10)
        self.assertGreater(st["sorts"], 400)
        self.assertGreater(st["dons"], 100)
        self.assertFalse([w for w in DB.warnings if "editions" in w])

    def test_missing_2014_content_added(self):
        oath = DB.subclass("Paladin", "Parjure")
        self.assertEqual(oath["edition"], 2014)
        self.assertTrue(oath["capacites"])
        self.assertIn("Chevalier de l'Écho", [s["nom"] for s in DB.subclasses("Guerrier")])
        self.assertIn("Filet", DB.weapons)
        hail = DB.find_spell("Grêle d'épines")
        self.assertEqual((hail["niveau"], hail["edition"], hail["classes"]), (1, 2014, ["Rôdeur"]))
        self.assertIsNone(DB.find_spell("Piques argentées"))          # = Barbes argentées, déjà présent

    def test_2024_content_suffixed_on_collision(self):
        fb = DB.find_spell("Boule de feu (2024)")
        self.assertEqual(fb["edition"], 2024)
        self.assertEqual(DB.find_spell("Boule de feu")["edition"], 2014)
        self.assertIn("Elfe (2024)", DB.races)
        self.assertEqual(DB.races["Elfe"]["edition"], 2014)
        self.assertEqual(DB.speeds["Goliath (2024)"], 10.5)
        acolyte = DB.backgrounds["Acolyte (2024)"]
        self.assertEqual(acolyte["caracteristiques_2024"], ["Intelligence", "Sagesse", "Charisme"])

    def test_official_feat_texts(self):
        durable = DB.feats["Dur à cuire"]                              # nom de l'app conservé (sauvegardes)
        self.assertEqual(durable["carac_choix"], ["Constitution"])
        self.assertIn("deux fois", durable["description"])
        mam = DB.feats["Maître des armures intermédiaires"]
        self.assertEqual((mam["asi_texte"], mam["carac_choix"]), ("Aucune", []))


class FilterTests(unittest.TestCase):
    def test_races_backgrounds_feats(self):
        e14, e24, lib = make("2014"), make("2024"), make("libre")
        self.assertNotIn("Elfe (2024)", e14.race_options())
        self.assertIn("Elfe (2024)", e24.race_options())
        self.assertNotIn("Elfe", e24.race_options())
        self.assertIn("Humain", e24.race_options())                   # race actuelle toujours visible
        self.assertTrue({"Elfe", "Elfe (2024)"} <= set(lib.race_options()))
        self.assertIn("Acolyte (2024)", e24.background_options())
        self.assertNotIn("Acolyte (2024)", e14.background_options())
        f24 = e24.feat_options()
        self.assertTrue(f24 and all(DB.feats[n]["edition"] == 2024 for n in f24))
        self.assertTrue(all(DB.feats[n]["edition"] == 2014 for n in e14.feat_options()))

    def test_spell_library(self):
        names14 = {s["nom"] for s in make("2014").available_spells("Magicien")}
        names24 = {s["nom"] for s in make("2024").available_spells("Magicien")}
        self.assertIn("Boule de feu", names14)
        self.assertNotIn("Boule de feu (2024)", names14)
        self.assertIn("Boule de feu (2024)", names24)
        self.assertNotIn("Boule de feu", names24)
        lib = {s["nom"] for s in make("libre").available_spells("Magicien")}
        self.assertTrue({"Boule de feu", "Boule de feu (2024)"} <= lib)

    def test_edition_tips_only_in_free_mode(self):
        items = {"Elfe (2024)": DB.races["Elfe (2024)"]}
        self.assertEqual(make("2024").edition_tips(items), {})
        self.assertTrue(make("libre").edition_tips(items)["Elfe (2024)"].startswith("Édition 2024"))


if __name__ == "__main__":
    unittest.main()


class Classes2024Tests(unittest.TestCase):
    def sheet(self, name, level, sub=""):
        ch = Engine.new_character(DB)
        ch.edition_mode = "2024"
        ch.classes = [{"nom": name, "niveau": level, "sous_classe": sub, "pv_jets": []}]
        eng = Engine(DB, ch)
        eng.normalize()
        return eng

    def test_view_and_classes(self):
        eng = self.sheet("Guerrier", 5)
        self.assertEqual(eng.sheet_edition, 2024)
        self.assertEqual(eng.ch.classes[0]["edition"], 2024)
        self.assertNotIn("Artificier", eng.db.class_names())             # pas d'Artificier en 2024
        self.assertEqual([s["nom"] for s in eng.db.subclasses("Guerrier")],
                         ["Maître de guerre", "Champion", "Chevalier occulte", "Soldat psi"])
        self.assertEqual(DB.subclasses("Guerrier")[0]["edition"], 2014)  # la base reste en 2014
        info = eng.db.start_info("Guerrier")
        self.assertIn("Armures lourdes", info["armures"])
        self.assertEqual(info["nb_competences"], 2)

    def test_2024_rules(self):
        pal = self.sheet("Paladin", 5)
        self.assertEqual(pal.spell_slots()[:2], [4, 2])
        c = pal.casters()[0]
        self.assertEqual((c["mode"], c["prepares_max"]), ("prepared", 6))
        self.assertEqual(self.sheet("Paladin", 1).spell_slots()[0], 2)    # sorts dès le niveau 1
        self.assertEqual(pal.subclass_level("Clerc"), 3)                 # sous-classe au niveau 3 partout
        wiz = self.sheet("Magicien", 1)
        self.assertEqual((wiz.casters()[0]["prepares_max"], wiz.casters()[0]["mineurs_max"]), (4, 3))
        monk = self.sheet("Moine", 5)
        self.assertEqual(monk.martial_arts_die(5), 8)                    # 2014 : d6
        res = dict(monk.resources(monk.ch.classes[0]))
        self.assertEqual(res["Points de concentration"], "5")

    def test_asi_and_epic_boon(self):
        eng = self.sheet("Guerrier", 20)
        levels = sorted(s["niveau"] for s in eng.asi_slots())
        self.assertEqual(levels, [4, 6, 8, 12, 14, 16, 19])

    def test_switching_edition(self):
        eng = self.sheet("Guerrier", 3)
        eng.set_edition_mode("2014")
        self.assertEqual((eng.sheet_edition, eng.ch.classes[0]["edition"]), (2014, 2014))
        self.assertIn("Maître de guerre", [s["nom"] for s in eng.db.subclasses("Guerrier")])


class Sheet2024Tests(unittest.TestCase):
    def new2024(self, cls="Guerrier", level=4):
        ch = Engine.new_character(DB)
        ch.classes = [{"nom": cls, "niveau": level, "sous_classe": "", "pv_jets": []}]
        eng = Engine(DB, ch)
        eng.normalize()
        eng.set_edition_mode("2024")
        return eng

    def test_race_and_background_switch(self):
        eng = self.new2024()
        self.assertEqual((eng.ch.race, eng.ch.historique), ("Humain (2024)", "Acolyte (2024)"))
        eng.set_edition_mode("2014")
        self.assertEqual((eng.ch.race, eng.ch.historique), ("Humain", "Acolyte"))

    def test_background_abilities_and_origin_feat(self):
        eng = self.new2024()
        self.assertEqual(eng.background_abilities(), ["Intelligence", "Sagesse", "Charisme"])
        rule = eng.race_rule()
        self.assertEqual((rule["origine"], rule["libres"]), ("historique", [2, 1]))
        eng.ch.bonus_libres = ["Force", "Sagesse"]                      # Force : hors de l'historique
        bonus = eng.race_bonus()
        self.assertEqual((bonus["Force"], bonus["Sagesse"]), (0, 1))
        origin = eng.origin_feat()
        self.assertEqual(DB.feats[origin]["edition"], 2024)
        self.assertIn(origin, eng.chosen_feats())

    def test_trackers_follow_2024_tables(self):
        eng = self.new2024("Clerc", 6)
        tr = {t["key"]: t for t in eng.resource_trackers()}
        self.assertEqual(tr["conduit"]["total"], 3)                    # 2014 : 2
        ftr = {t["key"]: t for t in self.new2024("Guerrier", 4).resource_trackers()}
        self.assertEqual(ftr["second_souffle"]["total"], 3)
        pal = {t["key"] for t in self.new2024("Paladin", 3).resource_trackers()}
        self.assertNotIn("sens_divin", pal)
        monk = {t["key"]: t for t in self.new2024("Moine", 5).resource_trackers()}
        self.assertEqual(monk["ki"]["label"], "Points de concentration")
        rgr = {t["key"]: t for t in self.new2024("Rôdeur", 5).resource_trackers()}
        self.assertEqual(rgr["ennemi_favori"]["total"], 3)
        self.assertNotIn("cap:ennemi_jure", rgr)


class StylesAndMasteryTests(unittest.TestCase):
    def sheet(self, cls, level, edition="2024"):
        ch = Engine.new_character(DB)
        ch.classes = [{"nom": cls, "niveau": level, "sous_classe": "", "pv_jets": []}]
        eng = Engine(DB, ch)
        eng.normalize()
        eng.set_edition_mode(edition)
        return eng

    def test_fighting_style_feats_2024(self):
        eng = self.sheet("Guerrier", 1)
        options = eng.style_options("Guerrier|1")
        self.assertEqual(len(options), 10)
        self.assertIn("Armes à deux mains", options)                    # nom 2024 « Arme à deux mains »
        self.assertNotIn("Technique supérieure", options)                # option de Tasha (2014)
        eng.ch.styles_combat["Guerrier|1"] = "Défense"
        eng.normalize()
        self.assertTrue(eng.style_active("Défense"))
        self.assertIn("Combattant béni", self.sheet("Paladin", 2).style_options("Paladin|1"))
        self.assertIn("Technique supérieure", self.sheet("Guerrier", 1, "2014").style_options("Guerrier|1"))

    def test_weapon_mastery_counts(self):
        self.assertEqual(self.sheet("Guerrier", 1).mastery_count(), 3)
        self.assertEqual(self.sheet("Barbare", 4).mastery_count(), 3)
        self.assertEqual(self.sheet("Roublard", 1).mastery_count(), 2)
        self.assertEqual(self.sheet("Magicien", 3).mastery_count(), 0)
        self.assertEqual(self.sheet("Magicien", 3, "2014").mastery_count(), 0)    # règle de la table inactive

    def test_weapon_mastery_choice(self):
        eng = self.sheet("Guerrier", 1)
        sword = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        eng.ch.armes_cac[0] = sword
        self.assertEqual(eng.mastery_weapons(), ["Épée longue"])          # arme équipée proposée par défaut
        self.assertEqual(eng.weapon_stats(sword)["botte"], "Sape")
        for w in ("Hache d’armes", "Arc long", "Rapière"):
            eng.set_mastery(w, True)
        self.assertFalse(eng.set_mastery("Fouet", True))                  # limite de 3 atteinte
        self.assertEqual(len(eng.mastery_weapons()), 3)
        eng.set_mastery("Épée longue", False)
        self.assertEqual(eng.weapon_stats(sword)["botte"], "")
        old = self.sheet("Guerrier", 1, "2014")
        old.set_house_rule("maitrises_armes_2014", True)
        self.assertIsNone(old.mastery_count())                            # 2014 + règle : toutes les armes
        old.ch.armes_cac[0] = sword
        self.assertEqual(old.weapon_stats(sword)["botte"], "Sape")

    def test_mastery_dialog_smoke(self):
        sys.path.insert(0, str(ROOT / "tests"))
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.mastery_dialog import MasteryDialog
        win = MainWindow(DB)
        win.engine = self.sheet("Guerrier", 1)
        dlg = MasteryDialog(win)
        dlg.checks["Arc long"].setChecked(True)
        dlg.accept()
        self.assertIn("Arc long", win.engine.ch.bottes_choisies)


class Warlock2024Tests(unittest.TestCase):
    def sheet(self, cls, level, edition="2024"):
        ch = Engine.new_character(DB)
        ch.classes = [{"nom": cls, "niveau": level, "sous_classe": "", "pv_jets": []}]
        eng = Engine(DB, ch)
        eng.normalize()
        eng.set_edition_mode(edition)
        return eng

    def test_invocations_from_level_1_and_pact_as_invocation(self):
        eng = self.sheet("Occultiste", 1)
        self.assertEqual(len(eng.db.manifestations), 28)
        self.assertEqual(eng.manifestation_slots()["classe"], 1)          # 2014 : 0 au niveau 1
        self.assertFalse(eng.pact_available())
        self.assertEqual(eng.pact_options(), [])
        eng.ch.manifestations = ["Pacte de la lame"]
        eng.normalize()
        self.assertEqual(eng.ch.pacte, "Pacte de la lame")
        self.assertEqual(eng.manifestation_status("Pacte de la lame"), ("ok", ""))
        self.assertFalse([m for m in self.sheet("Occultiste", 3).missing_choices() if "pacte" in m["message"].lower()])

    def test_invocation_prerequisites(self):
        eng = self.sheet("Occultiste", 12)
        self.assertEqual(eng.manifestation_status("Châtiment occulte")[0], "ko")          # sans Pacte de la lame
        eng.ch.manifestations = ["Pacte de la lame", "Châtiment occulte", "Lame dévorante"]
        eng.normalize()
        self.assertEqual(eng.manifestation_status("Châtiment occulte"), ("ok", ""))
        self.assertIn("Lame assoiffée", eng.manifestation_status("Lame dévorante")[1])
        eng.ch.manifestations.append("Lame assoiffée")
        self.assertEqual(eng.manifestation_status("Lame dévorante"), ("ok", ""))
        self.assertEqual(self.sheet("Occultiste", 3, "2014").manifestation_slots()["classe"], 2)

    def test_metamagic_2024(self):
        eng = self.sheet("Ensorceleur", 2)
        opts = eng.metamagic_option_set()
        self.assertEqual((opts["total"], len(opts["options"])), (2, 10))
        self.assertIn("Sort ample", opts["options"])                                   # nom 2024
        self.assertEqual(self.sheet("Ensorceleur", 10).metamagic_option_set()["total"], 4)
        self.assertIsNone(self.sheet("Ensorceleur", 2, "2014").metamagic_option_set())  # 2014 : niveau 3
        eng.ch.options_classe = {"metamagie": ["Sort ample", "Sort jumeau"]}
        self.assertEqual(eng.chosen_metamagic(), ["Sort ample", "Sort jumeau"])


class UiSheet2024Smoke(unittest.TestCase):
    def test_every_tab_with_2024_sheets(self):
        sys.path.insert(0, str(ROOT / "tests"))
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        for cls, level, invocations in (("Occultiste", 5, ["Pacte de la lame", "Châtiment occulte"]),
                                        ("Ensorceleur", 4, []), ("Guerrier", 3, []), ("Paladin", 6, [])):
            ch = Engine.new_character(DB)
            ch.classes = [{"nom": cls, "niveau": level, "sous_classe": "", "pv_jets": []}]
            eng = Engine(DB, ch)
            eng.normalize()
            eng.set_edition_mode("2024")
            ch.manifestations = list(invocations)
            eng.normalize()
            win.engine = eng
            win.refresh_all()
            for i in range(win.tabs.count()):
                win.tabs.setCurrentIndex(i)
            win.refresh_all()
            self.assertIs(win.combat_tab.db, eng.db)                     # les onglets lisent la base de la fiche
