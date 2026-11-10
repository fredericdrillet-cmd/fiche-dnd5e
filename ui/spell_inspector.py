"""
Inspecteur de sort (v49) : fiche détaillée affichée au CLIC simple dans les listes de sorts (assistant de création,
assistant de niveau) — école, temps d'incantation, portée, composantes, durée, concentration, rituel, texte complet.
Le double-clic et le bouton « Apprendre le sort » / « Préparer » font la même action.
"""
from __future__ import annotations

import html as _html

from PyQt6.QtWidgets import QTextBrowser

from . import theme


def _esc(text) -> str:
    return _html.escape(str(text), quote=False)


def spell_card_html(spell: dict | None) -> str:
    if not spell:
        return "<p><i>Cliquez sur un sort pour afficher sa fiche détaillée.</i></p>"
    t = theme.current()
    lvl = int(spell.get("niveau") or 0)
    head = "Tour de magie" if lvl == 0 else "Sort de niveau {}".format(lvl)
    rows = [("École", spell.get("ecole", "")), ("Temps d'incantation", spell.get("temps", "")),
            ("Portée", spell.get("portee", "")), ("Composantes", spell.get("composantes", "")),
            ("Durée", spell.get("duree", "")), ("Concentration", "oui" if spell.get("concentration") else "non"),
            ("Rituel", "oui" if spell.get("rituel") else "non")]
    table = "".join("<tr><td><b>{}</b></td><td>{}</td></tr>".format(_esc(a), _esc(str(b) or "—"))
                    for a, b in rows)
    classes = spell.get("classes") or []
    return ("<h3 style='color:{}'>{}</h3><p><i>{}{}</i></p><table cellpadding='2'>{}</table><p>{}</p>{}".format(
        t.accent_text, _esc(spell.get("nom", "")), head,
        " — {}".format(_esc(spell.get("ecole", ""))) if spell.get("ecole") else "", table,
        _esc(spell.get("description", "")).replace("\n", "<br/>"),
        "<p><i>Listes : {}</i></p>".format(_esc(", ".join(classes))) if classes else ""))


def make_inspector(min_height: int = 200) -> QTextBrowser:
    view = QTextBrowser()
    view.setMinimumHeight(min_height)
    view.setHtml(spell_card_html(None))
    return view
