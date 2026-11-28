"""
Ce que la fiche gère toute seule (v53) — logique pure mélangée à Engine.

Pour un objet magique, un trait racial, une capacité de classe ou un don : trois listes lisibles
  - « auto » : appliqué automatiquement (bonus, résistances, avantages, tuile de l'onglet En partie, PV temporaires…) ;
  - « jet »  : proposé en case à cocher avant le d20 (avantage sous condition, core/situational.py) ;
  - « main » : effets du texte que la fiche ne gère pas — à appliquer soi-même en partie.
Les phrases purement descriptives (apparence, histoire) ne sont pas listées.
"""
from __future__ import annotations

import re

from .rules import norm
from .situational import parse_situational

# une phrase de règle (et non d'ambiance) : elle parle de jets, d'actions, de dégâts, de conditions de jeu…
RULE_WORDS = ("vous pouvez", "action", "reaction", "jet", "test", "degats", "avantage", "desavantage", "charge",
              "repos", "points de vie", "pv ", "sort", "vitesse", "cible", "creature", "resistance", "immunise",
              "bonus", "ca ", "classe d'armure", "dd ", "une fois", "minute", "rayon", "portee", "etat ")
_FLAVOR = ("histoire", "legende", "on raconte", "apparence", "ressemble", "fabrique", "forge", "on dit")


def _sentences(text: str) -> list[str]:
    return [s.strip(" •-\t") for s in re.split(r"(?<=[.!?])\s+|\n+", text or "") if len(s.strip(" •-\t")) > 3]


def _short(text: str, n: int = 110) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[:n - 2].rsplit(" ", 1)[0] + "…"


def _is_rule(sentence: str) -> bool:
    n = norm(sentence) + " "
    return any(w in n for w in RULE_WORDS) and not any(n.startswith(f) for f in _FLAVOR)


def mech_lines(m: dict) -> list[str]:
    """Modificateur (format mechanics) → lignes lisibles."""
    out = []
    for ab, v in (m.get("carac_min") or {}).items():
        out.append("{} portée à {}".format(ab, v))
    for ab, v in (m.get("carac") or {}).items():
        out.append("{:+d} en {}".format(v, ab))
    if m.get("ca"):
        out.append("{:+d} à la CA".format(m["ca"]))
    for key, label in (("js", "JS"), ("tests", "tests")):
        for ab, vals in (m.get(key) or {}).items():
            for v in vals:
                target = "aux {}".format(label) if ab == "*" else ("aux JS de " + ab if key == "js" else
                                                                     "aux tests de " + ab)
                if ab == "sorts":
                    target = "aux JS contre les sorts"
                out.append("{} {}".format("avantage" if v == "avantage" else "désavantage" if v == "désavantage"
                                          else "{:+d}".format(v) if isinstance(v, int) else str(v), target))
    for sk, vals in (m.get("competences") or {}).items():
        for v in vals:
            out.append("{} en {}".format("avantage" if v == "avantage" else "désavantage" if v == "désavantage"
                                         else "{:+d}".format(v) if isinstance(v, int) else str(v), sk))
    for v in m.get("initiative") or []:
        out.append("{} à l'initiative".format(v))
    if m.get("attaque"):
        out.append("jets d'attaque : " + ", ".join(str(v) for v in m["attaque"]))
    if m.get("resistances"):
        out.append("résistance : " + ", ".join(m["resistances"]))
    if m.get("immunites"):
        out.append("immunité : " + ", ".join(m["immunites"]))
    if m.get("etats_immunises"):
        out.append("immunité aux états : " + ", ".join(k.replace("_1", "") for k in m["etats_immunises"]))
    if m.get("vitesse_bonus"):
        out.append("vitesse {:+g} m".format(m["vitesse_bonus"]))
    if m.get("pv_max"):
        out.append("PV max {:+d}".format(m["pv_max"]))
    return out


