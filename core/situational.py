"""
Avantages sous condition (v53) — logique pure mélangée à Engine.

Un objet équipé, un trait racial, une capacité de classe ou un don peut donner un avantage limité à une situation :
« avantage aux jets de Sagesse (Perception) basés sur la vue », « aux jets de sauvegarde contre le poison », « aux
jets d'attaque contre les élémentaires »… Ces avantages ne sont jamais appliqués d'office : ils sont proposés en
cases à cocher (décochées) avant le d20, seulement pour le jet concerné et seulement si le personnage en possède
un. Un personnage sans rien de tel lance ses dés comme avant, sans fenêtre de plus.

Les avantages sans condition sont appliqués ailleurs (core/item_passives.py, effets de race / classe / dons) :
ils ne sont pas repris ici.
"""
from __future__ import annotations

import re
import unicodedata

ABILITIES = {"force": "Force", "dexterite": "Dextérité", "constitution": "Constitution",
             "intelligence": "Intelligence", "sagesse": "Sagesse", "charisme": "Charisme"}
_AB = "force|dexterite|constitution|intelligence|sagesse|charisme"
# phrases de pouvoir activé (une action, une charge, pendant 1 minute…) : ce ne sont pas des situations de jet
ACTIVE = ("une action", "action bonus", "votre reaction", "par une reaction", "depenser", "charge", "pendant 1 ",
          "pendant 10 ", "pendant une minute", "pendant une heure", "par jour", "si vous lancez",
          "lorsque vous lancez", "quand vous lancez", "lorsque vous utilisez", "la creature", "la cible")
# fin du libellé de la condition
_CUT = re.compile(r"\s*(?:;|, et |, mais | et vous |, vous | tandis qu|, tandis qu| tant que vous (?:portez|tenez|etes)|"
                  r",? (?:et |ainsi que )?(?:la |l')(?:resistance|immunite)|$)")


def _fold(text: str) -> str:
    """Minuscules sans accents, longueur conservée (les positions restent valables dans le texte d'origine)."""
    out = []
    for c in text:
        if c in "’‘":
            out.append("'")
            continue
        d = "".join(x for x in unicodedata.normalize("NFD", c) if unicodedata.category(x) != "Mn")
        out.append((d[:1] or c).lower()[:1] or c)
    return "".join(out)


def _sentences(text: str) -> list[str]:
    return [s.strip(" •-\t") for s in re.split(r"(?<=[.!?])\s+|\n+|•", text or "") if s.strip(" •-\t")]


def _condition(orig: str, start: int) -> str:
    """Texte de la condition à partir de `start` (texte d'origine), jusqu'à la fin de la proposition."""
    rest = orig[start:]
    m = _CUT.search(_fold(rest))
    cond = rest[:m.start()] if m else rest
    return cond.strip(" ,.;:").rstrip(")").strip()


def _is_condition(text: str) -> bool:
    """Une vraie condition (« basés sur la vue », « contre le poison », « pour vous cacher »…) ?"""
    f = _fold(text).strip()
    return bool(f) and bool(re.match(r"(qui |bases|basees|base |basee|lies|liees|lie |liee|effectues|faits|pour |"
                                     r"lorsque|quand|contre|dirige|concernant|visant|avec|reposant|si |tant que|"
                                     r"impliquant|en |afin|destines|relatifs)", f))


def parse_situational(text: str, source: str) -> list[dict]:
    """Avantages conditionnels lus dans un texte : [{cible, carac, competence, condition, source}].
    cible : « competence » | « test » | « sauvegarde » | « attaque » ; carac / competence : « » = toutes."""
    out: list[dict] = []
    for orig in _sentences(text):
        f = _fold(orig)
        for mt in re.finditer(r"(?<!des)avantage (?:a |aux |sur |pour |lors des? |a vos |a tous les |a tout )", f):
            head = f[:mt.start()]
            if not re.search(r"\bvous\b", head) or any(w in f for w in ACTIVE):
                continue
            pre = re.search(r"(tant que [^,]+|lorsque vous [^,]+|quand vous [^,]+|si vous [^,]+),", head)
            precond = orig[pre.start(1):pre.end(1)].strip() if pre else ""
            if precond and re.match(r"(tant que vous (?:portez|etes equipe|en etes equipe|tenez|maniez|etes lie|"
                                    r"etes harmonise|avez)|lorsque vous (?:portez|tenez)|"
                                    r"tant que (?:cette|cet|ce|la|le|l')\b)", _fold(precond)):
                precond = ""                              # « tant que vous portez l'objet » : pas une situation
            pos = mt.end()
            seg_end = len(f)
            nxt = re.search(r"(?<!des)avantage ", f[pos:])
            if nxt:
                seg_end = pos + nxt.start()
            seg_f, seg_o = f[pos:seg_end], orig[pos:seg_end]
            found = _targets(seg_f, seg_o)
            for target in found:
                cond = target.pop("condition")
                if not _is_condition(cond):
                    cond = ""
                if precond:
                    cond = (precond + (" — " + cond if cond else ""))
                if not cond:
                    continue                              # sans condition : géré ailleurs (appliqué d'office)
                out.append(dict(target, condition=cond, source=source))
    return out


