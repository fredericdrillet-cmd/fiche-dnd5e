"""Corrections structurelles — Druide (issues de l'audit)."""
CLASSE = "Druide"
FIXES = [
    # --- Classe de base : options de Tasha ---
    {"op": "rename", "sous_classe": None, "nom": "Compagnon sauvage (Optionnel)",
     "nouveau": "Compagnon sauvage (option Tasha)"},
    {"op": "add", "sous_classe": None, "nom": "Sorts de druide supplémentaires (option Tasha)", "niveau": 1},
    {"op": "add", "sous_classe": None, "nom": "Polyvalence des sorts mineurs (option Tasha)", "niveau": 4},
    # --- Cercle de la Lune ---
    {"op": "rename", "sous_classe": "Cercle de la Lune", "nom": "Forme sauvage de combat & Guérison sauvage",
     "nouveau": "Forme sauvage de combat & Formes du cercle"},
    {"op": "rename", "sous_classe": "Cercle de la Lune", "nom": "Mille visages", "nouveau": "Mille formes"},
    # --- Cercle de la Terre : un terrain au choix (onglet Classes) ; Forêt par défaut (sorts_domaine) ---
    {"op": "champ", "sous_classe": "Cercle de la Terre", "champ": "terrain_defaut", "valeur": "Forêt"},
    {"op": "champ", "sous_classe": "Cercle de la Terre", "champ": "terrains", "valeur": {
        "Arctique": ["Immobilisation de personne", "Croissance d'épines", "Lenteur", "Tempête de neige",
                     "Liberté de mouvement", "Tempête de grêle", "Communion avec la nature", "Cône de froid"],
        "Côte": ["Image miroir", "Foulée brumeuse", "Respiration aquatique", "Marche sur l'eau",
                 "Contrôle de l'eau", "Liberté de mouvement", "Invocation d'élémentaire", "Scrutation"],
        "Désert": ["Flou", "Silence", "Création de nourriture et d'eau", "Protection contre une énergie",
                   "Flétrissement", "Terrain hallucinatoire", "Fléau d'insectes", "Mur de pierre"],
        "Forêt": ["Peau d'écorce", "Pattes d'araignée", "Appel de la foudre", "Croissance végétale",
                  "Divination", "Liberté de mouvement", "Communion avec la nature", "Passage par les arbres"],
        "Marais": ["Ténèbres", "Flèche acide de Melf", "Marche sur l'eau", "Nuage nauséabond",
                   "Liberté de mouvement", "Localisation de créature", "Fléau d'insectes", "Scrutation"],
        "Montagne": ["Pattes d'araignée", "Croissance d'épines", "Éclair", "Fusion dans la pierre",
                     "Façonnage de la pierre", "Peau de pierre", "Passe-muraille", "Mur de pierre"],
        "Outreterre": ["Pattes d'araignée", "Toile d'araignée", "Forme gazeuse", "Nuage nauséabond",
                       "Invisibilité supérieure", "Façonnage de la pierre", "Brume mortelle", "Fléau d'insectes"],
        "Prairie": ["Invisibilité", "Passage sans trace", "Lumière du jour", "Hâte",
                    "Divination", "Liberté de mouvement", "Songe", "Fléau d'insectes"],
    }},
    {"op": "sorts", "sous_classe": "Cercle de la Terre",
     "sorts": ["Peau d'écorce", "Pattes d'araignée", "Appel de la foudre", "Croissance végétale",
               "Divination", "Liberté de mouvement", "Communion avec la nature", "Passage par les arbres"]},
    # --- Xanathar : pas de sorts de cercle ---
    {"op": "sorts", "sous_classe": "Cercle des Rêves", "sorts": []},
    {"op": "sorts", "sous_classe": "Cercle du Berger", "sorts": []},
    # --- Tasha ---
    {"op": "sorts", "sous_classe": "Cercle des Astres", "sorts": ["Éclair traçant"]},
    {"op": "sorts", "sous_classe": "Cercle des Spores",
     "sorts": ["Cécité/Surdité", "Préservation des morts", "Animation des morts", "Forme gazeuse",
               "Flétrissement", "Confusion", "Brume mortelle", "Contagion"]},
    {"op": "rename", "sous_classe": "Cercle des Fournaises (Wildfire)", "nom": "Cautère spectrale",
     "nouveau": "Flammes cautérisantes"},
    {"op": "sorts", "sous_classe": "Cercle des Fournaises (Wildfire)",
     "sorts": ["Mains brûlantes", "Soins", "Sphère de feu", "Rayon ardent", "Croissance végétale",
               "Retour à la vie", "Aura de vie", "Bouclier de feu", "Colonne de flamme", "Soins de groupe"]},
    # --- Homebrew : noms de sorts invalides ---
    {"op": "sorts", "sous_classe": "Cercle de la Mutation",
     "sorts": ["Simulacre de vie", "Modification d'apparence", "Forme gazeuse", "Métamorphose", "Création",
               "Réincarnation"]},
    {"op": "sorts", "sous_classe": "Cercle de la Sangsue",
     "sorts": ["Frayeur", "Rayon affaiblissant", "Cécité/Surdité", "Toucher du vampire", "Fléau",
               "Flétrissement"]},
]
