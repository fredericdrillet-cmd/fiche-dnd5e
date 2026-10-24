"""
Évaluation des formules écrites dans les descriptions (aptitudes de classe, traits raciaux, dons...).

    « 1d10 + votre niveau de guerrier »                -> « 1d10 + 5 (niveau de guerrier) »
    « 8 + bonus de maîtrise + modificateur de Sagesse » -> « 8 + 3 (bonus de maîtrise) + 2 (modificateur de Sagesse) = 13 »
    « 5 × votre niveau de paladin »                    -> « 5 × 6 (niveau de paladin) = 30 »
    « égal à votre modificateur de Charisme »          -> « égal à votre modificateur de Charisme (+3) »

Le texte d'origine est conservé ; les valeurs du personnage actif sont simplement insérées à côté.
Module pur (aucune dépendance à l'interface) : `annotate()` renvoie du texte, `annotate_html()` du HTML.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field

ABIL = {"for": "Force", "dex": "Dextérité", "con": "Constitution", "int": "Intelligence", "sag": "Sagesse",
        "cha": "Charisme"}
CLASSES = {"barbare": "Barbare", "barde": "Barde", "clerc": "Clerc", "druide": "Druide", "ensorceleur": "Ensorceleur",
           "guerrier": "Guerrier", "magicien": "Magicien", "moine": "Moine", "occultiste": "Occultiste",
           "paladin": "Paladin", "rodeur": "Rôdeur", "rôdeur": "Rôdeur", "roublard": "Roublard",
           "artificier": "Artificier"}

_AB = r"(force|dext[ée]rit[ée]|constitution|intelligence|sagesse|charisme|for|dex|con|int|sag|cha)\b"
_CL = r"(barbare|barde|clerc|druide|ensorceleur|guerrier|magicien|moine|occultiste|paladin|r[ôo]deur|roublard|artificier)"
_APOS = r"(?:de\s+|d['’]\s*)"

# (motif, type) — l'ordre compte : les formes les plus longues d'abord
PATTERNS = [
    (re.compile(r"(?:votre\s+)?(?:modificateur|mod\.?)\s+(?:de\s+)?(?:caract[ée]ristique\s+)?d['’]\s*incantation"
                r"|mod\.?\s*carac\.?\s*inc\.?", re.I), "spell"),
    (re.compile(r"(?:votre\s+)?(?:modificateur|mod\.?)\s+" + _APOS + "?" + _AB, re.I), "mod"),
    (re.compile(r"(?:votre\s+)?bonus\s+de\s+ma[îi]trise", re.I), "prof"),
    (re.compile(r"(?:la\s+)?moiti[ée]\s+\(arrondie\s+au\s+sup[ée]rieur\)\s+(?:de\s+votre|du)\s+niveau\s+" + _APOS + _CL
                + r"|(?:la\s+)?moiti[ée]\s+(?:de\s+votre|du)\s+niveau\s+" + _APOS + _CL
                + r"\s+\(arrondie\s+au\s+sup[ée]rieur\)", re.I), "half_up"),
    (re.compile(r"(?:la\s+)?moiti[ée]\s+(?:de\s+votre|du)\s+niveau\s+" + _APOS + _CL, re.I), "half_class"),
    (re.compile(r"(?:votre\s+)?niveau\s+" + _APOS + _CL, re.I), "class"),
    (re.compile(r"(?:votre\s+)?niveau\s+(?:de\s+personnage|global)", re.I), "total"),
    (re.compile(r"(?:votre\s+)?niveau\s+de\s+classe|votre\s+niveau(?!\s+(?:de|d['’]|global|de\s+sort))", re.I), "ctx"),
]


@dataclass
class FormulaContext:
    """Valeurs du personnage utilisées pour évaluer les formules."""
    mods: dict = field(default_factory=dict)          # {"Force": 3, ...}
    prof: int = 2
    levels: dict = field(default_factory=dict)        # {"Guerrier": 5, ...}
    current_class: str = ""                            # classe de l'aptitude affichée (« votre niveau »)
    spell_mod: int | None = None                       # modificateur d'incantation de cette classe
    total_level: int = 0                               # niveau de personnage (traits raciaux, dons)


def _value(kind: str, m: re.Match, ctx: FormulaContext):
    """(valeur, signée ?) ou None si la formule ne peut pas être évaluée pour ce personnage."""
    if kind == "mod":
        ab = ABIL.get(m.group(1).lower()[:3].replace("é", "e"))
        return (ctx.mods[ab], True) if ab in ctx.mods else None
    if kind == "spell":
        return (ctx.spell_mod, True) if ctx.spell_mod is not None else None
    if kind == "prof":
        return ctx.prof, True
    if kind in ("class", "half_class", "half_up"):
        cls = CLASSES.get(next(g for g in m.groups() if g).lower())
        lvl = ctx.levels.get(cls)
        if not lvl:
            return None
        return ((lvl + 1) // 2 if kind == "half_up" else lvl // 2 if kind == "half_class" else lvl), False
    if kind == "total":
        return (ctx.total_level, False) if ctx.total_level else None
    if kind == "ctx":
        lvl = ctx.levels.get(ctx.current_class) if ctx.current_class else ctx.total_level
        return (lvl, False) if lvl else None
    return None


def short_label(phrase: str) -> str:
    """Libellé court affiché après une valeur calculée : « 3 (mod. Constitution) », « 3 (maîtrise) »."""
    p = re.sub(r"^votre\s+", "", phrase.strip(), flags=re.I)
    low = p.lower()
    if "incantation" in low or "carac" in low and "inc" in low:
        return "mod. incantation"
    m = re.match(r"(?:modificateur|mod\.?)\s+(?:de\s+|d['’]\s*)?(\w+)", p, re.I)
    if m:
        ab = ABIL.get(m.group(1).lower()[:3].replace("é", "e"), m.group(1).capitalize())
        return "mod. " + ab
    if "maîtrise" in low or "maitrise" in low:
        return "maîtrise"
    m = re.match(r"(la\s+)?moiti[ée].*niveau\s+(?:de\s+|d['’]\s*)(\w+)", p, re.I)
    if m:
        return "½ niv. " + m.group(2).lower()
    m = re.match(r"niveau\s+(?:de\s+|d['’]\s*)(\w+)", p, re.I)
    if m:
        return "niv. " + m.group(1).lower()
    return p


def _tokenize(text: str, ctx: FormulaContext):
    """Remplace chaque formule reconnue par un jeton \\x00i\\x00 ; renvoie (texte, jetons)."""
    spans = []
    for rx, kind in PATTERNS:
        for m in rx.finditer(text):
            if any(not (m.end() <= a or m.start() >= b) for a, b, *_ in spans):
                continue
            val = _value(kind, m, ctx)
            if val is not None:
                spans.append((m.start(), m.end(), m.group(0).strip(), val[0], val[1]))
    spans.sort()
    tokens, out, pos = [], [], 0
    for start, end, phrase, value, signed in spans:
        out.append(text[pos:start])
        out.append("\x00{}\x00".format(len(tokens)))
        tokens.append((phrase, value, signed))
        pos = end
    out.append(text[pos:])
    return "".join(out), tokens


_TERM = r"(?:\d+d\d+|\d+|\x00\d+\x00)"
_CHAIN = re.compile(_TERM + r"(?:\s*(?:[+\-×*]|x(?=\s*[\d\x00]))\s*" + _TERM + r")+")


def _render(text: str, tokens, fmt_val, fmt_txt) -> str:
    """Rend le texte : chaînes arithmétiques évaluées (« = total ») et jetons isolés annotés."""
    def token_phrase(i: int) -> str:
        return tokens[i][0]

    pieces, pos = [], 0
    for m in _CHAIN.finditer(text):
        chain = m.group(0)
        if "\x00" not in chain:
            continue
        pieces.append(("txt", text[pos:m.start()]))
        parts = re.split(r"(\s*(?:[+\-×*]|x(?=\s*[\d\x00]))\s*)", chain)
        total, op, dice, rendered = 0, "+", False, []
        for part in parts:
            stripped = part.strip()
            if stripped in ("+", "-", "×", "*", "x"):
                op = "×" if stripped in ("×", "*", "x") else stripped
                rendered.append(("op", op))
                continue
            tok = re.fullmatch(r"\x00(\d+)\x00", stripped)
            if tok:
                phrase, value, _signed = tokens[int(tok.group(1))]
                if op == "+" and value < 0 and rendered and rendered[-1][0] == "op":
                    rendered[-1] = ("op", "-")
                    shown, op_eff, val_eff = abs(value), "-", abs(value)
                else:
                    shown, op_eff, val_eff = value, op, value
                rendered.append(("val", (shown, short_label(phrase))))
            elif re.fullmatch(r"\d+d\d+", stripped):
                dice, op_eff, val_eff = True, op, 0
                rendered.append(("txt", stripped))
            else:
                op_eff, val_eff = op, int(stripped)
                rendered.append(("txt", stripped))
            if not dice:
                total = total + val_eff if op_eff == "+" else total - val_eff if op_eff == "-" else total * val_eff
        for kind, payload in rendered:
            if kind == "op":
                pieces.append(("txt", " {} ".format(payload)))
            elif kind == "val":
                pieces.append(("val", str(payload[0])))
                pieces.append(("txt", " ({})".format(payload[1])))
            else:
                pieces.append(("txt", payload))
        if not dice:
            pieces.append(("txt", " = "))
            pieces.append(("val", str(total)))
        pos = m.end()
    pieces.append(("txt", text[pos:]))

    out = []
    for kind, payload in pieces:
        if kind == "val":
            out.append(fmt_val(payload))
            continue
        # jetons restés isolés (hors calcul) : « modificateur de Sagesse (+2) »
        segments = re.split(r"\x00(\d+)\x00", payload)
        for i, seg in enumerate(segments):
            if i % 2 == 0:
                out.append(fmt_txt(seg))
            else:
                phrase, value, signed = tokens[int(seg)]
                out.append(fmt_txt(phrase + " ("))
                out.append(fmt_val("{:+d}".format(value) if signed else str(value)))
                out.append(fmt_txt(")"))
    _ = token_phrase
    return "".join(out)


def annotate(text: str, ctx: FormulaContext) -> str:
    """Texte avec les valeurs du personnage insérées à côté des formules."""
    if not text:
        return text
    tokenized, tokens = _tokenize(text, ctx)
    if not tokens:
        return text
    return _render(tokenized, tokens, lambda v: v, lambda t: t)


def annotate_html(text: str, ctx: FormulaContext, color: str = "") -> str:
    """Version HTML : texte échappé, valeurs calculées en gras (et en couleur d'accent si fournie)."""
    if not text:
        return ""
    tokenized, tokens = _tokenize(text, ctx)
    style = " style='color:{}'".format(color) if color else ""
    if not tokens:
        return html.escape(text).replace("\n", "<br/>")
    return _render(tokenized, tokens, lambda v: "<b{}>{}</b>".format(style, html.escape(v)),
                   lambda t: html.escape(t).replace("\n", "<br/>"))
