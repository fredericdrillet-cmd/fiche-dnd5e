"""
Dessins (v53) des capacités de classe, de sous-classe et d'espèce : composition choisie à la main pour chacune,
écrite en formule courte —
  « a »        : élément seul ;
  « a+b »      : élément a en grand, b détouré en bas à droite ;
  « a^b »      : b détouré en haut à droite ;
  « cercle:a » : a dans un cercle ; « vide:a/b » : b évidé dans a.
Éléments : motifs de core/art_motifs, armes de core/art_armes (nom en minuscules sans accents, ex. « epee longue »),
éléments de core/art_kit (silhouette, fantome, foule, tete, demon, dragon, ange, cheval, insecte, oiseau, arbre,
nuage, tornade, porte_arche, hutte, main_levee, cercueil, miroir, carquois, balance, contrat, livre_ferme).
"""
from __future__ import annotations

from functools import lru_cache

from . import art_kit as KIT
from .art_motifs import MOTIFS
from .rules import norm

KIT_ELEMENTS = {
    "silhouette": lambda: KIT.figure(32, 32, 1.1), "fantome": lambda: KIT.ghost_figure(32, 32, 1.1), "foule": KIT.crowd,
    "tete": KIT.head_profile, "demon": KIT.demon, "dragon": KIT.dragon_head, "ange": KIT.angel_wings, "cheval": KIT.horse,
    "insecte": KIT.insect, "oiseau": KIT.bird, "arbre": KIT.tree, "nuage": lambda: KIT.cloud(30, 1.1),
    "tornade": KIT.tornado, "porte_arche": KIT.doorway, "hutte": KIT.hut, "main_levee": lambda: KIT.hand_up(32, 34, 1.1),
    "cercueil": KIT.coffin, "miroir": KIT.mirror, "carquois": KIT.quiver, "balance": KIT.scales, "contrat": KIT.contract,
    "livre_ferme": KIT.book_closed, "rayons": KIT.sunburst,
}


def element(name: str) -> str:
    if name in KIT_ELEMENTS:
        return KIT_ELEMENTS[name]()
    if name in MOTIFS:
        return MOTIFS[name]()
    from . import art_armes as AA
    for w, fn in AA.WEAPONS.items():
        if norm(w) == name:
            return fn()
    raise KeyError(name)


def build(formula: str) -> str:
    if formula.startswith("cercle:"):
        return KIT.ring(element(formula[7:]))
    if formula.startswith("vide:"):
        a, b = formula[5:].split("/")
        return KIT.inside(element(a), element(b), 0.48)
    if "^" in formula:
        a, b = formula.split("^")
        return KIT.corner(element(a), element(b), 0.4)
    if "+" in formula:
        a, b = formula.split("+")
        return KIT.duo(element(a), element(b), 0.44)
    return KIT.place(element(formula), 32, 32, 1.0)


