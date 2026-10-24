"""Corrections structurelles — Occultiste (issues de l'audit)."""
CLASSE = "Occultiste"

_GENIE_COMMUNS = ["Détection du mal et du bien", "Force fantasmagorique", "Création de nourriture et d'eau",
                  "Assassin imaginaire", "Création", "Souhait"]

FIXES = [
    # --- Classe de base ---
    {"op": "rename", "sous_classe": None, "nom": "Maître des arcanes", "nouveau": "Maître de l'occulte"},
    {"op": "add", "sous_classe": None, "nom": "Polyvalence occulte (option Tasha)", "niveau": 4},
    # --- L'Archifée (PHB) ---
    {"op": "sorts", "sous_classe": "L'Archifée",
     "sorts": ["Lueurs féeriques", "Sommeil", "Apaisement des émotions", "Force fantasmagorique", "Clignotement",
               "Croissance végétale", "Domination de bête", "Invisibilité supérieure", "Domination de personne",
               "Apparence trompeuse"]},
    # --- Le Fiélon (PHB) ---
    {"op": "sorts", "sous_classe": "Le Fiélon",
     "sorts": ["Mains brûlantes", "Injonction", "Cécité/Surdité", "Rayon ardent", "Boule de feu",
               "Nuage nauséabond", "Bouclier de feu", "Mur de feu", "Colonne de flamme", "Sanctification"]},
    # --- Le Grand Ancien (PHB) ---
    {"op": "sorts", "sous_classe": "Le Grand Ancien",
     "sorts": ["Murmures dissonants", "Fou rire de Tasha", "Détection des pensées", "Force fantasmagorique",
               "Clairvoyance", "Communication à distance", "Domination de bête", "Tentacules noirs d'Evard",
               "Domination de personne", "Télékinésie"]},
    # --- Le Céleste (XGE) ---
    {"op": "sorts", "sous_classe": "Le Céleste",
     "sorts": ["Soins", "Éclair traçant", "Sphère de feu", "Restauration partielle", "Lumière du jour",
               "Retour à la vie", "Gardien de la foi", "Mur de feu", "Colonne de flamme",
               "Restauration supérieure"]},
    # --- La Lame maudite (XGE) ---
    {"op": "rename", "sous_classe": "La Lame maudite (Magelame)", "nom": "Maître des malédictions",
     "nouveau": "Maître des maléfices"},
    {"op": "sorts", "sous_classe": "La Lame maudite (Magelame)",
     "sorts": ["Bouclier", "Châtiment courroucé", "Flou", "Châtiment révélateur", "Clignotement",
               "Arme élémentaire", "Assassin imaginaire", "Châtiment débilitant", "Châtiment du ban",
               "Cône de froid"]},
    # --- Le Génie (TCE) : sorts propres au type + sorts communs à tous les génies ---
    {"op": "sorts", "sous_classe": "Le Génie (Dao - Terre)",
     "sorts": ["Sanctuaire", "Croissance d'épines", "Fusion dans la pierre", "Façonnage de la pierre",
               "Mur de pierre"] + _GENIE_COMMUNS},
    {"op": "sorts", "sous_classe": "Le Génie (Djinn - Air)",
     "sorts": ["Vague tonnante", "Bourrasque", "Mur de vent", "Invisibilité supérieure",
               "Apparence trompeuse"] + _GENIE_COMMUNS},
    {"op": "sorts", "sous_classe": "Le Génie (Éfrit - Feu)",
     "sorts": ["Mains brûlantes", "Rayon ardent", "Boule de feu", "Bouclier de feu",
               "Colonne de flamme"] + _GENIE_COMMUNS},
    {"op": "sorts", "sous_classe": "Le Génie (Maride - Eau)",
     "sorts": ["Nappe de brouillard", "Flou", "Tempête de neige", "Contrôle de l'eau",
               "Cône de froid"] + _GENIE_COMMUNS},
    # --- L'Insondable (TCE) ---
    {"op": "sorts", "sous_classe": "L'Insondable",
     "sorts": ["Création ou destruction d'eau", "Vague tonnante", "Bourrasque", "Silence", "Éclair",
               "Tempête de neige", "Contrôle de l'eau", "Convocation d'élémentaire", "Main de Bigby",
               "Cône de froid"]},
    # --- Homebrew : noms de sorts invalides remplacés par des sorts thématiques de la base ---
    {"op": "sorts", "sous_classe": "Le Moissonneur",
     "sorts": ["Simulacre de vie", "Rayon empoisonné", "Rayon affaiblissant", "Cécité/Surdité",
               "Animation des morts", "Mort simulée", "Flétrissement", "Protection contre la mort",
               "Brume mortelle", "Contagion"]},
    {"op": "sorts", "sous_classe": "Le Protecteur astral",
     "sorts": ["Lueurs féeriques", "Feuille morte", "Lévitation", "Force fantasmagorique", "Clairvoyance",
               "Clignotement", "Porte dimensionnelle", "Oeil magique", "Télékinésie",
               "Cercle de téléportation"]},
]
