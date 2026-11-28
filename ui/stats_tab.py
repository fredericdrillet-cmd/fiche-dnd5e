"""
Onglet unique « Caractéristiques & Compétences » : vue fluide et défilante qui regroupe
    - en haut : la génération des caractéristiques (achat de points, 4d6, saisie manuelle), bonus raciaux, totaux ;
    - en dessous : compétences, jets de sauvegarde et valeurs passives (tables à hauteur ajustée, sans défilement
      interne : toute la page défile d'un bloc).
Les deux panneaux d'origine (AbilitiesTab, SkillsTab) sont réutilisés tels quels : aucune fonctionnalité perdue.
v48 — Mode guidé : les sélecteurs de caractéristiques brutes sont retirés (choisis dans l'assistant de création,
puis améliorés par « Niveau supérieur ») ; un résumé en lecture seule les remplace. Ils réapparaissent en Mode libre,
ou tant qu'un choix de caractéristique reste à faire (ancienne fiche).
"""
from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QGridLayout, QGroupBox, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from core import rules as R
from core.rules import ABILITIES

from .abilities_tab import AbilitiesTab
from .common import BaseTab, make_label, rich_tip
from .skills_tab import SkillsTab


class StatsTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        lay = QVBoxLayout(body)
        lay.setSpacing(4)                                # v51 : page compacte, sans défilement sur un écran 1080p
        lay.setContentsMargins(4, 2, 4, 2)
        self.abilities = AbilitiesTab(win)
        self.abilities.set_compact_layout()              # v53 : Mode libre — sans défilement en 16:9
        self.skills = SkillsTab(win, compact=True)
        # résumé en lecture seule (Mode guidé)
        self.summary = QGroupBox("Caractéristiques (lecture seule — Mode guidé)")
        g = QGridLayout(self.summary)
        self.summary_cells = {}
        for i, ab in enumerate(ABILITIES):
            from .ability_icons import icon_button        # v53 : grande icône cliquable = test de caractéristique
            head = QHBoxLayout()
            head.setSpacing(8)
            head.addStretch(1)
            head.addWidget(icon_button(ab, 52, self._roll_check))
            names = QVBoxLayout()
            names.setSpacing(0)
            names.addWidget(make_label(R.ABBR[ab], "head"))
            val = make_label("", "stat")
            names.addWidget(val)
            head.addLayout(names)
            head.addStretch(1)
            g.addLayout(head, 0, i)
            self.summary_cells[ab] = val
        self.summary.setToolTip(rich_tip("Caractéristiques", "Valeurs choisies dans l'assistant de création ; les "
                                         "améliorations passent par « ▲ Niveau supérieur ». Mode libre (Options) : "
                                         "édition directe."))      # v51 : texte explicatif déplacé en infobulle
        lay.addWidget(self.summary)
        lay.addWidget(self.abilities)
        lay.addWidget(self.skills)
        lay.addStretch(1)

    def _roll_check(self, ab: str) -> None:
        from .dice_dialog import roll_dice
        roll_dice(self.win, self.engine.ability_check_spec(ab))

    def editors_visible(self) -> bool:
        if getattr(self.win, "free_mode", True):
            return True
        return any(m["onglet"] == "caracteristiques" and m["encart"] != "Compétences"
                   for m in self.engine.missing_choices())

    def refresh(self):
        show = self.editors_visible()
        self.abilities.setVisible(show)
        self.summary.setVisible(not show)
        if show:
            self.abilities.refresh()
        else:
            eng = self.engine
            for ab, w in self.summary_cells.items():
                w.setText("{} ({})".format(eng.score(ab), R.fmt_bonus(eng.mod(ab))))
                w.setToolTip(rich_tip(ab, "Valeur {} — modificateur {}".format(eng.score(ab), R.fmt_bonus(eng.mod(ab)))))
        self.skills.refresh()
