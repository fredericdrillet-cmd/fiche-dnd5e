"""
Icône unique de chaque sort (v53).

- Sorts dessinés à la main : core/icon_art.SPELL_ART (tous les tours de magie et les sorts les plus utilisés).
- Les autres : icône COMPOSÉE à partir des données du sort — effet (type de dégâts ou nature : soins, contrôle,
  déplacement…), forme (rayon, cône, sphère, mur, nuage, projectiles, contact…), élément reconnaissable (bête,
  arme, porte, œil, plante…) et badge de l'école dans un coin.
- Un sort et sa version 2024 partagent la même icône ; deux sorts différents n'ont jamais la même
  (`all_spell_icons` vérifie l'unicité et ajoute au besoin une marque distinctive).
Aucune dépendance à Qt : renvoie le corps SVG (viewBox 64 × 64, blanc, noir = découpe).
"""
from __future__ import annotations

import hashlib
import re
from typing import Optional

from . import icon_art as A
from .rules import norm

EFFECT_GLYPH = {
    "feu": A.flame, "froid": A.snowflake, "foudre": A.bolt, "tonnerre": A.waves,
    "acide": lambda: A.drop() + A.bubbles(), "poison": A.ICONS["effet_poison"], "necrotique": A.skull,
    "radiant": A.sun, "force": A.diamond_burst, "psychique": A.brain, "contondant": A.hammer,
    "perforant": A.ICONS["effet_perforant"], "tranchant": lambda: A.rot(A.place(A.sword(), 32, 32, 1.0), 35),
    "soins": A.ICONS["effet_soins"], "controle": A.chain, "protection": A.shield, "deplacement": A.wing,
    "information": A.eye, "amelioration": A.arrow_up, "lumiere": A.bulb, "invocation": A.portal,
    "illusion": A.mask, "transformation": A.cycle_arrows, "creation": A.tool, "communication": A.bubble,
    "vie": lambda: A.place(A.heart(), 32, 36, 0.7) + A.place(A.sun(), 32, 12, 0.3), "ombre": A.moon,
    "temps": A.hourglass, "terrain": A.tremor_earth, "nature": A.leaf, "eau": A.water_wave,
}

SCHOOL_GLYPH = {"abjuration": A.shield, "divination": A.eye, "enchantement": A.ICONS["ecole_enchantement"],
                "evocation": A.burst, "illusion": A.mask, "invocation": A.portal, "necromancie": A.skull,
                "transmutation": A.cycle_arrows}

DAMAGE_KEYS = ("feu", "froid", "foudre", "tonnerre", "acide", "poison", "necrotique", "radiant", "force",
               "psychique", "contondant", "perforant", "tranchant")

EFFECT_WORDS = [                                         # du plus précis au plus général
    ("soins", r"(?:rend|regagn|recuper|restaur)\w* .{0,40}(?:points de vie|\bpv\b)|soign|\bguerit|guerison"),
    ("vie", r"ressuscit|revient a la vie|ramene a (?:la vie|\d+ pv)|rappel a la vie|creature morte"),
    ("eau", r"\beau\b|vague|maree|tourbillon d.eau|deferle"),
    ("froid", r"neige|blizzard|glace|givre|gel\b"),
    ("feu", r"\bfeu\b|flamme|brul|incendi"),
    ("foudre", r"foudre|eclair"),
    ("invocation", r"\binvoque|convoque|appel\w* .{0,20}(?:esprit|creature|elementaire|fee|bete)"),
    ("controle", r"charme|effraye|paralyse|entrave|neutralise|aveugle|assourdi|agrippe|etourdi"),
    ("deplacement", r"teleport|vitesse de vol|vous volez|deplace\w* instantanement|vitesse .{0,15}augment|levit"),
    ("information", r"detect|vous apprenez|vous savez|localis|clairvoy|divin|voir a travers|vision"),
    ("lumiere", r"lumiere vive|emet une lumiere|illumin"),
    ("ombre", r"tenebr|obscurit|ombre"),
    ("protection", r"classe d.armure|resistance aux|immunise|protege|bouclier|barriere"),
    ("illusion", r"illusion|image illusoire|apparence"),
    ("transformation", r"transform|metamorph|changez de forme|prend la forme"),
    ("communication", r"communiqu|telepath|message|parler avec|comprendre"),
    ("temps", r"\btemps\b|round supplementaire"),
    ("nature", r"plante|vegeta|ronces|lianes|arbre"),
    ("terrain", r"\bsol\b|terrain|terre|pierre|roche"),
    ("amelioration", r"avantage|bonus de \+|ajoute 1d|\+1d"),
    ("creation", r"\bcree\w*|faconne|fabriqu"),
]

