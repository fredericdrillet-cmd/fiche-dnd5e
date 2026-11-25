"""
Onglet « Combat » : PV, CA, initiative, armure, armes (actions d'arme façon BG3, munitions), sorts mineurs,
barre d'états actifs (buffs / débuffs / conditions), concentration, réactions du round et repos interactifs.
"""
from __future__ import annotations

import html
import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton,
                             QScrollArea, QSizePolicy, QSpinBox, QToolButton, QVBoxLayout, QWidget)

from core.engine_extras import ExtrasMixin
from core import effects as FX
from core import engine_extras as X
from core import mechanics as M
from core import rules as R
from core import weapon_actions as WA
from core.proficiencies import CAST_BLOCKED, WEAPON_WARNING
from . import theme
from .orbs import GaugeBar, OrbBar
from core import dice as D
from core import durations as D_
from .common import (CENTER, BaseTab, DamageLabel, adv_badge, blocked, no_truncate, calc_tip, center, fill_combo, formula_html,
                     head, hline, make_label, rich_tip)
from .dialogs import ask_choice, ask_int, ask_yes_no
from .dice_dialog import d20_button, d20_icon, die_icon, retain_when_hidden, roll_damage_dialog, roll_dice
from .game_widgets import ActionChip, EffectBadge, clear_layout
from .rest_dialog import run_rest

ALL_CATS = "Toutes les catégories"
NO_AMMO = "— munition ordinaire —"
FX_PER_ROW = 12

def prof_toggle() -> QPushButton:
    """Pastille-interrupteur de maîtrise (remplace la case à cocher) : survol et état « allumé » visibles."""
    b = QPushButton("○ Non maîtrisée")
    b.setCheckable(True)
    b.setProperty("role", "toggle")
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setMinimumWidth(128)
    return b


LAY_ON_HANDS_TARGETS = ["Sur soi", "Sur un allié", "Guérir maladie / poison (5 PV)"]
PLACEHOLDER_WEAPON = "— choisir une arme —"
PLACEHOLDER_SPELL = "— choisir un sort mineur —"
MAGIC_CHOICES = ["+0", "+1", "+2", "+3"]


