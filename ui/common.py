"""Utilitaires partagés par tous les onglets : widgets centrés, cellules de tableau, info-bulles."""
from __future__ import annotations

import html
from contextlib import contextmanager
from typing import Callable, Iterable, Optional

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (QAbstractItemView, QCheckBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QStyle,
                             QStyledItemDelegate, QTableWidget, QTableWidgetItem, QWidget)

CENTER = Qt.AlignmentFlag.AlignCenter
LEFT = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft


@contextmanager
def blocked(*widgets: QWidget):
    """Bloque temporairement les signaux de plusieurs widgets (évite les boucles de rafraîchissement)."""
    for w in widgets:
        w.blockSignals(True)
    try:
        yield
    finally:
        for w in widgets:
            w.blockSignals(False)


_TIP_TAGS = ("<br/>", "<br>", "<b>", "</b>", "<i>", "</i>", "<u>", "</u>", "<small>", "</small>")


def tip_text(text: str) -> str:
    """
    Texte d'infobulle sûr : tout est échappé, puis seules quelques balises de mise en forme sont rétablies
    (<br/>, <b>, <i>…) et les retours à la ligne deviennent <br/> — plus aucune balise brute affichée.
    """
    out = html.escape(text or "")
    for tag in _TIP_TAGS:
        out = out.replace(html.escape(tag), tag)
    return out.replace("\n", "<br/>")


def rich_tip(title: str, text: str) -> str:
    """Info-bulle HTML (retour à la ligne automatique) : titre en gras + description mise en forme."""
    return "<qt><b>{}</b><br/>{}</qt>".format(html.escape(title), tip_text(text))


def calc_tip(title: str, rows: list, total: str = "", notes: Optional[list] = None) -> str:
    """
    Infobulle « style Pathfinder » : détail ligne à ligne du calcul (source → valeur), total, puis remarques
    (avantage, désavantage...). Fond opaque (QSS QToolTip).
    """
    body = "".join("<tr><td>{}</td><td align='right'><b>{}</b></td></tr>".format(html.escape(str(a)), html.escape(str(b)))
                   for a, b in rows)
    if total != "":
        body += "<tr><td colspan='2'><hr/></td></tr><tr><td><b>Total</b></td><td align='right'><b>{}</b></td></tr>".format(
            html.escape(str(total)))
    extra = "".join("<p style='margin:2px 0'>{}</p>".format(html.escape(n)) for n in (notes or []))
    return "<qt><b>{}</b><table cellspacing='0' cellpadding='2' width='100%'>{}</table>{}</qt>".format(
        html.escape(title), body, extra)


def adv_badge(state: str) -> tuple[str, str]:
    """(texte du badge, rôle de couleur) pour un état avantage / désavantage / échec automatique."""
    return {"avantage": ("▲ Avantage", "good"), "désavantage": ("▼ Désavantage", "warn"),
            "échec": ("✖ Échec auto", "warn")}.get(state, ("", ""))


def formula_tip(engine, title: str, text: str, class_name: str = "") -> str:
    """Info-bulle dont les formules sont évaluées pour le personnage (« 1d10 + 5 (niveau de guerrier) »)."""
    from core.formulas import annotate
    return rich_tip(title, annotate(text, engine.formula_context(class_name)))


def formula_html(engine, text: str, class_name: str = "") -> str:
    """Description HTML dont les valeurs calculées sont mises en évidence (gras, couleur d'accent)."""
    from core.formulas import annotate_html
    from . import theme
    return annotate_html(text, engine.formula_context(class_name), theme.current().accent_text)


def set_combo_text(combo, text: str) -> None:
    idx = combo.findText(text)
    combo.setCurrentIndex(idx if idx >= 0 else 0)


def fill_combo(combo, items: Iterable[str], current: str = "", tips: Optional[dict[str, str]] = None) -> None:
    """Remplit un QComboBox seulement si son contenu a changé, puis sélectionne `current` (+ info-bulles par entrée)."""
    items = list(items)
    with blocked(combo):
        if [combo.itemText(i) for i in range(combo.count())] != items:
            combo.clear()
            combo.addItems(items)
            if tips:
                for i, name in enumerate(items):
                    if name in tips:
                        combo.setItemData(i, tips[name], Qt.ItemDataRole.ToolTipRole)
        set_combo_text(combo, current)


