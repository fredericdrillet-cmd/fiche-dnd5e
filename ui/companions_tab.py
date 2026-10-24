"""
Onglet « Ménagerie & Montures » : ménagerie active du personnage (familiers, compagnons de classe, invocations,
montures) + mini-fiche interactive.

    - à gauche : la ménagerie active (familiers 🐾, compagnons de classe ⚔, invocations ✨), boutons
      « + Ajouter une entité » (sélecteur filtrable Familiers / Compagnons de classe / Invocations, entités
      recommandées ★ en tête) et « ✖ Retirer » ; conseils contextuels (Maître des bêtes, Pacte de la chaîne…) ;
    - à droite : mini-fiche de l'entité sélectionnée — nom personnalisable, statut, niveau du sort de convocation,
      CA, PV (jauge cliquable + compteurs), vitesses, caractéristiques et sauvegardes cliquables (d20 animé),
      compétences, traits (infobulles), attaques (d20 de toucher puis dés de dégâts animés), réactions.
    Toutes les valeurs viennent du moteur (core/companions.py) : mise à l'échelle selon le bonus de maîtrise, le
    niveau de classe, la caractéristique d'incantation ou le niveau du sort.
"""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QComboBox, QDialog, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QPushButton, QScrollArea, QSpinBox, QSplitter, QTextBrowser,
                             QVBoxLayout, QWidget)

from core import companions as C
from core import dice as D
from core import rules as R
from core.rules import norm
from . import theme
from .common import BaseTab, DamageLabel, blocked, make_label, rich_tip
from .dialogs import BlurBackdrop
from .dice_dialog import d20_button, die_icon, roll_damage_dialog, roll_dice
from .game_widgets import ActionChip, clear_layout
from .orbs import GaugeBar

TYPE_ICONS = {"familiar": "🐾", "class_companion": "⚔", "summons": "✨", "mount": "🐴"}
ABBR = {"Force": "FOR", "Dextérité": "DEX", "Constitution": "CON", "Intelligence": "INT", "Sagesse": "SAG",
        "Charisme": "CHA"}


def _cell(*widgets) -> QWidget:
    """Cellule de grille : widgets alignés à gauche et centrés verticalement, sans marge."""
    box = QWidget()
    lay = QHBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(6)
    for w in widgets:
        lay.addWidget(w, 0, Qt.AlignmentFlag.AlignVCenter)
    lay.addStretch(1)
    return box


def _dash() -> QLabel:
    return make_label("—", "muted")


def _die(formula: str) -> QLabel:
    """Petite icône du plus gros dé de la formule (d4 → d12), même taille que le bouton d20."""
    groups, _ = D.parse_damage(formula)
    lab = QLabel()
    lab.setPixmap(die_icon(groups[0][2] if groups else 6, 22).pixmap(20, 20))
    lab.setFixedSize(30, 30)                             # même gabarit que le bouton d20
    lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return lab


def entity_summary_html(ent: dict, accent: str) -> str:
    """Aperçu court d'une entité (sélecteur)."""
    e = html.escape
    speeds = ", ".join("{} {}".format(C.SPEED_LABELS.get(k, k), v) for k, v in (ent.get("speed") or {}).items())
    stats = " · ".join("{} {}".format(ABBR[C.AB_KEYS[k]], v) for k, v in (ent.get("stats") or {}).items()
                       if k in C.AB_KEYS)
    srcs = "; ".join(s["name"] for s in (ent.get("summon_info") or {}).get("sources", []))
    acts = "".join("<li><b>{}</b> — {}</li>".format(e(a["name"]), e(a.get("description", "")[:160]))
                   for a in ent.get("actions") or [])
    return ("<h3 style='color:{}'>{}</h3><p><i>{} {} — {} — FP {}</i></p><p><b>CA</b> {} {} — <b>PV</b> {} ({}) — "
            "{}</p><p>{}</p><p><b>Obtenu par :</b> {}</p><ul>{}</ul>").format(
        accent, e(ent["name"]), e(ent.get("type", "")), e(C.SIZE_LABELS.get(ent.get("size", ""), ent.get("size", ""))),
        e(ent.get("alignment", "")), e(str(ent.get("cr") if ent.get("cr") is not None else "—")), ent.get("ac"),
        e(ent.get("ac_note") or ""), ent.get("hp_base"), e(str(ent.get("hp_formula", ""))), e(speeds), e(stats),
        e(srcs or "—"), acts)


