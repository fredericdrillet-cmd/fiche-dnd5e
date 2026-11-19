"""
Sous-classes 2024 sans équivalent 2014 (v52) : tuiles d'action et effets automatiques.

- Tuiles (format `class_tiles.T`, réservées aux fiches 2024 par le champ `ed`) : Voie de l'Arbre-Monde (Force
  vivifiante, Branches de l'Arbre, Voyage au gré de l'arbre), Collège de la Danse (Déplacement exaltant, Pirouettes
  coordonnées), Cercle de la Terre (Aval de la terre, Sanctuaire de dame Nature), Cercle des Mers (Courroux des
  mers), Credo des Éléments (Lien élémentaire, Décharge élémentaire), Domaine de la Lumière (Halo de lumière),
  Évocateur (Surcharge magique).
- Effets (`Subclass2024Mixin`) : PV temporaires de la Vitalité de l'arbre à l'entrée en rage, choix du Cœur sauvage
  (Rage du prédateur, Aspect de faune, Puissance de la faune) et résistances de l'Ours, Protégé de dame Nature,
  Enfant des tempêtes, Avatar de bataille, dé d'inspiration aux frappes à mains nues (Danse), outils de l'Assassin,
  Frappes surprises, Héros du champ d'honneur et Survivant du Champion (début de tour, jets contre la mort).
"""
from __future__ import annotations

from .rules import norm

LONG, SHORT = "repos long", "repos court"


def _t(tid, nom, icone, classe, sc, niveau, kind, desc, **kw):
    from .class_tiles import T
    tile = T(tid, nom, icone, classe, sc, niveau, kind, desc, **kw)
    tile["ed"] = 2024
    return tile


def tiles_2024() -> list[dict]:
    KI = {"ressource": "ki", "n": 1}
    INSP = {"ressource": "inspiration", "n": 1}
    FORME = {"ressource": "forme", "n": 1}
    return [
        # Barbare — Voie de l'Arbre-Monde
        _t("force_vivifiante", "Force vivifiante", "🌳", "Barbare", "arbre-monde", 3, "Spécial",
           "Au début de votre tour, en rage : une autre créature à 3 m gagne des PV temporaires (autant de d6 que "
           "votre bonus aux dégâts de rage).", degats="{RAGE_DES}d6", requiert="rage"),
        _t("branches_arbre", "Branches de l'Arbre", "🌿", "Barbare", "arbre-monde", 6, "Réaction",
           "Une créature commence son tour à 9 m, en rage : JS de Force ou elle est téléportée à 1,50 m de vous "
           "(vitesse réduite à 0 jusqu'à la fin du tour).", js="FOR", js_carac="Force", requiert="rage"),
        _t("voyage_arbre", "Voyage au gré de l'arbre", "🌲", "Barbare", "arbre-monde", 14, "Action bonus",
           "En rage : téléportation jusqu'à 18 m (une fois par rage : 45 m avec six créatures consentantes).",
           requiert="rage"),
        # Barde — Collège de la Danse
        _t("deplacement_exaltant", "Déplacement exaltant", "💃", "Barde", "danse", 6, "Réaction",
           "Un ennemi termine son tour à 1,50 m : déplacez-vous de la moitié de votre vitesse, puis un allié à 9 m "
           "aussi (sans attaque d'opportunité).", cout=INSP),
        _t("pirouettes_coordonnees", "Pirouettes coordonnées", "🎶", "Barde", "danse", 6, "Spécial",
           "En lançant l'initiative : vous et vos alliés à 9 m ajoutez le dé d'inspiration à l'initiative.",
           cout=INSP, degats="1{DE_INSP}"),
        # Druide — Cercle de la Terre
        _t("aval_terre", "Aval de la terre", "🌼", "Druide", "cercle de la terre", 3, "Action",
           "Sphère de 3 m à 18 m : JS de Constitution ou dégâts nécrotiques (moitié si réussite) ; une créature de "
           "la zone regagne autant de d6 en PV.", cout=FORME, degats={3: "2d6", 10: "3d6", 14: "4d6"},
           type_degats="nécrotique", js="SAG", js_carac="Constitution"),
        _t("sanctuaire_nature", "Sanctuaire de dame Nature", "🌳", "Druide", "cercle de la terre", 14, "Action",
           "Cube de 4,50 m à 36 m pendant 1 minute : abri partiel et résistance de Protégé de dame Nature pour vous "
           "et vos alliés.", cout=FORME),
        # Druide — Cercle des Mers
        _t("courroux_mers", "Courroux des mers", "🌊", "Druide", "cercle des mers", 3, "Action bonus",
           "Émanation d'embruns pendant 10 minutes ; à chaque action bonus, une créature dans l'émanation fait un JS "
           "de Constitution ou subit les dégâts de froid (et est repoussée de 4,50 m).", cout=FORME,
           degats="{MOD_SAG_MIN}d6", type_degats="froid", js="SAG", js_carac="Constitution", effet="courroux_mers"),
        # Moine — Credo des Éléments
        _t("lien_elementaire", "Lien élémentaire", "🌀", "Moine", "credo des elements", 3, "Spécial",
           "10 minutes : allonge +3 m de vos frappes à mains nues, qui infligent acide, froid, feu, foudre ou tonnerre "
           "et peuvent déplacer la cible de 3 m (JS de Force).", cout=KI, effet="lien_elementaire"),
        _t("decharge_elementaire", "Décharge élémentaire", "💥", "Moine", "credo des elements", 6, "Action",
           "Sphère de 6 m à 36 m : JS de Dextérité, trois dés d'arts martiaux (moitié si réussite).",
           cout={"ressource": "ki", "n": 2}, degats="3d{MA}", js="SAG", js_carac="Dextérité"),
        # Clerc — Domaine de la Lumière
        _t("halo_lumiere", "Halo de lumière", "☀️", "Clerc", "domaine de la lumiere", 17, "Action",
           "1 minute : lumière vive sur 18 m ; vos ennemis y ont le désavantage aux JS contre Radiance de l'aube et "
           "les sorts de feu ou radiants.", uses="MOD:Sagesse"),
        # Magicien — Évocateur
        _t("surcharge_magique", "Surcharge magique", "⚡", "Magicien", "evocateur", 14, "Spécial",
           "Sort de magicien de niveau 1 à 5 : dégâts maximum. La première fois sans contrepartie ; ensuite 2d12 "
           "nécrotiques par niveau d'emplacement (+1d12 à chaque nouvelle utilisation).", uses=1),
    ]


