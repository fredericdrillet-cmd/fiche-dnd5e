"""Corrections structurelles — Guerrier (issues de l'audit)."""
CLASSE = "Guerrier"
FIXES = [
    # Classe de base : capacité optionnelle de Tasha
    {"op": "add", "sous_classe": None, "nom": "Polyvalence martiale (option Tasha)", "niveau": 4},

    # Champion (PHB)
    {"op": "rename", "sous_classe": "Champion", "nom": "Coup critique amélioré & Athlète accompli",
     "nouveau": "Critique amélioré"},
    {"op": "rename", "sous_classe": "Champion", "nom": "Coup critique supérieur & Survivant",
     "nouveau": "Critique supérieur"},
    {"op": "rename", "sous_classe": "Champion", "nom": "Survivant (Maîtrise)", "nouveau": "Survivant"},

    # Maître de guerre (PHB)
    {"op": "rename", "sous_classe": "Maître de guerre", "nom": "Supériorité martiale & Disciple martial",
     "nouveau": "Supériorité martiale"},
    {"op": "add", "sous_classe": "Maître de guerre", "nom": "Disciple de la guerre", "niveau": 3},
    {"op": "rename", "sous_classe": "Maître de guerre", "nom": "Observation de l'ennemi",
     "nouveau": "Connaître son ennemi"},
    {"op": "rename", "sous_classe": "Maître de guerre", "nom": "Dés de supériorité améliorés (d10 / d12)",
     "nouveau": "Supériorité martiale améliorée (d10)"},
    {"op": "rename", "sous_classe": "Maître de guerre", "nom": "Relance de supériorité (Implacable)",
     "nouveau": "Implacable"},
    {"op": "rename", "sous_classe": "Maître de guerre", "nom": "Maîtrise des dés de supériorité",
     "nouveau": "Supériorité martiale améliorée (d12)"},

    # Chevalier occulte (PHB)
    {"op": "rename", "sous_classe": "Chevalier occulte", "nom": "Incantation & Arme occulte",
     "nouveau": "Incantation"},
    {"op": "add", "sous_classe": "Chevalier occulte", "nom": "Lien avec une arme", "niveau": 3},
    {"op": "rename", "sous_classe": "Chevalier occulte", "nom": "Fragilisation occulte (Frappe arcanique)",
     "nouveau": "Frappe occulte"},
    {"op": "rename", "sous_classe": "Chevalier occulte", "nom": "Magie de guerre supérieure",
     "nouveau": "Magie de guerre améliorée"},
    {"op": "sorts", "sous_classe": "Chevalier occulte", "sorts": []},

    # Archer arcanique (Xanathar)
    {"op": "rename", "sous_classe": "Archer arcanique", "nom": "Tir arcanique & Connaissances de l'archer",
     "nouveau": "Savoir de l'archer arcanique"},
    {"op": "add", "sous_classe": "Archer arcanique", "nom": "Tir arcanique", "niveau": 3},
    {"op": "rename", "sous_classe": "Archer arcanique", "nom": "Flèche magique & Tir incurvé",
     "nouveau": "Flèche magique"},
    {"op": "add", "sous_classe": "Archer arcanique", "nom": "Tir incurvé", "niveau": 7},
    {"op": "rename", "sous_classe": "Archer arcanique", "nom": "Tir récurrent (Implacable)",
     "nouveau": "Tir infaillible"},

    # Cavalier (Xanathar)
    {"op": "rename", "sous_classe": "Cavalier", "nom": "Maîtrise supplémentaire, Né sur un cheval & Marque tenace",
     "nouveau": "Maîtrise supplémentaire"},
    {"op": "add", "sous_classe": "Cavalier", "nom": "Né en selle", "niveau": 3},
    {"op": "add", "sous_classe": "Cavalier", "nom": "Marque inébranlable", "niveau": 3},
    {"op": "rename", "sous_classe": "Cavalier", "nom": "Manœuvre défensive", "nouveau": "Manœuvre d'interposition"},
    {"op": "rename", "sous_classe": "Cavalier", "nom": "On ne passe pas (Inébranlable)", "nouveau": "Tenir la ligne"},

    # Samouraï (Xanathar)
    {"op": "add", "sous_classe": "Samouraï", "nom": "Esprit combatif", "niveau": 3},
    {"op": "rename", "sous_classe": "Samouraï", "nom": "Volonté inébranlable", "nouveau": "Esprit infatigable"},
    {"op": "rename", "sous_classe": "Samouraï", "nom": "Combativité & Frappe fulgurante", "nouveau": "Frappe éclair"},
    {"op": "rename", "sous_classe": "Samouraï", "nom": "Solide face à la mort", "nouveau": "Force avant la mort"},

    # Chevalier runique (Tasha)
    {"op": "rename", "sous_classe": "Chevalier runique", "nom": "Sculpteur de runes & Maître des runes",
     "nouveau": "Maître des runes"},
    {"op": "rename", "sous_classe": "Chevalier runique",
     "nom": "Maîtrise des outils, Langue des géants & Puissance des géants", "nouveau": "Puissance des géants"},
    {"op": "add", "sous_classe": "Chevalier runique", "nom": "Maîtrises supplémentaires", "niveau": 3},
    {"op": "add", "sous_classe": "Chevalier runique", "nom": "Sculpteur de runes", "niveau": 3},
    {"op": "rename", "sous_classe": "Chevalier runique", "nom": "Grande carrure", "nouveau": "Grande stature"},
    {"op": "rename", "sous_classe": "Chevalier runique", "nom": "Mastodonte runique", "nouveau": "Colosse runique"},

    # Soldat psi (Tasha) — nom de sous-classe conservé
    {"op": "rename", "sous_classe": "Guerrier Psi (Soldat psi)", "nom": "Applications télékinétiques",
     "nouveau": "Adepte télékinétique"},
    {"op": "rename", "sous_classe": "Guerrier Psi (Soldat psi)", "nom": "Esprit blindé & Bulle de protection",
     "nouveau": "Esprit gardé"},
    {"op": "rename", "sous_classe": "Guerrier Psi (Soldat psi)", "nom": "Rempart de force supérieur",
     "nouveau": "Rempart de force"},

    # Chevalier de Sang (homebrew) : noms de sorts invalides remplacés
    {"op": "sorts", "sous_classe": "Chevalier de Sang",
     "sorts": ["Châtiment courroucé", "Frayeur", "Arme magique", "Rayon affaiblissant", "Toucher du vampire", "Peur"]},
]
