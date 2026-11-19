"""v52 : aides de jeu — lexique des règles (survol, F1, option « Aides pour débuter »)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from core.data_loader import Database  # noqa: E402

DB = Database(ROOT / "data")


class GlossaryTests(unittest.TestCase):
    def test_data_loaded(self):
        g = DB.glossary
        self.assertGreaterEqual(len(g.terms), 60)
        self.assertFalse(any("Lexique" in w for w in DB.warnings))
        self.assertIn("combat", g.tab_help)
        self.assertIn("Classe", g.step_help)
        self.assertIs(DB.view_2024().glossary, g)

    def test_find_whole_words_longest_first(self):
        g = DB.glossary
        found = [t["terme"] for t in g.find("Par une action bonus, JS de Sagesse DD 13 ; charmé. Charme-personne.", 10)]
        self.assertEqual(found, ["Action bonus", "Jet de sauvegarde", "DD", "Charmé"])
        self.assertEqual(g.find("Esquive instinctive"), [])            # « Esquiver » n'est pas une variante

    def test_definition_by_edition(self):
        g = DB.glossary
        rest = g.get("Repos long")
        self.assertIn("moitié", g.definition(rest, 2014))
        self.assertNotIn("moitié", g.definition(rest, 2024))
        self.assertIn("2014 :", g.definition(rest, 0))
        self.assertTrue(g.search("concentration"))


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        cls.win = MainWindow(DB)

    def test_rich_tip_has_definitions(self):
        from ui import common
        tip = common.rich_tip("Bouclier", "Réaction : +5 à la CA jusqu'au début de votre prochain tour.")
        self.assertIn("Lexique", tip)
        self.assertIn("Réaction", tip)
        self.assertNotIn("Lexique", common.rich_tip("Avantage", "Lancez deux dés."))   # le titre lui-même exclu

    def test_beginner_option(self):
        from ui import common
        win = self.win
        win.settings["aides_debutant"] = False
        win.refresh_help_banner()
        self.assertEqual(win.help_banner.text(), "")
        self.assertNotIn("<u>", common.make_label("Une action bonus", wrap=True).text())
        win.settings["aides_debutant"] = True
        win.tabs.currentWidget = lambda: win.combat_tab          # faux Qt : onglet courant imposé
        win.refresh_help_banner()
        self.assertIn("tuile", win.help_banner.text())
        self.assertIn("<u>action bonus</u>", common.make_label("Une action bonus", wrap=True).text())
        win.settings["aides_debutant"] = False

    def test_glossary_dialog(self):
        from ui.glossary_dialog import GlossaryDialog, term_html
        dlg = GlossaryDialog(self.win, DB.glossary, 2024, "concentration")
        self.assertTrue(dlg._shown)
        self.assertIn("(votre fiche)", term_html(DB.glossary, DB.glossary.get("Repos long"), 2024))

    def test_wizard_step_help(self):
        from ui.creation_wizard import CreationWizard
        self.win.settings["aides_debutant"] = True
        wiz = CreationWizard(self.win)
        wiz.go(2)
        self.assertIn("métier", wiz.step_help.text())
        self.win.settings["aides_debutant"] = False
        wiz.go(1)
        self.assertEqual(wiz.step_help.text(), "")


if __name__ == "__main__":
    unittest.main()


from core.engine import Engine  # noqa: E402


def _sheet(cls, lvl, edition="2014", sub=""):
    ch = Engine.new_character(DB)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": "", "pv_jets": []}]
    eng = Engine(DB, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
    eng.ch.classes[0]["sous_classe"] = sub
    eng.normalize()
    return eng


class TurnReminderTests(unittest.TestCase):
    def test_start_turn_resets_and_reminds(self):
        for ed in ("2014", "2024"):
            eng = _sheet("Barbare", 5, ed)
            eng.use_class_action("rage")
            eng.ch.tour_action = eng.ch.tour_bonus = True
            eng.ch.concentration = "Bénédiction"
            res = eng.start_turn()
            self.assertFalse(eng.ch.tour_action or eng.ch.tour_bonus)
            self.assertTrue(any(r.startswith("Rage") for r in res["rappels"]), ed)
            self.assertTrue(any("Concentration" in r for r in res["rappels"]))
        dying = _sheet("Guerrier", 3)
        dying.ch.pv_actuels = 0
        self.assertTrue(any("jet contre la mort" in r for r in dying.start_turn()["rappels"]))

    def test_text_triggers_both_editions(self):
        tree = _sheet("Barbare", 3, "2024", "Voie de l'Arbre-Monde")
        tree.use_class_action("rage")
        self.assertTrue(any(r.startswith("Vitalité de l'arbre") for r in tree.start_turn()["rappels"]))
        champ = _sheet("Guerrier", 18, "2024", "Champion")
        champ.ch.inspiration = False
        res = champ.start_turn()
        self.assertIn("Héros du champ d'honneur : Inspiration héroïque", res["appliques"])
        self.assertFalse(any(r.startswith("Survivant") for r in res["rappels"]))        # déjà appliqué
        for ed in ("2014", "2024"):
            barb = _sheet("Barbare", 7, ed)
            barb.roll_initiative(10)
            self.assertEqual([r for r in barb.initiative_reminders() if r.startswith("Instinct")], [])   # appliqué
        dance = _sheet("Barde", 6, "2024", "Collège de la Danse")
        dance.roll_initiative(10)
        self.assertTrue(any(r.startswith("Pirouettes coordonnées") for r in dance.initiative_reminders()))

    def test_end_turn_unused(self):
        for ed in ("2014", "2024"):
            eng = _sheet("Guerrier", 3, ed)
            msgs = eng.end_turn()
            self.assertTrue(any(m.startswith("Action non utilisée") for m in msgs))
            self.assertTrue(any("Second souffle" in m for m in msgs), ed)
            eng.ch.tour_action = eng.ch.tour_bonus = True
            self.assertEqual([m for m in eng.end_turn() if "non utilisée" in m], [])
        barb = _sheet("Barbare", 5, "2014")
        barb.use_class_action("rage")
        self.assertFalse(any("Entrer en rage" in m for m in barb.end_turn()))           # déjà en rage

    def test_ui_buttons(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        tab = win.combat_tab
        tab._on_new_round()
        self.assertIn("Début de votre tour", tab.turn_banner_text.text())
        tab._on_end_turn()
        self.assertIn("Fin de votre tour", tab.turn_banner_text.text())
        tab.show_turn_banner("", [])
        self.assertEqual(tab.turn_banner_text.text(), "")


class OnHitTests(unittest.TestCase):
    def test_options_nothing_checked_and_costs(self):
        for ed in ("2014", "2024"):
            rogue = _sheet("Roublard", 5, ed)
            rapier = {"nom": "Rapière", "bonus": 0, "maitrise": None}
            opts = rogue.on_hit_options(rapier, [("Marque du chasseur", "1d6")])
            self.assertEqual([o["key"] for o in opts], ["rider:0", "sournoise"])
            self.assertEqual(rogue.apply_on_hit(opts, []), [])                     # rien d'office
            self.assertEqual(rogue.apply_on_hit(opts, ["sournoise"]), [("Attaque sournoise", "3d6")])
            self.assertEqual(rogue.on_hit_options(rapier), [])                    # une fois par tour
            club = {"nom": "Massue", "bonus": 0, "maitrise": None}
            self.assertEqual(_sheet("Roublard", 5, ed).on_hit_options(club), [])  # ni finesse ni distance

    def test_smite_2014_vs_2024(self):
        sword = {"nom": "Épée longue", "bonus": 0, "maitrise": None}
        pal14 = _sheet("Paladin", 5, "2014")
        opts = pal14.on_hit_options(sword)
        pal14.apply_on_hit(opts, ["chatiment:2"])
        self.assertEqual(pal14.ch.emplacements_utilises[:2], [0, 1])
        self.assertTrue(pal14.on_hit_options(sword))                              # 2014 : à chaque coup
        pal24 = _sheet("Paladin", 5, "2024")
        opts = pal24.on_hit_options(sword)
        self.assertEqual(pal24.apply_on_hit(opts, ["chatiment:1", "chatiment:2"]), [("Châtiment divin", "2d8")])
        self.assertTrue(pal24.ch.tour_bonus)                                      # action bonus dépensée
        self.assertEqual(pal24.on_hit_options(sword), [])                         # un seul par tour
        self.assertEqual(pal14.on_hit_options({"nom": "Arc long", "bonus": 0, "maitrise": None}), [])

    def test_dialog(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.on_hit_dialog import OnHitDialog
        win = MainWindow(DB)
        pal = _sheet("Paladin", 5, "2014")
        opts = pal.on_hit_options({"nom": "Épée longue", "bonus": 0, "maitrise": None}, [("Faveur", "1d4")])
        dlg = OnHitDialog(win, "Attaque", opts)
        self.assertEqual(dlg.chosen(), [])
        dlg.checks["rider:0"].setChecked(True)
        self.assertEqual(dlg.chosen(), ["rider:0"])


class _R:
    def __init__(self, v):
        self.v = v

    def randint(self, a, b):
        return min(b, self.v)


class DefenseTests(unittest.TestCase):
    def test_shield_turns_hit_into_miss(self):
        for ed, spell in (("2014", "Bouclier"), ("2024", "Bouclier (2024)")):
            wiz = _sheet("Magicien", 3, ed)
            wiz.ch.sorts["Magicien"] = [{"nom": spell, "prepare": True}]
            ca = wiz.armor_class()[0]
            self.assertTrue(wiz.attack_check(ca + 2)["touche"])
            opt = next(o for o in wiz.defense_options("attaque") if o["key"] == "bouclier")
            self.assertTrue(wiz.use_defense(opt)["ok"])
            self.assertFalse(wiz.attack_check(ca + 2)["touche"], ed)            # +5 CA
            self.assertEqual(wiz.ch.emplacements_utilises[0], 1)
            self.assertEqual(wiz.defense_options("attaque"), [])                # réaction utilisée
            self.assertIn("Fin de : Bouclier (sort)", wiz.start_turn()["appliques"])

    def test_damage_reactions(self):
        for ed in ("2014", "2024"):
            rogue = _sheet("Roublard", 5, ed)
            opt = rogue.defense_options("degats")[0]
            res = rogue.use_defense(opt)
            self.assertEqual(rogue.damage_after_reactions(13, [res]), 6)
        monk14, monk24 = _sheet("Moine", 3, "2014"), _sheet("Moine", 3, "2024")
        self.assertEqual(monk14.defense_options("degats", melee=True), [])        # 2014 : distance seulement
        self.assertTrue(monk14.defense_options("degats", melee=False))
        opt = monk24.defense_options("degats", melee=True)[0]                     # 2024 : toute attaque
        res = monk24.use_defense(opt, _R(4))
        self.assertEqual(res["reduction"], 4 + monk24.mod("Dextérité") + 3)

    def test_dialog_take_damage(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.defense_dialog import DefenseDialog
        win = MainWindow(DB)
        win.engine = _sheet("Roublard", 5, "2024")
        win.engine.ch.pv_actuels = 30
        dlg = DefenseDialog(win, "degats", 12)
        dlg._use(win.engine.defense_options("degats")[0])
        self.assertEqual(dlg.final_damage()[0], 6)
        dlg._on_take()
        self.assertEqual(win.engine.ch.pv_actuels, 24)
        dlg2 = DefenseDialog(win, "attaque")
        dlg2.atk.setValue(1)
        self.assertFalse(dlg2.touches())


class RestSummaryTests(unittest.TestCase):
    def test_unused_resources(self):
        for ed in ("2014", "2024"):
            ftr = _sheet("Guerrier", 5, ed)
            self.assertTrue(any(u.startswith("Second souffle") for u in ftr.unused_before_rest("court")), ed)
            ftr.use_class_action("second_souffle")
            self.assertFalse(any(u.startswith("Second souffle") for u in ftr.unused_before_rest("court")))
            barb = _sheet("Barbare", 3, ed)
            self.assertEqual(barb.unused_before_rest("court"), [])            # la rage revient au repos long
            self.assertTrue(any(u.startswith("Rages") for u in barb.unused_before_rest("long")))
            cleric = _sheet("Clerc", 3, ed)
            self.assertTrue(any(u.startswith("Emplacements de sort") for u in cleric.unused_before_rest("long")))
            cleric.ch.emplacements_utilises[0] = 1
            self.assertFalse(any(u.startswith("Emplacements de sort") for u in cleric.unused_before_rest("long")))

    def test_dialog_shows_section(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        from ui.rest_dialog import RestDialog
        win = MainWindow(DB)
        win.engine = _sheet("Guerrier", 5, "2024")
        RestDialog(win, "short")


class NoveltyTests(unittest.TestCase):
    def test_level_up_marks_new_and_clears(self):
        for ed in ("2014", "2024"):
            eng = _sheet("Guerrier", 1, ed)
            before = eng.snapshot_known()
            eng.ch.classes[0]["niveau"] = 2
            eng.normalize()
            new = eng.mark_new_since(before)
            self.assertIn("act:sursaut", new, ed)                          # Fougue / Sursaut d'activité
            tile = next(t for t in eng.turn_actions() if (t.get("ref") or {}).get("action") == "sursaut")
            self.assertTrue(tile["nouveau"])
            eng.use_class_action("sursaut")
            self.assertFalse(eng.is_new("act:sursaut"))
            self.assertTrue(any(k.startswith("apt:") for k in eng.ch.nouveautes))
            eng.long_rest()
            self.assertEqual(eng.ch.nouveautes, [])

    def test_new_spell_badge_and_save(self):
        from core.character import Character
        eng = _sheet("Magicien", 3, "2024")
        eng.mark_new("sort:Projectile magique (2024)")
        self.assertEqual(Character.from_dict(eng.ch.to_dict()).nouveautes, ["sort:Projectile magique (2024)"])
        eng.cast_spell("Projectile magique (2024)")
        self.assertFalse(eng.is_new("sort:Projectile magique (2024)"))


class RememberTests(unittest.TestCase):
    def test_lists_by_edition(self):
        for ed in ("2014", "2024"):
            barb = _sheet("Barbare", 11, ed)
            groups = barb.remember_list()
            self.assertTrue(any(x.startswith("Attaque téméraire") for x in groups["Avant d'attaquer"]))
            rage = [x for x in groups["En défense"] if x.startswith("Rage implacable")]
            self.assertEqual(len(rage), 1)
            self.assertEqual("deux fois" in rage[0], ed == "2024")
        self.assertIn("Visée stable", " ".join(_sheet("Roublard", 3, "2024").remember_list()["Avant d'attaquer"]))
        self.assertNotIn("Visée stable", " ".join(_sheet("Roublard", 3, "2014").remember_list().get(
            "Avant d'attaquer", [])))                                         # option Tasha : jamais d'office

    def test_race_traits_only_from_race(self):
        eng = _sheet("Magicien", 4, "2014")
        eng.ch.race = "Gnome"
        eng.normalize()
        flat = " ".join(x for v in eng.remember_list().values() for x in v)
        self.assertIn("Ruse gnome", flat)
        self.assertNotIn("Action rusée", flat)                               # « Ruse » du roublard ≠ Ruse gnome

    def test_ui_box(self):
        import qt_stub
        qt_stub.install()
        from ui.main_window import MainWindow
        win = MainWindow(DB)
        win.engine = _sheet("Barbare", 5, "2024")
        win.combat_tab._refresh_remember()
        self.assertIn("Attaque téméraire", win.combat_tab.remember_text.text())
        win.combat_tab._on_remember_toggle()
        self.assertIn("Afficher", win.combat_tab.remember_toggle.text())