FORMULES = {
    "adaptation du terrain": "terre+cycle", "ailes de dragon": "dragon+aile", "allegeance divine": "soleil+chaine",
    "ame de l'artifice": "outil+coeur", "ame oceane & tentacule gardien": "vague+tentacules", "ame radieuse": "silhouette+soleil",
    "ame vengeresse": "fantome+epee", "ange de la vengeance": "ange+epee", "animation fongique": "crane+feuille",
    "arme occulte": "epee longue+oeil", "armes du kensei, parade agile & tir du kensei": "baton+poing",
    "armure de malefices": "armure+crane", "armure parachevee": "armure+etoile", "ascendance draconique": "dragon",
    "ascendance gigante": "silhouette+pierres", "attaque de frenesie": "hache d'armes+flamme",
    "attenuation des elements": "bouclier+flocon", "attraction violente": "main+retour", "aura de tempete : desert": "cercle:soleil",
    "aura de tempete : mer": "cercle:vague", "aura de tempete : toundra": "cercle:flocon", "aura du gardien": "cercle:bouclier",
    "aura du phenix": "oiseau+flamme", "aval de la terre": "terre+bouclier", "avenir convergent": "oeil+sablier",
    "balancement emeche": "silhouette+spirale", "bastion de la loi": "vide:bouclier/balance",
    "baume de la cour d'ete": "feuille+soin", "benediction de l'escroc": "masque+soleil", "benediction de la forge": "marteau+soleil",
    "benediction de la reine corbeau": "oiseau+lune", "bond psi": "botte+cerveau", "bouclier runique": "vide:bouclier/rune",
    "bouclier solaire": "vide:bouclier/soleil", "bouclier spirituel": "fantome+bouclier", "branches de l'arbre": "arbre+main",
    "bras du moi astral": "main_levee+etoile", "bribes des defunts": "crane+bulle", "cadran d'arcanes & retrogradation": "sablier+eclat",
    "camouflage svirfnebelin": "pierres+oeil_clos", "canon occulte": "mousquet+eclat", "carapace cameleon": "silhouette+masque",
    "carapace necrotique": "vide:armure/crane", "champ defensif": "bouclier^eclat", "champ protecteur": "bouclier+cerveau",
    "champion antique": "couronne+epee", "chance alteree": "cycle+etoile", "chance du nombre": "foule+etoile",
    "chance du tenebreux": "lune+etoile", "chance forcee": "etoile+main", "chancellements emeches": "botte+spirale",
    "changeforme": "silhouette+cycle", "chant de defense": "note+bouclier", "chant de la lame": "epee longue+note",
    "charmantes defenses": "bouclier+coeur", "charme instinctif": "coeur+masque", "chatiment de sang": "epee+goutte",
    "chatiment divin (gratuit)": "epee longue+soleil", "chatiment divin (sort)": "soleil+epee", "chien de mauvais augure": "bete+lune",
    "clone d'ombre": "fantome+silhouette", "combat perspicace": "oeil+epee", "combattant clairvoyant": "epee+oeil",
    "commander le compagnon": "patte+bulle", "commander le defenseur d'acier": "casque+bulle", "comme par hasard": "masque+etoile",
    "compagnon primitif": "bete+feuille", "concu pour reussir": "outil+etoile",
    "conduit divin : benediction du dieu de la guerre": "soleil+epee longue",
    "conduit divin : emissaire de paix & reprimander la violence": "soleil+coeur", "conjuration mineure": "eclat+outil",
    "connaissance d'une vie anterieure": "livre+cycle", "connaissance de la pierre": "pierres+livre",
    "conquerant invincible": "couronne+bouclier", "conscience magique": "oeil+eclat",
    "conscience temporelle & dephasage chronal": "sablier+portail", "contre-attaque du tueur": "dague^cycle",
    "convocation de l'esprit du feu sauvage": "flamme^portail", "cornes martelantes": "tete+fleche_haut",
    "coup de chance": "etoile+eclair", "courroux de la tempete": "eclair+vague", "courroux des mers": "vague+eclair",
    "cri draconique": "dragon+ondes", "decharge arcanique": "eclat+explosion", "decharge elementaire": "flamme+explosion",
    "defense de carapace": "vide:bouclier/pierres", "defense de chasseur superieure": "arc+bouclier",
    "defense glorieuse": "bouclier+couronne", "defense patiente (gratuite)": "bouclier+main", "defense spectrale": "fantome+bouclier^",
    "defenseur vigilant": "bouclier+oeil", "deplacement exaltant": "botte+fleche_haut", "deviation arcanique": "bouclier+eclat",
    "deviation arcanique & esprit tactique": "bouclier+cerveau^", "deviation d'assaut": "bouclier+retour",
    "disciple draconique": "dragon+livre", "dispersion de l'essaim": "insecte+cycle", "don elementaire": "flamme+goutte",
    "don feerique": "aile+eclat", "double illusoire": "silhouette+masque^", "echappatoire brumeuse": "brume+botte",
    "elixir experimental": "fiole+eclat", "embuscade effrayante": "oeil_clos+crane", "embusque redoutable": "oeil_clos+arc",
    "endurance de pierre": "pierres+coeur", "endurance implacable": "coeur+crane", "entite symbiotique": "feuille+coeur",
    "escarmoucheur": "botte+epee", "escarmoucheur & survivaliste": "botte+bouclier", "esprit combatif": "poing+eclair",
    "esprit de l'aigle : foncer": "oiseau+botte", "esprit du feu sauvage : graine de flamme": "flamme+feuille",
    "esprit garde": "fantome+oeil", "esprit manifeste": "fantome+eclat", "esprit totem": "bete+eclat",
    "esquive des ombres": "lune+esquive", "esquive hadozi": "aile+esquive", "essaim rassemble": "insecte+chaine",
    "etincelle astrale": "etoile+flamme", "faveur des dieux": "soleil+etoile", "fioriture defensive": "note+bouclier^",
    "fioriture mobile": "note+botte", "fioriture tranchante": "note+epee", "flammes cauterisantes": "flamme+soin",
    "fleche affaiblissante": "fleche+crane", "fleche bannissante": "fleche+portail", "fleche charmeuse": "fleche+coeur",
    "fleche de saisie": "fleche+feuille", "fleche explosive": "fleche+explosion", "fleche perforante": "fleche+bouclier",
    "force avant la mort": "crane+poing", "force vivifiante": "coeur+eclair", "forme de geant": "silhouette+fleche_haut",
    "forme de la bete": "bete", "forme de la bete : griffes": "griffes+bete", "forme de la bete : morsure": "bete+crane",
    "forme de la bete : queue": "bete+cycle", "forme etoilee": "silhouette+etoile", "forme hybride": "silhouette+bete",
    "forme sauvage de combat : soins": "bete+soin", "forme stellaire": "etoile+silhouette", "formes de metamorphose": "cycle+bete",
    "foulee d'ombre": "lune+botte", "foulee des fees": "aile+botte", "frappe en arc ardent": "flamme+epee longue",
    "frappe malicieuse : assommer": "dague+marteau", "frappe malicieuse : aveugler": "dague+oeil_clos",
    "frappe malicieuse : croc-en-jambe": "dague+botte", "frappe malicieuse : hebetement": "dague+spirale",
    "frappe malicieuse : poison": "dague+fiole", "frappe malicieuse : repli": "dague+retour", "frappe psionique": "poing+cerveau",
    "frappes autoguidees": "cible+fleche", "frappes terribles": "poing+explosion", "frappes terrifiantes": "poing+crane",
    "frayeur predatrice": "griffes+crane", "fuite agile": "botte+vent", "fuite brumeuse": "brume+esquive",
    "fureur de la tempete": "eclair+tornade", "fureur des petits": "poing+fleche_haut", "gambade heureuse": "botte+note",
    "garde entropique": "bouclier+spirale", "generation alchimique": "fiole+cycle", "gnome des forets": "feuille+masque",
    "gnome des roches": "outil+pierres", "guerrier planaire": "epee longue+portail", "halo de lumiere": "silhouette+soleil^",
    "halo de spores": "cercle:feuille", "illumination protectrice": "ampoule+bouclier", "illumination protectrice amelioree": "ampoule+etoile",
    "inexorable martyr": "coeur+bouclier", "inflexible": "pierres+bouclier", "inspiration au combat": "note+epee longue",
    "inspiration contagieuse": "note+explosion", "inspiration martiale": "note+poing", "intervention divine": "soleil+main",
    "intrepide": "coeur+eclair^", "jeton etrange": "gemme+oeil", "lames psychiques": "dague+cerveau",
    "langage de la foret & totem spirituel": "feuille+bulle", "legende vivante": "couronne+etoile",
    "lien avec l'arme : rappel": "epee longue+retour", "lien elementaire": "chaine+flamme", "lien enhardissant": "chaine+coeur",
    "lien mental": "cerveau+chaine", "lien parfait": "chaine+etoile", "lien protecteur": "chaine+bouclier",
    "lumiere guerisseuse": "soleil+soin", "machoires affamees": "crane+griffes", "magie de guerre": "epee longue+eclat",
    "magie mecanique & retablir l'equilibre": "outil+cycle", "magie renforcante": "eclat+fleche_haut", "magie tempetueuse": "eclat+vent",
    "main de mage arcanique": "main_levee+eclat", "main de souffrance": "main+crane", "main du mal": "main+lune",
    "mains guerisseuses": "main+soin", "mains lestes": "main+vent", "maitre tacticien": "cible+couronne",
    "maitre telekinetique": "main_levee+pierres", "maitrises sup. & fureur de l'ouragan": "tornade+eclair",
    "malediction de la lame maudite": "epee longue+crane", "manifestation d'un echo": "fantome+ondes",
    "manoeuvre d'interposition": "bouclier+botte", "manoeuvre protectrice": "bouclier+coeur^", "manteau d'inspiration": "cape+note",
    "manteau de majeste": "cape+couronne", "marche dans l'ombre": "lune+fantome", "maree du chaos": "vague+spirale",
    "marque inebranlable": "cible+bouclier", "martyr de l'ombre": "lune+coeur", "memoire kenku": "oiseau+livre",
    "metamagie : sort accelere": "eclat+eclair", "metamagie : sort ample": "eclat+explosion^", "metamagie : sort amplifie": "eclat+fleche_haut^",
    "metamagie : sort distant": "eclat+fleche", "metamagie : sort etendu": "eclat+sablier", "metamagie : sort intensifie": "eclat+flamme",
    "metamagie : sort prevenant": "eclat+oeil", "metamagie : sort prudent": "eclat+bouclier", "metamagie : sort renforce": "eclat+poing",
    "metamorphose": "cycle+silhouette", "modelage du corps": "silhouette+main", "moi illusoire": "silhouette+fantome",
    "morsure vampirique": "crane+goutte", "mots cinglants": "bulle+dague", "mouvement telekinetique": "main_levee+fleche",
    "murmures psychiques": "cerveau+bulle", "nemesis des lanceurs": "epee longue+eclat^", "nimbe sacre": "cercle:etoile",
    "onde de choc acoustique": "ondes+explosion", "opportuniste": "oeil+dague", "panache": "couronne+note",
    "paroles troublantes": "bulle+spirale", "pas de l'ombre": "lune+portail", "pas de lumiere etoilee": "etoile+botte",
    "pas du vent (gratuit)": "vent+botte", "pas ethere": "fantome+botte", "pas invisible": "fantome+portail",
    "pied agile": "botte+eclair", "pirouettes coordonnees": "foule+cycle", "plaintes d'outre-tombe": "crane+ondes",
    "planer": "aile+vent", "plenitude du corps": "silhouette+soin", "plenitude physique": "coeur+botte",
    "poussee d'adrenaline": "coeur+fleche_haut", "pouvoirs psioniques": "cerveau+eclat", "presage": "oeil+lune",
    "presage cosmique": "etoile+oeil", "presence feerique": "aile+couronne", "presence intimidante": "casque+crane",
    "presence zelee": "casque+flamme", "pretre de guerre": "soleil+hache d'armes", "proie du chasseur": "cible+patte",
    "proie du tueur": "cible+crane", "protection projetee": "bouclier+fleche", "puissance des geants": "poing+pierres",
    "quinte flush royale": "couronne+gemme", "rechargement eclair": "arbalete+eclair", "recuperation psionique": "cerveau+cycle",
    "redirection": "retour+bouclier", "regard hypnotique": "oeil+spirale", "rempart de force": "vide:bouclier/explosion",
    "represailles": "retour+epee", "representation animee": "note+eclat", "representation de la creation": "note+outil",
    "reprimande vigilante": "oeil+retour", "reseau maille": "toile+cerveau", "retablir l'equilibre": "balance",
    "revelation celeste": "ange", "revelation dans la chair": "silhouette+tentacules", "riposte capricieuse": "retour+spirale",
    "ruee cornue": "tete+botte", "rugissement intimidant": "bete+ondes", "rune de la colline": "rune+terre",
    "rune de la pierre": "rune+pierres", "rune du feu": "rune+flamme", "rune du givre": "rune+flocon", "rune du nuage": "rune+nuage",
    "rupture spirituelle": "fantome+explosion", "ruse magique": "masque+eclat", "sanctuaire de dame nature": "arbre+bouclier",
    "sanguisuga supreme": "goutte+coeur", "saut de lapin": "botte+fleche_haut^", "saut des nuees (geants des nuages)": "nuage+botte",
    "savoir-faire renforce": "outil+fleche_haut", "seconde lame psychique": "dague+cerveau^", "sentinelle au seuil de la mort": "crane+oeil",
    "sorcellerie innee": "spirale+eclat", "sorcellerie innee (2 points de sorcellerie)": "spirale+etoile", "sort mineur supp. & illumination protectrice": "ampoule+eclat",
    "souffle": "souffle", "spores pacifiantes ou toxiques": "feuille+fiole", "surcharge magique": "explosion+eclat",
    "symbiote & halo de spores": "feuille+crane", "teleportation psychique": "cerveau+portail",
    "tempete dechainee (desert)": "tornade+soleil", "tempete dechainee (mer)": "tornade+vague", "tentacule des profondeurs": "tentacules",
    "tir du kensei": "arc+poing", "torsion seduisante": "spirale+coeur", "toucher purifiant": "main+goutte",
    "trait de soleil radieux": "soleil+fleche", "transposition bienveillante": "cycle+coeur", "tueur de colosses": "epee longue+silhouette",
    "union avec le verbe": "bulle+livre", "vengeur implacable": "epee longue+cible", "voile de murmure": "cape+bulle",
    "voile necrotique": "cape+crane", "voile psychique": "cape+cerveau", "voleur de sort": "main+eclat^",
    "voyage au gre de l'arbre": "arbre+portail", "yeux de la tombe": "oeil+crane",
}


def _clean(f: str) -> str:
    """Les « ^ » en fin de formule servent seulement à distinguer deux compositions proches : variante en coin."""
    if f.endswith("^^"):
        a, b = f[:-2].split("+")
        return a + "^" + b
    if f.endswith("^"):
        f = f[:-1]
        if "+" in f:
            a, b = f.split("+")
            return a + "^" + b
    return f


@lru_cache(maxsize=1)
def drawings() -> dict:
    """{nom normalisé de la capacité : fonction → corps SVG}."""
    out = {}
    for name, f in FORMULES.items():
        formula = _clean(f)
        out[norm(name)] = (lambda fm=formula: build(fm))
    return out
