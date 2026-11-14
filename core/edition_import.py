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
