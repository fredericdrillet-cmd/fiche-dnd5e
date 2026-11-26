"""
Grille de cartes à choisir (v53) — espèce, classe, historique dans l'assistant de création, façon jeu de rôle :
image ou icône carrée, nom dessous, description au survol ; un clic choisit.
"""
from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import QListWidget, QListWidgetItem

from core.rules import norm
from . import icons as IC
from . import theme
from .common import blocked

# v53 : icône de chaque classe — [(dessin de core/action_icons.G, x, y, échelle, angle)], dessinés dans l'ordre
CLASS_LAYERS = {
    "artificier": [("marteau", 23, 30, 0.7, -25), ("cle_plate", 42, 28, 0.6, 25), ("fiole", 47, 48, 0.42, 0)],
    "barbare": [("grande_hache", 32, 32, 0.95, 28)],
    "barde": [("note", 32, 32, 0.88, 0)],
    "clerc": [("masse", 32, 32, 0.95, 30)],
    "druide": [("serpe", 30, 31, 0.86, 0), ("feuille", 47, 46, 0.5, -10)],
    "ensorceleur": [("flamme", 27, 29, 0.8, 0), ("sang", 47, 46, 0.45, 0)],
    "guerrier": [("epee_longue", 32, 32, 1.0, 0)],
    "magicien": [("magie", 32, 18, 0.58, 0), ("livre", 32, 42, 0.68, 0)],
    "moine": [("main", 32, 32, 0.88, 0)],
    "occultiste": [("magie", 32, 20, 0.62, 0), ("oeil", 32, 40, 0.8, 0)],
    "paladin": [("ecu", 32, 32, 0.92, 0)],
    "rodeur": [("arc", 27, 30, 0.8, 0), ("patte", 47, 47, 0.42, 0)],
    "roublard": [("dague", 26, 33, 0.85, 0), ("masque", 45, 16, 0.42, 0), ("cle", 47, 45, 0.5, 35)],
}

