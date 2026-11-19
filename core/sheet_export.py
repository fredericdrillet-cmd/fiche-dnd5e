"""
Fiche imprimable (v52) — HTML pur (aucune dépendance Qt), converti en PDF par l'interface (ui/pdf_export.py).

Organisation inspirée de la fiche de personnage classique (mise en page originale) :
- page 1 : identité ; caractéristiques, inspiration, maîtrise, jets de sauvegarde, compétences, perception passive
  (colonne gauche) ; CA, initiative, vitesse, PV, dés de vie, jets contre la mort, attaques (centre) ; personnalité
  et maîtrises / langues (droite) ;
- page 2 : aptitudes et traits (texte court), dons, équipement et argent ;
- page 3 (lanceurs de sorts) : caractéristique, DD, attaque, emplacements, sorts par niveau.
Lisible en noir et blanc : uniquement des traits, du gris clair et du texte.
"""
from __future__ import annotations

import html
import re

from . import rules as R
from .rules import ABILITIES, norm

CSS = """
body { font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 8.5pt; color: #000; }
h1 { font-size: 15pt; margin: 0; }
h2 { font-size: 10pt; margin: 6px 0 3px 0; border-bottom: 1px solid #000; }
table { border-collapse: collapse; }
td, th { padding: 2px 4px; vertical-align: top; }
.box { border: 1px solid #000; }
.big { font-size: 15pt; font-weight: bold; text-align: center; }
.lab { font-size: 7pt; color: #444; text-align: center; }
.muted { color: #444; }
.grey { background: #eeeeee; }
"""


def _e(text) -> str:
    return html.escape(str(text if text is not None else ""))


def _short(text: str, limit: int = 230) -> str:
    t = re.sub(r"\s+", " ", text or "").strip()
    return t if len(t) <= limit else t[:limit].rsplit(" ", 1)[0] + "…"


def _box(label: str, value, width: str = "") -> str:
    w = " width='{}'".format(width) if width else ""
    return "<td class='box'{}><div class='big'>{}</div><div class='lab'>{}</div></td>".format(w, _e(value), _e(label))


def _identity(eng) -> str:
    ch = eng.ch
    classes = " / ".join("{} {}{}".format(c["nom"], c["niveau"], " ({})".format(c["sous_classe"]) if
                                          c.get("sous_classe") else "") for c in ch.classes)
    cells = [("Classe et niveau", classes), ("Historique", ch.historique), ("Joueur", ch.joueur),
             ("Espèce", ch.race + (" ({})".format(ch.sous_race) if ch.sous_race else "")),
             ("Alignement", ch.alignement), ("Expérience", ch.experience),
             ("Édition", "D&D 5e {}".format(eng.sheet_edition))]
    row = "".join("<td class='box'><b>{}</b><br/><span class='lab'>{}</span></td>".format(_e(v), _e(k))
                  for k, v in cells)
    portrait = "<td rowspan='2' width='90'><img src='portrait.png' width='85'/></td>" if ch.portrait else ""
    return ("<table width='100%'><tr><td colspan='7'><h1>{}</h1></td>{}</tr><tr>{}</tr></table>"
            .format(_e(ch.nom or "Sans nom"), portrait, row))


def _left_column(eng) -> str:
    rows = "".join("<tr><td class='box' width='34'><div class='big'>{}</div><div class='lab'>mod.</div></td>"
                   "<td class='box' width='88'><div class='big'>{}</div><div class='lab'>{}</div></td></tr>"
                   .format(R.fmt_bonus(eng.mod(ab)), eng.score(ab), _e(ab)) for ab in ABILITIES)
    saves = "".join("<tr><td>{}</td><td align='right'>{}</td><td>{}</td></tr>".format(
        "●" if s["maitrise"] else "○", R.fmt_bonus(s["bonus"]), _e(s["carac"])) for s in eng.save_rows())
    skills = "".join("<tr><td>{}</td><td align='right'>{}</td><td>{} <span class='muted'>({})</span></td></tr>"
                     .format("◆" if s["expertise"] else "●" if s["maitrise"] else "○", R.fmt_bonus(s["bonus"]),
                             _e(s["nom"]), _e(R.ABBR.get(s["carac"], s["carac"])))
                     for s in eng.skill_rows())
    return ("<table>{}</table><table width='100%'><tr>{}{}</tr></table><h2>Jets de sauvegarde</h2><table>{}</table>"
            "<h2>Compétences</h2><table>{}</table><p><b>Perception passive : {}</b></p>").format(
        rows, _box("Inspiration", "✔" if eng.ch.inspiration else ""), _box("Bonus de maîtrise",
                                                                         R.fmt_bonus(eng.prof)),
        saves, skills, eng.passive_perception())


