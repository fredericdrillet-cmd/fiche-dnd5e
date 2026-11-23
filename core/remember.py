"""
Encart « 📌 À ne pas oublier » (v52) — capacités de situation que la fiche ne peut pas calculer seule.

Une ligne par capacité, rangée par moment (avant d'attaquer, quand vous touchez, en défense, pour vos alliés,
déplacement, hors combat). Les capacités déjà appliquées automatiquement (Sens du danger, Talent fiable, Évasion
dans les JS…) ou proposées au bon moment (réactions, « quand vous touchez ») n'y figurent pas.
Chaque entrée : (fragments de nom d'aptitude / trait / don, moment, texte, édition : None = les deux).
"""
from __future__ import annotations

import re

from .rules import norm

MOMENTS = ["Avant d'attaquer", "Quand vous touchez", "En défense", "Pour vos alliés", "Déplacement", "Hors combat"]

ENTRIES = [
    # --- avant d'attaquer
    (("attaque temeraire",), "Avant d'attaquer", "Attaque téméraire : avant votre première attaque, avantage à vos "
     "attaques de Force ce tour-ci ; les attaques contre vous ont l'avantage jusqu'à votre prochain tour.", None),
    (("visee stable",), "Avant d'attaquer", "Visée stable : action bonus, sans vous être déplacé : avantage à votre "
     "prochaine attaque ce tour-ci (votre vitesse tombe à 0).", None),
    (("attaque alimentee par le ki",), "Avant d'attaquer", "Attaque alimentée par le ki : si votre action a dépensé "
     "du ki, une attaque à mains nues ou d'arme de moine par une action bonus.", 2014),
    (("bond instinctif",), "Déplacement", "Bond instinctif : en entrant en rage, déplacez-vous jusqu'à la moitié de "
     "votre vitesse.", 2014),
    (("inspiration magique",), "Pour vos alliés", "Inspiration magique : un allié qui a votre dé d'inspiration peut "
     "l'ajouter aux dégâts ou aux soins d'un sort.", 2014),
    (("polyvalence", "versatilite magique", "sorts mineurs polyvalents"), "Hors combat", "Polyvalence (Tasha) : à "
     "chaque niveau d'amélioration de caractéristique, vous pouvez échanger un style de combat, un sort mineur, "
     "une option de Métamagie ou un sort connu.", 2014),
    (("formules de sorts mineurs",), "Hors combat", "Formules de sorts mineurs : après un repos long, échangez un "
     "tour de magie de magicien.", 2014),
    (("focaliseur d'incantation",), "Hors combat", "Focaliseur d'incantation : un focaliseur druidique remplace les "
     "composantes matérielles de vos sorts de rôdeur.", 2014),
    (("attaque sournoise",), "Avant d'attaquer", "Attaque sournoise : cherchez l'avantage ou un allié à 1,50 m de la "
     "cible, avec une arme de finesse ou à distance (une fois par tour).", None),
    (("frappe brutale",), "Avant d'attaquer", "Frappe brutale : avec Attaque téméraire, renoncez à l'avantage sur une "
     "attaque pour +1d10 dégâts et un effet (repousser, ralentir…).", 2024),
    (("attaque supplementaire",), "Avant d'attaquer", "Attaque supplémentaire : l'action Attaquer vous donne plusieurs "
     "attaques — la tuile d'arme compte « attaque 1 / 2 ».", None),
    # --- quand vous touchez
    (("frappe etourdissante", "coup etourdissant"), "Quand vous touchez", "Frappe étourdissante : quand une attaque "
     "de corps à corps touche, 1 point de ki : JS de Constitution ou la cible est étourdie.", None),
    (("frappe rusee",), "Quand vous touchez", "Frappe rusée : en infligeant l'Attaque sournoise, retirez des d6 pour "
     "empoisonner, faire tomber ou vous replier (tuiles « Frappe malicieuse »).", 2024),
    (("critique brutal",), "Quand vous touchez", "Critique brutal : sur un coup critique au corps à corps, ajoutez un "
     "dé de dégâts de l'arme de plus.", 2014),
    # --- en défense
    (("rage implacable",), "En défense", "Rage implacable : tombé à 0 PV en rage, JS de Constitution DD 10 (+5 par "
     "nouvelle utilisation) pour rester à 1 PV.", 2014),
    (("rage implacable",), "En défense", "Rage implacable : tombé à 0 PV en rage, JS de Constitution DD 10 (+5 par "
     "nouvelle utilisation) : vos PV reviennent à deux fois votre niveau de barbare.", 2024),
    (("race:endurance implacable",), "En défense", "Endurance implacable : une fois par repos long, réduit à 0 PV sans être "
     "tué, vous restez à 1 PV.", None),
    (("race:chanceux",), "En défense", "Chanceux (halfelin) : sur un 1 au d20 d'une attaque, d'un test ou d'un JS, relancez "
     "le dé.", None),
    (("race:brave",), "En défense", "Brave : avantage aux JS contre l'état effrayé.", None),
    # v53 : traits des races importées (marques draconiques, Wildemount, Fizban, Côte des Épées)
    (("race:agilite halfeline",), "Déplacement", "Agilité halfeline : vous traversez l'espace de toute créature plus "
     "grande que vous.", None),
    (("race:marche sylvestre",), "Déplacement", "Marche sylvestre : désavantage aux tests pour vous pister ; la "
     "végétation non magique n'est pas un terrain difficile pour vous.", None),
    (("race:presence imposante",), "Hors combat", "Présence imposante : une fois par repos court ou long, avantage à "
     "un test de Persuasion ou d'Intimidation.", None),
    (("race:esprit psionique", "race:discours silencieux"), "Hors combat", "Télépathie raciale : vous parlez par "
     "télépathie à une créature à 9 m ou moins (elle doit comprendre une langue que vous parlez).", None),
    (("race:plus ils sont grands",), "Hors combat", "Plus ils sont grands : dès le niveau 3, Amitié avec les animaux "
     "et Communication avec les animaux ciblent aussi une bête ou une monstruosité d'Intelligence 3 ou plus.", None),
    (("race:sorts de la marque",), "Hors combat", "Sorts de la Marque : si vous lancez des sorts, ceux de votre "
     "marque s'ajoutent à la liste de votre classe (déjà proposés dans l'onglet Magie).", None),
    (("race:resistance naine",), "En défense", "Résistance naine : avantage aux JS contre le poison.", None),
    (("race:ascendance feerique",), "En défense", "Ascendance féerique : avantage aux JS contre l'état charmé ; la magie ne "
     "peut pas vous endormir.", None),
    (("race:ruse gnome",), "En défense", "Ruse gnome : avantage aux JS d'Intelligence, de Sagesse et de Charisme (contre "
     "la magie en 2014).", None),
    (("perception aveugle",), "En défense", "Perception aveugle : vous percevez les créatures cachées ou invisibles "
     "à 3 m.", 2014),
    # --- pour vos alliés
    (("aura de protection",), "Pour vos alliés", "Aura de protection : vos alliés à 3 m (9 m au niveau 18) ajoutent "
     "votre modificateur de Charisme à leurs JS.", None),
    (("aura de courage",), "Pour vos alliés", "Aura de courage : vos alliés dans l'aura ne peuvent pas être effrayés.",
     None),
    (("aura de devotion",), "Pour vos alliés", "Aura de dévotion : vos alliés dans l'aura ne peuvent pas être "
     "charmés.", None),
    (("inspiration bardique",), "Pour vos alliés", "Inspiration bardique : action bonus, un allié qui vous entend "
     "gagne un dé à ajouter à un jet.", None),
    # --- déplacement
    (("action rusee", "=ruse"), "Déplacement", "Action rusée : action bonus pour Foncer, Se désengager ou Se cacher.",
     None),
    (("pas du vent",), "Déplacement", "Pas du vent : Se désengager ou Foncer par une action bonus (1 point de ki ; "
     "gratuit en 2024 pour Foncer), saut doublé.", None),
    # --- hors combat
    (("adepte des rituels", "incantation rituelle"), "Hors combat", "Rituels : un sort avec l'étiquette rituel se lance "
     "en 10 minutes de plus, sans emplacement.", None),
    (("sens divin",), "Hors combat", "Sens divin : détectez célestes, fiélons et morts-vivants à 18 m.", None),
]


