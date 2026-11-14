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
    "Lance psychique de Raulothim", "Glace entravante de Rime", "Piques argentées", "Châtiment de stupeur",
    "Invocation d'esprit draconique", "Préméditation", "Rafale de vent")}

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
             "armes": 0}
    if not cat.available():
        return stats
    _merge_spells(db, cat, stats)
    _merge_feats(db, cat, stats)
    _merge_backgrounds(db, cat, stats)
    _merge_subclasses(db, cat, stats)
    _merge_species(db, cat, stats)
    _merge_weapons(db, cat, stats)
    db._spell_index = {norm(n): n for n in db.spells}
    return stats


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
            if sp.get("test") and not sp.get("js_succes"):
                sp["js_succes"] = "aucun" if int(sp.get("niveau") or 0) == 0 else "moitie"
            db.spells[sp["nom"]] = sp
            stats["sorts"] += 1


def _merge_feats(db, cat, stats):
    from .data_loader import normalize_feat
    present = {norm(n) for n in db.feats}
    for f in cat.list("dons", "2014"):
        en = f.get("nom_en", "")
        if norm(f.get("categorie", "")) and any(x in norm(f.get("categorie", "")) for x in FEAT_CATEGORIES_EXCLUDED):
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


def _expand_features(c: dict) -> list[dict]:
    """Aptitudes niveau par niveau d'après la colonne « capacites » de la table (améliorations répétées comprises)."""
    feats = c.get("capacites") or []
    by_name = {norm(f.get("nom", "")): f for f in feats}
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

    def style_description(self, class_name: str, style: str) -> str:
        from .data_loader import Database
        return Database.style_description(self, class_name, style)
