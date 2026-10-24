"""Version web : façade du moteur (web/service.py) et routes Flask. Ignoré si Flask n'est pas installé."""
import json
import unittest

try:
    import flask  # noqa: F401
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

from web import service as S
from core.character import Character


class ServiceTests(unittest.TestCase):
    def test_new_character(self):
        r = S.apply(None)
        self.assertEqual(r["errors"], [])
        self.assertIn("sheet", r)
        self.assertEqual(r["sheet"]["resume"]["niveau"], 1)

    def test_round_trip_desktop_format(self):
        r = S.apply(None, [{"op": "class_change", "idx": 0, "name": "Magicien"},
                           {"op": "class_level", "idx": 0, "level": 5},
                           {"op": "spell_add", "cls": "Magicien", "nom": "Boule de feu"},
                           {"op": "set", "field": "nom", "value": "Test"}])
        self.assertEqual(r["errors"], [])
        ch = Character.from_dict(json.loads(json.dumps(r["character"])))   # même format que la sauvegarde bureau
        self.assertEqual(ch.nom, "Test")
        self.assertEqual(ch.sorts["Magicien"][0]["nom"], "Boule de feu")

    def test_cast_uses_slot(self):
        r = S.apply(None, [{"op": "class_change", "idx": 0, "name": "Magicien"},
                           {"op": "class_level", "idx": 0, "level": 5},
                           {"op": "spell_add", "cls": "Magicien", "nom": "Boule de feu"},
                           {"op": "cast", "nom": "Boule de feu"}])
        self.assertEqual(r["sheet"]["magie"]["utilises"][2], 1)

    def test_damage_and_rest(self):
        r = S.apply(None, [{"op": "damage", "amount": 3}])
        hp = r["sheet"]["combat"]
        self.assertEqual(hp["pv"], hp["pv_max"] - 3)
        r = S.apply(r["character"], [{"op": "long_rest"}])
        self.assertEqual(r["sheet"]["combat"]["pv"], r["sheet"]["combat"]["pv_max"])

    def test_invalid_inputs_are_reported(self):
        r = S.apply(None, [{"op": "inconnue"}, {"op": "set", "field": "classes", "value": []},
                           {"op": "race", "name": "Pas une espèce"}])
        self.assertEqual(len(r["errors"]), 3)
        with self.assertRaises(S.ActionError):
            S.apply({"pas": "un personnage"})

    def test_text_export(self):
        txt = S.text_sheet(S.apply(None)["character"])
        self.assertIn("## Caractéristiques", txt)

    def test_catalog_has_themes(self):
        cat = S.catalog()
        self.assertIn("bg3", cat["themes"])
        self.assertTrue(cat["sorts"])


class LevelUpTests(unittest.TestCase):
    def _char(self, cls, lvl, extra=()):
        return S.apply(None, [{"op": "class_change", "idx": 0, "name": cls},
                              {"op": "class_level", "idx": 0, "level": lvl}] + list(extra))["character"]

    def test_asi_level(self):
        from web.levelup import wizard
        ch = self._char("Guerrier", 3, [{"op": "class_sub", "idx": 0, "name": "Champion"}])
        w = wizard(ch, "Guerrier", [])
        self.assertFalse(w["pret"])
        slot = w["choix"]["asi"][0]["id"]
        with self.assertRaises(S.ActionError):
            wizard(ch, "Guerrier", [], confirm=True)            # choix manquant : refusé
        r = wizard(ch, "Guerrier", [{"op": "asi", "slot": slot, "mode": "plus2", "a1": "Force"}], confirm=True)
        self.assertEqual(r["sheet"]["resume"]["niveau"], 4)
        self.assertEqual(r["character"]["ameliorations"][slot]["mode"], "plus2")

    def test_subclass_and_spells(self):
        from web.levelup import wizard
        ch = self._char("Magicien", 1)
        w = wizard(ch, "Magicien", [{"op": "sub", "name": "École d'Évocation"}])
        self.assertIn("sous_classe", w["choix"])
        name = next(o["nom"] for o in w["sorts"][0]["options"] if o["niveau"] > 0)
        w = wizard(ch, "Magicien", [{"op": "sub", "name": "École d'Évocation"},
                                    {"op": "learn", "cls": "Magicien", "name": name}])
        self.assertTrue(any(s["nom"] == name and s["nouveau"] for s in w["sorts"][0]["mes_sorts"]))

    def test_spell_swap_replay(self):
        from web.levelup import wizard
        ch = self._char("Ensorceleur", 4, [{"op": "spell_add", "cls": "Ensorceleur", "nom": "Projectile magique"}])
        ops = [{"op": "swap_forget", "cls": "Ensorceleur", "name": "Projectile magique"}]
        w = wizard(ch, "Ensorceleur", ops)
        new = w["sorts"][0]["echange"]["options"][0]["nom"]
        w = wizard(ch, "Ensorceleur", ops + [{"op": "swap_choose", "cls": "Ensorceleur", "name": new}])
        self.assertEqual(w["sorts"][0]["echange"]["etat"]["nouveau"], new)


