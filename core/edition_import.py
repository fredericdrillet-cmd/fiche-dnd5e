"""
v52 (étape 2) : fusion des données de référence `data/editions/` dans la base de l'application, au chargement.

Règles de fusion (décisions de l'utilisateur, ARCHITECTURE_EDITIONS_v52.md §5) :
- **2014** : les données actuelles de l'app sont gardées (plus complètes). On n'ajoute que ce qui manque : sorts,
  dons, historiques, 14 sous-classes officielles et le Filet. Quelques dons 2014 dont le texte de l'app était faux
  reçoivent le texte officiel (le nom de l'app est conservé : sauvegardes et effets intacts).
- **2024** : sorts, dons, historiques et espèces sont ajoutés avec `edition: 2024`. Si le nom existe déjà en 2014,
  l'élément 2024 prend le suffixe « (2024) » (les noms servent de clés dans tout le moteur).
- Classes et sous-classes 2024 : pas encore (le moteur doit d'abord distinguer « Paladin 2014 » et « Paladin 2024 »).
- Armes et armures : communes aux deux éditions (mêmes statistiques) ; les bottes d'arme 2024 sont une règle de la
  table (`maitrises_armes_2014`).

Les fichiers de `data/*.json` ne sont jamais modifiés : la fusion est refaite à chaque chargement.
"""
from __future__ import annotations

import difflib
import re
from typing import Optional

from .rules import ABILITIES, norm

SUFFIX_2024 = " (2024)"

# sorts 2014 des nouvelles données déjà présents dans l'app sous une autre traduction
SPELL_TRANSLATIONS_2014 = {norm(n) for n in (
    "Lance psychique de Raulothim", "Piques argentées", "Châtiment de stupeur",
    "Invocation d'esprit draconique", "Préméditation")}       # v53 : « Rafale de vent » (Gust, tour de magie) importé

# sous-classes 2014 absentes de l'app (identifiées par leur nom anglais ; les autres sont des traductions de
# sous-classes déjà présentes)
SUBCLASSES_2014 = {
    "Path of the Giant", "Path of the Battlerager", "College of Spirits", "Lunar Sorcery", "Echo Knight",
    "Purple Dragon Knight (Banneret)", "Graviturgy Magic", "Way of the Ascendant Dragon", "Way of the Long Death",
    "The Undying", "The Undead", "Oathbreaker", "Oath of the Crown", "Drakewarden"}

# dons 2014 déjà présents dans l'app (nom anglais) ; la valeur, quand elle existe, est le nom de l'app dont le texte
# est remplacé par le texte officiel (audit §8.3)
FEATS_2014_PRESENT = {
    "Actor": None, "Martial Adept": None, "Alert": None, "Athlete": None, "Savage Attacker": None,
    "Tavern Brawler": None, "Great Weapon Master": None, "Lucky": None, "Dual Wielder": None,
    "Mounted Combatant": None, "Crossbow Expert": None, "Magic Initiate": None, "War Caster": None,
    "Weapon Master": None, "Polearm Master": None, "Shield Master": None, "Mobile": None, "Observant": None,
    "Resilient": None, "Ritual Caster": None, "Tough": None, "Sharpshooter": None, "Dungeon Delver": None,
    "Prodigy": None, "Bountiful Luck": None, "Infernal Constitution": None, "Squat Nimbleness": None,
    "Metamagic Adept": None, "Artificer Initiate": None, "Crusher": None, "Chef": None, "Fighting Initiate": None,
    "Eldritch Adept": None, "Gunner": None, "Telekinetic": None, "Telepathic": None,
    "Durable": "Dur à cuire", "Medium Armor Master": "Maître des armures intermédiaires",
    "Heavy Armor Master": "Maître des armures lourdes", "Elemental Adept": "Adepte élémentaire",
    "Keen Mind": "Esprit affûté", "Poisoner": "Maître des poisons", "Piercer": "Perçant", "Slasher": "Tranchant",
    "Fey Touched": "Affamé de magie", "Skill Expert": "Prodigieusement doué", "Shadow Touched": "Adepte des ombres",
    "Spell Sniper": "Percheur", "Aberrant Dragonmark": "Marque aberrante"}
# catégories de « dons » 2014 qui n'en sont pas au sens de l'amélioration de caractéristique (Theros, faveurs…)
FEAT_CATEGORIES_EXCLUDED = ("piete", "piété", "benediction", "charme", "surnaturel", "faveur epique", "don sombre")

WEAPONS_2014 = {"Net"}            # armes 2014 absentes (les armes futuristes du Guide du maître restent à part)

BACKGROUND_GOLD = re.compile(r"(\d+)\s*po\b")


# ----------------------------------------------------------------------------------------------- utilitaires
def _unique(name: str, existing, edition: int) -> str:
    if name not in existing:
        return name
    base = name + (SUFFIX_2024 if edition == 2024 else " ({})".format(edition))
    candidate, n = base, 2
    while candidate in existing:
        candidate, n = "{} {}".format(base, n), n + 1
    return candidate


def _source(item: dict) -> str:
    src = item.get("source") or {}
    return src.get("titre", "") if isinstance(src, dict) else str(src)


def _text(value) -> str:
    if isinstance(value, list):
        return "\n".join(_text(v) for v in value)
    if isinstance(value, dict):
        name, desc = value.get("nom"), value.get("description", "")
        return "{}. {}".format(name, desc) if name else desc
    return str(value or "")


def _flat(value) -> str:
    """Texte d'un champ qui peut être une chaîne ou une liste (« A, B »)."""
    if isinstance(value, list):
        return ", ".join(_text(v) for v in value if v)
    return _text(value)


def _asi(benefits) -> tuple[str, list[str]]:
    """Augmentation de caractéristique d'un don officiel -> (texte façon app, caractéristiques au choix)."""
    for b in benefits or []:
        text = _text(b)
        t = norm(text)
        if not re.search(r"augmentez .*de 1\b", t):
            continue
        if "de votre choix" in t or "au choix" in t:
            return "Augmente une caractéristique au choix +1", list(ABILITIES)
        found = [ab for ab in ABILITIES if norm(ab) in t]
        if found:
            return " ou ".join(found) + " +1", found
    return "Aucune", []


