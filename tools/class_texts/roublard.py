"""Descriptions enrichies — Roublard (PHB, Xanathar, Tasha ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Roublard"

BASE = {
    "Expertise": (
        "Choisissez deux compétences que vous maîtrisez, ou une compétence maîtrisée et les outils de voleur. "
        "Pour tout test de caractéristique utilisant l'une d'elles, vous doublez votre bonus de maîtrise au lieu de "
        "l'ajouter une seule fois. Vous choisissez deux maîtrises supplémentaires de la même façon au niveau 6 "
        "(aptitude Expertise supplémentaire)."
    ),
    "Attaque sournoise": (
        "Une fois par tour, vous infligez des dégâts supplémentaires à une créature que vous touchez avec une attaque "
        "effectuée avec une arme de finesse ou une arme à distance, à condition d'avoir l'avantage sur le jet "
        "d'attaque. L'avantage n'est pas nécessaire si un autre ennemi de la cible se trouve à 1,50 m d'elle, que cet "
        "ennemi n'est pas incapable d'agir et que vous n'avez pas le désavantage sur le jet. Les dés supplémentaires "
        "sont des d6, en nombre égal à la moitié (arrondie au supérieur) de votre niveau de roublard. Progression : 1d6 (niveaux 1-2), "
        "2d6 (niveaux 3-4), 3d6 (niveaux 5-6), 4d6 (niveaux 7-8), 5d6 (niveaux 9-10), 6d6 (niveaux 11-12), "
        "7d6 (niveaux 13-14), 8d6 (niveaux 15-16), 9d6 (niveaux 17-18) et 10d6 (niveaux 19-20). En cas de coup "
        "critique, ces dés sont doublés comme les dés de l'arme."
    ),
    "Jargon des voleurs": (
        "Vous connaissez le jargon des voleurs, un mélange d'argot, de termes codés et de tournures détournées qui "
        "permet de glisser un message caché dans une conversation anodine. Seule une créature qui connaît aussi ce "
        "jargon en comprend le sens, et transmettre une idée de cette façon prend quatre fois plus de temps que de la "
        "dire clairement. Vous comprenez également un ensemble de signes et symboles secrets (danger, territoire d'une "
        "guilde, cachette, cible facile, maison sûre…)."
    ),
    "Action rusée": (
        "Votre vivacité d'esprit et votre agilité vous permettent d'agir plus vite : à chacun de vos tours de combat, "
        "vous pouvez effectuer l'action Foncer, Se désengager ou Se cacher par une action bonus. C'est ce qui permet au "
        "roublard de frapper puis de se mettre à couvert ou de quitter la mêlée sans subir d'attaque d'opportunité."
    ),
    "Archétype de roublard": (
        "Au niveau 3, vous choisissez un archétype qui reflète votre façon d'exercer vos talents : Voleur, Assassin, "
        "Arnaqueur arcanique (Manuel des joueurs), Bretteur, Conspirateur, Éclaireur, Enquêteur (Xanathar), Lame "
        "psychique ou Fantôme (Tasha), ou une option communautaire. Votre archétype vous accorde des aptitudes aux "
        "niveaux 3, 9, 13 et 17."
    ),
    "Visée stable (option Tasha)": (
        "Capacité de classe optionnelle du Chaudron des merveilles de Tasha. Par une action bonus, vous vous "
        "donnez l'avantage sur votre prochain jet d'attaque effectué pendant le tour en cours. Vous ne pouvez l'utiliser "
        "que si vous ne vous êtes pas encore déplacé pendant ce tour, et votre vitesse tombe à 0 jusqu'à la fin du tour "
        "après l'avoir utilisée. Elle garantit l'Attaque sournoise à distance mais empêche d'utiliser Action rusée le "
        "même tour."
    ),
    "Esquive instinctive": (
        "Lorsqu'un attaquant que vous pouvez voir vous touche avec une attaque, vous pouvez utiliser votre réaction "
        "pour réduire de moitié les dégâts que cette attaque vous inflige. Utilisable une fois par round (une réaction), "
        "sans limite d'utilisations par repos ; elle ne s'applique pas aux sorts à jet de sauvegarde."
    ),
    "Expertise supplémentaire": (
        "Choisissez deux autres compétences que vous maîtrisez (ou une compétence et les outils de voleur, s'ils n'ont "
        "pas déjà été choisis). Pour les tests de caractéristique qui les utilisent, vous doublez votre bonus de "
        "maîtrise. Vous possédez ainsi quatre maîtrises bénéficiant de l'Expertise."
    ),
    "Évasion": (
        "Vous esquivez avec agilité certains effets de zone, comme le souffle d'un dragon ou une boule de feu. Lorsque "
        "vous êtes soumis à un effet qui vous permet de faire un jet de sauvegarde de Dextérité pour ne subir que la "
        "moitié des dégâts, vous ne subissez aucun dégât si vous réussissez le jet, et seulement la moitié des dégâts "
        "si vous l'échouez."
    ),
    "Talent fiable": (
        "Vous avez affiné vos compétences jusqu'à les rendre quasi infaillibles. Chaque fois que vous faites un test de "
        "caractéristique qui vous permet d'ajouter votre bonus de maîtrise, vous pouvez considérer tout résultat de 9 "
        "ou moins sur le d20 comme un 10. Cela s'applique aussi aux compétences bénéficiant de l'Expertise et aux "
        "outils maîtrisés."
    ),
    "Perception aveugle": (
        "Au niveau 14, tant que vous pouvez entendre, vous connaissez l'emplacement de toute "
        "créature cachée ou invisible située à 3 m ou moins de vous. Vous savez où elle se trouve, mais elle reste "
        "invisible ou cachée : vos attaques contre elle subissent toujours le désavantage si vous ne la voyez pas."
    ),
    "Esprit fuyant": (
        "Votre esprit est devenu particulièrement difficile à saisir. Vous obtenez la maîtrise des jets de sauvegarde "
        "de Sagesse, ce qui vous protège mieux contre les charmes, la terreur et de nombreux effets de contrôle mental."
    ),
    "Insaisissable": (
        "Vous êtes si évasif que les attaquants prennent rarement le dessus sur vous : "
        "aucun jet d'attaque ne peut bénéficier de l'avantage contre vous tant que vous n'êtes pas neutralisé "
        "(condition incapable d'agir). Les effets qui donnent normalement l'avantage (vous êtes à terre, aveuglé, "
        "entravé, invisible pour vous…) n'en accordent plus, mais le désavantage de l'attaquant s'applique toujours."
    ),
    "Coup de chance": (
        "Vous avez le don étrange de réussir quand cela compte. Si vous ratez une attaque contre une cible à votre "
        "portée, vous pouvez transformer cet échec en coup au but. Si vous échouez à un test de caractéristique, vous "
        "pouvez à la place considérer le résultat du d20 comme un 20. Une fois utilisée, cette aptitude n'est plus "
        "disponible avant la fin d'un repos court ou long."
    ),
}

SUB = {
    "Voleur": {
        "Mains lestes & Monte-en-l'air": (
            "Mains lestes : l'action bonus de votre Action rusée vous permet aussi de faire un test de Dextérité "
            "(Escamotage), d'utiliser vos outils de voleur pour désamorcer un piège ou crocheter une serrure, ou "
            "d'effectuer l'action Utiliser un objet (potion, fiole d'acide, bille, chausse-trappe…). "
            "Monte-en-l'air : escalader ne vous coûte plus de déplacement supplémentaire, et lorsque vous faites un "
            "saut en longueur avec élan, la distance parcourue augmente de 30 cm × votre modificateur de Dextérité."
        ),
        "Furtivité suprême": (
            "Au niveau 9, vous avez l'avantage aux tests de Dextérité (Discrétion) si vous ne vous déplacez pas de plus "
            "de la moitié de votre vitesse pendant ce tour. Combinée à Action rusée (Se cacher), elle permet de rester "
            "dissimulé presque à chaque tour."
        ),
        "Utilisation d'objets magiques": (
            "Au niveau 13, vous avez appris suffisamment sur le fonctionnement de la magie pour improviser l'usage "
            "d'objets qui ne vous sont pas destinés : vous ignorez toutes les conditions de classe, de race et de "
            "niveau liées à l'utilisation des objets magiques (y compris les parchemins de sorts, que vous pouvez lire "
            "quelle que soit votre classe)."
        ),
        "Réflexes de voleur": (
            "Au niveau 17, vous êtes passé maître dans l'art de tendre des embuscades et de fuir rapidement. Vous jouez "
            "deux tours lors du premier round de chaque combat : le premier à votre initiative normale, le second à "
            "votre initiative moins 10. Vous ne pouvez pas utiliser cette aptitude si vous êtes surpris."
        ),
    },
    "Assassin": {
        "Maîtrises supplémentaires & Assassinat": (
            "Maîtrises supplémentaires : vous maîtrisez le matériel de déguisement et le matériel d'empoisonneur. "
            "Assassinat : vous avez l'avantage aux jets d'attaque contre toute créature qui n'a pas encore joué son "
            "tour dans le combat. De plus, toute attaque qui touche une créature surprise est automatiquement un coup "
            "critique (dés de l'arme et dés d'Attaque sournoise doublés)."
        ),
        "Expert en infiltration": (
            "Au niveau 9, vous pouvez créer de façon infaillible une fausse identité. Vous devez passer 7 jours et "
            "dépenser 25 po pour lui forger un passé, une profession et des affiliations crédibles (documents, "
            "connaissances, relations). Vous ne pouvez pas usurper l'identité d'une personne existante. Une fois "
            "établie, cette identité est acceptée par les autres comme si elle était réelle tant que rien ne leur "
            "donne de raison d'en douter."
        ),
        "Imposteur": (
            "Au niveau 13, vous pouvez imiter sans faille la voix, l'écriture et le comportement d'une autre personne. "
            "Vous devez l'étudier pendant au moins 3 heures (l'écouter, lire ses écrits, observer ses manières). Les "
            "observateurs occasionnels ne détectent pas la supercherie ; si une créature méfiante soupçonne quelque "
            "chose, vous avez l'avantage à vos tests de Charisme (Tromperie) pour éviter d'être démasqué."
        ),
        "Coup meurtrier": (
            "Au niveau 17, lorsque vous attaquez et touchez une créature surprise, elle doit faire un jet de sauvegarde "
            "de Constitution (DD = 8 + votre bonus de maîtrise + votre modificateur de Dextérité). En cas d'échec, "
            "les dégâts de votre attaque contre elle sont doublés (après le coup critique automatique d'Assassinat)."
        ),
    },
    "Arnaqueur arcanique": {
        "Sorts & Passe-passe à distance": (
            "Incantation : vous lancez des sorts de magicien avec l'Intelligence (DD de sauvegarde = 8 + votre bonus de "
            "maîtrise + votre modificateur d'Intelligence ; attaque avec un sort = votre bonus de maîtrise + votre "
            "modificateur d'Intelligence). Vous connaissez le tour de magie Main du mage et 2 autres tours de magicien "
            "(un 4e au niveau 10). Vous connaissez 3 sorts de niveau 1 au niveau 3, puis 4 (niveau 4), 5 (7), 6 (8), "
            "7 (10), 8 (11), 9 (13), 10 (14), 11 (16), 12 (19) et 13 (20) ; ils doivent être d'enchantement ou "
            "d'illusion, sauf ceux appris aux niveaux 3, 8, 14 et 20, de n'importe quelle école. Emplacements : 2 de "
            "niveau 1 (niveau 3), 3 (niveau 4), 4 de niveau 1 et 2 de niveau 2 (niveau 7), 3 de niveau 2 (niveau 10), 2 de "
            "niveau 3 (niveau 13), 3 de niveau 3 (niveau 16), 1 de niveau 4 (niveau 19) ; récupérés après un repos long. "
            "Passe-passe à distance : votre Main du mage peut être invisible, ranger ou prendre un objet dans un "
            "contenant porté par une autre créature, crocheter une serrure ou désamorcer un piège à distance avec vos "
            "outils de voleur ; vous la contrôlez par une action bonus (Escamotage opposé à la Sagesse (Perception) "
            "pour ne pas être remarqué)."
        ),
        "Embuscade magique": (
            "Au niveau 9, si vous êtes caché d'une créature au moment où vous lancez un sort sur elle, cette créature a "
            "le désavantage à tout jet de sauvegarde qu'elle effectue contre ce sort pendant ce tour."
        ),
        "Escroquerie polyvalente": (
            "Au niveau 13, par une action bonus, vous désignez une "
            "créature située à 1,50 m ou moins de la main spectrale créée par votre sort Main du mage. Vous avez "
            "l'avantage aux jets d'attaque contre cette créature jusqu'à la fin du tour, ce qui active aussi votre "
            "Attaque sournoise."
        ),
        "Voleur de sort": (
            "Au niveau 17, immédiatement après qu'une créature a lancé un sort qui vous cible ou vous inclut dans sa "
            "zone d'effet, vous pouvez utiliser votre réaction pour la forcer à faire un jet de sauvegarde basé sur "
            "sa propre caractéristique de lanceur de sorts, contre le DD de vos sorts. En cas d'échec, vous annulez l'effet du sort contre "
            "vous et, s'il est d'un niveau que vous pouvez lancer (niveau 1 ou plus), vous en volez la connaissance "
            "pendant 8 heures : vous pouvez le lancer avec vos emplacements, tandis que la créature ne peut plus le "
            "lancer pendant cette durée. Une fois par repos long."
        ),
    },
    "Bretteur (Swashbuckler)": {
        "Jeu de jambes sophistiqué & Audace désinvolte": (
            "Jeu de jambes sophistiqué : pendant votre tour, si vous effectuez une attaque au corps à corps contre une "
            "créature, celle-ci ne peut pas faire d'attaque d'opportunité contre vous pendant le reste de ce tour. "
            "Audace désinvolte : vous ajoutez votre modificateur de Charisme à vos jets d'initiative. De plus, vous "
            "pouvez appliquer votre Attaque sournoise sans avoir l'avantage si la cible est à 1,50 m ou moins de vous, "
            "qu'aucune autre créature ne se trouve à 1,50 m ou moins de vous et que vous n'avez pas le désavantage."
        ),
        "Panache": (
            "Au niveau 9, par une action, vous faites un test de Charisme (Persuasion) opposé au test de Sagesse "
            "(Perspicacité) d'une créature qui peut vous entendre et parle une langue commune avec vous. Créature "
            "hostile : en cas de réussite, pendant 1 minute elle a le désavantage aux attaques contre d'autres cibles "
            "que vous et ne peut pas faire d'attaque d'opportunité contre elles ; l'effet cesse si vos alliés "
            "l'attaquent ou l'affectent avec un sort, ou si vous êtes à plus de 18 m l'un de l'autre. Créature non "
            "hostile : elle est charmée par vous pendant 1 minute (fin si vous ou vos alliés lui nuisez)."
        ),
        "Manœuvre élégante": (
            "Au niveau 13, vous pouvez utiliser une action bonus pour obtenir l'avantage au prochain test de Dextérité "
            "(Acrobaties) ou de Force (Athlétisme) que vous effectuez pendant ce tour (pour vous dégager d'une "
            "empoignade, bousculer, franchir un obstacle…)."
        ),
        "Maître duelliste": (
            "Au niveau 17, lorsque vous ratez un jet d'attaque, vous pouvez le relancer immédiatement avec l'avantage. "
            "Une fois cette aptitude utilisée, vous devez terminer un repos court ou long pour l'utiliser de nouveau."
        ),
    },
    "Conspirateur (Mastermind)": {
        "Maître des intrigues & Maître tacticien": (
            "Maître des intrigues : vous maîtrisez le matériel de déguisement, le matériel de contrefaçon et un type de "
            "jeu, et apprenez deux langues de votre choix. Si vous écoutez une créature parler pendant au moins "
            "1 minute, vous pouvez imiter son élocution et son accent. Maître tacticien : vous pouvez effectuer "
            "l'action Aider par une action bonus. Quand vous aidez un allié à attaquer, la cible peut se trouver jusqu'à "
            "9 m de vous (au lieu de 1,50 m) si elle peut vous voir ou vous entendre."
        ),
        "Manipulateur perspicace": (
            "Au niveau 9, si vous passez au moins 1 minute à observer une créature ou à interagir avec elle hors combat, "
            "vous apprenez si elle vous est égale, supérieure ou inférieure dans deux des domaines suivants, au choix : "
            "valeur d'Intelligence, valeur de Sagesse, valeur de Charisme, niveaux de classe. Le MD peut aussi vous "
            "révéler un élément de son histoire ou de sa personnalité."
        ),
        "Redirection": (
            "Au niveau 13, lorsque vous êtes la cible d'une attaque alors qu'une créature située à 1,50 m ou moins de "
            "vous vous procure un abri contre cette attaque, vous pouvez utiliser votre réaction pour que l'attaque "
            "prenne cette créature pour cible à votre place."
        ),
        "Âme du trompeur": (
            "Au niveau 17, vos pensées ne peuvent pas être lues par télépathie ou par d'autres moyens, sauf si vous le "
            "permettez. Vous pouvez présenter de fausses pensées en réussissant un test de Charisme (Tromperie) opposé "
            "au test de Sagesse (Perspicacité) du lecteur. Quoi que vous disiez, la magie qui détecte les mensonges "
            "vous indique toujours comme sincère, et vous ne pouvez pas être magiquement contraint à dire la vérité."
        ),
    },
    "Éclaireur (Scout)": {
        "Escarmoucheur & Survivaliste": (
            "Escarmoucheur : lorsqu'un ennemi termine son tour à 1,50 m ou moins de vous, vous pouvez utiliser votre "
            "réaction pour vous déplacer d'une distance égale à la moitié de votre vitesse ; ce déplacement ne provoque "
            "pas d'attaque d'opportunité. Survivaliste : vous obtenez la maîtrise des compétences Nature et Survie si "
            "vous ne les avez pas déjà, et vous doublez votre bonus de maîtrise pour les tests qui les utilisent."
        ),
        "Mobilité supérieure": (
            "Au niveau 9, votre vitesse de marche augmente de 3 m. Si vous avez une vitesse d'escalade ou de nage, "
            "elle augmente également de 3 m."
        ),
        "Maître de l'embuscade": (
            "Au niveau 13, vous avez l'avantage aux jets d'initiative. De plus, la première créature que vous touchez "
            "lors du premier round d'un combat devient plus vulnérable : les autres créatures ont l'avantage aux jets "
            "d'attaque contre elle jusqu'au début de votre prochain tour."
        ),
        "Frappe soudaine": (
            "Au niveau 17, si vous effectuez l'action Attaquer pendant votre tour, vous pouvez porter une attaque "
            "supplémentaire par une action bonus. Cette attaque peut bénéficier de votre Attaque sournoise même si vous "
            "l'avez déjà utilisée pendant ce tour, mais jamais deux fois contre la même cible au cours d'un même tour."
        ),
    },
    "Enquêteur (Inquisitive)": {
        "Détecteur de mensonges, Œil perçant & Sagacité au combat": (
            "Détecteur de mensonges : lors d'un test de Sagesse (Perspicacité) pour déterminer si une créature ment, "
            "considérez tout résultat de 7 ou moins sur le d20 comme un 8. Œil perçant : par une action bonus, vous "
            "pouvez faire un test de Sagesse (Perception) pour repérer une créature ou un objet cachés, ou un test "
            "d'Intelligence (Investigation) pour découvrir ou déchiffrer des indices. Sagacité au combat : par une "
            "action bonus, test de Sagesse (Perspicacité) opposé au test de Charisme (Tromperie) d'une créature visible "
            "qui n'est pas neutralisée ; en cas de réussite, vous pouvez lui appliquer votre Attaque sournoise sans "
            "avoir l'avantage (mais pas si vous avez le désavantage) pendant 1 minute ou jusqu'à ce que vous utilisiez "
            "de nouveau cette aptitude sur une autre cible."
        ),
        "Attentif": (
            "Au niveau 9, vous avez l'avantage aux tests de Sagesse (Perception) et d'Intelligence (Investigation) si "
            "vous ne vous déplacez pas de plus de la moitié de votre vitesse pendant ce tour."
        ),
        "Vision infaillible": (
            "Au niveau 13, par une action, vous percevez la présence d'illusions, de métamorphes qui ne sont pas sous "
            "leur forme d'origine et de toute autre magie destinée à tromper les sens, dans un rayon de 9 m, à condition "
            "de ne pas être aveuglé ou assourdi. Vous savez qu'un effet trompeur est là, sans en connaître la nature "
            "exacte. Utilisable un nombre de fois égal à votre modificateur de Sagesse (minimum 1) ; récupération après "
            "un repos long."
        ),
        "Sens de la faiblesse": (
            "Au niveau 17, lorsque votre Sagacité au combat est active contre une créature, les dégâts de votre "
            "Attaque sournoise contre elle augmentent de 3d6."
        ),
    },
    "Lame psychique / Soulknife": {
        "Pouvoir psionique & Lames psychiques": (
            "Pouvoir psionique : vous disposez d'un nombre de dés d'énergie psionique égal à 2 × votre bonus de "
            "maîtrise. Ce sont des d6 au niveau 3, d8 au niveau 5, d10 au niveau 11 et d12 au niveau 17. Vous les "
            "récupérez tous après un repos long, et une fois par repos court ou long vous pouvez en récupérer un par "
            "une action bonus. Savoir-faire renforcé : si vous ratez un test de caractéristique avec une compétence ou "
            "un outil maîtrisé, lancez un dé psionique et ajoutez-le ; il n'est dépensé que si le test réussit. "
            "Murmures psychiques : par une action, vous liez télépathiquement un nombre de créatures visibles égal à "
            "votre bonus de maîtrise pendant un nombre d'heures égal au résultat d'un dé psionique (portée 1,5 km) ; la "
            "première utilisation après un repos long est gratuite. Lames psychiques : quand vous effectuez l'action "
            "Attaquer, vous pouvez manifester une lame (arme courante de corps à corps, finesse, lancer 18/36 m) qui "
            "inflige 1d6 dégâts psychiques + le modificateur utilisé ; ensuite, par une action bonus, une seconde lame "
            "dans l'autre main (main libre requise) inflige 1d4 dégâts psychiques + ce modificateur."
        ),
        "Lames spirituelles": (
            "Au niveau 9. Frappes autoguidées : si vous ratez une attaque avec vos Lames psychiques, lancez un dé "
            "psionique et ajoutez-le au jet d'attaque ; le dé n'est dépensé que si l'attaque touche alors. "
            "Téléportation psychique : par une action bonus, dépensez un dé psionique, lancez-le et projetez une lame "
            "vers un espace inoccupé visible situé à une distance maximale de 3 m × le résultat du dé ; vous vous "
            "téléportez à cet endroit et la lame disparaît."
        ),
        "Voile psychique": (
            "Au niveau 13, par une action, vous devenez invisible, ainsi que tout ce que vous portez ou transportez, "
            "pendant 1 heure ou jusqu'à ce que vous y mettiez fin (aucune action requise). L'invisibilité cesse "
            "immédiatement après que vous avez infligé des dégâts à une créature ou forcé une créature à faire un jet de "
            "sauvegarde. Une fois par repos long, ou en dépensant un dé d'énergie psionique pour l'utiliser de nouveau."
        ),
        "Rupture spirituelle": (
            "Au niveau 17, lorsque vous infligez les dégâts de votre Attaque sournoise avec vos Lames psychiques, vous "
            "pouvez forcer la cible à faire un jet de sauvegarde de Sagesse (DD = 8 + votre bonus de maîtrise + votre "
            "modificateur de Dextérité). En cas d'échec, elle est étourdie pendant 1 minute et peut retenter le jet à la "
            "fin de chacun de ses tours pour y mettre fin. Une fois par repos long, ou en dépensant 3 dés d'énergie "
            "psionique pour l'utiliser de nouveau."
        ),
    },
    "Fantôme (Phantom)": {
        "Murmures des défunts & Lamentations sépulcrales": (
            "Murmures des défunts : à la fin d'un repos court ou long, vous obtenez la maîtrise d'une compétence ou d'un "
            "outil de votre choix, soufflée par un esprit ; elle dure jusqu'à ce que vous utilisiez de nouveau cette "
            "aptitude. Lamentations sépulcrales : juste après avoir infligé les dégâts de votre Attaque sournoise "
            "pendant votre tour, vous pouvez viser une seconde créature visible située à 9 m ou moins de la première ; "
            "lancez la moitié de vos dés d'Attaque sournoise (arrondie au supérieur) : elle subit ce total en dégâts "
            "nécrotiques. Utilisable un nombre de fois égal à votre bonus de maîtrise ; récupération après un repos long."
        ),
        "Bribes des défunts": (
            "Au niveau 9, quand une créature que vous pouvez voir meurt à 9 m "
            "ou moins de vous, vous pouvez utiliser votre réaction pour faire apparaître dans votre main libre une "
            "babiole d'âme (objet Très petit). Vous pouvez en posséder un nombre maximal égal à votre bonus de maîtrise. "
            "Tant que vous en tenez une : avantage aux jets de sauvegarde contre la mort et de Constitution. Quand vous "
            "infligez votre Attaque sournoise pendant votre tour, vous pouvez détruire une babiole pour utiliser "
            "Lamentations sépulcrales sans dépenser d'utilisation. Par une action, vous pouvez détruire une babiole "
            "pour poser une question à l'esprit qui y est lié ; il répond brièvement dans une langue qu'il connaissait."
        ),
        "Marche spectrale": (
            "Au niveau 13, par une action bonus, vous prenez une forme spectrale pendant 10 minutes : vous obtenez une "
            "vitesse de vol de 3 m et pouvez faire du vol stationnaire, les jets d'attaque contre vous ont le "
            "désavantage, et vous pouvez traverser créatures et objets comme un terrain difficile (vous subissez 1d10 "
            "dégâts de force si vous terminez votre tour à l'intérieur). Vous reprenez votre forme normale par une "
            "action bonus. Une fois par repos long, ou en détruisant une babiole d'âme pour l'utiliser de nouveau."
        ),
        "Intime du trépas": (
            "Au niveau 17, vos Lamentations sépulcrales infligent leurs dégâts nécrotiques à la fois à la première et à "
            "la seconde créature. De plus, à la fin d'un repos long, une babiole d'âme apparaît dans votre main si vous "
            "n'en possédez aucune."
        ),
    },
    "Lame d'ombre": {
        "Pas des ombres & Frappe ténébreuse": (
            "Enfant des ténèbres : vous obtenez la vision dans le noir sur 18 m (ou +9 m si vous l'avez déjà). Pas des "
            "ombres : par une action bonus, alors que vous êtes dans une zone de lumière faible ou d'obscurité, vous "
            "vous téléportez jusqu'à 9 m vers un espace inoccupé visible lui aussi dans la lumière faible ou "
            "l'obscurité. Utilisable un nombre de fois égal à votre bonus de maîtrise ; récupération après un repos "
            "long. Frappe ténébreuse : lorsque vous infligez votre Attaque sournoise alors que vous ou la cible êtes "
            "dans la lumière faible ou l'obscurité, vous pouvez convertir ses dégâts en dégâts nécrotiques ; si vous "
            "avez utilisé Pas des ombres pendant ce tour, ils deviennent au choix nécrotiques ou de force."
        ),
        "Manteau d'obscurité": (
            "Au niveau 9, tant que vous êtes dans l'obscurité, vous êtes invisible pour toute créature qui compte sur "
            "la vision dans le noir pour vous voir (la vision véritable et la vision aveugle vous perçoivent "
            "normalement). De plus, vous avez l'avantage aux tests de Dextérité (Discrétion) effectués dans la lumière "
            "faible ou l'obscurité, et vous pouvez utiliser Pas des ombres sans dépenser d'utilisation une fois par "
            "repos court ou long."
        ),
        "Clone d'ombre": (
            "Au niveau 13, par une action bonus, vous détachez votre ombre dans un espace inoccupé visible à 9 m ou "
            "moins ; elle persiste 1 minute (concentration, comme un sort). Le clone a votre CA, 1 point de vie, ne "
            "peut pas agir et se déplace de 9 m à votre demande pendant votre tour (sans action). Tant qu'il se trouve "
            "à 1,50 m ou moins d'une créature, il compte comme un ennemi de celle-ci pour votre Attaque sournoise. "
            "Lorsqu'une attaque vous touche, vous pouvez utiliser votre réaction pour échanger votre place avec le "
            "clone : l'attaque le vise à votre place et le détruit. Une fois par repos long, ou en dépensant 2 "
            "utilisations de Pas des ombres."
        ),
        "Exécution ténébreuse": (
            "Au niveau 17, par une action bonus, vous marquez une créature visible à 18 m ou moins pendant 1 minute. "
            "Une fois pendant cette durée, lorsque vous attaquez la créature marquée, vous pouvez d'abord vous "
            "téléporter dans un espace inoccupé à 1,50 m d'elle (si l'un de vous deux est dans la lumière faible ou "
            "l'obscurité) et avez l'avantage à cette attaque. Si elle touche et que vous infligez votre Attaque "
            "sournoise, la cible fait un jet de sauvegarde de Constitution (DD = 8 + votre bonus de maîtrise + votre "
            "modificateur de Dextérité) : en cas d'échec, les dés d'Attaque sournoise infligent leur maximum ; en cas "
            "de réussite, ils sont lancés normalement. Une fois par repos court ou long."
        ),
    },
    "Pistoléro": {
        "Armurier & Tir ciblé": (
            "Armurier : vous maîtrisez les armes à feu et les outils de bricoleur, avec lesquels vous fabriquez "
            "10 balles (valeur 3 po) en 1 heure lors d'un repos. Pistolet : 1d10 perforants, portée 9/27 m, légère ; "
            "mousquet : 1d12 perforants, portée 12/36 m, deux mains. Ce sont des armes à distance : elles permettent "
            "l'Attaque sournoise. Enrayement : sur un 1 naturel au d20, l'arme s'enraye et ne peut plus tirer avant "
            "que vous utilisiez une action (ou l'action bonus de votre Action rusée) pour la dégager. Tir ciblé : une "
            "fois par tour, lorsque vous touchez avec une arme à feu et infligez votre Attaque sournoise, vous pouvez "
            "renoncer à 1d6 de ces dés pour viser un point précis (JS contre DD = 8 + votre bonus de maîtrise + votre "
            "modificateur de Dextérité) : jambe (aucun JS, vitesse réduite de moitié jusqu'à la fin de son prochain "
            "tour), bras (JS de Force ou elle lâche un objet tenu de votre choix), tête (JS de Constitution ou "
            "désavantage à ses jets d'attaque jusqu'à la fin de son prochain tour)."
        ),
        "Rechargement éclair": (
            "Au niveau 9, vous ignorez la propriété chargement des armes à feu et n'avez pas le désavantage aux attaques "
            "à distance avec une arme à feu lorsqu'un ennemi se trouve à 1,50 m de vous. De plus, lorsque vous faites "
            "tomber une créature à 0 point de vie avec une attaque d'arme à feu pendant votre tour, vous pouvez utiliser "
            "votre réaction pour effectuer une attaque d'arme à feu contre une autre créature à portée ; l'Attaque "
            "sournoise s'y applique si vous ne l'avez pas encore utilisée ce tour."
        ),
        "Ricochet acrobatique": (
            "Au niveau 13, vos tirs d'arme à feu ignorent l'abri partiel (abri à moitié). De plus, lorsque vous ratez "
            "une attaque d'arme à feu, vous pouvez faire ricocher la balle : effectuez immédiatement un nouveau jet "
            "d'attaque, avec les mêmes bonus, contre une autre créature visible située à 3 m ou moins de la cible "
            "d'origine. L'Attaque sournoise s'y applique si vous ne l'avez pas encore utilisée ce tour. Utilisable un "
            "nombre de fois égal à votre bonus de maîtrise ; récupération après un repos long."
        ),
        "Pluie de plomb": (
            "Au niveau 17, par une action, vous faites feu sur un maximum de 3 créatures visibles situées dans la "
            "portée normale de votre arme, avec un jet d'attaque distinct pour chacune (aucune munition ni chargement "
            "supplémentaire requis). Vous n'avez pas besoin d'avantage pour l'Attaque sournoise lors de ces tirs, tant "
            "que vous n'avez pas le désavantage : la première créature touchée subit tous vos dés d'Attaque sournoise, "
            "les suivantes la moitié de ces dés (arrondie au supérieur). Une fois par repos court ou long."
        ),
    },
}

CORRIGE = [
    ("mineur", "Attaque sournoise", "Dé fixe « 1d6 » dans le nom ; description sans condition d'arme ni progression — "
     "renommée et décrite avec la formule (moitié arrondie au supérieur du niveau de roublard, en d6)",
     "Arme de finesse ou à distance ; 1d6 au niveau 1 puis +1d6 tous les 2 niveaux (10d6 au niveau 19)"),
    ("mineur", "Attaque sournoise", "« Allié à 1,5 m » sans préciser qu'il ne doit pas être neutralisé ni l'absence de désavantage",
     "Ennemi de la cible à 1,50 m, non neutralisé, et vous n'avez pas le désavantage"),
    ("mineur", "Action rusée", "Anglicisme « Dasher »", "Action Foncer (Dash)"),
    ("mineur", "Visée stable (option Tasha)", "Nom non officiel ; vitesse réduite à 0 non mentionnée",
     "Visée stable (TCE) : action bonus, sans s'être déplacé, puis vitesse 0 jusqu'à la fin du tour"),
    ("mineur", "Perception aveugle", "Nom non officiel « Sens aveugle »", "Perception aveugle (Blindsense), 3 m"),
    ("mineur", "Insaisissable", "Nom non officiel « Elusif » et accent manquant", "Insaisissable (Elusive)"),
    ("mineur", "Coup de chance", "« Réussite automatique » sur un test et « 1/repos » ambigu",
     "Le d20 du test est considéré comme un 20 ; une fois par repos court ou long"),
    ("mineur", "Voleur / Mains lestes & Monte-en-l'air", "Bonus de saut en longueur (+ mod. de Dextérité) omis",
     "Saut en longueur avec élan augmenté d'un nombre de pieds égal au modificateur de Dextérité"),
    ("mineur", "Voleur / Réflexes de voleur", "Faute de frappe « initiale » ; restriction surprise absente",
     "Initiative normale puis initiative − 10 ; inutilisable si surpris"),
    ("majeur", "Assassin / Coup meurtrier", "DD fixe de 14 dans les données",
     "DD = 8 + modificateur de Dextérité + bonus de maîtrise (PHB)"),
    ("info", "Arnaqueur arcanique / sorts_domaine", "Liste fixe de sorts fournie, alors que l'archétype n'en a pas — liste vidée",
     "Choix libre parmi les sorts de magicien (enchantement/illusion, sauf 4 choix libres)"),
    ("info", "Arnaqueur arcanique / Sorts & Passe-passe à distance", "Emplacements, sorts connus et DD absents",
     "Lanceur au tiers (Intelligence) : 3 sorts connus au niveau 3 jusqu'à 13 ; emplacements jusqu'au niveau 4"),
    ("mineur", "Arnaqueur arcanique / Escroquerie polyvalente", "Nom non officiel « Omniprésence » ; cible « adjacente » à vous",
     "Escroquerie polyvalente (Versatile Trickster) : créature à 1,50 m de la main spectrale"),
    ("mineur", "Arnaqueur arcanique / Voleur de sort", "Présenté comme un Contresort",
     "Réaction après un sort qui vous cible : JS contre votre DD de sort, annulation et vol 8 h ; 1/repos long"),
    ("mineur", "Bretteur (Swashbuckler) / Jeu de jambes sophistiqué & Audace désinvolte",
     "Faute d'accord « sophistiqués » ; abréviation « mod. »", "Jeu de jambes sophistiqué ; modificateur de Charisme"),
    ("mineur", "Bretteur (Swashbuckler) / Panache", "« Test de Charisme opposé à la Sagesse » imprécis",
     "Charisme (Persuasion) opposé à Sagesse (Perspicacité), action, 1 minute"),
    ("mineur", "Conspirateur (Mastermind) / Maître des intrigues & Maître tacticien", "Jeu (gaming set) et imitation d'accent omis",
     "Matériel de déguisement, de contrefaçon, un jeu, deux langues, imitation après 1 minute d'écoute"),
    ("mineur", "Conspirateur (Mastermind) / Redirection", "Condition d'abri absente",
     "La créature à 1,50 m doit vous fournir un abri contre l'attaque"),
    ("mineur", "Éclaireur (Scout) / Escarmoucheur & Survivaliste", "Déclencheur « un ennemi s'approche » inexact",
     "Réaction quand un ennemi termine son tour à 1,50 m de vous"),
    ("mineur", "Éclaireur (Scout) / Frappe soudaine", "Restriction de cible omise",
     "Pas deux Attaques sournoises contre la même cible le même tour"),
    ("mineur", "Enquêteur (Inquisitive) / Détecteur de mensonges, Œil perçant & Sagacité au combat",
     "Œil perçant non décrit ; durée de Sagacité (1 minute) omise",
     "Œil perçant : action bonus Perception/Investigation ; Sagacité dure 1 minute"),
    ("majeur", "Enquêteur (Inquisitive) / Vision infaillible", "Limitée à 1/repos long ; portée omise",
     "Utilisations = modificateur de Sagesse (min. 1) par repos long, rayon de 9 m"),
    ("majeur", "Lame psychique / Soulknife / Pouvoir psionique & Lames psychiques", "Dés psioniques fixés à d12 ; nombre de dés absent",
     "2 × bonus de maîtrise dés ; d6 (niveau 3), d8 (niveau 5), d10 (niveau 11), d12 (niveau 17)"),
    ("majeur", "Lame psychique / Soulknife / Rupture spirituelle", "DD fixe de 14",
     "DD = 8 + bonus de maîtrise + modificateur de Dextérité ; 1/repos long ou 3 dés psioniques"),
    ("majeur", "Fantôme (Phantom) / Murmures des défunts & Lamentations sépulcrales", "Dégâts fixes de 5d6 ; utilisations absentes",
     "Moitié des dés d'Attaque sournoise (arrondie au supérieur), bonus de maîtrise fois par repos long"),
    ("majeur", "Fantôme (Phantom) / Bribes des défunts", "Obtenue au niveau 6 sous le nom « Bribes funèbres (Jetons d'âme) » — "
     "renommée et déplacée au niveau 9",
     "Bribes des défunts (Tokens of the Departed) au niveau 9 ; le Fantôme n'a rien au niveau 6"),
    ("mineur", "Fantôme (Phantom) / Marche spectrale", "Durée et utilisations absentes ; action bonus correcte",
     "10 minutes, 1/repos long ou en détruisant une babiole d'âme"),
    ("mineur", "Lame d'ombre / sorts_domaine", "Entrées numériques « 1 » à « 5 » mêlées aux noms de sorts — supprimées",
     "Liste ne devant contenir que des noms de sorts (archétype non lanceur : liste inutilisée)"),
    ("mineur", "Lame d'ombre / sorts_domaine", "« Passage dans l'éther » n'existe pas — remplacé par Double illusoire (niveau 5)",
     "Sort officiel « Forme éthérée » (niveau 7), hors de portée d'un roublard"),
]

AUDIT = [
    ("info", "Lame psychique / Soulknife", "Nom de sous-classe mêlant français et anglais : non renommée pour ne pas "
     "casser les fiches existantes", "Lame psychique (Soulknife, TCE)"),
]
