"""
Fiche imprimable (v52) — HTML pur (aucune dépendance Qt), converti en PDF par l'interface (ui/pdf_export.py).

Style « grimoire » inspiré de Baldur's Gate 3, en noir et blanc : bandeau de titre noir, sections à bandeau noir et
losanges, médaillons de caractéristiques à double trait, police à empattements (choisie par ui/pdf_export.py).
- page 1 : identité ; six caractéristiques ; CA, initiative, vitesse, PV, maîtrise, perception, inspiration ;
  jets de sauvegarde, compétences, maîtrises et langues (gauche) ; attaques et aptitudes (droite, autant que la
  page en contient) ;
- page 2 : suite des aptitudes, traits d'espèce, dons, équipement, personnalité ;
- page 3 (lanceurs de sorts) : DD, attaque, emplacements à cocher, sorts par niveau.
"""
from __future__ import annotations

import html
import re

from . import rules as R
from .rules import ABILITIES, norm

INK, PAPER, SHADE = "#000000", "#ffffff", "#ececec"
CSS = """
body { font-size: 8.5pt; color: #000000; }
td, th { vertical-align: top; }
.lab { font-size: 6.5pt; font-variant: small-caps; }
.mut { color: #555555; }
.small { font-size: 7.5pt; }
"""
SKIP_FEATURES = ("amelioration de caracteristique", "capacite de sous-classe", "aptitude de sous-classe",
                 "sous-classe de", "incantation", "caracteristiques (2024)")


def _e(text) -> str:
    return html.escape(re.sub(r"\s*\(2024\)", "", str(text if text is not None else "")))


def _short(text: str, limit: int = 230) -> str:
    t = re.sub(r"\s+", " ", text or "").strip()
    return t if len(t) <= limit else t[:limit].rsplit(" ", 1)[0] + "…"


def section(title: str) -> str:
    """Bandeau de section noir, titre en petites capitales entre losanges."""
    return ("<table width='100%' cellspacing='0' cellpadding='3' style='margin-top:6px'><tr>"
            "<td bgcolor='{}'><font color='{}'><b>&#9670;&nbsp; <span style='font-variant: small-caps'>{}</span>"
            "&nbsp; &#9670;</b></font></td></tr></table>".format(INK, PAPER, _e(title)))


def _stat(label: str, value, sub: str = "", width: str = "") -> str:
    """Médaillon : grande valeur, libellé en petites capitales, double trait."""
    w = " width='{}'".format(width) if width else ""
    return ("<td align='center'{} style='border: 3px double {}; padding: 3px'>"
            "<span style='font-size: 15pt; font-weight: bold'>{}</span>{}<br/><span class='lab'>{}</span></td>"
            .format(w, INK, value, "<br/><span class='small'>{}</span>".format(_e(sub)) if sub else "", _e(label)))


def _header(eng) -> str:
    ch = eng.ch
    classes = " / ".join("{} {}{}".format(c["nom"], c["niveau"], " — {}".format(c["sous_classe"]) if
                                          c.get("sous_classe") else "") for c in ch.classes)
    line = " &nbsp;&#9670;&nbsp; ".join(_e(x) for x in (
        classes, ch.race + (" ({})".format(ch.sous_race) if ch.sous_race else ""), ch.historique, ch.alignement,
        "D&D 5e {}".format(eng.sheet_edition)) if x)
    meta = "Joueur : {} &nbsp;·&nbsp; Expérience : {} &nbsp;·&nbsp; Niveau {}".format(
        _e(ch.joueur or "—"), _e(ch.experience), eng.total_level)
    portrait = ("<td width='92' align='center' bgcolor='{}'><img src='portrait.png' width='86'/></td>".format(INK)
                if ch.portrait else "")
    return ("<table width='100%' cellspacing='0' cellpadding='6'><tr><td bgcolor='{ink}'>"
            "<font color='{paper}'><span style='font-size: 22pt; font-weight: bold; font-variant: small-caps'>{name}"
            "</span><br/><span style='font-size: 9pt'>{line}</span><br/><span style='font-size: 7.5pt'>{meta}</span>"
            "</font></td>{portrait}</tr></table>"
            "<p align='center' style='margin: 2px 0'>&#9670; &#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212; "
            "&#10070; &#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212; &#9670;</p>").format(
        ink=INK, paper=PAPER, name=_e(ch.nom or "Sans nom"), line=line, meta=meta, portrait=portrait)


def _abilities(eng) -> str:
    cells = "".join(_stat(_e(ab), _e(R.fmt_bonus(eng.mod(ab))), str(eng.score(ab)), "16%") for ab in ABILITIES)
    return "<table width='100%' cellspacing='4' cellpadding='0'><tr>{}</tr></table>".format(cells)


