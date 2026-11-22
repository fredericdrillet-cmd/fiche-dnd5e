"""Filet de sécurité (v52) : une erreur Python inattendue est enregistrée, la fiche sauvegardée, l'utilisateur
prévenu — et l'application continue (sans ce filet, PyQt6 la fermerait sans message)."""
from __future__ import annotations

import sys

from core import crash_report as CR

_STATE = {"busy": False, "window": None, "last": None}


def handle_exception(exc_type, exc, tb) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc, tb)
        return
    if _STATE["busy"]:                                    # erreur pendant le traitement d'une erreur
        sys.__excepthook__(exc_type, exc, tb)
        return
    _STATE["busy"] = True
    try:
        win = _STATE["window"]
        character = None
        try:
            character = win.engine.ch.to_dict() if win is not None else None
        except Exception:                                 # noqa: BLE001 — la fiche elle-même peut être en cause
            character = None
        text = CR.format_report(exc_type, exc, tb, character)
        path = CR.write_report(text)
        _STATE["last"] = path
        saved = False
        try:
            saved = bool(win is not None and win.autosave())
        except Exception:                                 # noqa: BLE001
            saved = False
        if sys.stderr is not None:
            sys.stderr.write(text)
        _show(win, exc_type, exc, path, text, saved)
    finally:
        _STATE["busy"] = False


def _show(win, exc_type, exc, path, text, saved) -> None:
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        if QApplication.instance() is None:
            return
        box = QMessageBox(win)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Une erreur est survenue")
        box.setText("Une erreur inattendue est survenue. {}\n\nVous pouvez continuer à jouer ; si quelque chose "
                    "semble faux, rouvrez la fiche.".format(
                        "Votre fiche a été sauvegardée (sauvegarde automatique)." if saved else
                        "Pensez à enregistrer votre fiche (Ctrl+S)."))
        box.setInformativeText(CR.short_message(exc_type, exc) + ("\n\nRapport : {}".format(path) if path else ""))
        copy = box.addButton("Copier le rapport", QMessageBox.ButtonRole.ActionRole)
        box.addButton("Continuer", QMessageBox.ButtonRole.AcceptRole)
        box.exec()
        if box.clickedButton() is copy:
            QApplication.clipboard().setText(text)
    except Exception:                                     # noqa: BLE001 — l'affichage ne doit jamais relancer
        pass


def install(window=None) -> None:
    _STATE["window"] = window
    sys.excepthook = handle_exception


def open_reports_folder() -> str:
    folder = CR.reports_dir()
    folder.mkdir(parents=True, exist_ok=True)
    try:
        from PyQt6.QtCore import QUrl
        from PyQt6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
    except Exception:                                     # noqa: BLE001
        pass
    return str(folder)
