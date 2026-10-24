"""Corrections structurelles — Magicien (issues de l'audit)."""
CLASSE = "Magicien"

_OFFICIELLES = [
    "École d'Abjuration", "École de Divination", "École d'Enchantement", "École d'Évocation", "École d'Illusion",
    "École de l'Invocation", "École de la Nécromancie", "École de la Transmutation", "Magie de guerre",
    "Chantelame", "Ordre des scribes", "Magie de la Chronurgie",
]

FIXES = [
    # --- Classe de base
    {"op": "remove", "sous_classe": None, "nom": "Prospérité des rituels (Optionnel)"},
    {"op": "add", "sous_classe": None, "nom": "Formules de sorts mineurs (option Tasha)", "niveau": 3},
    {"op": "rename", "sous_classe": None, "nom": "Signature magique", "nouveau": "Sorts de prédilection"},
    # --- Noms officiels des aptitudes de tradition
    {"op": "rename", "sous_classe": "École d'Abjuration", "nom": "École projetée", "nouveau": "Égide projetée"},
    {"op": "rename", "sous_classe": "École de Divination", "nom": "Présage renforcé", "nouveau": "Présage supérieur"},
    {"op": "rename", "sous_classe": "École d'Enchantement", "nom": "Détournement d'hostilité", "nouveau": "Charme instinctif"},
    {"op": "rename", "sous_classe": "École d'Enchantement", "nom": "Enchantement bifide", "nouveau": "Enchantement partagé"},
    {"op": "rename", "sous_classe": "École d'Évocation", "nom": "Sort mineur appuyé", "nouveau": "Sort mineur puissant"},
    {"op": "rename", "sous_classe": "École d'Évocation", "nom": "Évocation améliorée", "nouveau": "Évocation renforcée"},
    {"op": "rename", "sous_classe": "École d'Illusion", "nom": "Réalité chimérique", "nouveau": "Réalité illusoire"},
    {"op": "rename", "sous_classe": "École de l'Invocation", "nom": "Permutation", "nouveau": "Transposition bienveillante"},
    {"op": "rename", "sous_classe": "École de l'Invocation", "nom": "Invocation consciencieuse", "nouveau": "Invocation focalisée"},
    {"op": "rename", "sous_classe": "École de l'Invocation", "nom": "Convocations coriaces", "nouveau": "Convocations durables"},
    {"op": "rename", "sous_classe": "École de la Nécromancie", "nom": "Insensibilité à la non-vie", "nouveau": "Endurci contre la non-vie"},
    {"op": "rename", "sous_classe": "École de la Nécromancie", "nom": "Contrôle des morts-vivants", "nouveau": "Commandement des morts-vivants"},
    {"op": "rename", "sous_classe": "Magie de guerre", "nom": "Voile de déviation", "nouveau": "Linceul déflecteur"},
    {"op": "rename", "sous_classe": "Ordre des scribes", "nom": "Érudition réifiée", "nouveau": "Esprit manifesté"},
    {"op": "rename", "sous_classe": "Magie de la Chronurgie", "nom": "Conscience temporelle & Altération du sort",
     "nouveau": "Conscience temporelle & Déphasage chronal"},
    {"op": "rename", "sous_classe": "Magie de la Chronurgie", "nom": "Abri d'arcanes", "nouveau": "Suspension arcanique"},
    {"op": "rename", "sous_classe": "Magie de la Chronurgie", "nom": "Altération convergente", "nouveau": "Avenir convergent"},
    # --- Sources
    {"op": "source", "sous_classe": "Ordre des scribes", "source": "Chaudron des Merveilles de Tasha"},
] + [
    # --- Les traditions arcaniques officielles n'ont pas de liste de sorts de sous-classe
    {"op": "sorts", "sous_classe": s, "sorts": []} for s in _OFFICIELLES
] + [
    # --- Homebrew : noms de sorts corrigés (tous présents dans la base)
    {"op": "sorts", "sous_classe": "Magicien du Sang", "sorts": [
        "Mort simulée", "Frayeur", "Rayon affaiblissant", "Cécité/Surdité", "Toucher du vampire", "Peur",
        "Fléau d'insectes", "Flétrissement", "Domination de monstre", "Énervation"]},
    {"op": "sorts", "sous_classe": "Liaison élémentaire", "sorts": [
        "Mains brûlantes", "Nappe de brouillard", "Rayon ardent", "Sphère de feu", "Boule de feu", "Tempête de grêle",
        "Mur de feu", "Cône de froid", "Colonne de flamme", "Nuée de météores"]},
    {"op": "sorts", "sous_classe": "Gravure runique", "sorts": [
        "Alarme", "Bouclier", "Glyphe de protection", "Arme magique", "Clairvoyance", "Protection contre une énergie",
        "Oeil magique", "Fabrication", "Mur de force", "Création"]},
]