def _skills(text, db) -> list[str]:
    text = ", ".join(map(str, text)) if isinstance(text, list) else str(text or "")
    parts = [p.strip(" .") for p in re.split(r",| et |;", text) if p.strip(" .")]
    return [db.canonical_skill(p) for p in parts if db.canonical_skill(p) in db.skill_names]


# ----------------------------------------------------------------------------------------------- fusion
def merge(db) -> dict:
    """Fusionne `data/editions/` dans `db` ; renvoie le nombre d'éléments ajoutés par type."""
    for coll in (db.spells, db.feats, db.backgrounds, db.races, db.weapons):
        for item in coll.values():
            item.setdefault("edition", 2014)
    for cls in db.classes.values():
        for sub in cls.get("sous_classes", []):
            sub.setdefault("edition", 2014)
    cat = db.editions
    stats = {"sorts": 0, "dons": 0, "dons_corriges": 0, "historiques": 0, "sous_classes": 0, "especes": 0,
             "armes": 0, "objets_magiques": 0, "races_2014": 0, "equipement_2024": 0, "listes_sorts": 0}
    if not cat.available():
        return stats
    _merge_spells(db, cat, stats)
    _merge_spell_lists(db, cat, stats)
    _merge_feats(db, cat, stats)
    _merge_backgrounds(db, cat, stats)
    _merge_subclasses(db, cat, stats)
    _merge_species(db, cat, stats)
    _merge_races_2014(db, cat, stats)
    _merge_weapons(db, cat, stats)
    _merge_magic_items(db, cat, stats)
    _merge_gear_2024(db, cat, stats)
    db._spell_index = {norm(n): n for n in db.spells}
    return stats


# v53 : objets qui « fonctionnent comme » un objet du catalogue (Tombe de l'Annihilation) -> mêmes effets et case
MAGIC_ALIASES = {"Anneau de protection d'Obo'laka": "Anneau de protection",
                 "Bracelets d'archerie de Kubazan": "Bracelets d'archer",
                 "Œuf de gruog pétrifié de Nangnang (perle de puissance)": "Perle de pouvoir",
                 "Charme de Joho": "Heaume de compréhension des langues",
                 "Instrument de barde de Shagambi (mandoline de Canaith)": "Mandoline de Canaith",
                 "Corne d'I'jin (baguette de prodiges)": "Baguette des merveilles",
                 "Robe de couleurs scintillantes d'Unkh": "Robe prismatique"}


def _merge_magic_items(db, cat, stats):
    """v53 : objets magiques de la référence absents de data/objets_magiques.json (Tasha, Xanathar, Eberron,
    Wildemount, Fizban…) — même format que les objets chargés. Doublons écartés par nom français, nom anglais et
    formes « +1, +2 ou +3 » déjà découpées en paliers (« Armure +1 »…)."""
    import json
    from .data_loader import normalize_magic_item
    from .paths import get_resource_path
    names_en = set()
    try:                                                 # noms anglais des objets déjà chargés
        with open(get_resource_path("data/objets_magiques.json"), encoding="utf-8") as f:
            names_en = {norm(o.get("nom_en") or "") for o in json.load(f).get("objets", [])} - {""}
    except (OSError, ValueError, AttributeError):
        pass
    present = {norm(n) for n in db.magic_items}
    for o in cat.items("objets"):
        name = o.get("nom", "")
        if not name or norm(name) in present or norm(o.get("nom_en") or "-") in names_en:
            continue
        if "+1, +2 ou +3" in name and norm(name.replace("+1, +2 ou +3", "+1")) in present:
            continue
        m = re.match(r"\s*([^(]+?)\s*(?:\((.*)\))?\s*$", o.get("type", "") or "")
        kind, prec = (m.group(1), m.group(2) or "") if m else (o.get("type", ""), "")
        raw = {"id": o.get("id", name), "nom": name, "type": kind or "Objet merveilleux", "type_precision": prec,
               "rarete_texte": o.get("rarete", ""), "lien": bool(o.get("attunement")),
               "lien_condition": o.get("attunement_precision") or "", "description": _text(o.get("description", "")),
               "source": _source(o)}
        item = normalize_magic_item(raw)
        item.update(edition=int(o.get("edition") or 2014), importe=True)
        twin = db.magic_items.get(MAGIC_ALIASES.get(name, ""))
        if twin:                                         # effets de l'objet dont il tient lieu
            item.update(comme=twin["nom"], ca=twin["ca"], js=twin["js"], lien=twin["lien"] or item["lien"],
                        description=item["description"] + "\n\n" + twin["description"])
        db.magic_items[name] = item
        present.add(norm(name))
        stats["objets_magiques"] += 1


def _merge_spells(db, cat, stats):
    from .data_loader import normalize_spell
    present = {norm(n) for n in db.spells}
    for ed in (2014, 2024):
        for s in cat.list("sorts", str(ed)):
            if ed == 2014 and (norm(s["nom"]) in present or norm(s["nom"]) in SPELL_TRANSLATIONS_2014):
                continue
            duration = s.get("duration", "") or ""
            desc = s.get("description", "") or ""
            if s.get("aux_niveaux_superieurs"):
                desc += "\n\n" + s["aux_niveaux_superieurs"]
            raw = {"nom": _unique(s["nom"], db.spells, ed), "niveau": s.get("niveau", 0), "ecole": s.get("ecole", ""),
                   "incantation": s.get("casting_time", ""), "portee": s.get("range", ""),
                   "composantes": s.get("components", ""), "concentration": "concentration" in norm(duration),
                   "rituel": bool(s.get("ritual")), "duree": duration, "description": desc,
                   "classes": list(s.get("classes") or [])}
            sp = normalize_spell(raw, {})
            sp.update(edition=ed, source=_source(s), id=s.get("id", ""))
            if ed == 2024:                                   # v52 : soins, JS, surclassement des sorts 2024
                _enrich_2024(sp, db.spells.get(re.sub(r"\s*\(2024\)$", "", sp["nom"])))
            if sp.get("test") and not sp.get("js_succes"):
                sp["js_succes"] = "aucun" if int(sp.get("niveau") or 0) == 0 else "moitie"
            db.spells[sp["nom"]] = sp
            stats["sorts"] += 1