# tuile 2014 -> aptitude 2024 équivalente (nom différent) ; nom, texte et niveau 2024 remplacent ceux de 2014
TILE_FEATURE_2024 = {
    "cap:manteau_inspiration": "Mante d'inspiration", "cap:manteau_majeste": "Mante de majesté",
    "cap:inspiration_combat": "Inspiration martiale", "cap:eclat_protecteur": "Illumination protectrice",
    "cap:forme_etoilee": "Forme stellaire", "cap:ailes_dragon": "Ailes draconiques",
    "cap:marees_chaos": "Marée du chaos", "cap:chance_alteree": "Chance forcée", "cap:lien_arme": "Arme occulte",
    "cap:moi_illusoire": "Double illusoire", "cap:main_souffrance": "Main du mal",
    "cap:pas_ombre_moine": "Foulée d'ombre", "cap:plenitude_corps": "Plénitude physique",
    "cap:presence_feerique": "Foulée des fées", "cap:fuite_brumeuse": "Échappatoire brumeuse",
    "cap:garde_entropique": "Combattant clairvoyant", "cap:ange_vengeur": "Ange de la vengeance",
    "cap:ordre_compagnon": "Compagnon primitif", "cap:frappes_terribles": "Frappes terrifiantes",
    "cap:torsion_seduisante": "Revirement envoûtant", "cap:embuscade_terrible": "Embuscade effrayante",
    "cap:tueur_colosses": "Proie du chasseur",
}
TILES_HIDDEN_2024 = {"cap:frenesie"}                     # mécanisme 2024 différent : voir subclass24_riders