def _combat_row(eng) -> str:
    ch = eng.ch
    hp_cur = ch.pv_actuels if ch.pv_actuels >= 0 else eng.hp_max()
    dice = ", ".join("{} {}".format(n, d) for d, n in eng.hit_dice().items())
    death = "{} / {}".format("&#9679;" * ch.mort_reussites + "&#9675;" * (3 - ch.mort_reussites),
                             "&#9679;" * ch.mort_echecs + "&#9675;" * (3 - ch.mort_echecs))
    cells = [_stat("Classe d'armure", eng.armor_class()[0]),
             _stat("Initiative", _e(R.fmt_bonus(eng.initiative_detail()["total"]))),
             _stat("Vitesse", _e(eng.speed_text().split(" (")[0])),
             _stat("PV maximum", eng.hp_max(), "actuels {} · temp. {}".format(hp_cur, ch.pv_temporaires or 0)),
             _stat("Maîtrise", _e(R.fmt_bonus(eng.prof))),
             _stat("Perception passive", eng.passive_perception()),
             _stat("Inspiration", "&#9670;" if ch.inspiration else "&#9671;")]
    return ("<table width='100%' cellspacing='4' cellpadding='0'><tr>{}</tr></table>"
            "<p class='small' align='center' style='margin:1px 0'>Dés de vie : <b>{}</b> &nbsp;&#9670;&nbsp; "
            "Jets contre la mort (réussites / échecs) : <b>{}</b></p>").format("".join(cells), _e(dice), death)


def _saves_and_skills(eng) -> str:
    rows = []
    for i, s in enumerate(eng.save_rows()):
        bg = " bgcolor='{}'".format(SHADE) if i % 2 else ""
        rows.append("<tr{}><td width='12'>{}</td><td align='right' width='24'><b>{}</b></td><td>{}</td></tr>".format(
            bg, "&#9670;" if s["maitrise"] else "&#9671;", R.fmt_bonus(s["bonus"]), _e(s["carac"])))
    saves = "<table width='100%' cellspacing='0' cellpadding='1'>{}</table>".format("".join(rows))
    rows = []
    for i, s in enumerate(eng.skill_rows()):
        bg = " bgcolor='{}'".format(SHADE) if i % 2 else ""
        mark = "&#10070;" if s["expertise"] else "&#9670;" if s["maitrise"] else "&#9671;"
        rows.append("<tr{}><td width='12'>{}</td><td align='right' width='24'><b>{}</b></td><td>{} "
                    "<span class='mut small'>{}</span></td></tr>".format(
                        bg, mark, R.fmt_bonus(s["bonus"]), _e(s["nom"]), _e(R.ABBR.get(s["carac"], s["carac"]))))
    skills = "<table width='100%' cellspacing='0' cellpadding='1'>{}</table>".format("".join(rows))
    legend = "<p class='small mut'>&#9670; maîtrise &nbsp; &#10070; expertise</p>"
    return section("Jets de sauvegarde") + saves + section("Compétences") + skills + legend


def _proficiencies(eng) -> str:
    ch = eng.ch
    tools = list(dict.fromkeys(list(ch.outils or []) + eng.granted_tools()))
    langs = ", ".join(list(ch.langues_liste or []) + ([ch.langues] if ch.langues else []))
    return section("Maîtrises et langues") + (
        "<p class='small'><b>Armures</b> : {}<br/><b>Armes</b> : {}<br/><b>Outils</b> : {}<br/><b>Langues</b> : {}</p>"
        .format(_e(", ".join(eng.armor_proficiencies()) or "—"), _e(", ".join(eng.weapon_proficiencies()) or "—"),
                _e(", ".join(tools) or "—"), _e(langs or "—")))


def _attacks(eng) -> tuple[str, int]:
    rows = []
    for key in ("armes_cac", "armes_distance"):
        for slot in getattr(eng.ch, key, []) or []:
            st = eng.weapon_stats(slot) if slot.get("nom") else None
            if st:
                rows.append((st.get("affichage", st["nom"]), R.fmt_bonus(st["attaque"]),
                             "{} {}".format(st["degats"], st["type_degats"]), st.get("botte", "")))
    for c in eng.ch.sorts_mineurs or []:
        st = eng.cantrip_stats(c.get("nom", "")) if c.get("nom") else None
        if st and st.get("degats"):
            rows.append((st["nom"] + " (tour de magie)", "—", "{} {}".format(st["degats"], st.get("type_degats", "")),
                         ""))
    body = "".join("<tr{}><td><b>{}</b>{}</td><td align='center'>{}</td><td>{}</td></tr>".format(
        " bgcolor='{}'".format(SHADE) if i % 2 else "", _e(n), " <span class='mut small'>(botte : {})</span>".format(
            _e(b)) if b else "", _e(a), _e(d)) for i, (n, a, d, b) in enumerate(rows)) or \
        "<tr><td colspan='3' class='mut'>Aucune arme équipée</td></tr>"
    table = ("<table width='100%' cellspacing='0' cellpadding='2'><tr><th align='left' class='lab'>Arme / sort</th>"
             "<th class='lab'>Toucher</th><th align='left' class='lab'>Dégâts</th></tr>{}</table>").format(body)
    return section("Attaques") + table, len(rows)


