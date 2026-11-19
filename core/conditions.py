"""
États selon l'édition (v52) — logique pure mélangée à Engine.

- Textes et effets 2024 des états qui ont changé (`CONDITIONS_2024`) : Agrippé (désavantage aux attaques contre
  une autre cible que l'agrippeur), Étourdi (on peut encore se déplacer), Invisible (avantage à l'initiative),
  Neutralisé (désavantage à l'initiative), Inconscient, Paralysé, Pétrifié.
- Neutralisé, Étourdi, Paralysé, Inconscient, Pétrifié : la concentration est rompue (2014 et 2024).
- Caché prend fin quand vous attaquez ou lancez un sort.
- « Se libérer » d'Agrippé / Entravé : 2014 = test simple (meilleur d'Athlétisme et d'Acrobaties), le joueur
  indique s'il l'emporte ; 2024 = test contre le DD indiqué (DD de la prise).
"""
from __future__ import annotations

from . import effects as FX
from . import mechanics as M

INCAPACITATING = ("neutralise", "etourdi", "paralyse", "inconscient", "petrifie")
ESCAPABLE = ("agrippe", "entrave")
ESCAPE_DC_2024 = 15

_FAIL_STR_DEX = {"Force": [M.FAIL], "Dextérité": [M.FAIL]}
CONDITIONS_2024 = {
    "agrippe": {
        "description": "Vitesse 0 (aucun bonus possible). Désavantage aux jets d'attaque contre toute cible autre "
                       "que l'agrippeur. L'agrippeur peut vous déplacer (chaque mètre lui en coûte un de plus). "
                       "Action : test de Force (Athlétisme) ou de Dextérité (Acrobaties) contre le DD de la prise "
                       "pour vous libérer ; l'état prend fin si l'agrippeur est neutralisé ou trop loin.",
        "mech": {"vitesse_mult": 0.0},
        "notes": ["Attaques contre une autre cible que l'agrippeur : désavantage",
                  "Se libérer : Athlétisme ou Acrobaties contre le DD de la prise"]},
    "entrave": {
        "description": "Vitesse 0. Désavantage à vos jets d'attaque et à vos JS de Dextérité ; les attaques "
                       "contre vous ont l'avantage.",
        "mech": {"attaque": [M.DIS], "js": {"Dextérité": [M.DIS]}, "vitesse_mult": 0.0}},
    "etourdi": {
        "description": "Vous êtes Neutralisé (ni action, ni action bonus, ni réaction ; concentration rompue). "
                       "Échec automatique aux JS de Force et de Dextérité ; les attaques contre vous ont "
                       "l'avantage. Vous pouvez encore vous déplacer.",
        "mech": {"js": _FAIL_STR_DEX},
        "notes": ["Neutralisé", "Attaques contre vous : avantage"]},
    "neutralise": {
        "description": "Ni action, ni action bonus, ni réaction ; concentration rompue ; vous ne pouvez pas parler. "
                       "Si vous êtes neutralisé quand vous lancez l'initiative, vous avez le désavantage.",
        "mech": {"initiative": "désavantage"},
        "notes": ["Aucune action, action bonus ni réaction", "Désavantage à l'initiative"]},
    "inconscient": {
        "description": "Neutralisé et À terre, vitesse 0, vous lâchez ce que vous tenez. Échec automatique aux JS "
                       "de Force et de Dextérité ; attaques contre vous avec avantage, et coup critique si "
                       "l'attaquant est à 1,50 m.",
        "mech": {"js": _FAIL_STR_DEX, "vitesse_mult": 0.0, "initiative": "désavantage"}},
    "paralyse": {
        "description": "Neutralisé, vitesse 0. Échec automatique aux JS de Force et de Dextérité ; attaques contre "
                       "vous avec avantage, et coup critique si l'attaquant est à 1,50 m.",
        "mech": {"js": _FAIL_STR_DEX, "vitesse_mult": 0.0, "initiative": "désavantage"}},
    "petrifie": {
        "description": "Changé en substance inanimée (poids ×10, vous ne vieillissez plus). Neutralisé, vitesse 0, "
                       "échec automatique aux JS de Force et de Dextérité, attaques contre vous avec avantage. "
                       "Résistance à tous les dégâts, immunité à l'état Empoisonné.",
        "mech": {"js": _FAIL_STR_DEX, "vitesse_mult": 0.0, "resistances": ["tous les dégâts"],
                 "initiative": "désavantage"}},
    "invisible": {
        "description": "Avantage à l'initiative. Vous n'êtes pas affecté par ce qui demande de vous voir (sauf si "
                       "la créature vous voit). Vos jets d'attaque ont l'avantage ; ceux contre vous ont le "
                       "désavantage, sauf si l'attaquant vous voit.",
        "mech": {"attaque": [M.ADV], "initiative": "avantage"}},
    "cache": {
        "description": "Caché (action Se cacher réussie, DD 15) : vous avez l'état Invisible ; il prend fin si "
                       "vous faites du bruit, attaquez, lancez un sort à composante verbale ou êtes trouvé.",
        "mech": {"attaque": [M.ADV], "initiative": "avantage"}},
}