SHAPES = [
    ("rayon", r"\brayon (?:de lumiere|d.energie|ardent|scintillant)|un rayon\b|\btrait\b"),
    ("cone", r"\bcone\b"),
    ("mur", r"\bmur\b|muraille|paroi"),
    ("nuage", r"nuage|brume|brouillard|vapeur"),
    ("ligne", r"\bligne de\b"),
    ("cube", r"\bcube\b"),
    ("colonne", r"cylindre|colonne"),
    ("projectiles", r"projectile|flechette|dard|eclat"),
    ("sphere", r"sphere|rayon de \d+[,.]?\d* ?m|centre\w* sur un point"),
    ("contact", r"\bcontact\b|touchez"),
]

MOTIFS = [
    ("bete", r"\bbete|animal|loup|aigle|cheval|monture|ours|araign|insecte|serpent", A.paw),
    ("arme", r"\barme\b|epee|lame|fleche|marteau", lambda: A.rot(A.place(A.sword(), 32, 32, 1.0), 35)),
    ("porte", r"\bporte\b|portail|passage", A.door),
    ("oeil", r"\boeil|\byeux|regard", A.eye),
    ("main", r"\bmain\b|poigne", A.open_hand),
    ("plante", r"plante|ronces|lianes|arbre|bois\b", A.leaf),
    ("pierre", r"pierre|roche|terre", A.stones if hasattr(A, "stones") else A.gem),
    ("vent", r"\bvent|\bair\b|tourbillon", A.gust if hasattr(A, "gust") else A.waves),
    ("mort", r"mort-vivant|cadavre|squelette|zombie", A.skull),
    ("esprit", r"\besprit|fantom|spectr", A.wing),
    ("glace", r"glace|givre", A.snowflake),
    ("feu", r"flamme|brasier", A.flame),
    ("etoile", r"etoile|astral|lune|celeste", A.star),
]

ACCENTS = [lambda: A.sparkle(10, 54, 5), lambda: A.circle(10, 54, 4, True), lambda: A.star(10, 54, 6, 2.6),
           lambda: A.poly([(10, 48), (15, 58), (5, 58)]), lambda: A.rect(6, 50, 8, 8, 1.5),
           lambda: A.poly([(10, 48), (16, 54), (10, 60), (4, 54)]), lambda: A.circle(10, 54, 4.5, False, 2),
           lambda: A.line(4, 58, 16, 46, 3), lambda: A.path("M4 54 C8 48 12 60 16 54", w=2.5)]


def base_name(name: str) -> str:
    return re.sub(r"\s*\(2024\)\s*$", "", name or "").strip()


def spell_traits(spell: dict) -> dict:
    """{effet, forme, motif, ecole} déduits des données du sort."""
    desc = norm(spell.get("description", ""))
    dtype = norm(spell.get("type_degats", "") or "")
    effect = next((k for k in DAMAGE_KEYS if dtype.startswith(k)), "")
    if effect in ("contondant", "perforant", "tranchant"):   # dégâts physiques d'un élément : l'élément prime
        element = next((k for k, rx in EFFECT_WORDS if k in ("eau", "froid", "feu", "foudre", "terrain", "nature")
                        and re.search(rx, desc)), "")
        effect = element or effect
    if not effect:
        effect = next((k for k, rx in EFFECT_WORDS if re.search(rx, desc)), "")
    shape = next((k for k, rx in SHAPES if re.search(rx, desc)), "")
    if not shape and norm(spell.get("portee", "")).startswith("contact"):
        shape = "contact"
    motif = next((k for k, rx, _f in MOTIFS if re.search(rx, desc + " " + norm(spell.get("nom", "")))), "")
    school = norm(spell.get("ecole", ""))
    return {"effet": effect, "forme": shape, "motif": motif, "ecole": school}


def is_healing(spell: dict) -> bool:
    return spell_traits(spell)["effet"] in ("soins", "vie")


