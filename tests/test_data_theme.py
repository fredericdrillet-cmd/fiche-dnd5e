"""Tests du croisement des données JSON, de la vitesse en cases et de l'accessibilité des thèmes (WCAG AA)."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import rules as R  # noqa: E402
from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402

# theme.py n'importe PyQt6 qu'à l'intérieur de apply_palette : on peut le charger sans Qt
_spec = importlib.util.spec_from_file_location("theme_mod", ROOT / "ui" / "theme.py")
theme = importlib.util.module_from_spec(_spec)
sys.modules["theme_mod"] = theme
_spec.loader.exec_module(theme)

DB = Database(ROOT / "data")


class DataTests(unittest.TestCase):
    def test_everything_loaded(self):
        self.assertGreaterEqual(len(DB.spells), 400)
        self.assertGreaterEqual(len(DB.weapons), 38)
        self.assertGreaterEqual(len(DB.armors), 15)
        self.assertGreaterEqual(len(DB.shields), 2)
        self.assertGreaterEqual(len(DB.feats), 80)
        self.assertGreaterEqual(len(DB.equipment), 80)
        self.assertEqual(len(DB.languages), 16)

    def test_dons_json_repaired(self):
        # v25 : la francisation réécrit Dons.json en JSON valide (la réparation automatique reste disponible)
        from core.data_loader import read_json
        data, warn = read_json(ROOT / "data" / "Dons.json")
        self.assertTrue(data)
        self.assertIn("Alerte", DB.feats)


    def test_weapons_parsed(self):
        w = DB.weapons["Épée longue"]
        self.assertEqual((w["categorie"], w["type"], w["degats"], w["type_degats"], w["polyvalent"]),
                         ("guerre", "cac", "1d8", "tranchant", "1d10"))
        self.assertEqual(DB.weapons["Arc long"]["type"], "distance")
        self.assertEqual(DB.weapons["Arc long"]["portee"], "45/180")
        self.assertEqual(DB.weapons["Dague"]["portee"], "6/18")
        self.assertEqual(DB.weapons["Rapière"]["botte"], "Ouverture")
        self.assertIn("Mains nues", DB.weapons)

    def test_armors_parsed(self):
        c = DB.armors["Cuirasse"]
        self.assertEqual((c["ca_base"], c["dex_max"], c["categorie"]), (14, 2, "intermédiaire"))
        self.assertEqual(DB.armors["Armure de cuir"]["dex_max"], None)
        self.assertEqual(DB.armors["Cotte de mailles"]["force_min"], 13)
        self.assertEqual(DB.armors["Harnois"]["dex_max"], 0)
        self.assertEqual(DB.shields["Bouclier"]["bonus_ca"], 2)

    def test_spells_have_class_lists(self):
        missing = [n for n, s in DB.spells.items() if not s["classes"]]
        self.assertEqual(missing, [])
        self.assertIn("Magicien", DB.spells["Boule de feu"]["classes"])
        self.assertNotIn("Clerc", DB.spells["Boule de feu"]["classes"])
        self.assertIn("Clerc", DB.spells["Soins"]["classes"])

    def test_spell_mechanics_extracted(self):
        tf = DB.spells["Trait de feu"]
        self.assertEqual((tf["degats"], tf["type_degats"], tf["test"]), ("1d10", "feu", "A"))
        self.assertEqual(DB.spells["Flamme sacrée"]["test"], "Dex")

    def test_feat_parsing(self):
        self.assertEqual(DB.feats["Alerte"]["effets"], {"initiative": 5})
        self.assertGreater(len(DB.feats["Résistant"]["carac_choix"]), 1)

    def test_equipment_matching(self):
        self.assertEqual(DB.match_item("2 flasques d'huile")[:2], (2, "Huile"))
        self.assertEqual(DB.match_item("sac de couchage")[:2], (1, "Sac de couchage"))
        contents = DB.pack_contents("Paquetage d’explorateur")
        names = [n for _, n, _ in contents]
        self.assertIn("Corde", names)
        self.assertIn("Rations", names)


class FeatureTests(unittest.TestCase):
    def _eng(self):
        eng = Engine(DB, Engine.new_character(DB))
        eng.ch.methode = "manuel"
        return eng

    def test_speed_in_cells(self):
        self.assertEqual(R.fmt_speed(9), "9 m (6 cases)")
        self.assertEqual(R.fmt_speed(7.5), "7,5 m (5 cases)")
        self.assertEqual(R.fmt_speed(10.5), "10,5 m (7 cases)")
        eng = self._eng()
        eng.ch.race = "Nain des collines"
        self.assertEqual(eng.speed_text(), "7,5 m (5 cases)")

    def test_shield_and_armor(self):
        eng = self._eng()
        eng.ch.armure.update({"nom": "Harnois", "bouclier": True, "bouclier_nom": "Bouclier"})
        self.assertEqual(eng.armor_class()[0], 18 + 2)

    def test_feat_prerequisites(self):
        eng = self._eng()
        eng.ch.classes = [{"nom": "Guerrier", "niveau": 1, "sous_classe": "", "pv_jets": []}]
        eng.normalize()
        self.assertEqual(eng.feat_status("Alerte")[0], "ok")
        self.assertEqual(eng.feat_status("Maître des armures lourdes")[0], "ok")      # le guerrier maîtrise tout
        eng.ch.classes = [{"nom": "Magicien", "niveau": 1, "sous_classe": "", "pv_jets": []}]
        eng.normalize()
        self.assertEqual(eng.feat_status("Maître des armures lourdes")[0], "ko")      # le magicien : aucune armure
        self.assertEqual(eng.feat_status("Initié au combat")[0], "?")                  # formulation non reconnue

    def test_inventory_weight(self):
        eng = self._eng()
        eng.add_item("Corde", 2)
        eng.add_item("Corde", 1)
        self.assertEqual(eng.ch.equipement, [{"nom": "Corde", "qte": 3}])
        self.assertAlmostEqual(eng.carried_weight(), 7.5)
        eng.add_pack("Paquetage d’explorateur")
        self.assertGreater(len(eng.ch.equipement), 3)

    def test_weapon_with_new_data(self):
        eng = self._eng()
        eng.ch.classes = [{"nom": "Guerrier", "niveau": 1, "sous_classe": "", "pv_jets": []}]
        eng.ch.scores_manuel["Force"] = 16
        eng.ch.regles_optionnelles["maitrises_armes_2014"] = True      # v52 : la botte est une règle de la table
        st = eng.weapon_stats({"nom": "Hache d’armes", "bonus": 1, "maitrise": None})
        # v46 : main secondaire libre -> polyvalente tenue à deux mains automatiquement
        self.assertEqual(st["degats"], "1d10+4")
        self.assertEqual(st["polyvalent"], "1d8+4")
        self.assertEqual(st["botte"], "Renversement")

    def test_library_filter_and_all(self):
        eng = self._eng()
        eng.ch.classes = [{"nom": "Magicien", "niveau": 3, "sous_classe": "", "pv_jets": []}]
        eng.normalize()
        only = {s["nom"] for s in eng.available_spells("Magicien")}
        everything = {s["nom"] for s in eng.available_spells("Magicien", include_all=True)}
        self.assertIn("Projectile magique", only)
        self.assertNotIn("Soins", only)
        self.assertIn("Soins", everything)
        self.assertNotIn("Boule de feu à retardement", only)          # niveau 7 : hors de portée au niveau 3
        self.assertIn("Boule de feu à retardement", everything)       # v19 : le mode MJ lève aussi le niveau


class ThemeTests(unittest.TestCase):
    ORDER = ["bg3", "witcher", "skyrim", "souls", "diablo", "cp2077", "ff", "hollow", "masseffect", "zelda"]

    def test_ten_themes_bg3_default(self):
        self.assertEqual(list(theme.THEMES), self.ORDER)
        self.assertEqual(len(theme.THEMES), 10)
        self.assertEqual(theme.DEFAULT_THEME, "bg3")
        from core import settings
        self.assertEqual(settings.DEFAULTS["theme"], "bg3")
        self.assertEqual(theme.resolve_key("parchemin"), "bg3")        # ancienne préférence -> défaut
        self.assertEqual(theme.resolve_key("hades"), "bg3")

    def test_games_requested(self):
        names = " | ".join(t.game for t in theme.THEMES.values())
        for game in ("Witcher", "Cyberpunk", "Skyrim", "Dark Souls", "Baldur", "Diablo", "Final Fantasy",
                     "Hollow Knight", "Mass Effect", "Zelda"):
            self.assertIn(game, names)

    def test_bg3_keeps_specified_palette(self):
        t = theme.THEMES["bg3"]
        self.assertEqual((t.bg, t.bg2, t.panel, t.panel2, t.ornament, t.text),
                         ("#181514", "#110F0E", "#24201D", "#2C2724", "#C5A059", "#E2D9CD"))
        self.assertEqual(t.button_bg2, "#611A1A")

    def test_each_theme_is_distinct(self):
        signatures = {(t.bg, t.panel, t.ornament, t.button_bg) for t in theme.THEMES.values()}
        self.assertEqual(len(signatures), 10)
        self.assertGreaterEqual(len({t.texture for t in theme.THEMES.values()}), 8)     # textures variées
        self.assertGreaterEqual(len({t.frame for t in theme.THEMES.values()}), 3)       # cadres variés
        self.assertGreaterEqual(len({t.font_title for t in theme.THEMES.values()}), 5)  # typographies variées

    def test_light_and_dark_families(self):
        dark = [k for k, t in theme.THEMES.items() if theme.luminance(t.bg) < 0.2]
        light = [k for k, t in theme.THEMES.items() if theme.luminance(t.bg) >= 0.5]
        self.assertEqual(set(light), {"ff", "zelda"})
        self.assertEqual(len(dark), 8)

    def test_cyberpunk_neon_cyan_magenta_bevel(self):
        t = theme.THEMES["cp2077"]
        self.assertEqual(t.ornament, "#00F0FF")
        self.assertEqual(t.frame, "outset")
        self.assertIn("outset", theme.build_stylesheet(t))
        self.assertEqual(t.texture, "scan")

    def test_skyrim_runes_and_dark_souls_double_frame(self):
        self.assertEqual(theme.THEMES["skyrim"].texture, "runes")
        self.assertEqual(theme.THEMES["souls"].frame, "double")
        self.assertIn("double", theme.build_stylesheet(theme.THEMES["souls"]))

    def test_wcag_aa_with_textures_on_all_themes(self):
        for key, t in theme.THEMES.items():
            self.assertEqual(t.audit(), [], key)
            self.assertGreaterEqual(theme.contrast_ratio(t.text, t.bg), 7.0, key)
            self.assertGreaterEqual(theme.contrast_ratio(t.text, t.panel2), 7.0, key)

    def test_danger_button_always_readable(self):
        for key, t in theme.THEMES.items():
            self.assertGreaterEqual(theme.contrast_ratio(t.danger_text, t.warn), 4.5, key)

    def test_contrast_function(self):
        self.assertAlmostEqual(theme.contrast_ratio("#000000", "#FFFFFF"), 21.0, places=1)
        self.assertAlmostEqual(theme.contrast_ratio("#777777", "#777777"), 1.0, places=2)

    def test_stylesheet_gradients_texture_and_dialog_styles(self):
        for t in theme.THEMES.values():
            qss = theme.build_stylesheet(t, 15, "/tmp/tex.png")
            flat = qss.replace("\n", " ")
            self.assertGreaterEqual(qss.count("qlineargradient"), 12, t.key)
            self.assertIn("QMainWindow, QDialog { background: qlineargradient", flat, t.key)
            self.assertIn('background-image: url("/tmp/tex.png")', flat)
            self.assertIn("QFrame#dialogCard", qss)                    # carte de la fenêtre de confirmation
            self.assertIn('QPushButton[role="ghost"]:hover', qss)       # état survol du bouton « Non »
            self.assertIn("font-size: 15px", qss)
            self.assertNotIn("background-image", theme.build_stylesheet(t, 15, ""))


if __name__ == "__main__":
    unittest.main()
