"""
Moteur de thèmes graphiques : DIX thèmes « jeux vidéo » à dégradés, textures et cadres propres + audit WCAG.

    1. Porte de Baldur (BG3)   [défaut]   6. Cyberpunk 2077
    2. The Witcher 3                       7. Final Fantasy (Crystal Era)
    3. Skyrim                              8. Hollow Knight
    4. Dark Souls / Elden Ring             9. Mass Effect
    5. Diablo IV                          10. Zelda / RPG japonais

Équivalent des « variables CSS » : chaque thème est un objet `Theme` (palette + typographie + cadre + texture)
dont toutes les couleurs sont des variables injectées dans UNE SEULE feuille de style Qt (QSS) générée par
`build_stylesheet`. Ajouter un thème = ajouter une entrée dans `THEMES`.

Dégradés : QSS n'a pas de `linear-gradient` CSS ; l'équivalent est `qlineargradient(x1:0, y1:0, x2:0, y2:1,
stop:0 #A, stop:1 #B)`. Les textures (grain de cuir, lignes de balayage, grille holographique, runes...) sont des
tuiles PNG générées au premier lancement (voir `ui/textures.py`) et superposées aux dégradés très faiblement.

Accessibilité : chaque texte est audité (WCAG AA, >= 4,5:1) sur les DEUX extrémités de chaque dégradé ET avec la
texture à son maximum d'intensité ; bordures fonctionnelles >= 3:1 (`Theme.audit()`, `tests/`).
"""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_THEME = "bg3"

# --------------------------------------------------------------------------------------
# Couleurs : contraste WCAG et mélanges
# --------------------------------------------------------------------------------------


def _rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def luminance(hex_color: str) -> float:
    """Luminance relative WCAG 2.1."""
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in _rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    """Rapport de contraste entre deux couleurs (1 à 21)."""
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def blend(c1: str, c2: str, t: float) -> str:
    """Mélange linéaire de deux couleurs (t=0 -> c1, t=1 -> c2)."""
    a, b = _rgb(c1), _rgb(c2)
    return "#" + "".join(f"{round((x + (y - x) * t) * 255):02X}" for x, y in zip(a, b))


def vgrad(top: str, bottom: str) -> str:
    """Dégradé linéaire vertical QSS."""
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {top}, stop:1 {bottom})"


def brushed(base: str, amount: float = 0.07) -> str:
    """Dégradé « métal brossé » : reflet clair en haut, ombre en bas, nuance centrale = couleur de base."""
    hi, lo = blend(base, "#FFFFFF", amount), blend(base, "#000000", amount)
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {hi}, stop:0.5 {base}, stop:1 {lo})"


def best_text(*backgrounds: str) -> str:
    """Noir ou blanc : celui qui offre le meilleur contraste MINIMAL sur toutes les couleurs de fond données."""
    return max(("#000000", "#FFFFFF"), key=lambda c: min(contrast_ratio(c, b) for b in backgrounds))


TEXTURE_MARGIN = 0.06     # intensité maximale d'une texture (décalage de luminosité) prise en compte par l'audit