def cases_text(meters: float) -> str:
    """« 6 cases (9 m) » — cases de 1,50 m d'abord, mètres à côté (v41)."""
    n = int(meters // 1.5)
    return "{} case{} ({:g} m)".format(n, "s" * (n > 1), meters).replace(".", ",")


class CombatTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        root = QVBoxLayout(body)

        # Ordre tactique : 1. PV + CA + style de combat  2. statistiques  3. ressources  4. réactions
        #                  5. effets actifs (et concentration)  6. armes CaC puis distance  7. sorts mineurs
        self.stat_labels: dict[str, object] = {}

        # ================= 0. Forme sauvage active : PV tampon de la bête, dégâts, soins du Cercle de la Lune
        self.form_box = QGroupBox("🐾 Forme sauvage active")
        fg = QGridLayout(self.form_box)
        self.form_info = make_label("", "head", wrap=True)
        self.form_hp = QSpinBox()
        self.form_hp.setRange(0, 999)
        self.form_hp.setToolTip(rich_tip("PV de la bête", "PV tampon : vos propres PV sont mis de côté et restaurés "
                                         "à la fin de la forme."))
        self.form_dmg = QSpinBox()
        self.form_dmg.setRange(0, 999)
        self.form_dmg_btn = QPushButton("💥 Subir ces dégâts")
        self.form_dmg_btn.setToolTip(rich_tip("Dégâts sous forme sauvage", "Retirés des PV de la bête ; à 0, la forme "
                                              "prend fin et l'excédent est retiré de vos PV normaux."))
        self.moon_lvl = QComboBox()
        self.moon_btn = QPushButton("🌙 Soin du Cercle de la Lune (action bonus)")
        self.moon_btn.setToolTip(rich_tip("Forme sauvage de combat", "Action bonus : dépensez un emplacement de sort "
                                          "pour regagner 1d8 PV par niveau de l'emplacement (sur les PV de la bête)."))
        self.form_end = QPushButton("Reprendre sa forme normale")
        self.form_end.setProperty("role", "ghost")
        self.form_info.setWordWrap(True)                  # v52 : mis en page pour la colonne de gauche
        fg.addWidget(self.form_info, 0, 0, 1, 3)
        fg.addWidget(make_label("PV de la bête"), 1, 0)
        fg.addWidget(self.form_hp, 1, 1, 1, 2)
        fg.addWidget(make_label("Dégâts"), 2, 0)
        fg.addWidget(self.form_dmg, 2, 1)
        fg.addWidget(self.form_dmg_btn, 2, 2)
        self.moon_caption = make_label("Emplacement")
        fg.addWidget(self.moon_caption, 3, 0)
        fg.addWidget(self.moon_lvl, 3, 1)
        fg.addWidget(self.moon_btn, 3, 2)
        fg.addWidget(self.form_end, 4, 0, 1, 3)
        fg.setColumnStretch(2, 1)
        self.form_box.setVisible(False)
        root.addWidget(self.form_box)
        self.form_hp.valueChanged.connect(self._on_form_hp)
        self.form_dmg_btn.clicked.connect(self._on_form_damage)
        self.moon_btn.clicked.connect(self._on_moon_heal)
        self.form_end.clicked.connect(self._on_form_end)

        # ================= 1. Points de vie | Armure & CA | Style de combat
        top = QHBoxLayout()
        hp = QGroupBox("Points de vie")
        self.hp_box = hp
        g = QGridLayout(hp)
        self.hp_max = center("", "stat")
        self.hp_cur, self.hp_tmp, self.hp_misc = QSpinBox(), QSpinBox(), QSpinBox()
        self.hp_cur.setRange(0, 9999)
        self.hp_tmp.setRange(0, 999)
        self.hp_misc.setRange(-999, 999)
        self.hit_dice = make_label("", "muted", wrap=True)
        # v52 : saisie rapide des PV — « 7 » ou « -7 » = dégâts, « +5 » = soins, puis Entrée (Ctrl+D)
        quick = QHBoxLayout()
        self.hp_entry = QLineEdit()
        self.hp_entry.setPlaceholderText("-7 dégâts, +5 soins (Ctrl+D)")
        self.hp_entry.setToolTip(rich_tip("Saisie rapide des PV", "Tapez un nombre puis Entrée : « 7 » ou « -7 » "
                                          "pour des dégâts, « +5 » pour des soins. Les PV temporaires sont consommés "
                                          "en premier, et le jet de concentration est rappelé."))
        self.hp_entry.returnPressed.connect(lambda: self._quick_hp(""))
        self.dmg_btn = QPushButton("💥 Dégâts")
        self.dmg_btn.setToolTip("Retirer la valeur saisie des PV (PV temporaires d'abord).")
        self.dmg_btn.clicked.connect(lambda: self._quick_hp("degats"))
        self.heal_btn = QPushButton("💚 Soins")
        self.heal_btn.setToolTip("Ajouter la valeur saisie aux PV (sans dépasser le maximum).")
        self.heal_btn.clicked.connect(lambda: self._quick_hp("soins"))
        self.dmg_type = QComboBox()                           # v52 : type de dégâts -> résistances et réductions
        self.dmg_type.addItems(["Type : —"] + [t.capitalize() for t in ExtrasMixin.DAMAGE_TYPES])
        self.dmg_type.setToolTip(rich_tip("Type de dégâts", "Facultatif : avec le type, la fiche applique vos "
                                          "immunités, résistances (moitié) et réductions (Maître des armures lourdes)."))
        self.dmg_magic = QCheckBox("magique")
        self.dmg_magic.setToolTip(rich_tip("Dégâts magiques", "Arme ou attaque magique : les résistances « non "
                                           "magiques » et la réduction 2014 de Maître des armures lourdes ne "
                                           "s'appliquent pas."))
        quick.addWidget(self.hp_entry, 1)
        quick.addWidget(self.dmg_type)
        quick.addWidget(self.dmg_magic)
        quick.addWidget(self.dmg_btn)
        quick.addWidget(self.heal_btn)
        g.addLayout(quick, 8, 0, 1, 2)
        free = QHBoxLayout()                              # v52 : jet libre (Ctrl+R)
        self.free_roll = QLineEdit()
        self.free_roll.setPlaceholderText("🎲 Jet libre : 2d6+3, d20+5, 4d6… (Ctrl+R)")
        self.free_roll.setToolTip(rich_tip("Jet libre", "Tapez une formule de dés puis Entrée : les dés roulent et "
                                           "le résultat va dans l'historique des lancers (Ctrl+H)."))
        self.free_roll.returnPressed.connect(self._on_free_roll)
        self.free_roll_btn = QPushButton("🎲 Lancer")
        self.free_roll_btn.clicked.connect(self._on_free_roll)
        self.free_roll_last = make_label("", "muted")
        free.addWidget(self.free_roll, 1)
        free.addWidget(self.free_roll_btn)
        free.addWidget(self.free_roll_last)
        g.addLayout(free, 9, 0, 1, 2)
        self.hp_old_labels = [make_label(t) for t in ("PV max", "PV actuels", "PV temporaires", "Bonus de PV divers")]
        for r, (lab, wid) in enumerate(zip(self.hp_old_labels, (self.hp_max, self.hp_cur, self.hp_tmp,
                                                                  self.hp_misc))):
            g.addWidget(lab, r, 0)
            g.addWidget(wid, r, 1)
        g.addWidget(self.hit_dice, 4, 0, 1, 2)
        death = QHBoxLayout()
        self.ok_boxes = [QCheckBox() for _ in range(3)]
        self.ko_boxes = [QCheckBox() for _ in range(3)]
        self.death_labels = [make_label("Jets contre la mort — réussites"), make_label("échecs")]
        death.addWidget(self.death_labels[0])
        for b in self.ok_boxes:
            death.addWidget(b)
        death.addWidget(self.death_labels[1])
        for b in self.ko_boxes:
            death.addWidget(b)
        self.death_btn = QPushButton("🎲 Jet contre la mort")      # v52 : résultat appliqué automatiquement
        self.death_btn.setToolTip(rich_tip("Jet contre la mort", "d20 : 10 ou plus = réussite, moins = échec ; "
                                           "1 naturel = deux échecs ; 20 naturel = vous reprenez 1 PV. Disponible à "
                                           "0 PV ; les cases se cochent toutes seules."))
        death.addWidget(self.death_btn)
        g.addLayout(death, 5, 0, 1, 2)
        rest = QHBoxLayout()
        self.short_btn = QPushButton("🔥 Repos court…")
        self.long_btn = QPushButton("🌙 Repos long…")
        rest.addWidget(self.short_btn)
        rest.addWidget(self.long_btn)
        g.addLayout(rest, 6, 0, 1, 2)
        self.time_label = make_label("", "muted")
        g.addWidget(self.time_label, 7, 0, 1, 2)
        g.setColumnStretch(1, 1)
        top.addWidget(hp, 1)

        ar = QGroupBox("Classe d'armure")
        a = QGridLayout(ar)
        self.stat_labels["ca"] = center("", "stat")
        self.armor = QComboBox()
        self.armor_magic = QComboBox()
        self.armor_magic.addItems(MAGIC_CHOICES)
        self.shield = QComboBox()
        self.ac_formula = make_label("", "head", wrap=True)      # « CA = 12 + Dex (max 2) + 2 (bouclier) »
        self.ac_detail = make_label("", "muted", wrap=True)      # « = 12 + 2 + 2 = 16 »
        self.armor_warn = make_label("", "warn", wrap=True)
        a.addWidget(self.stat_labels["ca"], 0, 0, 1, 2)
        a.addWidget(make_label("Armure"), 1, 0)
        a.addWidget(self.armor, 1, 1)
        a.addWidget(make_label("Bonus magique"), 2, 0)
        a.addWidget(self.armor_magic, 2, 1)
        a.addWidget(make_label("Bouclier"), 3, 0)
        a.addWidget(self.shield, 3, 1)
        a.setColumnStretch(1, 1)
        a.addWidget(self.ac_formula, 4, 0, 1, 2)
        a.addWidget(self.ac_detail, 5, 0, 1, 2)
        a.addWidget(self.armor_warn, 6, 0, 1, 2)
        a.setRowStretch(7, 1)
        top.addWidget(ar, 1)

        self.style_box = QGroupBox("Style de combat et modèle d'armure")
        self.style_layout = QGridLayout(self.style_box)
        self.style_rows: list[dict] = []
        self._style_key = None          # None : première construction forcée (même sans aucun emplacement)
        self.style_empty = make_label("", "muted", wrap=True)
        right_col = QVBoxLayout()
        # v52 : emplacements de sorts dans l'onglet En partie (mêmes compteurs que l'onglet Magie)
        self.slots_box = QGroupBox("✨ Emplacements de sorts")
        sg = QGridLayout(self.slots_box)
        self.slot_strip = []
        for lvl in range(9):
            lab = make_label("Niv. {}".format(lvl + 1), "head")
            orbs = OrbBar("emplacement", orb=18, gap=4, per_row=5)
            orbs.changed.connect(lambda used, n=lvl: self._on_slot_used(n, used))
            sg.addWidget(lab, lvl // 3, (lvl % 3) * 2)
            sg.addWidget(orbs, lvl // 3, (lvl % 3) * 2 + 1)
            self.slot_strip.append((lab, orbs))
        self.pact_strip = (make_label("Pacte", "warn"), OrbBar("pacte", orb=18, gap=4, per_row=5))
        self.pact_strip[1].changed.connect(self._on_pact_used)
        sg.addWidget(self.pact_strip[0], 3, 0)
        sg.addWidget(self.pact_strip[1], 3, 1, 1, 5)
        right_col.addWidget(self.slots_box)
        right_col.addWidget(self.style_box, 1)
        # v52 : bottes d'arme (maîtrise d'arme 2024) — nombre limité sur une fiche 2024
        self.mastery_box = QGroupBox("Bottes d'arme")
        mb = QHBoxLayout(self.mastery_box)
        self.mastery_label = make_label("", "muted", wrap=True)
        self.mastery_btn = QPushButton("Choisir les bottes…")
        self.mastery_btn.clicked.connect(self._choose_masteries)
        mb.addWidget(self.mastery_label, 1)
        mb.addWidget(self.mastery_btn)
        right_col.addWidget(self.mastery_box)
        # v52 : « À ne pas oublier » — capacités de situation, une ligne chacune, repliable
        self.remember_box = QGroupBox("📌 À ne pas oublier")
        rl = QVBoxLayout(self.remember_box)
        self.remember_toggle = QPushButton("▾ Masquer")
        self.remember_toggle.setProperty("role", "ghost")
        self.remember_toggle.clicked.connect(self._on_remember_toggle)
        rl.addWidget(self.remember_toggle)
        self.remember_text = make_label("", "", wrap=True)
        rl.addWidget(self.remember_text)
        self._remember_open = True
        right_col.addWidget(self.remember_box)
        # jets de sauvegarde ultra-condensés (3 × 2) juste sous le style de combat
        self.saves_box = QGroupBox("Jets de sauvegarde")
        sg = QGridLayout(self.saves_box)
        sg.setHorizontalSpacing(6)
        sg.setVerticalSpacing(2)
        self.save_cells: dict[str, dict] = {}
        for n, ab in enumerate(R.ABILITIES):
            cell_w = QWidget()
            cl = QHBoxLayout(cell_w)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(2)
            lab = make_label("", "head")
            btn = d20_button("Jet de sauvegarde de " + ab)
            btn.clicked.connect(lambda _=False, a=ab: roll_dice(self.win, self.engine.save_spec(a)))
            cl.addWidget(lab, 1)
            cl.addWidget(btn)
            sg.addWidget(cell_w, n // 3, n % 3)
            self.save_cells[ab] = {"label": lab, "btn": btn}
        self.saves_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        right_col.addWidget(self.saves_box)
        top.addLayout(right_col, 1)
        root.addLayout(top)

        # ================= 2. Statistiques de base
        # cinq encarts de même largeur (stretch 1, largeur minimale libre) : aucun dépassement de la ligne
        # v51 : grille unique, hauteur FIXE identique pour les cinq encarts, contenu centré verticalement
        stats = QGridLayout()
        stats.setHorizontalSpacing(8)
        self.stat_boxes = {}
        for col, (key, title) in enumerate((("init", "Initiative"), ("vit", "Vitesse"), ("prof", "Maîtrise"),
                                            ("perc", "Perception passive"), ("vision", "Vision dans le noir"))):
            box = QGroupBox(title)
            box.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            box.setMinimumWidth(0)
            box.setFixedHeight(self.STAT_BOX_HEIGHT)
            lay = QVBoxLayout(box)
            lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            lab = center("", "stat")
            lab.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
            lab.setWordWrap(True)                        # vitesses multiples : retour à la ligne plutôt que rognage
            if key == "init":                            # v45 : dé d20 cliquable = jet d'initiative
                row = QHBoxLayout()
                row.addWidget(lab, 1)
                self.init_btn = d20_button("Jet d'initiative : 1d20 + modificateur d'initiative")
                self.init_btn.clicked.connect(self._on_roll_initiative)
                row.addWidget(self.init_btn)
                lay.addLayout(row)
                self.init_last = center("", "muted")
                lay.addWidget(self.init_last)
            else:
                lay.addWidget(lab)
            self.stat_labels[key] = lab
            self.stat_boxes[key] = box
            stats.addWidget(box, 0, col)
            stats.setColumnStretch(col, 1)
        root.addLayout(stats)

        # ================= 2 bis. Ce tour-ci (v30, barre d'action façon BG3) : tout ce qui est jouable, filtré par coût
        root.addWidget(self._turn_group())

        # ================= 3. Actions & capacités de classe : sphères de ressources (rage, ki, dés de supériorité,
        # conduit divin...) + actions spéciales — placé au-dessus des armes de corps à corps (voir plus bas)
        self.res_box = QGroupBox("⚔ Actions, capacités de classe")
        res_outer = QVBoxLayout(self.res_box)
        res_outer.setSpacing(6)
        res_grid = QWidget()
        self.res_layout = QGridLayout(res_grid)
        self.res_layout.setContentsMargins(0, 0, 0, 0)
        res_outer.addWidget(res_grid)
        self.res_sep = hline()
        res_outer.addWidget(self.res_sep)
        act_grid = QWidget()
        self.act_layout = QGridLayout(act_grid)
        self.act_layout.setContentsMargins(0, 0, 0, 0)
        self.act_layout.setVerticalSpacing(4)
        res_outer.addWidget(act_grid)
        # sous-section « Passifs de classe » (Rage implacable, Évasion, Aura de protection…) — infobulle complète
        self.pass_title = make_label("◈ Passifs de classe — survolez un passif pour sa description complète", "head")
        res_outer.addWidget(self.pass_title)
        pass_grid = QWidget()
        self.pass_layout = QGridLayout(pass_grid)
        self.pass_layout.setContentsMargins(0, 0, 0, 0)
        self.pass_layout.setHorizontalSpacing(6)
        res_outer.addWidget(pass_grid)
        self._pass_key = None
        self.res_rows: list[dict] = []
        self.act_rows: list[dict] = []
        self._res_key = None
        self._act_key = None
        self.res_box.setVisible(False)
        self.res_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        # ================= 4. (v41) l'ancien encart « Réactions » est retiré : chaque réaction a sa tuile dans le
        # groupe « ⚡ Réactions » de « Ce tour-ci » ; la réaction du round se suit dans le pied de tour.

        # ================= 5. Effets actifs (buffs, débuffs, états) + concentration
        fx = QGroupBox("États et effets actifs — survolez une icône pour ses règles, cliquez pour la retirer")
        fl = QVBoxLayout(fx)
        conc = QHBoxLayout()
        self.conc_label = make_label("", "banner", wrap=True)
        self.conc_label.setToolTip(rich_tip("Concentration", "Un seul sort de concentration à la fois ; subir des "
                                            "dégâts impose un JS de Constitution (DD 10 ou moitié des dégâts)."))
        self.conc_btn = QPushButton("Rompre la concentration")
        self.conc_btn.setToolTip(rich_tip("Rompre la concentration", "Met fin au sort en cours."))
        self.conc_btn.setProperty("role", "ghost")
        conc.addWidget(self.conc_label, 1)
        conc.addWidget(self.conc_btn)
        fl.addLayout(conc)
        exh = QHBoxLayout()                               # v52 : épuisement selon l'édition
        self.exh_minus = QPushButton("−")
        self.exh_plus = QPushButton("＋")
        for b in (self.exh_minus, self.exh_plus):
            b.setProperty("role", "ghost")
            b.setFixedWidth(34)
        self.exh_label = make_label("")
        self.exh_roll = QPushButton("🎲 JS d'épuisement…")
        self.exh_roll.setProperty("role", "ghost")
        self.exh_roll.setToolTip(rich_tip("JS d'épuisement", "Marche forcée, chaleur ou froid extrêmes, privation… "
                                          "Le DD officiel est proposé ; un échec ajoute un niveau d'épuisement."))
        self.exh_minus.setToolTip(rich_tip("Épuisement", "Retire un niveau (un repos long en retire un aussi)."))
        self.exh_plus.setToolTip(rich_tip("Épuisement", "Ajoute un niveau d'épuisement."))
        self.exh_caption = make_label("Épuisement", "muted")
        exh.addWidget(self.exh_caption)
        exh.addWidget(self.exh_minus)
        exh.addWidget(self.exh_label)
        exh.addWidget(self.exh_plus)
        exh.addWidget(self.exh_roll)
        exh.addStretch(1)
        fl.addLayout(exh)
        self.fx_holder = QWidget()
        self.fx_grid = QGridLayout(self.fx_holder)
        self.fx_grid.setContentsMargins(0, 0, 0, 0)
        self.fx_grid.setSpacing(6)
        self.fx_empty = make_label("Aucun effet actif.", "muted")
        fl.addWidget(self.fx_holder)
        fl.addWidget(self.fx_empty)
        self.fx_cat = QComboBox()
        self.fx_cat.addItems([ALL_CATS] + FX.CATEGORIES)
        self.fx_search = QLineEdit()
        self.fx_search.setPlaceholderText("Rechercher un effet (Hâte, Empoisonné, Aura…)")
        self.fx_combo = QComboBox()
        self.fx_combo.setMinimumWidth(260)
        self.fx_add = QPushButton("＋ Ajouter l'effet")
        self.fx_clear = QPushButton("🧹 Retirer les effets temporaires")
        self.fx_clear.setProperty("role", "ghost")
        self.fx_clear.setToolTip(rich_tip("Nettoyage rapide", "Retire en un clic tous les effets ajoutés (sorts, "
                                          "potions, états passagers). Les traits raciaux et les aptitudes de classe "
                                          "permanentes (🔒) sont conservés."))
        self.fx_cat.setToolTip(rich_tip("Catégorie", "Filtre la bibliothèque d'effets : bonus, malus, états, "
                                        "auras, aptitudes."))
        self.fx_search.setToolTip(rich_tip("Recherche", "Tapez une partie du nom, de la source ou des règles "
                                           "(ex. « poison », « Hâte », « feu »)."))
        self.fx_add.setToolTip(rich_tip("Ajouter l'effet", "Active l'effet choisi : ses modificateurs s'appliquent "
                                        "immédiatement à la fiche (CA, jets, compétences, vitesse…)."))
        pick = QGridLayout()                              # v52 : deux lignes (colonne de gauche étroite)
        self.fx_combo.setMinimumWidth(0)
        self.fx_clear.setText("🧹 Retirer les temporaires")
        pick.addWidget(self.fx_cat, 0, 0)
        pick.addWidget(self.fx_search, 0, 1, 1, 2)
        pick.addWidget(self.fx_combo, 1, 0, 1, 2)
        pick.addWidget(self.fx_add, 1, 2)
        pick.addWidget(self.fx_clear, 2, 0, 1, 3)
        pick.setColumnStretch(1, 1)
        fl.addLayout(pick)
        self.fx_summary = make_label("", "head", wrap=True)
        fl.addWidget(self.fx_summary)
        self.fx_defenses = make_label("", "muted", wrap=True)
        fl.addWidget(self.fx_defenses)
        root.addWidget(fx)
        self._fx_key = None

        # ================= 6. Armes (CaC puis distance)  7. Sorts mineurs
        self.weapon_rows: dict[str, list[dict]] = {}
        self._box_heads: dict[str, list] = {}           # en-têtes de colonnes : masqués tant que l'encart est vide
        # attaques de la bête (Forme sauvage) : remplacent armes et sorts mineurs tant que la forme est active
        self.beast_box = QGroupBox("🐺 Attaques de la bête — modificateurs de la créature")
        self.beast_grid = QGridLayout(self.beast_box)
        self._beast_key = None
        self.beast_box.setVisible(False)
        self.weapon_boxes = [self._weapon_group("Armes de corps à corps (CaC)", "armes_cac", "cac"),
                             self._weapon_group("Armes à distance", "armes_distance", "distance")]
        root.addWidget(self.res_box)                     # actions de classe : juste au-dessus du corps à corps
        root.addWidget(self.weapon_boxes[0])
        root.addWidget(self.beast_box)                   # entre les armes de corps à corps et à distance
        root.addWidget(self.weapon_boxes[1])
        self.cantrip_box = self._cantrip_group()
        root.addWidget(self.cantrip_box)

        # ================= 8. Capacités de combat raciales (souffle draconique...) — affiché seulement si utile
        self.racial_box = QGroupBox("Capacités de combat raciales et de lignage")
        self.racial_layout = QVBoxLayout(self.racial_box)
        self._racial_key = None
        self.racial_box.setVisible(False)
        root.addWidget(self.racial_box)
        root.addStretch(1)

        # ---------------- connexions
        self.hp_cur.valueChanged.connect(self._on_hp_cur)
        self.hp_tmp.valueChanged.connect(lambda v: self._set("pv_temporaires", v))
        self.hp_misc.valueChanged.connect(lambda v: self._set("pv_divers", v))
        for i, b in enumerate(self.ok_boxes):
            b.toggled.connect(lambda _=False: self._on_death())
        for b in self.ko_boxes:
            b.toggled.connect(lambda _=False: self._on_death())
        self.death_btn.clicked.connect(self._on_death_save)
        self.short_btn.clicked.connect(lambda: self._on_rest("short"))
        self.long_btn.clicked.connect(lambda: self._on_rest("long"))
        self.fx_cat.activated.connect(lambda _=0: self._fill_fx_picker())
        self.fx_search.textChanged.connect(lambda _="": self._fill_fx_picker())
        self.fx_add.clicked.connect(self._on_add_effect)
        self.fx_combo.activated.connect(lambda _=0: None)
        self.fx_clear.clicked.connect(self._on_clear_effects)
        self.exh_minus.clicked.connect(lambda: self._on_exhaustion(-1))
        self.exh_plus.clicked.connect(lambda: self._on_exhaustion(1))
        self.exh_roll.clicked.connect(lambda: self.open_exhaustion())
        self.conc_btn.clicked.connect(self._on_break_concentration)
        self.armor.activated.connect(self._on_armor)
        self.armor_magic.activated.connect(self._on_armor)
        self.shield.activated.connect(lambda _=0: self._on_armor())
        self._relayout(root)                              # v52 : disposition 16/9 (bandeau, colonne, tuiles)

    STAT_BOX_HEIGHT = 104                                # v51 : hauteur commune des encarts de statistiques

    # ------------------------------------------------------------------ v52 : disposition 16/9
    def _relayout(self, root) -> None:
        """Bandeau du haut (PV, CA, initiative, vitesse, maîtrise, perception, vision, inspiration, épuisement),
        colonne de gauche (caractéristiques et JS, PV, repos, ressources, rappels, états) et zone principale (tuiles
        du tour en colonnes). Les anciens encarts (armure, style, armes, sorts mineurs) restent créés mais masqués."""
        while root.count():
            root.takeAt(0)
        self._parking = QWidget(self)                    # anciens encarts conservés (logique, tests) mais cachés
        self._parking.hide()
        park = QVBoxLayout(self._parking)
        ac_box = self.stat_labels["ca"].parentWidget()
        fx_box = self.fx_holder.parentWidget()
        turn_box = self.turn_banner.parentWidget()
        # --- bandeau du haut
        hdr = QFrame()
        hdr.setObjectName("partyHeader")
        hdr_lines = QVBoxLayout(hdr)                     # v53 : deux lignes — chiffres, puis états du personnage
        hdr_lines.setContentsMargins(8, 4, 8, 4)
        hdr_lines.setSpacing(2)
        hl = QHBoxLayout()
        hl.setSpacing(14)
        hdr_lines.addLayout(hl)
        self.hp_big = make_label("", "stat")
        self.hp_big.setToolTip(rich_tip("Points de vie", "PV actuels / maximum (+ PV temporaires). Corrections "
                                        "fines dans l'encart « Points de vie » de la colonne de gauche."))
        self.dmg_open_btn = QPushButton("💥 Dégâts")
        self.dmg_open_btn.setToolTip(rich_tip("Dégâts subis", "Demande le montant et le type : résistances, "
                                              "immunités et réactions sont appliquées (Ctrl+D)."))
        self.heal_open_btn = QPushButton("💚 Soins")
        self.heal_open_btn.setToolTip(rich_tip("Soins reçus", "Demande le nombre de PV regagnés (ou de PV "
                                               "temporaires)."))
        self.dmg_open_btn.clicked.connect(self.open_damage)
        self.heal_open_btn.clicked.connect(self.open_heal)
        hl.addWidget(self.hp_big)
        hl.addWidget(self.dmg_open_btn)
        hl.addWidget(self.heal_open_btn)

        def stat(caption: str, *widgets):
            box = QVBoxLayout()
            box.setSpacing(0)
            box.addWidget(make_label(caption, "muted"), 0, Qt.AlignmentFlag.AlignHCenter)
            row = QHBoxLayout()
            row.setSpacing(2)
            for w in widgets:
                w.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
                row.addWidget(w)
            box.addLayout(row)
            hl.addLayout(box)
        stat("CA", self.stat_labels["ca"])
        stat("Initiative", self.stat_labels["init"], self.init_btn)
        stat("Vitesse", self.stat_labels["vit"])
        stat("Maîtrise", self.stat_labels["prof"])
        stat("Perception", self.stat_labels["perc"])
        stat("Vision", self.stat_labels["vision"])
        for key in ("init", "vit", "prof", "perc", "vision", "ca"):
            self.stat_labels[key].setWordWrap(False)
        hl.addStretch(1)
        hl = QHBoxLayout()                               # 2e ligne : inspiration, jets contre la mort, épuisement
        hl.setSpacing(14)
        hdr_lines.addLayout(hl)
        self.insp_check = QCheckBox("🌟 Inspiration")
        self.insp_check.setToolTip(rich_tip("Inspiration", "Cochée : vous avez un point d'inspiration (accordé par "
                                            "le MJ, ou Ingénieux). Il se dépense dans la fenêtre d'un jet de d20."))
        self.insp_check.toggled.connect(self._on_inspiration)
        no_truncate(self.insp_check)
        hl.addWidget(self.insp_check)
        # v53 : jets contre la mort dans le bandeau, à droite de l'inspiration (visibles à 0 PV seulement)
        death = QHBoxLayout()
        death.setSpacing(4)
        self.death_labels[0].setText("☠ Réussites")
        self.death_labels[1].setText("Échecs")
        self.death_labels[0].setToolTip(rich_tip("Jets contre la mort", "À 0 PV : 3 réussites = stabilisé, "
                                                 "3 échecs = mort. Les cases se cochent avec le bouton 🎲."))
        death.addWidget(self.death_labels[0])
        for b in self.ok_boxes:
            death.addWidget(b)
        death.addWidget(self.death_labels[1])
        for b in self.ko_boxes:
            death.addWidget(b)
        self.death_btn.setText("🎲 Jet")
        death.addWidget(self.death_btn)
        no_truncate(*self.death_labels, self.death_btn)
        hl.addLayout(death)
        self.style_badge = make_label("", "muted")
        hl.addWidget(self.style_badge)
        hl.addStretch(1)
        self.exh_minus.setText("−")                       # v52 : − / + bien lisibles
        self.exh_plus.setText("+")
        self.exh_roll.setText("🎲 JS")
        for b in (self.exh_minus, self.exh_plus):
            b.setFixedSize(30, 26)
        hl.addWidget(make_label("Épuisement", "muted"))
        hl.addWidget(self.exh_minus)
        hl.addWidget(self.exh_label)
        hl.addWidget(self.exh_plus)
        hl.addWidget(self.exh_roll)
        root.addWidget(hdr)
        # --- corps : colonne de gauche + zone principale
        body = QHBoxLayout()
        body.setSpacing(10)
        left = QWidget()
        left.setMaximumWidth(470)
        left.setMinimumWidth(380)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(6)
        ll.addWidget(self.form_box)
        ll.addWidget(self._abilities_box())
        ll.addWidget(self.hp_box)
        ll.addWidget(self.mastery_box)
        ll.addWidget(self.racial_box)
        ll.addStretch(1)
        body.addWidget(left)
        main = QVBoxLayout()
        park.addWidget(self.beast_box)                    # v52 : les attaques de la bête sont des tuiles
        park.addWidget(self.res_box)                      # v52 : les ressources sont affichées sur les tuiles
        main.addWidget(turn_box)
        under = QHBoxLayout()                             # sous les tuiles : états actifs | à ne pas oublier
        under.addWidget(fx_box, 1)
        under.addWidget(self.remember_box, 1)
        main.addLayout(under)
        main.addStretch(1)
        body.addLayout(main, 1)
        self.exh_caption.setVisible(False)
        root.addLayout(body, 1)
        # v53 : bandeau des ressources (cases façon jeu de rôle) au-dessus des icônes ; l'ancien encart des
        # emplacements de sorts est rangé
        from .resource_bar import ResourceStrip
        self.resource_strip = ResourceStrip(self)
        self.turn_slots_layout.addWidget(self.resource_strip, 1)
        park.addWidget(self.slots_box)
        # PV : PV max dans le bandeau ; actuels / temporaires / divers sur une seule ligne
        g = self.hp_box.layout()
        for w in self.hp_old_labels + [self.hp_max]:
            w.setVisible(False)
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        for caption, spin in (("Actuels", self.hp_cur), ("Temp.", self.hp_tmp), ("Divers", self.hp_misc)):
            rl.addWidget(make_label(caption, "muted"))
            spin.setVisible(True)
            rl.addWidget(spin, 1)
        g.addWidget(row, 0, 0, 1, 2)
        self.hp_box.setTitle("Points de vie (corrections)")
        # PV : la saisie rapide est remplacée par les boutons Dégâts / Soins du bandeau
        for w in (self.hp_entry, self.dmg_type, self.dmg_magic, self.dmg_btn, self.heal_btn):
            w.setVisible(False)
        # ressources : seules les sphères restent (les actions sont des tuiles)
        self.act_layout.parentWidget().setVisible(False)
        self.res_sep.setVisible(False)
        # encarts retirés de l'écran (armure / bouclier -> inventaire, style -> création, armes -> tuiles)
        for w in [ac_box, self.style_box, self.saves_box, self.cantrip_box] + list(self.weapon_boxes) + \
                list(self.stat_boxes.values()):
            park.addWidget(w)

    def _abilities_box(self) -> QGroupBox:
        """Caractéristiques avec leur jet de sauvegarde sur la même ligne (le dé juste à côté)."""
        box = QGroupBox("Caractéristiques et jets de sauvegarde")
        g = QGridLayout(box)
        g.setHorizontalSpacing(8)
        g.setVerticalSpacing(2)
        self.ab_labels = {}
        for r, ab in enumerate(R.ABILITIES):
            name = make_label(ab, "head")
            score = make_label("", "")
            self.ab_labels[ab] = score
            cell_w = self.save_cells[ab]["label"].parentWidget()
            cl = cell_w.layout()
            if cl is not None and hasattr(cl, "setStretch"):
                cl.setStretch(0, 0)                       # le dé juste à côté du bonus
                cl.addStretch(1)
            self.save_cells[ab]["label"].setMinimumWidth(80)
            g.addWidget(name, r, 0)
            g.addWidget(score, r, 1)
            g.addWidget(make_label("JS", "muted"), r, 2)
            g.addWidget(cell_w, r, 3)
        g.setColumnStretch(3, 1)
        return box

    def _refresh_header(self) -> None:
        eng, ch = self.engine, self.ch
        hp_max = eng.hp_max()
        cur = ch.pv_actuels if ch.pv_actuels >= 0 else hp_max
        form = eng.form_status()
        if form and ch.forme_active and not eng.wild_shape_2024():   # PV de la bête (vos PV sont mis de côté)
            self.hp_big.setText("{} {} / {}  (vos PV : {} / {})".format(form["icone"], ch.forme_pv, form["pv_max"],
                                                                     cur, hp_max))
        else:
            self.hp_big.setText("❤ {} / {}{}".format(cur, hp_max, "  (+{} temp.)".format(ch.pv_temporaires)
                                                    if ch.pv_temporaires else ""))
        for ab, lab in self.ab_labels.items():
            lab.setText("{} ({})".format(eng.score(ab), R.fmt_bonus(eng.mod(ab))))
        with blocked(self.insp_check):
            self.insp_check.setChecked(bool(ch.inspiration))
        styles = []
        for sid, name in (ch.styles_combat or {}).items():
            if name and "|modele" not in sid:
                styles.append((name, self.db.style_description(sid.split("|")[0], name)))
        self.style_badge.setText(" · ".join("⚔ " + n for n, _d in styles))
        self.style_badge.setToolTip(rich_tip("Style de combat", "\n".join("{} : {}".format(n, d) for n, d in styles))
                                    if styles else "")
        down = ch.pv_actuels == 0 and not ch.forme_active          # jets contre la mort seulement à 0 PV
        for w in self.death_labels + self.ok_boxes + self.ko_boxes + [self.death_btn]:
            w.setVisible(down)

    def _on_inspiration(self, on: bool) -> None:
        self.ch.inspiration = bool(on)
        self.changed()

    def open_damage(self) -> bool:
        from .hp_dialogs import DamageDialog
        dlg = DamageDialog(self.win)
        if not dlg.exec():
            return False
        amount, dtype, magical = dlg.values()
        return self.apply_damage(amount, dtype, magical)

    def apply_damage(self, amount: int, dtype: str = "", magical: bool = False) -> bool:
        if amount <= 0:
            return False
        if self.engine.defense_options("degats"):        # réactions possibles avant les dégâts
            return self.open_defense("degats", amount, dtype, magical)
        self._message(self.engine.take_damage(amount, dtype, magical))
        self.changed()
        self.maybe_concentration_save()
        self.maybe_zero_hp()
        return True

    def open_heal(self) -> bool:
        from .hp_dialogs import HealDialog
        dlg = HealDialog(self.win)
        if not dlg.exec():
            return False
        amount, temp = dlg.values()
        return self.apply_heal(amount, temp)

    def apply_heal(self, amount: int, temp: bool = False) -> bool:
        if amount <= 0:
            return False
        if temp:
            self.ch.pv_temporaires = max(int(self.ch.pv_temporaires), int(amount))
            self._message("PV temporaires : {}.".format(self.ch.pv_temporaires))
        else:
            self._message(self.engine.receive_healing(amount))
        self.changed()
        return True

    def maybe_form_ended(self) -> None:
        """v52 : la bête tombe à 0 PV — fenêtre « fin de la transformation » (puis 0 PV éventuel)."""
        eng = self.engine
        msg = getattr(eng, "form_ended_message", "")
        if not msg:
            return
        eng.form_ended_message = ""
        ask_yes_no(self.win, "Fin de la transformation", msg, yes="Compris", no="Fermer", default_no=False)

    def maybe_zero_hp(self) -> None:
        """v52 : à 0 PV, message et jet contre la mort proposé."""
        self.maybe_form_ended()
        eng = self.engine
        if not getattr(eng, "dropped_to_zero", False):
            return
        eng.dropped_to_zero = False
        if ask_yes_no(self.win, "0 PV — inconscient", "Vous tombez à 0 PV : vous êtes inconscient et à terre.\n\n"
                      "Faites un jet de sauvegarde contre la mort au début de chacun de vos tours (10 ou plus : "
                      "réussite ; 3 réussites : stabilisé ; 3 échecs : mort).", yes="🎲 Lancer le jet maintenant",
                      no="Plus tard", default_no=False):
            self._on_death_save()

    # ------------------------------------------------------------------ barre du tour (v30)
    TURN_FILTERS = ["Tout", "Action", "Action bonus", "Réaction", "Gratuit"]
    TURN_GROUPS = [("attaques", "🗡️ Attaques au corps à corps et à distance"), ("magie", "✨ Sorts et magie"),
                   ("reactions", "⚡ Réactions"), ("generiques", "🏃 Actions génériques"),
                   ("capacites", "🎖️ Capacités de classe et de race"),
                   ("objets", "💎 Objets magiques — capacités activables")]
    TURN_ICONS = {"Action": "●", "Action bonus": "▲", "Réaction": "◆", "Gratuit": "○"}

    def _turn_group(self) -> QGroupBox:
        box = QGroupBox("⚔ Ce tour-ci — cliquez une icône pour l'utiliser (survol : règles complètes)")
        lay = QVBoxLayout(box)
        lay.setSpacing(6)
        # v52 : bandeau de rappels (début / fin de tour, initiative) — se ferme d'un clic, jamais bloquant
        self.turn_banner = QWidget()
        tb = QHBoxLayout(self.turn_banner)
        tb.setContentsMargins(0, 0, 0, 0)
        self.turn_banner_text = make_label("", "banner", wrap=True)
        self.turn_banner_close = QPushButton("✕")
        self.turn_banner_close.setProperty("role", "ghost")
        self.turn_banner_close.setToolTip("Fermer les rappels")
        self.turn_banner_close.clicked.connect(lambda: self.show_turn_banner("", []))
        tb.addWidget(self.turn_banner_text, 1)
        tb.addWidget(self.turn_banner_close)
        self.turn_banner.setVisible(False)
        lay.addWidget(self.turn_banner)
        filt = QHBoxLayout()
        self.turn_filter = "Tout"
        self.turn_filter_btns = {}
        for name in self.TURN_FILTERS:
            b = QPushButton(name)
            b.setCheckable(True)
            b.setProperty("role", "toggle")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, n=name: self._on_turn_filter(n))
            filt.addWidget(b)
            self.turn_filter_btns[name] = b
        filt.addStretch(1)
        lay.addLayout(filt)
        # v41 : quatre groupes de tuiles (attaques, sorts, réactions, actions génériques)
        self.turn_groups: dict[str, tuple] = {}
        for gkey, title in self.TURN_GROUPS:
            frame = QWidget()
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(0, 2, 0, 2)
            fl.setSpacing(4)
            head_lab = make_label(title, "head")
            fl.addWidget(head_lab)
            holder = QWidget()
            grid = QGridLayout(holder)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(6)
            grid.setVerticalSpacing(6)
            fl.addWidget(holder)
            lay.addWidget(frame)
            self.turn_groups[gkey] = (frame, head_lab, grid)
        self.turn_grid = self.turn_groups["attaques"][2]          # compatibilité (anciens accès)
        for frame, _h, _g in self.turn_groups.values():           # v52 : remplacés par les colonnes ci-dessous
            frame.setParent(None)
            frame.hide()
        for b in self.turn_filter_btns.values():
            b.setVisible(False)
        # v52 : une seule grille de tuiles, une couleur par type (attaque, capacité, magie, objet, action commune) ;
        # le coût (● Action, ▲ Bonus, ◆ Réaction, ○ Gratuit) est écrit sur chaque tuile
        top = QHBoxLayout()
        self.turn_slots_layout = QHBoxLayout()            # v53 : bandeau des ressources (cases)
        top.addLayout(self.turn_slots_layout, 1)
        lay.addLayout(top)
        self.turn_legend = make_label("", "muted")
        self.turn_legend.setTextFormat(Qt.TextFormat.RichText)
        legend_row = QHBoxLayout()                       # v53 : légende + retour à l'ordre par défaut des tuiles
        legend_row.addWidget(self.turn_legend, 1)
        self.turn_order_reset = QPushButton("↺ Ordre par défaut")
        self.turn_order_reset.setProperty("role", "ghost")
        self.turn_order_reset.setToolTip(rich_tip("Ordre des tuiles", "Glissez une tuile sur une autre pour la "
                                                  "placer avant ou après (ordre enregistré avec le personnage). Ce "
                                                  "bouton rétablit l'ordre par catégorie."))
        self.turn_order_reset.clicked.connect(self._reset_tile_order)
        legend_row.addWidget(self.turn_order_reset)
        lay.addLayout(legend_row)
        holder = QWidget()
        self.turn_flow = QGridLayout(holder)
        self.turn_flow.setContentsMargins(0, 0, 0, 0)
        self.turn_flow.setHorizontalSpacing(5)
        self.turn_flow.setVerticalSpacing(5)
        lay.addWidget(holder)
        self.turn_cols = {}                               # compatibilité
        self.turn_empty = make_label("Rien à faire dans cette catégorie.", "muted")
        lay.addWidget(self.turn_empty)
        self.turn_tiles: dict[str, QPushButton] = {}
        self._turn_key = None
        lay.addWidget(hline())
        # pied de tour : voyants Action / Bonus / Réaction, déplacement, réaction automatique, nouveau round
        foot = QHBoxLayout()
        foot.addWidget(make_label("Pied de tour", "head"))
        self.turn_lights = {}
        for kind in ("Action", "Action bonus", "Réaction"):
            b = QPushButton()
            b.setCheckable(True)
            b.setProperty("role", "toggle")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, k=kind: self._on_turn_light(k))
            foot.addWidget(b)
            self.turn_lights[kind] = b
        foot.addWidget(make_label("🦶 Déplacé"))
        self.turn_move = QSpinBox()                      # v41 : saisie en cases de 1,50 m
        self.turn_move.setSuffix(" case(s)")
        self.turn_move.setToolTip(rich_tip("Déplacement du tour", "Cases parcourues ce tour (1 case = 1,50 m)."))
        self.turn_move.valueChanged.connect(self._on_turn_move)
        foot.addWidget(self.turn_move)
        self.turn_move_left = make_label("", "muted")
        foot.addWidget(self.turn_move_left)
        foot.addStretch(1)
        lay.addLayout(foot)
        foot = QHBoxLayout()                              # v52 : 2e ligne — tour, attaque subie, environnement
        foot.addStretch(1)
        self.turn_auto_btn = QPushButton("")
        self.turn_auto_btn.setProperty("role", "ghost")
        self.turn_auto_btn.clicked.connect(self._on_auto_reaction)
        foot.addWidget(self.turn_auto_btn)
        self.turn_round_btn = QPushButton("▶ Début de mon tour")       # v52 : remplace « Nouveau round »
        self.turn_round_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.turn_round_btn.setToolTip(rich_tip("Début de mon tour", "Action, action bonus, réaction et "
                                                "déplacement redeviennent disponibles ; les effets de début de tour "
                                                "s'appliquent et les rappels s'affichent."))
        self.turn_round_btn.clicked.connect(self._on_new_round)
        foot.addWidget(self.turn_round_btn)
        self.turn_end_btn = QPushButton("⏹ Fin de mon tour")
        self.turn_end_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.turn_end_btn.setToolTip(rich_tip("Fin de mon tour", "Rappelle ce qui n'a pas servi (action, action "
                                              "bonus) et ce qui se déclenche à la fin de votre tour."))
        self.turn_end_btn.clicked.connect(self._on_end_turn)
        foot.addWidget(self.turn_end_btn)
        self.attacked_btn = QPushButton("🛡 On m'attaque !")         # v52 : jet ennemi, réactions, dégâts
        self.attacked_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.attacked_btn.setToolTip(rich_tip("On m'attaque !", "Saisissez le jet de l'ennemi : la fiche le compare "
                                              "à votre CA, propose vos réactions (Bouclier, Esquive instinctive, "
                                              "Parade…) puis applique les dégâts."))
        self.attacked_btn.clicked.connect(lambda: self.open_defense("attaque"))
        foot.addWidget(self.attacked_btn)
        lay.addLayout(foot)
        foot = QHBoxLayout()                              # v53 : environnement et fin du combat sur une 3e ligne
        foot.addStretch(1)
        self.env_btn = QPushButton("🌪 Environnement…")             # v52 : chute, suffocation
        self.env_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.env_btn.setToolTip(rich_tip("Environnement", "Chute (1d6 par 3 m, À terre, Chute ralentie, Feuille "
                                         "morte) et suffocation (souffle retenu, décompte en rounds)."))
        self.env_btn.clicked.connect(self.open_environment)
        foot.addWidget(self.env_btn)
        self.end_combat_btn = QPushButton("🏁 Fin du combat")       # v52 : bilan et munitions récupérées
        self.end_combat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.end_combat_btn.setToolTip(rich_tip("Fin du combat", "Récupère la moitié des munitions tirées, met fin "
                                                "à la rage et aux effets de tour (Esquiver, Bouclier…), aux états "
                                                "Surpris, Caché et À terre, et affiche le bilan. Les sorts en cours "
                                                "gardent leur durée."))
        self.end_combat_btn.clicked.connect(self._on_end_combat)
        foot.addWidget(self.end_combat_btn)
        lay.addLayout(foot)
        box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        return box

    def _refresh_turn(self) -> None:
        eng, t = self.engine, theme.current()
        tiles = eng.turn_actions()
        shown = [x for x in tiles if self.turn_filter == "Tout" or x["type"] == self.turn_filter]
        counts = {k: sum(1 for x in tiles if x["type"] == k) for k in self.TURN_FILTERS[1:]}
        for name, b in self.turn_filter_btns.items():
            with blocked(b):
                b.setChecked(name == self.turn_filter)
            b.setText("{} ({})".format(name, len(tiles) if name == "Tout" else counts.get(name, 0)))
        key = tuple((x["id"], x["nom"], x["disponible"], x["origine"], x.get("groupe"), x.get("nouveau"))
                    for x in shown) + \
            (self.turn_filter, t.key)
        spheres = self._tile_spheres()
        key = key + (tuple(sorted(spheres.items())),
                     tuple((k, i, r["cle"], r.get("dd"), self.engine.weapon_action_state(r))
                           for k, i, r, _w in self._weapon_action_rows()))
        if key != self._turn_key:
            self._turn_key = key
            self._render_turn_columns(shown, spheres)
            self.turn_empty.setVisible(not shown)
        st = eng.turn_state()
        for kind, b in self.turn_lights.items():
            with blocked(b):
                b.setChecked(st[kind])
            b.setText("{} {}".format("●" if st[kind] else "○", "Bonus" if kind == "Action bonus" else kind))
            b.setToolTip("{} {} — clic : basculer (correction manuelle).".format(
                kind, "dépensée ce tour" if st[kind] else "disponible"))
        speed_cases = int(st["vitesse"] // 1.5)
        with blocked(self.turn_move):
            self.turn_move.setRange(0, max(0, speed_cases * 2))
            self.turn_move.setValue(int(round(st["deplacement"] / 1.5)))
        left = st["vitesse"] - st["deplacement"]
        self.turn_move_left.setText("Déplacement : reste {} (vitesse {})".format(
            cases_text(max(0.0, left)), cases_text(st["vitesse"])))
        self.turn_move_left.setStyleSheet("color: {};".format(t.warn) if left < 0 else "")
        used = self.ch.reaction_utilisee
        if used:                                         # réaction du round : nom de la tuile utilisée
            name = next((x["nom"] for x in tiles if x["id"] in ("reaction:" + used, used) or
                         x["id"] == "sort:" + used.replace("sort:", "")), used.split(":")[-1])
            self.turn_lights["Réaction"].setToolTip("Réaction utilisée ce round : {} — clic : annuler.".format(name))
        self.turn_auto_btn.setVisible(False)             # v40 : plus de réaction « automatique »

    # ------------------------------------------------------------------ v52 : colonnes de tuiles
    def _tile_spheres(self) -> dict:
        """Ressource restante affichée sur chaque tuile de capacité : {id de tuile: « ●●○ 2/3 »}."""
        eng = self.engine
        trackers = {t["key"]: t for t in eng.resource_trackers()}
        acts = {a["id"]: a for a in eng.class_actions()}
        out = {}
        for x in eng.turn_actions():
            ref = x.get("ref") or {}
            a = acts.get(ref.get("action", "")) if isinstance(ref, dict) else None
            cost = (a or {}).get("cout") or {}
            tr = trackers.get(cost.get("ressource", "")) if isinstance(cost, dict) else None
            if tr is None and a is not None:
                tr = trackers.get(a["id"])
            if tr and tr.get("total"):
                total, left = int(tr["total"]), max(0, int(tr["total"]) - eng.resource_used(tr["key"]))
                out[x["id"]] = ("●" * left + "○" * (total - left) if total <= 10 else "") + " {}/{}".format(
                    left, total)
        return out

    @staticmethod
    def _is_spell_tile(x: dict) -> bool:
        return x["id"].startswith("sort:") or x.get("groupe") == "magie"

    # v52 : libellés courts des petites tuiles d'actions communes (le nom complet reste dans l'infobulle)
    SHORT_COMMON = {"Se désengager": "Désengager", "Se cacher": "Cacher", "Se tenir prêt": "Prêt",
                    "Utiliser un objet": "Objet", "Boire une potion (Action bonus)": "Potion", "Influencer": "Influence"}

    ICON_SIZE = 56                                       # v53 : icônes carrées façon jeu de rôle

    @classmethod
    def short_label(cls, name: str) -> str:
        """v53 : nom court de tuile — « Attaque — Épée longue » -> « Épée longue », « Utiliser — Baguette de
        boules de feu » -> « Baguette de boules de feu », parenthèses retirées, coupé sur deux lignes."""
        n = (name or "").replace(" (2024)", "").lstrip("★ ").strip()
        n = cls.SHORT_COMMON.get(n, n)
        if " — " in n:
            left, right = n.split(" — ", 1)
            n = right if left in ("Attaque", "Utiliser", "Lancer") else left
        if " : " in n:                                   # « Conduit divin : Renvoi des morts-vivants »
            n = n.split(" : ", 1)[1]
        n = re.sub(r"\s*\(.*?\)", "", n).replace("_", "").replace("*", "").strip()
        n = n[:1].upper() + n[1:]
        if len(n) > 26:
            n = n[:25].rstrip() + "…"
        if len(n) > 12 and " " in n:                    # retour à la ligne au plus près du milieu
            spaces = [i for i, ch in enumerate(n) if ch == " "]
            cut = min(spaces, key=lambda i: abs(i - len(n) / 2))
            n = n[:cut] + "\n" + n[cut + 1:]
        return n

    def _tile_pixmap(self, x: dict, res: str = ""):
        """Icône de la tuile (core/tile_icons) dans la couleur de sa catégorie ; ressource restante en coin."""
        from core.tile_icons import tile_icon
        from . import icons as IC
        kind, name, cat = tile_icon(x)
        dim = not x.get("disponible", True)
        if kind == "sort":
            pix = IC.spell_pixmap(self.db, name, size=self.ICON_SIZE, dim=dim)
        elif kind == "action":                           # v53 : icône unique de chaque action
            pix = IC.action_pixmap(name, cat, self.ICON_SIZE, dim)
        elif kind == "arme":
            pix = IC.weapon_pixmap(name, self.ICON_SIZE, dim)
        else:
            pix = IC.icon_pixmap(name, cat, self.ICON_SIZE, dim)
        count = res.split()[-1] if res else ""
        if (count or x.get("nouveau")) and IC.HAS_SVG:
            from PyQt6.QtGui import QFont, QPainter, QColor
            pix = pix.copy()
            p = QPainter(pix)
            f = QFont()
            f.setBold(True)
            f.setPointSizeF(7.5)
            p.setFont(f)
            if count:                                    # « 2/3 » en bas à droite, sur pastille sombre
                w = p.fontMetrics().horizontalAdvance(count) + 6
                p.setBrush(QColor(0, 0, 0, 170))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawRoundedRect(self.ICON_SIZE - w - 2, self.ICON_SIZE - 15, w, 13, 4, 4)
                p.setPen(QColor("#FFFFFF"))
                p.drawText(self.ICON_SIZE - w + 1, self.ICON_SIZE - 5, count)
            if x.get("nouveau"):                         # ✨ nouvelle capacité
                p.setPen(QColor("#FFE08A"))
                p.drawText(4, 13, "✨")
            p.end()
        return pix

    def _make_tile(self, x: dict, spheres: dict, compact: bool = False):
        """v53 : tuile = icône carrée ; nom et règles complètes dans l'infobulle (option : nom sous l'icône)."""
        from PyQt6.QtCore import QSize
        from PyQt6.QtGui import QIcon
        res = spheres.get(x["id"], "")
        x = dict(x, nom=x["nom"].replace(" (2024)", ""))  # l'édition est celle de la fiche : inutile de la répéter
        names = bool((getattr(self.win, "settings", {}) or {}).get("icones_noms", True))   # v53 : nom sous l'icône
        from .tile_button import TileButton
        b = TileButton(x["id"], self._on_tile_drop)      # v53 : déplaçable (glisser sur une autre tuile)
        b.setIcon(QIcon(self._tile_pixmap(x, res)))
        b.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        b.setAutoRaise(True)
        if names:                                        # v53 : icône + nom le plus court possible (2 lignes)
            b.setText(self.short_label(x["nom"]))
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            b.setIconSize(QSize(self.ICON_SIZE - 8, self.ICON_SIZE - 8))
            b.setFixedSize(self.ICON_SIZE + 40, self.ICON_SIZE + 34)
        else:
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            b.setFixedSize(self.ICON_SIZE + 6, self.ICON_SIZE + 6)
        b.setStyleSheet("QToolButton { border: none; background: transparent; padding: 0px; font-size: 11px; }"
                        "QToolButton:hover { background: rgba(255,255,255,0.10); border-radius: 8px; }")
        b.setProperty("indisponible", not x["disponible"])   # v53 : reste déplaçable ; icône assombrie
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setToolTip(rich_tip("{} {}".format(x["icone"], x["nom"]), "{}{}{}{}{}{}".format(
            "<i>{} — {}</i>\n".format(x["type"], x["origine"]) if x.get("origine") else "<i>{}</i>\n".format(x["type"]),
            x["description"], "\n<b>Coût : {}</b>".format(x["cout"]) if x["cout"] else "",
            "\n<b>Restant : {}</b>".format(res) if res else "",
            "\n<b>🔒 {}</b>".format(x["raison"]) if not x["disponible"] and x["raison"] else "",
            "\n\n<b>Règle complète</b>\n{}".format(x["regle_complete"]) if x.get("regle_complete") else "")))
        if x["disponible"]:
            b.clicked.connect(lambda _=False, tid=x["id"]: self._on_turn_tile(tid))
        else:                                            # indisponible : raison dans la barre d'état
            b.clicked.connect(lambda _=False, n=x["nom"], r=x.get("raison", ""): self.win.statusBar().showMessage(
                "🔒 {} : {}".format(n, r or "indisponible pour le moment."), 6000))
        self.turn_tiles[x["id"]] = b
        return b

    def _use_quick(self, slot: dict, tile_id: str) -> None:
        """Potion / huile : effet officiel (game_widgets.use_consumable) ; parchemin de sort : choix du sort, le
        parchemin est consommé puis le sort résolu. Annulé : l'action dépensée est rendue."""
        eng, win = self.engine, self.win

        def refund() -> None:
            if slot["type"] == "Action bonus":
                self.ch.tour_bonus = False
            else:
                self.ch.tour_action = False
        if slot["genre"] != "parchemin":
            from .game_widgets import use_consumable
            if not use_consumable(win, slot["source"], slot["index"]):
                refund()
                win.statusBar().showMessage("{} : rien n'a été utilisé.".format(slot["nom"]), 6000)
            return
        level = eng.scroll_level(slot["nom"])
        if level is None:                                # parchemin de protection… : effet raconté
            eng.consume_one(slot["source"], slot["index"])
            win.statusBar().showMessage("📜 {} lu : appliquez son effet (voir sa description).".format(slot["nom"]),
                                        8000)
            return
        spells = eng.scroll_spells(slot["nom"])
        picked = ask_choice(win, slot["nom"], "Quel sort ce parchemin contient-il ?", spells) if spells else ""
        if not picked:
            refund()
            return
        eng.consume_one(slot["source"], slot["index"])
        from .spell_flow import resolve_spell
        win.statusBar().showMessage("📜 {} : {} (le parchemin tombe en poussière).".format(slot["nom"], picked), 8000)
        resolve_spell(win, eng, picked, level, "", self._attack_flow)

    # ------------------------------------------------------------------ v53 : ordre des tuiles
    def _on_tile_drop(self, src: str, dst: str, after: bool) -> None:
        from PyQt6.QtCore import QTimer
        from .tile_button import reorder
        self.ch.ordre_tuiles = reorder(self.ch.ordre_tuiles, list(getattr(self, "_tile_ids", [])), src, dst, after)
        self._turn_key = None
        QTimer.singleShot(0, self.changed)               # la tuile cible est reconstruite : hors de son événement

    def _reset_tile_order(self) -> None:
        self.ch.ordre_tuiles = []
        self._turn_key = None
        self.win.statusBar().showMessage("Tuiles remises dans l'ordre par catégorie.", 4000)
        self.changed()

    TILE_CATS = [("attaque", "Attaques"), ("capacite", "Capacités de classe et de race"), ("magie", "Magie"),
                 ("objet", "Objets magiques"), ("reaction", "Réactions"), ("commune", "Actions communes")]

    def _tile_cat(self, x: dict) -> str:
        if self._is_spell_tile(x):
            return "magie"
        g = x.get("groupe", "")
        if g == "generiques":
            return "commune"
        if g == "attaques":
            return "attaque"
        if g == "objets":
            return "objet"
        if x["type"] == "Réaction":
            return "reaction"
        return "capacite"

    ICON_COLS = 10                                       # v53 : tuiles icône + nom (largeur d'écran courante)

    def _render_turn_columns(self, shown: list, spheres: dict) -> None:
        """v53 : barre d'icônes carrées, regroupées par catégorie (attaques, capacités, magie, objets, réactions,
        actions communes) ; une couleur par catégorie (école pour les sorts)."""
        self.turn_tiles = {}
        clear_layout(self.turn_flow)
        order = {k: n for n, (k, _l) in enumerate(self.TILE_CATS)}
        eco = {"Action": 0, "Action bonus": 1, "Réaction": 2, "Gratuit": 3}
        items = [x for x in shown if not x["id"].startswith("inspiration:")
                 and x["id"] != "commune:magie"]          # v52 : sorts et objets ont déjà leurs tuiles
        items.sort(key=lambda x: (order[self._tile_cat(x)], eco.get(x["type"], 4)))
        cols = self.ICON_COLS
        cells = [self._make_tile(x, spheres) for x in items if self._tile_cat(x) != "commune"]
        if self.turn_filter in ("Tout", "Action"):        # v52 : actions d'arme (bottes, actions BG3)
            for key, i, row, weapon in self._weapon_action_rows():
                if R.norm(row.get("action", "")) == "passive":   # botte passive : appliquée à chaque attaque
                    continue
                ok, why = self.engine.weapon_action_state(row)   # v53 : économie d'action et 1 / repos court
                fake = {"id": "arme_action:{}:{}:{}".format(key, i, row["cle"]), "nom": row["nom"], "arme": weapon,
                        "icone": row.get("icone", "⚔"), "type": row.get("action") or "Action", "origine": weapon,
                        "groupe": "", "disponible": ok, "description": "", "cout": "", "raison": why}
                b = self._make_tile(fake, {})
                b.setToolTip(WA.tooltip_html(row, theme.current().accent_text) + (
                             "<p style='color:gray'><i>🎲 Clic : jet d'attaque avec cette arme.</i></p>" if ok else
                             "<p><b>🔒 {}</b></p>".format(why)))
                b.clicked.disconnect()
                b.clicked.connect(lambda _=False, k=key, idx=i, r=row: self._on_weapon_action(k, idx, r))
                cells.append(b)
        common = [self._make_tile(x, spheres) for x in items if self._tile_cat(x) == "commune"]
        from .tile_button import apply_order                # v53 : ordre choisi par le joueur
        saved = list(self.ch.ordre_tuiles or [])
        cells = [cells[k] for k in apply_order([b.tile_id for b in cells], saved)]
        common = [common[k] for k in apply_order([b.tile_id for b in common], saved)]
        self._tile_ids = [b.tile_id for b in cells + common]
        self.turn_order_reset.setVisible(bool(saved))
        n = 0
        for b in cells:
            self.turn_flow.addWidget(b, n // cols, n % cols, Qt.AlignmentFlag.AlignLeft)
            n += 1
        n = (n + cols - 1) // cols * cols                 # actions communes : nouvelle rangée
        for b in common:
            self.turn_flow.addWidget(b, n // cols, n % cols, Qt.AlignmentFlag.AlignLeft)
            n += 1
        for c in range(cols):
            self.turn_flow.setColumnStretch(c, 0)
        self.turn_flow.setColumnStretch(cols, 1)
        pal = theme.icon_palette(theme.current())
        present = {self._tile_cat(x) for x in items}
        legend = {"attaque": "attaque", "capacite": "capacite", "objet": "objet", "reaction": "reaction",
                  "commune": "commune", "magie": "ecole_evocation"}
        self.turn_legend.setText("  ".join("<span style='color:{c}'>■</span> {l}".format(
            c=pal[legend[k]]["cadre"], l=l if k != "magie" else "Magie (couleur de l'école)")
            for k, l in self.TILE_CATS if k in present))

    def _weapon_action_rows(self) -> list:
        """Actions d'arme des armes équipées (main principale, distance) : [(clé de liste, indice, action, arme)]."""
        out = []
        for key in ("armes_cac", "armes_distance"):
            for i, slot in enumerate(getattr(self.ch, key)):
                if key == "armes_cac" and i > 0 or not slot.get("nom"):
                    continue
                if not self.engine.weapon_stats(slot):
                    continue
                for row in self.engine.weapon_actions(slot):
                    out.append((key, i, row, slot["nom"]))
        return out

    def _on_roll_initiative(self) -> None:
        from .dice_dialog import roll_initiative
        roll_initiative(self.win)

    def _on_turn_filter(self, name: str) -> None:
        self.turn_filter = name
        self._refresh_turn()

    def _on_turn_light(self, kind: str) -> None:
        self.engine.toggle_economy(kind)
        self.changed()

    def _on_turn_move(self, value: int) -> None:
        self.engine.set_movement(value * 1.5)            # cases -> mètres
        self._refresh_turn()
        self.win.light_changed()

    def _on_auto_reaction(self) -> None:
        res = self.engine.use_auto_reaction()
        self.win.statusBar().showMessage(res["message"], 6000)
        self.changed()

    def _on_turn_tile(self, tile_id: str) -> None:
        """Tuile : dépense l'action / l'action bonus / la réaction, puis le jet animé (attaque, dés) ou le sort."""
        eng, win = self.engine, self.win
        count = 0
        if tile_id.startswith("objet:"):                  # v52 : charges ou perles à dépenser
            choice = eng.item_count_choice(tile_id)
            if choice and choice["max"] > choice["min"]:
                count = ask_int(win, choice["objet"], "Combien de {} dépenser ({} à {}) ?".format(
                    choice["nom"], choice["min"], choice["max"]), choice["min"], choice["min"], choice["max"])
                if count is None:
                    return
        res = eng.use_turn_action(tile_id, count) if count else eng.use_turn_action(tile_id)
        win.statusBar().showMessage(res["message"], 6000)
        if res.get("sort"):
            from .spell_flow import choose_slot_level, resolve_spell
            magic = getattr(win, "magic_tab", None)
            spell = self.db.find_spell(res["sort"]) or {}
            level = res.get("niveau_effectif", 0) or 0
            ok = magic is not None
            if ok and spell.get("niveau") and res.get("emplacement", True):
                level = choose_slot_level(win, eng, spell)            # 1. niveau d'emplacement (surclassement)
                ok = level is not None
            if ok:                                                     # 2. lancement : emplacement dépensé
                ok = magic.cast(res["sort"], res.get("emplacement", True), level or 0, limit_key=res.get("limite", ""))
            if not ok:                                   # lancement annulé : l'économie d'action est rendue
                from core.turn import spell_economy
                kind = spell_economy(spell)
                if kind == "Action":
                    self.ch.tour_action = False
                elif kind == "Action bonus":
                    self.ch.tour_bonus = False
                elif kind == "Réaction":
                    self.ch.reaction_utilisee = ""
            else:                                        # 3. résolution : attaque, DD de sauvegarde, dégâts, soins
                resolve_spell(win, eng, spell["nom"], getattr(magic, "last_cast_level", 0) or level or 0, "",
                              self._attack_flow)
            self.changed()
            return
        if res.get("rapide"):                             # v53 : emplacement rapide (potion, huile, parchemin)
            self._use_quick(res["rapide"], tile_id)
            self.changed()
            return
        if res.get("potion"):                             # v40 : potion bue par une action bonus
            from .game_widgets import use_consumable
            drinks = eng.drinkable_potions()
            labels = {"{} (×{})".format(p["nom"], p["qte"]): p for p in drinks}
            picked = ask_choice(win, "Boire une potion (action bonus)", "Quelle potion buvez-vous ?", list(labels)) \
                if labels else ""
            if not picked or not use_consumable(win, labels[picked]["source"], labels[picked]["index"]):
                self.ch.tour_bonus = False                # annulé : l'action bonus est rendue
                win.statusBar().showMessage("Aucune potion bue.", 6000)
            self.changed()
            return
        if res.get("objet"):                              # v45 : capacité d'un objet magique
            self._use_item_power(res)
            if res.get("destruction") and res.get("entree") is not None:   # v52 : dernière charge -> d20
                r = roll_damage_dialog(win, D.DamageSpec("Dernière charge — " + res["objet"]["objet"], "1d20",
                                                         kind="de"))
                if r is not None:
                    self._message(eng.resolve_item_destruction(res["entree"], r.total))
            self.changed()
            return
        if res.get("ok") and tile_id == "classe:cap:forme_sauvage":   # v39 : choix de la bête puis transformation
            beasts = sorted(b["nom"] for b in eng.allowed_beasts())
            picked = ask_choice(win, "Forme sauvage", "Quelle bête ?", beasts) if beasts else ""
            if not picked or not eng.assume_form(picked):
                kind = next((t["type"] for t in eng.turn_actions() if t["id"] == tile_id), "Action")
                if kind == "Action bonus":
                    self.ch.tour_bonus = False
                else:
                    self.ch.tour_action = False
                win.statusBar().showMessage("Forme sauvage annulée.", 6000)
            else:
                win.statusBar().showMessage("Forme sauvage : {}.".format(picked), 6000)
            self.changed()
            return
        if res.get("liberer"):                            # v52 : Se libérer (Agrippé / Entravé)
            self._escape(res)
            self.changed()
            return
        if res.get("tests"):                              # v52 : action commune résolue par un test
            self._common_test(res)
            self.changed()
            return
        if res.get("attaque") is not None:
            self._attack_flow(res["attaque"], res.get("degats"), res.get("slot"))
        elif res.get("degats") is not None:
            r = roll_damage_dialog(win, res["degats"])
            if r is not None and res.get("soin"):
                eng.heal(r.total)
        self.changed()

    def _escape(self, res: dict) -> None:
        eng, conds = self.engine, res["liberer"]
        key = conds[0]
        if len(conds) > 1:
            names = {FX.EFFECTS[k]["nom"]: k for k in conds}
            picked = ask_choice(self.win, "Se libérer", "De quel état ?", list(names))
            if not picked:
                return
            key = names[picked]
        dc = res.get("dd", 0)
        if dc:                                            # 2024 : DD de la prise (8 + For + maîtrise de l'agrippeur)
            dc = ask_int(self.win, "Se libérer", "DD de la prise (donné par le MJ, 8 + Force + maîtrise de "
                         "l'agrippeur) :", dc)
            if dc is None:
                return
        spec = eng.skill_spec(res["competence"])
        spec.title = "Se libérer — " + spec.title + (" — DD {}".format(dc) if dc else "")
        r = roll_dice(self.win, spec)
        if r is None:
            return
        if dc:
            success = r.total >= dc
        else:                                             # 2014 : test en opposition, le MJ compare
            success = ask_yes_no(self.win, "Se libérer", "Votre test : {}.\n\nL'emportez-vous sur le jet adverse "
                                 "(ou le DD de l'effet) ?".format(r.total), yes="✔ Réussi", no="✘ Raté",
                                 default_no=False)
        self._message(eng.resolve_escape(key, bool(success), r.total, dc))

    def _common_test(self, res: dict) -> None:
        eng, skills = self.engine, res["tests"]
        if len(skills) > 1:
            rows = {r["nom"]: r for r in eng.skill_rows()}
            labels = {"{} ({:+d})".format(s, rows[s]["bonus"]) if s in rows else s: s for s in skills}
            picked = ask_choice(self.win, res["message"].split(" :")[0], "Quelle compétence ?", list(labels))
            if not picked:
                return
            skill = labels[picked]
        else:
            skill = skills[0]
        spec = eng.skill_spec(skill)
        if res.get("dd"):
            spec.title += " — DD {}".format(res["dd"])
        r = roll_dice(self.win, spec)
        if r is not None:
            self._message(eng.resolve_common_test(res.get("commune", ""), skill, r.total, res.get("dd", 0)))

    def _use_item_power(self, res: dict) -> None:
        """Sort lancé par l'objet (sans emplacement : charges déjà décomptées) -> résolution habituelle (attaque,
        DD, dégâts, soins) ; autre capacité -> rappel de l'effet."""
        from .spell_flow import resolve_spell
        win, info = self.win, res["objet"]
        if res.get("objet_sort"):
            self.engine.item_spell_override = info.get("stats")   # v53 : DD / attaque fixes (Tatouage sortilège)
            try:
                resolve_spell(win, self.engine, res["objet_sort"], int(res.get("objet_niveau") or 0), "",
                              self._attack_flow)
            finally:
                self.engine.item_spell_override = None
        elif info.get("degats"):                          # v53 : capacité qui inflige des dégâts (Vrilles agrippantes)
            if ask_yes_no(win, "[Objet Magique : {}]".format(info["objet"]), "{}\n\n{}\n\nLancer les dégâts (si la "
                          "cible rate son jet de sauvegarde) ?".format(info["message"], info["description"][:600]),
                          yes="Lancer les dégâts", no="Fermer", default_no=False):
                roll_damage_dialog(win, D.DamageSpec("{} — {}".format(info["objet"], info.get("dd", "")),
                                                     info["degats"], info.get("type_degats", "")))
        else:
            ask_yes_no(win, "[Objet Magique : {}]".format(info["objet"]), "{}\n\n{}".format(
                info["message"], info["description"][:900]), yes="OK", no="Fermer", default_no=False)

    # ------------------------------------------------------------------ construction des groupes
    def _weapon_group(self, title: str, key: str, kind: str) -> QGroupBox:
        box = QGroupBox(title)
        g = QGridLayout(box)
        cols = ["Arme", "Maîtrisée", "Magique", "Carac.", "Attaque", "Jet", "Dégâts", "Actions d'arme"]
        if kind == "distance":
            cols.append("Munition")
        cols.append("Détails")
        heads = [head(h) for h in cols]
        for c, h in enumerate(heads):
            g.addWidget(h, 0, c)
        self._box_heads[key] = heads
        rows = []
        for i in range(4):
            w = {"combo": QComboBox(), "prof": prof_toggle(), "magic": QComboBox(), "ab": center(),
                 "atk": center("", "stat"), "dmg": DamageLabel("", "stat"), "acts": QWidget(),
                 "info": make_label("", "muted", wrap=True), "_acts_key": None}
            w["acts_lay"] = QHBoxLayout(w["acts"])
            w["acts_lay"].setContentsMargins(0, 0, 0, 0)
            w["acts_lay"].setSpacing(4)
            w["d20"] = d20_button("Jet d'attaque avec cette arme")
            w["d20"].clicked.connect(lambda _=False, k=key, n=i: self._attack_flow(
                self.engine.weapon_attack_spec(getattr(self.ch, k)[n]),
                self.engine.weapon_damage_spec(getattr(self.ch, k)[n], offhand=(k == "armes_cac" and n == 1)),
                getattr(self.ch, k)[n]))
            w["dmg"].clicked.connect(lambda k=key, n=i: self._roll_weapon_damage(k, n))
            # dégâts + commutateur « 1 main / 2 mains » des armes polyvalentes
            w["dmg_box"] = QWidget()
            db_lay = QHBoxLayout(w["dmg_box"])
            db_lay.setContentsMargins(0, 0, 0, 0)
            db_lay.setSpacing(6)
            w["hands"] = QPushButton("✋ 1 main")
            w["hands"].setCheckable(True)
            w["hands"].setProperty("role", "toggle")
            w["hands"].setCursor(Qt.CursorShape.PointingHandCursor)
            w["hands"].clicked.connect(lambda checked=False, k=key, n=i: self._on_hands(k, n, checked))
            w["power"] = QPushButton("💪 −5/+10")              # v52 : Tireur d'élite / Briseur d'armes lourdes
            w["power"].setCheckable(True)
            w["power"].setProperty("role", "toggle")
            w["power"].setToolTip(rich_tip("Attaque puissante", "−5 au toucher, +10 aux dégâts (Tireur d'élite "
                                           "ou Briseur d'armes lourdes). Même bascule que la tuile « Attaque "
                                           "puissante »."))
            w["power"].clicked.connect(lambda checked=False: self._on_power(checked))
            w["power"].setVisible(False)
            db_lay.addWidget(w["dmg"])
            db_lay.addWidget(w["hands"])
            db_lay.addWidget(w["power"])
            db_lay.addStretch(1)
            order = ["combo", "prof", "magic", "ab", "atk", "d20", "dmg_box", "acts"]
            if kind == "distance":
                w["ammo_box"] = QWidget()
                al = QHBoxLayout(w["ammo_box"])
                al.setContentsMargins(0, 0, 0, 0)
                w["ammo"], w["shoot"] = QComboBox(), QPushButton("🏹 Tirer")
                w["ammo"].setMinimumWidth(170)
                al.addWidget(w["ammo"])
                al.addWidget(w["shoot"])
                w["ammo"].activated.connect(lambda _=0, n=i: self._on_ammo(n))
                w["shoot"].clicked.connect(lambda _=False, n=i: self._on_shoot(n))
                order.append("ammo_box")
            order.append("info")
            w["_order"] = order
            w["magic"].addItems(MAGIC_CHOICES)
            w["combo"].setMinimumWidth(200)
            for c, k in enumerate(order):
                if k in ("prof", "d20"):
                    g.addWidget(w[k], i + 1, c, CENTER)       # case à cocher / dé centrés dans leur colonne
                else:
                    g.addWidget(w[k], i + 1, c)
            w["combo"].activated.connect(lambda _=0, k=key, n=i: self._on_weapon(k, n, True))
            w["magic"].activated.connect(lambda _=0, k=key, n=i: self._on_weapon(k, n, False))
            w["prof"].clicked.connect(lambda _=False, k=key, n=i: self._on_weapon_prof(k, n))
            rows.append(w)
        g.setColumnStretch(6, 2)
        g.setColumnStretch(len(cols) - 1, 3)
        g.setVerticalSpacing(4)
        box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)   # jamais plus haut que son contenu
        self.weapon_rows[key] = rows
        box.setProperty("kind", kind)
        return box

    def _compact_rows(self, key: str, rows: list[dict], filled: list[bool], shown: int) -> None:
        """
        Encart à hauteur adaptative : en-têtes masqués tant qu'aucune arme n'est choisie ; une ligne vide n'affiche
        que son sélecteur ; les lignes au-delà de `shown` ne prennent aucune place.
        """
        filled = list(filled) + [False] * (len(rows) - len(filled))
        for h in self._box_heads.get(key, []):
            h.setVisible(any(filled))
        for i, w in enumerate(rows):
            visible = i < shown
            for k in w["_order"]:
                w[k].setVisible(visible and (k == "combo" or filled[i]))
            retain_when_hidden(w["d20"], False)

    def _cantrip_group(self) -> QGroupBox:
        box = QGroupBox("Sorts mineurs offensifs / utilitaires")
        g = QGridLayout(box)
        heads = [head(h) for h in ["Sort mineur", "Attaque / JS", "Jet", "Dégâts (niveau global)", "Type", "Portée"]]
        for c, h in enumerate(heads):
            g.addWidget(h, 0, c)
        self._box_heads["cantrips"] = heads
        self.cantrip_rows = []
        for i in range(4):
            w = {"combo": QComboBox(), "test": center(), "dmg": DamageLabel("", "stat"), "type": make_label(),
                 "range": make_label("", "muted")}
            w["combo"].setMinimumWidth(200)
            w["d20"] = d20_button("Jet d'attaque de sort")
            w["dmg"].clicked.connect(lambda n=i: self._roll_cantrip_damage(n))
            w["d20"].clicked.connect(lambda _=False, n=i: roll_dice(
                self.win, self.engine.spell_attack_spec(self.ch.sorts_mineurs[n].get("nom", ""))))
            for c, k in enumerate(["combo", "test", "d20", "dmg", "type", "range"]):
                if k == "d20":
                    g.addWidget(w[k], i + 1, c, CENTER)       # dé recadré au centre de sa colonne « Jet »
                else:
                    g.addWidget(w[k], i + 1, c)
            w["combo"].activated.connect(lambda _=0, n=i: self._on_cantrip(n))
            self.cantrip_rows.append(w)
        g.setColumnMinimumWidth(2, 40)
        g.setVerticalSpacing(4)
        box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        g.setColumnStretch(3, 2)
        g.setColumnStretch(5, 1)
        return box

    # ------------------------------------------------------------------ handlers
    def _set(self, attr: str, value):
        setattr(self.ch, attr, value)
        self.changed()

    def _on_death_save(self):
        r = roll_dice(self.win, self.engine.death_save_spec())
        if r is None:
            return
        self.win.statusBar().showMessage(self.engine.apply_death_save(r.natural, r.total), 10000)
        self.changed()

    def _on_death(self):
        self.ch.mort_reussites = sum(b.isChecked() for b in self.ok_boxes)
        self.ch.mort_echecs = sum(b.isChecked() for b in self.ko_boxes)

    def _on_armor(self):
        a = self.ch.armure
        a["nom"] = self.armor.currentText()
        a["bonus"] = int(self.armor_magic.currentText())
        sh = self.shield.currentText()
        a["bouclier"] = sh != "Aucun"
        a["bouclier_nom"] = "" if sh == "Aucun" else sh
        added = [n for n in (a["nom"] if a["nom"] != "Aucune armure" else "", a["bouclier_nom"])
                 if n and self.engine.ensure_in_inventory(n)]
        if added:                                         # armure / bouclier choisis ici : aussi dans le sac
            self.win.statusBar().showMessage("Ajouté à l'inventaire : {}.".format(", ".join(added)), 5000)
        self.changed()

    def _on_weapon(self, key: str, i: int, weapon_changed: bool):
        w = self.weapon_rows[key][i]
        slot = getattr(self.ch, key)[i]
        text = w["combo"].currentText()
        slot["nom"] = "" if text.startswith("—") else text
        slot["bonus"] = int(w["magic"].currentText())
        if weapon_changed and slot["nom"] and self.engine.ensure_in_inventory(slot["nom"]):
            self.win.statusBar().showMessage("{} ajouté(e) à l'inventaire.".format(slot["nom"]), 5000)
        if weapon_changed:
            slot["maitrise"] = None  # retour à la détection automatique
        self.changed()

    def _on_weapon_prof(self, key: str, i: int):
        getattr(self.ch, key)[i]["maitrise"] = self.weapon_rows[key][i]["prof"].isChecked()
        self.changed()

    @staticmethod
    def _style_prof(btn, st) -> None:
        """Pastille de maîtrise : état lisible + indication « automatique / forcée »."""
        on = bool(st and st["maitrise"])
        btn.setText("✦ Maîtrisée" if on else "○ Non maîtrisée")
        if st:
            auto = "détectée automatiquement" if st["maitrise"] == st["auto_maitrise"] else "forcée à la main"
            btn.setToolTip(rich_tip("Maîtrise de l'arme", "Cliquez pour basculer maîtrisée / non maîtrisée "
                                    "({}). La maîtrise ajoute votre bonus de maîtrise au jet d'attaque.".format(auto)))

    def _on_cantrip(self, i: int):
        text = self.cantrip_rows[i]["combo"].currentText()
        self.ch.sorts_mineurs[i]["nom"] = "" if text.startswith("—") else text
        self.changed()

    # ------------------------------------------------------------------ repos, effets, concentration, réactions
    def _message(self, text: str) -> None:
        if text:
            self.win.statusBar().showMessage(text, 6000)

    def _on_rest(self, kind: str):
        done = run_rest(self.win, kind)
        self._message(("Repos long terminé." if kind == "long" else "Repos court terminé.") if done else "")
        self.changed()

    def _fill_fx_picker(self):
        cat = self.fx_cat.currentText()
        keys = [k for k in FX.search(self.fx_search.text(), "" if cat == ALL_CATS else cat)
                if k not in self.ch.effets_actifs]
        current = self.fx_combo.currentData()
        with blocked(self.fx_combo):
            self.fx_combo.clear()
            for i, k in enumerate(keys):
                e = FX.EFFECTS[k]
                self.fx_combo.addItem("{} {}  ·  {}".format(e["icone"], e["nom"], e["categorie"]), k)
                lines = M.mech_lines(k)
                self.fx_combo.setItemData(i, self.engine.effect_tooltip(k) + ("<p><b>Appliqué à la fiche :</b> {}</p>".format(
                    " · ".join(lines)) if lines else ""), Qt.ItemDataRole.ToolTipRole)
            idx = self.fx_combo.findData(current)
            if idx >= 0:
                self.fx_combo.setCurrentIndex(idx)
        self.fx_add.setEnabled(bool(keys))

    def _on_add_effect(self):
        key = self.fx_combo.currentData()
        if key == "metamorphose":                        # état « Métamorphose » : ouvre le tableau des bêtes
            from .druid_tab import start_polymorph
            start_polymorph(self.win, use_slot=False)
            return
        blocked = self.engine.effect_blocked(key) if key else ""
        if blocked:                                      # v52 : immunité aux états
            self.win.statusBar().showMessage(blocked, 8000)
            return
        if key and self.engine.add_effect(key):
            if self.engine.last_effect_message:          # v52 : état neutralisant -> concentration rompue
                self._message(self.engine.last_effect_message)
            self.changed()

    def _on_remove_effect(self, key: str):
        """Retrait d'un effet ; un trait permanent (race / classe) demande confirmation."""
        source = self.engine.innate_source(key)
        if source:
            what = "des traits raciaux" if source.startswith("Trait racial") else "des aptitudes de classe"
            if not ask_yes_no(self.win, "Retirer un trait permanent ?",
                              "Ce bonus fait partie intégrante {} de votre personnage ({}).\n\nÊtes-vous sûr de "
                              "vouloir retirer cet état ?".format(what, source.split(" : ", 1)[-1])):
                return
        self.engine.remove_effect(key)
        self.changed()

    def _on_clear_effects(self):
        n = self.engine.clear_temporary_effects()
        self._message("{} effet(s) temporaire(s) retiré(s) — traits permanents conservés.".format(n))
        self.changed()

    def _on_break_concentration(self):
        old = self.engine.break_concentration()
        self._message("Concentration rompue : {}.".format(old) if old else "")
        self.changed()

    def _on_reaction(self, key: str):
        self.engine.use_reaction(key)
        self.changed()

    def _on_reaction_mode(self, key: str, mode: str):
        self.engine.set_reaction_mode(key, mode)
        self.changed()

    def _on_new_round(self):
        res = self.engine.start_turn()                   # v52 : début de tour + rappels
        lines = ["✔ " + m for m in res["appliques"]] + ["• " + m for m in res["rappels"]]
        self.show_turn_banner("▶ Début de votre tour", lines or ["Rien de particulier à ce début de tour."])
        self.changed()

    def open_environment(self) -> bool:
        from .environment_dialog import EnvironmentDialog
        dlg = EnvironmentDialog(self.win)
        if dlg.exec() and dlg.result_text:
            self._message(dlg.result_text)
            self.changed()
            self.maybe_concentration_save()
            return True
        return False

    def _on_end_combat(self):
        self.show_turn_banner("🏁 Fin du combat", ["• " + m for m in self.engine.end_combat()])
        self.changed()

    def _on_end_turn(self):
        lines = ["• " + m for m in self.engine.end_turn()]
        self.show_turn_banner("⏹ Fin de votre tour", lines or ["Tout a servi : bon tour !"])
        self.changed()

    def show_turn_banner(self, title: str, lines: list) -> None:
        """Bandeau de rappels en tête de « Ce tour-ci » (vide = masqué)."""
        if not title:
            self.turn_banner_text.setText("")
            self.turn_banner.setVisible(False)
            return
        self.turn_banner_text.setText("<b>{}</b><br/>{}".format(html.escape(title), "<br/>".join(
            html.escape(x) for x in lines)))
        self.turn_banner.setVisible(True)

    def _on_ammo(self, i: int):
        self.ch.armes_distance[i]["munition"] = self.weapon_rows["armes_distance"][i]["ammo"].currentData() or ""
        self.changed()

    def _on_shoot(self, i: int):
        self._message(self.engine.shoot(self.ch.armes_distance[i]))
        self.changed()

    def _refresh_effects(self):
        eng, t = self.engine, theme.current()
        keys = eng.active_effect_keys()
        timers = tuple(eng.effect_rounds(k) for k in keys)
        state = (tuple(keys), tuple(eng.innate_effects()), self.ch.concentration, t.key, timers)
        if state != self._fx_key:
            self._fx_key = state
            clear_layout(self.fx_grid)
            for n, k in enumerate(keys):
                e = dict(FX.EFFECTS[k])
                if k == "concentration":                  # icône de concentration : nom du sort en cours
                    e["nom"] = self.ch.concentration
                source = eng.innate_source(k)
                lines = M.mech_lines(k)
                tip = eng.effect_tooltip(k, t.accent_text)  # v52 : texte de l'état selon l'édition
                if k.startswith("epuisement_") and eng.sheet_edition == 2024:     # v52 : règle 2024
                    tip = "<p><b>{}</b> — règle 2024</p><p>{}</p>".format(e["nom"], html.escape(eng.exhaustion_text()))
                    lines = []
                if lines:
                    tip += "<p><b>Appliqué à la fiche :</b> {}</p>".format(" · ".join(lines))
                if source:
                    tip += "<p>🔒 <b>{}</b> — permanent</p>".format(source)
                if k == "concentration":
                    tip += "<p>🧠 Sort en cours : <b>{}</b> — clic : rompre la concentration.</p>".format(
                        self.ch.concentration)
                left = eng.effect_rounds(k)
                short = ""
                if left is not None:                      # v52 : décompte en rounds
                    tip += "<p>⏳ <b>{}</b> — baisse à chaque « ▶ Début de mon tour » et avec le temps qui " \
                           "passe.</p>".format(eng.effect_rounds_text(k))
                    short = "{} r".format(left) if left < 20 else D_.rounds_text(left)
                badge = EffectBadge(k, e["icone"], e["nom"], e["categorie"], tip,
                                    on_remove=self._on_remove_effect, permanent=bool(source), timer=short,
                                    on_extend=self._on_extend_effect if left is not None else None)
                self.fx_grid.addWidget(badge, n // FX_PER_ROW, n % FX_PER_ROW)
            self.fx_grid.setColumnStretch(FX_PER_ROW, 1)
        self.fx_holder.setVisible(bool(keys))
        self.fx_empty.setVisible(not keys)
        self.fx_clear.setEnabled(bool(self.ch.effets_actifs))
        d = eng.defenses()
        parts = []
        for label, field in (("🛡 Résistances", "resistances"), ("💠 Immunités", "immunites")):
            if d[field]:
                parts.append("{} : {}".format(label, ", ".join(dict.fromkeys(x for x, _ in d[field]))))
        self.fx_defenses.setText("   ".join(parts))
        self.fx_defenses.setToolTip(rich_tip("Résistances et immunités", "\n".join(
            "{} — {}".format(x, src) for field in ("resistances", "immunites") for x, src in d[field])) if parts else "")
        n = eng.exhaustion_level()
        self.exh_label.setText("Niveau {}".format(n) if n else "aucun")   # v52 : l'effet est dans l'infobulle
        tip = rich_tip("Épuisement — niveau {} / 6".format(n), eng.exhaustion_text() if n else
                       "Aucun niveau d'épuisement.")
        for w in (self.exh_label, self.exh_minus, self.exh_plus):
            w.setToolTip(tip)
        t = theme.current()
        for b in (self.exh_minus, self.exh_plus):         # suit le thème choisi
            b.setStyleSheet("QPushButton {{ padding: 0px; font-weight: bold; font-size: 17px; color: {}; }}"
                            "QPushButton:disabled {{ color: {}; }}".format(t.accent_text, t.locked))
        self.exh_minus.setEnabled(n > 0)
        self.exh_plus.setEnabled(n < 6)
        lines = eng.effect_summary_lines()
        self.fx_summary.setText("Modificateurs en vigueur : " + " · ".join(lines) if lines else "")
        self._fill_fx_picker()

    def _refresh_concentration(self):
        name = self.ch.concentration
        self.conc_label.setVisible(bool(name))
        self.conc_btn.setVisible(bool(name))
        if name:
            self.conc_label.setText("🧠 Concentration en cours : {}{} — lancer un autre sort de concentration la "
                                    "romprait. Un JS de Constitution (DD 10 ou moitié des dégâts) est requis quand "
                                    "vous subissez des dégâts.".format(name, " (lancé sur un allié)"
                                                                       if self.ch.concentration_cible == "allie" else "")
                                    + (" ⏳ " + self.engine.effect_rounds_text("concentration") + "."
                                       if self.engine.effect_rounds("concentration") is not None else ""))

    def _refresh_weapon_extras(self, key: str, i: int, w: dict, slot: dict, st):
        """Pastilles d'actions d'arme (infobulle riche immédiate) et sélecteur de munitions."""
        rows = self.engine.weapon_actions(slot) if st else []
        acts_key = (tuple((r["cle"], r["dd"]) for r in rows), theme.current().key)
        if acts_key != w["_acts_key"]:
            w["_acts_key"] = acts_key
            clear_layout(w["acts_lay"])
            for r in rows:
                label = r["nom"] + (" (DD {})".format(r["dd"]) if r["dd"] else "")
                tip = WA.tooltip_html(r, theme.current().accent_text) + \
                    "<p style='color:gray'><i>🎲 Clic : jet d'attaque avec cette arme.</i></p>"
                w["acts_lay"].addWidget(ActionChip(r["icone"], label, tip,
                                                   on_click=lambda k=key, n=i, row=r: self._on_weapon_action(k, n, row)))
            w["acts_lay"].addStretch(1)
        if "ammo" not in w:
            return
        opts = self.engine.ammo_options(slot) if st else []
        has_ammo = bool(st) and bool(self.engine.ammo_kind(self.db.weapons.get(slot.get("nom", ""), {})))
        w["ammo_box"].setEnabled(has_ammo)
        with blocked(w["ammo"]):
            w["ammo"].clear()
            w["ammo"].addItem(NO_AMMO, "")
            for a in opts:
                w["ammo"].addItem("{}{} — stock {}".format(a["nom"], " ✦" if a["magique"] else "", a["qte"]), a["nom"])
            idx = w["ammo"].findData(slot.get("munition", ""))
            w["ammo"].setCurrentIndex(max(0, idx))
        chosen = self.engine.selected_ammo(slot)
        w["ammo"].setToolTip(rich_tip(chosen["nom"], chosen["description"] or "Munition choisie.") if chosen else
                             rich_tip("Munitions", "Ajoutez des munitions (Munitions, Billes, objets magiques "
                                      "« Munition +1 »…) dans l'Inventaire pour les choisir ici." if not opts else
                                      "Choisissez la munition tirée : son bonus magique s'ajoute à l'attaque et aux "
                                      "dégâts, et « Tirer » décompte le stock."))
        w["shoot"].setEnabled(has_ammo and any(a["qte"] > 0 for a in opts))

    # ------------------------------------------------------------------ forme sauvage
    def _on_hp_cur(self, value: int):
        """PV actuels : ceux de la bête tant qu'une transformation est active, sinon ceux du personnage."""
        if self.ch.forme_active:
            self._on_form_hp(value)
        else:
            self._set("pv_actuels", value)

    def _on_form_hp(self, value: int):
        self.ch.forme_pv = value
        if value <= 0 and self.ch.forme_active:
            self.engine.end_form()
        self.changed()

    def _on_form_damage(self):
        self._message(self.engine.damage_form(self.form_dmg.value()))
        self.form_dmg.setValue(0)
        self.changed()
        self.maybe_concentration_save()
        self.maybe_zero_hp()                              # v52 : fin de transformation, puis 0 PV éventuel

    def _on_moon_heal(self):
        text = self.moon_lvl.currentText()
        if not text:
            return
        res = self.engine.moon_heal(int(text.split()[-1]))
        if res:
            self._message("🌙 Emplacement de niveau {} dépensé : {} = +{} PV pour la bête.".format(
                res["niveau"], " + ".join(map(str, res["des"])), res["gain"]))
        self.changed()

    def _on_form_end(self):
        self.engine.end_form()
        self.changed()

    def _refresh_form(self):
        eng, ch = self.engine, self.ch
        beast = eng.wild_form()
        self.form_box.setVisible(beast is not None)
        self.beast_box.setVisible(beast is not None)
        titles = ["Armes de corps à corps (CaC)", "Armes à distance", "Sorts mineurs offensifs / utilitaires"]
        for box, title in zip(self.weapon_boxes + [self.cantrip_box], titles):
            box.setEnabled(beast is None)                # armes et sorts indisponibles sous forme animale
            box.setTitle(title + ("  — indisponible sous forme animale" if beast is not None else ""))
        if beast is None:
            return
        hp_max = eng.beast_hp_max(beast["nom"])
        c = beast["carac"]
        poly = ch.forme_type == "metamorphose"
        self.form_box.setTitle("🦋 Métamorphose active" if poly else "🐾 Forme sauvage active")
        self.beast_box.setTitle("{} Attaques de la bête : {} ({}) — modificateurs de la créature".format(
            "🦋" if poly else "🐺", beast["nom"], "Métamorphose" if poly else "Forme sauvage"))
        self.beast_box.setToolTip("<qt><b>{}</b></qt>".format(eng.form_status()["libelle"]))
        self.form_end.setText("Mettre fin à la Métamorphose" if poly else "Reprendre sa forme normale")
        kept = ("INT {} SAG {} CHA {} de la bête (Métamorphose : toutes les caractéristiques sont remplacées ; "
                "concentration du lanceur requise)".format(c["INT"][0], c["SAG"][0], c["CHA"][0]) if poly else
                "INT, SAG, CHA, maîtrises et alignement du druide conservés")
        hp_note = ("vous gardez vos PV ({}/{}) et vos PV temporaires de forme (2024)".format(ch.pv_actuels, eng.hp_max())
                   if eng.wild_shape_2024() else "vos PV ({}/{}) sont mis de côté".format(ch.pv_actuels, eng.hp_max()))
        self.form_info.setText("{} — CA {} — vitesse {} — FOR {} DEX {} CON {} — {} — {}".format(
            beast["nom"], eng.beast_ac(beast), beast["vitesse"], c["FOR"][0], c["DEX"][0], c["CON"][0], kept, hp_note))
        self.form_hp.setVisible(not eng.wild_shape_2024())   # 2024 : pas de PV de bête
        with blocked(self.form_hp):
            self.form_hp.setRange(0, hp_max)
            self.form_hp.setValue(ch.forme_pv)
            self.form_hp.setSuffix(" / {}".format(hp_max))
        moon = eng.moon_heal_available()
        levels = eng.moon_heal_levels() if moon else []
        fill_combo(self.moon_lvl, ["Niveau {}".format(n) for n in levels], self.moon_lvl.currentText())
        for w in (self.moon_lvl, self.moon_btn, self.moon_caption):
            w.setVisible(moon)
        self.moon_btn.setEnabled(bool(levels) and ch.forme_pv < hp_max)
        attacks = eng.beast_attacks()
        key = (beast["nom"], tuple(a["attaque"] for a in attacks), theme.current().key)
        if key == self._beast_key:
            return
        self._beast_key = key
        clear_layout(self.beast_grid)
        for col, h in enumerate(["Attaque", "Bonus", "Jet", "Dégâts", "Portée", "Détail"]):
            self.beast_grid.addWidget(head(h), 0, col)
        for r, a in enumerate(attacks, start=1):
            spec = eng.beast_attack_spec(a)
            tip = calc_tip("{} — {}".format(beast["nom"], a["nom"]), [(t.label, t.text().split(" (")[0])
                                                                      for t in spec.terms], R.fmt_bonus(a["attaque"]))
            name = make_label(a["nom"], "head")
            bonus = make_label(R.fmt_bonus(a["attaque"]), "stat")
            bonus.setToolTip(tip)
            btn = d20_button("Attaque : " + a["nom"])
            btn.clicked.connect(lambda _=False, att=a: roll_dice(self.win, self.engine.beast_attack_spec(att)))
            dmg = DamageLabel("{} {}".format(a["degats"], a["type"]).strip(), "stat")
            dmg.set_formula(a["degats"])
            dmg.clicked.connect(lambda att=a, b=beast["nom"]: roll_damage_dialog(
                self.win, D.DamageSpec("{} — {}".format(b, att["nom"]), att["degats"], att["type"])))
            info = make_label("FOR/DEX de la bête : {} {:+d} · maîtrise +{}".format(
                a["carac"], a["mod"], a["maitrise"]), "muted", wrap=True)
            for col, w in enumerate((name, bonus, btn, dmg, make_label(a["portee"], "muted"), info)):
                if w is btn:
                    self.beast_grid.addWidget(w, r, col, CENTER)
                else:
                    self.beast_grid.addWidget(w, r, col)
        if not attacks:
            self.beast_grid.addWidget(make_label("Aucune attaque chiffrée pour cette bête.", "muted"), 1, 0, 1, 6)
        self.beast_grid.setColumnStretch(5, 1)

    # ------------------------------------------------------------------ capacités raciales de combat
    NO_COLOR = "— choisir la couleur —"

    def _color_tips(self) -> dict:
        return {c: rich_tip("Dragon " + c.lower(), "Dégâts : {} — souffle : {} — JS de {}".format(t, z, js))
                for c, (t, z, js) in X.DRACONIC.items()}

    def _on_race_color(self, combo):
        text = combo.currentText()
        self.ch.ascendance_raciale = "" if text.startswith("—") else text
        self.changed()

    def _on_sorc_color(self, combo):
        text = combo.currentText()
        self.ch.ascendance_ensorceleur = "" if text.startswith("—") else text
        self.changed()

    def _on_breath_orb(self, used: int):
        self.engine.set_resource_used("souffle", used)
        self.changed()

    def _refresh_racial(self):
        """Encart des capacités raciales de combat : souffle draconique calculé selon la couleur, armes naturelles,
        réactions chiffrées… + lignée de l'Ensorceleur draconique. Masqué si le personnage n'en a aucune."""
        eng, t = self.engine, theme.current()
        traits = eng.racial_combat_traits()
        breath = eng.breath_weapon()
        sorc = eng.is_draconic_sorcerer()
        self.racial_box.setVisible(bool(traits or sorc))
        key = (self.ch.race, self.ch.ascendance_raciale, self.ch.ascendance_ensorceleur, eng.total_level,
               eng.prof, eng.mod("Constitution"), eng.mod("Charisme"), sorc, bool(breath and breath["utilise"]), t.key)
        if key == self._racial_key:
            return
        self._racial_key = key
        clear_layout(self.racial_layout)
        tips = self._color_tips()
        if breath is not None:
            row = QHBoxLayout()
            row.addWidget(make_label("🐉 Couleur du dragon ancestral ({})".format(self.ch.race), "head"))
            combo = QComboBox()
            fill_combo(combo, [self.NO_COLOR] + list(X.DRACONIC), breath["couleur"] or self.NO_COLOR, tips)
            combo.setToolTip(rich_tip("Ascendance draconique", "Détermine le type de dégâts et la zone du souffle, "
                                      "le jet de sauvegarde et la résistance draconique (état permanent 🔒)."))
            combo.activated.connect(lambda _=0, c=combo: self._on_race_color(c))
            row.addWidget(combo)
            row.addStretch(1)
            self.racial_layout.addLayout(row)
            card = QHBoxLayout()
            if breath["type"]:
                text = ("<b>Souffle draconique ({t})</b> — {z} — JS de {js} <b>DD {dd}</b> — <b>{d} {t}</b>, moitié "
                        "en cas de réussite — action — 1 fois par repos court ou long (bouton « Utiliser » de "
                        "l'encart Actions)").format(
                    t=breath["type"], z=breath["zone"], js=breath["js"], dd=breath["dd"], d=breath["degats"])
            else:
                text = "<b>Souffle draconique</b> — choisissez la couleur de votre dragon ancestral pour le calculer."
            lab = make_label(text, wrap=True)
            lab.setToolTip(calc_tip("Souffle draconique", [
                ("DD : 8", "8"), ("Maîtrise", R.fmt_bonus(eng.prof)),
                (R.mod_label("Constitution"), R.fmt_bonus(eng.mod("Constitution")))], "DD {}".format(breath["dd"]),
                ["Dégâts : 2d6, 3d6 au niveau 6, 4d6 au niveau 11, 5d6 au niveau 16 (niveau de personnage)."]))
            card.addWidget(lab, 1)                       # sphère d'utilisation : encart Actions (classe et race)
            self.racial_layout.addLayout(card)
        for tr in traits:
            if tr["souffle"] and breath is not None:
                continue                                 # déjà présenté sous forme calculée
            lab = make_label("<b>{}</b> — {}".format(tr["nom"], formula_html(eng, tr["description"])), wrap=True)
            lab.setToolTip(rich_tip(tr["nom"], tr["description"]))
            self.racial_layout.addWidget(lab)
        if sorc:
            row = QHBoxLayout()
            row.addWidget(make_label("🔥 Lignée draconique (Ensorceleur) — dragon ancestral", "head"))
            combo = QComboBox()
            lineage = eng.sorcerer_lineage()
            fill_combo(combo, [self.NO_COLOR] + list(X.DRACONIC), lineage["couleur"] if lineage else self.NO_COLOR, tips)
            combo.setToolTip(rich_tip("Ancêtre dragon", "Détermine le type de dégâts de l'Affinité élémentaire "
                                      "(niveau 6) et de la Résilience draconique."))
            combo.activated.connect(lambda _=0, c=combo: self._on_sorc_color(c))
            row.addWidget(combo)
            row.addStretch(1)
            self.racial_layout.addLayout(row)
            if lineage:
                info = ("Type de dégâts : <b>{}</b>. ".format(lineage["type"])
                        + ("Affinité élémentaire : +{} (modificateur de Charisme) à un jet de dégâts de vos sorts de "
                           "{} ; vous pouvez dépenser 1 point de sorcellerie pour gagner la résistance à ce type "
                           "pendant 1 heure.".format(lineage["bonus_degats"], lineage["type"])
                           if lineage["niveau"] >= 6 else "Affinité élémentaire au niveau 6 d'ensorceleur."))
                self.racial_layout.addWidget(make_label(info, "muted", wrap=True))

    # ------------------------------------------------------------------ ressources (rage, ki)
    def _rebuild_resources(self, trackers: list[dict]):
        while self.res_layout.count():
            item = self.res_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)            # retrait immédiat (pas de superposition à l'écran)
                item.widget().deleteLater()
        self.res_rows = []
        for r, tr in enumerate(trackers):
            w = {"key": tr["key"], "label": make_label(tr["label"], "head"), "left": center("", "stat"),
                 "info": make_label(tr["info"], "muted")}
            if tr["total"] is None:                       # Barbare niveau 20 : rages illimitées
                w["orbs"] = make_label("∞  illimitées", "stat")
            else:
                # grande réserve de points (Imposition des mains) : jauge ; sinon sphères
                w["orbs"] = GaugeBar() if tr["kind"] == "jauge" else OrbBar(tr["kind"])
                w["orbs"].changed.connect(lambda used, k=tr["key"]: self._on_orbs(k, used))
            if tr.get("de"):                              # dés de supériorité / d'inspiration : taille du dé
                w["label"].setText("{} ({})".format(tr["label"], tr["de"]))
            # v52 : colonne étroite — nom et compteur sur une ligne, sphères dessous, détail en infobulle
            w["label"].setToolTip(rich_tip(tr["label"], tr["info"]))
            w["info"].setVisible(False)
            self.res_layout.addWidget(w["label"], 2 * r, 0)
            self.res_layout.addWidget(w["left"], 2 * r, 1)
            self.res_layout.addWidget(w["orbs"], 2 * r + 1, 0, 1, 2)
            self.res_layout.addWidget(w["info"], 2 * r + 1, 2)
            self.res_rows.append(w)
        self.res_layout.setColumnStretch(0, 1)

    def _on_orbs(self, key: str, used: int):
        """Clic sur une sphère : la sphère s'est déjà redessinée ; on met à jour le compteur sans tout recalculer."""
        self.engine.set_resource_used(key, used)
        if key in ("rage", "forme"):                   # l'état actif change (et les dégâts de rage) : recalcul complet
            self.changed()
            return
        for tr, w in zip(self.engine.resource_trackers("combat"), self.res_rows):
            if tr["key"] == key and tr["total"] is not None:
                w["left"].setText("{} / {}".format(tr["total"] - self.engine.resource_used(key), tr["total"]))
        self._refresh_actions()                      # une sphère récupérée / dépensée (dé)verrouille les actions
        self.win.light_changed()

    def _refresh_resources(self):
        """Compteurs visibles seulement si le personnage possède la ressource (Barbare, Moine niveau 2+)."""
        eng = self.engine
        trackers = eng.resource_trackers("combat")
        key = tuple((t["key"], t["total"]) for t in trackers)
        if key != self._res_key:
            self._rebuild_resources(trackers)
            self._res_key = key
        actions = self._refresh_actions()
        passives = self._refresh_passives()
        racial = any(a.get("origine") == "race" for a in actions)
        self.res_box.setTitle("Ressources")              # v52 : les actions sont des tuiles ; ici, les compteurs
        self.res_sep.setVisible(bool(trackers) and bool(actions))
        self.res_box.setVisible(bool(trackers) or bool(passives))   # v52 : les actions sont des tuiles
        for tr, w in zip(trackers, self.res_rows):
            if tr["total"] is None:
                w["left"].setText("")
                continue
            used = eng.resource_used(tr["key"])
            w["orbs"].set_state(tr["total"], used)
            w["left"].setText("{} / {}".format(tr["total"] - used, tr["total"]))

    def _refresh_vision(self):
        """Encart « Vision dans le noir » : portée lue dans les traits de l'espèce, sinon « Vision normale »."""
        dv = self.engine.darkvision()
        box, lab = self.stat_boxes["vision"], self.stat_labels["vision"]
        if dv["portee"]:
            box.setTitle("Vision dans le noir")
            lab.setText(("🌑 {:g} m" + (" ✦" if dv.get("magique") else "")).format(dv["portee"]).replace(".", ","))
            lab.setToolTip(rich_tip("Vision dans le noir{}{} — {:g} m".format(
                " supérieure" if dv["superieure"] else "",
                " (ténèbres magiques comprises)" if dv.get("magique") else "", dv["portee"]).replace(".", ","),
                "{}\n<i>Source : {}</i>".format(dv["detail"], dv["source"])))
        else:
            box.setTitle("Vision")
            lab.setText("👁 Normale")
            lab.setToolTip(rich_tip("Vision normale", "Votre espèce ne voit pas dans le noir : dans les ténèbres, "
                                    "vous êtes aveuglé ; dans la pénombre, désavantage aux tests de Sagesse "
                                    "(Perception) basés sur la vue."))

    def _refresh_saves(self):
        """● = maîtrise ; ▲ / ▼ = avantage / désavantage ; infobulle : détail du calcul."""
        for row in self.engine.save_rows():
            w = self.save_cells.get(row["carac"])
            if w is None:
                continue
            mark = {"avantage": " ▲", "désavantage": " ▼", "échec": " ✖"}.get(row["etat"], "")
            w["label"].setText("{} {} {}{}".format("●" if row["maitrise"] else "○", R.ABBR[row["carac"]],
                                                   R.fmt_bonus(row["bonus"]), mark))
            notes = (["Avantage : " + ", ".join(row["avantage"])] if row["avantage"] else []) + \
                    (["Désavantage : " + ", ".join(row["desavantage"])] if row["desavantage"] else [])
            w["label"].setToolTip(calc_tip("Jet de sauvegarde de " + row["carac"], row["detail"],
                                           R.fmt_bonus(row["bonus"]), notes or None))

    # ------------------------------------------------------------------ actions spéciales de classe
    def _refresh_actions(self) -> list[dict]:
        """Lignes d'actions (Déluge de coups, Second souffle, Châtiment divin...) : verrouillées si la ressource
        nécessaire est épuisée ; mention courte de l'effet de l'option choisie à droite du bouton."""
        eng = self.engine
        actions = eng.class_actions()
        conduits = {a["classe"]: eng.channel_options(a["classe"]) for a in actions if a.get("choix") == "conduit"}
        key = tuple((a["id"], tuple(o["nom"] for o in conduits.get(a["classe"], [])) if a.get("choix") == "conduit"
                     else ()) for a in actions)
        if key != self._act_key:
            self._rebuild_actions(actions, conduits)
            self._act_key = key
        t = theme.current()
        for a, w in zip(actions, self.act_rows):
            ok = a["disponible"]
            w["btn"].setEnabled(ok)
            w["btn"].setText("Mettre fin" if a.get("actif") else "Utiliser")
            w["name"].setStyleSheet("" if ok else "color: {};".format(t.locked))
            w["cost"].setText(a["cout_txt"] or "—")
            free_roll = a.get("jet") == "attaque_mains_nues" or not a.get("cout")
            w["dmg"].setText(a["formule"] or "—")
            w["dmg"].set_formula(a["formule"] if free_roll else "", "" if free_roll else
                                 "Ce dé est lancé par le bouton « Utiliser » (la ressource est alors dépensée).")
            w["locked"] = "" if ok else a["raison"]
            self._update_hint(a["id"])
            if a["id"] == "imposition" and "amount" in w:
                left = eng.lay_on_hands_left()
                w["amount"].setRange(1, max(1, left))
                w["amount"].setEnabled(left > 0)
                w["target"].setEnabled(left > 0)
        return actions

    RUSE_HINTS = {"Foncer": "Déplacement supplémentaire égal à votre vitesse ce tour-ci.",
                  "Se désengager": "Votre déplacement ne provoque pas d'attaque d'opportunité ce tour-ci.",
                  "Se cacher": "Test de Dextérité (Discrétion) pour devenir caché."}

    def _update_hint(self, aid: str) -> None:
        """Mention courte à droite du bouton : effet de la manœuvre / du Conduit divin / de la ruse choisie,
        ou la raison du verrouillage."""
        from core.class_actions import short_text
        w = self._action_row(aid)
        if w is None:
            return
        if w.get("locked"):
            w["state"].setText("🔒 " + w["locked"])
            w["state"].setProperty("role", "warn")
            w["state"].setStyleSheet("color: {};".format(theme.current().warn))
            return
        text, tip = "", ""
        kind = w.get("choix", "")
        if kind == "manoeuvres":
            name = w["option"].currentText()
            tip = self.db.maneuvers.get(name, "")
            text = short_text(tip) + " (DD {})".format(self.engine.maneuver_dc())
        elif kind == "ruse":
            text = self.RUSE_HINTS.get(w["option"].currentText(), "")
        elif kind == "conduit":
            opts = w.get("options", [])
            idx = w["option"].currentIndex()
            if opts and 0 <= idx < len(opts):
                text, tip = opts[idx]["court"], opts[idx]["description"]
            elif not opts:
                text = "Choisissez votre serment / domaine (onglet Classes) pour afficher ses options."
        w["state"].setText(text)
        w["state"].setStyleSheet("color: {};".format(theme.current().muted))
        w["state"].setToolTip(rich_tip(w["option"].currentText(), tip) if tip else "")

    def _rebuild_actions(self, actions: list[dict], conduits: dict | None = None):
        clear_layout(self.act_layout)
        self.act_rows = []
        conduits = conduits or {}
        if not actions:
            return
        for c, h in enumerate(["Action", "Type", "Coût", "Jet / dé", "", "Option", "Effet"]):
            self.act_layout.addWidget(head(h), 0, c)
        for r, a in enumerate(actions, start=1):
            name = make_label("{} {}".format(a.get("icone", "⚔"), a["nom"]), "head")
            origin = ("Race : {}{}".format(a["race"], " — niv. {}".format(a["niveau"]) if a["niveau"] > 1 else "")
                      if a.get("origine") == "race" else "{} niv. {}{}".format(
                          a["classe"], a["niveau"], " ({})".format(a["sous_classe"]) if a.get("sous_classe") else ""))
            name.setToolTip(rich_tip(a["nom"], "{}\n<i>{} — {}</i>".format(a["description"], a["type"], origin)))
            btn = QPushButton("Utiliser")
            btn.setMinimumWidth(96)
            jet = a.get("jet", "aucun")
            if jet == "attaque_mains_nues":
                btn.setIcon(d20_icon(20))
            elif a.get("formule"):
                groups, _ = D.parse_damage(a["formule"])
                btn.setIcon(die_icon(groups[0][2] if groups else 6, 20))
            btn.setToolTip(rich_tip(a["nom"], a["description"] + ("\n<b>Coût : {}</b> (dépensé au clic)".format(
                a["cout_txt"]) if a["cout_txt"] and a["cout_txt"] != "—" else "") +
                ("\n<b>Consomme votre réaction du round.</b>" if a.get("type") == "Réaction" else "")))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _=False, aid=a["id"]: self._on_action(aid))
            dmg = DamageLabel("", "stat")
            dmg.clicked.connect(lambda aid=a["id"]: self._roll_action_damage(aid))
            option = QComboBox()
            options = conduits.get(a["classe"], []) if a.get("choix") == "conduit" else []
            choices = (list(self.db.maneuvers) if a.get("choix") == "manoeuvres" else
                       list(self.db.cunning_actions) if a.get("choix") == "ruse" else
                       [o["nom"] for o in options])
            option.addItems(choices)
            option.setVisible(bool(choices))
            for i, n in enumerate(choices):
                desc = self.db.maneuvers.get(n) if a.get("choix") == "manoeuvres" else \
                    options[i]["description"] if a.get("choix") == "conduit" else ""
                if desc:
                    option.setItemData(i, rich_tip(n, desc), Qt.ItemDataRole.ToolTipRole)
            option.currentIndexChanged.connect(lambda _=0, aid=a["id"]: self._update_hint(aid))
            extra = {}
            if a.get("choix") == "imposition":            # Imposition des mains : points à dépenser + cible
                box = QWidget()
                bl = QHBoxLayout(box)
                bl.setContentsMargins(0, 0, 0, 0)
                bl.setSpacing(4)
                extra["amount"] = QSpinBox()
                extra["amount"].setRange(1, 100)
                extra["amount"].setSuffix(" PV")
                extra["amount"].setToolTip("Points puisés dans la réserve")
                extra["target"] = QComboBox()
                extra["target"].addItems(LAY_ON_HANDS_TARGETS)
                bl.addWidget(extra["amount"])
                bl.addWidget(extra["target"])
                option = box
            w = {"id": a["id"], "name": name, "type": make_label(a["type"], "muted"),
                 "cost": center("", "muted"), "btn": btn, "dmg": dmg, "option": option,
                 "state": make_label("", "muted", wrap=True), "choix": a.get("choix", ""), "options": options,
                 "locked": "", **extra}
            for c, k in enumerate(("name", "type", "cost", "dmg", "btn", "option", "state")):
                self.act_layout.addWidget(w[k], r, c)
            self.act_rows.append(w)
        self.act_layout.setColumnStretch(0, 2)
        self.act_layout.setColumnStretch(6, 4)

    def _refresh_passives(self) -> list[dict]:
        """Sous-section « Passifs de classe » : nom de chaque capacité passive, description complète en infobulle."""
        passives = self.engine.class_passives()
        key = tuple(p["nom"] for p in passives)
        if key != self._pass_key:
            self._pass_key = key
            clear_layout(self.pass_layout)
            for n, p in enumerate(passives):
                tip = ("<div style='max-width:380px'><p><b>{}</b> <i>— {}</i></p><p>{}</p></div>").format(
                    html.escape(p["nom"]), html.escape(p["source"]), html.escape(p["description"]))
                self.pass_layout.addWidget(ActionChip("◈", p["nom"], tip), n // 2, n % 2)   # colonne étroite
            self.pass_layout.setColumnStretch(4, 1)
        self.pass_title.setVisible(bool(passives))
        return passives

    def _action_row(self, aid: str) -> dict | None:
        return next((w for w in self.act_rows if w["id"] == aid), None)

    def _on_action(self, aid: str):
        """Utiliser : dépense immédiate de la ressource (sphère), état associé, puis jet animé."""
        eng, win = self.engine, self.win
        a = next((x for x in eng.class_actions() if x["id"] == aid), None)
        if a is None:
            return
        if aid == "cap:forme_sauvage":                    # même flux que la tuile du tour (choix de la bête)
            self._on_turn_tile("classe:cap:forme_sauvage")
            return
        row = self._action_row(aid)
        if aid == "imposition" and row is not None:
            target = row["target"].currentIndex()
            res = eng.use_lay_on_hands(row["amount"].value(), "allie" if target == 1 else "soi", cure=target == 2)
            win.statusBar().showMessage(res["message"], 8000)
            self.changed()
            return
        choice = row["option"].currentText() if row and a.get("choix") in ("manoeuvres", "ruse", "conduit") else ""
        slot = 0
        if (a.get("cout") or {}).get("emplacement"):
            levels = eng.smite_levels()
            if len(levels) > 1:
                labels = {"Emplacement de niveau {} — {}".format(lvl, eng.class_action_formula(a, lvl)): lvl
                          for lvl in levels}
                picked = ask_choice(win, a["nom"], "Quel emplacement de sort dépenser ?", list(labels))
                if not picked:
                    return
                slot = labels[picked]
            elif levels:
                slot = levels[0]
        if a.get("depense_si_reussite"):                 # dé lancé d'abord, dépensé seulement si le jet réussit
            spec = eng.class_action_preview(aid)
            r = roll_damage_dialog(win, spec) if spec else None
            if r is None or not ask_yes_no(win, a["nom"], "Résultat du dé : +{}.\n\nLe jet réussit-il maintenant ? "
                                           "(Le dé psionique n'est dépensé qu'en cas de réussite.)".format(r.total),
                                           yes="Oui : dépenser le dé", no="Non : le garder"):
                win.statusBar().showMessage("{} : dé conservé.".format(a["nom"]), 6000)
                return
            res = eng.use_class_action(aid, slot, choice)
            win.statusBar().showMessage(res["message"], 6000)
            self.changed()
            return
        res = eng.use_class_action(aid, slot, choice)
        win.statusBar().showMessage(res["message"], 6000)
        if not res["ok"]:
            self.changed()
            return
        if res["attaque"] is not None:
            weapon = eng.action_weapon_slot(a) if a and a.get("attaque_arme") else None
            self._attack_flow(res["attaque"], res.get("degats"), weapon)   # Déluge de coups… : dégâts si l'attaque touche
        elif res["degats"] is not None and res.get("lancer_maintenant", True):
            r = roll_damage_dialog(win, res["degats"])
            if r is not None and res["soin"]:
                gained = eng.heal(r.total)
                win.statusBar().showMessage("{} : +{} PV (jet {}).".format(a["nom"], gained, r.total), 8000)
        self.changed()

    def _roll_action_damage(self, aid: str):
        a = next((x for x in self.engine.class_actions() if x["id"] == aid), None)
        if a and a["formule"]:
            roll_damage_dialog(self.win, D.DamageSpec(a["nom"], a["formule"], a.get("type_degats", "")))

    def _refresh_hands(self, w: dict, st: dict) -> None:
        """v46 — indicateur de prise des armes polyvalentes, déterminée AUTOMATIQUEMENT par la main secondaire :
        libre -> à deux mains (dé supérieur), bouclier ou seconde arme -> à une main."""
        show = bool(st.get("polyvalente"))
        w["hands"].setVisible(show)
        if not show:
            return
        with blocked(w["hands"]):
            w["hands"].setChecked(st["deux_mains"])
        w["hands"].setText("🙌 À deux mains" if st["deux_mains"] else "✋ À une main")
        w["hands"].setEnabled(False)                    # prise automatique : pas de bascule manuelle
        w["hands"].setToolTip(rich_tip(
            "Arme polyvalente — prise automatique", "À une main : {}\nÀ deux mains : {}\n{}".format(
                st["calcul_1m"] or st["degats_1m"], st["calcul_2m"] or st["degats_2m"],
                "Main secondaire libre : l'arme est tenue à deux mains." if st["deux_mains"] else
                "Main secondaire occupée (bouclier ou seconde arme) : l'arme est tenue à une main.")))

    def _on_hands(self, key: str, i: int, checked: bool):
        """Conservé pour compatibilité : la prise suit désormais la main secondaire (v46)."""
        self.changed()

    def _on_weapon_action(self, key: str, i: int, row: dict):
        """Action d'arme (Sape, Brise-crâne, Frappe affaiblissante…) : dépense l'action (ou l'action bonus) et son
        utilisation (1 / repos court), puis jet d'attaque de l'arme équipée."""
        res = self.engine.use_weapon_action(row)          # v53 : plus de « spam » des actions d'arme
        self.win.statusBar().showMessage(res["message"], 6000)
        if not res["ok"]:
            return
        slot = getattr(self.ch, key)[i]
        self._attack_flow(self.engine.weapon_action_spec(slot, row), self.engine.weapon_damage_spec(slot), slot)
        self.changed()

    def _attack_flow(self, attack_spec, damage_spec=None, slot=None) -> bool:
        """Jet de toucher (d20 animé) puis « L'attaque touche-t-elle ? » : OUI -> dés de dégâts animés (dés doublés
        sur un 20 naturel), NON -> on ferme. Un 1 naturel rate toujours. Renvoie True si des dégâts ont été lancés."""
        win = self.win
        r = roll_dice(win, attack_spec)
        if r is not None:
            self.engine.reveal_after_attack()            # v52 : attaquer met fin à l'état Caché
            if slot is not None:
                shot = self.engine.fire_ammo(slot)        # v52 : une munition par attaque
                if shot:
                    self.win.statusBar().showMessage(shot, 6000)
        if r is None or damage_spec is None:
            return False
        if r.critical == "echec":
            graze = self.engine.mastery_on_miss(slot)       # v52 : Effleurement aussi sur un 1 naturel
            win.statusBar().showMessage("1 naturel : l'attaque rate automatiquement." + (" " + graze if graze else ""),
                                        12000)
            return False
        crit = r.critical == "succes"
        question = "d20 = {} → total {}{}. Comparez à la CA de la cible : l'attaque touche-t-elle ?".format(
            r.natural, r.total, " — 20 naturel : coup critique, les dés de dégâts sont doublés" if crit else "")
        options = self.engine.on_hit_options(slot, getattr(damage_spec, "options", []) or [])
        mastery = self.engine.mastery_on_hit(slot)       # v52 : rappel de la botte d'arme
        if options:                                      # v53 : « touche ? » + bonus au toucher, une seule fenêtre
            from .on_hit_dialog import ask_hit
            chosen = ask_hit(win, attack_spec.title + ("\n" + mastery if mastery else ""), question, options, crit)
            hit = chosen is not None
        else:
            hit = ask_yes_no(win, "L'attaque touche-t-elle ?", "{}\n\n{}".format(attack_spec.title, question),
                             yes="Oui : lancer les dégâts", no="Non", default_no=False)
            chosen = []
        if not hit:
            graze = self.engine.mastery_on_miss(slot)       # v52 : Effleurement sur un raté
            if graze:
                win.statusBar().showMessage(graze, 12000)
            return False
        spec = D.DamageSpec(damage_spec.title, damage_spec.formula, damage_spec.damage_type, damage_spec.note,
                            damage_spec.kind)
        spec.parts = list(getattr(damage_spec, "parts", []) or [])   # v52 : dégâts par type
        if mastery:
            spec.note = (spec.note + " ; " if spec.note else "") + mastery
        added = self.engine.apply_on_hit(options, chosen)
        drain = [a for a in added if a[0].startswith("Fureur sanglante")]     # v53 : en dernier (soins = ces dés)
        for label, dice in [a for a in added if a not in drain] + drain:
            spec.formula += "+" + dice
            spec.note = (spec.note + " ; " if spec.note else "") + "{} : +{}".format(label, dice)
            if spec.parts:
                kind = D.damage_type_in(label) or ("radiants" if "chatiment" in R.norm(label) else spec.damage_type)
                spec.parts.append((dice, kind))
        if crit:
            parts = [(D.critical_formula(p), t) for p, t in spec.parts]
            spec = D.DamageSpec(spec.title + " (critique)", D.critical_formula(spec.formula),
                                spec.damage_type, "Coup critique : dés doublés." + (" " + spec.note if spec.note else ""),
                                spec.kind)
            spec.parts = parts
        r = roll_damage_dialog(win, spec)
        if r is not None and drain:                       # v53 : Fureur sanglante — PV = dégâts nécrotiques infligés
            n = 8 if crit else 4
            gained = self.engine.heal(sum(v for faces, v, sign in r.dice[-n:] if faces == 6 and sign > 0))
            win.statusBar().showMessage("Fureur sanglante : vous regagnez {} PV.".format(gained), 8000)
            self.changed()
        return True

    def _roll_weapon_damage(self, key: str, i: int):
        slot = getattr(self.ch, key)[i]
        spec = self.engine.weapon_damage_spec(slot, offhand=(key == "armes_cac" and i == 1))
        if spec is not None:                              # v46 : calcul détaillé (caractéristique, objet, style…)
            roll_damage_dialog(self.win, spec)

    def _roll_cantrip_damage(self, i: int):
        name = self.ch.sorts_mineurs[i].get("nom", "")
        st = self.engine.cantrip_stats(name) if name else None
        if st and st.get("degats"):
            note = ("Total si les {n} rayons touchent — chaque rayon est une attaque séparée : {r} par rayon."
                    .format(n=st["rayons"], r=st["degats_rayon"]) if st.get("rayons") else "")
            if st.get("effets"):
                note = (note + "\n" if note else "") + "\n".join(st["effets"])
            roll_damage_dialog(self.win, D.DamageSpec("Dégâts — " + st["nom"], st["degats"], st["type_degats"], note))

    # ------------------------------------------------------------------ styles de combat
    def _rebuild_styles(self, slots: list[dict]):
        while self.style_layout.count():
            item = self.style_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.style_rows = []
        if not slots:
            self.style_empty = make_label(
                "Aucun style de combat ni modèle d'armure à ce niveau (Guerrier niv. 1, Paladin et Rôdeur niv. 2, "
                "Collège des Épées niv. 3, Armurier niv. 3).", "muted", wrap=True)
            self.style_layout.addWidget(self.style_empty, 0, 0)
            return
        for r, sl in enumerate(slots):
            w = {"id": sl["id"], "label": make_label(""), "combo": QComboBox(), "desc": make_label("", "muted", wrap=True),
                 "tech": QComboBox()}
            w["combo"].setMinimumWidth(220)
            w["combo"].activated.connect(lambda _=0, sid=sl["id"]: self._on_style(sid))
            # Technique supérieure : choix de la manœuvre apprise (visible seulement avec ce style)
            w["tech"].setMinimumWidth(200)
            w["tech"].setVisible(False)
            w["tech"].activated.connect(lambda _=0, c=w["tech"]: self._on_tech_maneuver(c))
            self.style_layout.addWidget(w["label"], r * 2, 0)
            self.style_layout.addWidget(w["combo"], r * 2, 1)
            self.style_layout.addWidget(w["tech"], r * 2, 2)
            self.style_layout.addWidget(w["desc"], r * 2 + 1, 0, 1, 3)
            self.style_rows.append(w)
        self.style_layout.setColumnStretch(1, 1)
        self.style_layout.setColumnStretch(2, 1)

    def _on_power(self, checked: bool) -> None:
        self.ch.attaque_puissante = bool(checked)
        self.changed()

    def _on_remember_toggle(self) -> None:
        self._remember_open = not self._remember_open
        self._refresh_remember()

    def _refresh_remember(self) -> None:
        groups = self.engine.remember_list()
        self.remember_box.setVisible(bool(groups))
        n = sum(len(v) for v in groups.values())
        self.remember_box.setTitle("📌 À ne pas oublier ({})".format(n))
        self.remember_toggle.setText("▾ Masquer" if self._remember_open else "▸ Afficher")
        self.remember_text.setVisible(self._remember_open)
        self.remember_text.setText("".join("<b>{}</b><br/>{}<br/>".format(
            html.escape(m), "<br/>".join("• " + html.escape(x) for x in lines)) for m, lines in groups.items()))

    NO_MANEUVER = "— choisir une manœuvre —"

    def _on_tech_maneuver(self, combo) -> None:
        text = combo.currentText()
        self.ch.technique_manoeuvre = "" if text == self.NO_MANEUVER else text
        self.changed()

    def _on_style(self, slot_id: str):
        w = next(r for r in self.style_rows if r["id"] == slot_id)
        text = w["combo"].currentText()
        if text.startswith("—"):
            self.ch.styles_combat.pop(slot_id, None)
        else:
            self.ch.styles_combat[slot_id] = text
        self.changed()

    # ------------------------------------------------------------------ v52 : saisie rapide des PV, emplacements
    def _on_free_roll(self) -> None:
        formula = D.free_formula(self.free_roll.text())
        if not formula:
            self.win.statusBar().showMessage("Formule de dés non reconnue : essayez « 2d6+3 » ou « d20+5 ».", 6000)
            return
        r = roll_damage_dialog(self.win, D.DamageSpec("Jet libre", formula, kind="de"))
        if r is not None:
            self.free_roll_last.setText("{} → {}".format(formula, r.total))
            self.free_roll.selectAll()
            self.changed()

    def focus_free_roll(self) -> None:
        self.free_roll.setFocus()
        self.free_roll.selectAll()

    def focus_hp_entry(self) -> None:
        """Ctrl+D : fenêtre des dégâts (v52 : le champ de saisie rapide est remplacé)."""
        self.open_damage()

    def _on_extend_effect(self, key: str) -> None:
        msg = self.engine.extend_effect(key)
        if msg:
            self._message(msg)
            self.changed()

    def _on_exhaustion(self, delta: int) -> None:
        self._message(self.engine.set_exhaustion(self.engine.exhaustion_level() + delta))
        self.changed()

    def open_exhaustion(self, cause: str = "marche") -> bool:
        from .exhaustion_dialog import ExhaustionDialog
        dlg = ExhaustionDialog(self.win, cause)
        if dlg.exec() and dlg.result_text:
            self._message(dlg.result_text)
            self.changed()
            return True
        return False

    def maybe_concentration_save(self) -> None:
        """v52 : après des dégâts subis en se concentrant, propose le JS de Constitution et applique le résultat."""
        eng = self.engine
        damage = int(getattr(eng, "pending_concentration", 0) or 0)
        if not damage or not eng.ch.concentration:
            return
        if not ask_yes_no(self.win, "Concentration", "Vous subissez {} dégâts en vous concentrant sur {}.\n\nLancer le "
                          "JS de Constitution (DD {}) ?".format(damage, eng.ch.concentration,
                                                              eng.concentration_dc(damage)),
                          yes="🎲 Lancer le JS", no="Plus tard", default_no=False):
            return
        r = roll_dice(self.win, eng.concentration_save_spec(damage))
        if r is not None:
            self._message(eng.resolve_concentration(r.total, damage))
            self.changed()

    def open_defense(self, start: str = "attaque", amount: int = 0, dtype: str = "", magical: bool = False) -> bool:
        from .defense_dialog import DefenseDialog
        dlg = DefenseDialog(self.win, start, amount, dtype, magical)
        if dlg.exec() and dlg.result_text:
            self._message(dlg.result_text)
            self.changed()
            self.maybe_concentration_save()
            self.maybe_zero_hp()
            return True
        self.changed()
        return False

    def _quick_hp(self, kind: str) -> None:
        idx = self.dmg_type.currentIndex()
        dtype = ExtrasMixin.DAMAGE_TYPES[idx - 1] if idx > 0 else ""
        m = re.fullmatch(r"\s*([+-]?)\s*(\d+)\s*", self.hp_entry.text() or "")
        is_damage = bool(m) and (kind == "degats" or (not kind and m.group(1) != "+"))
        if is_damage and self.engine.defense_options("degats"):     # v52 : réactions proposées avant les dégâts
            self.hp_entry.clear()
            self.open_defense("degats", int(m.group(2)), dtype, self.dmg_magic.isChecked())
            return
        msg = self.engine.apply_hp_input(self.hp_entry.text(), kind, dtype, self.dmg_magic.isChecked())
        if not msg:
            self.win.statusBar().showMessage("Saisissez un nombre : « 7 » ou « -7 » pour des dégâts, « +5 » pour des "
                                             "soins.", 6000)
            return
        self.hp_entry.clear()
        self._message(msg)
        self.changed()
        self.maybe_concentration_save()            # v52

    def _on_slot_used(self, level_idx: int, used: int) -> None:
        self.ch.emplacements_utilises[level_idx] = used
        self.win.light_changed()

    def _on_pact_used(self, used: int) -> None:
        self.ch.pacte_utilises = used
        self.win.light_changed()

    def _refresh_slot_strip(self) -> None:
        eng, ch = self.engine, self.ch
        slots = eng.spell_slots()
        n_pact, pact_lvl = eng.pact()
        self.slots_box.setVisible(any(slots) or n_pact > 0)
        for i, (lab, orbs) in enumerate(self.slot_strip):
            lab.setVisible(slots[i] > 0)
            orbs.setVisible(slots[i] > 0)
            if slots[i]:
                orbs.set_state(slots[i], ch.emplacements_utilises[i])
        for w in self.pact_strip:
            w.setVisible(n_pact > 0)
        if n_pact:
            self.pact_strip[0].setText("Pacte (niv. {})".format(pact_lvl))
            self.pact_strip[1].set_state(n_pact, ch.pacte_utilises)

    def _refresh_masteries(self):
        """Encart « Bottes d'arme » : visible si la fiche a des bottes (aptitude 2024 ou règle de la table)."""
        eng = self.engine
        count = eng.mastery_count()
        self.mastery_box.setVisible(count is None or count > 0)
        self.mastery_btn.setVisible(False)              # v52 : choisies à la création / montée de niveau, une
        #                                                 se change au repos long
        self.mastery_label.setToolTip(rich_tip("Bottes d'arme", "Choisies à la création et à la montée de niveau "
                                               "(rappel dans l'onglet Classes) ; une botte se change à la fin d'un "
                                               "repos long.") if count else "")
        if count is None:
            self.mastery_label.setText("Règle de la table : la botte de chaque arme maîtrisée s'applique.")
        elif count:
            chosen = eng.mastery_weapons() or []
            self.mastery_label.setText("{} / {} : {}".format(len(chosen), count, ", ".join(chosen) or "aucune "
                                                             "(les armes équipées sont proposées par défaut)"))

    def _choose_masteries(self):
        from .mastery_dialog import MasteryDialog
        MasteryDialog(self.win).exec()

    def _refresh_styles(self):
        """Sélecteurs : actifs uniquement si le niveau de classe requis est atteint (règles 5e)."""
        eng, db = self.engine, self.engine.db          # v52 : styles de l'édition de la fiche
        slots = eng.fighting_style_slots()
        key = tuple((s["id"], s["debloque"]) for s in slots)
        if key != self._style_key:
            self._rebuild_styles(slots)
            self._style_key = key
        for sl, w in zip(slots, self.style_rows):
            is_model = sl["kind"] == "modele"
            current = self.ch.styles_combat.get(sl["id"], "")
            options = eng.style_options(sl["id"])
            if is_model:
                tips = {n: rich_tip(n, db.armor_models.get(n, "")) for n in options}
                noun, ask = "Modèle d'armure", "— choisir un modèle —"
            else:
                tips = {n: rich_tip(n, db.style_description(sl["classe"], n)) for n in options}
                noun, ask = "Style de combat", "— choisir un style —"
            placeholder = ask if sl["debloque"] else "— niveau {} requis —".format(sl["niveau_requis"])
            fill_combo(w["combo"], [placeholder] + options, current if current in options else placeholder, tips)
            w["combo"].setEnabled(sl["debloque"])
            extra = " (supplémentaire)" if (not is_model and sl["source"] != sl["classe"]
                                            and "supplementaire" in sl["source"].lower()) else ""
            w["label"].setText("{} — {} (niveau {}){}".format(sl["classe"], noun, sl["niveau_requis"], extra))
            if not sl["debloque"]:
                w["desc"].setText("Se débloque au niveau {} de {}.".format(sl["niveau_requis"], sl["classe"]))
            elif is_model:
                name, desc = eng.armor_model()
                w["desc"].setText("{} : {}".format(name, desc) if name else "")
            else:
                w["desc"].setText(db.style_description(sl["classe"], current))
            from core.class_actions import SUPERIOR_TECHNIQUE
            tech = not is_model and current == SUPERIOR_TECHNIQUE and sl["debloque"]
            w["tech"].setVisible(tech)
            if tech:
                names = list(db.maneuvers)
                tips = {n: rich_tip(n, db.maneuvers[n]) for n in names}
                pick = self.ch.technique_manoeuvre
                fill_combo(w["tech"], [self.NO_MANEUVER] + names, pick if pick in names else self.NO_MANEUVER, tips)
                w["tech"].setToolTip(rich_tip("Technique supérieure", "Manœuvre apprise : elle apparaît dans l'encart "
                                              "« Actions, capacités de classe » avec 1 dé de supériorité (d6), "
                                              "récupéré au repos court ou long."))

    # ------------------------------------------------------------------ rafraîchissement
    def refresh(self):
        self._refresh_header()                            # v52 : bandeau du haut, caractéristiques, jets contre la mort
        self.mark_box(self.style_box, "Style de combat et modèle d'armure", "combat", "Style de combat")
        eng, ch, db = self.engine, self.ch, self.db
        ac_info = eng.armor_class_detail()
        ac = ac_info["valeur"]
        form_ca = eng.form_status()
        gear = eng.unproficient_gear()                   # v43 : armure / bouclier non maîtrisés
        self.stat_labels["ca"].setText(("{} ".format(form_ca["icone"]) if form_ca else "") + str(ac)
                                       + (" ⚠" if gear else ""))
        terms = [t.strip() for t in ac_info["formule"].split(" + ")]
        values = [v.strip() for v in ac_info["chiffres"].split("=")[0].split(" + ")]
        rows = list(zip(terms, values)) if len(terms) == len(values) else [(ac_info["formule"], ac_info["chiffres"])]
        self.stat_labels["ca"].setToolTip(calc_tip("Classe d'armure" + (" — " + ac_info["note"] if ac_info["note"] else ""),
                                                   rows, ac, ["{} {}".format(form_ca["icone"], form_ca["libelle"])]
                                                   if form_ca else ["Les effets actifs (Hâte, Bouclier de la foi, "
                                                                    "Armure du mage, Chant de la lame…) sont inclus."]
                                                   + ["⚠ {} ({})".format(g["message"], g["nom"]) for g in gear]
                                                   + ([CAST_BLOCKED] if gear else [])))
        last = self.ch.initiative_jet
        self.init_last.setText("Dernier jet : {}".format(last) if last else "🎲 Cliquez sur le d20")
        init_fx = eng.check_mods("Dextérité")
        self.stat_labels["init"].setText(R.fmt_bonus(eng.initiative()) + (" " + adv_badge(M.adv_state(init_fx))[0][0]
                                                                         if M.adv_state(init_fx) else ""))
        idet = eng.initiative_detail()                   # v45 : détail complet (dons, aptitudes, effets)
        init_tip = calc_tip("Initiative (test de Dextérité)", [(a, R.fmt_bonus(b)) for a, b in idet["termes"]]
                            + list(idet["des"]), R.fmt_bonus(eng.initiative()),
                            ["Avantage : " + ", ".join(idet["avantage"])] * bool(idet["avantage"])
                            + ["Désavantage : " + ", ".join(idet["desavantage"])] * bool(idet["desavantage"])
                            + ["🎲 Cliquez sur le d20 pour lancer l'initiative."])
        self.stat_labels["init"].setToolTip(init_tip)
        self.init_btn.setToolTip(init_tip)
        self.stat_labels["vit"].setText(eng.speed_text())
        fx = eng.effect_mods()
        self.stat_labels["vit"].setToolTip(calc_tip("Vitesse de marche", [
            ("Vitesse de base (race, classe, dons)", "{:g} m".format(
                eng.speed() / fx["vitesse_mult"] - fx["vitesse_bonus"] if fx["vitesse_mult"] else 0)),
            ("Bonus des effets", "{:+g} m".format(fx["vitesse_bonus"])), ("Multiplicateur des effets",
                                                                          "×{:g}".format(fx["vitesse_mult"]))],
            eng.speed_text(), ["1 case = 1,50 m (règle officielle D&D 5e)."] + (
                ["Vitesse de nage : {} (Don des profondeurs).".format(R.fmt_speed(eng.swim_speed()))]
                if eng.swim_speed() else [])))
        self.stat_labels["prof"].setText(R.fmt_bonus(eng.prof))
        self.stat_labels["prof"].setToolTip(rich_tip("Bonus de maîtrise", "Dépend du niveau global du personnage "
                                                     "(+2 aux niveaux 1-4, +3 aux niveaux 5-8, … +6 aux niveaux 17-20)."))
        self.stat_labels["perc"].setText(str(eng.passive_perception()))
        self._refresh_vision()
        perc = next((r for r in eng.skill_rows() if r["nom"] == "Perception"), None)
        if perc:
            self.stat_labels["perc"].setToolTip(calc_tip("Perception passive", [("Base", "10")] + perc["detail"] + (
                [("Avantage (PHB)", "+5")] if perc["etat"] == "avantage" else
                [("Désavantage (PHB)", "-5")] if perc["etat"] in ("désavantage", "échec") else []),
                eng.passive_perception()))

        form = eng.form_status()
        hp = form["pv_max"] if form else eng.hp_max()
        self.hp_max.setText(("{} ".format(form["icone"]) if form else "") + str(hp))
        tip = ("<qt><b>{} {}</b><br/>PV de la bête ; vos PV ({}/{}) réapparaissent à la fin de la transformation."
               "</qt>".format(form["icone"], form["libelle"], ch.pv_actuels, eng.hp_max()) if form else "")
        for w in (self.hp_max, self.hp_cur):
            w.setToolTip(tip)
        self.hp_box.setTitle("Points de vie — {} {}".format(form["icone"], form["bete"]) if form else "Points de vie (corrections)")
        with blocked(self.hp_cur, self.hp_tmp, self.hp_misc, *self.ok_boxes, *self.ko_boxes):
            self.hp_cur.setRange(0, hp)
            self.hp_cur.setValue(form["pv"] if form else ch.pv_actuels)
            self.hp_tmp.setValue(ch.pv_temporaires)
            self.hp_misc.setValue(ch.pv_divers)
            for i, b in enumerate(self.ok_boxes):
                b.setChecked(i < ch.mort_reussites)
            for i, b in enumerate(self.ko_boxes):
                b.setChecked(i < ch.mort_echecs)
        self.death_btn.setEnabled(ch.pv_actuels == 0 and not form)
        self.hit_dice.setText("Dés de vie restants : " + ", ".join(
            "{} / {} {}".format(p["restants"], p["total"], p["de"]) for p in eng.hit_dice_pool())
            + " — dépensez-les lors d'un repos court. PV max calculés avec la valeur moyenne fixe des dés de vie.")

        armor_tips = {n: rich_tip(n, "CA {} — {} — {} ({}). {}".format(
            a.get("ca_base", "—"), a["categorie"], a["poids"], a["origine"], a.get("description", "")))
            for n, a in db.armors.items()}
        fill_combo(self.armor, list(db.armors), ch.armure.get("nom", "Aucune armure"), armor_tips)
        shield_tips = {n: rich_tip(n, "+{} CA — {} ({}). {}".format(sh["bonus_ca"], sh["poids"], sh["origine"],
                                                                    sh.get("description", "")))
                       for n, sh in db.shields.items()}
        current_shield = ch.armure.get("bouclier_nom") or next(iter(db.shields), "") if ch.armure.get("bouclier") \
            else "Aucun"
        fill_combo(self.shield, ["Aucun"] + list(db.shields), current_shield, shield_tips)
        with blocked(self.armor_magic):
            self.armor_magic.setCurrentIndex(max(0, min(3, int(ch.armure.get("bonus", 0)))))
        # affichage de la règle appliquée (et non plus le simple nom de l'armure)
        self.ac_formula.setText("CA = {}{}".format(ac_info["formule"], "   ({})".format(ac_info["note"])
                                                   if ac_info["note"] else ""))
        self.ac_detail.setText("= " + ac_info["chiffres"] if " + " in ac_info["formule"] else "")
        self._refresh_styles()
        self._refresh_masteries()
        self._refresh_slot_strip()
        if hasattr(self, "resource_strip"):
            self.resource_strip.refresh()
        self._refresh_remember()                         # v52 : À ne pas oublier
        self._refresh_resources()
        self._refresh_saves()
        self._refresh_effects()
        self._refresh_form()
        self._refresh_racial()
        self._refresh_concentration()
        self._refresh_turn()
        self.time_label.setText("⏳ Jour & Heure : {}".format(eng.time_text()))
        self.armor_warn.setText("\n".join("⚠ " + w for w in eng.armor_warnings()))

        for key, rows in self.weapon_rows.items():
            kind = "cac" if key == "armes_cac" else "distance"
            names = [PLACEHOLDER_WEAPON] + [n for n, w in db.weapons.items() if w["type"] == kind]
            tips = {n: rich_tip(n, "{} {} — {}. Botte : {}.".format(
                w["degats"], w["type_degats"], ", ".join(w["proprietes"]) or "sans propriété", w["botte"] or "—"))
                for n, w in db.weapons.items()}
            slots = getattr(ch, key)
            shown = R.lazy_slot_count([bool(sl.get("nom")) for sl in slots], len(rows))   # 1 ligne, puis une de plus à chaque ajout
            for i, w in enumerate(rows):
                for k in w["_order"]:
                    w[k].setVisible(i < shown)
                slot = slots[i]
                fill_combo(w["combo"], names, slot.get("nom") or PLACEHOLDER_WEAPON, tips)
                with blocked(w["magic"], w["prof"]):
                    w["magic"].setCurrentIndex(max(0, min(3, int(slot.get("bonus", 0)))))
                st = eng.weapon_stats(slot, offhand=(key == "armes_cac" and i == 1))
                self._refresh_weapon_extras(key, i, w, slot, st)
                w["d20"].setEnabled(bool(st))
                if not st:
                    for k in ("ab", "atk", "dmg", "info"):
                        w[k].setText("")
                    w["dmg"].set_formula("")
                    w["hands"].setVisible(False)
                    w["prof"].setEnabled(False)
                    with blocked(w["prof"]):
                        w["prof"].setChecked(False)
                    self._style_prof(w["prof"], None)
                    continue
                w["prof"].setEnabled(True)
                with blocked(w["prof"]):
                    w["prof"].setChecked(st["maitrise"])
                self._style_prof(w["prof"], st)
                w["ab"].setText(R.ABBR[st["carac"]])
                state = st.get("etat", "")
                unprof = not st["maitrise"] and st["nom"] != "Mains nues"     # v43 : arme non maîtrisée
                w["atk"].setText(("⚠ " if unprof else "") + R.fmt_bonus(st["attaque"])
                                 + (" " + " ".join(st["des_attaque"]) if st.get("des_attaque") else "")
                                 + ({"avantage": " ▲", "désavantage": " ▼"}.get(state, "")))
                w["atk"].setToolTip(calc_tip(("⚠ " if unprof else "") + "Jet d'attaque — " + st.get("affichage", st["nom"]), [
                    (R.mod_label(st["carac"]), R.fmt_bonus(eng.mod(st["carac"])))]
                    + ([("Maîtrise", R.fmt_bonus(eng.prof))] if st["maitrise"] else [])
                    + ([("Bonus magique", R.fmt_bonus(st["magique"]))] if st["magique"] else [])
                    + [(x, "") for x in st["styles"] if "toucher" in x or "Archerie" in x],
                    R.fmt_bonus(st["attaque"]),
                    ["Avantage : " + ", ".join(st["avantage"])] * bool(st.get("avantage"))
                    + ["Désavantage : " + ", ".join(st["desavantage"])] * bool(st.get("desavantage"))
                    + [WEAPON_WARNING] * unprof))
                dmg = "{} {}".format(st["degats"], st["type_degats"])
                w["dmg"].setText(dmg)
                other = ("À une main : {}".format(st["calcul_1m"]) if st["deux_mains"] else
                         "À deux mains : {}".format(st["calcul_2m"])) if st["polyvalente"] else ""
                calc = "<b>Calcul :</b> " + html.escape(st.get("calcul", "")) + (
                    " ({})".format(st["prise"]) if st.get("prise") else "")
                w["dmg"].set_formula(st["degats"], calc + ("<br/>" + html.escape(other) if other else ""))
                self._refresh_hands(w, st)
                w["power"].setVisible(bool(st.get("puissance_possible")))
                with blocked(w["power"]):
                    w["power"].setChecked(bool(st.get("puissance")))
                info = ", ".join(st["proprietes"])
                if st["portee"]:
                    info += " — portée {} m".format(st["portee"])
                if st["magique"]:
                    info = "Arme magique +{} ; ".format(st["magique"]) + info
                w["info"].setText(info)
                if st["botte"]:
                    info += " — Botte : {}".format(st["botte"])
                if st["styles"]:
                    info += " — " + " ; ".join(st["styles"])
                w["info"].setText(info)
                w["info"].setToolTip(rich_tip("{} — botte d'arme : {}".format(st["nom"], st["botte"] or "—"),
                                              st["botte_desc"] or info))

            self._compact_rows(key, rows, [bool(sl.get("nom")) for sl in slots], shown)

        cantrips = [PLACEHOLDER_SPELL] + eng.available_cantrips()
        shown = R.lazy_slot_count([bool(c.get("nom")) for c in ch.sorts_mineurs], len(self.cantrip_rows))
        filled = [bool(c.get("nom")) for c in ch.sorts_mineurs][:len(self.cantrip_rows)]
        filled += [False] * (len(self.cantrip_rows) - len(filled))
        any_filled = any(filled)
        for h in self._box_heads.get("cantrips", []):
            h.setVisible(any_filled)
        for i, w in enumerate(self.cantrip_rows):
            name = ch.sorts_mineurs[i].get("nom", "") if i < len(ch.sorts_mineurs) else ""
            w["combo"].setVisible(i < shown)
            for widget in (w["test"], w["dmg"], w["type"], w["range"]):
                widget.setVisible(i < shown and bool(name))    # ligne vide : seul le sélecteur est affiché
            # le dé garde sa place dans une ligne remplie (sort sans jet d'attaque) mais pas dans une ligne vide
            retain_when_hidden(w["d20"], i < shown and bool(name))
            w["d20"].setVisible(i < shown and bool(name) and eng.spell_attack_spec(name) is not None)
            if name and name not in cantrips:
                cantrips.append(name)
            fill_combo(w["combo"], cantrips, name or PLACEHOLDER_SPELL)
            st = eng.cantrip_stats(name) if name else None
            if st:
                w["test"].setText(st["test"])
                w["dmg"].setText(st["degats"] or "—")
                w["dmg"].set_formula(st["degats"] or "")
                w["type"].setText(st["type_degats"])
                w["range"].setText(st["portee"])
                w["combo"].setToolTip(rich_tip(st["nom"], st["description"]))
                if st.get("effets") or st.get("rayons"):     # manifestations : effets visibles sur la tuile
                    w["dmg"].setToolTip(rich_tip("Dégâts — " + st["nom"], "\n".join(
                        (["{} rayon(s) : {} chacun (attaque séparée)".format(st["rayons"], st["degats_rayon"])]
                         if st.get("rayons") else []) + st.get("effets", []))))
            else:
                for k in ("test", "dmg", "type", "range"):
                    w[k].setText("")
                w["dmg"].set_formula("")
                w["combo"].setToolTip("")
