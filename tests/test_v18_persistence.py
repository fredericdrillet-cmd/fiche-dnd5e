"""Tests v18 : modale de sortie à 3 boutons, ajout de sort rapide, boutons d'action contextuels (Mes sorts vs
Bibliothèque), et intégrité complète de la sauvegarde (aller-retour JSON de tous les états dynamiques)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402


def make_win():
    import ui.main_window as mw
    mw.save_settings = lambda data: None
    return mw, mw.MainWindow(DB)


class ExitDialogTests(unittest.TestCase):
    def setUp(self):
        self.mw, self.win = make_win()
        saved = self.mw.ask_save_changes
        self.addCleanup(lambda: setattr(self.mw, "ask_save_changes", saved))
        self.tmp = Path(tempfile.mkdtemp())

    def test_dialog_buttons_order(self):
        from ui.dialogs import SaveChangesDialog
        dlg = SaveChangesDialog(None)
        self.assertEqual([dlg.save_btn.text(), dlg.discard_btn.text(), dlg.cancel_btn.text()],
                         ["Enregistrer", "Ne pas enregistrer et quitter", "Annuler"])

    def test_cancel_keeps_sheet(self):
        self.mw.ask_save_changes = lambda parent, label="": "cancel"
        self.win._dirty = True
        self.assertFalse(self.win._confirm_discard())
        self.assertTrue(self.win._dirty)

    def test_discard_quits(self):
        self.mw.ask_save_changes = lambda parent, label="": "discard"
        self.win._dirty = True
        self.assertTrue(self.win._confirm_discard())

    def test_save_then_quit(self):
        self.mw.ask_save_changes = lambda parent, label="": "save"
        path = self.tmp / "perso.json"
        self.win.path = path
        self.win.ch.nom = "Elara"
        self.win._dirty = True
        self.assertTrue(self.win._confirm_discard())
        self.assertFalse(self.win._dirty)
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["nom"], "Elara")

    def test_save_as_cancelled_stays(self):
        self.mw.ask_save_changes = lambda parent, label="": "save"
        self.win.path = None
        orig = self.mw.QFileDialog.getSaveFileName
        self.addCleanup(lambda: setattr(self.mw.QFileDialog, "getSaveFileName", orig))
        self.mw.QFileDialog.getSaveFileName = staticmethod(lambda *a, **k: ("", ""))
        self.win._dirty = True
        self.assertFalse(self.win._confirm_discard())


class MagicActionTests(unittest.TestCase):
    def setUp(self):
        self.mw, self.win = make_win()
        self.win.ch.classes = [{"nom": "Magicien", "niveau": 5, "sous_classe": "", "pv_jets": []}]
        self.win.changed()
        self.tab = self.win.magic_tab
        self.tab.select_class("Magicien")

    def test_add_is_targeted(self):
        tab, win = self.tab, self.win
        tab._on_level_chip(0)
        calls = []
        orig = win.refresh_all
        win.refresh_all = lambda: calls.append(1) or orig()
        self.addCleanup(lambda: setattr(win, "refresh_all", orig))
        tab.library.setCurrentRow(3)
        name = tab._lib_rows[3]["nom"]
        tab._on_add()
        self.assertEqual(calls, [])                                # aucun rafraîchissement global
        self.assertIn(name, [s["nom"] for s in win.ch.sorts["Magicien"]])
        self.assertIn(name, [r["nom"] for r in tab._chosen_rows])
        self.assertIn(name, tab._lib_painted)
        self.assertTrue(win._dirty)

    def test_buttons_disabled_in_library(self):
        tab, win = self.tab, self.win
        tab._on_level_chip(0)
        tab.library.setCurrentRow(0)
        tab._on_add()
        idx = next(i for i, r in enumerate(tab._chosen_rows) if not r.get("separator"))
        tab.chosen.setCurrentRow(idx)
        state = {}
        for b in ("cast_btn", "attack_btn"):
            getattr(tab, b).setEnabled = (lambda k: lambda v: state.__setitem__(k, v))(b)
        tab.center_tabs.setCurrentIndex(1)
        tab._update_action_btns()
        self.assertFalse(state["cast_btn"])
        self.assertFalse(state["attack_btn"])
        tab.center_tabs.setCurrentIndex(0)
        tab._update_action_btns()
        self.assertTrue(state["cast_btn"])


class PersistenceTests(unittest.TestCase):
    """Aller-retour complet : enregistrer -> rouvrir -> état identique."""

    def setUp(self):
        self.mw, self.win = make_win()
        self.tmp = Path(tempfile.mkdtemp())

    def _roundtrip(self):
        win, mw = self.win, self.mw
        path = self.tmp / "save.json"
        before = win.ch.to_dict()
        win._write(path)
        self.assertFalse(win._dirty)
        orig = mw.QFileDialog.getOpenFileName
        self.addCleanup(lambda: setattr(mw.QFileDialog, "getOpenFileName", orig))
        mw.QFileDialog.getOpenFileName = staticmethod(lambda *a, **k: (str(path), ""))
        mw2, win2 = make_win()
        win2.action_open()
        after = win2.ch.to_dict()
        diff = {k: (before[k], after.get(k)) for k in before if before[k] != after.get(k)}
        self.assertEqual(diff, {})
        return win2

    def test_wild_shape_and_buffs(self):
        win, eng, ch = self.win, self.win.engine, self.win.ch
        ch.classes = [{"nom": "Druide", "niveau": 8, "sous_classe": "Cercle de la Lune", "pv_jets": []}]
        win.changed()
        ch.pv_actuels = 40
        ch.sorts["Druide"] = [{"nom": "Soins", "prepare": True}, {"nom": "Lueurs féeriques", "prepare": False}]
        res = eng.cast_spell("Lueurs féeriques", True)
        self.assertTrue(res["ok"], res)
        self.assertTrue(eng.assume_form("Ours brun"))
        eng.damage_form(5)
        eng.add_effect("benediction")
        ch.effets_potions.append("resist_feu")
        ch.effets_actifs.append("resist_feu")
        ch.temps_minutes, ch.dernier_repos_long = 615, 0
        ch.reaction_utilisee = "Attaque d'opportunité"
        ch.mort_reussites = 1
        win.changed()
        self.assertTrue(ch.forme_active and ch.forme_pv and ch.concentration and any(ch.emplacements_utilises))
        win2 = self._roundtrip()
        self.assertEqual(win2.ch.forme_active, "Ours brun")
        self.assertEqual(win2.engine.form_status()["pv"], ch.forme_pv)
        self.assertEqual(win2.ch.concentration, "Lueurs féeriques")
        self.assertIn("benediction", win2.engine.active_effect_keys())

    def test_polymorph_upcast_and_lists(self):
        win, eng, ch = self.win, self.win.engine, self.win.ch
        ch.classes = [{"nom": "Magicien", "niveau": 9, "sous_classe": "", "pv_jets": []}]
        win.changed()
        ch.sorts["Magicien"] = [{"nom": "Métamorphose", "prepare": True}, {"nom": "Projectile magique", "prepare": False},
                                {"nom": "Trait de feu", "prepare": True}]
        ch.emplacements_utilises[3] = 3                              # niveau 4 épuisé -> surclassement niveau 5
        res = eng.cast_polymorph("Ours brun", True)
        self.assertTrue(res.get("ok", True))
        eng.add_gm_spell("Lumière", "À volonté", "Relique du temple")
        ch.sorts_mineurs[0]["nom"] = "Trait de feu"
        ch.ressources_utilisees["arcanes"] = 1
        ch.ascendance_raciale = "Rouge"
        ch.armes_distance[0] = {"nom": "Arc court", "bonus": 1, "maitrise": True, "munition": "Flèche"}
        ch.objets_magiques.append({"nom": "Anneau de protection", "bonus": 0, "equipe": True, "harmonise": True})
        win.changed()
        self.assertEqual(ch.forme_type, "metamorphose")
        win2 = self._roundtrip()
        self.assertEqual(win2.ch.forme_type, "metamorphose")
        self.assertEqual(win2.ch.emplacements_utilises, ch.emplacements_utilises)
        self.assertEqual(win2.ch.sorts_mj, ch.sorts_mj)

    def test_every_field_serialized(self):
        """Tout l'état du personnage est un champ du dataclass, donc écrit dans le JSON (rien n'est gardé ailleurs)."""
        from core.character import Character
        data = self.win.ch.to_dict()
        for key in Character().__dict__:
            self.assertIn(key, data)


if __name__ == "__main__":
    unittest.main()
