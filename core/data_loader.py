"""
Chargement de la base de données locale (fichiers JSON) et croisement des données.

Le chargeur identifie chaque fichier par son CONTENU (pas par son nom) :
    classes (clé « classe »), Classes_Depart, Compétences, Races, Historiques, Outils, Langues,
    Armes (« armes_dnd_5e »), Armures (« armures_dnd_5e »), Équipement (« equipement_aventurier_dnd_5e »),
    Dons (liste de « don »), Magie-N (« sorts_niveau_N »), Sorts_Listes (listes de classes par sort),
    Bonus_Raciaux.

Il est tolérant : un JSON avec une virgule manquante entre deux objets est réparé automatiquement
(et signalé), un fichier absent est remplacé par un petit jeu de secours intégré.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from .rules import (ABBR_TO_FULL, ABILITIES, CLASS_SKILL_COUNT, norm, parse_spell_mechanics, parse_weight)

# Noms alternatifs de classes / compétences rencontrés dans les fichiers fournis
CLASS_ALIASES = {"sorcier": "Occultiste"}  # Classes_Depart.json utilise « Sorcier » pour l'Occultiste
SKILL_ALIASES = {"intuition": "Perspicacité", "dresseur de betes": "Dressage", "dressage": "Dressage"}

# Compétences de classe absentes de Classes_Depart.json (ajoutées à la liste de choix sans modifier vos fichiers).
SKILL_FIXES = {
    "Moine": ["Perspicacité"], "Druide": ["Perspicacité"], "Guerrier": ["Dressage", "Perspicacité"],
    "Paladin": ["Perspicacité"], "Rôdeur": ["Perspicacité"], "Roublard": ["Perspicacité", "Tromperie"],
    "Ensorceleur": ["Perspicacité", "Tromperie"], "Magicien": ["Perspicacité"],
    "Occultiste": ["Intimidation", "Tromperie"],
}

# Effets mécaniques de certains dons (Dons.json ne contient que du texte). Clé = nom normalisé.
# v45 : dons de maîtrise d'armures du Manuel des joueurs, absents de Dons.json (ajoutés sans modifier vos fichiers)
EXTRA_FEATS = [
    {"don": "Maîtrise des armures légères", "source": "Manuel des Joueurs (PHB)", "prerequis": "Aucun",
     "augmentation_caracteristique": "Force ou Dextérité +1",
     "description": "Vous êtes entraîné à porter les armures légères : vous gagnez la maîtrise des armures légères."},
    {"don": "Maîtrise des armures intermédiaires", "source": "Manuel des Joueurs (PHB)",
     "prerequis": "Maîtrise des armures légères", "augmentation_caracteristique": "Force ou Dextérité +1",
     "description": "Vous êtes entraîné à porter les armures intermédiaires et les boucliers : vous gagnez la maîtrise "
                    "des armures intermédiaires et des boucliers."},
    {"don": "Maîtrise des armures lourdes", "source": "Manuel des Joueurs (PHB)",
     "prerequis": "Maîtrise des armures intermédiaires", "augmentation_caracteristique": "Force +1",
     "description": "Vous êtes entraîné à porter les armures lourdes : vous gagnez la maîtrise des armures lourdes."},
]
# maîtrises accordées par un don : nom normalisé -> (armures, armes)
FEAT_PROFICIENCIES = {
    "maitrise des armures legeres": (["Armures légères"], []),
    "maitrise des armures intermediaires": (["Armures intermédiaires", "Boucliers"], []),
    "maitrise des armures lourdes": (["Armures lourdes"], []),
    "armure legere": (["Armures légères"], []),                # variantes de nom (VF non officielles)
    "armure intermediaire": (["Armures intermédiaires", "Boucliers"], []),
    "armure lourde": (["Armures lourdes"], []),
    "armure": (["Armures intermédiaires", "Boucliers"], []),     # « Armuré » (Moderately Armored)
    "cuirasse": (["Armures lourdes"], []),                        # « Cuirassé » (Heavily Armored)
}

FEAT_EFFECTS = {
    "alerte": {"initiative": 5},
    "robuste": {"pv_par_niveau": 2},
    "mobile": {"vitesse": 3},
    "observateur": {"perception_passive": 5},
}

UNARMED = {"nom": "Mains nues", "categorie": "courante", "type": "cac", "degats": "1", "type_degats": "contondant",
           "proprietes": ["Arts martiaux (Moine)"], "polyvalent": "", "portee": "", "botte": "",
           "botte_desc": "", "poids": "—", "prix": "—", "origine": "Officiel"}
NO_ARMOR = {"nom": "Aucune armure", "categorie": "aucune", "ca_base": 10, "dex_max": None, "force_min": 0,
            "desavantage_discretion": False, "poids": "—", "prix": "—", "origine": "Officiel",
            "description": "CA = 10 + modificateur de Dextérité.", "shield": False}

# --------------------------------------------------------------------------------------
# Jeu de secours (formes « brutes » identiques à vos JSON) — permet une exécution immédiate
# --------------------------------------------------------------------------------------
FALLBACK: dict[str, Any] = {
    "competences": [{"competence": n, "caracteristique": c} for n, c in (
        ("Acrobaties", "Dextérité"), ("Arcanes", "Intelligence"), ("Athlétisme", "Force"), ("Discrétion", "Dextérité"),
        ("Dressage", "Sagesse"), ("Escamotage", "Dextérité"), ("Histoire", "Intelligence"),
        ("Intimidation", "Charisme"), ("Investigation", "Intelligence"), ("Médecine", "Sagesse"),
        ("Nature", "Intelligence"), ("Perception", "Sagesse"), ("Perspicacité", "Sagesse"),
        ("Persuasion", "Charisme"), ("Religion", "Intelligence"), ("Représentation", "Charisme"),
        ("Survie", "Sagesse"), ("Tromperie", "Charisme"))],
    "classes_depart": [
        {"classe": "Guerrier", "pv_initiaux": 10, "de_vie": "d10",
         "competences_disponibles": ["Acrobaties", "Athlétisme", "Histoire", "Intimidation", "Perception", "Survie"],
         "jets_de_sauvegarde": ["Force", "Constitution"], "armures_maitrisees": ["Toutes les armures", "Boucliers"],
         "armes_maitrisees": ["Armes courantes", "Armes de guerre"]},
        {"classe": "Magicien", "pv_initiaux": 6, "de_vie": "d6",
         "competences_disponibles": ["Arcanes", "Histoire", "Investigation", "Médecine", "Religion"],
         "jets_de_sauvegarde": ["Intelligence", "Sagesse"], "armures_maitrisees": ["Aucune"],
         "armes_maitrisees": ["Dagues", "Dard", "Frondes", "Bâtons", "Arbalètes légères"]}],
    "classes": [
        {"nom": "Guerrier", "de_vie": "d10", "carac_principale": "Force ou Dextérité", "sous_classes": [
            {"nom": "Champion", "source": "Manuel des Joueurs", "capacites": [
                {"niveau": 3, "nom": "Coup critique amélioré", "description": "Critique sur 19-20."}]}],
         "capacites_classe": [
             {"niveau": 1, "nom": "Second souffle", "description": "Regagne 1d10 + niveau PV (action bonus)."},
             {"niveau": 4, "nom": "Amélioration de caractéristiques", "description": "+2 ou don."}]},
        {"nom": "Magicien", "de_vie": "d6", "carac_principale": "Intelligence", "sous_classes": [],
         "capacites_classe": [
             {"niveau": 1, "nom": "Incantation", "description": "Sorts préparés basés sur l'Intelligence."}]}],
    "races": {"especes": [{"nom": "Humain", "source": "MJ", "caracteristiques": "Toutes +1", "langues": ["Commun"],
                           "capacites": [{"nom": "Polyvalent", "description": "+1 à tout."}]}]},
    "historiques": [{"historique": "Soldat", "competence_1": "Athlétisme", "competence_2": "Intimidation",
                     "langues": "", "outil_maitrise": "", "inventaire_historique": "Insigne de grade, Corde", "or": 10}],
    "outils": {"outils_dnd_5e": [{"nom": "Outils de voleur", "categorie": "Autres outils", "prix": "25 po",
                                  "caracteristique": "Dextérité", "poids": "0,5 kg",
                                  "utilisation": "crocheter une serrure (DD 15)"}]},
    "sorts_part": [{"nom": "Trait de feu", "niveau": 0, "ecole": "évocation", "incantation": "1 action",
                    "portee": "36 m", "composantes": "V, S", "concentration": False, "rituel": False,
                    "description": "Si l'attaque avec un sort touche, inflige 1d10 dégâts de feu (dégâts/niv)."}],
    "sorts_listes": {"listes_de_classes": {"Trait de feu": ["Magicien", "Ensorceleur"]}},
    "armes": {"armes_dnd_5e": [
        {"nom": "Épée longue", "categorie": "Armes de guerre de corps à corps", "degats": "1d8 tranchants",
         "proprietes": "Polyvalente (1d10)", "botte_arme": "Sape", "description_botte": "", "poids": "1,5 kg",
         "prix": "15 po"},
        {"nom": "Arc long", "categorie": "Armes de guerre à distance", "degats": "1d8 perforants",
         "proprietes": "Deux mains, Lourde, Munitions (portée 45/180 ; flèches)", "botte_arme": "Ralentissement",
         "description_botte": "", "poids": "1 kg", "prix": "50 po"}]},
    "armures": {"armures_dnd_5e": [
        {"nom": "Cotte de mailles", "categorie": "Armures lourdes", "classe_armure": "16", "force_requise": "For 13",
         "discretion": "Désavantage", "poids": "27,5 kg", "prix": "75 po", "origine": "Officiel"},
        {"nom": "Bouclier", "categorie": "Bouclier", "classe_armure": "+2", "force_requise": "—",
         "discretion": "Normale", "poids": "3 kg", "prix": "10 po", "origine": "Officiel"}]},
    "dons": [{"don": "Alerte", "source": "MJ", "prerequis": "Aucun", "augmentation_caracteristique": "Aucune",
              "description": "+5 à l'initiative."}],
    "equipement": {"equipement_aventurier_dnd_5e": [
        {"nom": "Corde", "poids": "2,5 kg", "prix": "1 po", "description": "Corde robuste."}]},
    "langues": [{"categorie": "Standard", "langue": "Commun", "locuteurs_typiques": "Tous"}],
    "objets_magiques": {"objets": [
        {"id": "anneau-de-protection", "nom": "Anneau de protection", "type": "Anneau", "type_precision": None,
         "rarete": "rare", "rarete_texte": "rare", "lien": True, "lien_condition": None,
         "description": "Vous obtenez un bonus de +1 à la CA et aux jets de sauvegarde lorsque vous portez cet anneau.",
         "source_livre": "Dungeon Master's Guide"}]},
    "styles": {"styles_de_combat_et_armures": {
        "guerrier": [{"nom": "Défense", "description": "+1 à la CA lorsque vous portez une armure."}],
        "modeles_d_armure": [{"nom": "Gardien", "description": "Armure d'exocombat de mêlée."},
                             {"nom": "Infiltré", "description": "Armure d'exocombat à distance."}]}},
    "manifestations": {"manifestations_occultes": [
        {"nom": "Armure d'ombres", "categorie": "Communes / Pactes",
         "description": "Lance le sort Armure de mage à volonté."}]},
    "bonus_raciaux": {"races": {"Humain": {"fixe": {a: 1 for a in ABILITIES}, "libres": []}},
                      "vitesses": {"Nain": 7.5}, "sous_races": {}},
}


# --------------------------------------------------------------------------------------
# Lecture JSON tolérante
# --------------------------------------------------------------------------------------
def read_json(path: Path) -> tuple[Any, Optional[str]]:
    """Lit un JSON ; répare l'erreur courante « } { » (virgule manquante entre objets). Retourne (contenu, avertissement)."""
    text = path.read_text(encoding="utf-8-sig")
    try:
        return json.loads(text), None
    except json.JSONDecodeError as first:
        fixed = re.sub(r"\}(\s*)\{", r"},\1{", text)
        fixed = re.sub(r"\](\s*)\[", r"],\1[", fixed)
        try:
            return json.loads(fixed), f"{path.name} : syntaxe invalide (ligne {first.lineno}), réparé automatiquement."
        except json.JSONDecodeError:
            raise first