# --------------------------------------------------------------------------------------
# Définition d'un thème
# --------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Theme:
    key: str
    name: str
    game: str           # jeu / univers d'inspiration
    description: str
    # --- fonds en dégradé : (haut, bas)
    bg: str
    bg2: str
    panel: str
    panel2: str
    panel_alt: str      # bandeaux, en-têtes, onglets (rendus en « métal brossé »)
    input_bg: str
    # --- textes
    text: str
    muted: str          # texte secondaire (>= 4,5:1)
    accent_text: str    # accent utilisé comme couleur de TEXTE (>= 4,5:1)
    # --- bordures / ornements
    border: str         # bordure fonctionnelle (>= 3:1)
    ornament: str       # accent décoratif (filets, soulignements)
    # --- boutons (dégradé haut/bas, normal et survolé)
    button_bg: str
    button_bg2: str
    button_hover: str
    button_hover2: str
    button_text: str
    # --- états
    select_bg: str
    select_text: str
    warn: str
    good: str
    locked: str
    tooltip_bg: str
    tooltip_text: str
    # --- identité visuelle
    font: str = '"Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif'
    font_title: str = '"Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif'
    frame: str = "solid"        # style de cadre : solid | ridge | double | outset
    texture: str = ""           # type de tuile : grain | scan | runes | stone | embers | crystal | ink | hologram | leaf
    # --- finitions (v24) : vides / nulles = rendu d'origine (le thème BG3, référence, n'en utilise aucune)
    glow: str = ""              # lueur de survol / focus (bordures, onglets, champs, info-bulles)

    # ---- dérivés
    @property
    def row_alt(self) -> str:
        return blend(self.panel, self.panel_alt, 0.45)

    @property
    def highlight(self) -> str:
        """Surbrillance douce (lignes de compétences de classe...)."""
        return blend(self.panel2, self.ornament, 0.14)

    @property
    def alt_hi(self) -> str:
        return blend(self.panel_alt, "#FFFFFF", 0.07)

    @property
    def alt_lo(self) -> str:
        return blend(self.panel_alt, "#000000", 0.07)

    @property
    def danger_text(self) -> str:
        return best_text(self.warn, blend(self.warn, "#000000", 0.18))

    @property
    def frame_width(self) -> int:
        return {"double": 3, "ridge": 2, "outset": 2}.get(self.frame, 1)

    def audit(self) -> list[tuple[str, float, float]]:
        """Paires de couleurs sous le seuil WCAG : [(description, ratio, minimum)] (vide = tout est conforme)."""
        grounds = {"fond (haut)": self.bg, "fond (bas)": self.bg2, "panneau (haut)": self.panel,
                   "panneau (bas)": self.panel2, "bandeau": self.panel_alt, "bandeau clair": self.alt_hi,
                   "bandeau sombre": self.alt_lo, "champ": self.input_bg, "ligne alternée": self.row_alt,
                   "surbrillance": self.highlight}
        if self.texture:        # la texture éclaircit ou assombrit légèrement les fonds sur lesquels elle est posée
            for name in ("fond (haut)", "fond (bas)", "panneau (haut)", "panneau (bas)"):
                base = grounds[name]
                grounds[name + " + texture claire"] = blend(base, "#FFFFFF", TEXTURE_MARGIN)
                grounds[name + " + texture sombre"] = blend(base, "#000000", TEXTURE_MARGIN)
        checks: list[tuple[str, str, str, float]] = []
        for gname, g in grounds.items():
            checks.append((f"texte sur {gname}", self.text, g, 4.5))
            checks.append((f"texte atténué sur {gname}", self.muted, g, 4.5))
            checks.append((f"texte d'accent sur {gname}", self.accent_text, g, 4.5))
            checks.append((f"avertissement sur {gname}", self.warn, g, 4.5))
            checks.append((f"valeur positive sur {gname}", self.good, g, 4.5))
            checks.append((f"élément verrouillé sur {gname}", self.locked, g, 4.5))
        for label, bgc in (("bouton (haut)", self.button_bg), ("bouton (bas)", self.button_bg2),
                           ("bouton survolé (haut)", self.button_hover), ("bouton survolé (bas)", self.button_hover2)):
            checks.append((label, self.button_text, bgc, 4.5))
        checks += [
            ("interrupteur activé", self.good, blend(self.panel2, self.good, 0.22), 4.5),
            ("sélection", self.select_text, self.select_bg, 4.5),
            ("info-bulle", self.tooltip_text, self.tooltip_bg, 4.5),
            ("bouton danger (haut)", self.danger_text, self.warn, 4.5),
            ("bouton danger (bas)", self.danger_text, blend(self.warn, "#000000", 0.18), 4.5),
            ("bordure / fond", self.border, self.bg, 3.0),
            ("bordure / panneau", self.border, self.panel2, 3.0),
            ("bordure / champ", self.border, self.input_bg, 3.0),
        ]
        return [(label, round(contrast_ratio(fg, bgc), 2), minimum)
                for label, fg, bgc, minimum in checks if contrast_ratio(fg, bgc) < minimum]


# --------------------------------------------------------------------------------------
# Les dix thèmes (ordre = ordre des menus ; le premier est le thème par défaut)
# --------------------------------------------------------------------------------------
_SERIF = '"Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif'
_GOTHIC = '"Garamond", "Cambria", "Palatino Linotype", Georgia, serif'
_TECH = '"Bahnschrift", "Segoe UI", "Rajdhani", "Arial Narrow", Arial, sans-serif'
_CLEAN = '"Segoe UI", "Candara", "Calibri", "Helvetica Neue", Arial, sans-serif'

