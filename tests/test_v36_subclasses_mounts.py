"""Tests v36 : temps et CA lisibles, quota de langues, Chevalier runique, Soldat psi, Archer arcanique, montures,
écoles imposées (Chevalier occulte, Arnaqueur arcanique)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core.engine import Engine  # noqa: E402


def make(cls="Guerrier", lvl=3, sub="", race="Humain"):
    eng = Engine(DB, Engine.new_character(DB))
    eng.change_race(race)
    eng.ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng.normalize()
    return eng


def acts(eng):
    return {a["nom"]: a for a in eng.class_actions()}


def window(eng):
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    win = mw.MainWindow(DB)
    win.engine = eng
    win.refresh_all()
    return win


class UiFixTests(unittest.TestCase):
    def test_time_format(self):
        self.assertRegex(make().time_text(), r"^Jour \d+, \d\d:\d\d$")
        src = (ROOT / "ui" / "combat_tab.py").read_text(encoding="utf-8")
        self.assertIn("Jour & Heure :", src)

    def test_ac_breakdown(self):
        eng = make()
        eng.ch.armure.update({"nom": "Armure de cuir clouté", "bouclier": True, "bouclier_nom": "Bouclier"})
        eng.normalize()
        text = eng.ac_breakdown_text()
        self.assertTrue(text.startswith("CA de base (Armure de cuir clouté : 12) + Mod. Dextérité"))
        self.assertIn("Bouclier (+2)", text)
        self.assertTrue(text.endswith("= {}".format(eng.armor_class()[0])))

    def test_header_tooltips(self):
        src0 = (ROOT / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertIn('self.badges["ca"].setToolTip(rich_tip("Classe d\'armure", eng.ac_breakdown_text()', src0)
        window(make())                                        # construit sans erreur
        src = (ROOT / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertIn("Cliquez ici pour lancer l'assistant de montée de", src)

    def test_language_quota(self):
        eng = make()                                          # Humain : Commun + 1 au choix ; Acolyte : 2 au choix
        self.assertEqual(eng.languages_allowed(), 4)
        eng.ch.langues_liste = ["Commun"]
        eng.normalize()
        self.assertEqual(eng.languages_known(), 1)
        self.assertTrue(any("langue" in m["message"] for m in eng.missing_choices()))
        eng.ch.langues_liste = [n for n in DB.language_names()][:6]
        eng.normalize()
        self.assertTrue(any(w.startswith("Langues : 6 connues pour 4") for w in eng.warnings()))

    def test_language_feat_grant(self):
        eng = make()
        before = eng.languages_allowed()
        sid = "race|don"
        eng.change_race("Humain variant")
        eng.ch.ameliorations[sid] = {"mode": "don", "don": "Connaissance ancestrale"}
        eng.normalize()
        self.assertIn(("Don : Connaissance ancestrale", 2), eng.language_grants())
        self.assertGreater(eng.languages_allowed(), before - 1)

    def test_language_counter_widget(self):
        win = window(make())
        win.race_tab.refresh()
        self.assertIn("Langues choisies :", win.race_tab.lang_count.text())


class RuneKnightTests(unittest.TestCase):
    def test_choices_by_level(self):
        eng = make(lvl=3, sub="Chevalier runique")
        s = eng.option_sets()[0]
        self.assertEqual(s["total"], 2)
        self.assertNotIn("Rune de la tempête", s["options"])         # niveau 7
        self.assertEqual(make(lvl=7, sub="Chevalier runique").option_sets()[0]["total"], 3)
        self.assertIn("Runes (Chevalier runique) : 2 à choisir", [m["message"] for m in eng.missing_choices()])

    def test_rune_actions_and_rest(self):
        eng = make(lvl=3, sub="Chevalier runique")
        eng.set_class_option("runes", 0, "Rune du feu")
        eng.set_class_option("runes", 1, "Rune du nuage")
        a = acts(eng)
        self.assertEqual(a["Rune du feu"]["formule"], "2d6")
        self.assertEqual(a["Rune du nuage"]["type"], "Réaction")
        self.assertEqual(a["Puissance des géants"]["formule"], "1d6")
        self.assertTrue(eng.use_class_action("rune:rune-du-feu")["ok"])
        self.assertFalse(eng.use_class_action("rune:rune-du-feu")["ok"])
        eng.short_rest()
        self.assertTrue(eng.use_class_action("rune:rune-du-feu")["ok"])
        self.assertIn("Rune du feu (passif)", [p["nom"] for p in eng.class_passives()])
        giant = next(t for t in eng.resource_trackers("combat") if t["key"] == "puissance_geants")
        self.assertEqual((giant["total"], giant["recover"]), (eng.prof, "repos long"))

    def test_giant_die_and_rune_uses_scale(self):
        eng = make(lvl=15, sub="Chevalier runique")
        eng.set_class_option("runes", 0, "Rune du givre")
        self.assertEqual(acts(eng)["Puissance des géants"]["formule"], "1d8")
        tr = next(t for t in eng.resource_trackers("combat") if t["key"] == "rune:rune-du-givre")
        self.assertEqual(tr["total"], 2)                                 # Maître des runes
        self.assertIn("Bouclier runique", acts(eng))

    def test_reset_on_subclass_change(self):
        eng = make(lvl=3, sub="Chevalier runique")
        eng.set_class_option("runes", 0, "Rune du feu")
        eng.ch.classes[0]["sous_classe"] = "Champion"
        eng.normalize()
        self.assertEqual(eng.ch.options_classe, {})
        self.assertNotIn("Rune du feu", acts(eng))


class PsiWarriorTests(unittest.TestCase):
    def test_dice_and_actions(self):
        eng = make(lvl=5, sub="Soldat psi")
        tr = next(t for t in eng.resource_trackers("combat") if t["key"] == "psi_guerrier")
        self.assertEqual((tr["total"], tr["de"]), (2 * eng.prof, "d8"))
        a = acts(eng)
        for name in ("Champ protecteur", "Frappe psionique", "Mouvement télékinétique", "Récupération psionique"):
            self.assertIn(name, a)
        self.assertNotIn("Bond psi", a)                                   # niveau 7
        self.assertTrue(a["Frappe psionique"]["formule"].startswith("1d8"))

    def test_free_use_then_die_then_recovery(self):
        eng = make(lvl=7, sub="Soldat psi")
        self.assertIn("gratuit", eng.use_class_action("psi_tk")["message"])
        eng.use_class_action("psi_tk")
        self.assertEqual(eng.resource_used("psi_guerrier"), 1)
        eng.use_class_action("psi_recup_g")
        self.assertEqual(eng.resource_used("psi_guerrier"), 0)
        self.assertIn("Bond psi", acts(eng))


class ArcaneArcherTests(unittest.TestCase):
    def test_options_and_uses(self):
        eng = make(lvl=3, sub="Archer arcanique")
        self.assertEqual(eng.option_sets()[0]["total"], 2)
        eng.set_class_option("tirs", 0, "Flèche d'ombre")
        eng.set_class_option("tirs", 1, "Flèche perforante")
        a = acts(eng)
        self.assertEqual((a["Flèche d'ombre"]["formule"], a["Flèche d'ombre"]["type_degats"]), ("2d6", "psychiques"))
        self.assertEqual(a["Flèche perforante"]["formule"], "1d6")
        self.assertTrue(eng.use_class_action("tir:fleche-d-ombre")["ok"])
        self.assertTrue(eng.use_class_action("tir:fleche-perforante")["ok"])
        self.assertFalse(eng.use_class_action("tir:fleche-d-ombre")["ok"])     # 2 utilisations
        eng.short_rest()
        self.assertTrue(eng.use_class_action("tir:fleche-d-ombre")["ok"])

    def test_level_18_doubles(self):
        eng = make(lvl=18, sub="Archer arcanique")
        self.assertEqual(eng.option_sets()[0]["total"], 6)
        eng.set_class_option("tirs", 0, "Flèche explosive")
        self.assertEqual(acts(eng)["Flèche explosive"]["formule"], "4d6")


class MountTests(unittest.TestCase):
    def test_seven_mounts(self):
        mounts = {e["id"]: e for e in DB.entities.values() if e["entity_type"] == "mount"}
        self.assertEqual(set(mounts), {"cheval_selle", "cheval_trait", "cheval_guerre", "poney", "mule", "chameau",
                                       "matin"})
        war = mounts["cheval_guerre"]
        self.assertEqual((war["ac"], war["hp_base"], war["speed"]["walk"]), (11, 19, "18m"))
        eng = make()
        inst = eng.menagerie_add("cheval_guerre")
        sh = eng.entity_sheet(inst)
        self.assertEqual(sh["pv_max"], 19)
        self.assertEqual(sh["actions"][0]["damage_dice"].replace(" ", ""), "2d6+4")

    def test_cavalier_hint_and_tab_name(self):
        eng = make(lvl=3, sub="Cavalier")
        hint = next(h for h in eng.companion_hints() if "Cavalier" in h["texte"])
        self.assertIn("cheval_guerre", hint["recommandes"])
        eng.menagerie_add("cheval_guerre")
        self.assertFalse(any("Cavalier" in h["texte"] for h in eng.companion_hints()))
        win = window(make())
        self.assertEqual(win._tab_name("menagerie"), "Ménagerie & Montures")

    def test_tool_idempotent(self):
        import json
        sys.path.insert(0, str(ROOT / "tools"))
        import add_mounts
        data = json.loads((ROOT / "data" / "Familiers_Invocations.json").read_text(encoding="utf-8"))
        self.assertEqual(sum(1 for e in data if e["entity_type"] == "mount"), len(add_mounts.MOUNTS))


class SchoolTests(unittest.TestCase):
    def test_eldritch_knight(self):
        eng = make(lvl=3, sub="Chevalier occulte")
        r = eng.school_restriction("Guerrier")
        self.assertEqual((r["ecoles"], r["libres_max"]), (("Évocation", "Abjuration"), 1))
        self.assertTrue(eng.school_check("Guerrier", DB.find_spell("Bouclier"))[0])            # abjuration
        charm = DB.find_spell("Charme-personne")
        ok, why = eng.school_check("Guerrier", charm)
        self.assertTrue(ok)
        self.assertIn("Sort libre", why)
        eng.ch.sorts["Guerrier"] = [{"nom": "Charme-personne", "prepare": True}]
        eng.normalize()
        self.assertFalse(eng.school_check("Guerrier", DB.find_spell("Sommeil"))[0])
        self.assertEqual(make(lvl=8, sub="Chevalier occulte").school_restriction("Guerrier")["libres_max"], 2)

    def test_arcane_trickster_mage_hand(self):
        eng = make("Roublard", 3, "Arnaqueur arcanique")
        self.assertIn("Main de mage", [s["nom"] for s in eng.ch.sorts.get("Roublard", [])])
        self.assertIn("Main de mage arcanique", acts(eng))
        self.assertEqual(eng.school_restriction("Roublard")["ecoles"], ("Enchantement", "Illusion"))
        eng.ch.classes[0]["sous_classe"] = "Voleur"
        eng.normalize()
        self.assertNotIn("Main de mage", [s["nom"] for s in eng.ch.sorts.get("Roublard", [])])

    def test_excess_off_school_is_incoherence(self):
        eng = make(lvl=3, sub="Chevalier occulte")
        eng.ch.sorts["Guerrier"] = [{"nom": "Charme-personne", "prepare": True}, {"nom": "Sommeil", "prepare": True}]
        eng.normalize()
        self.assertTrue(any("hors Évocation / Abjuration" in w for w in eng.warnings()))

    def test_other_classes_unrestricted(self):
        eng = make("Magicien", 3)
        self.assertIsNone(eng.school_restriction("Magicien"))
        self.assertTrue(eng.school_check("Magicien", DB.find_spell("Charme-personne"))[0])


if __name__ == "__main__":
    unittest.main()