def split_top_level(text: str) -> list[str]:
    """Découpe sur les virgules situées hors des parenthèses."""
    return [p.strip() for p in re.split(r",\s*(?![^()]*\))", text or "") if p.strip()]


def parse_race_bonus(text: str) -> dict:
    """
    Analyse le champ « caracteristiques » d'une race :
      « Dex +2, Sag +1 »             -> fixe {Dextérité: 2, Sagesse: 1}
      « +2, +1 »                     -> libres [2, 1] (à répartir au choix)
      « +2, +1 (ou +1, +1, +1) »     -> libres [2, 1] et alternative [1, 1, 1]
      « Toutes +1 »                  -> fixe : +1 partout
      « Cha +2, +1 »                 -> fixe {Charisme: 2} + libres [1]
    """
    fixe: dict[str, int] = {}
    libres: list[int] = []
    alternative: list[int] = []
    body = text or ""
    alt = re.search(r"\(ou ([^)]*)\)", body)
    if alt:
        alternative = [int(x) for x in re.findall(r"\+(\d+)", alt.group(1))]
        body = body[:alt.start()]
    for token in body.split(","):
        m = re.match(r"\s*(\S+)?\s*\+(\d+)", token)
        if not m:
            continue
        name, value = m.group(1), int(m.group(2))
        if not name:
            libres.append(value)
        elif norm(name) in ("toutes", "tous"):
            for ab in ABILITIES:
                fixe[ab] = fixe.get(ab, 0) + value
        elif full_ability(name):
            fixe[full_ability(name)] = fixe.get(full_ability(name), 0) + value
    return {"fixe": fixe, "libres": libres, "alternative": alternative}


