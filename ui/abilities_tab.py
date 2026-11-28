"""Onglet « Caractéristiques » : génération (achat de points / 4d6 / manuel), bonus raciaux, modificateurs."""
from __future__ import annotations

from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QPushButton,
                             QSpinBox, QVBoxLayout, QWidget)

from core import rules as R
from core.rules import ABILITIES, norm
from . import theme
from .dice_dialog import d20_button, retain_when_hidden, roll_dice
from .common import CENTER, BaseTab, blocked, calc_tip, center, fill_combo, hline, make_label, rich_tip

METHODS = {"Achat de points (27 points)": "achat", "Tirage de dés (4d6, on garde les 3 plus hauts)": "des",
           "Saisie manuelle": "manuel"}
NONE_LABEL = "— non assignée —"


class AbilitiesTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        root = QVBoxLayout(self)

        # ---------------- méthode
        top = QHBoxLayout()
        self.method = QComboBox()
        self.method.addItems(list(METHODS))
        top.addWidget(make_label("Méthode de génération", "title"))
        top.addWidget(self.method)
        self.roll_btn = QPushButton("🎲 Lancer 6 × 4d6")
        self.auto_btn = QPushButton("Assigner automatiquement")
        self.reset_btn = QPushButton("Réinitialiser (8 partout)")
        self.reset_btn.setToolTip(rich_tip("Réinitialiser", "Remet toutes les valeurs à leur minimum et rend "
                                           "les 27 points."))
        self.points_label = make_label("", "head")       # v53 : à côté du menu déroulant (moins de hauteur)
        top.addSpacing(12)
        top.addWidget(self.points_label)
        top.addStretch(1)
        root.addLayout(top)
        btns = QHBoxLayout()                             # v53 : boutons sur leur ligne (rien ne sort à droite)
        for b in (self.roll_btn, self.auto_btn, self.reset_btn):
            btns.addWidget(b)
        btns.addStretch(1)
        root.addLayout(btns)
        self._top_row = top
        self.rolls_label = make_label("", "muted", wrap=True)
        root.addWidget(self.rolls_label)

        # ---------------- six cartes côte à côte : FOR DEX CON INT SAG CHA
        box = QGroupBox("Caractéristiques")
        cards = QGridLayout(box)
        cards.setHorizontalSpacing(10)
        self._cards_grid = cards
        self.rows: dict[str, dict] = {}
        for col, ab in enumerate(ABILITIES):
            w = {"buy": QWidget(), "minus": QPushButton("−"), "plus": QPushButton("+"), "value": center("8", "stat"),
                 "roll": QComboBox(), "manual": QSpinBox(), "misc": QSpinBox(),
                 "cost": center("", "abpart"), "race": center(), "asi": center(), "total": center("", "abtotal"),
                 "mod": center("", "abmod"), "card": QFrame()}
            card = w["card"]
            card.setProperty("role", "abcard")
            card.setMinimumWidth(150)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(8, 4, 8, 6)                # v51 : cartes légèrement moins hautes
            cl.setSpacing(2)
            # en-tête : abréviation + dé de test (taille fixe, toujours au même endroit)
            top_row = QHBoxLayout()
            top_row.setSpacing(6)
            from .ability_icons import icon_button, icon_label   # v53 : symbole (plus grand), cliquable = test
            if getattr(self.win, "no_dice", False) is True:
                top_row.addWidget(icon_label(ab, 44))
            else:
                top_row.addWidget(icon_button(ab, 44, self._roll_check))
            names = QVBoxLayout()                         # v53 : abréviation + badge, puis nom, sur l'en-tête
            names.setSpacing(0)
            abbr_row = QHBoxLayout()
            abbr_row.setSpacing(6)
            abbr_row.addWidget(make_label(R.ABBR.get(ab, ab[:3].upper()), "abbr"))
            # v49 : badge de recommandation selon la classe / la sous-classe visée (infobulle : pourquoi)
            w["badge"] = make_label("", "head")
            abbr_row.addWidget(w["badge"])
            abbr_row.addStretch(1)
            names.addLayout(abbr_row)
            names.addWidget(make_label(ab, "muted"))
            top_row.addLayout(names, 1)
            w["d20"] = d20_button("Test de " + ab)
            w["d20"].clicked.connect(lambda _=False, a=ab: roll_dice(self.win, self.engine.ability_check_spec(a)))
            top_row.addWidget(w["d20"])
            if getattr(self.win, "no_dice", False) is True:   # v52 : assistant de création — pas de jet de dés
                retain_when_hidden(w["d20"], True)
                w["d20"].setVisible(False)
            cl.addLayout(top_row)
            # valeur finale + modificateur, sur la même ligne (v53 : carte moins haute)
            mod_row = QHBoxLayout()
            mod_row.addStretch(1)
            mod_row.addWidget(w["total"])
            mod_row.addSpacing(8)
            mod_row.addWidget(w["mod"])
            mod_row.addStretch(1)
            cl.addLayout(mod_row)
            cl.addWidget(hline())
            # génération : achat de points (− valeur +) / tirage / saisie — un seul visible, même emplacement
            buy_lay = QHBoxLayout(w["buy"])
            buy_lay.setContentsMargins(0, 0, 0, 0)
            buy_lay.setSpacing(4)
            for key in ("minus", "plus"):
                w[key].setProperty("role", "step")
                w[key].setFixedWidth(34)
            buy_lay.addWidget(w["minus"])
            buy_lay.addWidget(w["value"], 1)
            buy_lay.addWidget(w["plus"])
            w["manual"].setRange(1, 30)
            w["misc"].setRange(-10, 10)
            gen = QWidget()
            gen_lay = QVBoxLayout(gen)
            gen_lay.setContentsMargins(0, 0, 0, 0)
            for key in ("buy", "roll", "manual"):
                gen_lay.addWidget(w[key])
            cl.addWidget(gen)
            # bonus : race | améliorations / dons | divers — compacts, côte à côte
            parts = QGridLayout()
            parts.setHorizontalSpacing(6)
            parts.setVerticalSpacing(2)
            for c, (h, tip) in enumerate((("Coût", "Points dépensés pour cette valeur (achat de points)"),
                                          ("Race", "Bonus racial (race, sous-race, bonus libres)"),
                                          ("Amél.", "Améliorations de caractéristiques et dons"),
                                          ("Divers", "Ajustement manuel (objet, bénédiction du MJ…)"))):
                lab = make_label(h, "abpart", align=CENTER)
                lab.setToolTip(tip)
                parts.addWidget(lab, 0, c)
            parts.addWidget(w["cost"], 1, 0)              # v53 : coût dans la ligne des bonus
            parts.addWidget(w["race"], 1, 1)
            parts.addWidget(w["asi"], 1, 2)
            parts.addWidget(w["misc"], 1, 3)
            for c in range(4):
                parts.setColumnStretch(c, 1)
            cl.addLayout(parts)
            cards.addWidget(card, 0, col)
            cards.setColumnStretch(col, 1)
            w["minus"].clicked.connect(lambda _=False, a=ab: self._on_buy(a, -1))
            w["plus"].clicked.connect(lambda _=False, a=ab: self._on_buy(a, +1))
            w["manual"].valueChanged.connect(lambda v, a=ab: self._on_manual(a, v))
            w["misc"].valueChanged.connect(lambda v, a=ab: self._on_misc(a, v))
            w["roll"].activated.connect(lambda i, a=ab: self._on_roll_assign(a))
            self.rows[ab] = w
        root.addWidget(box)

        # ---------------- bonus raciaux
        # v53 : onglet Caractéristiques en Mode libre — encart replié quand rien n'est à choisir (page sans défilement)
        self.compact_racial = False
        self._racial_open = False
        self.racial_toggle = QPushButton("▸ Bonus raciaux de caractéristiques")
        self.racial_toggle.setProperty("role", "ghost")
        self.racial_toggle.setToolTip(rich_tip("Bonus raciaux", "Afficher l'encart des bonus raciaux (règle libre "
                                               "« +2 / +1 », variante +1 / +1 / +1)."))
        self.racial_toggle.clicked.connect(self._open_racial)
        self.racial_toggle.setVisible(False)
        btns.insertWidget(btns.count() - 1, self.racial_toggle)
        rbox = self.racial_bonus_box = QGroupBox("Bonus raciaux de caractéristiques")
        rl = QVBoxLayout(rbox)
        self.race_info = make_label("", wrap=True)
        rl.addWidget(self.race_info)
        free = QHBoxLayout()
        self.free_chk = QCheckBox("Règle libre « +2 / +1 au choix » (origine personnalisée)")
        self.alt_chk = QCheckBox("Variante +1, +1, +1")
        self.free_combos: list[QComboBox] = [QComboBox(), QComboBox(), QComboBox()]
        self.free_labels = [make_label("+2"), make_label("+1"), make_label("+1")]
        free.addWidget(self.free_chk)
        free.addWidget(self.alt_chk)
        free.addStretch(1)
        rl.addLayout(free)
        picks = QHBoxLayout()                            # v53 : listes sur leur propre ligne, noms entiers
        for lab, cb in zip(self.free_labels, self.free_combos):
            try:
                cb.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
                cb.setMinimumWidth(160)
            except (AttributeError, TypeError):
                pass
            picks.addWidget(lab)
            picks.addWidget(cb)
        picks.addStretch(1)
        rl.addLayout(picks)
        root.addWidget(rbox)

        self.warn = make_label("", "warn", wrap=True)
        root.addWidget(self.warn)
        root.addStretch(1)

        # ---------------- connexions
        self.method.activated.connect(self._on_method)
        self.roll_btn.clicked.connect(self._on_roll)
        self.auto_btn.clicked.connect(self._on_auto)
        self.reset_btn.clicked.connect(self._on_reset)
        self.free_chk.toggled.connect(self._on_free_rule)
        self.alt_chk.toggled.connect(self._on_alt_rule)
        for i, cb in enumerate(self.free_combos):
            cb.activated.connect(lambda _=0, k=i: self._on_free_pick(k))

    def _roll_check(self, ab: str) -> None:
        roll_dice(self.win, self.engine.ability_check_spec(ab))

    def set_columns(self, n: int) -> None:
        """v53 : cartes sur n colonnes (assistant de création : 3 × 2, sans défilement horizontal)."""
        for i, ab in enumerate(ABILITIES):
            card = self.rows[ab]["card"]
            self._cards_grid.removeWidget(card)
            self._cards_grid.addWidget(card, i // n, i % n)
        for c in range(6):
            self._cards_grid.setColumnStretch(c, 1 if c < n else 0)

    def _apply_guided_locks(self) -> None:
        """v52 : Mode guidé — valeurs de base et bonus raciaux fixés à la création ; seul un choix manquant
        (tirage à assigner, bonus libre à attribuer) reste modifiable. Le bonus « divers » reste libre."""
        guided = self.guided
        rolls_open = not guided or self.engine.missing_in("caracteristiques", "Caractéristiques") > 0
        picks_open = not guided or self.engine.missing_in("caracteristiques", "Bonus raciaux de caractéristiques") > 0
        tip = self.GUIDED_TIP if guided else ""
        no_rolls = not self.ch.des_tirages               # Mode guidé : lancer une seule fois, jamais relancer
        for w in (self.method, self.roll_btn, self.auto_btn, self.reset_btn):
            open_ = (w is self.roll_btn and rolls_open and no_rolls) or (w is self.auto_btn and rolls_open)
            w.setEnabled(not guided or open_)
            w.setToolTip(tip)
        for row in self.rows.values():
            for k in ("minus", "plus", "manual"):
                if guided:
                    row[k].setEnabled(False)
                row[k].setToolTip(tip or row[k].toolTip())
            row["roll"].setEnabled(rolls_open)
        if guided:
            self.free_chk.setEnabled(False)
            self.alt_chk.setEnabled(picks_open)
        for cb in self.free_combos:
            cb.setEnabled(picks_open)

    # ------------------------------------------------------------------ handlers
    def _on_method(self, _=0):
        self.ch.methode = METHODS[self.method.currentText()]
        self.changed()

    def _on_buy(self, ab: str, delta: int):
        """Point Buy : un cran de plus ou de moins, validé par le moteur (valeurs 8-15, budget de 27 points)."""
        self.engine.buy_step(ab, delta)
        self.changed()

    def _on_manual(self, ab: str, value: int):
        self.ch.scores_manuel[ab] = value
        self.changed()

    def _on_misc(self, ab: str, value: int):
        self.ch.bonus_divers[ab] = value
        self.changed()

    def _on_reset(self):
        """Remet les valeurs de la méthode active à leur base (Point Buy : 8 partout, 27 points restants)."""
        self.engine.reset_scores()
        self.changed()

    def _on_roll(self):
        rolls = R.roll_ability_set()
        self.ch.des_tirages = [{"total": t, "des": d} for t, d in rolls]
        self.ch.des_affectation = {ab: -1 for ab in ABILITIES}
        self.ch.methode = "des"
        self._on_auto()

    def _priority(self) -> list[str]:
        """Ordre d'assignation : caractéristiques principales de la 1re classe, puis Constitution, puis le reste."""
        main = self.db.classes.get(self.engine.first_class(), {}).get("carac_principale", "")
        order = [ab for ab in ABILITIES if norm(ab) in norm(main)]
        for ab in ("Constitution", "Dextérité", "Sagesse", "Charisme", "Intelligence", "Force"):
            if ab not in order:
                order.append(ab)
        return order

    def _on_auto(self):
        if not self.ch.des_tirages:
            self.changed()
            return
        ranked = sorted(range(len(self.ch.des_tirages)), key=lambda i: -self.ch.des_tirages[i]["total"])
        self.ch.des_affectation = {ab: ranked[k] for k, ab in enumerate(self._priority())}
        self.changed()

    def _on_roll_assign(self, ab: str):
        idx = self.rows[ab]["roll"].currentIndex() - 1     # 0 = « non assignée »
        for other, v in list(self.ch.des_affectation.items()):
            if other != ab and idx >= 0 and v == idx:
                self.ch.des_affectation[other] = self.ch.des_affectation.get(ab, -1)  # échange
        self.ch.des_affectation[ab] = idx
        self.changed()

    def _on_free_rule(self, checked: bool):
        self.ch.regle_libre = checked
        self.ch.bonus_libres = []
        self.changed()

    def _on_alt_rule(self, checked: bool):
        """Bascule entre « +2, +1 » et la variante « +1, +1, +1 » (races à bonus libres)."""
        self.ch.bonus_alt = checked
        self.ch.bonus_libres = []
        self.changed()

    def _on_free_pick(self, k: int):
        picks = list(self.ch.bonus_libres) + [""] * 3
        text = self.free_combos[k].currentText()
        picks[k] = "" if text == "—" else text
        self.ch.bonus_libres = picks[:3]
        self.changed()

    # ------------------------------------------------------------------ rafraîchissement
    def set_compact_layout(self) -> None:
        """v53 : onglet Caractéristiques (Mode libre) — bonus raciaux repliés, boutons sur la ligne de la méthode,
        pour tenir sans défilement en 16:9. L'assistant de création garde sa mise en page."""
        self.compact_racial = True
        top = self._top_row
        for b in (self.roll_btn, self.auto_btn, self.reset_btn, self.racial_toggle):
            top.insertWidget(top.count() - 1, b)

    def _open_racial(self) -> None:
        self._racial_open = not self._racial_open
        self.refresh()

    def refresh(self):
        pending = self.mark_box(self.racial_bonus_box, "Bonus raciaux de caractéristiques", "caracteristiques",
                                "Bonus raciaux de caractéristiques")
        ch, eng = self.ch, self.engine
        if self.compact_racial:                          # v53 : replié s'il n'y a rien à choisir (Mode libre)
            self.layout().setSpacing(4)
            show = bool(pending) or self._racial_open
            self.racial_bonus_box.setVisible(show)
            self.racial_toggle.setVisible(not pending)
            self.racial_toggle.setText(("▾ " if show else "▸ ") + "Bonus raciaux de caractéristiques")
        else:
            self.racial_bonus_box.setVisible(True)
            self.racial_toggle.setVisible(False)
        with blocked(self.method):
            self.method.setCurrentIndex(list(METHODS.values()).index(ch.methode))
        m = ch.methode
        self.roll_btn.setVisible(m == "des")
        self.auto_btn.setVisible(m == "des")
        self.reset_btn.setVisible(m != "des")
        self.reset_btn.setText("Réinitialiser (8 partout)" if m == "achat" else "Réinitialiser (10 partout)")
        self.points_label.setVisible(m == "achat")
        if m == "achat":
            used = R.point_buy_total(ch.scores_achat)
            self.points_label.setText("Points dépensés : {} / {} — restants : {}".format(
                used, R.POINT_BUY_TOTAL, R.point_buy_remaining(ch.scores_achat)))
        if m == "des":
            if ch.des_tirages:
                self.rolls_label.setText("Tirages : " + "   |   ".join(
                    "{} ({})".format(t["total"], "+".join(str(x) for x in t["des"][:3]) + " ~" + str(t["des"][3]))
                    for t in ch.des_tirages))
            else:
                self.rolls_label.setText("Cliquez sur « Lancer 6 × 4d6 » pour générer vos valeurs.")
        else:
            self.rolls_label.setText("")
        self.rolls_label.setVisible(m == "des")

        race, asi = eng.race_bonus(), eng.asi_bonus()
        recs = eng.ability_recommendations()             # v49 : ⭐ principale / ✦ secondaire
        cls = ch.classes[0]["nom"] if ch.classes else ""
        roll_items = [NONE_LABEL] + ["{} (tirage {})".format(t["total"], i + 1) for i, t in enumerate(ch.des_tirages)]
        for ab in ABILITIES:
            w, parts = self.rows[ab], eng.score_parts(ab)
            role, why = recs.get(ab, ("", ""))
            w["badge"].setText({"principale": "⭐ [Principale]", "secondaire": "✦ [Secondaire]"}.get(role, ""))
            w["badge"].setToolTip(rich_tip("{} — caractéristique {} ({})".format(ab, role, cls), why) if role else "")
            w["badge"].setStyleSheet("color: {};".format(theme.current().accent_text if role == "principale" else
                                                          theme.current().ornament) if role else "")
            score = ch.scores_achat[ab]
            w["value"].setText(str(score))
            w["minus"].setEnabled(score > R.POINT_BUY_MIN)
            can_up = R.can_raise(ch.scores_achat, ab)
            w["plus"].setEnabled(can_up)
            w["plus"].setToolTip("" if can_up else (
                "Maximum {} en achat de points.".format(R.POINT_BUY_MAX) if score >= R.POINT_BUY_MAX
                else "Pas assez de points restants ({} nécessaires).".format(
                    R.POINT_BUY_COST[score + 1] - R.POINT_BUY_COST[score])))
            with blocked(w["manual"], w["misc"], w["roll"]):
                w["manual"].setValue(ch.scores_manuel[ab])
                w["misc"].setValue(ch.bonus_divers.get(ab, 0))
            fill_combo(w["roll"], roll_items, roll_items[ch.des_affectation.get(ab, -1) + 1]
                       if ch.des_affectation.get(ab, -1) + 1 < len(roll_items) else NONE_LABEL)
            w["buy"].setVisible(m == "achat")
            w["roll"].setVisible(m == "des")
            w["manual"].setVisible(m == "manuel")
            w["cost"].setText("{} pt{}".format(R.POINT_BUY_COST[score], "s" if R.POINT_BUY_COST[score] > 1
                                               else "") if m == "achat" else "—")
            w["race"].setText(R.fmt_bonus(race[ab]) if race[ab] else "—")
            w["asi"].setText(R.fmt_bonus(asi[ab]) if asi[ab] else "—")
            boosted = parts.get("effets", 0)
            form = eng.form_status() if parts.get("forme") else None
            w["total"].setText(str(parts["total"]) + (" " + form["icone"] if form else " ★" if boosted else ""))
            w["race"].setToolTip("Bonus racial : {}".format(R.fmt_bonus(race[ab]) if race[ab] else "aucun"))
            w["mod"].setText(R.fmt_bonus(R.ability_modifier(parts["total"])))
            rows = [("Base", parts["base"]), ("Race", R.fmt_bonus(parts["race"])),
                    ("Améliorations / dons", R.fmt_bonus(parts["asi"]))]
            if parts["champion"]:
                rows.append(("Champion primitif", "+{}".format(parts["champion"])))
            if parts["divers"]:
                rows.append(("Divers", R.fmt_bonus(parts["divers"])))
            if boosted:
                rows.append(("Sans effet actif", parts.get("sans_effets", parts["total"])))
                rows += [(src, "") for src in parts.get("effets_sources", [])]
            tip = calc_tip(ab, rows, "{} (mod. {})".format(parts["total"], R.fmt_bonus(R.ability_modifier(parts["total"]))),
                           ["★ Valeur modifiée par un effet actif (potion, sort…)."] if boosted else None)
            if form:
                tip = "<qt><b>{} {}</b><br/>{} de la bête : {} (votre valeur est mise de côté).</qt>".format(
                    form["icone"], form["libelle"], ab, parts["total"])
            w["total"].setToolTip(tip)
            w["mod"].setToolTip(tip)

        # bonus raciaux
        rule = eng.race_rule()
        with blocked(self.free_chk):
            self.free_chk.setChecked(ch.regle_libre or rule["libre_regle"])
        self.free_chk.setEnabled((not rule["libre_regle"] or ch.regle_libre) and rule.get("origine") != "historique")
        sub = eng.subrace()
        if rule.get("origine") == "historique":            # v52 : règle 2024
            txt = "Historique {} (2024) : +2 et +1 (ou +1, +1, +1) parmi {}.".format(
                ch.historique, ", ".join(rule["choix"]))
        elif rule["libre_regle"]:
            txt = "{} : aucun bonus fixe dans la base — répartissez +2 et +1 librement.".format(ch.race or "Race")
        else:
            fixed = ", ".join("{} {}".format(a, R.fmt_bonus(v)) for a, v in rule["fixe"].items())
            txt = "{} : {}".format(ch.race, fixed or "aucun bonus fixe")
            if rule["libres"]:
                txt += " + {} bonus libre(s) à répartir".format(len(rule["libres"]))
            if sub:
                txt += " ; sous-race {} : {}".format(sub["nom"], ", ".join(
                    "{} {}".format(a, R.fmt_bonus(v)) for a, v in sub.get("bonus", {}).items()))
        self.race_info.setText(txt)
        picks = list(ch.bonus_libres) + [""] * 3
        can_alt = bool(rule["alternative"]) or rule["libre_regle"]
        self.alt_chk.setVisible(can_alt)
        with blocked(self.alt_chk):
            self.alt_chk.setChecked(ch.bonus_alt and can_alt)
        for i, (lab, cb) in enumerate(zip(self.free_labels, self.free_combos)):
            visible = i < len(rule["libres"])
            lab.setVisible(visible)
            cb.setVisible(visible)
            if visible:
                lab.setText(R.fmt_bonus(rule["libres"][i]))
                # bonus libres : uniquement sur d'AUTRES caractéristiques que les bonus fixes (Demi-elfe : Cha +2 fixe)
                others = {p for j, p in enumerate(picks[:3]) if j != i and p}   # deux caractéristiques DIFFÉRENTES
                allowed = [ab for ab in (rule.get("choix") or ABILITIES)          # v52 : historique 2024
                           if (rule["libre_regle"] or ab not in rule["fixe"]) and ab not in others]
                fill_combo(cb, ["—"] + allowed, picks[i] if picks[i] in allowed else "—")

        self._apply_guided_locks()
        warns = [w for w in eng.warnings() if any(k in w for k in ("Budget", "valeurs", "bonus raciaux", "Multiclassage",
                                                                   "doit être"))]
        self.warn.setText("\n".join("⚠ " + w for w in warns))
        self.warn.setVisible(bool(warns))                # v53 : pas de ligne vide sous les cartes
