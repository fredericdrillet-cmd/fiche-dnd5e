"""
Fenêtre de repos interactive (court / long), présentée comme les confirmations « jeu vidéo » (fond flouté).

Repos court (1 heure) : dépense des dés de vie un par un (jet + modificateur de Constitution, PV mis à jour en
direct), liste des aptitudes rechargées. Repos long (8 heures) : liste de tout ce qui est restauré, rappel de la
règle « un repos long par 24 heures » et, si la règle de survie est active (Options), vérification des rations.
« Annuler » rétablit les PV et dés de vie d'avant l'ouverture.
v44 : au repos long, boutons « Changer les sorts préparés » (Clerc, Druide, Paladin, Artificier, Magicien) et
« Changer un tour de magie » (Magicien, Tasha) ; les choix sont appliqués à la fin du repos.
"""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QCheckBox, QDialog, QFrame, QGraphicsDropShadowEffect, QGridLayout, QHBoxLayout,
                             QPushButton, QVBoxLayout)

from core import engine_extras as X
from .common import make_label
from .dialogs import BlurBackdrop


class RestDialog(QDialog):
    def __init__(self, win, kind: str):
        super().__init__(win)
        self.win, self.kind = win, kind
        eng, ch = win.engine, win.engine.ch
        self._snapshot = (ch.pv_actuels, dict(ch.des_vie_utilises))
        self.log: list[str] = []
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setStyleSheet("RestDialog { background: transparent; background-image: none; }")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 26, 26, 30)
        card = QFrame()
        card.setObjectName("dialogCard")
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(38)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 175))
        card.setGraphicsEffect(shadow)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(28, 24, 28, 22)
        lay.setSpacing(10)
        outer.addWidget(card)
        # v45 : fenêtre plus large (les libellés ne sont plus tronqués ni renvoyés à la ligne inutilement)
        card.setMinimumWidth(760 if kind == "long" else 620)
        self.setMinimumWidth(820 if kind == "long" else 680)

        long_rest = kind == "long"
        minutes = eng.long_rest_minutes() if long_rest else X.SHORT_REST_MIN
        lay.addWidget(make_label(("🌙  Repos long" if long_rest else "🔥  Repos court"), "title"))
        lay.addWidget(make_label("⏳ Temps écoulé : {} — {} → {}".format(
            ("4 heures (Transe elfique)" if minutes == 240 else "8 heures") if long_rest else "1 heure",
            eng.time_text(), eng.time_text(ch.temps_minutes + minutes)),
            "head", wrap=True))
        self.hp = make_label("", "stat")
        lay.addWidget(self.hp)

        if not long_rest:
            lay.addWidget(make_label("Dépensez des dés de vie : chaque dé rend 1 dé + votre modificateur de Constitution "
                                     "({:+d}) PV.".format(eng.mod("Constitution")), "muted", wrap=True))
            self.dice_grid = QGridLayout()
            self.dice_rows: dict[str, dict] = {}
            for r, pool in enumerate(eng.hit_dice_pool()):
                row = {"label": make_label(""), "btn": QPushButton("🎲 Dépenser 1 {}".format(pool["de"]))}
                row["btn"].clicked.connect(lambda _=False, d=pool["de"]: self._spend(d))
                self.dice_grid.addWidget(row["label"], r, 0)
                self.dice_grid.addWidget(row["btn"], r, 1)
                self.dice_rows[pool["de"]] = row
            lay.addLayout(self.dice_grid)
            self.log_label = make_label("", "muted", wrap=True)
            lay.addWidget(self.log_label)
            recharges = eng.short_rest_recharges()
        else:
            recharges = eng.long_rest_recharges()
        lay.addWidget(make_label("Rechargé à la fin du repos :", "head"))
        lay.addWidget(make_label("<br/>".join("✔ " + html.escape(x) for x in recharges), wrap=True))
        ending = eng.effects_ending(long_rest)
        if ending:
            lay.addWidget(make_label("Effets temporaires qui prendront fin :", "head"))
            lay.addWidget(make_label("⌛ " + ", ".join(html.escape(x) for x in ending)
                                     + "<br/><i>Les traits raciaux et aptitudes permanentes sont conservés.</i>",
                                     "muted", wrap=True))

        self.pending_prep: dict[str, list[str]] = {}     # v44 : sorts préparés choisis, appliqués à la fin du repos
        self.spell_messages: list[str] = []
        self.pending_cantrip = None                      # v44 : (ancien, nouveau) tour de magie du Magicien
        self.prep_labels: dict[str, object] = {}
        self.cantrip_label = None
        if long_rest:
            self._build_spell_section(lay)

        self.ration = None
        if long_rest:
            warn = eng.long_rest_warning()
            if warn:
                lay.addWidget(make_label("⚠ " + warn, "warn", wrap=True))
            if win.settings.get("regle_survie"):
                n = eng.rations_available()
                self.ration = QCheckBox("Consommer 1 ration (rations dans l'inventaire : {})".format(n))
                self.ration.setChecked(n > 0)
                self.ration.setEnabled(n > 0)
                lay.addWidget(self.ration)
                if n == 0:
                    lay.addWidget(make_label("⚠ Aucune ration : le personnage se repose le ventre vide. Au-delà de "
                                             "3 + modificateur de Constitution jours sans manger, il subit un niveau "
                                             "d'épuisement par jour (PHB).", "warn", wrap=True))

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setProperty("role", "ghost")
        self.ok_btn = QPushButton("Se reposer")
        for b in (self.cancel_btn, self.ok_btn):
            b.setMinimumWidth(120)
            buttons.addWidget(b)
        lay.addLayout(buttons)
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self._update()

    # ------------------------------------------------------------------ v44 : sorts de la journée à venir
    def _build_spell_section(self, lay) -> None:
        eng = self.win.engine
        classes = eng.rest_prepare_classes()
        cantrip = eng.cantrip_swap_available()
        if not classes and not cantrip:
            return
        lay.addWidget(make_label("📖 Sorts pour la journée à venir :", "head"))
        lay.addWidget(make_label("Les changements sont appliqués à la fin du repos (« Se reposer ») ; « Annuler » "
                                 "les abandonne.", "muted", wrap=True))
        grid = QGridLayout()
        row = 0
        for cls in classes:
            btn = QPushButton("[ Changer les sorts préparés ]" + (" — {}".format(cls) if len(classes) > 1 else ""))
            btn.setToolTip("{} : choisir les sorts préparés pour la journée (niveau de classe + modificateur "
                           "d'incantation).".format(cls))
            btn.clicked.connect(lambda _=False, c=cls: self.open_prepare(c))
            label = make_label("", "muted", wrap=True)
            grid.addWidget(btn, row, 0)
            grid.addWidget(label, row, 1)
            self.prep_labels[cls] = label
            row += 1
        if cantrip:
            btn = QPushButton("[ Changer un tour de magie ]")
            btn.setToolTip("Magicien — Formules de sorts mineurs (Tasha) : remplacer un tour de magie connu par un "
                           "autre tour de magie de la liste du Magicien.")
            btn.clicked.connect(lambda _=False: self.open_cantrip())
            self.cantrip_label = make_label("", "muted", wrap=True)
            grid.addWidget(btn, row, 0)
            grid.addWidget(self.cantrip_label, row, 1)
        lay.addLayout(grid)
        self._update_spell_labels()

    def _update_spell_labels(self) -> None:
        eng = self.win.engine
        for cls, label in self.prep_labels.items():
            info = eng.rest_prepare_info(cls)
            if info is None:
                continue
            chosen = self.pending_prep.get(cls)
            n = len(chosen) if chosen is not None else len(info["prepares"])
            label.setText("{} — préparés : {} / {}{}".format(cls, n, info["maximum"],
                                                            " ✎ (modifié)" if chosen is not None else ""))
        if self.cantrip_label is not None:
            self.cantrip_label.setText("🔁 {} → {}".format(*self.pending_cantrip) if self.pending_cantrip else
                                       "Magicien — tours de magie inchangés")

    def open_prepare(self, cls: str) -> bool:
        from .spell_rest_dialogs import PrepareSpellsDialog
        info = self.win.engine.rest_prepare_info(cls)
        if info is None:
            return False
        dlg = PrepareSpellsDialog(self, info, self.pending_prep.get(cls))
        if dlg.exec() != 1:
            return False
        return self.set_prepared_choice(cls, dlg.selected)

    def set_prepared_choice(self, cls: str, names) -> bool:
        info = self.win.engine.rest_prepare_info(cls)
        if info is None or len(list(names)) > info["maximum"]:
            return False
        self.pending_prep[cls] = list(names)
        self._update_spell_labels()
        return True

    def open_cantrip(self) -> bool:
        from .spell_rest_dialogs import CantripSwapDialog
        eng = self.win.engine
        dlg = CantripSwapDialog(self, eng.cantrip_swap_known(), eng.cantrip_swap_options())
        if dlg.exec() != 1 or dlg.choice() is None:
            return False
        return self.set_cantrip_choice(*dlg.choice())

    def set_cantrip_choice(self, old: str, new: str) -> bool:
        eng = self.win.engine
        if not any(s["nom"] == old for s in eng.cantrip_swap_known()) or \
                not any(s["nom"] == new for s in eng.cantrip_swap_options()):
            return False
        self.pending_cantrip = (old, new)
        self._update_spell_labels()
        return True

    def _apply_spell_changes(self) -> list[str]:
        eng, out = self.win.engine, []
        if self.pending_cantrip:
            ok, msg = eng.swap_cantrip(*self.pending_cantrip)
            out.append(msg)
        for cls, names in self.pending_prep.items():
            ok, msg = eng.rest_set_prepared(cls, names)
            out.append(msg)
        return out

    # ------------------------------------------------------------------ logique
    def _update(self):
        eng, ch = self.win.engine, self.win.engine.ch
        cur = ch.pv_actuels if ch.pv_actuels >= 0 else eng.hp_max()
        target = eng.hp_max() if self.kind == "long" else cur
        self.hp.setText("❤ PV : {} / {}{}".format(cur, eng.hp_max(), "  →  {}".format(target) if target != cur else ""))
        if self.kind == "short":
            for pool in eng.hit_dice_pool():
                row = self.dice_rows.get(pool["de"])
                if row:
                    row["label"].setText("{} : {} / {} restant(s)".format(pool["de"], pool["restants"], pool["total"]))
                    row["btn"].setEnabled(pool["restants"] > 0 and cur < eng.hp_max())
            self.log_label.setText("<br/>".join(self.log[-6:]))

    def _spend(self, die: str, roll: int | None = None):
        res = self.win.engine.spend_hit_die(die, roll)
        if res:
            self.log.append("🎲 {} : {} {:+d} (Con) → +{} PV".format(res["de"], res["jet"], res["con"], res["gain"]))
        self._update()
        return res

    def apply(self):
        eng = self.win.engine
        if self.kind == "long":
            eng.do_long_rest(eat_ration=bool(self.ration and self.ration.isChecked()))
            self.spell_messages = self._apply_spell_changes()
        else:
            eng.do_short_rest()

    def restore(self):
        ch = self.win.engine.ch
        ch.pv_actuels, ch.des_vie_utilises = self._snapshot[0], dict(self._snapshot[1])

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self.adjustSize()
        parent = self.parentWidget()
        if parent is not None:
            self.move(parent.frameGeometry().center() - self.rect().center())