THEMES: dict[str, Theme] = {
    "bg3": Theme(
        key="bg3", name="Porte de Baldur (BG3)", game="Baldur's Gate 3",
        description="Cuir sombre, ors incrustés, bordeaux de vin et touches de pourpre profond.",
        bg="#181514", bg2="#110F0E", panel="#24201D", panel2="#2C2724", panel_alt="#35283A",
        input_bg="#1B1816", text="#E2D9CD", muted="#B6AA97", accent_text="#C5A059", border="#8A7340",
        ornament="#C5A059", button_bg="#7C2424", button_bg2="#611A1A", button_hover="#923030",
        button_hover2="#732121", button_text="#F3EADB", select_bg="#7A2F6B", select_text="#FFF4EC",
        warn="#E8A15A", good="#9ACD8E", locked="#B3A895", tooltip_bg="#0C0A09", tooltip_text="#E2D9CD",
        font=_SERIF, font_title=_SERIF, frame="ridge", texture="grain"),
    "witcher": Theme(
        key="witcher", name="The Witcher 3", game="The Witcher 3 : Wild Hunt",
        description="Cuir d'ombre et parchemin brûlé, or du médaillon de loup, sang séché sur les boutons.",
        bg="#15120E", bg2="#0F0D0A", panel="#201B15", panel2="#28221A", panel_alt="#2E2519",
        input_bg="#120F0B", text="#ECE2C8", muted="#C2B494", accent_text="#E0B44A", border="#9C7C32",
        ornament="#C9A13B", button_bg="#6E2A1C", button_bg2="#561F14", button_hover="#84341F",
        button_hover2="#672718", button_text="#FBEFD5", select_bg="#7A5A18", select_text="#FFF6DB",
        warn="#F0A062", good="#A9C977", locked="#BDAE8C", tooltip_bg="#0B0907", tooltip_text="#ECE2C8",
        font=_SERIF, font_title='"Garamond", "Palatino Linotype", Georgia, serif', frame="ridge", texture="grain",
        glow="#E8C266"),
    "skyrim": Theme(
        key="skyrim", name="Skyrim", game="The Elder Scrolls V : Skyrim",
        description="Givre nordique et ardoise, acier argenté, runes gravées et lueur bleutée des Draugr.",
        bg="#0D1015", bg2="#090B0F", panel="#141920", panel2="#1A2029", panel_alt="#232B36",
        input_bg="#0E1218", text="#EEF2F6", muted="#B7C0CA", accent_text="#B9D3EA", border="#7E8A98",
        ornament="#AFC2D6", button_bg="#3E4A58", button_bg2="#2D3742", button_hover="#4E5D6E",
        button_hover2="#3A4654", button_text="#FFFFFF", select_bg="#3D5A7A", select_text="#FFFFFF",
        warn="#E8B86A", good="#9ED2B4", locked="#A9B3BE", tooltip_bg="#07090C", tooltip_text="#EEF2F6",
        font=_SERIF, font_title=_SERIF, frame="ridge", texture="runes",       # même typographie que BG3
        glow="#CFE6FF"),
    "souls": Theme(
        key="souls", name="Dark Souls / Elden Ring", game="Dark Souls · Elden Ring",
        description="Cendres et pierre gothique, or de l'Arbre-Monde, silence mélancolique.",
        bg="#0E0D0B", bg2="#090807", panel="#181614", panel2="#201D19", panel_alt="#29251E",
        input_bg="#0C0B09", text="#E4DCC6", muted="#B2A88F", accent_text="#D9B969", border="#8A7A44",
        ornament="#C2A255", button_bg="#3E3627", button_bg2="#2B251B", button_hover="#524733",
        button_hover2="#3A3224", button_text="#F3EAD0", select_bg="#6E5B26", select_text="#FFF6D9",
        warn="#E9A866", good="#9CBB86", locked="#ADA48D", tooltip_bg="#050504", tooltip_text="#E4DCC6",
        font=_GOTHIC, font_title='"Garamond", "Georgia", serif', frame="double", texture="stone",
        glow="#E8CF85"),
    "diablo": Theme(
        key="diablo", name="Diablo IV", game="Diablo IV",
        description="Ténèbres de Sanctuaire, rouge sang, os blanchis et braises infernales.",
        bg="#0B0707", bg2="#070404", panel="#170E0D", panel2="#1F1311", panel_alt="#2A1714",
        input_bg="#0A0505", text="#ECDDD2", muted="#BCA79A", accent_text="#F0846F", border="#B4483A",
        ornament="#A8241C", button_bg="#8C1C15", button_bg2="#6A140F", button_hover="#A62519",
        button_hover2="#7E1A12", button_text="#FFF1E8", select_bg="#8C1C15", select_text="#FFF1E8",
        warn="#EDA552", good="#9FC57F", locked="#B5A396", tooltip_bg="#040202", tooltip_text="#ECDDD2",
        font='"Georgia", "Palatino Linotype", serif',
        font_title='"Trajan Pro", "Copperplate Gothic Bold", "Georgia", serif', frame="ridge", texture="embers",
        glow="#FF6A4A"),
    "cp2077": Theme(
        key="cp2077", name="Cyberpunk 2077", game="Cyberpunk 2077",
        description="Night City : néons cyan et magenta, jaune signalétique, biseaux sur nuit d'encre.",
        bg="#07070D", bg2="#0B0B16", panel="#10111F", panel2="#171A2C", panel_alt="#1F2240",
        input_bg="#06060C", text="#EFFBFF", muted="#A8C3D4", accent_text="#5EF2FF", border="#1FB5C4",
        ornament="#00F0FF", button_bg="#B8115F", button_bg2="#8A0C47", button_hover="#D4197A",
        button_hover2="#A50F5A", button_text="#FFFFFF", select_bg="#FCEE0A", select_text="#0A0A12",
        warn="#FCEE0A", good="#3DFFA8", locked="#A3B1CF", tooltip_bg="#000000", tooltip_text="#EFFBFF",
        font=_TECH, font_title=_TECH, frame="outset", texture="scan",
        glow="#FF2A9D"),
    "ff": Theme(
        key="ff", name="Final Fantasy (Crystal Era)", game="Final Fantasy",
        description="Nacre et saphir, cristaux dorés et élégance féerique lumineuse.",
        bg="#EEF4FC", bg2="#E1EBF8", panel="#FAFCFF", panel2="#EEF3FB", panel_alt="#DEE8F6",
        input_bg="#FFFFFF", text="#13233F", muted="#3C5379", accent_text="#1A4F9E", border="#5C81B4",
        ornament="#C9A75A", button_bg="#2A5DB0", button_bg2="#1F4890", button_hover="#326BC6",
        button_hover2="#2858A6", button_text="#FFFFFF", select_bg="#2F6FD0", select_text="#FFFFFF",
        warn="#8A3C08", good="#1A6038", locked="#465C80", tooltip_bg="#13233F", tooltip_text="#EEF4FC",
        font=_CLEAN, font_title='"Constantia", "Palatino Linotype", Georgia, serif', frame="solid",
        texture="crystal", glow="#7FB2E8"),
    "hollow": Theme(
        key="hollow", name="Hollow Knight", game="Hollow Knight",
        description="Nid-de-Hallow : noir d'encre, blanc d'os et lueur bleutée de l'âme.",
        bg="#09090A", bg2="#050506", panel="#121214", panel2="#18181B", panel_alt="#212126",
        input_bg="#08080A", text="#F0EEE8", muted="#B5B2AA", accent_text="#C9DAF0", border="#85858F",
        ornament="#DCD8CC", button_bg="#26262C", button_bg2="#1A1A1F", button_hover="#34343C",
        button_hover2="#25252B", button_text="#F6F3EA", select_bg="#DCD8CC", select_text="#09090A",
        warn="#E6AE66", good="#A9CDA3", locked="#A6A39A", tooltip_bg="#000000", tooltip_text="#F0EEE8",
        font='"Garamond", "Georgia", serif', font_title='"Garamond", "Georgia", serif', frame="solid",
        texture="ink", glow="#9FC3EE"),
    "masseffect": Theme(
        key="masseffect", name="Mass Effect", game="Mass Effect",
        description="Passerelle du Normandy : hologrammes bleu électrique, alertes ambrées, verre sombre.",
        bg="#03070D", bg2="#060D18", panel="#091221", panel2="#0E1A2F", panel_alt="#142643",
        input_bg="#040A14", text="#E7F2FF", muted="#A2B9D5", accent_text="#5CC2FF", border="#2F7ED4",
        ornament="#34B0FF", button_bg="#0F5AAE", button_bg2="#0A4588", button_hover="#1769C2",
        button_hover2="#0F55A6", button_text="#FFFFFF", select_bg="#125CB3", select_text="#FFFFFF",
        warn="#FFAE45", good="#5CE6B0", locked="#9AB2D0", tooltip_bg="#02050A", tooltip_text="#E7F2FF",
        font=_TECH, font_title=_TECH, frame="solid", texture="hologram", glow="#7FD4FF"),
    "zelda": Theme(
        key="zelda", name="Zelda / RPG japonais", game="The Legend of Zelda",
        description="Plaines d'Hyrule : parchemin clair, vert forêt, or de la Triforce.",
        bg="#F2EFDA", bg2="#E3E8C8", panel="#FBF9EB", panel2="#EFF2DA", panel_alt="#E1E9C2",
        input_bg="#FFFEF4", text="#26351A", muted="#45562C", accent_text="#3B5810", border="#6A893A",
        ornament="#C99A12", button_bg="#2F6B2A", button_bg2="#255721", button_hover="#387A31",
        button_hover2="#2E6828", button_text="#FFFFFF", select_bg="#3F7D2A", select_text="#FFFFFF",
        warn="#874000", good="#245E18", locked="#50613B", tooltip_bg="#26351A", tooltip_text="#F2EFDA",
        font='"Candara", "Trebuchet MS", "Segoe UI", sans-serif',
        font_title='"Candara", "Constantia", Georgia, serif', frame="ridge", texture="leaf",
        glow="#E2B93B"),
}

