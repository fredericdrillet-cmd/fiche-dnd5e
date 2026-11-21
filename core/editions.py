"""
Éditions de règles (v52) : mode 2014, 2024 ou libre, filtrage des données et multiclassage inter-éditions.

Logique pure (aucune dépendance à l'interface), utilisée par le moteur, l'application bureau et la version web.

- **Modes** : « 2014 » (contenu 2014 seul), « 2024 » (contenu 2024 seul) et « libre » (les deux éditions, avec un
  badge d'édition à l'affichage). Le mode est enregistré dans chaque personnage (`Character.edition_mode`) ; la
  valeur par défaut des nouveaux personnages vient des préférences.
- **Édition d'un élément** : champ `edition` (2014 / 2024) des nouveaux fichiers de `data/editions/`. Les
  anciennes données de `data/*.json` n'ont pas ce champ : elles valent 2014.
- **Catalogue** : `EditionCatalog` lit les fichiers de `data/editions/` à la demande et les filtre selon le mode.
- **Multiclassage** : chaque entrée de classe porte son édition. En 2014, un demi-incantateur (Paladin, Rôdeur)
  compte pour la moitié de ses niveaux arrondie à l'inférieur ; en 2024, arrondie au supérieur, et il lance des
  sorts dès le niveau 1. Les tiers d'incantateur (Chevalier occulte, Escroc arcanique) arrondissent à l'inférieur
  dans les deux éditions ; l'Artificier (2014 seulement) arrondit au supérieur.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable, Optional

from . import rules as R

MODE_2014, MODE_2024, MODE_LIBRE = "2014", "2024", "libre"
MODES: dict[str, str] = {
    MODE_2014: "Édition 2014 uniquement",
    MODE_2024: "Édition 2024 uniquement",
    MODE_LIBRE: "Libre (2014 et 2024 combinées)",
}
MODE_HELP: dict[str, str] = {
    MODE_2014: "Seuls les classes, sorts, dons, historiques, races et objets de l'édition 2014 sont proposés.",
    MODE_2024: "Seul le contenu de l'édition 2024 est proposé.",
    MODE_LIBRE: "Tout le contenu est proposé, avec un badge « 2014 » ou « 2024 ». Un personnage peut combiner des "
                "classes des deux éditions (par exemple Guerrier 2024 et Roublard 2014).",
}
DEFAULT_MODE = MODE_2014
EDITIONS = (2014, 2024)
DEFAULT_EDITION = 2014


# --------------------------------------------------------------------------------------------- modes et éditions
def normalize_mode(value: Any) -> str:
    """Valeur enregistrée -> mode reconnu (« 2014 », « 2024 », « libre ») ; inconnu -> 2014."""
    text = str(value or "").strip().lower()
    if text in ("libre", "hybride", "mixte", "free", "both"):
        return MODE_LIBRE
    if text.startswith("2024"):
        return MODE_2024
    return MODE_2014 if text.startswith("2014") or not text else DEFAULT_MODE


def editions_of_mode(mode: str) -> frozenset[int]:
    """Éditions autorisées par un mode."""
    mode = normalize_mode(mode)
    if mode == MODE_LIBRE:
        return frozenset(EDITIONS)
    return frozenset({int(mode)})


def item_edition(item: Any, default: int = DEFAULT_EDITION) -> int:
    """Édition d'un élément (dict avec `edition`, ou un entier / texte). Sans indication : 2014."""
    raw = item.get("edition") if isinstance(item, dict) else item
    try:
        value = int(str(raw).strip()[:4])
    except (TypeError, ValueError):
        return default
    return value if value in EDITIONS else default


def allowed(item: Any, mode: str) -> bool:
    """L'élément est-il autorisé dans ce mode ?"""
    return item_edition(item) in editions_of_mode(mode)


def filter_items(items: Iterable[Any], mode: str, dedupe: bool = True) -> list:
    """
    Garde les éléments autorisés par le mode. `dedupe` écarte les réimpressions (`doublon_de` : même élément paru
    dans un autre livre de la même édition) pour ne proposer qu'une seule fois chaque choix.
    """
    eds = editions_of_mode(mode)
    out = []
    for it in items:
        if item_edition(it) not in eds:
            continue
        if dedupe and isinstance(it, dict) and it.get("doublon_de"):
            continue
        out.append(it)
    return out