class ConditionsMixin:
    """Mélangé à Engine."""

    last_effect_message = ""                             # message du dernier add_effect (concentration rompue…)

    def condition_mech(self, key: str) -> dict:
        """Mécanique d'un effet selon l'édition de la fiche."""
        if self.sheet_edition == 2024 and key in CONDITIONS_2024:
            return CONDITIONS_2024[key]["mech"]
        return M.mech(key)

    def effect_description(self, key: str) -> str:
        if self.sheet_edition == 2024 and key in CONDITIONS_2024:
            return CONDITIONS_2024[key]["description"]
        return FX.EFFECTS.get(key, {}).get("description", "")

    def effect_tooltip(self, key: str, accent: str = "") -> str:
        """Infobulle d'un effet : texte 2024 des états qui ont changé."""
        tip = FX.tooltip_html(key, accent)
        if self.sheet_edition == 2024 and key in CONDITIONS_2024:
            import html
            old = html.escape(FX.EFFECTS[key]["description"])
            info = CONDITIONS_2024[key]
            tip = tip.replace(old, html.escape(info["description"]) + " <i>(règle 2024)</i>")
            if "notes" in info:
                import re
                items = "".join("<li>{}</li>".format(html.escape(n)) for n in info["notes"])
                tip = re.sub(r"<ul style='[^']*'>.*?</ul>", lambda _m: "<ul style='margin:2px 0 0 -20px'>{}</ul>"
                             .format(items), tip, count=1, flags=re.S)
        return tip

    def condition_initiative(self) -> tuple[list[str], list[str]]:
        """(avantage, désavantage) à l'initiative dus aux états (2024 : Invisible, Neutralisé…)."""
        adv, dis = [], []
        if self.sheet_edition != 2024:
            return adv, dis
        for k in self.active_effect_keys():
            mode = CONDITIONS_2024.get(k, {}).get("mech", {}).get("initiative")
            if mode == "avantage":
                adv.append(FX.EFFECTS[k]["nom"])
            elif mode == "désavantage":
                dis.append(FX.EFFECTS[k]["nom"])
        return adv, dis

    # ------------------------------------------------------------------ neutralisé : concentration rompue
    def incapacitation_breaks(self, key: str) -> str:
        """Appelé à l'ajout d'un état : un état neutralisant rompt la concentration (2014 et 2024)."""
        if key in INCAPACITATING and self.ch.concentration:
            old = self.break_concentration()
            return "Concentration rompue ({}) : {} prend fin.".format(FX.EFFECTS[key]["nom"], old)
        return ""

    # ------------------------------------------------------------------ Caché
    def reveal_after_attack(self) -> str:
        """Attaquer ou lancer un sort met fin à l'état Caché."""
        if "cache" in self.ch.effets_actifs:
            self.remove_effect("cache")
            return "Vous n'êtes plus caché."
        return ""

    # ------------------------------------------------------------------ Se libérer
    def escape_conditions(self) -> list[str]:
        return [k for k in ESCAPABLE if k in self.active_effect_keys()]

    def escape_skill(self) -> str:
        """Meilleur bonus entre Athlétisme et Acrobaties."""
        rows = {r["nom"]: r for r in self.skill_rows()}
        return max(("Athlétisme", "Acrobaties"), key=lambda s: rows[s]["bonus"] if s in rows else -99)

    def resolve_escape(self, key: str, success: bool, total: int = 0, dc: int = 0) -> str:
        name = FX.EFFECTS[key]["nom"]
        detail = " ({} contre DD {})".format(total, dc) if dc else ""
        if success:
            self.remove_effect(key)
            return "Libéré{} : vous n'êtes plus {}.".format(detail, name.lower())
        return "Toujours {}{}.".format(name.lower(), detail)
