"""Corrections structurelles — Artificier (issues de l'audit)."""
CLASSE = "Artificier"
FIXES = [
    # Noms officiels (Chaudron des merveilles de Tasha)
    {"op": "rename", "sous_classe": None, "nom": "Influx d'objet", "nouveau": "Infusion d'objets"},
    {"op": "rename", "sous_classe": None, "nom": "Outil de circonstance", "nouveau": "Le bon outil pour la tâche"},
    {"op": "rename", "sous_classe": None, "nom": "Trait de génie", "nouveau": "Éclair de génie"},
    # Forgeron de guerre : Décharge arcanique obtenue au niveau 9
    {"op": "niveau", "sous_classe": "Forgeur d'armes", "nom": "Décharge arcanique", "niveau": 9},
    # Listes de sorts officielles (Tasha)
    {"op": "sorts", "sous_classe": "Alchimiste", "sorts": [
        "Mot de guérison", "Rayon empoisonné", "Flèche acide de Melf", "Sphère de feu", "Forme gazeuse",
        "Mot de guérison de groupe", "Flétrissement", "Protection contre la mort", "Brume mortelle",
        "Rappel à la vie"]},
    {"op": "sorts", "sous_classe": "Armurier", "sorts": [
        "Projectile magique", "Vague tonnante", "Image miroir", "Fracassement", "Motif hypnotique", "Éclair",
        "Bouclier de feu", "Invisibilité supérieure", "Passe-muraille", "Mur de force"]},
    {"op": "sorts", "sous_classe": "Artilleur", "sorts": [
        "Bouclier", "Vague tonnante", "Rayon ardent", "Fracassement", "Boule de feu", "Mur de vent",
        "Tempête de grêle", "Mur de feu", "Cône de froid", "Mur de force"]},
    {"op": "sorts", "sous_classe": "Forgeur d'armes", "sorts": [
        "Héroïsme", "Bouclier", "Châtiment révélateur", "Lien de protection", "Aura de vitalité",
        "Invocation de projectiles", "Aura de pureté", "Bouclier de feu", "Châtiment du ban", "Soins de groupe"]},
    # Sous-classes communautaires : noms anglais / inexistants remplacés par des sorts valides de la base
    {"op": "sorts", "sous_classe": "Automaturge", "sorts": [
        "Alarme", "Détection de la magie", "Sens des pièges", "Lévitation", "Clairvoyance", "Serviteur miniature",
        "Oeil magique", "Façonnage de la pierre", "Création", "Mur de force"]},
    {"op": "sorts", "sous_classe": "Cartomancien", "sorts": [
        "Murmures dissonants", "Image silencieuse", "Augure", "Localisation d'objet", "Clignotement",
        "Image majeure", "Oeil magique", "Confusion", "Quête", "Scrutation"]},
    {"op": "sorts", "sous_classe": "Horloger", "sorts": [
        "Grande foulée", "Sanctuaire", "Flou", "Apaisement des émotions", "Hâte", "Lenteur",
        "Liberté de mouvement", "Porte dimensionnelle", "Immobilisation de monstre", "Passe-muraille"]},
]