# v53 : sorts de la référence connus sous un autre nom dans l'application
SPELL_NAME_MAP = {"lance psychique de raulothim": "Lance d'arçon psychique de Raulothim",
                  "piques argentees": "Barbes argentées", "invocation d'esprit draconique": "Convocation d'esprit draconique",
                  }
CLASS_IDS = {"artificer": "Artificier", "druid": "Druide", "ranger": "Rôdeur", "sorcerer": "Ensorceleur",
             "wizard": "Magicien", "cleric": "Clerc", "paladin": "Paladin", "bard": "Barde", "warlock": "Occultiste"}


def _merge_spell_lists(db, cat, stats):
    """v53 : listes de sorts 2014 par classe complétées d'après sorts_par_classe_fr.json (sorts de Xanathar,
    Tasha… ajoutés aux listes officielles : Gelure pour l'Occultiste, Verrou magique pour l'Artificier…)."""
    import json
    from .paths import get_resource_path
    try:
        with open(get_resource_path("data/editions/sorts_par_classe_fr.json"), encoding="utf-8") as f:
            index = json.load(f).get("classes", {})
    except (OSError, ValueError):
        return
    by_id = {s.get("id"): s for s in cat.items("sorts")}
    names = {norm(n): n for n in db.spells if "(2024)" not in n}
    for cid, levels in index.items():
        parts = cid.split("-")
        if len(parts) < 3 or parts[2] != "2014" or parts[1] not in CLASS_IDS:
            continue
        cls = CLASS_IDS[parts[1]]
        for ids in (levels or {}).values():
            for sid in ids or []:
                ref = by_id.get(sid)
                if not ref or ref.get("restriction_acces"):     # dunamancie (Wildemount) : accès restreint
                    continue
                app = SPELL_NAME_MAP.get(norm(ref["nom"])) or names.get(norm(ref["nom"]))
                sp = db.spells.get(app or "")
                if sp is not None and cls not in sp.setdefault("classes", []):
                    sp["classes"].append(cls)
                    stats["listes_sorts"] += 1


def _enrich_2024(sp: dict, twin: Optional[dict]) -> None:
    """Complète un sort 2024 : règles lues dans son texte, puis règles auditées du sort 2014 équivalent pour ce que le
    texte ne donne pas (projectiles, modificateur aux dégâts, échelle des tours de magie…)."""
    from .rules import SPELL_RULE_KEYS, parse_spell_mechanics_2024
    parsed = parse_spell_mechanics_2024(sp.get("description", ""))
    for k, v in parsed.items():
        if k == "test" and sp.get("test") in ("A", "AC", "Arme"):
            continue
        sp[k] = v
    if twin and str(twin.get("edition", 2014)) != "2024" and int(twin.get("niveau") or 0) == int(sp.get("niveau") or 0):
        for k in SPELL_RULE_KEYS:
            if twin.get(k) not in (None, "", False) and sp.get(k) in (None, "", False):
                sp[k] = twin[k]
        if sp.get("degats") and str(twin.get("degats", "")).replace(" ", "").startswith(sp["degats"] + "+"):
            sp["degats"] = twin["degats"]                    # « 1d4 + 1 » (Projectile magique)
    if sp.get("test") in ("A", "AC", "Arme"):
        sp["js_succes"] = "aucun"


def _merge_feats(db, cat, stats):
    from .data_loader import normalize_feat
    present = {norm(n) for n in db.feats}
    gm_feats = []
    for f in cat.list("dons", "2014"):
        en = f.get("nom_en", "")
        if norm(f.get("categorie", "")) and any(x in norm(f.get("categorie", "")) for x in FEAT_CATEGORIES_EXCLUDED):
            if norm(f["nom"]) not in present:            # v53 : don accordé par le MJ (faveur épique, charme,
                gm_feats.append(f)                        # bénédiction, don de piété ou sombre) : hors progression
            continue
        asi, choices = _asi(f.get("benefices"))
        if en in FEATS_2014_PRESENT:
            app_name = FEATS_2014_PRESENT[en]
            if app_name and app_name in db.feats:          # texte officiel, nom de l'app conservé
                db.feats[app_name].update(source=_source(f), prerequis=f.get("prerequis") or "Aucun", asi_texte=asi,
                                          carac_choix=choices, description=f.get("description", ""),
                                          nom_officiel="{} ({})".format(f["nom"], en))
                stats["dons_corriges"] += 1
            continue
        if norm(f["nom"]) in present:
            continue
        _add_feat(db, f, 2014, asi, choices, normalize_feat, stats)
    for f in cat.list("dons", "2024"):
        asi, choices = _asi(f.get("benefices"))
        _add_feat(db, f, 2024, asi, choices, normalize_feat, stats)
    for f in gm_feats:                                   # après 2024 : les faveurs épiques 2024 gardent leur nom
        asi, choices = _asi(f.get("benefices"))
        _add_feat(db, f, 2014, asi, choices, normalize_feat, stats)
        name = next(n for n in reversed(list(db.feats)) if db.feats[n].get("id") == f.get("id", ""))
        db.feats[name]["mj_seulement"] = True
        stats["dons_mj"] = stats.get("dons_mj", 0) + 1
    db.feats = dict(sorted(db.feats.items(), key=lambda kv: (norm(kv[0]), kv[0])))


def _add_feat(db, f, ed, asi, choices, normalize_feat, stats):
    name = _unique(f["nom"], db.feats, ed)
    feat = normalize_feat({"don": name, "source": _source(f), "prerequis": f.get("prerequis") or "Aucun",
                           "augmentation_caracteristique": asi, "description": f.get("description", "")})
    feat.update(carac_choix=choices, edition=ed, categorie=f.get("categorie", ""), id=f.get("id", ""))
    db.feats[name] = feat
    stats["dons"] += 1