TERRAIN_RESIST = {"Aride": "feu", "Polaire": "froid", "Tempérée": "foudre", "Tropicale": "poison"}
BEAR_RESIST = ["acide", "contondant", "feu", "foudre", "froid", "perforant", "poison", "tonnerre", "tranchant"]
WILD_HEART = [
    ("coeur_sauvage_rage", 3, "Rage du prédateur (en entrant en rage)", {
        "Ours": "En rage : résistance à tous les dégâts sauf force, nécrotiques, psychiques et radiants.",
        "Aigle": "En entrant en rage : Se désengager et Foncer ; en rage, les deux par une action bonus.",
        "Loup": "En rage : vos alliés ont l'avantage aux attaques contre les ennemis à 1,50 m de vous."}),
    ("coeur_sauvage_aspect", 6, "Aspect de faune (après un repos long)", {
        "Chouette": "Vision dans le noir 18 m (ou +18 m).",
        "Panthère": "Vitesse d'escalade égale à votre vitesse.",
        "Saumon": "Vitesse de nage égale à votre vitesse."}),
    ("coeur_sauvage_puissance", 14, "Puissance de la faune (en entrant en rage)", {
        "Faucon": "En rage, sans armure : vitesse de vol égale à votre vitesse.",
        "Lion": "En rage : les ennemis à 1,50 m ont le désavantage aux attaques contre d'autres cibles que vous.",
        "Bélier": "En rage : une créature de taille G ou moins touchée au corps à corps tombe à terre."}),
]