_current: Theme = THEMES[DEFAULT_THEME]


def current() -> Theme:
    """Thème actif (lu par les widgets qui colorent des éléments en code : verrouillé, surbrillance...)."""
    return _current


def resolve_key(key: str) -> str:
    """Clé de thème valide : une préférence inconnue (ancienne version) retombe sur le thème par défaut."""
    return key if key in THEMES else DEFAULT_THEME


def set_current(key: str) -> Theme:
    global _current
    _current = THEMES[resolve_key(key)]
    return _current


# --------------------------------------------------------------------------------------
# Feuille de style
# --------------------------------------------------------------------------------------
def build_stylesheet(t: Theme, font_px: int = 14, texture_url: str = "") -> str:
    """
    QSS complet d'un thème : dégradés (fenêtre, panneaux, onglets, en-têtes, menus, boutons), cadre propre au
    thème (ridge / double / outset), typographie et — si `texture_url` est fourni — texture superposée.
    """
    big, huge = font_px + 5, font_px + 7
    window, panel = vgrad(t.bg, t.bg2), vgrad(t.panel, t.panel2)
    metal = brushed(t.panel_alt)
    btn, btn_h, btn_p = vgrad(t.button_bg, t.button_bg2), vgrad(t.button_hover, t.button_hover2), \
        vgrad(t.button_bg2, t.button_bg)
    tex = f'background-image: url("{texture_url}");' if texture_url else ""
    fw = t.frame_width
    frame = t.frame if t.frame != "solid" else "solid"
    btn_frame = "outset" if t.frame == "outset" else "solid"
    danger = vgrad(t.warn, blend(t.warn, "#000000", 0.18))
    return f"""
* {{ font-family: {t.font}; font-size: {font_px}px; }}
QMainWindow, QDialog {{ background: {window}; {tex} }}
QTabWidget::pane {{ border: {fw}px {frame} {t.ornament}; background: {panel}; {tex} top: -1px; }}
QTabBar::tab {{ background: {metal}; color: {t.muted}; padding: 9px 18px; margin-right: 3px;
               border: 1px solid {t.border}; border-bottom: none;
               border-top-left-radius: 8px; border-top-right-radius: 8px; }}
QTabBar::tab:selected {{ background: {panel}; color: {t.accent_text}; font-weight: bold;
                        border-bottom: 3px solid {t.ornament}; }}
QTabBar::tab:hover:!selected {{ color: {t.text}; background: {vgrad(t.alt_hi, t.panel_alt)}; }}
QGroupBox {{ background: {panel}; {tex} border: {fw}px {frame} {t.ornament}; border-radius: 8px;
            margin-top: 18px; padding: 14px 10px 10px 10px; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 14px; padding: 1px 10px; color: {t.accent_text};
                   background: {metal}; border: 1px solid {t.ornament}; border-radius: 6px; font-weight: bold;
                   font-family: {t.font_title}; }}
QLabel {{ background: transparent; color: {t.text}; }}
QLabel[role="title"] {{ color: {t.accent_text}; font-size: {big}px; font-weight: bold; font-family: {t.font_title}; }}
QLabel[role="muted"] {{ color: {t.muted}; }}
QLabel[clickable="true"] {{ text-decoration: underline; }}
QLabel[clickable="true"]:hover {{ color: {t.text}; background: {vgrad(t.panel, t.panel2)}; border-radius: 4px; }}
QFrame[role="abcard"] {{ background: {vgrad(t.panel2, t.panel)}; border: 1px solid {t.ornament}; border-radius: 10px; }}
QLabel[role="abbr"] {{ color: {t.accent_text}; font-size: {huge}px; font-weight: bold; font-family: {t.font_title};
                      letter-spacing: 2px; }}
QLabel[role="abtotal"] {{ color: {t.text}; font-size: {huge + 9}px; font-weight: bold; font-family: {t.font_title}; }}
QLabel[role="abmod"] {{ background: {metal}; color: {t.accent_text}; border: 1px solid {t.ornament};
                       border-radius: 11px; padding: 1px 10px; font-weight: bold; font-size: {big}px; }}
QLabel[role="abpart"] {{ color: {t.muted}; font-size: {font_px - 1}px; }}
QLabel[role="warn"] {{ color: {t.warn}; font-weight: bold; }}
QLabel[role="stat"] {{ color: {t.accent_text}; font-size: {huge}px; font-weight: bold; font-family: {t.font_title}; }}
QLabel[role="head"] {{ color: {t.accent_text}; font-weight: bold; }}
QLabel[role="badge"] {{ background: {metal}; border: 1px solid {t.ornament}; border-radius: 8px;
                       padding: 5px 12px; color: {t.text}; font-weight: bold; }}
QLabel[role="portrait"] {{ background: {panel}; color: {t.muted}; border: 4px {frame if fw > 1 else "solid"} {t.ornament};
                          border-radius: 10px; padding: 4px; }}
QPushButton[role="step"] {{ padding: 4px 0; font-size: {big}px; }}
QLabel[role="chip"] {{ background: {vgrad(t.panel, t.panel2)}; color: {t.text}; border: 1px solid {t.ornament};
                      border-radius: 10px; padding: 2px 8px; font-weight: bold; }}
QLabel[role="chip"]:hover {{ border: 1px solid {t.accent_text}; color: {t.accent_text}; }}
QLabel[role="chip"][state="ok"] {{ border: 2px solid {t.good}; }}
QLabel[role="chip"][state="used"] {{ color: {t.locked}; border: 1px dashed {t.border}; }}
QLabel[role="chip"][state="active"] {{ border: 2px solid {t.accent_text}; color: {t.accent_text}; }}
QLabel[role="banner"] {{ background: {metal}; border: 2px solid {t.accent_text}; border-radius: 8px;
                        padding: 6px 12px; color: {t.accent_text}; font-weight: bold; }}
QLineEdit, QPlainTextEdit, QTextEdit, QTextBrowser {{ background: {t.input_bg}; color: {t.text};
    border: 1px solid {t.border}; border-radius: 5px; padding: 3px 6px;
    selection-background-color: {t.select_bg}; selection-color: {t.select_text}; }}
QLineEdit:focus, QPlainTextEdit:focus {{ border: 2px solid {t.ornament}; }}
QPushButton {{ background: {btn}; color: {t.button_text}; border: {2 if btn_frame == "outset" else 1}px {btn_frame} {t.ornament};
              border-radius: 6px; padding: 7px 16px; font-weight: bold; }}
QPushButton:hover {{ background: {btn_h}; }}
QPushButton:pressed {{ background: {btn_p}; }}
QPushButton:disabled {{ background: {vgrad(t.panel, t.panel2)}; color: {t.locked}; border: 1px solid {t.border}; }}
QPushButton[role="danger"] {{ background: {danger}; color: {t.danger_text}; border: 1px solid {t.warn}; }}
QPushButton[role="ghost"] {{ background: {vgrad(t.panel, t.panel2)}; color: {t.text}; border: 2px solid {t.ornament}; }}
QPushButton[role="ghost"]:hover {{ background: {btn_h}; color: {t.button_text}; }}
QPushButton[role="ghost"]:focus, QPushButton:default {{ border: 2px solid {t.accent_text}; }}
QPushButton[role="attune"] {{ background: {vgrad(t.panel, t.panel2)}; color: {t.text}; border: 2px solid {t.ornament};
                             border-radius: 13px; padding: 4px 14px; font-weight: bold; }}
QPushButton[role="attune"]:hover {{ border: 2px solid {t.accent_text}; }}
QPushButton[role="attune"]:checked {{ background: {btn}; color: {t.button_text}; border: 2px solid {t.accent_text}; }}
QPushButton[role="attune"]:disabled {{ background: {vgrad(t.panel, t.panel2)}; color: {t.locked}; border: 1px dashed {t.border}; }}
QPushButton[role="toggle"] {{ background: {vgrad(t.panel, t.panel2)}; color: {t.muted}; border: 1px dashed {t.border};
                             border-radius: 12px; padding: 3px 12px; font-weight: normal; }}
QPushButton[role="toggle"]:hover {{ background: {vgrad(t.highlight, t.panel2)}; color: {t.text};
                                   border: 1px solid {t.accent_text}; }}
QPushButton[role="toggle"]:checked {{ background: {vgrad(blend(t.panel2, t.good, 0.22), blend(t.panel, t.good, 0.12))};
                                     color: {t.good}; border: 1px solid {t.good}; font-weight: bold; }}
QPushButton[role="toggle"]:checked:hover {{ border: 2px solid {t.accent_text}; }}
QPushButton[role="toggle"]:disabled {{ background: {vgrad(t.panel, t.panel2)}; color: {t.locked}; border: 1px dotted {t.border}; }}
QFrame#dialogCard {{ background: {panel}; border: {max(fw, 2)}px {frame} {t.ornament}; border-radius: 14px; }}
QFrame#themeCard {{ background: transparent; }}
QCheckBox {{ spacing: 7px; background: transparent; color: {t.text}; }}
QTableWidget, QListWidget, QTreeWidget {{ background: {t.input_bg}; alternate-background-color: {t.row_alt};
    color: {t.text}; border: 1px solid {t.border}; gridline-color: {t.panel_alt};
    selection-background-color: {t.select_bg}; selection-color: {t.select_text}; }}
QTableWidget::item {{ padding: 3px; }}
QHeaderView::section {{ background: {metal}; color: {t.text}; padding: 6px; border: 1px solid {t.border};
                       font-weight: bold; }}
QMenuBar {{ background: {metal}; color: {t.text}; }}
QMenuBar::item {{ padding: 5px 12px; background: transparent; }}
QMenuBar::item:selected {{ background: {btn}; color: {t.button_text}; }}
QMenu {{ background: {panel}; color: {t.text}; border: 1px solid {t.ornament}; }}
QMenu::item {{ padding: 6px 26px; }}
QMenu::item:selected {{ background: {btn}; color: {t.button_text}; }}
QStatusBar {{ background: {metal}; color: {t.text}; }}
QToolTip {{ background-color: {t.tooltip_bg}; color: {t.tooltip_text}; border: 1px solid {t.ornament};
           padding: 6px; opacity: 255; }}
QSplitter::handle {{ background: {t.ornament}; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QScrollBar:vertical {{ background: {t.input_bg}; width: 14px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {btn}; border: 1px solid {t.ornament}; border-radius: 6px; min-height: 30px; }}
QScrollBar:horizontal {{ background: {t.input_bg}; height: 14px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {btn}; border: 1px solid {t.ornament}; border-radius: 6px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
""" + polish_stylesheet(t, font_px)


