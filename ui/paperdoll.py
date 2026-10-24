"""
Mannequin d'équipement (v31, inspiré de l'inventaire de Baldur's Gate 3) : le personnage entouré de 12 cases.

    - à gauche : tête, amulette, cape, armure, gants ; à droite : ceinture, bottes, anneau ×2 ; en bas : main
      principale, main secondaire, distance ;
    - au centre : le portrait du personnage (onglet « Histoire, Portrait ») ;
    - clic sur une case : les objets de l'INVENTAIRE qui correspondent à son rôle — armures du sac, armes de corps à
      corps, boucliers et armes légères, armes à distance, anneaux, capes, bottes… (ou « Vider la case ») ; un objet
      par case, l'ancien est rangé ; l'armure et les armes choisies ici sont celles de l'onglet Combat ;
    - infobulle de chaque case : objet porté, rareté, harmonisation (◉) ; objet magique en surbrillance.
"""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QGroupBox, QLabel, QSizePolicy, QVBoxLayout

from core.equipment import MAGIC_SLOTS, SLOT_LABELS, SLOTS
from . import theme
from .common import make_label, rich_tip
from .dialogs import ask_choice

LAYOUT = {"tete": (0, 0), "amulette": (1, 0), "cape": (2, 0), "armure": (3, 0), "gants": (4, 0),
          "ceinture": (0, 2), "bottes": (1, 2), "anneau_1": (2, 2), "anneau_2": (3, 2),
          "main_principale": (5, 0), "main_secondaire": (5, 1), "distance": (5, 2)}
EMPTY = "— vide —"
CLEAR = "✖ Vider la case"


class SlotCard(QLabel):
    """Case cliquable du mannequin : texte AVEC retour à la ligne (un QPushButton tronque les noms longs)."""

    def __init__(self, on_click=None, min_w: int = 150, min_h: int = 66):
        super().__init__()
        self.on_click = on_click
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(min_w, min_h)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):  # noqa: N802
        if self.on_click and event.button() == Qt.MouseButton.LeftButton:
            self.on_click()
        else:
            super().mousePressEvent(event)

    def set_look(self, color: str, bold: bool = False, dashed: bool = False) -> None:
        t = theme.current()
        self.setStyleSheet("QLabel {{ color: {c}; font-weight: {w}; background: {bg}; border: 1px {st} {b}; "
                           "border-radius: 6px; padding: 4px 6px; }}".format(
                               c=color, w="bold" if bold else "normal", bg=t.panel2, b=t.border,
                               st="dashed" if dashed else "solid"))


