#!/usr/bin/env python3
"""
Règles chiffrées des sorts — référentiel audité v37 (Manuel des joueurs, Xanathar, Tasha), idempotent.

Écrit data/Regles_sorts.json (clé « regles_sorts ») : une surcouche lue par le chargeur (core/data_loader.py) qui
complète / corrige les fiches de data/Magie-N.json sans toucher aux descriptions :

  duree        durée officielle (« Concentration, jusqu'à … » pour les sorts de concentration)
  degats       dés de base (au niveau du sort) ; « type_degats » ; « test » (A, AC, Arme, For/Dex/Con/Int/Sag/Cha)
  mod          true = le modificateur de caractéristique d'incantation s'ajoute aux dégâts (règle du sort)
  soins        soins de base ; « soins_mod » : + modificateur d'incantation ; « pv_temp » : PV temporaires
  sup          dés ajoutés par niveau d'emplacement au-dessus du niveau du sort ; « sup_pas » : tous les N niveaux
  sup_soins / sup_pv_temp : idem pour les soins / PV temporaires
  sup_table    {niveau d'emplacement: dés} quand la progression n'est pas linéaire (Lame d'ombres…)
  projectiles  nombre de projectiles / rayons au niveau de base ; « sup_projectiles » : en plus par niveau
  sup_texte    effet du surclassement quand il ne s'agit pas de dés (cibles supplémentaires, durée…)
  echelle      false = sort mineur qui ne gagne PAS de dés aux niveaux 5 / 11 / 17 (Pierre magique…)
  rituel / concentration : corrections des étiquettes
  hors_corpus  sort absent du PHB / Xanathar / Tasha (non audité)

    python tools/spell_rules.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "Regles_sorts.json"

CODES = {"I": "Instantanée", "R": "1 round", "1m": "1 minute", "10m": "10 minutes", "1h": "1 heure",
         "2h": "2 heures", "6h": "6 heures", "8h": "8 heures", "24h": "24 heures", "1j": "1 jour", "7j": "7 jours",
         "10j": "10 jours", "30j": "30 jours", "D": "Jusqu'à dissipation", "DD": "Jusqu'à dissipation ou déclenchement",
         "S": "Spéciale", "6r": "6 rounds"}

# Durées (code ou texte). Les sorts de concentration reçoivent le préfixe « Concentration, jusqu'à ».
DUREES = """
Amis=1m; Aspersion d'acide=I; Assistance=1m; Bouffée de poison=I; Contact glacial=R; Contrôle des flammes=Instantanée ou 1 heure;
Coup au but=R; Coup de tonnerre=I; Druidisme=I; Décharge occulte=I; Embrasement=1m; Façonnage de l'eau=Instantanée ou 1 heure;
Façonnage de la terre=Instantanée ou 1 heure; Ferrage foudroyant=I; Flamme sacrée=I; Flammes=10m; Fouet épineux=I; Gelure=I;
Glas=I; Gourdin magique=1m; Illusion mineure=1m; Infestation=I; Lame aux flammes vertes=I; Lame retentissante=R; Lumière=1h;
Lumières dansantes=1m; Main de mage=1m; Message=R; Moquerie cruelle=I; Mot de radiance=I; Pierre magique=1m; Piqûre mentale=R;
Poigne électrique=I; Prestidigitation=Jusqu'à 1 heure; Protection contre les armes=R; Rayon de givre=I; Réparation=I;
Résistance=1m; Saute de vent=I; Sauvagerie primitive=I; Stabilisation=I; Thaumaturgie=Jusqu'à 1 minute; Trait de feu=I;
Éruption de lames=I;
Absorption des éléments=R; Alarme=8h; Amitié avec les animaux=24h; Appel de familier=I; Armure d'Agathys=1h; Armure de mage=8h;
Baies nourricières=I; Barbes argentées=I; Blessure=I; Bouclier=R; Bouclier de la foi=10m; Bénédiction=1m; Catapulte=I;
Charme-personne=1h; Châtiment calcinant=1m; Châtiment courroucé=1m; Châtiment tonitruant=1m; Collet=8h;
Communication avec les animaux=10m; Compréhension des langues=1h; Couleurs dansantes=R; Couteau de glace=I;
Création ou destruction d'eau=I; Cérémonie=I; Disque flottant de Tenser=1h; Duel forcé=1m; Déguisement=1h;
Détection de la magie=10m; Détection du mal et du bien=10m; Détection du poison et des maladies=10m; Enchevêtrement=1m;
Faveur divine=1m; Feuille morte=1m; Fléau=1m; Fou rire de Tasha=1m; Frappe du zéphyr=1m; Frappe piégeuse=1m; Frayeur=1m;
Graisse=1m; Grande foulée=1h; Héroïsme=1m; Identification=I; Image silencieuse=10m; Injonction=R; Lien avec une bête=10m;
Lueurs féeriques=1m; Mains brûlantes=I; Maléfice=1h; Marque du chasseur=1h; Mixture caustique de Tasha=1m;
Mot de guérison=I; Murmures dissonants=I; Nappe de brouillard=1h; Orbe chromatique=I; Projectile magique=I;
Protection contre le mal et le bien=10m; Rayon empoisonné=I; Repli expéditif=10m; Représailles infernales=I; Sanctuaire=1m;
Saut=1m; Secousse sismique=I; Serviteur invisible=1h; Simulacre de vie=1h; Soins=I; Sommeil=1m; Tentacules de Hadar=I;
Texte illusoire=10j; Trait ensorcelé=1m; Vague tonnante=I; Éclair de chaos=I; Éclair traçant=R;
Agrandissement/Rapetissement=1m; Aide=8h; Amélioration de caractéristique=1h; Apaisement des émotions=1m; Appel de destrier=I;
Arme magique=1h; Arme spirituelle=1m; Attraction terrestre=1m; Augure=I; Aura magique de Nystul=24h; Bouche magique=DD;
Bourrasque=1m; Châtiment révélateur=1m; Convocation de bête=1h; Corde enchantée=1h; Cordon de flèches=8h;
Couronne du dément=1m; Croissance d'épines=10m; Cécité/Surdité=1m; Discours captivant=1m; Déblocage=I;
Détection des pensées=1m; Espièglerie de Nathair=1m; Esprit guérisseur=1m; Flambée d'Aganazzar=I; Flamme éternelle=D;
Flou=1m; Flèche acide de Melf=I; Force fantasmagorique=1m; Fouet mental de Tasha=R; Foulée brumeuse=I; Fracassement=I;
Image miroir=1m; Immobilisation de personne=1m; Invisibilité=1h; Lame d'ombres=1m; Lame de feu=10m; Libellé aérien=1h;
Lien de protection=1h; Localisation d'animaux ou de plantes=I; Localisation d'objet=10m; Lévitation=10m; Messager animal=24h;
Modification d'apparence=1h; Métal brûlant=1m; Nuée de boules de neige de Snilloc=I; Nuée de dagues=1m;
Passage sans trace=1h; Pattes d'araignée=1h; Peau d'écorce=1h; Poigne terreuse de Maximilien=1m; Prière de guérison=I;
Protection contre le poison=1h; Préservation des morts=10j; Pyrotechnie=I; Rayon affaiblissant=1m; Rayon ardent=I;
Rayon de lune=1m; Restauration partielle=I; Sens animal=1h; Sens des pièges=I; Silence=10m; Souffle du dragon=1m;
Sphère de feu=1m; Suggestion=8h; Toile d'araignée=1h; Tourbillon de poussière=1m; Ténèbres=10m; Vent protecteur=10m;
Verrou magique=D; Vision dans le noir=8h; Voir l'invisible=1h; Zone de vérité=10m; Épine mentale=1h;
Animation des morts=I; Antidétection=8h; Appel de la foudre=10m; Arme élémentaire=1h; Aura de vitalité=1m; Aura du croisé=1m;
Boule de feu=I; Cercle magique=1h; Châtiment aveuglant=1m; Clairvoyance=10m; Clignotement=1m;
Communication avec les morts=10m; Communication avec les plantes=10m; Communication à distance=R; Contresort=I;
Convocation de démons mineurs=1h; Convocation de fée=1h; Convocation de mort-vivant=1h; Convocation de rejeton d'ombre=1h;
Croissance végétale=I; Création de nourriture et d'eau=I; Dissipation de la magie=I; Don des langues=1h;
Délivrance des malédictions=I; Ennemis à foison=1m; Esprits gardiens=10m; Flèche de foudre=1m; Flèches enflammées=1h;
Forme gazeuse=1h; Forteresse d'intellect=1h; Foulée d'Ashardalon=1m; Foulée tonitruante=I; Fusion dans la pierre=8h;
Glyphe de protection=DD; Hâte=1m; Image majeure=10m; Invocation d'animaux=1h; Invocation de projectiles=I; Lenteur=1m;
Lueur d'espoir=1m; Lumière du jour=1h; Malédiction=1m; Marche sur l'eau=1h; Minuscules météores de Melf=10m;
Monture fantôme=1h; Mort simulée=1h; Mot de guérison de groupe=I; Motif hypnotique=1m; Mur d'eau=10m; Mur de sable=10m;
Mur de vent=1m; Nuage nauséabond=1m; Petite hutte de Léomund=8h; Peur=1m; Protection contre une énergie=1h;
Raz-de-marée=I; Respiration aquatique=24h; Retour à la vie=I; Serviteur miniature=8h; Sieste=10m; Tempête de neige=1m;
Toucher du vampire=1m; Transfert de vie=I; Voile spirituel=1m; Vol=10m; Voracité de Hadar=1m; Éclair=I; Éruption de terre=I;
Appel de destrier supérieur=I; Assassin imaginaire=1m; Aura de pureté=10m; Aura de vie=10m; Bannissement=1m;
Bouclier de feu=10m; Charme-monstre=1h; Chien de garde de Mordenkainen=8h; Châtiment débilitant=1m;
Coffre secret de Léomund=I; Compulsion=1m; Confusion=1m; Contrôle de l'eau=10m; Convocation d'aberration=1h;
Convocation d'artificiel=1h; Convocation d'élémentaire=1h; Convocation de démon majeur=1h; Divination=I;
Domination de bête=1m; Fabrication=I; Façonnage de la pierre=I; Fléau élémentaire=1m; Flétrissement=I; Gardien de la foi=8h;
Gardien de la nature=1m; Insecte géant=10m; Invisibilité supérieure=1m; Invocation d'élémentaires mineurs=1h;
Invocation d'êtres sylvestres=1h; Lance d'arçon psychique de Raulothim=I; Liane avide=1m; Liberté de mouvement=1h;
Localisation de créature=1h; Mur de feu=1m; Métamorphose=1h; Oeil magique=1h; Ombre d'égarement=1m; Peau de pierre=1h;
Porte dimensionnelle=I; Protection contre la mort=8h; Rayonnement écoeurant=10m; Sanctuaire privé de Mordenkainen=24h;
Sphère aqueuse=1m; Sphère de tempête=1m; Sphère de vitriol=I; Sphère résiliente d'Otiluke=1m; Tempête de grêle=I;
Tentacules noirs d'Evard=1m; Terrain hallucinatoire=24h;
Amélioration de compétences=1h; Animation d'objets=1m; Apparence trompeuse=8h; Arme sacrée=1h; Assignation infernale=1h;
Aube=1m; Brume mortelle=10m; Carquois magique=1m; Cercle de pouvoir=10m; Cercle de téléportation=R; Châtiment du ban=1m;
Colonne de flamme=I; Communion avec la nature=I; Communion=1m; Contact avec un autre plan=1m; Contagion=7j; Contrat=24h;
Contrôle des vents=1h; Convocation d'esprit draconique=1h; Convocation de céleste=1h; Coquille antivie=1h; Création=S;
Cône de froid=I; Danse macabre=1h; Dissipation du mal et du bien=1m; Domination de personne=1m; Double illusoire=1h;
Déluge d'énergie négative=I; Fléau d'insectes=10m; Foulée dimensionnelle=1m; Frappe du vent d'acier=I;
Fureur de la nature=1m; Immobilisation de monstre=1m; Immolation=1m; Invocation d'élémentaire=1h; Invocation de volée=I;
Lien télépathique de Rary=1h; Maelström=1m; Main de Bigby=1m; Modification de mémoire=1m; Mur de force=10m;
Mur de lumière=10m; Mur de pierre=10m; Mythes et légendes=I; Passage par les arbres=1m; Passe-muraille=1h;
Perturbations synaptiques=I; Quête=30j; Rappel à la vie=I; Restauration supérieure=I; Réincarnation=I; Sanctification=D;
Scrutation=10m; Soins de groupe=I; Songe=8h; Transmutation de la pierre=D; Télékinésie=10m; Vague destructrice=I;
Énervation=1m; Éveil=I;
Allié planaire=I; Barrière de lames=10m; Bosquet des druides=24h; Bouclier de platine de Fizban=1m; Cage des âmes=8h;
Cercle de mort=I; Chaîne d'éclairs=I; Contamination=I; Convocation de fiélon=1h; Convocations instantanées de Drawmij=D;
Costume d'Outremonde de Tasha=1m; Création d'homoncule=I; Création de mort-vivant=I; Danse irrésistible d'Otto=1m;
Dispersion=I; Désintégration=I; Festin des héros=I; Globe d'invulnérabilité=1m; Guérison=I; Illusion programmée=D;
Interdiction=1j; Invocation de fée=1h; Marche sur le vent=8h; Mauvais oeil=1m; Mot de retour=I; Mur d'épines=10m;
Mur de glace=10m; Ossements de la Terre=I; Portail magique=10m; Prison mentale=1m; Protection primordiale=1m;
Protections et sceaux=24h; Prévoyance=10j; Pétrification=1m; Rayon de soleil=1m; Sacre de la glace=10m; Sacre de la pierre=10m;
Sacre des flammes=10m; Sacre du vent=10m; Sens de l'orientation=1j; Sphère glaciale d'Otiluke=I; Suggestion de groupe=24h;
Terraformage=2h; Transformation de Tenser=10m; Urne magique=D; Vision suprême=1h; Voie végétale=R;
Boule de feu à retardement=1m; Cage de force=1h; Changement de plan=I; Couronne d'étoiles=1h; Dissimulation=D;
Doigt de mort=I; Forme éthérée=8h; Inversion de la gravité=1m; Invocation de céleste=1h;
Manoir somptueux de Mordenkainen=24h; Mirage=10j; Mot de pouvoir douloureux=I; Parole divine=I; Projection d'image=1j;
Rayons prismatiques=I; Régénération=1h; Résurrection=I; Simulacre=D; Songe du voile bleu=6h; Symbole=DD;
Temple des dieux=24h; Tempête de feu=I; Tourbillon=1m; Transformation draconique=1m; Téléportation=I;
Épée de Mordenkainen=1m;
Aura sacrée=1m; Aversion/Attirance=10j; Bagou=1h; Champ antimagie=1h; Clone=I; Contrôle du climat=8h; Demi-plan=1h;
Domination de monstre=1h; Dragon illusoire=1m; Dédale=10m; Esprit faible=I; Esprit impénétrable=24h;
Flétrissure épouvantable d'Abi-Dalzim=I; Formes animales=24h; Forteresse majestueuse=I; Mot de pouvoir étourdissant=I;
Nuage incendiaire=1m; Tremblement de terre=1m; Tsunami=6r; Télépathie=24h; Ténèbres oppressantes=10m; Éclat du soleil=I;
Arrêt du temps=I; Changement de forme=1h; Emprisonnement=D; Ennemi subconscient=1m; Guérison de groupe=I;
Hurlement psychique=I; Invulnérabilité=10m; Lame du désastre=1m; Mot de pouvoir guérisseur=I; Mot de pouvoir mortel=I;
Mur prismatique=10m; Métamorphose de groupe=1h; Métamorphose suprême=1h; Nuée de météores=I; Portail=1m;
Projection astrale=S; Prémonition=8h; Résurrection suprême=I; Souhait=I; Tempête vengeresse=1m
"""

CHOICE = "au choix"
# nom: dict — dégâts, soins, surclassement (voir l'en-tête)
REGLES = {
    # ---------------------------------------------------------------- sorts mineurs
    "Fouet épineux": dict(test="AC"),
    "Pierre magique": dict(degats="1d6", type_degats="contondant", test="A", mod=True, echelle=False),
    "Gourdin magique": dict(degats="1d8", type_degats="contondant", test="Arme", mod=True, echelle=False),
    "Lame aux flammes vertes": dict(degats="", type_degats="feu", test="Arme"),
    "Lame retentissante": dict(degats="1d8", type_degats="tonnerre", test="Arme"),
    "Glas": dict(degats="1d8", type_degats="nécrotique", test="Sag"),
    # ---------------------------------------------------------------- niveau 1
    "Absorption des éléments": dict(degats="1d6", type_degats=CHOICE, sup="1d6"),
    "Armure d'Agathys": dict(degats="5", type_degats="froid", sup="5", pv_temp="5", sup_pv_temp="5"),
    "Blessure": dict(degats="3d10", type_degats="nécrotique", test="AC", sup="1d10"),
    "Catapulte": dict(degats="3d8", type_degats="contondant", test="Dex", sup="1d8"),
    "Châtiment calcinant": dict(degats="1d6", type_degats="feu", test="Con", sup="1d6"),
    "Châtiment courroucé": dict(degats="1d6", type_degats="psychique", test="Sag", sup="1d6"),
    "Châtiment tonitruant": dict(degats="2d6", type_degats="tonnerre", test="For"),
    "Couleurs dansantes": dict(sup_texte="+2d10 points de vie de créatures affectées par niveau au-delà du 1er"),
    "Couteau de glace": dict(degats="1d10", type_degats="perforant", test="A",
                             sup_texte="Explosion : 2d6 froid (JS Dex), +1d6 par niveau au-delà du 1er"),
    "Faveur divine": dict(degats="1d4", type_degats="radiant"),
    "Frappe du zéphyr": dict(degats="1d8", type_degats="force"),
    "Frappe piégeuse": dict(degats="1d6", type_degats="perforant", test="For", sup="1d6"),
    "Mains brûlantes": dict(degats="3d6", type_degats="feu", test="Dex", sup="1d6"),
    "Maléfice": dict(degats="1d6", type_degats="nécrotique",
                     sup_texte="Durée : 8 heures (emplacement de niveau 3 ou 4), 24 heures (niveau 5 ou plus)"),
    "Marque du chasseur": dict(degats="1d6", type_degats="de l'arme",
                               sup_texte="Durée : 8 heures (emplacement de niveau 3 ou 4), 24 heures (niveau 5 ou plus)"),
    "Mixture caustique de Tasha": dict(degats="2d4", type_degats="acide", test="Dex", sup="2d4"),
    "Mot de guérison": dict(soins="1d4", soins_mod=True, sup_soins="1d4"),
    "Murmures dissonants": dict(degats="3d6", type_degats="psychique", test="Sag", sup="1d6"),
    "Orbe chromatique": dict(degats="3d8", type_degats=CHOICE, test="A", sup="1d8"),
    "Projectile magique": dict(degats="1d4 + 1", type_degats="force", test="", projectiles=3, sup_projectiles=1),
    "Rayon empoisonné": dict(degats="2d8", type_degats="poison", test="A", sup="1d8"),
    "Représailles infernales": dict(degats="2d10", type_degats="feu", test="Dex", sup="1d10"),
    "Secousse sismique": dict(degats="1d6", type_degats="contondant", test="Dex", sup="1d6"),
    "Simulacre de vie": dict(pv_temp="1d4 + 4", sup_pv_temp="5"),
    "Soins": dict(soins="1d8", soins_mod=True, sup_soins="1d8"),
    "Sommeil": dict(sup_texte="+2d8 points de vie de créatures affectées par niveau au-delà du 1er"),
    "Tentacules de Hadar": dict(degats="2d6", type_degats="nécrotique", test="For", sup="1d6"),
    "Trait ensorcelé": dict(degats="1d12", type_degats="foudre", test="A", sup="1d12"),
    "Vague tonnante": dict(degats="2d8", type_degats="tonnerre", test="Con", sup="1d8"),
    "Éclair de chaos": dict(degats="2d8 + 1d6", type_degats="variable (d8)", test="A", sup="1d6"),
    "Éclair traçant": dict(degats="4d6", type_degats="radiant", test="A", sup="1d6"),
    "Bénédiction": dict(sup_texte="Une cible supplémentaire par niveau au-delà du 1er"),
    "Fléau": dict(sup_texte="Une cible supplémentaire par niveau au-delà du 1er"),
    "Charme-personne": dict(sup_texte="Une cible supplémentaire par niveau au-delà du 1er"),
    "Héroïsme": dict(sup_texte="Une cible supplémentaire par niveau au-delà du 1er"),
    "Injonction": dict(sup_texte="Une cible supplémentaire par niveau au-delà du 1er"),
    # ---------------------------------------------------------------- niveau 2
    "Aide": dict(sup_texte="+5 points de vie (maximum et actuels) par niveau au-delà du 2e"),
    "Arme magique": dict(sup_texte="Bonus +2 (emplacement de niveau 4 ou 5), +3 (niveau 6 ou plus)"),
    "Arme spirituelle": dict(degats="1d8", type_degats="force", test="AC", mod=True, sup="1d8", sup_pas=2),
    "Châtiment révélateur": dict(degats="2d6", type_degats="radiant", sup="1d6"),
    "Cordon de flèches": dict(degats="1d6", type_degats="perforant", test="Dex",
                              sup_texte="+2 munitions par niveau au-delà du 2e"),
    "Croissance d'épines": dict(degats="2d4", type_degats="perforant"),
    "Flambée d'Aganazzar": dict(degats="3d8", type_degats="feu", test="Dex", sup="1d8"),
    "Flèche acide de Melf": dict(degats="4d4", type_degats="acide", test="A", sup="1d4",
                                 sup_texte="Dégâts différés : 2d4 (+1d4 par niveau au-delà du 2e)"),
    "Fouet mental de Tasha": dict(degats="3d6", type_degats="psychique", test="Int",
                                  sup_texte="Une cible supplémentaire par niveau au-delà du 2e"),
    "Fracassement": dict(degats="3d8", type_degats="tonnerre", test="Con", sup="1d8"),
    "Lame d'ombres": dict(degats="2d8", type_degats="psychique", test="Arme", sup_table={3: "3d8", 5: "4d8", 7: "5d8"}),
    "Lame de feu": dict(degats="3d6", type_degats="feu", test="AC", sup="1d6", sup_pas=2),
    "Métal brûlant": dict(degats="2d8", type_degats="feu", test="Con", sup="1d8"),
    "Nuée de boules de neige de Snilloc": dict(degats="3d6", type_degats="froid", test="Dex", sup="1d6"),
    "Nuée de dagues": dict(degats="4d4", type_degats="tranchant", test="", sup="2d4"),
    "Poigne terreuse de Maximilien": dict(degats="2d6", type_degats="contondant", test="For"),
    "Rayon ardent": dict(degats="2d6", type_degats="feu", test="A", projectiles=3, sup_projectiles=1),
    "Rayon de lune": dict(degats="2d10", type_degats="radiant", test="Con", sup="1d10"),
    "Souffle du dragon": dict(degats="3d6", type_degats=CHOICE, test="Dex", sup="1d6"),
    "Sphère de feu": dict(degats="2d6", type_degats="feu", test="Dex", sup="1d6"),
    "Tourbillon de poussière": dict(degats="1d8", type_degats="contondant", test="For", sup="1d8"),
    "Épine mentale": dict(degats="3d8", type_degats="psychique", test="Sag", sup="1d8"),
    "Prière de guérison": dict(soins="2d8", soins_mod=True, sup_soins="1d8"),
    "Esprit guérisseur": dict(soins="1d6", sup_soins="1d6"),
    "Immobilisation de personne": dict(sup_texte="Une cible humanoïde supplémentaire par niveau au-delà du 2e"),
    "Invisibilité": dict(sup_texte="Une cible supplémentaire par niveau au-delà du 2e"),
    # ---------------------------------------------------------------- niveau 3
    "Appel de la foudre": dict(degats="3d10", type_degats="foudre", test="Dex", sup="1d10"),
    "Aura de vitalité": dict(soins="2d6"),
    "Boule de feu": dict(degats="8d6", type_degats="feu", test="Dex", sup="1d6"),
    "Châtiment aveuglant": dict(degats="3d8", type_degats="radiant", test="Con"),
    "Esprits gardiens": dict(degats="3d8", type_degats="radiant ou nécrotique", test="Sag", sup="1d8"),
    "Flèche de foudre": dict(degats="4d8", type_degats="foudre", test="Arme", sup="1d8",
                             sup_texte="Éclaboussure : 2d8 foudre (JS Dex), +1d8 par niveau au-delà du 3e"),
    "Flèches enflammées": dict(degats="1d6", type_degats="feu", sup_texte="+2 munitions par niveau au-delà du 3e"),
    "Foulée d'Ashardalon": dict(degats="1d6", type_degats="feu", test="Dex", sup="1d6"),
    "Foulée tonitruante": dict(degats="3d10", type_degats="tonnerre", test="Con", sup="1d10"),
    "Invocation de projectiles": dict(degats="3d8", type_degats="de la munition", test="Dex"),
    "Minuscules météores de Melf": dict(degats="2d6", type_degats="feu", test="Dex", projectiles=6, sup_projectiles=2),
    "Mot de guérison de groupe": dict(soins="1d4", soins_mod=True, sup_soins="1d4"),
    "Raz-de-marée": dict(degats="4d8", type_degats="contondant", test="Dex"),
    "Toucher du vampire": dict(degats="3d6", type_degats="nécrotique", test="AC", sup="1d6"),
    "Transfert de vie": dict(degats="4d8", type_degats="nécrotique (vous)", sup="1d8",
                             sup_texte="La cible regagne le double des dégâts nécrotiques que vous subissez"),
    "Voile spirituel": dict(degats="1d8", type_degats="radiant, nécrotique ou froid", sup="1d8", sup_pas=2),
    "Voracité de Hadar": dict(degats="2d6", type_degats="froid (+2d6 acide, JS Dex)"),
    "Éclair": dict(degats="8d6", type_degats="foudre", test="Dex", sup="1d6"),
    "Éruption de terre": dict(degats="3d12", type_degats="contondant", test="Dex", sup="1d12"),
    "Aura du croisé": dict(degats="1d4", type_degats="radiant"),
    "Arme élémentaire": dict(degats="1d4", type_degats=CHOICE, sup_table={5: "2d4", 7: "3d4"},
                             sup_texte="Bonus +2 (emplacement de niveau 5 ou 6), +3 (niveau 7 ou plus)"),
    "Glyphe de protection": dict(degats="5d8", type_degats=CHOICE, test="Dex", sup="1d8"),
    "Animation des morts": dict(sup_texte="Deux morts-vivants supplémentaires par niveau au-delà du 3e"),
    "Vol": dict(sup_texte="Une cible supplémentaire par niveau au-delà du 3e"),
    # ---------------------------------------------------------------- niveau 4
    "Assassin imaginaire": dict(degats="4d10", type_degats="psychique", test="Sag", sup="1d10"),
    "Bouclier de feu": dict(degats="2d8", type_degats="feu ou froid"),
    "Chien de garde de Mordenkainen": dict(degats="4d8", type_degats="perforant", test="A"),
    "Châtiment débilitant": dict(degats="4d6", type_degats="psychique", test="Sag"),
    "Fléau élémentaire": dict(degats="2d6", type_degats=CHOICE, test="Con",
                              sup_texte="Une cible supplémentaire par niveau au-delà du 4e"),
    "Flétrissement": dict(degats="8d8", type_degats="nécrotique", test="Con", sup="1d8"),
    "Gardien de la foi": dict(degats="20", type_degats="radiant", test="Dex"),
    "Lance d'arçon psychique de Raulothim": dict(degats="7d6", type_degats="psychique", test="Int", sup="1d6"),
    "Mur de feu": dict(degats="5d8", type_degats="feu", test="Dex", sup="1d8"),
    "Ombre d'égarement": dict(degats="2d8", type_degats="nécrotique"),
    "Rayonnement écoeurant": dict(degats="4d10", type_degats="radiant", test="Con"),
    "Sphère de tempête": dict(degats="2d6", type_degats="contondant", test="For", sup="1d6",
                              sup_texte="Éclair (attaque de sort) : 4d6 foudre, +1d6 par niveau au-delà du 4e"),
    "Sphère de vitriol": dict(degats="10d4", type_degats="acide", test="Dex", sup="2d4"),
    "Tempête de grêle": dict(degats="2d8", type_degats="contondant (+4d6 froid)", test="Dex", sup="1d8"),
    "Tentacules noirs d'Evard": dict(degats="3d6", type_degats="contondant", test="Dex"),
    "Bannissement": dict(sup_texte="Une cible supplémentaire par niveau au-delà du 4e"),
    # ---------------------------------------------------------------- niveau 5
    "Arme sacrée": dict(degats="2d8", type_degats="radiant"),
    "Aube": dict(degats="4d10", type_degats="radiant", test="Con"),
    "Brume mortelle": dict(degats="5d8", type_degats="poison", test="Con", sup="1d8"),
    "Châtiment du ban": dict(degats="5d10", type_degats="force"),
    "Colonne de flamme": dict(degats="4d6", type_degats="feu (+4d6 radiant)", test="Dex", sup="1d6"),
    "Contact avec un autre plan": dict(degats="6d6", type_degats="psychique", test="Int"),
    "Cône de froid": dict(degats="8d8", type_degats="froid", test="Con", sup="1d8"),
    "Déluge d'énergie négative": dict(degats="5d12", type_degats="nécrotique", test="Con"),
    "Fléau d'insectes": dict(degats="4d10", type_degats="perforant", test="Con", sup="1d10"),
    "Frappe du vent d'acier": dict(degats="6d10", type_degats="force", test="AC"),
    "Immolation": dict(degats="8d6", type_degats="feu", test="Dex"),
    "Invocation de volée": dict(degats="8d8", type_degats="de la munition", test="Dex"),
    "Maelström": dict(degats="6d6", type_degats="contondant", test="For"),
    "Main de Bigby": dict(degats="4d8", type_degats="force", test="AC", sup="2d8",
                          sup_texte="Main agrippeuse : 2d6 + mod. d'incantation, +2d6 par niveau au-delà du 5e"),
    "Mur de lumière": dict(degats="4d8", type_degats="radiant", test="Con", sup="1d8"),
    "Perturbations synaptiques": dict(degats="8d6", type_degats="psychique", test="Int"),
    "Quête": dict(degats="5d10", type_degats="psychique",
                  sup_texte="Durée : 1 an (emplacement de niveau 7 ou 8), permanente (niveau 9)"),
    "Vague destructrice": dict(degats="5d6", type_degats="tonnerre (+5d6 radiant ou nécrotique)", test="Con"),
    "Énervation": dict(degats="4d8", type_degats="nécrotique", test="Dex", sup="1d8"),
    "Soins de groupe": dict(soins="3d8", soins_mod=True, sup_soins="1d8"),
    "Danse macabre": dict(sup_texte="Deux morts-vivants supplémentaires par niveau au-delà du 5e"),
    "Animation d'objets": dict(sup_texte="Deux objets supplémentaires par niveau au-delà du 5e"),
    "Immobilisation de monstre": dict(sup_texte="Une cible supplémentaire par niveau au-delà du 5e"),
    "Rappel à la vie": dict(rituel=False),
    "Réincarnation": dict(rituel=False),
    # ---------------------------------------------------------------- niveau 6
    "Barrière de lames": dict(degats="6d10", type_degats="tranchant", test="Dex"),
    "Cercle de mort": dict(degats="8d6", type_degats="nécrotique", test="Con", sup="2d6"),
    "Chaîne d'éclairs": dict(degats="10d8", type_degats="foudre", test="Dex",
                             sup_texte="Un rebond supplémentaire par niveau au-delà du 6e"),
    "Contamination": dict(degats="14d6", type_degats="nécrotique", test="Con"),
    "Désintégration": dict(degats="10d6 + 40", type_degats="force", test="Dex", sup="3d6"),
    "Mur d'épines": dict(degats="7d8", type_degats="perforant", test="Dex", sup="1d8"),
    "Mur de glace": dict(degats="10d6", type_degats="froid", test="Dex", sup="2d6",
                         sup_texte="Air glacial : 5d6 froid (JS Con), +1d6 par niveau au-delà du 6e"),
    "Prison mentale": dict(degats="5d10", type_degats="psychique", test="Int"),
    "Rayon de soleil": dict(degats="6d8", type_degats="radiant", test="Con"),
    "Sacre de la glace": dict(degats="4d6", type_degats="froid", test="Con"),
    "Sacre des flammes": dict(degats="4d8", type_degats="feu", test="Dex"),
    "Sacre du vent": dict(degats="2d10", type_degats="contondant", test="Con"),
    "Sphère glaciale d'Otiluke": dict(degats="10d6", type_degats="froid", test="Con", sup="1d6"),
    "Ossements de la Terre": dict(degats="6d6", type_degats="contondant", test="Dex",
                                  sup_texte="Deux piliers supplémentaires par niveau au-delà du 6e"),
    "Guérison": dict(soins="70", sup_soins="10"),
    # ---------------------------------------------------------------- niveaux 7 à 9
    "Boule de feu à retardement": dict(degats="12d6", type_degats="feu", test="Dex", sup="1d6"),
    "Couronne d'étoiles": dict(degats="4d12", type_degats="radiant", test="A", projectiles=7, sup_projectiles=2),
    "Doigt de mort": dict(degats="7d8 + 30", type_degats="nécrotique", test="Con"),
    "Rayons prismatiques": dict(degats="10d6", type_degats="selon la couleur", test="Dex"),
    "Tempête de feu": dict(degats="7d10", type_degats="feu", test="Dex"),
    "Tourbillon": dict(degats="10d6", type_degats="contondant", test="Dex"),
    "Épée de Mordenkainen": dict(degats="3d10", type_degats="force", test="AC"),
    "Transformation draconique": dict(degats="6d8", type_degats=CHOICE, test="Dex"),
    "Régénération": dict(soins="4d8 + 15"),
    "Flétrissure épouvantable d'Abi-Dalzim": dict(degats="12d8", type_degats="nécrotique", test="Con"),
    "Nuage incendiaire": dict(degats="10d8", type_degats="feu", test="Dex"),
    "Tsunami": dict(degats="6d10", type_degats="contondant", test="For"),
    "Ténèbres oppressantes": dict(degats="8d8", type_degats="psychique", test="Sag"),
    "Éclat du soleil": dict(degats="12d6", type_degats="radiant", test="Con"),
    "Dragon illusoire": dict(degats="7d6", type_degats=CHOICE, test="Int"),
    "Esprit faible": dict(degats="4d6", type_degats="psychique", test="Int"),
    "Ennemi subconscient": dict(degats="4d10", type_degats="psychique", test="Sag"),
    "Hurlement psychique": dict(degats="14d6", type_degats="psychique", test="Int"),
    "Lame du désastre": dict(degats="4d12", type_degats="force", test="A"),
    "Nuée de météores": dict(degats="20d6", type_degats="feu (+20d6 contondant)", test="Dex"),
}

# Effet d'un JS RÉUSSI sur les dégâts (v40). Par défaut : sort de niveau 1+ = moitié des dégâts, sort mineur = aucun.
# Exceptions vérifiées sur le texte officiel :
#   « aucun »   : réussite = aucun dégât ;
#   « toujours » : les dégâts s'appliquent quoi qu'il arrive (le JS n'évite que l'état) ;
#   autre texte : dégâts réduits particuliers.
JS_SUCCES = {
    "Catapulte": "aucun", "Mixture caustique de Tasha": "aucun", "Secousse sismique": "aucun",
    "Frappe piégeuse": "aucun", "Cordon de flèches": "aucun", "Poigne terreuse de Maximilien": "aucun",
    "Foulée d'Ashardalon": "aucun", "Sphère de tempête": "aucun", "Tentacules noirs d'Evard": "aucun",
    "Assassin imaginaire": "aucun", "Rayonnement écoeurant": "aucun", "Maelström": "aucun",
    "Contact avec un autre plan": "aucun", "Désintégration": "aucun", "Ennemi subconscient": "aucun",
    "Quête": "aucun",
    "Châtiment calcinant": "toujours", "Châtiment courroucé": "toujours", "Châtiment tonitruant": "toujours",
    "Châtiment aveuglant": "toujours", "Châtiment débilitant": "toujours", "Métal brûlant": "toujours",
    "Fléau élémentaire": "toujours", "Prison mentale": "toujours", "Esprit faible": "toujours",
    "Voracité de Hadar": "toujours",
    "Énervation": "2d8 nécrotiques, puis le sort prend fin",
}

HORS_CORPUS = ["Vents contraires", "Projectile élémentaire", "Entraves de givre", "Sens de la distorsion",
               "Scellé de portail", "Invocation d'ombres"]


def parse_durations(text: str) -> dict:
    out = {}
    for chunk in text.replace("\n", " ").split(";"):
        if "=" not in chunk:
            continue
        name, code = (x.strip() for x in chunk.split("=", 1))
        out[name] = CODES.get(code, code)
    return out


def build() -> dict:
    rules = {name: {"duree": d} for name, d in parse_durations(DUREES).items()}
    for name, r in REGLES.items():
        rules.setdefault(name, {}).update({k: v for k, v in r.items()})
    for name, value in JS_SUCCES.items():
        rules.setdefault(name, {})["js_succes"] = value
    for name in HORS_CORPUS:
        rules.setdefault(name, {})["hors_corpus"] = True
    for r in rules.values():                       # JSON : clés de sup_table en texte
        if "sup_table" in r:
            r["sup_table"] = {str(k): v for k, v in r["sup_table"].items()}
    return rules


def apply(path: Path = PATH) -> int:
    rules = build()
    path.write_text(json.dumps({"regles_sorts": rules}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(rules)


if __name__ == "__main__":
    print("{} règles de sorts écrites dans {}".format(apply(), PATH.name))
    sys.exit(0)
