"""
Moteur de modificateurs : traduit les effets actifs (états, sorts, potions, traits innés) et l'équipement en
modificateurs chiffrés appliqués à la fiche — logique pure, sans Qt.

Schéma d'un modificateur (MECH[clé d'effet]) — toutes les entrées sont facultatives :
    ca: int                      bonus de CA            ca_min: int     CA minimale (Peau d'écorce)
    carac: {Force: +2}           bonus de score         carac_min: {Force: 21}  score fixé (au moins) à N
    attaque: [val]               tous les jets d'attaque
    degats: [str]                rappel des dégâts supplémentaires (affiché)
    js: {"*" | carac: [val]}     jets de sauvegarde (tous ou une caractéristique)
    tests: {"*" | carac: [val]}  tests de caractéristique (et donc compétences de cette caractéristique)
    competences: {nom: [val]}    compétence précise (Passage sans trace : Discrétion +10)
    vitesse_mult / vitesse_bonus
    resistances / immunites: [types de dégâts]      pv_max: int (Aide)
val : int (bonus fixe), « +1d4 » / « -1d4 » (dé ajouté), « avantage », « désavantage », « échec » (échec
automatique), « mod:Charisme » (modificateur de la caractéristique, minimum +1).

Les effets sans entrée MECH sont interprétés à partir de leurs « mods » génériques (core/effects.py).
Ce module enregistre aussi dans la bibliothèque les états de résistance / immunité aux 13 types de dégâts,
les effets de potions et quelques sorts manquants (Passage sans trace, Amélioration de caractéristique…).
"""
from __future__ import annotations

import re

from . import effects as FX
from .rules import ABILITIES, norm

ADV, DIS, FAIL = "avantage", "désavantage", "échec"

# ------------------------------------------------------------------------------------------------ types de dégâts
DAMAGE_TYPES = {   # clé -> (libellé, icône)
    "acide": ("acide", "🧪"), "contondant": ("contondants", "🔨"), "feu": ("feu", "🔥"), "force": ("force", "✴️"),
    "foudre": ("foudre", "⚡"), "froid": ("froid", "❄️"), "necrotique": ("nécrotiques", "💀"),
    "perforant": ("perforants", "🗡"), "poison": ("poison", "☠️"), "psychique": ("psychiques", "🧠"),
    "radiant": ("radiants", "☀️"), "tonnerre": ("tonnerre", "🔊"), "tranchant": ("tranchants", "⚔️"),
}
_TYPE_STEMS = [("acide", "acide"), ("contondant", "contondant"), ("feu", "feu"), ("force", "force"),
               ("foudre", "foudre"), ("froid", "froid"), ("necroti", "necrotique"), ("perforant", "perforant"),
               ("poison", "poison"), ("psychi", "psychique"), ("radiant", "radiant"), ("tonnerre", "tonnerre"),
               ("tranchant", "tranchant")]


def _register(key, nom, icone, categorie, source, duree, description, concentration=False, **mods):
    if key not in FX.EFFECTS:
        FX._e(key, nom, icone, categorie, source, duree, description, concentration, **mods)


for _k, (_label, _icon) in DAMAGE_TYPES.items():
    _register(f"resist_{_k}", f"Résistance ({_label})", _icon, "Bonus", "Trait, sort, objet ou potion", "Variable",
              f"Les dégâts {_label} que vous subissez sont réduits de moitié (arrondi à l'inférieur).",
              resistances=[_label])
    _register(f"immun_{_k}", f"Immunité ({_label})", "🛡", "Bonus", "Trait, sort ou objet", "Variable",
              f"Vous ne subissez aucun dégât {_label}.", notes=[f"Immunité aux dégâts {_label}"])

_register("metamorphose", "Métamorphose", "🦋", "État", "Sort de niveau 4 (Métamorphose)", "1 heure",
          "Vous êtes transformé en bête de FP inférieur ou égal à votre niveau : toutes vos caractéristiques (y "
          "compris mentales) et vos PV sont ceux de la bête ; vous ne pouvez ni parler ni lancer de sorts. À 0 PV, "
          "vous reprenez votre forme et l'excédent de dégâts s'applique à vos PV normaux.", True,
          notes=["Statistiques de la bête (y compris INT, SAG, CHA)", "Ni sorts ni parole", "Concentration du lanceur"])
