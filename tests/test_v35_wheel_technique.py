"""Tests v35 : molette neutralisée sur les contrôles (redirigée vers le défilement), style « Technique supérieure »."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import qt_stub  # noqa: E402

qt_stub.install()

from test_v5_features import DB  # noqa: E402
from core.engine import Engine  # noqa: E402
import ui.wheel_guard as wg  # noqa: E402


# ---------------------------------------------------------------- faux widgets (le module Qt factice ne distingue pas
# les classes) : on remplace les types utilisés par le filtre
class FWidget:
    def __init__(self, parent=None):
        self._parent = parent

    def parentWidget(self):  # noqa: N802
        return self._parent


class FCombo(FWidget):
    pass


class FSpin(FWidget):
    pass


class FTabBar(FWidget):
    pass


class FSlider(FWidget):
    pass


class FScrollBarWidget(FSlider):
    pass


class FBar:
    def __init__(self):
        self.v, self.lo, self.hi, self.step = 100, 0, 1000, 10

    def value(self):
        return self.v

    def setValue(self, v):  # noqa: N802
        self.v = max(self.lo, min(self.hi, v))

    def minimum(self):
        return self.lo

    def maximum(self):
        return self.hi

    def singleStep(self):  # noqa: N802
        return self.step


class FArea(FWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bar = FBar()

    def verticalScrollBar(self):  # noqa: N802
        return self.bar


class FEvent:
    def __init__(self, dy=-120):
        self.dy = dy

    def type(self):
        return "wheel"

    def angleDelta(self):  # noqa: N802
        dy = self.dy

        class P:
            def y(self):
                return dy
        return P()


class WheelGuardTests(unittest.TestCase):
    def setUp(self):
        self.saved = (wg.QWidget, wg.GUARDED, wg.QScrollBar, wg.QAbstractScrollArea, wg.QEvent)
        wg.QWidget, wg.QScrollBar, wg.QAbstractScrollArea = FWidget, FScrollBarWidget, FArea
        wg.GUARDED = (FCombo, FSpin, FTabBar, FSlider)

        class _E:
            class Type:
                Wheel = "wheel"
        wg.QEvent = _E

    def tearDown(self):
        wg.QWidget, wg.GUARDED, wg.QScrollBar, wg.QAbstractScrollArea, wg.QEvent = self.saved

    def test_controls_never_receive_wheel_and_page_scrolls(self):
        area = FArea()
        panel = FWidget(area)
        guard = wg.WheelGuard()
        for cls in (FCombo, FSpin, FTabBar, FSlider):
            area.bar.v = 100
            ctl = cls(panel)
            self.assertTrue(guard.eventFilter(ctl, FEvent(-120)), cls.__name__)   # événement consommé
            self.assertEqual(area.bar.v, 130, cls.__name__)                        # la page a défilé

    def test_inner_editor_of_spinbox_is_guarded(self):
        area = FArea()
        spin = FSpin(FWidget(area))
        editor = FWidget(spin)                                    # champ texte interne du compteur
        self.assertIs(wg.guarded_control(editor), spin)

    def test_plain_widgets_and_scrollbars_untouched(self):
        guard = wg.WheelGuard()
        self.assertFalse(guard.eventFilter(FWidget(FArea()), FEvent()))
        self.assertFalse(guard.eventFilter(FScrollBarWidget(FArea()), FEvent()))

    def test_no_scrollable_parent(self):
        guard = wg.WheelGuard()
        self.assertTrue(guard.eventFilter(FCombo(FWidget()), FEvent()))      # consommé quand même : valeur intacte

    def test_orbs_have_no_wheel_handler(self):
        src = (ROOT / "ui" / "orbs.py").read_text(encoding="utf-8")
        self.assertNotIn("def wheelEvent", src)

    def test_installed_by_main_window(self):
        src = (ROOT / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertIn("wheel_guard.install(QApplication.instance())", src)


def make(style="Technique supérieure", maneuver=""):
    eng = Engine(DB, Engine.new_character(DB))
    eng.ch.classes = [{"nom": "Guerrier", "niveau": 3, "sous_classe": "Champion", "pv_jets": []}]
    eng.ch.styles_combat["Guerrier|1"] = style
    eng.ch.technique_manoeuvre = maneuver
    eng.normalize()
    return eng


class SuperiorTechniqueTests(unittest.TestCase):
    def test_maneuver_to_choose(self):
        eng = make()
        self.assertIn("Technique supérieure : manœuvre à choisir",
                      [m["message"] for m in eng.missing_choices()])
        self.assertIsNone(eng.superior_technique_action())

    def test_action_and_d6_die(self):
        name = next(iter(DB.maneuvers))
        eng = make(maneuver=name)
        tr = next(t for t in eng.resource_trackers("combat") if t["key"] == "superiorite_tech")
        self.assertEqual((tr["total"], tr["de"], tr["recover"]), (1, "d6", "repos court"))
        a = next(x for x in eng.class_actions() if x["id"] == "manoeuvre_style")
        self.assertEqual(a["nom"], "Manœuvre : " + name)
        self.assertEqual(a["formule"], "1d6")
        self.assertTrue(eng.use_class_action("manoeuvre_style")["ok"])
        self.assertFalse(eng.use_class_action("manoeuvre_style")["ok"])          # dé dépensé
        eng.short_rest()
        self.assertTrue(eng.use_class_action("manoeuvre_style")["ok"])           # récupéré au repos court
        eng.long_rest()
        self.assertEqual(eng.resource_used("superiorite_tech"), 0)

    def test_riposte_uses_reaction(self):
        if "Riposte" not in DB.maneuvers:
            self.skipTest("Riposte absente des données")
        eng = make(maneuver="Riposte")
        eng.use_class_action("manoeuvre_style")
        self.assertTrue(eng.ch.reaction_utilisee)

    def test_reset_when_style_replaced(self):
        eng = make(maneuver=next(iter(DB.maneuvers)))
        eng.use_class_action("manoeuvre_style")
        eng.ch.styles_combat["Guerrier|1"] = "Défense"
        eng.normalize()
        self.assertEqual(eng.ch.technique_manoeuvre, "")
        self.assertNotIn("superiorite_tech", [t["key"] for t in eng.resource_trackers()])
        self.assertNotIn("superiorite_tech", eng.ch.ressources_utilisees)
        self.assertFalse(any(x["id"] == "manoeuvre_style" for x in eng.class_actions()))

    def test_style_description_fixed(self):
        desc = DB.style_description("Guerrier", "Technique supérieure")
        self.assertIn("repos court ou long", desc)
        self.assertNotIn("DD 14", desc)

    def test_combat_tab_picker(self):
        import ui.main_window as mw
        mw.save_settings = lambda data: None
        win = mw.MainWindow(DB)
        win.engine = make()
        win.refresh_all()
        tab = win.combat_tab
        tab.refresh()
        row = tab.style_rows[0]
        name = next(iter(DB.maneuvers))
        row["tech"].clear()
        row["tech"].addItems([tab.NO_MANEUVER, name])
        row["tech"].setCurrentIndex(1)
        tab._on_tech_maneuver(row["tech"])
        self.assertEqual(win.ch.technique_manoeuvre, name)
        self.assertTrue(any(x["id"] == "manoeuvre_style" for x in win.engine.class_actions()))


if __name__ == "__main__":
    unittest.main()
