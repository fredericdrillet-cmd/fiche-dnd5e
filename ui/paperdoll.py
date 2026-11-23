"""
Mannequin d'équipement (v31, inspiré de l'inventaire de Baldur's Gate 3) : le personnage entouré de 12 cases.

    - à gauche : tête, amulette, cape, armure, gants ; à droite : ceinture, bottes, anneau ×2 ; en bas : main
      principale, main secondaire, distance ;
    - au centre : le portrait du personnage (onglet « Histoire, Portrait ») ;
    - clic sur une case : les objets de l'INVENTAIRE qui correspondent à son rôle — armures du sac, armes de corps à
      corps, boucliers et armes légères, armes à distance, anneaux, capes, bottes… (ou « Vider la case ») ; un objet
      par case, l'ancien est rangé ; l'armure et les armes choisies ici sont celles de l'onglet Combat ;
    - infobulle de chaque case : objet porté, rareté, harmonisation (◉) ; objet magique en surbrillance.
"""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QGroupBox, QLabel, QSizePolicy, QVBoxLayout

from core.equipment import MAGIC_SLOTS, SLOT_LABELS, SLOTS, TATTOO_SLOTS
from . import theme
from .common import make_label, rich_tip
from .dialogs import ask_choice

LAYOUT = {"tete": (0, 0), "amulette": (1, 0), "cape": (2, 0), "armure": (3, 0), "gants": (4, 0),
          "ceinture": (0, 2), "bottes": (1, 2), "anneau_1": (2, 2), "anneau_2": (3, 2),
          "main_principale": (5, 0), "main_secondaire": (5, 1), "distance": (5, 2)}
EMPTY = "— vide —"
CLEAR = "✖ Vider la case"


class SlotCard(QLabel):
    """Case cliquable du mannequin : texte AVEC retour à la ligne (un QPushButton tronque les noms longs)."""

    def __init__(self, on_click=None, min_w: int = 150, min_h: int = 66, slot: str = "", on_drop=None):
        super().__init__()
        self.on_click = on_click
        self.slot, self.on_drop, self.filled = slot, on_drop, False      # v53 : glisser-déposer
        self._press = None
        if on_drop is not None:
            self.setAcceptDrops(True)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(min_w, min_h)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._press = event.position()                # clic ou début de glisser (case remplie -> sac)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        if self._press is not None and self.filled and self.slot and \
                (event.position() - self._press).manhattanLength() > 12:
            from PyQt6.QtCore import QMimeData
            from PyQt6.QtGui import QDrag
            from .inventory_grid import MIME_SLOT
            self._press = None
            mime = QMimeData()
            mime.setData(MIME_SLOT, self.slot.encode("utf-8"))
            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.setPixmap(self.grab())
            drag.exec(Qt.DropAction.MoveAction)
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        if self._press is not None and self.on_click and event.button() == Qt.MouseButton.LeftButton:
            self._press = None
            self.on_click()
            return
        self._press = None
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, e):  # noqa: N802
        from .inventory_grid import MIME_ITEM
        if e.mimeData().hasFormat(MIME_ITEM):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):  # noqa: N802
        from .inventory_grid import MIME_ITEM
        if e.mimeData().hasFormat(MIME_ITEM) and self.on_drop:
            self.on_drop(self.slot, bytes(e.mimeData().data(MIME_ITEM)).decode("utf-8"))
            e.acceptProposedAction()

    def set_look(self, color: str, bold: bool = False, dashed: bool = False) -> None:
        t = theme.current()
        self.setStyleSheet("QLabel {{ color: {c}; font-weight: {w}; background: {bg}; border: 1px {st} {b}; "
                           "border-radius: 6px; padding: 4px 6px; }}".format(
                               c=color, w="bold" if bold else "normal", bg=t.panel2, b=t.border,
                               st="dashed" if dashed else "solid"))


