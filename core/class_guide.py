"""
Guide pédagogique des classes et sous-classes (v49, inspiré de Baldur's Gate 3) — données et logique pure.

- CLASS_GUIDE : concept, style de jeu, mécaniques clés et caractéristiques recommandées de chaque classe ;
- SUBCLASS_ABILITIES : caractéristiques secondaires ajoutées par certaines sous-classes (Arnaqueur arcanique :
  Intelligence pour ses sorts, Chevalier occulte : Intelligence, Bretteur : Charisme…) ;
- subclass_summary() : résumé d'une sous-classe tiré des données (niveau de déblocage, pouvoirs principaux par
  niveau, orientation de gameplay déduite des textes).
"""
from __future__ import annotations

import re
from typing import Optional

from . import rules as R
from .rules import norm

P, S = "principale", "secondaire"

CLASS_GUIDE = {
    "Barbare": {
        "concept": "Guerrier des terres sauvages porté par une fureur primale : il encaisse et frappe plus fort que "
                   "quiconque au corps à corps.",
        "style": "Première ligne, attaques puissantes, très résistant.",
        "mecaniques": ["Rage : bonus aux dégâts de Force, résistance aux dégâts contondants, perforants et "
                       "tranchants", "Défense sans armure (10 + Dex + Con)", "Attaque téméraire (avantage contre "
                       "avantage adverse)", "Attaque supplémentaire au niveau 5"],
        "carac": {"Force": (P, "La Force augmente vos jets d'attaque et de dégâts au corps à corps, et le bonus de "
                                "Rage ne s'applique qu'aux attaques de Force."),
                  "Constitution": (S, "La Constitution augmente vos points de vie et votre CA (Défense sans "
                                      "armure).")}},
    "Barde": {
        "concept": "Artiste et érudit dont la musique et les mots tissent la magie : soutien, contrôle et "
                   "polyvalence.",
        "style": "Soutien et contrôle, touche-à-tout social.",
        "mecaniques": ["Inspiration bardique : dé bonus offert aux alliés", "Incantation (Charisme), sorts connus",
                       "Touche-à-tout et Expertise", "Secrets magiques : sorts d'autres classes"],
        "carac": {"Charisme": (P, "Le Charisme fixe le DD et l'attaque de vos sorts et le nombre d'Inspirations "
                                  "bardiques."),
                  "Dextérité": (S, "La Dextérité améliore votre CA en armure légère, votre initiative et vos "
                                   "attaques à la rapière ou à l'arc.")}},
    "Clerc": {
        "concept": "Intermédiaire entre les dieux et les mortels : soigneur, protecteur et pourfendeur selon son "
                   "domaine divin.",
        "style": "Soutien et soins, très bonne défense, magie divine variée.",
        "mecaniques": ["Domaine divin dès le niveau 1 (sorts de domaine toujours préparés)", "Conduit divin "
                       "(Renvoi des morts-vivants…)", "Préparation quotidienne dans toute la liste du clerc"],
        "carac": {"Sagesse": (P, "La Sagesse fixe le DD et l'attaque de vos sorts et le nombre de sorts préparés."),
                  "Constitution": (S, "La Constitution augmente vos PV et vos jets de sauvegarde de "
                                      "concentration.")}},
    "Druide": {
        "concept": "Gardien de la nature qui puise dans ses forces primordiales et peut adopter la forme des bêtes.",
        "style": "Contrôle de zone, soutien, métamorphose.",
        "mecaniques": ["Forme sauvage (niveau 2)", "Incantation (Sagesse), préparation quotidienne",
                       "Cercle druidique (niveau 2)"],
        "carac": {"Sagesse": (P, "La Sagesse fixe le DD et l'attaque de vos sorts et le nombre de sorts préparés."),
                  "Constitution": (S, "La Constitution augmente vos PV et protège votre concentration.")}},
    "Ensorceleur": {
        "concept": "Lanceur de sorts dont la magie est innée (lignée, don, accident) et qu'il plie à sa volonté.",
        "style": "Dégâts magiques à distance, sorts modelés par la métamagie.",
        "mecaniques": ["Origine magique dès le niveau 1", "Points de sorcellerie (niveau 2)",
                       "Métamagie : sorts prolongés, jumeaux, accélérés… (niveau 3)", "Sorts connus (Charisme)"],
        "carac": {"Charisme": (P, "Le Charisme fixe le DD et l'attaque de vos sorts."),
                  "Constitution": (S, "La Constitution augmente vos PV (dé de vie d6) et protège votre "
                                      "concentration.")}},
    "Guerrier": {
        "concept": "Maître des armes et des armures, discipliné et endurant, qui s'adapte à tous les combats.",
        "style": "Combat soutenu, nombreuses attaques, très polyvalent.",
        "mecaniques": ["Style de combat (niveau 1)", "Second souffle", "Fougue : une action supplémentaire "
                       "(niveau 2)", "Attaques supplémentaires (niveaux 5, 11, 20)", "Archétype martial (niveau 3)"],
        "carac": {"Force": (P, "Force OU Dextérité selon votre style : la Force pour les armes lourdes et "
                               "l'armure lourde."),
                  "Dextérité": (P, "Force OU Dextérité selon votre style : la Dextérité pour l'arc, les armes de "
                                   "finesse et l'armure légère."),
                  "Constitution": (S, "La Constitution augmente vos points de vie et votre endurance en première ligne.")}},
    "Magicien": {
        "concept": "Érudit des arcanes qui apprend ses sorts dans un grimoire : la plus grande bibliothèque de "
                   "magie du jeu.",
        "style": "Contrôle, utilitaire et dégâts de zone, à protéger en combat.",
        "mecaniques": ["Grimoire : sorts inscrits puis préparés chaque jour", "Restauration arcanique "
                       "(emplacements récupérés au repos court)", "Tradition arcanique (niveau 2)",
                       "Rituels depuis le grimoire"],
        "carac": {"Intelligence": (P, "L'Intelligence fixe le DD et l'attaque de vos sorts et le nombre de sorts "
                                      "préparés."),
                  "Constitution": (S, "La Constitution augmente vos PV (dé de vie d6) et protège votre "
                                      "concentration."),
                  "Dextérité": (S, "La Dextérité améliore votre CA et votre initiative sans armure.")}},
    "Moine": {
        "concept": "Artiste martial qui canalise son ki : vitesse, frappes multiples et techniques surnaturelles.",
        "style": "Mobile, frappes à mains nues rapides, contrôle (Frappe étourdissante).",
        "mecaniques": ["Arts martiaux et Défense sans armure (10 + Dex + Sag)", "Ki : Déluge de coups, Pas du vent, "
                       "Patience", "Déplacement sans armure", "Tradition monastique (niveau 3)"],
        "carac": {"Dextérité": (P, "La Dextérité augmente vos attaques, vos dégâts et votre CA."),
                  "Sagesse": (S, "La Sagesse augmente votre CA (Défense sans armure) et le DD de vos techniques "
                                 "de ki.")}},
    "Paladin": {
        "concept": "Guerrier saint lié par un serment : armure lourde, châtiments dévastateurs et aura protectrice.",
        "style": "Première ligne, gros dégâts ponctuels (Châtiment divin), soutien.",
        "mecaniques": ["Imposition des mains", "Châtiment divin (niveau 2)", "Serment sacré (niveau 3)",
                       "Aura de protection (niveau 6)"],
        "carac": {"Force": (P, "La Force augmente vos attaques et dégâts au corps à corps et permet l'armure "
                               "lourde."),
                  "Charisme": (S, "Le Charisme fixe le DD de vos sorts et votre Aura de protection (bonus à tous "
                                  "les jets de sauvegarde).")}},
    "Rôdeur": {
        "concept": "Chasseur et éclaireur des terres sauvages, archer ou bretteur, qui traque ses proies.",
        "style": "Attaques à distance ou à deux armes, exploration, un peu de magie.",
        "mecaniques": ["Ennemi juré et Explorateur-né", "Style de combat et Incantation (niveau 2)",
                       "Archétype de rôdeur (niveau 3)", "Attaque supplémentaire (niveau 5)"],
        "carac": {"Dextérité": (P, "La Dextérité augmente vos attaques à l'arc et aux armes de finesse, et votre "
                                   "CA."),
                  "Sagesse": (S, "La Sagesse fixe le DD et l'attaque de vos sorts.")}},
    "Roublard": {
        "concept": "Spécialiste de la discrétion et de la précision : il frappe là où ça fait mal et maîtrise de "
                   "nombreuses compétences.",
        "style": "Frappes uniques et précises, discrétion, compétences.",
        "mecaniques": ["Attaque sournoise", "Expertise", "Ruse : Foncer, Se désengager, Se cacher par une action "
                       "bonus (niveau 2)", "Archétype de roublard (niveau 3)", "Esquive instinctive (niveau 5)"],
        "carac": {"Dextérité": (P, "La Dextérité augmente vos attaques et dégâts (armes de finesse, arc), votre "
                                   "CA, votre initiative et vos compétences de roublard."),
                  "Constitution": (S, "La Constitution augmente vos points de vie.")}},
    "Occultiste": {
        "concept": "Lanceur de sorts lié à un protecteur surnaturel par un pacte : peu d'emplacements, mais "
                   "récupérés à chaque repos court.",
        "style": "Dégâts constants (Décharge occulte), magie personnalisée par les manifestations.",
        "mecaniques": ["Protecteur d'outre-monde dès le niveau 1", "Magie des pactes : emplacements de niveau "
                       "maximal, récupérés au repos court", "Manifestations occultes (niveau 2)",
                       "Faveur de pacte (niveau 3)"],
        "carac": {"Charisme": (P, "Le Charisme fixe le DD et l'attaque de vos sorts et améliore Décharge occulte "
                                  "(Décharge déchirante)."),
                  "Constitution": (S, "La Constitution augmente vos PV et protège votre concentration.")}},
    "Artificier": {
        "concept": "Inventeur qui insuffle la magie dans les objets : infusions, gadgets et soutien technique.",
        "style": "Soutien, défense, objets magiques améliorés.",
        "mecaniques": ["Bricolage magique", "Infusions (niveau 2)", "Spécialisation (niveau 3)",
                       "Préparation quotidienne (Intelligence)"],
        "carac": {"Intelligence": (P, "L'Intelligence fixe le DD et l'attaque de vos sorts."),
                  "Constitution": (S, "La Constitution augmente vos PV et protège votre concentration.")}},
}

