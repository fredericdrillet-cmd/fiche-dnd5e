"""
Modèle de données d'un personnage (état modifiable par l'utilisateur) + sauvegarde / chargement JSON.

Ce module ne contient AUCUN calcul de règles : les valeurs dérivées (modificateurs, PV, CA,
bonus de compétences...) sont calculées à la demande par `core.engine.Engine`.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .rules import ABILITIES

SAVE_FORMAT_VERSION = 1


def _default_scores(value: int) -> dict[str, int]:
    return {ab: value for ab in ABILITIES}


def _empty_weapon() -> dict:
    return {"nom": "", "bonus": 0, "maitrise": None}  # maitrise None = détection automatique


@dataclass
class Character:
    # ---- Identité -------------------------------------------------------------------
    nom: str = ""
    joueur: str = ""
    alignement: str = "Neutre"
    experience: int = 0
    # Liste de classes : {"nom", "niveau", "sous_classe", "pv_jets": [int, ...]}
    classes: list[dict] = field(default_factory=lambda: [])
    multiclassage: bool = False            # option « Multiclassage » : superposition de classes autorisée

    # ---- Race / historique ------------------------------------------------------------
    race: str = ""
    sous_race: str = ""
    race_acquis: dict = field(default_factory=lambda: {"langues": [], "langues_texte": [], "competences": []})
    # ce que la race a réellement ajouté (langues, compétences) : retiré proprement si l'on change de race
    historique: str = ""
    regle_libre: bool = False              # force la règle « +2/+1 au choix » (Tasha)
    bonus_libres: list[str] = field(default_factory=list)   # caractéristiques choisies (ordre des bonus libres)
    bonus_alt: bool = False                # variante « +1, +1, +1 » des races à bonus libres

    # ---- Caractéristiques -------------------------------------------------------------
    methode: str = "achat"                 # "achat" | "des" | "manuel"
    scores_achat: dict[str, int] = field(default_factory=lambda: _default_scores(8))
    scores_manuel: dict[str, int] = field(default_factory=lambda: _default_scores(10))
    des_tirages: list[dict] = field(default_factory=list)   # [{"total": 14, "des": [6,5,3,1]}, ...]
    des_affectation: dict[str, int] = field(default_factory=lambda: {ab: -1 for ab in ABILITIES})
    bonus_divers: dict[str, int] = field(default_factory=lambda: _default_scores(0))
    # Choix d'amélioration de caractéristiques : identifiant d'emplacement -> choix
    # {"mode": "aucun|plus2|plus1x2|don", "a1": str, "a2": str, "don": str, "don_carac": str}
    ameliorations: dict[str, dict] = field(default_factory=dict)
    dons_mj: list[str] = field(default_factory=list)       # dons accordés par le MJ (hors progression)
    # ménagerie active : [{uid, id, nom, pv, pv_temp, statut, niveau_sort, auto}]
    menagerie: list[dict] = field(default_factory=list)

    # ---- Compétences / sauvegardes ----------------------------------------------------
    competences: dict[str, dict] = field(default_factory=dict)       # nom -> {"maitrise": bool, "expertise": bool}
    competences_historique: list[str] = field(default_factory=list)  # compétences accordées par l'historique
    sauvegardes: dict[str, bool] = field(default_factory=lambda: {ab: False for ab in ABILITIES})
    outils: list[str] = field(default_factory=list)
    langues: str = ""                                               # autres langues (texte libre)
    langues_liste: list[str] = field(default_factory=lambda: ["Commun"])  # langues de Langues.json

    # ---- Combat -----------------------------------------------------------------------
    pv_mode: str = "moyenne"               # "moyenne" | "jets"
    pv_divers: int = 0
    pv_actuels: int = -1                   # -1 = pleins PV (initialisé par le moteur)
    pv_temporaires: int = 0
    mort_reussites: int = 0
    mort_echecs: int = 0
    des_vie_utilises: dict[str, int] = field(default_factory=dict)
    armure: dict = field(default_factory=lambda: {"nom": "Aucune armure", "bonus": 0, "bouclier": False,
                                                  "bouclier_nom": "", "bonus_bouclier": 0})
    armes_cac: list[dict] = field(default_factory=lambda: [_empty_weapon() for _ in range(4)])
    armes_distance: list[dict] = field(default_factory=lambda: [_empty_weapon() for _ in range(4)])
    sorts_mineurs: list[dict] = field(default_factory=lambda: [{"nom": ""} for _ in range(4)])

    styles_combat: dict[str, str] = field(default_factory=dict)   # emplacement de style -> nom du style

    # ---- Roleplay -----------------------------------------------------------------------
    histoire: str = ""                      # histoire du personnage (backstory)
    sac_sans_fond: bool = False             # « Possède un Sac sans fond » : la limite de charge est ignorée
    forme_active: str = ""                  # Druide : bête dont la forme sauvage est actuellement adoptée
    forme_pv: int = 0                       # PV actuels de la bête (tampon : les PV du druide restent intacts)
    forme_type: str = ""                    # "sauvage" (Forme sauvage du druide) | "metamorphose" (sort Métamorphose)
    portrait: str = ""                      # image du portrait encodée en base64 (PNG), incluse dans la sauvegarde

    # ---- État de jeu (combat, temps, repos) ---------------------------------------------
    effets_actifs: list[str] = field(default_factory=list)      # clés de core/effects.py (buffs, débuffs, états)
    effets_retires: list[str] = field(default_factory=list)     # traits innés (race / classe) retirés volontairement
    effets_potions: list[str] = field(default_factory=list)     # effets venus d'un consommable (expirent au repos)
    concentration: str = ""                 # sort dont la concentration est en cours
    concentration_cible: str = ""           # "soi" | "allie" : destinataire du sort de concentration
    concentration_effet: str = ""           # effet appliqué sur soi par ce sort (retiré quand la concentration cesse)
    ascendance_raciale: str = ""            # Drakéide / Demi-dragon : couleur du dragon ancestral
    ascendance_ensorceleur: str = ""        # Ensorceleur (Lignée draconique) : dragon ancestral
    sorts_mj: list[dict] = field(default_factory=list)   # sorts accordés par le MJ : [{nom, usage, note}]
    reaction_utilisee: str = ""             # réaction dépensée ce round ("" = disponible)
    tour_action: bool = False               # v30 — suivi du tour : action dépensée
    tour_bonus: bool = False                # action bonus dépensée
    tour_attaques: int = 0                  # attaques faites dans l'action Attaquer (Attaque supplémentaire)
    tour_utilises: list[str] = field(default_factory=list)   # v39 : capacités « 1 fois par tour » déjà utilisées
    tour_deplacement: float = 0.0           # mètres parcourus ce tour
    modes_reactions: dict[str, str] = field(default_factory=dict)   # clé de réaction -> "auto" | "off"
    options_classe: dict[str, list] = field(default_factory=dict)   # v36 — runes, options de Tir arcanique…
    technique_manoeuvre: str = ""           # v35 — style « Technique supérieure » : manœuvre apprise
    jeu_armes: str = "melee"                # v31, sans effet depuis v34 (gardé pour les anciennes sauvegardes)
    temps_minutes: int = 0                  # temps de jeu écoulé depuis le jour 1, 8 h 00
    dernier_repos_long: int = -1            # instant (minutes) du dernier repos long, -1 = jamais
    initiative_jet: int = 0                 # v45 : dernier jet d'initiative (0 = aucun)

    # ---- Magie ------------------------------------------------------------------------
    pacte: str = ""                         # Pacte divin de l'Occultiste (lame / chaîne / grimoire / talisman)
    manifestations: list[str] = field(default_factory=list)   # manifestations occultes choisies
    sorts_raciaux: dict[str, str] = field(default_factory=dict)   # v48 : trait racial -> sort mineur choisi
    rituels_livre: list[str] = field(default_factory=list)    # v37 — Livre des secrets anciens : rituels inscrits
    sorts: dict[str, list[dict]] = field(default_factory=dict)   # classe -> [{"nom", "prepare"}]
    emplacements_utilises: list[int] = field(default_factory=lambda: [0] * 9)
    pacte_utilises: int = 0

    # ---- Ressources de classe et objets magiques -------------------------------------
    ressources_utilisees: dict[str, int] = field(default_factory=dict)    # rage / ki / sorcellerie : nombre dépensé
    objets_magiques: list[dict] = field(default_factory=list)             # [{"nom", "bonus", "equipe", "harmonise"}]
    objets_perso: dict[str, dict] = field(default_factory=dict)          # v33 : objets magiques sur mesure (fiche complète)

    # ---- Divers -----------------------------------------------------------------------
    equipement: list[dict] = field(default_factory=list)          # [{"nom": str, "qte": int}]
    inventaire: str = ""                                          # notes libres d'équipement
    pieces: dict[str, int] = field(default_factory=lambda: {"po": 0, "pa": 0, "pc": 0})
    traits: str = ""
    notes: str = ""

    # ------------------------------------------------------------------ propriétés simples
    @property
    def niveau_total(self) -> int:
        return sum(c["niveau"] for c in self.classes)

    def find_class(self, name: str) -> dict | None:
        return next((c for c in self.classes if c["nom"] == name), None)

    # ------------------------------------------------------------------ sérialisation
    def to_dict(self) -> dict[str, Any]:
        data = copy.deepcopy(self.__dict__)
        data["_version"] = SAVE_FORMAT_VERSION
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Character":
        """Reconstruit un personnage ; les clés inconnues sont ignorées, les manquantes prennent le défaut."""
        char = cls()
        for key, default in char.__dict__.items():
            if key in data:
                value = copy.deepcopy(data[key])
                if isinstance(default, dict) and isinstance(value, dict):
                    merged = copy.deepcopy(default)
                    merged.update(value)
                    value = merged
                setattr(char, key, value)
        if "multiclassage" not in data:                 # anciennes sauvegardes : déjà multiclassé = option active
            char.multiclassage = len(char.classes) > 1
        # Garanties de structure
        while len(char.armes_cac) < 4:
            char.armes_cac.append(_empty_weapon())
        while len(char.armes_distance) < 4:
            char.armes_distance.append(_empty_weapon())
        while len(char.sorts_mineurs) < 4:
            char.sorts_mineurs.append({"nom": ""})
        char.emplacements_utilises = (list(char.emplacements_utilises) + [0] * 9)[:9]
        for c in char.classes:
            c.setdefault("sous_classe", "")
            c.setdefault("pv_jets", [])
            c["niveau"] = max(1, min(20, int(c.get("niveau", 1))))
        return char

    def save(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "Character":
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict) or "classes" not in data:
            raise ValueError("Ce fichier n'est pas une sauvegarde de personnage valide.")
        return cls.from_dict(data)
