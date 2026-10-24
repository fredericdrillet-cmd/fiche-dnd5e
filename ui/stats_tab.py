"""
Onglet unique « Caractéristiques & Compétences » : vue fluide et défilante qui regroupe
    - en haut : la génération des caractéristiques (achat de points, 4d6, saisie manuelle), bonus raciaux, totaux ;
    - en dessous : compétences, jets de sauvegarde et valeurs passives (tables à hauteur ajustée, sans défilement
      interne : toute la page défile d'un bloc).
Les deux panneaux d'origine (AbilitiesTab, SkillsTab) sont réutilisés tels quels : aucune fonctionnalité perdue.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from .abilities_tab import AbilitiesTab
from .common import BaseTab
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
        lay.setSpacing(8)
        self.abilities = AbilitiesTab(win)
        self.skills = SkillsTab(win, compact=True)
        lay.addWidget(self.abilities)
        lay.addWidget(self.skills)
        lay.addStretch(1)

    def refresh(self):
        self.abilities.refresh()
        self.skills.refresh()