def badge(item: Any, mode: str) -> str:
    """Badge d'édition à afficher : « 2014 » ou « 2024 » en mode libre, rien sinon (une seule édition visible)."""
    return str(item_edition(item)) if normalize_mode(mode) == MODE_LIBRE else ""


def label(name: str, item: Any, mode: str) -> str:
    """Nom suivi de son badge d'édition en mode libre : « Guerrier [2024] »."""
    b = badge(item, mode)
    return "{} [{}]".format(name, b) if b else name


# --------------------------------------------------------------------------------------------- catalogue
CATALOG_FILES: dict[str, str] = {
    "classes_fr.json": "classes", "sorts_fr.json": "sorts", "dons_fr.json": "dons",
    "historiques_fr.json": "historiques", "races_fr.json": "races", "objets_magiques_fr.json": "objets",
    "equipement_fr.json": "*", "sorts_par_classe_fr.json": "-", "tables_fr.json": "tables",
}
# sections de classes_fr.json ; « * » : toutes les listes du fichier (équipement) ; « - » : index (pas de liste)
CLASS_SECTIONS = ("classes", "sous_classes", "supplements_de_classe")


class EditionCatalog:
    """
    Données de référence par édition (dossier `data/editions/`), chargées à la demande.

        cat = EditionCatalog(get_resource_path("data") / "editions")
        cat.list("sorts", "2024")                      # sorts de l'édition 2024 (sans réimpressions)
        cat.list("sous_classes", "libre", classe="Guerrier")
        cat.get("classe-fighter-2024-phb24")
    """

    def __init__(self, root: Path | str):
        self.root = Path(root)
        self._kinds: Optional[dict[str, list[dict]]] = None
        self._by_id: dict[str, dict] = {}
        self._spell_index: dict = {}
        self.warnings: list[str] = []

    # ---------------------------------------------------------------- chargement
    def available(self) -> bool:
        return self.root.is_dir() and any(self.root.glob("*.json"))

    def _load(self) -> dict[str, list[dict]]:
        if self._kinds is not None:
            return self._kinds
        kinds: dict[str, list[dict]] = {}
        for fname, key in CATALOG_FILES.items():
            path = self.root / fname
            if not path.is_file():
                continue
            try:
                with open(path, encoding="utf-8") as fh:
                    data = json.load(fh)
            except (OSError, json.JSONDecodeError) as exc:
                self.warnings.append("{} illisible : {}".format(fname, exc))
                continue
            if key == "-":
                self._spell_index = data if isinstance(data, dict) else {}
            elif key == "*":
                for section, value in data.items():
                    if isinstance(value, list):
                        kinds[section] = value
            elif key == "classes":
                for section in CLASS_SECTIONS:
                    kinds[section] = list(data.get(section, []))
            else:
                kinds[key] = list(data.get(key, []))
        for items in kinds.values():
            for it in items:
                if isinstance(it, dict) and it.get("id"):
                    self._by_id[it["id"]] = it
        self._kinds = kinds
        return kinds

    # ---------------------------------------------------------------- accès
    def kinds(self) -> list[str]:
        return sorted(self._load())

    def items(self, kind: str) -> list[dict]:
        return self._load().get(kind, [])

    def get(self, item_id: str) -> Optional[dict]:
        self._load()
        return self._by_id.get(item_id)

    def list(self, kind: str, mode: str, dedupe: bool = True, **filters: Any) -> list[dict]:
        """
        Éléments d'un type autorisés par le mode. Filtres simples sur un champ : `classe="Guerrier"`,
        `niveau=3`, `categorie="Origine"`… (comparaison exacte ; pour une liste, appartenance).
        """
        out = []
        for it in filter_items(self.items(kind), mode, dedupe):
            ok = True
            for field, wanted in filters.items():
                value = it.get(field)
                ok = wanted in value if isinstance(value, list) else value == wanted
                if not ok:
                    break
            if ok:
                out.append(it)
        return out

    def find(self, kind: str, name: str, edition: Optional[int] = None) -> Optional[dict]:
        """Élément par nom français ou anglais (insensible aux accents), d'une édition donnée si précisée."""
        target = R.norm(name)
        for it in self.items(kind):
            if edition is not None and item_edition(it) != edition:
                continue
            if target in (R.norm(it.get("nom", "")), R.norm(it.get("nom_en", ""))):
                return it
        return None

    def counts(self) -> dict[str, dict[int, int]]:
        """Nombre d'éléments par type et par édition (affiché dans « À propos »)."""
        out: dict[str, dict[int, int]] = {}
        for kind, items in self._load().items():
            per: dict[int, int] = {}
            for it in items:
                if isinstance(it, dict) and "edition" in it:
                    per[item_edition(it)] = per.get(item_edition(it), 0) + 1
            if per:
                out[kind] = per
        return out

    # ---------------------------------------------------------------- liens
    def subclasses_of(self, class_name: str, mode: str, edition: Optional[int] = None) -> list[dict]:
        """Sous-classes d'une classe (nom français), filtrées par mode et, si précisé, par édition de la classe."""
        subs = self.list("sous_classes", mode, classe=class_name)
        return [s for s in subs if edition is None or item_edition(s) == edition]

    def spells_for_class(self, class_id: str, mode: str) -> list[dict]:
        """Sorts accessibles à une classe (identifiant `classe-…`), filtrés par mode."""
        return [s for s in self.list("sorts", mode) if class_id in (s.get("classe_ids") or [])]


