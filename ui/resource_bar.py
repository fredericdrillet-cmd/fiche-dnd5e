"""
Bandeau des ressources (v53), au-dessus des icônes du tour, façon jeu de rôle : un groupe par ressource (ki, dés de
supériorité, rage, conduit divin, emplacements de sorts par niveau, Magie des pactes…), une petite case par usage.
Case pleine = disponible, vide = dépensée ; un clic sur une case dépense ou récupère jusqu'à elle.
Les grandes réserves (Imposition des mains : 30 PV) s'affichent en nombre.
"""
from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from . import theme
from .game_widgets import clear_layout

MAX_SQUARES = 12                                         # au-delà : affichage numérique


class Squares(QWidget):
    """Rangée de cases cliquables (total, dépensées). on_change(nouvel_usage)."""

    SIZE, GAP = 13, 3

    def __init__(self, total: int, used: int, color: str, on_change: Callable[[int], None], tip: str = ""):
        super().__init__()
        self.total, self.used, self.color, self._cb = total, used, color, on_change
        self.setToolTip(tip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(self.sizeHint())

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(self.total * (self.SIZE + self.GAP) - self.GAP + 2, self.SIZE + 2)

    def paintEvent(self, _e) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        left = self.total - self.used
        for i in range(self.total):
            r = QRectF(1 + i * (self.SIZE + self.GAP), 1, self.SIZE, self.SIZE)
            p.setPen(QPen(QColor(self.color), 1.5))
            p.setBrush(QColor(self.color) if i < left else QColor(0, 0, 0, 90))
            p.drawRoundedRect(r, 2.5, 2.5)
        p.end()

    def mousePressEvent(self, e) -> None:  # noqa: N802
        i = int(e.position().x() // (self.SIZE + self.GAP))
        if not 0 <= i < self.total:
            return
        left = self.total - self.used
        new_left = i if i < left else i + 1               # clic sur une case pleine : dépenser jusqu'à elle
        self.used = self.total - max(0, min(self.total, new_left))
        self.update()
        self._cb(self.used)


class ResourceStrip(QWidget):
    """Bandeau complet : reconstruit seulement quand la liste des ressources change."""

    def __init__(self, tab):
        super().__init__()
        self.tab = tab
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(14)
        self._key = None
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    def groups(self) -> list[dict]:
        """[{cle, libelle, total, utilise, categorie, regle}] : ressources de classe, emplacements, pacte."""
        eng, ch = self.tab.engine, self.tab.ch
        out = []
        for t in eng.resource_trackers():
            if t.get("total") in (None, 0) or t.get("race") or t.get("where") == "interne":
                continue
            out.append({"cle": t["key"], "libelle": t["label"], "total": int(t["total"]),
                        "utilise": eng.resource_used(t["key"]), "categorie": "capacite",
                        "regle": "{} — {}".format(t.get("recover", ""), t.get("info", "")).strip(" —")})
        for i, n in enumerate(eng.spell_slots()):
            if n:
                out.append({"cle": "slot:{}".format(i), "libelle": "Niv. {}".format(i + 1), "total": int(n),
                            "utilise": int(ch.emplacements_utilises[i]), "categorie": "magie",
                            "regle": "Emplacements de sorts de niveau {} (repos long).".format(i + 1)})
        count, lvl = eng.pact()
        if count:
            out.append({"cle": "pacte", "libelle": "Pacte niv. {}".format(lvl), "total": int(count),
                        "utilise": int(ch.pacte_utilises), "categorie": "magie",
                        "regle": "Magie des pactes (repos court ou long)."})
        return out

    def refresh(self) -> None:
        groups = self.groups()
        key = tuple((g["cle"], g["total"], g["utilise"]) for g in groups) + (theme.current().key,)
        self.setVisible(bool(groups))
        if key == self._key:
            return
        self._key = key
        clear_layout(self.lay)
        pal = theme.icon_palette(theme.current())
        for g in groups:
            box = QWidget()
            h = QHBoxLayout(box)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(5)
            color = pal[g["categorie"]]["cadre"]
            lab = QLabel(g["libelle"])
            lab.setStyleSheet("color: {}; font-size: 11px;".format(color))
            h.addWidget(lab)
            tip = "<b>{}</b> : {} / {} disponibles<br/>{}<br/><i>Clic sur une case : dépenser ou récupérer.</i>".format(
                g["libelle"], g["total"] - g["utilise"], g["total"], g["regle"])
            if g["total"] <= MAX_SQUARES:
                h.addWidget(Squares(g["total"], g["utilise"], color, lambda used, k=g["cle"]: self._spend(k, used),
                                    tip))
            else:
                num = QLabel("{} / {}".format(g["total"] - g["utilise"], g["total"]))
                num.setStyleSheet("color: {}; font-weight: bold;".format(color))
                num.setToolTip(tip)
                h.addWidget(num)
            self.lay.addWidget(box)
        self.lay.addStretch(1)

    def _spend(self, key: str, used: int) -> None:
        tab = self.tab
        if key.startswith("slot:"):
            tab._on_slot_used(int(key[5:]), used)
        elif key == "pacte":
            tab._on_pact_used(used)
        else:
            tab.engine.set_resource_used(key, used)
        self._key = None
        tab.changed()