class PaperdollPanel(QGroupBox):
    def __init__(self, win):
        super().__init__("🧍 Mannequin d'équipement")
        self.win = win
        lay = QVBoxLayout(self)
        grid = QGridLayout()
        grid.setSpacing(6)
        self.slot_btns: dict[str, SlotCard] = {}
        for key, (r, c) in LAYOUT.items():
            b = SlotCard(lambda k=key: self._on_slot(k), slot=key, on_drop=self.drop_on_slot)
            grid.addWidget(b, r, c)
            self.slot_btns[key] = b
        # au centre : le portrait DU PERSONNAGE (onglet « Histoire, Portrait »), qu'on équipe
        self.portrait = SlotCard(self._on_portrait, 170, 230, on_drop=self.drop_on_slot)   # dépôt : case naturelle
        self.portrait.setProperty("role", "portrait")
        self._portrait_shown = None
        grid.addWidget(self.portrait, 0, 1, 5, 1)
        for col in range(3):
            grid.setColumnStretch(col, 1)
        lay.addLayout(grid)
        # v53 : harmonisation — un objet qui l'exige en prend un emplacement dès qu'il est équipé
        from PyQt6.QtWidgets import QHBoxLayout
        from .orbs import OrbBar
        att = QHBoxLayout()
        att.addWidget(make_label("✦ Harmonisation", "head"))
        self.attune_orbs = OrbBar("harmonisation", per_row=6, interactive=False)
        self.attune_left = make_label("", "stat")
        att.addWidget(self.attune_orbs)
        att.addWidget(self.attune_left)
        att.addStretch(1)
        lay.addLayout(att)
        self.attuned = make_label("", "muted", wrap=True)          # objets harmonisés (et portés hors case)
        self.attuned.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(self.attuned)
        # v53 : emplacements rapides (potions, huiles, parchemins) -> tuiles de l'onglet « En partie »
        quick_head = make_label("⚡ Emplacements rapides", "head")
        quick_head.setToolTip(rich_tip("Emplacements rapides", "Glissez ici une potion, une huile ou un parchemin "
                                       "du sac (ou cliquez une case) : sa tuile apparaît dans l'onglet « En partie » "
                                       "pour l'utiliser. Glissez une case vers le sac pour la vider."))
        lay.addWidget(quick_head)
        quick = QHBoxLayout()
        quick.setSpacing(6)
        from core.quick_slots import QUICK_SLOTS
        self.quick_btns = []
        for n in range(QUICK_SLOTS):
            b = SlotCard(lambda k=n: self._on_quick(k), 96, 54, slot="rapide:{}".format(n),
                         on_drop=self.drop_on_quick)
            quick.addWidget(b)
            self.quick_btns.append(b)
        lay.addLayout(quick)
        # v53 : quatre cases de tatouages (Chaudron de Tasha), rangée masquable (réglage mémorisé)
        tat_head = QHBoxLayout()
        from PyQt6.QtWidgets import QPushButton
        self.tattoo_toggle = QPushButton()
        self.tattoo_toggle.setProperty("role", "ghost")
        self.tattoo_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tattoo_toggle.setToolTip(rich_tip("Tatouages", "Afficher ou masquer les quatre cases de tatouages "
                                               "magiques. Un tatouage qui exige l'harmonisation l'est dès qu'il "
                                               "est dans une case."))
        self.tattoo_toggle.clicked.connect(self._toggle_tattoos)
        tat_head.addWidget(self.tattoo_toggle)
        tat_head.addStretch(1)
        lay.addLayout(tat_head)
        from PyQt6.QtWidgets import QWidget
        self.tattoo_row = QWidget()
        tat = QHBoxLayout(self.tattoo_row)
        tat.setContentsMargins(0, 0, 0, 0)
        tat.setSpacing(6)
        for key, _lab, _icon in TATTOO_SLOTS:
            b = SlotCard(lambda k=key: self._on_slot(k), 96, 64, slot=key, on_drop=self.drop_on_slot)
            tat.addWidget(b)
            self.slot_btns[key] = b                       # rafraîchies et cliquées comme les autres cases
        lay.addWidget(self.tattoo_row)
        lay.addStretch(1)
        self.hint = make_label("Glissez un objet du sac sur une case, ou cliquez une case pour choisir parmi les objets qui correspondent à "
                               "son rôle (armures, armes, boucliers, anneaux, capes…). Un objet par case.",
                               "muted", wrap=True)
        lay.addWidget(self.hint)
        self.setMaximumWidth(560)

    @property
    def engine(self):
        return self.win.engine

    def refresh(self) -> None:
        eng, t = self.engine, theme.current()
        doll = eng.paperdoll()
        icons = {k: icon for k, _lab, icon in SLOTS + TATTOO_SLOTS}
        for key, b in self.slot_btns.items():
            item = doll.get(key)
            label = SLOT_LABELS[key]
            b.filled = bool(item)
            if item:
                mark = " ◉" if item.get("harmonise") else ""
                warn = eng.item_proficiency_warning(item["nom"]) if key in (
                    "armure", "main_principale", "main_secondaire", "distance") else ""
                magic = item["source"] == "objet" or item.get("magique")
                if key.startswith("tatouage"):            # v53 : petite case — nom court, sans « Tatouage »
                    import re as _re
                    short = _re.sub(r"^Tatouage (?:de la |de l'|de |d'|du )?", "", item["nom"]).strip()
                    b.setText("{} {}{}".format(icons[key], short[:1].upper() + short[1:], mark))
                else:
                    b.setText("{} {}\n{}{}{}{}".format(icons[key], label, "⚠ " if warn else "",
                                                       "✨ " if magic else "", item["nom"], mark))
                color = theme.rarity_color(item.get("rarete", ""), t, t.panel2) if magic else t.text
                b.set_look(t.warn if warn else color, bold=True)          # v53 : couleur de la rareté
                b.setToolTip(rich_tip(("⚠ " if warn else "") + item["nom"], "{}{}{}{}".format(
                    label, " — " + html.escape(item.get("detail", "")) if item.get("detail") else "",
                    "\n◉ Harmonisé" if item.get("harmonise") else
                    "\n○ Harmonisation requise (non harmonisé : sans effet)" if item.get("lien") else "",
                    "\n⚠ " + warn if warn else "")))
            else:
                n = sum(1 for c in eng.slot_inventory(key)   # objets du sac (pas déjà portés) pour cette case
                        if c.get("kind") != "magique" or not eng.ch.objets_magiques[c["index"]].get("equipe"))
                b.setText("{} {}\n{}".format(icons[key], label, EMPTY if not n else "{} objet{} disponible{}".format(
                    n, "s" * (n > 1), "s" * (n > 1))))
                b.set_look(t.muted, dashed=True)
                b.setToolTip(rich_tip(label, "Case vide." + (" Clic : choisir un objet." if n else "")))
        self._refresh_attunement(doll)
        self._refresh_quick()
        self._refresh_tattoo_toggle(doll)
        self._refresh_portrait()

    def _refresh_attunement(self, doll: dict) -> None:
        """v53 : jauge (sphères pleines = emplacements libres) et liste des objets harmonisés ; les objets portés
        sans case du mannequin (baguette, bâton, pierre…) y figurent aussi."""
        eng, t = self.engine, theme.current()
        limit, used = eng.attunement_limit(), eng.attuned_count()
        self.attune_orbs.set_state(limit, used)
        self.attune_left.setText("{} / {}".format(used, limit))
        tip = rich_tip("Harmonisation", "{} objet(s) harmonisé(s) sur {} possibles. Équiper un objet qui exige "
                       "l'harmonisation en prend un emplacement ; le ranger le libère. Les aptitudes de l'Artificier "
                       "(niv. 10, 14, 18) augmentent ce maximum.".format(used, limit))
        self.attune_orbs.setToolTip(tip)
        self.attune_left.setToolTip(tip)
        slotted = {v.get("index") for v in doll.values() if v.get("source") == "objet"}
        parts = []
        for i, e in enumerate(eng.ch.objets_magiques):
            if not e.get("equipe"):
                continue
            item = eng.magic_item(e["nom"]) or {}
            from core import mechanics as M
            consumable = M.is_consumable(e["nom"]) or item.get("type") in ("Potion", "Parchemin")
            hors_case = not e.get("base") and i not in slotted and not consumable   # potion : dans le sac
            if not (e.get("harmonise") or hors_case):
                continue
            parts.append("<span style='color:{}'><b>{}{}</b></span>{}".format(
                theme.rarity_color(e.get("palier") or item.get("rarete", ""), t), "◉ " if e.get("harmonise") else "",
                html.escape(eng.magic_display_name(e)), " <i>(porté, sans case)</i>" if hors_case else ""))
        self.attuned.setText(" · ".join(parts) if parts else
                             "Aucun objet harmonisé : équipez un objet ✦ (sac ou case) pour l'harmoniser.")

    def _tattoos_shown(self) -> bool:
        return bool((getattr(self.win, "settings", {}) or {}).get("tatouages_visibles", True))

    def _refresh_tattoo_toggle(self, doll: dict) -> None:
        n = sum(1 for k, _l, _i in TATTOO_SLOTS if k in doll)
        shown = self._tattoos_shown()
        self.tattoo_toggle.setText("{} 🖋 Tatouages ({} / 4)".format("▾" if shown else "▸", n))
        self.tattoo_row.setVisible(shown)

    def _toggle_tattoos(self) -> None:
        settings = getattr(self.win, "settings", None)
        if settings is None:
            return
        settings["tatouages_visibles"] = not self._tattoos_shown()
        try:
            from core.settings import save_settings
            save_settings(settings)
        except (ImportError, OSError):
            pass
        self._refresh_tattoo_toggle(self.engine.paperdoll())

    def _refresh_quick(self) -> None:
        eng, t = self.engine, theme.current()
        for n, (b, s) in enumerate(zip(self.quick_btns, eng.quick_slots())):
            b.filled = bool(s)
            if s:
                item = eng.magic_item(s["nom"]) or {}
                b.setText("{} {}{}".format("📜" if s["genre"] == "parchemin" else "🧪", s["nom"],
                                           " ×{}".format(s["qte"]) if s["qte"] > 1 else ""))
                b.set_look(theme.rarity_color(item.get("rarete", ""), t, t.panel2) if item else t.text, bold=True)
                b.setToolTip(rich_tip(s["nom"], "Emplacement rapide {} — {} dans l'onglet « En partie ». Clic : "
                                      "changer ou vider ; glisser vers le sac : vider.".format(n + 1, s["type"])))
            else:
                b.setText("⚡ {}\n— vide —".format(n + 1))
                b.set_look(t.muted, dashed=True)
                b.setToolTip(rich_tip("Emplacement rapide {}".format(n + 1), "Glissez une potion, une huile ou un "
                                      "parchemin du sac, ou cliquez pour choisir."))

    def drop_on_quick(self, slot: str, key: str) -> bool:
        ok, msg = self.engine.set_quick_slot(int(slot.split(":")[1]), key)
        self.win.statusBar().showMessage(msg, 6000)
        if ok:
            self.win.changed()
        return ok

    def _on_quick(self, n: int) -> None:
        """Case rapide cliquée : potions, huiles et parchemins du sac (ou « Vider la case »)."""
        eng, win = self.engine, self.win
        names = list(dict.fromkeys([it["nom"] for it in eng.ch.equipement if eng.is_quick_item(it["nom"])] +
                                   [e["nom"] for e in eng.ch.objets_magiques if eng.is_quick_item(e["nom"])]))
        options = names + ([CLEAR] if eng.quick_slots()[n] else [])
        if not options:
            win.statusBar().showMessage("Aucune potion, huile ni parchemin dans le sac.", 6000)
            return
        picked = ask_choice(win, "Emplacement rapide {}".format(n + 1), "Objet à garder sous la main :", options)
        if not picked:
            return
        if picked == CLEAR:
            eng.clear_quick_slot(n)
        else:
            win.statusBar().showMessage(eng.set_quick_slot(n, picked)[1], 6000)
        win.changed()

    def _refresh_portrait(self) -> None:
        """Portrait du personnage (importé dans l'onglet « Histoire, Portrait »), réduit au cadre ; sinon invitation."""
        data = self.engine.ch.portrait
        if data == self._portrait_shown:
            return
        self._portrait_shown = data
        pix = None
        if data:
            try:
                from .rp_tab import b64_to_pixmap
                pix = b64_to_pixmap(data)
                if pix.isNull():
                    pix = None
            except Exception:                             # pragma: no cover - image illisible
                pix = None
        if pix is not None:
            scaled = pix.scaled(160, 220, Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
            self.portrait.setText("")
            self.portrait.setPixmap(scaled)
            self.portrait.setToolTip(rich_tip(self.engine.ch.nom or "Portrait", "Portrait du personnage — clic : "
                                              "le changer dans l'onglet « Histoire, Portrait »."))
        else:
            from PyQt6.QtGui import QPixmap
            self.portrait.setPixmap(QPixmap())
            self.portrait.setText("🧍\nAucun portrait\n\nCliquez pour l'importer (onglet « Histoire, Portrait »)")
            self.portrait.setToolTip("Importez le portrait de votre personnage dans l'onglet « Histoire, Portrait ».")
        self.portrait.set_look(theme.current().muted, dashed=pix is None)

    def _on_portrait(self) -> None:
        if hasattr(self.win, "go_to_tab"):
            self.win.go_to_tab("rp")

    # ------------------------------------------------------------------ actions
    def drop_on_slot(self, slot: str, key: str) -> bool:
        """v53 : tuile du sac déposée sur une case (ou le portrait, `slot` vide) : équipée dans cette case si elle y
        va, sinon dans sa case naturelle."""
        ok, msg = self.engine.equip_from_bag(key, slot)
        self.win.statusBar().showMessage(msg, 7000)
        if ok:
            self.win.changed()
        return ok

    def _on_slot(self, key: str) -> None:
        """Case cliquée : objets de l'inventaire correspondant à son RÔLE (armure, arme, bouclier, anneau, cape…)."""
        eng, win = self.engine, self.win
        cands = eng.slot_inventory(key)
        doll = eng.paperdoll()
        labels = {}
        for c in cands:
            suffix = "  (porté ici)" if c["equipe"] else "  (remplace {})".format(doll[key]["nom"]) if key in doll else ""
            labels["{}{}".format(c["nom"], suffix)] = c
        if key in doll:
            labels[CLEAR] = None
        if not labels:
            where = ("le « Catalogue » du sac" if key not in MAGIC_SLOTS else
                     "le sous-onglet « Objets magiques »")
            win.statusBar().showMessage("Aucun objet de l'inventaire ne va en « {} » : ajoutez-en via {}.".format(
                SLOT_LABELS[key], where), 7000)
            return
        picked = ask_choice(win, SLOT_LABELS[key], "Objets de votre inventaire pour cette case (un objet par case) :",
                            list(labels))
        if not picked:
            return
        if labels[picked] is None:
            eng.unequip_slot(key)
            win.statusBar().showMessage("{} : case vidée (l'objet reste dans l'inventaire).".format(SLOT_LABELS[key]),
                                        5000)
        else:
            win.statusBar().showMessage(eng.equip_slot(key, labels[picked]), 7000)
        win.changed()