class GameplayTests(unittest.TestCase):
    def test_turn_attack(self):
        r = S.apply(None, [{"op": "weapon", "key": "armes_cac", "i": 0, "nom": "Épée longue"}])
        tile = r["sheet"]["tour"]["actions"][0]["id"]
        r = S.apply(r["character"], [{"op": "turn_use", "tile": tile}])
        self.assertEqual(r["errors"], [])
        self.assertTrue(r["rolls"])
        self.assertTrue(r["sheet"]["tour"]["etat"]["Action"])
        r = S.apply(r["character"], [{"op": "turn_new"}])
        self.assertFalse(r["sheet"]["tour"]["etat"]["Action"])

    def test_wild_shape(self):
        r = S.apply(None, [{"op": "class_change", "idx": 0, "name": "Druide"}, {"op": "class_level", "idx": 0, "level": 4}])
        beast = r["sheet"]["formes"]["druide"]["betes"][0]["nom"]
        r = S.apply(r["character"], [{"op": "form_assume", "name": beast}])
        self.assertEqual(r["sheet"]["formes"]["forme"]["bete"], beast)
        r = S.apply(r["character"], [{"op": "form_end"}])
        self.assertIsNone(r["sheet"]["formes"]["forme"])

    def test_companion_gm_spell_custom_item(self):
        r = S.apply(None, [{"op": "menagerie_add", "id": "araignee"},
                           {"op": "gm_spell_add", "nom": "Boule de feu", "usage": "1 fois par repos long"},
                           {"op": "custom_magic", "nom": "Bague test", "rarete": "rare"}])
        self.assertEqual(r["errors"], [])
        self.assertEqual(r["sheet"]["menagerie"][0]["id"], "araignee")
        self.assertEqual(r["sheet"]["sorts_mj"][0]["nom"], "Boule de feu")
        self.assertIn("Bague test", [m["nom"] for m in r["sheet"]["inventaire"]["magiques"]])

    def test_warlock_options(self):
        r = S.apply(None, [{"op": "class_change", "idx": 0, "name": "Occultiste"}, {"op": "class_level", "idx": 0, "level": 3},
                           {"op": "pact", "name": "Pacte du grimoire"}])
        o = r["sheet"]["options"]
        name = next(m["nom"] for m in o["manifestations"]["options"] if m["etat"] == "ok")
        r = S.apply(r["character"], [{"op": "manifestation_add", "name": name}])
        self.assertIn(name, r["character"]["manifestations"])


@unittest.skipUnless(HAS_FLASK, "Flask non installé")
class RouteTests(unittest.TestCase):
    def setUp(self):
        from web.app import app
        self.c = app.test_client()

    def test_routes(self):
        self.assertEqual(self.c.get("/").status_code, 200)
        self.assertEqual(self.c.get("/healthz").status_code, 200)
        self.assertEqual(self.c.get("/api/catalog").status_code, 200)
        r = self.c.post("/api/character", json={"character": None, "ops": []})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.c.post("/api/character", json={"character": {"x": 1}}).status_code, 422)
        self.assertEqual(self.c.post("/api/roll", json={"expression": "2d6+3"}).status_code, 200)
        ch = self.c.post("/api/character", json={"character": None}).get_json()["character"]
        self.assertEqual(self.c.post("/api/levelup", json={"character": ch, "ops": []}).status_code, 200)


if __name__ == "__main__":
    unittest.main()
