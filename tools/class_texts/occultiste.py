"""Descriptions enrichies — Occultiste (PHB, Xanathar, Tasha ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Occultiste"

BASE = {
    "Protecteur d'outre-monde": (
        "Au niveau 1, vous concluez un marché avec une entité d'outre-monde qui devient votre patron : l'Archifée, le "
        "Fiélon, le Grand Ancien (PHB), le Céleste, la Lame maudite (XGE), le Génie, l'Insondable (TCE), ou un patron "
        "communautaire. Ce choix vous accorde des aptitudes aux niveaux 1, 6, 10 et 14, ainsi qu'une liste de sorts "
        "étendue : ces sorts (deux par niveau de sort, du 1er au 5e) s'ajoutent à la liste de sorts d'occultiste pour "
        "vous, sans être connus d'office ; vous pouvez les choisir lorsque vous apprenez un nouveau sort."
    ),
    "Magie des pactes": (
        "Vous lancez vos sorts grâce au Charisme. DD de sauvegarde des sorts = 8 + votre bonus de maîtrise + votre "
        "modificateur de Charisme ; modificateur d'attaque des sorts = votre bonus de maîtrise + votre modificateur de "
        "Charisme. Vous pouvez utiliser un focaliseur arcanique. Sorts mineurs connus : 2 (3 au niveau 4, 4 au niveau "
        "10). Sorts connus : 2 au niveau 1, puis +1 par niveau jusqu'à 10 au niveau 9, 11 au niveau 11, 12 au niveau "
        "13, 13 au niveau 15, 14 au niveau 17 et 15 au niveau 19 ; à chaque niveau gagné, vous pouvez remplacer un "
        "sort connu par un autre de la liste. Particularité : tous vos emplacements de sorts sont du même niveau et "
        "sont récupérés à la fin de chaque repos court ou long. Emplacements : 1 (niveau 1), 2 (niveau 2), 3 (niveau "
        "11), 4 (niveau 17). Niveau des emplacements : 1er (niveaux 1-2), 2e (3-4), 3e (5-6), 4e (7-8), 5e (niveau 9 "
        "et au-delà) ; le 5e niveau est le maximum de la Magie des pactes."
    ),
    "Invocations occultes": (
        "Au niveau 2, vous apprenez deux manifestations occultes (invocations occultes) de votre choix : fragments de "
        "savoir interdit qui renforcent la Décharge occulte (Décharge déchirante : + votre modificateur de Charisme "
        "aux dégâts de chaque rayon ; Décharge répulsive : repousse de 3 m), donnent des sorts utilisables à volonté "
        "ou une fois par repos, ou des capacités permanentes (Vision du diable : voir dans les ténèbres magiques à "
        "36 m). Certaines exigent un niveau minimal dans la classe, un pacte ou un sort précis. Nombre connu : 2, puis 3 "
        "au niveau 5, 4 au niveau 7, 5 au niveau 9, 6 au niveau 12, 7 au niveau 15 et 8 au niveau 18. À chaque "
        "niveau gagné dans cette classe, vous pouvez en remplacer une par une autre dont vous remplissez les conditions."
    ),
    "Pacte divin": (
        "Au niveau 3, votre patron vous accorde une faveur de pacte. Pacte de la Lame : par une action, vous créez une "
        "arme de pacte de corps à corps de la forme de votre choix dans votre main ; vous la maîtrisez, elle est "
        "magique et disparaît si elle reste plus d'une minute à plus de 1,50 m de vous (un rituel d'une heure permet "
        "de lier une arme magique). Pacte de la Chaîne : vous apprenez Appel de familier (rituel) avec des formes "
        "spéciales (diablotin, pseudodragon, quasit, esprit follet) et pouvez renoncer à une de vos attaques pour que "
        "le familier attaque par sa réaction. Pacte du Grimoire : vous recevez un Livre des ombres contenant trois sorts "
        "mineurs de n'importe quelles listes, lançables à volonté tant que vous l'avez sur vous. Pacte du Talisman "
        "(Tasha) : son porteur peut ajouter 1d4 à un test de caractéristique raté, un nombre de fois égal à votre "
        "bonus de maîtrise par repos long."
    ),
    "Polyvalence occulte (option Tasha)": (
        "Option de Tasha. Chaque fois que vous atteignez dans cette classe un niveau qui vous octroie l'aptitude "
        "Amélioration de caractéristique (niveaux 4, 8, 12, 16 et 19), vous pouvez effectuer un de ces changements : "
        "remplacer un sort mineur d'occultiste connu par un autre de la liste d'occultiste ; remplacer l'option de "
        "Pacte divin choisie au niveau 3 par une autre option de pacte (Pacte de la Chaîne, de la Lame, du Grimoire "
        "ou du Talisman) ; ou, à partir du niveau 12, remplacer le sort d'un de vos Arcanums mystiques par un autre "
        "sort d'occultiste du même niveau. Si ce changement vous fait perdre les prérequis d'une manifestation "
        "occulte, vous devez aussi remplacer cette manifestation par une autre dont vous remplissez les conditions."
    ),
    "Arcanum mystique (6e niveau)": (
        "Au niveau 11, votre patron vous confie un secret : choisissez un sort de 6e niveau de la liste d'occultiste. "
        "Vous pouvez le lancer une fois sans dépenser d'emplacement ; il faut terminer un repos long pour recommencer. "
        "Il ne peut pas être lancé à un niveau supérieur et ne profite pas de vos emplacements de Magie des pactes. "
        "Vous obtenez d'autres arcanums aux niveaux 13 (7e), 15 (8e) et 17 (9e)."
    ),
    "Arcanum mystique (7e niveau)": (
        "Au niveau 13, vous choisissez un sort de 7e niveau de la liste d'occultiste comme arcanum. Vous pouvez le "
        "lancer une fois sans emplacement de sort et récupérez cette utilisation à la fin d'un repos long. Comme pour "
        "les autres arcanums, le sort est lancé à son niveau de base uniquement."
    ),
    "Arcanum mystique (8e niveau)": (
        "Au niveau 15, vous choisissez un sort de 8e niveau de la liste d'occultiste comme arcanum. Vous pouvez le "
        "lancer une fois sans emplacement de sort et récupérez cette utilisation à la fin d'un repos long. Le sort est "
        "lancé à son niveau de base uniquement."
    ),
    "Arcanum mystique (9e niveau)": (
        "Au niveau 17, vous choisissez un sort de 9e niveau de la liste d'occultiste comme arcanum (Prémonition, "
        "Emprisonnement, Mot de pouvoir mortel, Projection astrale, Portail, Métamorphose suprême…). Vous pouvez le "
        "lancer une fois sans emplacement de sort et récupérez cette utilisation à la fin d'un repos long."
    ),
    "Maître de l'occulte": (
        "Au niveau 20, vous pouvez puiser dans votre réserve intérieure de puissance mystique "
        "en implorant votre patron pendant 1 minute : vous récupérez tous les emplacements de Magie des pactes que "
        "vous avez dépensés. Une fois utilisée, cette aptitude n'est de nouveau disponible qu'après un repos long. "
        "Les arcanums mystiques ne sont pas concernés."
    ),
}


def _genie(kind: str, element: str, damage: str) -> dict:
    """Textes communs aux quatre variantes du Génie (TCE)."""
    return {
        f"Vaisseau du Génie & Conduit du génie ({element})": (
            f"Votre patron ({kind}) vous remet un vaisseau magique de taille Très petite (lampe, anneau, flacon…) "
            "qui vous sert de focaliseur d'incantation. Sa CA est égale à 8 + votre bonus de maîtrise + votre "
            "modificateur de Charisme, ses points de vie égaux à votre niveau d'occultiste + votre bonus de maîtrise, "
            "et il est immunisé contre les dégâts de poison et psychiques. Refuge en bouteille : par une action, vous "
            "disparaissez à l'intérieur (pièce cylindrique de 6 m de rayon et 6 m de haut) pendant au maximum "
            "2 × votre bonus de maîtrise heures ; vous en sortez par une action bonus. Une fois par repos long. "
            f"Courroux du génie : une fois à chacun de vos tours, lorsque vous touchez avec un jet d'attaque, la cible "
            f"subit des dégâts {damage} supplémentaires égaux à votre bonus de maîtrise. Votre liste de sorts "
            "étendue comprend aussi les sorts communs à tous les génies (Détection du mal et du bien, Force "
            "fantasmagorique, Création de nourriture et d'eau, Assassin imaginaire, Création), et Souhait s'y ajoute "
            "comme choix possible pour l'Arcanum mystique de 9e niveau."
        ),
        f"Présent élémentaire ({element})": (
            f"Au niveau 6, vous obtenez la résistance aux dégâts {damage}. De plus, par une action bonus, vous gagnez "
            "une vitesse de vol de 9 m pendant 10 minutes, avec la possibilité de faire du surplace. Vous pouvez "
            "utiliser ce vol un nombre de fois égal à votre bonus de maîtrise, et récupérez toutes les utilisations à "
            "la fin d'un repos long."
        ),
        "Sanctuaire du Vaisseau": (
            "Au niveau 10, quand vous entrez dans votre vaisseau via Refuge en bouteille, vous pouvez y emmener "
            "jusqu'à cinq créatures consentantes situées dans un rayon de 9 m (choix au moment de l'action). Par une "
            "action bonus, vous pouvez expulser n'importe quelle créature présente ; tout le monde ressort si vous "
            "quittez le vaisseau. Un repos court pris à l'intérieur ne dure que 10 minutes, et chaque créature qui "
            "le termine ajoute votre bonus de maîtrise aux points de vie récupérés par ses dés de vie."
        ),
        "Souhait limité": (
            "Au niveau 14, par une action, vous pouvez demander à votre patron de produire l'effet d'un sort de 6e "
            "niveau ou moins dont le temps d'incantation est d'une action, issu de n'importe quelle liste de classe. "
            "Le sort ne requiert aucune composante et ne dépense aucun emplacement. Après utilisation, vous devez "
            "terminer 1d4 repos longs avant de pouvoir recommencer."
        ),
    }


SUB = {
    "L'Archifée": {
        "Présence féerique": (
            "Par une action, vous dégagez une aura de charme ou d'effroi : chaque créature dans un cube de 3 m "
            "d'arête partant de vous doit réussir un jet de sauvegarde de Sagesse (DD = 8 + votre bonus de maîtrise "
            "+ votre modificateur de Charisme) ou être charmée ou effrayée par vous (au choix) jusqu'à la fin de "
            "votre prochain tour. Une fois utilisée, l'aptitude se recharge à la fin d'un repos court ou long."
        ),
        "Échappatoire brumeuse": (
            "Au niveau 6, lorsque vous subissez des dégâts, vous pouvez utiliser votre réaction pour devenir "
            "invisible et vous téléporter jusqu'à 18 m vers un espace inoccupé que vous voyez. L'invisibilité dure "
            "jusqu'au début de votre prochain tour, ou jusqu'à ce que vous attaquiez ou lanciez un sort. Une fois "
            "par repos court ou long."
        ),
        "Charmantes défenses": (
            "Au niveau 10, vous êtes immunisé contre l'état charmé. Lorsqu'une autre créature tente de vous charmer, "
            "vous pouvez utiliser votre réaction pour lui renvoyer l'effet : elle doit réussir un jet de sauvegarde "
            "de Sagesse contre votre DD de sauvegarde des sorts ou être charmée par vous pendant 1 minute, ou jusqu'à "
            "ce qu'elle subisse des dégâts."
        ),
        "Sombre délire": (
            "Au niveau 14, par une action, choisissez une créature visible à 18 m ou moins : elle doit réussir un "
            "jet de sauvegarde de Sagesse contre votre DD de sauvegarde des sorts ou être charmée ou effrayée par "
            "vous (au choix) pendant 1 minute, ou jusqu'à ce que votre concentration soit rompue (comme pour un "
            "sort). Elle se croit perdue dans un royaume féerique brumeux et ne perçoit que vous ; l'effet prend fin "
            "si elle subit des dégâts. Une fois par repos court ou long."
        ),
    },
    "Le Fiélon": {
        "Bénédiction du ténébreux": (
            "Chaque fois que vous réduisez une créature hostile à 0 point de vie, vous gagnez un nombre de points de "
            "vie temporaires égal à votre modificateur de Charisme + votre niveau d'occultiste (minimum 1). Aucune "
            "limite d'utilisation ; comme tous les PV temporaires, ils ne se cumulent pas avec d'autres."
        ),
        "Chance du ténébreux": (
            "Au niveau 6, lorsque vous effectuez un test de caractéristique ou un jet de sauvegarde, vous pouvez "
            "ajouter 1d10 au résultat, après avoir vu le jet mais avant que ses effets ne soient appliqués. Une fois "
            "utilisée, l'aptitude se recharge à la fin d'un repos court ou long."
        ),
        "Résistance fiélonne": (
            "Au niveau 10, à la fin de chaque repos court ou long, choisissez un type de dégâts : vous obtenez la "
            "résistance à ce type jusqu'à ce que vous en choisissiez un autre. Les dégâts infligés par des armes "
            "magiques ou en argent ignorent cette résistance."
        ),
        "Traversée des enfers": (
            "Au niveau 14, lorsque vous touchez une créature avec un jet d'attaque, vous pouvez la projeter à travers "
            "les plans inférieurs : elle disparaît et revient à la fin de votre prochain tour à l'emplacement qu'elle "
            "occupait (ou au plus proche espace libre). Si ce n'est pas un fiélon, elle subit alors 10d10 dégâts "
            "psychiques en revenant, traumatisée. Une fois par repos long."
        ),
    },
    "Le Grand Ancien": {
        "Esprit éveillé": (
            "Vous pouvez communiquer par télépathie avec toute créature que vous voyez à 9 m ou moins. Il n'est pas "
            "nécessaire de partager une langue, mais la créature doit comprendre au moins une langue pour saisir vos "
            "pensées. Il s'agit d'une communication à sens unique sauf si la créature répond à voix haute."
        ),
        "Protection entropique": (
            "Au niveau 6, lorsqu'une créature effectue un jet d'attaque contre vous, vous pouvez utiliser votre "
            "réaction pour lui imposer le désavantage. Si l'attaque échoue, votre prochain jet d'attaque contre "
            "cette créature a l'avantage s'il a lieu avant la fin de votre prochain tour. Une fois par repos court ou "
            "long."
        ),
        "Bouclier mental": (
            "Au niveau 10, nul ne peut lire vos pensées par télépathie ou autre moyen sans votre accord. Vous avez "
            "la résistance aux dégâts psychiques, et chaque fois qu'une créature vous inflige des dégâts psychiques, "
            "elle subit la même quantité de dégâts."
        ),
        "Asservissement": (
            "Au niveau 14, par une action, vous touchez un humanoïde neutralisé : il est charmé par vous jusqu'à ce "
            "qu'un sort de Délivrance des malédictions soit lancé sur lui, que l'état charmé lui soit retiré, ou que "
            "vous utilisiez de nouveau cette aptitude. Tant qu'il est sur le même plan que vous, vous pouvez "
            "communiquer télépathiquement avec lui, quelle que soit la distance."
        ),
    },
    "Le Céleste": {
        "Sorts mineurs bonus & Lumière guérisseuse": (
            "Vous apprenez les sorts mineurs Lumière et Flamme sacrée (ils comptent comme sorts d'occultiste sans "
            "entrer dans le total de sorts mineurs connus). Lumière guérisseuse : vous disposez d'une réserve de "
            "d6 dont le nombre est égal à 1 + votre niveau d'occultiste. Par une action bonus, vous soignez une "
            "créature visible à 18 m ou moins en dépensant des dés de la réserve (au maximum un nombre égal à votre "
            "modificateur de Charisme, minimum 1) : elle récupère des points de vie égaux au total obtenu. Les dés "
            "dépensés sont récupérés à la fin d'un repos long."
        ),
        "Âme rayonnante": (
            "Au niveau 6, vous obtenez la résistance aux dégâts radiants. De plus, lorsque vous lancez un sort qui "
            "inflige des dégâts radiants ou de feu, vous ajoutez votre modificateur de Charisme à un jet de dégâts "
            "radiants ou de feu de ce sort contre une de ses cibles."
        ),
        "Persévérance céleste": (
            "Au niveau 10, à la fin de chaque repos court ou long, vous gagnez des points de vie temporaires égaux à "
            "votre niveau d'occultiste + votre modificateur de Charisme. Choisissez en outre jusqu'à cinq créatures "
            "visibles : chacune gagne des PV temporaires égaux à la moitié de votre niveau d'occultiste + votre "
            "modificateur de Charisme."
        ),
        "Vengeance ardente": (
            "Au niveau 14, lorsque vous devez effectuer un jet de sauvegarde contre la mort au début de votre tour, "
            "vous pouvez à la place vous relever dans une explosion de lumière : vous récupérez la moitié de vos "
            "points de vie maximum et vous redressez si vous le souhaitez. Chaque créature de votre choix à 9 m ou "
            "moins subit 2d8 + votre modificateur de Charisme dégâts radiants et est aveuglée jusqu'à la fin du tour "
            "en cours. Une fois par repos long."
        ),
    },
    "La Lame maudite (Magelame)": {
        "Guerrier des maléfices & Malédiction de la Lame": (
            "Guerrier des maléfices : vous maîtrisez les armures intermédiaires, les boucliers et les armes de "
            "guerre. À la fin d'un repos long, touchez une arme que vous maîtrisez et dépourvue de la propriété à "
            "deux mains : vous utilisez votre Charisme au lieu de la Force ou de la Dextérité pour ses jets d'attaque "
            "et de dégâts (s'applique aussi à votre arme de pacte). Malédiction de la Lame : par une action bonus, "
            "maudissez une créature visible à 9 m ou moins pendant 1 minute. Vous gagnez un bonus aux dégâts contre "
            "elle égal à votre bonus de maîtrise, vos attaques contre elle sont critiques sur 19-20, et si elle "
            "meurt vous récupérez des points de vie égaux à votre niveau d'occultiste + votre modificateur de "
            "Charisme (minimum 1). Une fois par repos court ou long."
        ),
        "Spectre maudit": (
            "Au niveau 6, lorsque vous tuez un humanoïde, vous pouvez faire se relever son esprit sous forme de "
            "spectre dans un espace inoccupé à proximité. Il gagne des PV temporaires égaux à la moitié de votre "
            "niveau d'occultiste, obéit à vos ordres verbaux, agit à votre initiative et ajoute votre modificateur "
            "de Charisme (minimum 0) à ses jets d'attaque. Il reste jusqu'à la fin de votre prochain repos long, puis "
            "disparaît. Une fois par repos long."
        ),
        "Armure de maléfices": (
            "Au niveau 10, lorsque la cible de votre Malédiction de la Lame effectue un jet d'attaque contre vous, "
            "vous pouvez utiliser votre réaction pour lancer un d20 : sur un résultat de 4 ou plus, l'attaque échoue, "
            "quel que soit son jet."
        ),
        "Maître des maléfices": (
            "Au niveau 14, lorsque la créature maudite par votre Malédiction de la Lame meurt, vous pouvez appliquer "
            "la malédiction à une autre créature visible à 9 m ou moins, à condition de ne pas être neutralisé. Vous "
            "ne récupérez alors pas les points de vie normalement octroyés par la mort de la première cible. Cela ne "
            "consomme pas d'utilisation de la Malédiction."
        ),
    },
    "Le Génie (Dao - Terre)": _genie("dao", "Terre", "contondants"),
    "Le Génie (Djinn - Air)": _genie("djinn", "Air", "de tonnerre"),
    "Le Génie (Éfrit - Feu)": _genie("éfrit", "Feu", "de feu"),
    "Le Génie (Maride - Eau)": _genie("maride", "Eau", "de froid"),
    "L'Insondable": {
        "Tentacule abyssal & Faveur de la mer": (
            "Faveur de la mer : vous gagnez une vitesse de nage de 12 m et pouvez respirer sous l'eau. Tentacule "
            "abyssal : par une action bonus, vous créez un tentacule spectral de 3 m de long en un point visible à "
            "18 m ou moins, pour 1 minute ou jusqu'à ce que vous en recréiez un. À sa création, vous pouvez faire "
            "une attaque de sort au corps à corps contre une créature à 3 m ou moins de lui : 1d8 dégâts de froid "
            "(2d8 au niveau 10) et vitesse de la cible réduite de 3 m jusqu'au début de votre prochain tour. Par une "
            "action bonus lors des tours suivants, vous pouvez le déplacer de 9 m et répéter l'attaque. Utilisations : "
            "un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Âme océane & Tentacule gardien": (
            "Au niveau 6, vous obtenez la résistance aux dégâts de froid ; lorsque vous et une autre créature êtes "
            "totalement immergés, vous vous comprenez mutuellement quelle que soit la langue. Tentacule gardien : "
            "lorsque vous ou une créature visible subissez des dégâts en étant à 3 m ou moins de votre tentacule, "
            "vous pouvez utiliser votre réaction pour réduire ces dégâts de 1d8 (2d8 au niveau 10)."
        ),
        "Tentacules agrippants": (
            "Au niveau 10, vous apprenez Tentacules noirs d'Evard ; il compte comme sort d'occultiste sans entrer "
            "dans vos sorts connus. Vous pouvez le lancer une fois sans emplacement, récupéré après un repos long. "
            "Chaque fois que vous lancez ce sort, vous gagnez des PV temporaires égaux à votre niveau d'occultiste, "
            "et les dégâts ne peuvent pas rompre votre concentration sur lui."
        ),
        "Plongeon abyssal": (
            "Au niveau 14, par une action, vous vous téléportez avec jusqu'à cinq créatures consentantes visibles à "
            "9 m ou moins. Vous réapparaissez dans des espaces inoccupés à 9 m ou moins d'une étendue d'eau d'au "
            "moins la taille d'un bassin que vous avez déjà vue, située à 1,5 km ou moins. Une fois par repos court "
            "ou long."
        ),
    },
    "Le Moissonneur": {
        "Toucher de la faucheuse": (
            "Vous apprenez le sort mineur Contact glacial s'il ne vous est pas déjà connu (il ne compte pas dans vos "
            "sorts mineurs). Une fois à chacun de vos tours, lorsque vous lancez un sort mineur d'occultiste qui "
            "cible une seule créature et inflige des dégâts nécrotiques, vous pouvez désigner une seconde cible à "
            "portée, située à 1,50 m ou moins de la première ; elle effectue son propre jet ou subit sa propre "
            "attaque. Utilisations : un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Moisson d'âmes": (
            "Au niveau 6, lorsqu'une créature hostile qui n'est ni un artificiel ni un mort-vivant meurt à 9 m ou "
            "moins de vous et que vous la voyez, vous pouvez absorber son essence (aucune action) : vous récupérez un "
            "emplacement de Magie des pactes dépensé. Une fois par repos long. Si vous n'avez aucun emplacement à "
            "récupérer, vous gagnez à la place des PV temporaires égaux à votre niveau d'occultiste."
        ),
        "Marche macabre": (
            "Au niveau 10, vous obtenez la résistance aux dégâts nécrotiques. Par une action bonus, vous devenez "
            "semi-intangible jusqu'à la fin de votre tour : vous pouvez traverser créatures et objets comme un "
            "terrain difficile, avez la résistance aux dégâts contondants, perforants et tranchants, et les attaques "
            "d'opportunité contre vous ont le désavantage. Si vous terminez votre tour dans un objet, vous êtes "
            "expulsé vers l'espace libre le plus proche et subissez 1d10 dégâts de force par tranche de 1,50 m "
            "parcourue. Utilisations : un nombre de fois égal à votre bonus de maîtrise par repos long."
        ),
        "Avatar de la Mort": (
            "Au niveau 14, par une action bonus, vous revêtez une forme spectrale armée d'une faux pendant 1 minute "
            "(pas de concentration) : une aura de 3 m de rayon vous entoure. Les créatures hostiles dans l'aura ne "
            "peuvent pas récupérer de points de vie et leur régénération est suspendue. Une créature hostile qui "
            "commence son tour dans l'aura effectue un jet de sauvegarde de Constitution (DD = 8 + votre bonus de "
            "maîtrise + votre modificateur de Charisme) : 3d8 dégâts nécrotiques en cas d'échec, moitié en cas de "
            "réussite. Vos dégâts nécrotiques ignorent la résistance à ce type. Une fois par repos long."
        ),
    },
    "Le Protecteur astral": {
        "Puits de gravité & Éclat stellaire": (
            "Vous apprenez le sort mineur Illusion mineure (il ne compte pas dans vos sorts mineurs connus). Éclat "
            "stellaire : une fois à chacun de vos tours, lorsque vous infligez des dégâts de force ou radiants à une "
            "créature de taille G ou inférieure avec un sort, vous pouvez la déplacer de 1,50 m horizontalement dans "
            "la direction de votre choix (sans jet de sauvegarde). Ce déplacement se cumule avec celui de la "
            "manifestation Décharge répulsive."
        ),
        "Saut de météore": (
            "Au niveau 6, par une action bonus, vous vous téléportez jusqu'à 9 m vers un espace inoccupé visible. À "
            "votre point de départ éclate une onde de choc : chaque créature de votre choix à 3 m ou moins de ce "
            "point effectue un jet de sauvegarde de Force (DD = 8 + votre bonus de maîtrise + votre modificateur de "
            "Charisme) ; en cas d'échec, elle subit 1d10 dégâts de force et est attirée jusqu'à 3 m vers le point de "
            "départ. Utilisations : un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Voile d'apesanteur": (
            "Au niveau 10, vous ne subissez plus de dégâts de chute et pouvez ralentir votre chute à volonté (comme "
            "Feuille morte). Par une action bonus, vous gagnez une vitesse de vol égale à votre vitesse de marche, "
            "avec la possibilité de faire du surplace, pendant 10 minutes. Une fois par repos court ou long ; vous "
            "pouvez aussi dépenser un emplacement de Magie des pactes pour l'utiliser de nouveau."
        ),
        "Effondrement singulier": (
            "Au niveau 14, par une action, vous créez une singularité en un point visible à 36 m ou moins, qui "
            "persiste jusqu'au début de votre prochain tour. Chaque créature dans une sphère de 6 m de rayon centrée "
            "sur ce point effectue un jet de sauvegarde de Force contre votre DD de sauvegarde des sorts : en cas "
            "d'échec, elle subit 6d10 dégâts de force, est attirée jusqu'à 4,50 m vers le centre et est entravée "
            "jusqu'à la fin de votre prochain tour ; en cas de réussite, elle subit la moitié des dégâts seulement. "
            "Une fois par repos long."
        ),
    },
}

AUDIT = [
    ('info', 'Pacte divin', "Nom non officiel : non renommée (le logiciel s'appuie sur « Pacte divin » pour le choix du pacte)", 'PHB : « Faveur de pacte » (Pact Boon), obtenue au niveau 3'),
    ('info', 'Sous-classes', "Patrons officiels absents : ajout de sous-classes hors du périmètre des corrections (pas d'opération de création)", "L'Immortel (SCAG) et Le Mort-vivant (Van Richten) ne figurent pas dans les données"),
    ('info', 'La Lame maudite (Magelame)', 'Nom de sous-classe erroné (« Magelame » = Bladesinger du magicien) : non renommée pour ne pas casser les fiches existantes', 'XGE : « La Lame maudite » (Hexblade)'),
    ('info', 'Le Génie', 'Sous-classe éclatée en 4 entrées (dao, djinn, éfrit, maride) : non fusionnée pour ne pas casser les fiches existantes', 'TCE : un seul patron, le type de génie étant choisi au niveau 1'),
    ('info', 'Invocations occultes', "Nom non officiel (VF : « Manifestations occultes ») : non renommée, le logiciel gère les manifestations occultes par un panneau dédié indépendant du nom de l'aptitude", 'PHB : « Manifestations occultes » (Eldritch Invocations), niveau 2'),
    ('info', 'Magie des pactes', "Nom légèrement différent de la VF (« Magie de pacte ») : non renommée (nom utilisé par le moteur d'incantation)", 'PHB : « Magie de pacte » (Pact Magic)'),
]

CORRIGE = [
    # Écarts résolus par class_fixes/occultiste.py et par les descriptions enrichies ci-dessus
    ('mineur', 'Maître des arcanes', 'Nom non officiel', "PHB : « Maître de l'occulte » (Eldritch Master), niveau 20, 1 minute, récupère tous les emplacements, 1/repos long"),
    ('mineur', 'Magie des pactes', "Ni nombre d'emplacements, ni niveau, ni sorts connus indiqués", '1 emplacement (niv. 1), 2 (niv. 2), 3 (niv. 11), 4 (niv. 17) ; niveau 1er→5e max (5e au niv. 9) ; récupération repos court'),
    ('mineur', 'Invocations occultes', "Nombre d'invocations connues absent", '2 au niv. 2, 3 au niv. 5, 4 au niv. 7, 5 au niv. 9, 6 au niv. 12, 7 au niv. 15, 8 au niv. 18'),
    ('info', 'Pacte divin', 'Pacte du Talisman (Tasha) mêlé aux pactes du PHB sans mention de source', 'Pacte du Talisman : TCE, +1d4 à un test raté, bonus de maîtrise fois par repos long'),
    ('mineur', 'Capacités de classe optionnelles', 'Option de Tasha absente', "TCE : Polyvalence de l'occultiste (niv. 4, 8, 12, 16, 19 : remplacer un sort mineur, l'arcanum ou la faveur de pacte)"),
    ('majeur', "L'Archifée / Présence féerique", 'Récupération au repos long', "1 fois par repos court ou long ; action, cube de 3 m, JS Sagesse, effet jusqu'à la fin de votre prochain tour"),
    ('majeur', "L'Archifée / Échappatoire brumeuse", 'Récupération au repos long', "1 fois par repos court ou long ; invisible jusqu'au début de votre prochain tour"),
    ('mineur', "L'Archifée / Sombre délire", 'Portée, durée et recharge absentes', 'Action, 18 m, JS Sagesse, charmé ou effrayé 1 minute (concentration), 1/repos court ou long'),
    ('mineur', "L'Archifée / sorts_domaine", 'Noms anglais : « Faerie Fire », « Sleep »', 'Lueurs féeriques, Sommeil'),
    ('majeur', "L'Archifée / sorts_domaine", "Liste fausse : Calme des émotions (nom invalide), Invisibilité, Fléau d'insectes, Porte dimensionnelle, Domination de monstre, Création", 'Lueurs féeriques, Sommeil / Apaisement des émotions, Force fantasmagorique / Clignotement, Croissance végétale / Domination de bête, Invisibilité supérieure / Domination de personne, Apparence trompeuse'),
    ('mineur', 'Le Fiélon / Bénédiction du ténébreux', 'Formule abrégée (« mod. Charisme »)', "PV temporaires = modificateur de Charisme + niveau d'occultiste (minimum 1)"),
    ('majeur', 'Le Fiélon / sorts_domaine', '« Commandement » et « Colonne de feu » invalides ; Forme gazeuse et Immolation hors liste', 'Mains brûlantes, Injonction / Cécité/Surdité, Rayon ardent / Boule de feu, Nuage nauséabond / Bouclier de feu, Mur de feu / Colonne de flamme, Sanctification'),
    ('mineur', 'Le Grand Ancien / Bouclier mental', '« Immunité à la télépathie » imprécis', 'Vos pensées ne peuvent être lues sans votre accord ; résistance psychique ; renvoi des dégâts psychiques'),
    ('mineur', 'Le Grand Ancien / Asservissement', "« Créature » au lieu d'humanoïde", "Toucher (action) un humanoïde neutralisé ; charmé jusqu'à Délivrance des malédictions ou nouvel usage"),
    ('majeur', 'Le Grand Ancien / sorts_domaine', "Noms invalides (Désorientation, Chuchotements dissonants, Force fantasmatique, Rapidité, Tentacules de noirs éboulis, Moisson d'esprit) ; Télépathie (8e) hors liste ; Domination de personne mal placée", "Murmures dissonants, Fou rire de Tasha / Détection des pensées, Force fantasmagorique / Clairvoyance, Communication à distance / Domination de bête, Tentacules noirs d'Evard / Domination de personne, Télékinésie"),
    ('majeur', 'Le Céleste / Lumière guérisseuse', 'Réserve fixe de 20d6 et 1d6 max par utilisation', "Réserve = 1 + niveau d'occultiste d6 ; max par usage = modificateur de Charisme (min 1) ; repos long"),
    ('majeur', 'Le Céleste / Persévérance céleste', 'Valeurs fixes (20 et 10 PV temporaires)', "Niveau d'occultiste + mod. Charisme pour vous ; moitié du niveau + mod. Charisme pour 5 créatures"),
    ('majeur', 'Le Céleste / Vengeance ardente', 'Déclenché par un jet réussi ; 41 PV fixes', "À la place d'un jet contre la mort : récupère la moitié des PV max ; 2d8 + mod. Charisme radiants à 9 m, aveuglés ; 1/repos long"),
    ('mineur', 'Le Céleste / Âme rayonnante', 'Bonus appliqué à tous les dégâts', 'Mod. Charisme ajouté à un seul jet de dégâts radiants ou de feu du sort, contre une cible'),
    ('majeur', 'Le Céleste / sorts_domaine', "Noms invalides (Restaurer l'innocence, Revitalisation, Colonne de feu) ; Bénédiction, Aide, Rappel à la vie hors liste", 'Soins, Éclair traçant / Sphère de feu, Restauration partielle / Lumière du jour, Retour à la vie / Gardien de la foi, Mur de feu / Colonne de flamme, Restauration supérieure'),
    ('majeur', 'La Lame maudite / Malédiction de la Lame', 'Récupération au repos long ; durée et portée absentes', 'Action bonus, 9 m, 1 minute ; +bonus de maîtrise aux dégâts ; 1 fois par repos court ou long'),
    ('majeur', 'La Lame maudite / Armure de maléfices', "Jet d'un d6 (4+)", "Réaction, jet d'un d20 : sur 4 ou plus, l'attaque échoue"),
    ('mineur', 'La Lame maudite / Spectre maudit', 'Restrictions et statistiques absentes', "Humanoïde tué ; PV temp = moitié du niveau d'occultiste ; +mod. Charisme à l'attaque ; 1/repos long"),
    ('mineur', 'La Lame maudite / Maître des malédictions', 'Nom inexact', 'XGE : « Maître des maléfices » (Master of Hexes), cible à 9 m, sans regain de PV'),
    ('majeur', 'La Lame maudite / sorts_domaine', "Noms invalides (Marque du reître, Pinte d'obscurité, Rapidité, Fléau d'animation, Conflit) ; Clairvoyance, Invisibilité supérieure, Flétrissement hors liste", 'Bouclier, Châtiment courroucé / Flou, Châtiment révélateur / Clignotement, Arme élémentaire / Assassin imaginaire, Châtiment débilitant / Châtiment du ban, Cône de froid'),
    ('majeur', 'Le Génie / sorts_domaine', 'Sorts communs à tous les génies absents des 4 listes', "Détection du mal et du bien (1), Force fantasmagorique (2), Création de nourriture et d'eau (3), Assassin imaginaire (4), Création (5), Souhait (9)"),
    ('mineur', 'Le Génie / Vaisseau du Génie', 'Refuge confondu avec le repos court de 10 min (aptitude de niveau 10)', 'Niv. 1 : vaisseau (CA = DD des sorts, PV = niveau + bonus de maîtrise), Refuge en bouteille 2 × bonus de maîtrise heures, 1/repos long'),
    ('majeur', 'Le Génie (Dao - Terre) / sorts_domaine', 'Création de nourriture et Passage par la pierre invalides ; Immobilisation de personne, Divination hors liste', "Sanctuaire / Croissance d'épines / Fusion dans la pierre / Façonnage de la pierre / Mur de pierre"),
    ('majeur', 'Le Génie (Djinn - Air) / sorts_domaine', '« Onde de choc » invalide ; Forme gazeuse, Liberté de mouvement, Domination de monstre hors liste', 'Vague tonnante / Bourrasque / Mur de vent / Invisibilité supérieure / Apparence trompeuse'),
    ('majeur', 'Le Génie (Éfrit - Feu) / sorts_domaine', '« Colonne de feu » invalide ; Immolation hors liste', 'Mains brûlantes / Rayon ardent / Boule de feu / Bouclier de feu / Colonne de flamme'),
    ('majeur', 'Le Génie (Maride - Eau) / sorts_domaine', 'Raz-de-marée, Tempête de grêle, Cercle de téléportation hors liste', "Nappe de brouillard / Flou / Tempête de neige / Contrôle de l'eau / Cône de froid"),
    ('majeur', "L'Insondable / Tentacule abyssal", '2d8 dès le niveau 1 ; utilisations absentes', '1d8 froid (2d8 au niv. 10), vitesse -3 m ; utilisations = bonus de maîtrise par repos long'),
    ('majeur', "L'Insondable / Tentacule gardien", 'Réduction de 2d8 dès le niveau 6', 'Réaction, réduction de 1d8 (2d8 au niv. 10) à 3 m du tentacule'),
    ('majeur', "L'Insondable / Tentacules agrippants", '20 PV temporaires fixes', "PV temporaires = niveau d'occultiste ; concentration non rompue par les dégâts"),
    ('majeur', "L'Insondable / Plongeon abyssal", 'Récupération au repos long', '1 fois par repos court ou long ; créatures à 9 m'),
    ('majeur', "L'Insondable / sorts_domaine", "Noms invalides (Tentacules de noirs éboulis, Ascension, Implosion) ; Nappe de brouillard, Fléau, Immobilisation de personne, Clairvoyance, Forme gazeuse, Invocation d'élémentaires mineurs hors liste", "Création ou destruction d'eau, Vague tonnante / Bourrasque, Silence / Éclair, Tempête de neige / Contrôle de l'eau, Convocation d'élémentaire / Main de Bigby, Cône de froid"),
    ('mineur', 'Le Moissonneur / sorts_domaine', "Noms inexistants : « Faux repos », « Rayon d'affaiblissement », « Pulsion de mort » ; 6 sorts au lieu de 10", 'Suggestion : Simulacre de vie, Rayon empoisonné / Rayon affaiblissant, Cécité/Surdité / Animation des morts, Mort simulée / Flétrissement, Protection contre la mort / Brume mortelle, Contagion'),
    ('mineur', 'Le Protecteur astral / sorts_domaine', 'Noms invalides : « Lueur féérique », « Flottement », « Levitation », « Force fantasmatique », « Œil mystique », « Anticipation », « Périple planétaire »', 'Suggestion : Lueurs féeriques, Feuille morte / Lévitation, Force fantasmagorique / Clairvoyance, Clignotement / Porte dimensionnelle, Oeil magique / Télékinésie, Cercle de téléportation'),
]