class EntityPicker(QDialog):
    """Sélecteur d'entités : puces de type, recherche, recommandées ★ en tête, aperçu à droite."""

    def __init__(self, parent, engine, start_type: str = "familiar", recommended: set | None = None):
        super().__init__(parent)
        self.engine = engine
        self.recommended = set(recommended or ())
        self.selected = ""
        self.setWindowTitle("Ajouter une entité")
        self.setModal(True)
        self.resize(900, 560)
        lay = QVBoxLayout(self)
        lay.addWidget(make_label("✚ Ajouter une entité à la ménagerie", "title"))
        chips = QHBoxLayout()
        self.type_btns: dict[str, QPushButton] = {}
        for key, label in C.TYPE_LABELS.items():
            b = QPushButton("{} {}".format(TYPE_ICONS[key], label))
            b.setCheckable(True)
            b.setProperty("role", "attune")
            b.clicked.connect(lambda _=False, k=key: self.set_type(k))
            chips.addWidget(b)
            self.type_btns[key] = b
        chips.addStretch(1)
        lay.addLayout(chips)
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔎 Rechercher (nom, type, sort ou aptitude d'origine)…")
        self.search.setClearButtonEnabled(True)
        lay.addWidget(self.search)
        body = QHBoxLayout()
        self.list = QListWidget()
        self.preview = QTextBrowser()
        body.addWidget(self.list, 2)
        body.addWidget(self.preview, 3)
        lay.addLayout(body, 1)
        self.hint = make_label("★ = recommandé pour votre classe / sous-classe", "muted")
        lay.addWidget(self.hint)
        btns = QHBoxLayout()
        btns.addStretch(1)
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setProperty("role", "ghost")
        self.ok_btn = QPushButton("Ajouter")
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.ok_btn)
        lay.addLayout(btns)
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self._accept)
        self.list.itemDoubleClicked.connect(lambda _it: self._accept())
        self.list.currentRowChanged.connect(self._on_row)
        self.search.textChanged.connect(lambda _t: self.fill())
        self._ids: list[str] = []
        self.etype = start_type
        self.set_type(start_type)

    def set_type(self, key: str) -> None:
        self.etype = key
        for k, b in self.type_btns.items():
            with blocked(b):
                b.setChecked(k == key)
        self.fill()

    def fill(self) -> None:
        text = norm(self.search.text())
        ents = self.engine.entities_of_type(self.etype)
        if text:
            ents = [e for e in ents if text in norm(" ".join([e["name"], e.get("type", ""), " ".join(
                s["name"] for s in (e.get("summon_info") or {}).get("sources", []))]))]
        ents.sort(key=lambda e: (e["id"] not in self.recommended, norm(e["name"])))
        self._ids = [e["id"] for e in ents]
        with blocked(self.list):
            self.list.clear()
            for e in ents:
                star = "★ " if e["id"] in self.recommended else ""
                it = QListWidgetItem("{}{} — {} (FP {})".format(star, e["name"], e.get("type", ""),
                                                               e.get("cr") if e.get("cr") is not None else "—"))
                self.list.addItem(it)
        if self._ids:
            self.list.setCurrentRow(0)
            self._on_row(0)

    def _on_row(self, row: int) -> None:
        if 0 <= row < len(self._ids):
            self.preview.setHtml(entity_summary_html(self.engine.entity(self._ids[row]), theme.current().accent_text))

    def _accept(self) -> None:
        row = self.list.currentRow()
        if 0 <= row < len(self._ids):
            self.selected = self._ids[row]
            self.accept()


