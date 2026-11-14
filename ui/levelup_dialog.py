"""
Assistant « Niveau supérieur » (v29, inspiré de Baldur's Gate 3 et Solasta).

Six étapes, à gauche une colonne de pastilles ○ / ✔ :
    1. Classe à monter (multiclassage proposé avec ses prérequis) ;
    2. Points de vie (moyenne fixe du dé de vie, comme le reste de la fiche) ;
    3. Aptitudes gagnées (lecture seule) ;
    4. Choix du niveau : sous-classe, amélioration ou don (une carte par emplacement : +2, +1 à deux
       caractéristiques DIFFÉRENTES, ou don avec infobulle au survol et résumé sous le sélecteur), style de combat,
       faveur de pacte ;
    5. Nouveaux sorts (v40) : quotas de la classe à ce niveau (sorts mineurs, sorts connus, grimoire) et liste des
       sorts apprenables ; la préparation quotidienne reste dans l'onglet Magie ; v44 : encart facultatif
       « Remplacer un sort connu » (classes à sorts connus : oublier 1 sort, puis choisir son remplaçant, écoles
       imposées du Chevalier occulte / de l'Arnaqueur arcanique respectées) ;
    6. Récapitulatif avant / après.
Les compétences, langues… restent listées « à faire ensuite ». « Confirmer » reste grisé tant qu'un choix des étapes
4 ou 5 manque (motif en infobulle). Les pages 4 et 5 défilent : rien n'est coupé. Tout se fait sur une copie :
« Annuler » ne change rien à la fiche.
"""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QComboBox, QDialog, QFrame, QGraphicsDropShadowEffect, QGridLayout, QHBoxLayout,
                             QCheckBox, QLineEdit, QListWidget, QListWidgetItem, QProgressBar, QPushButton,
                             QScrollArea, QSizeGrip, QSizePolicy, QStackedWidget, QTabWidget, QTextBrowser, QVBoxLayout,
                             QWidget)

from core.levelup import SCHOOLS, filter_spells, roadmap_icons
from core.rules import ABILITIES
from . import theme
from .common import blocked, make_label, rich_tip
from .dialogs import BlurBackdrop
from .class_guide_panel import ClassGuidePanel, subclass_html
from .game_widgets import clear_layout
from .spell_inspector import make_inspector, spell_card_html

STEPS = ["Classe", "Points de vie", "Aptitudes gagnées", "Choix du niveau", "Nouveaux sorts", "Récapitulatif"]
SPELL_STEP = 4
NO_CHOICE = "— à choisir —"
ALL_SCHOOLS = "Toutes les écoles"
ASI_MODES = {"+2 à une caractéristique": "plus2", "+1 à deux caractéristiques": "plus1x2", "Don": "don"}


