"""
Fenêtres de confirmation « jeu vidéo » : fond flouté, apparition animée (fondu + glissement), boutons français.

`ask_yes_no(parent, titre, message)` remplace QMessageBox.question (dont les boutons « Yes / No » ne sont pas traduits) :
    - le contenu de la fenêtre principale est capturé, flouté et assombri derrière la modale (backdrop) ;
    - la carte apparaît en fondu en montant légèrement (≈ 180 ms) ;
    - boutons « Oui » / « Non » avec états survol / focus / pressé fournis par le thème actif (QSS).
"""
from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QDialog, QFrame, QGraphicsBlurEffect, QGraphicsDropShadowEffect, QHBoxLayout, QLabel,
                             QPushButton, QVBoxLayout, QWidget)

from .common import make_label


class BlurBackdrop:
    """Capture la fenêtre parente, la floute et l'assombrit ; `dispose()` retire le voile."""

    def __init__(self, window: QWidget, radius: float = 14.0, tint: str = "rgba(0, 0, 0, 120)"):
        self.image = QLabel(window)
        self.image.setPixmap(window.grab())
        self.image.setGeometry(window.rect())
        blur = QGraphicsBlurEffect(self.image)
        blur.setBlurRadius(radius)
        self.image.setGraphicsEffect(blur)
        self.tint = QWidget(window)
        self.tint.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.tint.setStyleSheet(f"background: {tint};")
        self.tint.setGeometry(window.rect())
        for w in (self.image, self.tint):
            w.show()
            w.raise_()

    def dispose(self) -> None:
        for w in (self.tint, self.image):
            w.hide()
            w.deleteLater()


class ConfirmDialog(QDialog):
    """Carte de confirmation sans cadre système, centrée sur la fenêtre parente."""

    def __init__(self, parent: QWidget | None, title: str, message: str, yes: str = "Oui", no: str = "Non",
                 default_no: bool = True):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setStyleSheet("ConfirmDialog { background: transparent; background-image: none; }")   # la carte porte le décor du thème
        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 26, 26, 30)                           # marge pour l'ombre portée

        card = QFrame()
        card.setObjectName("dialogCard")
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(38)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 175))
        card.setGraphicsEffect(shadow)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(28, 24, 28, 22)
        lay.setSpacing(14)
        lay.addWidget(make_label("⚜  " + title, "title"))
        body = make_label(message, wrap=True)
        body.setMinimumWidth(380)
        lay.addWidget(body)
        buttons = QHBoxLayout()
        self.button_row = buttons
        buttons.addStretch(1)
        self.no_btn = QPushButton(no)
        self.no_btn.setProperty("role", "ghost")
        self.yes_btn = QPushButton(yes)
        for b in (self.no_btn, self.yes_btn):
            b.setMinimumWidth(110)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            buttons.addWidget(b)
        lay.addLayout(buttons)
        outer.addWidget(card)

        self.yes_btn.clicked.connect(self.accept)
        self.no_btn.clicked.connect(self.reject)
        (self.no_btn if default_no else self.yes_btn).setDefault(True)
        (self.no_btn if default_no else self.yes_btn).setFocus()
        self._anims: list[QPropertyAnimation] = []

    def showEvent(self, event):  # noqa: N802 (nom imposé par Qt)
        super().showEvent(event)
        self.adjustSize()
        parent = self.parentWidget()
        if parent is not None:
            self.move(parent.frameGeometry().center() - self.rect().center())
        end = self.pos()
        self.setWindowOpacity(0.0)
        fade = QPropertyAnimation(self, b"windowOpacity", self)
        fade.setDuration(180)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        slide = QPropertyAnimation(self, b"pos", self)
        slide.setDuration(220)
        slide.setStartValue(end + QPoint(0, 18))
        slide.setEndValue(end)
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anims = [fade, slide]
        for a in self._anims:
            a.start()


class SaveChangesDialog(ConfirmDialog):
    """
    « Des modifications n'ont pas été enregistrées. » — trois boutons, de gauche à droite :
    [Enregistrer] (action principale) · [Ne pas enregistrer et quitter] (destructive) · [Annuler] (retour à la fiche).
    exec() renvoie SAVE (1), DISCARD (2) ou CANCEL (0 — aussi avec Échap).
    """
    CANCEL, SAVE, DISCARD = 0, 1, 2

    def __init__(self, parent: QWidget | None, discard_label: str = "Ne pas enregistrer et quitter", note: str = ""):
        super().__init__(parent, "Modifications non enregistrées",
                         "Des modifications n'ont pas été enregistrées.\n\nEnregistrer le personnage avant de "
                         "continuer ?" + ("\n\n○ " + note if note else ""), yes="Enregistrer", no="Annuler",
                         default_no=False)
        row = self.button_row
        row.removeWidget(self.yes_btn)
        row.removeWidget(self.no_btn)
        self.save_btn, self.cancel_btn = self.yes_btn, self.no_btn
        self.discard_btn = QPushButton(discard_label)
        self.discard_btn.setProperty("role", "danger")
        self.discard_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.discard_btn.clicked.connect(lambda: self.done(self.DISCARD))
        for b in (self.save_btn, self.discard_btn, self.cancel_btn):
            b.setMinimumWidth(110)
            row.addWidget(b)
        self.save_btn.setDefault(True)
        self.save_btn.setFocus()