# (classe, fragment normalisé de sous-classe) -> {caractéristique: (rôle, raison)}
SUBCLASS_ABILITIES = [
    ("Roublard", "arnaqueur", {"Intelligence": (S, "L'Intelligence augmente le Degré de Difficulté (DD) des jets "
                                                   "de sauvegarde et le bonus d'attaque de vos sorts d'Arnaqueur "
                                                   "arcanique.")}),
    ("Roublard", "escroc", {"Intelligence": (S, "L'Intelligence augmente le DD et l'attaque de vos sorts d'Escroc "
                                                "arcanique.")}),
    ("Roublard", "bretteur", {"Charisme": (S, "Audace désinvolte ajoute votre Charisme à l'initiative et à vos "
                                              "attaques sournoises en duel.")}),
    ("Roublard", "lame psychique", {"Intelligence": (S, "L'Intelligence fixe le DD de vos pouvoirs psioniques.")}),
    ("Roublard", "enqueteur", {"Sagesse": (S, "Œil infaillible et Perspicacité reposent sur la Sagesse.")}),
    ("Guerrier", "chevalier occulte", {"Intelligence": (S, "L'Intelligence augmente le DD et l'attaque de vos "
                                                           "sorts de Chevalier occulte.")}),
    ("Guerrier", "guerrier psi", {"Intelligence": (S, "L'Intelligence fixe le DD de vos pouvoirs psioniques.")}),
    ("Guerrier", "chevalier runique", {"Constitution": (S, "La Constitution fixe le DD de vos runes.")}),
    ("Barde", "vaillance", {"Dextérité": (S, "Armes de guerre et armure intermédiaire : la Dextérité (ou la "
                                            "Force) compte pour vos attaques.")}),
    ("Barde", "epees", {"Dextérité": (S, "Vos fioritures de lame utilisent des armes de finesse : la Dextérité "
                                        "augmente attaques et dégâts.")}),
    ("Magicien", "chantelame", {"Dextérité": (S, "Chant de la lame : attaques à l'épée de finesse et CA en armure "
                                                "légère reposent sur la Dextérité.")}),
    ("Occultiste", "lame maudite", {"Charisme": (P, "Guerrier du maléfice : vous attaquez avec votre Charisme au "
                                                   "lieu de la Force ou de la Dextérité.")}),
    ("Clerc", "guerre", {"Force": (S, "Domaine de la Guerre : armure lourde et attaques au corps à corps.")}),
    ("Clerc", "forge", {"Force": (S, "Domaine de la Forge : armure lourde (Force 15 pour le harnois).")}),
    ("Clerc", "tempete", {"Force": (S, "Domaine de la Tempête : armure lourde et armes de guerre.")}),
    ("Druide", "lune", {"Constitution": (S, "Cercle de la Lune : la Constitution protège votre concentration "
                                            "sous forme animale.")}),
    ("Moine", "kensei", {"Dextérité": (P, "Armes de kensei : la Dextérité augmente attaques et dégâts.")}),
    ("Paladin", "", {}),
]

