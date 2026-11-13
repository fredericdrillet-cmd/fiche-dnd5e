"""
Assistant de création de personnage niveau 1 (v48, inspiré de Baldur's Gate 3).

Sept étapes, à gauche les pastilles ○ / ✔, à droite le RÉSUMÉ DYNAMIQUE du personnage (mis à jour à chaque choix) :
    1. Race / Sous-race  — illustration, traits et pouvoirs ;
    2. Classe            — dé de vie, maîtrises, sous-classe de niveau 1, style de combat, compétences et expertises ;
    3. Historique        — compétences, langues au choix ;
    4. Caractéristiques  — achat de points, tableau standard / dés, bonus raciaux ;
    5. Sorts             — tours de magie et sorts de niveau 1 de la classe, magie raciale [Sort Racial]
                           (sort mineur au choix du Haut-elfe…) : visible même pour une classe non lanceuse ;
    6. Équipement        — équipement de l'historique offert + paquetage de classe standard OU boutique
                           (budget = or de la classe + or de l'historique) ;
    7. Identité          — nom du personnage, joueur, alignement.
Tout se fait sur une COPIE : « Annuler » ne change rien ; « ✔ Créer le personnage » remplace la fiche. Les choix
encore ouverts sont listés (jamais bloquants) et restent signalés par les pastilles ○ de la fiche.
Les écrans Race, Historique, Caractéristiques et Compétences réutilisent les panneaux de la fiche.
"""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (QComboBox, QDialog, QFileDialog, QFrame, QGraphicsDropShadowEffect, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPlainTextEdit, QPushButton,
                             QScrollArea, QSizeGrip, QStackedWidget, QTextBrowser, QVBoxLayout, QWidget)

from core import rules as R
from core.engine import Engine
from core.rules import ABILITIES
from . import theme
from .common import blocked, fill_combo, make_label, rich_tip
from .dialogs import BlurBackdrop
from .class_guide_panel import ClassGuidePanel
from .game_widgets import clear_layout
from .spell_inspector import make_inspector, spell_card_html

STEPS = ["Race / Sous-race", "Classe", "Historique", "Caractéristiques", "Sorts et tours de magie", "Équipement",
         "Identité"]
NO_CHOICE = "— à choisir —"
ALL_CATS = "Toutes catégories"


class WizardHost:
    """Fenêtre « factice » donnée aux panneaux réutilisés : leur moteur est la COPIE de l'assistant."""

    def __init__(self, dialog: "CreationWizard", win, engine):
        self.dialog, self.win, self.engine = dialog, win, engine
        self.db = win.db
        self.settings = win.settings
        self.lazy_refresh = False
        self.free_mode = True

    @property
    def ch(self):
        return self.engine.ch

    def changed(self) -> None:
        self.engine.normalize()
        self.dialog.refresh()

    def mark_dirty(self) -> None:
        self.dialog.refresh_summary()

    def light_changed(self, *_a, **_k) -> None:
        self.dialog.refresh_summary()

    def refresh_warnings(self) -> None:
        self.dialog.refresh_summary()

    def statusBar(self):  # noqa: N802 (nom Qt)
        return self.win.statusBar()

    def open_magic(self, *_a) -> None:
        pass

    def go_to_tab(self, *_a) -> None:
        pass

    def _start_dir(self) -> str:
        return self.win._start_dir() if hasattr(self.win, "_start_dir") else ""


