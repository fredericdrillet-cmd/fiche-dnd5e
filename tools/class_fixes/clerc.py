"""Corrections structurelles — Clerc (issues de l'audit)."""
CLASSE = "Clerc"

_PHB = "Manuel des Joueurs (PHB)"
_XGE = "Xanathar's Guide to Everything (XGE)"
_TCE = "Tasha's Cauldron of Everything (TCE)"

FIXES = [
    # ---------------------------------------------------------------- classe de base
    # Faute de frappe « Détruction » -> « Destruction »
    {"op": "rename", "sous_classe": None, "nom": "Détruction des morts-vivants (FP 1/2)",
     "nouveau": "Destruction des morts-vivants (FP 1/2)"},
    {"op": "rename", "sous_classe": None, "nom": "Détruction des morts-vivants (FP 1)",
     "nouveau": "Destruction des morts-vivants (FP 1)"},
    {"op": "rename", "sous_classe": None, "nom": "Détruction des morts-vivants (FP 2)",
     "nouveau": "Destruction des morts-vivants (FP 2)"},
    {"op": "rename", "sous_classe": None, "nom": "Détruction des morts-vivants (FP 3)",
     "nouveau": "Destruction des morts-vivants (FP 3)"},
    {"op": "rename", "sous_classe": None, "nom": "Détruction des morts-vivants (FP 4)",
     "nouveau": "Destruction des morts-vivants (FP 4)"},
    # Aptitudes de domaine dupliquées dans la classe de base (déjà présentes dans chaque domaine)
    {"op": "remove", "sous_classe": None, "nom": "Frappe divine / Incantation puissante"},
    {"op": "remove", "sous_classe": None, "nom": "Frappe divine améliorée"},
    # Options de classe du Chaudron des merveilles de Tasha
    {"op": "add", "sous_classe": None, "nom": "Sorts de clerc supplémentaires (option Tasha)", "niveau": 1},
    {"op": "add", "sous_classe": None, "nom": "Conduit divin : Canalisation de puissance divine (option Tasha)",
     "niveau": 2},
    {"op": "add", "sous_classe": None, "nom": "Sorts mineurs polyvalents (option Tasha)", "niveau": 4},
    {"op": "add", "sous_classe": None, "nom": "Frappes bénies (option Tasha)", "niveau": 8},

    # ---------------------------------------------------------------- Domaine de la Guerre (PHB)
    {"op": "rename", "sous_classe": "Domaine de la Guerre", "nom": "Conduit divin : Dieu de la guerre",
     "nouveau": "Conduit divin : Bénédiction du dieu de la guerre"},
    {"op": "niveau", "sous_classe": "Domaine de la Guerre", "nom": "Conduit divin : Bénédiction du dieu de la guerre",
     "niveau": 6},
    {"op": "rename", "sous_classe": "Domaine de la Guerre", "nom": "Impact divin", "nouveau": "Frappe divine"},
    {"op": "sorts", "sous_classe": "Domaine de la Guerre",
     "sorts": ["Faveur divine", "Bouclier de la foi", "Arme magique", "Arme spirituelle", "Aura du croisé",
               "Esprits gardiens", "Liberté de mouvement", "Peau de pierre", "Colonne de flamme",
               "Immobilisation de monstre"]},
    {"op": "source", "sous_classe": "Domaine de la Guerre", "source": _PHB},

    # ---------------------------------------------------------------- Domaine de la Lumière (PHB)
    {"op": "rename", "sous_classe": "Domaine de la Lumière", "nom": "Illumination améliorée",
     "nouveau": "Illumination protectrice améliorée"},
    {"op": "rename", "sous_classe": "Domaine de la Lumière", "nom": "Auréole", "nouveau": "Couronne de lumière"},
    {"op": "sorts", "sous_classe": "Domaine de la Lumière",
     "sorts": ["Mains brûlantes", "Lueurs féeriques", "Sphère de feu", "Rayon ardent", "Boule de feu",
               "Lumière du jour", "Gardien de la foi", "Mur de feu", "Colonne de flamme", "Scrutation"]},
    {"op": "source", "sous_classe": "Domaine de la Lumière", "source": _PHB},

    # ---------------------------------------------------------------- Domaine de la Nature (PHB)
    {"op": "rename", "sous_classe": "Domaine de la Nature", "nom": "Conduit divin : Cordialité avec la faune et la flore",
     "nouveau": "Conduit divin : Charme des animaux et des plantes"},
    {"op": "rename", "sous_classe": "Domaine de la Nature", "nom": "Impact divin", "nouveau": "Frappe divine"},
    {"op": "sorts", "sous_classe": "Domaine de la Nature",
     "sorts": ["Amitié avec les animaux", "Communication avec les animaux", "Peau d'écorce", "Croissance d'épines",
               "Croissance végétale", "Mur de vent", "Domination de bête", "Liane avide", "Fléau d'insectes",
               "Passage par les arbres"]},
    {"op": "source", "sous_classe": "Domaine de la Nature", "source": _PHB},

    # ---------------------------------------------------------------- Domaine de la Ruse (PHB)
    {"op": "rename", "sous_classe": "Domaine de la Ruse", "nom": "Faveur du filou", "nouveau": "Bénédiction du filou"},
    {"op": "rename", "sous_classe": "Domaine de la Ruse", "nom": "Impact divin", "nouveau": "Frappe divine"},
    {"op": "sorts", "sous_classe": "Domaine de la Ruse",
     "sorts": ["Charme-personne", "Déguisement", "Image miroir", "Passage sans trace", "Clignotement",
               "Dissipation de la magie", "Porte dimensionnelle", "Métamorphose", "Domination de personne",
               "Modification de mémoire"]},
    {"op": "source", "sous_classe": "Domaine de la Ruse", "source": _PHB},

    # ---------------------------------------------------------------- Domaine du Savoir (PHB)
    {"op": "rename", "sous_classe": "Domaine du Savoir", "nom": "Faveur érudite", "nouveau": "Bénédictions du savoir"},
    {"op": "rename", "sous_classe": "Domaine du Savoir", "nom": "Conduit divin : Savoir ancestral",
     "nouveau": "Conduit divin : Savoir des âges"},
    {"op": "sorts", "sous_classe": "Domaine du Savoir",
     "sorts": ["Injonction", "Identification", "Augure", "Suggestion", "Antidétection", "Communication avec les morts",
               "Oeil magique", "Confusion", "Mythes et légendes", "Scrutation"]},
    {"op": "source", "sous_classe": "Domaine du Savoir", "source": _PHB},

    # ---------------------------------------------------------------- Domaine de la Tempête (PHB)
    {"op": "rename", "sous_classe": "Domaine de la Tempête", "nom": "Choc foudroyant", "nouveau": "Frappe de l'éclair"},
    {"op": "rename", "sous_classe": "Domaine de la Tempête", "nom": "Impact divin", "nouveau": "Frappe divine"},
    {"op": "rename", "sous_classe": "Domaine de la Tempête", "nom": "Enfant de la tempête",
     "nouveau": "Né de la tempête"},
    {"op": "sorts", "sous_classe": "Domaine de la Tempête",
     "sorts": ["Nappe de brouillard", "Vague tonnante", "Bourrasque", "Fracassement", "Appel de la foudre",
               "Tempête de neige", "Contrôle de l'eau", "Tempête de grêle", "Vague destructrice", "Fléau d'insectes"]},
    {"op": "source", "sous_classe": "Domaine de la Tempête", "source": _PHB},

    # ---------------------------------------------------------------- Domaine de la Vie (PHB)
    {"op": "rename", "sous_classe": "Domaine de la Vie", "nom": "Conduit divin : Survivance",
     "nouveau": "Conduit divin : Préservation de la vie"},
    {"op": "rename", "sous_classe": "Domaine de la Vie", "nom": "Impact divin", "nouveau": "Frappe divine"},
    {"op": "sorts", "sous_classe": "Domaine de la Vie",
     "sorts": ["Bénédiction", "Soins", "Restauration partielle", "Arme spirituelle", "Lueur d'espoir",
               "Retour à la vie", "Protection contre la mort", "Gardien de la foi", "Soins de groupe",
               "Rappel à la vie"]},
    {"op": "source", "sous_classe": "Domaine de la Vie", "source": _PHB},

    # ---------------------------------------------------------------- Domaine de la Mort (DMG)
    {"op": "rename", "sous_classe": "Domaine de la Mort", "nom": "Conduit divin : Caresse de la mort",
     "nouveau": "Conduit divin : Toucher de la mort"},
    {"op": "rename", "sous_classe": "Domaine de la Mort", "nom": "Impact divin", "nouveau": "Frappe divine"},
    {"op": "sorts", "sous_classe": "Domaine de la Mort",
     "sorts": ["Simulacre de vie", "Rayon empoisonné", "Cécité/Surdité", "Rayon affaiblissant", "Animation des morts",
               "Toucher du vampire", "Flétrissement", "Protection contre la mort", "Brume mortelle", "Contagion"]},
    {"op": "source", "sous_classe": "Domaine de la Mort", "source": "Dungeon Master's Guide"},

    # ---------------------------------------------------------------- Domaine de la Forge (XGE)
    {"op": "rename", "sous_classe": "Domaine de la Forge", "nom": "Impact divin", "nouveau": "Frappe divine"},
    {"op": "sorts", "sous_classe": "Domaine de la Forge",
     "sorts": ["Identification", "Châtiment calcinant", "Métal brûlant", "Arme magique", "Arme élémentaire",
               "Protection contre une énergie", "Fabrication", "Mur de feu", "Animation d'objets", "Création"]},
    {"op": "source", "sous_classe": "Domaine de la Forge", "source": _XGE},

    # ---------------------------------------------------------------- Domaine de la Tombe (XGE)
    {"op": "rename", "sous_classe": "Domaine de la Tombe", "nom": "Cercle de la mort & Yeux de la tombe",
     "nouveau": "Cercle de mortalité & Yeux de la tombe"},
    {"op": "sorts", "sous_classe": "Domaine de la Tombe",
     "sorts": ["Fléau", "Simulacre de vie", "Préservation des morts", "Rayon affaiblissant", "Retour à la vie",
               "Toucher du vampire", "Bannissement", "Protection contre la mort", "Coquille antivie",
               "Rappel à la vie"]},
    {"op": "source", "sous_classe": "Domaine de la Tombe", "source": _XGE},

    # ---------------------------------------------------------------- Domaine du Crépuscule (TCE)
    {"op": "rename", "sous_classe": "Domaine du Crépuscule",
     "nom": "Maîtrises sup., Yeux de la nuit & Faveur de vigilance",
     "nouveau": "Maîtrises sup., Yeux de la nuit & Bénédiction de vigilance"},
    {"op": "rename", "sous_classe": "Domaine du Crépuscule", "nom": "Foulée nocturne", "nouveau": "Foulée crépusculaire"},
    {"op": "rename", "sous_classe": "Domaine du Crépuscule", "nom": "Impact divin", "nouveau": "Frappe divine"},
    {"op": "sorts", "sous_classe": "Domaine du Crépuscule",
     "sorts": ["Lueurs féeriques", "Sommeil", "Rayon de lune", "Voir l'invisible", "Aura de vitalité",
               "Petite hutte de Léomund", "Aura de vie", "Invisibilité supérieure", "Cercle de pouvoir",
               "Double illusoire"]},
    {"op": "source", "sous_classe": "Domaine du Crépuscule", "source": _TCE},

    # ---------------------------------------------------------------- Domaine de l'Ordre (TCE)
    {"op": "rename", "sous_classe": "Domaine de l'Ordre", "nom": "Maîtrises sup. & Voie de l'autorité",
     "nouveau": "Maîtrises sup. & Voix de l'autorité"},
    {"op": "rename", "sous_classe": "Domaine de l'Ordre", "nom": "Conduit divin : Règne de l'ordre",
     "nouveau": "Conduit divin : Exigence de l'ordre"},
    {"op": "rename", "sous_classe": "Domaine de l'Ordre", "nom": "La loi incarnée", "nouveau": "Incarnation de la loi"},
    {"op": "rename", "sous_classe": "Domaine de l'Ordre", "nom": "Impact divin", "nouveau": "Frappe divine"},
    {"op": "sorts", "sous_classe": "Domaine de l'Ordre",
     "sorts": ["Héroïsme", "Injonction", "Immobilisation de personne", "Zone de vérité", "Lenteur",
               "Communication à distance", "Compulsion", "Localisation de créature", "Communion",
               "Domination de personne"]},
    {"op": "source", "sous_classe": "Domaine de l'Ordre", "source": _TCE},

    # ---------------------------------------------------------------- Domaine de la Paix (TCE)
    {"op": "rename", "sous_classe": "Domaine de la Paix", "nom": "Maîtrises sup. & Lien de hardiesse",
     "nouveau": "Instrument de paix & Lien de hardiesse"},
    {"op": "sorts", "sous_classe": "Domaine de la Paix",
     "sorts": ["Héroïsme", "Sanctuaire", "Aide", "Lien de protection", "Lueur d'espoir", "Communication à distance",
               "Aura de pureté", "Sanctuaire privé de Mordenkainen", "Restauration supérieure",
               "Lien télépathique de Rary"]},
    {"op": "source", "sous_classe": "Domaine de la Paix", "source": _TCE},

    # ---------------------------------------------------------------- Domaine du Sang (homebrew)
    {"op": "rename", "sous_classe": "Domaine du Sang (Communauté)", "nom": "Impact divin", "nouveau": "Frappe divine"},
    {"op": "sorts", "sous_classe": "Domaine du Sang (Communauté)",
     "sorts": ["Fléau", "Frayeur", "Rayon affaiblissant", "Immobilisation de personne", "Toucher du vampire", "Peur",
               "Flétrissement", "Compulsion", "Contagion", "Fléau d'insectes"]},
    {"op": "source", "sous_classe": "Domaine du Sang (Communauté)", "source": "Création de la communauté (Homebrew)"},

    # ---------------------------------------------------------------- Domaine des Arcanes (SCAG)
    {"op": "rename", "sous_classe": "Domaine de l'Arcane (Communauté)", "nom": "Initiation profane & Domptage d'énergie",
     "nouveau": "Initié aux arcanes"},
    {"op": "rename", "sous_classe": "Domaine de l'Arcane (Communauté)", "nom": "Conduit divin : Bannières profanes",
     "nouveau": "Conduit divin : Abjuration arcanique"},
    {"op": "rename", "sous_classe": "Domaine de l'Arcane (Communauté)", "nom": "Soins épurateurs",
     "nouveau": "Briseur de sorts"},
    {"op": "rename", "sous_classe": "Domaine de l'Arcane (Communauté)", "nom": "Maître des arcanes",
     "nouveau": "Maîtrise des arcanes"},
    {"op": "sorts", "sous_classe": "Domaine de l'Arcane (Communauté)",
     "sorts": ["Détection de la magie", "Projectile magique", "Arme magique", "Aura magique de Nystul",
               "Dissipation de la magie", "Cercle magique", "Oeil magique", "Coffre secret de Léomund", "Contrat",
               "Cercle de téléportation"]},
    {"op": "source", "sous_classe": "Domaine de l'Arcane (Communauté)",
     "source": "Guide de l'Aventurier pour la Côte des Epées (SCAG)"},
]