def _attacks(eng) -> str:
    rows = []
    for key in ("armes_cac", "armes_distance"):
        for slot in getattr(eng.ch, key, []) or []:
            st = eng.weapon_stats(slot) if slot.get("nom") else None
            if st:
                rows.append("<tr><td>{}</td><td align='center'>{}</td><td>{} {}</td></tr>".format(
                    _e(st.get("affichage", st["nom"])), R.fmt_bonus(st["attaque"]), _e(st["degats"]),
                    _e(st["type_degats"])))
    for c in eng.ch.sorts_mineurs or []:
        st = eng.cantrip_stats(c.get("nom", "")) if c.get("nom") else None
        if st and st.get("degats"):
            rows.append("<tr><td>{} <span class='muted'>(tour de magie)</span></td><td align='center'>—</td>"
                        "<td>{} {}</td></tr>".format(_e(st["nom"]), _e(st["degats"]), _e(st.get("type_degats", ""))))
    if not rows:
        rows.append("<tr><td colspan='3' class='muted'>Aucune arme équipée</td></tr>")
    return ("<h2>Attaques et sorts offensifs</h2><table width='100%'><tr class='grey'><th align='left'>Nom</th>"
            "<th>Toucher</th><th align='left'>Dégâts / type</th></tr>{}</table>").format("".join(rows))


def _middle_column(eng) -> str:
    ch = eng.ch
    hp_cur = ch.pv_actuels if ch.pv_actuels >= 0 else eng.hp_max()
    dice = ", ".join("{} {}".format(n, d) for d, n in eng.hit_dice().items())
    death = "Réussites {} · Échecs {}".format("●" * ch.mort_reussites + "○" * (3 - ch.mort_reussites),
                                              "●" * ch.mort_echecs + "○" * (3 - ch.mort_echecs))
    return ("<table width='100%'><tr>{}{}{}</tr></table>"
            "<table width='100%'><tr>{}{}{}</tr></table>"
            "<p><b>Dés de vie :</b> {} &nbsp; <b>Jets contre la mort :</b> {}</p>{}").format(
        _box("Classe d'armure", eng.armor_class()[0]), _box("Initiative", R.fmt_bonus(eng.initiative_detail()["total"])),
        _box("Vitesse", eng.speed_text()), _box("PV maximum", eng.hp_max()), _box("PV actuels", hp_cur),
        _box("PV temporaires", ch.pv_temporaires or ""), _e(dice), death, _attacks(eng))


def _right_column(eng) -> str:
    ch = eng.ch
    tools = list(dict.fromkeys(list(ch.outils or []) + eng.granted_tools()))
    langs = ", ".join([x for x in (ch.langues_liste or [])] + ([ch.langues] if ch.langues else []))
    parts = ["<h2>Personnalité</h2><p>{}</p>".format(_e(_short(ch.traits, 600)) or "<span class='muted'>—</span>"),
             "<h2>Maîtrises et langues</h2>",
             "<p><b>Armures :</b> {}<br/><b>Armes :</b> {}<br/><b>Outils :</b> {}<br/><b>Langues :</b> {}</p>".format(
                 _e(", ".join(eng.armor_proficiencies()) or "—"), _e(", ".join(eng.weapon_proficiencies()) or "—"),
                 _e(", ".join(tools) or "—"), _e(langs or "—"))]
    return "".join(parts)