def make_label(text: str = "", role: str = "", wrap: bool = False, align=None) -> QLabel:
    lab = QLabel(text)
    if role:
        lab.setProperty("role", role)
    lab.setWordWrap(wrap)
    if align is not None:
        lab.setAlignment(align)
    return lab


def center(text: str = "", role: str = "") -> QLabel:
    """Étiquette centrée horizontalement et verticalement (colonnes numériques des grilles)."""
    return make_label(text, role, align=CENTER)


def head(text: str) -> QLabel:
    """Intitulé de colonne de grille : centré, couleur d'accent."""
    return make_label(text, "head", align=CENTER)


def indicator_qss(t, selector: str = "QCheckBox") -> str:
    """Cases à cocher bien visibles quel que soit le thème (v34) : 20 px, bordure contrastée, intérieur plein et
    coche « ✔ » simulée par un fond d'accent une fois cochée. `selector` : QCheckBox ou QListWidget."""
    ind = "{}::indicator".format(selector)
    return ("{sel} {{ color: {txt}; spacing: 8px; }}"
            "{ind} {{ width: 18px; height: 18px; border: 2px solid {brd}; border-radius: 4px; background: {bg}; }}"
            "{ind}:hover {{ border-color: {acc}; }}"
            "{ind}:checked {{ background: {acc}; border-color: {acc}; }}").format(
        sel=selector, ind=ind, txt=t.text, brd=t.ornament or t.border, bg=t.input_bg, acc=t.accent_text)


def hline() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    return line


# --------------------------------------------------------------------------------------
# Tableaux : cellules et cases à cocher parfaitement centrées
# --------------------------------------------------------------------------------------
USER_ROLE = 0x0100                                  # valeur de Qt.ItemDataRole.UserRole
CHECK_ROLE = USER_ROLE + 41                         # True / False : la cellule est une case à cocher dessinée
CHECK_ENABLED_ROLE = USER_ROLE + 42


class CheckDelegate(QStyledItemDelegate):
    """
    Case à cocher vectorielle, centrée et aux couleurs du thème, dessinée directement dans la cellule.
    Avantages : TOUTE la cellule est cliquable (le clic est géré par le tableau via `cellClicked`) et aucun widget
    n'est créé par ligne, ce qui rend les tableaux instantanés même avec beaucoup de lignes.
    """

    def paint(self, painter, option, index):
        value = index.data(CHECK_ROLE)
        super().paint(painter, option, index)            # fond (sélection, lignes alternées, survol)
        if value is None:
            return
        from . import theme
        t = theme.current()
        enabled = index.data(CHECK_ENABLED_ROLE) is not False
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
        size = max(12.0, min(option.rect.height() - 12.0, 20.0))
        c = QRectF(option.rect).center()
        box = QRectF(c.x() - size / 2, c.y() - size / 2, size, size)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        fill = QColor(t.button_bg if value else t.input_bg)
        border = QColor(t.accent_text if (hovered and enabled) else (t.ornament if value else t.border))
        if not enabled:
            fill.setAlpha(70)
            border = QColor(t.locked)
        painter.setPen(QPen(border, 2.0 if hovered and enabled else 1.6))
        painter.setBrush(fill)
        painter.drawRoundedRect(box, 4, 4)
        if value:
            pen = QPen(QColor(t.button_text if enabled else t.locked), 2.4)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            path = QPainterPath(QPointF(box.left() + size * 0.22, box.top() + size * 0.52))
            path.lineTo(QPointF(box.left() + size * 0.42, box.top() + size * 0.72))
            path.lineTo(QPointF(box.left() + size * 0.78, box.top() + size * 0.30))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
        painter.restore()


def check_item(checked: bool, enabled: bool = True, tip: str = "") -> QTableWidgetItem:
    """Cellule « case à cocher » dessinée par `CheckDelegate` (pas de widget). Le clic se gère avec `cellClicked`."""
    it = QTableWidgetItem("")
    it.setFlags(Qt.ItemFlag.ItemIsEnabled)
    it.setData(CHECK_ROLE, bool(checked))
    it.setData(CHECK_ENABLED_ROLE, bool(enabled))
    it.setTextAlignment(CENTER)
    if tip:
        it.setToolTip(tip)
    return it