def _targets(seg_f: str, seg_o: str) -> list[dict]:
    """Cibles d'une proposition « avantage aux … » et la condition qui les suit."""
    out = []
    skills = list(re.finditer(r"(?:" + _AB + r") \(([^)]+)\)", seg_f))
    if skills:
        end = skills[-1].end()
        cond = _condition(seg_o, end)
        for s in skills:
            out.append({"cible": "competence", "carac": ABILITIES[s.group(0).split(" (")[0]],
                        "competence": seg_o[s.start(1):s.end(1)].strip(), "condition": cond})
        return out
    multi = re.match(r"(?:vos |tous les |les )?jets d'attaque, (?:aux |de |les )?(?:jets de )?sauvegarde et (?:aux |de |"
                     r"les )?(?:(?:tests|jets) )?(?:de )?caracteristiques?", seg_f)
    if multi:
        cond = _condition(seg_o, multi.end())
        return [{"cible": c, "carac": "", "competence": "", "condition": cond}
                for c in ("attaque", "sauvegarde", "test")]
    sv = re.match(r"(?:vos |tous les |les |tout )?jets? de sauvegarde(?: de (" + _AB + r"))?", seg_f)
    if sv:
        return [{"cible": "sauvegarde", "carac": ABILITIES.get(sv.group(1) or "", ""), "competence": "",
                 "condition": _condition(seg_o, sv.end())}]
    at = re.match(r"(?:vos |tous les |les |votre |un |au |aux )?(?:prochain )?jets? d'attaque", seg_f)
    if at:
        return [{"cible": "attaque", "carac": "", "competence": "", "condition": _condition(seg_o, at.end())}]
    te = re.match(r"(?:vos |tous les |les |tout )?(?:tests|jets) (?:de caracteristiques?|d'(" + _AB + r")|de (" +
                  _AB + r"))", seg_f)
    if te:
        ab = te.group(1) or te.group(2) or ""
        return [{"cible": "test", "carac": ABILITIES.get(ab, ""), "competence": "",
                 "condition": _condition(seg_o, te.end())}]
    return out


class SituationalMixin:
    """Mélangé à Engine : avantages sous condition proposés avant un jet de d20."""

    def situational_sources(self) -> list[tuple[str, str]]:
        """[(libellé de la source, texte)] : objets magiques portés (et harmonisés si besoin), traits raciaux,
        capacités de classe débloquées, dons."""
        out: list[tuple[str, str]] = []
        for entry in self.ch.objets_magiques:
            item = self.magic_item(entry.get("nom", "")) or {}
            if not entry.get("equipe", True) or entry.get("detruit") or (item.get("lien") and
                                                                          not entry.get("harmonise")):
                continue
            if item.get("perso"):
                continue                                  # objet sur mesure : avantages choisis explicitement
            out.append((self.magic_display_name(entry) if entry.get("base") else entry.get("nom", ""),
                        item.get("description", "") or ""))
        for c in self._race_trait_list() if hasattr(self, "_race_trait_list") else []:
            out.append((c.get("nom", ""), c.get("description", "") or ""))
        for e in self.ch.classes:
            for f in self.features(e):
                if f.get("debloque") and not self.feature_replaced(norm_name(f["nom"])):
                    out.append((f["nom"], f.get("description", "") or ""))
        for name in list(self.chosen_feats()) + list(getattr(self.ch, "dons_mj", []) or []):
            feat = self.db.feats.get(name) or {}
            out.append((name, feat.get("description", "") or ""))
        return out

    def situational_advantages(self) -> list[dict]:
        cache = getattr(self, "_situational_cache", None)
        key = (id(self.ch), len(self.ch.objets_magiques), tuple(e.get("nom") for e in self.ch.objets_magiques),
               tuple((e.get("equipe", True), e.get("harmonise")) for e in self.ch.objets_magiques),
               self.ch.race, self.ch.sous_race, tuple((e["nom"], e["niveau"], e.get("sous_classe", ""))
                                                      for e in self.ch.classes),
               tuple(self.chosen_feats()), tuple(getattr(self.ch, "dons_mj", []) or []))
        if cache and cache[0] == key:
            return cache[1]
        out, seen = [], set()
        for label, text in self.situational_sources():
            for opt in parse_situational(text, label):
                k = (opt["cible"], opt["carac"], opt["competence"], opt["condition"].lower(), label)
                if k not in seen:
                    seen.add(k)
                    out.append(opt)
        self._situational_cache = (key, out)
        return out

    def situational_options(self, spec) -> list[dict]:
        """Cases à proposer avant ce jet : [{label, source}] (vide = pas de fenêtre)."""
        kind = getattr(spec, "kind", "")
        ab, skill = getattr(spec, "ability", ""), getattr(spec, "skill", "")
        out = []
        for o in self.situational_advantages():
            ok = (o["cible"] == "attaque" and kind == "attaque"
                  or o["cible"] == "sauvegarde" and kind == "sauvegarde" and (
                      ("la mort" in _fold(o["condition"])) == (ab == "mort")) and o["carac"] in ("", ab)
                  or o["cible"] == "test" and kind in ("test", "competence") and o["carac"] in ("", ab) and ab
                  or o["cible"] == "competence" and kind == "competence" and skill and
                  _fold(o["competence"]) == _fold(skill))
            if not ok or o["source"] in (getattr(spec, "avantage", []) or []) or \
                    "Objet : " + o["source"] in (getattr(spec, "avantage", []) or []):
                continue
            cond = o["condition"] if len(o["condition"]) <= 80 else o["condition"][:78].rsplit(" ", 1)[0] + "…"
            out.append({"label": "{} — {}".format(cond[:1].upper() + cond[1:], o["source"]), "detail": o["condition"],
                        "source": o["source"]})
        return out

    @staticmethod
    def apply_situational(spec, chosen: list[str]):
        """Copie du jet avec les avantages cochés (sources ajoutées à l'avantage, mode recalculé)."""
        import dataclasses
        from . import dice as D
        if not chosen:
            return spec
        adv = list(spec.avantage) + [c for c in chosen if c not in spec.avantage]
        return dataclasses.replace(spec, avantage=adv, mode=D.mode_of(adv, spec.desavantage, spec.echec))


def norm_name(name: str) -> str:
    from .rules import norm
    return norm(name)