class RememberMixin:
    """Mélangé à Engine."""

    def remember_list(self) -> dict[str, list[str]]:
        names = [norm(f["nom"]) for e in self.ch.classes for f in self.features(e)
                 if f.get("debloque") and self.feature_allowed(f["nom"])]
        names += [norm(n) for n in self.chosen_feats()]
        race = [norm(c.get("nom", "")) for c in self.race_capacities()]

        def match(f: str) -> bool:
            if f.startswith("race:"):
                return any(n == f[5:] or n.startswith(f[5:] + " ") for n in race)
            if f.startswith("="):
                return f[1:] in names
            return any(n == f or n.startswith(f + " ") for n in names)
        out: dict[str, list[str]] = {m: [] for m in MOMENTS}
        for frags, moment, text, ed in ENTRIES:
            if ed and ed != self.sheet_edition:
                continue
            if any(match(f) for f in frags):
                out[moment].append(text)
        for name in self.chosen_feats():                # v53 : dons du MJ situationnels -> rappel lisible
            f = self.db.feats.get(name) or {}
            if not f.get("mj_seulement"):
                continue
            spec = self._gm_spec(name, f) if hasattr(self, "_gm_spec") else {}
            text = (f.get("description") or "").replace("\n", " ")
            sentences = [x.strip() for x in re.split(r"(?<=[.!])\s+", text) if x.strip()]
            first = next((x for x in sentences if re.search(r"avantage|resistance|immunis|pouvez|bonus|gagnez|vous etes",
                                                             norm(x))), sentences[0] if sentences else "")[:240].rstrip(".")
            done = any(spec.get(k) for k in ("pv_max", "vitesse", "sorts", "pouvoir", "competences_toutes",
                                              "vision_veritable", "champion"))
            mods = spec.get("mods") or {}
            if not done and not spec.get("emplacement_9") and not (
                    mods.get("ca") or mods.get("carac") or mods.get("resistances") or mods.get("immunites") or
                    mods.get("competences")):
                low = norm(text)
                moment = "En défense" if re.search(r"jets? de sauvegarde|degats|empoign|entrav", low) else \
                    "Avant d'attaquer" if "attaque" in low else "Déplacement" if "vitesse" in low else "Hors combat"
                out[moment].append("{} : {}.".format(name, first))
            elif spec.get("note_js"):
                out["En défense"].append("{} : {}.".format(name, spec["note_js"]))
        if self.mastery_count():
            out["Quand vous touchez"].append("Bottes d'arme : chaque attaque avec une arme dont vous maîtrisez la "
                                             "botte applique son effet (Sape, Ouverture, Poussée…).")
        return {m: v for m, v in out.items() if v}