def _merge_backgrounds(db, cat, stats):
    present = {norm(n) for n in db.backgrounds}
    for ed in (2014, 2024):
        for h in cat.list("historiques", str(ed)):
            if h.get("competences") is None or (ed == 2014 and norm(h["nom"]) in present):
                continue
            skills = _skills(h.get("competences", ""), db)
            parent_ref = h.get("variante_de")
            if not skills and parent_ref:                  # variante (Gladiateur, Espion…) : compétences du parent
                parent = cat.get(parent_ref) or cat.find("historiques", str(parent_ref), ed)
                skills = _skills((parent or {}).get("competences", ""), db)
                app_parent = db.backgrounds.get((parent or {}).get("nom", ""))
                if len(skills) < 2 and app_parent:          # repli : compétences du même historique dans l'app
                    skills = [x for x in (app_parent.get("competence_1"), app_parent.get("competence_2")) if x]
            equip = _flat(h.get("equipement"))
            gold = BACKGROUND_GOLD.findall(equip)
            name = _unique(h["nom"], db.backgrounds, ed)
            db.backgrounds[name] = {
                "historique": name, "competence_1": skills[0] if skills else "",
                "competence_2": skills[1] if len(skills) > 1 else "", "langues": _flat(h.get("langues")) or "-",
                "outil_maitrise": _flat(h.get("outils")) or "-", "inventaire_historique": equip,
                "or": int(gold[0]) if gold else 0, "description": h.get("description", ""),
                "capacite": _text(h.get("capacite")), "source": _source(h), "edition": ed, "id": h.get("id", ""),
                # 2024 : les augmentations de caractéristiques et le don d'origine viennent de l'historique
                "caracteristiques_2024": list(h.get("caracteristiques") or []), "don_origine": h.get("don") or ""}
            stats["historiques"] += 1


def _merge_subclasses(db, cat, stats):
    for s in cat.list("sous_classes", "2014"):
        if s.get("nom_en") not in SUBCLASSES_2014 or s.get("classe") not in db.classes:
            continue
        subs = db.classes[s["classe"]].setdefault("sous_classes", [])
        if any(norm(x["nom"]) == norm(s["nom"]) for x in subs):
            continue
        raw_spells = s.get("sorts_de_sous_classe") or {}
        groups = raw_spells.values() if isinstance(raw_spells, dict) else [raw_spells]
        spells = []
        for group in groups:
            for n in (group if isinstance(group, list) else [group]):
                name = n.get("nom", "") if isinstance(n, dict) else str(n or "")
                if name:
                    spells.append(name[:1].upper() + name[1:])
        subs.append({"nom": s["nom"], "source": _source(s), "edition": 2014, "id": s.get("id", ""),
                     "description": s.get("introduction", ""), "sorts_domaine": spells,
                     "capacites": [{"niveau": int(c.get("niveau") or 0), "nom": c.get("nom", ""),
                                    "description": c.get("description", "")} for c in s.get("capacites", [])]})
        stats["sous_classes"] += 1


def _merge_species(db, cat, stats):
    for r in cat.list("races", "2024"):
        if r.get("sous_race_de"):
            continue
        name = _unique(r["nom"], db.races, 2024)
        traits = [{"nom": t.get("nom", ""), "description": t.get("description", "")}
                  for t in r.get("traits_raciaux") or [] if isinstance(t, dict)]
        traits.insert(0, {"nom": "Caractéristiques (2024)",
                          "description": "En 2024, les augmentations de caractéristiques viennent de l'historique "
                                         "(+2/+1 ou +1/+1/+1 parmi les trois caractéristiques qu'il propose) ; "
                                         "l'application les propose ici, au choix."})
        db.races[name] = {"nom": name, "source": _source(r), "caracteristiques": "+2, +1 (ou +1, +1, +1)",
                          "langues": ["Commun", "Au choix"], "capacites": traits, "edition": 2024,
                          "id": r.get("id", ""), "description": r.get("description", "")}
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*m", str((r.get("caracteristiques") or {}).get("vitesse", "")))
        if m:
            db.speeds[name] = float(m.group(1).replace(",", "."))
        stats["especes"] += 1


# v53 : races et sous-races 2014 absentes de Races.json (Eberron, Fizban, Wildemount, Côte des Épées)
RACES_2014_SKIP = {          # déjà dans l'application sous un autre nom, ou texte de règles (pas une race jouable)
    "genasi", "drow", "elfe noir", "demi-orc", "homme-lezard", "tortelin", "forge de guerre", "metamorphe",
    "harengon", "sang-sorcier", "renaissant", "nain gris", "nain d'or", "nain des ecus", "elfe de la lune",
    "elfe du soleil", "halfelin coeur-vaillant", "personnaliser", "ethnies", "sous-races d'elfes rares",
    "tieffelin de feerune", "etre creux"}
RACES_2014_SKIP_EXACT = {"haut-elfe", "elfe des bois", "fee", "humain (variante)"}   # Elfe (sous-races), Fadette…
# race 2014 de l'application qui sert de parent quand la référence ne donne qu'un renvoi au manuel :
# (race, traits propres à retirer, bonus de base)
APP_PARENTS = {"drakeide": ("Drakéide", (), ""), "dragonborn": ("Drakéide", (), ""),
               "demi-elfe": ("Demi-elfe", ("polyvalence", "augmentation de caracteristiques"), ""),
               "aasimar": ("Aasimar protecteur", ("ame radieuse",), "Cha +2")}
RACE_PARENTS = {"dragonborn": "Drakéide", "drakeide": "Drakéide", "elf": "Elfe", "elfe": "Elfe", "halfling": "Halfelin",
                "halfelin": "Halfelin", "dwarf": "Nain", "nain": "Nain", "aasimar": "Aasimar", "gnome": "Gnome",
                "humain": "Humain", "demi-elfe": "Demi-elfe", "demi-orc / humain": "Humain"}
ABILITY_WORDS = {"force": "For", "dexterite": "Dex", "constitution": "Con", "intelligence": "Int", "sagesse": "Sag",
                 "charisme": "Cha"}
DROP_TRAITS = ("augmentation de caracteristique", "age", "alignement", "langues", "sous-race", "type de creature",
               "sorts de la marque")