_register("avantage_js_poison", "Robustesse contre le poison", "💚", "Aptitude", "Trait racial", "Permanente",
          "Vous avez l'avantage aux jets de sauvegarde contre le poison et l'état empoisonné.",
          notes=["Avantage aux JS contre le poison / l'état empoisonné"])
_register("ascendance_feerique", "Ascendance féerique", "🧚", "Aptitude", "Trait racial", "Permanente",
          "Vous avez l'avantage aux jets de sauvegarde contre l'état charmé, et la magie ne peut pas vous endormir.",
          notes=["Avantage aux JS contre l'état charmé", "Immunisé au sommeil magique"])
_register("passage_sans_trace", "Passage sans trace", "👣", "Bonus", "Sort de niveau 2 (Passage sans trace)",
          "1 heure", "Un voile d'ombres et de silence vous entoure, ainsi que vos alliés à 9 m : +10 aux tests de "
          "Dextérité (Discrétion) ; vous ne laissez aucune trace, sauf par magie.", True,
          notes=["+10 en Discrétion"])
for _key, _nom, _ab in (("force_taureau", "Force du taureau", "Force"), ("grace_chat", "Grâce féline", "Dextérité"),
                        ("endurance_ours", "Endurance de l'ours", "Constitution"),
                        ("ruse_renard", "Ruse du renard", "Intelligence"),
                        ("sagesse_hibou", "Sagesse du hibou", "Sagesse"),
                        ("splendeur_aigle", "Splendeur de l'aigle", "Charisme")):
    _register(_key, _nom, "🌟", "Bonus", "Sort de niveau 2 (Amélioration de caractéristique)", "1 heure",
              f"Vous avez l'avantage aux tests de {_ab}.", True, notes=[f"Avantage aux tests de {_ab}"])
_register("lien_protection", "Lien de protection", "🔗", "Bonus", "Sort de niveau 2 (Lien de protection)", "1 heure",
          "+1 à la CA et aux jets de sauvegarde, résistance à tous les dégâts ; le lanceur subit les mêmes dégâts.",
          ca=1, js=1, resistances=["tous les dégâts"])
_register("antitoxine", "Antitoxine", "💊", "Bonus", "Équipement (Antitoxine) / potion", "1 heure",
          "Avantage aux jets de sauvegarde contre le poison pendant 1 heure.",
          notes=["Avantage aux JS contre le poison"])
_register("ivresse_magique", "Inspiration (Héroïsme)", "🦸", "Bonus", "Potion d'héroïsme", "1 heure",
          "Vous gagnez 10 PV temporaires et êtes sous l'effet du sort Bénédiction pendant 1 heure.",
          attaque="+1d4", js="+1d4")
_register("potion_vitesse", "Potion de vitesse", "⏩", "Bonus", "Potion (effet de Hâte, sans concentration)",
          "1 minute", "Effets de Hâte : vitesse doublée, +2 à la CA, avantage aux JS de Dextérité, une action "
          "supplémentaire limitée (Attaquer une fois, Foncer, Se désengager, Se cacher, Utiliser un objet).",
          ca=2, vitesse_mult=2.0, notes=["Avantage aux JS de Dextérité", "Action supplémentaire limitée"])
_register("potion_escalade", "Potion d'escalade", "🧗", "Bonus", "Potion", "1 heure",
          "Vitesse d'escalade égale à votre vitesse ; avantage aux tests de Force (Athlétisme) pour escalader.",
          notes=["Vitesse d'escalade", "Avantage en Athlétisme (escalade)"])
_register("potion_invulnerabilite", "Invulnérabilité", "💎", "Bonus", "Potion d'invulnérabilité", "1 minute",
          "Résistance à tous les dégâts pendant 1 minute.", resistances=["tous les dégâts"])
_register("potion_forme_gazeuse", "Forme gazeuse", "🌫", "Bonus", "Potion de forme gazeuse", "1 heure",
          "Vous devenez un nuage : vitesse de vol 3 m, résistance aux dégâts non magiques, avantage aux JS de "
          "Force, Dextérité et Constitution ; vous ne pouvez ni attaquer ni lancer de sorts.",
          resistances=["dégâts non magiques"])