def run_rest(win, kind: str) -> bool:
    """Ouvre la fenêtre de repos ; applique le repos si validé, sinon annule les dés de vie dépensés."""
    backdrop = BlurBackdrop(win)
    dialog = RestDialog(win, kind)
    try:
        ok = dialog.exec() == 1
    finally:
        backdrop.dispose()
    if ok:
        dialog.apply()
        msgs = getattr(dialog, "spell_messages", None)
        if kind == "long" and isinstance(msgs, list) and msgs:
            win.statusBar().showMessage(" ".join(msgs), 10000)
        # v44 : la préparation se fait désormais DANS la fenêtre de repos (bouton « Changer les sorts préparés ») ;
        # offer_preparation() reste disponible pour l'onglet Magie
    else:
        dialog.restore()
    return ok


def offer_preparation(win) -> bool:
    """Après un repos long (comme Solasta) : les lanceurs à préparation (Clerc, Druide, Paladin, Artificier,
    Magicien) peuvent changer leurs sorts préparés ; on propose d'ouvrir l'onglet Magie sur la bonne classe."""
    from .dialogs import ask_yes_no
    casters = [c for c in win.engine.casters() if c.get("prepares_max") is not None]
    if not casters:
        return False
    names = ", ".join(c["classe"] for c in casters)
    if not ask_yes_no(win, "Préparation des sorts", "Repos long terminé : vous pouvez changer vos sorts préparés "
                      "({}).\n\nOuvrir l'onglet Magie pour les revoir maintenant ?".format(names),
                      yes="Revoir mes sorts", no="Plus tard", default_no=False):
        return False
    if hasattr(win, "go_to_tab"):
        win.go_to_tab("magie")
    tab = getattr(win, "magic_tab", None)
    if tab is not None:
        tab.select_class(casters[0]["classe"])
        tab.prepared_only.setChecked(False)             # le grimoire complet, pour choisir quoi préparer
    return True