def polish_stylesheet(t: Theme, font_px: int = 14) -> str:
    """
    Finitions « ultra-léchées » des thèmes qui définissent une lueur (`glow`) : titres soulignés, liserés
    lumineux au survol et au focus, onglets et en-têtes soulignés, listes survolées, info-bulles arrondies.
    Le thème BG3 (référence) n'a pas de lueur : sa feuille de style reste strictement celle d'origine.
    """
    if not t.glow:
        return ""
    btn_h = vgrad(t.button_hover, t.button_hover2)
    soft = blend(t.panel2, t.glow, 0.10)
    return f"""
QGroupBox::title {{ padding: 2px 12px; border: 1px solid {t.ornament};
                   border-bottom: 2px solid {t.glow}; }}
QGroupBox {{ border-radius: 10px; }}
QTabBar::tab:selected {{ border-top: 2px solid {t.glow}; border-bottom: 3px solid {t.ornament}; }}
QTabBar::tab:hover:!selected {{ border: 1px solid {t.glow}; border-bottom: none; color: {t.text}; }}
QHeaderView::section {{ border-bottom: 2px solid {t.ornament}; }}
QPushButton:hover {{ background: {btn_h}; border: 1px solid {t.glow}; }}
QPushButton:focus {{ border: 1px solid {t.glow}; }}
QPushButton[role="ghost"]:hover, QPushButton[role="attune"]:hover {{ border: 2px solid {t.glow}; }}
QLineEdit:hover, QPlainTextEdit:hover, QTextEdit:hover, QComboBox:hover, QSpinBox:hover {{ border: 1px solid {t.glow}; }}
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus {{ border: 2px solid {t.glow}; }}
QComboBox, QSpinBox {{ background: {t.input_bg}; color: {t.text}; border: 1px solid {t.border}; border-radius: 5px;
                      padding: 3px 8px; selection-background-color: {t.select_bg}; selection-color: {t.select_text}; }}
QComboBox QAbstractItemView {{ background: {t.input_bg}; color: {t.text}; border: 1px solid {t.glow};
                              selection-background-color: {t.select_bg}; selection-color: {t.select_text}; }}
QTableWidget::item:hover, QListWidget::item:hover {{ background: {soft}; }}
QLabel[role="chip"]:hover {{ border: 1px solid {t.glow}; }}
QLabel[role="badge"], QLabel[role="banner"] {{ border-color: {t.glow}; }}
QPushButton[role="toggle"]:hover {{ border: 1px solid {t.glow}; }}
QToolTip {{ border: 1px solid {t.glow}; border-radius: 6px; padding: 7px; }}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{ background: {btn_h}; border: 1px solid {t.glow}; }}
QSplitter::handle:hover {{ background: {t.glow}; }}
QFrame#dialogCard {{ border-radius: 16px; }}
"""