def _all_features(eng) -> list[tuple[str, str, str]]:
    """[(nom, origine, texte)] : aptitudes de classe actives, traits d'espèce, dons."""
    out = []
    for e in eng.ch.classes:
        for f in eng.features(e):
            if f.get("debloque") and eng.feature_allowed(f["nom"]) and re.search(r"\w", f["nom"]) and \
                    not norm(f["nom"]).startswith(SKIP_FEATURES):
                out.append((f["nom"], "{} {}".format(e["nom"], f["niveau"]), f.get("description", "")))
    for c in eng.race_capacities():
        if c.get("nom") and not norm(c["nom"]).startswith(("taille", "caracteristiques", "augmentation")):
            out.append((c["nom"], eng.ch.race, c.get("description", "")))
    for f in dict.fromkeys(eng.chosen_feats()):
        out.append((f, "Don", (eng.db.feats.get(f) or {}).get("description", "")))
    return out


def _feature_list(items, limit: int) -> str:
    return "".join("<p style='margin: 1px 0 3px 0'><b>&#9670; {}</b> <span class='mut small'>({})</span><br/>"
                   "<span class='small'>{}</span></p>".format(_e(n), _e(o), _e(_short(t, limit)))
                   for n, o, t in items)


def _page1(eng) -> tuple[str, list]:
    attacks, n_att = _attacks(eng)
    feats = _all_features(eng)
    budget = max(6, 20 - n_att)                          # aptitudes qui tiennent à côté des compétences
    first, rest = feats[:budget], feats[budget:]
    right = attacks + section("Aptitudes et traits") + _feature_list(first, 165) + (
        "<p class='mut small' align='right'>Suite au verso &#9670;</p>" if rest else _personality(eng))
    left = _saves_and_skills(eng) + _proficiencies(eng) + _equipment(eng, limit=12)
    body = ("<table width='100%' cellspacing='0' cellpadding='4'><tr><td width='34%'>{}</td>"
            "<td width='66%'>{}</td></tr></table>").format(left, right)
    return _header(eng) + _abilities(eng) + _combat_row(eng) + body, rest


def _header_small(eng) -> str:
    return ("<table width='100%' cellspacing='0' cellpadding='4'><tr><td bgcolor='{}'><font color='{}'>"
            "<b><span style='font-variant: small-caps; font-size: 12pt'>{}</span></b> &nbsp;&#9670;&nbsp; {}"
            "</font></td></tr></table>").format(INK, PAPER, _e(eng.ch.nom or "Sans nom"), _e(" / ".join(
                "{} {}".format(c["nom"], c["niveau"]) for c in eng.ch.classes)))


def _equipment(eng, limit: int = 0) -> str:
    ch = eng.ch
    items = [(i["nom"], int(i.get("qte", 1) or 1)) for i in ch.equipement if i.get("nom")]
    more = len(items) - limit if limit and len(items) > limit else 0
    if more:
        items = items[:limit] + [("… et {} autre(s) objet(s)".format(more), 1)]
    rows = "".join("<tr{}><td>{}</td><td align='right'>{}</td></tr>".format(
        " bgcolor='{}'".format(SHADE) if k % 2 else "", _e(n), q if q > 1 else "") for k, (n, q) in enumerate(items))
    table = ("<table width='100%' cellspacing='0' cellpadding='1'>{}</table>".format(rows) if rows
             else "<p class='small mut'>—</p>")
    coins = [(k, int(v or 0)) for k, v in (ch.pieces or {}).items()]
    purse = "<table width='100%' cellspacing='4'><tr>{}</tr></table>".format("".join(
        _stat(k.upper(), v) for k, v in coins)) if coins else ""
    magic = [m.get("nom", "") for m in ch.objets_magiques if m.get("nom")]
    out = section("Équipement") + table + section("Bourse") + purse
    if magic:
        out += section("Objets magiques") + "<p class='small'>{}</p>".format(_e(", ".join(magic)))
    return out


def _personality(eng) -> str:
    return section("Personnalité") + "<p class='small'>{}</p>".format(_e(_short(eng.ch.traits, 900)) or "—")


