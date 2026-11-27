"""
Icônes soignées (v53) des états et effets actifs (core/effects.EFFECTS) : un dessin pour chaque état officiel
(À terre, Aveuglé, Charmé…), le dessin du sort ou de la capacité d'origine quand il existe (Bénédiction, Hâte, Rage…),
sinon un motif composé (bouclier + type de dégâts pour les résistances, etc.). Grille 64 × 64, blanc = dessin.
"""
from __future__ import annotations

from typing import Optional

from .art_actions import figure, hand, lightning
from .art_armes import Cc, G, K, L, P, R, S, eye, heart, over, star4
from .art_motifs import MOTIFS as M


def _lying():
    return (G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H6 L5 26 H-5 L-6 8 H-12 Z"), 34, 44, 90, 0.9)
            + L([(4, 58), (60, 58)], 3.4) + curved_arrow_down())


def curved_arrow_down():
    return S("M48 8 C56 14 56 24 50 30", 3.2) + P("M50 34 L44 26 L54 26 Z")


def _grappled():
    return over(hand(22, 34, 0.8, 70), hand(42, 30, 0.8, -110))


def _deafened():
    ear = P("M34 8 C46 8 52 18 52 28 C52 38 44 40 42 46 C40 52 36 56 30 56 C24 56 20 52 20 46 L26 46 C26 49 28 50 30 50 "
            "C34 50 36 46 38 42 C40 36 46 34 46 28 C46 20 41 14 34 14 C27 14 22 20 22 26 L16 26 C16 16 24 8 34 8 Z")
    return ear + L([(8, 8), (56, 56)], 6) + L([(8, 8), (56, 56)], 2.4, K)


def _blinded():
    return eye(32, 32, 1.1) + L([(8, 8), (56, 56)], 6) + L([(8, 8), (56, 56)], 2.4, K)


def _charmed():
    return (heart(32, 34, 1.1) + S("M32 30 a3 3 0 1 1 3 3 a6 6 0 1 1 -6 -6 a9 9 0 1 1 9 9", 3, K)
            + star4(54, 10, 5) + star4(10, 10, 4))


def _frightened():
    face = P("M32 8 C46 8 54 16 54 30 C54 46 44 56 32 56 C20 56 10 46 10 30 C10 16 18 8 32 8 Z")
    return (face + '<ellipse cx="24" cy="28" rx="4.4" ry="6" fill="#000000"/><ellipse cx="40" cy="28" rx="4.4" ry="6" fill="#000000"/>'
            + '<ellipse cx="32" cy="44" rx="5" ry="7" fill="#000000"/>' + S("M16 16 L24 20", 3, K) + S("M48 16 L40 20", 3, K))


def _poisoned():
    return (
        P("M26 4 H38 V10 H36 V18 C46 22 52 30 52 40 C52 52 44 60 32 60 C20 60 12 52 12 40 C12 30 18 22 28 18 V10 H26 Z")
        + G(Cc(0, -4, 8, K) + R(-5, 2, 10, 6, 2, K) + Cc(-3, -4, 2.4) + Cc(3, -4, 2.4) + R(-1, 4, 2, 4, 0), 32, 42))


def _restrained():
    return over(figure(32, 32, 1.1), M["chaine"](), 5)


def _stunned():
    return (Cc(32, 40, 18) + S("M22 36 L28 42 M28 36 L22 42", 2.6, K) + S("M36 36 L42 42 M42 36 L36 42", 2.6, K)
            + star4(14, 12, 6) + star4(32, 6, 5) + star4(50, 12, 6))


def _incapacitated():
    return figure(32, 34, 1.0) + '<circle cx="32" cy="32" r="27" fill="none" stroke="#FFFFFF" stroke-width="4.4"/>' \
        + L([(13, 13), (51, 51)], 4.4)


def _unconscious():
    z = lambda x, y, s: '<path transform="translate({} {}) scale({})" d="M0 0 h12 v3 l-8 9 h8 v3 h-13 v-3 l8 -9 h-7 Z" fill="#FFFFFF"/>'.format(x, y, s)
    return (G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H6 L5 26 H-5 L-6 8 H-12 Z"), 30, 50, 90, 0.8)
            + z(36, 6, 1.1) + z(48, 22, 0.8) + z(22, 18, 0.6))