def _race_name_2014(name: str) -> str:
    """« Humain (variante) : Marque du passage » -> « Humain (Marque du passage) » ; « Sous-race naine : Marque de
    Garde » -> « Nain (Marque de garde) »."""
    m = re.match(r"(?:Sous-race (naine|elfique|halfeline)|(.+?)(?: \(variante\))?)\s*:\s*(.+)$", name)
    if not m:
        return name
    parent = {"naine": "Nain", "elfique": "Elfe", "halfeline": "Halfelin"}.get(m.group(1) or "", m.group(2) or "")
    parent = parent.replace("Demi-orc ou humain", "Demi-orque ou humain")
    mark = m.group(3)
    return "{} ({})".format(parent, mark[:1].upper() + mark[1:].lower().replace("marque", "Marque", 1))


def _asi_text(text: str) -> str:
    """« Votre valeur de Dextérité augmente de 2, et une autre valeur … de votre choix augmente de 1 » -> « Dex +2, +1 »."""
    n = norm(text)
    parts = ["{} +{}".format(ABILITY_WORDS[w], v) for w, v in re.findall(
        r"(force|dexterite|constitution|intelligence|sagesse|charisme)(?: augmente de| \+)\s*(\d)", n)]
    parts += ["+{}".format(v) for v in re.findall(r"(?:de votre choix|une autre|au choix)[^.]*?augmente de (\d)", n)]
    if not parts and ("une valeur de caracteristique de 2" in n or "augmentez une valeur" in n):
        return "+2, +1 (ou +1, +1, +1)"
    return ", ".join(parts)


RACE_TEXT_FIXES = {"tour de magie bourrasque": "tour de magie rafale de vent",   # Marque de la tempête : Gust
                   "sort rafale de vent": "sort bourrasque",                   # puis Gust of Wind (Bourrasque)
                   "purification de la nourriture et de l'eau": "purification de nourriture et d'eau"}
SPELL_STOP = {"une", "grace", "par", "avec", "sans", "lorsque", "quand", "a", "au", "des", "vous", "pour", "sur",
              "en", "si", "dans", "jusqu'a", "fois"}


def _mark_race_spells(text: str, spells: dict) -> str:
    """Noms de sorts accordés écrits en *italique* (convention de Races.json lue par Engine.racial_spells) :
    « Vous connaissez le tour de magie illusion mineure. … lancer le sort invisibilité » -> *illusion mineure*…
    Plusieurs sorts à la suite (« détection de la magie et détection du poison et des maladies ») : le plus long
    nom reconnu à chaque position."""
    text = text.replace("’", "'")
    for bad, good in RACE_TEXT_FIXES.items():
        text = re.sub(bad, good, text, flags=re.I)
    out = text
    for m in re.finditer(r"(?:tour de magie|le sort|les sorts|lancer)\s+([^.;:(]+)", text, re.I):
        segment = re.sub(r"^(?:aussi\s+|également\s+)?(?:le|les)\s+sorts?\s+", "", m.group(1), flags=re.I)
        words = segment.replace(",", " , ").split()
        i = 0
        while i < len(words):
            hit = 0
            for k in range(min(8, len(words) - i), 0, -1):
                cand = " ".join(words[i:i + k]).strip(" «»\"")
                if len(cand) >= 4 and norm(cand) in spells:
                    hit = k
                    if "*" + cand not in out:
                        out = out.replace(cand, "*" + cand + "*", 1)
                    break
            if hit:
                i += hit
            elif norm(words[i]) in ("et", "ou", ","):
                i += 1
            else:
                break                                    # fin de l'énumération des sorts
    return out


