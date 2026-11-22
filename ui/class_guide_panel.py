"""
Panneau pédagogique de classe (v49, inspiré de Baldur's Gate 3) — assistant de création et assistant de niveau.

    ┌ Concept · style de jeu ───────────────┐ ┌ Sous-classes (niveau N) ┐
    │ Mécaniques clés (puces)               │ │ ▸ Voleur — PHB          │  clic : la fiche de la
    │ Caractéristiques recommandées ⭐ / ✦   │ │ ▸ Assassin — PHB        │  sous-classe se déplie
    │ Dé de vie, sauvegardes, maîtrises     │ │ …                       │  dessous (accordéon)
    └───────────────────────────────────────┘ └─────────────────────────┘
                     Fiche de la sous-classe : niveau de déblocage, orientation, pouvoirs par niveau
"""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QTextBrowser, QVBoxLayout, QWidget

from . import theme
from .common import blocked, make_label, rich_tip

ROLE_BADGE = {"principale": "⭐ [Principale]", "secondaire": "✦ [Secondaire]"}


def class_guide_html(engine, cls: str, sub: str = "") -> str:
    g = engine.class_guide(cls)
    t = theme.current()
    recs = engine.ability_recommendations(cls, sub)
    out = ["<h2 style='color:{}'>{}</h2>".format(t.accent_text, html.escape(cls))]
    if g.get("concept"):
        out.append("<p><b>Concept :</b> {}</p>".format(html.escape(g["concept"])))
    if g.get("style"):
        out.append("<p><b>Style de jeu :</b> {}</p>".format(html.escape(g["style"])))
    if g.get("mecaniques"):
        out.append("<p><b>Mécaniques clés :</b></p><ul>" + "".join(
            "<li>{}</li>".format(html.escape(m)) for m in g["mecaniques"]) + "</ul>")
    if recs:
        out.append("<p><b>Caractéristiques recommandées{} :</b></p><ul>".format(
            " (avec {})".format(html.escape(sub)) if sub else "") + "".join(
            "<li>{} <b>{}</b> — {}</li>".format(ROLE_BADGE[role], html.escape(ab), html.escape(why))
            for ab, (role, why) in sorted(recs.items(), key=lambda kv: kv[1][0] != "principale")) + "</ul>")
    out.append("<p><i>Dé de vie {} · Sauvegardes : {} · Armures : {} · Armes : {}</i></p>".format(
        html.escape(g.get("de_vie", "")), html.escape(", ".join(g.get("sauvegardes", []))),
        html.escape(", ".join(g.get("armures", [])) or "aucune"), html.escape(", ".join(g.get("armes", [])) or "aucune")))
    out.append("<p><b>Sous-classe au niveau {}</b> — {} option(s) ; cliquez dans la liste pour la découvrir.</p>"
               .format(g["niveau_sous_classe"], len(g.get("sous_classes", []))))
    return "".join(out)


def subclass_html(engine, cls: str, sub: str) -> str:
    s = engine.subclass_summary(cls, sub)
    if not s:
        return ""
    t = theme.current()
    out = ["<h3 style='color:{}'>{}</h3>".format(t.accent_text, html.escape(s["nom"])),
           "<p><i>{} — débloquée au niveau {} de {}</i></p>".format(html.escape(s["source"]), s["niveau"],
                                                                   html.escape(cls))]
    if s["orientation"]:
        out.append("<p><b>Orientation :</b> {}</p>".format(" · ".join(html.escape(o) for o in s["orientation"])))
    if s["sorts"]:
        out.append("<p><b>Sorts accordés :</b> {}</p>".format(html.escape(", ".join(s["sorts"]))))
    out.append("<p><b>Pouvoirs principaux :</b></p><ul>" + "".join(
        "<li><b>Niv. {} — {}</b> : {}</li>".format(lvl, html.escape(name), html.escape(text))
        for lvl, name, text in s["pouvoirs"]) + "</ul>")
    recs = engine.ability_recommendations(cls, sub)
    extra = [(ab, why) for ab, (role, why) in recs.items() if role == "secondaire"]
    if extra:
        out.append("<p><b>Caractéristiques à surveiller :</b> " + " ; ".join(
            "{} ({})".format(html.escape(ab), html.escape(why)) for ab, why in extra) + "</p>")
    return "".join(out)


class ClassGuidePanel(QWidget):
    """Fiche de classe + liste des sous-classes ; un clic déplie la fiche de la sous-classe."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine, self.cls, self.sub = None, "", ""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        self.view = QTextBrowser()
        self.view.setMinimumHeight(260)
        top.addWidget(self.view, 3)
        side = QVBoxLayout()
        self.sub_title = make_label("Sous-classes", "head")
        side.addWidget(self.sub_title)
        self.subs = QListWidget()
        self.subs.setMinimumWidth(230)
        self.subs.itemClicked.connect(lambda it: self.show_subclass(it.data(Qt.ItemDataRole.UserRole)))
        side.addWidget(self.subs, 1)
        top.addLayout(side, 2)
        lay.addLayout(top)
        self.sub_view = QTextBrowser()
        self.sub_view.setMinimumHeight(160)
        self.sub_view.setVisible(False)
        lay.addWidget(self.sub_view)

    def set_class(self, engine, cls: str, sub: str = "") -> None:
        self.engine, self.cls = engine, cls
        self.view.setHtml(class_guide_html(engine, cls, sub))
        g = engine.class_guide(cls)
        self.sub_title.setText("Sous-classes — choix au niveau {}".format(g["niveau_sous_classe"]))
        with blocked(self.subs):
            self.subs.clear()
            for s in g["sous_classes"]:
                it = QListWidgetItem("▸ {} — {}".format(s["nom"], s["source"]))
                it.setData(Qt.ItemDataRole.UserRole, s["nom"])
                summ = engine.subclass_summary(cls, s["nom"]) or {}
                it.setToolTip(rich_tip(s["nom"], "Niveau {} — {}".format(s["niveau"], " · ".join(
                    summ.get("orientation", [])) or "voir la fiche")))
                self.subs.addItem(it)
        if sub:
            self.show_subclass(sub, toggle=False)
        elif self.sub and self.sub not in [s["nom"] for s in g["sous_classes"]]:
            self.show_subclass("")


    def show_subclass(self, name: str, toggle: bool = True) -> str:
        """Déplie (ou replie si on reclique) la fiche de la sous-classe. Renvoie le HTML affiché."""
        if not name or (toggle and name == self.sub and self.sub_view.isVisible() is True):
            self.sub = ""
            self.sub_view.setVisible(False)
            return ""
        self.sub = name
        text = subclass_html(self.engine, self.cls, name) if self.engine else ""
        self.sub_view.setHtml(text)
        self.sub_view.setVisible(bool(text))
        return text