def pick_entity(win, engine, start_type: str = "familiar", recommended=None) -> str:
    backdrop = BlurBackdrop(win, tint="rgba(0, 0, 0, 90)") if win is not None else None
    dlg = EntityPicker(win, engine, start_type, recommended)
    try:
        return dlg.selected if dlg.exec() == 1 else ""
    finally:
        if backdrop is not None:
            backdrop.dispose()


class CompanionsTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        root = QVBoxLayout(self)
        root.addWidget(make_label("Familiers, compagnons et invocations", "title"))
        self.hints_box = QVBoxLayout()
        root.addLayout(self.hints_box)
        split = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(split, 1)

        # ---------------- ménagerie active
        left = QGroupBox("Ménagerie active")
        ll = QVBoxLayout(left)
        self.list = QListWidget()
        ll.addWidget(self.list, 1)
        self.add_btn = QPushButton("✚ Ajouter une entité")
        self.mount_btn = QPushButton("🐴 Ajouter une monture")          # v36 : accès direct aux montures
        self.mount_btn.setToolTip("Cheval de selle, de trait, de guerre, poney, mule, chameau, mâtin.")
        self.remove_btn = QPushButton("✖ Retirer")
        self.remove_btn.setProperty("role", "ghost")
        ll.addWidget(self.add_btn)
        ll.addWidget(self.mount_btn)
        ll.addWidget(self.remove_btn)
        self.empty = make_label("Aucune entité. Ajoutez un familier, un compagnon de classe, une invocation ou une "
                                "monture.",
                                "muted", wrap=True)
        ll.addWidget(self.empty)
        left.setMinimumWidth(240)
        split.addWidget(left)

        # ---------------- mini-fiche
        self.sheet_scroll = QScrollArea()
        self.sheet_scroll.setWidgetResizable(True)
        self.sheet_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.sheet = QWidget()
        self.sheet_lay = QVBoxLayout(self.sheet)
        self.sheet_scroll.setWidget(self.sheet)
        split.addWidget(self.sheet_scroll)
        split.setSizes([280, 900])

        self.add_btn.clicked.connect(self._on_add)
        self.mount_btn.clicked.connect(lambda _=False: self._on_add("mount"))
        self.remove_btn.clicked.connect(self._on_remove)
        self.list.currentRowChanged.connect(self._on_select)
        self._uids: list[str] = []
        self.current_uid = ""
        self.w: dict = {}

    # ------------------------------------------------------------------ ménagerie
    def _on_add(self, start_type: str = "", recommended=None):
        eng = self.engine
        rec = recommended if recommended is not None else eng.recommended_entities()
        if not start_type:
            types = {eng.entity(i)["entity_type"] for i in rec if eng.entity(i)}
            start_type = ("class_companion" if "class_companion" in types else "mount" if types == {"mount"}
                          else "familiar")
        eid = pick_entity(self.win, eng, start_type, rec)
        if eid:
            inst = eng.menagerie_add(eid)
            self.current_uid = inst["uid"]
            self.changed()

    def _on_remove(self):
        if self.current_uid:
            self.engine.menagerie_remove(self.current_uid)
            self.current_uid = ""
            self.changed()

    def _on_select(self, row: int):
        if 0 <= row < len(self._uids):
            self.current_uid = self._uids[row]
            self._build_sheet()

    def _inst(self):
        return self.engine.menagerie_get(self.current_uid)

    # ------------------------------------------------------------------ rafraîchissement
    def refresh(self):
        eng, ch = self.engine, self.ch
        clear_layout(self.hints_box)
        for h in eng.companion_hints():
            row = QHBoxLayout()
            lab = make_label(("⚠ " if h["niveau"] == "warning" else "✦ ") + h["texte"],
                             "warn" if h["niveau"] == "warning" else "head", wrap=True)
            btn = QPushButton("Voir les recommandés ★")
            btn.clicked.connect(lambda _=False, ids=tuple(h["recommandes"]): self._on_add(
                eng.entity(ids[0])["entity_type"], set(ids)))
            row.addWidget(lab, 1)
            row.addWidget(btn)
            box = QWidget()
            box.setLayout(row)
            self.hints_box.addWidget(box)
        self._uids = [m["uid"] for m in ch.menagerie]
        if self.current_uid not in self._uids:
            self.current_uid = self._uids[0] if self._uids else ""
        with blocked(self.list):
            self.list.clear()
            for m in ch.menagerie:
                ent = eng.entity(m["id"]) or {}
                sh = eng.entity_sheet(m)
                it = QListWidgetItem("{} {}{} — PV {}/{}{}".format(
                    TYPE_ICONS.get(ent.get("entity_type"), "•"), m.get("nom") or ent.get("name", "?"),
                    "" if m.get("nom") == ent.get("name") else " ({})".format(ent.get("name", "")),
                    m.get("pv"), sh["pv_max"], "" if m.get("statut", "Actif") == "Actif" else " — " + m["statut"]))
                it.setToolTip(rich_tip(ent.get("name", ""), "Ajouté automatiquement (aptitude de classe)."
                                       if m.get("auto") else C.TYPE_LABELS.get(ent.get("entity_type"), "")))
                self.list.addItem(it)
            if self.current_uid:
                self.list.setCurrentRow(self._uids.index(self.current_uid))
        self.empty.setVisible(not self._uids)
        self.remove_btn.setEnabled(bool(self.current_uid))
        self._build_sheet()

    # ------------------------------------------------------------------ mini-fiche
    def _build_sheet(self):
        clear_layout(self.sheet_lay)
        self.w = {}
        inst = self._inst()
        if inst is None:
            self.sheet_lay.addWidget(make_label("Sélectionnez une entité de la ménagerie.", "muted"))
            self.sheet_lay.addStretch(1)
            return
        eng, t = self.engine, theme.current()
        sh = eng.entity_sheet(inst)
        ent = sh["entite"]

        # en-tête : nom personnalisable, statut, niveau du sort
        head = QGroupBox("{} {}".format(TYPE_ICONS.get(ent.get("entity_type"), "•"), ent.get("name", "")))
        hl = QGridLayout(head)
        self.w["name"] = QLineEdit(inst.get("nom") or "")
        self.w["name"].setPlaceholderText("Nom personnalisé…")
        self.w["name"].editingFinished.connect(self._on_rename)
        hl.addWidget(make_label("Nom"), 0, 0)
        hl.addWidget(self.w["name"], 0, 1)
        self.w["status"] = QComboBox()
        self.w["status"].addItems(C.STATUSES)
        self.w["status"].setCurrentIndex(max(0, C.STATUSES.index(inst.get("statut", "Actif"))
                                             if inst.get("statut", "Actif") in C.STATUSES else 0))
        self.w["status"].activated.connect(self._on_status)
        hl.addWidget(make_label("Statut"), 0, 2)
        hl.addWidget(self.w["status"], 0, 3)
        sub = "{} {} — {} — FP {} — source : {}".format(ent.get("type", ""), sh["taille"].lower(),
                                                       ent.get("alignment", ""), ent.get("cr") or "—",
                                                       ent.get("source", ""))
        hl.addWidget(make_label(sub, "muted", wrap=True), 1, 0, 1, 4)
        if sh["niveau_sort_min"]:
            self.w["spell"] = QSpinBox()
            self.w["spell"].setRange(sh["niveau_sort_min"], 9)
            self.w["spell"].setValue(int(inst.get("niveau_sort") or sh["niveau_sort_min"]))
            self.w["spell"].setPrefix("Sort de niveau ")
            self.w["spell"].valueChanged.connect(self._on_spell_level)
            hl.addWidget(make_label("Convoqué avec"), 2, 0)
            hl.addWidget(self.w["spell"], 2, 1)
        ctx = sh["contexte"]
        if ctx:
            scale = ("Mise à l'échelle : BM +{} — niveau de classe {} — mod. {:+d} — attaque de sort {:+d} — DD {}"
                     .format(ctx["BM"], ctx["class_level"], ctx["ability_mod"], ctx["spell_attack_modifier"],
                             ctx["spell_save_dc"]))
            if "spell_level" in ctx:
                scale += " — niveau du sort {}".format(ctx["spell_level"])
            hl.addWidget(make_label(scale, "muted", wrap=True), 3, 0, 1, 4)
        self.sheet_lay.addWidget(head)

        # défense : CA, PV (jauge + compteurs), vitesses, perception passive
        dfn = QGroupBox("Défense et déplacement")
        dl = QGridLayout(dfn)
        ca = make_label("🛡 CA {}".format(sh["ca"]), "badge")
        ca.setToolTip(rich_tip("Classe d'armure", sh["ca_note"] or "Valeur du profil."))
        dl.addWidget(ca, 0, 0)
        self.w["gauge"] = GaugeBar(height=26, text_color="#000000")      # texte noir contrasté sur la jauge
        self.w["gauge"].set_state(sh["pv_max"], sh["pv_max"] - int(inst.get("pv") or 0))
        self.w["gauge"].changed.connect(self._on_gauge)
        dl.addWidget(self.w["gauge"], 0, 1, 1, 3)
        self.w["hp"] = QSpinBox()
        self.w["hp"].setRange(0, sh["pv_max"])
        self.w["hp"].setValue(int(inst.get("pv") or 0))
        self.w["hp"].setPrefix("PV ")
        self.w["hp"].setSuffix(" / {}".format(sh["pv_max"]))
        self.w["hp"].valueChanged.connect(self._on_hp)
        self.w["tmp"] = QSpinBox()
        self.w["tmp"].setRange(0, 999)
        self.w["tmp"].setValue(int(inst.get("pv_temp") or 0))
        self.w["tmp"].setPrefix("PV temp. ")
        self.w["tmp"].valueChanged.connect(self._on_tmp)
        dl.addWidget(self.w["hp"], 1, 1)
        dl.addWidget(self.w["tmp"], 1, 2)
        if sh["pv_temp_sort"]:
            dl.addWidget(make_label("PV temporaires conférés : {}".format(sh["pv_temp_sort"]), "muted"), 1, 3)
        speeds = " · ".join("{} {}".format(k, v) for k, v in sh["vitesses"].items())
        dl.addWidget(make_label("🦶 " + (speeds or "—"), "head", wrap=True), 2, 0, 1, 3)
        dl.addWidget(make_label("👁 Perception passive {}".format(sh["perception_passive"] or "—"), "muted"), 2, 3)
        for c, stretch in enumerate((0, 2, 2, 2)):
            dl.setColumnStretch(c, stretch)
        dl.setHorizontalSpacing(12)
        self.sheet_lay.addWidget(dfn)

        # caractéristiques : test (clic sur la carte) et sauvegarde (bouton JS)
        abil = QGroupBox("Caractéristiques — cliquez pour un test, « JS » pour une sauvegarde")
        al = QGridLayout(abil)
        for col, (ab, val) in enumerate(sh["stats"].items()):
            card = QPushButton("{}\n{}  ({})".format(ABBR[ab], val, R.fmt_bonus(sh["tests"][ab])))
            card.setProperty("role", "attune")
            card.setMinimumHeight(54)
            card.setToolTip(rich_tip(ab, "Test : d20 {} — Sauvegarde : d20 {}".format(
                R.fmt_bonus(sh["tests"][ab]), R.fmt_bonus(sh["sauvegardes"][ab]))))
            card.clicked.connect(lambda _=False, a=ab: roll_dice(self.win, eng.entity_check_spec(self._inst(), a)))
            save = QPushButton("JS {}".format(R.fmt_bonus(sh["sauvegardes"][ab])))
            save.setProperty("role", "toggle")
            save.clicked.connect(lambda _=False, a=ab: roll_dice(self.win, eng.entity_check_spec(self._inst(), a, True)))
            al.addWidget(card, 0, col)
            al.addWidget(save, 1, col)
        self.sheet_lay.addWidget(abil)

        # compétences, sens, langues, résistances
        info = QGroupBox("Compétences et sens")
        il = QVBoxLayout(info)
        chips = QHBoxLayout()
        for skill, bonus in sh["competences"].items():
            chips.addWidget(ActionChip("🎲", "{} {}".format(skill, R.fmt_bonus(bonus)),
                                       "<qt><b>{}</b><br/>Clic : jet de d20 {}</qt>".format(html.escape(skill),
                                                                                           R.fmt_bonus(bonus)),
                                       on_click=lambda s=skill: roll_dice(self.win, eng.entity_skill_spec(
                                           self._inst(), s))))
        if not sh["competences"]:
            chips.addWidget(make_label("Aucune compétence particulière.", "muted"))
        chips.addStretch(1)
        il.addLayout(chips)
        lines = [("Sens", ent.get("senses")), ("Langues", ent.get("languages")),
                 ("Résistances", ", ".join(ent.get("damage_resistances") or [])),
                 ("Immunités", ", ".join((ent.get("damage_immunities") or []) + (ent.get("condition_immunities") or []))),
                 ("Vulnérabilités", ", ".join(ent.get("damage_vulnerabilities") or []))]
        for label, val in lines:
            if val:
                il.addWidget(make_label("<b>{}</b> : {}".format(label, html.escape(str(val))), wrap=True))
        self.sheet_lay.addWidget(info)

        # traits (infobulles)
        if sh["traits"]:
            tr = QGroupBox("Traits et aptitudes — survolez pour le détail")
            tl = QGridLayout(tr)
            for n, trait in enumerate(sh["traits"]):
                tl.addWidget(ActionChip("◈", trait["name"], "<div style='max-width:380px'><b>{}</b><p>{}</p></div>"
                                        .format(html.escape(trait["name"]), html.escape(trait["description"]))),
                             n // 3, n % 3)
            self.sheet_lay.addWidget(tr)

        # actions : grille alignée (une cellule = un conteneur centré verticalement, même hauteur pour chaque ligne)
        # Action | Type | Toucher (d20 + bonus) | Dégâts (dé + formule + type) | Supplément | Sauvegarde
        acts = QGroupBox("Actions{}".format(" — {} attaques par Attaques multiples".format(sh["attaques_multiples"])
                                             if sh["attaques_multiples"] else ""))
        gl = QGridLayout(acts)
        gl.setHorizontalSpacing(14)
        gl.setVerticalSpacing(6)
        for c, h in enumerate(["Action", "Type", "Toucher", "Dégâts", "Supplément", "Sauvegarde"]):
            gl.addWidget(make_label(h, "head"), 0, c, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.w["actions"] = []
        for r, a in enumerate(sh["actions"], start=1):
            name = make_label(a["name"], "head")
            name.setToolTip(rich_tip(a["name"], a.get("description", "")))
            kind = make_label({"bonus_action": "Action bonus", "reaction": "Réaction"}.get(a.get("activation"), "Action")
                              + (" — {}".format(a["uses"]) if a.get("uses") else ""), "muted", wrap=True)
            row = {"name": name}
            cells = [name, kind]
            if a.get("attack_type") not in (None, "none"):
                btn = d20_button("Attaque : " + a["name"])
                btn.clicked.connect(lambda _=False, act=a: roll_dice(self.win, eng.entity_attack_spec(self._inst(), act)))
                bonus = make_label(R.fmt_bonus(int(a.get("attack_bonus") or 0)), "head")
                bonus.setMinimumWidth(30)
                cells.append(_cell(btn, bonus))
                row["d20"] = btn
            else:
                cells.append(_dash())
            if a.get("damage_dice"):
                dmg = DamageLabel(str(a["damage_dice"]), "head")
                dmg.set_formula(str(a["damage_dice"]))
                dmg.clicked.connect(lambda act=a: roll_damage_dialog(self.win, D.DamageSpec(
                    "{} — {}".format(sh["nom"], act["name"]), str(act["damage_dice"]), (act.get("damage_type") or "").lower())))
                cells.append(_cell(_die(str(a["damage_dice"])), dmg, make_label((a.get("damage_type") or "").lower(),
                                                                               "muted")))
                row["dmg"] = dmg
            else:
                cells.append(_dash())
            if a.get("extra_damage_dice"):
                extra = DamageLabel("+" + str(a["extra_damage_dice"]), "head")
                extra.set_formula(str(a["extra_damage_dice"]))
                extra.clicked.connect(lambda act=a: roll_damage_dialog(self.win, D.DamageSpec(
                    "{} — {} (supplément)".format(sh["nom"], act["name"]), str(act["extra_damage_dice"]),
                    (act.get("extra_damage_type") or "").lower())))
                cells.append(_cell(_die(str(a["extra_damage_dice"])), extra,
                                   make_label((a.get("extra_damage_type") or "").lower(), "muted")))
            else:
                cells.append(_dash())
            if a.get("save"):
                sv = a["save"]
                save_lab = make_label("JS {} DD {}".format(sv.get("ability", ""), sv.get("dc", "?")), "warn")
                save_lab.setToolTip(rich_tip("Sauvegarde", "Réussite : " + str(sv.get("on_success") or "—")))
                cells.append(save_lab)
            else:
                cells.append(_dash())
            for c, wdg in enumerate(cells):
                gl.addWidget(wdg, r, c, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                gl.setRowMinimumHeight(r, 34)
            self.w["actions"].append(row)
        for c, stretch in enumerate((3, 2, 1, 2, 2, 2)):
            gl.setColumnStretch(c, stretch)
        self.sheet_lay.addWidget(acts)

        # réactions
        if sh["reactions"]:
            rb = QGroupBox("Réactions")
            rl = QVBoxLayout(rb)
            for re_ in sh["reactions"]:
                lab = make_label("⚡ <b>{}</b> — {}".format(html.escape(re_["name"]), html.escape(re_.get("description", ""))),
                                 wrap=True)
                rl.addWidget(lab)
            self.sheet_lay.addWidget(rb)

        # convocation : durée, contrôle, sources
        si = ent.get("summon_info") or {}
        if si:
            sb = QGroupBox("Convocation et contrôle")
            sl = QVBoxLayout(sb)
            sl.addWidget(make_label("<b>Durée</b> : {}{}".format(html.escape(si.get("duration", "—")),
                                                                 " — concentration" if si.get("concentration") else ""),
                                    wrap=True))
            sl.addWidget(make_label("<b>Contrôle</b> : " + html.escape(si.get("control", "—")), wrap=True))
            for src in si.get("sources", []):
                sl.addWidget(make_label("• <b>{}</b> (niv. {}) — {}".format(
                    html.escape(src["name"]), src.get("level_min") or "—", html.escape(src.get("notes", ""))),
                    "muted", wrap=True))
            self.sheet_lay.addWidget(sb)
        self.sheet_lay.addStretch(1)

    # ------------------------------------------------------------------ éditions
    def _on_rename(self):
        inst = self._inst()
        if inst is not None:
            inst["nom"] = self.w["name"].text().strip() or (self.engine.entity(inst["id"]) or {}).get("name", "")
            self.win.light_changed()
            self.refresh()

    def _on_status(self, _=0):
        inst = self._inst()
        if inst is not None:
            inst["statut"] = self.w["status"].currentText()
            self.win.light_changed()
            self.refresh()

    def _on_spell_level(self, value: int):
        inst = self._inst()
        if inst is not None:
            inst["niveau_sort"] = int(value)
            inst["pv"] = self.engine.entity_sheet(inst)["pv_max"]      # nouvelle convocation : PV pleins
            self.changed()

    def _on_hp(self, value: int):
        inst = self._inst()
        if inst is not None:
            inst["pv"] = int(value)
            top = self.engine.entity_sheet(inst)["pv_max"]
            self.w["gauge"].set_state(top, top - int(value))
            if value == 0 and inst.get("statut") == "Actif":
                inst["statut"] = "À 0 PV"
            self.win.light_changed()

    def _on_tmp(self, value: int):
        inst = self._inst()
        if inst is not None:
            inst["pv_temp"] = int(value)
            self.win.light_changed()

    def _on_gauge(self, used: int):
        inst = self._inst()
        if inst is not None:
            top = self.engine.entity_sheet(inst)["pv_max"]
            with blocked(self.w["hp"]):
                self.w["hp"].setValue(top - used)
            self._on_hp(top - used)