def _merge_races_2014(db, cat, stats):
    present = {norm(n) for n in db.races}
    refs = cat.items("races")
    parents = {}
    for r in refs:                                       # parent 2014 : la fiche du Manuel (avec ses bonus)
        if str(r.get("edition")) == "2014" and not r.get("sous_race_de"):
            score = sum(1 for t in r.get("traits_raciaux") or [] if isinstance(t, dict) and
                        norm(t.get("nom", "")).startswith(("augmentation de caract", "langues")))
            if score > parents.get(norm(r["nom"]), ({}, -1))[1]:
                parents[norm(r["nom"])] = (r, score)
    parents = {k: v[0] for k, v in parents.items()}
    languages = [x for x in db.language_names()] if hasattr(db, "language_names") else []
    for r in refs:
        if str(r.get("edition")) != "2014" or not r.get("traits_raciaux"):
            continue
        name = _race_name_2014(r["nom"])
        n = norm(r["nom"])
        if norm(name) in present or n in RACES_2014_SKIP_EXACT or any(k in n for k in RACES_2014_SKIP):
            continue
        raw_traits = [t for t in r.get("traits_raciaux") or [] if isinstance(t, dict)]
        drop_parent = set()
        for t in raw_traits:                             # « (option, remplace Polyvalence) » : trait parent retiré
            for w in re.findall(r"remplace ([^)]+)\)", t.get("nom", "")):
                drop_parent.add(norm(w.strip()))
        traits = [t for t in raw_traits if "renvoi" not in norm(t.get("nom", "")) and
                  not norm(t.get("nom", "")).startswith("variantes de")]
        stub = len(traits) < len(raw_traits)
        own = {norm(t.get("nom", "")) for t in traits}
        asi_trait = next((t for t in traits if norm(t.get("nom", "")).startswith("augmentation de caract")), None)
        car = r.get("caracteristiques") if isinstance(r.get("caracteristiques"), dict) else {}
        asi = _asi_text((asi_trait or {}).get("description", "") or car.get("bonus_caracteristiques", "")
                        or car.get("bonus", ""))
        if "resistance" in norm(str(car.get("remplace", ""))):
            drop_parent.add("resistance")                # Drakéide ravenite : la résistance du parent est remplacée
        pkey = norm(r.get("sous_race_de") or "")
        parent = parents.get(norm(RACE_PARENTS.get(pkey, r.get("sous_race_de") or "")))
        stub = stub or any("renvoi" in norm(t.get("nom", "")) for t in (parent or {}).get("traits_raciaux") or []
                           if isinstance(t, dict))        # la référence du parent n'est qu'un renvoi au manuel
        app_parent = APP_PARENTS.get(pkey) if (stub or parent is None) else None
        if app_parent and app_parent[0] in db.races:     # renvoi au manuel : traits de la race 2014 de l'appli
            ar = db.races[app_parent[0]]
            drop_parent |= set(app_parent[1])
            parent = {"nom": app_parent[0], "traits_raciaux": [
                c for c in ar.get("capacites", []) if not any(norm(c.get("nom", "")).startswith(d) or
                                                               d.startswith(norm(c.get("nom", ""))) for d in drop_parent)],
                "_asi": app_parent[2] or ar.get("caracteristiques", ""), "_langues": ar.get("langues", [])}
        full = "type de creature" in own
        replaces = full or "remplac" in norm(r.get("description", "")) or "remplace" in car or \
            sum(int(x) for x in re.findall(r"\+(\d)", asi)) >= 3
        merged = []
        if parent and not full:                          # traits de la race parente, sauf ceux que la sous-race change
            pt = [t for t in parent.get("traits_raciaux") or [] if isinstance(t, dict)]
            merged = [t for t in pt if norm(t.get("nom", "")) not in own and
                      not any(norm(t.get("nom", "")).startswith(d) for d in drop_parent)]
            if not replaces:
                p_asi = next((t for t in pt if norm(t.get("nom", "")).startswith("augmentation de caract")), None)
                base = parent.get("_asi") or _asi_text((p_asi or {}).get("description", ""))
                asi = ", ".join(x for x in (base, asi) if x)
        merged += traits
        lang_text = " ".join(t.get("description", "").split(".")[0] for t in merged
                             if norm(t.get("nom", "")) == "langues")             # 1re phrase : les langues parlées
        langs = [x for x in languages if norm(x) and re.search(r"\b{}\b".format(re.escape(norm(x))), norm(lang_text))] \
            or list((parent or {}).get("_langues") or ["Commun"])
        if "autre langue" in norm(lang_text) or "de votre choix" in norm(lang_text):
            langs.append("1 au choix")
        spell_names = {norm(n): n for n, sp in db.spells.items() if "(2024)" not in n}
        caps = [{"nom": t.get("nom", ""), "description": _mark_race_spells(t.get("description", ""), spell_names)
                 if re.search(r"tour de magie|sort", norm(t.get("description", ""))) else t.get("description", "")}
                for t in merged if not norm(t.get("nom", "")).startswith(DROP_TRAITS)]
        spells = r.get("sorts_de_la_marque")
        if isinstance(spells, dict) and spells:          # sorts de la marque : ajoutés aux listes des lanceurs
            caps.append({"nom": "Sorts de la Marque", "description": "Si vous avez la capacité Incantation, ces "
                         "sorts s'ajoutent à la liste de sorts de votre classe : " + " ; ".join(
                             "niveau {} : {}".format(k[0], ", ".join(v)) for k, v in spells.items())})
        mark_spells = []
        if isinstance(spells, dict):                     # noms de l'application (sorts 2014)
            for group in spells.values():
                for sp_name in group or []:
                    app = SPELL_NAME_MAP.get(norm(sp_name)) or spell_names.get(norm(sp_name))
                    if app:
                        mark_spells.append(app)
        db.races[name] = {"nom": name, "source": _source(r), "caracteristiques": asi or "+2, +1 (ou +1, +1, +1)",
                          "sorts_marque": mark_spells,
                          "langues": list(dict.fromkeys(langs)), "capacites": caps, "edition": 2014,
                          "id": r.get("id", ""), "description": r.get("description", ""),
                          "sous_race_de": (parent or {}).get("nom", "")}
        speed = next((t.get("description", "") for t in reversed(merged)        # la sous-race prime (10,50 m)
                      if "vitesse de marche" in norm(t.get("description", ""))), "")
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*m", speed)
        if m:
            db.speeds[name] = float(m.group(1).replace(",", "."))
        present.add(norm(name))
        stats["races_2014"] += 1


def _merge_gear_2024(db, cat, stats):
    """v53 : paquetages 2024 (« Sac d'explorateur »…) et équipement d'aventurier 2024 absent du catalogue, pour
    l'équipement de départ des personnages 2024 (développés en objets comme les paquetages 2014)."""
    if not hasattr(db, "equipment"):
        return
    added = False
    for kind in ("equipement_aventurier", "kits"):
        for o in cat.list(kind, "2024"):
            name = o.get("nom", "")
            if not name or name in db.equipment or name in db.catalog or norm(name).startswith("parchemin de sort"):
                continue
            weight = o.get("poids_kg")
            desc = o.get("description", "") or ""
            if kind == "kits" and o.get("contenu"):          # liste lisible par Database.parse_item_list
                desc = "Contient " + ", ".join("{}{}".format("{} ".format(c["quantite"]) if int(c.get(
                    "quantite") or 1) > 1 else "", c["objet"]) for c in o["contenu"]) + "."
            db.equipment[name] = {"nom": name, "poids": "{} kg".format(str(weight).replace(".", ",")) if isinstance(
                weight, (int, float)) else "—", "prix": o.get("cout") or "—", "description": desc,
                "categorie": "Paquetage" if kind == "kits" else "Équipement", "edition": 2024}
            stats["equipement_2024"] += 1
            added = True
    if added and hasattr(db, "_build_catalog"):
        db._build_catalog()


def _merge_weapons(db, cat, stats):
    from .data_loader import normalize_weapon
    for w in cat.list("armes", "2014"):
        if w.get("nom_en") not in WEAPONS_2014 or w["nom"] in db.weapons:
            continue
        cat_name = "Armes {} {}".format("courantes" if "courante" in norm(w.get("categorie", "")) else "de guerre",
                                       "à distance" if "distance" in norm(w.get("type", "")) else "de corps à corps")
        raw = {"nom": w["nom"], "categorie": cat_name, "degats": w.get("degats") or "—",
               "proprietes": ", ".join(p[:1].upper() + p[1:] for p in w.get("proprietes") or []),
               "botte_arme": "", "description_botte": "", "poids": "{} kg".format(w.get("poids_kg", "—")),
               "prix": w.get("cout", "—")}
        weapon = normalize_weapon(raw)
        weapon.update(edition=2014, id=w.get("id", ""))
        db.weapons[weapon["nom"]] = weapon
        stats["armes"] += 1