class CreationWizard(QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.engine = Engine(win.db, Engine.new_character(win.db))
        from .rules_dialog import apply_table_defaults                 # v52 : édition et règles de la table
        apply_table_defaults(self.engine.ch, getattr(win, "settings", {}) or {})
        self.host = WizardHost(self, win, self.engine)
        self.step = 0
        self.equip_mode = "paquetage"
        self.class_gold = self.engine.starting_gold()["moyenne"]
        self.cart: dict[str, int] = {}
        self.spell_widgets: dict = {}
        self.inspector = None
        self.inspected = ""
        # v50 : vraie fenêtre (barre de titre, boutons Réduire / Agrandir / Fermer) : maximisable et redimensionnable
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowSystemMenuHint
                            | Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("Création de personnage — niveau 1")
        self.setModal(True)
        self.setMinimumSize(900, 600)
        self._fit_to_screen()

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
        lay.setContentsMargins(24, 20, 24, 18)
        lay.setSpacing(10)
        outer.addWidget(card)
        head = QHBoxLayout()
        head.addWidget(make_label("⚜  Création de personnage — niveau 1", "title"))
        head.addStretch(1)
        self.full_btn = QPushButton("⛶ Plein écran")
        self.full_btn.setProperty("role", "ghost")
        self.full_btn.setToolTip("Agrandir la fenêtre à tout l'écran (ou revenir à la taille normale).")
        self.full_btn.clicked.connect(self.toggle_maximized)
        head.addWidget(self.full_btn)
        lay.addLayout(head)

        body = QHBoxLayout()
        self.step_list = QListWidget()
        self.step_list.setFixedWidth(240)
        self.step_list.currentRowChanged.connect(self._on_step_clicked)
        body.addWidget(self.step_list)
        self.pages = QStackedWidget()
        body.addWidget(self.pages, 1)
        right = QVBoxLayout()
        right.addWidget(make_label("Résumé du personnage", "head"))
        self.summary = QTextBrowser()
        self.summary.setMinimumWidth(300)
        self.summary.setMaximumWidth(360)
        right.addWidget(self.summary, 1)
        body.addLayout(right)
        lay.addLayout(body, 1)

        self._build_pages()

        buttons = QHBoxLayout()
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setProperty("role", "ghost")
        self.cancel_btn.clicked.connect(self.reject)
        self.prev_btn = QPushButton("◀ Précédent")
        self.prev_btn.clicked.connect(lambda: self.go(self.step - 1))
        self.next_btn = QPushButton("Suivant ▶")
        self.next_btn.clicked.connect(lambda: self.go(self.step + 1))
        self.create_btn = QPushButton("✔ Créer le personnage")
        self.create_btn.clicked.connect(self._on_create)
        buttons.addWidget(self.cancel_btn)
        buttons.addStretch(1)
        for b in (self.prev_btn, self.next_btn, self.create_btn):
            b.setMinimumWidth(140)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            buttons.addWidget(b)
        buttons.addWidget(QSizeGrip(card), 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        lay.addLayout(buttons)
        self.go(0)

    @property
    def ch(self):
        return self.engine.ch

    def _fit_to_screen(self) -> None:
        """Taille de départ adaptée à l'écran (85 %), jamais plus grande que lui."""
        screen = self.screen() if hasattr(self, "screen") else None
        geo = screen.availableGeometry() if screen is not None else None
        try:
            sw, sh = int(geo.width()), int(geo.height())
        except (AttributeError, TypeError, ValueError):
            sw, sh = 1600, 1000
        self.resize(max(900, min(1400, int(sw * 0.85))), max(600, min(900, int(sh * 0.88))))

    def toggle_maximized(self) -> None:
        if self.isMaximized() is True:
            self.showNormal()
            self.full_btn.setText("⛶ Plein écran")
        else:
            self.showMaximized()
            self.full_btn.setText("🗗 Taille normale")

    # ------------------------------------------------------------------ construction
    def _scroll(self, widget: QWidget) -> QScrollArea:
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.Shape.NoFrame)
        area.setWidget(widget)
        return area

    def _page(self) -> tuple[QWidget, QVBoxLayout]:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(4, 4, 12, 4)
        return w, lay

    def _build_pages(self) -> None:
        from .abilities_tab import AbilitiesTab
        from .race_tab import RaceTab
        from .skills_tab import SkillsTab
        # 1. race
        self.race_panel = RaceTab(self.host)
        self.race_panel.bg_box.setVisible(False)
        self.race_panel.lang_box.setVisible(False)
        self.pages.addWidget(self._scroll(self.race_panel))      # v50 : défilement en fenêtre réduite
        # 2. classe
        w, lay = self._page()
        row = QHBoxLayout()
        row.addWidget(make_label("Classe", "head"))
        self.class_combo = QComboBox()
        self.class_combo.activated.connect(lambda _=0: self._on_class(self.class_combo.currentText()))
        row.addWidget(self.class_combo, 1)
        lay.addLayout(row)
        self.class_info = make_label("", "muted", wrap=True)
        lay.addWidget(self.class_info)
        self.guide = ClassGuidePanel()                    # v49 : fiche pédagogique de la classe et des sous-classes
        self.guide.subs.itemClicked.connect(lambda it: self.set_target_subclass(it.data(Qt.ItemDataRole.UserRole)))
        lay.addWidget(self.guide)
        self.choice_grid = QGridLayout()
        lay.addLayout(self.choice_grid)
        self.skills_panel = SkillsTab(self.host, compact=True)
        lay.addWidget(self.skills_panel)
        lay.addStretch(1)
        self.pages.addWidget(self._scroll(w))
        # 3. historique
        self.bg_panel = RaceTab(self.host)
        self.bg_panel.race_box.setVisible(False)
        self.bg_panel.add_inv.setVisible(False)          # l'équipement de l'historique est ajouté à l'étape 6
        self.pages.addWidget(self._scroll(self.bg_panel))
        # 4. caractéristiques
        self.abilities_panel = AbilitiesTab(self.host)
        self.pages.addWidget(self._scroll(self.abilities_panel))
        # 5. sorts
        w, self.spells_lay = self._page()
        self.pages.addWidget(self._scroll(w))
        # 6. équipement
        w, lay = self._page()
        modes = QHBoxLayout()
        self.kit_btn = QPushButton("🎒 Paquetage de classe standard")
        self.shop_btn = QPushButton("🪙 Boutique (acheter avec l'or de départ)")
        for b, mode in ((self.kit_btn, "paquetage"), (self.shop_btn, "boutique")):
            b.setCheckable(True)
            b.setProperty("role", "toggle")
            b.clicked.connect(lambda _=False, m=mode: self.set_equip_mode(m))
            modes.addWidget(b)
        modes.addStretch(1)
        lay.addLayout(modes)
        self.bg_items_label = make_label("", "", wrap=True)
        lay.addWidget(self.bg_items_label)
        self.kit_label = make_label("", "", wrap=True)
        lay.addWidget(self.kit_label)
        self.shop_box = QWidget()
        sl = QVBoxLayout(self.shop_box)
        sl.setContentsMargins(0, 0, 0, 0)
        gold = QHBoxLayout()
        self.gold_label = make_label("", "head")
        self.roll_gold_btn = QPushButton("🎲 Lancer l'or de départ")
        self.avg_gold_btn = QPushButton("Moyenne")
        self.avg_gold_btn.setProperty("role", "ghost")
        self.roll_gold_btn.clicked.connect(self.roll_gold)
        self.avg_gold_btn.clicked.connect(self.average_gold)
        gold.addWidget(self.gold_label, 1)
        gold.addWidget(self.roll_gold_btn)
        gold.addWidget(self.avg_gold_btn)
        sl.addLayout(gold)
        flt = QHBoxLayout()
        self.shop_cat = QComboBox()
        self.shop_cat.addItems([ALL_CATS, "Arme", "Armure", "Bouclier", "Équipement", "Paquetage", "Outil"])
        self.shop_search = QLineEdit()
        self.shop_search.setPlaceholderText("Rechercher un objet…")
        self.shop_cat.currentIndexChanged.connect(lambda _=0: self._fill_shop())
        self.shop_search.textChanged.connect(lambda _="": self._fill_shop())
        flt.addWidget(self.shop_cat)
        flt.addWidget(self.shop_search, 1)
        sl.addLayout(flt)
        lists = QHBoxLayout()
        col1, col2 = QVBoxLayout(), QVBoxLayout()
        col1.addWidget(make_label("Boutique (double-clic : acheter)", "muted"))
        self.shop_list = QListWidget()
        self.shop_list.setMinimumHeight(260)
        self.shop_list.itemDoubleClicked.connect(lambda it: self.buy(it.data(Qt.ItemDataRole.UserRole)))
        col1.addWidget(self.shop_list)
        col2.addWidget(make_label("Panier (double-clic : retirer 1)", "muted"))
        self.cart_list = QListWidget()
        self.cart_list.itemDoubleClicked.connect(lambda it: self.unbuy(it.data(Qt.ItemDataRole.UserRole)))
        col2.addWidget(self.cart_list)
        self.budget_label = make_label("", "head", wrap=True)
        col2.addWidget(self.budget_label)
        lists.addLayout(col1, 3)
        lists.addLayout(col2, 2)
        sl.addLayout(lists)
        lay.addWidget(self.shop_box)
        lay.addStretch(1)
        self.pages.addWidget(self._scroll(w))
        # 7. identité
        w, lay = self._page()
        grid = QGridLayout()
        self.name_edit, self.player_edit = QLineEdit(), QLineEdit()
        self.name_edit.setPlaceholderText("Nom du personnage")
        self.player_edit.setPlaceholderText("Nom du joueur")
        self.align_combo = QComboBox()
        self.align_combo.addItems(R.ALIGNMENTS)
        self.name_edit.textEdited.connect(lambda t: self._set_identity("nom", t))
        self.player_edit.textEdited.connect(lambda t: self._set_identity("joueur", t))
        self.align_combo.activated.connect(lambda _=0: self._set_identity("alignement",
                                                                          self.align_combo.currentText()))
        for r, (label, wid) in enumerate((("Nom du personnage", self.name_edit), ("Joueur", self.player_edit),
                                          ("Alignement (facultatif)", self.align_combo))):
            grid.addWidget(make_label(label, "head"), r, 0)
            grid.addWidget(wid, r, 1)
        grid.setColumnStretch(1, 1)
        lay.addLayout(grid)
        lay.addWidget(make_label("En Mode guidé, le nom est fixé à la création (Mode libre dans Options pour le "
                                 "changer ensuite).", "muted", wrap=True))
        # v49 : portrait et histoire (repris dans l'onglet « Histoire, Portrait », modifiables à tout moment)
        ident = QHBoxLayout()
        pcol = QVBoxLayout()
        self.portrait = QLabel("Aucun portrait")
        self.portrait.setProperty("role", "portrait")
        self.portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.portrait.setFixedSize(180, 240)
        self.portrait_btn = QPushButton("[ Importer un portrait ]")
        self.portrait_btn.clicked.connect(self._on_import_portrait)
        self.portrait_clear = QPushButton("Retirer")
        self.portrait_clear.setProperty("role", "ghost")
        self.portrait_clear.clicked.connect(lambda: self.set_portrait(""))
        pcol.addWidget(self.portrait, 0, Qt.AlignmentFlag.AlignHCenter)
        pcol.addWidget(self.portrait_btn)
        pcol.addWidget(self.portrait_clear)
        pcol.addStretch(1)
        ident.addLayout(pcol)
        bcol = QVBoxLayout()
        bcol.addWidget(make_label("Passé du personnage (backstory)", "head"))
        self.story = QPlainTextEdit()
        self.story.setPlaceholderText("Origines, famille, événements marquants, motivations, secrets…")
        self.story.setMinimumHeight(220)
        self.story.textChanged.connect(lambda: self._set_identity("histoire", self.story.toPlainText()))
        bcol.addWidget(self.story, 1)
        ident.addLayout(bcol, 1)
        lay.addLayout(ident)
        self.remaining = make_label("", "", wrap=True)
        lay.addWidget(self.remaining)
        lay.addStretch(1)
        self.pages.addWidget(self._scroll(w))

    # ------------------------------------------------------------------ navigation
    def go(self, step: int) -> None:
        self.step = max(0, min(len(STEPS) - 1, step))
        self.pages.setCurrentIndex(self.step)
        self.refresh()

    def _on_step_clicked(self, row: int) -> None:
        if 0 <= row < len(STEPS) and row != self.step:
            self.go(row)

    def step_done(self) -> list[bool]:
        miss = self.engine.missing_choices()

        def none(pred) -> bool:
            return not any(pred(m) for m in miss)
        class_ok = none(lambda m: (m["onglet"], m["encart"]) in (("caracteristiques", "Compétences"),
                                                                 ("combat", "Style de combat"),
                                                                 ("classes", "Sous-classe")))
        return [bool(self.ch.race), class_ok, none(lambda m: m["onglet"] == "race"),
                none(lambda m: m["onglet"] == "caracteristiques" and m["encart"] != "Compétences"),
                none(lambda m: m["onglet"] == "magie"),
                self.equip_mode == "paquetage" or self.engine.cart_total(self.cart) <= self.budget(),
                bool(self.ch.nom.strip())]

    def refresh(self) -> None:
        """Rafraîchit la page visible, les pastilles et le résumé."""
        refreshers = [self.race_panel.refresh, self._refresh_class, self.bg_panel.refresh,
                      self.abilities_panel.refresh, self._build_spells, self._refresh_equipment,
                      self._refresh_identity]
        refreshers[self.step]()
        done = self.step_done()
        with blocked(self.step_list):
            self.step_list.clear()
            for i, name in enumerate(STEPS):
                self.step_list.addItem("{} {}. {}".format("✔" if done[i] else "○", i + 1, name))
            self.step_list.setCurrentRow(self.step)
        self.prev_btn.setEnabled(self.step > 0)
        self.next_btn.setEnabled(self.step < len(STEPS) - 1)
        self.refresh_summary()

    # ------------------------------------------------------------------ résumé dynamique
    def summary_html(self) -> str:
        eng, ch, t = self.engine, self.ch, theme.current()
        cls = ch.classes[0] if ch.classes else {}
        rows = [("Nom", ch.nom or "—"), ("Joueur", ch.joueur or "—"),
                ("Race", ch.race + (" — {}".format(ch.sous_race) if ch.sous_race else "")),
                ("Classe", "{} {}{}".format(cls.get("nom", ""), cls.get("niveau", 1),
                                            " — {}".format(cls["sous_classe"]) if cls.get("sous_classe") else "")),
                ("Historique", ch.historique or "—")]
        out = ["<h3 style='color:{}'>{}</h3><table cellpadding='2'>".format(t.accent_text, html.escape(
            ch.nom or "Nouveau personnage"))]
        out += ["<tr><td><b>{}</b></td><td>{}</td></tr>".format(html.escape(a), html.escape(b)) for a, b in rows]
        out.append("</table><p><b>Caractéristiques</b><br/>" + " · ".join(
            "{} {} ({})".format(R.ABBR[ab], eng.score(ab), R.fmt_bonus(eng.mod(ab))) for ab in ABILITIES) + "</p>")
        out.append("<p>PV {} · CA {} · Vitesse {} · Initiative {}</p>".format(
            eng.hp_max(), eng.armor_class()[0], eng.speed_text(), R.fmt_bonus(eng.initiative())))
        skills = sorted(n for n, s in ch.competences.items() if s.get("maitrise"))
        out.append("<p><b>Compétences</b> : {}</p>".format(html.escape(", ".join(skills)) or "—"))
        spells = [s["nom"] for lst in ch.sorts.values() for s in lst]
        racial = [r["nom"] + " [Sort Racial]" for r in eng.racial_spells() if r["debloque"]]
        if spells or racial:
            out.append("<p><b>Sorts</b> : {}</p>".format(html.escape(", ".join(spells + racial))))
        if self.equip_mode == "boutique":
            out.append("<p><b>Équipement</b> : boutique — {:g} po dépensés sur {} po</p>".format(
                self.engine.cart_total(self.cart), self.budget()))
        else:
            out.append("<p><b>Équipement</b> : paquetage de {}</p>".format(html.escape(cls.get("nom", ""))))
        miss = eng.missing_choices()
        if miss:
            out.append("<p style='color:{}'><b>○ Choix restants</b><br/>{}</p>".format(
                t.ornament, "<br/>".join(html.escape(m["message"]) for m in miss)))
        return "".join(out)

    def refresh_summary(self) -> None:
        self.summary.setHtml(self.summary_html())

    # ------------------------------------------------------------------ étape 2 : classe
    def _on_class(self, name: str) -> None:
        if name and self.ch.classes and name != self.ch.classes[0]["nom"]:
            self.engine.change_class(0, name)
            self.class_gold = self.engine.starting_gold(name)["moyenne"]
            self.cart = {}
            self.engine.__dict__["_sous_classe_visee"] = ""
        self.host.changed()

    def _refresh_class(self) -> None:
        eng, db = self.engine, self.engine.db
        cls = self.ch.classes[0]["nom"]
        tips = {n: rich_tip(n, "Dé de vie {} — sauvegardes : {}".format(
            db.start_info(n)["de_vie"], ", ".join(db.start_info(n)["sauvegardes"]))) for n in db.class_names()}
        fill_combo(self.class_combo, db.class_names(), cls, tips)
        info = db.start_info(cls)
        self.class_info.setText("Dé de vie : {} — PV au niveau 1 : {} — Jets de sauvegarde : {}<br/>Armures : {} — "
                                "Armes : {}".format(info["de_vie"], eng.hp_max(), ", ".join(info["sauvegardes"]),
                                                    ", ".join(info["armures"]) or "aucune",
                                                    ", ".join(info["armes"]) or "aucune"))
        entry = self.ch.classes[0]
        self.guide.set_class(eng, cls, entry.get("sous_classe") or self.engine.__dict__.get("_sous_classe_visee", ""))
        clear_layout(self.choice_grid)
        row = 0
        if R.SUBCLASS_LEVEL.get(cls, 3) <= 1 and db.subclasses(cls):     # Clerc, Ensorceleur, Occultiste
            combo = QComboBox()
            subs = [s["nom"] for s in db.subclasses(cls)]
            fill_combo(combo, [NO_CHOICE] + subs, entry.get("sous_classe") or NO_CHOICE)
            combo.activated.connect(lambda _=0, c=combo: self.set_subclass(c.currentText()))
            self.choice_grid.addWidget(make_label("◆ Sous-classe (niveau 1)", "head"), row, 0)
            self.choice_grid.addWidget(combo, row, 1)
            row += 1
        for slot in eng.fighting_style_slots():
            if not slot["debloque"]:
                continue
            combo = QComboBox()
            opts = eng.style_options(slot["id"])
            fill_combo(combo, [NO_CHOICE] + opts, self.ch.styles_combat.get(slot["id"]) or NO_CHOICE)
            combo.activated.connect(lambda _=0, c=combo, sid=slot["id"]: self.set_style(sid, c.currentText()))
            self.choice_grid.addWidget(make_label("⚔ Style de combat", "head"), row, 0)
            self.choice_grid.addWidget(combo, row, 1)
            row += 1
        if R.SUBCLASS_LEVEL.get(cls, 3) > 1 and db.subclasses(cls):   # v49 : sous-classe VISÉE (aperçu)
            combo = QComboBox()
            subs = [s["nom"] for s in db.subclasses(cls)]
            target = self.engine.__dict__.get("_sous_classe_visee", "")
            fill_combo(combo, ["— aucune pour l'instant —"] + subs, target if target in subs else
                       "— aucune pour l'instant —")
            combo.activated.connect(lambda _=0, c=combo: self.set_target_subclass(c.currentText()))
            self.choice_grid.addWidget(make_label("◇ Sous-classe visée (niveau {}) — adapte les recommandations de "
                                                  "caractéristiques".format(R.SUBCLASS_LEVEL.get(cls, 3)), "muted"),
                                       row, 0)
            self.choice_grid.addWidget(combo, row, 1)
            row += 1
        self.choice_grid.setColumnStretch(1, 1)
        self.skills_panel.refresh()

    def set_target_subclass(self, name: str) -> None:
        """Sous-classe visée (choisie plus tard, au niveau requis) : sert aux recommandations ⭐ / ✦."""
        cls = self.ch.classes[0]["nom"]
        subs = [s["nom"] for s in self.engine.db.subclasses(cls)]
        if name and name == self.engine.__dict__.get("_sous_classe_visee") and not self.guide.sub:
            name = ""                                     # second clic : fiche repliée, sous-classe visée effacée
        if R.SUBCLASS_LEVEL.get(cls, 3) <= 1 and name in subs:
            self.ch.classes[0]["sous_classe"] = name       # niveau 1 : c'est le vrai choix
        self.engine.__dict__["_sous_classe_visee"] = name if name in subs else ""
        self.host.changed()

    def set_subclass(self, name: str) -> None:
        self.ch.classes[0]["sous_classe"] = "" if name == NO_CHOICE else name
        self.host.changed()

    def set_style(self, sid: str, name: str) -> None:
        if name == NO_CHOICE:
            self.ch.styles_combat.pop(sid, None)
        else:
            self.ch.styles_combat[sid] = name
        self.host.changed()

    # ------------------------------------------------------------------ étape 5 : sorts
    def _build_spells(self) -> None:
        eng = self.engine
        lay = self.spells_lay
        clear_layout(lay)
        self.spell_widgets = {}
        cls = self.ch.classes[0]["nom"]
        plan = eng.level_spell_plan(eng, cls)
        if plan:
            lay.addWidget(make_label("Sorts de {} au niveau 1".format(cls), "head"))
            for kind, label in (("mineurs", "Tours de magie"), ("sorts", "Sorts de niveau 1")):
                quota = plan["mineurs"] if kind == "mineurs" else (plan["connus"] or plan["grimoire"] or
                                                                   plan["prepares"])
                if not quota or not quota[1]:
                    continue
                lay.addWidget(make_label("{} : {} / {}".format(label, quota[0], quota[1]), "head"))
                row = QHBoxLayout()
                avail, mine = QListWidget(), QListWidget()
                for lst in (avail, mine):
                    lst.setMinimumHeight(170)
                opts = [sp for sp in eng.level_spell_options(eng, cls) if (sp["niveau"] == 0) == (kind == "mineurs")]
                owned = [eng.db.find_spell(s["nom"]) or {"nom": s["nom"], "niveau": 1}
                         for s in self.ch.sorts.get(cls, [])]
                owned = [sp for sp in owned if (sp.get("niveau", 1) == 0) == (kind == "mineurs")]
                for lst, rows in ((avail, opts), (mine, owned)):
                    for sp in rows:
                        it = QListWidgetItem("{} ({})".format(sp["nom"], sp.get("ecole", "")))
                        it.setData(Qt.ItemDataRole.UserRole, sp["nom"])
                        it.setToolTip(rich_tip(sp["nom"], sp.get("description", "")))
                        lst.addItem(it)
                avail.itemDoubleClicked.connect(lambda it, c=cls: self.learn(c, it.data(Qt.ItemDataRole.UserRole)))
                mine.itemDoubleClicked.connect(lambda it, c=cls: self.unlearn(c, it.data(Qt.ItemDataRole.UserRole)))
                for lst in (avail, mine):                 # v49 : clic simple = fiche détaillée
                    lst.itemClicked.connect(lambda it: self.inspect(it.data(Qt.ItemDataRole.UserRole)))
                verb = "Préparer" if eng.prepares_from_list(plan) and kind == "sorts" else "Apprendre le sort"
                learn_btn = QPushButton("✚ " + verb)
                learn_btn.clicked.connect(lambda _=False, a=avail, c=cls: self._learn_current(c, a))
                drop_btn = QPushButton("✖ Retirer")
                drop_btn.setProperty("role", "ghost")
                drop_btn.clicked.connect(lambda _=False, m=mine, c=cls: self._drop_current(c, m))
                c1, c2 = QVBoxLayout(), QVBoxLayout()
                c1.addWidget(make_label("Disponibles (clic : fiche ; double-clic ou bouton : {})".format(
                    verb.lower()), "muted"))
                c1.addWidget(avail)
                c1.addWidget(learn_btn)
                c2.addWidget(make_label("Choisis (double-clic ou bouton : retirer)", "muted"))
                c2.addWidget(mine)
                c2.addWidget(drop_btn)
                row.addLayout(c1, 3)
                row.addLayout(c2, 2)
                lay.addLayout(row)
                self.spell_widgets[kind] = (avail, mine)
            lay.addWidget(make_label("Fiche du sort", "head"))
            self.inspector = make_inspector()
            self.inspector.setHtml(spell_card_html(eng.db.find_spell(self.inspected) if self.inspected else None))
            lay.addWidget(self.inspector)
        else:
            lay.addWidget(make_label("{} ne lance pas de sorts au niveau 1.".format(cls), "muted", wrap=True))
        # magie raciale (toutes classes)
        slots = eng.racial_choice_slots()
        racial = eng.racial_spells()
        if slots or racial:
            lay.addWidget(make_label("✦ Magie raciale — [Sort Racial] (disponible quelle que soit la classe)", "head"))
        for s in slots:
            combo = QComboBox()
            opts = eng.racial_choice_options(s["cle"])
            fill_combo(combo, [NO_CHOICE] + [o["nom"] for o in opts], s["choix"] or NO_CHOICE,
                       {o["nom"]: rich_tip(o["nom"], o.get("description", "")) for o in opts})
            combo.activated.connect(lambda _=0, c=combo, k=s["cle"]: self.set_racial(k, c.currentText()))
            r = QHBoxLayout()
            r.addWidget(make_label("{} — sort mineur de la liste du {} :".format(s["source"], s["liste"].lower())))
            r.addWidget(combo, 1)
            lay.addLayout(r)
        for r in racial:
            lay.addWidget(make_label("{} {} [Sort Racial] — {}{} ({})".format(
                "✦" if r["debloque"] else "🔒", r["nom"], r["usage"], "" if r["debloque"] else
                " — à partir du niveau {}".format(r["niveau_requis"]), r["source"]), "", wrap=True))
        if not plan and not slots and not racial:
            lay.addWidget(make_label("Aucun sort à choisir : passez à l'étape suivante.", "muted"))
        lay.addStretch(1)

    def inspect(self, name: str) -> str:
        """Clic simple : fiche détaillée du sort (école, incantation, portée, composantes, durée, texte)."""
        self.inspected = name or ""
        text = spell_card_html(self.engine.db.find_spell(name) if name else None)
        if self.inspector is not None:
            self.inspector.setHtml(text)
        return text

    def _learn_current(self, cls: str, lst) -> bool:
        it = lst.currentItem()
        name = it.data(Qt.ItemDataRole.UserRole) if it is not None else self.inspected
        return bool(name) and self.learn(cls, name)

    def _drop_current(self, cls: str, lst) -> None:
        it = lst.currentItem()
        if it is not None:
            self.unlearn(cls, it.data(Qt.ItemDataRole.UserRole))

    def learn(self, cls: str, name: str) -> bool:
        ok = self.engine.level_learn_spell(self.engine, cls, name)
        self.host.changed()
        return ok

    def unlearn(self, cls: str, name: str) -> None:
        self.ch.sorts[cls] = [s for s in self.ch.sorts.get(cls, []) if s["nom"] != name or s.get("accorde")]
        self.host.changed()

    def set_racial(self, key: str, name: str) -> None:
        self.engine.set_racial_choice(key, "" if name == NO_CHOICE else name)
        self.host.changed()

    # ------------------------------------------------------------------ étape 6 : équipement
    def budget(self) -> int:
        return int(self.class_gold) + self.engine.background_gold()

    def set_equip_mode(self, mode: str) -> None:
        self.equip_mode = mode
        self.refresh()

    def roll_gold(self, rng=None) -> int:
        self.class_gold = self.engine.roll_starting_gold(rng=rng)
        self._trim_cart()
        self.refresh()
        return self.class_gold

    def average_gold(self) -> None:
        self.class_gold = self.engine.starting_gold()["moyenne"]
        self._trim_cart()
        self.refresh()

    def _trim_cart(self) -> None:
        """Budget réduit (nouveau jet) : on retire des achats jusqu'à rentrer dans le budget."""
        while self.cart and self.engine.cart_total(self.cart) > self.budget():
            last = list(self.cart)[-1]
            self.unbuy(last, refresh=False)

    def buy(self, name: str) -> bool:
        price = next((i["prix"] for i in self.engine.shop_items() if i["nom"] == name), None)
        if price is None:
            return False
        if self.engine.cart_total(self.cart) + price > self.budget() + 1e-6:
            self.win.statusBar().showMessage("Budget insuffisant pour {} ({:g} po).".format(name, price), 6000)
            return False
        self.cart[name] = self.cart.get(name, 0) + 1
        self.refresh()
        return True

    def unbuy(self, name: str, refresh: bool = True) -> None:
        if name in self.cart:
            self.cart[name] -= 1
            if self.cart[name] <= 0:
                del self.cart[name]
        if refresh:
            self.refresh()

    def _fill_shop(self) -> None:
        cat = self.shop_cat.currentText()
        items = self.engine.shop_items("" if cat == ALL_CATS else cat, self.shop_search.text())
        left = self.budget() - self.engine.cart_total(self.cart)
        with blocked(self.shop_list):
            self.shop_list.clear()
            for i in items:
                it = QListWidgetItem("{} — {} ({})".format(i["nom"], i["prix_txt"], i["categorie"]))
                it.setData(Qt.ItemDataRole.UserRole, i["nom"])
                it.setToolTip(rich_tip(i["nom"], "{} — {}".format(i["description"], i["poids_txt"])))
                if i["prix"] > left + 1e-6:
                    it.setForeground(QBrush(QColor(theme.current().locked)))
                self.shop_list.addItem(it)

    def _refresh_equipment(self) -> None:
        eng = self.engine
        with blocked(self.kit_btn, self.shop_btn):
            self.kit_btn.setChecked(self.equip_mode == "paquetage")
            self.shop_btn.setChecked(self.equip_mode == "boutique")
        bg_items = eng.background_items()
        self.bg_items_label.setText("<b>Équipement de l'historique ({}) — offert :</b> {} ; or : {} po".format(
            html.escape(self.ch.historique), html.escape(", ".join("{} ×{}".format(n, q) if q > 1 else n
                                                                     for q, n in bg_items)) or "—",
            eng.background_gold()))
        kit = eng.class_kit()
        self.kit_label.setVisible(self.equip_mode == "paquetage")
        self.kit_label.setText("<b>Paquetage de {} :</b> {}<br/><i>Armure, bouclier et armes sont équipés "
                               "automatiquement.</i>".format(html.escape(self.ch.classes[0]["nom"]), html.escape(
                                   ", ".join("{} ×{}".format(n, q) if q > 1 else n for q, n in kit)) or "—"))
        self.shop_box.setVisible(self.equip_mode == "boutique")
        g = eng.starting_gold()
        self.gold_label.setText("Or de départ — {} : {} po (moyenne {} po) + historique {} po = budget {} po".format(
            g["formule"], self.class_gold, g["moyenne"], eng.background_gold(), self.budget()))
        self._fill_shop()
        with blocked(self.cart_list):
            self.cart_list.clear()
            prices = {i["nom"]: i["prix"] for i in eng.shop_items()}
            for n, q in self.cart.items():
                it = QListWidgetItem("{} ×{} — {:g} po".format(n, q, prices.get(n, 0) * q))
                it.setData(Qt.ItemDataRole.UserRole, n)
                self.cart_list.addItem(it)
        spent = eng.cart_total(self.cart)
        self.budget_label.setText("Dépensé : {:g} po — reste {:g} po (versé dans la bourse)".format(
            spent, self.budget() - spent))

    # ------------------------------------------------------------------ étape 7 : identité
    def _set_identity(self, attr: str, value: str) -> None:
        setattr(self.ch, attr, value)
        self.refresh_summary()

    def _on_import_portrait(self) -> bool:
        from .rp_tab import IMAGE_FILTER
        path, _ = QFileDialog.getOpenFileName(self, "Importer un portrait", self.host._start_dir(), IMAGE_FILTER)
        return self.import_portrait(path) if isinstance(path, str) and path else False

    def import_portrait(self, path: str) -> bool:
        """Image réduite et encodée comme dans l'onglet Histoire, Portrait (même cadre 3:4)."""
        from .rp_tab import image_to_b64
        try:
            data = image_to_b64(path)
        except (OSError, ValueError) as exc:
            self.win.statusBar().showMessage("Portrait illisible : {}".format(exc), 8000)
            return False
        if not data:
            return False
        self.set_portrait(data)
        return True

    def set_portrait(self, data: str) -> None:
        self.ch.portrait = data or ""
        self._show_portrait()
        self.refresh_summary()

    def _show_portrait(self) -> None:
        from PyQt6.QtGui import QPixmap
        from .rp_tab import b64_to_pixmap
        pix = b64_to_pixmap(self.ch.portrait) if self.ch.portrait else None
        if pix is None or pix.isNull() is True:
            self.portrait.setPixmap(QPixmap())
            self.portrait.setText("Aucun portrait")
        else:
            self.portrait.setText("")
            self.portrait.setPixmap(pix.scaled(172, 232, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation))
        self.portrait_clear.setEnabled(bool(self.ch.portrait))

    def _refresh_identity(self) -> None:
        with blocked(self.story):
            if self.story.toPlainText() != self.ch.histoire:
                self.story.setPlainText(self.ch.histoire)
        self._show_portrait()
        with blocked(self.name_edit, self.player_edit, self.align_combo):
            if self.name_edit.text() != self.ch.nom:
                self.name_edit.setText(self.ch.nom)
            if self.player_edit.text() != self.ch.joueur:
                self.player_edit.setText(self.ch.joueur)
            fill_combo(self.align_combo, R.ALIGNMENTS, self.ch.alignement)
        miss = self.engine.missing_choices()
        t = theme.current()
        self.remaining.setText("<p style='color:{}'><b>○ Choix encore ouverts</b> (vous pourrez les faire sur la fiche, "
                               "pastilles ○) :<br/>{}</p>".format(t.ornament, "<br/>".join(
                                   html.escape(m["message"]) for m in miss)) if miss else
                               "<p style='color:{}'>✔ Tous les choix du niveau 1 sont faits.</p>".format(t.good))

    # ------------------------------------------------------------------ validation
    def finalize(self) -> dict:
        """Applique l'équipement (paquetage ou boutique) sur la copie ; renvoie le résumé de l'équipement."""
        if not self.ch.nom.strip():
            self.ch.nom = "Sans nom"
        res = self.engine.apply_starting_equipment(self.equip_mode, self.class_gold, self.cart)
        self.ch.pv_actuels = self.engine.hp_max()
        return res

    INCOMPLETE_TITLE = "Création de personnage incomplète"
    INCOMPLETE_TEXT = ("Il semble que certains choix essentiels (compétences, équipements ou sorts) n'aient pas encore "
                       "été finalisés. Souhaitez-vous tout de même générer ce personnage en l'état ? (Vous pourrez "
                       "ajuster les détails ultérieurement via le Mode Libre si nécessaire).")

    def incomplete_items(self) -> list[str]:
        """Choix essentiels encore ouverts (compétences, sorts, caractéristiques, langues…) et équipement."""
        items = [m["message"] for m in self.engine.missing_choices()]
        if self.equip_mode == "boutique" and not self.cart:
            items.append("Équipement : aucun achat dans la boutique")
        if not self.ch.nom.strip():
            items.append("Identité : nom du personnage")
        return items

    def first_incomplete_step(self) -> int:
        done = self.step_done()
        return next((i for i, ok in enumerate(done) if not ok), self.step)

    def confirm_incomplete(self) -> bool:
        """v50 : modale « Création de personnage incomplète » — True = « Valider malgré tout »."""
        from .dialogs import ask_yes_no
        items = self.incomplete_items()
        if not items:
            return True
        return ask_yes_no(self, self.INCOMPLETE_TITLE, self.INCOMPLETE_TEXT + "\n\nÀ finaliser :\n• " +
                          "\n• ".join(items[:12]), yes="Valider malgré tout", no="Poursuivre la création",
                          default_no=True)

    def _on_create(self) -> None:
        if not self.confirm_incomplete():                 # « Poursuivre la création » : retour à l'étape incomplète
            self.go(self.first_incomplete_step())
            return
        try:
            self.result_equipment = self.finalize()
        except ValueError as exc:
            self.win.statusBar().showMessage(str(exc), 8000)
            self.go(5)
            return
        self.accept()


def run_creation(win) -> bool:
    """Ouvre l'assistant ; « Créer le personnage » remplace la fiche (non enregistrée : à sauvegarder)."""
    backdrop = BlurBackdrop(win)
    dialog = CreationWizard(win)
    try:
        ok = dialog.exec() == 1
    finally:
        backdrop.dispose()
    if not ok:
        return False
    apply_creation(win, dialog)
    return True


def apply_creation(win, dialog: "CreationWizard") -> None:
    win.engine = dialog.engine
    win.path, win._dirty = None, True
    win.refresh_all()
    if hasattr(win, "schedule_autosave"):
        win.schedule_autosave()
    win.statusBar().showMessage("{} créé : {} {} — pensez à le sauvegarder (Fichier > Sauvegarder).".format(
        win.engine.ch.nom, win.engine.ch.race, win.engine.ch.classes[0]["nom"]), 10000)
