"""
Badge « ✨ Nouveau » (v52) — logique pure mélangée à Engine.

À la montée de niveau, tout ce qui apparaît (tuiles d'action, réactions, aptitudes, sorts) est mémorisé dans
`Character.nouveautes` ; un sort ajouté ensuite dans l'onglet Magie l'est aussi. Le badge disparaît à la première
utilisation (tuile, sort lancé) ou au repos long suivant.
"""
from __future__ import annotations


class NoveltyMixin:
    def snapshot_known(self) -> set[str]:
        keys = {"act:" + a["id"] for a in self.class_actions()}
        keys |= {"reac:" + r["cle"] for r in self.reactions()}
        keys |= {"sort:" + n for n in self.known_spell_names()}
        keys |= {"apt:" + f["nom"] for e in self.ch.classes for f in self.features(e) if f.get("debloque")}
        keys |= {"don:" + n for n in self.chosen_feats()}
        return keys

    def mark_new_since(self, before: set[str]) -> list[str]:
        """Nouveautés = ce qui n'existait pas avant (remplace les nouveautés du niveau précédent)."""
        self.ch.nouveautes = sorted(self.snapshot_known() - set(before))
        return list(self.ch.nouveautes)

    def mark_new(self, key: str) -> None:
        if key not in (self.ch.nouveautes or []):
            self.ch.nouveautes = list(self.ch.nouveautes or []) + [key]

    def is_new(self, key: str) -> bool:
        return key in (self.ch.nouveautes or [])

    def clear_new(self, key: str) -> None:
        if key in (self.ch.nouveautes or []):
            self.ch.nouveautes = [k for k in self.ch.nouveautes if k != key]