def stats_text(stats: Optional[dict]) -> str:
    if not stats:
        return ""
    return ("Données 2014 / 2024 ajoutées : {sorts} sorts, {dons} dons ({dons_corriges} textes corrigés), "
            "{historiques} historiques, {sous_classes} sous-classes, {especes} espèces 2024, {armes} arme(s).").format(
        **stats)


# ----------------------------------------------------------------------------------------------- classes 2024
SAVE_SPLIT = re.compile(r",| et ")
ARMOR_WORDS = (("legere", "Armures légères"), ("intermediaire", "Armures intermédiaires"),
               ("lourde", "Armures lourdes"), ("bouclier", "Boucliers"))


def _parse_skill_choice(text: str, db) -> tuple[list[str], int]:
    """« Choisissez-en 2 : A, B ou C » -> ([A, B, C], 2) ; « Choisissez 3 compétences au choix » -> (toutes, 3)."""
    t = str(text or "")
    m = re.search(r"(\d+)", t)
    count = int(m.group(1)) if m else 2
    if ":" not in t and "au choix" in norm(t):
        return list(db.skill_names), count
    body = t.split(":", 1)[1] if ":" in t else t
    body = re.sub(r"\bparmi\b", "", body)
    parts = [p.strip(" .") for p in re.split(r",| ou | et ", body) if p.strip(" .")]
    skills = []
    for p in parts:
        cs = db.canonical_skill(p)
        if cs in db.skill_names and cs not in skills:
            skills.append(cs)
    return skills, count


def _parse_weapons(text: str, db) -> list[str]:
    t = norm(text)
    out = ["Armes courantes"] if ("courante" in t or "simple" in t) else []
    if "guerre" in t:
        restrict = [p for p in ("legere", "finesse") if p in t.split("guerre", 1)[1]]
        if restrict:                                  # Moine, Roublard 2024 : armes de guerre Légère / Finesse
            out += sorted(n for n, w in db.weapons.items() if w.get("categorie") == "guerre"
                          and any(r in norm(" ".join(w.get("proprietes", []))) for r in restrict))
        else:
            out.append("Armes de guerre")
    return out



# nom dans la table de progression 2024 -> nom de l'aptitude dans les descriptions (traductions différentes)
FEATURE_ALIASES_2024 = {
    "maitrise des armes": "bottes d'arme", "restauration de soi": "autosubsistance", "indomptable": "inflexible",
    "derobade": "esquive totale", "talent fiable": "savoir-faire", "frappes retorses": "coups vicieux",
    "expansion de l'aura": "aura etendue", "nomade": "arpenteur", "connaissance primitive": "savoir primal",
    "bond instinctif": "bond agressif", "concentration du moine": "credo du moine",
}

def _expand_features(c: dict) -> list[dict]:
    """Aptitudes niveau par niveau d'après la colonne « capacites » de la table (améliorations répétées comprises)."""
    feats = c.get("capacites") or []
    by_name = {norm(f.get("nom", "")): f for f in feats}
    by_name.update({k: by_name[v] for k, v in FEATURE_ALIASES_2024.items() if v in by_name and k not in by_name})
    out = []
    for row in c.get("table_progression") or []:
        lvl = int(row.get("niveau") or 0)
        names = [n.strip() for n in re.split(r",(?![^()]*\))", str(row.get("capacites") or "")) if n.strip()]
        for n in names:
            base = re.sub(r"\s*\(.*?\)\s*$", "", n)
            f = by_name.get(norm(base)) or next((v for k, v in by_name.items() if k and norm(base).startswith(k)), None)
            if f is None:                             # nom de la table différent de celui de l'aptitude
                same = [x for x in feats if int(x.get("niveau") or 0) == lvl]
                scored = [(difflib.SequenceMatcher(None, norm(base), norm(x.get("nom", ""))).ratio(), x) for x in same]
                best = max(scored, key=lambda t: t[0], default=(0, None))
                f = best[1] if best[0] >= 0.4 else None
            if norm(base).startswith(("faveur epique", "don epique")):
                n = "Amélioration de caractéristique ou Faveur épique"      # niveau 19 : don de faveur épique
            out.append({"niveau": lvl, "nom": n, "description": (f or {}).get("description", ""),
                        "edition": 2024})
    if not out:                                       # table sans colonne d'aptitudes : liste brute
        out = [{"niveau": int(f.get("niveau") or 0), "nom": f.get("nom", ""),
                "description": f.get("description", ""), "edition": 2024} for f in feats]
    return out


def build_classes_2024(db) -> dict[str, dict]:
    """Classes 2024 au format du moteur (`Database.classes`), avec leurs sous-classes 2024 et leur table."""
    cat = db.editions
    out: dict[str, dict] = {}
    if not cat.available():
        return out
    for c in cat.list("classes", "2024"):
        b = c.get("caracteristiques_de_base") or {}
        die = re.search(r"d(\d+)", norm(b.get("de_vie", "")))
        skills, n_skills = _parse_skill_choice(b.get("competences", ""), db)
        saves = [s.strip() for s in SAVE_SPLIT.split(str(b.get("jets_de_sauvegarde") or "")) if s.strip()]
        armors_t = norm(b.get("armures", ""))
        armors = [label for key, label in ARMOR_WORDS if key in armors_t]
        subs = []
        for s in cat.list("sous_classes", "2024", classe=c["nom"]):
            subs.append({"nom": s["nom"], "source": _source(s), "edition": 2024, "id": s.get("id", ""),
                         "description": s.get("introduction", ""),
                         "capacites": [{"niveau": int(f.get("niveau") or 0), "nom": f.get("nom", ""),
                                        "description": f.get("description", "")} for f in s.get("capacites", [])]})
        out[c["nom"]] = {
            "nom": c["nom"], "edition": 2024, "id": c.get("id", ""), "source": _source(c),
            "de_vie": "d{}".format(die.group(1)) if die else "d8",
            "carac_principale": b.get("caracteristique_principale", ""),
            "maitriser_sauvegardes": saves,
            "maitrises": {"competences_choix": skills, "competences_nombre": n_skills, "armures": armors,
                          "armes": _parse_weapons(b.get("armes", ""), db)},
            "outils_texte": b.get("outils") or "", "equipement_depart": b.get("equipement_de_depart", ""),
            "capacites_classe": _expand_features(c), "sous_classes": subs,
            "table_2024": {int(r.get("niveau") or 0): r for r in c.get("table_progression") or []}}
    return out