BACKGROUND_GLYPHS = [   # (fragment du nom normalisé, dessin, médaillon) — le plus précis d'abord
    ("idiot du village", "cerveau", "spirale"), ("enfant trouve des geants", "pierres", "main"),
    ("rejeton d'aventurier", "etoile", "epee"), ("stagiaire rival", "livre", "eclair"),
    ("etudiant de lorehold", "livre", "pierres"), ("etudiant de prismari", "livre", "flamme"),
    ("etudiant de quandrix", "livre", "spirale"), ("etudiant de silverquill", "livre", "note"),
    ("etudiant de witherbloom", "livre", "feuille"), ("mage de la haute sorcellerie", "etoile", "baguette"),
    ("garde de la cite (variante", "lance", "loupe"), ("garde de la cite", "lance", "porte"),
    ("chasseur de primes urbain", "cible", "porte"), ("chasseur de primes", "cible", "diamant"),
    ("chevalier de solamnie", "bouclier", "couronne"), ("chevalier de l'ordre", "bouclier", "glyphe"),
    ("membre de tribu", "hache", "patte"), ("membre de guilde", "anneau", "outil"),
    ("marchand de guilde", "diamant", "anneau"), ("marchand failli", "diamant", "chaine_brisee"),
    ("artisan de clan", "marteau", "rune"), ("artisan de guilde", "outil", "anneau"), ("artisan local", "outil", ""),
    ("voyageur lointain", "portail", "vent"), ("veteran mercenaire", "epee", "sablier"),
    ("noblesse d'epee", "couronne", "epee"), ("noblesse de robe", "couronne", "parchemin"),
    ("noble waterdhavien", "couronne", "vague"), ("sang bleu", "couronne", "goutte"),
    ("bandit de grand chemin", "epee", "masque"), ("voleur a la tire", "main", "anneau"),
    ("enfant des rues", "main", "retour"), ("gens du voyage", "vent", "botte"), ("habitant de la foret", "feuille", ""),
    ("gardien tribal", "lance", "feuille"), ("graveur de runes", "rune", "marteau"), ("homme de loi", "parchemin", "bouclier"),
    ("homme-medecine", "soin", "feuille"), ("heros du peuple", "etoile", "main"), ("pilleur de ruines", "pierres", "diamant"),
    ("agent de faction", "masque", "glyphe"), ("agent de maison", "couronne", "masque"),
    ("agent volstrucker", "masque", "dague"), ("erudit cloitre", "livre", "porte"),
    ("acolyte", "soleil", ""), ("devot", "soleil", "note"), ("predicateur", "soleil", "ondes"),
    ("inquisiteur", "oeil", "flamme"), ("initie", "glyphe", ""), ("anthropologue", "loupe", "coeur"),
    ("archeolog", "loupe", "pierres"), ("artisan", "marteau", "outil"), ("artiste", "note", ""),
    ("saltimbanque", "note", "etoile"), ("assassin", "dague", "crane"), ("athlete", "poing", "botte"),
    ("brigand", "hache", "masque"), ("batard", "couronne", "chaine_brisee"), ("cambrioleur", "main", "diamant"),
    ("captif", "chaine", ""), ("charlatan", "masque", "gemme"), ("escroc", "masque", ""), ("grinner", "masque", "note"),
    ("chasseur", "arc", "patte"), ("chevalier", "bouclier", "epee"), ("colporteur", "diamant", "botte"),
    ("commercant", "diamant", "main"), ("marchand", "diamant", ""), ("courtisan", "couronne", "note"),
    ("crapule", "poing", "masque"), ("criminel", "dague", "masque"), ("cuisinier", "fiole", "flamme"),
    ("enqueteur", "loupe", "oeil"), ("limier", "loupe", "patte"), ("ermite", "lune", "feuille"),
    ("solitaire", "oeil_clos", ""), ("espion", "oeil", "masque"), ("explorateur", "fleche", "feuille"),
    ("eclaireur", "oeil", "fleche"), ("patrouilleur", "bouclier", "fleche"), ("guide", "fleche_haut", ""),
    ("fermier", "feuille", "terre"), ("laboureur", "terre", ""), ("villageois", "feuille", "porte"),
    ("journalier", "outil", "sablier"), ("manouvrier", "marteau", ""), ("fugitif", "botte", "chaine_brisee"),
    ("garde", "lance", "bouclier"), ("gladiateur", "epee", "couronne"), ("hante", "crane", "brume"),
    ("juriste", "parchemin", "glyphe"), ("medecin", "soin", ""), ("rebouteux", "soin", "main"),
    ("heritier", "couronne", "anneau"), ("itinerant", "botte", ""), ("vagabond", "botte", "lune"),
    ("joueur", "cycle", "diamant"), ("matelot", "vague", "fleche"), ("marin", "vague", ""), ("pirate", "vague", "crane"),
    ("mercenaire", "epee", "diamant"), ("militaire", "epee", "bouclier"), ("officier", "epee", "etoile"),
    ("soldat", "epee", ""), ("naturaliste", "feuille", "loupe"), ("noble", "couronne", ""),
    ("palefrenier", "patte", "botte"), ("plaignant", "parchemin", "main"), ("precepteur", "livre", "main"),
    ("primitif", "griffes", ""), ("sauvageon", "patte", ""), ("repenti", "coeur", "chaine_brisee"),
    ("sage", "livre", ""), ("erudit", "livre", "loupe"), ("scribe", "parchemin", ""), ("serveur", "fiole", "main"),
    ("serviteur", "main", "porte"), ("trappeur", "patte", "chaine"), ("voyageur", "fleche", "vent"),
    ("mendiant", "main", ""), ("miserable", "main", "goutte"), ("misereux", "main", "goutte"), ("orphelin", "coeur", "main"),
]


def background_glyphs(name: str) -> tuple[str, str]:
    n = norm(name.replace(" (2024)", ""))
    return next(((m, b) for k, m, b in BACKGROUND_GLYPHS if k in n), ("parchemin", ""))


