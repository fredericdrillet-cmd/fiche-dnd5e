"""
Lexique des règles (v52) — `data/Lexique.json`, logique pure.

Chaque terme a une définition courte et, s'il y a lieu, sa variante 2014 / 2024. `Glossary.find(text)` repère les
termes d'un texte (mots entiers, accents et majuscules ignorés, expressions les plus longues d'abord) ; l'interface
s'en sert pour compléter les infobulles et, avec l'option « Aides pour débuter », souligner les mots dans les textes.
"""
from __future__ import annotations

import re
from typing import Optional

from .rules import norm


class Glossary:
    def __init__(self, data: Optional[dict] = None):
        data = data or {}
        self.terms: list[dict] = [t for t in data.get("termes", []) if t.get("terme")]
        self.tab_help: dict[str, str] = dict(data.get("aides_onglets", {}))
        self.step_help: dict[str, str] = dict(data.get("aides_creation", {}))
        self._by_name = {norm(t["terme"]): t for t in self.terms}
        forms = []
        for t in self.terms:
            if not t.get("auto", True):
                continue
            for f in [t["terme"]] + list(t.get("variantes", [])):
                forms.append((norm(f).replace("’", "'"), t))
        forms.sort(key=lambda ft: -len(ft[0]))
        self._forms = {f: t for f, t in forms}
        self._rx = re.compile(r"(?<![\w-])(" + "|".join(re.escape(f) for f, _ in forms) + r")(?![\w-])") \
            if forms else None

    def __bool__(self) -> bool:
        return bool(self.terms)

    def get(self, name: str) -> Optional[dict]:
        return self._by_name.get(norm(name))

    def categories(self) -> list[str]:
        return list(dict.fromkeys(t.get("categorie", "") for t in self.terms))

    def search(self, text: str) -> list[dict]:
        q = norm(text or "")
        if not q:
            return list(self.terms)
        return [t for t in self.terms if q in norm(" ".join([t["terme"], t.get("definition", ""),
                                                             t.get("2014", ""), t.get("2024", "")] +
                                                            list(t.get("variantes", []))))]

    def spans(self, text: str) -> list[tuple[int, int, dict]]:
        """Positions (début, fin, terme) des termes trouvés dans `text` (norm() garde la longueur du texte)."""
        if not self._rx or not text:
            return []
        n = norm(text).replace("’", "'")
        if len(n) != len(text):                          # normalisation qui change la longueur : pas de surlignage
            return [(0, 0, self._forms[m.group(1)]) for m in self._rx.finditer(n)]
        return [(m.start(), m.end(), self._forms[m.group(1)]) for m in self._rx.finditer(n)]

    def find(self, text: str, limit: int = 3) -> list[dict]:
        out = []
        for _, _, t in self.spans(text):
            if t not in out:
                out.append(t)
            if len(out) >= limit:
                break
        return out

    @staticmethod
    def definition(term: dict, edition: int = 0) -> str:
        """Définition, avec la précision de l'édition de la fiche (ou des deux éditions si edition = 0)."""
        text = term.get("definition", "")
        notes = []
        for ed in (2014, 2024):
            if term.get(str(ed)) and edition in (0, ed):
                notes.append(("{} : ".format(ed) if edition == 0 else "") + term[str(ed)])
        return text + (" " + " ".join(notes) if notes else "")
