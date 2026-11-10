"""Onglet « Caractéristiques » : génération (achat de points / 4d6 / manuel), bonus raciaux, modificateurs."""
from __future__ import annotations

from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QPushButton,
                             QSpinBox, QVBoxLayout, QWidget)

from core import rules as R
from core.rules import ABILITIES, norm
from . import theme
from .dice_dialog import d20_button, roll_dice
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
        for b in (self.roll_btn, self.auto_btn, self.reset_btn):
            top.addWidget(b)
        top.addStretch(1)
        self.points_label = make_label("", "stat")
        top.addWidget(self.points_label)
        root.addLayout(top)
        self.rolls_label = make_label("", "muted", wrap=True)
        root.addWidget(self.rolls_label)

        # ---------------- six cartes côte à côte : FOR DEX CON INT SAG CHA
        box = QGroupBox("Caractéristiques")
        cards = QGridLayout(box)
        cards.setHorizontalSpacing(10)
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
            top_row.addWidget(make_label(R.ABBR.get(ab, ab[:3].upper()), "abbr"))
            top_row.addStretch(1)
            w["d20"] = d20_button("Test de " + ab)
            w["d20"].clicked.connect(lambda _=False, a=ab: roll_dice(self.win, self.engine.ability_check_spec(a)))
            top_row.addWidget(w["d20"])
            cl.addLayout(top_row)
            cl.addWidget(make_label(ab, "muted"))
            # v49 : badge de recommandation selon la classe / la sous-classe visée (infobulle : pourquoi)
            w["badge"] = make_label("", "head", align=CENTER)
            cl.addWidget(w["badge"])
            # valeur finale + modificateur
            cl.addWidget(w["total"])
            mod_row = QHBoxLayout()
            mod_row.addStretch(1)
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
            gen_lay.addWidget(w["cost"])
            cl.addWidget(gen)
            # bonus : race | améliorations / dons | divers — compacts, côte à côte
            parts = QGridLayout()
            parts.setHorizontalSpacing(6)
            parts.setVerticalSpacing(2)
            for c, (h, tip) in enumerate((("Race", "Bonus racial (race, sous-race, bonus libres)"),
                                          ("Amél.", "Améliorations de caractéristiques et dons"),
                                          ("Divers", "Ajustement manuel (objet, bénédiction du MJ…)"))):
                lab = make_label(h, "abpart", align=CENTER)
                lab.setToolTip(tip)
                parts.addWidget(lab, 0, c)
            parts.addWidget(w["race"], 1, 0)
            parts.addWidget(w["asi"], 1, 1)
            parts.addWidget(w["misc"], 1, 2)
            for c in range(3):
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
        for lab, cb in zip(self.free_labels, self.free_combos):
            free.addWidget(lab)
            free.addWidget(cb)
        free.addStretch(1)
        rl.addLayout(free)
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
    def refresh(self):
        self.mark_box(self.racial_bonus_box, "Bonus raciaux de caractéristiques", "caracteristiques",
                      "Bonus raciaux de caractéristiques")
        ch, eng = self.ch, self.engine
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
            w["cost"].setText("Coût : {} pt{}".format(R.POINT_BUY_COST[score], "s" if R.POINT_BUY_COST[score] > 1
                                                       else "") if m == "achat" else "")
            w["cost"].setVisible(m == "achat")
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
        self.free_chk.setEnabled(not rule["libre_regle"] or ch.regle_libre)
        sub = eng.subrace()
        if rule["libre_regle"]:
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
                allowed = [ab for ab in ABILITIES if (rule["libre_regle"] or ab not in rule["fixe"]) and ab not in others]
                fill_combo(cb, ["—"] + allowed, picks[i] if picks[i] in allowed else "—")

        warns = [w for w in eng.warnings() if any(k in w for k in ("Budget", "valeurs", "bonus raciaux", "Multiclassage",
                                                                   "doit être"))]
        self.warn.setText("\n".join("⚠ " + w for w in warns))
