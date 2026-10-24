"""Corrections structurelles — Roublard (issues de l'audit)."""
CLASSE = "Roublard"
FIXES = [
    # Classe de base : noms officiels (PHB / Tasha)
    {"op": "rename", "sous_classe": None, "nom": "Attaque sournoise (1d6)", "nouveau": "Attaque sournoise"},
    {"op": "rename", "sous_classe": None, "nom": "Visée constante (Optionnel - TCE)",
     "nouveau": "Visée stable (option Tasha)"},
    {"op": "rename", "sous_classe": None, "nom": "Sens aveugle", "nouveau": "Perception aveugle"},
    {"op": "rename", "sous_classe": None, "nom": "Elusif", "nouveau": "Insaisissable"},
    # Arnaqueur arcanique (PHB) : nom officiel, pas de liste de sorts imposée
    {"op": "rename", "sous_classe": "Arnaqueur arcanique", "nom": "Omniprésence", "nouveau": "Escroquerie polyvalente"},
    {"op": "sorts", "sous_classe": "Arnaqueur arcanique", "sorts": []},
    # Bretteur (Xanathar) : faute d'accord
    {"op": "rename", "sous_classe": "Bretteur (Swashbuckler)",
     "nom": "Jeu de jambes sophistiqués & Audace désinvolte",
     "nouveau": "Jeu de jambes sophistiqué & Audace désinvolte"},
    # Fantôme (Tasha) : aptitude de niveau 9 sous son nom officiel
    {"op": "rename", "sous_classe": "Fantôme (Phantom)", "nom": "Bribes funèbres (Jetons d'âme)",
     "nouveau": "Bribes des défunts"},
    {"op": "niveau", "sous_classe": "Fantôme (Phantom)", "nom": "Bribes des défunts", "niveau": 9},
    # Lame d'ombre (homebrew) : liste nettoyée (entrées numériques, sort inexistant), sorts de niveau 1 à 5
    {"op": "sorts", "sous_classe": "Lame d'ombre",
     "sorts": ["Nappe de brouillard", "Flou", "Forme gazeuse", "Invisibilité supérieure", "Double illusoire"]},
]
