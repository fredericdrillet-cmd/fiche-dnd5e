"""Corrections des espèces Aarakocra → Forgelier (issues de l'audit)."""

ALT = "+2, +1 (ou +1, +1, +1)"
MOTM = "Monstres du Multivers"
CARAC_INC = "Intelligence, Sagesse ou Charisme (choisie en adoptant l'espèce)"

FIXES = [
    # ------------------------------------------------------------------ Aarakocra (MotM)
    {"op": "set", "espece": "Aarakocra", "champ": "caracteristiques", "valeur": ALT},
    {"op": "set", "espece": "Aarakocra", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "trait", "espece": "Aarakocra", "nom": "Vol",
     "description": "Vous disposez d'une vitesse de vol égale à votre vitesse de marche (9 m). Vous ne pouvez pas "
                    "l'utiliser si vous portez une armure intermédiaire ou lourde."},
    {"op": "trait", "espece": "Aarakocra", "nom": "Serres",
     "description": "Vos serres sont des armes naturelles avec lesquelles vous pouvez porter des attaques à mains nues. "
                    "Un coup réussi inflige 1d6 + votre modificateur de Force dégâts tranchants, au lieu des dégâts "
                    "contondants habituels d'une attaque à mains nues."},
    {"op": "trait", "espece": "Aarakocra", "nom": "Appel du vent",
     "description": "Lancement : à partir du niveau 3, vous pouvez lancer *Bourrasque* (niv. 3, 1/repos long) sans "
                    "composante matérielle. Vous pouvez aussi le lancer avec vos emplacements de sort de niveau 2 ou "
                    f"supérieur. Caractéristique d'incantation : {CARAC_INC}."},

    # ------------------------------------------------------------------ Aasimar déchu (Volo)
    {"op": "set", "espece": "Aasimar déchu", "champ": "source", "valeur": "Guide de Volo"},
    {"op": "set", "espece": "Aasimar déchu", "champ": "caracteristiques", "valeur": "Cha +2, For +1"},
    {"op": "set", "espece": "Aasimar déchu", "champ": "langues", "valeur": ["Commun", "Céleste"]},
    {"op": "trait", "espece": "Aasimar déchu", "nom": "Taille", "description": "Moyenne."},
    {"op": "trait", "espece": "Aasimar déchu", "nom": "Sort",
     "description": "Connaît le sort mineur *Lumière* (Porteur de lumière). Le Charisme est votre caractéristique "
                    "d'incantation pour ce sort."},
    {"op": "trait", "espece": "Aasimar déchu", "nom": "Mains guérisseuses",
     "description": "Par une action, vous touchez une créature et lui rendez un nombre de points de vie égal à votre "
                    "niveau de personnage. Utilisable 1 fois par repos long."},
    {"op": "trait", "espece": "Aasimar déchu", "nom": "Voile nécrotique",
     "description": "À partir du niveau 3, par une action, vous déployez des ailes squelettiques et spectrales pendant "
                    "1 minute (1 fois par repos long). À l'activation, chaque créature autre que vos alliés située à "
                    "3 m ou moins et qui peut vous voir doit réussir un JS de Charisme (DD 8 + votre bonus de maîtrise "
                    "+ votre modificateur de Charisme) ou être effrayée jusqu'à la fin de votre prochain tour. Pendant "
                    "la transformation, une fois par tour, une attaque ou un sort qui inflige des dégâts ajoute des "
                    "dégâts nécrotiques égaux à votre niveau de personnage à une cible."},

    # ------------------------------------------------------------------ Aasimar protecteur (Volo)
    {"op": "set", "espece": "Aasimar protecteur", "champ": "source", "valeur": "Guide de Volo"},
    {"op": "set", "espece": "Aasimar protecteur", "champ": "caracteristiques", "valeur": "Cha +2, Sag +1"},
    {"op": "set", "espece": "Aasimar protecteur", "champ": "langues", "valeur": ["Commun", "Céleste"]},
    {"op": "trait", "espece": "Aasimar protecteur", "nom": "Taille", "description": "Moyenne."},
    {"op": "trait", "espece": "Aasimar protecteur", "nom": "Sort",
     "description": "Connaît le sort mineur *Lumière* (Porteur de lumière). Le Charisme est votre caractéristique "
                    "d'incantation pour ce sort."},
    {"op": "trait", "espece": "Aasimar protecteur", "nom": "Mains guérisseuses",
     "description": "Par une action, vous touchez une créature et lui rendez un nombre de points de vie égal à votre "
                    "niveau de personnage. Utilisable 1 fois par repos long."},
    {"op": "rename_trait", "espece": "Aasimar protecteur", "nom": "Transformation céleste", "nouveau": "Âme radieuse"},
    {"op": "trait", "espece": "Aasimar protecteur", "nom": "Âme radieuse",
     "description": "À partir du niveau 3, par une action, vos yeux s'illuminent et deux ailes lumineuses apparaissent "
                    "pendant 1 minute (1 fois par repos long) : vous gagnez une vitesse de vol de 9 m. Pendant la "
                    "transformation, une fois par tour, une attaque ou un sort qui inflige des dégâts ajoute des dégâts "
                    "radiants égaux à votre niveau de personnage à une cible. Vous pouvez y mettre fin par une action "
                    "bonus."},

    # ------------------------------------------------------------------ Autognome (Spelljammer)
    {"op": "set", "espece": "Autognome", "champ": "caracteristiques", "valeur": ALT},
    {"op": "trait", "espece": "Autognome", "nom": "Taille et type",
     "description": "Petite taille ; vous êtes une Créature artificielle (construct) et non un Humanoïde."},
    {"op": "trait", "espece": "Autognome", "nom": "Coque blindée",
     "description": "Tant que vous ne portez pas d'armure, votre CA est égale à 13 + votre modificateur de Dextérité. "
                    "Vous pouvez utiliser un bouclier et en conserver le bénéfice."},
    {"op": "trait", "espece": "Autognome", "nom": "Conçu pour réussir",
     "description": "Lorsque vous effectuez un jet d'attaque, un test de caractéristique ou un jet de sauvegarde, vous "
                    "pouvez lancer 1d4 et l'ajouter au résultat du d20. Utilisable un nombre de fois égal à votre "
                    "bonus de maîtrise par repos long."},
    {"op": "trait", "espece": "Autognome", "nom": "Machine de guérison",
     "description": "Quand le sort Réparation est lancé sur vous, vous pouvez dépenser un dé de vie, le lancer et "
                    "récupérer ce résultat + votre modificateur de Constitution en points de vie (minimum 1). Les sorts "
                    "Soins, Mot de guérison, leurs versions de groupe et Épargner les mourants fonctionnent sur vous "
                    "malgré votre nature artificielle."},
    {"op": "trait", "espece": "Autognome", "nom": "Nature mécanique",
     "description": "Vous avez la résistance aux dégâts de poison, l'immunité aux maladies et l'avantage aux jets de "
                    "sauvegarde contre les états paralysé et empoisonné. Vous n'avez besoin ni de manger, ni de boire, "
                    "ni de respirer."},
    {"op": "trait", "espece": "Autognome", "nom": "Repos de sentinelle",
     "description": "Votre repos long ne dure que 6 heures, passées immobile et inactif mais sans perdre conscience : "
                    "vous voyez et entendez normalement durant cette période."},

    # ------------------------------------------------------------------ Centaure (MotM)
    {"op": "trait", "espece": "Centaure", "nom": "Taille et type", "description": "Moyenne ; type Fée."},
    {"op": "trait", "espece": "Centaure", "nom": "Charge",
     "description": "Si vous vous déplacez d'au moins 9 m en ligne droite vers une cible puis la touchez avec une "
                    "attaque d'arme au corps à corps lors du même tour, vous pouvez immédiatement porter une attaque "
                    "avec vos Sabots contre elle par une action bonus."},
    {"op": "rename_trait", "espece": "Centaure", "nom": "Puissante carrure", "nouveau": "Morphologie équine"},
    {"op": "trait", "espece": "Centaure", "nom": "Morphologie équine",
     "description": "Vous comptez comme une créature de taille Grande pour déterminer votre capacité de charge et le "
                    "poids que vous pouvez pousser, tirer ou soulever. En revanche, chaque mètre d'escalade vous coûte "
                    "4 m de déplacement supplémentaires."},
    {"op": "trait", "espece": "Centaure", "nom": "Sabots",
     "description": "Vos sabots sont des armes naturelles avec lesquelles vous pouvez porter des attaques à mains nues. "
                    "Un coup réussi inflige 1d6 + votre modificateur de Force dégâts contondants."},

    # ------------------------------------------------------------------ Changelin (MotM)
    {"op": "set", "espece": "Changelin", "champ": "source", "valeur": MOTM},
    {"op": "set", "espece": "Changelin", "champ": "caracteristiques", "valeur": ALT},
    {"op": "set", "espece": "Changelin", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "trait", "espece": "Changelin", "nom": "Taille et type", "description": "Moyenne ou Petite (au choix) ; type Fée."},
    {"op": "trait", "espece": "Changelin", "nom": "Changeforme",
     "description": "Par une action, vous modifiez votre apparence et votre voix (traits, couleurs, longueur des "
                    "cheveux, sexe, taille entre Moyenne et Petite), y compris pour paraître d'une autre espèce, sans "
                    "changer vos statistiques. Vous ne pouvez pas copier un individu jamais vu, devez garder la même "
                    "disposition de membres, et vos vêtements ne changent pas. La forme dure jusqu'à ce que vous "
                    "repreniez votre forme véritable par une action ou mouriez."},
    {"op": "trait", "espece": "Changelin", "nom": "Instincts du changelin",
     "description": "Vous obtenez la maîtrise de deux compétences parmi Intimidation, Intuition, Persuasion, "
                    "Représentation et Tromperie."},

    # ------------------------------------------------------------------ Changeling ténébreux (homebrew : rééquilibré)
    {"op": "trait", "espece": "Changeling ténébreux", "nom": "Marcheur des ombres",
     "description": "Vous avez l'avantage aux tests de Dextérité (Discrétion) tant que vous vous trouvez dans une zone "
                    "de lumière faible ou d'obscurité. Vous pouvez tenter de vous cacher dans une telle zone même si "
                    "vous n'êtes que légèrement masqué."},
    {"op": "trait", "espece": "Changeling ténébreux", "nom": "Frappe ténébreuse",
     "description": "Une fois par repos court ou long, lorsque vous touchez avec une attaque une créature surprise ou "
                    "incapable de vous voir, vous lui infligez des dégâts nécrotiques supplémentaires : 1d6, 2d6 au "
                    "niveau 6, 3d6 au niveau 11, 4d6 au niveau 16."},

    # ------------------------------------------------------------------ Conil (homebrew calqué sur le Harengon)
    {"op": "set", "espece": "Conil", "champ": "caracteristiques", "valeur": ALT},
    {"op": "trait", "espece": "Conil", "nom": "Comme un lièvre",
     "description": "Vous ajoutez votre bonus de maîtrise à vos jets d'initiative."},
    {"op": "trait", "espece": "Conil", "nom": "Gambade heureuse",
     "description": "Lorsque vous ratez un jet de sauvegarde de Dextérité, vous pouvez utiliser votre réaction pour "
                    "lancer 1d4 et l'ajouter au résultat, ce qui peut transformer l'échec en réussite. Impossible si "
                    "vous êtes à terre ou si votre vitesse est de 0."},
    {"op": "trait", "espece": "Conil", "nom": "Saut de lapin",
     "description": "Par une action bonus, si votre vitesse n'est pas de 0, vous sautez d'une distance égale à 1,50 m × "
                    "votre bonus de maîtrise sans provoquer d'attaque d'opportunité. Utilisable un nombre de fois égal "
                    "à votre bonus de maîtrise par repos long."},

    # ------------------------------------------------------------------ Demi-dragon (homebrew : aligné sur le drakéide)
    {"op": "trait", "espece": "Demi-dragon", "nom": "Arme de souffle",
     "description": "Par une action, vous exhalez l'énergie de votre ascendance dans un cône de 4,50 m. Chaque créature "
                    "dans la zone effectue un JS de Dextérité (de Constitution pour le froid ou le poison), DD 8 + "
                    "votre bonus de maîtrise + votre modificateur de Constitution, et subit 2d6, 3d6 au niveau 6, 4d6 "
                    "au niveau 11, 5d6 au niveau 16 dégâts du type de l'ascendance, ou la moitié en cas de réussite. "
                    "Utilisable 1 fois par repos court ou long."},
    {"op": "trait", "espece": "Demi-dragon", "nom": "Griffes",
     "description": "Vos griffes sont des armes naturelles avec lesquelles vous pouvez porter des attaques à mains nues. "
                    "Un coup réussi inflige 1d6 + votre modificateur de Force dégâts tranchants."},

    # ------------------------------------------------------------------ Dhampir (Ravenloft)
    {"op": "set", "espece": "Dhampir", "champ": "caracteristiques", "valeur": ALT},
    {"op": "vitesse", "espece": "Dhampir", "valeur": 10.5},
    {"op": "trait", "espece": "Dhampir", "nom": "Ascension de l'araignée",
     "description": "Vous avez une vitesse d'escalade égale à votre vitesse de marche (10,50 m). À partir du niveau 3, "
                    "vous pouvez vous déplacer sur les surfaces verticales et au plafond, la tête en bas, en gardant "
                    "les mains libres."},
    {"op": "trait", "espece": "Dhampir", "nom": "Morsure vampirique",
     "description": "Votre morsure est une arme naturelle maîtrisée (attaque à mains nues) qui inflige 1d4 + votre "
                    "modificateur de Constitution dégâts perforants ; vous avez l'avantage à ce jet d'attaque tant qu'il "
                    "vous manque au moins la moitié de vos points de vie. Quand elle blesse une créature qui n'est ni "
                    "une Créature artificielle ni un Mort-vivant, vous pouvez soit récupérer autant de PV que les "
                    "dégâts infligés, soit ajouter ce nombre à votre prochain test de caractéristique ou jet d'attaque. "
                    "Ce bénéfice est utilisable un nombre de fois égal à votre bonus de maîtrise par repos long."},

    # ------------------------------------------------------------------ Drakéide (MdJ 2014)
    {"op": "trait", "espece": "Drakéide", "nom": "Ascendance draconique",
     "description": "Choisissez un dragon, qui fixe le type de dégâts et la zone de votre souffle : Noir ou Cuivre "
                    "(acide, ligne 1,50 × 9 m, JS Dex), Bleu ou Bronze (foudre, ligne 1,50 × 9 m, JS Dex), Airain "
                    "(feu, ligne 1,50 × 9 m, JS Dex), Or ou Rouge (feu, cône 4,50 m, JS Dex), Vert (poison, cône "
                    "4,50 m, JS Con), Argent ou Blanc (froid, cône 4,50 m, JS Con)."},
    {"op": "trait", "espece": "Drakéide", "nom": "Souffle",
     "description": "Par une action, vous soufflez l'énergie de votre ascendance dans la zone indiquée. Chaque créature "
                    "touchée effectue le JS correspondant, DD 8 + votre bonus de maîtrise + votre modificateur de "
                    "Constitution, et subit 2d6, 3d6 au niveau 6, 4d6 au niveau 11, 5d6 au niveau 16 dégâts, la "
                    "moitié en cas de réussite. Utilisable 1 fois par repos court ou long."},

    # ------------------------------------------------------------------ Duergar (MotM)
    {"op": "set", "espece": "Duergar", "champ": "caracteristiques", "valeur": ALT},
    {"op": "set", "espece": "Duergar", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "vitesse", "espece": "Duergar", "valeur": 9},
    {"op": "trait", "espece": "Duergar", "nom": "Résilience naine",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre l'état empoisonné et la résistance aux dégâts "
                    "de poison."},
    {"op": "rename_trait", "espece": "Duergar", "nom": "Résistance mentale", "nouveau": "Fortitude psionique"},
    {"op": "trait", "espece": "Duergar", "nom": "Fortitude psionique",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre les états charmé et étourdi."},
    {"op": "trait", "espece": "Duergar", "nom": "Magie duergar",
     "description": "Niveau 3 : *Agrandissement/Rapetissement* (sur vous uniquement, 1/repos long) ; Niveau 5 : "
                    "*Invisibilité* (sur vous uniquement, 1/repos long). Ces sorts se lancent sans composante "
                    "matérielle, et vous pouvez aussi les lancer avec vos emplacements de sort de niveau 2 ou "
                    f"supérieur. Caractéristique d'incantation : {CARAC_INC}."},

    # ------------------------------------------------------------------ Eladrin (MotM)
    {"op": "set", "espece": "Eladrin", "champ": "caracteristiques", "valeur": ALT},
    {"op": "set", "espece": "Eladrin", "champ": "langues", "valeur": ["Commun", "Au choix"]},
    {"op": "trait", "espece": "Eladrin", "nom": "Vision dans le noir", "description": "18 mètres."},
    {"op": "trait", "espece": "Eladrin", "nom": "Ascendance féerique",
     "description": "Vous avez l'avantage aux jets de sauvegarde pour éviter ou mettre fin à l'état charmé."},
    {"op": "trait", "espece": "Eladrin", "nom": "Sens aiguisés", "description": "Maîtrise de la compétence Perception."},
    {"op": "trait", "espece": "Eladrin", "nom": "Transe",
     "description": "Vous n'avez pas besoin de dormir et la magie ne peut pas vous endormir. Un repos long vous demande "
                    "4 heures de méditation consciente, à l'issue desquelles vous gagnez deux maîtrises d'arme ou "
                    "d'outil de votre choix jusqu'à votre prochain repos long."},
    {"op": "trait", "espece": "Eladrin", "nom": "Pas féerique",
     "description": "Par une action bonus, vous vous téléportez jusqu'à 9 m dans un espace inoccupé que vous voyez. "
                    "Utilisable un nombre de fois égal à votre bonus de maîtrise par repos long."},
    {"op": "trait", "espece": "Eladrin", "nom": "Changement de saison",
     "description": "À la fin d'un repos long, vous adoptez une saison qui, à partir du niveau 3, ajoute un effet à "
                    "votre Pas féerique (DD 8 + votre bonus de maîtrise + Int, Sag ou Cha choisi en adoptant l'espèce). "
                    "Automne : jusqu'à deux créatures visibles à 3 m ou moins réussissent un JS de Sagesse ou sont "
                    "charmées 1 minute (fin si vous ou vos alliés les blessez). Hiver : avant la téléportation, une "
                    "créature visible à 1,50 m réussit un JS de Sagesse ou est effrayée jusqu'à la fin de votre "
                    "prochain tour. Printemps : vous téléportez à votre place une créature consentante touchée à "
                    "1,50 m. Été : après la téléportation, chaque créature de votre choix à 1,50 m subit des dégâts "
                    "de feu égaux à votre bonus de maîtrise."},

    # ------------------------------------------------------------------ Elfe astral (Spelljammer)
    {"op": "trait", "espece": "Elfe astral", "nom": "Feu astral",
     "description": "Connaît un sort mineur au choix parmi *Lumières dansantes*, *Lumière* ou *Flamme sacrée*. "
                    f"Caractéristique d'incantation : {CARAC_INC}."},
    {"op": "trait", "espece": "Elfe astral", "nom": "Pas de lumière étoilée",
     "description": "Par une action bonus, vous vous téléportez jusqu'à 9 m dans un espace inoccupé que vous voyez. "
                    "Utilisable un nombre de fois égal à votre bonus de maîtrise par repos long."},
    {"op": "trait", "espece": "Elfe astral", "nom": "Trance astrale",
     "description": "Vous n'avez pas besoin de dormir et la magie ne peut pas vous endormir. Un repos long vous demande "
                    "4 heures de méditation consciente, à l'issue desquelles vous gagnez la maîtrise d'une compétence "
                    "et d'une arme ou d'un outil de votre choix jusqu'à votre prochain repos long."},

    # ------------------------------------------------------------------ Elfe des mers (MotM)
    {"op": "set", "espece": "Elfe des mers", "champ": "source", "valeur": MOTM},
    {"op": "rename_trait", "espece": "Elfe des mers", "nom": "Respiration aquatique", "nouveau": "Enfant de la mer"},
    {"op": "trait", "espece": "Elfe des mers", "nom": "Enfant de la mer",
     "description": "Vous avez une vitesse de nage égale à votre vitesse de marche (9 m) et vous pouvez respirer aussi "
                    "bien l'air que l'eau."},
    {"op": "rename_trait", "espece": "Elfe des mers", "nom": "Maîtrise", "nouveau": "Sens aiguisés"},
    {"op": "trait", "espece": "Elfe des mers", "nom": "Sens aiguisés", "description": "Maîtrise de la compétence Perception."},
    {"op": "trait", "espece": "Elfe des mers", "nom": "Ascendance féerique",
     "description": "Vous avez l'avantage aux jets de sauvegarde pour éviter ou mettre fin à l'état charmé."},
    {"op": "rename_trait", "espece": "Elfe des mers", "nom": "Communication", "nouveau": "Ami de la mer"},
    {"op": "trait", "espece": "Elfe des mers", "nom": "Ami de la mer",
     "description": "Vous pouvez communiquer des idées simples à toute Bête, tout Élémentaire et toute Créature "
                    "monstrueuse disposant d'une vitesse de nage."},
    {"op": "trait", "espece": "Elfe des mers", "nom": "Trance",
     "description": "Vous n'avez pas besoin de dormir et la magie ne peut pas vous endormir. Un repos long vous demande "
                    "4 heures de méditation consciente, à l'issue desquelles vous gagnez deux maîtrises d'arme ou "
                    "d'outil de votre choix jusqu'à votre prochain repos long."},

    # ------------------------------------------------------------------ Elfe sylvestre (MdJ)
    {"op": "trait", "espece": "Elfe sylvestre", "nom": "Cachette naturelle",
     "description": "Vous pouvez tenter de vous cacher même lorsque vous n'êtes que légèrement masqué par un phénomène "
                    "naturel : feuillage, forte pluie, neige qui tombe, brume ou autre."},

    # ------------------------------------------------------------------ Enfant de la lune (homebrew : rééquilibré)
    {"op": "trait", "espece": "Enfant de la lune", "nom": "Griffes lupines",
     "description": "Vos griffes sont des armes naturelles avec lesquelles vous pouvez porter des attaques à mains nues. "
                    "Un coup réussi inflige 1d6 + votre modificateur de Force dégâts tranchants."},
    {"op": "trait", "espece": "Enfant de la lune", "nom": "Posture hybride",
     "description": "Par une action bonus, vous adoptez une forme bestiale partielle pendant 1 minute (1 fois par repos "
                    "court ou long). Vous gagnez des points de vie temporaires égaux à 2 × votre bonus de maîtrise, et "
                    "vos Griffes lupines infligent 1d4 dégâts tranchants supplémentaires pendant la durée. Vous "
                    "pouvez reprendre votre forme normale par une action bonus."},

    # ------------------------------------------------------------------ Fadette (MotM)
    {"op": "set", "espece": "Fadette", "champ": "caracteristiques", "valeur": ALT},
    {"op": "trait", "espece": "Fadette", "nom": "Taille", "description": "Petite ; type Fée."},
    {"op": "trait", "espece": "Fadette", "nom": "Vol",
     "description": "Vous disposez d'une vitesse de vol égale à votre vitesse de marche (9 m). Vous ne pouvez pas "
                    "l'utiliser si vous portez une armure intermédiaire ou lourde."},
    {"op": "trait", "espece": "Fadette", "nom": "Magie des fadettes",
     "description": "Connaît le sort mineur *Druidisme* ; Niveau 3 : *Lueurs féeriques* (1/repos long) ; Niveau 5 : "
                    "*Agrandissement/Rapetissement* (1/repos long). Vous pouvez aussi lancer ces deux sorts avec vos "
                    f"emplacements de sort de niveau approprié. Caractéristique d'incantation : {CARAC_INC}."},

    # ------------------------------------------------------------------ Féral (MotM)
    {"op": "set", "espece": "Féral", "champ": "source", "valeur": MOTM},
    {"op": "set", "espece": "Féral", "champ": "caracteristiques", "valeur": ALT},
    {"op": "trait", "espece": "Féral", "nom": "Métamorphose",
     "description": "Par une action bonus, vous prenez une apparence bestiale pendant 1 minute (fin anticipée par une "
                    "action bonus ou si vous mourez) et gagnez des points de vie temporaires égaux à 2 × votre bonus "
                    "de maîtrise. Utilisable un nombre de fois égal à votre bonus de maîtrise par repos long. Vous "
                    "choisissez une forme à l'adoption de l'espèce (voir Formes de métamorphose)."},
    {"op": "trait", "espece": "Féral", "nom": "Formes de métamorphose",
     "description": "Peau de bête : +1d6 PV temporaires supplémentaires et +1 à la CA. Longues dents : par une action "
                    "bonus à chaque tour, attaque à mains nues avec vos crocs, 1d6 + votre modificateur de Force dégâts "
                    "perforants. Pas rapides : +3 m de vitesse, et par une réaction, quand une créature termine son "
                    "tour à 1,50 m ou moins de vous, déplacement de 3 m sans provoquer d'attaque d'opportunité. Chasse "
                    "sauvage : avantage aux tests de Sagesse, et aucune créature à 9 m ou moins n'a l'avantage à ses "
                    "jets d'attaque contre vous (sauf si vous êtes neutralisé)."},

    # ------------------------------------------------------------------ Firbolg (MotM)
    {"op": "set", "espece": "Firbolg", "champ": "caracteristiques", "valeur": ALT},
    {"op": "trait", "espece": "Firbolg", "nom": "Magie firbolg",
     "description": "Lancement de *Déguisement* (1/repos long) et de *Détection de la magie* (1/repos long). Avec ce "
                    "Déguisement, vous pouvez paraître jusqu'à 90 cm plus petit, ce qui permet de passer pour un "
                    "humain ou un elfe. Vous pouvez aussi lancer ces sorts avec vos emplacements de sort. "
                    f"Caractéristique d'incantation : {CARAC_INC}."},
    {"op": "rename_trait", "espece": "Firbolg", "nom": "Invisibilité", "nouveau": "Pas invisible"},
    {"op": "trait", "espece": "Firbolg", "nom": "Pas invisible",
     "description": "Par une action bonus, vous devenez invisible jusqu'au début de votre prochain tour, ou jusqu'à ce "
                    "que vous attaquiez, infligiez des dégâts ou imposiez un jet de sauvegarde. Utilisable un nombre de "
                    "fois égal à votre bonus de maîtrise par repos long."},
    {"op": "rename_trait", "espece": "Firbolg", "nom": "Communication", "nouveau": "Parler aux bêtes et aux plantes"},
    {"op": "trait", "espece": "Firbolg", "nom": "Parler aux bêtes et aux plantes",
     "description": "Vous pouvez communiquer de façon limitée avec les Bêtes, les Plantes et les végétaux, qui comprennent "
                    "le sens de vos paroles sans que vous compreniez forcément les leurs. Vous avez l'avantage aux tests "
                    "de Charisme destinés à les influencer."},
    {"op": "trait", "espece": "Firbolg", "nom": "Puissante carrure",
     "description": "Vous comptez comme une créature de taille Grande pour déterminer votre capacité de charge et le "
                    "poids que vous pouvez pousser, tirer ou soulever."},

    # ------------------------------------------------------------------ Forgelier (Eberron)
    {"op": "trait", "espece": "Forgelier", "nom": "Taille et type",
     "description": "Moyenne ; type Humanoïde (et non Créature artificielle)."},
    {"op": "trait", "espece": "Forgelier", "nom": "Résilience",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre l'état empoisonné, la résistance aux dégâts de "
                    "poison et l'immunité aux maladies. La magie ne peut pas vous endormir."},
    {"op": "trait", "espece": "Forgelier", "nom": "Besoin vital",
     "description": "Vous n'avez besoin ni de manger, ni de boire, ni de respirer, ni de dormir."},
    {"op": "trait", "espece": "Forgelier", "nom": "Protection intégrée",
     "description": "Vous gagnez un bonus de +1 à la CA. Vous ne pouvez revêtir une armure qu'en l'intégrant à votre "
                    "corps, ce qui prend 1 heure en restant en contact avec elle ; tant que vous êtes en vie, elle ne "
                    "peut pas vous être retirée contre votre gré."},
]

CORRIGE = [
    ("mineur", "Aarakocra / caractéristiques", "Dex +2, Sag +1 (EE)", "MotM : +2, +1 (ou +1, +1, +1)"),
    ("majeur", "Aarakocra / vitesse", "Vol = marche sans précision (mélange EE/MotM)", "Vol 9 m = marche, interdit en armure intermédiaire/lourde ; marche 9 m (défaut)"),
    ("mineur", "Aarakocra / Serres", "1d4 tranchants", "1d6 + For tranchants (mains nues)"),
    ("majeur", "Aarakocra / Appel du vent", "Trait absent", "Ajouté : Bourrasque niv. 3, 1/repos long ou emplacements, Int/Sag/Cha"),
    ("mineur", "Aarakocra / langues", "Commun, Aarakocra", "Commun + Au choix (MotM)"),
    ("info", "Aarakocra / version", "Données EE", "Toutes les données alignées sur MotM"),
    ("majeur", "Aasimar protecteur / Mains guérisseuses", "Trait absent", "Ajouté (Volo) : action, PV = niveau, 1/repos long"),
    ("majeur", "Aasimar déchu / Mains guérisseuses", "Trait absent", "Ajouté (Volo) : action, PV = niveau, 1/repos long"),
    ("mineur", "Aasimar protecteur / caractéristiques", "+2, +1 libres", "Volo : Cha +2, Sag +1"),
    ("mineur", "Aasimar déchu / caractéristiques", "+2, +1 libres", "Volo : Cha +2, For +1"),
    ("majeur", "Aasimar protecteur / Transformation céleste", "Action non précisée", "Renommé Âme radieuse : action, vol 9 m, +niveau radiants 1/tour, 1 min, 1/repos long"),
    ("majeur", "Aasimar déchu / Voile nécrotique", "Effroi et DD absents", "Action, effroi à 3 m (JS Cha DD 8 + maîtrise + Cha), +niveau nécrotiques 1/tour"),
    ("mineur", "Aasimar / langues", "Commun + Au choix", "Volo : Commun, Céleste"),
    ("info", "Aasimar / version", "Mélange Volo/MotM", "Sous-races = Volo : source fixée à « Guide de Volo », taille Moyenne"),
    ("mineur", "Autognome / caractéristiques", "+2, +1", "+2, +1 (ou +1, +1, +1)"),
    ("mineur", "Autognome / taille et type", "Absents", "Trait Taille et type : Petite, Créature artificielle"),
    ("majeur", "Autognome / Conçu pour réussir", "6 fois/repos long", "Bonus de maîtrise fois/repos long"),
    ("majeur", "Autognome / Machine de guérison", "Réparation rend 1d6 PV", "Réparation : dépense d'un dé de vie + Con ; liste des sorts de soin officielle"),
    ("mineur", "Autognome / Nature mécanique", "Respiration omise", "Pas besoin de respirer ajouté"),
    ("mineur", "Centaure / Charge", "Formulation imprécise", "9 m en ligne droite + attaque d'arme au corps à corps → Sabots en action bonus"),
    ("mineur", "Centaure / Morphologie équine", "Capacité vague, escalade absente", "Renommé ; compte comme Grande, +4 m par mètre d'escalade"),
    ("mineur", "Centaure / Sabots", "1d6 sans modificateur", "1d6 + For contondants"),
    ("mineur", "Centaure / type", "Absent", "Moyenne, Fée"),
    ("mineur", "Changelin / caractéristiques", "Cha +2, +1 (Eberron)", "MotM : +2, +1 (ou +1, +1, +1)"),
    ("mineur", "Changelin / langues", "Commun + 2 au choix", "Commun + Au choix (MotM)"),
    ("mineur", "Changelin / Instincts", "Représentation absente", "Liste MotM à 5 compétences"),
    ("mineur", "Changelin / taille et type", "Absents", "Moyenne ou Petite, Fée"),
    ("info", "Changelin / version", "Eberron malgré « MotM / Eberron »", "Version MotM (la plus récente) ; source fixée à Monstres du Multivers"),
    ("mineur", "Changeling ténébreux / Frappe ténébreuse", "Dégâts et repos non chiffrés", "Homebrew rééquilibré : 1d6 → 4d6 (niv. 6/11/16), 1/repos court ou long"),
    ("majeur", "Conil / Saut de lapin", "9 m fixe, 6 fois/repos long", "1,50 m × maîtrise, maîtrise fois/repos long"),
    ("mineur", "Conil / Gambade heureuse", "Réaction non précisée", "Réaction, +1d4 au JS de Dex raté"),
    ("majeur", "Demi-dragon / Arme de souffle", "Ni dégâts, ni DD, ni utilisations", "Cône 4,50 m, DD 8 + maîtrise + Con, 2d6 → 5d6, 1/repos court ou long"),
    ("majeur", "Dhampir / vitesse", "9 m par défaut", "10,5 m (marche et escalade)"),
    ("mineur", "Dhampir / Ascension de l'araignée", "Murs et plafonds dès le niveau 1", "Escalade niv. 1, surfaces verticales/plafonds niv. 3"),
    ("majeur", "Dhampir / Morsure vampirique", "Soin systématique, sans limite", "1d4 + Con ; soin ou bonus au choix, maîtrise fois/repos long"),
    ("mineur", "Dhampir / caractéristiques", "+2, +1", "+2, +1 (ou +1, +1, +1)"),
    ("majeur", "Drakéide / Souffle", "Absent", "Ajouté : action, 2d6 → 5d6, DD 8 + maîtrise + Con, 1/repos court ou long"),
    ("mineur", "Drakéide / Ascendance draconique", "Pas de table des dragons", "Table des 10 dragons (dégâts, zone, JS)"),
    ("majeur", "Duergar / vitesse", "7,5 m (MToF)", "MotM : 9 m"),
    ("mineur", "Duergar / Magie duergar", "Cible et carac. non précisées", "Sur soi, sans composante matérielle, emplacements, Int/Sag/Cha"),
    ("mineur", "Duergar / langues", "Commun, Nain", "Commun + Au choix (MotM)"),
    ("mineur", "Duergar / caractéristiques", "+2, +1", "+2, +1 (ou +1, +1, +1)"),
    ("mineur", "Duergar / Résistance mentale", "Nom non officiel", "Renommé Fortitude psionique"),
    ("majeur", "Eladrin / Changement de saison", "Sorts mineurs inventés", "Effets de saison MotM sur le Pas féerique (niv. 3), DD 8 + maîtrise + Int/Sag/Cha"),
    ("majeur", "Eladrin / Pas féerique", "1/repos long", "Action bonus, 9 m, maîtrise fois/repos long"),
    ("majeur", "Eladrin / traits elfiques", "Absents", "Vision 18 m, Ascendance féerique, Sens aiguisés, Transe ajoutés"),
    ("mineur", "Eladrin / caractéristiques", "Dex +2, +1 (Int ou Cha)", "+2, +1 (ou +1, +1, +1)"),
    ("mineur", "Eladrin / langues", "Commun, Elfique", "Commun + Au choix (MotM)"),
    ("majeur", "Elfe des mers / vitesse de nage", "Absente", "Enfant de la mer : nage = marche (9 m), respiration air/eau"),
    ("mineur", "Elfe des mers / Transe", "Sans maîtrises temporaires", "2 maîtrises d'arme/outil jusqu'au repos long"),
    ("mineur", "Elfe des mers / Ami de la mer", "« Animaux marins »", "Bêtes, Élémentaires, Créatures monstrueuses avec vitesse de nage (MotM)"),
    ("mineur", "Elfe des mers / source", "Libellé long", "« Monstres du Multivers »"),
    ("mineur", "Elfe des mers / Maîtrise", "Perception et charme confondus", "Séparés en Sens aiguisés et Ascendance féerique"),
    ("majeur", "Elfe astral / Pas de lumière étoilée", "6 fois/repos long", "Action bonus, 9 m, maîtrise fois/repos long"),
    ("mineur", "Elfe astral / Feu astral", "Carac. absente", "Int, Sag ou Cha"),
    ("mineur", "Elfe astral / Transe astrale", "« Immunité au sommeil magique »", "Pas besoin de dormir, ne peut être endormi par magie ; compétence + arme/outil"),
    ("mineur", "Elfe sylvestre / Cachette naturelle", "Formulation vague", "Légèrement masqué par feuillage, pluie, neige, brume"),
    ("mineur", "Enfant de la lune / Posture hybride", "Valeurs non chiffrées", "Homebrew rééquilibré : action bonus, 1 min, 2 × maîtrise PV temp., +1d4 griffes, 1/repos court ou long"),
    ("majeur", "Fadette / vitesse de vol", "Sans valeur", "Vol 9 m = marche, interdit en armure intermédiaire/lourde"),
    ("mineur", "Fadette / Magie des fadettes", "Carac. absente, coquille", "Lueurs féeriques, emplacements, Int/Sag/Cha"),
    ("mineur", "Fadette / type", "Absent", "Petite, Fée"),
    ("mineur", "Fadette / caractéristiques", "+2, +1", "+2, +1 (ou +1, +1, +1)"),
    ("majeur", "Féral / source", "« Guide de Xanathar / Homebrew »", "Monstres du Multivers (version la plus récente du Shifter)"),
    ("majeur", "Féral / Métamorphose", "12 PV temp. fixes, usages absents", "2 × maîtrise PV temp., maîtrise fois/repos long"),
    ("mineur", "Féral / Peau de bête", "+1 CA seul", "+1d6 PV temp. et +1 CA"),
    ("mineur", "Féral / Longs crocs", "Ni action ni modificateur", "Action bonus, 1d6 + For perforants"),
    ("mineur", "Féral / Pas rapides", "+3 m seul", "+3 m et réaction de déplacement de 3 m"),
    ("mineur", "Féral / Chasse sauvage", "Avantage aux JS de Sagesse", "Avantage aux tests de Sagesse, pas d'avantage contre vous à 9 m"),
    ("mineur", "Féral / caractéristiques", "+2, +1", "+2, +1 (ou +1, +1, +1)"),
    ("majeur", "Firbolg / Pas invisible", "Fin du tour suivant, 6 fois", "Jusqu'au début du prochain tour ou attaque/dégâts/JS, maîtrise fois/repos long"),
    ("mineur", "Firbolg / Puissante carrure", "Absent", "Ajouté"),
    ("mineur", "Firbolg / Parler aux bêtes et plantes", "« Avantage de charme »", "Avantage aux tests de Charisme pour les influencer"),
    ("mineur", "Firbolg / Magie firbolg", "Option 90 cm absente", "Ajoutée, + emplacements, Int/Sag/Cha"),
    ("mineur", "Firbolg / caractéristiques", "+2, +1", "+2, +1 (ou +1, +1, +1)"),
    ("mineur", "Forgelier / Résilience", "Respiration omise", "Pas besoin de respirer ; sommeil magique"),
    ("mineur", "Forgelier / Protection intégrée", "+1 CA seul", "Armure intégrée en 1 h, inamovible contre son gré"),
    ("mineur", "Forgelier / type", "Absent", "Humanoïde"),
]

AUDIT = [
    ("info", "Bonus_Raciaux.json / vitesses spéciales", "Vol (Aarakocra, Fadette, Aasimar protecteur), nage (Elfe des mers) et escalade (Dhampir) restent textuels", "Aucun champ de vitesse spéciale dans le format de données ; décrites dans les traits"),
    ("info", "rules.RACE_SPELL_ABILITY", "Duergar (Int) et Firbolg (Sag) restent figés dans le code", "Hors périmètre (fichier interdit) ; les traits indiquent Int/Sag/Cha au choix"),
    ("info", "Autognome / vitesse", "9 m inscrit dans vitesses (redondant)", "Aucune opération de suppression ; valeur correcte"),
    ("info", "Drakéide / taille", "Taille absente, pas de vision dans le noir", "Conforme au MdJ 2014 (Moyenne) ; non bloquant"),
    ("info", "Changeling ténébreux / source", "Homebrew ; langue Ombrelante absente de Langues.json", "Rééquilibré sans audit officiel"),
    ("info", "Conil / source", "Homebrew, doublon du Harengon", "Chiffres alignés sur le Harengon"),
    ("info", "Demi-dragon / source", "Homebrew", "Souffle aligné sur le drakéide"),
    ("info", "Enfant de la lune / source", "Homebrew, recoupe le Féral", "Chiffres rééquilibrés"),
    ("info", "Elfe sylvestre", "Conforme au MdJ", "Seule la description de Cachette naturelle a été précisée"),
]
