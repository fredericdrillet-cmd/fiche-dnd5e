"""
Tuile déplaçable de l'onglet « En partie » (v53) : un clic utilise la tuile ; glisser une tuile sur une autre la
place avant (moitié gauche) ou après (moitié droite) — l'ordre est enregistré dans la fiche (`ordre_tuiles`).
"""
from __future__ import annotations

from PyQt6.QtCore import QMimeData, Qt
from PyQt6.QtWidgets import QApplication, QToolButton

MIME_TILE = "application/x-dnd5e-tuile"


def reorder(saved: list, shown: list, src: str, dst: str, after: bool) -> list:
    """Nouvel ordre enregistré : `src` déplacée avant / après `dst` parmi les tuiles affichées (`shown`) ; les tuiles
    masquées (filtre) gardent leur place dans l'ordre enregistré."""
    if src == dst or src not in shown or dst not in shown:
        return list(saved)
    order = [i for i in shown if i != src]
    order.insert(order.index(dst) + (1 if after else 0), src)
    base = list(dict.fromkeys(list(saved) + [i for i in shown if i not in saved]))
    visible = set(shown)
    slots = [k for k, v in enumerate(base) if v in visible]
    for k, v in zip(slots, order):
        base[k] = v
    return base


def apply_order(ids: list, saved: list) -> list:
    """Indices de `ids` triés selon l'ordre enregistré ; les tuiles inconnues gardent l'ordre par défaut, après."""
    pos = {v: n for n, v in enumerate(saved)}
    return sorted(range(len(ids)), key=lambda k: (0, pos[ids[k]]) if ids[k] in pos else (1, k))


class TileButton(QToolButton):
    def __init__(self, tile_id: str, on_drop=None):
        super().__init__()
        self.tile_id, self.on_drop = tile_id, on_drop
        self._press = None
        self._base_qss = None                            # style d'origine, mis de côté pendant le survol de dépôt
        if on_drop is not None:
            self.setAcceptDrops(True)

    def mousePressEvent(self, e):  # noqa: N802
        if e.button() == Qt.MouseButton.LeftButton:
            self._press = e.position()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):  # noqa: N802
        if self._press is not None and self.on_drop is not None and \
                (e.position() - self._press).manhattanLength() >= QApplication.startDragDistance():
            from PyQt6.QtGui import QDrag
            self._press = None
            self.setDown(False)                          # pas de clic à la fin du glisser
            mime = QMimeData()
            mime.setData(MIME_TILE, self.tile_id.encode("utf-8"))
            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.setPixmap(self.icon().pixmap(self.iconSize()))
            drag.exec(Qt.DropAction.MoveAction)
            return
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):  # noqa: N802
        self._press = None
        super().mouseReleaseEvent(e)

    def _mark(self, on: bool) -> None:
        if on and self._base_qss is None:
            self._base_qss = self.styleSheet() or ""
            self.setStyleSheet(self._base_qss + "QToolButton { background: rgba(255,255,255,0.18); "
                                                "border-radius: 8px; }")
        elif not on and self._base_qss is not None:
            self.setStyleSheet(self._base_qss)
            self._base_qss = None

    def dragEnterEvent(self, e):  # noqa: N802
        if e.mimeData().hasFormat(MIME_TILE):
            e.acceptProposedAction()
            self._mark(True)
        else:
            e.ignore()

    def dragMoveEvent(self, e):  # noqa: N802
        if e.mimeData().hasFormat(MIME_TILE):
            e.acceptProposedAction()

    def dragLeaveEvent(self, e):  # noqa: N802
        self._mark(False)

    def dropEvent(self, e):  # noqa: N802
        self._mark(False)
        if not e.mimeData().hasFormat(MIME_TILE) or self.on_drop is None:
            return
        src = bytes(e.mimeData().data(MIME_TILE)).decode("utf-8")
        after = e.position().x() > self.width() / 2
        e.acceptProposedAction()
        self.on_drop(src, self.tile_id, after)
