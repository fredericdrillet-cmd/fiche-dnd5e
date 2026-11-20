"""
Manuel d'utilisation (v52) — logique pure, texte dans data/Manuel.json (modifiable sans toucher au code).

Format : {"manuel": {"chapitres": [{"id", "titre", "onglet" (clé d'onglet ou ""), "sections": [{"titre", "texte"}]}]}}
"""
from __future__ import annotations

import html
from typing import Optional

from .rules import norm


class Manual:
    def __init__(self, data: Optional[dict] = None):
        data = data or {}
        self.chapters: list[dict] = [c for c in data.get("chapitres", []) if c.get("id") and c.get("titre")]

    def __bool__(self) -> bool:
        return bool(self.chapters)

    def chapter(self, chapter_id: str) -> Optional[dict]:
        return next((c for c in self.chapters if c["id"] == chapter_id), None)

    def chapter_for_tab(self, tab_key: str) -> Optional[dict]:
        return next((c for c in self.chapters if c.get("onglet") == tab_key), None)

    def search(self, text: str) -> list[tuple[str, str, str]]:
        """[(id du chapitre, titre de section, extrait)] des sections qui contiennent le texte."""
        q = norm(text or "").strip()
        if len(q) < 2:
            return []
        out = []
        for c in self.chapters:
            for s in c.get("sections", []):
                body = s.get("texte", "")
                n = norm(body)
                if q in norm(s.get("titre", "")) or q in n or q in norm(c["titre"]):
                    i = max(0, n.find(q) - 40) if q in n else 0
                    snippet = ("…" if i else "") + body[i:i + 140] + ("…" if len(body) > i + 140 else "")
                    out.append((c["id"], s.get("titre", ""), snippet))
        return out

    def print_html(self) -> str:
        """Manuel complet pour l'export PDF (même style grimoire que la fiche : bandeaux noirs, losanges)."""
        from .sheet_export import CSS, section
        parts = ["<table width='100%' cellspacing='0' cellpadding='6'><tr><td bgcolor='#000000'><font color='#ffffff'>"
                 "<span style='font-size: 20pt; font-weight: bold; font-variant: small-caps'>Manuel d'utilisation"
                 "</span><br/><span style='font-size: 9pt'>Fiche de personnage D&amp;D 5e — éditions 2014 et 2024"
                 "</span></font></td></tr></table>"]
        for c in self.chapters:
            parts.append(section(c["titre"]))
            for s in c.get("sections", []):
                parts.append("<p style='margin: 3px 0'><b>&#9670; {}</b><br/>{}</p>".format(
                    html.escape(s.get("titre", "")), html.escape(s.get("texte", ""))))
        return "<html><head><style>{}</style></head><body>{}</body></html>".format(CSS, "".join(parts))

    def chapter_html(self, chapter_id: str, highlight: str = "") -> str:
        c = self.chapter(chapter_id)
        if c is None:
            return ""
        parts = ["<h2>{}</h2>".format(html.escape(c["titre"]))]
        for s in c.get("sections", []):
            body = html.escape(s.get("texte", ""))
            if highlight and len(highlight.strip()) >= 2:
                q = html.escape(highlight.strip())
                low = body.lower()
                i = low.find(q.lower())
                if i >= 0:
                    body = body[:i] + "<b><u>" + body[i:i + len(q)] + "</u></b>" + body[i + len(q):]
            parts.append("<h3>{}</h3><p>{}</p>".format(html.escape(s.get("titre", "")), body))
        return "".join(parts)