_register("potion_clairvoyance", "Clairvoyance", "🔮", "Bonus", "Potion de clairvoyance", "10 minutes",
          "Effet du sort Clairvoyance (sans concentration).", notes=["Capteur invisible à 1,5 km"])
_register("potion_pensees", "Lecture des pensées", "💭", "Bonus", "Potion de lecture des pensées", "1 minute",
          "Effet du sort Détection des pensées (DD 13).", notes=["Lire les pensées de surface"])
_register("potion_souffle", "Souffle enflammé", "🐉", "Bonus", "Potion de souffle enflammé", "1 heure",
          "Action bonus : soufflez du feu sur une cible à 9 m (JS Dex DD 13, 4d6 feu, moitié si réussite), "
          "3 fois maximum.", notes=["3 souffles : 4d6 feu, DD 13"])
_register("potion_amitie_animale", "Amitié avec les animaux", "🐾", "Bonus", "Potion", "1 heure",
          "Vous pouvez lancer Amitié avec les animaux (DD 13) à volonté.")
_register("huile_insaisissable", "Insaisissable", "🫧", "Bonus", "Huile d'insaisissabilité", "8 heures",
          "Effet de Liberté de mouvement ; vous pouvez traverser une ouverture d'au moins 2,5 cm.")
for _giant, _force in (("des collines", 21), ("des pierres", 23), ("du givre", 23), ("du feu", 25),
                       ("des nuages", 27), ("des tempêtes", 29)):
    _register("potion_force_" + norm(_giant).replace(" ", "_"), f"Force de géant {_giant}", "💪", "Bonus",
              f"Potion de force de géant {_giant}", "1 heure",
              f"Votre valeur de Force devient {_force} pendant 1 heure (sans effet si elle est déjà supérieure).",
              notes=[f"Force {_force}"])

