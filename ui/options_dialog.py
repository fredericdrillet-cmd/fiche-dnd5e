"""Fenêtre « Options » : galerie des 10 thèmes (aperçu en direct) et taille du texte — boutons en français."""
from __future__ import annotations

from PyQt6.QtWidgets import (QCheckBox, QDialog, QFrame, QGroupBox, QHBoxLayout, QPushButton, QScrollArea, QSpinBox,
                             QVBoxLayout, QWidget)

from . import theme
from .common import indicator_qss, make_label
from .theme_picker import ThemeGallery


class OptionsDialog(QDialog):
    """Le thème est appliqué immédiatement (aperçu) ; « Annuler » rétablit l'apparence d'origine."""

    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.setWindowTitle("Options")
        self.setMinimumWidth(720)
        self._initial = (win.settings["theme"], win.settings["font_px"])
        self._key = theme.resolve_key(win.settings["theme"])

        # v50 : contenu défilant (aucune option coupée en petite fenêtre), boutons toujours visibles en bas
        root = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(6, 6, 12, 6)
        scroll.setWidget(inner)
        root.addWidget(scroll, 1)
        self.setMinimumHeight(560)
        self.resize(820, 760)
        lay.addWidget(make_label("Apparence", "title"))

        box = QGroupBox("Thème graphique — cliquez pour l'appliquer")
        bl = QVBoxLayout(box)
        self.gallery = ThemeGallery(self._key)
        self.desc = make_label("", "muted", wrap=True)
        self.audit = make_label("", wrap=True)
        bl.addWidget(self.gallery)
        bl.addWidget(self.desc)
        bl.addWidget(self.audit)
        self.reset_btn = QPushButton("Revenir au thème par défaut (Porte de Baldur)")
        self.reset_btn.setProperty("role", "ghost")
        bl.addWidget(self.reset_btn)
        lay.addWidget(box)

        fbox = QGroupBox("Confort de lecture")
        fl = QHBoxLayout(fbox)
        self.font = QSpinBox()
        self.font.setRange(11, 22)
        self.font.setSuffix(" px")
        self.font.setValue(win.settings["font_px"])
        fl.addWidget(make_label("Taille du texte"))
        fl.addWidget(self.font)
        fl.addStretch(1)
        lay.addWidget(fbox)

        gbox = QGroupBox("Règles de jeu")
        gl = QVBoxLayout(gbox)
        self.survival = QCheckBox("Règle de survie : chaque repos long consomme 1 ration de l'inventaire")
        self.survival.setChecked(bool(win.settings.get("regle_survie", False)))
        gl.addWidget(self.survival)
        gl.addWidget(make_label("Sans ration, un avertissement rappelle le risque d'épuisement (PHB : on peut tenir "
                                "3 + modificateur de Constitution jours sans manger).", "muted", wrap=True))
        lay.addWidget(gbox)

        mbox = QGroupBox("Mode d'édition de la fiche")          # v48 : Mode guidé (défaut) / Mode libre
        ml = QVBoxLayout(mbox)
        self.free_mode = QCheckBox("Activer le Mode libre")
        self.free_mode.setChecked(bool(win.settings.get("mode_libre", False)))
        ml.addWidget(self.free_mode)
        ml.addWidget(make_label("Mode guidé (par défaut) : la progression passe uniquement par « ▲ Niveau "
                                "supérieur » (multiclassage compris), le nom du personnage est fixé à la création, "
                                "la race, l'historique et les caractéristiques se choisissent dans l'assistant de "
                                "création. Mode libre : toute la fiche redevient modifiable (niveaux, classes, race, "
                                "caractéristiques brutes, nom du personnage…).", "muted", wrap=True))
        lay.addWidget(mbox)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setProperty("role", "ghost")
        self.ok_btn = QPushButton("Valider")
        self.ok_btn.setDefault(True)
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.ok_btn)
        root.addLayout(buttons)
        for box in (self.survival, self.free_mode):      # v50 : cases bien visibles quel que soit le thème
            box.setStyleSheet(indicator_qss(theme.current()))
            box.setMinimumHeight(30)

        self._update_info()
        self.gallery.chosen.connect(self._choose)
        self.font.valueChanged.connect(lambda _=0: self._apply())
        self.reset_btn.clicked.connect(lambda: self._choose(theme.DEFAULT_THEME))
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _choose(self, key: str):
        self._key = theme.resolve_key(key)
        self.gallery.select(self._key)
        self._apply()

    def _apply(self):
        self.win.apply_appearance(self._key, self.font.value())
        self._update_info()

    def _update_info(self):
        t = theme.THEMES[self._key]
        self.desc.setText("{} — {}".format(t.name, t.description))
        fails = t.audit()
        self.audit.setText("Contraste texte / fond : {:.1f}:1 — {}".format(
            min(theme.contrast_ratio(t.text, t.bg), theme.contrast_ratio(t.text, t.bg2)),
            "toutes les paires de couleurs respectent WCAG AA (≥ 4,5:1)" if not fails
            else "{} paire(s) sous le seuil".format(len(fails))))

    def reject(self):
        self.win.apply_appearance(*self._initial)   # annule l'aperçu
        super().reject()

    def accept(self):
        self.win.settings["regle_survie"] = self.survival.isChecked()
        self.win.settings["mode_libre"] = self.free_mode.isChecked()
        self.win.apply_appearance(self._key, self.font.value(), save=True)
        super().accept()
