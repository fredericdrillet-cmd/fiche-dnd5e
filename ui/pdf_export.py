"""Export de la fiche en PDF (v52) : HTML de core/sheet_export.py imprimé par Qt (A4, portrait inclus)."""
from __future__ import annotations

import base64

from PyQt6.QtCore import QByteArray, QMarginsF, QUrl
from PyQt6.QtGui import QFont, QFontDatabase, QImage, QPageLayout, QPageSize, QPdfWriter, QTextDocument

from core.sheet_export import sheet_html


SERIF_FONTS = ("Palatino Linotype", "Book Antiqua", "Palatino", "Georgia", "Cambria", "DejaVu Serif", "FreeSerif",
               "Times New Roman")


def serif_family() -> str:
    """Police à empattements du style « grimoire » : la première disponible sur le système."""
    have = set(QFontDatabase.families())
    return next((f for f in SERIF_FONTS if f in have), "serif")


def export_pdf(engine, path: str, cheatsheet: bool = False) -> None:
    doc = QTextDocument()
    doc.setDefaultFont(QFont(serif_family(), 9))
    if engine.ch.portrait:                               # portrait base64 -> ressource « portrait.png »
        img = QImage()
        img.loadFromData(QByteArray(base64.b64decode(engine.ch.portrait)))
        doc.addResource(QTextDocument.ResourceType.ImageResource.value, QUrl("portrait.png"), img)
    doc.setHtml(sheet_html(engine, cheatsheet))
    writer = QPdfWriter(path)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(10, 10, 10, 10), QPageLayout.Unit.Millimeter)
    writer.setResolution(110)
    writer.setTitle("Fiche de personnage — {}".format(engine.ch.nom or "Sans nom"))
    doc.setPageSize(writer.pageLayout().paintRectPixels(writer.resolution()).size().toSizeF())
    doc.print(writer)