# ------------------------------------------------------------------------------------------------ modificateurs
_ALL_DEX = {"Dextérité": [ADV]}
MECH: dict[str, dict] = {
    # --- états
    "aveugle": {"attaque": [DIS]},
    "effraye": {"attaque": [DIS], "tests": {"*": [DIS]}},
    "empoisonne": {"attaque": [DIS], "tests": {"*": [DIS]}},
    "entrave": {"attaque": [DIS], "js": {"Dextérité": [DIS]}, "vitesse_mult": 0.0},
    "etourdi": {"js": {"Force": [FAIL], "Dextérité": [FAIL]}, "vitesse_mult": 0.0},
    "inconscient": {"js": {"Force": [FAIL], "Dextérité": [FAIL]}, "vitesse_mult": 0.0},
    "paralyse": {"js": {"Force": [FAIL], "Dextérité": [FAIL]}, "vitesse_mult": 0.0},
    "petrifie": {"js": {"Force": [FAIL], "Dextérité": [FAIL]}, "vitesse_mult": 0.0,
                 "resistances": ["tous les dégâts"], "immunites": ["poison"]},
    "epuisement_1": {"tests": {"*": [DIS]}},
    "epuisement_2": {"tests": {"*": [DIS]}, "vitesse_mult": 0.5},
    "epuisement_3": {"tests": {"*": [DIS]}, "vitesse_mult": 0.5, "attaque": [DIS], "js": {"*": [DIS]}},
    "epuisement_4": {"tests": {"*": [DIS]}, "vitesse_mult": 0.5, "attaque": [DIS], "js": {"*": [DIS]},
                     "pv_max_moitie": True},
    "epuisement_5": {"tests": {"*": [DIS]}, "vitesse_mult": 0.0, "attaque": [DIS], "js": {"*": [DIS]},
                     "pv_max_moitie": True},
    "alcoolise": {"tests": {"Dextérité": [DIS], "Sagesse": [DIS]}},
    "malade": {"tests": {"Force": [DIS], "Constitution": [DIS]}},
    "hebete": {"js": {"Dextérité": [DIS]}},
    "affaibli": {"tests": {"Force": [DIS]}, "attaque": [DIS]},
    "peur": {"attaque": [DIS], "tests": {"*": [DIS]}},
    "gele": {"attaque": [DIS], "js": {"Dextérité": [DIS]}, "vitesse_mult": 0.0},
    "toile": {"attaque": [DIS], "js": {"Dextérité": [DIS]}, "vitesse_mult": 0.0},
    "enchevetrement": {"attaque": [DIS], "js": {"Dextérité": [DIS]}, "vitesse_mult": 0.0},
    "immobilisation_personne": {"js": {"Force": [FAIL], "Dextérité": [FAIL]}, "vitesse_mult": 0.0},
    "sommeil": {"js": {"Force": [FAIL], "Dextérité": [FAIL]}, "vitesse_mult": 0.0},
    "malefice_cible": {"tests": {"Force": [DIS]}},
    "rapetissement": {"tests": {"Force": [DIS]}, "js": {"Force": [DIS]}},
    # --- bonus de sorts et d'aptitudes
    "agrandissement": {"tests": {"Force": [ADV]}, "js": {"Force": [ADV]}},
    "benediction": {"attaque": ["+1d4"], "js": {"*": ["+1d4"]}},
    "fleau": {"attaque": ["-1d4"], "js": {"*": ["-1d4"]}},
    "resistance": {"js": {"*": ["+1d4"]}},
    "assistance": {"tests": {"*": ["+1d4"]}},
    "hate": {"ca": 2, "vitesse_mult": 2.0, "js": _ALL_DEX},
    "potion_vitesse": {"ca": 2, "vitesse_mult": 2.0, "js": _ALL_DEX},
    "lenteur": {"ca": -2, "vitesse_mult": 0.5, "js": {"Dextérité": [-2]}},
    "abri_partiel": {"ca": 2, "js": {"Dextérité": [2]}},
    "abri_important": {"ca": 5, "js": {"Dextérité": [5]}},
    "esquive": {"js": _ALL_DEX},
    "defense_patiente": {"js": _ALL_DEX},
    "rage": {"tests": {"Force": [ADV]}, "js": {"Force": [ADV]},
             "resistances": ["contondants", "perforants", "tranchants"]},
    "chant_lame": {"competences": {"Acrobaties": [ADV]}, "vitesse_bonus": 3.0},
    "passage_sans_trace": {"competences": {"Discrétion": [10]}},
    "force_taureau": {"tests": {"Force": [ADV]}},
    "grace_chat": {"tests": {"Dextérité": [ADV]}},
    "endurance_ours": {"tests": {"Constitution": [ADV]}},
    "ruse_renard": {"tests": {"Intelligence": [ADV]}},
    "sagesse_hibou": {"tests": {"Sagesse": [ADV]}},
    "splendeur_aigle": {"tests": {"Charisme": [ADV]}},
    "lien_protection": {"ca": 1, "js": {"*": [1]}, "resistances": ["tous les dégâts"]},
    "arme_sacree": {"attaque": ["mod:Charisme"]},
    "aide": {"pv_max": 5},
    "ivresse_magique": {"attaque": ["+1d4"], "js": {"*": ["+1d4"]}},
    "potion_escalade": {"competences": {"Athlétisme": [ADV]}},
    "potion_forme_gazeuse": {"js": {"Force": [ADV], "Dextérité": [ADV], "Constitution": [ADV]}},
    "potion_invulnerabilite": {"resistances": ["tous les dégâts"]},
    "peau_ecorce": {"ca_min": 16},
    "invisible": {"attaque": [ADV]}, "invisibilite_sort": {"attaque": [ADV]}, "invisibilite_sup": {"attaque": [ADV]},
    "cache": {"attaque": [ADV]}, "voeu_inimitie": {"attaque": [ADV]}, "attaque_temeraire": {"attaque": [ADV]},
    "aura_protection": {},            # déjà appliquée automatiquement aux JS du paladin (évite un double compte)
}
for _giant, _force in (("des collines", 21), ("des pierres", 23), ("du givre", 23), ("du feu", 25),
                       ("des nuages", 27), ("des tempêtes", 29)):
    MECH["potion_force_" + norm(_giant).replace(" ", "_")] = {"carac_min": {"Force": _force}}
