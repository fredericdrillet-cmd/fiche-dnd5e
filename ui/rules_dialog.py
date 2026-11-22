"""
Fenêtre « Règles de la table » (v52) : mode d'édition du personnage (2014, 2024, libre) et règles optionnelles.

Les choix s'appliquent au personnage ouvert (ils sont enregistrés dans sa sauvegarde). La case « Utiliser ces réglages
pour les nouveaux personnages » les mémorise aussi dans les préférences.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFrame, QGroupBox, QHBoxLayout, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)

from core import editions as E
from core import house_rules as HR
from core.settings import save_settings
from .common import make_label


class RulesDialog(QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.setWindowTitle("Règles de la table")
        self.setMinimumWidth(640)
        eng = win.engine
        self._mode = eng.edition_mode
        self._rules = dict(eng.house_rules())

        root = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        scroll.setWidget(inner)
        root.addWidget(scroll, 1)

        lay.addWidget(make_label("Édition des règles", "title"))
        box = QGroupBox("Contenu proposé pour ce personnage")
        bl = QVBoxLayout(box)
        self.mode_combo = QComboBox()
        for key, text in E.MODES.items():
            if key != E.MODE_LIBRE or self._mode == E.MODE_LIBRE:      # une seule édition par fiche (mode libre masqué)
                self.mode_combo.addItem(text, key)
        self.mode_combo.setCurrentIndex(max(0, self.mode_combo.findData(self._mode)))
        self.mode_combo.currentIndexChanged.connect(self._on_mode)
        bl.addWidget(self.mode_combo)
        self.mode_help = make_label("", "muted", wrap=True)
        bl.addWidget(self.mode_help)
        self.problems = make_label("", "warning", wrap=True)
        bl.addWidget(make_label("Changer d'édition remplace les classes et sous-classes de la fiche par leur version "
                                "de l'autre édition (niveaux conservés). Les sous-classes absentes de l'autre "
                                "édition sont à choisir de nouveau.", "muted", wrap=True))
        bl.addWidget(self.problems)
        lay.addWidget(box)

        lay.addWidget(make_label("Règles optionnelles", "title"))
        self.checks: dict[str, QCheckBox] = {}
        for cat in dict.fromkeys(r.categorie for r in HR.RULES):
            gb = QGroupBox(cat)
            gl = QVBoxLayout(gb)
            for rule in (r for r in HR.RULES if r.categorie == cat):
                cb = QCheckBox(rule.nom)
                cb.setChecked(self._rules.get(rule.cle, False))
                cb.setToolTip(rule.description)
                self.checks[rule.cle] = cb
                gl.addWidget(cb)
                gl.addWidget(make_label("{} — {}".format(rule.description, rule.origine), "muted", wrap=True))
            lay.addWidget(gb)

        row = QHBoxLayout()
        reset = QPushButton("Valeurs par défaut du mode")
        reset.clicked.connect(self._reset)
        row.addWidget(reset)
        row.addStretch(1)
        lay.addLayout(row)
        self.as_default = QCheckBox("Utiliser ces réglages pour les nouveaux personnages")
        lay.addWidget(self.as_default)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("Annuler")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("Appliquer")
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(ok)
        root.addLayout(buttons)
        self._update_help()

    # ------------------------------------------------------------------ interactions
    def _current_mode(self) -> str:
        return E.normalize_mode(self.mode_combo.currentData())

    def _on_mode(self, _index: int = 0) -> None:
        self._update_help()

    def _update_help(self) -> None:
        mode = self._current_mode()
        self.mode_help.setText(E.MODE_HELP[mode])
        problems = E.validate_classes(self.win.engine.ch.classes, mode)
        self.problems.setText("\n".join("⚠ " + p for p in problems))

    def _reset(self) -> None:
        for key, value in HR.defaults_for(self._current_mode()).items():
            self.checks[key].setChecked(value)

    def selected_rules(self) -> dict[str, bool]:
        return {key: cb.isChecked() for key, cb in self.checks.items()}

    def accept(self) -> None:
        eng = self.win.engine
        eng.set_edition_mode(self._current_mode())
        eng.ch.regles_optionnelles = self.selected_rules()
        if self.as_default.isChecked():
            self.win.settings["edition_defaut"] = eng.edition_mode
            self.win.settings["regles_defaut"] = dict(eng.ch.regles_optionnelles)
            save_settings(self.win.settings)
        if hasattr(self.win, "changed"):
            self.win.changed()
        self.done(1)                                   # = QDialog.accept() (Accepted)


def apply_table_defaults(ch, settings: dict) -> None:
    """Nouveau personnage : édition et règles de la table par défaut (préférences)."""
    ch.edition_mode = E.normalize_mode(settings.get("edition_defaut"))
    ch.regles_optionnelles = HR.clean(settings.get("regles_defaut"))


def ask_edition(win):
    """Nouveau personnage : édition 2014 ou 2024 (None = annulé). Valeur proposée : préférence de la table."""
    from PyQt6.QtWidgets import QMessageBox
    box = QMessageBox(win)
    box.setWindowTitle("Nouveau personnage")
    box.setText("Quelle édition des règles pour ce personnage ?")
    box.setInformativeText("{}\n{}\n\nL'édition s'applique à toute la fiche (classes, sous-classes, espèces, "
                           "historiques, dons et sorts proposés).".format(E.MODE_HELP[E.MODE_2014],
                                                                          E.MODE_HELP[E.MODE_2024]))
    b14 = box.addButton("Édition 2014", QMessageBox.ButtonRole.AcceptRole)
    b24 = box.addButton("Édition 2024", QMessageBox.ButtonRole.AcceptRole)
    cancel = box.addButton("Annuler", QMessageBox.ButtonRole.RejectRole)
    default = E.normalize_mode((getattr(win, "settings", {}) or {}).get("edition_defaut"))
    box.setDefaultButton(b24 if default == E.MODE_2024 else b14)
    box.exec()
    clicked = box.clickedButton()
    if clicked is cancel:
        return None
    return E.MODE_2024 if clicked is b24 else (E.MODE_2014 if clicked is b14 else default)