PACTS = ["Pacte de la lame", "Pacte de la chaîne", "Pacte du grimoire", "Pacte du talisman"]

_GRANT = re.compile(r"^Lance(?:\s+le\s+sort)?\s+(.+?)(?:\s+sur\s+soi)?(?:\s+gratuitement)?"
                    r"(?:\s+à\s+volonté|\s*\(([^)]*)\))\.?$")


def parse_grants(description: str) -> list[dict]:
    """
    Détecte les sorts accordés par une manifestation occulte :
      « Lance le sort Armure de mage à volonté. »               -> À volonté
      « Lance le sort Imprécation (1 emplacement de sort/long repos). » -> 1 emplacement de sort / repos long
      « Modification d'apparence à volonté. »                    -> À volonté
    """
    text = (description or "").strip()
    m = _GRANT.match(text)
    if m:
        usage = (m.group(2) or "À volonté").replace("/long repos", " / repos long").replace("/repos long", " / repos long")
        return [{"sort": m.group(1).strip(), "usage": usage[:1].upper() + usage[1:]}]
    m = re.match(r"^([A-ZÉÈ][^.,;]{2,40}?)\s+à volonté\.?$", text)
    if m and not norm(m.group(1)).startswith(("avantage", "permet", "maitrise")):
        return [{"sort": m.group(1).strip(), "usage": "À volonté"}]
    return []


def normalize_manifestation(m: dict) -> dict:
    """Manifestation occulte : prérequis structurés (v37) ou, à défaut, déduits de la catégorie / description."""
    cat = norm(m.get("categorie", ""))
    pact = ""
    for label in PACTS:
        if cat.startswith(norm(label)):
            pact = label
    lvl = re.search(r"niv(?:eau|\.)?\s*(\d+)", cat)
    pre = m.get("prerequis") or {}
    if "sorts" in m:
        grants = [{"sort": g["sort"], "usage": g.get("usage", "À volonté"), "emplacement": bool(g.get("emplacement")),
                   "limite": g.get("limite", ""), "cible": g.get("cible", "")} for g in m["sorts"]]
    else:
        grants = [dict(g, emplacement="emplacement" in norm(g["usage"]) and "sans" not in norm(g["usage"]),
                       limite="repos long" if "repos" in norm(g["usage"]) else "", cible="")
                  for g in parse_grants(m.get("description", ""))]
    return {"nom": m["nom"], "categorie": m.get("categorie", ""), "description": m.get("description", ""),
            "pacte": pre.get("pacte", pact) if pre else pact,
            "niveau": int(pre.get("niveau", 0)) if pre else (int(lvl.group(1)) if lvl else 0),
            "sort_requis": pre.get("sort", ""), "special": pre.get("special", ""), "source": m.get("source", ""),
            "effets": list(m.get("effets", [])), "sorts": grants}


SAVE_TESTS = ("For", "Dex", "Con", "Int", "Sag", "Cha")


def save_success_text(spell: dict) -> str:
    """« Succès = 1/2 dégâts », « Succès = 0 dégât », « Dégâts même en cas de succès »… (sorts à JS)."""
    v = spell.get("js_succes", "")
    if not v or spell.get("test") not in SAVE_TESTS:
        return ""
    if not spell.get("degats"):
        return "Succès = aucun effet (ou effet réduit, voir la description)"
    return {"moitie": "Succès = 1/2 dégâts", "aucun": "Succès = 0 dégât",
            "toujours": "Dégâts même en cas de succès (le JS n'évite que l'effet)"}.get(v, "Succès = " + v)


def apply_spell_rule(spell: dict, rule: dict) -> None:
    """Applique la règle auditée d'un sort (durée, dégâts, soins, surclassement, étiquettes)."""
    if "rituel" in rule:
        spell["rituel"] = bool(rule["rituel"])
    if "concentration" in rule:
        spell["concentration"] = bool(rule["concentration"])
    if rule.get("duree"):
        d = rule["duree"]
        spell["duree"] = "Concentration, jusqu'à " + d[:1].lower() + d[1:] if spell["concentration"] else d
    for key in ("degats", "type_degats", "test"):
        if key in rule:
            spell[key] = rule[key]
    if "projectiles" in rule:
        spell["rayons"] = False
    for key in ("mod", "soins", "soins_mod", "pv_temp", "sup", "sup_pas", "sup_soins", "sup_pv_temp", "sup_table",
                "projectiles", "sup_projectiles", "sup_texte", "echelle", "hors_corpus", "js_succes"):
        if key in rule:
            spell[key] = rule[key]