for _k, (_label, _icon) in DAMAGE_TYPES.items():
    MECH[f"resist_{_k}"] = {"resistances": [_label]}
    MECH[f"immun_{_k}"] = {"immunites": [_label]}


def _generic(key: str) -> dict:
    """Interprétation des « mods » génériques d'un effet sans entrée MECH."""
    m = FX.EFFECTS.get(key, {}).get("mods") or {}
    out: dict = {}
    for k in ("ca", "vitesse_mult", "vitesse_bonus"):
        if k in m:
            out[k] = m[k]
    if m.get("attaque") not in (None, "", 0):
        out["attaque"] = [m["attaque"]]
    if m.get("js") not in (None, "", 0):
        out["js"] = {"*": [m["js"]]}
    if m.get("tests") not in (None, "", 0):
        out["tests"] = {"*": [m["tests"]]}
    if m.get("resistances"):
        out["resistances"] = list(m["resistances"])
    return out


def mech(key: str) -> dict:
    return MECH[key] if key in MECH else _generic(key)


# ------------------------------------------------------------------------------------------------ potions
POTION_RULES = [   # (fragment de nom normalisé, action) — l'ordre compte
    ("guerison supreme", ("soin", "10d4+20")), ("guerison superieure", ("soin", "8d4+8")),
    ("guerison majeure", ("soin", "4d4+4")), ("guerison", ("soin", "2d4+2")),
    ("force de geant", ("force", None)), ("vitesse", ("effet", "potion_vitesse")),
    ("vitalite", ("purge", ["empoisonne", "malade", "epuisement_1", "epuisement_2", "epuisement_3", "epuisement_4",
                            "epuisement_5"])),
    ("antitox", ("antidote", None)), ("antidote", ("antidote", None)),
    ("sante", ("purge", ["empoisonne", "malade", "aveugle", "assourdi", "paralyse"])),
    ("heroisme", ("heroisme", None)), ("agrandissement", ("effet", "agrandissement")),
    ("croissance", ("effet", "agrandissement")), ("diminution", ("effet", "rapetissement")),
    ("invisibilite", ("effet", "invisibilite_sort")), ("vol", ("effet", "vol")),
    ("respiration aquatique", ("effet", "respiration_aquatique")), ("escalade", ("effet", "potion_escalade")),
    ("invulnerabilite", ("effet", "potion_invulnerabilite")), ("forme gazeuse", ("effet", "potion_forme_gazeuse")),
    ("clairvoyance", ("effet", "potion_clairvoyance")), ("lecture des pensees", ("effet", "potion_pensees")),
    ("souffle enflamme", ("effet", "potion_souffle")), ("amitie avec les animaux", ("effet", "potion_amitie_animale")),
    ("insaisissabilite", ("effet", "huile_insaisissable")), ("resistance", ("resistance", None)),
    ("poison", ("poison", None)), ("amour", ("effet", "charme")),
]


def is_consumable(name: str) -> bool:
    n = norm(name)
    return n.startswith(("potion", "philtre", "elixir", "huile", "antitox")) or "antidote" in n


def potion_action(name: str):
    n = norm(name)
    for frag, action in POTION_RULES:
        if frag in n:
            return action
    return ("narratif", None)


# ------------------------------------------------------------------------------------------------ traits innés
_RES_RX = re.compile(r"r[ée]sistan(?:ce|t)e?s?\s+(?:aux|au|à|a)\s+(?:d[ée]g[âa]ts\s+)?([^.;]*?)(?:,\s+(?:et\s+)?(?:l'|la\s|vous|mais)|[.;]|$)",
                     re.I)
_IMM_RX = re.compile(r"immunis[ée]e?s?\s+(?:contre|aux?)(?:(?!r[ée]sistan|avez|,)[^.;])*?d[ée]g[âa]ts\s+([^,.;]*)",
                     re.I)
_IMM_POISON_RX = re.compile(r"immunis[ée]e?s?\s+(?:contre|aux?)\s+(?:les\s+maladies\s+(?:et|ainsi que)\s+)?(?:le|au|les)?\s*poisons?",
                            re.I)