def _rounded(src: QPixmap, size: int) -> QPixmap:
    """Image « couverture » carrée aux coins arrondis, cadre de la couleur du thème."""
    out = QPixmap(size, size)
    out.fill(Qt.GlobalColor.transparent)
    scaled = src.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation)
    x, y = (scaled.width() - size) // 2, (scaled.height() - size) // 2
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(1, 1, size - 2, size - 2, size * 0.14, size * 0.14)
    p.setClipPath(path)
    p.drawPixmap(0, 0, scaled.copy(x, y, size, size))
    p.setClipping(False)
    p.setPen(QPen(QColor(theme.current().ornament), 2))
    p.drawPath(path)
    p.end()
    return out


def race_pixmap(race: str, size: int = 72, subrace: str = "") -> QPixmap:
    from .race_portrait import find_race_image
    path = find_race_image(race, subrace)            # v53 : la sous-race a son propre portrait (Elfe des bois…)
    if path and IC.HAS_SVG:
        src = QPixmap(str(path))
        try:
            if not src.isNull():
                return _rounded(src, size)
        except TypeError:
            pass
    return IC.icon_pixmap("capacite_espece", "capacite", size)


def _glyph_pixmap(main: str, badge: str, category: str, size: int) -> QPixmap:
    from core.action_icons import pair_body
    return IC._render(pair_body(main, badge), category, size, theme.current().key, False)


def class_pixmap(name: str, size: int = 72) -> QPixmap:
    from core.action_icons import layered_body
    layers = CLASS_LAYERS.get(norm(name.split(" (")[0]), [("etoile", 32, 32, 0.8, 0)])
    return IC._render(layered_body(layers), "capacite", size, theme.current().key, False)


def background_pixmap(name: str, size: int = 72) -> QPixmap:
    main, badge = background_glyphs(name)
    return _glyph_pixmap(main, badge, "commune", size)


class CardPicker(QListWidget):
    """Grille de cartes à sélection unique : set_items([(nom, pixmap, infobulle)]), select(nom) ; on_pick(nom)."""

    def __init__(self, on_pick: Callable[[str], None], icon: int = 72, cell=(122, 116), height: int = 270,
                 max_height: Optional[int] = None):
        super().__init__()
        self._on_pick = on_pick
        self._key = None
        IC.card_grid(self, icon, cell)
        try:
            self.setMinimumHeight(height)
            if max_height:                               # v53 : sans plafond, la grille prend la place libre
                self.setMaximumHeight(max_height)
            self.setTextElideMode(Qt.TextElideMode.ElideNone)   # nom complet, sur deux lignes
            self.setUniformItemSizes(False)
            self.setSpacing(4)
            self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        except (AttributeError, TypeError):
            pass
        self.itemClicked.connect(self._clicked)

    def set_items(self, rows: list[tuple[str, Optional[QPixmap], str]], labels: Optional[dict] = None) -> None:
        """`labels` : texte affiché quand il diffère de la clé (variantes « race|sous-race »)."""
        key = tuple(r[0] for r in rows) + (theme.current().key,)
        if key == self._key:
            return
        self._key = key
        with blocked(self):
            self.clear()
            for name, pix, tip in rows:
                it = QListWidgetItem((labels or {}).get(name, name).replace(" (2024)", ""))
                it.setData(Qt.ItemDataRole.UserRole, name)
                if pix is not None and IC.HAS_SVG:
                    it.setIcon(QIcon(pix))
                if tip:
                    it.setToolTip(tip)
                self.addItem(it)

    def select(self, name: str) -> None:
        with blocked(self):
            for i in range(self.count()):
                it = self.item(i)
                if it.data(Qt.ItemDataRole.UserRole) == name:
                    self.setCurrentItem(it)
                    try:
                        self.scrollToItem(it)
                    except (AttributeError, TypeError):
                        pass
                    return

    def _clicked(self, it) -> None:
        name = it.data(Qt.ItemDataRole.UserRole)
        if name:
            self._on_pick(name)
