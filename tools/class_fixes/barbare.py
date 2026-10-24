"""Corrections structurelles — Barbare (issues de l'audit)."""
CLASSE = "Barbare"
FIXES = [
    # Options de classe du Chaudron des merveilles de Tasha
    {"op": "add", "sous_classe": None, "nom": "Connaissance primitive (option Tasha)", "niveau": 3},
    {"op": "add", "sous_classe": None, "nom": "Bond instinctif (option Tasha)", "niveau": 7},
    # Aptitudes de niveau 3 manquantes des sous-classes officielles
    {"op": "add", "sous_classe": "Voie totémique - Ours", "nom": "Chercheur spirituel", "niveau": 3},
    {"op": "add", "sous_classe": "Voie totémique - Aigle", "nom": "Chercheur spirituel", "niveau": 3},
    {"op": "add", "sous_classe": "Voie totémique - Loup", "nom": "Chercheur spirituel", "niveau": 3},
    {"op": "add", "sous_classe": "Voie du Zélote", "nom": "Guerrier des dieux", "niveau": 3},
]
