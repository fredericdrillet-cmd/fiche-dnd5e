"""
Mise à jour v22 du référentiel des espèces (vérifiée sur le Manuel des Joueurs, Xanathar et Tasha).

Retraits : Changeling ténébreux, Demi-dragon, Golem miniature, Harengon (doublon du Conil), Naïade, Orc cendré,
Mort-vivant (doublon du Revenant).

Ajouts (Manuel des Joueurs, p. 23 et suivantes ; règle « origine personnalisée » de Tasha via l'option
« +2 / +1 au choix » de l'onglet Caractéristiques) :
    - Demi-elfe : Cha +2 et +1 à deux autres caractéristiques, vision 18 m, ascendance féerique,
      polyvalence (2 compétences), Commun + Elfique + 1 langue ;
    - Drow : Dex +2, Cha +1, vision supérieure 36 m, sensibilité au soleil, magie drow (Charisme),
      armes drow ; traits elfes communs (ascendance féerique, sens aiguisés, transe) ;
    - Elfe : Dex +2, vision 18 m, ascendance féerique, sens aiguisés, transe ; sous-espèces Haut-elfe (Int +1)
      et Elfe des bois (Sag +1, vitesse 10,5 m).
"""

DARKVISION_18 = ("Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme en "
                 "pénombre. Dans le noir, vous ne distinguez pas les couleurs, seulement des nuances de gris.")
FEY = ("Vous avez l'avantage aux jets de sauvegarde contre l'état charmé, et la magie ne peut pas vous endormir.")
KEEN = "Vous avez la maîtrise de la compétence Perception."
TRANCE = ("Les elfes ne dorment pas : ils méditent profondément, en restant à demi conscients, 4 heures par jour. "
          "Après ce repos, vous obtenez les mêmes bénéfices qu'un humain après 8 heures de sommeil (repos long).")
ELF_WEAPONS = ("Vous avez la maîtrise de l'épée longue, de l'épée courte, de l'arc court et de l'arc long.")

ELFE = {
    "nom": "Elfe",
    "source": "Manuel des Joueurs",
    "caracteristiques": "Dex +2",
    "langues": ["Commun", "Elfique"],
    "capacites": [
        {"nom": "Taille", "description": "Moyenne (1,50 à 1,80 m environ). Vitesse de marche : 9 mètres."},
        {"nom": "Vision dans le noir", "description": DARKVISION_18},
        {"nom": "Ascendance féerique", "description": FEY},
        {"nom": "Sens aiguisés", "description": KEEN},
        {"nom": "Transe", "description": TRANCE},
    ],
    "sous_races": [
        {"nom": "Haut-elfe", "caracteristiques": "Int +1", "langues": ["1 au choix"],
         "capacites": [
             {"nom": "Entraînement aux armes elfiques", "description": ELF_WEAPONS},
             {"nom": "Sort mineur", "description": "Vous connaissez un sort mineur de votre choix de la liste du "
                                                   "magicien (à ajouter via « Sorts accordés » de l'onglet Magie). "
                                                   "L'Intelligence est votre caractéristique d'incantation pour ce sort."},
             {"nom": "Langue supplémentaire", "description": "Vous parlez, lisez et écrivez une langue "
                                                             "supplémentaire de votre choix."}]},
        {"nom": "Elfe des bois", "caracteristiques": "Sag +1", "vitesse": 10.5,
         "capacites": [
             {"nom": "Entraînement aux armes elfiques", "description": ELF_WEAPONS},
             {"nom": "Pied léger", "description": "Votre vitesse de marche de base passe à 10,5 mètres."},
             {"nom": "Cachette naturelle", "description": "Vous pouvez tenter de vous cacher même lorsque vous "
                                                          "n'êtes que légèrement masqué par du feuillage, une forte "
                                                          "pluie, de la neige qui tombe, de la brume ou un autre "
                                                          "phénomène naturel."}]},
    ],
}

DROW = {
    "nom": "Drow (Elfe noir)",
    "source": "Manuel des Joueurs",
    "caracteristiques": "Dex +2, Cha +1",
    "langues": ["Commun", "Elfique"],
    "capacites": [
        {"nom": "Taille", "description": "Moyenne (1,50 à 1,80 m environ). Vitesse de marche : 9 mètres."},
        {"nom": "Vision dans le noir supérieure", "description": "Vous voyez dans la pénombre jusqu'à 36 mètres "
                                                                 "comme en lumière vive, et dans le noir comme en "
                                                                 "pénombre (nuances de gris uniquement)."},
        {"nom": "Ascendance féerique", "description": FEY},
        {"nom": "Sens aiguisés", "description": KEEN},
        {"nom": "Transe", "description": TRANCE},
        {"nom": "Sensibilité au soleil", "description": "Vous avez le désavantage aux jets d'attaque et aux tests "
                                                        "de Sagesse (Perception) basés sur la vue lorsque vous, la "
                                                        "cible de votre attaque ou ce que vous essayez de percevoir "
                                                        "êtes en plein soleil."},
        {"nom": "Magie drow", "description": "Sorts : *Lumières dansantes* (sort mineur) ; *Lueurs féeriques* "
                                             "(niv. 3, 1/repos long) ; *Ténèbres* (niv. 5, 1/repos long). Le "
                                             "Charisme est votre caractéristique d'incantation pour ces sorts."},
        {"nom": "Entraînement aux armes drow", "description": "Vous avez la maîtrise de la rapière, de l'épée "
                                                              "courte et de l'arbalète de poing."},
    ],
}