class PaperdollPanel(QGroupBox):
    def __init__(self, win):
        super().__init__("🧍 Mannequin d'équipement")
        self.win = win
        lay = QVBoxLayout(self)
        grid = QGridLayout()
        grid.setSpacing(6)
        self.slot_btns: dict[str, SlotCard] = {}
        for key, (r, c) in LAYOUT.items():
            b = SlotCard(lambda k=key: self._on_slot(k))
            grid.addWidget(b, r, c)
            self.slot_btns[key] = b
        # au centre : le portrait DU PERSONNAGE (onglet « Histoire, Portrait »), qu'on équipe
        self.portrait = SlotCard(self._on_portrait, 170, 230)
        self.portrait.setProperty("role", "portrait")
        self._portrait_shown = None
        grid.addWidget(self.portrait, 0, 1, 5, 1)
        for col in range(3):
            grid.setColumnStretch(col, 1)
        lay.addLayout(grid)
        self.hint = make_label("Clic sur une case : choisir parmi les objets de l'inventaire qui correspondent à "
                               "son rôle (armures, armes, boucliers, anneaux, capes…). Un objet par case.",
                               "muted", wrap=True)
        lay.addWidget(self.hint)
        self.setMaximumWidth(560)

    @property
    def engine(self):
        return self.win.engine

    def refresh(self) -> None:
        eng, t = self.engine, theme.current()
        doll = eng.paperdoll()
        icons = {k: icon for k, _lab, icon in SLOTS}
        for key, b in self.slot_btns.items():
            item = doll.get(key)
            label = SLOT_LABELS[key]
            if item:
                mark = " ◉" if item.get("harmonise") else ""
                warn = eng.item_proficiency_warning(item["nom"]) if key in (
                    "armure", "main_principale", "main_secondaire", "distance") else ""
                magic = item["source"] == "objet" or item.get("magique")
                b.setText("{} {}\n{}{}{}{}".format(icons[key], label, "⚠ " if warn else "", "✨ " if magic else "",
                                                   item["nom"], mark))
                b.set_look(t.warn if warn else t.accent_text if magic else t.text, bold=True)
                b.setToolTip(rich_tip(("⚠ " if warn else "") + item["nom"], "{}{}{}{}".format(
                    label, " — " + html.escape(item.get("detail", "")) if item.get("detail") else "",
                    "\n◉ Harmonisé" if item.get("harmonise") else
                    "\n○ Harmonisation requise (non harmonisé : sans effet)" if item.get("lien") else "",
                    "\n⚠ " + warn if warn else "")))
            else:
                n = len(eng.slot_inventory(key))           # objets du sac qui vont dans cette case
                b.setText("{} {}\n{}".format(icons[key], label, EMPTY if not n else "{} objet{} disponible{}".format(
                    n, "s" * (n > 1), "s" * (n > 1))))
                b.set_look(t.muted, dashed=True)
                b.setToolTip(rich_tip(label, "Case vide." + (" Clic : choisir un objet." if n else "")))
        self._refresh_portrait()

    def _refresh_portrait(self) -> None:
        """Portrait du personnage (importé dans l'onglet « Histoire, Portrait »), réduit au cadre ; sinon invitation."""
        data = self.engine.ch.portrait
        if data == self._portrait_shown:
            return
        self._portrait_shown = data
        pix = None
        if data:
            try:
                from .rp_tab import b64_to_pixmap
                pix = b64_to_pixmap(data)
                if pix.isNull():
                    pix = None
            except Exception:                             # pragma: no cover - image illisible
                pix = None
        if pix is not None:
            scaled = pix.scaled(160, 220, Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
            self.portrait.setText("")
            self.portrait.setPixmap(scaled)
            self.portrait.setToolTip(rich_tip(self.engine.ch.nom or "Portrait", "Portrait du personnage — clic : "
                                              "le changer dans l'onglet « Histoire, Portrait »."))
        else:
            from PyQt6.QtGui import QPixmap
            self.portrait.setPixmap(QPixmap())
            self.portrait.setText("🧍\nAucun portrait\n\nCliquez pour l'importer (onglet « Histoire, Portrait »)")
            self.portrait.setToolTip("Importez le portrait de votre personnage dans l'onglet « Histoire, Portrait ».")
        self.portrait.set_look(theme.current().muted, dashed=pix is None)

    def _on_portrait(self) -> None:
        if hasattr(self.win, "go_to_tab"):
            self.win.go_to_tab("rp")

    # ------------------------------------------------------------------ actions
    def _on_slot(self, key: str) -> None:
        """Case cliquée : objets de l'inventaire correspondant à son RÔLE (armure, arme, bouclier, anneau, cape…)."""
        eng, win = self.engine, self.win
        cands = eng.slot_inventory(key)
        doll = eng.paperdoll()
        labels = {}
        for c in cands:
            suffix = "  (porté ici)" if c["equipe"] else "  (remplace {})".format(doll[key]["nom"]) if key in doll else ""
            labels["{}{}".format(c["nom"], suffix)] = c
        if key in doll:
            labels[CLEAR] = None
        if not labels:
            where = ("« Ajouter un objet » (sac)" if key not in MAGIC_SLOTS else
                     "le sous-onglet « Équipement, objets magiques »")
            win.statusBar().showMessage("Aucun objet de l'inventaire ne va en « {} » : ajoutez-en via {}.".format(
                SLOT_LABELS[key], where), 7000)
            return
        picked = ask_choice(win, SLOT_LABELS[key], "Objets de votre inventaire pour cette case (un objet par case) :",
                            list(labels))
        if not picked:
            return
        if labels[picked] is None:
            eng.unequip_slot(key)
            win.statusBar().showMessage("{} : case vidée (l'objet reste dans l'inventaire).".format(SLOT_LABELS[key]),
                                        5000)
        else:
            win.statusBar().showMessage(eng.equip_slot(key, labels[picked]), 7000)
        win.changed()
