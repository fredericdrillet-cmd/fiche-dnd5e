"""Corrections structurelles — Rodeur (issues de l'audit)."""
CLASSE = "Rodeur"

# Les listes de sorts du rôdeur restent au format « paires » (nom, palier 1 à 5) lu par Engine.domain_spells :
# palier 1 = niveau de rôdeur 3, 2 = 5, 3 = 9, 4 = 13, 5 = 17.
FIXES = [
    # ---------------------------------------------------------------- classe de base : noms officiels (PHB)
    {"op": "rename", "sous_classe": None, "nom": "Ennemi juré / Explorateur passionné (Optionnel)",
     "nouveau": "Ennemi juré"},
    {"op": "rename", "sous_classe": None, "nom": "Explorateur natif / Explorateur habile (Optionnel)",
     "nouveau": "Explorateur-né"},
    {"op": "rename", "sous_classe": None, "nom": "Vigilance arcanique / Conscience de la nature",
     "nouveau": "Conscience primitive"},
    {"op": "rename", "sous_classe": None, "nom": "Camouflage / Invisibilité temporelle (Optionnel)",
     "nouveau": "Camouflage"},
    {"op": "rename", "sous_classe": None, "nom": "Sens des bêtes", "nouveau": "Sens sauvages"},
    # améliorations d'Ennemi juré / Explorateur-né (PHB)
    {"op": "add", "sous_classe": None, "nom": "Ennemi juré et Explorateur-né (améliorations)", "niveau": 6},
    {"op": "add", "sous_classe": None, "nom": "Explorateur-né (amélioration)", "niveau": 10},
    {"op": "add", "sous_classe": None, "nom": "Ennemi juré (amélioration)", "niveau": 14},
    # options de classe du Chaudron des merveilles de Tasha
    {"op": "add", "sous_classe": None, "nom": "Ennemi favori (option Tasha)", "niveau": 1},
    {"op": "add", "sous_classe": None, "nom": "Explorateur expert (option Tasha)", "niveau": 1},
    {"op": "add", "sous_classe": None, "nom": "Focaliseur d'incantation (option Tasha)", "niveau": 2},
    {"op": "add", "sous_classe": None, "nom": "Conscience primordiale (option Tasha)", "niveau": 3},
    {"op": "add", "sous_classe": None, "nom": "Polyvalence martiale (option Tasha)", "niveau": 4},
    {"op": "add", "sous_classe": None, "nom": "Vagabond (option Tasha)", "niveau": 6},
    {"op": "add", "sous_classe": None, "nom": "Infatigable (option Tasha)", "niveau": 10},
    {"op": "add", "sous_classe": None, "nom": "Voile de la nature (option Tasha)", "niveau": 10},

    # ---------------------------------------------------------------- Maître des bêtes (PHB / Tasha)
    {"op": "rename", "sous_classe": "Maître des bêtes", "nom": "Compagnon du rôdeur / Compagnon primordial",
     "nouveau": "Compagnon du rôdeur"},
    {"op": "add", "sous_classe": "Maître des bêtes", "nom": "Compagnon primal (option Tasha)", "niveau": 3},
    {"op": "rename", "sous_classe": "Maître des bêtes", "nom": "Entraînement exceptionnel & Attaque de la bête magique",
     "nouveau": "Entraînement exceptionnel"},
    {"op": "rename", "sous_classe": "Maître des bêtes", "nom": "Lien partagé", "nouveau": "Partage des sorts"},

    # ---------------------------------------------------------------- Traqueur des ténèbres (Xanathar)
    {"op": "rename", "sous_classe": "Traqueur des ténèbres", "nom": "Embuscade effrayante & Vision des ombres",
     "nouveau": "Embusqué redoutable"},
    {"op": "add", "sous_classe": "Traqueur des ténèbres", "nom": "Magie du traqueur des ténèbres", "niveau": 3},
    {"op": "add", "sous_classe": "Traqueur des ténèbres", "nom": "Vision des ombres", "niveau": 3},
    {"op": "rename", "sous_classe": "Traqueur des ténèbres", "nom": "Mental d'acier", "nouveau": "Esprit de fer"},
    {"op": "sorts", "sous_classe": "Traqueur des ténèbres",
     "sorts": ["Déguisement", "1", "Corde enchantée", "2", "Peur", "3", "Invisibilité supérieure", "4",
               "Apparence trompeuse", "5"]},

    # ---------------------------------------------------------------- Arpenteur de l'horizon (Xanathar)
    {"op": "rename", "sous_classe": "Arpenteur de l'horizon", "nom": "Détection de portail & Guerrier planaire",
     "nouveau": "Guerrier planaire"},
    {"op": "add", "sous_classe": "Arpenteur de l'horizon", "nom": "Magie de l'arpenteur de l'horizon", "niveau": 3},
    {"op": "add", "sous_classe": "Arpenteur de l'horizon", "nom": "Détection de portail", "niveau": 3},
    {"op": "sorts", "sous_classe": "Arpenteur de l'horizon",
     "sorts": ["Protection contre le mal et le bien", "1", "Foulée brumeuse", "2", "Hâte", "3", "Bannissement", "4",
               "Cercle de téléportation", "5"]},

    # ---------------------------------------------------------------- Tueur de monstres (Xanathar)
    {"op": "rename", "sous_classe": "Tueur de monstres", "nom": "Sens du chasseur & Proie du tueur",
     "nouveau": "Proie du tueur"},
    {"op": "add", "sous_classe": "Tueur de monstres", "nom": "Magie du tueur de monstres", "niveau": 3},
    {"op": "add", "sous_classe": "Tueur de monstres", "nom": "Sens du chasseur", "niveau": 3},
    {"op": "sorts", "sous_classe": "Tueur de monstres",
     "sorts": ["Protection contre le mal et le bien", "1", "Zone de vérité", "2", "Cercle magique", "3",
               "Bannissement", "4", "Immobilisation de monstre", "5"]},

    # ---------------------------------------------------------------- Gardien de l'essaim (Tasha) — nom de sous-classe conservé
    {"op": "rename", "sous_classe": "Gardien des nuées", "nom": "Magie de la nuée & Nuée magique",
     "nouveau": "Essaim rassemblé"},
    {"op": "add", "sous_classe": "Gardien des nuées", "nom": "Magie du gardien de l'essaim", "niveau": 3},
    {"op": "rename", "sous_classe": "Gardien des nuées", "nom": "Nuée spirituelle", "nouveau": "Essaim puissant"},
    {"op": "rename", "sous_classe": "Gardien des nuées", "nom": "Dispersion de la nuée",
     "nouveau": "Dispersion de l'essaim"},
    {"op": "sorts", "sous_classe": "Gardien des nuées",
     "sorts": ["Main de mage", "1", "Lueurs féeriques", "1", "Toile d'araignée", "2", "Forme gazeuse", "3",
               "Oeil magique", "4", "Fléau d'insectes", "5"]},

    # ---------------------------------------------------------------- Vagabond féerique (Tasha) — nom de sous-classe conservé
    {"op": "rename", "sous_classe": "Vagabond féérique", "nom": "Charme mystique & Don des fées",
     "nouveau": "Frappes redoutables"},
    {"op": "add", "sous_classe": "Vagabond féérique", "nom": "Magie du vagabond féerique", "niveau": 3},
    {"op": "add", "sous_classe": "Vagabond féérique", "nom": "Charme de l'autre monde", "niveau": 3},
    {"op": "rename", "sous_classe": "Vagabond féérique", "nom": "Fascination détournée",
     "nouveau": "Torsion envoûtante"},
    {"op": "rename", "sous_classe": "Vagabond féérique", "nom": "Coups effroyables & Renforts féériques",
     "nouveau": "Renforts féeriques"},
    {"op": "sorts", "sous_classe": "Vagabond féérique",
     "sorts": ["Charme-personne", "1", "Foulée brumeuse", "2", "Dissipation de la magie", "3",
               "Porte dimensionnelle", "4", "Double illusoire", "5"]},

    # ---------------------------------------------------------------- sous-classes communautaires : sorts valides
    {"op": "sorts", "sous_classe": "Traqueur de sang",
     "sorts": ["Frayeur", "1", "Rayon affaiblissant", "2", "Toucher du vampire", "3", "Flétrissement", "4",
               "Contagion", "5"]},
    {"op": "sorts", "sous_classe": "Artisan des pièges",
     "sorts": ["Alarme", "1", "Immobilisation de personne", "2", "Glyphe de protection", "3", "Fabrication", "4",
               "Mur de force", "5"]},
]
