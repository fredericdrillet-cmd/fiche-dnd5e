"""
Manifestations occultes (Eldritch Invocations) et règles chiffrées des sorts — répercussions sur la fiche (v37).

Mélangé à `Engine`. Chaque manifestation porte des « effets » (data/Manifestations_occultes.json, écrit par
tools/invocation_fixes.py) lus ici :

  decharge:*            tuile / encart de Décharge occulte (Combat) : +mod. CHA par rayon, 90 m, poussée, attraction,
                        ralentissement ;
  armure_mage           Armure de mage à volonté sur soi (Magie) -> effet « Armure du mage » et CA 13 + Dex ;
  vision_diable         encart Vision (Combat) : 36 m, ténèbres magiques comprises ;
  competence:X          maîtrise de compétence (Compétences) ;
  attaques:2            Lame assoiffée : 2 attaques par action Attaquer ;
  arme_pacte:*          bonus de l'arme de pacte (encart des capacités passives) ;
  nage / livre_rituels / action:* …  vitesse de nage, Livre des secrets anciens, actions et réactions du Combat.

Les sorts accordés (« sorts ») sont injectés dans l'onglet Magie avec leur usage : à volonté, ou 1 fois par repos long
(avec ou sans emplacement d'occultiste) suivi par un compteur interne.
"""
from __future__ import annotations

import math
import re
from typing import Optional

from . import rules as R
from .rules import norm

ELDRITCH_BLAST = "Décharge occulte"
HEX = "Maléfice"
MANIF_RENAMES = {"Etreinte de Hadar": "Étreinte de Hadar"}     # anciennes sauvegardes (accent manquant)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", norm(text)).strip("_")


