"""Onglet « Histoire & Portrait (RP) » : portrait importé, histoire du personnage, notes de campagne.
v48 : encart « Résumé de la race » à côté du portrait (traits, langues, pouvoirs et sorts raciaux) — il remplace
l'onglet Race en Mode guidé — et choix de l'alignement (retiré de l'en-tête)."""
from __future__ import annotations

import base64
import html

from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, QSize, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (QComboBox, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPlainTextEdit,
                             QPushButton, QScrollArea, QVBoxLayout)

from core import rules as R
from . import theme
from .common import CENTER, BaseTab, blocked, fill_combo, make_label, rich_tip

IMAGE_FILTER = "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;Tous les fichiers (*)"
PORTRAIT_SIZE = (300, 400)        # cadre photo 3:4
MAX_STORED_SIDE = 640             # taille maximale de l'image enregistrée dans la sauvegarde (px)


def image_to_b64(path: str, max_side: int = MAX_STORED_SIDE) -> str:
    """
    Charge une image, la réduit si besoin et la retourne en PNG encodé base64 : le portrait est ainsi
    enregistré DANS le fichier JSON du personnage (aucun lien vers un fichier externe qui pourrait disparaître).
    """
    img = QImage(path)
    if img.isNull():
        raise ValueError("Ce fichier n'est pas une image lisible.")
    if max(img.width(), img.height()) > max_side:
        img = img.scaled(max_side, max_side, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    data = QByteArray()
    buf = QBuffer(data)
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    img.save(buf, "PNG")
    buf.close()
    return base64.b64encode(bytes(data.data())).decode("ascii")


def b64_to_pixmap(encoded: str) -> QPixmap:
    pix = QPixmap()
    if encoded:
        pix.loadFromData(base64.b64decode(encoded))
    return pix


class RPTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        root = QHBoxLayout(self)

        # ---------------- colonne gauche : portrait dans un cadre photo
        left = QVBoxLayout()
        box = QGroupBox("Portrait")
        bl = QVBoxLayout(box)
        self.frame = QLabel("Aucun portrait\n\nImportez une image\nde votre personnage")
        self.frame.setProperty("role", "portrait")          # cadre doré dégradé défini dans le thème
        self.frame.setAlignment(CENTER)
        self.frame.setFixedSize(*PORTRAIT_SIZE)
        self.caption = make_label("", "head", align=CENTER)
        self.caption.setWordWrap(True)
        self.import_btn = QPushButton("Importer un portrait…")
        self.clear_btn = QPushButton("Retirer le portrait")
        self.clear_btn.setProperty("role", "danger")
        bl.addWidget(self.frame, 0, CENTER)
        bl.addWidget(self.caption)
        bl.addWidget(self.import_btn)
        bl.addWidget(self.clear_btn)
        arow = QHBoxLayout()                              # v48 : alignement (retiré de l'en-tête)
        arow.addWidget(make_label("Alignement"))
        self.align = QComboBox()
        arow.addWidget(self.align, 1)
        bl.addLayout(arow)
        # v48 : résumé de la race à côté du portrait
        self.race_box = QGroupBox("☗ Résumé de la race")
        rbl = QVBoxLayout(self.race_box)
        self.race_summary = make_label("", "", wrap=True)
        self.race_summary.setTextFormat(Qt.TextFormat.RichText)
        self.race_summary.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(self.race_summary)
        rbl.addWidget(scroll)
        self.race_box.setMinimumWidth(300)
        top = QHBoxLayout()
        top.addWidget(box)
        top.addWidget(self.race_box, 1)
        left.addLayout(top)
        # traits de personnalité (déplacés de l'onglet Inventaire en v33 : les informations RP vivent ici)
        tbox = QGroupBox("Traits, idéaux, liens, défauts")
        tl = QVBoxLayout(tbox)
        self.traits = QPlainTextEdit()
        self.traits.setPlaceholderText("Traits de personnalité, idéaux, liens et défauts (voir l'historique)…")
        tl.addWidget(self.traits)
        left.addWidget(tbox, 1)
        root.addLayout(left, 0)

        # ---------------- colonne droite : histoire (grand champ) + notes de campagne
        right = QVBoxLayout()
        story = QGroupBox("Histoire du personnage (backstory)")
        sl = QVBoxLayout(story)
        self.story = QPlainTextEdit()
        self.story.setPlaceholderText("Origines, famille, événements marquants, motivations, secrets…")
        sl.addWidget(self.story)
        notes = QGroupBox("Notes de campagne")
        nl = QVBoxLayout(notes)
        self.notes = QPlainTextEdit()
        self.notes.setPlaceholderText("Quêtes en cours, PNJ rencontrés, lieux, indices, dettes…")
        nl.addWidget(self.notes)
        right.addWidget(story, 2)                        # v34 : l'histoire se lit, les notes s'écrivent en séance
        right.addWidget(notes, 3)
        root.addLayout(right, 1)

        self.align.activated.connect(lambda _=0: self._on_align(self.align.currentText()))
        self.import_btn.clicked.connect(self._on_import)
        self.clear_btn.clicked.connect(self._on_clear)
        self.story.textChanged.connect(lambda: self._on_text("histoire", self.story))
        self.notes.textChanged.connect(lambda: self._on_text("notes", self.notes))
        self.traits.textChanged.connect(lambda: self._on_text("traits", self.traits))
        self._shown: str | None = None      # portrait actuellement affiché (évite de le redessiner à chaque rafraîchissement)

    # ------------------------------------------------------------------ handlers
    def _on_align(self, value: str) -> None:
        self.ch.alignement = value
        self.win.mark_dirty()

    def race_summary_html(self) -> str:
        """Race / sous-race, traits (nom + début du texte), langues, pouvoirs et sorts raciaux [Sort Racial]."""
        eng, ch, t = self.engine, self.ch, theme.current()
        title = ch.race + (" — {}".format(ch.sous_race) if ch.sous_race else "")
        parts = ["<h3 style='color:{}'>{}</h3>".format(t.accent_text, html.escape(title or "Race non choisie"))]
        bg = ch.historique
        if bg:
            parts.append("<p><b>Historique :</b> {}</p>".format(html.escape(bg)))
        langs = list(ch.langues_liste) + ([ch.langues] if ch.langues else [])
        parts.append("<p><b>Langues :</b> {}</p>".format(html.escape(", ".join(langs)) if langs else "—"))
        spells = eng.racial_spells()
        if spells:
            parts.append("<p><b>Sorts raciaux :</b><br/>" + "<br/>".join(
                "{} {} [Sort Racial] — {}{}".format("✦" if r["debloque"] else "🔒", html.escape(r["nom"]),
                                                    html.escape(r["usage"]), "" if r["debloque"] else
                                                    " (niveau {})".format(r["niveau_requis"])) for r in spells) + "</p>")
        traits = eng.race_capacities()
        if traits:
            parts.append("<p><b>Traits raciaux :</b></p><ul style='margin-left:-20px'>" + "".join(
                "<li><b>{}</b> — {}</li>".format(html.escape(c.get("nom", "")), html.escape(
                    (c.get("description", "") or "")[:160] + ("…" if len(c.get("description", "") or "") > 160 else "")))
                for c in traits) + "</ul>")
        return "".join(parts)

    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importer un portrait", self.win._start_dir(), IMAGE_FILTER)
        if not path:
            return
        try:
            self.ch.portrait = image_to_b64(path)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Image illisible", str(exc))
            return
        self.changed()

    def _on_clear(self):
        self.ch.portrait = ""
        self.changed()

    def _on_text(self, attr: str, widget: QPlainTextEdit):
        setattr(self.ch, attr, widget.toPlainText())
        self.win.mark_dirty()

    # ------------------------------------------------------------------ rafraîchissement
    def refresh(self):
        ch, eng = self.ch, self.engine
        if self._shown != ch.portrait:
            pix = b64_to_pixmap(ch.portrait)
            if pix.isNull():
                self.frame.setPixmap(QPixmap())
                self.frame.setText("Aucun portrait\n\nImportez une image\nde votre personnage")
            else:
                inner = QSize(PORTRAIT_SIZE[0] - 16, PORTRAIT_SIZE[1] - 16)        # intérieur du cadre (bordure + marge)
                self.frame.setPixmap(pix.scaled(inner, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation))
            self._shown = ch.portrait
        self.clear_btn.setEnabled(bool(ch.portrait))
        with blocked(self.align):
            fill_combo(self.align, R.ALIGNMENTS, ch.alignement)
        self.race_summary.setText(self.race_summary_html())
        classes = " / ".join("{} {}".format(c["nom"], c["niveau"]) for c in ch.classes)
        # le nom du personnage figure déjà dans l'en-tête : sous le portrait, seulement la race et les classes
        self.caption.setText("{} — {}".format(ch.race, classes) if ch.race else classes)
        self.frame.setToolTip(rich_tip("Portrait", "Enregistré dans la sauvegarde du personnage (image réduite à "
                                       "{} px max).".format(MAX_STORED_SIDE)))
        for attr, widget in (("histoire", self.story), ("notes", self.notes), ("traits", self.traits)):
            if widget.toPlainText() != getattr(ch, attr):
                with blocked(widget):
                    widget.setPlainText(getattr(ch, attr))