def full_ability(name: str) -> str:
    """'Dex' / 'dextérité' / 'Dextérité' -> 'Dextérité' (chaîne vide si inconnue)."""
    n = norm(name)
    for ab in ABILITIES:
        if norm(ab) == n:
            return ab
    return ABBR_TO_FULL.get(n[:3], "")


# --------------------------------------------------------------------------------------
# Normalisation des formats
# --------------------------------------------------------------------------------------
def normalize_weapon(w: dict) -> dict:
    cat = norm(w.get("categorie", ""))
    parts = (w.get("degats", "") or "1").split(None, 1)
    kind = norm(parts[1]).rstrip("s") if len(parts) > 1 else ""
    polyvalent, portee, names = "", "", []
    for prop in split_top_level(w.get("proprietes", "")):
        if prop in ("—", "-"):
            continue
        name = re.sub(r"\s*\(.*\)", "", prop).strip()
        detail = (re.search(r"\((.*)\)", prop) or [None, ""])[1]
        if norm(name).startswith("polyvalent"):
            polyvalent = detail
        rng = re.search(r"portee\s*([\d.,/]+)", norm(detail))
        if rng:
            portee = rng.group(1)
        names.append(name)
    return {"nom": w["nom"], "categorie": "courante" if "courante" in cat else "guerre",
            "type": "distance" if "distance" in cat else "cac", "degats": parts[0], "type_degats": kind,
            "proprietes": names, "polyvalent": polyvalent, "portee": portee, "botte": w.get("botte_arme", ""),
            "botte_desc": w.get("description_botte", ""), "poids": w.get("poids", "—"), "prix": w.get("prix", "—"),
            "origine": w.get("origine", "Officiel")}


def normalize_armor(a: dict) -> dict:
    ca = a.get("classe_armure", "")
    cat = norm(a.get("categorie", ""))
    if "bouclier" in cat:
        bonus = re.search(r"\d+", ca)
        return {"nom": a["nom"], "bonus_ca": int(bonus.group()) if bonus else 2, "poids": a.get("poids", "—"),
                "prix": a.get("prix", "—"), "origine": a.get("origine", "Officiel"),
                "description": a.get("description", ""), "shield": True}
    base = re.search(r"\d+", ca)
    has_dex = "dex" in norm(ca)
    mx = re.search(r"max\s*(\d+)", norm(ca))
    dex_max = (int(mx.group(1)) if mx else None) if has_dex else 0
    force = re.search(r"\d+", a.get("force_requise", ""))
    category = "légère" if "leg" in cat else "intermédiaire" if "inter" in cat else "lourde"
    return {"nom": a["nom"], "categorie": category, "ca_base": int(base.group()) if base else 10, "dex_max": dex_max,
            "force_min": int(force.group()) if force else 0,
            "desavantage_discretion": norm(a.get("discretion", "")).startswith("desav"),
            "poids": a.get("poids", "—"), "prix": a.get("prix", "—"), "origine": a.get("origine", "Officiel"),
            "description": a.get("description", ""), "shield": False}


def normalize_feat(d: dict) -> dict:
    asi = d.get("augmentation_caracteristique", "")
    if "+1" in asi and "au choix" in norm(asi):
        choices = list(ABILITIES)
    else:
        choices = [ab for ab in ABILITIES if norm(ab) in norm(asi)] if "+1" in asi else []
    name = d.get("don") or d.get("nom", "")
    return {"nom": name, "source": d.get("source", ""), "prerequis": d.get("prerequis", "Aucun"),
            "asi_texte": asi, "carac_choix": choices, "description": d.get("description", ""),
            "effets": d.get("effets") or FEAT_EFFECTS.get(norm(name), {})}


def normalize_magic_item(o: dict) -> dict:
    """
    Objet magique (objets_magiques.json). Champs utiles : lien (harmonisation requise) + condition, rareté, description.
    Les bonus sont déduits : « +1, +2 ou +3 » dans le nom = bonus variable à choisir ; « bonus de +N à la CA (et aux jets
    de sauvegarde) » dans la description = bonus automatique appliqué à la fiche quand l'objet est actif.
    """
    desc = o.get("description", "") or ""
    variable = bool(re.search(r"\+1, \+2 ou \+3", o["nom"]))
    m = re.search(r"bonus de \+(\d) à la CA(?! contre)", desc)
    ca = int(m.group(1)) if (m and not variable) else 0
    tier = re.fullmatch(r"(Armure|Bouclier) \+(\d)", o["nom"])
    if tier:                                   # paliers séparés : « Armure +2 », « Bouclier +1 »
        ca = int(tier.group(2))
    js = ca if re.search(r"bonus de \+\d à la CA et aux jets de sauvegarde", desc) else 0
    return {"id": o.get("id", o["nom"]), "nom": o["nom"], "type": o.get("type", "") or "",
            "precision": o.get("type_precision") or "", "rarete": o.get("rarete_texte") or o.get("rarete", "") or "",
            "lien": bool(o.get("lien")), "condition": o.get("lien_condition") or "", "description": desc,
            "variable": variable, "ca_variable": variable and o.get("type") in ("Armure",), "ca": ca, "js": js,
            "source": o.get("source_livre") or o.get("source", "") or ""}


def merge_statblock_lines(lines: list[str]) -> list[str]:
    """
    Recolle les lignes de statblock coupées en deux dans le JSON :
    ["A|Morsure. +4, 1,50 m, 1d10+2", "perforants"] -> ["A|Morsure. +4, 1,50 m, 1d10+2 perforants"].
    """
    out: list[str] = []
    for line in lines:
        line = (line or "").strip()
        if not line:
            continue
        if out and not line.startswith("A|") and not line[0].isupper():
            out[-1] = out[-1] + " " + line
        else:
            out.append(line)
    return out


