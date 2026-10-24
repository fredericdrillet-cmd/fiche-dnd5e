"""Descriptions enrichies — Ensorceleur (PHB, Xanathar, Tasha ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Ensorceleur"

BASE = {
    "Incantation": (
        "Vous lancez des sorts d'ensorceleur grâce à une magie innée ; le Charisme est votre caractéristique "
        "d'incantation. DD de sauvegarde de vos sorts = 8 + votre bonus de maîtrise + votre modificateur de Charisme ; "
        "bonus d'attaque avec un sort = votre bonus de maîtrise + votre modificateur de Charisme. Vous connaissez 4 tours "
        "de magie au niveau 1 (5 au niveau 4, 6 au niveau 10) et 2 sorts de niveau 1 ; le nombre de sorts connus "
        "augmente ensuite jusqu'à 15 au niveau 17, et chaque nouveau sort doit être d'un niveau pour lequel vous avez "
        "des emplacements. Chaque fois que vous gagnez un niveau dans cette classe, vous pouvez remplacer un sort connu par un autre de la "
        "liste. Vos emplacements se récupèrent après un repos long. Vous pouvez utiliser un focaliseur arcanique comme "
        "focaliseur d'incantation."
    ),
    "Origine magique": (
        "Au niveau 1, vous choisissez la source de votre pouvoir inné : Lignée draconique ou Magie sauvage (PHB), Âme "
        "divine, Magie des ombres ou Sorcellerie des tempêtes (Xanathar), Esprit aberrant ou Âme mécanique (Tasha). "
        "Cette origine vous accorde des aptitudes aux niveaux 1, 6, 14 et 18, et parfois des sorts supplémentaires "
        "toujours connus qui ne comptent pas dans votre nombre de sorts connus."
    ),
    "Source de magie": (
        "À partir du niveau 2, vous disposez d'un nombre de points de sorcellerie égal à votre niveau d'ensorceleur ; "
        "ils se récupèrent tous après un repos long. Incantation flexible : par une action bonus, vous transformez des "
        "points en un emplacement de sort (niveau 1 : 2 points ; niveau 2 : 3 ; niveau 3 : 5 ; niveau 4 : 6 ; "
        "niveau 5 : 7 ; impossible au-delà du niveau 5). Les emplacements ainsi créés disparaissent à la fin d'un repos "
        "long. Toujours par une action bonus, vous pouvez aussi dépenser un emplacement pour gagner un nombre de points "
        "égal à son niveau, sans jamais dépasser votre maximum de points."
    ),
    "Métamagie": (
        "Au niveau 3, vous choisissez deux options de Métamagie (une de plus aux niveaux 10 et 17). Une seule option "
        "par sort, sauf mention contraire. Options du PHB : Sort prudent (1 point, un nombre de créatures égal à votre "
        "modificateur de Charisme réussissent automatiquement la sauvegarde), Sort distant (1 point, portée doublée ou "
        "contact porté à 9 m), Sort renforcé (1 point, relancez un nombre de dés de dégâts égal à votre modificateur de "
        "Charisme, cumulable avec une autre option), Sort étendu (1 point, durée doublée jusqu'à 24 h), Sort intensifié "
        "(3 points, une cible a un désavantage à son premier jet de sauvegarde), Sort accéléré (2 points, temps "
        "d'incantation d'une action réduit à une action bonus), Sort subtil (1 point, sans composantes verbales ni "
        "somatiques), Sort jumeau (points égaux au niveau du sort, 1 pour un tour de magie : seconde cible pour un sort "
        "à cible unique). Options de Tasha : Sort chercheur (2 points, relancez un jet d'attaque raté avec ce sort, "
        "utilisable même avec une autre option) et Sort transmuté (1 point, changez le type de dégâts acide, feu, froid, "
        "foudre, poison ou tonnerre en un autre de cette liste)."
    ),
    "Sorts d'ensorceleur supplémentaires (option Tasha)": (
        "Capacité optionnelle de Tasha (niveau 1). Si votre MD l'autorise, la liste de sorts d'ensorceleur "
        "s'enrichit de nouveaux sorts, que vous pouvez apprendre comme n'importe quel sort d'ensorceleur, par "
        "exemple Graisse (niveau 1), Arme magique, Lame de feu, Sphère de feu, Épine mentale (niveau 2), Toucher du "
        "vampire (niveau 3), Bouclier de feu (niveau 4) ou Main de Bigby (niveau 5), ainsi que des sorts de plus "
        "haut niveau."
    ),
    "Versatilité magique (option Tasha)": (
        "Capacité optionnelle de Tasha (niveau 4). Chaque fois que vous atteignez un niveau qui vous accorde "
        "l'aptitude Amélioration de caractéristiques (4, 8, 12, 16 et 19), vous pouvez remplacer une de vos options "
        "de Métamagie par une autre à laquelle vous avez accès, ou remplacer un de vos tours de magie d'ensorceleur "
        "par un autre tour de magie de la liste d'ensorceleur."
    ),
    "Guidage magique (option Tasha)": (
        "Capacité optionnelle de Tasha (niveau 5). Lorsque vous ratez un test de caractéristique, vous pouvez "
        "dépenser 1 point de sorcellerie pour relancer le d20 ; vous devez conserver le nouveau résultat, même s'il "
        "est moins bon. Vous puisez pour cela dans la réserve de points de sorcellerie de l'aptitude Source de magie."
    ),
    "Métamagie supplémentaire@10": (
        "Au niveau 10, vous apprenez une troisième option de Métamagie de votre choix parmi celles décrites dans "
        "l'aptitude Métamagie (y compris, avec les règles de Tasha, Sort chercheur et Sort transmuté). Les règles "
        "habituelles s'appliquent : une seule option par sort, sauf pour celles qui précisent le contraire, et le coût "
        "en points de sorcellerie est payé au moment de l'incantation."
    ),
    "Métamagie supplémentaire@17": (
        "Au niveau 17, vous apprenez une quatrième et dernière option de Métamagie de votre choix parmi celles "
        "décrites dans l'aptitude Métamagie. Les règles restent les mêmes : une seule option de Métamagie par sort, "
        "sauf pour Sort renforcé et Sort chercheur qui peuvent s'ajouter à une autre option, et le coût en points de "
        "sorcellerie est payé au moment de l'incantation."
    ),
    "Restauration de sorcellerie": (
        "Au niveau 20, vous récupérez 4 points de sorcellerie dépensés chaque fois que vous terminez un repos court, "
        "sans pouvoir dépasser votre maximum de points (égal à votre niveau d'ensorceleur). Cela vous permet de "
        "réutiliser régulièrement la Métamagie ou l'Incantation flexible au cours d'une même journée d'aventure."
    ),
}

SUB = {
    "Lignée draconique": {
        "Ancêtre dragon & Résilience draconique": (
            "Choisissez un dragon ancestral, qui détermine le type de dégâts associé : noir ou cuivre (acide), bleu ou "
            "bronze (foudre), airain, or ou rouge (feu), vert (poison), argent ou blanc (froid). Vous parlez, lisez et "
            "écrivez le draconique, et lorsque vous faites un test de Charisme pour interagir avec un dragon, votre "
            "bonus de maîtrise est doublé s'il s'applique. Résilience draconique : votre maximum de points de vie "
            "augmente de votre niveau d'ensorceleur (+1 au niveau 1, puis +1 par niveau gagné dans cette classe), et "
            "lorsque vous ne portez pas d'armure, votre CA est égale à 13 + votre modificateur de Dextérité."
        ),
        "Affinité élémentaire": (
            "Au niveau 6, lorsque vous lancez un sort qui inflige des dégâts du type associé à votre ancêtre, vous "
            "ajoutez votre modificateur de Charisme à un jet de dégâts de ce sort. Au même moment, vous pouvez "
            "dépenser 1 point de sorcellerie pour obtenir la résistance à ce type de dégâts pendant 1 heure."
        ),
        "Ailes draconiques": (
            "Au niveau 14, par une action bonus, vous déployez des ailes de dragon dans votre dos et gagnez une "
            "vitesse de vol égale à votre vitesse actuelle. Elles durent jusqu'à ce que vous les fassiez disparaître "
            "par une autre action bonus. Vous ne pouvez pas les faire apparaître si vous portez une armure qui n'a pas "
            "été conçue pour les laisser passer, et un vêtement non adapté peut être déchiré."
        ),
        "Présence draconique": (
            "Au niveau 18, par une action, vous dépensez 5 points de sorcellerie pour projeter une aura de "
            "fascination ou de terreur (au choix) dans un rayon de 18 m. Elle dure 1 minute ou jusqu'à ce que vous "
            "perdiez votre concentration (comme pour un sort). Toute créature hostile qui commence son tour dans "
            "l'aura doit réussir un jet de sauvegarde de Sagesse (DD = 8 + votre bonus de maîtrise + votre "
            "modificateur de Charisme) ou être charmée (fascination) ou effrayée (terreur) jusqu'à la fin de l'aura. "
            "Une créature qui réussit est immunisée contre votre aura pendant 24 heures."
        ),
    },
    "Magie sauvage": {
        "Pic de magie sauvage & Marée du chaos": (
            "Pic de magie sauvage : immédiatement après que vous avez lancé un sort d'ensorceleur de niveau 1 ou "
            "supérieur, le MD peut vous demander de lancer un d20 ; sur un 1, lancez un d100 sur la table Excès de "
            "magie sauvage pour déterminer un effet aléatoire. Marée du chaos : vous pouvez vous accorder un avantage "
            "à un jet d'attaque, un test de caractéristique ou un jet de sauvegarde. Une fois utilisée, cette faculté "
            "revient après un repos long, ou plus tôt si le MD vous fait lancer sur la table Excès de magie sauvage "
            "après un sort d'ensorceleur de niveau 1 ou supérieur."
        ),
        "Comme par hasard": (
            "Au niveau 6, lorsqu'une créature que vous pouvez voir effectue un jet d'attaque, un test de "
            "caractéristique ou un jet de sauvegarde, vous pouvez utiliser votre réaction et dépenser 2 points de "
            "sorcellerie pour lancer 1d4 et ajouter ou soustraire le résultat à son jet (au choix). Vous le faites "
            "après le jet, mais avant que ses effets ne soient appliqués."
        ),
        "Chaos contrôlé": (
            "Au niveau 14, vous maîtrisez mieux le chaos : chaque fois que vous devez lancer un dé sur la table Excès "
            "de magie sauvage, vous lancez deux fois le d100 et choisissez lequel des deux résultats s'applique. Cela "
            "vous permet souvent d'écarter les effets les plus dangereux pour vous ou vos alliés."
        ),
        "Torrent arcanique": (
            "Au niveau 18, lorsque vous lancez les dés de dégâts d'un sort et qu'au moins un dé donne son résultat "
            "maximal, vous pouvez choisir l'un de ces dés, le relancer et ajouter le nouveau résultat aux dégâts. "
            "Vous ne pouvez utiliser cette aptitude qu'une fois par tour."
        ),
    },
    "Âme divine": {
        "Magie divine & Favori des dieux": (
            "Lorsque Incantation vous permet d'apprendre ou de remplacer un sort d'ensorceleur, vous pouvez le choisir "
            "dans la liste de sorts de clerc ou dans celle d'ensorceleur ; il compte alors comme un sort d'ensorceleur. "
            "Choisissez aussi une affinité qui vous donne un sort supplémentaire toujours connu : Bien (Soins), Mal "
            "(Blessure), Loi (Bénédiction), Chaos (Fléau) ou Neutralité (Protection contre le mal et le bien). Favori "
            "des dieux : lorsque vous ratez un jet de sauvegarde ou un jet d'attaque, vous pouvez lancer 2d4 et ajouter "
            "le résultat, ce qui peut transformer l'échec en réussite. Une utilisation, récupérée après un repos court "
            "ou long."
        ),
        "Soins améliorés": (
            "Au niveau 6, lorsque vous-même ou un allié situé à 1,50 m ou moins de vous lancez des dés pour déterminer "
            "les points de vie rendus par un sort, vous pouvez dépenser 1 point de sorcellerie pour relancer autant de "
            "ces dés que vous le souhaitez, une seule fois, à condition de ne pas être neutralisé. Une fois par tour."
        ),
        "Ailes d'outre-monde": (
            "Au niveau 14, par une action bonus, vous faites apparaître des ailes spectrales qui vous donnent une "
            "vitesse de vol de 9 m. Elles durent jusqu'à ce que vous soyez neutralisé, que vous mouriez ou que vous "
            "les congédiiez par une action bonus. Leur aspect dépend de votre affinité : ailes d'aigle (Bien ou Loi), "
            "de chauve-souris (Mal ou Chaos) ou de libellule (Neutralité)."
        ),
        "Rétablissement céleste": (
            "Au niveau 18, par une action bonus, lorsqu'il vous reste moins de la moitié de vos points de vie maximum, "
            "vous récupérez un nombre de points de vie égal à la moitié de votre maximum. Une fois utilisée, cette "
            "aptitude ne peut plus l'être avant la fin d'un repos long."
        ),
    },
    "Magie des ombres": {
        "Yeux de ténèbres & Force de la tombe": (
            "Yeux de ténèbres : vous obtenez la vision dans le noir sur 36 m. Au niveau 3, vous apprenez le sort "
            "Ténèbres (sans qu'il compte dans vos sorts connus) ; vous pouvez le lancer avec un emplacement ou en "
            "dépensant 2 points de sorcellerie, et dans ce dernier cas vous voyez à travers ces ténèbres. Force de la "
            "tombe : lorsque des dégâts vous font tomber à 0 point de vie, sauf s'il s'agit de dégâts radiants ou d'un "
            "coup critique, vous pouvez faire un jet de sauvegarde de Charisme (DD 5 + les dégâts subis) ; en cas de "
            "réussite, vous tombez à 1 point de vie à la place. Une fois par repos long."
        ),
        "Chien de mauvais augure": (
            "Au niveau 6, par une action bonus, vous dépensez 3 points de sorcellerie et désignez une créature visible "
            "à 36 m ou moins. Un loup sanguinaire d'ombre apparaît dans un espace libre à 9 m ou moins d'elle ; il a "
            "des points de vie temporaires égaux à la moitié de votre niveau d'ensorceleur, agit à votre tour, ne se "
            "déplace que vers la cible et ne peut attaquer qu'elle. Il traverse créatures et objets comme un terrain "
            "difficile et subit 5 dégâts de force s'il finit son tour dans un objet. Tant qu'il est à 1,50 m ou moins "
            "de la cible, celle-ci a un désavantage à ses jets de sauvegarde contre vos sorts. Il disparaît au bout de "
            "5 minutes, à 0 point de vie, si la cible tombe à 0 point de vie, ou par une action bonus."
        ),
        "Traverser les ombres": (
            "Au niveau 14, lorsque vous vous trouvez dans une zone de lumière faible ou d'obscurité, vous pouvez par "
            "une action bonus vous téléporter jusqu'à 36 m vers un espace libre que vous voyez et qui est lui aussi "
            "dans une lumière faible ou dans l'obscurité. Aucune limite d'utilisation hormis votre action bonus."
        ),
        "Forme d'ombre": (
            "Au niveau 18, par une action bonus, vous dépensez 6 points de sorcellerie pour prendre une forme "
            "d'ombre pendant 1 minute. Vous obtenez la résistance à tous les dégâts sauf de force et radiants, et vous "
            "pouvez traverser créatures et objets comme un terrain difficile ; vous subissez 5 dégâts de force si vous "
            "terminez votre tour dans un objet. La forme prend fin si vous êtes neutralisé, si vous mourez ou si vous "
            "la congédiez par une action bonus."
        ),
    },
    "Sorcellerie des tempêtes": {
        "Langage du vent & Magie tumultueuse": (
            "Langage du vent : vous parlez, lisez et écrivez le primordial, ce qui vous permet aussi de comprendre "
            "ses dialectes (aquatique, aérien, igné et terreux) et d'être compris de leurs locuteurs. Magie "
            "tumultueuse : juste avant ou juste après avoir lancé un sort de niveau 1 ou supérieur, vous pouvez par "
            "une action bonus voler sur 3 m au maximum sans provoquer d'attaque d'opportunité."
        ),
        "Cœur de la tempête & Guide des tempêtes": (
            "Cœur de la tempête : vous avez la résistance aux dégâts de foudre et de tonnerre. Quand vous commencez à "
            "lancer un sort de niveau 1 ou supérieur qui inflige des dégâts de foudre ou de tonnerre, les créatures de "
            "votre choix situées à 3 m ou moins de vous subissent des dégâts de foudre ou de tonnerre (au choix) égaux "
            "à la moitié de votre niveau d'ensorceleur. Guide des tempêtes : s'il pleut, par une action, vous empêchez "
            "la pluie de tomber dans une sphère de 6 m de rayon centrée sur vous (jusqu'à ce que vous y mettiez fin "
            "par une action bonus) ; s'il y a du vent, par une action bonus à chaque round, vous choisissez la "
            "direction du vent dans un rayon de 30 m autour de vous jusqu'à la fin de votre tour suivant."
        ),
        "Fureur de la tempête": (
            "Au niveau 14, lorsqu'une créature vous touche avec une attaque au corps à corps, vous pouvez utiliser "
            "votre réaction pour lui infliger des dégâts de foudre égaux à votre niveau d'ensorceleur. Elle doit "
            "aussi réussir un jet de sauvegarde de Force (DD = 8 + votre bonus de maîtrise + votre modificateur de "
            "Charisme) ou être repoussée en ligne droite jusqu'à 6 m de vous."
        ),
        "Âme du vent": (
            "Au niveau 18, vous obtenez l'immunité contre les dégâts de foudre et de tonnerre, ainsi qu'une vitesse "
            "de vol magique de 18 m. Par une action, vous pouvez réduire cette vitesse à 9 m pendant 1 heure et "
            "choisir un nombre de créatures égal à 3 + votre modificateur de Charisme situées à 9 m ou moins : elles "
            "gagnent une vitesse de vol de 9 m pendant 1 heure. Cette action se récupère après un repos court ou long."
        ),
    },
    "Esprit aberrant": {
        "Discours télépathique & Sorts psioniques": (
            "Sorts psioniques : vous apprenez des sorts toujours connus qui ne comptent pas dans vos sorts connus — "
            "niveau 1 : Tentacules de Hadar, Murmures dissonants et le tour de magie Piqûre mentale ; niveau 3 : "
            "Apaisement des émotions, Détection des pensées ; niveau 5 : Voracité de Hadar, Communication à distance ; "
            "niveau 7 : Tentacules noirs d'Evard, Convocation d'aberration ; niveau 9 : Lien télépathique de Rary, "
            "Télékinésie. "
            "Chacun peut être échangé contre un sort de divination ou d'enchantement du même niveau. Discours "
            "télépathique : par une action bonus, vous liez votre esprit à une créature visible à 9 m ou moins ; vous "
            "pouvez communiquer par télépathie tant que vous êtes à une distance (en km) inférieure à 1,5 × votre "
            "modificateur de Charisme (minimum 1,5 km), pendant un nombre de minutes égal à votre niveau d'ensorceleur."
        ),
        "Sorcellerie psionique & Défenses psychiques": (
            "Sorcellerie psionique : au niveau 6, quand vous lancez un de vos sorts psioniques de niveau 1 ou supérieur, vous pouvez dépenser "
            "un nombre de points de sorcellerie égal au niveau du sort au lieu d'un emplacement ; le sort est alors "
            "lancé sans composantes verbales ni somatiques, ni composantes matérielles sauf si elles sont consommées "
            "ou ont un coût. Défenses psychiques : vous avez la résistance aux dégâts psychiques et un avantage aux "
            "jets de sauvegarde contre les états charmé et effrayé."
        ),
        "Révélation incarnée": (
            "Au niveau 14, par une action bonus, vous dépensez 1 point de sorcellerie ou plus ; pour chaque point, "
            "vous obtenez un des avantages suivants pendant 10 minutes : voir les créatures invisibles à 18 m ou moins ; "
            "une vitesse de vol égale à votre vitesse au sol avec vol stationnaire ; une vitesse de nage égale au "
            "double de votre vitesse au sol et la respiration aquatique ; la capacité de vous faufiler par un espace "
            "de 2,5 cm sans vous serrer et de dépenser 1,50 m de déplacement pour échapper à une entrave non magique "
            "ou à une empoignade."
        ),
        "Distorsion implosive": (
            "Au niveau 18, par une action, vous vous téléportez dans un espace libre visible à 36 m ou moins. Chaque "
            "créature à 9 m ou moins de l'espace que vous quittez fait un jet de sauvegarde de Force (DD = 8 + votre "
            "bonus de maîtrise + votre modificateur de Charisme) : en cas d'échec, elle subit 3d10 dégâts de force et "
            "est attirée vers cet espace aussi près que possible ; en cas de réussite, demi-dégâts seulement. Une fois "
            "par repos long, ou en dépensant 5 points de sorcellerie."
        ),
    },
    "Âme mécanique": {
        "Magie mécanique & Rétablir l'équilibre": (
            "Magie mécanique : vous apprenez des sorts toujours connus — niveau 1 : Alarme, Protection contre le mal "
            "et le bien ; niveau 3 : Aide, Restauration partielle ; niveau 5 : Dissipation de la magie, Protection "
            "contre une énergie ; niveau 7 : Liberté de mouvement, Convocation d'artificiel ; niveau 9 : Mur "
            "de force, Restauration supérieure (échangeables contre un sort d'abjuration ou de transmutation du même "
            "niveau). Rétablir l'équilibre : quand une créature visible à 18 m ou moins va lancer un d20 avec avantage "
            "ou désavantage, vous pouvez utiliser votre réaction pour l'en empêcher. Utilisable un nombre de fois égal "
            "à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Bastion de la loi": (
            "Au niveau 6, par une action, vous dépensez de 1 à 5 points de sorcellerie pour protéger vous-même ou une "
            "créature visible à 9 m ou moins. La protection compte autant de d8 que de points dépensés ; quand la "
            "créature subit des dégâts, elle peut dépenser un nombre quelconque de ces dés, les lancer et réduire les "
            "dégâts du total. La protection dure jusqu'à votre prochain repos long ou jusqu'à ce que vous réutilisiez "
            "cette aptitude."
        ),
        "Transe d'ordre": (
            "Au niveau 14, par une action bonus, vous entrez dans une transe ordonnée pendant 1 "
            "minute : les jets d'attaque contre vous ne peuvent pas bénéficier d'un avantage, et chaque fois que vous "
            "faites un jet d'attaque, un test de caractéristique ou un jet de sauvegarde, vous pouvez traiter un "
            "résultat de 9 ou moins au d20 comme un 10. Une fois par repos long, ou en dépensant 5 points de "
            "sorcellerie."
        ),
        "Cavalcade mécanique": (
            "Au niveau 18, par une action, vous invoquez des esprits d'ordre dans un cube de 9 m "
            "d'arête partant de vous. Ils rendent jusqu'à 100 points de vie, répartis comme vous le souhaitez entre "
            "les créatures du cube, réparent entièrement les objets endommagés qui s'y trouvent, et mettent fin à tous "
            "les sorts de niveau 6 ou inférieur affectant les créatures et objets de votre choix dans la zone. Une fois "
            "par repos long, ou en dépensant 7 points de sorcellerie."
        ),
    },
    "Lignée du Sang": {
        "Magie d'hématologie & Sacrifice vital": (
            "Vous gagnez la maîtrise de la compétence Médecine et apprenez les sorts de votre lignée, toujours connus. "
            "Sacrifice vital (à partir du niveau 2) : une fois par tour, par une action bonus, vous pouvez dépenser un "
            "de vos dés de vie sans le lancer pour regagner 1 point de sorcellerie ; vous subissez alors 1d6 dégâts "
            "nécrotiques qui ne peuvent être réduits d'aucune façon. Vous pouvez le faire un nombre de fois égal à "
            "votre bonus de maîtrise, récupérées après un repos long, sans dépasser votre maximum de points."
        ),
        "Métamagie sanguine": (
            "Au niveau 6, lorsque vous appliquez une option de Métamagie, vous pouvez payer tout ou partie de son "
            "coût (2 points au maximum) avec votre sang : pour chaque point ainsi évité, vous subissez 1d6 dégâts "
            "nécrotiques qui ne peuvent être réduits, et ces dégâts ne peuvent pas provoquer de jet de concentration. "
            "Utilisable un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Ébullition magique": (
            "Au niveau 14, une fois par tour, quand un de vos sorts inflige des dégâts à une créature qui n'est pas à "
            "son maximum de points de vie, elle doit réussir un jet de sauvegarde de Constitution (DD = 8 + votre bonus "
            "de maîtrise + votre modificateur de Charisme) ou se mettre à saigner pendant 1 minute : au début de chacun "
            "de ses tours, elle subit 2d6 dégâts nécrotiques, puis peut refaire le jet à la fin de son tour pour y "
            "mettre fin. Une seule créature peut saigner ainsi à la fois ; les morts-vivants et créatures artificielles "
            "sont immunisés."
        ),
        "Souverain du sang": (
            "Au niveau 18, par une action, vous prenez le contrôle du sang d'une créature vivante visible à 18 m ou "
            "moins (pas un mort-vivant ni une créature artificielle). Elle fait un jet de sauvegarde de Constitution "
            "(DD = 8 + votre bonus de maîtrise + votre modificateur de Charisme) ; en cas d'échec, elle est paralysée "
            "ou, au choix, vous obéit : à chacun de vos tours, par une action bonus, vous la faites se déplacer de sa "
            "vitesse et effectuer une attaque contre une cible de votre choix. L'effet dure 1 minute (concentration) ; "
            "elle refait le jet à la fin de chacun de ses tours. Une fois par repos long, ou en dépensant 7 points de "
            "sorcellerie."
        ),
    },
    "Magie Cosmique": {
        "Alignement astronomique": (
            "Vous apprenez les sorts de votre lignée, toujours connus. À la fin d'un repos long, choisissez une phase "
            "active jusqu'au repos long suivant. Solaire : vous connaissez le tour de magie Lumière et, une fois par "
            "tour, un sort infligeant des dégâts de feu ou radiants inflige 1d4 dégâts supplémentaires du même type à "
            "une cible. Lunaire : quand vous lancez un sort de niveau 1 ou supérieur, une créature de votre choix à 9 m "
            "ou moins gagne 1d4 + le niveau du sort points de vie temporaires. Vide : juste après avoir lancé un sort "
            "de niveau 1 ou supérieur, vous pouvez par une action bonus vous téléporter de 3 m vers un espace libre "
            "visible."
        ),
        "Saut stellaire": (
            "Au niveau 6, par une action bonus, vous dépensez 2 points de sorcellerie pour changer de phase "
            "astronomique. Une onde cosmique jaillit alors de vous : chaque créature de votre choix à 3 m ou moins "
            "fait un jet de sauvegarde de Dextérité (DD = 8 + votre bonus de maîtrise + votre modificateur de "
            "Charisme) et subit 2d8 dégâts de force en cas d'échec, ou la moitié en cas de réussite."
        ),
        "Gravité déformée": (
            "Au niveau 14, par une action, vous déformez la gravité dans une sphère de 6 m de rayon centrée sur vous "
            "et qui se déplace avec vous, pendant 1 minute (concentration). Les créatures hostiles traitent la zone "
            "comme un terrain difficile, et les attaques à distance avec une arme contre vous ou vos alliés situés "
            "dans la sphère ont un désavantage. Une fois par repos long, ou en dépensant 3 points de sorcellerie."
        ),
        "Supernova": (
            "Au niveau 18, par une action, vous dépensez 5 points de sorcellerie pour faire exploser une étoile "
            "miniature en un point visible à 36 m ou moins (sphère de 6 m de rayon). Les ennemis dans la zone font un "
            "jet de sauvegarde de Constitution (DD = 8 + votre bonus de maîtrise + votre modificateur de Charisme) : "
            "échec, 8d6 dégâts radiants ou de force (au choix) et aveuglés jusqu'à la fin de votre prochain tour ; "
            "réussite, moitié des dégâts seulement. Vos alliés dans la zone ne subissent rien et regagnent 2d8 + votre "
            "modificateur de Charisme points de vie. Une fois par repos long."
        ),
    },
}

CORRIGE = [
    ("majeur", "Capacités de classe optionnelles (TCE)", "Guidage magique absent",
     "Niveau 5 : si vous ratez un test de caractéristique, 1 point de sorcellerie pour relancer le d20 (nouveau résultat obligatoire)"),
    ("mineur", "Métamagie", "Options de Tasha (Sort chercheur, Sort transmuté) non mentionnées",
     "TCE ajoute Sort chercheur (2 points) et Sort transmuté (1 point)"),
    ("info", "Capacités de classe optionnelles (TCE)", "Sorts supplémentaires de la liste d'ensorceleur de Tasha non signalés",
     "TCE étend la liste de sorts d'ensorceleur (ex. Bouclier de feu, Lame aux flammes vertes…)"),
    ("mineur", "Versatilité magique (Optionnel - TCE)", "Obtenue au niveau 5 et permettant de changer un sort connu",
     "Niveau 4 : à chaque niveau d'Amélioration de caractéristiques, remplace une option de Métamagie ou un tour de magie"),
    ("mineur", "Source de magie", "Pas de table de coût de l'Incantation flexible ni d'action bonus",
     "Action bonus ; emplacement de niveau 1/2/3/4/5 = 2/3/5/6/7 points, niveau 5 maximum ; points = niveau d'ensorceleur"),
    ("mineur", "Lignée draconique / Ancêtre dragon & Résilience draconique", "Table des ancêtres et types de dégâts absente",
     "10 dragons : noir/cuivre acide, bleu/bronze foudre, airain/or/rouge feu, vert poison, argent/blanc froid"),
    ("mineur", "Lignée draconique / Ailes draconiques", "Vitesse de vol et durée non précisées",
     "Vitesse de vol = vitesse actuelle, jusqu'à congédiement (action bonus), incompatible avec une armure non adaptée"),
    ("mineur", "Lignée draconique / Présence draconique", "Action et concentration non mentionnées ; immunité 24 h absente",
     "Action, 5 points, aura 18 m, 1 min avec concentration ; réussite = immunité 24 h"),
    ("mineur", "Magie sauvage / Pic de magie sauvage & Marée du chaos", "« 1 fois/tour jet de 1d20 »",
     "Le d20 est lancé, à la discrétion du MD, après un sort d'ensorceleur de niveau 1+ ; table Excès sur un 1"),
    ("mineur", "Magie sauvage / Comme par hasard", "Réaction non mentionnée", "Réaction, 2 points, 1d4 après le jet"),
    ("majeur", "Âme divine / sorts_domaine", "Liste de 10 sorts de domaine inventée",
     "Aucune liste étendue : un seul sort d'affinité (Soins, Blessure, Bénédiction, Fléau ou Protection contre le mal et le bien) + accès à la liste de clerc"),
    ("mineur", "Âme divine / Magie divine & Favori des dieux", "Affinité et sort associé non décrits ; récupération « 1/repos » imprécise",
     "Choix d'affinité ; Favori des dieux 2d4, 1 fois par repos court ou long"),
    ("mineur", "Âme divine / Ailes d'outre-monde", "Vitesse de vol non précisée", "Vitesse de vol de 9 m"),
    ("mineur", "Âme divine / Rétablissement céleste", "Action bonus non mentionnée", "Action bonus, sous la moitié des PV max"),
    ("majeur", "Magie des ombres / sorts_domaine", "Liste de 10 sorts inventée",
     "Magie des ombres (XGE) n'a pas de liste de sorts étendue (seulement Ténèbres)"),
    ("mineur", "Magie des ombres / Yeux de ténèbres & Force de la tombe", "Ténèbres appris au niveau 1 ; exceptions radiant/critique absentes",
     "Ténèbres au niveau 3 ; Force de la tombe sans effet contre dégâts radiants ou coup critique"),
    ("majeur", "Magie des ombres / Chien de mauvais augure", "Coût en points absent et 10 PV temporaires fixes",
     "Action bonus, 3 points ; PV temporaires = moitié du niveau d'ensorceleur ; désavantage aux JS contre vos sorts"),
    ("mineur", "Magie des ombres / Chien de mauvais augure", "« inflige -5 PV si fin de tour dedans » ambigu",
     "Le chien subit 5 dégâts de force s'il finit son tour dans un objet"),
    ("majeur", "Sorcellerie des tempêtes / sorts_domaine", "Liste de 10 sorts inventée",
     "Sorcellerie des tempêtes (XGE) n'a pas de liste de sorts étendue"),
    ("mineur", "Sorcellerie des tempêtes / sorts_domaine", "Nom anglais/mixte « Tempête de sleet »",
     "Nom français : Tempête de neige (Sleet Storm)"),
    ("mineur", "Sorcellerie des tempêtes / Langage du vent & Magie tumultueuse", "Dialectes du primordial non mentionnés",
     "Compréhension de l'aquatique, de l'aérien, de l'igné et du terreux"),
    ("majeur", "Sorcellerie des tempêtes / Cœur de la tempête & Guide des tempêtes", "Dégâts fixes de 10",
     "Dégâts = moitié du niveau d'ensorceleur"),
    ("majeur", "Sorcellerie des tempêtes / Fureur de la tempête", "Dégâts fixes de 20 et DD non précisé",
     "Dégâts de foudre = niveau d'ensorceleur ; JS Force contre DD des sorts"),
    ("majeur", "Sorcellerie des tempêtes / Âme du vent", "3 créatures fixes ; vitesse de vol personnelle non précisée",
     "Vol 18 m ; 3 + modificateur de Charisme créatures à 9 m, vol 9 m pendant 1 h ; 1 fois par repos court ou long"),
    ("majeur", "Esprit aberrant / sorts_domaine", "Noms faux/inexistants (Désorientation, Armure de mage, Calme des émotions, Tentacules de noirs éboulis, Invocation de béhémoth, Télépathie, Moisson d'esprit)",
     "Bras d'Hadar, Murmures dissonants, Éclat mental ; Apaisement des émotions, Détection des pensées ; Faim d'Hadar, Communication à distance ; Tentacules noirs d'Evard, Invocation d'aberration ; Lien télépathique de Rary, Télékinésie"),
    ("mineur", "Esprit aberrant / Discours télépathique & Sorts psioniques", "Distance 1,5 km et durée 20 min fixes",
     "Distance = modificateur de Charisme en miles (×1,5 km) ; durée = niveau d'ensorceleur en minutes"),
    ("mineur", "Esprit aberrant / Distortion implosive", "Faute de frappe « Distortion » ; DD et attraction absents",
     "Distorsion implosive : JS Force contre DD des sorts, 3d10 force + attraction, moitié si réussite"),
    ("majeur", "Âme mécanique / sorts_domaine", "Liste fausse (Compréhension des langues, Zone de vérité, Œil mystique, Bannissement, Création)",
     "Alarme, Protection contre le mal et le bien ; Aide, Restauration partielle ; Dissipation de la magie, Protection contre l'énergie ; Liberté de mouvement, Invocation de créature artificielle ; Mur de force, Restauration supérieure"),
    ("majeur", "Âme mécanique / Équilibre restauré & Sorts d'ordre", "6 utilisations fixes, portée absente",
     "Rétablir l'équilibre : utilisations = bonus de maîtrise par repos long, portée 18 m"),
    ("mineur", "Âme mécanique / Bastion de loi", "Nom", "Bastion de la loi"),
    ("mineur", "Âme mécanique / Transe harmonique", "Nom et seuil « inférieur à 9 »",
     "Transe d'ordre : un résultat de 9 ou moins compte comme 10"),
    ("mineur", "Âme mécanique / Chevauchée méca.", "Nom abrégé", "Cavalcade mécanique"),
    ("mineur", "Lignée du Sang / sorts_domaine", "Noms invalides : « Vampirisme »",
     "Nom français : Caresse du vampire ; niveaux incohérents (Fléau de niveau 1, Domination de monstre de niveau 8 en fin de liste)"),
    ("mineur", "Magie Cosmique / sorts_domaine", "Noms invalides : « Lueur féérique », « Colonne de feu »",
     "Noms français : Lueur féerique, Colonne de flamme"),
    ("mineur", "Esprit aberrant / Magie psionique & Défense psychique", "Noms non officiels",
     "Sorcellerie psionique (niveau 6) et Défenses psychiques"),
    ("mineur", "Âme mécanique / Équilibre restauré & Sorts d'ordre", "Noms non officiels",
     "Magie mécanique (sorts toujours connus) et Rétablir l'équilibre (réaction)"),
    ("mineur", "Métamagie supplémentaire (niveau 17)", "Texte inventé (combinaisons libres avec la création d'emplacements)",
     "Niveau 17 : une option de Métamagie de plus, mêmes règles (une option par sort sauf Sort renforcé/chercheur)"),
]

AUDIT = [
    ("info", "Magie sauvage / noms d'aptitudes", "Pic de magie sauvage, Comme par hasard et Torrent arcanique diffèrent "
     "des noms habituels de la VF (Montée de magie sauvage, Plier la chance, Bombardement de sorts) : non renommés, "
     "traduction officielle non vérifiable ici, règles décrites exactes",
     "Wild Magic Surge, Tides of Chaos, Bend Luck, Controlled Chaos, Spell Bombardment"),
    ("info", "Lignée draconique / Ailes draconiques", "Nom VF habituel « Ailes de dragon » : non renommé (même incertitude), "
     "règle décrite exacte", "Dragon Wings (niveau 14)"),
    ("info", "Aptitudes fusionnées (ex. Ancêtre dragon & Résilience draconique)", "Deux aptitudes officielles du même "
     "niveau regroupées en une seule entrée : non scindées pour ne pas casser les fiches existantes",
     "Les aptitudes sont distinctes dans les livres mais de même niveau"),
]
