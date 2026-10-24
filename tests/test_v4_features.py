"""Tests : manifestations occultes, sorts accordés, PV au niveau supérieur, lignes progressives, styles/modèles,
nouvelles données (races, classes), fenêtre de confirmation en français."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core import rules as R  # noqa: E402
from core.data_loader import Database, parse_grants, parse_race_bonus  # noqa: E402
from core.engine import Engine  # noqa: E402

DB = Database(ROOT / "data")


def make(classes, **kw):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": n, "niveau": l, "sous_classe": s, "pv_jets": []} for n, l, s in classes]
    ch.methode = "manuel"
    ch.race = "Aucune race"
    ch.scores_manuel = {a: 10 for a in R.ABILITIES}
    ch.scores_manuel.update(kw)
    eng = Engine(DB, ch)
    eng.normalize()
    return eng


class NewDataTests(unittest.TestCase):
    def test_race_bonus_parsing(self):
        self.assertEqual(parse_race_bonus("Con +2, For +1")["fixe"], {"Constitution": 2, "Force": 1})
        self.assertEqual(parse_race_bonus("+2, +1")["libres"], [2, 1])
        r = parse_race_bonus("+2, +1 (ou +1, +1, +1)")
        self.assertEqual((r["libres"], r["alternative"]), ([2, 1], [1, 1, 1]))
        self.assertEqual(set(parse_race_bonus("Toutes +1")["fixe"].values()), {1})
        self.assertEqual(parse_race_bonus("Cha +2, +1"), {"fixe": {"Charisme": 2}, "libres": [1], "alternative": []})

    def test_races_json_drives_bonuses_and_languages(self):
        self.assertIn("Nain des collines", DB.races)
        self.assertEqual(DB.race_ability_rule("Nain des montagnes")["fixe"], {"Constitution": 2, "Force": 2})   # PHB : nain +2 Con, nain des montagnes +2 For
        eng = make([("Guerrier", 1, "")])
        eng.ch.race = "Nain des collines"
        eng.apply_race_languages()
        self.assertIn("Nain", eng.ch.langues_liste)
        # « Ténacité naine » : +1 PV par niveau
        base = make([("Guerrier", 3, "")]).hp_max()
        eng2 = make([("Guerrier", 3, "")])
        eng2.ch.race = "Nain des collines"
        # +1 PV/niveau du trait, plus le bonus de Constitution racial (Con +2 -> modificateur +1 par niveau)
        self.assertEqual(eng2.hp_max(), base + 3 + 3 * eng2.mod("Constitution"))

    def test_variant_plus_one_three_times(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.regle_libre = True
        self.assertEqual(eng.race_rule()["libres"], [2, 1])
        eng.ch.bonus_alt = True
        self.assertEqual(eng.race_rule()["libres"], [1, 1, 1])

    def test_arnaqueur_arcanique_is_a_third_caster(self):
        names = [s["nom"] for s in DB.subclasses("Roublard")]
        self.assertIn("Arnaqueur arcanique", names)
        eng = make([("Roublard", 3, "Arnaqueur arcanique")], Intelligence=14)
        self.assertEqual(eng.caster("Roublard")["liste"], "Magicien")
        self.assertEqual(eng.spell_slots()[0], 2)

    def test_artificer_masteries_from_new_format(self):
        info = DB.start_info("Artificier")
        self.assertEqual(info["nb_competences"], 2)
        self.assertTrue(info["armures"])

    def test_style_file_structure(self):
        self.assertIn("Duel", DB.styles_by_class["Guerrier"])
        self.assertIn("Combattant béni", DB.styles_by_class["Paladin"])
        self.assertIn("Combattant druidique", DB.styles_by_class["Rôdeur"])
        self.assertIn("Duel", DB.styles_by_class["Barde"])
        self.assertTrue({"Gardien", "Infiltré"} <= set(DB.armor_models))

    def test_domain_spells_ranger_pairs_and_sorcerer_lists(self):
        eng = make([("Rôdeur", 5, "Traqueur des ténèbres")])
        names = eng.domain_spells(eng.ch.classes[0])
        self.assertEqual(names, ["Déguisement", "Corde enchantée"])        # Traqueur des ténèbres (XGE) : rôdeur 3 et 5
        self.assertNotIn("1", names)
        self.assertEqual(make([("Ensorceleur", 5, "Âme divine")]).domain_spells({"nom": "Ensorceleur", "niveau": 5,
                         "sous_classe": "Âme divine"}), [])                     # XGE : pas de liste étendue
        eng = make([("Ensorceleur", 5, "Esprit aberrant")])
        spells = eng.domain_spells(eng.ch.classes[0])
        self.assertIn("Tentacules de Hadar", spells)
        self.assertNotIn("Communication à distance" if False else "Télékinésie", spells)   # sort de niveau 9


class StyleSlotTests(unittest.TestCase):
    def test_sword_bard_style_slot(self):
        eng = make([("Barde", 3, "Collège des Épées")])
        slots = eng.fighting_style_slots()
        self.assertEqual([(s["classe"], s["niveau_requis"], s["debloque"]) for s in slots], [("Barde", 3, True)])
        self.assertEqual(eng.style_options(slots[0]["id"]), ["Duel", "Combat à deux armes"])
        self.assertEqual(make([("Barde", 2, "")]).fighting_style_slots(), [])

    def test_armorer_armor_model(self):
        eng = make([("Artificier", 3, "Armurier")])
        slot = next(s for s in eng.fighting_style_slots() if s["kind"] == "modele")
        self.assertEqual(eng.style_options(slot["id"]), ["Gardien", "Infiltré"])
        eng.ch.styles_combat[slot["id"]] = "Infiltré"
        self.assertEqual(eng.armor_model()[0], "Infiltré")
        self.assertEqual(eng.speed(), 9 + 1.5)
        eng.ch.classes[0]["niveau"] = 15
        eng.normalize()
        self.assertEqual(eng.armor_model()[0], "Infiltré parachevé")


class ManifestationTests(unittest.TestCase):
    def test_grant_parsing(self):
        self.assertEqual(parse_grants("Lance le sort Armure de mage à volonté."),
                         [{"sort": "Armure de mage", "usage": "À volonté"}])
        g = parse_grants("Lance le sort Imprécation (1 emplacement de sort/long repos).")
        self.assertEqual(g[0]["sort"], "Imprécation")
        self.assertIn("repos long", g[0]["usage"])
        self.assertEqual(parse_grants("Lance le sort Simulacre de vie sur soi à volonté.")[0]["sort"], "Simulacre de vie")
        self.assertEqual(parse_grants("Lance Animation des morts (1 fois/long repos).")[0]["sort"], "Animation des morts")
        self.assertEqual(parse_grants("Modification d'apparence à volonté.")[0]["sort"], "Modification d'apparence")
        self.assertEqual(parse_grants("Avantage aux jets de sauvegarde de Constitution."), [])

    def test_catalog_prerequisites(self):
        m = DB.manifestations
        self.assertEqual((m["Lame assoiffée"]["pacte"], m["Lame assoiffée"]["niveau"]), ("Pacte de la lame", 5))
        self.assertEqual(m["Maître des formes"]["niveau"], 15)
        self.assertEqual(m["Armure d'ombres"]["pacte"], "")

    def test_slots_follow_warlock_level_and_feats(self):
        self.assertEqual(R.invocations_known(1), 0)
        self.assertEqual([R.invocations_known(n) for n in (2, 5, 7, 9, 12, 15, 18)], [2, 3, 4, 5, 6, 7, 8])
        eng = make([("Occultiste", 5, "")])
        self.assertEqual(eng.manifestation_slots()["total"], 3)
        # un don « Initié aux arcanes occultes » ajoute une manifestation, même sans Occultiste
        sid = "Guerrier|4"
        eng2 = make([("Guerrier", 4, "")])
        feat = next(n for n in DB.feats if "arcanes occultes" in n.lower())
        eng2.ch.ameliorations[sid] = {"mode": "don", "don": feat}
        self.assertEqual(eng2.manifestation_slots(), {"classe": 0, "dons": 1, "sources_dons": [feat], "total": 1})

    def test_prerequisites_pact_and_level(self):
        eng = make([("Occultiste", 5, "")])
        self.assertEqual(eng.manifestation_status("Armure d'ombres")[0], "ok")
        self.assertEqual(eng.manifestation_status("Lame assoiffée")[0], "ko")        # pacte non choisi
        eng.ch.pacte = "Pacte de la lame"
        self.assertEqual(eng.manifestation_status("Lame assoiffée")[0], "ok")
        self.assertEqual(eng.manifestation_status("Maître des formes")[0], "ko")      # niveau 15 requis
        eng.ch.pacte = "Pacte du grimoire"
        self.assertEqual(eng.manifestation_status("Lame assoiffée")[0], "ko")

    def test_magic_link_injects_spells_with_source(self):
        eng = make([("Occultiste", 5, "")])
        eng.ch.manifestations = ["Armure d'ombres", "Mille visages", "Vision occulte", "Esprit occulte"]
        spells = eng.granted_spells()
        self.assertEqual([g["nom"] for g in spells], ["Armure de mage", "Déguisement", "Détection de la magie"])
        self.assertTrue(all(g["source"].startswith("Manifestation : ") for g in spells))
        self.assertTrue(spells[0]["usage"].startswith("À volonté"))                # v37 : « (sans emplacement), sur soi »
        self.assertTrue(all(g["sort"] is not None for g in spells))                  # fiches retrouvées dans Magie-N.json
        eng.ch.manifestations = ["Mille visages"]
        self.assertEqual([g["nom"] for g in eng.granted_spells()], ["Déguisement"])  # mise à jour dynamique

    def test_locked_manifestation_grants_nothing(self):
        eng = make([("Occultiste", 5, "")])
        eng.ch.manifestations = ["Voile d'ombres"]                                    # niveau 15 requis
        self.assertEqual(eng.granted_spells(), [])
        self.assertTrue(any("Voile d'ombres" in w for w in eng.warnings()))

    def test_quota_warning_and_normalization(self):
        eng = make([("Occultiste", 2, "")])
        eng.ch.manifestations = ["Armure d'ombres", "Mille visages", "Vision occulte", "Inconnue", "Mille visages"]
        eng.normalize()
        self.assertEqual(eng.ch.manifestations, ["Armure d'ombres", "Mille visages", "Vision occulte"])
        self.assertTrue(any("Manifestations occultes" in w for w in eng.warnings()))

    def test_eldritch_blast_bonuses(self):
        eng = make([("Occultiste", 5, "")], Charisme=16)
        base = eng.cantrip_stats("Décharge occulte")
        eng.ch.sorts["Occultiste"] = [{"nom": "Décharge occulte", "prepare": True}]   # v37 : prérequis du sort
        eng.ch.manifestations = ["Décharge déchirante", "Lance occulte"]
        better = eng.cantrip_stats("Décharge occulte")
        self.assertEqual(base["degats"], "2 × 1d10")             # niveau 5 : deux rayons
        self.assertEqual(better["degats"], "2 × 1d10+3")         # v37 : + mod. de Charisme (16 -> +3), plus « +1 »
        self.assertEqual(better["portee"], "90 m")


class LevelUpTests(unittest.TestCase):
    def test_current_hp_follow_new_max_on_level_up(self):
        eng = make([("Guerrier", 1, "")], Constitution=14)
        eng.ch.pv_actuels = 3
        eng.set_class_level(0, 4)
        self.assertEqual(eng.ch.pv_actuels, eng.hp_max())
        eng.ch.pv_actuels = 5
        eng.set_total_level(6, 0)
        self.assertEqual(eng.ch.pv_actuels, eng.hp_max())

    def test_adding_a_class_counts_as_level_up(self):
        eng = make([("Guerrier", 2, "")])
        eng.ch.pv_actuels = 1
        eng.add_class("Magicien")
        self.assertEqual(eng.ch.pv_actuels, eng.hp_max())

    def test_level_down_only_clamps(self):
        eng = make([("Guerrier", 5, "")])
        eng.ch.pv_actuels = eng.hp_max()
        eng.set_class_level(0, 2)
        self.assertEqual(eng.ch.pv_actuels, eng.hp_max())
        eng.ch.pv_actuels = 4
        eng.set_class_level(0, 1)
        self.assertEqual(eng.ch.pv_actuels, 4)                                       # pas de soin à la descente

    def test_jets_mode_levels_up_cleanly(self):
        eng = make([("Guerrier", 1, "")])
        eng.ch.pv_mode = "jets"
        eng.ch.pv_actuels = 1
        eng.set_class_level(0, 3)
        self.assertEqual(eng.ch.pv_actuels, eng.hp_max())


class LazySlotTests(unittest.TestCase):
    def test_rule(self):
        self.assertEqual(R.lazy_slot_count([False] * 4), 1)                          # un seul emplacement au départ
        self.assertEqual(R.lazy_slot_count([True, False, False, False]), 2)
        self.assertEqual(R.lazy_slot_count([True, True, False, False]), 3)
        self.assertEqual(R.lazy_slot_count([True, True, True, False]), 4)
        self.assertEqual(R.lazy_slot_count([True, True, True, True]), 4)             # maximum 4
        self.assertEqual(R.lazy_slot_count([False, False, True, False]), 4)          # trou laissé par un retrait

    def test_combat_tab_shows_rows_progressively(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        tab = win.combat_tab

        def visible(rows):
            return sum(1 for w in rows if w["combo"]._st["kids"].get("setVisible") is not None)

        eng = win.engine
        eng.ch.armes_cac[0]["nom"] = "Épée longue"
        eng.ch.sorts_mineurs[0]["nom"] = "Trait de feu"
        win.changed()
        self.assertEqual(R.lazy_slot_count([bool(s["nom"]) for s in eng.ch.armes_cac]), 2)
        self.assertEqual(R.lazy_slot_count([bool(s["nom"]) for s in eng.ch.sorts_mineurs]), 2)
        self.assertEqual(tab.weapon_rows["armes_cac"][0]["combo"].currentText(), "Épée longue")


class DialogTests(unittest.TestCase):
    def test_buttons_are_french(self):
        import qt_stub
        qt_stub.install()
        from ui.dialogs import ConfirmDialog, ask_yes_no
        dlg = ConfirmDialog(None, "Modifications non enregistrées", "Voulez-vous abandonner les modifications ?")
        self.assertEqual((dlg.yes_btn.text(), dlg.no_btn.text()), ("Oui", "Non"))
        self.assertIsInstance(ask_yes_no(None, "t", "m"), bool)

    def test_main_window_uses_confirmation_dialog(self):
        import qt_stub
        qt_stub.install()
        import ui.main_window as mw
        calls = []
        saved = mw.ask_save_changes
        self.addCleanup(lambda: setattr(mw, "ask_save_changes", saved))
        mw.ask_save_changes = lambda parent, label="": calls.append(label) or "discard"
        win = mw.MainWindow(DB)
        self.assertTrue(win._confirm_discard())                                       # rien à perdre : pas de question
        win._dirty = True
        self.assertTrue(win._confirm_discard())
        self.assertEqual(len(calls), 1)


class UiSmokeV4(unittest.TestCase):
    def test_magic_manifestations_and_rp(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        eng = win.engine
        eng.ch.classes = [{"nom": "Occultiste", "niveau": 5, "sous_classe": "", "pv_jets": []}]
        eng.ch.manifestations = ["Armure d'ombres"]
        win.changed()
        self.assertEqual(len(win.magic_tab._granted_rows), 1)
        win.magic_tab.manif._on_pact()
        win.magic_tab.manif._on_remove()
        win.rp_tab.refresh()
        self.assertNotIn("Sans nom", win.rp_tab.caption.text())
        win.apply_appearance("cp2077", 14)
        for key in ("witcher", "masseffect", "zelda"):
            win.apply_appearance(key, 15)
        from ui.options_dialog import OptionsDialog
        dlg = OptionsDialog(win)
        dlg._choose("hollow")
        self.assertEqual((dlg.ok_btn.text(), dlg.cancel_btn.text()), ("Valider", "Annuler"))


if __name__ == "__main__":
    unittest.main()
