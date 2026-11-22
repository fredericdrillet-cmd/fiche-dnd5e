"""
Journal de session (v52) — logique pure mélangée à Engine.

Événements horodatés (jour de jeu + heure réelle), gardés dans la sauvegarde (`Character.journal`, 500 au plus,
le plus récent en tête) et jamais annulés. Deux sources :
- explicites (`log`) : sorts lancés, repos, niveau gagné ;
- déduites de la fiche avant / après chaque modification (`journal_from_diff`) : dégâts, soins, PV temporaires,
  emplacements et ressources dépensés, états ajoutés ou terminés, concentration.
"""
from __future__ import annotations

import datetime as _dt

from . import effects as FX

MAX_JOURNAL = 500


class JournalMixin:
    """Mélangé à Engine."""

    def log(self, text: str) -> None:
        if not text:
            return
        entry = {"jour": self.time_text(), "heure": _dt.datetime.now().strftime("%d/%m %H:%M"), "texte": text}
        self.ch.journal = ([entry] + list(self.ch.journal or []))[:MAX_JOURNAL]

    def journal_from_diff(self, before: dict, after: dict) -> list[str]:
        out = []
        if not before:
            return out
        pv0, pv1 = int(before.get("pv_actuels", 0)), int(after.get("pv_actuels", 0))
        long_rest = before.get("dernier_repos_long") != after.get("dernier_repos_long")
        if pv1 < pv0:
            out.append("Dégâts : −{} PV ({} → {})".format(pv0 - pv1, pv0, pv1))
        elif pv1 > pv0 and not long_rest:
            out.append("Soins : +{} PV ({} → {})".format(pv1 - pv0, pv0, pv1))
        t0, t1 = int(before.get("pv_temporaires", 0)), int(after.get("pv_temporaires", 0))
        if t1 > t0:
            out.append("PV temporaires : {}".format(t1))
        if long_rest:
            return out                                     # le repos long est journalisé à part
        cast = any(e.get("texte", "").startswith("Sort lancé") for e in (after.get("journal") or [])[:3]
                   if e not in (before.get("journal") or []))
        if not cast:
            for lvl, (a, b) in enumerate(zip(before.get("emplacements_utilises", []),
                                             after.get("emplacements_utilises", [])), 1):
                if int(b) > int(a):
                    out.append("Emplacement de niveau {} dépensé".format(lvl))
            if int(after.get("pacte_utilises", 0)) > int(before.get("pacte_utilises", 0)):
                out.append("Emplacement de pacte dépensé")
        labels = {t["key"]: (t["label"], t.get("total", 0)) for t in self.resource_trackers()}
        r0, r1 = before.get("ressources_utilisees", {}) or {}, after.get("ressources_utilisees", {}) or {}
        for key, used in r1.items():
            if int(used) > int(r0.get(key, 0)) and key in labels:
                label, total = labels[key]
                out.append("{} : {} utilisé(s) ({} / {} restant(s))".format(
                    label, int(used) - int(r0.get(key, 0)), max(0, int(total) - int(used)), total))
        e0, e1 = set(before.get("effets_actifs", [])), set(after.get("effets_actifs", []))
        for k in after.get("effets_actifs", []):
            if k not in e0 and k in FX.EFFECTS:
                out.append("État ou effet : {}".format(FX.EFFECTS[k]["nom"]))
        ended = [FX.EFFECTS[k]["nom"] for k in before.get("effets_actifs", []) if k not in e1 and k in FX.EFFECTS]
        if ended:
            out.append("Fin de : " + ", ".join(ended))
        c0, c1 = before.get("concentration", ""), after.get("concentration", "")
        if c0 and c0 != c1:
            out.append("Concentration terminée : " + c0)
        for a, b in zip(before.get("classes", []), after.get("classes", [])):
            if a.get("nom") == b.get("nom") and int(b.get("niveau", 0)) > int(a.get("niveau", 0)):
                out.append("Niveau gagné : {} {}".format(b["nom"], b["niveau"]))
        return out

    def record_diff(self, before: dict) -> list[str]:
        """Ajoute au journal les événements déduits depuis l'état `before` (dict de la sauvegarde)."""
        events = self.journal_from_diff(before, self.ch.to_dict())
        for text in reversed(events):
            self.log(text)
        return events

    def journal_text(self) -> str:
        return "\n".join("[{}] {} — {}".format(e.get("jour", ""), e.get("heure", ""), e.get("texte", ""))
                         for e in reversed(self.ch.journal or []))