class InvocationsMixin:
    # ------------------------------------------------------------------ prérequis
    def knows_spell(self, name: str) -> bool:
        """Sort appris dans une liste de classe (sans passer par les sorts accordés : pas de récursion)."""
        n = norm(name)
        return any(norm(s.get("nom", "")) == n for lst in self.ch.sorts.values() for s in lst)

    def has_curse_feature(self) -> bool:
        """Sort Maléfice connu, ou aptitude d'occultiste qui maudit (Malédiction de la Lame maudite)."""
        if self.knows_spell(HEX):
            return True
        e = self.ch.find_class("Occultiste")
        return bool(e and "lame maudite" in norm(e.get("sous_classe", "")))

    def invocation_prereq_issue(self, m: dict) -> str:
        """Prérequis de sort ou condition spéciale non remplis : raison (vide si tout va bien)."""
        if m.get("sort_requis") and not self.knows_spell(m["sort_requis"]):
            return "requiert le sort mineur {}".format(m["sort_requis"])
        if m.get("special") and "malefice" in norm(m["special"]) and not self.has_curse_feature():
            return "requiert le sort Maléfice ou une aptitude de malédiction"
        req = re.search(r"la manifestation (.+?)(?: ;|$)", m.get("special") or "")      # v52 : prérequis 2024
        if req and req.group(1).strip() not in self.ch.manifestations:
            return "requiert la manifestation {}".format(req.group(1).strip())
        return ""

    def migrate_manifestations(self) -> None:
        self.ch.manifestations = [MANIF_RENAMES.get(n, n) for n in self.ch.manifestations]

    # ------------------------------------------------------------------ manifestations actives
    def active_invocations(self) -> list[dict]:
        return [self.db.manifestations[n] for n in self.ch.manifestations
                if n in self.db.manifestations and self.manifestation_status(n)[0] == "ok"]

    def invocation_effects(self) -> set[str]:
        return {fx for m in self.active_invocations() for fx in m.get("effets", [])}

    def has_invocation(self, name: str) -> bool:
        return any(norm(m["nom"]) == norm(name) for m in self.active_invocations())

    # ------------------------------------------------------------------ Décharge occulte
    def eldritch_blast_bonus(self) -> dict:
        """
        Effets des manifestations sur Décharge occulte (tuile du Combat, encart des sorts mineurs) :
        {plat, plat_source, portee, effets: [texte court par rayon], notes: [texte complet]}.
        """
        fx = self.invocation_effects()
        cha = self.mod("Charisme")
        effets = []
        if "decharge:repousse" in fx:
            effets.append("Décharge répulsive : repousse la cible de 3 m en ligne droite à chaque rayon qui touche")
        if "decharge:attire" in fx:
            effets.append("Étreinte de Hadar : attire la cible de 3 m vers vous (1 fois par tour)")
        if "decharge:ralentit" in fx:
            effets.append("Lance de léthargie : vitesse de la cible −3 m jusqu'à la fin de votre prochain tour "
                          "(1 fois par tour)")
        notes = ["{} : {}".format(m["nom"], m["description"]) for m in self.active_invocations()
                 if any(x.startswith("decharge:") for x in m.get("effets", []))]
        return {"plat": cha if "decharge:plat_cha" in fx else 0,
                "plat_source": "Décharge déchirante (modificateur de Charisme)" if "decharge:plat_cha" in fx else "",
                "portee": "90 m" if "decharge:portee" in fx else "", "effets": effets, "notes": notes}

    # ------------------------------------------------------------------ sens, compétences, vitesse, attaques
    def devils_sight(self) -> bool:
        return "vision_diable" in self.invocation_effects()

    def invocation_skills(self) -> set[str]:
        return {fx.split(":", 1)[1] for fx in self.invocation_effects() if fx.startswith("competence:")}

    def swim_speed(self) -> float:
        """Vitesse de nage accordée (Don des profondeurs : égale à la vitesse de marche), 0 sinon."""
        return self.speed() if "nage" in self.invocation_effects() else 0.0

    def thirsting_blade(self) -> bool:
        return "attaques:2" in self.invocation_effects()

    def concentration_advantage(self) -> list[str]:
        return ["Esprit occulte"] if "concentration_avantage" in self.invocation_effects() else []

    # ------------------------------------------------------------------ sorts accordés : limites d'usage
    @staticmethod
    def grant_key(manifestation: str, spell: str) -> str:
        return "manif:" + _slug(manifestation) + ":" + _slug(spell)

    def granted_limit_left(self, key: str) -> Optional[int]:
        """Utilisations restantes d'un sort accordé limité (None = à volonté)."""
        tr = next((t for t in self.invocation_trackers() if t["key"] == key), None)
        return None if tr is None else max(0, tr["total"] - self.resource_used(key))

    def spend_granted_limit(self, key: str) -> None:
        if key and self.granted_limit_left(key) is not None:
            self.set_resource_used(key, self.resource_used(key) + 1)

    # ------------------------------------------------------------------ Livre des secrets anciens
    def ritual_book_active(self) -> bool:
        return "livre_rituels" in self.invocation_effects()

    def ritual_book_max_level(self) -> int:
        """Rituels recopiables : niveau ≤ moitié du niveau d'occultiste (arrondie au supérieur), au moins 1."""
        return max(1, math.ceil(self.class_level("Occultiste") / 2))

    def ritual_book_options(self) -> list[dict]:
        """Rituels inscriptibles (toutes listes de classe) — les 2 premiers doivent être de niveau 1."""
        top = self.ritual_book_max_level()
        return sorted((s for s in self.db.spells.values() if s.get("rituel") and 1 <= s["niveau"] <= top
                       and s.get("classes")), key=lambda s: (s["niveau"], norm(s["nom"])))

    def ritual_book_missing(self) -> int:
        """Nombre de rituels de niveau 1 encore à choisir (2 offerts par la manifestation)."""
        if not self.ritual_book_active():
            return 0
        lvl1 = [n for n in self.ch.rituels_livre if (self.db.find_spell(n) or {}).get("niveau") == 1]
        return max(0, 2 - len(lvl1))

    def ritual_book_can_add(self, name: str) -> tuple[bool, str]:
        spell = self.db.find_spell(name)
        if not self.ritual_book_active():
            return False, "Manifestation « Livre des secrets anciens » non choisie."
        if not spell or not spell.get("rituel"):
            return False, "Seuls les sorts possédant l'étiquette rituel peuvent être inscrits."
        if spell["nom"] in self.ch.rituels_livre:
            return False, "Déjà inscrit dans le Livre des ombres."
        if self.ritual_book_missing() > 0 and spell["niveau"] != 1:
            return False, "Choisissez d'abord les deux rituels de niveau 1 offerts par la manifestation."
        if spell["niveau"] > self.ritual_book_max_level():
            return False, "Niveau {} maximum (moitié du niveau d'occultiste, arrondie au supérieur).".format(
                self.ritual_book_max_level())
        return True, ""

    def add_ritual(self, name: str) -> bool:
        ok, _ = self.ritual_book_can_add(name)
        if ok:
            self.ch.rituels_livre.append(self.db.find_spell(name)["nom"])
        return ok

    def remove_ritual(self, name: str) -> None:
        self.ch.rituels_livre = [n for n in self.ch.rituels_livre if n != name]

    def sanitize_ritual_book(self) -> None:
        if not self.ritual_book_active():
            return                                       # conservé : la manifestation peut revenir (pacte rechoisi)
        top, seen, out = self.ritual_book_max_level(), set(), []
        for n in self.ch.rituels_livre:
            sp = self.db.find_spell(n)
            if sp and sp.get("rituel") and 1 <= sp["niveau"] <= top and sp["nom"] not in seen:
                seen.add(sp["nom"])
                out.append(sp["nom"])
        self.ch.rituels_livre = out

    def ritual_book_spells(self) -> list[dict]:
        if not self.ritual_book_active():
            return []
        out = []
        for n in self.ch.rituels_livre:
            sp = self.db.find_spell(n)
            if sp:
                out.append({"nom": sp["nom"], "niveau": sp["niveau"], "usage": "Rituel uniquement (+10 minutes)",
                            "source": "Livre des secrets anciens", "sort": sp, "categorie": "Manifestations occultes",
                            "emplacement": False, "limite": "", "cle": "", "rituel_seul": True})
        return out

    # ------------------------------------------------------------------ compteurs, actions, passifs
    @staticmethod
    def _inv_tracker(key: str, label: str, total: int, recover: str, info: str, kind: str = "conduit",
                     where: str = "combat") -> dict:
        return {"key": key, "label": label, "total": total, "kind": kind, "recover": recover, "info": info,
                "where": where, "de": ""}

    def invocation_trackers(self) -> list[dict]:
        out = []
        pb = self.prof
        for m in self.active_invocations():
            fx = m.get("effets", [])
            for g in m["sorts"]:
                if g.get("limite"):
                    out.append(self._inv_tracker(self.grant_key(m["nom"], g["sort"]), "{} ({})".format(
                        g["sort"], m["nom"]), 1, g["limite"], g["usage"], where="interne"))
            if "action:tombe_levistus" in fx:
                out.append(self._inv_tracker("inv:tombe_levistus", "Tombe de Levistus", 1, "repos court",
                                             "1 utilisation — récupérée au repos court ou long", kind="sursaut"))
            if "action:voile_mouches" in fx:
                out.append(self._inv_tracker("inv:voile_mouches", "Voile de mouches", 1, "repos court",
                                             "1 utilisation — récupérée au repos court ou long", kind="sursaut"))
            if "action:regard_fantomatique" in fx:
                out.append(self._inv_tracker("inv:regard_fantomatique", "Regard fantomatique", 1, "repos court",
                                             "1 utilisation — récupérée au repos court ou long", kind="sens"))
            if "action:present_sauveurs" in fx:
                out.append(self._inv_tracker("inv:present_sauveurs", "Présent des sauveurs", 1, "repos long",
                                             "1 déclenchement — récupéré au repos long", kind="sens"))
            if "action:protection_talisman" in fx:
                out.append(self._inv_tracker("inv:protection_talisman", "Protection du talisman", pb, "repos long",
                                             "Bonus de maîtrise ({}) utilisations — repos long".format(pb)))
            if "action:lien_talisman" in fx:
                out.append(self._inv_tracker("inv:lien_talisman", "Lien du talisman", pb, "repos long",
                                             "Bonus de maîtrise ({}) utilisations — repos long".format(pb)))
        return out

    def invocation_short_rest_keys(self) -> list[str]:
        return [t["key"] for t in self.invocation_trackers() if t["recover"] == "repos court"]

    def _inv_act(self, aid: str, nom: str, icone: str, kind: str, desc: str, cost: Optional[dict] = None,
                 degats: str = "", type_degats: str = "", niveau: int = 1, **extra) -> dict:
        return dict({"id": aid, "nom": nom, "icone": icone, "classe": "Occultiste", "sous_classe": "",
                     "niveau": niveau, "type": kind, "cout": cost or {}, "jet": "degats" if degats else "aucun",
                     "degats": degats, "type_degats": type_degats, "description": desc, "origine": "manifestation"},
                    **extra)

    def invocation_actions(self) -> list[dict]:
        out = []
        cha, pb, occ = self.mod("Charisme"), self.prof, self.class_level("Occultiste")
        for m in self.active_invocations():
            fx = set(m.get("effets", []))
            if "action:attaque_occulte" in fx:
                count, plvl = self.pact()
                out.append(self._inv_act("inv:attaque_occulte", "Attaque occulte", "⚡", "Spécial",
                                         "Une fois par tour, quand votre arme de pacte touche : dépensez un emplacement "
                                         "de Pacte (niveau {}) pour infliger {}d8 dégâts de force supplémentaires ; la "
                                         "cible tombe à terre si elle est de taille Très grande ou inférieure."
                                         .format(plvl or "—", 1 + (plvl or 1)),
                                         {"pacte": True}, "{OCCULTE}", "force", 5))
            if "action:tombe_levistus" in fx:
                out.append(self._inv_act("inv:tombe_levistus", "Tombe de Levistus", "🧊", "Réaction",
                                         "Quand vous subissez des dégâts : {} PV temporaires (10 × niveau d'occultiste) "
                                         "qui absorbent les dégâts ; jusqu'à la fin de votre prochain tour, vulnérabilité "
                                         "au feu, vitesse 0 et neutralisé.".format(10 * occ),
                                         {"ressource": "inv:tombe_levistus", "n": 1}, niveau=5, pv_temp=10 * occ))
            if "action:voile_mouches" in fx:
                out.append(self._inv_act("inv:voile_mouches", "Voile de mouches", "🪰", "Action bonus",
                                         "Aura de 1,50 m jusqu'à ce que vous soyez neutralisé ou la congédiiez : avantage "
                                         "en Intimidation, désavantage aux autres tests de Charisme ; toute créature qui "
                                         "commence son tour dans l'aura subit {} dégâts de poison (modificateur de "
                                         "Charisme, minimum 0).".format(max(0, cha)),
                                         {"ressource": "inv:voile_mouches", "n": 1}, niveau=5))
            if "action:malefice_accablant" in fx:
                out.append(self._inv_act("inv:malefice_accablant", "Maléfice accablant", "🌀", "Action bonus",
                                         "La créature maudite (Maléfice, Malédiction de la Lame maudite) à 9 m ou moins "
                                         "et chaque créature de votre choix à 1,50 m d'elle subissent {} dégâts "
                                         "psychiques (modificateur de Charisme, minimum 1).".format(max(1, cha)),
                                         niveau=5))
            if "action:malefice_implacable" in fx:
                out.append(self._inv_act("inv:malefice_implacable", "Maléfice implacable", "🌀", "Action bonus",
                                         "Téléportation jusqu'à 9 m vers un espace inoccupé visible à 1,50 m ou moins de "
                                         "la créature maudite (à 9 m ou moins de vous).", niveau=7))
            if "action:regard_fantomatique" in fx:
                out.append(self._inv_act("inv:regard_fantomatique", "Regard fantomatique", "👁", "Action",
                                         "Concentration, jusqu'à 1 minute : vous voyez à travers les objets solides "
                                         "jusqu'à 9 m et dans le noir comme dans la pénombre.",
                                         {"ressource": "inv:regard_fantomatique", "n": 1}, niveau=7))
            if "action:maitre_ombres" in fx:
                out.append(self._inv_act("inv:maitre_ombres", "Maître des ombres", "🌑", "Action",
                                         "Dans une zone de lumière faible ou de ténèbres : vous devenez invisible jusqu'à "
                                         "ce que vous vous déplaciez ou effectuiez une action ou une réaction.",
                                         niveau=5, effet="invisible"))
            if "action:perception_transferee" in fx:
                out.append(self._inv_act("inv:perception_transferee", "Perception transférée", "👁", "Action",
                                         "Touchez un humanoïde consentant : vous percevez par ses sens jusqu'à la fin de "
                                         "votre prochain tour (aveuglé et assourdi pour votre propre environnement) ; "
                                         "une action par tour prolonge le lien."))
            if "action:reprimande_talisman" in fx:
                out.append(self._inv_act("inv:reprimande_talisman", "Réprimande du talisman", "🧿", "Réaction",
                                         "Quand le porteur de votre talisman est touché par un attaquant visible à 9 m : "
                                         "{} dégâts psychiques (bonus de maîtrise) et l'attaquant est repoussé de 3 m."
                                         .format(pb)))
            if "action:protection_talisman" in fx:
                out.append(self._inv_act("inv:protection_talisman", "Protection du talisman", "🧿", "Spécial",
                                         "Le porteur du talisman rate un jet de sauvegarde : il ajoute 1d4 au jet.",
                                         {"ressource": "inv:protection_talisman", "n": 1}, "1d4", "", 7))
            if "action:lien_talisman" in fx:
                out.append(self._inv_act("inv:lien_talisman", "Lien du talisman", "🧿", "Action",
                                         "Téléportation dans un espace inoccupé à 1,50 m du porteur du talisman (même "
                                         "plan) ; le porteur peut faire de même pour vous rejoindre.",
                                         {"ressource": "inv:lien_talisman", "n": 1}, niveau=12))
            if "action:present_sauveurs" in fx:
                out.append(self._inv_act("inv:present_sauveurs", "Présent des sauveurs", "📖", "Spécial",
                                         "Une créature dont le nom est inscrit (jusqu'à {} noms, bonus de maîtrise) "
                                         "tombe à 0 PV sans être tuée sur le coup : elle tombe à 1 PV à la place."
                                         .format(pb), {"ressource": "inv:present_sauveurs", "n": 1}, niveau=9))
            if "action:engagement_ordre" in fx:
                out.append(self._inv_act("inv:engagement_ordre", "Engagement du maître : ordre", "🐾", "Action bonus",
                                         "Votre familier effectue l'action Attaquer (attaques magiques, DD de vos sorts)."))
            if "action:engagement_resistance" in fx:
                out.append(self._inv_act("inv:engagement_resistance", "Engagement du maître : protection", "🐾",
                                         "Réaction", "Votre familier subit des dégâts : il obtient la résistance contre "
                                         "ces dégâts."))
        return out

    def invocation_passives(self) -> list[dict]:
        """Manifestations sans action (encart des capacités passives du Combat), valeurs calculées."""
        out = []
        cha, pb = self.mod("Charisme"), self.prof
        texts = {
            "concentration_avantage": "Avantage aux jets de sauvegarde de Constitution pour maintenir la concentration.",
            "vision_diable": "Vision dans les ténèbres magiques et non magiques jusqu'à 36 m.",
            "lecture": "Vous pouvez lire toutes les écritures.",
            "sommeil_immunite": "Aucun besoin de dormir, ne peut être endormi ; repos long en activité légère.",
            "soins_maximaux": "Familier à 30 m ou moins : dés de soins au maximum quand vous regagnez des PV.",
            "familier_ameliore": "Familier : vol ou nage 12 m, attaques magiques, votre DD de sauvegarde des sorts.",
            "familier_telepathie": "Télépathie avec le familier, perception par ses sens et parole par sa bouche.",
            "vision_veritable_9m": "Voit la forme véritable des métamorphes et créatures déguisées par magie à 9 m.",
            "arme_pacte:+1": "Arme de pacte : +1 aux jets d'attaque et de dégâts (si elle n'a pas déjà de bonus), "
                             "focaliseur d'incantation ; arcs et arbalètes possibles.",
            "arme_pacte:necrotique_cha": "Arme de pacte : +{} dégâts nécrotiques à chaque coup (modificateur de "
                                         "Charisme, minimum 1).".format(max(1, cha)),
            "attaques:2": "Deux attaques avec l'arme de pacte par action Attaquer.",
            "nage": "Respiration aquatique permanente ; vitesse de nage {} (égale à la marche).".format(
                R.fmt_speed(self.speed())),
            "noms_bm": "Page du Livre des ombres : {} noms au maximum (bonus de maîtrise).".format(pb),
            "competence:Tromperie": "Maîtrise de Tromperie et de Persuasion.",
            "livre_rituels": "Livre des ombres : rituels inscrits (2 de niveau 1 offerts, puis niveau {} max.), "
                             "lancés uniquement comme rituels.".format(self.ritual_book_max_level()),
        }
        for m in self.active_invocations():
            for fx in m.get("effets", []):
                if fx in texts:
                    out.append({"nom": "Manifestation : " + m["nom"], "description": texts[fx], "niveau": m["niveau"],
                                "source": "Occultiste — manifestation occulte ({})".format(m.get("source") or "—")})
        return out

    def pact_weapon_notes(self) -> list[str]:
        fx = self.invocation_effects()
        out = []
        if "arme_pacte:+1" in fx:
            out.append("Arme de pacte améliorée : +1 attaque et dégâts")
        if "arme_pacte:necrotique_cha" in fx:
            out.append("Buveuse de vie : +{} nécrotiques".format(max(1, self.mod("Charisme"))))
        if "attaques:2" in fx:
            out.append("Lame assoiffée : 2 attaques par action")
        return out

    # ------------------------------------------------------------------ dégâts des sorts (règles chiffrées)
    def spell_damage_bonus(self, spell: dict) -> list[tuple[str, int]]:
        """
        Modificateurs ajoutés aux dégâts d'un sort, uniquement quand une règle le prévoit :
          - le sort lui-même (« mod » : Arme spirituelle, Pierre magique, Gourdin magique…) ;
          - Incantation puissante (Clerc) : mod. de Sagesse aux sorts mineurs de clerc ;
          - Évocation renforcée (Magicien d'évocation) : mod. d'Intelligence à un jet de dégâts d'un sort d'évocation ;
          - Affinité élémentaire (Ensorceleur draconique) : mod. de Charisme si le type correspond à l'ancêtre.
        """
        out = []
        if spell.get("mod"):
            caster = next((c for c in self.casters() if c["liste"] in spell.get("classes", [])), None) or \
                (self.casters()[0] if self.casters() else None)
            if caster:
                out.append(("modificateur d'incantation ({})".format(caster["carac"]), caster["mod"]))
        lvl = int(spell.get("niveau") or 0)
        names = self.unlocked_feature_names()
        if lvl == 0 and "Clerc" in spell.get("classes", []) and self.class_level("Clerc") and \
                any(n.startswith("incantation puissante") for n in names):
            out.append(("Incantation puissante (Sagesse)", self.mod("Sagesse")))
        if norm(spell.get("ecole", "")) == "evocation" and "Magicien" in spell.get("classes", []) and \
                any(n.startswith("evocation renforcee") for n in names):
            out.append(("Évocation renforcée (Intelligence)", self.mod("Intelligence")))
        if self.class_level("Ensorceleur") >= 6 and any(n.startswith("affinite elementaire") for n in names):
            from .engine_extras import DRACONIC
            dtype = DRACONIC.get(self.ch.ascendance_ensorceleur, ("",))[0]
            if dtype and dtype in norm(spell.get("type_degats", "")):
                out.append(("Affinité élémentaire (Charisme)", self.mod("Charisme")))
        return out

    # ------------------------------------------------------------------ niveau effectif (surclassement, pacte)
    def pact_only_caster(self) -> bool:
        """Seule la Magie des pactes fournit des emplacements (aucun emplacement de lanceur classique)."""
        count, _ = self.pact()
        return bool(count) and not any(self.spell_slots())

    def known_by_class(self, class_name: str, spell_name: str) -> bool:
        n = norm(spell_name)
        return any(norm(s.get("nom", "")) == n for s in self.ch.sorts.get(class_name, []))

    def default_slot_level(self, name: str, class_name: str = "") -> int:
        """
        Niveau d'emplacement retenu par défaut pour afficher et lancer un sort de niveau 1+ :
          - Magie des pactes (Occultiste) : TOUS les emplacements sont du niveau du pacte, donc un sort d'occultiste
            est d'office surclassé à ce niveau (niveau 5 : sorts de niveau 1 et 2 lancés au niveau 3) ;
            idem pour un sort accordé par une manifestation qui dépense un emplacement d'occultiste ;
          - sinon : le niveau du sort (le joueur peut surclasser via le sélecteur d'emplacement).
        """
        spell = self.db.find_spell(name)
        if not spell or not spell["niveau"]:
            return 0
        base = int(spell["niveau"])
        count, plvl = self.pact()
        if not count or plvl < base:
            return base
        if class_name:
            return plvl if class_name == "Occultiste" else base
        grants = [g for g in self.granted_spells() if g["nom"] == spell["nom"]] if not self.known_by_class(
            "Occultiste", spell["nom"]) else []
        if self.known_by_class("Occultiste", spell["nom"]):
            others = [c for c in self.ch.sorts if c != "Occultiste" and self.known_by_class(c, spell["nom"])]
            return plvl if self.pact_only_caster() or not others else base
        if grants:
            return plvl if any(g.get("emplacement") and g.get("categorie") == "Manifestations occultes"
                               for g in grants) else base
        return plvl if self.pact_only_caster() else base

    def spell_description_at(self, name: str, slot_level: int = 0, class_name: str = "") -> tuple[str, list[str]]:
        """Description réécrite au niveau effectif (dés et projectiles surclassés) : (texte, valeurs modifiées)."""
        spell = self.db.find_spell(name)
        if not spell:
            return "", []
        if spell["niveau"] and not slot_level:
            slot_level = self.default_slot_level(name, class_name)
        return R.describe_at(spell, slot_level)

    def spell_values(self, name: str, slot_level: int = 0, class_name: str = "") -> Optional[dict]:
        """
        Valeurs chiffrées d'un sort de niveau 1+ au niveau d'emplacement choisi (0 = niveau effectif par défaut,
        c.-à-d. le niveau du pacte pour un occultiste) :
        {niveau, base, surclasse, pacte, degats, type_degats, soins, pv_temp, projectiles, texte, regle_sup, bonus}.
        """
        spell = self.db.find_spell(name)
        if not spell or not spell["niveau"]:
            return None
        default = self.default_slot_level(name, class_name)
        slot_level = int(slot_level or default)
        sc = R.spell_scaling(spell, slot_level)
        bonus = self.spell_damage_bonus(spell)
        dmg = sc["degats"]
        if dmg and sc["projectiles"]:                    # chaque projectile / rayon ; bonus de classe : un seul jet
            per = R.add_flat(dmg, sum(v for lab, v in bonus if lab.startswith("modificateur d'incantation")))
            extra = sum(v for lab, v in bonus if not lab.startswith("modificateur d'incantation"))
            per = per if re.fullmatch(r"\d+d\d+", per) else "({})".format(per)
            dmg = "{} × {}".format(sc["projectiles"], per) + (" {:+d}".format(extra) if extra else "")
        elif dmg and bonus:
            dmg = R.add_flat(dmg, sum(v for _, v in bonus))
        heal = sc["soins"]
        if heal and spell.get("soins_mod"):
            caster = next((c for c in self.casters() if c["liste"] in spell.get("classes", [])), None) or \
                (self.casters()[0] if self.casters() else None)
            if caster:
                heal = R.add_flat(heal, caster["mod"])
        count, plvl = self.pact()
        return {"niveau": sc["niveau"], "base": int(spell["niveau"]), "surclasse": sc["niveau"] > int(spell["niveau"]),
                "pacte": bool(count) and sc["niveau"] == plvl and default == plvl,
                "degats": dmg, "type_degats": spell.get("type_degats", ""), "soins": heal,
                "pv_temp": sc["pv_temp"], "projectiles": sc["projectiles"], "texte": sc["texte"],
                "regle_sup": R.upcast_summary(spell), "bonus": bonus}