def _features_page(eng) -> str:
    ch = eng.ch
    out = ["<h2>Aptitudes et traits</h2>"]
    for e in ch.classes:
        feats = [f for f in eng.features(e) if f.get("debloque") and eng.feature_allowed(f["nom"])
                 and not norm(f["nom"]).startswith(("amelioration de caracteristique", "capacite de sous-classe",
                                                    "aptitude de sous-classe", "sous-classe de"))]
        out.append("<p><b>{} {}</b></p>".format(_e(e["nom"]), e["niveau"]))
        out += ["<p>• <b>{}</b> (niv. {}) — {}</p>".format(_e(f["nom"]), f["niveau"], _e(_short(f["description"])))
                for f in feats]
    caps = eng.race_capacities()
    if caps:
        out.append("<p><b>Espèce : {}</b></p>".format(_e(ch.race)))
        out += ["<p>• <b>{}</b> — {}</p>".format(_e(c.get("nom", "")), _e(_short(c.get("description", ""))))
                for c in caps if c.get("nom")]
    feats = list(dict.fromkeys(eng.chosen_feats()))
    if feats:
        out.append("<h2>Dons</h2>")
        out += ["<p>• <b>{}</b> — {}</p>".format(_e(f), _e(_short((eng.db.feats.get(f) or {}).get("description", ""))))
                for f in feats]
    items = ["{} ×{}".format(i["nom"], i.get("qte", 1)) if int(i.get("qte", 1) or 1) > 1 else i["nom"]
             for i in ch.equipement if i.get("nom")]
    magic = [m.get("nom", "") for m in ch.objets_magiques if m.get("nom")]
    coins = ", ".join("{} {}".format(v, k) for k, v in (ch.pieces or {}).items() if v)
    out.append("<h2>Équipement</h2><p>{}</p>".format(_e(", ".join(items) or "—")))
    if magic:
        out.append("<p><b>Objets magiques :</b> {}</p>".format(_e(", ".join(magic))))
    out.append("<p><b>Argent :</b> {}</p>".format(_e(coins or "—")))
    return "".join(out)


def _spells_page(eng) -> str:
    casters = eng.casters()
    names = eng.known_spell_names()
    if not casters and not names:
        return ""
    out = ["<h2>Sorts</h2>"]
    for c in casters:
        out.append("<p><b>{}</b> — caractéristique : {} · DD {} · attaque {}</p>".format(
            _e(c["classe"]), _e(c["carac"]), c["dc"], R.fmt_bonus(c["attaque"])))
    slots = eng.spell_slots()
    if any(slots):
        out.append("<p><b>Emplacements :</b> {}</p>".format(" · ".join(
            "niv. {} : {}".format(i + 1, n) for i, n in enumerate(slots) if n)))
    count, plvl = eng.pact()
    if count:
        out.append("<p><b>Magie de pacte :</b> {} emplacement(s) de niveau {}</p>".format(count, plvl))
    by_level: dict[int, list[dict]] = {}
    for n in list(dict.fromkeys([c.get("nom") for c in eng.ch.sorts_mineurs or [] if c.get("nom")] + names)):
        sp = eng.db.find_spell(n)
        if sp:
            by_level.setdefault(int(sp.get("niveau") or 0), []).append(sp)
    rows = []
    for lvl in sorted(set(by_level) | {i + 1 for i, n in enumerate(slots) if n}):
        boxes = "○" * slots[lvl - 1] if 0 < lvl <= len(slots) and slots[lvl - 1] else ""
        rows.append("<tr class='grey'><td colspan='6'><b>{}</b>{}</td></tr>".format(
            "Tours de magie" if lvl == 0 else "Niveau {}".format(lvl),
            " — emplacements {}".format(boxes) if boxes else ""))
        rows += ["<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td align='center'>{}</td><td align='center'>{}"
                 "</td></tr>".format(_e(sp["nom"]), _e(sp.get("temps", "")), _e(sp.get("portee", "")),
                                     _e(_short(sp.get("duree", ""), 40)), "●" if sp.get("concentration") else "",
                                     "●" if sp.get("rituel") else "")
                 for sp in sorted(by_level.get(lvl, []), key=lambda s: norm(s["nom"]))]
    out.append("<table width='100%'><tr><th align='left' width='34%'>Sort</th><th align='left' width='16%'>Temps</th>"
               "<th align='left' width='14%'>Portée</th><th align='left' width='28%'>Durée</th><th width='4%'>C</th>"
               "<th width='4%'>R</th></tr>{}</table>".format("".join(rows)))
    out.append("<p class='muted'>C : concentration · R : rituel</p>")
    return "".join(out)


def sheet_html(eng) -> str:
    """Fiche complète en HTML (pages séparées par des sauts de page)."""
    with eng.batch():
        page1 = ("{}<table width='100%'><tr><td width='30%'>{}</td><td width='40%'>{}</td><td width='30%'>{}</td>"
                 "</tr></table>").format(_identity(eng), _left_column(eng), _middle_column(eng), _right_column(eng))
        page2 = _features_page(eng)
        page3 = _spells_page(eng)
    br = "<div style='page-break-before: always'></div>"
    return "<html><head><style>{}</style></head><body>{}{}{}{}</body></html>".format(
        CSS, page1, br + page2, br + page3 if page3 else "", "")