def apply_palette(app, t: Theme) -> None:
    """Palette Qt (style Fusion) : champs, listes déroulantes et compteurs suivent le thème."""
    from PyQt6.QtGui import QColor, QPalette
    pal = QPalette()
    roles = {
        QPalette.ColorRole.Window: t.bg, QPalette.ColorRole.WindowText: t.text,
        QPalette.ColorRole.Base: t.input_bg, QPalette.ColorRole.AlternateBase: t.row_alt,
        QPalette.ColorRole.Text: t.text, QPalette.ColorRole.Button: t.panel_alt,
        QPalette.ColorRole.ButtonText: t.text, QPalette.ColorRole.Highlight: t.select_bg,
        QPalette.ColorRole.HighlightedText: t.select_text, QPalette.ColorRole.ToolTipBase: t.tooltip_bg,
        QPalette.ColorRole.ToolTipText: t.tooltip_text, QPalette.ColorRole.PlaceholderText: t.muted,
        QPalette.ColorRole.Mid: t.border, QPalette.ColorRole.Dark: t.border,
        QPalette.ColorRole.Light: t.panel2, QPalette.ColorRole.Link: t.accent_text,
    }
    for role, color in roles.items():
        pal.setColor(role, QColor(color))
    for role in (QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText, QPalette.ColorRole.WindowText):
        pal.setColor(QPalette.ColorGroup.Disabled, role, QColor(t.locked))
    app.setPalette(pal)


def apply_theme(app, key: str, font_px: int = 14) -> Theme:
    """Applique un thème à TOUTE l'application, à chaud (palette + feuille de style + texture)."""
    from .textures import texture_url
    t = set_current(key)
    app.setStyle("Fusion")
    apply_palette(app, t)
    app.setStyleSheet(build_stylesheet(t, font_px, texture_url(t)))
    return t
