"""
Recherche rapide (v52, Ctrl+F) — logique pure mélangée à Engine.

`quick_search(texte)` renvoie d'abord ce qui est sur la fiche (sorts, aptitudes, dons, objets, actions, états actifs),
puis les règles de l'édition de la fiche (sorts, dons, objets magiques, états, lexique). Chaque résultat :
{groupe: "fiche" | "regles", type, nom, texte, onglet (clé d'onglet de la fenêtre, "" = fenêtre de détail)}.
"""
from __future__ import annotations

from . import effects as FX
from .rules import norm

MAX_RESULTS = 60


class SearchMixin:
    """Mélangé à Engine."""

    def _edition_ok(self, name: str, item: dict) -> bool:
        ed = int((item or {}).get("edition") or 2014)
        if self.sheet_edition == 2024:
            return ed == 2024 or "(2024)" in name
        return ed != 2024 and "(2024)" not in name

    def _sheet_entries(self) -> list[dict]:
        out = []
        for name in self.known_spell_names() + [s.get("nom", "") for s in self.ch.sorts_mineurs if s.get("nom")]:
            sp = self.db.find_spell(name) or {}
            out.append({"type": "Sort", "nom": name, "texte": sp.get("description", ""), "onglet": "magie"})
        for e in self.ch.classes:
            for f in self.features(e):
                if f.get("debloque"):
                    out.append({"type": "Aptitude ({} {})".format(e["nom"], f.get("niveau", "")), "nom": f["nom"],
                                "texte": f.get("description", ""), "onglet": "classes"})
        for c in self.race_capacities():
            out.append({"type": "Trait d'espèce", "nom": c.get("nom", ""), "texte": c.get("description", ""),
                        "onglet": "race"})
        for feat in self.chosen_feats():
            out.append({"type": "Don", "nom": feat, "texte": self.db.feats.get(feat, {}).get("description", ""),
                        "onglet": "progression"})
        for entry in self.ch.objets_magiques:
            item = self.magic_item(entry.get("nom", "")) or {}
            out.append({"type": "Objet magique", "nom": self.magic_display_name(entry),
                        "texte": item.get("description", ""), "onglet": "inventaire"})
        for it in self.ch.equipement:
            out.append({"type": "Équipement", "nom": it.get("nom", ""), "texte": "Quantité : {}".format(
                it.get("qte", 1)), "onglet": "inventaire"})
        for t in self.turn_actions():
            out.append({"type": "Action ({})".format(t["type"]), "nom": t["nom"], "texte": t.get("description", ""),
                        "onglet": "combat"})
        for k in self.active_effect_keys():
            if k in FX.EFFECTS:
                out.append({"type": "État actif", "nom": FX.EFFECTS[k]["nom"], "texte": self.effect_description(k),
                            "onglet": "combat"})
        return out

    def _rule_entries(self) -> list[dict]:
        out = []
        for name, sp in self.db.spells.items():
            if self._edition_ok(name, sp):
                out.append({"type": "Sort niv. {}".format(sp.get("niveau", 0)) if sp.get("niveau") else
                            "Tour de magie", "nom": name, "texte": sp.get("description", ""), "onglet": ""})
        for name, ft in self.db.feats.items():
            if self._edition_ok(name, ft):
                out.append({"type": "Don", "nom": name, "texte": ft.get("description", ""), "onglet": ""})
        for name, it in getattr(self.db, "magic_items", {}).items():
            out.append({"type": "Objet magique", "nom": name, "texte": it.get("description", ""), "onglet": ""})
        for k, e in FX.EFFECTS.items():
            if e["categorie"] == "État":
                out.append({"type": "État", "nom": e["nom"], "texte": self.effect_description(k), "onglet": ""})
        glossary = getattr(self.db, "glossary", None)
        for t in (glossary.terms if glossary else []):
            out.append({"type": "Lexique", "nom": t["terme"], "texte": glossary.definition(t, self.sheet_edition),
                        "onglet": ""})
        return out

    def quick_search(self, text: str, limit: int = MAX_RESULTS) -> list[dict]:
        q = norm(text or "").strip()
        if len(q) < 2:
            return []
        results = []
        for group, entries in (("fiche", self._sheet_entries()), ("regles", self._rule_entries())):
            scored, seen = [], set()
            for e in entries:
                n = norm(e["nom"])
                if not n or (n, e["type"]) in seen:
                    continue
                if n.startswith(q):
                    rank = 0
                elif q in n:
                    rank = 1
                elif q in norm(e["texte"]):
                    rank = 2
                else:
                    continue
                seen.add((n, e["type"]))
                scored.append((rank, len(n), dict(e, groupe=group)))
            scored.sort(key=lambda x: (x[0], x[1]))
            results += [e for _, _, e in scored]
        sheet = [r for r in results if r["groupe"] == "fiche"][:limit // 2]
        rules = [r for r in results if r["groupe"] == "regles"][:limit - len(sheet)]
        return sheet + rules