DEMI_ELFE = {
    "nom": "Demi-elfe",
    "source": "Manuel des Joueurs",
    "caracteristiques": "Cha +2, +1, +1",
    "langues": ["Commun", "Elfique", "1 au choix"],
    "capacites": [
        {"nom": "Taille", "description": "Moyenne (1,50 à 1,80 m environ). Vitesse de marche : 9 mètres."},
        {"nom": "Augmentation de caractéristiques", "description": "Votre Charisme augmente de 2, et deux autres "
                                                                   "caractéristiques de votre choix augmentent de 1."},
        {"nom": "Vision dans le noir", "description": DARKVISION_18},
        {"nom": "Ascendance féerique", "description": FEY},
        {"nom": "Polyvalence", "description": "Vous obtenez la maîtrise de deux compétences de votre choix (à "
                                              "cocher dans l'onglet Compétences)."},
    ],
}

REMOVED = ["Changeling ténébreux", "Demi-dragon", "Golem miniature", "Harengon", "Naïade", "Orc cendré",
           "Mort-vivant", "Elfe sylvestre", "Enfant de la lune"]   # Enfant de la lune = doublon du Féral          # Elfe sylvestre = Elfe des bois (sous-espèce de l'Elfe)

# anciennes fiches : espèce retirée -> (nouvelle espèce, sous-espèce) appliqué au chargement
RENAMED = {"Elfe sylvestre": ("Elfe", "Elfe des bois"), "Harengon": ("Conil", ""), "Mort-vivant": ("Revenant", ""),
           "Enfant de la lune": ("Féral", "")}

FIXES = [{"op": "remove_espece", "espece": n} for n in REMOVED] + [
    {"op": "add_espece", "espece": e["nom"], "entree": e} for e in (DEMI_ELFE, DROW, ELFE)]

# Rapport d'audit (repris dans AUDIT_REGLES.md) : (gravité, objet, constat, correction)
CORRIGE = [
    ("majeur", "Demi-elfe", "Espèce absente (Manuel des Joueurs)",
     "Ajoutée : Cha +2 et +1 à deux AUTRES caractéristiques, vision 18 m, ascendance féerique, polyvalence "
     "(2 compétences), Commun + Elfique + 1 langue"),
    ("majeur", "Drow (Elfe noir)", "Espèce absente (sous-espèce elfe du Manuel des Joueurs)",
     "Ajoutée : Dex +2, Cha +1, vision 36 m, sensibilité au soleil, magie drow (Lumières dansantes, Lueurs "
     "féeriques au niv. 3, Ténèbres au niv. 5, Charisme), rapière / épée courte / arbalète de poing, plus les "
     "traits elfes communs (ascendance féerique, sens aiguisés, transe)"),
    ("majeur", "Elfe", "Espèce de base absente (seules des variantes existaient)",
     "Ajoutée : Dex +2, vision 18 m, ascendance féerique, sens aiguisés, transe ; sous-espèces Haut-elfe (Int +1, "
     "armes elfiques, sort mineur de magicien, langue) et Elfe des bois (Sag +1, vitesse 10,5 m, armes elfiques, "
     "cachette naturelle)"),
    ("mineur", "Harengon / Mort-vivant", "Doublons du Conil et du Revenant", "Retirés"),
    ("mineur", "Enfant de la lune", "Doublon du Féral", "Retiré ; anciennes fiches converties en Féral"),
    ("mineur", "Elfe sylvestre", "Doublon : nom VF de l'Elfe des bois (Wood Elf) du Manuel des Joueurs",
     "Retiré ; l'Elfe des bois est la sous-espèce de l'Elfe"),
    ("mineur", "Changeling ténébreux, Demi-dragon, Golem miniature, Naïade, Orc cendré",
     "Espèces non retenues pour le référentiel", "Retirées"),
]

AUDIT = [
    ("info", "Ascendance féerique (PHB 2014)", "Le PHB parle d'avantage contre le fait d'être charmé et "
     "d'immunité au sommeil magique", "Repris tel quel ; affiché comme trait permanent dans la barre d'états"),
    ("info", "Transe", "4 heures de méditation = bénéfices de 8 heures de sommeil (repos long de 8 h toujours requis "
     "pour ses autres effets)", "Texte du PHB ; aucune automatisation du temps de repos"),
    ("info", "Haut-elfe / sort mineur", "Choix libre dans la liste du magicien", "À ajouter via « Sorts accordés » "
     "(onglet Magie) ; Intelligence"),
    ("info", "Demi-elfe / Polyvalence", "Deux compétences au choix", "À cocher dans l'onglet Compétences"),
    ("info", "Anciennes fiches", "Espèces retirées encore présentes dans des sauvegardes",
     "Converties au chargement : Elfe sylvestre -> Elfe (Elfe des bois), Harengon -> Conil, Mort-vivant -> Revenant"),
    ("info", "Règle de Tasha (origine personnalisée)", "+2 / +1 (ou +1/+1/+1) au choix à la place des bonus fixes",
     "Option « Règle libre » de l'onglet Caractéristiques, valable pour les nouvelles espèces"),
]
