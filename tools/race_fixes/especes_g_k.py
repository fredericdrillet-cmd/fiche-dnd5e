"""Corrections des espèces Genasi d'air … Kitsune (issues de l'audit)."""

MOTM = "+2, +1 (ou +1, +1, +1)"
VD18 = ("Vous voyez dans une lumière faible jusqu'à 18 mètres comme s'il s'agissait d'une lumière vive, et dans "
        "l'obscurité comme en lumière faible (en nuances de gris uniquement).")
TAILLE_MP = "Moyenne ou Petite, au choix à la création du personnage."
TAILLE_P = "Petite (environ 90 cm à 1,20 m) ; vous pouvez traverser les espaces prévus pour les créatures Petites."
PUISSANTE_CARRURE = ("Vous comptez comme une créature d'une taille supérieure pour déterminer votre capacité de charge "
                     "et le poids que vous pouvez pousser, tirer ou soulever.")
FEY = ("Vous avez l'avantage aux jets de sauvegarde effectués pour éviter l'état charmé ou y mettre fin.")
SLOTS_MOTM = ("Vous pouvez aussi lancer ces sorts avec vos emplacements de sort du niveau approprié ; ils ne "
              "demandent aucune composante matérielle et utilisent l'Intelligence, la Sagesse ou le Charisme "
              "(choisi à la création).")