def _invisible():
    return figure(32, 32, 1.15).replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2.6" '
                                                          'stroke-dasharray="4 3"') + star4(52, 10, 5)


def _paralyzed():
    return over(figure(32, 32, 1.15), lightning(46, 22, 0.55) + lightning(18, 40, 0.45))


def _petrified():
    return (figure(32, 32, 1.15) + L([(26, 14), (30, 24), (26, 32)], 2, K) + L([(36, 34), (40, 44), (34, 52)], 2, K)
            + L([(4, 60), (60, 60)], 3))


def _exhaustion():
    return (G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H6 L5 26 H-5 L-6 8 H-12 Z"), 30, 34, 20, 1.0)
            + P("M46 18 C52 26 54 32 50 38 C46 40 42 36 44 30 Z") + P("M54 34 C57 38 58 42 55 44 C52 45 51 42 52 40 Z"))


def _surprised():
    return (R(26, 4, 12, 36, 6) + Cc(32, 52, 7) + star4(10, 14, 5) + star4(54, 14, 5))


def _bleeding():
    return M["goutte"]() + P("M10 50 C14 44 18 50 14 56 Z") + P("M50 52 C54 46 58 52 54 58 Z")


def _burning():
    return M["flamme"]()


def _wet():
    return P("M20 6 C26 16 32 22 32 30 C32 38 26 42 20 42 C14 42 8 38 8 30 C8 22 14 16 20 6 Z") \
        + P("M44 22 C49 30 54 34 54 42 C54 50 49 54 44 54 C39 54 34 50 34 42 C34 34 39 30 44 22 Z")


def _frozen():
    return M["flocon"]()


def _slowed():
    shell = P("M16 46 C10 46 8 40 10 34 C14 22 26 16 36 18 C48 20 54 30 52 40 C51 44 48 46 44 46 Z")
    swirl = S("M30 40 C24 38 24 30 30 28 C36 26 40 32 36 36", 2.6, K)
    body = P("M4 50 H56 C60 50 62 46 58 44 L52 46 H8 C4 46 2 48 4 50 Z") + P("M52 44 C56 36 60 34 62 36 C62 40 58 44 54 46 Z")
    return shell + swirl + body + L([(58, 34), (56, 26)], 2) + L([(62, 36), (64, 28)], 2)


def _sick():
    return (P("M32 8 C46 8 54 16 54 30 C54 46 44 56 32 56 C20 56 10 46 10 30 C10 16 18 8 32 8 Z")
            + S("M20 28 Q24 24 28 28", 2.6, K) + S("M36 28 Q40 24 44 28", 2.6, K) + S("M22 44 C26 40 30 46 34 42 C38 40 42 44 42 44", 2.6, K)
            + R(46, 34, 14, 4, 2) + Cc(60, 36, 3))


def _concentration():
    return M["cerveau"]() + '<circle cx="32" cy="32" r="29" fill="none" stroke="#FFFFFF" stroke-width="2"/>'


def _drunk():
    return (P("M14 14 H44 V52 C44 56 42 58 38 58 H20 C16 58 14 56 14 52 Z") + R(14, 8, 30, 10, 4)
            + S("M44 22 H50 C56 22 56 40 50 40 H44", 4) + P("M18 24 H40 V52 H18 Z", K) + P("M18 34 H40 V52 H18 Z")
            + Cc(20, 12, 4) + Cc(30, 10, 4.4) + Cc(40, 12, 4))


def _light(kind: str):
    return {"bougie": lambda: R(26, 28, 12, 28, 2) + P("M32 10 C36 16 38 20 36 24 C34 27 30 27 28 24 C26 20 28 16 32 10 Z"),
            "torche": M["torche"], "lanterne": lambda: __import__("core.art_objets", fromlist=["x"]).OBJECTS["objet_lanterne"](),
            "sourde": lambda: __import__("core.art_objets", fromlist=["x"]).OBJECTS["objet_lanterne"]()
            + P("M44 24 L62 14 V46 L44 36 Z")}[kind]()