_FEY_RX = re.compile(r"avantage aux jets de sauvegarde (?:contre|pour (?:éviter|eviter)[^.]*?) (?:le charme|l'[ée]tat "
                     r"charm)|avantage contre le charme", re.I)
_POISON_SAVE_RX = re.compile(r"avantage aux jets de sauvegarde contre (?:le poison|l'[ée]tat empoisonn)", re.I)


def damage_types_in(text: str) -> list[str]:
    n = norm(text)
    if "type de degats" in n or "au choix" in n or "sauf" in n or "tous les" in n or "votre element" in n:
        return []
    return [key for stem, key in _TYPE_STEMS if re.search(r"\b" + stem, n)]


def innate_from_text(text: str) -> list[str]:
    """Clés d'effets permanents décrits par un trait (résistances, immunités, robustesse au poison)."""
    out = []
    for m in _RES_RX.finditer(text):
        out += [f"resist_{t}" for t in damage_types_in(m.group(1))]
    for m in _IMM_RX.finditer(text):
        out += [f"immun_{t}" for t in damage_types_in(m.group(1))]
    if _IMM_POISON_RX.search(text):
        out.append("immun_poison")
    if _POISON_SAVE_RX.search(text):
        out.append("avantage_js_poison")
    if _FEY_RX.search(text) and re.search(r"endormir|sommeil", text, re.I):
        out.append("ascendance_feerique")               # Ascendance féerique (elfes, demi-elfes)
    return list(dict.fromkeys(out))


# ------------------------------------------------------------------------------------------------ calculs
def value_of(val, mods: dict) -> tuple[int, str]:
    """(bonus numérique, dé éventuel) d'une valeur de modificateur."""
    if isinstance(val, bool):
        return 0, ""
    if isinstance(val, int):
        return val, ""
    if isinstance(val, str) and val.startswith("mod:"):
        return max(1, int(mods.get(val[4:], 0))), ""
    if isinstance(val, str) and re.fullmatch(r"[+-]\d+d\d+", val.replace(" ", "")):
        return 0, val.replace(" ", "")
    return 0, ""


def collect(entries: list[tuple[str, list]], mods: dict) -> dict:
    """
    Agrège des valeurs [(source, [val...])] : {bonus, des, avantage, desavantage, echec, detail}
    detail : [(libellé, texte de la valeur)] pour les infobulles « style Pathfinder ».
    """
    res = {"bonus": 0, "des": [], "avantage": [], "desavantage": [], "echec": [], "detail": []}
    for source, values in entries:
        for v in values:
            if v == ADV:
                res["avantage"].append(source)
            elif v == DIS:
                res["desavantage"].append(source)
            elif v == FAIL:
                res["echec"].append(source)
            else:
                n, dice = value_of(v, mods)
                if n:
                    res["bonus"] += n
                    res["detail"].append((source, "{:+d}".format(n)))
                if dice:
                    res["des"].append(dice)
                    res["detail"].append((source, dice))
    return res


def adv_state(res: dict) -> str:
    """« avantage », « désavantage », « échec » ou '' (avantage et désavantage s'annulent — PHB)."""
    if res["echec"]:
        return FAIL
    if res["avantage"] and res["desavantage"]:
        return ""
    return ADV if res["avantage"] else DIS if res["desavantage"] else ""


ABILITY_SET = set(ABILITIES)


