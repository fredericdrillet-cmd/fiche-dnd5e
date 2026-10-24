"""Descriptions enrichies — Clerc (PHB, DMG, Xanathar, Tasha, SCAG ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Clerc"


def _frappe(type_degats: str, nature: str = "") -> str:
    return ("Vous imprégnez vos armes de la puissance de votre divinité" + nature + ". Une fois à chacun "
            "de vos tours, lorsque vous touchez une créature avec une attaque d'arme, vous pouvez lui infliger 1d8 "
            "dégâts supplémentaires " + type_degats + ". Ces dégâts passent à 2d8 au niveau 14 de clerc. "
            "Variante (Tasha) : l'option Frappes bénies peut remplacer cette aptitude.")


_PUISSANTE = ("Vous ajoutez votre modificateur de Sagesse aux dégâts que vous infligez avec "
              "n'importe quel sort mineur de clerc (une seule fois par lancement, même si le sort touche plusieurs "
              "cibles ou fait plusieurs jets de dégâts). Exemple : Flamme sacrée inflige alors 1d8 + votre "
              "modificateur de Sagesse dégâts radiants (2d8 au niveau 5, 3d8 au niveau 11, 4d8 au niveau 17). "
              "Variante (Tasha) : l'option Frappes bénies peut remplacer cette aptitude.")

BASE = {
    "Incantation": (
        "Vous lancez des sorts divins grâce à la Sagesse, votre caractéristique d'incantation. Vous connaissez 3 sorts "
        "mineurs de clerc (4 au niveau 4, 5 au niveau 10). Après chaque repos long, vous préparez un nombre de sorts de "
        "clerc égal à votre modificateur de Sagesse + votre niveau de clerc (minimum 1), choisis dans toute la liste du "
        "clerc parmi les niveaux pour lesquels vous avez des emplacements ; lancer un sort dépense un emplacement de "
        "niveau égal ou supérieur. DD de sauvegarde de vos sorts = 8 + votre bonus de maîtrise + votre modificateur de "
        "Sagesse ; bonus d'attaque des sorts = votre bonus de maîtrise + votre modificateur de Sagesse. Vous pouvez "
        "lancer en rituel tout sort préparé possédant l'étiquette rituel, et utiliser un symbole sacré comme "
        "focaliseur. Les sorts de domaine sont toujours préparés et ne comptent pas dans ce total."),
    "Domaine divin": (
        "Vous choisissez un domaine lié à votre divinité (Guerre, Lumière, Nature, Ruse, Savoir, Tempête, Vie, Mort, "
        "Forge, Tombe, Crépuscule, Ordre, Paix, Arcanes…). Il vous accorde dès le niveau 1 des aptitudes (souvent des "
        "maîtrises supplémentaires), puis d'autres aux niveaux 2, 6, 8 et 17. Ses sorts de domaine (deux par niveau de "
        "sort, obtenus aux niveaux de clerc 1, 3, 5, 7 et 9) sont toujours préparés, ne comptent pas dans votre nombre "
        "de sorts préparés et sont considérés comme des sorts de clerc pour vous."),
    "Conduit divin (1/repos)": (
        "Vous pouvez canaliser l'énergie divine pour produire un effet magique : Renvoi des morts-vivants, ou l'effet "
        "propre à votre domaine (chaque domaine en ajoute au moins un). Vous choisissez l'effet au moment d'utiliser le "
        "Conduit divin. Vous disposez d'une utilisation, récupérée à la fin d'un repos court ou long (2 utilisations au "
        "niveau 6, 3 au niveau 18). Les effets qui imposent un jet de sauvegarde utilisent le DD de vos sorts de clerc : "
        "8 + votre bonus de maîtrise + votre modificateur de Sagesse."),
    "Conduit divin : Renvoi des morts-vivants": (
        "Par une action, vous brandissez votre symbole sacré et prononcez une prière. Chaque mort-vivant situé à 9 m "
        "ou moins qui peut vous voir ou vous entendre fait un jet de sauvegarde de Sagesse (DD 8 + votre bonus de "
        "maîtrise + votre modificateur de Sagesse). En cas d'échec, il est renvoyé pendant 1 minute ou jusqu'à ce "
        "qu'il subisse des dégâts : il doit s'éloigner de vous le plus possible, ne peut pas volontairement s'approcher "
        "à 9 m ou moins de vous ni prendre de réaction, et ne peut utiliser son action que pour Foncer ou tenter de se "
        "libérer d'un effet qui l'empêche de bouger (Esquiver s'il n'a nulle part où aller)."),
    "Destruction des morts-vivants (FP 1/2)": (
        "Lorsqu'un mort-vivant rate son jet de sauvegarde contre votre Renvoi des "
        "morts-vivants, il est instantanément détruit si son facteur de puissance est inférieur ou égal à 1/2 "
        "(squelettes, zombis…). Le seuil augmente avec les niveaux de clerc : FP 1 au niveau 8, FP 2 au niveau 11, FP 3 au "
        "niveau 14 et FP 4 au niveau 17. Les morts-vivants plus puissants qui échouent sont simplement renvoyés."),
    "Conduit divin (2/repos)": (
        "À partir du niveau 6, vous pouvez utiliser Conduit divin deux fois entre deux repos (les utilisations sont "
        "toutes récupérées à la fin d'un repos court ou long). Vous pouvez dépenser les deux pour le même effet ou pour "
        "deux effets différents (Renvoi des morts-vivants, option de domaine). Au niveau 18, vous passerez à trois "
        "utilisations."),
    "Destruction des morts-vivants (FP 1)": (
        "Un mort-vivant qui rate son jet de sauvegarde contre votre "
        "Renvoi des morts-vivants est désormais détruit instantanément si son facteur de puissance est inférieur ou "
        "égal à 1 (goules, ombres, spectres mineurs…). Le seuil passera à FP 2 au niveau 11, FP 3 au niveau 14 et "
        "FP 4 au niveau 17."),
    "Sorts de clerc supplémentaires (option Tasha)": (
        "Option de classe (Chaudron des merveilles de Tasha, avec l'accord du MD). Les sorts suivants rejoignent la "
        "liste de sorts du clerc et peuvent donc être préparés comme n'importe quel sort de clerc dès que vous avez "
        "des emplacements du niveau voulu : Aura de vitalité et Voile spirituel (niveau 3), Aura de vie et Aura de "
        "pureté (niveau 4), Rayon de soleil (niveau 6), Éclat du soleil (niveau 8) et Mot de pouvoir guérisseur "
        "(niveau 9)."),
    "Conduit divin : Canalisation de puissance divine (option Tasha)": (
        "Option de classe (Chaudron des merveilles de Tasha). Par une action bonus, vous touchez votre symbole sacré, "
        "murmurez une prière et dépensez une utilisation de Conduit divin pour récupérer un emplacement de sort "
        "dépensé. Le niveau de cet emplacement ne peut pas dépasser la moitié (arrondie au supérieur) de votre bonus "
        "de maîtrise : niveau 1 jusqu'au niveau 4 de clerc, niveau 2 du niveau 5 au niveau 12, niveau 3 à partir du "
        "niveau 13. Cette option est utilisable une fois entre deux repos longs, deux fois à partir du niveau 6 et "
        "trois fois à partir du niveau 18."),
    "Sorts mineurs polyvalents (option Tasha)": (
        "Option de classe (Chaudron des merveilles de Tasha). Chaque fois que la classe de clerc vous accorde une "
        "Amélioration de caractéristique (niveaux 4, 8, 12, 16 et 19), vous pouvez remplacer l'un de vos sorts mineurs de clerc "
        "par un autre sort mineur de la liste du clerc."),
    "Frappes bénies (option Tasha)": (
        "Option de classe (Chaudron des merveilles de Tasha). Au niveau 8, vous pouvez prendre cette aptitude à la "
        "place de la Frappe divine ou de l'Incantation puissante accordée par votre domaine. Lorsqu'une créature "
        "subit des dégâts de l'un de vos sorts mineurs ou de l'une de vos attaques d'arme, vous pouvez lui infliger "
        "1d8 dégâts radiants supplémentaires. Une seule fois par tour ; ces dégâts n'augmentent pas au niveau 14."),
    "Intervention divine": (
        "Par une action, vous implorez l'aide de votre divinité en décrivant l'assistance souhaitée, puis vous lancez "
        "un d100 : si le résultat est inférieur ou égal à votre niveau de clerc, la divinité intervient. Le MD choisit "
        "la forme de l'intervention ; l'effet d'un sort de clerc ou de domaine est approprié. En cas de réussite, vous "
        "ne pouvez plus utiliser cette aptitude pendant 7 jours ; en cas d'échec, vous pouvez réessayer après avoir "
        "terminé un repos long."),
    "Destruction des morts-vivants (FP 2)": (
        "Au niveau 11, Renvoi des morts-vivants détruit instantanément "
        "tout mort-vivant qui rate son jet de sauvegarde et dont le facteur de puissance est inférieur ou égal à 2 "
        "(blêmes, goules de grande taille…). Le seuil passera à FP 3 au niveau 14 puis FP 4 au niveau 17."),
    "Destruction des morts-vivants (FP 3)": (
        "Au niveau 14, Renvoi des morts-vivants détruit instantanément "
        "tout mort-vivant qui rate son jet de sauvegarde et dont le facteur de puissance est inférieur ou égal à 3 "
        "(nécrophages, momies mineures…). Le seuil passera à FP 4 au niveau 17."),
    "Destruction des morts-vivants (FP 4)": (
        "Au niveau 17, Renvoi des morts-vivants détruit instantanément "
        "tout mort-vivant qui rate son jet de sauvegarde et dont le facteur de puissance est inférieur ou égal à 4 "
        "(fantômes, nécrophages puissants…)."),
    "Conduit divin (3/repos)": (
        "À partir du niveau 18, vous pouvez utiliser Conduit divin trois fois entre deux repos ; toutes les "
        "utilisations sont récupérées à la fin d'un repos court ou long. Chaque utilisation peut alimenter Renvoi des "
        "morts-vivants ou n'importe quelle option de Conduit divin accordée par votre domaine."),
    "Intervention divine garantie": (
        "Au niveau 20, votre appel à l'Intervention divine réussit automatiquement : vous n'avez plus besoin de lancer "
        "le d100. Vous utilisez toujours une action pour implorer l'aide de votre divinité, et après une intervention "
        "réussie vous devez encore attendre 7 jours avant de pouvoir y recourir de nouveau."),
}

SUB = {
    "Domaine de la Guerre": {
        "Maîtrises sup. & Prêtre de guerre": (
            "Maîtrises supplémentaires : armes de guerre et armures lourdes. Prêtre de guerre : quand vous utilisez "
            "l'action Attaquer, vous pouvez effectuer une attaque d'arme supplémentaire par une action bonus. Vous "
            "disposez d'un nombre d'utilisations égal à votre modificateur de Sagesse (minimum 1), récupérées à la fin "
            "d'un repos long."),
        "Conduit divin : Frappe guidée": (
            "Lorsque vous effectuez un jet d'attaque, vous pouvez dépenser une utilisation de Conduit divin pour obtenir "
            "un bonus de +10 à ce jet. Vous décidez d'utiliser cette aptitude après avoir vu le résultat du d20, mais "
            "avant que le MD n'annonce si l'attaque touche ou rate."),
        "Conduit divin : Bénédiction du dieu de la guerre": (
            "Au niveau 6, quand une créature située à 9 m ou moins de vous effectue un "
            "jet d'attaque, vous pouvez utiliser votre réaction et dépenser une utilisation de Conduit divin pour lui "
            "accorder un bonus de +10 à ce jet. Vous prenez cette décision après avoir vu le d20, mais avant de savoir "
            "si l'attaque touche."),
        "Frappe divine": _frappe("du même type que ceux de l'arme"),
        "Avatar de bataille": (
            "Au niveau 17, vous obtenez la résistance aux dégâts contondants, perforants et tranchants infligés par des "
            "armes non magiques. Cette protection est permanente et ne demande aucune action."),
    },
    "Domaine de la Lumière": {
        "Sort mineur supp. & Illumination protectrice": (
            "Vous apprenez le sort mineur Lumière s'il ne vous est pas déjà connu (il ne compte pas dans vos sorts "
            "mineurs). Illumination protectrice : quand une créature que vous pouvez voir, à 9 m ou moins, vous attaque, "
            "vous pouvez utiliser votre réaction pour lui imposer un désavantage au jet d'attaque grâce à un éclair de "
            "lumière, avant de savoir si elle touche. Les créatures qui ne peuvent pas être aveuglées y sont immunisées. "
            "Utilisations : un nombre de fois égal à votre modificateur de Sagesse (minimum 1), récupérées après un "
            "repos long."),
        "Conduit divin : Radiance de l'aube": (
            "Par une action, vous brandissez votre symbole sacré : toute ténèbre magique à 9 m ou moins de vous est "
            "dissipée. Chaque créature hostile à 9 m ou moins fait un jet de sauvegarde de Constitution (DD 8 + votre "
            "bonus de maîtrise + votre modificateur de Sagesse) ; elle subit 2d10 + votre niveau de clerc dégâts "
            "radiants en cas d'échec, la moitié en cas de réussite. Une créature bénéficiant d'un abri total contre "
            "vous n'est pas affectée."),
        "Illumination protectrice améliorée": (
            "Au niveau 6, vous pouvez aussi utiliser Illumination protectrice lorsqu'une créature que vous pouvez voir "
            "à 9 m ou moins attaque une autre créature que vous. Le coût reste votre réaction et une utilisation "
            "(un nombre de fois égal à votre modificateur de Sagesse, récupérées après un repos long), et l'attaquant "
            "subit le désavantage au jet d'attaque."),
        "Incantation puissante": _PUISSANTE,
        "Couronne de lumière": (
            "Au niveau 17, par une action, vous activez une aura de lumière solaire pendant 1 minute (ou jusqu'à ce que "
            "vous la congédiez par une autre action). Vous émettez une lumière vive dans un rayon de 18 m et une lumière "
            "faible sur 9 m supplémentaires. Vos ennemis situés dans la lumière vive ont un désavantage aux jets de "
            "sauvegarde contre les sorts qui infligent des dégâts de feu ou radiants."),
    },
    "Domaine de la Nature": {
        "Acolyte de la nature & Maîtrise sup.": (
            "Acolyte de la nature : vous apprenez un sort mineur de druide de votre choix (il compte comme sort mineur "
            "de clerc) et obtenez la maîtrise d'une compétence parmi Dressage, Nature et Survie. Maîtrise "
            "supplémentaire : vous maîtrisez les armures lourdes."),
        "Conduit divin : Charme des animaux et des plantes": (
            "Par une action, vous brandissez votre symbole sacré et nommez votre "
            "divinité. Chaque bête ou créature végétale qui peut vous voir à 9 m ou moins fait un jet de sauvegarde de "
            "Sagesse (DD 8 + votre bonus de maîtrise + votre modificateur de Sagesse). En cas d'échec, elle est charmée "
            "par vous pendant 1 minute ou jusqu'à ce qu'elle subisse des dégâts, et se montre amicale envers vous et "
            "les créatures que vous désignez."),
        "Atténuation des éléments": (
            "Au niveau 6, lorsque vous ou une créature à 9 m ou moins de vous subissez des dégâts d'acide, de froid, de "
            "feu, de foudre ou de tonnerre, vous pouvez utiliser votre réaction pour accorder la résistance contre ce "
            "type de dégâts pour cette occurrence. Aucune limite d'utilisations : seule votre réaction (une par round) "
            "est consommée."),
        "Frappe divine": _frappe("de froid, de feu ou de foudre (au choix à chaque coup)", ", qui canalise les éléments"),
        "Maître de la nature": (
            "Au niveau 17, tant que des créatures sont charmées par votre Charme des animaux et des plantes, vous "
            "pouvez, par une action bonus, leur ordonner verbalement ce qu'elles feront à leur prochain tour. Les "
            "ordres peuvent viser toutes les créatures charmées à la fois."),
    },
    "Domaine de la Ruse": {
        "Bénédiction du filou": (
            "Par une action, vous touchez une créature consentante autre que vous : elle obtient "
            "un avantage aux tests de Dextérité (Discrétion). L'effet dure 1 heure ou jusqu'à ce que vous utilisiez de "
            "nouveau cette aptitude. Aucune limite d'utilisations."),
        "Conduit divin : Invocation de réplique": (
            "Par une action, vous créez un double illusoire parfait de vous-même dans un espace inoccupé visible à 9 m "
            "ou moins, pour 1 minute (comme un sort à concentration). Par une action bonus, vous pouvez le déplacer de "
            "9 m au maximum ; il disparaît s'il se trouve à plus de 36 m de vous. Vous pouvez lancer vos sorts comme si "
            "vous étiez à sa place (avec vos propres sens), et vous avez un avantage aux jets d'attaque contre une "
            "créature si vous et le double êtes tous deux à 1,50 m ou moins d'elle."),
        "Conduit divin : Linceul d'ombre": (
            "Au niveau 6, par une action, vous dépensez une utilisation de Conduit divin pour devenir invisible jusqu'à "
            "la fin de votre prochain tour. L'invisibilité prend fin plus tôt si vous attaquez ou lancez un sort."),
        "Frappe divine": _frappe("de poison"),
        "Réplique améliorée": (
            "Au niveau 17, Invocation de réplique crée jusqu'à quatre doubles au lieu d'un. Par une action bonus, vous "
            "pouvez déplacer autant de doubles que vous le souhaitez, de 9 m chacun au maximum, et chacun doit rester "
            "à 36 m ou moins de vous. Vous pouvez lancer vos sorts depuis l'emplacement de n'importe lequel d'entre eux."),
    },
    "Domaine du Savoir": {
        "Bénédictions du savoir": (
            "Vous apprenez deux langues de votre choix et obtenez la maîtrise de deux "
            "compétences parmi Arcanes, Histoire, Nature et Religion. Votre bonus de maîtrise est doublé pour tout "
            "test de caractéristique utilisant l'une de ces deux compétences."),
        "Conduit divin : Savoir des âges": (
            "Par une action, vous choisissez une compétence ou un outil : vous en obtenez la maîtrise "
            "pendant 10 minutes. Cette maîtrise s'ajoute normalement à vos tests, mais ne se double pas avec d'autres "
            "effets d'expertise."),
        "Conduit divin : Lecture des pensées": (
            "Au niveau 6, par une action, vous choisissez une créature visible à 18 m ou moins ; elle fait un jet de "
            "sauvegarde de Sagesse (DD 8 + votre bonus de maîtrise + votre modificateur de Sagesse). Si elle réussit, "
            "vous ne pouvez plus la cibler ainsi avant un repos long. Si elle échoue, vous lisez ses pensées de surface "
            "pendant 1 minute tant qu'elle reste à 18 m ou moins ; pendant ce temps, vous pouvez par une action mettre "
            "fin à l'effet pour lui lancer Suggestion sans dépenser d'emplacement, et elle rate automatiquement son jet."),
        "Incantation puissante": _PUISSANTE,
        "Vision du passé": (
            "Au niveau 17, après au moins 1 minute de méditation, vous recevez des visions du passé (en vous "
            "concentrant comme pour un sort, jusqu'à un nombre de minutes égal à votre valeur de Sagesse). Lecture "
            "d'objet : en tenant un objet, vous voyez son dernier propriétaire et comment il l'a perdu. Lecture des "
            "lieux : vous voyez les événements marquants survenus à proximité (cube d'environ 15 m) au cours d'un "
            "nombre de jours égal à votre valeur de Sagesse. Utilisable une fois, récupérée après un repos court ou long."),
    },
    "Domaine de la Tempête": {
        "Maîtrises sup. & Fureur de l'ouragan": (
            "Maîtrises supplémentaires : armes de guerre et armures lourdes. Fureur de l'ouragan : quand une créature "
            "visible à 1,50 m ou moins vous touche avec une attaque, vous pouvez utiliser votre réaction pour lui "
            "imposer un jet de sauvegarde de Dextérité (DD 8 + votre bonus de maîtrise + votre modificateur de "
            "Sagesse) ; elle subit 2d8 dégâts de foudre ou de tonnerre (au choix) en cas d'échec, la moitié en cas de "
            "réussite. Utilisations : un nombre de fois égal à votre modificateur de Sagesse (minimum 1), récupérées "
            "après un repos long."),
        "Conduit divin : Fureur destructrice": (
            "Quand vous lancez les dés de dégâts de foudre ou de tonnerre, vous pouvez dépenser une utilisation de "
            "Conduit divin pour infliger le maximum possible au lieu de lancer les dés. Idéal avec Appel de la foudre, "
            "Vague tonnante ou Fureur de l'ouragan."),
        "Frappe de l'éclair": (
            "Au niveau 6, lorsque vous infligez des dégâts de foudre à une créature de taille Grande "
            "ou inférieure, vous pouvez aussi la repousser jusqu'à 3 m de vous. Aucune limite d'utilisations ni action "
            "requise."),
        "Frappe divine": _frappe("de tonnerre"),
        "Né de la tempête": (
            "Au niveau 17, vous obtenez une vitesse de vol égale à votre vitesse de marche lorsque "
            "vous n'êtes ni sous terre ni à l'intérieur d'un bâtiment."),
    },
    "Domaine de la Vie": {
        "Maîtrises sup. & Disciple de la vie": (
            "Maîtrise supplémentaire : armures lourdes. Disciple de la vie : chaque fois que vous utilisez un sort de "
            "niveau 1 ou supérieur pour rendre des points de vie à une créature, elle récupère en plus 2 + le niveau du "
            "sort points de vie (par exemple +3 avec Soins lancé au niveau 1, +5 au niveau 3)."),
        "Conduit divin : Préservation de la vie": (
            "Par une action, vous brandissez votre symbole sacré et répartissez jusqu'à "
            "5 × votre niveau de clerc points de vie entre les créatures de votre choix situées à 9 m ou moins. Aucune "
            "créature ne peut ainsi dépasser la moitié de son maximum de points de vie. Sans effet sur les "
            "morts-vivants et les créatures artificielles."),
        "Guérisseur béni": (
            "Au niveau 6, quand vous lancez un sort de niveau 1 ou supérieur qui rend des points de vie à une créature "
            "autre que vous, vous récupérez vous-même 2 + le niveau du sort points de vie."),
        "Frappe divine": _frappe("radiants"),
        "Guérison suprême": (
            "Au niveau 17, lorsque vous devriez lancer des dés pour déterminer les points de vie rendus par un sort, "
            "vous utilisez à la place le maximum de chaque dé (Soins au niveau 1 rend ainsi 8 + votre modificateur de "
            "Sagesse, plus le bonus de Disciple de la vie)."),
    },
    "Domaine de la Mort": {
        "Maîtrises sup. & Faucheur": (
            "Maîtrise supplémentaire : armes de guerre. Faucheur : vous apprenez un sort mineur de nécromancie de "
            "n'importe quelle liste (il compte comme sort mineur de clerc). Quand vous lancez un sort mineur de "
            "nécromancie qui ne cible normalement qu'une créature, il peut en cibler deux situées à 1,50 m ou moins "
            "l'une de l'autre."),
        "Conduit divin : Toucher de la mort": (
            "Quand vous touchez une créature avec une attaque au corps à corps, vous pouvez "
            "dépenser une utilisation de Conduit divin pour lui infliger 5 + 2 × votre niveau de clerc dégâts "
            "nécrotiques supplémentaires. Vous décidez après avoir touché."),
        "Destruction inéluctable": (
            "Au niveau 6, les dégâts nécrotiques infligés par vos sorts de clerc et par vos options de Conduit divin "
            "ignorent la résistance aux dégâts nécrotiques (l'immunité s'applique toujours)."),
        "Frappe divine": _frappe("nécrotiques"),
        "Faucheur amélioré": (
            "Au niveau 17, quand vous lancez un sort de nécromancie de niveau 1 à 5 qui ne cible qu'une seule "
            "créature, il peut en cibler deux situées à 1,50 m ou moins l'une de l'autre. Si le sort consomme des "
            "composantes matérielles, vous devez les fournir pour chaque cible."),
    },
    "Domaine de la Forge": {
        "Maîtrises sup. & Bénédiction de la forge": (
            "Maîtrises supplémentaires : armures lourdes et outils de forgeron. Bénédiction de la forge : à la fin d'un "
            "repos long, vous touchez une arme ou une armure non magique ; jusqu'à la fin de votre prochain repos long, "
            "elle devient magique et confère +1 à la CA (armure) ou +1 aux jets d'attaque et de dégâts (arme). "
            "Utilisable une fois par repos long."),
        "Conduit divin : Bénédiction de l'artisan": (
            "Au cours d'un rituel d'une heure, vous créez un objet non magique contenant du métal : arme courante ou de "
            "guerre, armure, 10 munitions, outils ou autre objet métallique d'une valeur maximale de 100 po. Vous devez "
            "fournir du métal (pièces comprises) d'une valeur égale à celle de l'objet, qui est consommé. L'objet "
            "apparaît dans un espace inoccupé à 1,50 m ou moins de vous."),
        "Âme de la forge": (
            "Au niveau 6, vous obtenez la résistance aux dégâts de feu. Tant que vous portez une armure lourde, vous "
            "bénéficiez en outre d'un bonus de +1 à la CA."),
        "Frappe divine": _frappe("de feu", ", embrasée du feu de la forge"),
        "Saint de la forge et du feu": (
            "Au niveau 17, vous obtenez l'immunité aux dégâts de feu. Tant que vous portez une armure lourde, vous avez "
            "la résistance aux dégâts contondants, perforants et tranchants infligés par des attaques non magiques."),
    },
    "Domaine de la Tombe": {
        "Cercle de mortalité & Yeux de la tombe": (
            "Cercle de mortalité : quand vous devriez lancer des dés pour rendre des points de vie, par un sort, à une "
            "créature à 0 point de vie, vous utilisez le maximum de chaque dé. Vous apprenez aussi Épargner les "
            "mourants (sans le décompter), avec une portée de 9 m et lancé par une action bonus. Yeux de la tombe : "
            "par une action, jusqu'à la fin de votre prochain tour, vous connaissez l'emplacement de tout mort-vivant "
            "à 18 m ou moins non protégé par un abri total ni par la magie de divination ; un nombre de fois égal à "
            "votre modificateur de Sagesse (minimum 1), récupérées après un repos long."),
        "Conduit divin : Chemin de la tombe": (
            "Par une action, vous maudissez une créature visible à 9 m ou moins jusqu'à la fin de votre prochain tour. "
            "La prochaine fois que vous ou un allié la touchez avec une attaque, elle est vulnérable à tous les dégâts "
            "de cette attaque, puis la malédiction prend fin. Seule cette attaque est concernée."),
        "Sentinelle au seuil de la mort": (
            "Au niveau 6, quand vous ou une créature visible à 9 m ou moins subissez un coup critique, vous pouvez "
            "utiliser votre réaction pour le transformer en coup normal ; les effets déclenchés par le critique sont "
            "annulés. Utilisations : un nombre de fois égal à votre modificateur de Sagesse (minimum 1), récupérées "
            "après un repos long."),
        "Incantation puissante": _PUISSANTE,
        "Gardien des âmes": (
            "Au niveau 17, quand un ennemi visible meurt à 18 m ou moins de vous, vous ou une créature de votre choix "
            "à 18 m ou moins récupérez un nombre de points de vie égal au nombre de dés de vie de l'ennemi. Une fois "
            "par tour, et pas si vous êtes neutralisé."),
    },
    "Domaine du Crépuscule": {
        "Maîtrises sup., Yeux de la nuit & Bénédiction de vigilance": (
            "Maîtrises : armes de guerre et armures lourdes. Yeux de la nuit : vision dans le noir sur 90 m ; par une "
            "action, vous la partagez pendant 1 heure avec un nombre de créatures consentantes égal à votre "
            "modificateur de Sagesse (minimum 1) à 3 m ou moins (une fois par repos long, ou en dépensant un "
            "emplacement de sort). Bénédiction de vigilance : par une action, une créature (vous compris) a un "
            "avantage à son prochain jet d'initiative ; l'effet cesse après ce jet ou si vous réutilisez l'aptitude."),
        "Conduit divin : Sanctuaire du crépuscule": (
            "Par une action, vous créez une sphère de pénombre de 9 m de rayon centrée sur vous, qui se déplace avec "
            "vous pendant 1 minute (ou jusqu'à ce que vous soyez neutralisé ou mouriez). Quand une créature (vous "
            "compris) termine son tour dans la sphère, vous pouvez lui accorder 1d6 + votre niveau de clerc points de "
            "vie temporaires, ou mettre fin à un effet qui la charme ou l'effraie."),
        "Foulée crépusculaire": (
            "Au niveau 6, par une action bonus, lorsque vous êtes dans une zone de lumière faible "
            "ou de ténèbres, vous obtenez une vitesse de vol égale à votre vitesse de marche pendant 1 minute. "
            "Utilisations : un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos long."),
        "Frappe divine": _frappe("radiants"),
        "Linceul crépusculaire": (
            "Au niveau 17, vous et vos alliés bénéficiez d'un abri partiel (+2 à la CA et aux jets de sauvegarde de "
            "Dextérité) tant que vous êtes dans la sphère de votre Sanctuaire du crépuscule."),
    },
    "Domaine de l'Ordre": {
        "Maîtrises sup. & Voix de l'autorité": (
            "Maîtrises : armures lourdes et une compétence parmi Intimidation et Persuasion. Voix de l'autorité : quand "
            "vous lancez un sort de niveau 1 ou supérieur avec un emplacement et qu'il cible un allié, celui-ci peut "
            "utiliser sa réaction juste après pour faire une attaque d'arme contre une créature de votre choix qu'il "
            "peut voir. Si le sort cible plusieurs alliés, vous choisissez lequel attaque."),
        "Conduit divin : Exigence de l'ordre": (
            "Par une action, vous brandissez votre symbole sacré : chaque créature de votre choix "
            "qui peut vous voir ou vous entendre à 9 m ou moins fait un jet de sauvegarde de Sagesse (DD 8 + votre bonus "
            "de maîtrise + votre modificateur de Sagesse) ou est charmée jusqu'à la fin de votre prochain tour ou "
            "jusqu'à ce qu'elle subisse des dégâts. Vous pouvez aussi forcer les créatures charmées à lâcher ce qu'elles "
            "tiennent."),
        "Incarnation de la loi": (
            "Au niveau 6, quand vous lancez un sort d'enchantement de niveau 1 ou supérieur dont le temps "
            "d'incantation est d'une action, vous pouvez le lancer par une action bonus à la place. Utilisations : un "
            "nombre de fois égal à votre modificateur de Sagesse (minimum 1), récupérées après un repos long."),
        "Frappe divine": _frappe("psychiques"),
        "Courroux de l'ordre": (
            "Au niveau 17, quand vous infligez les dégâts de Frappe divine à une créature pendant votre tour, vous "
            "pouvez la maudire jusqu'au début de votre prochain tour. La prochaine fois qu'un de vos alliés la touche "
            "avec une attaque, elle subit 2d8 dégâts psychiques supplémentaires et la malédiction prend fin. Une seule "
            "malédiction par tour."),
    },
    "Domaine de la Paix": {
        "Instrument de paix & Lien de hardiesse": (
            "Instrument de paix : maîtrise d'Intuition, de Persuasion ou de Représentation. Lien de hardiesse : par une "
            "action, vous liez un nombre de créatures consentantes égal à votre bonus de maîtrise (vous compris) à 9 m "
            "ou moins, pour 10 minutes. Tant qu'une créature liée est à 9 m ou moins d'une autre, elle peut, une fois "
            "par tour, ajouter 1d4 à un jet d'attaque, un test de caractéristique ou un jet de sauvegarde. "
            "Utilisations : un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos long."),
        "Conduit divin : Baume de la paix": (
            "Par une action, vous vous déplacez jusqu'à votre vitesse sans provoquer d'attaque d'opportunité. Quand "
            "vous passez à 1,50 m ou moins d'une autre créature pendant ce déplacement, vous pouvez lui rendre 2d6 + "
            "votre modificateur de Sagesse points de vie (minimum 1). Chaque créature ne peut en bénéficier qu'une "
            "fois par utilisation."),
        "Lien protecteur": (
            "Au niveau 6, quand une créature affectée par votre Lien de hardiesse est sur le point de subir des dégâts, "
            "une autre créature liée à 9 m ou moins d'elle peut utiliser sa réaction pour se téléporter dans un espace "
            "inoccupé à 1,50 m ou moins de la première et subir tous ces dégâts à sa place."),
        "Incantation puissante": _PUISSANTE,
        "Lien étendu": (
            "Au niveau 17, la portée de Lien de hardiesse et de Lien protecteur passe de 9 m à 18 m. De plus, une "
            "créature qui utilise sa réaction pour Lien protecteur obtient la résistance aux dégâts qu'elle encaisse "
            "ainsi."),
    },
    "Domaine du Sang (Communauté)": {
        "Focus sanguin & Sens de la vie": (
            "Focus sanguin : quand vous lancez un sort de clerc dont la composante matérielle n'a pas de coût indiqué, "
            "vous pouvez la remplacer par votre sang en subissant 1d4 dégâts nécrotiques (ne pouvant être réduits). "
            "Sens de la vie : par une action, pendant 1 minute, vous percevez l'emplacement de toute créature vivante "
            "(ni mort-vivant ni créature artificielle) à 18 m ou moins qui n'est pas à son maximum de points de vie, "
            "sauf derrière un abri total. Utilisations : un nombre de fois égal à votre modificateur de Sagesse "
            "(minimum 1), récupérées après un repos long."),
        "Conduit divin : Malédiction sanguine": (
            "Par une action, vous choisissez une créature visible à 9 m ou moins qui possède du sang ; elle fait un jet "
            "de sauvegarde de Constitution (DD 8 + votre bonus de maîtrise + votre modificateur de Sagesse). En cas "
            "d'échec, sa vitesse tombe à 0 et elle a un désavantage à ses jets d'attaque jusqu'à la fin de son prochain "
            "tour. En cas de réussite, sa vitesse est seulement réduite de moitié pendant la même durée."),
        "Marionnette de sang": (
            "Au niveau 6, par une action, vous dépensez une utilisation de Conduit divin pour l'un de ces effets. "
            "Pantin : une créature vivante de taille Grande ou inférieure visible à 9 m ou moins fait un jet de "
            "sauvegarde de Constitution (DD 8 + votre bonus de maîtrise + votre modificateur de Sagesse) ; en cas "
            "d'échec, vous la déplacez de la moitié de sa vitesse (ce mouvement provoque normalement les attaques "
            "d'opportunité) et elle ne peut pas prendre de réaction avant le début de votre prochain tour. Cadavre : un "
            "cadavre de taille Moyenne ou inférieure mort depuis moins d'une minute se relève comme zombi sous votre "
            "contrôle pendant 1 minute."),
        "Frappe divine": _frappe("nécrotiques", ", nourrie par le sang versé"),
        "Transfusion vasculaire": (
            "Au niveau 17, par une action, vous arrachez le sang de vos ennemis : chaque créature de votre choix dans "
            "une sphère de 6 m de rayon centrée sur un point à 18 m ou moins fait un jet de sauvegarde de Constitution "
            "(DD 8 + votre bonus de maîtrise + votre modificateur de Sagesse), subissant 6d8 dégâts nécrotiques en cas "
            "d'échec, la moitié en cas de réussite (sans effet sur les morts-vivants et créatures artificielles). Vous "
            "répartissez ensuite la moitié des dégâts totaux infligés en points de vie rendus aux créatures de votre "
            "choix à 18 m ou moins. Une fois par repos long."),
    },
    "Domaine de l'Arcane (Communauté)": {
        "Initié aux arcanes": (
            "Vous obtenez la maîtrise de la compétence Arcanes et apprenez deux sorts mineurs de votre choix dans la "
            "liste du magicien. Pour vous, ils comptent comme des sorts mineurs de clerc (la Sagesse est votre "
            "caractéristique d'incantation pour ces sorts) et ne sont pas décomptés de vos sorts mineurs connus."),
        "Conduit divin : Abjuration arcanique": (
            "Par une action, vous brandissez votre symbole sacré : un céleste, un élémentaire, une "
            "fée ou un fiélon visible à 9 m ou moins qui peut vous voir ou vous entendre fait un jet de sauvegarde de "
            "Sagesse (DD 8 + votre bonus de maîtrise + votre modificateur de Sagesse) ou est renvoyé pendant 1 minute "
            "ou jusqu'à ce qu'il subisse des dégâts (mêmes restrictions que Renvoi des morts-vivants). À partir du "
            "niveau 5, s'il échoue et que son FP ne dépasse pas le seuil de Destruction des morts-vivants, il est banni "
            "pendant 1 minute (comme Bannissement, sans concentration)."),
        "Briseur de sorts": (
            "Au niveau 6, quand vous rendez des points de vie à un allié avec un sort de niveau 1 ou "
            "supérieur, vous pouvez aussi mettre fin à un sort de votre choix qui l'affecte, à condition que son niveau "
            "soit inférieur ou égal à celui de l'emplacement utilisé pour le sort de soins."),
        "Incantation puissante": _PUISSANTE,
        "Maîtrise des arcanes": (
            "Au niveau 17, vous choisissez quatre sorts de la liste du magicien, un de chacun des "
            "niveaux 6, 7, 8 et 9. Ils s'ajoutent à vos sorts de domaine : toujours préparés, ne comptant pas dans "
            "votre total, et considérés comme des sorts de clerc pour vous."),
    },
}

CORRIGE = [
    # --- Capacités de base ---
    ("mineur", "Clerc / Destruction des morts-vivants", "Faute de frappe « Détruction » dans les 5 entrées (FP 1/2 à FP 4)",
     "Nom officiel : « Destruction des morts-vivants »"),
    ("majeur", "Clerc / Intervention divine", "Aucun délai après une réussite, ni coût en action ni réessai après repos long",
     "Action ; après une réussite, 7 jours d'attente ; après un échec, nouvel essai après un repos long"),
    ("mineur", "Clerc / Intervention divine garantie", "Ne rappelle pas le délai de 7 jours après réussite",
     "Au niveau 20 la réussite est automatique, mais le délai de 7 jours s'applique toujours"),
    ("mineur", "Clerc / Conduit divin : Renvoi des morts-vivants", "Omet la fin sur dégâts et les restrictions d'action",
     "Renvoyé 1 minute ou jusqu'à subir des dégâts ; pas de réaction ; action limitée à Foncer/se libérer (DD des sorts)"),
    ("info", "Clerc / Incantation", "Description sans nombre de sorts mineurs/préparés, DD ni bonus d'attaque",
     "3/4/5 sorts mineurs (niv. 1/4/10) ; sorts préparés = modificateur de Sagesse + niveau de clerc ; DD 8 + maîtrise + Sagesse ; rituels"),
    ("info", "Clerc / Frappe divine / Incantation puissante (niveau 8)", "Aptitude de domaine dupliquée dans les capacités de base",
     "Dans le PHB, Frappe divine ou Incantation puissante est une aptitude du domaine (déjà présente dans chaque sous-classe)"),
    ("info", "Clerc / Frappe divine améliorée (niveau 14)", "Palier de domaine placé dans les capacités de base",
     "Le passage à 2d8 au niveau 14 fait partie de l'aptitude Frappe divine de chaque domaine concerné"),
    ("mineur", "Clerc / Capacités de classe optionnelles (Tasha)", "Absente : Sorts de clerc supplémentaires (niveau 1)",
     "Ajoute à la liste du clerc : Aura de vitalité, Linceul spirituel (3), Aura de vie, Aura de pureté (4), Rayon de soleil (6), Explosion solaire (8), Mot de pouvoir guérisseur (9)"),
    ("mineur", "Clerc / Capacités de classe optionnelles (Tasha)", "Absente : Conduit divin : Canalisation de puissance divine (niveau 2)",
     "Action bonus + Conduit divin : récupère un emplacement de niveau ≤ moitié du bonus de maîtrise (arrondi sup.) ; 1/2/3 fois par repos long (niv. 2/6/18)"),
    ("mineur", "Clerc / Capacités de classe optionnelles (Tasha)", "Absente : Sorts mineurs polyvalents (niveau 4)",
     "À chaque Amélioration de caractéristique, remplacer un sort mineur de clerc par un autre"),
    ("mineur", "Clerc / Capacités de classe optionnelles (Tasha)", "Absente : Frappes bénies (niveau 8)",
     "Remplace Frappe divine / Incantation puissante : 1d8 dégâts radiants une fois par tour (sort mineur ou arme)"),
    # --- Champs source ---
    ("mineur", "Domaine de la Guerre / source", "Champ \"source\" absent/vide", "Manuel des joueurs (PHB)"),
    ("mineur", "Domaine de la Lumière / source", "Champ \"source\" absent/vide", "Manuel des joueurs (PHB)"),
    ("mineur", "Domaine de la Nature / source", "Champ \"source\" absent/vide", "Manuel des joueurs (PHB)"),
    ("mineur", "Domaine de la Ruse / source", "Champ \"source\" absent/vide", "Manuel des joueurs (PHB)"),
    ("mineur", "Domaine du Savoir / source", "Champ \"source\" absent/vide", "Manuel des joueurs (PHB)"),
    ("mineur", "Domaine de la Tempête / source", "Champ \"source\" absent/vide", "Manuel des joueurs (PHB)"),
    ("mineur", "Domaine de la Vie / source", "Champ \"source\" absent/vide", "Manuel des joueurs (PHB)"),
    ("mineur", "Domaine de la Mort / source", "Champ \"source\" absent/vide", "Guide du maître (DMG)"),
    ("mineur", "Domaine de la Forge / source", "Champ \"source\" absent/vide", "Xanathar's Guide to Everything (XGE)"),
    ("mineur", "Domaine de la Tombe / source", "Champ \"source\" absent/vide", "Xanathar's Guide to Everything (XGE)"),
    ("mineur", "Domaine du Crépuscule / source", "Champ \"source\" absent/vide", "Tasha's Cauldron of Everything (TCE)"),
    ("mineur", "Domaine de l'Ordre / source", "Champ \"source\" absent/vide", "Tasha's Cauldron of Everything (TCE)"),
    ("mineur", "Domaine de la Paix / source", "Champ \"source\" absent/vide", "Tasha's Cauldron of Everything (TCE)"),
    ("mineur", "Domaine du Sang (Communauté) / source", "Champ \"source\" absent/vide", "Homebrew / communauté (à indiquer)"),
    ("mineur", "Domaine de l'Arcane (Communauté) / source", "Champ \"source\" absent/vide",
     "Domaine des Arcanes officiel : Sword Coast Adventurer's Guide (SCAG)"),
    # --- Guerre ---
    ("majeur", "Domaine de la Guerre / Prêtre de guerre", "1 utilisation par repos long",
     "Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long"),
    ("majeur", "Domaine de la Guerre / Conduit divin : Dieu de la guerre", "Obtenu au niveau 2",
     "Bénédiction du dieu de la guerre : niveau 6"),
    ("majeur", "Domaine de la Guerre / Impact divin", "+2d8 dès le niveau 8",
     "1d8 au niveau 8, 2d8 au niveau 14 ; dégâts du type de l'arme"),
    ("mineur", "Domaine de la Guerre / Avatar de bataille", "Résistance sans restriction",
     "Résistance contondant/perforant/tranchant des armes non magiques uniquement"),
    ("majeur", "Domaine de la Guerre / sorts_domaine", "Fracassement, Fléau d'insectes et « Colonne de feu » dans la liste",
     "Faveur divine, Bouclier de la foi, Arme magique, Arme spirituelle, Manteau du croisé, Esprits gardiens, Liberté de mouvement, Peau de pierre, Colonne de flamme, Immobilisation de monstre"),
    # --- Lumière ---
    ("majeur", "Domaine de la Lumière / Illumination protectrice", "2 utilisations par repos long",
     "Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long"),
    ("majeur", "Domaine de la Lumière / Conduit divin : Radiance de l'aube", "Jet de sauvegarde de Sagesse",
     "Jet de sauvegarde de Constitution ; 2d10 + niveau de clerc radiants, moitié si réussite"),
    ("majeur", "Domaine de la Lumière / sorts_domaine", "« Flamme colossale » (inexistant) et « Colonne de feu » ; « Lueur féérique » mal orthographié",
     "Mains brûlantes, Lueur féerique, Sphère de feu, Rayon ardent, Boule de feu, Lumière du jour, Gardien de la foi, Mur de feu, Colonne de flamme, Scrutation"),
    # --- Nature ---
    ("majeur", "Domaine de la Nature / Atténuation des éléments", "Limité à 1 fois par combat",
     "Réaction, sans limite d'utilisations (acide, froid, feu, foudre, tonnerre ; vous ou créature à 9 m)"),
    ("majeur", "Domaine de la Nature / Impact divin", "+2d8 dès le niveau 8 (« attaque d'énergie »)",
     "Attaque d'arme : 1d8 froid, feu ou foudre au niveau 8, 2d8 au niveau 14"),
    ("majeur", "Domaine de la Nature / sorts_domaine", "Noms faux ou sorts erronés (Parler avec les animaux, Murailles de ronces, Domination d'animal, Lianes étouffantes, Communion avec la nature)",
     "Amitié avec les animaux, Communication avec les animaux, Peau d'écorce, Croissance d'épines, Croissance végétale, Mur de vent, Domination de bête, Liane avide, Fléau d'insectes, Passage par les arbres"),
    # --- Ruse ---
    ("mineur", "Domaine de la Ruse / Faveur du filou", "Nom et cible imprécis",
     "Bénédiction du filou : créature consentante autre que vous, avantage Discrétion 1 heure"),
    ("mineur", "Domaine de la Ruse / Conduit divin : Linceul d'ombre", "Durée non précisée",
     "Invisible jusqu'à la fin de votre prochain tour (fin si attaque ou sort)"),
    ("majeur", "Domaine de la Ruse / Impact divin", "+2d8 dès le niveau 8", "1d8 poison au niveau 8, 2d8 au niveau 14"),
    ("majeur", "Domaine de la Ruse / sorts_domaine", "Désorientation, Silence, Clairvoyance, Dissimulation à la place des sorts officiels",
     "Charme-personne, Déguisement, Image miroir, Passage sans trace, Clignotement, Dissipation de la magie, Porte dimensionnelle, Métamorphose, Domination de personne, Modification de mémoire"),
    # --- Savoir ---
    ("mineur", "Domaine du Savoir / Conduit divin : Lecture des pensées", "Portée et lien avec Suggestion absents",
     "Créature à 18 m, sauvegarde de Sagesse ; pensées 1 minute puis Suggestion gratuite (échec automatique)"),
    ("majeur", "Domaine du Savoir / sorts_domaine", "Détection des pensées, Clairvoyance, Langues, Divination, « Œil mystique », « Légende »",
     "Injonction, Identification, Augure, Suggestion, Antidétection, Communication avec les morts, Œil magique, Confusion, Mythes et légendes, Scrutation"),
    # --- Tempête ---
    ("majeur", "Domaine de la Tempête / Fureur de l'ouragan", "2 utilisations par repos long",
     "Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long"),
    ("mineur", "Domaine de la Tempête / Choc foudroyant", "Pas de limite de taille",
     "Repousse de 3 m une créature de taille Grande ou inférieure"),
    ("majeur", "Domaine de la Tempête / Impact divin", "+2d8 dès le niveau 8", "1d8 tonnerre au niveau 8, 2d8 au niveau 14"),
    ("majeur", "Domaine de la Tempête / sorts_domaine", "« Tempête de sleet » (anglais), « Rafale de vent », Liberté de mouvement, « Insectes dévorants »",
     "Nappe de brouillard, Vague tonnante, Bourrasque, Fracassement, Appel de la foudre, Tempête de neige, Contrôle de l'eau, Tempête de grêle, Vague destructrice, Fléau d'insectes"),
    # --- Vie ---
    ("majeur", "Domaine de la Vie / Conduit divin : Survivance", "Soigne 100 PV fixes sur une cible",
     "Préservation de la vie : 5 × niveau de clerc PV répartis à 9 m, max. moitié des PV max de chaque cible"),
    ("mineur", "Domaine de la Vie / Guérisseur béni", "Ne précise pas que la cible doit être une autre créature",
     "Se déclenche en soignant une créature autre que vous avec un sort de niveau 1+"),
    ("majeur", "Domaine de la Vie / Impact divin", "+2d8 dès le niveau 8", "1d8 radiants au niveau 8, 2d8 au niveau 14"),
    ("majeur", "Domaine de la Vie / sorts_domaine", "Esprits gardiens, Divination, « Restauration suprême », « Fanal d'espoir » ; manque Retour à la vie, Protection contre la mort, Gardien de la foi",
     "Bénédiction, Soins, Restauration partielle, Arme spirituelle, Lueur d'espoir, Retour à la vie, Protection contre la mort, Gardien de la foi, Soins de groupe, Rappel à la vie"),
    # --- Mort ---
    ("majeur", "Domaine de la Mort / Conduit divin : Caresse de la mort", "+45 dégâts nécrotiques fixes",
     "Toucher de la mort : 5 + 2 × niveau de clerc dégâts nécrotiques, sur une attaque au corps à corps qui touche"),
    ("mineur", "Domaine de la Mort / Destruction inéluctable", "S'applique à tous les dégâts nécrotiques",
     "Seulement aux dégâts nécrotiques des sorts de clerc et du Conduit divin"),
    ("majeur", "Domaine de la Mort / Impact divin", "+2d8 dès le niveau 8", "1d8 nécrotiques au niveau 8, 2d8 au niveau 14"),
    ("majeur", "Domaine de la Mort / sorts_domaine", "Faux repos, Frayeur, Peur, Fléau, Fléau d'insectes, « Vampirisme », « Rayon d'affaiblissement »",
     "Simulacre de vie, Rayon empoisonné, Cécité/Surdité, Rayon affaiblissant, Animation des morts, Caresse du vampire, Flétrissement, Protection contre la mort, Brume mortelle, Contagion"),
    # --- Forge ---
    ("mineur", "Domaine de la Forge / Saint de la forge et du feu", "Résistance sans restriction",
     "Résistance contondant/perforant/tranchant des attaques non magiques, en armure lourde"),
    ("majeur", "Domaine de la Forge / Impact divin", "+2d8 dès le niveau 8", "1d8 feu au niveau 8, 2d8 au niveau 14"),
    ("majeur", "Domaine de la Forge / sorts_domaine", "Colonne de feu, Châtiment d'aveuglement, « Arme chauffée », « Protections élémentaires »",
     "Identification, Châtiment incandescent, Chauffer le métal, Arme magique, Arme élémentaire, Protection contre l'énergie, Fabrication, Mur de feu, Animation d'objets, Création"),
    # --- Tombe ---
    ("mineur", "Domaine de la Tombe / Cercle de la mort & Yeux de la tombe", "Nom « Cercle de la mort » ; utilisations de Yeux de la tombe et portée d'Épargner les mourants absentes",
     "Cercle de mortalité ; Épargner les mourants à 9 m par action bonus ; Yeux de la tombe modificateur de Sagesse fois par repos long"),
    ("majeur", "Domaine de la Tombe / Conduit divin : Chemin de la tombe", "Vulnérabilité à tous les dégâts sans limite",
     "Vulnérabilité aux dégâts de la prochaine attaque qui touche seulement (malédiction jusqu'à la fin de votre prochain tour)"),
    ("majeur", "Domaine de la Tombe / Sentinelle au seuil de la mort", "2 utilisations par repos",
     "Réaction ; un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long"),
    ("majeur", "Domaine de la Tombe / sorts_domaine", "Bénédiction, Sanctuaire, Repos éternel, Animation des morts, Fléau (mal placé), Contagion, « Mortaise suprême » (inexistant), « Rappeler à la vie »",
     "Fléau, Simulacre de vie, Doux repos, Rayon affaiblissant, Retour à la vie, Caresse du vampire, Bannissement, Protection contre la mort, Coquille antivie, Rappel à la vie"),
    # --- Crépuscule ---
    ("mineur", "Domaine du Crépuscule / Maîtrises sup., Yeux de la nuit & Faveur de vigilance", "Avantage permanent à l'initiative ; partage de vision non chiffré",
     "Bénédiction de vigilance : action, avantage au prochain jet d'initiative d'une créature ; partage 1 h, 1/repos long"),
    ("mineur", "Domaine du Crépuscule / Conduit divin : Sanctuaire du crépuscule", "Aucune valeur de PV temporaires",
     "1d6 + niveau de clerc PV temporaires (ou fin de charme/terreur), sphère 9 m, 1 minute"),
    ("majeur", "Domaine du Crépuscule / Foulée nocturne", "6 utilisations par repos long ; nom",
     "Foulée crépusculaire : bonus de maîtrise fois par repos long, vol 1 minute"),
    ("majeur", "Domaine du Crépuscule / Impact divin", "+2d8 dès le niveau 8", "1d8 radiants au niveau 8, 2d8 au niveau 14"),
    ("majeur", "Domaine du Crépuscule / sorts_domaine", "Invisibilité, Vol, Sphère d'invisibilité, Aura de pureté, « Ombre trompeuse », Cercle de téléportation",
     "Lueur féerique, Sommeil, Rayon de lune, Voir l'invisible, Aura de vitalité, Petite hutte de Léomund, Aura de vie, Invisibilité supérieure, Cercle de pouvoir, Double illusoire"),
    # --- Ordre ---
    ("mineur", "Domaine de l'Ordre / Maîtrises sup. & Voie de l'autorité", "Maîtrise de compétence absente",
     "Armures lourdes + Intimidation ou Persuasion"),
    ("majeur", "Domaine de l'Ordre / La loi incarnée", "1 utilisation par repos long",
     "Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long"),
    ("info", "Domaine de l'Ordre / Courroux de l'ordre", "« 1 fois/tour » conforme",
     "Limité à une malédiction par tour (pas de limite par repos) ; +2d8 psychiques sur la prochaine attaque d'un allié"),
    ("majeur", "Domaine de l'Ordre / Impact divin", "+2d8 dès le niveau 8", "1d8 psychiques au niveau 8, 2d8 au niveau 14"),
    ("majeur", "Domaine de l'Ordre / sorts_domaine", "« Lueur de vérité » (inexistant) et « Mots d'éloquence » (inexistant)",
     "Héroïsme, Injonction, Immobilisation de personne, Zone de vérité, Lenteur, Communication à distance, Compulsion, Localisation de créature, Communion, Domination de personne"),
    # --- Paix ---
    ("majeur", "Domaine de la Paix / Lien de hardiesse", "6 créatures fixes ; durée et utilisations absentes",
     "Bonus de maîtrise créatures, 10 minutes, bonus de maîtrise utilisations par repos long ; 1d4 une fois par tour"),
    ("majeur", "Domaine de la Paix / Conduit divin : Baume de la paix", "Soins de 2d6 + 1",
     "2d6 + modificateur de Sagesse (min. 1) par créature croisée à 1,50 m"),
    ("mineur", "Domaine de la Paix / Incantation puissante", "« Ajoute des dégâts » imprécis",
     "Ajoute le modificateur de Sagesse aux dégâts des sorts mineurs de clerc"),
    ("mineur", "Domaine de la Paix / Maîtrises sup. & Lien de hardiesse", "Maîtrise Instrument de paix absente",
     "Maîtrise d'Intuition, Persuasion ou Représentation"),
    ("majeur", "Domaine de la Paix / sorts_domaine", "Bénédiction, « Warding Bond » (anglais), « Don de balistique » (inexistant), Protection contre la mort, Divination, « Sanctuaire protecteur », Rappel à la vie, Communion",
     "Héroïsme, Sanctuaire, Aide, Lien de protection, Lueur d'espoir, Communication à distance, Aura de pureté, Sanctuaire privé de Mordenkainen, Restauration supérieure, Lien télépathique de Rary"),
    # --- Communautaires / SCAG ---
    ("mineur", "Domaine du Sang (Communauté) / sorts_domaine", "« Lien sanglant » inexistant ; « Vampirisme » et « Rayon d'affaiblissement » mal nommés",
     "Remplacer par un sort officiel (ex. Flétrissement) ; noms officiels Caresse du vampire, Rayon affaiblissant"),
    ("majeur", "Domaine de l'Arcane (Communauté) / sorts_domaine", "Projectiles magiques, Fracassement, Protection contre l'énergie, « Œil mystique », Bannissement, Création",
     "Arcanes (SCAG) : Détection de la magie, Projectile magique, Arme magique, Aura magique de Nystul, Dissipation de la magie, Cercle magique, Œil magique, Coffre secret de Léomund, Lien planaire, Cercle de téléportation"),
    ("mineur", "Domaine de l'Arcane (Communauté) / aptitudes", "Noms et effets approximatifs (Domptage d'énergie, Bannières profanes, Soins épurateurs)",
     "Initié aux arcanes (Arcanes + 2 sorts mineurs de magicien), Abjuration arcanique, Briseur de sorts, Incantation puissante, Maîtrise des arcanes"),
    # --- Noms d'aptitudes alignés sur les noms officiels (corrigés en même temps que l'audit) ---
    ("info", "Clerc / domaines / Impact divin", "Aptitude de niveau 8 nommée « Impact divin » dans 10 domaines",
     "Nom officiel : Frappe divine (1d8 au niveau 8, 2d8 au niveau 14)"),
    ("info", "Clerc / domaines / noms d'aptitudes", "Noms non officiels (Dieu de la guerre, Illumination améliorée, Auréole, Cordialité avec la faune et la flore, Faveur du filou, Faveur érudite, Savoir ancestral, Choc foudroyant, Enfant de la tempête, Survivance, Caresse de la mort, Foulée nocturne, Règne de l'ordre, La loi incarnée)",
     "Bénédiction du dieu de la guerre, Illumination protectrice améliorée, Couronne de lumière, Charme des animaux et des plantes, Bénédiction du filou, Bénédictions du savoir, Savoir des âges, Frappe de l'éclair, Né de la tempête, Préservation de la vie, Toucher de la mort, Foulée crépusculaire, Exigence de l'ordre, Incarnation de la loi"),
    ("mineur", "Domaine du Sang (Communauté) / sorts_domaine (ordre)", "Sorts non rangés par niveau (le logiciel débloque les sorts par paires : niveaux 1, 2, 3, 4, 5)",
     "Liste homebrew réordonnée : Fléau, Frayeur / Rayon affaiblissant, Immobilisation de personne / Toucher du vampire, Peur / Flétrissement, Compulsion / Contagion, Fléau d'insectes"),
]

AUDIT = [
    ("info", "Domaine de l'Arcane (Communauté) / nom", "Sous-classe officielle (SCAG) nommée « Domaine de l'Arcane (Communauté) »",
     "Nom officiel : Domaine des Arcanes — non renommée pour ne pas casser les fiches sauvegardées (source et sorts corrigés)"),
    ("info", "Domaine du Sang (Communauté) / nature", "Sous-classe homebrew (communauté), sans équivalent officiel",
     "Conservée telle quelle ; seuls les sorts invalides ont été remplacés par des sorts de la base (Lien sanglant -> Flétrissement, Cécité/Surdité -> Compulsion pour équilibrer les paliers)"),
]