def _story(eng) -> str:
    ch = eng.ch
    out = ""
    if ch.histoire:
        out += section("Histoire") + "<p class='small'>{}</p>".format(_e(_short(ch.histoire, 1800)))
    if ch.notes:
        out += section("Notes") + "<p class='small'>{}</p>".format(_e(_short(ch.notes, 900)))
    return out


def _note_lines(n: int) -> str:
    rows = "".join("<tr><td style='border-bottom: 1px solid #999999'>&nbsp;</td></tr>" for _ in range(n))
    return section("Notes de campagne") + "<table width='100%' cellspacing='0' cellpadding='3'>{}</table>".format(rows)


def _page2(eng, rest: list) -> str:
    out = [_header_small(eng)]
    if rest:
        out.append(section("Aptitudes et traits (suite)") + _feature_list(rest, 260) + _personality(eng))
    out.append(_story(eng))
    grimoire = _grimoire(eng)
    out.append(grimoire)
    out.append(_note_lines(max(6, 34 - 3 * len(rest) - grimoire.count("<tr"))))
    return "".join(out)


def _grimoire(eng) -> str:
    casters = eng.casters()
    names = eng.known_spell_names()
    if not casters and not names:
        return ""
    out = [section("Grimoire")]
    if casters:
        cells = []
        for c in casters:
            cells += [_stat("DD des sorts — " + c["classe"], c["dc"]),
                      _stat("Attaque de sort", _e(R.fmt_bonus(c["attaque"]))),
                      _stat("Caractéristique", _e(c["carac"][:3].upper()), _e(c["carac"]))]
        out.append("<table cellspacing='4'><tr>{}</tr></table>".format("".join(cells)))
    slots = eng.spell_slots()
    count, plvl = eng.pact()
    by_level: dict[int, list[dict]] = {}
    for n in list(dict.fromkeys([c.get("nom") for c in eng.ch.sorts_mineurs or [] if c.get("nom")] + names)):
        sp = eng.db.find_spell(n)
        if sp:
            by_level.setdefault(int(sp.get("niveau") or 0), []).append(sp)
    rows = []
    for lvl in sorted(set(by_level) | {i + 1 for i, n in enumerate(slots) if n}):
        boxes = "&#9671;" * slots[lvl - 1] if 0 < lvl <= len(slots) and slots[lvl - 1] else ""
        rows.append("<tr><td colspan='6' bgcolor='{}'><font color='{}'><b>{}</b> {}</font></td></tr>".format(
            INK, PAPER, "Tours de magie" if lvl == 0 else "Niveau {}".format(lvl),
            "&nbsp; emplacements {}".format(boxes) if boxes else ""))
        for i, sp in enumerate(sorted(by_level.get(lvl, []), key=lambda s: norm(s["nom"]))):
            rows.append("<tr{}><td><b>{}</b></td><td>{}</td><td>{}</td><td>{}</td><td align='center'>{}</td>"
                        "<td align='center'>{}</td></tr>".format(
                            " bgcolor='{}'".format(SHADE) if i % 2 else "", _e(sp["nom"]), _e(sp.get("temps", "")),
                            _e(sp.get("portee", "")), _e(_short(sp.get("duree", ""), 40)),
                            "&#9670;" if sp.get("concentration") else "", "&#9670;" if sp.get("rituel") else ""))
    out.append("<table width='100%' cellspacing='0' cellpadding='2'><tr><th align='left' width='34%' class='lab'>"
               "Sort</th><th align='left' width='16%' class='lab'>Temps</th><th align='left' width='14%' class='lab'>"
               "Portée</th><th align='left' width='28%' class='lab'>Durée</th><th width='4%' class='lab'>C</th>"
               "<th width='4%' class='lab'>R</th></tr>{}</table>".format("".join(rows)))
    if count:
        out.append("<p class='small'><b>Magie de pacte</b> : {} emplacement(s) de niveau {} &nbsp;{}</p>".format(
            count, plvl, "&#9671;" * count))
    out.append("<p class='small mut'>C : concentration &nbsp;·&nbsp; R : rituel &nbsp;·&nbsp; &#9671; emplacement à "
               "cocher</p>")
    return "".join(out)




def sheet_html(eng) -> str:
    """Fiche complète en HTML : recto (identité, caractéristiques, combat, compétences, aptitudes), puis verso
    (suite des aptitudes, équipement, personnalité, grimoire, notes)."""
    with eng.batch():
        page1, rest = _page1(eng)
        page2 = _page2(eng, rest)
    br = "<div style='page-break-before: always'></div>"
    return "<html><head><style>{}</style></head><body>{}{}</body></html>".format(CSS, page1, br + page2)
