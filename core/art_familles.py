"""
Dessins propres (v53) des familles d'icônes qui se ressemblaient : les « Mot de pouvoir » (la parole prononcée,
deux ondes de chaque côté, et l'effet au centre en grand), les options de Métamagie (l'étoile magique transformée
selon l'option) et les types de compagnons. Grille 64 × 64, blanc = dessin, noir = découpe.
"""
from __future__ import annotations

from .art_armes import Cc, K, L, S, burst, curved_arrow, over, star4
from .art_kit import black, doorway, figure, horse, place, ring
from .art_motifs import MOTIFS as M


def spoken(inner: str, s: float = 0.86) -> str:
    """Mot prononcé : effet au centre en grand, une onde de parole de chaque côté, détouré par-dessus."""
    waves = S("M5 22 C1 28 1 36 5 42", 3.4) + S("M59 22 C63 28 63 36 59 42", 3.4)
    return over(waves, place(inner, 32, 32, s), 6)


def _word_heal():
    return M["soin"]()


def _word_pain():
    return burst(32, 32, 28, 9) + Cc(32, 32, 9, K) + L([(26, 26), (38, 38)], 3) + L([(38, 26), (26, 38)], 3)


def _word_fortify():
    return place(M["poing"](), 32, 32, 0.95) + star4(52, 10, 6)


def _word_stun():
    return Cc(32, 36, 16) + Cc(32, 36, 10, K) + Cc(32, 36, 4) + star4(14, 12, 6) + star4(32, 6, 5) + star4(50, 12, 6)


def _word_return():
    return doorway() + black(place(curved_arrow("M44 44 V30 C44 20 36 16 28 16 H18", (12, 16), 180, 6, 12), 32, 36, 0.6))


POWER_WORDS = {
    "Mot de pouvoir douloureux": lambda: spoken(_word_pain()),
    "Mot de pouvoir fortifiant": lambda: spoken(_word_fortify()),
    "Mot de pouvoir étourdissant": lambda: spoken(_word_stun()),
    "Mot de pouvoir guérisseur": lambda: spoken(_word_heal()),
    "Mot de pouvoir mortel": lambda: spoken(M["crane"]()),
    "Mot de retour": lambda: spoken(_word_return()),
    "Parole divine": lambda: spoken(M["soleil"](), 0.86),
}


def _spark(x=32, y=32, r=22):
    return star4(x, y, r) + Cc(x, y, r * 0.18, K)


METAMAGIC = {
    "metamagie : sort accelere": lambda: _spark(38, 32, 20) + "".join(L([(4, y), (4 + w, y)], 3.6) for y, w in ((22, 14), (32, 18), (42, 14))),
    "metamagie : sort ample": lambda: _spark(32, 32, 14) + "".join(
        '<circle cx="32" cy="32" r="{}" fill="none" stroke="#FFFFFF" stroke-width="{}"/>'.format(r, w) for r, w in ((21, 3.4), (28, 2.4))),
    "metamagie : sort amplifie": lambda: _spark(32, 36, 16) + _spark(20, 22, 9) + _spark(46, 14, 7),
    "metamagie : sort distant": lambda: _spark(50, 14, 12) + '<path d="M6 58 C18 40 30 28 40 22" fill="none" stroke="#FFFFFF" '
                                                             'stroke-width="3" stroke-dasharray="5 4"/>' + Cc(6, 58, 4),
    "metamagie : sort etendu": lambda: _spark(26, 30, 18) + over("", place(M["sablier"](), 48, 46, 0.42), 7),
    "metamagie : sort intensifie": lambda: over(place(M["flamme"](), 32, 32, 1.0), _spark(32, 40, 11), 5),
    "metamagie : sort prevenant": lambda: place(M["oeil"](), 32, 34, 1.0) + black(_spark(32, 34, 7)),
    "metamagie : sort prudent": lambda: _spark(32, 14, 10) + S("M8 40 C8 24 56 24 56 40", 4) + figure(20, 46, 0.45)
                                         + figure(32, 46, 0.45) + figure(44, 46, 0.45),
    "metamagie : sort renforce": lambda: over(place(M["poing"](), 30, 38, 0.85), _spark(48, 16, 12), 6),
}


def _familiar():
    from .art_retouches import owl
    return owl()


def _companion():
    from .art_retouches import wolf_profile
    return wolf_profile(32, 32, 1.0)


def _summons():
    return ring(M["portail"](), True)


COMPANIONS = {"familiar": _familiar, "class_companion": _companion, "summons": _summons, "mount": horse}