class LevelUpDialog(QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win, self.engine = win, win.engine
        # v50 : vraie fenêtre (barre de titre, boutons Réduire / Agrandir / Fermer) : maximisable et redimensionnable
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowSystemMenuHint
                            | Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("Niveau supérieur")
        self.setModal(True)
        self.setMinimumSize(900, 600)
        self._fit_to_screen()
        # v51 : en Mode guidé, une classe dont les prérequis de multiclassage ne sont pas remplis n'est pas proposée
        # (elle est listée « 🔒 » avec la raison) ; elle ne peut donc plus bloquer « Confirmer » en cours de route
        every = self.engine.level_up_options()
        guided = not getattr(win, "free_mode", False)
        self.locked_options = [o for o in every if o["prerequis"]] if guided else []
        self.options = [o for o in every if not (guided and o["prerequis"])]
        self.sim = None
        self.cls = ""
        self.report: dict = {}
        self.step = 0
        self.choice_widgets: dict = {}
        self.style_labels: dict = {}
        self.swap_widgets: dict = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        card = QFrame()
        card.setObjectName("dialogCard")
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(38)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 175))
        card.setGraphicsEffect(shadow)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(28, 24, 28, 22)
        lay.setSpacing(12)
        self.title = make_label("▲  Niveau supérieur", "title")
        lay.addWidget(self.title)

        body = QHBoxLayout()
        self.step_list = QListWidget()
        self.step_list.setFixedWidth(250)
        self.step_list.currentRowChanged.connect(self._on_step_clicked)
        body.addWidget(self.step_list)
        self.pages = QStackedWidget()
        body.addWidget(self.pages, 1)
        lay.addLayout(body, 1)

        # --- page 1 : classe (zones défilantes pour toutes les pages : rien n'est coupé)
        p1 = self._scroll_page("_p1_lay")
        l1 = self._p1_lay
        l1.addWidget(make_label("Quelle classe gagne un niveau ?", "head"))
        self.class_combo = QComboBox()
        self.class_combo.addItems([o["label"] for o in self.options])
        self.class_combo.currentIndexChanged.connect(self._on_class)
        l1.addWidget(self.class_combo)
        self.prereq = make_label("", "warn", wrap=True)
        l1.addWidget(self.prereq)
        self.locked_label = make_label("", "muted", wrap=True)
        self.locked_label.setText("🔒 Multiclassage indisponible (prérequis officiels de caractéristiques) :<br/>" +
                                  "<br/>".join("• {} — {}".format(html.escape(o["classe"]), html.escape(o["prerequis"]))
                                               for o in self.locked_options) +
                                  "<br/><i>Mode libre (Options) : possible avec l'accord du MJ.</i>"
                                  if self.locked_options else "")
        l1.addWidget(self.locked_label)
        self.class_info = make_label("", "muted", wrap=True)
        l1.addWidget(self.class_info)
        self.guide = ClassGuidePanel()                    # v49 : fiche pédagogique de la classe et des sous-classes
        l1.addWidget(self.guide)
        l1.addStretch(1)
        self.pages.addWidget(p1)
        # --- page 2 : points de vie
        p2 = self._scroll_page("_p2_lay")
        l2 = self._p2_lay
        l2.addWidget(make_label("Points de vie gagnés", "head"))
        self.hp_info = make_label("", wrap=True)
        l2.addWidget(self.hp_info)
        l2.addStretch(1)
        self.pages.addWidget(p2)
        # --- page 3 : aptitudes
        p3 = QWidget()
        l3 = QVBoxLayout(p3)
        self.feats_view = QTextBrowser()
        l3.addWidget(self.feats_view)
        self.pages.addWidget(p3)
        # --- page 4 : choix (zone défilante : rien n'est coupé, quel que soit le nombre de choix)
        self.pages.addWidget(self._scroll_page("choices_lay"))
        # --- page 5 : nouveaux sorts (v40)
        self.pages.addWidget(self._scroll_page("spells_lay"))
        self.spell_added: dict[str, list[str]] = {}
        # --- page 5 : récapitulatif
        p5 = QWidget()
        l5 = QVBoxLayout(p5)
        self.recap_view = QTextBrowser()
        l5.addWidget(self.recap_view)
        self.pages.addWidget(p5)

        buttons = QHBoxLayout()
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setProperty("role", "ghost")
        self.cancel_btn.clicked.connect(self.reject)
        self.prev_btn = QPushButton("◀ Précédent")
        self.prev_btn.clicked.connect(lambda: self.go(self.step - 1))
        self.next_btn = QPushButton("Suivant ▶")
        self.next_btn.clicked.connect(lambda: self.go(self.step + 1))
        self.confirm_btn = QPushButton("✔ Confirmer le niveau")
        self.confirm_btn.clicked.connect(self._on_confirm)
        buttons.addWidget(self.cancel_btn)
        buttons.addStretch(1)
        for b in (self.prev_btn, self.next_btn, self.confirm_btn):
            b.setMinimumWidth(130)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            buttons.addWidget(b)
        grip = QSizeGrip(card)                           # v42 : fenêtre redimensionnable (poignée en bas à droite)
        buttons.addWidget(grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        lay.addLayout(buttons)
        outer.addWidget(card)

        if self.options:
            self._on_class(0)
        self.go(0)

    def _fit_to_screen(self) -> None:
        """v42 : taille par défaut confortable (jusqu'à 85 % de l'écran, 1200 × 820 visés), sans jamais dépasser
        l'écran ; la poignée en bas à droite permet d'agrandir encore."""
        screen = self.screen() if hasattr(self, "screen") else None
        geo = screen.availableGeometry() if screen is not None else None
        try:
            sw, sh = int(geo.width()), int(geo.height())
        except (AttributeError, TypeError, ValueError):
            sw, sh = 1600, 1000
        w = max(900, min(max(1200, int(sw * 0.75)), sw - 40))
        h = max(600, min(max(820, int(sh * 0.85)), sh - 40))
        self.resize(w, h)

    def _scroll_page(self, attr: str) -> QScrollArea:
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(4, 4, 12, 4)
        lay.setSpacing(10)
        setattr(self, attr, lay)
        area.setWidget(inner)
        return area

    # ------------------------------------------------------------------ état
    def option(self) -> dict:
        i = self.class_combo.currentIndex()
        return self.options[i] if 0 <= i < len(self.options) else {}

    def pending(self) -> list[dict]:
        """Choix de l'étape 4 encore à faire (sur la copie)."""
        if self.sim is None:
            return []
        return list(self.engine.level_up_report(self.sim, self.cls)["dans_assistant"])

    def _rebuild_report(self) -> None:
        self.report = self.engine.level_up_report(self.sim, self.cls) if self.sim is not None else {}

    # ------------------------------------------------------------------ navigation
    def go(self, step: int) -> None:
        self.step = max(0, min(len(STEPS) - 1, step))
        self.pages.setCurrentIndex(self.step)
        self._refresh_steps()

    def _on_step_clicked(self, row: int) -> None:
        if 0 <= row < len(STEPS) and row != self.step:
            self.go(row)

    def _refresh_steps(self) -> None:
        missing = self.pending()
        choices = [m for m in missing if m.get("kind") != "sorts"]
        spells = [m for m in missing if m.get("kind") == "sorts"]
        done = [bool(self.sim), bool(self.sim), bool(self.sim), not choices, bool(self.sim) and not spells,
                bool(self.sim) and not missing]
        with blocked(self.step_list):
            self.step_list.clear()
            for i, name in enumerate(STEPS):
                mark = "✔" if done[i] else "○"
                n = len(choices) if i == 3 else len(spells) if i == SPELL_STEP else 0
                self.step_list.addItem("{} {}. {}{}".format(mark, i + 1, name, "  ({})".format(n) if n else ""))
            self.step_list.setCurrentRow(self.step)
        self.prev_btn.setEnabled(self.step > 0)
        self.next_btn.setEnabled(self.step < len(STEPS) - 1)
        ok = self.sim is not None and not missing
        self.confirm_btn.setEnabled(ok)
        self.confirm_btn.setToolTip("" if ok else rich_tip("Choix manquants", "Faites d'abord les étapes 4 et 5 : " +
                                                           "; ".join(m["message"] for m in missing) if missing else
                                                           "Choisissez une classe."))

    # ------------------------------------------------------------------ étape 1
    def _on_class(self, index: int = 0) -> None:
        opt = self.option()
        if not opt:
            return
        self.cls = opt["classe"]
        self.sim = self.engine.simulate_level_up(self.cls)
        self.spell_added = {}
        self.title.setText("▲  Niveau supérieur — {} {} → {}".format(self.cls, opt["avant"] or "—", opt["apres"]))
        self.prereq.setText("⚠ Prérequis de multiclassage non remplis : {}. (Possible avec l'accord du MJ.)".format(
            opt["prerequis"]) if opt["prerequis"] else "")
        entry = self.sim.ch.find_class(self.cls) or {}
        self.guide.set_class(self.sim, self.cls, entry.get("sous_classe", ""))
        hp = self.sim.level_hp_info(self.cls)
        self.class_info.setText("Dé de vie {} — niveau global {} → {}.".format(
            hp["de"], self.engine.total_level, self.sim.total_level))
        self._refresh_all_pages()

    def _refresh_all_pages(self) -> None:
        self._rebuild_report()
        self._refresh_hp()
        self._refresh_feats()
        self._build_choices()
        self._build_spells()
        self._refresh_recap()
        self._refresh_steps()

    # ------------------------------------------------------------------ étape 2
    def _refresh_hp(self) -> None:
        hp = self.sim.level_hp_info(self.cls)
        how = ("maximum du dé de vie ({})".format(hp["moyenne"]) if hp["premier"] else
               "moyenne du {} : {}".format(hp["de"], hp["moyenne"]))
        self.hp_info.setText("<b>+{} PV</b> — {} {:+d} (Constitution){}.<br/>PV maximum : {} → <b>{}</b>.<br/>"
                             "<i>La fiche applique la moyenne fixe du dé de vie à chaque niveau (règle du Manuel des "
                             "Joueurs).</i>".format(hp["gain"], how, hp["con"],
                                                    " {:+d} (aptitudes, race)".format(hp["bonus"]) if hp["bonus"] else "",
                                                    self.engine.hp_max(), self.sim.hp_max()))

    # ------------------------------------------------------------------ étape 3
    def _refresh_feats(self) -> None:
        t = theme.current()
        feats = self.report.get("aptitudes", [])
        entry = self.sim.ch.find_class(self.cls)
        road = self.sim.class_roadmap(entry)
        nxt = next((c for c in road if c["niveau"] > entry["niveau"] and roadmap_icons(c)), None)
        parts = ["<h3 style='color:{}'>Niveau {} de {}</h3>".format(t.accent_text, entry["niveau"], html.escape(self.cls))]
        if not feats:
            parts.append("<p><i>Aucune nouvelle aptitude à ce niveau (progression des valeurs seulement).</i></p>")
        for f in feats:
            parts.append("<p><b>✦ {}</b>{}<br/>{}</p>".format(
                html.escape(f["nom"]), " <i>({})</i>".format(html.escape(f["source"])) if f["sous_classe"] else "",
                html.escape(f["description"])))
        if nxt:
            parts.append("<hr/><p style='color:{}'><i>Prochain palier : niveau {} {} — {}</i></p>".format(
                t.muted, nxt["niveau"], roadmap_icons(nxt), html.escape(", ".join(nxt["aptitudes"]) or
                                                                         "amélioration ou don")))
        self.feats_view.setHtml("".join(parts))

    # ------------------------------------------------------------------ étape 4
    def _build_choices(self) -> None:
        clear_layout(self.choices_lay)
        self.choice_widgets = {}
        self.style_labels = {}
        rep = self.report
        self.choices_lay.addWidget(make_label("Choix à faire maintenant", "head"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        row = 0
        entry = self.sim.ch.find_class(self.cls)
        kinds = {m["kind"] for m in rep.get("dans_assistant", [])}
        # sous-classe (on garde le choix visible une fois fait, pour pouvoir le changer)
        need_sub = "sous_classe" in kinds or (entry.get("sous_classe") and entry.get("_wizard_sub"))
        if need_sub:
            combo = QComboBox()
            subs = [s["nom"] for s in self.sim.db.subclasses(self.cls)]
            combo.addItems([NO_CHOICE] + subs)
            if entry.get("sous_classe") in subs:
                combo.setCurrentIndex(subs.index(entry["sous_classe"]) + 1)
            combo.activated.connect(lambda _=0, c=combo: self._set_sub(c.currentText()))
            for i, n in enumerate(subs):                 # v49 : résumé de chaque sous-classe au survol
                summ = self.sim.subclass_summary(self.cls, n) or {}
                unofficial = self.sim.db.subclass_tips(self.cls).get(n, "")
                combo.setItemData(i + 1, "<qt><b>{}</b>{}<br/>{}<br/>{}</qt>".format(
                    html.escape(n), "<br/><i>{}</i>".format(html.escape(unofficial)) if unofficial else "",
                    html.escape(" · ".join(summ.get("orientation", []))), "<br/>".join(
                        "Niv. {} — {}".format(lvl, html.escape(nm)) for lvl, nm, _ in summ.get("pouvoirs", [])[:5])),
                    Qt.ItemDataRole.ToolTipRole)
            grid.addWidget(make_label("◆ Sous-classe"), row, 0)
            grid.addWidget(combo, row, 1, 1, 3)
            self.choice_widgets["sous_classe"] = combo
            row += 1
            if entry.get("sous_classe"):                 # fiche de la sous-classe choisie, sous le sélecteur
                view = QTextBrowser()
                view.setMinimumHeight(170)
                view.setHtml(subclass_html(self.sim, self.cls, entry["sous_classe"]))
                grid.addWidget(view, row, 0, 1, 4)
                self.choice_widgets["sous_classe_fiche"] = view
                row += 1
        # amélioration de caractéristiques ou don : une carte par emplacement (v40, plus de chevauchement)
        for slot in self._new_asi_slots():
            self._asi_card(slot)
        # style de combat (v42) : une carte par emplacement, infobulle au survol, aperçu dynamique et résumé
        for slot in self._new_style_slots():
            self._style_card(slot)
        # faveur de pacte — v45 : seulement quand le niveau est pris en Occultiste (jamais pour un Guerrier)
        warlock = self.cls == "Occultiste"
        if warlock and ("pacte" in kinds or self.sim.ch.pacte and self.engine.class_level("Occultiste") < 3 <=
                        self.sim.class_level("Occultiste")):
            combo = QComboBox()
            pacts = self.sim.pact_options()
            combo.addItems([NO_CHOICE] + pacts)
            if self.sim.ch.pacte in pacts:
                combo.setCurrentIndex(pacts.index(self.sim.ch.pacte) + 1)
            combo.activated.connect(lambda _=0, c=combo: self._set_pact(c.currentText()))
            grid.addWidget(make_label("✧ Faveur de pacte"), row, 0)
            grid.addWidget(combo, row, 1, 1, 3)
            self.choice_widgets["pacte"] = combo
            row += 1
        if warlock:
            self._invocation_card()                      # v43 : manifestations occultes de l'Occultiste
        if row == 0 and not self._new_asi_slots() and not self._new_style_slots() and not (warlock and
                                                                                         self._inv_slots()):
            grid.addWidget(make_label("Aucun choix à faire dans l'assistant à ce niveau.", "muted"), 0, 0, 1, 4)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        self.choices_lay.insertLayout(1, grid)
        later = rep.get("ensuite", [])
        if later:
            self.choices_lay.addWidget(make_label("À faire ensuite dans les onglets (pastilles ○ après confirmation)",
                                                  "head"))
            for m in later:
                self.choices_lay.addWidget(make_label("○ {} — {}".format(self.win._tab_name(m["onglet"])
                                                                         if hasattr(self.win, "_tab_name") else
                                                                         m["onglet"], m["message"]), "muted", wrap=True))
        self.choices_lay.addStretch(1)

    def _new_asi_slots(self) -> list[dict]:
        old = {s["id"] for s in self.engine.asi_slots()}
        return [s for s in self.sim.asi_slots() if s["id"] not in old]

    def _new_style_slots(self) -> list[dict]:
        old = {s["id"] for s in self.engine.fighting_style_slots() if s["debloque"]}
        return [s for s in self.sim.fighting_style_slots() if s["debloque"] and s["id"] not in old
                and s.get("classe", self.cls) in (self.cls, "")]          # v45 : choix de la classe montée seulement

    def _changed(self) -> None:
        self.sim.normalize()
        self._rebuild_report()
        self._refresh_feats()
        self._build_spells()
        self._refresh_recap()
        self._refresh_steps()

    def _set_sub(self, name: str) -> None:
        entry = self.sim.ch.find_class(self.cls)
        entry["sous_classe"] = "" if name == NO_CHOICE else name
        entry["_wizard_sub"] = True                    # garde le sélecteur visible (marqueur retiré à la confirmation)
        self._changed()
        self._build_choices()

    def _set_asi(self, sid: str, widgets, feats: list[str]) -> None:
        mode, a1, a2, feat = widgets
        m = ASI_MODES.get(mode.currentText(), "aucun")
        choice = {"mode": m}
        if a1.currentText() in ABILITIES:
            choice["a1"] = a1.currentText()
        if a2.currentText() in ABILITIES and m == "plus1x2" and a2.currentText() != choice.get("a1"):
            choice["a2"] = a2.currentText()               # « deux caractéristiques DIFFÉRENTES »
        i = feat.currentIndex() - 1
        if m == "don" and 0 <= i < len(feats):
            choice["don"] = feats[i]
        self.sim.ch.ameliorations[sid] = choice
        self._changed()
        self._build_choices()

    def feat_tip(self, name: str) -> str:
        """Infobulle d'un don : description, prérequis, bonus de caractéristique et source."""
        f = self.sim.db.feats.get(name, {})
        state, why = self.sim.feat_status(name)
        extra = []
        if f.get("prerequis") and f["prerequis"] != "Aucun":
            extra.append("Prérequis : {}{}".format(f["prerequis"], "" if state == "ok" else " ⚠ " + why))
        if f.get("asi_texte"):
            extra.append("Bonus : " + f["asi_texte"])
        if f.get("source"):
            extra.append("Source : " + f["source"])
        return rich_tip(name, (f.get("description", "") or "") + ("\n" + "\n".join(extra) if extra else ""))

    def _asi_card(self, slot: dict) -> None:
        """Carte « Amélioration ou don » : mode, puis caractéristiques (+2 / +1 et +1 différentes) ou don + résumé."""
        c = self.sim.ch.ameliorations.get(slot["id"], {})
        card = QFrame()
        card.setObjectName("opaqueBox")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)
        lay.addWidget(make_label("▲ " + slot["label"], "head"))
        row = QHBoxLayout()
        row.setSpacing(8)
        mode = QComboBox()
        modes = ["Don"] if slot.get("don_seul") else list(ASI_MODES)
        mode.addItems([NO_CHOICE] + modes)
        cur = next((k for k, v in ASI_MODES.items() if v == c.get("mode")), "")
        if cur in modes:
            mode.setCurrentIndex(modes.index(cur) + 1)
        mode.setMinimumWidth(240)
        row.addWidget(mode)
        m = c.get("mode")
        a1, a2, feat = QComboBox(), QComboBox(), QComboBox()
        for cb in (a1, a2, feat):
            cb.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
            cb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        a1.addItems([NO_CHOICE] + list(ABILITIES))
        a1.setCurrentIndex(ABILITIES.index(c["a1"]) + 1 if c.get("a1") in ABILITIES else 0)
        others = [ab for ab in ABILITIES if ab != c.get("a1")]
        a2.addItems([NO_CHOICE] + others)
        a2.setCurrentIndex(others.index(c["a2"]) + 1 if c.get("a2") in others else 0)
        feats = sorted(self.sim.db.feats, key=lambda n: (self.sim.feat_status(n)[0] != "ok", n))
        feat.addItems([NO_CHOICE] + ["{} {}".format("✔" if self.sim.feat_status(n)[0] == "ok" else "⚠", n)
                                     for n in feats])
        for i, n in enumerate(feats):                       # infobulle au survol de chaque don de la liste
            feat.setItemData(i + 1, self.feat_tip(n), Qt.ItemDataRole.ToolTipRole)
        if c.get("don") in feats:
            feat.setCurrentIndex(feats.index(c["don"]) + 1)
        if m in ("plus2", "plus1x2"):
            row.addWidget(make_label("+2 à" if m == "plus2" else "+1 à"))
            row.addWidget(a1, 1)
            if m == "plus1x2":
                row.addWidget(make_label("et +1 à"))
                row.addWidget(a2, 1)
        elif m == "don":
            row.addWidget(feat, 2)
        else:
            row.addStretch(1)
        lay.addLayout(row)
        # aperçu / résumé sous le sélecteur
        if m in ("plus2", "plus1x2"):
            gains = {c.get("a1"): 2 if m == "plus2" else 1}
            if m == "plus1x2" and c.get("a2"):
                gains[c["a2"]] = 1
            parts = ["{} {} → {}".format(ab, self.engine.score(ab), self.sim.score(ab)) for ab in gains if ab]
            over = [ab for ab in gains if ab and self.engine.score(ab) + gains[ab] > 20]
            text = " · ".join(parts) or "Choisissez la ou les caractéristiques."
            if m == "plus1x2" and not (c.get("a1") and c.get("a2")):
                text += " — choisissez deux caractéristiques différentes."
            if over:
                text += " ⚠ Maximum 20 : {}.".format(", ".join(over))
            lay.addWidget(make_label(text, "muted", wrap=True))
        elif m == "don" and c.get("don"):
            f = self.sim.db.feats.get(c["don"], {})
            state, why = self.sim.feat_status(c["don"])
            summary = "<b>{}</b> — {}{}{}".format(
                html.escape(c["don"]), html.escape(f.get("description", "")),
                "<br/><i>Bonus : {}</i>".format(html.escape(f["asi_texte"])) if f.get("asi_texte") else "",
                "" if state == "ok" else "<br/><span style='color:{}'>⚠ {}</span>".format(theme.current().warn,
                                                                                         html.escape(why)))
            lab = make_label("", wrap=True)
            lab.setTextFormat(Qt.TextFormat.RichText)
            lab.setText(summary)
            lay.addWidget(lab)
        elif m == "don":
            lay.addWidget(make_label("Survolez la liste pour lire l'effet de chaque don.", "muted", wrap=True))
        for cb in (mode, a1, a2, feat):
            cb.activated.connect(lambda _=0, s=slot["id"], w=(mode, a1, a2, feat), f=feats: self._set_asi(s, w, f))
        self.choice_widgets["asi:" + slot["id"]] = (mode, a1, a2, feat)
        self.choices_lay.addWidget(card)

    # ------------------------------------------------------------------ manifestations occultes (v43)
    def _inv_base(self) -> list[str]:
        return list(self.engine.ch.manifestations)

    def _inv_slots(self) -> int:
        if self.sim is None:
            return 0
        return max(0, self.sim.manifestation_slots()["total"] - len(self._inv_base()))

    def invocation_tip(self, name: str) -> str:
        m = self.sim.db.manifestations.get(name, {})
        pre = [x for x in (m.get("pacte"), "Occultiste niveau {}".format(m["niveau"]) if m.get("niveau") else "",
                           "sort mineur " + m["sort_requis"] if m.get("sort_requis") else "", m.get("special"))
               if x]
        src = {"PHB": "Manuel des joueurs", "XGtE": "Guide complet de Xanathar",
               "TCoE": "Chaudron des merveilles de Tasha"}.get(m.get("source", ""), m.get("source", ""))
        grants = "; ".join("{} ({})".format(g["sort"], g["usage"]) for g in m.get("sorts", []))
        return rich_tip(name, m.get("description", "") + ("\nSort accordé : " + grants if grants else "") +
                        "\nPrérequis : " + (", ".join(pre) or "aucun") + ("\nSource : " + src if src else ""))

    def _invocation_html(self, name: str, prefix: str) -> str:
        m = self.sim.db.manifestations.get(name, {})
        grants = "; ".join("{} ({})".format(g["sort"], g["usage"]) for g in m.get("sorts", []))
        return "<b>{} {}</b> — {}{}".format(prefix, html.escape(name), html.escape(m.get("description", "")),
                                           "<br/><i>Sort accordé : {}</i>".format(html.escape(grants)) if grants else "")

    def _invocation_card(self) -> None:
        n = self._inv_slots()
        if n <= 0:
            return
        base = self._inv_base()
        added = [x for x in self.sim.ch.manifestations if x not in base]
        card = QFrame()
        card.setObjectName("opaqueBox")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)
        total = self.sim.manifestation_slots()["total"]
        lay.addWidget(make_label("✧ Manifestations occultes — {} à choisir à ce niveau ({} / {} connues)".format(
            n, len(self.sim.ch.manifestations), total), "head"))
        lay.addWidget(make_label("Seules les manifestations dont les prérequis sont remplis (niveau d'occultiste, "
                                 "pacte, sort mineur) sont proposées. Survolez la liste pour lire l'effet complet.",
                                 "muted", wrap=True))
        options = [m["nom"] for m in self.engine.level_invocation_options(self.sim)]
        for i in range(n):
            current = added[i] if i < len(added) else ""
            names = sorted(set(options + ([current] if current else [])))
            combo = QComboBox()
            combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            combo.addItems([NO_CHOICE] + names)
            for k, nm in enumerate(names):
                combo.setItemData(k + 1, self.invocation_tip(nm), Qt.ItemDataRole.ToolTipRole)
            if current in names:
                combo.setCurrentIndex(names.index(current) + 1)
            hover = make_label("", "muted", wrap=True)
            hover.setTextFormat(Qt.TextFormat.RichText)
            hover.setVisible(False)
            chosen = make_label("", wrap=True)
            chosen.setTextFormat(Qt.TextFormat.RichText)
            chosen.setText(self._invocation_html(current, "✔ Choisie :") if current else
                           "<i>Aucune manifestation choisie pour cet emplacement.</i>")

            def on_highlight(k: int, nm=names, lab=hover) -> None:
                if 1 <= k <= len(nm):
                    lab.setText(self._invocation_html(nm[k - 1], "👁 Aperçu :"))
                    lab.setVisible(True)
                else:
                    lab.setVisible(False)
            combo.highlighted.connect(on_highlight)
            combo.activated.connect(lambda _=0, idx=i, c=combo: self._set_invocation(idx, c.currentText()))
            lay.addWidget(make_label("Manifestation {} :".format(i + 1)))
            lay.addWidget(combo)
            lay.addWidget(hover)
            lay.addWidget(chosen)
            self.choice_widgets["manifestation:{}".format(i)] = combo
        self.choices_lay.addWidget(card)

    def _set_invocation(self, index: int, name: str) -> None:
        base = self._inv_base()
        added = [x for x in self.sim.ch.manifestations if x not in base]
        while len(added) <= index:
            added.append("")
        added[index] = "" if name == NO_CHOICE else name
        seen = []
        for x in added:                                   # pas deux fois la même manifestation
            if x and x not in seen:
                seen.append(x)
        self.sim.ch.manifestations = base + seen
        self._changed()
        self._build_choices()

    def style_tip(self, cls: str, name: str) -> str:
        from core.fighting_styles import style_applied
        desc = self.sim.db.style_description(cls, name)
        applied = style_applied(name)
        return rich_tip(name, desc + ("\n<i>Sur la fiche : {}</i>".format(applied) if applied else ""))

    def _style_html(self, cls: str, name: str, prefix: str) -> str:
        from core.fighting_styles import style_applied
        applied = style_applied(name)
        return "<b>{} {}</b> — {}{}".format(prefix, html.escape(name), html.escape(self.sim.db.style_description(
            cls, name)), "<br/><i>Sur la fiche : {}</i>".format(html.escape(applied)) if applied else "")

    def _style_card(self, slot: dict) -> None:
        """Carte « Style de combat » : liste avec infobulle par style, aperçu au survol, texte complet du choix."""
        modele = slot["kind"] == "modele"
        card = QFrame()
        card.setObjectName("opaqueBox")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)
        lay.addWidget(make_label("⚔ {} — {}".format("Modèle d'armure" if modele else "Style de combat",
                                                    slot["classe"]), "head"))
        combo = QComboBox()
        combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        opts = self.sim.style_options(slot["id"])
        combo.addItems([NO_CHOICE] + opts)
        current = self.sim.ch.styles_combat.get(slot["id"])
        if current in opts:
            combo.setCurrentIndex(opts.index(current) + 1)
        for i, n in enumerate(opts):                         # infobulle au survol de chaque style de la liste
            combo.setItemData(i + 1, self.style_tip(slot["classe"], n), Qt.ItemDataRole.ToolTipRole)
        lay.addWidget(combo)
        hover = make_label("", "muted", wrap=True)
        hover.setTextFormat(Qt.TextFormat.RichText)
        chosen = make_label("", wrap=True)
        chosen.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(hover)
        lay.addWidget(chosen)
        if current in opts:
            chosen.setText(self._style_html(slot["classe"], current, "✔ Style choisi :"))
        else:
            chosen.setText("<i>Survolez ou parcourez la liste pour lire l'effet de chaque style.</i>")
        hover.setVisible(False)

        def on_highlight(i: int, c=slot["classe"]) -> None:      # aperçu en direct pendant la navigation
            if 1 <= i <= len(opts):
                hover.setText(self._style_html(c, opts[i - 1], "👁 Aperçu :"))
                hover.setVisible(True)
            else:
                hover.setVisible(False)
        combo.highlighted.connect(on_highlight)
        combo.activated.connect(lambda _=0, s=slot["id"], c=combo: self._set_style(s, c.currentText()))
        self.choice_widgets["style:" + slot["id"]] = combo
        self.style_labels[slot["id"]] = (hover, chosen)
        self.choices_lay.addWidget(card)

    # ------------------------------------------------------------------ étape 5 : nouveaux sorts (v40)
    def _spell_classes(self) -> list[str]:
        out = []
        for e in self.sim.ch.classes if self.sim else []:
            plan = self.engine.level_spell_plan(self.sim, e["nom"])
            if plan and (e["nom"] == self.cls or any(m.get("kind") == "sorts" and m["message"].startswith(e["nom"])
                                                    for m in self.pending())):
                out.append(e["nom"])
        return out

    def _build_spells(self) -> None:
        """Étape « Nouveaux sorts » (v41) : par classe, deux onglets — Tours de magie / Sorts de niveau 1+ — avec
        compteurs indépendants, filtres en temps réel (niveau, école, Rituel, Concentration, recherche) et jauge des
        sorts préparés (cases à cocher)."""
        lay = self.spells_lay
        clear_layout(lay)
        self.spell_widgets = {}
        self.swap_widgets = {}
        classes = self._spell_classes()
        lay.addWidget(make_label("Nouveaux sorts du niveau", "head"))
        if not classes:
            lay.addWidget(make_label("Cette classe ne lance pas de sorts à ce niveau.", "muted", wrap=True))
            lay.addStretch(1)
            return
        for cls in classes:
            plan = self.engine.level_spell_plan(self.sim, cls)
            box = QFrame()
            box.setObjectName("opaqueBox")
            bl = QVBoxLayout(box)
            bl.setContentsMargins(12, 10, 12, 10)
            bl.addWidget(make_label("<b>{}</b> — niveau de sort maximal : {}".format(cls, plan["niveau_max"]), "",
                                    wrap=True))
            tabs = QTabWidget()
            w = {"tabs": tabs, "filtre_niveau": None}
            # --- onglet 1 : tours de magie
            t0 = QWidget()
            l0 = QVBoxLayout(t0)
            w["cnt0"] = make_label("", "head")
            l0.addWidget(w["cnt0"])
            f0 = QHBoxLayout()
            w["search0"] = QLineEdit()
            w["search0"].setPlaceholderText("Rechercher un tour de magie…")
            w["school0"] = QComboBox()
            w["school0"].addItems([ALL_SCHOOLS] + SCHOOLS)
            f0.addWidget(w["search0"], 2)
            f0.addWidget(w["school0"], 1)
            l0.addLayout(f0)
            r0 = QHBoxLayout()
            w["avail0"], w["mine0"] = QListWidget(), QListWidget()
            r0.addLayout(self._list_col("Disponibles (double-clic : apprendre)", w["avail0"]), 3)
            r0.addLayout(self._list_col("Vos tours de magie (double-clic : retirer ceux de ce niveau)", w["mine0"]), 2)
            l0.addLayout(r0)
            tabs.addTab(t0, "Tours de magie")
            # --- onglet 2 : sorts de niveau 1+
            t1 = QWidget()
            l1 = QVBoxLayout(t1)
            w["cnt1"] = make_label("", "head")
            l1.addWidget(w["cnt1"])
            lv = QHBoxLayout()
            lv.addWidget(make_label("Niveau :"))
            w["lvl_btns"] = {}
            for lvl in [None] + list(range(1, max(1, plan["niveau_max"]) + 1)):
                b = QPushButton("Tous" if lvl is None else "Niveau {}".format(lvl))
                b.setCheckable(True)
                b.setProperty("role", "toggle")
                b.setChecked(lvl is None)
                b.clicked.connect(lambda _=False, c=cls, n=lvl: self._on_spell_level(c, n))
                lv.addWidget(b)
                w["lvl_btns"][lvl] = b
            lv.addStretch(1)
            l1.addLayout(lv)
            f1 = QHBoxLayout()
            w["search1"] = QLineEdit()
            w["search1"].setPlaceholderText("Rechercher un sort…")
            w["school1"] = QComboBox()
            w["school1"].addItems([ALL_SCHOOLS] + SCHOOLS)
            w["ritual"] = QCheckBox("Rituel (R)")
            w["conc"] = QCheckBox("Concentration (C)")
            for wid, stretch in ((w["search1"], 2), (w["school1"], 1), (w["ritual"], 0), (w["conc"], 0)):
                f1.addWidget(wid, stretch)
            l1.addLayout(f1)
            prep = QHBoxLayout()
            w["prep_label"] = make_label("", "muted")
            w["prep_bar"] = QProgressBar()
            w["prep_bar"].setTextVisible(False)
            w["prep_bar"].setFixedHeight(10)
            prep.addWidget(w["prep_label"])
            prep.addWidget(w["prep_bar"], 1)
            l1.addLayout(prep)
            r1 = QHBoxLayout()
            w["avail1"], w["mine1"] = QListWidget(), QListWidget()
            r1.addLayout(self._list_col("Disponibles (double-clic : {})".format(
                "préparer" if self.engine.prepares_from_list(plan) else "apprendre"), w["avail1"]), 3)
            r1.addLayout(self._list_col("Vos sorts — cochez ceux qui sont préparés", w["mine1"]), 2)
            l1.addLayout(r1)
            tabs.addTab(t1, "Sorts de niveau 1+")
            bl.addWidget(tabs)
            # v49 : clic simple = fiche du sort ; bouton « Apprendre le sort » / « Préparer » = double-clic
            act = QHBoxLayout()
            verb = "Préparer" if self.engine.prepares_from_list(plan) else "Apprendre le sort"
            w["learn_btn"] = QPushButton("✚ " + verb)
            w["learn_btn"].clicked.connect(lambda _=False, c=cls: self._learn_selected(c))
            act.addWidget(w["learn_btn"])
            act.addStretch(1)
            bl.addLayout(act)
            w["inspector"] = make_inspector(170)
            bl.addWidget(w["inspector"])
            if self.engine.prepares_from_list(plan):
                bl.addWidget(make_label("{} prépare ses sorts chaque jour dans toute sa liste : la jauge suit la limite "
                                        "de la classe (niveau + modificateur). Vous pourrez la modifier après chaque "
                                        "repos long dans l'onglet Magie.".format(cls), "muted", wrap=True))
            # signaux (filtres en temps réel)
            for key in ("search0", "search1"):
                w[key].textChanged.connect(lambda _t="", c=cls: self._fill_spell_lists(c))
            for key in ("school0", "school1"):
                w[key].currentIndexChanged.connect(lambda _i=0, c=cls: self._fill_spell_lists(c))
            for key in ("ritual", "conc"):
                w[key].toggled.connect(lambda _b=False, c=cls: self._fill_spell_lists(c))
            for key in ("avail0", "avail1", "mine0", "mine1"):
                w[key].itemClicked.connect(lambda it, c=cls, k=key: self.inspect_spell(c, it.data(Qt.ItemDataRole.UserRole), k))
            for key in ("avail0", "avail1"):
                w[key].itemDoubleClicked.connect(lambda it, c=cls: self._learn(c, it.data(Qt.ItemDataRole.UserRole)))
            for key in ("mine0", "mine1"):
                w[key].itemDoubleClicked.connect(lambda it, c=cls: self._unlearn(c, it.data(Qt.ItemDataRole.UserRole)))
            w["mine1"].itemChanged.connect(lambda it, c=cls: self._on_prepare_item(c, it))
            self.spell_widgets[cls] = w
            lay.addWidget(box)
            self._fill_spell_lists(cls)
            if cls == self.cls and self.engine.level_swap_allowed(self.sim, cls):     # v44 : échange facultatif
                lay.addWidget(self._swap_card(cls))
        lay.addStretch(1)

    # ------------------------------------------------------------------ v44 : remplacer un sort connu
    def _swap_card(self, cls: str) -> QFrame:
        box = QFrame()
        box.setObjectName("opaqueBox")
        bl = QVBoxLayout(box)
        bl.setContentsMargins(12, 10, 12, 10)
        bl.addWidget(make_label("🔁 <b>Remplacer un sort connu</b> — {} (facultatif, 1 sort au maximum)".format(cls),
                                "head", wrap=True))
        bl.addWidget(make_label(self.engine.level_swap_rule(self.sim, cls), "muted", wrap=True))
        w = {"box": box}
        bl.addWidget(make_label("Étape 1 — Oublier : choisissez le sort connu à oublier", ""))
        w["forget"] = QComboBox()
        bl.addWidget(w["forget"])
        w["forget_text"] = make_label("", "muted", wrap=True)
        bl.addWidget(w["forget_text"])
        w["step2"] = make_label("", "")
        bl.addWidget(w["step2"])
        f = QHBoxLayout()
        w["search"] = QLineEdit()
        w["search"].setPlaceholderText("Rechercher un sort de remplacement…")
        w["school"] = QComboBox()
        w["school"].addItems([ALL_SCHOOLS] + SCHOOLS)
        f.addWidget(w["search"], 2)
        f.addWidget(w["school"], 1)
        bl.addLayout(f)
        w["options"] = QListWidget()
        w["options"].setMinimumHeight(170)
        bl.addWidget(w["options"])
        row = QHBoxLayout()
        w["summary"] = make_label("", "head", wrap=True)
        w["cancel"] = QPushButton("✖ Annuler l'échange")
        w["cancel"].setProperty("role", "ghost")
        row.addWidget(w["summary"], 1)
        row.addWidget(w["cancel"])
        bl.addLayout(row)
        w["forget"].currentIndexChanged.connect(lambda i, c=cls: self._on_swap_forget(c, i))
        w["search"].textChanged.connect(lambda _t="", c=cls: self._fill_swap(c))
        w["school"].currentIndexChanged.connect(lambda _i=0, c=cls: self._fill_swap(c))
        w["options"].itemDoubleClicked.connect(lambda it, c=cls: self.swap_choose(c, it.data(Qt.ItemDataRole.UserRole)))
        w["cancel"].clicked.connect(lambda _=False, c=cls: self.swap_cancel(c))
        self.swap_widgets[cls] = w
        self._fill_swap(cls)
        return box

    def _fill_swap(self, cls: str) -> None:
        w = self.swap_widgets.get(cls)
        if not w:
            return
        eng = self.engine
        st = eng.level_swap_state(self.sim, cls)
        cands = eng.level_swap_candidates(self.sim, cls)
        names = [sp["nom"] for sp in cands]
        if st["oublie"] and st["oublie"] not in names:
            names.insert(0, st["oublie"])
            cands.insert(0, self.sim.db.find_spell(st["oublie"]) or {"nom": st["oublie"], "niveau": 1})
        w["names"] = names
        with blocked(w["forget"]):
            w["forget"].clear()
            w["forget"].addItem("— garder tous mes sorts —")
            for i, sp in enumerate(cands):
                w["forget"].addItem(self._spell_label(sp))
                w["forget"].setItemData(i + 1, sp["nom"], Qt.ItemDataRole.UserRole)
                w["forget"].setItemData(i + 1, rich_tip(sp["nom"], sp.get("description", "")),
                                        Qt.ItemDataRole.ToolTipRole)
            w["forget"].setCurrentIndex(names.index(st["oublie"]) + 1 if st["oublie"] else 0)
            w["forget"].setEnabled(not st["nouveau"])
        old = self.sim.db.find_spell(st["oublie"]) or {} if st["oublie"] else {}
        w["forget_text"].setText("Oublié : <b>{}</b>{}".format(html.escape(st["oublie"]),
                                                               " — il occupait un emplacement libre : le remplaçant "
                                                               "peut être de n'importe quelle école." if st["libre"]
                                                               else "") if old else "")
        opts = eng.level_swap_options(self.sim, cls)
        school = "" if w["school"].currentText() == ALL_SCHOOLS else w["school"].currentText()
        opts = filter_spells(opts, None, school, texte=w["search"].text())
        ready = bool(st["oublie"]) and not st["nouveau"]
        w["step2"].setText("Étape 2 — Remplacer : {}".format(
            "double-cliquez sur le nouveau sort ({} possible(s))".format(len(opts)) if ready else
            "choix effectué" if st["nouveau"] else "choisissez d'abord un sort à oublier (étape 1)"))
        for key in ("search", "school", "options"):
            w[key].setEnabled(ready)
        with blocked(w["options"]):
            w["options"].clear()
            for sp in opts if ready else []:
                it = QListWidgetItem(self._spell_label(sp))
                it.setData(Qt.ItemDataRole.UserRole, sp["nom"])
                it.setToolTip(rich_tip(sp["nom"], sp.get("description", "")))
                w["options"].addItem(it)
        w["summary"].setText("✔ Échange : {} → {}".format(st["oublie"], st["nouveau"]) if st["nouveau"] else
                             "⚠ Choisissez le remplaçant de {}.".format(st["oublie"]) if st["oublie"] else
                             "Aucun échange (facultatif).")
        w["cancel"].setEnabled(bool(st["oublie"]))

    def _on_swap_forget(self, cls: str, index: int) -> None:
        names = self.swap_widgets[cls].get("names", [])
        self.swap_forget(cls, names[index - 1] if 0 < index <= len(names) else "")

    def swap_forget(self, cls: str, name: str) -> bool:
        if not name:
            ok = self.engine.level_swap_cancel(self.sim, cls)
        else:
            ok = self.engine.level_swap_forget(self.sim, cls, name)
        self._after_swap(cls)
        return ok

    def swap_choose(self, cls: str, name: str) -> bool:
        ok = bool(name) and self.engine.level_swap_choose(self.sim, cls, name)
        self._after_swap(cls)
        return ok

    def swap_cancel(self, cls: str) -> bool:
        ok = self.engine.level_swap_cancel(self.sim, cls)
        self._after_swap(cls)
        return ok

    def _after_swap(self, cls: str) -> None:
        self._rebuild_report()
        self._fill_swap(cls)
        if cls in self.spell_widgets:
            self._fill_spell_lists(cls)
        self._refresh_recap()
        self._refresh_steps()

    @staticmethod
    def _list_col(title: str, lst: QListWidget) -> QVBoxLayout:
        col = QVBoxLayout()
        col.addWidget(make_label(title, "muted", wrap=True))
        lst.setMinimumHeight(190)
        col.addWidget(lst)
        return col

    def _on_spell_level(self, cls: str, lvl) -> None:
        w = self.spell_widgets[cls]
        w["filtre_niveau"] = lvl
        for key, b in w["lvl_btns"].items():
            with blocked(b):
                b.setChecked(key == lvl)
        self._fill_spell_lists(cls)

    @staticmethod
    def _spell_label(sp: dict) -> str:
        tags = "".join(x for x, on in ((" Ⓒ", sp.get("concentration")), (" ᴿ", sp.get("rituel"))) if on)
        return "{} — {} ({}){}".format(sp["nom"], "tour de magie" if sp["niveau"] == 0 else
                                       "niveau {}".format(sp["niveau"]), sp.get("ecole", ""), tags)

    def _fill_spell_lists(self, cls: str) -> None:
        w = self.spell_widgets[cls]
        eng = self.engine
        plan = eng.level_spell_plan(self.sim, cls)
        prep = eng.level_prepare_info(self.sim, cls)
        added = self.spell_added.get(cls, [])
        school0 = "" if w["school0"].currentText() == ALL_SCHOOLS else w["school0"].currentText()
        school1 = "" if w["school1"].currentText() == ALL_SCHOOLS else w["school1"].currentText()
        options = eng.level_spell_options(self.sim, cls)
        cantrips = filter_spells([sp for sp in options if sp["niveau"] == 0], 0, school0, texte=w["search0"].text())
        leveled = filter_spells([sp for sp in options if sp["niveau"] > 0], w["filtre_niveau"], school1,
                                w["ritual"].isChecked(), w["conc"].isChecked(), w["search1"].text())
        mine = [self.sim.db.find_spell(x["nom"]) or {"nom": x["nom"], "niveau": 1} for x in
                self.sim.ch.sorts.get(cls, [])]
        flags = {x["nom"]: bool(x.get("prepare")) for x in self.sim.ch.sorts.get(cls, [])}
        mine0 = [sp for sp in mine if sp.get("niveau") == 0]
        mine1 = filter_spells([sp for sp in mine if sp.get("niveau", 1) > 0], w["filtre_niveau"], school1,
                              w["ritual"].isChecked(), w["conc"].isChecked(), w["search1"].text())
        # compteurs indépendants
        have0, max0 = plan["mineurs"]
        w["cnt0"].setText("Tours de magie : {} / {}{}".format(have0, max0, "  (+{} à ce niveau)".format(
            plan["gain_mineurs"]) if plan["gain_mineurs"] else ""))
        quota = plan["connus"] or plan["grimoire"] or plan["prepares"]
        label = "Sorts connus" if plan["connus"] else "Grimoire" if plan["grimoire"] else "Sorts préparés"
        w["cnt1"].setText("{} : {} / {}{}".format(label, quota[0], quota[1], "  (+{} à ce niveau)".format(
            plan["gain_sorts"]) if plan["gain_sorts"] else "") if quota else "Aucun sort de niveau 1+")
        w["tabs"].setTabText(0, "Tours de magie ({} / {})".format(have0, max0))
        w["tabs"].setTabText(1, "Sorts de niveau 1+ ({} / {})".format(quota[0], quota[1]) if quota else
                             "Sorts de niveau 1+")
        if prep["toujours"]:
            w["prep_label"].setText("Préparés : tous vos sorts connus ({} / {}) — classe à sorts connus".format(
                prep["prepares"], prep["maximum"]))
        else:
            w["prep_label"].setText("Préparés : {} / {} (limite de la classe)".format(prep["prepares"], prep["maximum"]))
        w["prep_bar"].setRange(0, max(1, prep["maximum"]))
        w["prep_bar"].setValue(min(prep["prepares"], max(1, prep["maximum"])))
        with blocked(w["avail0"], w["avail1"], w["mine0"], w["mine1"]):
            for key, rows in (("avail0", cantrips), ("avail1", leveled)):
                w[key].clear()
                for sp in rows:
                    it = QListWidgetItem(self._spell_label(sp))
                    it.setData(Qt.ItemDataRole.UserRole, sp["nom"])
                    it.setToolTip(rich_tip(sp["nom"], sp.get("description", "")))
                    w[key].addItem(it)
            for key, rows in (("mine0", mine0), ("mine1", mine1)):
                w[key].clear()
                for sp in rows:
                    it = QListWidgetItem(("✦ " if sp["nom"] in added else "") + self._spell_label(sp))
                    it.setData(Qt.ItemDataRole.UserRole, sp["nom"])
                    it.setToolTip(rich_tip(sp["nom"], sp.get("description", "") + (
                        "\nAppris à ce niveau : double-clic pour le retirer." if sp["nom"] in added else "")))
                    if key == "mine1" and prep["toujours"]:        # sorts connus : toujours utilisables
                        it.setText("✔ " + it.text())
                    elif key == "mine1":                             # case « Préparé »
                        it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        it.setCheckState(Qt.CheckState.Checked if flags.get(sp["nom"]) else Qt.CheckState.Unchecked)
                    w[key].addItem(it)

    def _on_prepare_item(self, cls: str, item) -> None:
        name = item.data(Qt.ItemDataRole.UserRole)
        on = item.checkState() == Qt.CheckState.Checked
        if not self.engine.level_set_prepared(self.sim, cls, name, on) and on:
            self.win.statusBar().showMessage("Limite de sorts préparés atteinte pour {}.".format(cls), 6000)
        self._rebuild_report()
        self._fill_spell_lists(cls)
        self._refresh_recap()
        self._refresh_steps()

    def inspect_spell(self, cls: str, name: str, source: str = "") -> str:
        """Clic simple : fiche détaillée (école, incantation, portée, composantes, durée, texte complet)."""
        w = self.spell_widgets.get(cls)
        if w is None:
            return ""
        w["selection"] = (name, source)
        text = spell_card_html(self.sim.db.find_spell(name) if name else None)
        w["inspector"].setHtml(text)
        return text

    def _learn_selected(self, cls: str) -> None:
        w = self.spell_widgets.get(cls) or {}
        name, source = w.get("selection", ("", ""))
        if name and source.startswith("avail"):
            self._learn(cls, name)

    def _learn(self, cls: str, name: str) -> None:
        if name and self.engine.level_learn_spell(self.sim, cls, name):
            self.spell_added.setdefault(cls, []).append(name)
            self._rebuild_report()
            self._fill_spell_lists(cls)
            self._refresh_recap()
            self._refresh_steps()

    def _unlearn(self, cls: str, name: str) -> None:
        if name in self.spell_added.get(cls, []):
            self.spell_added[cls].remove(name)
            self.sim.ch.sorts[cls] = [s for s in self.sim.ch.sorts.get(cls, []) if s["nom"] != name]
            self.sim.normalize()
            self._rebuild_report()
            self._fill_spell_lists(cls)
            self._refresh_recap()
            self._refresh_steps()

    def _set_style(self, sid: str, name: str) -> None:
        if name == NO_CHOICE:
            self.sim.ch.styles_combat.pop(sid, None)
        else:
            self.sim.ch.styles_combat[sid] = name
        self._changed()
        self._build_choices()                            # résumé du style choisi sous le sélecteur

    def _set_pact(self, name: str) -> None:
        self.sim.ch.pacte = "" if name == NO_CHOICE else name
        self._changed()

    # ------------------------------------------------------------------ étape 5
    def _refresh_recap(self) -> None:
        t = theme.current()
        rows = "".join("<tr><td>{}</td><td align='center'>{}</td><td align='center'>→</td>"
                       "<td align='center'><b>{}</b></td></tr>".format(html.escape(a), html.escape(b), html.escape(c))
                       for a, b, c in self.report.get("recap", []))
        later = self.report.get("ensuite", [])
        note = ("<p style='color:{}'>○ Ensuite : {}</p>".format(t.ornament, html.escape("; ".join(
            m["message"] for m in later))) if later else "")
        self.recap_view.setHtml("<h3 style='color:{}'>Avant / après</h3><table cellpadding='4' width='100%'>"
                                "<tr><th align='left'>Valeur</th><th>Avant</th><th></th><th>Après</th></tr>{}</table>{}"
                                .format(t.accent_text, rows, note))

    # ------------------------------------------------------------------ confirmation
    def _on_confirm(self) -> None:
        if self.sim is None or self.pending():
            return
        for e in self.sim.ch.classes:
            e.pop("_wizard_sub", None)
        self.sim.__dict__.pop("_level_swaps", None)      # v44 : échange appliqué, état de l'assistant effacé
        self.sim.normalize()
        self.accept()


def run_level_up(win) -> bool:
    """Ouvre l'assistant ; à la confirmation, la copie de travail devient la fiche du personnage."""
    if not win.engine.level_up_options():
        win.statusBar().showMessage("Niveau 20 atteint : plus de montée de niveau possible.", 6000)
        return False
    backdrop = BlurBackdrop(win)
    dialog = LevelUpDialog(win)
    try:
        ok = dialog.exec() == 1
    finally:
        backdrop.dispose()
    if not ok or dialog.sim is None:
        return False
    apply_level_up(win, dialog.sim, dialog.cls)
    return True


def apply_level_up(win, sim, cls: str) -> None:
    for e in sim.ch.classes:
        e.pop("_wizard_sub", None)
    win.engine = sim
    win.changed()
    note = win.missing_note() if hasattr(win, "missing_note") else ""
    win.statusBar().showMessage("{} : niveau {} atteint (niveau global {}).{}".format(
        cls, sim.ch.find_class(cls)["niveau"], sim.total_level, " " + note + "." if note else ""), 10000)
