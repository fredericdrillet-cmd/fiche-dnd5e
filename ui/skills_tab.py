"""Panneau « Compétences » (intégré à l'onglet Caractéristiques & Compétences) : maîtrise, expertise, valeur finale dynamique, jets de sauvegarde, valeurs passives."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QAbstractItemView, QGroupBox, QHBoxLayout, QTableWidget, QVBoxLayout

from core import rules as R
from core.rules import ABILITIES
from . import theme
from .dice_dialog import d20_icon, roll_dice
from .common import BaseTab, adv_badge, calc_tip, cell, check_item, make_label, rich_tip, style_table


def fit_table_height(table) -> None:
    """Hauteur exacte pour afficher toutes les lignes (la page entière défile, pas la table)."""
    try:
        h = table.horizontalHeader().height() + table.verticalHeader().length() + 2 * table.frameWidth() + 4
        table.setFixedHeight(int(h))
    except TypeError:                   # environnement de test sans Qt
        pass


class SkillsTab(BaseTab):
    def __init__(self, win, compact: bool = False):
        super().__init__(win)
        self.compact = compact          # intégré à la vue « Caractéristiques & Compétences » : tables sans défilement
        root = QHBoxLayout(self)
        if compact:
            root.setContentsMargins(0, 0, 0, 0)

        left = self.skills_box = QGroupBox("Compétences")
        ll = QVBoxLayout(left)
        self.status = make_label("", "muted", wrap=True)
        ll.addWidget(self.status)
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Maîtrise", "Expertise", "Compétence", "Carac.", "Bonus", "Source",
                                              "Av. / Désav.", "Jet"])
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        style_table(self.table, stretch_col=2, row_h=26 if compact else 32)     # v51 : lignes compactes
        self.table.setCursor(Qt.CursorShape.PointingHandCursor)
        self.table.cellClicked.connect(self._on_skill_click)      # clic n'importe où sur la ligne
        ll.addWidget(self.table)
        root.addWidget(left, 3)

        right = QVBoxLayout()
        sbox = QGroupBox("Jets de sauvegarde")
        sl = QVBoxLayout(sbox)
        self.saves = QTableWidget(6, 5)
        self.saves.setHorizontalHeaderLabels(["Maîtrise", "Caractéristique", "Bonus", "Av. / Désav.", "Jet"])
        self.saves.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        style_table(self.saves, stretch_col=1, row_h=26 if compact else 32)
        self.saves.setCursor(Qt.CursorShape.PointingHandCursor)
        self.saves.cellClicked.connect(self._on_save_click)
        sl.addWidget(self.saves)
        right.addWidget(sbox, 3)
        pbox = QGroupBox("Valeurs passives")
        pl = QVBoxLayout(pbox)
        self.passive = make_label("", "stat")
        self.legend = make_label(
            "Cliquez n'importe où sur une ligne pour cocher / décocher la maîtrise ; cliquez dans la colonne "
            "« Expertise » pour l'expertise.\nMaîtrise : + bonus de maîtrise (niveau global).\nExpertise (réservée aux compétences maîtrisées) : "
            "bonus de maîtrise doublé.\nLes compétences de l'historique sont cochées automatiquement ; les lignes "
            "surlignées sont celles proposées par votre classe de départ.", "muted", wrap=True)
        pl.addWidget(self.passive)
        pl.addWidget(self.legend)
        if compact:                                       # v51 : légende réduite à l'essentiel (gain de hauteur)
            self.legend.setText("Clic sur une ligne : maîtrise · colonne « Expertise » : expertise · « Jet » : d20.")
        right.addWidget(pbox, 2)
        root.addLayout(right, 2)

    # ------------------------------------------------------------------ handlers
    def _on_skill_click(self, row: int, col: int):
        """
        Zone de clic élargie : la colonne « Expertise » bascule l'expertise ; un clic partout ailleurs sur la ligne
        (case, nom, caractéristique, bonus, source) bascule la maîtrise.
        """
        names = self.db.skill_names
        if not 0 <= row < len(names):
            return
        if col == self.ROLL_COL:                         # colonne « Jet » : lancer de d20 animé
            roll_dice(self.win, self.engine.skill_spec(names[row]))
            return
        st = self.ch.competences.setdefault(names[row], {"maitrise": False, "expertise": False})
        if col == 1:
            if not st.get("maitrise"):
                return                                   # l'expertise exige la maîtrise
            st["expertise"] = not st.get("expertise")
        else:
            st["maitrise"] = not st.get("maitrise")
            if not st["maitrise"]:
                st["expertise"] = False
        self.changed()

    def _on_save_click(self, row: int, col: int):
        if not 0 <= row < len(ABILITIES):
            return
        if col == self.SAVE_ROLL_COL:
            roll_dice(self.win, self.engine.save_spec(ABILITIES[row]))
            return
        ab = ABILITIES[row]
        if ab in self.engine.resilient_saves():         # maîtrise imposée par un don : non modifiable
            return
        self.ch.sauvegardes[ab] = not self.ch.sauvegardes.get(ab, False)
        self.changed()

    # ------------------------------------------------------------------ rafraîchissement
    ROLL_COL, SAVE_ROLL_COL = 7, 4

    def _roll_cell(self, tip: str):
        it = cell("", "center", "<qt><b>🎲 {}</b><br/>Ouvre le lancer de d20 animé.</qt>".format(tip))
        if getattr(self, "_icon_key", None) != theme.current().key:
            self._icon, self._icon_key = d20_icon(22), theme.current().key
        it.setIcon(self._icon)
        return it

    @staticmethod
    def _calc_tip(title: str, row: dict) -> str:
        """Détail du calcul (source → valeur) + avantages / désavantages et leur origine."""
        notes = []
        if row.get("avantage"):
            notes.append("▲ Avantage : " + ", ".join(row["avantage"]))
        if row.get("desavantage"):
            notes.append("▼ Désavantage : " + ", ".join(row["desavantage"]))
        if row.get("echec"):
            notes.append("✖ Échec automatique : " + ", ".join(row["echec"]))
        if row.get("avantage") and row.get("desavantage"):
            notes.append("Avantage et désavantage s'annulent (PHB).")
        total = R.fmt_bonus(row["bonus"]) + "".join(" " + d for d in row.get("des", []))
        return calc_tip(title, row.get("detail", []), total, notes)

    def refresh(self):
        self.mark_box(self.skills_box, "Compétences", "caracteristiques", "Compétences")
        eng, t = self.engine, theme.current()
        rows = eng.skill_rows()
        self.table.setUpdatesEnabled(False)
        st = eng.class_skill_status()
        options = set(st["options"])
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            name = row["nom"]
            self.table.setItem(r, 0, check_item(row["maitrise"], True, "Maîtrise — cliquez sur la ligne"))
            self.table.setItem(r, 1, check_item(row["expertise"], row["maitrise"],
                                                "Expertise (bonus de maîtrise doublé)" if row["maitrise"]
                                                else "L'expertise exige la maîtrise"))
            src = []
            if row["historique"]:
                src.append("Historique")
            if name in options:
                src.append("Classe")
            if row["expertise"]:
                src.append("Expertise")
            tip = self._calc_tip(name, row)
            badge, role = adv_badge(row["etat"])
            bonus_txt = R.fmt_bonus(row["bonus"]) + ("".join(" " + d for d in row["des"]) if row["des"] else "")
            items = [cell(name, "left", tip),
                     cell(R.ABBR.get(row["carac"], row["carac"]), "center", tip),
                     cell(bonus_txt, "center", tip, color=t.accent_text, bold=True),
                     cell(", ".join(src), "left", tip),
                     cell(badge, "center", tip, color=getattr(t, role) if role else None, bold=True)]
            items.append(self._roll_cell("Lancer le d20 : " + name))
            for col, it in enumerate(items, start=2):
                if name in options:
                    it.setBackground(QBrush(QColor(t.highlight)))
                self.table.setItem(r, col, it)

        for r, s in enumerate(eng.save_rows()):
            tip = self._calc_tip("Jet de sauvegarde de " + s["carac"], s)
            badge, role = adv_badge(s["etat"])
            self.saves.setItem(r, 0, check_item(s["maitrise"], not s["auto"],
                                                "Maîtrise accordée par un don" if s["auto"] else "Maîtrise du jet de sauvegarde"))
            self.saves.setItem(r, 1, cell(s["carac"], "left", tip))
            self.saves.setItem(r, 2, cell(R.fmt_bonus(s["bonus"]) + "".join(" " + d for d in s["des"]), "center", tip,
                                          color=t.accent_text, bold=True))
            self.saves.setItem(r, 3, cell(badge, "center", tip, color=getattr(t, role) if role else None, bold=True))
            self.saves.setItem(r, 4, self._roll_cell("Lancer le jet de sauvegarde de " + s["carac"]))

        self.table.setUpdatesEnabled(True)
        if self.compact:
            fit_table_height(self.table)
            fit_table_height(self.saves)
        n_ok = len(st["choisies"])
        warn = "  ⚠ trop de compétences cochées" if n_ok > st["nombre"] else ""
        self.status.setText("Compétences de classe ({}) : {}/{} choisies parmi {}.{}".format(
            eng.first_class(), n_ok, st["nombre"], ", ".join(st["options"]) or "—", warn))
        self.passive.setText("Perception passive : {}".format(eng.passive_perception()))