FIXES = [
    # ------------------------------------------------------------------ Genasi (MotM 2022)
    {"op": "set", "espece": "Genasi d'air", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "set", "espece": "Genasi d'air", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "vitesse", "espece": "Genasi d'air", "valeur": 10.5},
    {"op": "trait", "espece": "Genasi d'air", "nom": "Taille", "description": TAILLE_MP},
    {"op": "trait", "espece": "Genasi d'air", "nom": "Vision dans le noir", "description": VD18},
    {"op": "rename_trait", "espece": "Genasi d'air", "nom": "Souffle", "nouveau": "Souffle infini"},
    {"op": "trait", "espece": "Genasi d'air", "nom": "Souffle infini",
     "description": "Vous pouvez retenir votre respiration indéfiniment tant que vous n'êtes pas neutralisé."},
    {"op": "trait", "espece": "Genasi d'air", "nom": "Résistance à la foudre",
     "description": "Vous avez la résistance aux dégâts de foudre."},
    {"op": "rename_trait", "espece": "Genasi d'air", "nom": "Sort", "nouveau": "Mêlé au vent"},
    {"op": "trait", "espece": "Genasi d'air", "nom": "Mêlé au vent",
     "description": "Connaît le tour de magie *Poigne électrique*. Niveau 3 : *Feuille morte* (1/repos long) ; "
                    "Niveau 5 : *Lévitation* (1/repos long). " + SLOTS_MOTM},

    {"op": "set", "espece": "Genasi d'eau", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "set", "espece": "Genasi d'eau", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "trait", "espece": "Genasi d'eau", "nom": "Taille", "description": TAILLE_MP},
    {"op": "trait", "espece": "Genasi d'eau", "nom": "Vision dans le noir", "description": VD18},
    {"op": "rename_trait", "espece": "Genasi d'eau", "nom": "Résistance", "nouveau": "Résistance à l'acide"},
    {"op": "trait", "espece": "Genasi d'eau", "nom": "Résistance à l'acide",
     "description": "Vous avez la résistance aux dégâts d'acide."},
    {"op": "trait", "espece": "Genasi d'eau", "nom": "Amphibie",
     "description": "Vous respirez aussi bien à l'air libre que sous l'eau. Vous disposez en outre d'une vitesse "
                    "de nage égale à votre vitesse de marche (9 m)."},
    {"op": "rename_trait", "espece": "Genasi d'eau", "nom": "Sorts", "nouveau": "Appel de la vague"},
    {"op": "trait", "espece": "Genasi d'eau", "nom": "Appel de la vague",
     "description": "Connaît le tour de magie *Aspersion d'acide*. Niveau 3 : *Création ou destruction d'eau* "
                    "(1/repos long) ; Niveau 5 : *Marche sur l'eau* (1/repos long). " + SLOTS_MOTM},

    {"op": "set", "espece": "Genasi de feu", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "set", "espece": "Genasi de feu", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "trait", "espece": "Genasi de feu", "nom": "Taille", "description": TAILLE_MP},
    {"op": "trait", "espece": "Genasi de feu", "nom": "Vision dans le noir", "description": VD18},
    {"op": "rename_trait", "espece": "Genasi de feu", "nom": "Résistance", "nouveau": "Résistance au feu"},
    {"op": "trait", "espece": "Genasi de feu", "nom": "Résistance au feu",
     "description": "Vous avez la résistance aux dégâts de feu."},
    {"op": "rename_trait", "espece": "Genasi de feu", "nom": "Sorts", "nouveau": "Toucher la flamme"},
    {"op": "trait", "espece": "Genasi de feu", "nom": "Toucher la flamme",
     "description": "Connaît le tour de magie *Flammes*. Niveau 3 : *Mains brûlantes* (1/repos long) ; "
                    "Niveau 5 : *Lame de feu* (1/repos long). " + SLOTS_MOTM},

    {"op": "set", "espece": "Genasi de terre", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "set", "espece": "Genasi de terre", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "trait", "espece": "Genasi de terre", "nom": "Taille", "description": TAILLE_MP},
    {"op": "trait", "espece": "Genasi de terre", "nom": "Vision dans le noir", "description": VD18},
    {"op": "rename_trait", "espece": "Genasi de terre", "nom": "Marche", "nouveau": "Marche sur la terre"},
    {"op": "trait", "espece": "Genasi de terre", "nom": "Marche sur la terre",
     "description": "Vous traversez les terrains difficiles faits de terre ou de pierre sans dépenser de "
                    "mouvement supplémentaire."},
    {"op": "rename_trait", "espece": "Genasi de terre", "nom": "Sort", "nouveau": "Fusion avec la pierre"},
    {"op": "trait", "espece": "Genasi de terre", "nom": "Fusion avec la pierre",
     "description": "Connaît le tour de magie *Protection contre les armes*, que vous pouvez lancer par une action "
                    "bonus un nombre de fois égal à votre bonus de maîtrise par repos long. Niveau 3 : "
                    "*Passage sans trace* (1/repos long). " + SLOTS_MOTM},

    # ------------------------------------------------------------------ Giff (Spelljammer, AiS)
    {"op": "set", "espece": "Giff", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "trait", "espece": "Giff", "nom": "Étincelle astrale",
     "description": "Quand vous touchez une cible avec une arme courante ou de guerre, vous pouvez lui infliger un "
                    "supplément de dégâts de force égal à votre bonus de maîtrise. Une seule fois par tour, et un "
                    "nombre de fois égal à votre bonus de maîtrise par repos long."},
    {"op": "rename_trait", "espece": "Giff", "nom": "Armes à feu", "nouveau": "Maîtrise des armes à feu"},
    {"op": "trait", "espece": "Giff", "nom": "Maîtrise des armes à feu",
     "description": "Vous maîtrisez toutes les armes à feu. Vous ignorez leur propriété de chargement, et attaquer "
                    "à longue portée avec une arme à feu ne vous impose pas de désavantage."},
    {"op": "trait", "espece": "Giff", "nom": "Physique d'hippopotame",
     "description": "Vous avez l'avantage aux tests de Force et aux jets de sauvegarde de Force. " + PUISSANTE_CARRURE},
    {"op": "trait", "espece": "Giff", "nom": "Nageur",
     "description": "Vous disposez d'une vitesse de nage égale à votre vitesse de marche (9 m)."},

    # ------------------------------------------------------------------ Githyanki (MotM)
    {"op": "set", "espece": "Githyanki", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "set", "espece": "Githyanki", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "rename_trait", "espece": "Githyanki", "nom": "Maîtrises", "nouveau": "Savoir astral"},
    {"op": "trait", "espece": "Githyanki", "nom": "Savoir astral",
     "description": "À la fin de chaque repos long, vous gagnez la maîtrise d'une compétence au choix et d'une arme "
                    "ou d'un type d'outil au choix. Ces maîtrises durent jusqu'à la fin de votre prochain repos long."},
    {"op": "trait", "espece": "Githyanki", "nom": "Résilience psychique",
     "description": "Vous avez la résistance aux dégâts psychiques."},
    {"op": "trait", "espece": "Githyanki", "nom": "Sorts psioniques",
     "description": "Connaît le tour de magie *Main de mage* (la main spectrale est invisible). Niveau 3 : *Saut* "
                    "(1/repos long) ; Niveau 5 : *Foulée brumeuse* (1/repos long). Vous pouvez aussi lancer ces sorts "
                    "avec vos emplacements de sort ; ils ne demandent aucune composante et utilisent l'Intelligence, "
                    "la Sagesse ou le Charisme (choisi à la création)."},

    # ------------------------------------------------------------------ Githzerai (MotM)
    {"op": "set", "espece": "Githzerai", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "set", "espece": "Githzerai", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "rename_trait", "espece": "Githzerai", "nom": "Défense mentale", "nouveau": "Discipline mentale"},
    {"op": "trait", "espece": "Githzerai", "nom": "Discipline mentale",
     "description": "Vous avez l'avantage aux jets de sauvegarde effectués pour éviter les états charmé et effrayé "
                    "ou y mettre fin."},
    {"op": "trait", "espece": "Githzerai", "nom": "Résilience psychique",
     "description": "Vous avez la résistance aux dégâts psychiques."},
    {"op": "trait", "espece": "Githzerai", "nom": "Sorts psioniques",
     "description": "Connaît le tour de magie *Main de mage* (la main spectrale est invisible). Niveau 3 : "
                    "*Bouclier* (1/repos long) ; Niveau 5 : *Détection des pensées* (1/repos long). Vous pouvez aussi "
                    "lancer ces sorts avec vos emplacements de sort ; ils ne demandent aucune composante et utilisent "
                    "l'Intelligence, la Sagesse ou le Charisme (choisi à la création)."},

    # ------------------------------------------------------------------ Gnomes (MdJ / MotM)
    {"op": "trait", "espece": "Gnome des forêts", "nom": "Taille", "description": "Petite (entre 90 cm et 1,20 m environ)."},
    {"op": "trait", "espece": "Gnome des forêts", "nom": "Ruse gnomique",
     "description": "Vous avez l'avantage à tous les jets de sauvegarde d'Intelligence, de Sagesse et de Charisme "
                    "contre la magie."},
    {"op": "trait", "espece": "Gnome des forêts", "nom": "Vision dans le noir", "description": VD18},
    {"op": "rename_trait", "espece": "Gnome des forêts", "nom": "Magie", "nouveau": "Illusionniste-né"},
    {"op": "trait", "espece": "Gnome des forêts", "nom": "Illusionniste-né",
     "description": "Connaît le tour de magie *Illusion mineure* ; l'Intelligence est votre caractéristique "
                    "d'incantation pour ce sort."},
    {"op": "trait", "espece": "Gnome des forêts", "nom": "Communication avec les petits animaux",
     "description": "Par des sons et des gestes, vous pouvez transmettre des idées simples aux bêtes de taille "
                    "Petite ou inférieure. Les gnomes des forêts apprivoisent souvent ainsi écureuils, blaireaux "
                    "ou lapins."},

    {"op": "set", "espece": "Gnome des profondeurs", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "set", "espece": "Gnome des profondeurs", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "vitesse", "espece": "Gnome des profondeurs", "valeur": 9},
    {"op": "trait", "espece": "Gnome des profondeurs", "nom": "Taille", "description": "Petite."},
    {"op": "trait", "espece": "Gnome des profondeurs", "nom": "Vision dans le noir",
     "description": "Vous voyez dans une lumière faible jusqu'à 36 mètres comme en lumière vive, et dans "
                    "l'obscurité comme en lumière faible (en nuances de gris uniquement)."},
    {"op": "rename_trait", "espece": "Gnome des profondeurs", "nom": "Discrétion", "nouveau": "Camouflage svirfnebelin"},
    {"op": "trait", "espece": "Gnome des profondeurs", "nom": "Camouflage svirfnebelin",
     "description": "Lorsque vous faites un test de Dextérité (Discrétion), vous pouvez le faire avec avantage, un "
                    "nombre de fois égal à votre bonus de maîtrise par repos long."},
    {"op": "trait", "espece": "Gnome des profondeurs", "nom": "Ruse gnomique",
     "description": "Vous avez l'avantage aux jets de sauvegarde d'Intelligence, de Sagesse et de Charisme contre "
                    "les sorts."},
    {"op": "trait", "espece": "Gnome des profondeurs", "nom": "Don du svirfnebelin",
     "description": "Sorts innés : Niveau 3 : *Déguisement* (1/repos long) ; Niveau 5 : *Antidétection* "
                    "(1/repos long). " + SLOTS_MOTM},

    {"op": "trait", "espece": "Gnome des roches", "nom": "Taille", "description": "Petite (entre 90 cm et 1,20 m environ)."},
    {"op": "trait", "espece": "Gnome des roches", "nom": "Vision dans le noir", "description": VD18},
    {"op": "trait", "espece": "Gnome des roches", "nom": "Ruse gnomique",
     "description": "Vous avez l'avantage à tous les jets de sauvegarde d'Intelligence, de Sagesse et de Charisme "
                    "contre la magie."},
    {"op": "rename_trait", "espece": "Gnome des roches", "nom": "Ingénierie", "nouveau": "Savoir de l'artificier"},
    {"op": "trait", "espece": "Gnome des roches", "nom": "Savoir de l'artificier",
     "description": "Lors d'un test d'Intelligence (Histoire) portant sur un objet magique, alchimique ou "
                    "technologique, vous ajoutez deux fois votre bonus de maîtrise au lieu de toute autre maîtrise."},
    {"op": "trait", "espece": "Gnome des roches", "nom": "Bricoleur",
     "description": "Vous maîtrisez les outils de bricoleur. En 1 heure et avec 10 po de matériaux, vous fabriquez "
                    "un mécanisme de taille Très petite (CA 5, 1 PV) : jouet mécanique, briquet ou boîte à musique. "
                    "Il fonctionne 24 heures (sauf réparation d'une heure) et vous ne pouvez en avoir que trois "
                    "actifs à la fois ; une action permet d'en démonter un pour récupérer ses matériaux."},

    # ------------------------------------------------------------------ Gobelin (MotM)
    {"op": "set", "espece": "Gobelin", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "set", "espece": "Gobelin", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "trait", "espece": "Gobelin", "nom": "Vision dans le noir", "description": VD18},
    {"op": "rename_trait", "espece": "Gobelin", "nom": "Action rusée", "nouveau": "Fuite agile"},
    {"op": "trait", "espece": "Gobelin", "nom": "Fuite agile",
     "description": "À chacun de vos tours, vous pouvez effectuer l'action Se désengager ou Se cacher par une "
                    "action bonus."},
    {"op": "rename_trait", "espece": "Gobelin", "nom": "Fureur", "nouveau": "Fureur des petits"},
    {"op": "trait", "espece": "Gobelin", "nom": "Fureur des petits",
     "description": "Quand vous blessez avec une attaque ou un sort une créature d'une taille supérieure à la vôtre, "
                    "vous pouvez lui infliger un supplément de dégâts égal à votre bonus de maîtrise. Une fois par "
                    "tour, un nombre de fois égal à votre bonus de maîtrise par repos long."},
    {"op": "trait", "espece": "Gobelin", "nom": "Ascendance féerique", "description": FEY},

    # ------------------------------------------------------------------ Gobelours (MotM)
    {"op": "set", "espece": "Gobelours", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "set", "espece": "Gobelours", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "trait", "espece": "Gobelours", "nom": "Membres allongés",
     "description": "Quand vous faites une attaque au corps à corps pendant votre tour, votre allonge augmente "
                    "de 1,50 m pour cette attaque."},
    {"op": "trait", "espece": "Gobelours", "nom": "Vision dans le noir", "description": VD18},
    {"op": "trait", "espece": "Gobelours", "nom": "Furtif",
     "description": "Vous maîtrisez la compétence Discrétion. De plus, vous pouvez vous glisser dans un espace "
                    "assez grand pour une créature Petite sans qu'il soit considéré comme exigu pour vous."},
    {"op": "trait", "espece": "Gobelours", "nom": "Attaque surprise",
     "description": "Si vous touchez avec un jet d'attaque une créature qui n'a pas encore joué de tour dans ce "
                    "combat, elle subit 2d6 dégâts supplémentaires. Une seule fois par combat."},
    {"op": "trait", "espece": "Gobelours", "nom": "Puissante carrure", "description": PUISSANTE_CARRURE},
    {"op": "trait", "espece": "Gobelours", "nom": "Ascendance féerique", "description": FEY},

    # ------------------------------------------------------------------ Golem miniature (homebrew : rééquilibré)
    {"op": "trait", "espece": "Golem miniature", "nom": "Taille", "description": "Petite (environ 1 m)."},
    {"op": "trait", "espece": "Golem miniature", "nom": "Nature de construct",
     "description": "Vous avez la résistance aux dégâts de poison et l'avantage aux jets de sauvegarde contre "
                    "l'état empoisonné. Vous n'avez besoin ni de manger, ni de boire, ni de respirer."},
    {"op": "trait", "espece": "Golem miniature", "nom": "Agilité d'horlogerie",
     "description": "Vous disposez d'une vitesse d'escalade égale à votre vitesse de marche (9 m) et vous maîtrisez "
                    "un type d'outils d'artisan au choix."},
    {"op": "trait", "espece": "Golem miniature", "nom": "Surcharge à vapeur",
     "description": "Par une action bonus, vous libérez la pression de vos chaudières : jusqu'à la fin de votre tour, "
                    "votre vitesse augmente de 3 m et vous effectuez l'action Foncer ou Se désengager. Une fois, "
                    "récupérée à la fin d'un repos court ou long."},

    # ------------------------------------------------------------------ Goliath (MotM)
    {"op": "set", "espece": "Goliath", "champ": "source", "valeur": "Monstres du Multivers"},
    {"op": "set", "espece": "Goliath", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "set", "espece": "Goliath", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "trait", "espece": "Goliath", "nom": "Taille",
     "description": "Moyenne (entre 2,10 m et 2,40 m) ; Petit géant vous fait compter comme Grand pour la charge."},
    {"op": "rename_trait", "espece": "Goliath", "nom": "Maîtrise", "nouveau": "Petit géant"},
    {"op": "trait", "espece": "Goliath", "nom": "Petit géant",
     "description": "Vous maîtrisez la compétence Athlétisme. " + PUISSANTE_CARRURE},
    {"op": "trait", "espece": "Goliath", "nom": "Endurance de pierre",
     "description": "Quand vous subissez des dégâts, vous pouvez utiliser votre réaction pour lancer 1d12 + votre "
                    "modificateur de Constitution et réduire les dégâts de ce total. Utilisable un nombre de fois "
                    "égal à votre bonus de maîtrise par repos long."},
    {"op": "rename_trait", "espece": "Goliath", "nom": "Résistance", "nouveau": "Né des montagnes"},
    {"op": "trait", "espece": "Goliath", "nom": "Né des montagnes",
     "description": "Vous avez la résistance aux dégâts de froid et vous êtes naturellement acclimaté à la haute "
                    "altitude (au-delà de 6 000 m)."},

    # ------------------------------------------------------------------ Grung (One Grung Above)
    {"op": "set", "espece": "Grung", "champ": "source", "valeur": "One Grung Above (DMs Guild, WotC)"},
    {"op": "vitesse", "espece": "Grung", "valeur": 7.5},
    {"op": "trait", "espece": "Grung", "nom": "Taille", "description": "Petite (environ 90 cm)."},
    {"op": "trait", "espece": "Grung", "nom": "Escalade",
     "description": "Vous disposez d'une vitesse d'escalade de 7,5 m, égale à votre vitesse de marche."},
    {"op": "trait", "espece": "Grung", "nom": "Vigilance arboricole",
     "description": "Vous maîtrisez la compétence Perception."},
    {"op": "trait", "espece": "Grung", "nom": "Amphibie",
     "description": "Vous respirez aussi bien à l'air libre que sous l'eau."},
    {"op": "trait", "espece": "Grung", "nom": "Immunité",
     "description": "Vous êtes immunisé contre les dégâts de poison et l'état empoisonné."},
    {"op": "trait", "espece": "Grung", "nom": "Peau venimeuse",
     "description": "Toute créature qui vous agrippe ou touche directement votre peau doit réussir un JS de "
                    "Constitution DD 12 ou être empoisonnée pendant 1 minute (nouveau JS à la fin de chacun de ses "
                    "tours une fois le contact rompu). Vous pouvez aussi enduire une arme perforante lors d'une "
                    "attaque : une cible touchée doit réussir un JS de Constitution DD 12 ou subir 2d4 dégâts de "
                    "poison."},
    {"op": "trait", "espece": "Grung", "nom": "Saut",
     "description": "Avec ou sans élan, vous pouvez sauter jusqu'à 7,5 m en longueur et 4,5 m en hauteur."},
    {"op": "trait", "espece": "Grung", "nom": "Dépendance à l'eau",
     "description": "Si vous ne restez pas immergé au moins 1 heure dans l'eau au cours d'une journée, vous subissez "
                    "un niveau d'épuisement à la fin de celle-ci. Seules la magie ou une immersion d'1 heure "
                    "permettent de récupérer de cet épuisement."},

    # ------------------------------------------------------------------ Hadozi (Spelljammer, AiS)
    {"op": "set", "espece": "Hadozi", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "trait", "espece": "Hadozi", "nom": "Taille", "description": TAILLE_MP},
    {"op": "trait", "espece": "Hadozi", "nom": "Escalade",
     "description": "Vous disposez d'une vitesse d'escalade égale à votre vitesse de marche (9 m)."},
    {"op": "trait", "espece": "Hadozi", "nom": "Pied agile",
     "description": "Par une action bonus, vous pouvez effectuer l'action Utiliser un objet en vous servant de "
                    "vos pieds."},
    {"op": "trait", "espece": "Hadozi", "nom": "Planer",
     "description": "Quand vous tombez d'au moins 3 m, vous pouvez utiliser votre réaction pour déployer vos "
                    "membranes : vous ne subissez aucun dégât de chute et vous planez horizontalement d'une distance "
                    "égale à votre vitesse de marche, dans la direction de votre choix."},
    {"op": "trait", "espece": "Hadozi", "nom": "Esquive hadozi",
     "description": "Quand vous subissez des dégâts, vous pouvez utiliser votre réaction pour lancer 1d6 + votre "
                    "bonus de maîtrise et réduire les dégâts de ce total. Utilisable un nombre de fois égal à votre "
                    "bonus de maîtrise par repos long."},

    # ------------------------------------------------------------------ Halfelins (MdJ)
    {"op": "trait", "espece": "Halfelin Pied-léger", "nom": "Taille", "description": "Petite (environ 90 cm)."},
    {"op": "trait", "espece": "Halfelin Pied-léger", "nom": "Chanceux",
     "description": "Quand vous obtenez un 1 naturel au d20 d'un jet d'attaque, d'un test de caractéristique ou "
                    "d'un jet de sauvegarde, vous relancez le dé et devez conserver le nouveau résultat."},
    {"op": "trait", "espece": "Halfelin Pied-léger", "nom": "Brave",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre l'état effrayé."},
    {"op": "trait", "espece": "Halfelin Pied-léger", "nom": "Agilité halfeline",
     "description": "Vous pouvez traverser l'espace occupé par une créature d'une taille supérieure à la vôtre."},
    {"op": "trait", "espece": "Halfelin Pied-léger", "nom": "Discrétion naturelle",
     "description": "Vous pouvez tenter de vous cacher même si vous n'êtes masqué que par une créature d'au moins "
                    "une taille de plus que vous."},
    {"op": "trait", "espece": "Halfelin robuste", "nom": "Taille", "description": "Petite (environ 90 cm)."},
    {"op": "trait", "espece": "Halfelin robuste", "nom": "Chanceux",
     "description": "Quand vous obtenez un 1 naturel au d20 d'un jet d'attaque, d'un test de caractéristique ou "
                    "d'un jet de sauvegarde, vous relancez le dé et devez conserver le nouveau résultat."},
    {"op": "trait", "espece": "Halfelin robuste", "nom": "Brave",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre l'état effrayé."},
    {"op": "trait", "espece": "Halfelin robuste", "nom": "Agilité halfeline",
     "description": "Vous pouvez traverser l'espace occupé par une créature d'une taille supérieure à la vôtre."},
    {"op": "rename_trait", "espece": "Halfelin robuste", "nom": "Résistance au poison", "nouveau": "Résilience des robustes"},
    {"op": "trait", "espece": "Halfelin robuste", "nom": "Résilience des robustes",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre le poison et la résistance aux dégâts de "
                    "poison."},

    # ------------------------------------------------------------------ Harengon (MotM)
    {"op": "set", "espece": "Harengon", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "trait", "espece": "Harengon", "nom": "Taille", "description": TAILLE_MP},
    {"op": "trait", "espece": "Harengon", "nom": "Initiative",
     "description": "Vous ajoutez votre bonus de maîtrise à vos jets d'initiative."},
    {"op": "trait", "espece": "Harengon", "nom": "Gambade heureuse",
     "description": "Quand vous ratez un jet de sauvegarde de Dextérité, vous pouvez utiliser votre réaction pour "
                    "lancer 1d4 et l'ajouter au résultat, ce qui peut le transformer en réussite. Impossible si vous "
                    "êtes à terre ou si votre vitesse est de 0."},
    {"op": "trait", "espece": "Harengon", "nom": "Saut de lapin",
     "description": "Par une action bonus, si votre vitesse n'est pas de 0, vous sautez d'une distance de 1,50 m × "
                    "votre bonus de maîtrise sans provoquer d'attaques d'opportunité. Utilisable un nombre de fois "
                    "égal à votre bonus de maîtrise par repos long."},
    {"op": "trait", "espece": "Harengon", "nom": "Sens léporides",
     "description": "Vous maîtrisez la compétence Perception."},

    # ------------------------------------------------------------------ Hobgobelin (MotM)
    {"op": "trait", "espece": "Hobgobelin", "nom": "Ascendance féerique", "description": FEY},
    {"op": "trait", "espece": "Hobgobelin", "nom": "Vision dans le noir", "description": VD18},
    {"op": "trait", "espece": "Hobgobelin", "nom": "Chance du nombre",
     "description": "Quand vous ratez un jet d'attaque, un test de caractéristique ou un jet de sauvegarde, vous "
                    "gagnez un bonus au jet égal au nombre d'alliés que vous voyez à 9 m ou moins (maximum +3). "
                    "Utilisable un nombre de fois égal à votre bonus de maîtrise par repos long."},
    {"op": "trait", "espece": "Hobgobelin", "nom": "Don féerique",
     "description": "Vous pouvez effectuer l'action Aider par une action bonus, un nombre de fois égal à votre bonus "
                    "de maîtrise par repos long. À partir du niveau 3, chaque Aide ajoute une option au choix : "
                    "Hospitalité (vous et la créature aidée gagnez 1d6 + votre bonus de maîtrise PV temporaires), "
                    "Passage (vous et elle gagnez +3 m de vitesse jusqu'au début de votre prochain tour) ou Rancune "
                    "(la cible de l'Aide a le désavantage à son prochain jet d'attaque avant ce moment)."},

    # ------------------------------------------------------------------ Homme lézard (MotM)
    {"op": "trait", "espece": "Homme lézard", "nom": "Morsure",
     "description": "Votre gueule est une arme naturelle avec laquelle vous pouvez porter des attaques à mains nues : "
                    "un coup inflige 1d6 + votre modificateur de Force dégâts tranchants."},
    {"op": "trait", "espece": "Homme lézard", "nom": "Apnée",
     "description": "Vous pouvez retenir votre respiration jusqu'à 15 minutes."},
    {"op": "trait", "espece": "Homme lézard", "nom": "Mâchoires affamées",
     "description": "Par une action bonus, vous effectuez une attaque spéciale avec votre Morsure ; si elle touche, "
                    "elle inflige ses dégâts normaux et vous gagnez des PV temporaires égaux à votre bonus de "
                    "maîtrise. Utilisable un nombre de fois égal à votre bonus de maîtrise par repos long."},
    {"op": "trait", "espece": "Homme lézard", "nom": "Armure naturelle",
     "description": "Sans armure, votre CA est égale à 13 + votre modificateur de Dextérité. Vous pouvez utiliser "
                    "un bouclier et conserver ce bénéfice."},
    {"op": "trait", "espece": "Homme lézard", "nom": "Intuition",
     "description": "Vous maîtrisez deux compétences au choix parmi Dressage, Médecine, Nature, Perception, "
                    "Discrétion et Survie."},
    {"op": "trait", "espece": "Homme lézard", "nom": "Nageur",
     "description": "Vous disposez d'une vitesse de nage égale à votre vitesse de marche (9 m)."},

    # ------------------------------------------------------------------ Hybride Simic (GGR)
    {"op": "set", "espece": "Hybride Simic", "champ": "caracteristiques", "valeur": "Con +2, +1"},
    {"op": "trait", "espece": "Hybride Simic", "nom": "Vision dans le noir", "description": VD18},
    {"op": "trait", "espece": "Hybride Simic", "nom": "Améliorations",
     "description": "Au niveau 1, choisissez une amélioration : Raie manta (en tombant, réduisez de 30 m la hauteur "
                    "de chute pour les dégâts et avancez de 60 cm à l'horizontale par 30 cm de descente), Grimpeur "
                    "agile (vitesse d'escalade égale à la marche) ou Adaptation aquatique (respiration aquatique et "
                    "vitesse de nage égale à la marche)."},
    {"op": "trait", "espece": "Hybride Simic", "nom": "Amélioration supplémentaire (niveau 5)",
     "description": "Au niveau 5, choisissez une option de niveau 1 non prise ou : Appendices de saisie (attaque à "
                    "mains nues 1d6 + votre modificateur de Force contondants, puis empoignade par une action bonus), "
                    "Carapace (+1 CA sans armure lourde) ou Crachat d'acide (action, cible à 9 m, JS de Dextérité DD "
                    "8 + votre bonus de maîtrise + votre modificateur de Constitution, 2d10 acide, 3d10 au niveau 11, "
                    "4d10 au niveau 17 ; un nombre de fois égal à votre modificateur de Constitution, minimum 1, par "
                    "repos long)."},

    # ------------------------------------------------------------------ Kalashtar (ERLW)
    {"op": "trait", "espece": "Kalashtar", "nom": "Esprit double",
     "description": "Vous avez l'avantage à tous les jets de sauvegarde de Sagesse."},
    {"op": "trait", "espece": "Kalashtar", "nom": "Discipline mentale",
     "description": "Vous avez la résistance aux dégâts psychiques."},
    {"op": "trait", "espece": "Kalashtar", "nom": "Lien mental",
     "description": "Vous parlez par télépathie à une créature que vous voyez dans un rayon en mètres égal à 3 × "
                    "votre niveau de personnage, si elle comprend une langue que vous parlez. Par une action, vous "
                    "lui permettez de vous répondre par télépathie pendant 1 heure."},
    {"op": "trait", "espece": "Kalashtar", "nom": "Séparé des rêves",
     "description": "Les sorts et effets qui exigent que vous rêviez (comme le sort Songe) n'ont aucun effet sur "
                    "vous ; ceux qui vous plongent simplement dans le sommeil fonctionnent normalement."},

    # ------------------------------------------------------------------ Kender (Dragonlance SotDQ)
    {"op": "vitesse", "espece": "Kender", "valeur": 9},
    {"op": "trait", "espece": "Kender", "nom": "Taille", "description": "Petite (environ 90 cm à 1,20 m)."},
    {"op": "trait", "espece": "Kender", "nom": "Intrépide",
     "description": "Vous avez l'avantage aux jets de sauvegarde pour éviter l'état effrayé ou y mettre fin. Une fois "
                    "par repos long, vous pouvez transformer un échec à un tel jet en réussite."},
    {"op": "trait", "espece": "Kender", "nom": "Aptitude kender",
     "description": "Vous maîtrisez une compétence au choix parmi Perspicacité, Investigation, Escamotage, "
                    "Discrétion et Survie."},
    {"op": "trait", "espece": "Kender", "nom": "Provocation",
     "description": "Par une action bonus, vous raillez une créature à 18 m ou moins qui peut vous entendre : elle "
                    "doit réussir un JS de Sagesse (DD 8 + votre bonus de maîtrise + votre modificateur "
                    "d'Intelligence, de Sagesse ou de Charisme, au choix) ou avoir le désavantage à ses jets "
                    "d'attaque contre toute autre cible que vous jusqu'au début de votre prochain tour. Un nombre de "
                    "fois égal à votre bonus de maîtrise par repos long."},

    # ------------------------------------------------------------------ Kenku (MotM)
    {"op": "set", "espece": "Kenku", "champ": "caracteristiques", "valeur": MOTM},
    {"op": "trait", "espece": "Kenku", "nom": "Taille", "description": TAILLE_MP},
    {"op": "trait", "espece": "Kenku", "nom": "Mimétisme",
     "description": "Vous imitez avec précision les sons et voix que vous avez entendus. Un auditeur ne décèle "
                    "l'imitation qu'en réussissant un test de Sagesse (Perspicacité) DD 8 + votre bonus de maîtrise "
                    "+ votre modificateur de Charisme."},
    {"op": "rename_trait", "espece": "Kenku", "nom": "Falsification", "nouveau": "Duplication experte"},
    {"op": "trait", "espece": "Kenku", "nom": "Duplication experte",
     "description": "Quand vous copiez un écrit ou un ouvrage artisanal (le vôtre ou celui d'autrui), vous avez "
                    "l'avantage aux tests effectués pour en produire une reproduction exacte."},
    {"op": "rename_trait", "espece": "Kenku", "nom": "Maîtrises", "nouveau": "Mémoire kenku"},
    {"op": "trait", "espece": "Kenku", "nom": "Mémoire kenku",
     "description": "Vous maîtrisez deux compétences au choix. Avant un test utilisant une compétence que vous "
                    "maîtrisez, vous pouvez vous accorder l'avantage, un nombre de fois égal à votre bonus de maîtrise "
                    "par repos long."},

    # ------------------------------------------------------------------ Kitsune (homebrew : rééquilibré)
    {"op": "trait", "espece": "Kitsune", "nom": "Taille", "description": TAILLE_MP},
    {"op": "trait", "espece": "Kitsune", "nom": "Vision dans le noir", "description": VD18},
    {"op": "trait", "espece": "Kitsune", "nom": "Magie innée des renards",
     "description": "Connaît le tour de magie *Illusion mineure*. Vous pouvez aussi lancer *Déguisement* "
                    "(1/repos long), ou avec vos emplacements de sort ; le Charisme est votre caractéristique "
                    "d'incantation pour ces sorts."},
    {"op": "trait", "espece": "Kitsune", "nom": "Forme hybride",
     "description": "Par une action bonus, vous laissez paraître oreilles, queues et traits de renard pendant 1 "
                    "minute : vous avez l'avantage aux tests de Charisme (Tromperie) et (Persuasion). Utilisable un "
                    "nombre de fois égal à votre bonus de maîtrise par repos long."},
]

CORRIGE = [
    ("majeur", "Genasi (4) / version", "Les quatre genasi suivaient EE 2015 malgré la source MotM",
     "Alignés sur MotM 2022 : +2/+1 ou +1/+1/+1, Commun + 1 au choix, taille Moyenne ou Petite, VD 18 m"),
    ("majeur", "Genasi d'air / vitesse", "9 m par défaut", "10,5 m"),
    ("majeur", "Genasi d'air / traits MotM", "VD et résistance à la foudre absentes", "Traits ajoutés"),
    ("majeur", "Genasi d'air / Mêlé au vent", "Lévitation dès le niveau 1",
     "Poigne électrique ; niv. 3 Feuille morte ; niv. 5 Lévitation ; 1/repos long ou emplacements"),
    ("majeur", "Genasi d'eau / Appel de la vague", "Façonnage de l'eau + Création d'eau",
     "Aspersion d'acide ; niv. 3 Création ou destruction d'eau ; niv. 5 Marche sur l'eau"),
    ("mineur", "Genasi d'eau / nage", "Vitesse de nage non chiffrée", "Nage = marche (9 m)"),
    ("majeur", "Genasi de feu / sort mineur", "« *Flamme* » résolu en Flamme sacrée", "*Flammes* ; niv. 5 Lame de feu ajoutée"),
    ("majeur", "Genasi de terre / Fusion avec la pierre", "Passage sans trace au niv. 1, Protection contre les armes absente",
     "Protection contre les armes (action bonus, bonus de maîtrise fois/repos long) ; niv. 3 Passage sans trace"),
    ("mineur", "Genasi / langues et taille", "Commun, Primordial ; taille absente", "Commun + 1 au choix ; Moyenne ou Petite"),
    ("majeur", "Giff / Étincelle astrale", "+6 force, 6 fois/repos long", "Bonus de maîtrise en force, 1/tour, BM fois/repos long"),
    ("majeur", "Giff / vitesse de nage", "Nage absente", "Trait Nageur : nage = marche"),
    ("mineur", "Giff / caractéristiques", "+2, +1 sans alternative", "+2, +1 (ou +1, +1, +1)"),
    ("majeur", "Githyanki / Maîtrises", "Armures + langue + compétence (MToF)", "Savoir astral (compétence + arme/outil par repos long)"),
    ("majeur", "Githyanki / Résilience psychique", "Absente", "Résistance aux dégâts psychiques"),
    ("mineur", "Githyanki / Psionique", "Main invisible non précisée", "Main invisible, emplacements, sans composante, Int/Sag/Cha"),
    ("mineur", "Githyanki, Githzerai / carac. et langues", "Valeurs MToF", "+2/+1 ou +1/+1/+1 ; Commun + 1 au choix"),
    ("majeur", "Githzerai / Défense mentale", "+1 CA inventé", "Remplacé par Discipline mentale (avantage contre charmé/effrayé)"),
    ("majeur", "Githzerai / Résilience psychique", "Absente", "Résistance aux dégâts psychiques"),
    ("mineur", "Gnome des forêts / taille et traits", "Taille absente ; Illusionniste-né et Communication fusionnés",
     "Taille Petite ; deux traits distincts précis"),
    ("majeur", "Gnome des profondeurs / vitesse", "7,5 m (MToF/EE)", "9 m (MotM)"),
    ("majeur", "Gnome des profondeurs / Don du svirfnebelin", "Absent", "Niv. 3 Déguisement, niv. 5 Antidétection, 1/repos long"),
    ("mineur", "Gnome des profondeurs / Camouflage", "Avantage sur terrain rocheux (EE)", "Avantage en Discrétion, BM fois/repos long"),
    ("mineur", "Gnome des profondeurs / Ruse, carac., langues", "Libellé flou ; valeurs EE", "Contre les sorts ; MotM"),
    ("mineur", "Gnome des roches / Savoir de l'artificier, Bricoleur, taille", "Libellés imprécis ; taille absente",
     "Double maîtrise Histoire ; mécanismes détaillés ; Petite"),
    ("majeur", "Gobelin / Fureur des petits", "+6 dégâts, 6 fois/repos long", "Bonus de maîtrise, 1/tour, BM fois/repos long"),
    ("mineur", "Gobelin / Ascendance féerique, carac., langues", "Absente ; valeurs Volo", "Ajoutée ; MotM"),
    ("majeur", "Gobelours / Attaque surprise", "Ennemi surpris au 1er tour (Volo)", "Créature n'ayant pas encore joué, 1/combat"),
    ("mineur", "Gobelours / allonge, traits, carac., langues", "Allonge non chiffrée ; Puissante carrure et Ascendance absentes",
     "+1,50 m ; traits ajoutés ; MotM"),
    ("majeur", "Goliath / taille", "Grande", "Moyenne (+ Puissante carrure via Petit géant)"),
    ("majeur", "Goliath / source", "« Manuel des Joueurs / MtoM »", "Monstres du Multivers (version appliquée)"),
    ("majeur", "Goliath / Endurance de pierre", "1/repos long, modificateur non précisé", "1d12 + Con, BM fois/repos long"),
    ("mineur", "Goliath / Né des montagnes, carac.", "Altitude absente ; valeurs Volo", "Acclimatation ajoutée ; MotM"),
    ("majeur", "Grung / source", "« One-D&D / Homebrew »", "One Grung Above (DMs Guild, WotC)"),
    ("majeur", "Grung / vitesse", "9 m par défaut", "7,5 m, escalade 7,5 m"),
    ("majeur", "Grung / Vigilance arboricole", "Absente", "Maîtrise de Perception"),
    ("mineur", "Grung / Peau venimeuse, taille", "Contact = 2d4 ; taille absente", "Contact = empoisonné 1 min ; 2d4 via arme ; Petite"),
    ("majeur", "Hadozi / Esquive", "6 fois/repos long", "Réaction, 1d6 + BM, BM fois/repos long"),
    ("mineur", "Hadozi / Planer, carac.", "Distance absente ; sans alternative", "Distance = vitesse de marche ; MotM"),
    ("mineur", "Halfelins / taille, Chanceux", "Taille absente ; jet non précisé", "Petite ; 1 naturel sur attaque, test ou JS"),
    ("mineur", "Halfelin robuste / Agilité halfeline", "Trait commun aux halfelins absent", "Ajouté"),
    ("majeur", "Harengon / Saut de lapin", "Distance non chiffrée, 6 fois/repos long", "1,50 m × BM, BM fois/repos long"),
    ("mineur", "Harengon / Gambade, taille, carac.", "Réaction absente ; taille absente", "Réaction ; Moyenne ou Petite ; MotM"),
    ("majeur", "Hobgobelin / Don féerique", "Niv. 3, 6 fois ; *Aider* en italique", "Dès le niv. 1, BM fois ; options au niv. 3 ; sans italique"),
    ("majeur", "Hobgobelin / Chance du nombre", "6 fois/repos long", "BM fois/repos long"),
    ("majeur", "Homme lézard / Mâchoires affamées", "6 PV temp., 6 fois/jour", "PV temp. = BM, BM fois/repos long"),
    ("majeur", "Homme lézard / nage", "Absente", "Trait Nageur : nage = marche"),
    ("mineur", "Homme lézard / Morsure", "Sans modificateur", "1d6 + For tranchants"),
    ("majeur", "Hybride Simic / caractéristiques", "« Con +2, autre +1 » : le +1 libre n'était pas lu", "« Con +2, +1 »"),
    ("mineur", "Hybride Simic / Améliorations", "Options niv. 1 et 5 mélangées, Crachat d'acide non chiffré",
     "Deux traits séparés ; Crachat 2d10/3d10/4d10, DD 8 + BM + Con, mod. Con fois/repos long"),
    ("majeur", "Kalashtar / Lien mental", "1,5 km fixe", "3 m × niveau de personnage"),
    ("majeur", "Kender / vitesse", "7,5 m", "9 m"),
    ("majeur", "Kender / Intrépide", "Avantage 1/repos long", "Avantage permanent + échec → réussite 1/repos long"),
    ("majeur", "Kender / Provocation", "Ni JS, ni portée, ni utilisations", "18 m, JS Sag DD 8 + BM + Int/Sag/Cha, BM fois/repos long"),
    ("majeur", "Kenku / Mémoire kenku", "Liste de 4 compétences (Volo)", "2 compétences au choix + avantage BM fois/repos long"),
    ("mineur", "Kenku / taille, carac., Mimétisme", "Taille absente ; valeurs Volo ; DD absent", "Moyenne ou Petite ; MotM ; DD 8 + BM + Cha"),
    ("mineur", "Kitsune / Forme hybride (homebrew)", "Bonus non chiffré", "Avantage Tromperie/Persuasion 1 min, BM fois/repos long"),
    ("mineur", "Golem miniature / Surcharge à vapeur (homebrew)", "Effet non chiffré (action « fulgurante »)",
     "Action bonus : +3 m et Foncer ou Se désengager, 1/repos court ; Nature de construct précisée (empoisonné)"),
]

AUDIT = [
    ("info", "Githyanki, Githzerai / carac. d'incantation",
     "rules.RACE_SPELL_ABILITY fige Int (Githyanki) et Sag (Githzerai) ; hors périmètre de ce module",
     "MotM : Int, Sag ou Cha au choix (indiqué dans le texte du trait)"),
    ("info", "Halfelins, Gobelin / langues", "« Halfelin » absent de Langues.json (fichier hors périmètre)",
     "Langue standard MdJ : Halfelin"),
    ("info", "Grung, Kalashtar / langues exotiques", "Grung et Quori sans entrée dans Langues.json",
     "Langues de cadre de campagne, notées en texte libre"),
    ("info", "Humain, Humain variant", "Conformes au MdJ : aucune correction", "Manuel des joueurs"),
    ("info", "Kitsune, Golem miniature / source", "Espèces non officielles : chiffres rééquilibrés, non auditées comme officielles",
     "Aucune source 5e officielle"),
    ("info", "Vitesses spéciales (nage, escalade)", "Le moteur ne modélise que la marche ; nage/escalade décrites dans les traits",
     "Bonus_Raciaux.json ne gère qu'une vitesse par espèce"),
]
