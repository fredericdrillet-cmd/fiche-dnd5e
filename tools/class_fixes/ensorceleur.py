"""Corrections structurelles — Ensorceleur (issues de l'audit)."""
CLASSE = "Ensorceleur"
FIXES = [
    # --- Classe de base : options de Tasha ---
    {"op": "rename", "sous_classe": None, "nom": "Versatilité magique (Optionnel - TCE)",
     "nouveau": "Versatilité magique (option Tasha)"},
    {"op": "niveau", "sous_classe": None, "nom": "Versatilité magique (option Tasha)", "niveau": 4},
    {"op": "add", "sous_classe": None, "nom": "Sorts d'ensorceleur supplémentaires (option Tasha)", "niveau": 1},
    {"op": "add", "sous_classe": None, "nom": "Guidage magique (option Tasha)", "niveau": 5},

    # --- Sous-classes officielles sans liste de sorts étendue ---
    {"op": "sorts", "sous_classe": "Âme divine", "sorts": []},
    {"op": "sorts", "sous_classe": "Magie des ombres", "sorts": []},
    {"op": "sorts", "sous_classe": "Sorcellerie des tempêtes", "sorts": []},

    # --- Esprit aberrant (Tasha) ---
    {"op": "sorts", "sous_classe": "Esprit aberrant", "sorts": [
        "Piqûre mentale", "Tentacules de Hadar", "Murmures dissonants",
        "Apaisement des émotions", "Détection des pensées",
        "Voracité de Hadar", "Communication à distance",
        "Tentacules noirs d'Evard", "Convocation d'aberration",
        "Lien télépathique de Rary", "Télékinésie"]},
    {"op": "rename", "sous_classe": "Esprit aberrant", "nom": "Magie psionique & Défense psychique",
     "nouveau": "Sorcellerie psionique & Défenses psychiques"},
    {"op": "rename", "sous_classe": "Esprit aberrant", "nom": "Distortion implosive",
     "nouveau": "Distorsion implosive"},

    # --- Âme mécanique (Tasha) ---
    {"op": "sorts", "sous_classe": "Âme mécanique", "sorts": [
        "Alarme", "Protection contre le mal et le bien",
        "Aide", "Restauration partielle",
        "Dissipation de la magie", "Protection contre une énergie",
        "Liberté de mouvement", "Convocation d'artificiel",
        "Mur de force", "Restauration supérieure"]},
    {"op": "rename", "sous_classe": "Âme mécanique", "nom": "Équilibre restauré & Sorts d'ordre",
     "nouveau": "Magie mécanique & Rétablir l'équilibre"},
    {"op": "rename", "sous_classe": "Âme mécanique", "nom": "Bastion de loi", "nouveau": "Bastion de la loi"},
    {"op": "rename", "sous_classe": "Âme mécanique", "nom": "Transe harmonique", "nouveau": "Transe d'ordre"},
    {"op": "rename", "sous_classe": "Âme mécanique", "nom": "Chevauchée méca.", "nouveau": "Cavalcade mécanique"},

    # --- Sous-classes homebrew : noms de sorts valides, niveaux 1 à 5 dans l'ordre ---
    {"op": "sorts", "sous_classe": "Lignée du Sang", "sorts": [
        "Fléau", "Frayeur",
        "Rayon affaiblissant", "Cécité/Surdité",
        "Toucher du vampire", "Peur",
        "Flétrissement", "Domination de bête",
        "Contagion", "Fléau d'insectes"]},
    {"op": "sorts", "sous_classe": "Magie Cosmique", "sorts": [
        "Mains brûlantes", "Lueurs féeriques",
        "Rayon ardent", "Lévitation",
        "Boule de feu", "Lumière du jour",
        "Tempête de grêle", "Porte dimensionnelle",
        "Colonne de flamme", "Cercle de téléportation"]},
]