def _shape_layer(shape: str) -> str:
    """Forme du sort, dessinée en fond (traits fins) derrière le glyphe principal."""
    if shape == "rayon":
        return A.line(4, 60, 60, 4, 3) + A.line(4, 60, 60, 4, 9).replace('stroke="#FFFFFF"', 'stroke="#FFFFFF" '
                                                                         'stroke-opacity="0.22"')
    if shape == "cone":
        return A.path("M4 32 L60 6 M4 32 L60 58", w=2.5) + A.path("M60 6 C66 24 66 40 60 58", w=2)
    if shape == "mur":
        return "".join(A.rect(x, 52, 13, 8, 1, False, 2) for x in (4, 18, 32, 46))
    if shape == "nuage":
        return A.path("M6 52 C6 46 12 44 16 46 C18 40 26 40 28 44 C34 40 42 42 42 48 C48 46 56 48 56 54 Z", w=2)
    if shape == "ligne":
        return A.line(4, 32, 60, 32, 2.5) + A.line(4, 26, 60, 26, 1.2) + A.line(4, 38, 60, 38, 1.2)
    if shape == "cube":
        return A.rect(8, 8, 48, 48, 2, False, 2) + A.path("M8 8 L16 2 H62 V48 L56 56 M56 8 L62 2", w=1.5)
    if shape == "colonne":
        return A.path("M18 6 V58 M46 6 V58", w=2) + '<ellipse cx="32" cy="6" rx="14" ry="3" fill="none" ' \
            'stroke="#FFFFFF" stroke-width="2"/>'
    if shape == "projectiles":
        return "".join(A.line(x, 60, x + 12, 46, 2.5) for x in (2, 14, 26))
    if shape == "sphere":
        return A.circle(32, 32, 29, False, 2) + A.circle(32, 32, 24, False, 1)
    if shape == "contact":
        return A.place(A.open_hand(), 10, 52, 0.32)
    return ""


def compose(spell: dict, variant: int = 0) -> str:
    """Effet au centre (grand), forme du sort en fond, élément reconnaissable en haut à gauche. L'école est donnée
    par la COULEUR de l'icône (ui/icons) : pas de badge, rien de superflu. `variant` ajoute une petite marque
    distinctive quand deux sorts tomberaient sur le même dessin."""
    t = spell_traits(spell)
    effect = EFFECT_GLYPH.get(t["effet"]) or SCHOOL_GLYPH.get(t["ecole"]) or A.sparkle
    layer = _shape_layer(t["forme"])
    out = layer + A.place(effect(), 32, 32, 0.7 if layer else 0.82)
    motif = next((f for k, _rx, f in MOTIFS if k == t["motif"]), None)
    if motif is not None and t["motif"] != t["effet"]:
        out += A.place(motif(), 13, 13, 0.32)
    if variant:
        out += ACCENTS[(variant - 1) % len(ACCENTS)]()
        if variant > len(ACCENTS):                       # encore identique : seconde marque, en haut à droite
            out += A.place(ACCENTS[(variant // len(ACCENTS)) % len(ACCENTS)](), 54, 10, 1.0)
    return out


_CACHE: dict = {}


def all_spell_icons(spells) -> dict[str, str]:
    """{nom de base: corps SVG} pour tous les sorts — dessin à la main sinon composition ; unicité garantie."""
    key = id(spells)
    if key in _CACHE:
        return _CACHE[key]
    by_base: dict[str, dict] = {}
    for sp in (spells.values() if isinstance(spells, dict) else spells):
        b = base_name(sp.get("nom", ""))
        if b and (b not in by_base or sp.get("nom") == b):     # la version 2014 sert de référence
            by_base[b] = sp
    out, seen = {}, set()
    for b in sorted(by_base, key=lambda n: (n not in A.SPELL_ART, n)):
        art = A.SPELL_ART.get(b)
        if art is not None:
            body = art()
        else:
            seed = int(hashlib.md5(b.encode("utf-8")).hexdigest(), 16)
            body, v = compose(by_base[b]), 0
            while body in seen and v < 90:
                v += 1
                body = compose(by_base[b], v)
            while body in seen:                          # filet de sécurité (jamais atteint en pratique)
                body += A.circle(6 + seed % 50, 60, 1.5, True)
                seed += 7
        seen.add(body)
        out[b] = body
    _CACHE[key] = out
    return out


def spell_icon(spells, name: str) -> Optional[str]:
    return all_spell_icons(spells).get(base_name(name))
