"""
Choix manquants (v28) : tout ce que le joueur doit encore décider pour que sa fiche soit complète.

`missing_choices()` renvoie une liste d'éléments {onglet, encart, message, nombre} :
    - onglet  : clé de l'onglet où le choix se corrige (classes, caracteristiques, race, combat, magie, progression) ;
    - encart  : nom de l'encart concerné (pour le titre « … — 2 à choisir ») ;
    - nombre  : combien de choix restent (≥ 1).
Seuls les OUBLIS sont comptés ici (moins que le permis) ; les EXCÈS et prérequis non remplis restent dans
`warnings()` (incohérences). Rien n'est jamais bloqué : la fiche reste libre, les manques sont signalés.
"""
from __future__ import annotations

import re

from . import rules as R
from .engine_extras import _batch_memo
from .rules import ABILITIES, norm

NUMBERS = {"un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4}
DRACONIC_RACES = ("drakeide",)


def _count_word(text: str) -> int:
    """« Deux au choix » -> 2 ; « 1 au choix » -> 1 ; « Au choix » -> 1."""
    t = norm(text)
    m = re.search(r"(\d+)", t)
    if m:
        return int(m.group(1))
    for word, n in NUMBERS.items():
        if re.search(r"\b" + word + r"\b", t):
            return n
    return 1


class MissingChoicesMixin:
    """Mélangé à Engine."""

    # ------------------------------------------------------------------ compétences
    def race_skill_picks(self) -> int:
        """Compétences au choix accordées par l'espèce (Demi-elfe : 2, Humain variant : 1, Kenku : 2…)."""
        total = 0
        for c in self.race_capacities():
            d = norm(c.get("description", ""))
            if "competence" not in d or not ("au choix" in d or "de votre choix" in d):
                continue
            if "maitrise" not in d and "maitrisez" not in d:
                continue
            m = re.search(r"(\d+|une|un|deux|trois|quatre) competences?", d)
            total += _count_word(m.group(1)) if m else 1
        return total

    def skills_missing(self) -> int:
        """Maîtrises de compétences encore à cocher : classe + choix de l'espèce, hors historique et race fixes."""
        if not self.ch.classes:
            return 0
        st = self.class_skill_status()
        fixed = set(self.ch.competences_historique) | set(self._acquis().get("competences", []))
        have = [n for n, s in self.ch.competences.items() if s.get("maitrise") and n not in fixed]
        expected = st["nombre"] + self.race_skill_picks()
        return max(0, expected - len(have))

    def expertise_allowed(self) -> int:
        """Expertises accordées : 2 par aptitude « Expertise » débloquée (Roublard 1 et 6, Barde 3 et 10…)."""
        n = 0
        for e in self.ch.classes:
            for f in self.features(e):
                if f["debloque"] and norm(f["nom"]).startswith("expertise"):
                    n += 2
        return n

    def expertise_missing(self) -> int:
        have = sum(1 for s in self.ch.competences.values() if s.get("maitrise") and s.get("expertise"))
        return max(0, self.expertise_allowed() - have)

    # ------------------------------------------------------------------ langues
    def language_grants(self) -> list[tuple[str, int]]:
        """Langues « au choix » accordées : [(source, nombre)] — espèce, historique, dons et aptitudes de classe
        (« deux langues de votre choix », don Connaissance ancestrale, Prodige…)."""
        out = []
        langs = list(self.db.race_languages(self.ch.race)) + list((self.subrace() or {}).get("langues", []))
        n = sum(_count_word(x) for x in langs if "choix" in norm(x))
        if n:
            out.append(("Espèce ({})".format(self.ch.race), n))
        bg = self.db.backgrounds.get(self.ch.historique) or {}
        text = bg.get("langues", "") or ""
        if "choix" in norm(text):
            out.append(("Historique ({})".format(self.ch.historique), _count_word(text)))
        rx = re.compile(r"(\d+|une|un|deux|trois|quatre) langues? (?:de votre choix|au choix)")
        for feat in self.chosen_feats():
            m = rx.search(norm(str(self.db.feats.get(feat, {}).get("description", ""))))
            if m:
                out.append(("Don : " + feat, _count_word(m.group(1))))
        for e in self.ch.classes:
            for f in self.features(e):
                m = rx.search(norm(f["description"])) if f["debloque"] else None
                if m:
                    out.append(("{} : {}".format(e["nom"], f["nom"]), _count_word(m.group(1))))
        return out

    def language_picks(self) -> int:
        return sum(n for _src, n in self.language_grants())

    def languages_fixed(self) -> set:
        known = {norm(n) for n in self.db.language_names()}
        langs = list(self.db.race_languages(self.ch.race)) + list((self.subrace() or {}).get("langues", []))
        bg_text = (self.db.backgrounds.get(self.ch.historique) or {}).get("langues", "") or ""
        fixed = {norm(x) for x in langs if "choix" not in norm(x)}
        fixed |= {norm(x.strip()) for x in re.split(r",|;| et ", bg_text) if x.strip() and "choix" not in norm(x)
                  and norm(x.strip()) in known}
        return fixed

    def languages_known(self) -> int:
        have = {norm(x) for x in self.ch.langues_liste}
        have |= {norm(p.strip()) for p in re.split(r";|,", self.ch.langues or "") if p.strip()}
        return len(have)

    def languages_allowed(self) -> int:
        """Nombre total de langues accordées : langues fixes (espèce, historique) + langues au choix."""
        return len(self.languages_fixed()) + self.language_picks()

    def languages_missing(self) -> int:
        if not self.language_picks():
            return 0
        return max(0, self.languages_allowed() - self.languages_known())

    def languages_excess(self) -> int:
        allowed = self.languages_allowed()
        return max(0, self.languages_known() - allowed) if allowed else 0

    # ------------------------------------------------------------------ synthèse
    @_batch_memo
    def missing_choices(self) -> list[dict]:
        ch, out = self.ch, []

        def add(tab: str, box: str, n: int, message: str) -> None:
            if n > 0:
                out.append({"onglet": tab, "encart": box, "nombre": int(n), "message": message})

        # caractéristiques
        if ch.methode == "des":
            n = sum(1 for ab in ABILITIES if ch.des_affectation.get(ab, -1) < 0)
            add("caracteristiques", "Caractéristiques", n,
                "{} valeur{} tirée{} à assigner".format(n, "s" * (n > 1), "s" * (n > 1)))
        rule = self.race_rule()
        if rule["libres"]:
            picks = [p for p in ch.bonus_libres[:len(rule["libres"])] if p]
            n = len(rule["libres"]) - len(picks)
            add("caracteristiques", "Bonus raciaux de caractéristiques", n,
                "{} bonus racia{} libre{} à attribuer".format(n, "ux" if n > 1 else "l", "s" * (n > 1)))
        n = self.skills_missing()
        add("caracteristiques", "Compétences", n,
            "{} compétence{} à choisir (classe{})".format(n, "s" * (n > 1),
                                                         ", espèce" if self.race_skill_picks() else ""))
        n = self.expertise_missing()
        add("caracteristiques", "Compétences", n, "{} expertise{} à attribuer".format(n, "s" * (n > 1)))
        n = self.racial_choices_missing()                # v48 : sort mineur racial au choix (Haut-elfe…)
        add("magie", "Sorts raciaux", n, "{} sort{} mineur{} racia{} à choisir".format(
            n, "s" * (n > 1), "s" * (n > 1), "ux" if n > 1 else "l"))
        # classes
        for e in ch.classes:
            need = self.subclass_level(e["nom"])
            if e["niveau"] >= need and not e.get("sous_classe") and self.db.subclasses(e["nom"]):
                add("classes", "Sous-classe", 1, "{} : sous-classe à choisir (niveau {} atteint)".format(e["nom"], need))
        # race, historique, langues
        n = self.languages_missing()
        add("race", "Langues", n, "{} langue{} au choix à ajouter".format(n, "s" * (n > 1)))
        if any(norm(ch.race).startswith(r) for r in DRACONIC_RACES) and hasattr(self, "has_breath") \
                and self.has_breath() and not ch.ascendance_raciale:
            add("combat", "Capacités de combat raciales", 1, "Couleur du dragon ancestral à choisir")
        # combat : styles de combat, modèle d'armure
        for slot in self.fighting_style_slots():
            if slot["debloque"] and slot["id"] not in ch.styles_combat:
                what = "Modèle d'armure" if slot["kind"] == "modele" else "Style de combat"
                add("combat", "Style de combat", 1, "{} à choisir ({})".format(what, slot["classe"]))
        for st in self.option_sets():                   # runes, options de Tir arcanique
            n = st["total"] - len(st["chosen"])
            add("combat", "Options de sous-classe", n, "{} : {} à choisir".format(st["label"], n))
        if self.superior_technique() and not ch.technique_manoeuvre:
            add("combat", "Style de combat", 1, "Technique supérieure : manœuvre à choisir")
        # magie
        for c in self.casters():
            cnt = self.spell_counts(c["classe"])
            n = c["mineurs_max"] - cnt["mineurs"]
            add("magie", "Sorts", n, "{} : {} sort{} mineur{} à choisir".format(c["classe"], n, "s" * (n > 1),
                                                                                  "s" * (n > 1)))
            if c["connus_max"] is not None:
                n = c["connus_max"] - cnt["sorts"]
                add("magie", "Sorts", n, "{} : {} sort{} connu{} à choisir".format(c["classe"], n, "s" * (n > 1),
                                                                                   "s" * (n > 1)))
            if c["classe"] == "Magicien":
                n = 6 + 2 * (c["niveau"] - 1) - cnt["sorts"]
                add("magie", "Sorts", n, "Magicien : {} sort{} à inscrire dans le grimoire".format(n, "s" * (n > 1)))
            if c["prepares_max"] is not None:
                n = min(c["prepares_max"], cnt["sorts"] if c["classe"] == "Magicien" else c["prepares_max"]) \
                    - cnt["prepares"]
                add("magie", "Sorts", n, "{} : {} sort{} à préparer".format(c["classe"], n, "s" * (n > 1)))
        if self.class_level("Occultiste") >= 3 and not ch.pacte:
            add("magie", "Pacte", 1, "Occultiste : faveur de pacte à choisir")
        slots_m = self.manifestation_slots()
        n = slots_m["total"] - len(ch.manifestations)
        add("magie", "Manifestations occultes", n, "{} manifestation{} occulte{} à choisir".format(
            n, "s" * (n > 1), "s" * (n > 1)))
        n = self.ritual_book_missing()                   # v37 : Livre des secrets anciens
        add("magie", "Manifestations occultes", n, "Livre des secrets anciens : {} rituel{} de niveau 1 à "
            "inscrire".format(n, "s" * (n > 1)))
        # progression : améliorations de caractéristiques et dons
        for slot in self.asi_slots():
            c = ch.ameliorations.get(slot["id"], {})
            mode = c.get("mode", "aucun")
            incomplete = (mode in ("", "aucun") or (mode == "don" and not c.get("don"))
                          or (mode == "plus2" and not c.get("a1"))
                          or (mode == "plus1x2" and not (c.get("a1") and c.get("a2") and c["a1"] != c["a2"])))
            if incomplete:
                add("progression", "Emplacements débloqués", 1, "{} : {} à choisir".format(
                    slot["label"], "don" if slot.get("don_seul") else "amélioration ou don"))
        return out

    def missing_by_tab(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for m in self.missing_choices():
            counts[m["onglet"]] = counts.get(m["onglet"], 0) + m["nombre"]
        return counts

    def missing_in(self, tab: str, box: str) -> int:
        return sum(m["nombre"] for m in self.missing_choices() if m["onglet"] == tab and m["encart"] == box)