def normalize_beast(m: dict) -> dict:
    """Bête du bestiaire : FP numérique, vitesses de vol / nage détectées, lignes d'attaques recollées."""
    from .rules import parse_cr
    speed = m.get("vitesse", "") or ""
    kind = m.get("description_type", "") or ""
    size = re.search(r"taille (\w+)", kind)
    traits, actions = [], []
    for line in merge_statblock_lines(m.get("traits_et_attaques", [])):
        (actions if line.startswith("A|") else traits).append(line[2:] if line.startswith("A|") else line)
    xp = re.search(r"\((\d[\d\s]*)\s*PX\)", m.get("puissance", ""))
    return {"nom": m["nom"], "type": kind, "taille": size.group(1) if size else "", "ca": m.get("classe_d_armure", ""),
            "pv": m.get("points_de_vie", ""), "vitesse": speed, "vol": bool(re.search(r"\bvol\b", speed)),
            "nage": bool(re.search(r"\bnage\b", speed)), "fp": parse_cr(m.get("puissance", "")),
            "fp_txt": (m.get("puissance", "") or "").split(" ")[0], "px": int(xp.group(1).replace(" ", "")) if xp else 0,
            "carac": {k: (v.get("score", 10), v.get("mod", "+0")) for k, v in (m.get("caracteristiques") or {}).items()},
            "competences": m.get("competences", ""), "sens": m.get("sens", ""), "langues": m.get("langues", ""),
            "traits": traits, "actions": actions, "nuee": "nuée" in kind.lower()}


def normalize_equipment(e: dict) -> dict:
    return {"nom": e["nom"], "poids": e.get("poids", "—"), "prix": e.get("prix", "—"),
            "description": e.get("description", ""),
            "categorie": "Paquetage" if norm(e["nom"]).startswith("paquetage") else "Équipement"}


def normalize_spell(s: dict, classes: dict[str, list[str]]) -> dict:
    mech = parse_spell_mechanics(s.get("description", ""))
    conc = bool(s.get("concentration"))
    out = {"nom": s["nom"], "niveau": int(s.get("niveau", 0)), "ecole": str(s.get("ecole", "")).capitalize(),
           "temps": s.get("incantation", s.get("temps", "")), "portee": s.get("portee", ""),
           "composantes": s.get("composantes", ""), "concentration": conc, "rituel": bool(s.get("rituel")),
           "duree": "Concentration" if conc else s.get("duree", ""), "description": s.get("description", ""),
           "classes": classes.get(norm(s["nom"]), s.get("classes", []))}
    out.update(mech)
    return out


UNOFFICIAL_NOTE = "Sous-classe non officielle (création de la communauté)."