class AutomationMixin:
    """Mélangé à Engine : rapport « automatique / proposé au jet / à la main »."""

    # ------------------------------------------------------------------ objets magiques
    def item_automation(self, name: str, entry: dict | None = None) -> dict:
        from . import mechanics as M
        item = self.magic_item(name) or {}
        entry = entry or next((e for e in self.ch.objets_magiques if e.get("nom") == name), None) or {"nom": name}
        desc = item.get("description", "") or ""
        auto: list[str] = []
        m = dict(M.item_mech(name) or M.item_mech(item.get("comme", "") or "-"))
        from .tattoos import tattoo_key
        m.update(self.tattoo_mech(tattoo_key(name)))
        for k, v in self.item_passive_mech(entry, item).items():
            if k not in m and k != "etats_immunises" or k == "etats_immunises":
                m.setdefault(k, v)
        auto += mech_lines(m)
        if item.get("ca") and "ca" not in m:
            auto.append("+{} à la CA{}".format(item["ca"], " et aux jets de sauvegarde" if item.get("js") else ""))
        tier = self.magic_gear_tier(item, entry) if entry.get("base") else 0
        if tier and self.magic_gear_kind(item) == "arme":
            auto.append("+{} à l'attaque et aux dégâts".format(tier))
        slot = {"objet": entry.get("uid", ""), "nom": entry.get("base", "")} if entry.get("uid") else None
        if slot:
            always, cond = self.item_damage_riders(slot)
            auto += ["dégâts en plus : {}".format(r[0].split(" : ", 1)[-1]) for r in always]
            auto += ["dégâts en plus à cocher au toucher : {}".format(r[0].split(" : ", 1)[-1]) for r in cond]
            for o in self.item_crit_options(slot):
                auto.append("sur un 20 naturel : " + o["label"].split(" : ", 1)[-1])
            if self.item_crit_min(slot) < 20:
                auto.append("critique sur 19-20")
        powers = [p for p in self.magic_item_powers() if p.get("entree") is not None and
                  self.ch.objets_magiques[p["entree"]] is entry]
        for p in powers:
            auto.append("tuile « {} » dans l'onglet En partie{}".format(
                p.get("sort") or p.get("nom") or "Utiliser",
                " ({} charges)".format(p["charges"]) if p.get("charges") else ""))
        if not powers and item and not item.get("perso"):   # objet pas encore équipé : tuile à venir
            from .magic_gear import CHARGES
            spells = self._item_spells(desc) if hasattr(self, "_item_spells") else []
            mc = CHARGES.search(desc)
            if spells or mc:
                auto.append("tuile{} dans l'onglet En partie une fois équipé{}".format(
                    " « " + " », « ".join(sp["nom"] for sp in spells[:3]) + " »" if spells else "",
                    " ({} charges, décomptées)".format(mc.group(1)) if mc else ""))
        jet = ["avantage {} ({})".format(o["condition"], self._target_label(o))
               for o in parse_situational(desc, name)] if not item.get("perso") else []
        main = self._manual_sentences(desc, covered=bool(auto) or bool(jet), item=item, entry=entry)
        if item.get("perso"):
            main = []                                     # objet sur mesure : tout ce qui est coché est appliqué
        return {"auto": list(dict.fromkeys(auto)), "jet": list(dict.fromkeys(jet)), "main": main}

    @staticmethod
    def _target_label(o: dict) -> str:
        if o["cible"] == "competence":
            return o["competence"]
        if o["cible"] == "sauvegarde":
            return "JS" + (" de " + o["carac"] if o["carac"] else "")
        if o["cible"] == "attaque":
            return "attaques"
        return "tests" + (" de " + o["carac"] if o["carac"] else "")

    def _manual_sentences(self, desc: str, covered: bool = False, item: dict | None = None,
                          entry: dict | None = None) -> list[str]:
        """Phrases de règle que la fiche n'applique pas (ni passif lu, ni avantage proposé au jet)."""
        out = []
        for s in _sentences(desc):
            if not _is_rule(s):
                continue
            if self._sentence_handled(s, item, entry):
                continue
            out.append(_short(s))
        return out[:6]

    def _sentence_handled(self, sentence: str, item: dict | None, entry: dict | None) -> bool:
        from . import mechanics as M
        n = norm(sentence)
        if parse_situational(sentence, "-"):
            return True
        if M.innate_from_text(sentence):
            return True
        if item is not None:
            probe = dict(item, description=sentence, perso=False)
            if self.item_passive_mech(entry or {}, probe):
                return True
            if re.search(r"\+\d (?:aux jets d'attaque et de degats|a la ca|a la classe d'armure)", n):
                return True
            if re.search(r"\d+d\d+ (?:points de )?degats (?:de |d')?\w+ supplementaires", n):
                return True
            if re.search(r"obtenez un 20|coup critique sur un|19 ou 20|temporaires egal aux degats supplementaires", n):
                return True
            if re.search(r"(?:possede|a) \d+ charges|regagne \d|recupere \d|lancer (?:le sort|l'un des sorts)|"
                         r"depenser \d+ charges?|lancer [a-z]|\bcharges?\b|derniere charge", n):
                return True                               # charges et sorts : tuile de l'onglet En partie
            if re.search(r"harmonis|lien avec|vous devez etre", n):
                return True                               # condition d'harmonisation : gérée par la fiche
        return False

    # ------------------------------------------------------------------ traits, capacités, dons
    def text_automation(self, name: str, desc: str, kind: str = "race") -> dict:
        """Rapport d'un trait racial (kind « race »), d'une capacité de classe (« classe ») ou d'un don (« don »)."""
        from . import effects as FX
        from . import mechanics as M
        auto: list[str] = []
        for key in M.innate_from_text(desc):
            if key in FX.EFFECTS:
                auto.append(FX.EFFECTS[key]["nom"].lower() + " (état permanent)")
        nd = norm(desc)
        if "vision dans le noir" in nd and re.search(r"\d+ m", nd):
            auto.append("vision dans le noir (bandeau de l'onglet En partie)")
        acts = []
        if kind == "race" and hasattr(self, "race_actions"):
            acts = [a for a in self.race_actions() if norm(a["nom"]) == norm(name)]
        elif hasattr(self, "class_actions"):
            acts = [a for a in self.class_actions() if norm(a["nom"]).startswith(norm(name)[:24])]
        for a in acts[:1]:
            uses = a.get("utilisations") or 0
            auto.append("tuile « {} » dans l'onglet En partie{}".format(
                a["nom"], " ({} utilisation{} / {})".format(uses, "s" * (uses > 1), a.get("recuperation", "repos"))
                if uses else ""))
            if a.get("pv_temp"):
                auto.append("{} PV temporaires appliqués à l'utilisation".format(a["pv_temp"]))
            if a.get("pv_temp_si_touche"):
                auto.append("{} PV temporaires si l'attaque touche (question posée)".format(a["pv_temp_si_touche"]))
            if a.get("degats") and a.get("jet") == "degats":
                auto.append("dés lancés : {}".format(a["degats"]))
        if re.search(r"(?:connait|connaissez|apprenez) (?:le|un) tour de magie|pouvez lancer le sort", nd):
            auto.append("sorts accordés ajoutés à l'onglet Magie")
        if re.search(r"maitrise (?:de la|des|d'une|de deux|de la competence)|vous maitrisez|maitrise de l'outil", nd):
            auto.append("maîtrises ajoutées (onglet Compétences / Race)")
        jet = ["avantage {} ({})".format(o["condition"], self._target_label(o)) for o in parse_situational(desc, name)]
        handled_by_tile = bool(acts)
        main = []
        for s in _sentences(desc):
            if not _is_rule(s) or self._sentence_handled(s, None, None):
                continue
            ns = norm(s)
            if handled_by_tile and re.search(r"utilis|repos|une fois|action bonus|par une action|nombre de fois", ns):
                continue
            if re.search(r"maitrise (?:de la|des|d'une|de deux)|vous maitrisez", ns):
                continue
            if "vision dans le noir" in ns or "tour de magie" in ns or "lancer le sort" in ns or \
                    re.search(r"^(vous )?(etes|êtes) de taille|^taille|vitesse de marche (de base )?(est|de)", ns):
                continue
            main.append(_short(s))
        return {"auto": list(dict.fromkeys(auto)), "jet": list(dict.fromkeys(jet)), "main": main[:5]}


