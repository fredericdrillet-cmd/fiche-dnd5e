"""
Faux module PyQt6 (sans fenêtre) utilisé uniquement pour des tests de fumée : il permet d'exécuter
tout le code d'interface (construction + rafraîchissements + gestionnaires) sur une machine sans
PyQt6 ni écran. Il ne valide PAS l'API Qt réelle, seulement la logique Python de l'application.
"""
import sys
import types


class W:
    """Widget factice : mémorise valeur/texte/éléments, et accepte n'importe quel appel."""

    def __init__(self, *a, **k):
        object.__setattr__(self, "_st", {"items": [], "idx": 0, "val": 0, "text": "", "chk": False, "rows": 0,
                                         "cells": {}, "row": 0, "props": {}, "kids": {}, "cs": None})
        if a and isinstance(a[0], str):
            self._st["text"] = a[0]

    # --- comportements « état »
    def __getattr__(self, name):
        st = object.__getattribute__(self, "_st")
        if name.startswith("__"):
            raise AttributeError(name)
        sp = {
            "addItems": lambda items: st["items"].extend(items),
            "addItem": lambda it, *r: st["items"].append(it),
            "addTab": lambda w, t="": (st["items"].append(w), st["props"].__setitem__(("tab", len(st["items"]) - 1), t)),
            "removeTab": lambda i: st["items"].pop(i),
            "setTabText": lambda i, t: None,
            "widget": lambda i: st["items"][i] if 0 <= i < len(st["items"]) else None,
            "clear": lambda: (st["items"].clear(), st["cells"].clear()),
            "count": lambda: len(st["items"]),
            "itemText": lambda i: st["items"][i],
            "findText": lambda t: st["items"].index(t) if t in st["items"] else -1,
            "currentText": lambda: st["items"][st["idx"]] if 0 <= st["idx"] < len(st["items"]) else "",
            "currentIndex": lambda: st["idx"],
            "setCurrentIndex": lambda i: st.__setitem__("idx", i),
            "setValue": lambda v: st.__setitem__("val", v),
            "value": lambda: st["val"],
            "setText": lambda t: st.__setitem__("text", t),
            "text": lambda: st["text"],
            "setStyleSheet": lambda q: st["props"].__setitem__("qss", q),
            "styleSheet": lambda: st["props"].get("qss", ""),
            "setTitle": lambda t: st.__setitem__("text", t),     # QGroupBox : le titre est le texte du widget
            "title": lambda: st["text"],
            "setPlainText": lambda t: st.__setitem__("text", t),
            "toPlainText": lambda: st["text"],
            "setChecked": lambda c: st.__setitem__("chk", bool(c)),
            "isChecked": lambda: st["chk"],
            "checkState": lambda: st["cs"],
            "setCheckState": lambda c: st.__setitem__("cs", c),
            "setRowCount": lambda n: st.__setitem__("rows", n),
            "rowCount": lambda: st["rows"],
            "setItem": lambda r, c, it: st["cells"].__setitem__((r, c), it),
            "item": lambda r, c=None: st["cells"].get((r, c)) or W(),
            "currentRow": lambda: st["row"],
            "setCurrentRow": lambda r: st.__setitem__("row", r),
            "isVisible": lambda: True,
            "actions": lambda: [],
            "columnCount": lambda: 5,
            "currentColumn": lambda: 0,
            "isFullScreen": lambda: False,
            "currentData": lambda: (st["data"].get(st["idx"]) if "data" in st else None),
            "addItem": lambda it, *r: (st["items"].append(it), st.setdefault("data", {}).__setitem__(len(st["items"]) - 1, r[0] if r else None)),
            "findData": lambda d: next((i for i, v in st.get("data", {}).items() if v == d), -1),
            "setItemData": lambda *a: None,
        }
        if name in sp:
            return sp[name]
        kids = st["kids"]
        if name not in kids:
            kids[name] = W()
        return kids[name]

    def __call__(self, *a, **k):
        return W()

    def __or__(self, o):
        return W()

    __ror__ = __or__

    def __iter__(self):
        return iter(())


class Meta(type):
    """Les attributs de classe inconnus (ex. QAbstractItemView.SelectionMode) renvoient un W en cache."""

    def __getattr__(cls, name):
        if name.startswith("__"):
            raise AttributeError(name)
        w = W()
        type.__setattr__(cls, name, w)
        return w


def install():
    import os
    os.environ["DND_EAGER_REFRESH"] = "1"      # tests : tous les onglets sont recalculés à chaque changement
    names = {
        "QtCore": ["Qt", "QTimer", "QStringListModel", "QEvent", "QObject", "QBuffer", "QByteArray", "QIODevice", "QSize", "QPoint", "QPointF", "QRectF", "QPropertyAnimation",
                   "QEasingCurve", "pyqtSignal", "QEvent"],
        "QtGui": ["QAction", "QActionGroup", "QKeySequence", "QBrush", "QColor", "QFont", "QPalette", "QImage", "QPixmap", "QPainter", "QPen", "QLinearGradient", "QRadialGradient", "QIcon", "QPainterPath", "QCursor"],
        "QtWidgets": ["QCompleter", "QSizeGrip", "QAbstractScrollArea", "QAbstractSlider", "QAbstractSpinBox", "QScrollBar", "QTabBar", "QToolButton", "QToolTip", "QStyle", "QStyledItemDelegate", "QProgressBar", "QSizePolicy", "QGraphicsBlurEffect", "QGraphicsDropShadowEffect", "QDialog", "QDialogButtonBox", "QAbstractItemView", "QApplication", "QCheckBox", "QComboBox", "QFileDialog", "QFrame",
                      "QGridLayout", "QGroupBox", "QHBoxLayout", "QHeaderView", "QLabel", "QLineEdit", "QListWidget",
                      "QListWidgetItem", "QMainWindow", "QMessageBox", "QPlainTextEdit", "QPushButton", "QScrollArea",
                      "QSpinBox", "QDoubleSpinBox", "QSplitter", "QStackedWidget", "QTabWidget", "QTableWidget", "QTableWidgetItem", "QTextBrowser",
                      "QVBoxLayout", "QWidget"],
    }
    root = types.ModuleType("PyQt6")
    sys.modules["PyQt6"] = root
    for mod, classes in names.items():
        m = types.ModuleType("PyQt6." + mod)
        for c in classes:
            setattr(m, c, Meta(c, (W,), {}) if c not in ("Qt", "QTimer") else W())
        sys.modules["PyQt6." + mod] = m
        setattr(root, mod, m)
    # QTimer.singleShot doit exécuter immédiatement le rappel
    sys.modules["PyQt6.QtCore"].QTimer = Meta("QTimer", (W,), {"singleShot": staticmethod(lambda ms, fn: fn()),
                                                             "isActive": lambda self: False})
    # Qt est un « espace de noms » : attributs en cache (comparaisons d'énumérations stables)
