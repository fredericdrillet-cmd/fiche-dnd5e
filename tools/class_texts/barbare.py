"""Descriptions enrichies — Barbare (PHB, Xanathar, Tasha ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Barbare"

BASE = {
    "Rage": (
        "Au prix d'une action bonus, vous entrez en rage pour 1 minute, à condition de ne pas porter d'armure lourde. "
        "Tant qu'elle dure : avantage aux tests et jets de sauvegarde de Force ; bonus aux dégâts des attaques au corps à "
        "corps utilisant la Force (+2, +3 au niveau 9, +4 au niveau 16) ; résistance aux dégâts contondants, perforants "
        "et tranchants. Vous ne pouvez ni lancer de sorts ni vous concentrer sur un sort. La rage s'arrête plus tôt si "
        "vous tombez inconscient, si vous n'avez ni attaqué une créature hostile ni subi de dégâts depuis votre dernier "
        "tour, ou si vous y mettez fin (action bonus). Utilisations : 2 (3 au niveau 3, 4 au niveau 6, 5 au niveau 12, "
        "6 au niveau 17, illimitées au niveau 20), récupérées après un repos long."
    ),
    "Défense sans armure": (
        "Lorsque vous ne portez aucune armure, votre classe d'armure est égale à 10 + votre modificateur de Dextérité + "
        "votre modificateur de Constitution. Vous pouvez porter un bouclier et conserver ce calcul, le bonus du bouclier "
        "s'ajoutant normalement. Cette aptitude ne se cumule pas avec une autre méthode de calcul de la CA (Défense sans "
        "armure du moine, Armure du mage…) : vous choisissez celle qui vous avantage."
    ),
    "Attaque téméraire": (
        "Au moment de porter la première attaque de votre tour, vous pouvez décider de vous battre sans retenue. Vous "
        "obtenez alors l'avantage à tous vos jets d'attaque au corps à corps utilisant la Force pendant ce tour, mais en "
        "contrepartie les jets d'attaque effectués contre vous ont l'avantage jusqu'au début de votre prochain tour. "
        "Aucune limite d'utilisation."
    ),
    "Sens du danger": (
        "Vous percevez instinctivement ce qui cloche autour de vous. Vous avez l'avantage aux jets de sauvegarde de "
        "Dextérité contre les effets que vous pouvez voir, comme les pièges et les sorts. Ce bénéfice ne s'applique pas "
        "si vous êtes aveuglé, assourdi ou neutralisé."
    ),
    "Voie primitive": (
        "Au niveau 3, vous choisissez la voie qui façonne votre rage : Berserker, Guerrier totémique, Gardien ancestral, "
        "Héraut des tempêtes, Zélote, Bête, Magie sauvage, etc. Elle vous octroie des aptitudes au niveau 3, puis aux "
        "niveaux 6, 10 et 14."
    ),
    "Connaissance primitive (option Tasha)": (
        "Option de classe du Chaudron des merveilles de Tasha. Au niveau 3, vous gagnez la maîtrise d'une compétence "
        "choisie dans la liste du barbare : Athlétisme, Dressage, Intimidation, Nature, Perception ou Survie. Au niveau "
        "10, vous gagnez la maîtrise d'une seconde compétence de cette même liste."
    ),
    "Attaque supplémentaire": (
        "Lorsque vous effectuez l'action Attaquer pendant votre tour, vous pouvez porter deux attaques au lieu d'une. "
        "Combinée à la rage et à l'Attaque téméraire, cette aptitude fait du barbare l'un des combattants au corps à "
        "corps les plus redoutables à partir du niveau 5."
    ),
    "Déplacement rapide": (
        "Votre vitesse au sol augmente de 3 mètres tant que vous ne portez pas d'armure lourde. Ce bonus est permanent "
        "et ne dépend pas de la rage."
    ),
    "Instinct sauvage": (
        "Vos réflexes animaux vous donnent l'avantage aux jets d'initiative. De plus, si vous êtes surpris au début d'un "
        "combat et que vous n'êtes pas neutralisé, vous pouvez agir normalement lors de votre premier tour, mais "
        "seulement si vous entrez en rage avant toute autre action pendant ce tour."
    ),
    "Bond instinctif (option Tasha)": (
        "Option de classe du Chaudron des merveilles de Tasha. Lorsque vous utilisez votre action bonus pour entrer en "
        "rage, cette même action bonus vous permet aussi de vous déplacer d'une distance allant jusqu'à la moitié de "
        "votre vitesse."
    ),
    "Critique brutal": (
        "Lorsque vous réussissez un coup critique avec une attaque au corps à corps, vous lancez un dé de dégâts "
        "d'arme supplémentaire et l'ajoutez aux dégâts du critique. Ce nombre de dés supplémentaires passe à 2 au "
        "niveau 13 et à 3 au niveau 17."
    ),
    "Rage implacable": (
        "Si vous tombez à 0 point de vie alors que vous êtes en rage, sans être tué sur le coup, vous pouvez faire un jet "
        "de sauvegarde de Constitution DD 10. En cas de réussite, vous restez à 1 point de vie. Chaque utilisation "
        "ultérieure augmente le DD de 5 ; il revient à 10 après un repos court ou long."
    ),
    "Rage persistante": (
        "Votre rage est si intense qu'elle ne s'interrompt plus faute d'avoir attaqué ou subi des dégâts. Elle ne prend "
        "fin avant sa durée normale que si vous tombez inconscient ou si vous décidez d'y mettre fin."
    ),
    "Puissance indomptable": (
        "Lorsque le total d'un de vos tests de Force est inférieur à votre valeur de Force, vous pouvez utiliser cette "
        "valeur à la place du résultat. Cela garantit un minimum élevé pour les tests d'Athlétisme, d'enfoncement de "
        "porte ou de lutte."
    ),
    "Champion primitif": (
        "Vous incarnez la puissance de la nature sauvage. Vos valeurs de Force et de Constitution augmentent chacune de "
        "4, et leur maximum passe à 24 au lieu de 20. Combiné aux rages illimitées du niveau 20, cela fait de vous une "
        "force quasi inarrêtable."
    ),
}

_MARCHEUR = (
    "Vous pouvez lancer le sort Communion avec la nature, uniquement sous forme de rituel. Un esprit animal "
    "correspondant à l'un de vos totems vous apparaît alors pour vous transmettre les informations recherchées sur la "
    "région (environ 4,5 km autour de vous en extérieur)."
)
_CHERCHEUR = (
    "Votre lien avec les esprits animaux vous permet de lancer les sorts Sens animal et Communication avec les "
    "animaux, mais uniquement sous forme de rituels (10 minutes de plus, sans emplacement de sort)."
)
_TEMPETE_PROTECTRICE = (
    "Vous partagez votre résistance élémentaire avec vos compagnons. Chaque créature de votre choix bénéficie de la "
    "résistance au type de dégâts accordé par votre Âme des tempêtes tant qu'elle se trouve dans votre Aura des "
    "tempêtes (rayon de 3 mètres autour de vous, active pendant votre rage)."
)
_AURA_REGLE = (
    " L'aura (rayon de 3 mètres centré sur vous, qui traverse les obstacles) s'active quand vous entrez en rage, puis "
    "par une action bonus lors de vos tours suivants tant que la rage dure."
)

SUB = {
    "Voie du Berserker": {
        "Frénésie": (
            "Lorsque vous entrez en rage, vous pouvez choisir de devenir frénétique. Pendant toute la durée de cette "
            "rage, vous pouvez effectuer une attaque d'arme au corps à corps par une action bonus à chacun de vos tours "
            "après celui où vous êtes entré en rage. Quand la rage prend fin, vous subissez un niveau d'épuisement."
        ),
        "Rage aveugle": (
            "Tant que vous êtes en rage, vous ne pouvez être ni charmé ni effrayé. Si vous êtes déjà sous l'effet d'un "
            "charme ou de la terreur au moment où vous entrez en rage, cet effet est suspendu pendant toute la durée de "
            "la rage."
        ),
        "Présence intimidante": (
            "Par une action, vous terrorisez une créature située à 9 mètres ou moins que vous pouvez voir et qui peut "
            "vous voir ou vous entendre. Elle fait un jet de sauvegarde de Sagesse DD 8 + votre bonus de maîtrise + "
            "votre modificateur de Charisme ; en cas d'échec, elle est effrayée jusqu'à la fin de votre prochain tour. "
            "Vous pouvez prolonger l'effet d'un tour avec une nouvelle action ; il cesse si la cible finit son tour hors "
            "de vue ou à plus de 18 m. Une créature qui réussit est immunisée pendant 24 heures."
        ),
        "Représailles": (
            "Lorsqu'une créature située à 1,50 mètre ou moins de vous vous inflige des dégâts, vous pouvez utiliser "
            "votre réaction pour effectuer une attaque d'arme au corps à corps contre elle."
        ),
    },
    "Voie totémique - Ours": {
        "Chercheur spirituel": _CHERCHEUR,
        "Totem spirituel (Ours)": (
            "Totem de l'ours : tant que vous êtes en rage, vous avez la résistance à "
            "tous les types de dégâts, à l'exception des dégâts psychiques."
        ),
        "Aspect de la bête (Ours)": (
            "Vous acquérez la robustesse de l'ours. Votre capacité de charge (y compris la charge maximale que vous "
            "pouvez pousser, tirer ou soulever) est doublée, et vous avez l'avantage aux tests de Force effectués pour "
            "pousser, tirer, soulever ou briser des objets."
        ),
        "Marcheur spirituel": _MARCHEUR,
        "Harmonisation totémique (Ours)": (
            "Tant que vous êtes en rage, toute créature hostile située à 1,50 mètre ou moins de vous a un désavantage "
            "aux jets d'attaque contre les cibles autres que vous ou qu'un autre personnage possédant cette aptitude. "
            "Un ennemi est immunisé s'il ne peut ni vous voir ni vous entendre, ou s'il ne peut pas être effrayé."
        ),
    },
    "Voie totémique - Aigle": {
        "Chercheur spirituel": _CHERCHEUR,
        "Totem spirituel (Aigle)": (
            "Totem de l'aigle : tant que vous êtes en rage sans porter d'armure "
            "lourde, les autres créatures ont un désavantage aux attaques d'opportunité contre vous, et vous pouvez "
            "effectuer l'action Foncer par une action bonus."
        ),
        "Aspect de la bête (Aigle)": (
            "Vous obtenez la vue perçante de l'aigle. Vous distinguez les détails jusqu'à 1,5 kilomètre comme s'ils "
            "n'étaient qu'à 30 mètres, et une lumière faible ne vous impose pas de désavantage aux tests de Sagesse "
            "(Perception)."
        ),
        "Marcheur spirituel": _MARCHEUR,
        "Harmonisation totémique (Aigle)": (
            "Tant que vous êtes en rage, vous gagnez une vitesse de vol égale à votre vitesse au sol. Ce vol ne "
            "fonctionne que pendant votre tour : si vous êtes encore en l'air à la fin de votre tour et que rien ne vous "
            "y maintient, vous tombez."
        ),
    },
    "Voie totémique - Loup": {
        "Chercheur spirituel": _CHERCHEUR,
        "Totem spirituel (Loup)": (
            "Totem du loup : tant que vous êtes en rage, vos amis ont l'avantage aux "
            "jets d'attaque au corps à corps contre toute créature hostile située à 1,50 mètre ou moins de vous."
        ),
        "Aspect de la bête (Loup)": (
            "Vous acquérez l'instinct de chasse du loup. Vous pouvez pister d'autres créatures en voyageant à allure "
            "rapide, et vous déplacer discrètement en voyageant à allure normale (au lieu de l'allure lente)."
        ),
        "Marcheur spirituel": _MARCHEUR,
        "Harmonisation totémique (Loup)": (
            "Tant que vous êtes en rage, lorsque vous touchez une créature de taille G ou inférieure avec une attaque au "
            "corps à corps, vous pouvez utiliser une action bonus pour la jeter à terre."
        ),
    },
    "Voie du Gardien ancestral": {
        "Protecteurs ancestraux": (
            "Des guerriers spectraux surgissent quand vous entrez en rage. La première créature que vous touchez par "
            "une attaque pendant chacun de vos tours de rage est harcelée par eux : jusqu'au début de votre prochain "
            "tour, elle a un désavantage à ses jets d'attaque contre toute cible autre que vous, et lorsqu'elle touche "
            "une autre créature avec une attaque, celle-ci a la résistance aux dégâts de cette attaque. L'effet prend "
            "fin si votre rage s'arrête."
        ),
        "Bouclier spirituel": (
            "Tant que vous êtes en rage, lorsqu'une créature que vous pouvez voir, située à 9 mètres ou moins de vous, "
            "subit des dégâts, vous pouvez utiliser votre réaction pour réduire ces dégâts de 2d6. La réduction passe à "
            "3d6 au niveau 10 et à 4d6 au niveau 14."
        ),
        "Consulter les esprits": (
            "Vous pouvez lancer Augure ou Clairvoyance sans dépenser d'emplacement de sort ni fournir de composantes "
            "matérielles, en utilisant la Sagesse comme caractéristique d'incantation. Pour Clairvoyance, un de vos "
            "esprits ancestraux devient le capteur invisible. Une fois utilisée, cette aptitude se recharge après un "
            "repos court ou long."
        ),
        "Ancêtres vengeurs": (
            "Vos esprits ancestraux contre-attaquent. Lorsque vous utilisez Bouclier spirituel pour réduire les dégâts "
            "d'une attaque, l'attaquant subit des dégâts de force égaux à la quantité de dégâts que votre bouclier a "
            "empêchés."
        ),
    },
    "Voie des tempêtes - Désert": {
        "Aura des tempêtes (Désert)": (
            "Désert : lorsque l'aura est activée, chaque autre créature de votre choix dans l'aura subit 2 dégâts de "
            "feu (aucun jet de sauvegarde). Les dégâts passent à 3 au niveau 5, 4 au niveau 10, 5 au niveau 15 et 6 au "
            "niveau 20." + _AURA_REGLE
        ),
        "Âme des tempêtes (Désert)": (
            "Vous avez la résistance aux dégâts de feu et ne souffrez pas des effets de la chaleur extrême. De plus, par "
            "une action, vous pouvez toucher un objet inflammable que personne ne porte ni ne tient pour l'enflammer."
        ),
        "Tempête protectrice": _TEMPETE_PROTECTRICE,
        "Tempête déchaînée (Désert)": (
            "Lorsqu'une créature située dans votre aura vous touche avec une attaque, vous pouvez utiliser votre "
            "réaction pour la forcer à faire un jet de sauvegarde de Dextérité DD 8 + votre bonus de maîtrise + votre "
            "modificateur de Constitution. En cas d'échec, elle subit des dégâts de feu égaux à la moitié de votre "
            "niveau de barbare."
        ),
    },
    "Voie des tempêtes - Mer": {
        "Aura des tempêtes (Mer)": (
            "Mer : lorsque l'aura est activée, vous choisissez une autre créature dans l'aura, qui fait un jet de "
            "sauvegarde de Dextérité DD 8 + votre bonus de maîtrise + votre modificateur de Constitution. Elle subit "
            "1d6 dégâts de foudre en cas d'échec, la moitié en cas de réussite. Les dégâts passent à 2d6 au niveau 10, "
            "3d6 au niveau 15 et 4d6 au niveau 20." + _AURA_REGLE
        ),
        "Âme des tempêtes (Mer)": (
            "Vous avez la résistance aux dégâts de foudre, vous pouvez respirer sous l'eau et vous gagnez une vitesse de "
            "nage de 9 mètres."
        ),
        "Tempête protectrice": _TEMPETE_PROTECTRICE,
        "Tempête déchaînée (Mer)": (
            "Lorsque vous touchez une créature située dans votre aura avec une attaque, vous pouvez utiliser votre "
            "réaction pour la forcer à faire un jet de sauvegarde de Force DD 8 + votre bonus de maîtrise + votre "
            "modificateur de Constitution. En cas d'échec, elle tombe à terre, comme renversée par une vague."
        ),
    },
    "Voie des tempêtes - Toundra": {
        "Aura des tempêtes (Toundra)": (
            "Toundra : lorsque l'aura est activée, chaque créature de votre choix dans l'aura (vous compris) gagne 2 "
            "points de vie temporaires. Ce nombre passe à 3 au niveau 5, 4 au niveau 10, 5 au niveau 15 et 6 au niveau "
            "20." + _AURA_REGLE
        ),
        "Âme des tempêtes (Toundra)": (
            "Vous avez la résistance aux dégâts de froid et ne souffrez pas des effets du froid extrême. De plus, par une "
            "action, vous pouvez toucher de l'eau pour en geler un cube de 1,50 mètre d'arête ; la glace fond après 1 "
            "minute. Cette action échoue si une créature se trouve dans ce cube."
        ),
        "Tempête protectrice": _TEMPETE_PROTECTRICE,
        "Tempête déchaînée (Toundra)": (
            "Chaque fois que l'effet de votre aura est activé, vous pouvez choisir une créature que vous voyez dans "
            "l'aura. Elle doit réussir un jet de sauvegarde de Force DD 8 + votre bonus de maîtrise + votre "
            "modificateur de Constitution, sans quoi sa vitesse tombe à 0 jusqu'au début de votre prochain tour, prise "
            "par le givre."
        ),
    },
    "Voie du Zélote": {
        "Guerrier des dieux": (
            "Votre âme est réclamée par les dieux. Tout sort dont le seul effet est de vous ramener à la vie (Revigorer, "
            "Rappel à la vie, Résurrection, Réincarnation…) ne requiert aucune composante matérielle lorsqu'il est lancé "
            "sur vous."
        ),
        "Fureur divine": (
            "Tant que vous "
            "êtes en rage, la première créature que vous touchez avec une attaque d'arme à chacun de vos tours subit "
            "1d6 + la moitié de votre niveau de barbare dégâts supplémentaires, nécrotiques ou radiants (choix fait en "
            "obtenant l'aptitude)."
        ),
        "Obstination fanatique": (
            "Si vous ratez un jet de sauvegarde alors que vous êtes en rage, vous pouvez le relancer et devez utiliser "
            "le nouveau résultat. Cette aptitude ne peut servir qu'une fois par rage."
        ),
        "Présence zélatrice": (
            "Par une action bonus, vous poussez un cri de guerre empreint de puissance divine. Jusqu'à 10 autres "
            "créatures de votre choix situées à 18 mètres ou moins et qui vous entendent ont l'avantage aux jets "
            "d'attaque et aux jets de sauvegarde jusqu'au début de votre prochain tour. Utilisable une fois, récupérée "
            "après un repos long."
        ),
        "Enragé par-delà la mort": (
            "Tant que vous êtes en rage, tomber à 0 point de vie ne vous rend pas inconscient. Vous faites toujours des "
            "jets de sauvegarde contre la mort et subissez les effets normaux des dégâts à 0 PV, mais si vous deviez "
            "mourir à cause des échecs, vous ne mourez qu'à la fin de votre rage, et seulement si vous êtes encore à 0 "
            "point de vie à ce moment-là."
        ),
    },
    "Voie de la Bête": {
        "Forme de la bête": (
            "Quand vous entrez en rage, vous choisissez une arme naturelle (maniée avec la Force, maîtrisée) qui dure "
            "jusqu'à la fin de la rage. Morsure : 1d8 perforants ; une fois par tour, si vous avez moins de la moitié "
            "de vos PV en touchant, vous regagnez un nombre de PV égal à votre bonus de maîtrise. Griffes : 1d6 "
            "tranchants par griffe ; une fois par tour, quand vous attaquez avec une griffe via l'action Attaquer, vous "
            "pouvez porter une attaque de griffe supplémentaire. Queue : 1d8 perforants, allonge de 3 m ; quand une "
            "créature à 3 m vous touche, vous pouvez par une réaction ajouter 1d8 à votre CA contre cette attaque."
        ),
        "Âme bestiale": (
            "Vos armes naturelles comptent comme magiques pour surmonter les résistances. Après chaque repos court ou "
            "long, choisissez un bienfait : vitesse de nage égale à votre vitesse et respiration aquatique ; vitesse "
            "d'escalade égale à votre vitesse, même au plafond sans test ; ou, quand vous sautez, un test de Force "
            "(Athlétisme) dont le total s'ajoute en pieds à la distance (une fois par tour)."
        ),
        "Fureur contagieuse": (
            "Tant que vous êtes en rage, lorsque vous touchez une créature avec vos armes naturelles, vous pouvez la "
            "forcer à faire un jet de sauvegarde de Sagesse DD 8 + votre bonus de maîtrise + votre modificateur de "
            "Constitution. En cas d'échec, vous choisissez : elle utilise sa réaction pour attaquer au corps à corps une "
            "autre créature de votre choix qu'elle voit, ou elle subit 2d12 dégâts psychiques. Utilisable un nombre de "
            "fois égal à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Hallali": (
            "Quand vous entrez en rage, vous pouvez choisir un nombre de créatures consentantes égal à votre "
            "modificateur de Constitution (minimum 1), situées à 9 mètres ou moins. Vous gagnez 5 PV temporaires par "
            "créature qui accepte. Pendant la rage, chacune peut, une fois à chacun de ses tours, infliger 1d6 dégâts "
            "supplémentaires du même type quand elle touche une cible. Utilisable un nombre de fois égal à votre bonus "
            "de maîtrise, récupérées après un repos long."
        ),
    },
    "Voie de la Magie sauvage": {
        "Conscience magique": (
            "Par une action, vous ouvrez vos sens à la magie : jusqu'à la fin de votre prochain tour, vous connaissez "
            "l'emplacement de tout sort ou objet magique situé à 18 mètres ou moins et non dissimulé derrière un abri "
            "total, ainsi que l'école de magie de chaque sort perçu. Utilisable un nombre de fois égal à votre bonus de "
            "maîtrise, récupérées après un repos long."
        ),
        "Accès sauvage": (
            "Chaque fois que vous entrez en rage, lancez un d8 sur la table de magie sauvage du barbare pour déterminer "
            "l'effet produit (explosion d'ombre, téléportation, esprit lumineux, arme imprégnée, lumière protectrice…). "
            "Si l'effet impose un jet de sauvegarde, le DD est égal à 8 + votre bonus de maîtrise + votre modificateur "
            "de Constitution. L'effet dure jusqu'à la fin de la rage."
        ),
        "Magie galvanisante": (
            "Par une action, vous touchez une créature (vous compris) et choisissez : pendant 10 minutes, elle peut "
            "lancer 1d3 et l'ajouter à un jet d'attaque ou à un test de caractéristique ; ou bien vous lancez 1d3 et "
            "elle récupère un emplacement de sort dépensé de niveau inférieur ou égal au résultat. Utilisable un nombre "
            "de fois égal à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Riposte capricieuse": (
            "Tant que vous êtes en rage, lorsque vous subissez des dégâts ou ratez un jet de sauvegarde, vous pouvez "
            "utiliser votre réaction pour lancer un nouveau d8 sur la table de magie sauvage. Le nouvel effet remplace "
            "immédiatement celui de votre Accès sauvage en cours."
        ),
        "Sauvagerie contrôlée": (
            "Chaque fois que vous lancez le dé sur la table de magie sauvage, vous pouvez le lancer deux fois et choisir "
            "l'effet que vous préférez parmi les deux. Si les deux dés donnent le même nombre, vous ignorez le résultat "
            "et choisissez librement n'importe quel effet de la table."
        ),
    },
    "Voie du Météore": {
        "Onde de choc & Impact gravitationnel": (
            "Tant que vous êtes en rage, lorsque vous atterrissez après un saut ou une chute d'au moins 3 mètres, vous "
            "pouvez déclencher une onde de choc (une fois par tour). Chaque créature de votre choix à 1,50 mètre ou "
            "moins fait un jet de sauvegarde de Force DD 8 + votre bonus de maîtrise + votre modificateur de "
            "Constitution : en cas d'échec, elle subit 1d6 + votre modificateur de Force dégâts de force et tombe à "
            "terre ; en cas de réussite, la moitié des dégâts seulement. Vous ne subissez aucun dégât de chute si la "
            "chute fait 6 mètres ou moins."
        ),
        "Projection météoritique": (
            "Tant que vous êtes en rage, par une action bonus, vous pouvez projeter une créature que vous agrippez (de "
            "taille M ou inférieure) ou un objet lourd jusqu'à 9 mètres. Chaque créature dans un rayon de 1,50 mètre "
            "autour du point d'impact fait un jet de sauvegarde de Dextérité DD 8 + votre bonus de maîtrise + votre "
            "modificateur de Constitution, subissant 2d6 dégâts contondants en cas d'échec (moitié en cas de "
            "réussite) ; la créature projetée subit les mêmes dégâts et tombe à terre. Utilisable un nombre de fois "
            "égal à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Puits de gravité": (
            "Quand vous entrez en rage, puis par une action bonus, vous pouvez choisir une créature à 9 mètres ou "
            "moins. Elle fait un jet de sauvegarde de Force DD 8 + votre bonus de maîtrise + votre modificateur de "
            "Constitution ; en cas d'échec, elle est attirée de 4,50 mètres vers vous et, jusqu'au début de votre "
            "prochain tour, elle ne peut pas volontairement s'éloigner de vous de plus de 4,50 mètres. Utilisable un "
            "nombre de fois égal à votre bonus de maîtrise par repos long."
        ),
        "Cataclysme céleste": (
            "Par une action, pendant votre rage, vous bondissez jusqu'à 9 mètres de haut puis retombez sur un point "
            "situé à 9 mètres ou moins, sans provoquer d'attaques d'opportunité ni subir de dégâts de chute. Chaque "
            "créature dans un rayon de 3 mètres fait un jet de sauvegarde de Constitution DD 8 + votre bonus de maîtrise "
            "+ votre modificateur de Constitution : 4d8 dégâts de force et étourdie jusqu'à la fin de votre prochain "
            "tour en cas d'échec, moitié des dégâts et aucun étourdissement en cas de réussite. Le sol devient un "
            "terrain difficile. Une fois par repos long."
        ),
    },
    "Voie du Colosse des Glaces": {
        "Armure de givre éternel": (
            "Quand vous entrez en rage, une carapace de glace vous recouvre : vous gagnez un nombre de points de vie "
            "temporaires égal à votre niveau de barbare, qui disparaissent à la fin de la rage. Tant que vous avez ces "
            "PV temporaires, une créature qui vous touche avec une attaque au corps à corps alors qu'elle se trouve à "
            "1,50 mètre ou moins de vous subit 1d4 dégâts de froid (une fois par tour)."
        ),
        "Sourdine glaciale": (
            "Tant que vous êtes en rage, lorsqu'une créature située à 1,50 mètre ou moins de vous vous touche avec une "
            "attaque au corps à corps, sa vitesse est réduite de 3 mètres jusqu'à la fin de son prochain tour. Une "
            "créature ne peut pas subir cette réduction plusieurs fois à la fois. Vous gagnez en outre la résistance aux "
            "dégâts de froid."
        ),
        "Avalanche percutante": (
            "Lorsque vous utilisez Attaque téméraire, vous pouvez d'abord charger en ligne droite jusqu'à votre vitesse, "
            "sans provoquer d'attaques d'opportunité. Chaque créature de taille G ou inférieure sur votre trajectoire "
            "fait un jet de sauvegarde de Force DD 8 + votre bonus de maîtrise + votre modificateur de Force ; en cas "
            "d'échec, elle est repoussée de 1,50 mètre hors de votre ligne et jetée à terre. Utilisable un nombre de "
            "fois égal à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Jugement du blizzard": (
            "Quand vous entrez en rage, vous pouvez déclencher un blizzard dans un rayon de 3 mètres autour de vous, "
            "qui vous suit pendant 1 minute. La zone est légèrement obscurcie et constitue un terrain difficile pour vos "
            "ennemis, qui ont un désavantage aux jets d'attaque à distance. Toute créature de votre choix qui commence "
            "son tour dans la zone subit 2d6 dégâts de froid (jet de sauvegarde de Constitution DD 8 + votre bonus de "
            "maîtrise + votre modificateur de Constitution pour moitié). Une fois par repos long."
        ),
    },
}

AUDIT = [
    ("info", "Voie totémique (Ours/Aigle/Loup)",
     "Scindée en trois sous-classes distinctes : non fusionnée pour ne pas casser les fiches existantes",
     "Officiellement une seule sous-classe (Voie du guerrier totémique) avec choix d'animal indépendant aux niv. 3, 6 et 14"),
    ("info", "Voie totémique", "Totems Élan et Tigre (SCAG) absents : non ajoutés car il faudrait créer de nouvelles "
     "sous-classes scindées (structure actuelle conservée)",
     "Options supplémentaires du Sword Coast Adventurer's Guide"),
    ("info", "Voie des tempêtes (Désert/Mer/Toundra)",
     "Scindée en trois sous-classes ; nom officiel non utilisé : non fusionnée ni renommée pour ne pas casser les fiches "
     "existantes",
     "Une seule sous-classe « Voie du héraut des tempêtes » ; l'environnement peut changer à chaque niveau de barbare"),
    ("info", "Sous-classes", "Voie du géant (Bigby) et Battlerager (SCAG) absentes : hors périmètre PHB/XGE/TCE, non ajoutées",
     "Sous-classes officielles hors PHB/XGE/TCE non incluses"),
]

CORRIGE = [
    ("majeur", "Rage", "Aucun nombre d'utilisations indiqué",
     "2 rages, 3 au niv. 3, 4 au niv. 6, 5 au niv. 12, 6 au niv. 17, illimitées au niv. 20 ; récupération au repos long"),
    ("majeur", "Rage", "Bonus aux dégâts non chiffré",
     "+2 aux dégâts (Force, corps à corps), +3 au niv. 9, +4 au niv. 16"),
    ("mineur", "Rage", "Durée et conditions de fin absentes",
     "1 minute ; fin anticipée si inconscient, ou sans attaque ni dégâts subis depuis le dernier tour, ou au choix (action bonus)"),
    ("majeur", "Rage", "Restrictions absentes",
     "Pas d'armure lourde ; impossible de lancer des sorts ou de se concentrer pendant la rage"),
    ("mineur", "Rage", "Type de dégâts « impact »",
     "Terme officiel français : dégâts contondants"),
    ("mineur", "Sens du danger", "Conditions d'application absentes",
     "Ne fonctionne pas si le barbare est aveuglé, assourdi ou neutralisé"),
    ("mineur", "Instinct sauvage", "« Ne peut plus être surpris »",
     "Le barbare peut être surpris, mais agit normalement au 1er tour s'il entre en rage avant toute autre action"),
    ("mineur", "Rage implacable", "Réinitialisation du DD non précisée",
     "Le DD revient à 10 après un repos court ou long"),
    ("majeur", "Capacités de classe optionnelles", "Connaissance primitive (TCE) absente",
     "Niv. 3 et niv. 10 : maîtrise d'une compétence de la liste du barbare"),
    ("majeur", "Capacités de classe optionnelles", "Bond instinctif (TCE) absent",
     "Niv. 7 : en entrant en rage, déplacement de la moitié de la vitesse avec la même action bonus"),
    ("majeur", "Voie du Berserker / Présence intimidante", "DD fixe de 14 dans les données",
     "DD = 8 + bonus de maîtrise + modificateur de Charisme (PHB), portée 9 m, effrayé jusqu'à la fin du prochain tour"),
    ("mineur", "Voie du Berserker / Représailles", "Déclencheur « dégâts au corps à corps »",
     "Déclencheur : dégâts infligés par une créature située à 1,50 m ou moins (quelle que soit l'attaque)"),
    ("majeur", "Voie totémique / Chercheur spirituel", "Aptitude de niveau 3 manquante",
     "Niv. 3 : Sens animal et Communication avec les animaux en rituels"),
    ("mineur", "Voie totémique - Aigle / Harmonisation totémique (Aigle)", "« Voler pour 1 tour »",
     "Vitesse de vol égale à la vitesse au sol pendant la rage, uniquement durant votre tour"),
    ("mineur", "Voie totémique - Loup / Harmonisation totémique (Loup)", "Condition de toucher absente",
     "Action bonus pour jeter à terre une créature de taille G ou inférieure après l'avoir touchée au corps à corps"),
    ("majeur", "Voie du Gardien ancestral / Bouclier spirituel", "Réduction fixe de 3d6",
     "2d6 au niv. 6, 3d6 au niv. 10, 4d6 au niv. 14"),
    ("mineur", "Voie du Gardien ancestral / Consulter les esprits", "« 1 fois par repos » imprécis",
     "Une utilisation, récupérée après un repos court ou long ; sans emplacement ni composantes matérielles"),
    ("majeur", "Voie des tempêtes - Désert / Aura des tempêtes (Désert)", "6 dégâts de feu fixes",
     "2 dégâts de feu, 3 au niv. 5, 4 au niv. 10, 5 au niv. 15, 6 au niv. 20"),
    ("majeur", "Voie des tempêtes - Mer / Aura des tempêtes (Mer)", "4d6 dégâts de foudre dès le niv. 3",
     "1d6, 2d6 au niv. 10, 3d6 au niv. 15, 4d6 au niv. 20 ; DD 8 + maîtrise + Constitution"),
    ("majeur", "Voie des tempêtes - Toundra / Aura des tempêtes (Toundra)", "6 PV temporaires fixes",
     "2 PV temporaires, 3 au niv. 5, 4 au niv. 10, 5 au niv. 15, 6 au niv. 20"),
    ("majeur", "Voie des tempêtes - Désert / Tempête déchaînée (Désert)", "10 dégâts de feu fixes",
     "Dégâts de feu = moitié du niveau de barbare (réaction, JS Dex DD 8 + maîtrise + Con)"),
    ("mineur", "Voie des tempêtes - Mer / Tempête déchaînée (Mer)", "Déclencheur « une créature vous touche »",
     "Déclencheur : lorsque VOUS touchez une créature dans l'aura (réaction), JS Force ou à terre"),
    ("mineur", "Voie des tempêtes - Toundra / Tempête déchaînée (Toundra)", "Déclencheur « une créature vous touche »",
     "Déclencheur : à chaque activation de l'aura, une créature dans l'aura fait un JS Force ou vitesse 0"),
    ("majeur", "Voie du Zélote / Guerrier des dieux", "Aptitude de niveau 3 manquante",
     "Niv. 3 : les sorts de résurrection lancés sur vous ne requièrent aucune composante matérielle"),
    ("majeur", "Voie du Zélote / Présence zélatrice", "Portée de 6 cases (9 m)",
     "Portée de 18 m (60 ft)"),
    ("majeur", "Voie du Zélote / Enragé par-delà la mort", "Mort « si 3 échecs ou à la fin de la rage »",
     "Pas de mort par échecs pendant la rage ; mort à la fin de la rage seulement si toujours à 0 PV"),
    ("info", "Voie du Zélote / Fureur divine", "« moitié de votre niveau » sans préciser la classe",
     "1d6 + moitié du niveau de barbare"),
    ("majeur", "Voie de la Bête / Forme de la bête", "Morsure rend 6 PV fixes",
     "PV rendus = bonus de maîtrise, une fois par tour, si moins de la moitié des PV max"),
    ("mineur", "Voie de la Bête / Forme de la bête", "Griffes et queue infligent des « dégâts magiques »",
     "Griffes : tranchants ; queue : perforants (allonge 3 m) ; caractère magique acquis au niv. 6"),
    ("mineur", "Voie de la Bête / Âme bestiale", "Armes naturelles magiques non mentionnées",
     "Niv. 6 : les armes naturelles comptent comme magiques ; choix du bienfait après chaque repos court ou long"),
    ("majeur", "Voie de la Bête / Fureur contagieuse", "DD fixe de 14 ; utilisations absentes",
     "DD 8 + maîtrise + Constitution ; utilisations = bonus de maîtrise par repos long"),
    ("majeur", "Voie de la Bête / Hallali", "1 seule créature ; 6 utilisations fixes",
     "Créatures consentantes = modificateur de Constitution (min. 1) à 9 m ; utilisations = bonus de maîtrise par repos long"),
    ("majeur", "Voie de la Magie sauvage / Conscience magique", "6 utilisations fixes",
     "Utilisations = bonus de maîtrise par repos long"),
    ("majeur", "Voie de la Magie sauvage / Accès sauvage", "DD fixe de 14",
     "DD = 8 + bonus de maîtrise + modificateur de Constitution"),
    ("majeur", "Voie de la Magie sauvage / Magie galvanisante", "6 utilisations fixes",
     "Utilisations = bonus de maîtrise par repos long"),
    ("mineur", "Voie de la Magie sauvage / Riposte capricieuse", "Déclencheur « attaqué »",
     "Déclencheur : subir des dégâts ou rater un jet de sauvegarde pendant la rage"),
]