def style_table(table: QTableWidget, stretch_col: Optional[int] = 0, row_h: int = 32) -> QTableWidget:
    """Réglages communs : en-têtes centrés, lignes alternées, hauteur uniforme, pas d'édition directe."""
    hh = table.horizontalHeader()
    hh.setDefaultAlignment(CENTER)
    hh.setHighlightSections(False)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(row_h)
    table.setAlternatingRowColors(True)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setShowGrid(True)
    table.setMouseTracking(True)                        # survol des cases à cocher dessinées
    table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)      # défilement fluide
    table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    table.setItemDelegate(CheckDelegate(table))
    if stretch_col is not None:
        for c in range(table.columnCount()):
            hh.setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch if c == stretch_col
                                    else QHeaderView.ResizeMode.ResizeToContents)
    return table


def cell(text: str, align: str = "center", tip: str = "", color: Optional[str] = None, bold: bool = False,
         selectable: bool = True) -> QTableWidgetItem:
    """Cellule de tableau en lecture seule. align : 'center' (valeurs, titres courts) ou 'left' (noms, textes)."""
    from PyQt6.QtGui import QBrush, QColor, QFont
    it = QTableWidgetItem(text)
    flags = Qt.ItemFlag.ItemIsEnabled
    if selectable:
        flags |= Qt.ItemFlag.ItemIsSelectable
    it.setFlags(flags)
    it.setTextAlignment(CENTER if align == "center" else LEFT)
    if tip:
        it.setToolTip(tip)
    if color:
        it.setForeground(QBrush(QColor(color)))
    if bold:
        f = QFont(it.font())
        f.setBold(True)
        it.setFont(f)
    return it


def check_cell(checked: bool, enabled: bool = True, on_toggle: Optional[Callable[[bool], None]] = None,
               tip: str = "") -> tuple[QWidget, QCheckBox]:
    """
    Case à cocher centrée dans une cellule (un QTableWidgetItem cochable resterait collé à gauche).
    À placer avec `table.setCellWidget(row, col, container)`.
    """
    box = QCheckBox()
    box.setChecked(checked)
    box.setEnabled(enabled)
    if tip:
        box.setToolTip(tip)
    if on_toggle is not None:
        box.toggled.connect(on_toggle)
    holder = QWidget()
    lay = QHBoxLayout(holder)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setAlignment(CENTER)
    lay.addWidget(box)
    return holder, box


class BaseTab(QWidget):
    """Classe de base d'un onglet : accès au moteur via la fenêtre principale."""

    def __init__(self, win):
        super().__init__()
        self.win = win

    @property
    def engine(self):
        return self.win.engine

    def mark_box(self, box, base: str, tab: str, encart: str) -> int:
        """Titre d'encart suivi du reste à faire (« Compétences — 2 à choisir ») — v28, choix manquants."""
        n = self.engine.missing_in(tab, encart)
        box.setTitle(base + ("  — ○ {} à choisir".format(n) if n else ""))
        return n

    @property
    def ch(self):
        return self.win.engine.ch

    @property
    def db(self):
        """Base de règles de la fiche ouverte (v52 : vue 2024 pour une fiche 2024, voir Engine.db)."""
        eng = getattr(self.win, "engine", None)
        return eng.db if eng is not None else self.win.db

    def changed(self) -> None:
        self.win.changed()

    def refresh(self) -> None:  # pragma: no cover - implémenté par les sous-classes
        raise NotImplementedError


class DamageLabel(QLabel):
    """
    Libellé de dégâts cliquable (« 1d8+3 tranchant ») : un clic lance l'animation multi-dés.
    `formula` vide (pas de dé) -> libellé inerte.
    """
    clicked = pyqtSignal()

    def __init__(self, text: str = "", role: str = "stat"):
        super().__init__(text)
        self.setProperty("role", role)
        self.formula = ""
        self.set_formula("")

    def set_formula(self, formula: str, tip: str = "") -> None:
        from core import dice as D
        self.formula = formula if D.has_dice(formula or "") else ""
        live = bool(self.formula)
        self.setProperty("clickable", "true" if live else "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor if live else Qt.CursorShape.ArrowCursor)
        self.setToolTip(("<qt><b>🎲 Lancer les dégâts : {}</b><br/>Cliquez pour lancer les dés animés ; le total "
                         "s'ajoute au bonus fixe.{}</qt>".format(html.escape(self.formula),
                                                                  ("<br/>" + tip) if tip else "")) if live else tip)
        style = self.style()
        if style is not None:
            try:
                style.unpolish(self)
                style.polish(self)
            except (AttributeError, TypeError):
                pass

    def mousePressEvent(self, event):  # noqa: N802
        if self.formula and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        else:
            super().mousePressEvent(event)
