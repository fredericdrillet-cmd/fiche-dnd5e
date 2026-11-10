"""Fenêtre principale : en-tête d'identité, onglets, menus Fichier / Affichage, sauvegarde et import JSON."""
from __future__ import annotations

import html
import os
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QActionGroup, QColor, QKeySequence
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget)

from core import rules as R
from core.character import Character
from core.data_loader import Database
from core.engine import Engine
from core.settings import save_settings
from .stats_tab import StatsTab
from .classes_tab import ClassesTab
from .combat_tab import CombatTab
from .druid_tab import DruidTab
from . import theme
from .common import blocked, fill_combo, make_label, rich_tip
from .dialogs import ask_choice, ask_save_changes, ask_yes_no
from .inventory_tab import InventoryTab
from .magic_tab import MagicTab
from .options_dialog import OptionsDialog
from .progression_tab import ProgressionTab
from .companions_tab import CompanionsTab
from .race_tab import RaceTab
from .rp_tab import RPTab
from .theme_picker import make_theme_combo, theme_icon

FILE_FILTER = "Personnage D&D (*.json);;Tous les fichiers (*)"


class MainWindow(QMainWindow):
    def __init__(self, db: Database, settings: dict | None = None):
        super().__init__()
        self.db = db
        self.settings = settings or {"theme": theme.DEFAULT_THEME, "font_px": 14, "last_dir": ""}
        self.settings["theme"] = theme.resolve_key(self.settings["theme"])   # ancienne préférence -> thème par défaut
        self.engine = Engine(db, Engine.new_character(db))
        self.path: Path | None = None
        self._dirty = False
        self.resize(1600, 900)                 # format 16/9
        self.setMinimumSize(1024, 640)          # v50 : fenêtre réduite possible (onglets défilants), maximisable

        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)
        lay.addLayout(self._build_header())
        # bannière persistante de Forme sauvage (visible sur tous les onglets)
        self.form_banner = QWidget()
        fb = QHBoxLayout(self.form_banner)
        fb.setContentsMargins(0, 0, 0, 0)
        self.form_label = make_label("", "banner", wrap=True)
        self.form_end_btn = QPushButton("✕ Reprendre sa forme normale")
        self.form_end_btn.setProperty("role", "ghost")
        self.form_end_btn.setToolTip("<qt><b>Fin de la forme sauvage</b><br/>Restaure vos statistiques physiques, "
                                     "votre CA et vos PV d'avant la transformation.</qt>")
        fb.addWidget(self.form_label, 1)
        fb.addWidget(self.form_end_btn)
        self.form_banner.setVisible(False)
        lay.addWidget(self.form_banner)
        self.form_end_btn.clicked.connect(self._on_end_form)

        # Rafraîchissement paresseux : seul l'onglet visible est recalculé ; les autres le seront à leur ouverture.
        # (DND_EAGER_REFRESH=1 force le recalcul de tout, utilisé par les tests sans interface.)
        self.lazy_refresh = os.environ.get("DND_EAGER_REFRESH") != "1"
        self._stale: set[str] = set()
        self.tabs = QTabWidget()
        self.tabs.setMovable(True)                          # onglets déplaçables par glisser-déposer
        self.classes_tab = ClassesTab(self)
        self.stats_tab = StatsTab(self)                     # Caractéristiques + Compétences en une seule vue
        self.abilities_tab = self.stats_tab.abilities
        self.race_tab = RaceTab(self)
        self.rp_tab = RPTab(self)
        self.skills_tab = self.stats_tab.skills
        self.combat_tab = CombatTab(self)
        self.magic_tab = MagicTab(self)
        self.progress_tab = ProgressionTab(self)
        self.inventory_tab = InventoryTab(self)
        self.druid_tab = DruidTab(self)
        self.companions_tab = CompanionsTab(self)
        # (clé, onglet, titre) : la clé sert à mémoriser l'ordre choisi par l'utilisateur
        self.tab_defs = [("classes", self.classes_tab, "⚔ Classes"),
                         ("caracteristiques", self.stats_tab, "✦ Caractéristiques, Compétences"),
                         ("race", self.race_tab, "☗ Race, Historique, Langues"),
                         ("rp", self.rp_tab, "✎ Histoire, Portrait (RP)"),
                         ("combat", self.combat_tab, "🛡 Combat"),
                         ("magie", self.magic_tab, "✧ Magie"),
                         ("druide", self.druid_tab, "🐾 Forme sauvage"),
                         ("menagerie", self.companions_tab, "🐴 Ménagerie && Montures"),
                         ("progression", self.progress_tab, "▲ Progression, Dons"),
                         ("inventaire", self.inventory_tab, "🎒 Inventaire")]
        self.tab_list = [(w, title) for _, w, title in self.tab_defs]
        self._key_of = {id(w): k for k, w, _ in self.tab_defs}
        self._tab_by_key = {k: (w, title) for k, w, title in self.tab_defs}
        self._sync_tabs()
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.tabs.tabBar().tabMoved.connect(self._on_tab_moved)
        lay.addWidget(self.tabs, 1)

        # v28 : deux voyants cliquables — « ○ N choix à faire » (oublis, couleur d'ornement) et « ⚠ N incohérence(s) »
        # (excès, prérequis) ; un clic ouvre la liste et mène à l'onglet concerné
        self.missing_btn = QPushButton("")
        self.missing_btn.setFlat(True)
        self.missing_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.missing_btn.clicked.connect(self.show_checklist)
        self.statusBar().addPermanentWidget(self.missing_btn)
        self.warn_label = QPushButton("")
        self.warn_label.setFlat(True)
        self.warn_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.warn_label.clicked.connect(self.show_checklist)
        self.warn_label.setContentsMargins(0, 0, 28, 0)          # légèrement décalé vers la gauche (équilibre visuel)
        self.statusBar().addPermanentWidget(self.warn_label)
        self._build_menu()
        # v48 : sauvegarde automatique (1,5 s après la dernière modification), hors du fichier du joueur
        from PyQt6.QtCore import QTimer
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.setInterval(1500)
        self._autosave_timer.timeout.connect(self.autosave)
        from . import wheel_guard                      # v35 : la molette ne modifie plus aucun contrôle
        wheel_guard.install(QApplication.instance())
        self.refresh_all()

    # ------------------------------------------------------------------ accès
    @property
    def ch(self) -> Character:
        return self.engine.ch

    @property
    def free_mode(self) -> bool:
        """v48 — Mode libre (Options) : toute la fiche est modifiable. Mode guidé (par défaut) : la progression
        passe par « Niveau supérieur », le nom est fixé à la création."""
        return bool(self.settings.get("mode_libre", False))

    def _apply_mode_locks(self) -> None:
        free = self.free_mode
        self.name_edit.setReadOnly(not free)
        self.name_edit.setToolTip("" if free else rich_tip("Nom du personnage", "Mode guidé : le nom est fixé à la "
                                                           "création (Fichier > Nouveau personnage). Activez le Mode "
                                                           "libre dans Options pour le modifier."))
        self.level.setEnabled(free)
        self.level.setVisible(free)
        self.level_label.setVisible(free)
        self.class_badge.setVisible(not free)
        if not free:
            parts = []
            for e in self.ch.classes:
                parts.append("<b>{}</b> {}{}".format(html.escape(e["nom"]), e["niveau"], " · <i>{}</i>".format(
                    html.escape(e["sous_classe"])) if e.get("sous_classe") else ""))
            self.class_badge.setText("⚔ {} &nbsp;—&nbsp; Niveau {}".format(" / ".join(parts), self.engine.total_level))
            self.class_badge.setToolTip(rich_tip("Classes et niveau", "Lecture seule en Mode guidé : utilisez "
                                                 "« ▲ Niveau supérieur » (multiclassage compris). Mode libre "
                                                 "(Options) : sélecteurs modifiables."))
        self.level.setToolTip("" if free else rich_tip("Niveau global", "Mode guidé : utilisez « ▲ Niveau "
                                                       "supérieur » (multiclassage compris). Le Mode libre (Options) "
                                                       "déverrouille ce compteur."))

    # ------------------------------------------------------------------ en-tête
    def _build_header(self) -> QHBoxLayout:
        h = QHBoxLayout()
        self.name_edit, self.player_edit = QLineEdit(), QLineEdit()
        self.name_edit.setPlaceholderText("Nom du personnage")
        self.player_edit.setPlaceholderText("Joueur")
        self.xp = QSpinBox()
        self.xp.setRange(0, 99_999_999)
        self.xp.setSingleStep(100)
        self.level = QSpinBox()
        self.level.setRange(1, R.MAX_LEVEL)
        self.xp_hint = make_label("", "muted")
        # v51 : « Vitesse » et « Maîtrise » retirées de l'en-tête (déjà affichées dans l'onglet Combat)
        self.badges = {k: make_label("", "badge") for k in ("pv", "ca", "init")}
        self.name_edit.setMinimumWidth(240)
        self.player_edit.setMinimumWidth(220)            # v48 : la place de l'alignement revient au joueur
        h.addWidget(make_label("⚜ Personnage", "title"))
        h.addWidget(self.name_edit, 2)
        h.addWidget(make_label("Joueur"))
        h.addWidget(self.player_edit, 2)
        h.addWidget(make_label("XP"))
        h.addWidget(self.xp)
        h.addWidget(self.xp_hint)
        self.level_label = make_label("Niveau global")
        h.addWidget(self.level_label)
        h.addWidget(self.level)
        # v50 : Mode guidé -> classe(s), sous-classe et niveau en texte statique stylé (badges)
        self.class_badge = make_label("", "badge")
        self.class_badge.setTextFormat(Qt.TextFormat.RichText)
        h.addWidget(self.class_badge)
        # v29 : montée de niveau guidée (le compteur reste disponible : mode « MJ », sans assistant)
        self.levelup_btn = QPushButton("▲ Niveau supérieur")
        self.levelup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.levelup_btn.setToolTip(rich_tip("Niveau supérieur", "Cliquez ici pour lancer l'assistant de montée de "
                                             "niveau pas à pas : classe, points de vie, aptitudes gagnées, choix du "
                                             "niveau, récapitulatif avant / après (Ctrl+L)."))
        self.levelup_btn.clicked.connect(self.action_level_up)
        h.addWidget(self.levelup_btn)
        from .dice_dialog import d20_button
        for k, b in self.badges.items():
            h.addWidget(b)
            if k == "init":                              # v45 : dé d20 cliquable à côté de l'initiative
                self.init_btn = d20_button("Jet d'initiative : 1d20 + modificateur d'initiative")
                self.init_btn.clicked.connect(self.action_roll_initiative)
                h.addWidget(self.init_btn)
        self.name_edit.textEdited.connect(lambda t: self._set_text("nom", t))
        self.player_edit.textEdited.connect(lambda t: self._set_text("joueur", t))
        self.xp.valueChanged.connect(self._on_xp)
        self.level.valueChanged.connect(self._on_level)
        return h

    def action_roll_initiative(self):
        from .dice_dialog import roll_initiative
        return roll_initiative(self)

    def _set_text(self, attr: str, value: str):
        setattr(self.ch, attr, value)
        self._dirty = True
        self._update_title()

    def _on_xp(self, value: int):
        self.ch.experience = value
        self.changed()

    def _on_level(self, value: int):
        self.engine.set_total_level(value, self.classes_tab.current_index())
        self.changed()

    # ------------------------------------------------------------------ menus
    def _build_menu(self):
        bar = self.menuBar()
        fm = bar.addMenu("&Fichier")
        for text, key, slot in (("Nouveau personnage… (assistant de création)", QKeySequence.StandardKey.New,
                                 self.action_new),
                                ("Charger…", QKeySequence.StandardKey.Open, self.action_open),
                                ("Sauvegarder", QKeySequence.StandardKey.Save, self.action_save),
                                ("Sauvegarder sous…", QKeySequence("Ctrl+Shift+S"), self.action_save_as)):
            act = QAction(text, self)
            act.setShortcut(key)
            act.triggered.connect(slot)
            fm.addAction(act)
        fm.addSeparator()
        lvl_act = QAction("▲ Niveau supérieur…", self)
        lvl_act.setShortcut(QKeySequence("Ctrl+L"))
        lvl_act.triggered.connect(self.action_level_up)
        fm.addAction(lvl_act)
        fm.addSeparator()
        quit_act = QAction("Quitter", self)
        quit_act.setShortcut(QKeySequence("Ctrl+Q"))
        quit_act.triggered.connect(self.close)
        fm.addAction(quit_act)

        vm = bar.addMenu("&Affichage")
        full = QAction("Plein écran", self)
        full.setShortcut(QKeySequence("F11"))
        full.triggered.connect(self.toggle_fullscreen)
        vm.addAction(full)
        reset_tabs = QAction("Réinitialiser l'ordre des onglets", self)
        reset_tabs.triggered.connect(self.reset_tab_order)
        vm.addAction(reset_tabs)

        om = bar.addMenu("&Options")
        prefs = QAction("Préférences… (thème, taille du texte)", self)
        prefs.setShortcut(QKeySequence("Ctrl+,"))
        prefs.triggered.connect(self.action_options)
        om.addAction(prefs)
        om.addSeparator()
        group = QActionGroup(self)
        group.setExclusive(True)
        for key, t in theme.THEMES.items():
            act = QAction(theme_icon(t), t.name, self, checkable=True)
            act.setChecked(key == self.settings["theme"])
            act.triggered.connect(lambda _=False, k=key: self.apply_appearance(k, self.settings["font_px"], save=True))
            group.addAction(act)
            om.addAction(act)
        self._theme_actions = group

        # sélecteur rapide de thème, toujours visible dans le coin de la barre de menus
        self.theme_combo = make_theme_combo()
        self.theme_combo.setCurrentIndex(max(0, self.theme_combo.findData(self.settings["theme"])))
        self.theme_combo.activated.connect(
            lambda _=0: self.apply_appearance(self.theme_combo.currentData(), self.settings["font_px"], save=True))
        bar.setCornerWidget(self.theme_combo)

        hm = bar.addMenu("&Aide")
        about = QAction("À propos / données chargées", self)
        about.triggered.connect(self.action_about)
        hm.addAction(about)

    def action_options(self):
        OptionsDialog(self).exec()

    def apply_appearance(self, key: str, font_px: int, save: bool = False) -> None:
        """Change le thème / la taille du texte à chaud (aperçu), et mémorise les préférences si `save`."""
        app = QApplication.instance()
        key = theme.resolve_key(key)
        theme.apply_theme(app, key, font_px)          # palette + QSS à dégradés, pour toute l'application
        self.settings["theme"], self.settings["font_px"] = key, font_px
        for act, k in zip(self._theme_actions.actions(), theme.THEMES):
            act.setChecked(k == key)
        with blocked(self.theme_combo):
            self.theme_combo.setCurrentIndex(max(0, self.theme_combo.findData(key)))
        if save:
            save_settings(self.settings)
        self.refresh_all()

    def mark_dirty(self):
        self._dirty = True
        self._update_title()

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    # ------------------------------------------------------------------ actions fichier
    def _confirm_discard(self, discard_label: str = "Ne pas enregistrer") -> bool:
        """
        Modifications non enregistrées : modale [Enregistrer] · [Ne pas enregistrer…] · [Annuler].
        Renvoie True si l'action peut continuer (sauvegarde réussie ou abandon volontaire), False sinon.
        """
        if not self._dirty:
            return True
        choice = ask_save_changes(self, discard_label)          # rappel des choix manquants : lu par la modale
        if choice == "save":
            self.action_save()
            return not self._dirty               # « Enregistrer sous » annulé ou erreur d'écriture : on reste
        return choice == "discard"

    def action_new(self):
        """Fichier > Nouveau personnage : assistant de création niveau 1 (inspiré de Baldur's Gate 3)."""
        if not self._confirm_discard():
            return False
        from .creation_wizard import run_creation
        return run_creation(self)

    def new_blank(self) -> None:
        """Personnage par défaut (sans assistant) — utilisé si l'assistant est fermé au premier lancement."""
        self.engine = Engine(self.db, Engine.new_character(self.db))
        self.path, self._dirty = None, False
        self.refresh_all()

    def action_open(self):
        if not self._confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Ouvrir un personnage", self._start_dir(), FILE_FILTER)
        if not path:
            return
        self.settings["last_dir"] = str(Path(path).parent)
        try:
            char = Character.load(path)
        except (OSError, ValueError, KeyError) as exc:
            QMessageBox.critical(self, "Chargement impossible", str(exc))
            return
        self.load_character(char, Path(path))

    def load_character(self, char: Character, path: Path | None, dirty: bool = False) -> None:
        self.engine = Engine(self.db, char)
        self.engine.normalize()
        if not char.competences_historique:
            self.engine.apply_background()
        self.path, self._dirty = path, dirty
        if path is not None:
            self.settings["dernier_fichier"] = str(path)
            save_settings(self.settings)
        self.refresh_all()

    def _start_dir(self) -> str:
        d = self.settings.get("last_dir") or ""
        return d if d and Path(d).is_dir() else str(Path.home())

    def action_save(self):
        if self.path is None:
            self.action_save_as()
        else:
            self._write(self.path)

    def action_save_as(self):
        default = (self.ch.nom or "personnage").replace(" ", "_") + ".json"
        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le personnage", str(Path(self._start_dir()) / default), FILE_FILTER)
        if path:
            if not path.lower().endswith(".json"):
                path += ".json"
            self._write(Path(path))

    def _write(self, path: Path):
        try:
            self.ch.save(path)
        except OSError as exc:
            QMessageBox.critical(self, "Enregistrement impossible", str(exc))
            return
        self.path, self._dirty = path, False
        self.settings["dernier_fichier"] = str(path)        # v48 : rouvert au prochain lancement
        save_settings(self.settings)
        self._update_title()
        note = self.missing_note()
        self.statusBar().showMessage("Personnage enregistré : {}{}".format(path, " — " + note if note else ""), 8000)

    # ------------------------------------------------------------------ v48 : sauvegarde automatique
    @staticmethod
    def autosave_path() -> Path:
        from core.paths import user_data_dir
        return user_data_dir() / "sauvegarde_auto.json"

    def schedule_autosave(self) -> None:
        timer = getattr(self, "_autosave_timer", None)
        if timer is not None:
            timer.start()

    def autosave(self, path: Path | None = None) -> bool:
        """Copie de sécurité du personnage en cours (avec le fichier d'origine), relue au prochain lancement."""
        import json
        target = path or self.autosave_path()
        data = self.ch.to_dict()
        data["_fichier"] = str(self.path) if self.path else ""
        data["_modifie"] = bool(self._dirty)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False)
        except OSError:
            return False
        return True

    def restore_last_session(self, autosave: Path | None = None) -> str:
        """Au lancement : la sauvegarde automatique si elle contient des modifications non enregistrées (ou un
        personnage jamais enregistré), sinon le dernier fichier enregistré. Renvoie ce qui a été rouvert."""
        import json
        auto = autosave or self.autosave_path()
        last = Path(self.settings.get("dernier_fichier") or "")
        try:
            data = json.loads(auto.read_text(encoding="utf-8")) if auto.exists() else None
        except (OSError, ValueError):
            data = None
        if isinstance(data, dict) and "classes" in data and (data.get("_modifie") or not data.get("_fichier")):
            src = Path(data["_fichier"]) if data.get("_fichier") else None
            self.load_character(Character.from_dict(data), src if src and src.exists() else None,
                                dirty=bool(data.get("_modifie")))
            return "auto"
        if str(last) not in ("", ".") and last.is_file():
            try:
                self.load_character(Character.load(last), last)
                return "fichier"
            except (OSError, ValueError, KeyError):
                return ""
        return ""

    def action_about(self):
        db = self.db
        QMessageBox.information(
            self, "Données chargées",
            "{} classes, {} races, {} historiques, {} sorts, {} armes, {} armures, {} boucliers, {} dons, "
            "{} objets d'équipement, {} langues, {} outils.\n\nDossier : {}\n{}".format(
                len(db.classes), len(db.races), len(db.backgrounds), len(db.spells), len(db.weapons),
                len(db.armors) - 1, len(db.shields), len(db.feats), len(db.equipment), len(db.languages),
                len(db.tools), db.data_dir, "\n".join(db.warnings)))

    def closeEvent(self, event):
        if self._confirm_discard("Ne pas enregistrer et quitter"):
            if self._dirty:                              # « Ne pas enregistrer » : la copie de sécurité est oubliée
                try:
                    self.autosave_path().unlink()
                except OSError:
                    pass
            event.accept()
        else:
            event.ignore()

    # ------------------------------------------------------------------ navigation
    def open_magic(self, class_name: str):
        self.magic_tab.select_class(class_name)
        self.tabs.setCurrentWidget(self.magic_tab)

    # ------------------------------------------------------------------ onglets : visibilité, ordre, glisser-déposer
    def _visible_keys(self) -> list[str]:
        """Onglets à afficher : « Forme sauvage » seulement si le personnage a des niveaux de Druide."""
        has_druid = any(c["nom"] == "Druide" for c in self.ch.classes)
        # v48 : onglet Race (choix de race / historique / langues) remplacé par l'assistant de création et l'encart
        # « Résumé de la race » ; il reste visible en Mode libre, ou tant qu'un choix de langue y est en attente
        race_tab = self.free_mode or any(m["onglet"] == "race" for m in self.engine.missing_choices())
        return [k for k, _, _ in self.tab_defs if (k != "druide" or has_druid) and (k != "race" or race_tab)]

    def _full_order(self) -> list[str]:
        """Ordre complet mémorisé (clés inconnues ignorées, nouvelles clés ajoutées à leur place par défaut)."""
        default = [k for k, _, _ in self.tab_defs]
        saved = [k for k in self.settings.get("ordre_onglets") or [] if k in default]
        for i, k in enumerate(default):
            if k not in saved:
                saved.insert(min(i, len(saved)), k)
        return saved

    def _current_keys(self) -> list[str]:
        """Clés des onglets présents dans la barre, y compris un onglet masqué (ordre de la barre)."""
        return [self._key_of.get(id(self.tabs.widget(i))) for i in range(self.tabs.count())]

    def shown_keys(self) -> list[str]:
        """Clés des onglets réellement affichés (l'onglet « Forme sauvage » est masqué hors Druide)."""
        visible = set(self._visible_keys())
        return [k for k in self._current_keys() if k in visible]

    def _sync_tabs(self) -> None:
        """
        Barre d'onglets : tous les onglets sont créés une fois dans l'ordre mémorisé ; l'onglet « Forme sauvage »
        est simplement masqué / affiché (setTabVisible) au lieu de reconstruire la barre. L'onglet sélectionné par
        l'utilisateur est donc conservé quand on change de classe (ex. passage en Druide).
        NB : les signaux de la QTabBar ne doivent jamais être bloqués — le QTabWidget s'en sert pour synchroniser
        la page affichée (c'était la cause du saut vers l'onglet Caractéristiques).
        """
        order = self._full_order()
        current = self.tabs.currentWidget()
        self._syncing = True
        try:
            if self._current_keys() != order:
                while self.tabs.count():
                    self.tabs.removeTab(0)
                for k in order:
                    widget, title = self._tab_by_key[k]
                    self.tabs.addTab(widget, title)
            visible = set(self._visible_keys())
            for i, k in enumerate(self._current_keys()):
                if hasattr(self.tabs, "setTabVisible"):
                    self.tabs.setTabVisible(i, k in visible)
            cur_key = self._key_of.get(id(current)) if current is not None else None
            if cur_key in visible:
                self.tabs.setCurrentWidget(current)
            elif cur_key is not None:                        # l'onglet courant vient d'être masqué
                self.tabs.setCurrentWidget(self._tab_by_key[next(k for k in order if k in visible)][0])
        finally:
            self._syncing = False

    def _on_tab_moved(self, _from: int = 0, _to: int = 0) -> None:
        """L'utilisateur a glissé un onglet : on mémorise le nouvel ordre (les onglets masqués gardent leur place)."""
        self.settings["ordre_onglets"] = [k for k in self._current_keys() if k]   # onglets masqués compris
        save_settings(self.settings)

    def reset_tab_order(self) -> None:
        self.settings["ordre_onglets"] = []
        save_settings(self.settings)
        self._sync_tabs()

    def _on_tab_changed(self, _index: int = 0) -> None:
        """À l'ouverture d'un onglet, on le recalcule seulement s'il a été marqué « à rafraîchir »."""
        if getattr(self, "_syncing", False):
            return
        key = self._key_of.get(id(self.tabs.currentWidget()))
        if key in self._stale:
            self._refresh_tab(key)

    def _refresh_tab(self, key: str) -> None:
        widget, _ = self._tab_by_key[key]
        with self.engine.batch():
            widget.refresh()
        self._stale.discard(key)

    # ------------------------------------------------------------------ cycle de rafraîchissement
    def changed(self):
        """Appelé après toute modification : normalise le personnage puis rafraîchit l'en-tête et l'onglet visible."""
        eng = self.engine
        eng.normalize()
        self._dirty = True
        self.refresh_all()
        self.schedule_autosave()

    def light_changed(self, keep_current: bool = True) -> None:
        """
        Modification légère (clic sur une sphère de ressource, une case d'emplacement...) : le widget cliqué s'est
        déjà mis à jour lui-même ; on se contente de marquer les autres onglets « à rafraîchir » — aucun recalcul.
        """
        self._dirty = True
        current = self._key_of.get(id(self.tabs.currentWidget()))
        self._stale = {k for k, _, _ in self.tab_defs if not (keep_current and k == current)}
        self._update_title()

    def refresh_all(self):
        """En-tête + onglet visible (les autres sont marqués et recalculés à leur ouverture)."""
        eng, ch = self.engine, self.ch
        with eng.batch():
            with blocked(self.name_edit, self.player_edit, self.xp, self.level):
                if self.name_edit.text() != ch.nom:
                    self.name_edit.setText(ch.nom)
                if self.player_edit.text() != ch.joueur:
                    self.player_edit.setText(ch.joueur)
                self.xp.setValue(ch.experience)
                self.level.setValue(eng.total_level)
            self.xp_hint.setText("(niveau {} selon l'XP)".format(eng.level_from_xp()))
            form = eng.form_status()
            if form:                                     # transformé : PV et CA de la bête, badge animal + infobulle
                tip = "<qt><b>{} {}</b><br/>PV et CA de la bête ; vos PV ({}/{}) sont mis de côté.</qt>".format(
                    form["icone"], form["libelle"], ch.pv_actuels, eng.hp_max())
                self.badges["pv"].setText("{} PV {}/{}".format(form["icone"], form["pv"], form["pv_max"]))
                self.badges["ca"].setText("{} CA {}".format(form["icone"], form["ca"]))
            else:
                tip = ""
                self.badges["pv"].setText("PV {}/{}".format(ch.pv_actuels, eng.hp_max()))
                self.badges["ca"].setText("CA {}{}".format(eng.armor_class()[0], " ⚠" if eng.unproficient_gear() else ""))
            for k in ("pv", "ca"):
                self.badges[k].setToolTip(tip)
            if not form:                                 # v36 : calcul détaillé de la CA au survol
                gear = eng.unproficient_gear()
                self.badges["ca"].setToolTip(rich_tip("Classe d'armure", eng.ac_breakdown_text() + "".join(
                    "\n⚠ {} ({})".format(g["message"], g["nom"]) for g in gear) + (
                    "\n⚠ Impossible de lancer un sort tout en portant une armure non maîtrisée." if gear else "")))
            idet = eng.initiative_detail()               # v45 : initiative + dernier jet
            self.badges["init"].setText("Init {}{}".format(R.fmt_bonus(idet["total"]), " (jet : {})".format(
                ch.initiative_jet) if ch.initiative_jet else ""))
            self.badges["init"].setToolTip(rich_tip("Initiative", "\n".join(
                "{} : {}".format(a, R.fmt_bonus(v)) for a, v in idet["termes"]) + "".join(
                "\n{} : {}".format(a, v) for a, v in idet["des"]) + (
                "\nAvantage : " + ", ".join(idet["avantage"]) if idet["avantage"] else "") +
                "\nCliquez sur le d20 pour lancer 1d20 + modificateur."))
            self.levelup_btn.setEnabled(eng.total_level < R.MAX_LEVEL)
            self._apply_mode_locks()
            self._refresh_form_banner()
            self._sync_tabs()
            current = self._key_of.get(id(self.tabs.currentWidget()))
            self._stale = {k for k, _, _ in self.tab_defs}
            for key in list(self._stale):
                if not self.lazy_refresh or key == current:
                    self._tab_by_key[key][0].refresh()
                    self._stale.discard(key)
            self.refresh_warnings()
        self._update_title()

    def refresh_warnings(self):
        """Voyants de la barre d'état (oublis / incohérences) + pastilles numérotées sur les onglets (v28)."""
        t = theme.current()
        warns = self.engine.warnings()
        missing = self.engine.missing_choices()
        n_missing = sum(m["nombre"] for m in missing)
        self.missing_btn.setVisible(bool(missing))
        self.missing_btn.setText("○ {} choix à faire".format(n_missing))
        self.missing_btn.setStyleSheet("color: {}; font-weight: bold; border: none;".format(t.ornament))
        self.missing_btn.setToolTip("<qt><b>Choix restant à faire</b><br/>" + "<br/>".join(
            "• {} — {}".format(self._tab_name(m["onglet"]), html.escape(m["message"])) for m in missing)
            + "<br/><i>Cliquez pour aller à l'onglet concerné.</i></qt>" if missing else "")
        if warns:
            self.warn_label.setText("⚠ {} incohérence{}".format(len(warns), "s" * (len(warns) > 1)))
            self.warn_label.setStyleSheet("color: {}; font-weight: bold; border: none;".format(t.warn))
        else:
            self.warn_label.setText("✔ Fiche complète et cohérente" if not missing else "✔ Aucune incohérence")
            self.warn_label.setStyleSheet("color: {}; border: none;".format(t.good))
        self.warn_label.setToolTip("<qt>" + "<br/>".join(html.escape(w) for w in warns) + "</qt>" if warns else "")
        self._refresh_tab_badges(missing)

    BADGES = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"

    def _tab_name(self, key: str) -> str:
        title = self._tab_by_key.get(key, (None, key))[1].replace("&&", "&")   # « && » = « & » affiché par Qt
        return title.split(" ", 1)[1] if " " in title else title

    def _refresh_tab_badges(self, missing: list[dict]) -> None:
        """Titre d'onglet suivi d'une pastille « ③ » (choix à faire), en couleur d'ornement ; retirée à zéro."""
        counts: dict[str, int] = {}
        for m in missing:
            counts[m["onglet"]] = counts.get(m["onglet"], 0) + m["nombre"]
        self.tab_badges = counts
        bar = self.tabs.tabBar()
        t = theme.current()
        for i, key in enumerate(self._current_keys()):
            if key not in self._tab_by_key:
                continue
            n = counts.get(key, 0)
            title = self._tab_by_key[key][1]
            badge = (" " + (self.BADGES[n - 1] if n <= len(self.BADGES) else "({})".format(n))) if n else ""
            self.tabs.setTabText(i, title + badge)
            self.tabs.setTabToolTip(i, "{} choix à faire dans cet onglet".format(n) if n else "")
            if hasattr(bar, "setTabTextColor"):
                bar.setTabTextColor(i, QColor(t.ornament) if n else QColor())

    def show_checklist(self) -> None:
        """Liste des choix restants et des incohérences ; le choix sélectionné ouvre son onglet."""
        missing = self.engine.missing_choices()
        warns = self.engine.warnings()
        if not missing and not warns:
            self.statusBar().showMessage("Fiche complète et cohérente : rien à corriger.", 5000)
            return
        labels = {}
        for m in missing:
            labels["○ {} — {}".format(self._tab_name(m["onglet"]), m["message"])] = m["onglet"]
        for w in warns:
            labels["⚠ " + w] = ""
        picked = ask_choice(self, "Choix à faire et incohérences",
                            "{} choix à faire, {} incohérence(s). Choisissez une ligne pour ouvrir l'onglet "
                            "concerné.".format(sum(m["nombre"] for m in missing), len(warns)), list(labels))
        self.go_to_tab(labels.get(picked, ""))

    def action_level_up(self) -> bool:
        from .levelup_dialog import run_level_up
        return run_level_up(self)

    def missing_note(self) -> str:
        """« 3 choix restent à faire (Magie, Compétences) » — rappel non bloquant à l'enregistrement."""
        missing = self.engine.missing_choices()
        if not missing:
            return ""
        n = sum(m["nombre"] for m in missing)
        tabs = list(dict.fromkeys(self._tab_name(m["onglet"]) for m in missing))
        return "{} choix {} à faire ({})".format(n, "restent" if n > 1 else "reste", ", ".join(tabs))

    def go_to_tab(self, key: str) -> None:
        if key in self._tab_by_key and key in self._visible_keys():
            self.tabs.setCurrentWidget(self._tab_by_key[key][0])

    def _on_end_form(self):
        self.engine.end_form()
        self.statusBar().showMessage("Forme normale reprise : statistiques du druide restaurées.", 6000)
        self.changed()

    def _refresh_form_banner(self):
        beast = self.engine.wild_form()
        self.form_banner.setVisible(beast is not None)
        if beast is not None:
            poly = self.ch.forme_type == "metamorphose"
            head = ("🦋 État actif : Métamorphose ({})" if poly else "🐾 Forme active : {}").format(beast["nom"])
            conc = (" — concentration sur Métamorphose (JS de Constitution à chaque dégât)" if poly else
                    " — concentration maintenue : " + self.ch.concentration if self.ch.concentration else "")
            self.form_label.setText("{} — PV de la bête {} / {} — CA {} — sorts indisponibles{}".format(
                head, self.ch.forme_pv, self.engine.beast_hp_max(beast["nom"]), self.engine.beast_ac(beast), conc))
            self.form_end_btn.setText("✕ Mettre fin à la Métamorphose" if poly else "✕ Reprendre sa forme normale")

    def _update_title(self):
        name = self.ch.nom or "Nouveau personnage"
        self.setWindowTitle("{}{} — Fiche de personnage D&D 5e".format("● " if self._dirty else "", name))


def run(db: Database, settings: dict | None = None) -> int:
    from core.settings import load_settings
    settings = settings or load_settings()
    settings["theme"] = theme.resolve_key(settings["theme"])
    app = QApplication.instance() or QApplication([])
    theme.apply_theme(app, settings["theme"], settings["font_px"])
    from core.paths import get_resource_path           # v47 : icône de l'appli (code source ou exécutable)
    for name in ("app_icon.ico", "app_icon.png"):
        icon_path = get_resource_path(os.path.join("assets", name))
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QIcon
            app.setWindowIcon(QIcon(icon_path))
            break
    win = MainWindow(db, settings)
    win.show()
    # v48 : le dernier personnage est rouvert ; sinon (premier lancement) l'assistant de création s'ouvre
    if not win.restore_last_session() and settings.get("assistant_au_demarrage", True):
        from .creation_wizard import run_creation
        run_creation(win)
    return app.exec()