class Subclass2024Mixin:
    """Mélangé à Engine : utilise class_level, ch, sheet_edition, mod, prof, active_effect_keys…"""

    def _sub24(self, cls: str, frag: str, lvl: int = 3) -> int:
        if getattr(self, "sheet_edition", 2014) != 2024:
            return 0
        e = self.ch.find_class(cls)
        return e["niveau"] if e and e["niveau"] >= lvl and frag in norm(e.get("sous_classe", "")) else 0

    def _opt(self, key: str) -> str:
        picked = (self.ch.options_classe or {}).get(key, [])
        return picked[0] if picked else ""

    # ------------------------------------------------------------------ choix
    def subclass24_option_sets(self) -> list[dict]:
        out = []
        for key, lvl, label, options in WILD_HEART:
            if self._sub24("Barbare", "coeur sauvage", lvl):
                out.append({"key": key, "label": label, "total": 1, "options": dict(options),
                            "chosen": list((self.ch.options_classe or {}).get(key, []))[:1]})
        return out

    # ------------------------------------------------------------------ modificateurs
    def subclass24_modifiers(self) -> list[tuple[str, dict]]:
        out = []
        raging = "rage" in self.active_effect_keys()
        if raging and self._sub24("Barbare", "coeur sauvage") and self._opt("coeur_sauvage_rage") == "Ours":
            out.append(("Rage du prédateur : Ours", {"resistances": list(BEAR_RESIST)}))
        e = self.ch.find_class("Druide")
        if self._sub24("Druide", "cercle de la terre", 10):
            terrain = self.land_terrain(e)
            if terrain in TERRAIN_RESIST:
                out.append(("Protégé de dame Nature", {"resistances": [TERRAIN_RESIST[terrain]]}))
        if self._sub24("Druide", "cercle des mers", 10) and "courroux_mers" in self.active_effect_keys():
            out.append(("Enfant des tempêtes", {"resistances": ["froid", "foudre", "tonnerre"]}))
        if self._sub24("Clerc", "domaine de la guerre", 17):
            out.append(("Avatar de bataille", {"resistances": ["contondant", "perforant", "tranchant"]}))
        return out

    def subclass24_darkvision(self) -> float:
        return 18.0 if self._sub24("Barbare", "coeur sauvage", 6) and self._opt("coeur_sauvage_aspect") == "Chouette" \
            else 0.0

    def subclass24_unarmed_die(self) -> int:
        """Collège de la Danse : dé d'inspiration bardique aux frappes à mains nues (sans armure ni bouclier)."""
        if not self._sub24("Barde", "danse") or self.ch.armure.get("bouclier"):
            return 0
        armor = self.db.armors.get(self.ch.armure.get("nom", ""), {})
        if armor.get("categorie", "aucune") != "aucune":
            return 0
        tr = next((t for t in self.resource_trackers() if t["key"] == "inspiration"), None)
        de = (tr or {}).get("de", "") or "d6"
        try:
            return int(str(de).lstrip("d"))
        except ValueError:
            return 6

    def subclass24_tools(self) -> list[str]:
        return ["Accessoires de déguisement", "Matériel d’empoisonneur"] if self._sub24("Roublard", "assassin") else []

    def subclass24_riders(self) -> list[tuple[str, str]]:
        out = []
        n = self._sub24("Roublard", "assassin")
        if n:
            out.append(("Frappes surprises (1er round, cible qui n'a pas joué, avec l'Attaque sournoise)", str(n)))
        if self._sub24("Barbare", "berserker") and "rage" in self.active_effect_keys():
            bonus = max(1, self.rage_damage_bonus())
            out.append(("Frénésie (Attaque téméraire, première cible touchée ce tour)", "{}d6".format(bonus)))
        return out

    # ------------------------------------------------------------------ déclencheurs
    def on_rage_start(self) -> str:
        msgs = []
        lvl = self._sub24("Barbare", "arbre-monde")
        if lvl:
            self.apply_temp_hp(lvl)
            msgs.append("Vitalité de l'arbre : {} PV temporaires".format(lvl))
        if "rage" not in self.ch.effets_actifs:          # la rage est ajoutée par l'action : on l'anticipe
            self.ch.effets_actifs.append("rage")
        gone = self.purge_immune_conditions()            # Rage aveugle (Berserker, 2014 et 2024)
        if gone:
            msgs.append("Rage aveugle : fin de " + ", ".join(gone))
        return " — ".join(msgs)

    def subclass24_turn_start(self) -> list[str]:
        """Début de tour (nouveau round) : Héros du champ d'honneur, Ralliement héroïque (Champion 2024)."""
        msgs = []
        if self._sub24("Guerrier", "champion", 10) and not self.ch.inspiration:
            self.ch.inspiration = True
            msgs.append("Héros du champ d'honneur : Inspiration héroïque")
        if self._sub24("Guerrier", "champion", 18):
            hp = self.ch.pv_actuels if self.ch.pv_actuels >= 0 else self.hp_max()
            if 1 <= hp <= self.hp_max() // 2:
                gained = self.heal(5 + self.mod("Constitution"))
                if gained:
                    msgs.append("Ralliement héroïque : +{} PV".format(gained))
        return msgs

    def death_save_crit_min(self) -> int:
        return 18 if self._sub24("Guerrier", "champion", 18) else 20

    def tile_feature_2024(self, tile: dict) -> dict:
        """Aptitude 2024 d'une tuile 2014 sur une fiche 2024 (sous-classe renommée) : {nom, description, niveau}."""
        if getattr(self, "sheet_edition", 2014) != 2024 or tile.get("ed") or not tile.get("sc"):
            return {}
        e = self.ch.find_class(tile["classe"])
        sub = self.db.subclass(tile["classe"], (e or {}).get("sous_classe", "")) if e else None
        if not sub or str(sub.get("edition", "")) != "2024":
            return {}
        if tile["id"] in TILES_HIDDEN_2024:
            return {"masquer": True}
        target = norm(TILE_FEATURE_2024.get(tile["id"], tile["nom"])).replace("’", "'")
        feats = sub.get("capacites", [])
        f = next((x for x in feats if norm(x["nom"]).replace("’", "'") == target), None) or \
            next((x for x in feats if target in norm(x["nom"]).replace("’", "'")
                  or norm(x["nom"]).replace("’", "'") in target), None)
        if not f:
            return {}
        from .class_actions import short_text
        return {"nom": f["nom"], "description": short_text(f["description"], 320), "niveau": int(f["niveau"])}

    def channel_options_2024(self, class_name: str, entry: dict, sub: dict) -> list[dict]:
        """Options de Conduit divin d'une sous-classe 2024 : aptitudes qui dépensent « une utilisation de votre
        Conduit divin » (Préservation de la vie, Radiance de l'aube, Frappe guidée, Arme sacrée…)."""
        from .class_actions import short_text
        out = []
        for f in sub.get("capacites", []):
            d = norm(f.get("description", ""))
            if f["niveau"] > entry["niveau"] or "conduit divin" not in d or "utilisation" not in d:
                continue
            out.append({"nom": f["nom"], "description": f["description"], "court": short_text(f["description"])})
        return out