def _cover(level: int):
    wall = "".join(R(4 + (i % 2) * 8 + 16 * (i // 2 % 3), 30 + 10 * (i // 6), 14, 8, 1) for i in range(12 if level > 1 else 6))
    return wall + figure(46, 24, 0.6)


def _resist(damage: str, immune: bool):
    dmg = {"acide": M["goutte"], "contondant": M["marteau"], "feu": M["flamme"], "force": M["diamant"],
           "foudre": M["eclair"], "froid": M["flocon"], "necrotique": M["crane"], "perforant": M["fleche"],
           "poison": M["fiole"], "psychique": M["cerveau"], "radiant": M["soleil"], "tonnerre": M["ondes"],
           "tranchant": M["epee"]}[damage]
    sh = G(P("M0 -26 L20 -19 V-2 C20 12 12 21 0 27 C-12 21 -20 12 -20 -2 V-19 Z"), 32, 32, 0, 1.15)
    inner = G(dmg(), 32, 32, 0, 0.5).replace("translate(32 32)", "translate(16 16)").replace('fill="#FFFFFF"', 'fill="#000000"')\
        .replace('stroke="#FFFFFF"', 'stroke="#000000"')
    ring = '<circle cx="32" cy="32" r="30" fill="none" stroke="#FFFFFF" stroke-width="3"/>' if immune else ""
    return sh + inner + ring


CONDITIONS = {
    "a_terre": _lying, "agrippe": _grappled, "assourdi": _deafened, "aveugle": _blinded, "charme": _charmed,
    "effraye": _frightened, "empoisonne": _poisoned, "entrave": _restrained, "etourdi": _stunned,
    "neutralise": _incapacitated, "inconscient": _unconscious, "invisible": _invisible, "paralyse": _paralyzed,
    "petrifie": _petrified, "alcoolise": _drunk, "saignement": _bleeding, "en_feu": _burning, "mouille": _wet,
    "glace": _frozen, "gele": lambda: over(figure(32, 30, 1.0), G(M["flocon"](), 32, 32, 0, 0.45).replace("translate(32 32)", "translate(28 28)")), "ralenti": _slowed,
    "malade": _sick, "concentration": _concentration, "hebete": _stunned, "surpris": _surprised,
    "plaie_beante": lambda: over(heart(32, 32, 1.1), L([(14, 50), (50, 14)], 4, K)),
    "desarme": lambda: __import__("core.art_armes", fromlist=["x"]).MANEUVERS["Désarmement"](),
    "affaibli": lambda: over(M["poing"](), G(R(-4, -16, 8, 18, 2) + P("M-11 2 H11 L0 16 Z"), 50, 44, 0, 0.7)),
    "desequilibre": lambda: G(figure(0, 0, 1.0), 30, 32, -25) + S("M46 50 C56 44 58 32 50 24", 3) + P("M48 20 L56 28 L46 30 Z"),
    "cache": lambda: __import__("core.art_actions", fromlist=["x"]).COMMON["se_cacher"](),
    "apnee": lambda: P("M32 8 C46 8 54 16 54 30 C54 46 44 56 32 56 C20 56 10 46 10 30 C10 16 18 8 32 8 Z")
                     + R(22, 40, 20, 4, 2, K) + Cc(24, 26, 3, K) + Cc(40, 26, 3, K)
                     + '<circle cx="56" cy="14" r="4" fill="none" stroke="#FFFFFF" stroke-width="2"/>',
    "suffoque": lambda: M["brume"](),
    "lumiere_bougie": lambda: _light("bougie"), "lumiere_torche": lambda: _light("torche"),
    "lumiere_lanterne": lambda: _light("lanterne"), "lumiere_sourde": lambda: _light("sourde"),
    "abri_partiel": lambda: _cover(1), "abri_important": lambda: _cover(2),
}


def _special(key: str):
    """Effets sans sort homonyme dessiné : renvoi vers le dessin le plus proche."""
    from . import art_actions as AC, art_armes as AA, art_sorts as AS
    table = {
        "armure_mage": lambda: AS.SPELLS["Armure de mage"](), "peau_pierre": lambda: M["pierres"](),
        "invisibilite_sup": lambda: _invisible() + star4(12, 52, 5), "maillet_occulte": lambda: M["marteau"](),
        "agrandissement": lambda: figure(32, 36, 1.0) + P("M32 0 L40 10 H24 Z") + L([(32, 8), (32, 12)], 3),
        "rapetissement": lambda: figure(32, 42, 0.6) + P("M32 22 L40 12 H24 Z"),
        "pattes_araignee": lambda: AS.SPELLS["Toile d'araignée"](), "toile": lambda: M["toile"](),
        "liberte_mouvement": lambda: M["chaine_brisee"](), "fausse_vie": lambda: over(M["coeur"](), G(M["crane"](), 32, 32, 0, 0.45)
                                                                                     .replace("translate(32 32)", "translate(17 17)")),
        "lethargie": lambda: _slowed(), "confusion": lambda: M["spirale"](), "cecite_surdite": lambda: _blinded(),
        "eclair_tracant": lambda: M["eclair"]() + star4(52, 12, 5), "cercle_pouvoir": lambda: AS.SPELLS["Cercle magique"](),
        "rage": lambda: AC.FEATURES["Entrer en rage"](), "frenesie": lambda: AC.FEATURES["Attaque téméraire"](),
        "fureur_divine": lambda: AC.FEATURES["Châtiment divin"](), "esquive": lambda: AC.COMMON["esquiver"](),
        "desengagement": lambda: AC.COMMON["desengager"](), "foncer": lambda: AC.COMMON["foncer"](),
        "voeu_inimitie": lambda: AA.MANEUVERS["Attaque précise"](), "deplacement_sans_armure": lambda: M["botte"](),
        "benediction_tenebreux": lambda: M["lune"](), "metamorphose": lambda: M["cycle"](),
        "avantage_js_poison": lambda: _resist("poison", False), "ascendance_feerique": lambda: M["eclat"](),
        "passage_sans_trace": lambda: M["brume"](), "antitoxine": lambda: M["fiole"](),
        "potion_invulnerabilite": lambda: _resist("force", True), "potion_clairvoyance": lambda: M["oeil"](),
        "potion_pensees": lambda: M["cerveau"](), "huile_insaisissable": lambda: M["goutte"](),
    }
    fn = table.get(key)
    return fn() if fn else None


def effect_body(key: str, name: str) -> Optional[str]:
    """Dessin de l'effet : état dessiné, sinon dessin du sort ou de la capacité homonyme, sinon résistance."""
    from . import art_actions, art_sorts
    from .rules import norm
    if key in CONDITIONS:
        return CONDITIONS[key]()
    special = _special(key)
    if special:
        return special
    if key.startswith("epuisement_"):
        return _exhaustion()
    for prefix, immune in (("resist_", False), ("immun_", True)):
        if key.startswith(prefix):
            return _resist(key[len(prefix):], immune)
    base = name.split(" (")[0].strip()
    for table in (art_sorts.SPELLS, art_actions.FEATURES):
        for cand, fn in table.items():
            if norm(cand) == norm(base) or norm(cand) == norm(name):
                return fn()
    keys = {"aura": "soleil", "potion": "fiole", "force": "poing", "protection": "bouclier", "bouclier": "bouclier",
            "inspiration": "note", "vision": "oeil", "souffle": "souffle", "forme": "cycle", "marque": "cible",
            "malefice": "crane", "lien": "chaine", "rayon": "eclair", "arme": "epee", "grace": "botte",
            "endurance": "coeur", "ruse": "masque", "sagesse": "lune", "splendeur": "couronne", "egide": "bouclier",
            "chant": "note", "sorcellerie": "spirale", "courroux": "vague", "elementaire": "flamme"}
    n = norm(name)
    for k, motif in keys.items():
        if k in n:
            return M[motif]()
    return None