ORIENTATIONS = [("🔮 Magie", r"\bsorts?\b|incantation|emplacement"), ("⚔ Offensive", r"degats|attaque"),
                ("🛡 Défense", r"\bca\b|resistance|points de vie temporaires|pv temporaires"),
                ("✚ Soutien", r"soins|regagne|allie"), ("🌑 Furtivité", r"discretion|invisible|cache"),
                ("🐾 Compagnon", r"compagnon|familier|bete"), ("🎓 Polyvalence", r"competence|maitrise")]


def subclass_level(class_name: str) -> int:
    return R.SUBCLASS_LEVEL.get(class_name, 3)


class ClassGuideMixin:
    """Mélangé à Engine."""

    def class_guide(self, class_name: str) -> dict:
        g = dict(CLASS_GUIDE.get(class_name) or {"concept": "", "style": "", "mecaniques": [], "carac": {}})
        info = self.db.start_info(class_name) if class_name in self.db.classes else {}
        g.update(nom=class_name, de_vie=info.get("de_vie", ""), sauvegardes=info.get("sauvegardes", []),
                 armures=info.get("armures", []), armes=info.get("armes", []),
                 niveau_sous_classe=subclass_level(class_name),
                 sous_classes=[{"nom": s["nom"], "source": self._source_label(s), "niveau": subclass_level(class_name),
                                "non_officielle": self.db.is_unofficial(s)}
                               for s in self.db.subclasses(class_name)])
        return g

    def _source_label(self, sub: dict) -> str:
        """Source affichée ; v52 : mention discrète « non officielle » pour les créations de la communauté."""
        src = sub.get("source", "")
        return "{} · non officielle".format(src) if self.db.is_unofficial(sub) else src

    def subclass_summary(self, class_name: str, sub_name: str) -> Optional[dict]:
        """{nom, source, niveau, orientation: [...], pouvoirs: [(niveau, nom, résumé)]} d'après les données."""
        sub = self.db.subclass(class_name, sub_name)
        if not sub:
            return None
        feats = sorted(sub.get("capacites") or [], key=lambda f: int(f.get("niveau") or 0))
        text = norm(" ".join(f.get("description", "") for f in feats))
        tags = [label for label, rx in ORIENTATIONS if re.search(rx, text)][:3]
        powers = []
        for f in feats:
            desc = (f.get("description") or "").strip()
            short = desc if len(desc) <= 220 else desc[:217].rsplit(" ", 1)[0] + "…"
            powers.append((int(f.get("niveau") or 0), f.get("nom", ""), short))
        spells = [x for x in (sub.get("sorts_domaine") or []) if isinstance(x, str) and not x.isdigit()]
        return {"nom": sub["nom"], "source": self._source_label(sub), "niveau": subclass_level(class_name),
                "non_officielle": self.db.is_unofficial(sub),
                "orientation": tags, "pouvoirs": powers, "sorts": spells[:10]}

    def ability_recommendations(self, class_name: str = "", sub_name: Optional[str] = None) -> dict:
        """{caractéristique: (« principale » | « secondaire », raison)} pour la classe et la sous-classe visée."""
        entry = self.ch.classes[0] if self.ch.classes else {}
        cls = class_name or entry.get("nom", "")
        if sub_name is None:
            sub_name = (self.ch.find_class(cls) or {}).get("sous_classe") or \
                self.__dict__.get("_sous_classe_visee", "")
        recs = dict((CLASS_GUIDE.get(cls) or {}).get("carac", {}))
        n = norm(sub_name or "")
        for c, frag, extra in SUBCLASS_ABILITIES:
            if c == cls and frag and frag in n:
                for ab, (role, why) in extra.items():
                    if recs.get(ab, ("", ""))[0] != P or role == P:
                        recs[ab] = (role, why)
        return recs