def report_html(rep: dict) -> str:
    """Trois paragraphes HTML (vides omis) pour une infobulle ou un panneau de détail."""
    import html
    parts = []
    if rep.get("auto"):
        parts.append("<p><b>✔ Appliqué automatiquement :</b> {}</p>".format(html.escape(" ; ".join(rep["auto"]))))
    if rep.get("jet"):
        parts.append("<p><b>🎲 Proposé au jet (case à cocher) :</b> {}</p>".format(html.escape(" ; ".join(rep["jet"]))))
    if rep.get("main"):
        parts.append("<p><b>✋ À gérer à la main :</b><br/>{}</p>".format(
            "<br/>".join("• " + html.escape(s) for s in rep["main"])))
    elif rep.get("auto") or rep.get("jet"):
        parts.append("<p><b>✋ À gérer à la main :</b> rien</p>")
    return "".join(parts)


def report_text(rep: dict) -> str:
    """Version texte (infobulles construites avec rich_tip)."""
    lines = []
    if rep.get("auto"):
        lines.append("✔ Appliqué automatiquement : " + " ; ".join(rep["auto"]))
    if rep.get("jet"):
        lines.append("🎲 Proposé au jet : " + " ; ".join(rep["jet"]))
    if rep.get("main"):
        lines.append("✋ À gérer à la main : " + " ; ".join(rep["main"]))
    elif lines:
        lines.append("✋ À gérer à la main : rien")
    return "\n".join(lines)
