"""Corrections structurelles — Paladin (issues de l'audit)."""
CLASSE = "Paladin"
FIXES = [
    # --- Classe de base ---
    {"op": "rename", "sous_classe": None, "nom": "Focaliseur de châtiment (Optionnel - TCE)",
     "nouveau": "Exploitation du pouvoir divin (option Tasha)"},
    {"op": "add", "sous_classe": None, "nom": "Polyvalence martiale (option Tasha)", "niveau": 4},
    {"op": "rename", "sous_classe": None, "nom": "Toucher purificateur", "nouveau": "Contact purifiant"},
    {"op": "remove", "sous_classe": None, "nom": "Champion sacré"},

    # --- Serment de Dévotion (PHB) ---
    {"op": "sorts", "sous_classe": "Serment de Dévotion", "sorts": [
        "Protection contre le mal et le bien", "Sanctuaire",
        "Restauration partielle", "Zone de vérité",
        "Lueur d'espoir", "Dissipation de la magie",
        "Liberté de mouvement", "Gardien de la foi",
        "Communion", "Colonne de flamme"]},
    {"op": "rename", "sous_classe": "Serment de Dévotion", "nom": "Nimbe sacrée", "nouveau": "Nimbe sacré"},

    # --- Serment des Anciens (PHB) ---
    {"op": "sorts", "sous_classe": "Serment des Anciens", "sorts": [
        "Frappe piégeuse", "Communication avec les animaux",
        "Rayon de lune", "Foulée brumeuse",
        "Croissance végétale", "Protection contre une énergie",
        "Tempête de grêle", "Peau de pierre",
        "Communion avec la nature", "Passage par les arbres"]},

    # --- Serment de Vengeance (PHB) ---
    {"op": "sorts", "sous_classe": "Serment de Vengeance", "sorts": [
        "Fléau", "Marque du chasseur",
        "Immobilisation de personne", "Foulée brumeuse",
        "Hâte", "Protection contre une énergie",
        "Bannissement", "Porte dimensionnelle",
        "Immobilisation de monstre", "Scrutation"]},

    # --- Serment de Conquête (Xanathar) ---
    {"op": "sorts", "sous_classe": "Serment de Conquête", "sorts": [
        "Armure d'Agathys", "Injonction",
        "Immobilisation de personne", "Arme spirituelle",
        "Malédiction", "Peur",
        "Domination de bête", "Peau de pierre",
        "Brume mortelle", "Domination de personne"]},

    # --- Serment de Rédemption (Xanathar) ---
    {"op": "sorts", "sous_classe": "Serment de Rédemption", "sorts": [
        "Sanctuaire", "Sommeil",
        "Apaisement des émotions", "Immobilisation de personne",
        "Contresort", "Motif hypnotique",
        "Sphère résiliente d'Otiluke", "Peau de pierre",
        "Immobilisation de monstre", "Mur de force"]},
    {"op": "rename", "sous_classe": "Serment de Rédemption", "nom": "Aura de sacrifice", "nouveau": "Aura du gardien"},
    {"op": "rename", "sous_classe": "Serment de Rédemption", "nom": "Protection spirituelle",
     "nouveau": "Esprit protecteur"},

    # --- Serment de la Gloire (Tasha) ---
    {"op": "sorts", "sous_classe": "Serment de la Gloire", "sorts": [
        "Éclair traçant", "Héroïsme",
        "Amélioration de caractéristique", "Arme magique",
        "Hâte", "Protection contre une énergie",
        "Compulsion", "Liberté de mouvement",
        "Communion", "Colonne de flamme"]},
    {"op": "rename", "sous_classe": "Serment de la Gloire", "nom": "Aura d'entrain", "nouveau": "Aura d'alacrité"},

    # --- Serment des Guetteurs (Tasha) ---
    {"op": "source", "sous_classe": "Serment des Guetteurs", "source": "Chaudron des Merveilles de Tasha"},
    {"op": "sorts", "sous_classe": "Serment des Guetteurs", "sorts": [
        "Alarme", "Détection de la magie",
        "Rayon de lune", "Voir l'invisible",
        "Contresort", "Antidétection",
        "Aura de vie", "Bannissement",
        "Immobilisation de monstre", "Scrutation"]},
    {"op": "rename", "sous_classe": "Serment des Guetteurs",
     "nom": "Conduit divin : Aplomb du guetteur & Conjuration d'extraplanaire",
     "nouveau": "Conduit divin : Volonté du guetteur & Abjuration de l'extraplanaire"},

    # --- Serment du Sang (homebrew) : sorts officiels, niveaux 1/2/3/4/5 aux niveaux 3/5/9/13/17 ---
    {"op": "sorts", "sous_classe": "Serment du Sang", "sorts": [
        "Frayeur", "Fléau",
        "Rayon affaiblissant", "Cécité/Surdité",
        "Toucher du vampire", "Peur",
        "Flétrissement", "Confusion",
        "Contagion", "Fléau d'insectes"]},

    # --- Serment des Cendres (homebrew) : sorts officiels, niveaux 1/2/3/4/5 aux niveaux 3/5/9/13/17 ---
    {"op": "sorts", "sous_classe": "Serment des Cendres", "sorts": [
        "Mains brûlantes", "Châtiment calcinant",
        "Rayon ardent", "Sphère de feu",
        "Boule de feu", "Châtiment aveuglant",
        "Mur de feu", "Bouclier de feu",
        "Colonne de flamme", "Immolation"]},
]