PACT_ALIASES_2024 = {"pacte du tome": "Pacte du grimoire"}


def build_manifestations_2024(db) -> dict[str, dict]:
    """Manifestations 2024 au format de l'app (prérequis de niveau, de pacte et d'autre manifestation analysés)."""
    from .data_loader import PACTS, normalize_manifestation
    cls = db.editions.find("classes", "Occultiste", 2024) or {}
    out = {}
    for o in cls.get("options") or []:
        if "manifestation" not in norm(o.get("categorie", "")):
            continue
        pre = o.get("prerequis") or ""
        lvl = re.search(r"niveau (\d+)", norm(pre))
        pact = ""
        req = re.search(r"manifestation (.+?)(?:,|$)", pre)
        special = ""
        if req:
            target = req.group(1).strip()
            pact = PACT_ALIASES_2024.get(norm(target), target if target in PACTS else "")
            if not pact:
                special = "la manifestation {}".format(target)
        if "tour de magie" in norm(pre):
            special = (special + " ; " if special else "") + "un tour de magie d'occultiste qui inflige des dégâts"
        m = normalize_manifestation({"nom": o["nom"], "categorie": "Niveau {}".format(lvl.group(1)) if lvl else "Communes",
                                     "description": o.get("description", ""), "source": "Manuel des joueurs 2024",
                                     "prerequis": {"niveau": int(lvl.group(1)) if lvl else 0, "pacte": pact,
                                                   "sort": "", "special": special}})
        m.update(edition=2024, prerequis_texte=pre)
        out[o["nom"]] = m
    return out


# noms 2024 -> noms de l'app (les effets calculés sont rattachés au nom)
STYLE_ALIASES_2024 = {"Arme à deux mains": "Armes à deux mains"}


class EditionView:
    """
    Base de données vue par une fiche 2024 : mêmes données que la base, sauf les classes (versions 2024).
    Les méthodes de classe de `Database` sont réutilisées telles quelles sur cette vue.
    """

    def __init__(self, base, classes: dict[str, dict]):
        object.__setattr__(self, "_base", base)
        object.__setattr__(self, "classes", classes)
        object.__setattr__(self, "edition", 2024)

    def __getattr__(self, name):
        return getattr(self._base, name)

    def __setattr__(self, name, value):
        setattr(self._base, name, value)

    def class_names(self) -> list[str]:
        return sorted(self.classes)

    def subclasses(self, class_name: str) -> list[dict]:
        return self.classes.get(class_name, {}).get("sous_classes", [])

    def subclass(self, class_name: str, sub_name: str):
        return next((s for s in self.subclasses(class_name) if s["nom"] == sub_name), None)

    def subclass_tips(self, class_name: str) -> dict[str, str]:
        return {}

    def start_info(self, class_name: str) -> dict:
        from .data_loader import Database
        info = Database.start_info(self, class_name)
        cls = self.classes.get(class_name, {})
        info["pv_initiaux"] = int(cls.get("de_vie", "d8")[1:] or 8)      # 2024 : maximum du dé de vie
        return info

    def table_row(self, class_name: str, level: int) -> dict:
        return (self.classes.get(class_name, {}).get("table_2024") or {}).get(int(level), {})

    @property
    def styles_by_class(self) -> dict[str, dict[str, str]]:
        """2024 : les styles de combat sont les dons « Style de combat » (+ options propres au Paladin et au Rôdeur)."""
        cached = self.__dict__.get("_styles")
        if cached is not None:
            return cached
        base = self._base.styles_by_class
        feats = {STYLE_ALIASES_2024.get(n, n): f.get("description", "") for n, f in self._base.feats.items()
                 if f.get("edition") == 2024 and "style" in norm(str(f.get("categorie", "")))}
        out = {k: dict(v) for k, v in base.items()}
        for cls, extra in (("Guerrier", ()), ("Paladin", ("Combattant béni",)), ("Rôdeur", ("Combattant druidique",))):
            styles = dict(sorted(feats.items()))
            for name in extra:                           # Guerrier béni / Guerrier druidique (option de classe)
                if name in base.get(cls, {}):
                    styles[name] = base[cls][name]
            out[cls] = styles
        object.__setattr__(self, "_styles", out)
        return out

    @property
    def manifestations(self) -> dict[str, dict]:
        """2024 : manifestations occultes de l'Occultiste 2024 (les pactes en font partie)."""
        cached = self.__dict__.get("_manifestations")
        if cached is None:
            cached = build_manifestations_2024(self._base)
            object.__setattr__(self, "_manifestations", cached)
        return cached

    def metamagic_2024(self) -> dict[str, tuple[int, str]]:
        """2024 : options de Métamagie {nom: (coût en points de sorcellerie, description)}."""
        cached = self.__dict__.get("_metamagic")
        if cached is None:
            cls = self._base.editions.find("classes", "Ensorceleur", 2024) or {}
            cached = {}
            for o in cls.get("options") or []:
                if "metamag" not in norm(o.get("categorie", "")):
                    continue
                desc = o.get("description", "")
                m = re.search(r"(\d+)\s+points?\s+de\s+sorcellerie", norm(desc))
                cached[o["nom"]] = (int(m.group(1)) if m else 1, desc)
            object.__setattr__(self, "_metamagic", cached)
        return cached

    def style_description(self, class_name: str, style: str) -> str:
        from .data_loader import Database
        return Database.style_description(self, class_name, style)