class Database:
    """Base de données de règles construite à partir des fichiers JSON du dossier `data_dir`."""

    def __init__(self, data_dir: Optional[Path | str] = None, use_fallback: bool = True):
        self.data_dir = Path(data_dir) if data_dir else None
        self.warnings: list[str] = []
        self._editions = None                                       # v52 : catalogue data/editions (à la demande)
        self.skills: list[dict] = []
        self.classes: dict[str, dict] = {}
        self.races: dict[str, dict] = {}
        self.backgrounds: dict[str, dict] = {}
        self.tools: list[dict] = []
        self.spells: dict[str, dict] = {}
        self.weapons: dict[str, dict] = {}
        self.armors: dict[str, dict] = {}
        self.shields: dict[str, dict] = {}
        self.feats: dict[str, dict] = {}
        self.equipment: dict[str, dict] = {}
        self.languages: list[dict] = []
        self.styles_by_class: dict[str, dict[str, str]] = {}   # classe -> {style: description}
        self.armor_models: dict[str, str] = {}                 # modèles d'armure de l'Armurier
        self.manifestations: dict[str, dict] = {}              # manifestations occultes (invocations)
        self.spell_rules: dict[str, dict] = {}                 # Regles_sorts.json : surcouche auditée des sorts
        self.magic_items: dict[str, dict] = {}                 # objets magiques (objets_magiques.json)
        self.beasts: dict[str, dict] = {}                      # bestiaire (monsters_db.json) : formes sauvages
        self.class_actions: list[dict] = []                    # Actions_Classes.json : actions spéciales de classe
        self.entities: dict[str, dict] = {}                    # Familiers_Invocations.json : ménagerie
        self.maneuvers: dict[str, str] = {}                    # manœuvres du Maître de guerre
        self.cunning_actions: list[str] = []
        self.class_passives: dict[str, list[str]] = {}
        self.catalog: dict[str, dict] = {}        # tout ce qui peut aller dans l'inventaire
        self.race_bonus: dict[str, dict] = {}
        self.speeds: dict[str, float] = {}
        self.subraces: dict[str, list[dict]] = {}
        self._starts: dict[str, dict] = {}
        self._raw: dict[str, Any] = {}
        self._scan()
        if use_fallback:
            self._apply_fallback()
        self._build()
        self.edition_stats: dict = {}
        if self.data_dir is not None:                              # v52 : données 2014 / 2024 de data/editions
            from .edition_import import merge
            try:
                self.edition_stats = merge(self)
            except (KeyError, TypeError, ValueError, AttributeError) as exc:      # données abîmées : app utilisable
                self.warnings.append("data/editions non fusionné : {}".format(exc))

    # ------------------------------------------------------------------ lecture des fichiers
    def _scan(self) -> None:
        classes, spell_parts, raw = [], [], {}
        if self.data_dir and self.data_dir.is_dir():
            for path in sorted(self.data_dir.glob("*.json")):
                try:
                    content, warn = read_json(path)
                except (OSError, json.JSONDecodeError) as exc:
                    self.warnings.append(f"{path.name} illisible : {exc}")
                    continue
                if warn:
                    self.warnings.append(warn)
                kind = self._detect(content)
                if kind == "classe":
                    classes.append(content["classe"])
                elif kind == "sorts_part":
                    spell_parts += content[next(k for k in content if k.startswith("sorts_niveau"))]
                elif kind:
                    raw[kind] = content
                else:
                    self.warnings.append(f"{path.name} ignoré (format non reconnu).")
        raw["classes"] = classes
        if spell_parts:
            raw["sorts_part"] = spell_parts
        self._raw = raw

    @staticmethod
    def _detect(content: Any) -> str:
        if isinstance(content, dict):
            for key, kind in (("classe", "classe"), ("especes", "races"), ("outils_dnd_5e", "outils"),
                              ("armes_dnd_5e", "armes"), ("armures_dnd_5e", "armures"),
                              ("equipement_aventurier_dnd_5e", "equipement"), ("listes_de_classes", "sorts_listes"),
                              ("styles_de_combat_et_armures", "styles"), ("manifestations_occultes", "manifestations"),
                              ("objets", "objets_magiques"), ("manoeuvres", "actions_classes"),
                              ("regles_sorts", "regles_sorts")):
                if key in content:
                    return kind
            if any(k.startswith("sorts_niveau") for k in content):
                return "sorts_part"
            if "sous_races" in content or "vitesses" in content:
                return "bonus_raciaux"
        elif isinstance(content, list) and content and isinstance(content[0], dict):
            first = content[0]
            if "description_type" in first and "puissance" in first:
                return "bestiaire"
            if "entity_type" in first and "stats" in first:
                return "entites"                     # Familiers_Invocations.json (familiers, compagnons, invocations)
            for key, kind in (("historique", "historiques"), ("competence", "competences"),
                              ("pv_initiaux", "classes_depart"), ("don", "dons"), ("langue", "langues")):
                if key in first:
                    return kind
        return ""

    def _apply_fallback(self) -> None:
        for key, value in FALLBACK.items():
            if key == "classes":
                if not self._raw.get("classes"):
                    self._raw["classes"] = value
                    self.warnings.append("Aucun fichier de classe : jeu de secours utilisé.")
            elif key not in self._raw:
                self._raw[key] = value
                if key not in ("sorts_listes", "bonus_raciaux"):
                    self.warnings.append(f"Données « {key} » absentes : jeu de secours utilisé.")

    # ------------------------------------------------------------------ construction
    def _build(self) -> None:
        raw = self._raw
        self.skills = [{"nom": s["competence"], "carac": full_ability(s["caracteristique"])} for s in raw["competences"]]
        for item in raw.get("classes_depart", []):
            name = CLASS_ALIASES.get(norm(item["classe"]), item["classe"])
            self._starts[name] = item
        self.classes = {cls["nom"]: cls for cls in raw["classes"]}
        self.races = {r["nom"]: r for r in raw["races"]["especes"]}
        self.backgrounds = {h["historique"]: h for h in raw["historiques"]}
        self.tools = raw["outils"]["outils_dnd_5e"]

        # armes et armures
        self.weapons = {w["nom"]: normalize_weapon(w) for w in raw["armes"]["armes_dnd_5e"]}
        self.weapons.setdefault("Mains nues", dict(UNARMED))
        self.armors = {"Aucune armure": dict(NO_ARMOR)}
        for a in raw["armures"]["armures_dnd_5e"]:
            n = normalize_armor(a)
            (self.shields if n.get("shield") else self.armors)[n["nom"]] = n
        # dons, langues, équipement
        names = {norm(f.get("don") or f.get("nom", "")) for f in raw["dons"]}
        extra = [f for f in EXTRA_FEATS if norm(f["don"]) not in names]          # v45 : dons de maîtrise d'armures
        feats = sorted(map(normalize_feat, list(raw["dons"]) + extra), key=lambda f: (norm(f["nom"]), f["nom"]))
        self.feats = {f["nom"]: f for f in feats}
        self.languages = [{"nom": x["langue"], "categorie": x.get("categorie", ""),
                           "locuteurs": x.get("locuteurs_typiques", "")} for x in raw["langues"]]
        self.equipment = {e["nom"]: normalize_equipment(e) for e in raw["equipement"]["equipement_aventurier_dnd_5e"]}
        key_class = {"paladin": "Paladin", "guerrier": "Guerrier", "rodeur": "Rôdeur", "barde_des_epees": "Barde"}
        block = raw["styles"]["styles_de_combat_et_armures"]
        self.styles_by_class = {key_class[k]: {x["nom"]: x["description"] for x in v}
                                for k, v in block.items() if k in key_class}
        self.armor_models = {x["nom"]: x["description"] for x in block.get("modeles_d_armure", [])}
        self.manifestations = {m["nom"]: normalize_manifestation(m)
                               for m in raw["manifestations"]["manifestations_occultes"]}
        self.magic_items = {x["nom"]: x for x in map(normalize_magic_item, raw["objets_magiques"]["objets"])}
        self.beasts = {b["nom"]: b for b in map(normalize_beast, raw.get("bestiaire", []))}
        # actions et capacités spéciales de classe (Actions_Classes.json) — encart « Actions de classe » du Combat
        acts = raw.get("actions_classes", {})
        self.class_actions = [a for a in acts.get("actions", []) if a.get("id") and a.get("classe")]
        self.entities = {e["id"]: e for e in raw.get("entites", []) if isinstance(e, dict) and e.get("id")}
        self.maneuvers = {m["nom"]: m.get("description", "") for m in acts.get("manoeuvres", [])}
        self.cunning_actions = list(acts.get("ruse", []))
        self.class_passives = {k: list(v) for k, v in acts.get("passifs", {}).items()}
        # sorts : fusion des fichiers Magie-N + listes de classes
        lists = {norm(k): v for k, v in raw["sorts_listes"]["listes_de_classes"].items()}
        self.spells = {s["nom"]: normalize_spell(s, lists) for s in raw["sorts_part"]}
        self.spell_rules = (raw.get("regles_sorts") or {}).get("regles_sorts", {})
        for name, rule in self.spell_rules.items():          # surcouche auditée (data/Regles_sorts.json, v37)
            if name in self.spells:
                apply_spell_rule(self.spells[name], rule)
        for sp in self.spells.values():                     # v40 : effet d'un JS réussi sur les dégâts
            if sp.get("test") in SAVE_TESTS and not sp.get("js_succes"):
                sp["js_succes"] = "aucun" if int(sp.get("niveau") or 0) == 0 else "moitie"
        self._spell_index = {norm(n): n for n in self.spells}
        unlisted = [n for n, s in self.spells.items() if not s["classes"]]
        if unlisted:
            self.warnings.append(f"{len(unlisted)} sort(s) sans liste de classe (visibles via « tous les sorts »).")
        # bonus raciaux
        bonus = raw.get("bonus_raciaux", {})
        self.race_bonus, self.speeds, self.subraces = bonus.get("races", {}), bonus.get("vitesses", {}), \
            bonus.get("sous_races", {})
        if not isinstance(self.subraces, dict):
            self.subraces = {}
        # sous-espèces décrites directement dans Races.json (« sous_races » : Haut-elfe, Elfe des bois…)
        for race in self.races.values():
            subs = []
            for s in race.get("sous_races", []):
                rule = parse_race_bonus(s.get("caracteristiques", ""))
                entry = {"nom": s["nom"], "bonus": rule["fixe"], "capacites": list(s.get("capacites", [])),
                         "langues": list(s.get("langues", [])),
                         "description": " ".join("{} : {}".format(c["nom"], c["description"])
                                                 for c in s.get("capacites", []))}
                if "vitesse" in s:
                    entry["vitesse"] = float(s["vitesse"])
                subs.append(entry)
            if subs:
                self.subraces[race["nom"]] = subs
        self._build_catalog()

    def _build_catalog(self) -> None:
        """Catalogue unifié : équipement, armes, armures, boucliers, outils (pour l'inventaire)."""
        cat: dict[str, dict] = {}
        for e in self.equipment.values():
            cat[e["nom"]] = {"nom": e["nom"], "categorie": e["categorie"], "poids": parse_weight(e["poids"]),
                             "poids_txt": e["poids"], "prix": e["prix"], "description": e["description"]}
        for w in self.weapons.values():
            if w["nom"] == "Mains nues":
                continue
            desc = f"{w['degats']} {w['type_degats']} — {', '.join(w['proprietes']) or 'aucune propriété'}"
            if w["botte"]:
                desc += f" — Botte : {w['botte']}"
            cat[w["nom"]] = {"nom": w["nom"], "categorie": "Arme", "poids": parse_weight(w["poids"]),
                             "poids_txt": w["poids"], "prix": w["prix"], "description": desc}
        for a in list(self.armors.values()) + list(self.shields.values()):
            if a["nom"] == "Aucune armure":
                continue
            ca = f"CA {a['ca_base']}" if "ca_base" in a else f"CA +{a['bonus_ca']}"
            cat[a["nom"]] = {"nom": a["nom"], "categorie": "Bouclier" if a.get("shield") else "Armure",
                             "poids": parse_weight(a["poids"]), "poids_txt": a["poids"], "prix": a["prix"],
                             "description": f"{ca}. {a.get('description', '')}".strip()}
        for t in self.tools:
            cat.setdefault(t["nom"], {"nom": t["nom"], "categorie": "Outil", "poids": parse_weight(t.get("poids", "")),
                                      "poids_txt": t.get("poids", "—"), "prix": t.get("prix", "—"),
                                      "description": t.get("utilisation", "")})
        self.catalog = cat
        self._catalog_index = {norm(n): n for n in cat}

    # ------------------------------------------------------------------ accès pratiques
    @property
    def shield(self) -> dict:
        return next(iter(self.shields.values()), {"nom": "Bouclier", "bonus_ca": 2})

    def view_2024(self):
        """v52 : base vue par une fiche 2024 (classes et sous-classes 2024), construite une seule fois."""
        if getattr(self, "_view_2024", None) is None:
            from .edition_import import EditionView, build_classes_2024
            self._view_2024 = EditionView(self, build_classes_2024(self) if self.data_dir is not None else {})
        return self._view_2024

    @property
    def editions(self):
        """v52 : catalogue des données de référence 2014 / 2024 (`data/editions/`), chargé à la première lecture."""
        if self._editions is None:
            from .editions import EditionCatalog
            self._editions = EditionCatalog((self.data_dir or Path(".")) / "editions")
        return self._editions

    @property
    def skill_names(self) -> list[str]:
        return [s["nom"] for s in self.skills]

    def skill_ability(self, skill: str) -> str:
        return next((s["carac"] for s in self.skills if s["nom"] == skill), "")

    def canonical_skill(self, name: str) -> str:
        """Ramène un nom de compétence (alias inclus) au nom officiel de Compétences.json."""
        n = norm(name)
        if n in SKILL_ALIASES:
            return SKILL_ALIASES[n]
        for s in self.skill_names:
            if norm(s) == n:
                return s
        return name.strip()

    def class_names(self) -> list[str]:
        return sorted(self.classes)

    def start_info(self, class_name: str) -> dict:
        """Infos de départ d'une classe (fusion de Classes_Depart.json et du fichier de la classe)."""
        cls = self.classes.get(class_name, {})
        st = self._starts.get(class_name, {})
        skills_raw = list(st.get("competences_disponibles", []))
        count = CLASS_SKILL_COUNT.get(class_name, 2)
        options: list[str] = []
        if any("toutes" in norm(s) for s in skills_raw):
            options = list(self.skill_names)
            for s in skills_raw:
                digits = [int(c) for c in s if c.isdigit()]
                if digits:
                    count = digits[0]
        else:
            for s in skills_raw + SKILL_FIXES.get(class_name, []):
                cs = self.canonical_skill(s)
                if cs not in options:
                    options.append(cs)
        mastery = cls.get("maitrises")
        if isinstance(mastery, dict):                               # nouveau format (Artificier)
            options = [self.canonical_skill(x) for x in mastery.get("competences_choix", [])] or options
            count = int(mastery.get("competences_nombre", count))
        choice = cls.get("competences_choix")
        if isinstance(choice, dict):
            options = []
            for s in choice.get("options", []):
                cs = self.canonical_skill(s)
                if cs not in options:
                    options.append(cs)
            count = int(choice.get("nombre", count))
        die = cls.get("de_vie") or st.get("de_vie") or "d8"
        saves = cls.get("maitriser_sauvegardes") or st.get("jets_de_sauvegarde") or []
        return {"de_vie": die, "pv_initiaux": int(st.get("pv_initiaux", int(die.replace("d", "")))),
                "competences": options, "nb_competences": count,
                "sauvegardes": [full_ability(s) for s in saves if full_ability(s)],
                "armures": list(cls.get("maitriser_armures") or (mastery or {}).get("armures")
                                or st.get("armures_maitrisees") or []),
                "armes": list(cls.get("maitriser_armes") or (mastery or {}).get("armes")
                              or st.get("armes_maitrisees") or [])}

    def subclasses(self, class_name: str) -> list[dict]:
        return self.classes.get(class_name, {}).get("sous_classes", [])

    @staticmethod
    def is_unofficial(sub: dict) -> bool:
        """v52 : sous-classe non officielle (source « Création de la communauté ») — proposée dans tous les modes."""
        return "communaut" in norm(str(sub.get("source", "")))

    def subclass_tips(self, class_name: str) -> dict[str, str]:
        """Info-bulles discrètes des sous-classes non officielles (menus déroulants)."""
        return {s["nom"]: UNOFFICIAL_NOTE for s in self.subclasses(class_name) if self.is_unofficial(s)}

    def subclass(self, class_name: str, sub_name: str) -> Optional[dict]:
        return next((s for s in self.subclasses(class_name) if s["nom"] == sub_name), None)

    def find_spell(self, name: str) -> Optional[dict]:
        real = self._spell_index.get(norm(name))
        return self.spells.get(real) if real else None

    def find_spell_fuzzy(self, name: str) -> Optional[dict]:
        """
        Recherche tolérante : nom exact, variantes séparées par « / », puis début de nom
        (« Création d'eau » -> « Création ou destruction d'eau », « Brouillard » -> « Nappe de brouillard »).
        """
        candidates = [name] + [p.strip() for p in name.split("/") if p.strip()]
        for c in candidates:
            spell = self.find_spell(c)
            if spell:
                return spell
        for c in candidates:
            n = norm(c)
            if len(n) < 4:
                continue
            words = n.split()
            for key, real in self._spell_index.items():
                if key.startswith(n) or (len(words) > 1 and key.startswith(words[0]) and key.endswith(words[-1])):
                    return self.spells[real]
            for key, real in self._spell_index.items():
                if re.search(r"\b" + re.escape(n) + r"\b", key):
                    return self.spells[real]
        return None

    def spells_for_class(self, class_name: str) -> list[dict]:
        """Bibliothèque de sorts filtrée sur la liste d'une classe."""
        return sorted((s for s in self.spells.values() if class_name in s.get("classes", [])),
                      key=lambda s: (s["niveau"], s["nom"]))

    def all_spells(self) -> list[dict]:
        return sorted(self.spells.values(), key=lambda s: (s["niveau"], s["nom"]))

    def race_names(self) -> list[str]:
        return sorted(self.races)

    def background_names(self) -> list[str]:
        return sorted(self.backgrounds)

    def subraces_of(self, race: str) -> list[dict]:
        return self.subraces.get(race, [])

    def style_names(self) -> list[str]:
        """Tous les styles de combat connus (toutes classes confondues)."""
        return sorted({n for d in self.styles_by_class.values() for n in d})

    def style_description(self, class_name: str, style: str) -> str:
        """Texte complet du style (core/fighting_styles.py), sinon celui du fichier ; modèles d'armure de l'Armurier."""
        from .fighting_styles import style_text
        data = self.styles_by_class.get(class_name, {}).get(style, "") or self.armor_models.get(style, "")
        return style_text(style, data)

    def race_ability_rule(self, race: str) -> Optional[dict]:
        """Règle de bonus de caractéristiques d'une race (lue dans Races.json, sinon dans Bonus_Raciaux.json)."""
        text = self.races.get(race, {}).get("caracteristiques")
        if text:
            return parse_race_bonus(text)
        old = self.race_bonus.get(race)
        return {"fixe": dict(old.get("fixe", {})), "libres": list(old.get("libres", [])), "alternative": []} \
            if old else None

    def race_languages(self, race: str) -> list[str]:
        return list(self.races.get(race, {}).get("langues", []))

    def language_names(self) -> list[str]:
        return [x["nom"] for x in self.languages]

    # ------------------------------------------------------------------ équipement : croisement des listes
    def match_item(self, text: str) -> tuple[int, str, bool]:
        """
        Associe un texte libre (« 2 flasques d'huile », « sac de couchage ») à un objet du catalogue.
        Retourne (quantité, nom, trouvé_dans_le_catalogue).
        """
        t = norm(text).strip(" .;")
        qty = 1
        m = re.match(r"(\d+)\s+(.*)", t)
        if m:
            qty, t = int(m.group(1)), m.group(2)
        else:
            t = re.sub(r"^(un|une|des|le|la|les|l')\s*", "", t)
        t = re.sub(r"^(flasques?\s+d'|jours?\s+de\s+|feuilles?\s+de\s+)", "", t)
        if t.startswith("etuis"):
            t = "etui a cartes ou a parchemins"
        index = self._catalog_index

        def stem(s: str) -> str:
            return re.sub(r"s\b", "", s)

        if t in index:
            return qty, index[t], True
        best = ""
        for key in index:
            if stem(key) == stem(t) or key.startswith(t) or (len(key) > 4 and t.startswith(key)):
                if len(key) > len(best):
                    best = key
        if best and len(t) >= 3:
            return qty, index[best], True
        clean = re.sub(r"^\s*\d+\s+", "", text).strip().strip(".")
        return qty, clean[:1].upper() + clean[1:], False

    def parse_item_list(self, text: str) -> list[tuple[int, str, bool]]:
        """'Contient sac à dos, 2 flasques d'huile et corde.' -> liste d'objets (quantité, nom, connu)."""
        body = re.sub(r"^\s*contient\s+", "", text or "", flags=re.I)
        parts: list[str] = []
        for chunk in split_top_level(body):
            parts += re.split(r"\s+et\s+", chunk) if "," not in chunk else [chunk]
        return [self.match_item(p) for p in parts if p.strip(" .")]

    def pack_contents(self, pack_name: str) -> list[tuple[int, str, bool]]:
        e = self.equipment.get(pack_name)
        return self.parse_item_list(e["description"]) if e else []
