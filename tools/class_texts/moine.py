"""Descriptions enrichies — Moine (PHB, Xanathar, Tasha ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Moine"

KI_DD = "8 + votre bonus de maîtrise + votre modificateur de Sagesse"

BASE = {
    "Défense sans armure": (
        "Tant que vous ne portez aucune armure et ne maniez pas de bouclier, votre Classe d'Armure est égale à "
        "10 + votre modificateur de Dextérité + votre modificateur de Sagesse. Ce calcul ne se cumule pas avec "
        "une autre méthode de calcul de base de la CA (Défense sans armure d'une autre classe, Armure du mage…)."
    ),
    "Arts martiaux": (
        "Tant que vous êtes à mains nues ou ne maniez que des armes de moine (épée courte et armes courantes de "
        "corps à corps sans les propriétés lourde ni à deux mains), sans armure ni bouclier : vous pouvez utiliser "
        "votre modificateur de Dextérité au lieu de votre modificateur de Force pour les jets d'attaque et de dégâts ; "
        "vous pouvez lancer votre dé d'arts martiaux à la place des dégâts normaux de l'arme ou de la frappe à mains "
        "nues ; et lorsque vous effectuez l'action Attaquer avec l'une de ces armes ou à mains nues, vous pouvez "
        "porter une frappe à mains nues par une action bonus. Le dé d'arts martiaux vaut d4 au niveau 1, d6 au "
        "niveau 5, d8 au niveau 11 et d10 au niveau 17."
    ),
    "Ki": (
        "Vous disposez d'un nombre de points de ki égal à votre niveau de moine ; vous récupérez tous vos points "
        "dépensés à la fin d'un repos court ou long (au moins 30 minutes de méditation). Le DD des jets de "
        "sauvegarde contre vos aptitudes de ki est égal à " + KI_DD + ". Options de base : Déluge de coups (après "
        "l'action Attaquer, 1 ki et une action bonus pour porter deux frappes à mains nues), Défense patiente "
        "(1 ki, action bonus Esquiver) et Déplacement aérien (1 ki, action bonus Se désengager ou Foncer, distance "
        "de saut doublée pour le tour)."
    ),
    "Déplacement sans armure": (
        "Tant que vous ne portez ni armure ni bouclier, votre vitesse augmente de 3 m. Ce bonus passe à +4,50 m au "
        "niveau 6, +6 m au niveau 10, +7,50 m au niveau 14 et +9 m au niveau 18. À partir du niveau 9, vous pouvez "
        "vous déplacer le long des surfaces verticales et à la surface des liquides pendant votre tour sans tomber "
        "au cours du mouvement."
    ),
    "Arme dédiée (option Tasha)": (
        "À la fin d'un repos court ou long, vous pouvez toucher une arme que vous maîtrisez et qui n'a ni la "
        "propriété lourde ni la propriété spéciale, et méditer : elle devient pour vous une arme de moine jusqu'à "
        "ce que vous utilisiez de nouveau cette aptitude. Vous ne pouvez avoir qu'une arme dédiée à la fois."
    ),
    "Attaque alimentée par le ki (option Tasha)": (
        "Lorsque vous dépensez au moins 1 point de ki dans le cadre de votre action pendant votre tour, vous "
        "pouvez, par une action bonus avant la fin de ce tour, effectuer une attaque avec une frappe à mains nues "
        "ou une arme de moine."
    ),
    "Tradition monastique": (
        "Au niveau 3, vous vous engagez dans une tradition monastique (sous-classe) qui façonne votre style de "
        "combat et votre usage du ki. Elle vous confère des aptitudes aux niveaux 3, 6, 11 et 17."
    ),
    "Parade de projectiles": (
        "Par une réaction, lorsqu'une attaque à distance avec une arme vous touche, vous réduisez ses dégâts de "
        "1d10 + votre modificateur de Dextérité + votre niveau de moine. Si les dégâts tombent à 0 et que vous avez "
        "une main libre, vous attrapez le projectile (s'il est assez petit). Vous pouvez alors dépenser 1 point de "
        "ki pour le relancer aussitôt dans la même réaction : attaque à distance (portée 6 m/18 m) avec maîtrise, "
        "considérée comme une arme de moine, infligeant votre dé d'arts martiaux + votre modificateur de Dextérité."
    ),
    "Chute ralentie": (
        "Par une réaction lorsque vous tombez, vous réduisez les dégâts de chute subis d'un montant égal à "
        "5 × votre niveau de moine."
    ),
    "Guérison accélérée (option Tasha)": (
        "Par une action, vous dépensez 2 points de ki et lancez votre dé d'arts martiaux : vous récupérez un "
        "nombre de points de vie égal au résultat + votre bonus de maîtrise."
    ),
    "Attaque supplémentaire": (
        "À partir du niveau 5, lorsque vous effectuez l'action Attaquer pendant votre tour, vous pouvez attaquer "
        "deux fois au lieu d'une. L'attaque à mains nues de l'action bonus d'Arts martiaux ou du Déluge de coups "
        "s'y ajoute."
    ),
    "Frappe étourdissante": (
        "Lorsque vous touchez une créature avec une attaque d'arme au corps à corps, vous pouvez dépenser 1 point de "
        "ki pour tenter de l'étourdir. Elle doit réussir un jet de sauvegarde de Constitution (DD " + KI_DD + ") ou "
        "être étourdie jusqu'à la fin de votre prochain tour. Vous pouvez tenter cette frappe à chaque attaque qui "
        "touche, tant qu'il vous reste du ki."
    ),
    "Visée concentrée (option Tasha)": (
        "Lorsque vous ratez un jet d'attaque, vous pouvez dépenser de 1 à 3 points de ki pour augmenter le "
        "résultat de ce jet de 2 par point dépensé, ce qui peut transformer l'échec en réussite."
    ),
    "Frappes renforcées par le Ki": (
        "À partir du niveau 6, vos frappes à mains nues comptent comme magiques pour surmonter la résistance et "
        "l'immunité aux attaques et aux dégâts non magiques."
    ),
    "Dérobade": (
        "Lorsqu'un effet vous permet de faire un jet de sauvegarde de Dextérité pour ne subir que la moitié des "
        "dégâts (souffle de dragon, Boule de feu…), vous ne subissez aucun dégât en cas de réussite et seulement "
        "la moitié en cas d'échec."
    ),
    "Sérénité": (
        "Par une action, vous mettez fin à un effet qui vous impose l'état charmé ou effrayé."
    ),
    "Pureté du corps": (
        "À partir du niveau 10, votre maîtrise du ki vous rend immunisé contre les maladies ainsi que contre les "
        "dégâts de poison et l'état empoisonné."
    ),
    "Langue du soleil et de la lune": (
        "Vous comprenez toutes les langues parlées. De plus, toute créature capable de comprendre une langue "
        "comprend ce que vous dites."
    ),
    "Âme diamantée": (
        "Vous obtenez la maîtrise de tous les jets de sauvegarde. De plus, chaque fois que vous ratez un jet de "
        "sauvegarde, vous pouvez dépenser 1 point de ki pour le relancer ; vous devez conserver le second résultat."
    ),
    "Corps intemporel": (
        "Votre ki vous préserve : vous ne souffrez plus des affres de la vieillesse et ne pouvez pas être vieilli "
        "par magie. Vous pouvez toujours mourir de vieillesse. Vous n'avez plus besoin de nourriture ni d'eau."
    ),
    "Corps vide": (
        "Par une action, vous dépensez 4 points de ki pour devenir invisible pendant 1 minute ; pendant ce temps, "
        "vous avez aussi la résistance à tous les dégâts, sauf de force. En outre, vous pouvez dépenser 8 points de "
        "ki pour lancer le sort Projection astrale sans composantes matérielles, mais vous seul pouvez être projeté."
    ),
    "Yô perfectionné": (
        "Au niveau 20, lorsque vous jouez l'initiative et qu'il ne vous reste aucun point de ki, vous en "
        "récupérez 4."
    ),
}

SUB = {
    "Voie de la Paume": {
        "Technique de la paume": (
            "Chaque fois que vous touchez une créature avec l'une des frappes de votre Déluge de coups, vous pouvez "
            "lui imposer l'un de ces effets (sans coût de ki supplémentaire) : elle doit réussir un jet de "
            "sauvegarde de Dextérité (DD " + KI_DD + ") ou tomber à terre ; elle doit réussir un jet de sauvegarde "
            "de Force (même DD) ou être repoussée jusqu'à 4,50 m de vous ; ou elle ne peut pas effectuer de "
            "réaction jusqu'à la fin de votre prochain tour."
        ),
        "Plénitude physique": (
            "Par une action, vous récupérez un nombre de points de vie égal à 3 × votre niveau de moine. Vous devez "
            "terminer un repos long avant de pouvoir réutiliser cette aptitude."
        ),
        "Ataraxie": (
            "À la fin d'un repos long, vous bénéficiez de l'effet du sort Sanctuaire, qui dure jusqu'au début de "
            "votre prochain repos long (le sort peut prendre fin normalement, notamment si vous attaquez ou lancez "
            "un sort affectant un ennemi). Le DD du jet de sauvegarde de Sagesse est égal à " + KI_DD + "."
        ),
        "Paume vibratoire": (
            "Lorsque vous touchez une créature avec une frappe à mains nues, vous pouvez dépenser 3 points de ki "
            "pour y déclencher des vibrations imperceptibles qui durent un nombre de jours égal à votre niveau de "
            "moine (inoffensives sauf si vous agissez). Par une action, alors que vous êtes sur le même plan, vous "
            "y mettez fin : la cible fait un jet de sauvegarde de Constitution (DD " + KI_DD + "). En cas d'échec, "
            "elle tombe à 0 point de vie ; en cas de réussite, elle subit 10d10 dégâts nécrotiques. Une seule "
            "créature à la fois peut subir cet effet ; vous pouvez aussi annuler les vibrations sans dégâts."
        ),
    },
    "Voie de l'Ombre": {
        "Artiste des ombres": (
            "Vous connaissez le sort mineur Illusion mineure. Par une action, vous pouvez dépenser 2 points de ki "
            "pour lancer Ténèbres, Vision dans le noir, Passage sans trace ou Silence, sans composantes matérielles. "
            "Votre caractéristique d'incantation est la Sagesse et le DD est égal à " + KI_DD + "."
        ),
        "Foulée d'ombre": (
            "Lorsque vous êtes dans une zone de lumière faible ou d'obscurité, vous pouvez, par une action bonus, "
            "vous téléporter jusqu'à 18 m vers un espace inoccupé que vous voyez et qui est lui aussi plongé dans la "
            "lumière faible ou l'obscurité. Vous avez alors l'avantage sur la première attaque au corps à corps que "
            "vous effectuez avant la fin de ce tour."
        ),
        "Linceul d'ombre": (
            "Lorsque vous êtes dans une zone de lumière faible ou d'obscurité, vous pouvez utiliser votre action "
            "pour devenir invisible. Vous le restez jusqu'à ce que vous attaquiez, lanciez un sort ou entriez dans "
            "une zone de lumière vive."
        ),
        "Opportuniste": (
            "Lorsqu'une créature située dans un rayon de 1,50 m autour de vous est touchée par une attaque effectuée "
            "par quelqu'un d'autre que vous, vous pouvez utiliser votre réaction pour effectuer une attaque au corps "
            "à corps contre elle."
        ),
    },
    "Voie des Quatre Éléments": {
        "Disciple des éléments & Harmonisation": (
            "Vous apprenez Harmonisation élémentaire (par une action, petits effets sans danger : allumer ou "
            "éteindre une flamme, refroidir ou réchauffer 500 g de matière pendant 1 heure, déplacer air, eau, "
            "feu ou terre dans un cube de 1,50 m pendant 1 minute…) et une autre discipline élémentaire. Vous "
            "apprenez une discipline supplémentaire aux niveaux 6, 11 et 17, et pouvez en échanger une à chacun de "
            "ces niveaux. Les disciplines coûtent du ki et peuvent lancer des sorts (DD " + KI_DD + ") ; certaines "
            "permettent de dépenser du ki supplémentaire pour augmenter le niveau du sort. Le maximum de ki par "
            "sort est de 2 (niveaux 3-4), 3 (5-8), 4 (9-12), 5 (13-16) et 6 (17-20)."
        ),
        "Discipline élémentaire supplémentaire": (
            "Au niveau 6, vous apprenez une nouvelle discipline élémentaire et pouvez en remplacer une que vous "
            "connaissez. Accessibles dès ce niveau : Gong du sommet (3 ki, Fracassement), Griffe du vent du nord "
            "(3 ki, Immobilisation de personne). Votre plafond de ki par sort passe à 3 dès le niveau 5."
        ),
        "Discipline élémentaire avancée": (
            "Au niveau 11, vous apprenez une nouvelle discipline élémentaire. Les disciplines de niveau 11 "
            "deviennent accessibles : Flammes du phénix (4 ki, Boule de feu), Posture de brume (4 ki, Forme "
            "gazeuse, sur vous seul) et Chevaucher le vent (4 ki, Vol, sur vous seul)."
        ),
        "Maîtrise élémentaire ultime": (
            "Au niveau 17, vous apprenez une nouvelle discipline élémentaire, et celles de niveau 17 deviennent "
            "accessibles : Souffle de l'hiver (6 ki, Cône de froid), Défense de la montagne éternelle (5 ki, Peau "
            "de pierre, sur vous seul), Rivière de flammes affamées (5 ki, Mur de feu) et Vague de terre "
            "déferlante (6 ki, Mur de pierre). Votre plafond de ki par sort est désormais de 6."
        ),
    },
    "Voie de l'Âme solaire": {
        "Rayon de soleil radiant": (
            "Vous pouvez lancer des rayons de lumière : attaque à distance (portée 9 m) avec maîtrise, utilisant "
            "votre modificateur de Dextérité, qui inflige votre dé d'arts martiaux + votre modificateur de "
            "Dextérité dégâts radiants. Ces rayons peuvent remplacer chacune des attaques de l'action Attaquer. "
            "Si vous effectuez l'action Attaquer à votre tour, vous pouvez dépenser 1 point de ki pour lancer deux "
            "rayons supplémentaires par une action bonus."
        ),
        "Vague brûlante": (
            "Immédiatement après avoir effectué l'action Attaquer, vous pouvez dépenser 2 points de ki pour lancer "
            "Mains brûlantes au niveau 1 par une action bonus (DD " + KI_DD + "). Chaque point de ki supplémentaire "
            "augmente le niveau du sort de 1, le total dépensé ne pouvant dépasser la moitié de votre niveau de "
            "moine."
        ),
        "Éruption solaire ardente": (
            "Par une action, vous créez un orbe lumineux qui explose en un point choisi à 45 m au plus : chaque "
            "créature dans une sphère de 6 m de rayon fait un jet de sauvegarde de Constitution (DD " + KI_DD + ") "
            "ou subit 2d6 dégâts radiants (aucun dégât en cas de réussite). Cette version ne coûte pas de ki ; vous "
            "pouvez dépenser jusqu'à 3 points de ki pour ajouter 2d6 dégâts par point."
        ),
        "Bouclier solaire": (
            "Vous émettez une aura de lumière vive sur 9 m et de lumière faible sur 9 m de plus (activable ou "
            "désactivable par une action bonus). Tant qu'elle brille, lorsqu'une créature vous touche avec une "
            "attaque au corps à corps, vous pouvez utiliser votre réaction pour lui infliger 5 + votre modificateur "
            "de Sagesse dégâts radiants."
        ),
    },
    "Voie du Kensei": {
        "Armes du kensei, Parade agile & Tir du kensei": (
            "Vous choisissez deux armes de kensei (une de corps à corps, une à distance, sans les propriétés "
            "lourde ni spéciale) qui deviennent des armes de moine ; vous en ajoutez une aux niveaux 6, 11 et 17. "
            "Parade agile : si vous portez une frappe à mains nues lors de l'action Attaquer en tenant une arme de "
            "kensei de corps à corps, vous gagnez +2 à la CA jusqu'au début de votre prochain tour. Tir du kensei : "
            "par une action bonus, vos attaques avec une arme de kensei à distance infligent 1d4 dégâts "
            "supplémentaires jusqu'à la fin du tour. Voie du pinceau : maîtrise du matériel de calligraphe ou de "
            "peintre."
        ),
        "Armes de kensei magiques & Frappe précise": (
            "Vos attaques avec vos armes de kensei comptent comme magiques. Frappe précise : une fois par tour, "
            "lorsque vous touchez une cible avec une arme de kensei, vous pouvez dépenser 1 point de ki pour "
            "ajouter votre dé d'arts martiaux aux dégâts."
        ),
        "Lame affûtée": (
            "Par une action bonus, vous dépensez jusqu'à 3 points de ki pour conférer à une arme de kensei que vous "
            "tenez un bonus aux jets d'attaque et de dégâts égal au nombre de points dépensés, pendant 1 minute "
            "(ou jusqu'à ce que vous réutilisiez l'aptitude). Sans effet sur une arme magique qui possède déjà un "
            "bonus."
        ),
        "Précision infaillible": (
            "Une fois par tour, si vous ratez un jet d'attaque avec une arme de moine, vous pouvez le relancer. "
            "Vous ne pouvez le faire qu'une fois par tour, sans coût de ki."
        ),
    },
    "Voie du Maître ivre": {
        "Maîtrises supplémentaires & Techniques de l'homme ivre": (
            "Vous gagnez la maîtrise de la compétence Représentation et des ustensiles de brasseur (si vous l'avez "
            "déjà, une autre compétence ou outil). Technique de l'ivrogne : chaque fois que vous utilisez Déluge de "
            "coups, vous bénéficiez de l'action Se désengager et votre vitesse augmente de 3 m jusqu'à la fin du "
            "tour."
        ),
        "Chancellements éméchés": (
            "Relevé d'un bond : se relever ne vous coûte que 1,50 m de déplacement. Réorientation : lorsqu'une "
            "créature rate une attaque au corps à corps contre vous, vous pouvez dépenser 1 point de ki et utiliser "
            "votre réaction pour que l'attaque touche à la place une autre créature de votre choix (autre que "
            "l'attaquant) située à 1,50 m de vous."
        ),
        "Chance de l'ivrogne": (
            "Lorsque vous faites un test de caractéristique, un jet d'attaque ou un jet de sauvegarde avec le "
            "désavantage, vous pouvez dépenser 2 points de ki pour annuler ce désavantage sur ce jet."
        ),
        "Frénésie alcoolisée": (
            "Lorsque vous utilisez Déluge de coups, vous pouvez porter jusqu'à trois attaques supplémentaires "
            "(cinq au total), à condition que chaque attaque du Déluge vise une créature différente."
        ),
    },
    "Voie de l'Astre intérieur": {
        "Bras astraux": (
            "Par une action bonus, vous dépensez 1 point de ki pour invoquer des bras spectraux pendant 10 minutes. "
            "À leur apparition, chaque créature de votre choix à 3 m ou moins fait un jet de sauvegarde de "
            "Dextérité (DD " + KI_DD + ") ou subit deux dés d'arts martiaux de dégâts de force. Tant qu'ils sont "
            "présents : vous utilisez votre modificateur de Sagesse au lieu de votre modificateur de Force pour les "
            "tests et jets de sauvegarde de Force ; vos frappes à mains nues avec les bras ont une allonge accrue "
            "de 1,50 m, peuvent utiliser votre modificateur de Sagesse ou de Dextérité et infligent des dégâts de "
            "force."
        ),
        "Visage astral": (
            "Par une action bonus, vous dépensez 1 point de ki pour invoquer un visage astral pendant 10 minutes "
            "(se combine avec les bras). Vision astrale : vous voyez normalement à 36 m dans les ténèbres, même "
            "magiques. Sagesse de l'esprit : avantage aux tests de Sagesse (Intuition) et de Charisme "
            "(Intimidation). Parole de l'esprit : votre voix porte jusqu'à 180 m, ou n'est audible que d'une "
            "créature choisie à 18 m ou moins."
        ),
        "Corps de l'astre intérieur": (
            "Lorsque vos bras et votre visage astraux sont tous deux invoqués, vous gagnez : Détournement d'énergie "
            "(réaction, réduit des dégâts d'acide, de feu, de force, de foudre, de froid ou de tonnerre de "
            "1d10 + votre modificateur de Sagesse + votre niveau de moine) et Bras renforcés (une fois par tour, "
            "lorsque vous touchez avec les bras astraux, +1 dé d'arts martiaux de dégâts)."
        ),
        "Astre intérieur accompli": (
            "Par une action bonus, vous dépensez 5 points de ki pour invoquer bras, visage et corps astraux pendant "
            "10 minutes. Armure de l'esprit : +2 à la CA. Barrage astral : lorsque vous effectuez l'action "
            "Attaquer, vous pouvez porter trois attaques avec les bras astraux au lieu de deux."
        ),
    },
    "Voie de la Miséricorde": {
        "Instrument de charité, Main guérisseuse & Main meurtrissante": (
            "Maîtrise d'Intuition, de Médecine et du matériel d'herboriste, plus un masque rituel. Main guérisseuse : "
            "par une action, 1 point de ki pour qu'une créature touchée récupère un dé d'arts martiaux + votre "
            "modificateur de Sagesse points de vie ; lors d'un Déluge de coups, une frappe peut être remplacée par "
            "une Main guérisseuse sans coût de ki. Main meurtrissante : une fois par tour, quand vous touchez avec "
            "une frappe à mains nues, 1 point de ki ajoute un dé d'arts martiaux + votre modificateur de Sagesse "
            "dégâts nécrotiques."
        ),
        "Caresse médicale": (
            "Votre Main guérisseuse met aussi fin à une maladie ou à l'un de ces états : aveuglé, assourdi, "
            "paralysé, empoisonné ou étourdi. Votre Main meurtrissante peut en outre empoisonner la cible jusqu'à "
            "la fin de votre prochain tour."
        ),
        "Déluge de soins et meurtrissures": (
            "Lors d'un Déluge de coups, vous pouvez remplacer chaque frappe à mains nues par une Main guérisseuse "
            "sans dépenser de ki pour le soin. De plus, une frappe du Déluge peut déclencher la Main meurtrissante "
            "sans coût de ki (toujours une fois par tour au maximum)."
        ),
        "Main de l'ultime miséricorde": (
            "Par une action, vous touchez le cadavre d'une créature morte depuis moins de 24 heures et dépensez 5 "
            "points de ki : elle revient à la vie avec 4d10 + votre modificateur de Sagesse points de vie, libérée "
            "des états aveuglé, assourdi, paralysé, empoisonné et étourdi. Utilisable une fois par repos long."
        ),
    },
    "Voie du Sang": {
        "Frappe hématologique & Sutures de Ki": (
            "Frappe hématologique : lorsque vous touchez avec une frappe à mains nues, vous pouvez infliger des "
            "dégâts nécrotiques au lieu de contondants. Sutures de ki : par une action bonus, vous dépensez 1 point "
            "de ki et touchez une créature à 1,50 m ou moins ; elle récupère un dé d'arts martiaux + votre "
            "modificateur de Sagesse points de vie. Lors d'un Déluge de coups, vous pouvez remplacer une des deux "
            "frappes par une Suture sans coût de ki supplémentaire. Sans effet sur les créatures artificielles et "
            "les morts-vivants."
        ),
        "Marionnette sanguine": (
            "Lorsque vous touchez avec une frappe à mains nues une créature qui n'a pas tous ses points de vie, vous "
            "pouvez dépenser 2 points de ki. Elle fait un jet de sauvegarde de Constitution (DD " + KI_DD + ") ; en "
            "cas d'échec, vous la déplacez immédiatement de 4,50 m au plus dans la direction de votre choix (sans "
            "provoquer d'attaque d'opportunité de votre part, et pas dans un danger évident comme un précipice) et "
            "elle ne peut pas effectuer de réaction jusqu'au début de votre prochain tour. Créatures artificielles, "
            "élémentaires, vases et morts-vivants y sont immunisés. Une fois par tour."
        ),
        "Transfusion de combat": (
            "Lorsque vous obtenez un coup critique avec une frappe à mains nues, ou réduisez une créature hostile à "
            "0 point de vie avec une frappe à mains nues, vous récupérez 1 point de ki et gagnez votre niveau de "
            "moine en points de vie temporaires. Une fois par tour, et un nombre de fois égal à votre bonus de "
            "maîtrise ; vous récupérez toutes les utilisations à la fin d'un repos long."
        ),
        "Ébullition de sang": (
            "Par une action, vous dépensez 5 points de ki : chaque créature de votre choix dans un rayon de 6 m "
            "autour de vous fait un jet de sauvegarde de Constitution (DD " + KI_DD + "). En cas d'échec, elle "
            "subit 6d10 dégâts nécrotiques et sa vitesse tombe à 0 jusqu'à la fin de votre prochain tour ; en cas "
            "de réussite, elle subit la moitié des dégâts sans autre effet. Créatures artificielles et "
            "morts-vivants sont immunisés."
        ),
    },
    "Voie de la Tempête": {
        "Pas fulgurant & Poings d'orage": (
            "Poings d'orage : vos frappes à mains nues peuvent infliger des dégâts de foudre ou de tonnerre au lieu "
            "de contondants, et vous pouvez dépenser 2 points de ki pour lancer Vague tonnante par une action "
            "(DD " + KI_DD + "), +1 ki par niveau de sort au-delà du 1er (même plafond que les disciplines "
            "élémentaires). Pas fulgurant : lorsque vous dépensez au moins 1 point de ki pendant votre tour, votre "
            "vitesse augmente de 3 m jusqu'à la fin de ce tour."
        ),
        "Décharge conductrice": (
            "Une fois par tour, lorsque vous touchez une créature avec une frappe à mains nues, vous pouvez dépenser "
            "1 point de ki : jusqu'à deux autres créatures de votre choix à 3 m ou moins de la cible font un jet de "
            "sauvegarde de Dextérité (DD " + KI_DD + ") ou subissent deux dés d'arts martiaux de dégâts de foudre "
            "(aucun dégât en cas de réussite)."
        ),
        "Forme d'éclair": (
            "Par une action bonus, vous dépensez 2 points de ki : jusqu'à la fin du tour, votre vitesse augmente "
            "de 6 m, vous pouvez traverser l'espace des créatures hostiles et vos déplacements ne provoquent pas "
            "d'attaque d'opportunité. Chaque créature dont vous traversez l'espace pour la première fois ce tour "
            "fait un jet de sauvegarde de Dextérité (DD " + KI_DD + ") ou subit 3d8 dégâts de foudre (moitié en "
            "cas de réussite). Vous pouvez aussi dépenser 4 points de ki pour lancer Appel de la foudre."
        ),
        "Avatar de la tempête": (
            "Par une action bonus, vous dépensez 5 points de ki pour devenir un avatar de la tempête pendant "
            "1 minute (concentration, comme pour un sort). Vous gagnez une vitesse de vol égale à votre vitesse "
            "de marche, l'immunité aux dégâts de foudre et la résistance aux dégâts de tonnerre. Au début de chacun "
            "de vos tours, chaque créature de votre choix à 3 m ou moins fait un jet de sauvegarde de Constitution "
            "(DD " + KI_DD + ") ou subit 2d10 dégâts de tonnerre et est repoussée de 3 m (moitié des dégâts, sans "
            "poussée, en cas de réussite)."
        ),
    },
}

AUDIT = [
    ("info", "Voie de la Paume", "Nom non officiel : sous-classe non renommée pour ne pas casser les fiches existantes",
     "Voie de la Main ouverte (PHB)"),
]

CORRIGE = [
    ("majeur", "Capacités de classe optionnelles (Tasha)",
     "Arme dédiée absente des données",
     "TCE, niveau 2 : après un repos court ou long, une arme maîtrisée (ni lourde ni spéciale) devient une arme de moine"),
    ("majeur", "Capacités de classe optionnelles (Tasha)",
     "Attaque alimentée par le ki (« Ki dédié ») absente",
     "TCE, niveau 3 : après avoir dépensé du ki par une action, une attaque d'arme ou à mains nues par une action bonus"),
    ("majeur", "Capacités de classe optionnelles (Tasha)",
     "Guérison accélérée (« Récupération adaptée ») absente",
     "TCE, niveau 4 : action, 2 ki, récupérer un dé d'arts martiaux + bonus de maîtrise PV"),
    ("majeur", "Capacités de classe optionnelles (Tasha)",
     "Visée concentrée (« Frappe concentrée ») absente",
     "TCE, niveau 5 : après un jet d'attaque raté, 1 à 3 ki pour +2 par point dépensé"),
    ("mineur", "Arts martiaux", "Progression du dé non précisée",
     "d4 (1), d6 (5), d8 (11), d10 (17) ; armes de moine = épée courte + armes courantes de CàC non lourdes/à deux mains"),
    ("mineur", "Ki / Énergie spirituelle", "Nom double ; DD du ki et récupération (repos court) absents",
     "Ki : DD = 8 + bonus de maîtrise + modificateur de Sagesse ; récupéré par repos court ou long"),
    ("mineur", "Déplacement sans armure", "Valeurs non chiffrées et course verticale/sur liquides (niv. 9) omise",
     "+3 m (2), +4,50 m (6), +6 m (10), +7,50 m (14), +9 m (18)"),
    ("mineur", "Parade de projectiles", "Formule de réduction et coût du renvoi absents",
     "Réduction 1d10 + modificateur de Dextérité + niveau de moine ; renvoi pour 1 ki"),
    ("mineur", "Chute lente", "Nom non officiel",
     "Chute ralentie (PHB) : réaction, réduit les dégâts de 5 × niveau de moine"),
    ("mineur", "Évasion", "Nom différent de la VF officielle", "Dérobade (PHB VF)"),
    ("mineur", "Pureté du corps", "Immunité aux dégâts de poison non précisée",
     "Immunité aux maladies, aux dégâts de poison et à l'état empoisonné"),
    ("mineur", "Défense sans armure", "Abréviations « mod. » dans le texte",
     "CA = 10 + modificateur de Dextérité + modificateur de Sagesse"),
    ("info", "Voie de la Paume / sorts_domaine", "Liste « Sanctuaire » alors que la voie n'a pas de liste de sorts",
     "Sanctuaire n'est obtenu que via Ataraxie (niveau 11)"),
    ("mineur", "Voie de la Paume / Technique de la paume", "Données : coût de 1 ki",
     "Aucun ki supplémentaire : l'effet s'applique à chaque frappe du Déluge de coups qui touche"),
    ("mineur", "Voie de la Paume / Plénitude physique", "Action non précisée", "Action ; 3 × niveau de moine PV, 1/repos long"),
    ("mineur", "Voie de la Paume / Ataraxie", "« Entre deux combats » imprécis",
     "Sanctuaire à la fin d'un repos long, jusqu'au prochain repos long ; DD = DD du ki"),
    ("majeur", "Voie de la Paume / Paume vibratoire", "Durée fixe de 20 jours",
     "Durée = niveau de moine en jours ; déclenchement par une action"),
    ("mineur", "Voie des Quatre Éléments / Incantation élémentaire renforcée",
     "Aptitude de niveau 5 inventée (règle incluse dans Disciple des éléments)",
     "Plafond de ki par sort : 2/3/4/5/6 aux niveaux 3/5/9/13/17"),
    ("mineur", "Voie des Quatre Éléments / Discipline élémentaire avancée",
     "Décrite comme « sorts de zone majeurs »", "Niveau 11 : simple discipline supplémentaire (Flammes du phénix, Posture de brume, Chevaucher le vent)"),
    ("majeur", "Voie des Quatre Éléments / sorts_domaine", "« Fléau d'éléments » ne fait pas partie des disciplines",
     "Sorts des disciplines : Mains brûlantes, Vague tonnante, Immobilisation de personne, Bourrasque, Fracassement, Boule de feu, Forme gazeuse, Vol, Cône de froid, Peau de pierre, Mur de feu, Mur de pierre"),
    ("mineur", "Voie de l'Âme solaire / Rayon de soleil radiant", "Dégâts et remplacement des attaques non précisés",
     "Dé d'arts martiaux + Dextérité radiants, 9 m ; 1 ki pour deux rayons en action bonus"),
    ("mineur", "Voie de l'Âme solaire / Vague brûlante", "Action bonus et plafond de ki absents",
     "Action bonus, 2 ki, +1 ki par niveau, max moitié du niveau de moine"),
    ("mineur", "Voie de l'Âme solaire / Éruption solaire ardente", "« 2d6+ » ambigu ; coût en ki non précisé",
     "2d6 radiants sans ki, +2d6 par ki (max 3 ki), aucun dégât si réussite"),
    ("majeur", "Voie de l'Âme solaire / Bouclier solaire", "Dégâts « automatiques » non chiffrés",
     "Réaction : 5 + modificateur de Sagesse dégâts radiants à l'attaquant au CàC"),
    ("mineur", "Voie du Kensei / Armes du kensei, Parade agile & Tir du kensei",
     "Bonus de Tir du kensei non chiffré", "Action bonus : +1d4 dégâts aux attaques à distance d'arme de kensei"),
    ("mineur", "Voie du Kensei / Lame affûtée", "Action bonus non mentionnée", "Action bonus, 1 à 3 ki, 1 minute"),
    ("mineur", "Voie du Kensei / Précision infaillible", "« Relance automatiquement » imprécis",
     "Une fois par tour, relance possible d'une attaque ratée avec une arme de moine"),
    ("majeur", "Voie du Maître ivre / Chance de l'ivrogne", "Coût de 1 ki",
     "2 points de ki pour annuler le désavantage"),
    ("mineur", "Voie du Maître ivre / Chancellements éméchés", "Réaction non mentionnée pour Réorientation",
     "1 ki + réaction"),
    ("majeur", "Voie de l'Astre intérieur / Bras astraux", "Coût (1 ki, action bonus, 10 min) et dégâts d'invocation absents",
     "Action bonus, 1 ki, 10 minutes ; JS Dex ou 2 dés d'arts martiaux de force à 3 m"),
    ("majeur", "Voie de l'Astre intérieur / Visage astral", "Avantage en Intimidation/Persuasion",
     "Avantage en Intuition et Intimidation ; vision astrale 36 m ; durée 10 minutes"),
    ("majeur", "Voie de l'Astre intérieur / Corps de l'astre intérieur", "« Résistances élémentaires » inventées",
     "Détournement d'énergie (réaction, 1d10 + Sagesse + niveau de moine) et Bras renforcés (+1 dé d'arts martiaux)"),
    ("majeur", "Voie de l'Astre intérieur / Astre intérieur accompli", "Effet non décrit",
     "Action bonus, 5 ki, 10 min : +2 CA et trois attaques avec les bras lors de l'action Attaquer"),
    ("mineur", "Voie de la Miséricorde / Instrument de charité, Main guérisseuse & Main meurtrissante",
     "Dégâts de Main meurtrissante non chiffrés ; masque omis",
     "Dé d'arts martiaux + Sagesse nécrotiques, 1 ki, une fois par tour"),
    ("mineur", "Voie de la Miséricorde / Caresse médicale", "Maladie omise ; durée de l'empoisonnement absente",
     "Met fin à une maladie ou un état ; empoisonné jusqu'à la fin de votre prochain tour"),
    ("mineur", "Voie de la Miséricorde / Main de l'ultime miséricorde", "PV de retour non précisés",
     "Revient avec 4d10 + modificateur de Sagesse PV"),
    ("mineur", "Voie du Sang / sorts_domaine", "« Rayon d'affaiblissement » n'est pas le nom VF officiel",
     "Rayon affaiblissant"),
    ("mineur", "Voie du Sang / sorts_domaine", "« Vampirisme » n'est pas un sort existant (remplacé par Toucher du vampire, nom de la base de sorts)", "Caresse du vampire"),
]
