"""Corrections structurelles — Barde (issues de l'audit)."""
CLASSE = "Barde"
FIXES = [
    # Classe de base : niveaux 14 et 18 de Secrets magiques (le PHB répète simplement l'aptitude)
    {"op": "rename", "sous_classe": None, "nom": "Secrets magiques supplémentaires",
     "nouveau": "Secrets magiques (niveau 14)"},
    {"op": "rename", "sous_classe": None, "nom": "Secrets magiques ultimes",
     "nouveau": "Secrets magiques (niveau 18)"},
    # Capacités de classe optionnelles (Chaudron des merveilles de Tasha)
    {"op": "add", "sous_classe": None, "nom": "Sorts de barde supplémentaires (option Tasha)", "niveau": 1},
    {"op": "add", "sous_classe": None, "nom": "Inspiration magique (option Tasha)", "niveau": 2},
    {"op": "add", "sous_classe": None, "nom": "Polyvalence bardique (option Tasha)", "niveau": 4},
    # Noms officiels des aptitudes de sous-classe
    {"op": "rename", "sous_classe": "Collège de la Vaillance", "nom": "Maîtrises supérieures",
     "nouveau": "Maîtrises supplémentaires"},
    {"op": "rename", "sous_classe": "Collège des Épées", "nom": "Maîtrises supérieures",
     "nouveau": "Maîtrises supplémentaires"},
    # Collèges de Xanathar : aucune liste de sorts officielle
    {"op": "sorts", "sous_classe": "Collège de la Séduction", "sorts": []},
    {"op": "sorts", "sous_classe": "Collège des Épées", "sorts": []},
    {"op": "sorts", "sous_classe": "Collège des Murmures", "sorts": []},
    # Collèges communautaires : sorts invalides remplacés par des sorts de la base, de niveau équivalent
    {"op": "sorts", "sous_classe": "Collège des Commandants",
     "sorts": ["Bénédiction", "Héroïsme", "Aide", "Injonction", "Clairvoyance", "Esprits gardiens",
               "Divination", "Liberté de mouvement", "Communion", "Quête"]},
    {"op": "sorts", "sous_classe": "Collège de la Discorde",
     "sorts": ["Vague tonnante", "Frayeur", "Fracassement", "Silence", "Appel de la foudre", "Peur",
               "Tempête de grêle", "Confusion", "Vague destructrice", "Perturbations synaptiques"]},
]
