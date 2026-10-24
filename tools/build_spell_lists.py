#!/usr/bin/env python3
"""
Génère data/Sorts_Listes.json : association « nom de sort -> classes pouvant l'apprendre ».

Vos fichiers Magie-N.json ne précisent pas quelles classes accèdent à chaque sort. Ce fichier comble ce
manque (listes officielles : Manuel des Joueurs, Xanathar, Tasha, Fizban, Strixhaven). Il est modifiable
à la main. Lettres : B Barde · C Clerc · D Druide · E Ensorceleur · M Magicien · O Occultiste ·
P Paladin · R Rôdeur · A Artificier.

Usage : python tools/build_spell_lists.py
"""
import json
from pathlib import Path

CLS = {"B": "Barde", "C": "Clerc", "D": "Druide", "E": "Ensorceleur", "M": "Magicien",
       "O": "Occultiste", "P": "Paladin", "R": "Rôdeur", "A": "Artificier"}

RAW = """
# ---- niveau 0
Amis=BEMO;Aspersion d'acide=EMA;Assistance=CDA;Bouffée de poison=DEMOA;Contact glacial=EMO;Contrôle des flammes=DEM
Coup au but=BEMO;Coup de tonnerre=BDEMA;Décharge occulte=O;Druidisme=D;Embrasement=DEMOA;Éruption de lames=EMOA
Façonnage de l'eau=DEM;Façonnage de la terre=DEM;Ferrage foudroyant=EMOA;Flamme sacrée=C;Flammes=D;Fouet épineux=DA
Gelure=DEMA;Glas=CMO;Gourdin magique=D;Illusion mineure=BEMO;Infestation=DEMO;Lame aux flammes vertes=EMOA
Lame retentissante=EMOA;Lumière=BCEMA;Lumières dansantes=BEMA;Main de mage=BEMOA;Message=BEMA;Moquerie cruelle=B
Mot de radiance=C;Pierre magique=DOA;Piqûre mentale=EMO;Poigne électrique=EMA;Prestidigitation=BEMOA
Protection contre les armes=BEMO;Rayon de givre=EMA;Réparation=BCDEMA;Résistance=CDA;Sauvagerie primitive=D
Saute de vent=DEM;Stabilisation=CA;Thaumaturgie=C;Trait de feu=EMA
# ---- niveau 1
Absorption des éléments=DEMRA;Alarme=MRA;Amitié avec les animaux=BDR;Appel de familier=M;Armure d'Agathys=O
Armure de mage=EM;Baies nourricières=DR;Barbes argentées=BEM;Bénédiction=CP;Blessure=C;Bouclier=EM
Bouclier de la foi=CP;Catapulte=EMA;Cérémonie=CP;Charme-personne=BDEMO;Châtiment calcinant=P;Châtiment courroucé=P
Châtiment tonitruant=P;Collet=DRMA;Communication avec les animaux=BDR;Compréhension des langues=BEMO
Couleurs dansantes=BEM;Couteau de glace=DEM;Création ou destruction d'eau=CD;Déguisement=BEMA
Détection de la magie=BCDEMPRA;Détection du mal et du bien=CP;Détection du poison et des maladies=BCDPR
Disque flottant de Tenser=M;Duel forcé=P;Éclair de chaos=E;Éclair traçant=C;Enchevêtrement=DR;Faveur divine=P
Feuille morte=BEMA;Fléau=BC;Fou rire de Tasha=BM;Frappe du zéphyr=R;Frappe piégeuse=R;Frayeur=EMO;Graisse=MA
Grande foulée=BDRMA;Héroïsme=BP;Identification=BMA;Image silencieuse=BEM;Injonction=CP;Lien avec une bête=DR
Lueurs féeriques=BDA;Mains brûlantes=EM;Maléfice=O;Marque du chasseur=R;Mixture caustique de Tasha=EMA
Mot de guérison=BCD;Murmures dissonants=B;Nappe de brouillard=DERM;Orbe chromatique=EM;Projectile élémentaire=EM
Projectile magique=EM;Protection contre le mal et le bien=CMOP;Rayon empoisonné=EM;Repli expéditif=EMOA
Représailles infernales=O;Sanctuaire=CA;Saut=DERMA;Secousse sismique=DEM;Serviteur invisible=BMO
Simulacre de vie=EM;Soins=BCDPRA;Sommeil=BEM;Tentacules de Hadar=O;Texte illusoire=BMO;Trait ensorcelé=EMO
Vague tonnante=BDEM;Vents contraires=DEM
# ---- niveau 2
Agrandissement/Rapetissement=EMA;Aide=CPRA;Amélioration de caractéristique=BCDEA;Apaisement des émotions=BC
Appel de destrier=P;Arme magique=PMA;Arme spirituelle=C;Attraction terrestre=DEMO;Augure=C
Aura magique de Nystul=MA;Bouche magique=BM;Bourrasque=DEM;Cécité/Surdité=BCEM;Châtiment révélateur=P
Convocation de bête=DR;Corde enchantée=M;Cordon de flèches=R;Couronne du dément=BEMO;Croissance d'épines=DR
Déblocage=BEMO;Détection des pensées=BEMO;Discours captivant=B;Entraves de givre=EM;Épine mentale=EMO
Espièglerie de Nathair=BEMO;Esprit guérisseur=DR;Flambée d'Aganazzar=EM;Flamme éternelle=CDMA;Flèche acide de Melf=M
Flou=EMA;Force fantasmagorique=BEM;Fouet mental de Tasha=EM;Foulée brumeuse=EMO;Fracassement=BEMO;Image miroir=BEMO
Immobilisation de personne=BCDEMO;Invisibilité=BEMOA;Lame d'ombres=EMO;Lame de feu=DE;Lévitation=EMA
Libellé aérien=BDEM;Lien de protection=C;Localisation d'animaux ou de plantes=BDR;Localisation d'objet=BCDPRM
Messager animal=BDR;Métal brûlant=BDA;Modification d'apparence=EMA;Nuée de boules de neige de Snilloc=EM
Nuée de dagues=BEMO;Passage sans trace=DR;Pattes d'araignée=EMOA;Peau d'écorce=DR;Poigne terreuse de Maximilien=EM
Préservation des morts=CM;Prière de guérison=CP;Protection contre le poison=CDPRA;Pyrotechnie=BEMA
Rayon affaiblissant=MO;Rayon ardent=EM;Rayon de lune=D;Restauration partielle=BCDPRA;Sens animal=DR
Sens de la distorsion=EM;Sens des pièges=CDR;Silence=BCR;Souffle du dragon=EM;Sphère de feu=DEM;Suggestion=BEM
Ténèbres=EMO;Toile d'araignée=EMA;Tourbillon de poussière=DEM;Vent protecteur=DEM;Verrou magique=M
Vision dans le noir=DEMR;Voir l'invisible=BEM;Zone de vérité=BCP
# ---- niveau 3
Animation des morts=CM;Antidétection=BRM;Appel de la foudre=D;Arme élémentaire=DPA;Aura de vitalité=CDP
Aura du croisé=CP;Boule de feu=EM;Cercle magique=CMOP;Châtiment aveuglant=P;Clairvoyance=BCEM;Clignotement=EMA
Communication à distance=BCM;Communication avec les morts=BC;Communication avec les plantes=BDR;Contresort=EMO
Convocation de démons mineurs=MO;Convocation de fée=DMOR;Convocation de mort-vivant=MO
Convocation de rejeton d'ombre=MO;Création de nourriture et d'eau=CP;Croissance végétale=BDR
Délivrance des malédictions=CMOP;Dissipation de la magie=BCDEMOPA;Don des langues=BCEMO;Éclair=EM
Ennemis à foison=BEMO;Éruption de terre=DEM;Esprits gardiens=C;Flèche de foudre=R;Flèches enflammées=DREM
Forme gazeuse=EMO;Forteresse d'intellect=BEMOA;Foulée d'Ashardalon=EMRA;Foulée tonitruante=EMO
Fusion dans la pierre=CDR;Glyphe de protection=BCMA;Hâte=EMA;Image majeure=BEMO;Invocation d'animaux=DR
Invocation de projectiles=R;Lenteur=EM;Lueur d'espoir=C;Lumière du jour=CDEPR;Malédiction=BCM
Marche sur l'eau=CDERA;Minuscules météores de Melf=EM;Monture fantôme=M;Mort simulée=BCDM
Mot de guérison de groupe=C;Motif hypnotique=BEMO;Mur d'eau=DEM;Mur de sable=M;Mur de vent=DR
Nuage nauséabond=BEM;Petite hutte de Léomund=BM;Peur=BEMO;Protection contre une énergie=CDERMA;Raz-de-marée=DEM
Respiration aquatique=DERMA;Retour à la vie=CPA;Serviteur miniature=MA;Sieste=BEMA;Tempête de neige=DEM
Toucher du vampire=MO;Transfert de vie=CM;Voile spirituel=CMOP;Vol=EMOA;Voracité de Hadar=O
# ---- niveau 4
Appel de destrier supérieur=P;Assassin imaginaire=BM;Aura de pureté=CP;Aura de vie=CP;Bannissement=CEMOP
Bouclier de feu=EM;Charme-monstre=BDEMO;Châtiment débilitant=P;Chien de garde de Mordenkainen=MA
Coffre secret de Léomund=M;Compulsion=B;Confusion=BDEMO;Contrôle de l'eau=CDEM;Convocation d'aberration=MO
Convocation d'artificiel=MA;Convocation d'élémentaire=DM;Convocation de démon majeur=MO;Divination=CDM
Domination de bête=DER;Fabrication=MA;Façonnage de la pierre=CDMA;Fléau élémentaire=DMOA;Flétrissement=DEMO
Gardien de la foi=C;Gardien de la nature=DR;Insecte géant=D;Invisibilité supérieure=BEM
Invocation d'élémentaires mineurs=DM;Invocation d'êtres sylvestres=DR;Invocation d'ombres=MO
Lance d'arçon psychique de Raulothim=BEMO;Liane avide=DR;Liberté de mouvement=BCDRPA;Localisation de créature=BCDPRM
Métamorphose=BDEM;Mur de feu=DEMA;Oeil magique=MA;Ombre d'égarement=O;Peau de pierre=DERMA
Porte dimensionnelle=BEMO;Protection contre la mort=CP;Rayonnement écoeurant=EMO;Sanctuaire privé de Mordenkainen=M
Scellé de portail=M;Sphère aqueuse=DEM;Sphère de tempête=EM;Sphère de vitriol=EM;Sphère résiliente d'Otiluke=MA
Tempête de grêle=DEM;Tentacules noirs d'Evard=M;Terrain hallucinatoire=BDMO
# ---- niveau 5
Amélioration de compétences=BEMA;Animation d'objets=BEM;Apparence trompeuse=BEM;Arme sacrée=CP;Assignation infernale=MO
Aube=CM;Brume mortelle=EM;Carquois magique=R;Cercle de pouvoir=P;Cercle de téléportation=BEM;Châtiment du ban=P
Colonne de flamme=C;Communion=C;Communion avec la nature=DR;Cône de froid=EM;Contact avec un autre plan=MO
Contagion=CD;Contrat=BCDM;Contrôle des vents=DEM;Convocation d'esprit draconique=DEM;Convocation de céleste=CP
Coquille antivie=D;Création=EMA;Danse macabre=MO;Déluge d'énergie négative=MO;Dissipation du mal et du bien=CP
Domination de personne=BEM;Double illusoire=BMO;Énervation=EMO;Éveil=BD;Fléau d'insectes=CDE
Foulée dimensionnelle=EMO;Frappe du vent d'acier=RM;Fureur de la nature=DR;Immobilisation de monstre=BEMO
Immolation=EM;Invocation d'élémentaire=DM;Invocation de volée=R;Lien télépathique de Rary=BM;Maelström=D
Main de Bigby=EMA;Modification de mémoire=BM;Mur de force=M;Mur de lumière=EMO;Mur de pierre=DEMA
Mythes et légendes=BCM;Passage par les arbres=DR;Passe-muraille=M;Perturbations synaptiques=BEMO;Quête=BCDPM
Rappel à la vie=BCP;Réincarnation=D;Restauration supérieure=BCDA;Sanctification=C;Scrutation=BCDMO
Soins de groupe=BCD;Songe=BMO;Télékinésie=EM;Transmutation de la pierre=DMA;Vague destructrice=CP
# ---- niveau 6
Allié planaire=C;Barrière de lames=C;Bosquet des druides=D;Bouclier de platine de Fizban=EM;Cage des âmes=MO
Cercle de mort=EMO;Chaîne d'éclairs=EM;Contamination=C;Convocation de fiélon=MO;Convocations instantanées de Drawmij=M
Costume d'Outremonde de Tasha=EMO;Création d'homoncule=M;Création de mort-vivant=CMO;Danse irrésistible d'Otto=BM
Désintégration=EM;Dispersion=EMO;Festin des héros=CD;Globe d'invulnérabilité=EM;Guérison=CD;Illusion programmée=BM
Interdiction=C;Invocation de fée=DO;Marche sur le vent=D;Mauvais oeil=BEMO;Mot de retour=C;Mur d'épines=D
Mur de glace=M;Ossements de la Terre=D;Pétrification=M;Portail magique=M;Prévoyance=M;Prison mentale=EMO
Protection primordiale=D;Protections et sceaux=BM;Rayon de soleil=CDEM;Sacre de la glace=DEMO
Sacre de la pierre=DEMO;Sacre des flammes=DEMO;Sacre du vent=DEMO;Sens de l'orientation=BCD
Sphère glaciale d'Otiluke=EM;Suggestion de groupe=BEMO;Terraformage=DEM;Transformation de Tenser=M
Urne magique=M;Vision suprême=BCEMO;Voie végétale=D
# ---- niveau 7
Boule de feu à retardement=EM;Cage de force=BMO;Changement de plan=CDEMO;Couronne d'étoiles=EMO;Dissimulation=M
Doigt de mort=EMO;Épée de Mordenkainen=M;Forme éthérée=BCEMO;Inversion de la gravité=DEM;Invocation de céleste=C
Manoir somptueux de Mordenkainen=BM;Mirage=BDM;Mot de pouvoir douloureux=BEMO;Parole divine=C
Projection d'image=BM;Rayons prismatiques=BEM;Régénération=BCD;Résurrection=BC;Simulacre=M
Songe du voile bleu=BMO;Symbole=BCDM;Téléportation=BEM;Tempête de feu=CDE;Temple des dieux=C;Tourbillon=DE
Transformation draconique=DEM
# ---- niveau 8
Aura sacrée=C;Aversion/Attirance=BDM;Bagou=B;Champ antimagie=CM;Clone=M;Contrôle du climat=CDEM;Dédale=M
Demi-plan=MO;Domination de monstre=BEMO;Dragon illusoire=M;Éclat du soleil=DEM;Esprit faible=BDMO
Esprit impénétrable=BM;Flétrissure épouvantable d'Abi-Dalzim=DEM;Formes animales=D;Forteresse majestueuse=M
Mot de pouvoir étourdissant=BEMO;Nuage incendiaire=DEM;Télépathie=M;Ténèbres oppressantes=MO
Tremblement de terre=CDE;Tsunami=D
# ---- niveau 9
Arrêt du temps=EM;Changement de forme=DM;Emprisonnement=MO;Ennemi subconscient=MO;Guérison de groupe=C
Hurlement psychique=BEMO;Invulnérabilité=M;Lame du désastre=EMO;Métamorphose de groupe=BEM
Métamorphose suprême=BMO;Mot de pouvoir guérisseur=BC;Mot de pouvoir mortel=EMO;Mur prismatique=BM
Nuée de météores=EM;Portail=CMO;Prémonition=BDMO;Projection astrale=CMO;Résurrection suprême=CD;Souhait=EM
Tempête vengeresse=D
"""


def build() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in RAW.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for entry in line.split(";"):
            name, letters = entry.rsplit("=", 1)
            out[name.strip()] = [CLS[c] for c in letters.strip()]
    return out


if __name__ == "__main__":
    data = build()
    path = Path(__file__).resolve().parent.parent / "data" / "Sorts_Listes.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"listes_de_classes": data}, fh, ensure_ascii=False, indent=1)
    print(f"{len(data)} sorts -> {path}")
