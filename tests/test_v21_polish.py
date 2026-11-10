"""Tests v21 : textes des capacités (manœuvres, Conduit divin, infobulles), Chant de la lame, passifs, actions
d'armes -> d20, synchronisation des réactions, JS condensés, sorts à PV temporaires, Armure de mage, sorts accordés
lançables, changement de classe et option Multiclassage."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core import dice as D  # noqa: E402
from core.engine import Engine  # noqa: E402


def make(c, lvl, sub=""):
    eng = Engine(DB, Engine.new_character(DB))
    eng.ch.classes = [{"nom": c, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng.normalize()
    return eng


def window(c, lvl, sub=""):
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    win = mw.MainWindow(DB)
    win.ch.classes = [{"nom": c, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    win.changed()
    return win


class TextTests(unittest.TestCase):
    def test_tooltips_clean(self):
        from ui.common import rich_tip
        tip = rich_tip("Déluge de coups", "Deux frappes.<br/><i>Action bonus</i>\nKi")
        self.assertIn("<br/>", tip)
        self.assertNotIn("&lt;br/&gt;", tip)
        self.assertNotIn("&lt;i&gt;", tip)
        self.assertIn("<i>Action bonus</i>", tip)
        self.assertIn("&lt;script&gt;", rich_tip("x", "<script>"))   # le reste reste échappé

    def test_title_without_ampersand(self):
        src = (ROOT / "ui" / "combat_tab.py").read_text(encoding="utf-8")
        self.assertIn('QGroupBox("⚔ Actions, capacités de classe")', src)

    def test_maneuver_hint(self):
        win = window("Guerrier", 3, "Maître de guerre")
        ct = win.combat_tab
        row = ct._action_row("manoeuvre")
        row["option"].setCurrentIndex(row["option"].findText("Riposte"))
        ct._update_hint("manoeuvre")
        self.assertIn("Réaction", row["state"].text())
        self.assertIn("DD", row["state"].text())

    def test_channel_divinity_by_oath(self):
        eng = make("Paladin", 3, "Serment de Vengeance")
        opts = eng.channel_options("Paladin")
        self.assertEqual([o["nom"] for o in opts], ["Condamnation de l'ennemi", "Vœu d'hostilité"])
        self.assertTrue(all(o["court"] for o in opts))
        res = eng.use_class_action("conduit_paladin", choice="Vœu d'hostilité")
        self.assertTrue(res["ok"])
        self.assertIn("voeu_inimitie", eng.ch.effets_actifs)
        win = window("Paladin", 3, "Serment de Dévotion")
        row = win.combat_tab._action_row("conduit_paladin")
        self.assertEqual(row["options"][0]["nom"], "Arme sacrée")
        win.combat_tab._update_hint("conduit_paladin")
        self.assertTrue(row["state"].text())


class ResourcesAndPassives(unittest.TestCase):
    def test_bladesong_toggle(self):
        eng = make("Magicien", 2, "Chantelame")
        tr = {t["key"]: t for t in eng.resource_trackers("combat")}
        self.assertEqual(tr["chant_lame"]["total"], 2)
        self.assertTrue(eng.use_class_action("chant_lame")["ok"])
        self.assertIn("chant_lame", eng.ch.effets_actifs)
        a = next(x for x in eng.class_actions() if x["id"] == "chant_lame")
        self.assertTrue(a["actif"])
        eng.use_class_action("chant_lame")                      # fin : gratuit
        self.assertNotIn("chant_lame", eng.ch.effets_actifs)
        self.assertEqual(eng.resource_used("chant_lame"), 1)
        eng.ch.armure["nom"] = next(n for n, a in DB.armors.items() if a.get("categorie") == "lourde")
        a = next(x for x in eng.class_actions() if x["id"] == "chant_lame")
        self.assertFalse(a["disponible"])

    def test_passives(self):
        eng = make("Barbare", 11, "")
        names = [p["nom"] for p in eng.class_passives()]
        self.assertIn("Rage implacable", names)
        self.assertNotIn("Attaque téméraire", names)            # déjà une action
        win = window("Barbare", 11, "")
        self.assertIn("Rage implacable", win.combat_tab._pass_key)


class ReactionAndWeaponTests(unittest.TestCase):
    def test_reaction_sync(self):
        win = window("Roublard", 5)
        ct = win.combat_tab
        ct._on_action("esquive_instinctive")
        self.assertTrue(win.ch.reaction_utilisee)
        self.assertIn("Esquive instinctive", win.ch.reaction_utilisee)
        a = next(x for x in win.engine.class_actions() if x["id"] == "esquive_instinctive")
        self.assertFalse(a["disponible"])
        win.engine.new_round()
        self.assertTrue(next(x for x in win.engine.class_actions() if x["id"] == "esquive_instinctive")["disponible"])
        eng = make("Guerrier", 3, "Maître de guerre")
        eng.use_class_action("manoeuvre", choice="Riposte")
        self.assertTrue(eng.ch.reaction_utilisee)
        self.assertFalse(eng.use_class_action("manoeuvre", choice="Parade")["ok"])
        self.assertTrue(eng.use_class_action("manoeuvre", choice="Attaque précise")["ok"])

    def test_weapon_action_rolls_attack(self):
        import ui.combat_tab as ct_mod
        win = window("Guerrier", 5)
        weapon = next(n for n, w in DB.weapons.items() if w["type"] == "cac" and n != "Mains nues")
        win.ch.armes_cac[0]["nom"] = weapon
        win.changed()
        rows = win.engine.weapon_actions(win.ch.armes_cac[0])
        self.assertTrue(rows)
        spec = win.engine.weapon_action_spec(win.ch.armes_cac[0], rows[0])
        self.assertIn(rows[0]["nom"], spec.title)
        self.assertTrue(spec.terms)
        got = []
        orig = ct_mod.roll_dice
        self.addCleanup(lambda: setattr(ct_mod, "roll_dice", orig))
        ct_mod.roll_dice = lambda w, s: got.append(s)
        win.combat_tab._on_weapon_action("armes_cac", 0, rows[0])
        self.assertEqual(len(got), 1)

    def test_condensed_saves(self):
        win = window("Guerrier", 1)
        cells = win.combat_tab.save_cells
        self.assertEqual(len(cells), 6)
        self.assertTrue(cells["Force"]["label"].text().startswith("●"))          # maîtrise du guerrier
        self.assertTrue(cells["Intelligence"]["label"].text().startswith("○"))


class SpellTests(unittest.TestCase):
    def test_temp_hp_formula(self):
        eng = make("Magicien", 5)
        self.assertTrue(eng.temp_hp_spell("Simulacre de vie"))
        self.assertEqual(eng.temp_hp_formula("Simulacre de vie", 1), "1d4+4")
        self.assertEqual(eng.temp_hp_formula("Simulacre de vie", 3), "1d4+14")
        self.assertEqual(eng.temp_hp_formula("Armure d'Agathys", 2), "10")
        eng.ch.pv_temporaires = 12
        self.assertEqual(eng.apply_temp_hp(8), 12)              # pas de cumul : on garde le plus haut
        self.assertEqual(eng.apply_temp_hp(15), 15)

    def test_cast_temp_hp_with_upcast(self):
        import ui.magic_tab as mt
        win = window("Magicien", 5)
        win.ch.sorts["Magicien"] = [{"nom": "Simulacre de vie", "prepare": True}]
        win.ch.pv_temporaires = 0
        win.changed()
        saved = (mt.ask_choice, mt.roll_damage_dialog)
        self.addCleanup(lambda: (setattr(mt, "ask_choice", saved[0]), setattr(mt, "roll_damage_dialog", saved[1])))
        mt.ask_choice = lambda parent, title, msg, options: next(o for o in options if o.startswith("Niveau 3"))
        seen = []
        mt.roll_damage_dialog = lambda w, spec: seen.append(spec) or D.DamageResult([(4, 3, 1)], 14, 17)
        self.assertTrue(win.magic_tab.cast("Simulacre de vie"))
        self.assertEqual(seen[0].formula, "1d4+14")
        self.assertEqual(seen[0].kind, "pv_temp")
        self.assertEqual(win.ch.pv_temporaires, 17)
        self.assertEqual(win.ch.emplacements_utilises[2], 1)    # emplacement de niveau 3 dépensé

    def test_mage_armor_warning(self):
        import ui.magic_tab as mt
        win = window("Magicien", 3)
        win.ch.armure["nom"] = next(n for n, a in DB.armors.items() if a.get("categorie") == "légère")
        saved = mt.ask_yes_no
        self.addCleanup(lambda: setattr(mt, "ask_yes_no", saved))
        asked = []
        mt.ask_yes_no = lambda *a, **k: asked.append(a[2]) or False
        self.assertFalse(win.magic_tab.cast("Armure de mage"))
        # v43 : un magicien ne maîtrise pas l'armure légère -> incantation impossible (règle du PHB)
        self.assertIn("armure non maîtrisée", asked[0])
        self.assertEqual(win.ch.emplacements_utilises[0], 0)

    def test_granted_spell_castable(self):
        import ui.magic_tab as mt
        saved = mt.ask_choice
        self.addCleanup(lambda: setattr(mt, "ask_choice", saved))
        mt.ask_choice = lambda parent, title, msg, options: options[0]          # « Sur soi »
        win = window("Magicien", 3)
        win.engine.add_gm_spell("Armure de mage", "À volonté", "Relique")
        win.changed()
        tab = win.magic_tab
        idx = next(i for i, r in enumerate(tab._granted_rows) if r["nom"] == "Armure de mage")
        tab.granted.setCurrentRow(idx)
        tab._on_mine_select(tab.granted, idx)
        tab._on_cast_btn()
        self.assertIn("armure_mage", win.ch.effets_actifs)
        self.assertEqual(win.ch.emplacements_utilises[0], 0)    # à volonté : aucun emplacement


class ClassChangeTests(unittest.TestCase):
    def test_change_purges_old_class(self):
        eng = make("Barbare", 5)
        eng.use_class_action("rage")
        eng.ch.sorts["Barbare"] = []
        self.assertTrue(eng.change_class(0, "Moine"))
        self.assertNotIn("rage", eng.ch.effets_actifs)
        self.assertNotIn("rage", eng.ch.ressources_utilisees)
        eng = make("Occultiste", 3)
        eng.ch.manifestations = ["X"]
        eng.ch.pacte_utilises = 1
        eng.change_class(0, "Guerrier")
        self.assertEqual((eng.ch.manifestations, eng.ch.pacte_utilises), ([], 0))

    def test_multiclass_option(self):
        from core.character import Character
        eng = make("Guerrier", 3)
        self.assertFalse(eng.ch.multiclassage)
        self.assertTrue(eng.add_class("Magicien"))
        self.assertTrue(eng.ch.multiclassage)
        removed = eng.set_multiclass(False)
        self.assertEqual(removed, ["Magicien"])
        self.assertEqual([c["nom"] for c in eng.ch.classes], ["Guerrier"])
        old = Character.from_dict({"classes": [{"nom": "Guerrier", "niveau": 1}, {"nom": "Magicien", "niveau": 1}]})
        self.assertTrue(old.multiclassage)                      # anciennes sauvegardes multiclassées

    def test_ui_gate(self):
        win = window("Guerrier", 3)
        win.settings["mode_libre"] = True                 # v48 : ajout direct de classe en Mode libre seulement
        tab = win.classes_tab
        tab.refresh()
        state = {}
        tab.add_btn.setEnabled = lambda v: state.__setitem__("add", v)
        tab.refresh()
        self.assertTrue(state["add"])                   # v50 : plus d'interrupteur, ajout direct en Mode libre
        win.settings["mode_libre"] = False
        tab.refresh()
        self.assertFalse(state["add"])                  # Mode guidé : par « Niveau supérieur »


if __name__ == "__main__":
    unittest.main()