def mech_lines(key: str) -> list[str]:
    """Impact mécanique lisible d'un effet (affiché dans les infobulles de la barre d'états)."""
    m, out = mech(key), []
    if m.get("ca"):
        out.append("CA {:+d}".format(m["ca"]))
    if m.get("ca_min"):
        out.append("CA minimale {}".format(m["ca_min"]))
    for ab, v in m.get("carac", {}).items():
        out.append("{} {:+d}".format(ab, v))
    for ab, v in m.get("carac_min", {}).items():
        out.append("{} portée à {}".format(ab, v))
    if "vitesse_mult" in m:
        out.append("Vitesse 0" if m["vitesse_mult"] == 0 else "Vitesse ×{:g}".format(m["vitesse_mult"]))
    if m.get("vitesse_bonus"):
        out.append("Vitesse {:+g} m".format(m["vitesse_bonus"]))

    def fmt(vals):
        return ", ".join("{:+d}".format(v) if isinstance(v, int) else
                         ("+ mod. " + v[4:]) if str(v).startswith("mod:") else str(v) for v in vals)
    if m.get("attaque"):
        out.append("Jets d'attaque : " + fmt(m["attaque"]))
    for label, field in (("Jets de sauvegarde", "js"), ("Tests", "tests")):
        for ab, vals in m.get(field, {}).items():
            out.append("{}{} : {}".format(label, "" if ab == "*" else " de " + ab, fmt(vals)))
    for skill, vals in m.get("competences", {}).items():
        out.append("{} : {}".format(skill, fmt(vals)))
    if m.get("resistances"):
        out.append("Résistance : " + ", ".join(m["resistances"]))
    if m.get("immunites"):
        out.append("Immunité : " + ", ".join(m["immunites"]))
    if m.get("pv_max"):
        out.append("PV max {:+d}".format(m["pv_max"]))
    if m.get("pv_max_moitie"):
        out.append("PV max divisés par deux")
    return out


# ------------------------------------------------------------------------------------------------ objets équipés
ITEM_MECH = [   # (fragment de nom normalisé, modificateur) — objets équipés (et harmonisés si nécessaire)
    ("ceinturon de force de geant des collines", {"carac_min": {"Force": 21}}),
    ("ceinturon de force de geant des pierres", {"carac_min": {"Force": 23}}),
    ("ceinturon de force de geant du givre", {"carac_min": {"Force": 23}}),
    ("ceinturon de force de geant du feu", {"carac_min": {"Force": 25}}),
    ("ceinturon de force de geant des nuages", {"carac_min": {"Force": 27}}),
    ("ceinturon de force de geant des tempetes", {"carac_min": {"Force": 29}}),
    ("gantelets de puissance d'ogre", {"carac_min": {"Force": 19}}),
    ("bandeau d'intelligence", {"carac_min": {"Intelligence": 19}}),
    ("amulette de sante", {"carac_min": {"Constitution": 19}}),
    ("ceinturon des nains", {"carac": {"Constitution": 2}, "resistances": ["poison"]}),
    ("bottes elfiques", {"competences": {"Discrétion": [ADV]}}),
    ("cape elfique", {"competences": {"Discrétion": [ADV]}}),
    ("pierre de ioun (force)", {"carac": {"Force": 2}}),
    ("pierre de ioun (agilite)", {"carac": {"Dextérité": 2}}),
    ("pierre de ioun (vigueur)", {"carac": {"Constitution": 2}}),
    ("pierre de ioun (intellect)", {"carac": {"Intelligence": 2}}),
    ("pierre de ioun (intuition)", {"carac": {"Sagesse": 2}}),
    ("pierre de ioun (dirigeant)", {"carac": {"Charisme": 2}}),
]


def item_mech(name: str) -> dict:
    n = norm(name)
    return next((m for frag, m in ITEM_MECH if n.startswith(frag)), {})


# ------------------------------------------------------------------------------------------------ sorts -> effets
SPELL_ALIASES = {"armure_mage": "Armure de mage", "agrandissement": "Agrandissement/Rapetissement",
                 "rapetissement": "Agrandissement/Rapetissement", "protection_energie": "Protection contre une énergie",
                 "vision_veritable": "Vision suprême"}
PERSONAL_BUFFS = {"passage sans trace"}           # sorts de zone centrés sur le lanceur : appliqués d'office


def spell_buffs(db) -> dict:
    """{nom normalisé du sort: [clés d'effets bénéfiques (catégories Bonus / Aura)]} pour la bibliothèque."""
    out: dict = {}
    for key, e in FX.EFFECTS.items():
        if e["categorie"] not in ("Bonus", "Aura"):
            continue
        name = SPELL_ALIASES.get(key)
        if not name:
            m = re.match(r"(?:Sort de niveau \d+|Tour de magie) \((.+)\)", e.get("source", ""))
            name = m.group(1) if m else ""
        spell = db.find_spell(name) if name else None
        if spell:
            out.setdefault(norm(spell["nom"]), []).append(key)
    return out