def ask_save_changes(parent: QWidget | None, discard_label: str = "Ne pas enregistrer et quitter",
                     note: str = "") -> str:
    """Modale de sortie : renvoie "save", "discard" ou "cancel". `note` : rappel des choix restant à faire."""
    if not note and parent is not None and callable(getattr(parent, "missing_note", None)):
        note = parent.missing_note()                     # « 3 choix restent à faire (Magie, …) » — non bloquant
    backdrop = BlurBackdrop(parent) if parent is not None else None
    dialog = SaveChangesDialog(parent, discard_label, note if isinstance(note, str) else "")
    try:
        res = dialog.exec()
    finally:
        if backdrop is not None:
            backdrop.dispose()
    return {SaveChangesDialog.SAVE: "save", SaveChangesDialog.DISCARD: "discard"}.get(res, "cancel")


def ask_yes_no(parent: QWidget | None, title: str, message: str, yes: str = "Oui", no: str = "Non",
               default_no: bool = True) -> bool:
    """Question Oui / Non modale avec fond flouté. Retourne True si l'utilisateur choisit « Oui »."""
    backdrop = BlurBackdrop(parent) if parent is not None else None
    dialog = ConfirmDialog(parent, title, message, yes, no, default_no)
    try:
        return dialog.exec() == 1          # QDialog.Accepted
    finally:
        if backdrop is not None:
            backdrop.dispose()


def ask_choice(parent: QWidget | None, title: str, message: str, options: list[str]) -> str:
    """Choix dans une liste (même carte « jeu vidéo » que ask_yes_no). Renvoie l'option choisie ou ''."""
    from PyQt6.QtWidgets import QComboBox
    backdrop = BlurBackdrop(parent) if parent is not None else None
    dialog = ConfirmDialog(parent, title, message, yes="Valider", no="Annuler", default_no=False)
    combo = QComboBox()
    combo.addItems(options)
    card = dialog.findChild(QFrame, "dialogCard")
    lay = card.layout() if card is not None else None
    if lay is not None:
        lay.insertWidget(max(0, lay.count() - 1), combo)
    try:
        return combo.currentText() if dialog.exec() == 1 else ""
    finally:
        if backdrop is not None:
            backdrop.dispose()


def ask_gm_spell(parent: QWidget | None, spell_names: list[str], usages: list[str]):
    """
    Fenêtre « Ajouter un sort (Accordé par le MJ) » : recherche + sort de la bibliothèque (ou nom libre),
    utilisation et note narrative. Renvoie (nom, utilisation, note) ou None.
    """
    from PyQt6.QtWidgets import QComboBox, QLineEdit
    from core.rules import norm
    backdrop = BlurBackdrop(parent) if parent is not None else None
    dialog = ConfirmDialog(parent, "Ajouter un sort (Accordé par le MJ)",
                           "Sort obtenu pour des raisons narratives (bénédiction, pacte, relique, quête…). Il "
                           "rejoint la section « Sorts accordés » de l'onglet Magie, à côté des manifestations "
                           "occultes.", yes="Ajouter", no="Annuler", default_no=False)
    search = QLineEdit()
    search.setPlaceholderText("Rechercher un sort… (ou tapez un nom libre)")
    spells = QComboBox()
    spells.setEditable(True)
    spells.addItems(spell_names)
    usage = QComboBox()
    usage.addItems(usages)
    note = QLineEdit()
    note.setPlaceholderText("Note (origine, conditions…) — facultatif")

    def _filter(text: str) -> None:
        n = norm(text)
        spells.clear()
        spells.addItems([s for s in spell_names if n in norm(s)] or [text])
    search.textChanged.connect(_filter)
    card = dialog.findChild(QFrame, "dialogCard")
    lay = card.layout() if card is not None else None
    if lay is not None:
        pos = max(0, lay.count() - 1)
        for i, w in enumerate((search, spells, usage, note)):
            lay.insertWidget(pos + i, w)
    try:
        if dialog.exec() != 1 or not spells.currentText().strip():
            return None
        return spells.currentText().strip(), usage.currentText(), note.text().strip()
    finally:
        if backdrop is not None:
            backdrop.dispose()


def ask_gm_feat(parent: QWidget | None, feat_names: list[str], preselect: str = "") -> str:
    """Fenêtre « Don accordé par le MJ » : recherche + choix du don. Renvoie le nom du don ou ''."""
    from PyQt6.QtWidgets import QComboBox, QLineEdit
    from core.rules import norm
    backdrop = BlurBackdrop(parent) if parent is not None else None
    dialog = ConfirmDialog(parent, "Don accordé par le MJ",
                           "Don supplémentaire obtenu hors progression (récompense, entraînement, bénédiction…). Il "
                           "s'ajoute aux emplacements de l'onglet Dons et ses bonus s'appliquent automatiquement.",
                           yes="Ajouter le don", no="Annuler", default_no=False)
    search = QLineEdit()
    search.setPlaceholderText("Rechercher un don…")
    feats = QComboBox()
    feats.addItems(feat_names)
    if preselect in feat_names:
        feats.setCurrentIndex(feat_names.index(preselect))

    def _filter(text: str) -> None:
        n = norm(text)
        feats.clear()
        feats.addItems([f for f in feat_names if n in norm(f)])
    search.textChanged.connect(_filter)
    card = dialog.findChild(QFrame, "dialogCard")
    lay = card.layout() if card is not None else None
    if lay is not None:
        pos = max(0, lay.count() - 1)
        lay.insertWidget(pos, search)
        lay.insertWidget(pos + 1, feats)
    try:
        return feats.currentText().strip() if dialog.exec() == 1 else ""
    finally:
        if backdrop is not None:
            backdrop.dispose()
