"""Mise à jour v25 : Humain et Humain variant réalignés sur le Manuel des Joueurs (traits explicites)."""

FIXES = [
    {"op": "set", "espece": "Humain", "champ": "caracteristiques", "valeur": "Toutes +1"},
    {"op": "trait", "espece": "Humain", "nom": "Augmentation de caractéristiques",
     "description": "Toutes vos valeurs de caractéristiques augmentent de 1."},
    {"op": "trait", "espece": "Humain", "nom": "Langues",
     "description": "Vous parlez, lisez et écrivez le commun et une langue supplémentaire de votre choix."},
    {"op": "set", "espece": "Humain variant", "champ": "caracteristiques", "valeur": "+1, +1"},
    {"op": "trait", "espece": "Humain variant", "nom": "Augmentation de caractéristiques",
     "description": "Deux valeurs de caractéristiques différentes de votre choix augmentent de 1 (à répartir dans "
                    "l'onglet Caractéristiques, section Bonus raciaux)."},
    {"op": "trait", "espece": "Humain variant", "nom": "Compétence",
     "description": "Vous obtenez la maîtrise d'une compétence de votre choix (à cocher dans l'onglet Compétences)."},
    {"op": "trait", "espece": "Humain variant", "nom": "Don",
     "description": "Vous obtenez un don de votre choix : emplacement « Humain variant — don de départ » de "
                    "l'onglet Progression, dons (ses bonus s'appliquent automatiquement)."},
]

CORRIGE = [
    ("mineur", "Humain variant", "Affichait « aucun bonus » tant que les +1 n'étaient pas répartis ; don et "
     "compétence sans effet", "+1 / +1 sur deux caractéristiques différentes, emplacement de don, rappel de la "
     "compétence à choisir"),
    ("mineur", "Humain", "Aucun trait listé (le panneau gardait les traits de la race précédente)",
     "Traits « Augmentation de caractéristiques » et « Langues »"),
]
AUDIT: list = []