# --------------------------------------------------------------------------------------------- multiclassage
def caster_index(kind: str, level: int, edition: int = DEFAULT_EDITION) -> int:
    """Niveau d'incantateur d'une classe seule. 2024 : les demi-incantateurs lancent des sorts dès le niveau 1."""
    if kind == "half" and item_edition(edition) == 2024:
        return math.ceil(level / 2)
    return R.caster_index(kind, level)


def multiclass_caster_level(kind: str, level: int, edition: int = DEFAULT_EDITION) -> int:
    """Contribution d'une classe au niveau d'incantateur combiné, selon l'édition de CETTE classe."""
    if kind == "half" and item_edition(edition) == 2024:
        return math.ceil(level / 2)
    return R.multiclass_caster_level(kind, level)


def spell_slots(casters: list[tuple]) -> list[int]:
    """
    Emplacements de sorts (hors Magie des pactes) pour des entrées (kind, niveau) ou (kind, niveau, édition).
    Une seule classe incantatrice : sa propre table ; plusieurs : niveau combiné, chaque classe selon son édition.
    """
    entries = [(c[0], c[1], c[2] if len(c) > 2 else DEFAULT_EDITION) for c in casters]
    active = [e for e in entries if e[0] != "pact" and caster_index(*e) > 0]
    if not active:
        return [0] * 9
    idx = caster_index(*active[0]) if len(active) == 1 else sum(multiclass_caster_level(*e) for e in active)
    idx = max(0, min(R.MAX_LEVEL, idx))
    slots = list(R._FULL_SLOTS[idx - 1]) if idx else []
    return slots + [0] * (9 - len(slots))


def min_casting_level(kind: str, default_min: int, edition: int) -> int:
    """Niveau à partir duquel une classe lance des sorts (2024 : demi-incantateurs dès le niveau 1)."""
    return 1 if kind == "half" and item_edition(edition) == 2024 else default_min


def validate_classes(classes: list[dict], mode: str) -> list[str]:
    """
    Problèmes d'édition des classes d'un personnage, sous forme de messages (liste vide = tout est cohérent) :
    une classe hors du mode actif, ou la même classe prise dans deux éditions différentes.
    """
    problems: list[str] = []
    eds = editions_of_mode(mode)
    seen: dict[str, int] = {}
    for entry in classes:
        name = entry.get("nom", "")
        ed = item_edition(entry)
        if ed not in eds:
            problems.append("{} ({}) n'est pas autorisé en mode « {} ».".format(name, ed, MODES[normalize_mode(mode)]))
        if name in seen and seen[name] != ed:
            problems.append("{} est présent en édition {} et {} : une même classe ne peut venir que d'une "
                            "édition.".format(name, seen[name], ed))
        seen.setdefault(name, ed)
    return problems
