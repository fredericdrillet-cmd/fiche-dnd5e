"""Corrections structurelles — Moine (issues de l'audit)."""
CLASSE = "Moine"
FIXES = [
    # Classe de base : noms officiels (PHB VF)
    {"op": "rename", "sous_classe": None, "nom": "Ki / Énergie spirituelle", "nouveau": "Ki"},
    {"op": "rename", "sous_classe": None, "nom": "Chute lente", "nouveau": "Chute ralentie"},
    {"op": "rename", "sous_classe": None, "nom": "Évasion", "nouveau": "Dérobade"},
    # Capacités de classe optionnelles (Tasha)
    {"op": "add", "sous_classe": None, "nom": "Arme dédiée (option Tasha)", "niveau": 2},
    {"op": "add", "sous_classe": None, "nom": "Attaque alimentée par le ki (option Tasha)", "niveau": 3},
    {"op": "add", "sous_classe": None, "nom": "Guérison accélérée (option Tasha)", "niveau": 4},
    {"op": "add", "sous_classe": None, "nom": "Visée concentrée (option Tasha)", "niveau": 5},
    # Voie de la Main ouverte (nom de sous-classe conservé) : pas de liste de sorts officielle
    {"op": "sorts", "sous_classe": "Voie de la Paume", "sorts": []},
    # Voie des Quatre Éléments : aptitude de niveau 5 inventée ; sorts réellement lancés par les disciplines
    {"op": "remove", "sous_classe": "Voie des Quatre Éléments", "nom": "Incantation élémentaire renforcée"},
    {"op": "sorts", "sous_classe": "Voie des Quatre Éléments", "sorts": [
        "Mains brûlantes", "Vague tonnante", "Immobilisation de personne", "Bourrasque", "Fracassement",
        "Boule de feu", "Forme gazeuse", "Vol", "Cône de froid", "Peau de pierre", "Mur de feu", "Mur de pierre",
    ]},
    # Voie du Sang (homebrew) : noms de sorts invalides remplacés par des sorts de la base
    {"op": "sorts", "sous_classe": "Voie du Sang", "sorts": ["Rayon affaiblissant", "Toucher du vampire"]},
]
