"""Descriptions enrichies — Magicien (PHB, Xanathar, Tasha, Wildemount ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Magicien"

DD = "8 + votre bonus de maîtrise + votre modificateur d'Intelligence"

BASE = {
    "Incantation": (
        "L'Intelligence est votre caractéristique d'incantation. DD de sauvegarde de vos sorts = " + DD + " ; "
        "bonus d'attaque des sorts = votre bonus de maîtrise + votre modificateur d'Intelligence. Vous connaissez "
        "3 sorts mineurs de magicien (4 au niveau 4, 5 au niveau 10). Votre grimoire contient au départ 6 sorts de "
        "magicien de niveau 1 ; chaque fois que vous gagnez un niveau dans cette classe, vous y ajoutez gratuitement 2 sorts d'un niveau "
        "que vous pouvez lancer. Après un repos long, vous préparez un nombre de sorts du grimoire égal à "
        "votre modificateur d'Intelligence + votre niveau de magicien (minimum 1) ; lancer un sort dépense un "
        "emplacement de son niveau ou d'un niveau supérieur. Vous pouvez lancer comme rituel (+10 minutes) tout "
        "sort de votre grimoire possédant l'étiquette rituel, même non préparé. Vous pouvez utiliser un "
        "focaliseur arcanique. Copier un sort trouvé dans le grimoire coûte 2 heures et 50 po par niveau du sort."
    ),
    "Restauration arcanique": (
        "Une fois par jour, à la fin d'un repos court, vous pouvez récupérer des emplacements de sorts dépensés. "
        "Leur niveau cumulé ne peut pas dépasser la moitié (arrondie au supérieur) de votre niveau de magicien, "
        "et aucun de ces emplacements ne peut être de niveau 6 ou plus. Exemple : au niveau 4, vous récupérez "
        "jusqu'à 2 niveaux d'emplacements (un emplacement de niveau 2 ou deux de niveau 1). La capacité se "
        "recharge après un repos long."
    ),
    "Tradition d'arcanes": (
        "Au niveau 2, vous choisissez une tradition arcanique (une école de magie ou une tradition comme la "
        "Chantelame, la Magie de guerre, l'Ordre des scribes ou la Chronurgie). Elle vous confère des aptitudes "
        "aux niveaux 2, 6, 10 et 14. Pour les écoles du Manuel des joueurs, l'aptitude « érudit » de niveau 2 "
        "divise par deux l'or et le temps nécessaires pour copier un sort de cette école dans votre grimoire."
    ),
    "Formules de sorts mineurs (option Tasha)": (
        "Vous avez gravé dans votre grimoire des formules de sorts mineurs. À la fin de chaque repos long, vous "
        "pouvez consulter ces formules et remplacer l'un de vos sorts mineurs de magicien connus par un autre "
        "sort mineur de la liste du magicien."
    ),
    "Maîtrise des sorts": (
        "Choisissez dans votre grimoire un sort de magicien de niveau 1 et un sort de niveau 2 dont le temps "
        "d'incantation est d'une action. Tant qu'ils sont préparés, vous pouvez les lancer à leur niveau le plus "
        "bas sans dépenser d'emplacement. Pour les lancer à un niveau supérieur, vous devez dépenser un "
        "emplacement normalement. En étudiant 8 heures, vous pouvez remplacer l'un ou les deux sorts choisis "
        "par d'autres sorts de mêmes niveaux."
    ),
    "Sorts de prédilection": (
        "Choisissez deux sorts de magicien de niveau 3 de votre grimoire. Ils sont "
        "toujours préparés, ne comptent pas dans votre nombre de sorts préparés et vous pouvez lancer chacun "
        "d'eux une fois au niveau 3 sans dépenser d'emplacement. Vous récupérez ces utilisations à la fin d'un "
        "repos court ou long. Pour les lancer à un niveau supérieur, vous dépensez un emplacement normalement."
    ),
}

SUB = {
    "École d'Abjuration": {
        "Abjurateur érudit & Égide arcanique": (
            "Abjurateur érudit : l'or et le temps nécessaires pour copier un sort d'abjuration dans votre grimoire "
            "sont divisés par deux. Égide arcanique : quand vous lancez un sort d'abjuration de niveau 1 ou plus, "
            "vous pouvez créer en même temps une égide magique qui dure jusqu'à votre prochain repos long (une "
            "création par repos long). Ses points de vie maximum valent 2 × votre niveau de magicien + votre "
            "modificateur d'Intelligence. Quand vous subissez des dégâts, l'égide les absorbe d'abord ; à 0 PV, "
            "l'excédent vous atteint. Chaque fois que vous lancez un sort d'abjuration de niveau 1 ou plus, l'égide "
            "regagne 2 PV par niveau du sort (jusqu'à son maximum)."
        ),
        "Égide projetée": (
            "Quand une créature que vous voyez à 9 m ou moins de vous subit des dégâts, vous "
            "pouvez utiliser votre réaction pour que votre Égide arcanique absorbe ces dégâts à sa place. Si "
            "l'égide tombe à 0 point de vie, la créature protégée subit les dégâts restants. Cette réaction est "
            "utilisable tant que l'égide existe et dispose de points de vie."
        ),
        "Abjuration améliorée": (
            "Quand vous lancez un sort d'abjuration qui vous demande un test de caractéristique (par exemple "
            "Contresort ou Dissipation de la magie contre un sort de niveau supérieur), vous ajoutez votre bonus "
            "de maîtrise à ce test. Cela s'applique au jet de caractéristique d'incantation effectué pour "
            "contrer ou dissiper un sort de niveau 4 ou plus."
        ),
        "Résistance aux sorts": (
            "Vous avez l'avantage aux jets de sauvegarde contre les sorts. De plus, vous avez la résistance aux "
            "dégâts infligés par les sorts, quelle que soit leur source ou leur type. Cette protection est "
            "permanente et ne nécessite aucune action."
        ),
    },
    "École de Divination": {
        "Devin érudit & Présage": (
            "Devin érudit : l'or et le temps pour copier un sort de divination sont divisés par deux. Présage : "
            "à la fin de chaque repos long, lancez deux d20 et notez les résultats. Vous pouvez remplacer "
            "n'importe quel jet d'attaque, jet de sauvegarde ou test de caractéristique effectué par vous ou par "
            "une créature que vous voyez par l'un de ces résultats, en le décidant avant le jet. Chaque résultat "
            "ne sert qu'une fois, une seule fois par tour, et les résultats non utilisés sont perdus au repos long "
            "suivant."
        ),
        "Divination experte": (
            "Quand vous lancez un sort de divination de niveau 2 ou plus en dépensant un emplacement, vous "
            "récupérez un emplacement de sort dépensé. Son niveau doit être inférieur à celui du sort lancé et ne "
            "peut pas dépasser 5. Exemple : lancer Clairvoyance (niveau 3) vous rend un emplacement de niveau 1 "
            "ou 2."
        ),
        "Troisième œil": (
            "Par une action, vous gagnez l'un des avantages suivants jusqu'à ce que vous soyez neutralisé ou que "
            "vous terminiez un repos court ou long : vision dans le noir sur 18 m ; vision éthérée (voir dans le "
            "plan Éthéré jusqu'à 18 m) ; lecture de toutes les langues écrites ; ou vision de l'invisible "
            "(créatures et objets invisibles à 3 m ou moins dans votre ligne de vue). Vous ne pouvez plus utiliser "
            "cette aptitude avant d'avoir terminé un repos."
        ),
        "Présage supérieur": (
            "Votre vision de l'avenir s'aiguise. Vous lancez désormais trois d20 au lieu de "
            "deux pour votre aptitude Présage à la fin de chaque repos long. Les règles d'utilisation restent "
            "identiques (une fois par tour, décision avant le jet, résultats perdus au repos long suivant)."
        ),
    },
    "École d'Enchantement": {
        "Enchanteur érudit & Regard hypnotique": (
            "Enchanteur érudit : l'or et le temps pour copier un sort d'enchantement sont divisés par deux. "
            "Regard hypnotique : par une action, choisissez une créature que vous voyez à 1,50 m ou moins. Si elle "
            "peut vous voir ou vous entendre, elle fait un jet de sauvegarde de Sagesse (DD " + DD + "). En cas "
            "d'échec, elle est charmée jusqu'à la fin de votre prochain tour : vitesse 0, neutralisée, "
            "visiblement hébétée. Chaque tour, vous pouvez prolonger l'effet d'un tour par une action, jusqu'à "
            "1 minute ; il cesse si vous vous éloignez à plus de 1,50 m, si elle ne vous voit ni ne vous entend "
            "plus ou si elle subit des dégâts. Une créature qui réussit sa sauvegarde ou sort de l'effet est "
            "immunisée contre ce regard jusqu'à votre prochain repos long (usage autrement illimité)."
        ),
        "Charme instinctif": (
            "Quand une créature que vous voyez à 9 m ou moins effectue un jet d'attaque "
            "contre vous, vous pouvez utiliser votre réaction pour détourner l'attaque, sauf si un autre effet "
            "l'empêche. L'attaquant fait un jet de sauvegarde de Sagesse (DD " + DD + "). En cas d'échec, il "
            "doit viser la créature la plus proche (autre que vous et lui) ; s'il y en a plusieurs, il choisit. "
            "En cas de réussite, il est immunisé contre ce charme pendant 24 heures. Les créatures immunisées "
            "contre l'état charmé ne sont pas affectées."
        ),
        "Enchantement partagé": (
            "Quand vous lancez un sort d'enchantement de niveau 1 ou plus qui ne cible "
            "qu'une seule créature, vous pouvez cibler une seconde créature, à condition qu'elle soit à portée "
            "du sort. Vous ne dépensez pas d'emplacement supplémentaire."
        ),
        "Altération mémorielle": (
            "Quand vous lancez un sort d'enchantement pour charmer une ou plusieurs créatures, vous pouvez faire "
            "en sorte que l'une d'elles ne se rende pas compte qu'elle a été charmée. De plus, une fois avant la "
            "fin du sort, vous pouvez utiliser votre action pour lui faire oublier une partie du temps passé sous "
            "le charme : elle fait un jet de sauvegarde d'Intelligence (DD " + DD + ") et, en cas d'échec, "
            "oublie jusqu'à 1 + votre modificateur de Charisme heures (minimum 1), sans dépasser la durée du sort."
        ),
    },
    "École d'Évocation": {
        "Évocateur érudit & Façonneur de sorts": (
            "Évocateur érudit : l'or et le temps pour copier un sort d'évocation sont divisés par deux. Façonneur "
            "de sorts : quand vous lancez un sort d'évocation qui affecte d'autres créatures que vous voyez, vous "
            "pouvez en choisir un nombre égal à 1 + le niveau du sort. Ces créatures réussissent automatiquement "
            "leur jet de sauvegarde contre le sort et, si elles devaient subir la moitié des dégâts en cas de "
            "réussite, elles n'en subissent aucun."
        ),
        "Sort mineur puissant": (
            "Vos sorts mineurs offensifs atteignent même les créatures qui les esquivent. "
            "Quand une créature réussit son jet de sauvegarde contre l'un de vos sorts mineurs, elle subit "
            "quand même la moitié des dégâts du sort (le cas échéant), mais aucun autre effet du sort."
        ),
        "Évocation renforcée": (
            "Vous ajoutez votre modificateur d'Intelligence à un jet de dégâts de tout sort "
            "d'évocation de magicien que vous lancez. Le bonus s'applique une seule fois par sort, sur un seul "
            "jet de dégâts (pour Projectile magique, à un seul projectile ou à la cible de votre choix), et "
            "s'ajoute aux dégâts contre chaque cible touchée par ce jet."
        ),
        "Surcharge magique": (
            "Quand vous lancez un sort de magicien de niveau 1 à 5 qui inflige des dégâts, vous pouvez infliger "
            "le maximum de dégâts avec ce sort. La première utilisation n'a aucun effet secondaire. Si vous "
            "l'utilisez de nouveau avant la fin d'un repos long, vous subissez 2d12 dégâts nécrotiques par "
            "niveau du sort juste après l'avoir lancé ; chaque utilisation supplémentaire avant le repos long "
            "augmente ces dégâts de 1d12 par niveau du sort. Ces dégâts ignorent résistance et immunité."
        ),
    },
    "École d'Illusion": {
        "Illusionniste érudit & Illusion mineure améliorée": (
            "Illusionniste érudit : l'or et le temps pour copier un sort d'illusion sont divisés par deux. "
            "Illusion mineure améliorée : vous apprenez le sort mineur Illusion mineure (ou un autre sort mineur "
            "de magicien de votre choix si vous le connaissez déjà, sans qu'il compte dans vos sorts mineurs "
            "connus). Quand vous lancez Illusion mineure, vous pouvez créer à la fois un son et une image avec un "
            "seul lancement du sort."
        ),
        "Illusions malléables": (
            "Quand vous lancez un sort d'illusion dont la durée est d'au moins 1 minute, vous pouvez utiliser "
            "votre action pour modifier la nature de cette illusion (en respectant les paramètres normaux du "
            "sort), à condition de voir l'illusion. Vous pouvez ainsi changer son apparence, ses sons ou son "
            "comportement sans relancer le sort."
        ),
        "Double illusoire": (
            "Quand une créature effectue un jet d'attaque contre vous, vous pouvez utiliser votre réaction pour "
            "interposer un double illusoire entre vous et l'attaquant : l'attaque vous rate automatiquement, puis "
            "l'illusion se dissipe. Une fois utilisée, cette aptitude ne peut plus l'être avant la fin d'un "
            "repos court ou long."
        ),
        "Réalité illusoire": (
            "Quand vous lancez un sort d'illusion de niveau 1 ou plus, vous pouvez choisir un "
            "objet inanimé non magique faisant partie de l'illusion et le rendre réel. Vous le faites par une "
            "action bonus à votre tour tant que le sort est actif. L'objet reste réel pendant 1 minute. Il ne "
            "peut pas infliger de dégâts ni nuire directement à quiconque (par exemple, un pont pour traverser "
            "un gouffre ou une porte pour bloquer un couloir)."
        ),
    },
    "École de l'Invocation": {
        "Invocateur érudit & Menue invocation": (
            "Invocateur érudit : l'or et le temps pour copier un sort d'invocation sont divisés par deux. Menue "
            "invocation : par une action, vous faites apparaître dans votre main ou sur le sol, dans un espace "
            "inoccupé à 3 m ou moins, un objet inanimé que vous avez déjà vu. Il ne peut pas mesurer plus de "
            "90 cm de côté ni peser plus de 5 kg, et doit être non magique. Il disparaît au bout de 1 heure, "
            "s'il subit des dégâts ou si vous utilisez de nouveau cette aptitude. L'objet est visiblement magique "
            "(lueur faible de 1,50 m)."
        ),
        "Transposition bienveillante": (
            "Par une action, vous vous téléportez jusqu'à 9 m vers un espace "
            "inoccupé que vous voyez. Vous pouvez aussi choisir un espace occupé par une créature consentante de "
            "taille P ou M à portée : vous échangez alors vos places. Une fois utilisée, l'aptitude se recharge "
            "après un repos long ou lorsque vous lancez un sort d'invocation de niveau 1 ou plus."
        ),
        "Invocation focalisée": (
            "Tant que vous vous concentrez sur un sort d'invocation, votre concentration "
            "ne peut pas être rompue à la suite des dégâts que vous subissez. Les autres causes (être neutralisé, "
            "mourir, lancer un autre sort à concentration) y mettent toujours fin."
        ),
        "Convocations durables": (
            "Toute créature que vous convoquez ou créez avec un sort d'invocation gagne "
            "30 points de vie temporaires à son apparition. Ces points de vie temporaires durent tant que la "
            "créature est présente et ne se cumulent pas avec d'autres points de vie temporaires."
        ),
    },
    "École de la Nécromancie": {
        "Nécromancien érudit & Sinistre moisson": (
            "Nécromancien érudit : l'or et le temps pour copier un sort de nécromancie sont divisés par deux. "
            "Sinistre moisson : une fois par tour, quand vous tuez une ou plusieurs créatures avec un sort de "
            "niveau 1 ou plus, vous regagnez un nombre de points de vie égal à 2 × le niveau du sort, ou à "
            "3 × le niveau du sort s'il s'agit d'un sort de nécromancie. Les créatures artificielles et les "
            "morts-vivants tués ne déclenchent pas cette aptitude."
        ),
        "Serviteurs morts-vivants": (
            "Vous ajoutez Animation des morts à votre grimoire (gratuitement). Quand vous lancez ce sort, vous "
            "pouvez cibler un cadavre ou un tas d'ossements supplémentaire pour créer un mort-vivant de plus. "
            "Chaque mort-vivant que vous créez avec un sort de nécromancie gagne un nombre de points de vie "
            "maximum supplémentaires égal à votre niveau de magicien et ajoute votre bonus de maîtrise à ses jets "
            "de dégâts avec une arme."
        ),
        "Endurci contre la non-vie": (
            "Vous avez la résistance aux dégâts nécrotiques, et votre maximum de "
            "points de vie ne peut pas être réduit. Vous êtes ainsi protégé des effets qui drainent la vie, "
            "comme l'attaque d'un spectre ou d'un vampire."
        ),
        "Commandement des morts-vivants": (
            "Par une action, choisissez un mort-vivant que vous voyez à 18 m ou "
            "moins. Il fait un jet de sauvegarde de Charisme (DD " + DD + "). S'il a une Intelligence de 8 ou "
            "plus, il a l'avantage ; s'il a une Intelligence de 12 ou plus et rate, il peut retenter la "
            "sauvegarde à la fin de chaque heure. En cas d'échec, il devient amical et vous obéit jusqu'à ce que "
            "vous réutilisiez cette aptitude. En cas de réussite, il est immunisé définitivement."
        ),
    },
    "École de la Transmutation": {
        "Transmutateur érudit & Alchimie mineure": (
            "Transmutateur érudit : l'or et le temps pour copier un sort de transmutation sont divisés par deux. "
            "Alchimie mineure : en 10 minutes, vous transformez un objet composé entièrement de bois, pierre (pas "
            "de pierre précieuse), fer, cuivre ou argent en un autre de ces matériaux, à raison de 30 cm cubes "
            "par tranche de 10 minutes. Après 1 heure, ou si vous perdez votre concentration, la matière reprend "
            "sa forme d'origine."
        ),
        "Pierre du transmutateur": (
            "En 8 heures, vous créez une pierre du transmutateur (une seule à la fois). Son porteur gagne un "
            "avantage de votre choix : vision dans le noir sur 18 m ; vitesse +3 m s'il n'est pas encombré ; "
            "maîtrise des jets de sauvegarde de Constitution ; ou résistance aux dégâts d'acide, de froid, de "
            "feu, de foudre ou de tonnerre (au choix). Chaque fois que vous lancez un sort de transmutation de "
            "niveau 1 ou plus, vous pouvez changer l'effet de la pierre si vous l'avez sur vous."
        ),
        "Métamorphe": (
            "Vous ajoutez Métamorphose à votre grimoire. Vous pouvez la lancer sans dépenser d'emplacement, "
            "uniquement sur vous-même, pour prendre la forme d'une bête de facteur de puissance 1 ou moins. Une "
            "fois utilisée de cette façon, l'aptitude se recharge à la fin d'un repos court ou long (vous pouvez "
            "toujours lancer le sort normalement avec un emplacement)."
        ),
        "Maître transmutateur": (
            "Par une action, vous détruisez votre pierre du transmutateur pour produire un effet : transformation "
            "majeure (transmuter un objet non magique de 1,50 m de côté au plus en un autre de même taille et "
            "masse, en 10 minutes) ; panacée (une créature touchée récupère tous ses PV et est libérée des "
            "malédictions, maladies, poisons) ; rappel à la vie (vous lancez Rappel à la vie sans emplacement ni "
            "composante) ; ou jouvence (une créature consentante rajeunit de 3d10 ans, minimum 13 ans). Vous "
            "pouvez ensuite créer une nouvelle pierre ; cette aptitude est utilisable une fois par repos long."
        ),
    },
    "Magie de guerre": {
        "Déviation arcanique & Esprit tactique": (
            "Déviation arcanique : quand vous êtes touché par une attaque ou ratez un jet de sauvegarde, vous "
            "pouvez utiliser votre réaction pour gagner +2 à la CA contre cette attaque ou +4 à ce jet de "
            "sauvegarde. Ensuite, jusqu'à la fin de votre prochain tour, vous ne pouvez lancer que des sorts "
            "mineurs. Esprit tactique : vous ajoutez votre modificateur d'Intelligence à vos jets d'initiative."
        ),
        "Surtension": (
            "Vous emmagasinez des surtensions : vous en avez une après chaque repos long, et vous en gagnez une "
            "chaque fois que vous mettez fin à un sort avec Dissipation de la magie ou Contresort. Vous pouvez en "
            "stocker au maximum un nombre égal à votre modificateur d'Intelligence (minimum 1) ; après un repos "
            "court, si vous n'en avez aucune, vous en récupérez une. Une fois par tour, quand vous infligez des "
            "dégâts à une créature ou un objet avec un sort de magicien, vous pouvez dépenser une surtension pour "
            "ajouter des dégâts de force égaux à la moitié de votre niveau de magicien."
        ),
        "Magie durable": (
            "Tant que vous maintenez votre concentration sur un sort, vous bénéficiez d'un bonus de +2 à la CA "
            "et à tous vos jets de sauvegarde. Le bonus disparaît dès que la concentration prend fin."
        ),
        "Linceul déflecteur": (
            "Quand vous utilisez votre Déviation arcanique, vous pouvez faire jaillir "
            "l'énergie magique sur jusqu'à trois créatures de votre choix que vous voyez à 18 m ou moins. "
            "Chacune subit des dégâts de force égaux à la moitié de votre niveau de magicien."
        ),
    },
    "Chantelame": {
        "Formation martiale et artistique & Chant de la lame": (
            "Formation : vous gagnez la maîtrise des armures légères, d'un type d'arme de corps à corps à une "
            "main et de la compétence Représentation (ou d'une autre compétence si vous l'avez déjà). Chant de la "
            "lame : par une action bonus, vous l'activez pour 1 minute si vous ne portez ni armure intermédiaire "
            "ou lourde ni bouclier. Bonus à la CA égal à votre modificateur d'Intelligence (minimum +1), vitesse "
            "de marche +3 m, avantage aux tests de Dextérité (Acrobaties) et bonus égal à votre modificateur "
            "d'Intelligence aux jets de sauvegarde de Constitution pour maintenir la concentration. Il prend fin "
            "si vous êtes neutralisé, enfilez une armure intermédiaire ou lourde ou un bouclier, ou attaquez avec "
            "une arme tenue à deux mains. Utilisations : un nombre de fois égal à votre bonus de maîtrise, "
            "récupérées après un repos long."
        ),
        "Attaque supplémentaire": (
            "Vous pouvez attaquer deux fois, au lieu d'une, quand vous effectuez l'action Attaquer pendant votre "
            "tour. Vous pouvez remplacer l'une de ces attaques par le lancement d'un de vos sorts mineurs de "
            "magicien dont le temps d'incantation est d'une action."
        ),
        "Chant de défense": (
            "Quand vous subissez des dégâts alors que votre Chant de la lame est actif, vous pouvez utiliser "
            "votre réaction pour dépenser un emplacement de sort : les dégâts sont réduits de 5 × le niveau de "
            "l'emplacement dépensé. Par exemple, un emplacement de niveau 3 réduit les dégâts de 15."
        ),
        "Chant de victoire": (
            "Tant que votre Chant de la lame est actif, vous ajoutez votre modificateur d'Intelligence (minimum "
            "+1) aux dégâts de vos attaques avec une arme de corps à corps. De plus, quand vous lancez un sort "
            "par une action pendant votre tour, vous pouvez effectuer une attaque avec une arme par une action "
            "bonus."
        ),
    },
    "Ordre des scribes": {
        "Plume du mage & Grimoire éveillé": (
            "Plume du mage : par une action bonus, vous créez une plume magique Minuscule dans votre main ; elle "
            "écrit sans encre dans la couleur de votre choix, peut effacer ce qu'elle a écrit (action bonus, "
            "1,50 m) et réduit le temps de copie d'un sort à 2 minutes par niveau. Grimoire éveillé : votre "
            "grimoire devient un focaliseur arcanique. Quand vous lancez un sort de magicien avec un emplacement, "
            "vous pouvez remplacer son type de dégâts par celui d'un autre sort de votre grimoire du même niveau. "
            "Une fois par repos long, vous pouvez lancer un sort rituel en un temps d'incantation normal."
        ),
        "Esprit manifesté": (
            "Par une action bonus, l'esprit de votre grimoire apparaît comme un objet spectral "
            "Minuscule dans un espace inoccupé à 18 m ou moins (lumière faible sur 3 m). Il dispose de la vision "
            "dans le noir sur 18 m, et vous pouvez voir et entendre à travers lui. Par une action bonus, vous le "
            "déplacez de 9 m. Quand vous lancez un sort de magicien sur votre tour, vous pouvez le lancer comme "
            "si vous étiez à la place de l'esprit, un nombre de fois égal à votre bonus de maîtrise par repos "
            "long ; au-delà, chaque utilisation supplémentaire vous coûte un emplacement de sort de n'importe quel "
            "niveau. L'esprit disparaît s'il s'éloigne à plus de 90 m de vous ou si vous le congédiez."
        ),
        "Maître scribe": (
            "Après un repos long, vous pouvez toucher une feuille vierge avec votre Plume du mage pour créer un "
            "parchemin magique contenant un sort de niveau 1 ou 2 de votre grimoire dont le temps d'incantation "
            "est d'une action. Lancé depuis ce parchemin, le sort est traité comme s'il était lancé avec un "
            "emplacement de un niveau de plus. Le parchemin disparaît à votre prochain repos long s'il n'a pas "
            "été utilisé. Vous ne pouvez avoir qu'un parchemin de ce type."
        ),
        "Union avec le verbe": (
            "Vous avez l'avantage aux tests d'Intelligence (Arcanes). Quand vous subissez des dégâts alors que "
            "votre esprit manifesté est présent, vous pouvez utiliser votre réaction pour le congédier et annuler "
            "tous ces dégâts. Lancez alors 3d6 : des sorts de votre grimoire dont le total des niveaux est au "
            "moins égal au résultat disparaissent du livre (vous choisissez) jusqu'à ce que vous terminiez 1d6 "
            "repos longs. Utilisable une fois par repos long."
        ),
    },
    "Magie de la Chronurgie": {
        "Conscience temporelle & Déphasage chronal": (
            "Conscience temporelle : vous ajoutez votre modificateur d'Intelligence à vos jets d'initiative. "
            "Déphasage chronal : quand une créature que vous voyez à 9 m ou moins effectue un jet d'attaque, un "
            "test de caractéristique ou un jet de sauvegarde, vous pouvez utiliser votre réaction pour l'obliger "
            "à relancer le d20, après le jet mais avant d'en connaître l'issue ; elle garde le nouveau résultat. "
            "Utilisable deux fois, récupérées après un repos long."
        ),
        "Stase momentanée": (
            "Par une action, choisissez une créature de taille G ou inférieure que vous voyez à 18 m ou moins. "
            "Elle doit réussir un jet de sauvegarde de Constitution (DD " + DD + ") ou être enfermée dans un "
            "champ temporel jusqu'à la fin de votre prochain tour ou jusqu'à ce qu'elle subisse des dégâts : "
            "elle est neutralisée et sa vitesse tombe à 0. Utilisable un nombre de fois égal à votre modificateur "
            "d'Intelligence (minimum 1), récupérées après un repos long."
        ),
        "Suspension arcanique": (
            "Quand vous lancez un sort de niveau 4 ou moins avec un emplacement, vous "
            "pouvez le condenser dans une perle grise pendant 1 heure au lieu de le lancer. Vous ou une autre "
            "créature tenant la perle pouvez, par une action, libérer le sort, qui utilise votre DD de "
            "sauvegarde et votre bonus d'attaque des sorts. Si personne ne le libère, la perle disparaît sans "
            "effet. Utilisable une fois par repos court ou long."
        ),
        "Avenir convergent": (
            "Quand une créature que vous voyez à 18 m ou moins effectue un jet d'attaque, un "
            "test de caractéristique ou un jet de sauvegarde, vous pouvez utiliser votre réaction pour décider "
            "que le d20 donne exactement le nombre nécessaire pour réussir ou pour échouer. Vous subissez alors "
            "un niveau d'épuisement, qui ne peut être retiré que par un repos long."
        ),
    },
    "Magicien du Sang": {
        "Magie viscérale & Sacrifice arcanique": (
            "Magie viscérale : l'or et le temps pour copier un sort de nécromancie ou d'enchantement sont divisés "
            "par deux. Sacrifice arcanique : par une action bonus, vous dépensez un ou plusieurs dés de vie sans "
            "les lancer et subissez 1d6 dégâts nécrotiques par dé dépensé (ces dégâts ne peuvent être ni réduits "
            "ni évités). Vous récupérez un emplacement de sort dont le niveau est égal au nombre de dés dépensés "
            "(niveau 3 maximum et au plus la moitié de votre niveau de magicien). Utilisable une fois par repos "
            "long. Saignée : une fois par tour, quand un de vos sorts de magicien inflige des dégâts, vous pouvez "
            "perdre 1d6 points de vie pour ajouter 1d6 dégâts nécrotiques à une cible touchée, un nombre de fois "
            "égal à votre bonus de maîtrise par repos long."
        ),
        "Pacte de sang": (
            "Quand vous infligez des dégâts à une créature avec un sort de magicien, vous pouvez utiliser une "
            "action bonus pour lier son sang au vôtre. Elle fait un jet de sauvegarde de Constitution (DD " + DD +
            ") ; les morts-vivants et créatures artificielles réussissent automatiquement. En cas d'échec, "
            "pendant 1 minute ou tant qu'elle reste à 18 m ou moins, elle subit un malus de 1d4 à ses jets "
            "d'attaque, et la première fois à chacun de vos tours que vous lui infligez des dégâts avec un sort, "
            "vous regagnez votre bonus de maîtrise + votre modificateur d'Intelligence points de vie. Un seul "
            "pacte à la fois ; utilisable un nombre de fois égal à votre bonus de maîtrise par repos long."
        ),
        "Maîtrise de l'hémomancie": (
            "Vos sorts de magicien ignorent la résistance (mais pas l'immunité) aux dégâts nécrotiques et de "
            "poison. De plus, les points de vie que vous perdez ou les dégâts que vous subissez via Sacrifice "
            "arcanique, Saignée ou vos autres aptitudes de Magicien du Sang ne vous obligent jamais à faire de jet "
            "de sauvegarde de Constitution pour maintenir votre concentration. Enfin, vous avez la résistance aux "
            "dégâts nécrotiques."
        ),
        "Avatar de sang": (
            "Par une action, vous vous drapez d'un manteau de sang pendant 1 minute (une fois par repos long, ou en "
            "dépensant un emplacement de niveau 5 ou plus). Vous êtes immunisé contre les états effrayé et "
            "empoisonné et gagnez une vitesse de vol de 9 m. Par une action bonus à chacun de vos tours, vous "
            "pouvez drainer une créature que vous voyez à 9 m ou moins : jet de sauvegarde de Constitution (DD "
            + DD + "), 4d8 dégâts nécrotiques en cas d'échec ou la moitié en cas de réussite, et vous regagnez "
            "des points de vie égaux à la moitié des dégâts infligés. L'avatar prend fin si vous êtes neutralisé."
        ),
    },
    "Liaison élémentaire": {
        "Affinité élémentaire": (
            "Choisissez un élément : feu, froid, foudre ou acide (vous pouvez en changer chaque fois que "
            "vous gagnez un niveau dans cette classe). Vous gagnez la résistance aux dégâts de cet élément. Quand vous lancez un sort de "
            "magicien qui inflige des dégâts d'acide, de froid, de feu, de foudre ou de tonnerre, vous pouvez "
            "remplacer ce type de dégâts par celui de votre élément. De plus, l'or et le temps pour copier un "
            "sort d'évocation infligeant l'un de ces types de dégâts sont divisés par deux."
        ),
        "Surcharge élémentaire": (
            "Les sorts de magicien que vous lancez ignorent la résistance (mais pas l'immunité) aux dégâts de "
            "votre élément. De plus, quand vous lancez les dés de dégâts d'un sort infligeant des dégâts de votre "
            "élément, vous pouvez traiter tout 1 obtenu sur un dé comme un 2."
        ),
        "Aura élémentaire": (
            "Par une action bonus, vous vous entourez d'une aura de votre élément de 3 m de rayon pendant "
            "1 minute (concentration). Toute créature de votre choix qui entre dans l'aura pour la première fois "
            "lors d'un tour ou y commence son tour subit 2d6 dégâts de votre élément (une fois par tour par "
            "créature). Vous et vos alliés dans l'aura avez la résistance aux dégâts de cet élément. Utilisable "
            "un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Incarner l'élément": (
            "Par une action, vous devenez énergie élémentaire pure pendant 1 minute (une fois par repos long, ou "
            "en dépensant un emplacement de niveau 6 ou plus). Vous êtes immunisé contre les dégâts de votre "
            "élément, gagnez une vitesse de vol de 9 m (vol stationnaire), avez la résistance aux dégâts "
            "contondants, perforants et tranchants non magiques et pouvez traverser un espace large de 2,5 cm "
            "sans vous faufiler. Une fois par tour, quand un de vos sorts inflige des dégâts de votre élément, "
            "vous ajoutez votre modificateur d'Intelligence à un jet de dégâts. L'effet cesse si vous êtes "
            "neutralisé."
        ),
    },
    "Gravure runique": {
        "Inscriptions de pouvoir": (
            "L'or et le temps pour copier un sort d'abjuration sont divisés par deux. À la fin d'un repos long, "
            "vous gravez un nombre de runes égal à votre bonus de maîtrise sur des créatures consentantes ou des "
            "objets (une rune par support) ; elles durent jusqu'à votre prochain repos long. Le porteur peut "
            "consommer sa rune pour en déclencher l'effet : garde (réaction quand il est touché, +2 à la CA contre "
            "cette attaque), endurance (réaction, résistance contre un type de dégâts élémentaires pour un coup), "
            "perspicacité (avantage à un test de caractéristique) ou éclat (lumière vive sur 6 m pendant 1 heure, "
            "sans consommer la rune). Vous pouvez aussi graver une rune lors d'un repos court."
        ),
        "Détonation runique": (
            "Par une action, vous faites exploser l'une de vos runes que vous voyez à 18 m ou moins. Chaque "
            "créature de votre choix à 3 m ou moins de la rune (hormis son porteur) fait un jet de sauvegarde de "
            "Force (DD " + DD + ") : en cas d'échec, elle subit 3d8 dégâts de force et est repoussée de 3 m, ou "
            "la moitié des dégâts sans être repoussée en cas de réussite. Les dégâts passent à 4d8 au niveau 14 "
            "de magicien. La rune est consommée ; une seule détonation par tour."
        ),
        "Barrière de glyphes": (
            "Par une action, vous tracez un cercle de glyphes de 3 m de rayon centré sur un point que vous voyez "
            "à 9 m ou moins, pendant 1 minute (concentration). Les créatures de votre choix dans le cercle "
            "bénéficient d'un abri aux trois quarts (+5 à la CA et aux jets de sauvegarde de Dextérité) contre les "
            "attaques à distance et les sorts provenant de l'extérieur du cercle. Utilisable une fois par repos "
            "long, ou en dépensant un emplacement de niveau 3 ou plus."
        ),
        "Rune d'infinité": (
            "À la fin d'un repos long, vous pouvez dépenser un emplacement de sort de niveau 6 ou moins pour "
            "graver une rune d'infinité contenant un sort de magicien de votre grimoire de ce niveau, dont le "
            "temps d'incantation est d'une action. Jusqu'à votre prochain repos long, vous pouvez déclencher la "
            "rune par une action bonus : le sort est lancé à ce niveau sans dépenser d'emplacement ni de "
            "composante, avec votre DD de sauvegarde et votre bonus d'attaque des sorts. Une seule rune "
            "d'infinité à la fois."
        ),
    },
}

_PHB_LIST = "les écoles du Manuel des joueurs n'ont pas de liste de sorts de sous-classe (sorts toujours préparés)"

_NO_LIST = "liste remplacée par [] (aucune liste de sorts de sous-classe officielle)"

CORRIGE = [
    # --- Classe de base
    ("mineur", "Restauration arcanique", "« moitié du niveau de magicien » sans arrondi ni limite d'1 fois par jour",
     "Niveaux cumulés ≤ moitié du niveau de magicien arrondie au supérieur, aucun emplacement de niveau 6+, une fois par jour après un repos court"),
    ("majeur", "Prospérité des rituels (Optionnel)", "Aptitude inventée, donnée au niveau 3 et marquée optionnelle : supprimée (déjà couverte par Incantation)",
     "L'incantation rituelle fait partie de l'Incantation du magicien dès le niveau 1 (PHB)"),
    ("mineur", "Capacités de classe optionnelles (TCE)", "Formules de sorts mineurs absente : ajoutée au niveau 3 (option Tasha)",
     "Niveau 3 (Tasha) : à la fin d'un repos long, remplacer un sort mineur de magicien connu par un autre"),
    ("mineur", "Signature magique", "Nom non officiel : renommée « Sorts de prédilection »",
     "« Sorts de prédilection » (Signature Spells) : deux sorts de niveau 3, une fois chacun par repos court ou long"),
    ("info", "Maîtrise des sorts", "Ne précise pas le lancement au niveau le plus bas ni le changement par 8 h d'étude",
     "Sorts lancés à leur niveau le plus bas sans emplacement ; remplaçables après 8 heures d'étude"),
    # --- Abjuration
    ("majeur", "École d'Abjuration / Abjurateur érudit & Égide arcanique", "Égide fixe de 20 PV temporaires",
     "PV max de l'égide = 2 × niveau de magicien + modificateur d'Intelligence ; regagne 2 × niveau du sort à chaque abjuration ; ce ne sont pas des PV temporaires"),
    ("mineur", "École d'Abjuration / École projetée", "Nom erroné : renommée", "« Égide projetée » (Projected Ward)"),
    ("mineur", "École d'Abjuration / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, _PHB_LIST),
    ("mineur", "École d'Abjuration / sorts_domaine", "Noms invalides : « Sphère résilient de Otiluke », « Anticipation » (liste vidée)",
     "« Sphère résiliente d'Otiluke » ; « Anticipation » n'existe pas (Contingence ?)"),
    # --- Divination
    ("mineur", "École de Divination / Troisième œil", "Sens choisi « après un repos »",
     "Action pour activer ; dure jusqu'à un repos court ou long ; vision dans le noir 18 m, éthérée 18 m, lecture des langues, ou voir l'invisible 3 m"),
    ("mineur", "École de Divination / Présage renforcé", "Nom erroné : renommée", "« Présage supérieur » (Greater Portent)"),
    ("mineur", "École de Divination / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, _PHB_LIST),
    ("mineur", "École de Divination / sorts_domaine", "Noms invalides : « Langue arcanique », « Pré Cognition » (liste vidée)",
     "Sorts inexistants (Don des langues ? Prémonition ?)"),
    # --- Enchantement
    ("majeur", "École d'Enchantement / Enchanteur érudit & Regard hypnotique", "Limité à 1 fois par repos long ; DD non précisé",
     "Usage illimité ; une même créature n'est plus affectable avant un repos long après la fin de l'effet ou une réussite ; DD des sorts, neutralisée, 1 minute max"),
    ("mineur", "École d'Enchantement / Détournement d'hostilité", "Nom erroné : renommée ; « l'assaillant rate » inexact",
     "« Charme instinctif » : réaction, JS Sagesse, l'attaque est redirigée vers la créature la plus proche"),
    ("mineur", "École d'Enchantement / Enchantement bifide", "Nom erroné : renommée ; ne précise pas « niveau 1+ » ni la portée",
     "« Enchantement partagé » : sort d'enchantement de niveau 1+ à cible unique, seconde cible à portée"),
    ("majeur", "École d'Enchantement / Altération mémorielle", "Durée oubliée fixe de 8 h",
     "Oubli de 1 + modificateur de Charisme heures (minimum 1), JS d'Intelligence, dans la limite de la durée du sort"),
    ("mineur", "École d'Enchantement / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, _PHB_LIST),
    ("mineur", "École d'Enchantement / sorts_domaine", "Noms invalides : « Ennemi suprême », « Forme animale » (liste vidée)",
     "Sorts inexistants ou hors liste du magicien (Formes animales est un sort de druide)"),
    # --- Évocation
    ("mineur", "École d'Évocation / Évocateur érudit & Façonneur de sorts", "Nombre de créatures protégées non précisé",
     "1 + niveau du sort créatures choisies"),
    ("mineur", "École d'Évocation / Sort mineur appuyé", "Nom erroné : renommée", "« Sort mineur puissant » (Potent Cantrip)"),
    ("mineur", "École d'Évocation / Évocation améliorée", "Nom : renommée ; ne précise pas « un seul jet de dégâts »",
     "« Évocation renforcée » : modificateur d'Intelligence ajouté à un jet de dégâts d'un sort d'évocation de magicien"),
    ("info", "École d'Évocation / Surcharge magique", "Dégâts de contrecoup non chiffrés",
     "2d12 nécrotiques par niveau du sort à la 2e utilisation, +1d12 par niveau à chaque utilisation suivante, ignorent résistance/immunité"),
    ("mineur", "École d'Évocation / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, _PHB_LIST),
    # --- Illusion
    ("mineur", "École d'Illusion / Réalité chimérique", "Nom : renommée ; ne précise pas que l'objet ne peut infliger de dégâts",
     "« Réalité illusoire » : objet inanimé non magique, 1 minute, ne peut blesser personne"),
    ("mineur", "École d'Illusion / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, _PHB_LIST),
    ("mineur", "École d'Illusion / sorts_domaine", "Noms invalides : « Mot de mire », « Illusion pathologique » (liste vidée)",
     "Sorts inexistants (Illusion programmée ?)"),
    # --- Invocation
    ("mineur", "École de l'Invocation / Invocateur érudit & Menue invocation", "Taille, portée et durée incomplètes",
     "Action, objet ≤ 90 cm de côté et ≤ 5 kg, à 3 m, dure 1 heure ou jusqu'à ce qu'il subisse des dégâts"),
    ("mineur", "École de l'Invocation / Permutation", "Nom erroné : renommée ; taille de l'allié non précisée",
     "« Transposition bienveillante » : échange avec une créature consentante de taille P ou M"),
    ("mineur", "École de l'Invocation / Invocation consciencieuse & Convocations coriaces", "Noms non officiels : renommées",
     "« Invocation focalisée » (Focused Conjuration) ; « Convocations durables » (Durable Summons)"),
    ("mineur", "École de l'Invocation / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, _PHB_LIST),
    ("mineur", "École de l'Invocation / sorts_domaine", "Noms invalides : « Trou de serrure », « Flèche acidulée de Melf » (liste vidée)",
     "Sort inexistant ; « Flèche acide de Melf »"),
    # --- Nécromancie
    ("majeur", "École de la Nécromancie / Serviteurs morts-vivants", "Bonus « aux jets d'attaque » ; PV max non chiffrés",
     "PV max + niveau de magicien et bonus de maîtrise ajouté aux jets de dégâts avec une arme"),
    ("info", "École de la Nécromancie / Sinistre moisson", "Restriction une fois par tour et exclusion morts-vivants/créatures artificielles absentes",
     "Une fois par tour ; ne fonctionne pas sur morts-vivants ni créatures artificielles"),
    ("mineur", "École de la Nécromancie / Contrôle des morts-vivants", "Portée, avantage selon l'Intelligence et relance horaire absents ; nom non officiel (renommée)",
     "« Commandement des morts-vivants » : action, 18 m, JS Charisme ; avantage si Int ≥ 8, nouvelle sauvegarde chaque heure si Int ≥ 12"),
    ("mineur", "École de la Nécromancie / Insensibilité à la non-vie", "Nom non officiel : renommée",
     "« Endurci contre la non-vie » (Inured to Undeath)"),
    ("mineur", "École de la Nécromancie / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, _PHB_LIST),
    ("mineur", "École de la Nécromancie / sorts_domaine", "Noms invalides : « Pulsion de mort », « cercle de la mort », « Drain de vie » (liste vidée)",
     "Sorts inexistants ; « Cercle de mort »"),
    # --- Transmutation
    ("mineur", "École de la Transmutation / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, _PHB_LIST),
    ("mineur", "École de la Transmutation / sorts_domaine",
     "Noms invalides : « Fait d'armes », « Création de nourriture », « Flottement », « Statue », « Porte des étoiles » (liste vidée)",
     "Sorts inexistants ou incomplets (« Création de nourriture et d'eau », sort de clerc)"),
    # --- Magie de guerre
    ("mineur", "Magie de guerre / Surtension", "Stock maximal et dégâts non chiffrés",
     "Maximum = modificateur d'Intelligence (min 1) ; dégâts de force = moitié du niveau de magicien, une fois par tour"),
    ("mineur", "Magie de guerre / Voile de déviation", "Nombre de cibles, portée et dégâts absents ; nom non officiel (renommée)",
     "« Linceul déflecteur » : jusqu'à 3 créatures à 18 m, dégâts de force = moitié du niveau de magicien"),
    ("mineur", "Magie de guerre / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, "La Magie de guerre (XGE) n'a pas de liste de sorts de sous-classe"),
    # --- Chantelame
    ("majeur", "Chantelame / Formation martiale et artistique & Chant de la lame", "6 utilisations fixes par repos long",
     "Un nombre de fois égal au bonus de maîtrise par repos long (TCE) ; bonus CA = modificateur d'Intelligence (min +1)"),
    ("mineur", "Chantelame / Chant de victoire", "Attaque d'arme en action bonus après un sort absente",
     "TCE : après avoir lancé un sort par une action, une attaque d'arme par une action bonus"),
    ("mineur", "Chantelame / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, "La Chantelame n'a pas de liste de sorts de sous-classe"),
    ("mineur", "Chantelame / sorts_domaine", "Noms invalides : « Longstrider » (anglais), « Châtiment planaire » (liste vidée)",
     "« Grande foulée » ; « Châtiment planaire » n'existe pas"),
    # --- Ordre des scribes
    ("mineur", "Ordre des scribes / source", "Source en anglais « Tasha's Cauldron of Everything » : corrigée",
     "« Chaudron des Merveilles de Tasha », comme les autres entrées"),
    ("majeur", "Ordre des scribes / Érudition réifiée", "6 utilisations fixes par repos long ; nom non officiel (renommée « Esprit manifesté »)",
     "Lancer depuis l'esprit un nombre de fois égal au bonus de maîtrise par repos long (+ en dépensant un emplacement)"),
    ("mineur", "Ordre des scribes / Union avec le verbe", "Coût de 3d6 niveaux de sorts et limite 1/repos long non précisés",
     "Réaction, annule les dégâts, perte de sorts du grimoire totalisant 3d6 niveaux pendant 1d6 repos longs"),
    ("mineur", "Ordre des scribes / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST, "L'Ordre des scribes n'a pas de liste de sorts de sous-classe"),
    ("mineur", "Ordre des scribes / sorts_domaine", "Nom invalide : « Langue arcanique » (liste vidée)", "Sort inexistant"),
    # --- Chronurgie
    ("mineur", "Magie de la Chronurgie / Conscience temporelle & Altération du sort", "« 2/repos » imprécis ; nom (renommée « Conscience temporelle & Déphasage chronal »)",
     "« Déphasage chronal » : réaction, 9 m, deux utilisations par repos long"),
    ("majeur", "Magie de la Chronurgie / Stase momentanée", "Cible « paralysée » ; ni portée ni utilisations",
     "Créature G ou inférieure à 18 m, neutralisée et vitesse 0 jusqu'à la fin de votre prochain tour ; modificateur d'Intelligence utilisations par repos long"),
    ("mineur", "Magie de la Chronurgie / Abri d'arcanes & Altération convergente", "Noms non officiels : renommées",
     "« Suspension arcanique » (Arcane Abeyance) ; « Avenir convergent » (Convergent Future)"),
    ("mineur", "Magie de la Chronurgie / sorts_domaine", "Liste de sorts inventée : " + _NO_LIST,
     "La Chronurgie (Wildemount) n'a pas de liste de sorts de sous-classe"),
    ("mineur", "Magie de la Chronurgie / sorts_domaine", "Noms invalides : « Don des alouettes », « Synapse » (liste vidée)", "Sorts inexistants"),
    # --- Homebrew : noms de sorts
    ("mineur", "Magicien du Sang / sorts_domaine", "Noms invalides : « Vampirisme », « Faux repos », « Rayon d'affaiblissement », « Drain de vie »",
     "Remplacés par « Toucher du vampire », « Mort simulée », « Rayon affaiblissant », « Énervation » (noms de la base)"),
    ("mineur", "Liaison élémentaire / sorts_domaine", "Noms invalides : « Colonne de feu », « Essaim de météores »",
     "« Colonne de flamme » ; « Nuée de météores »"),
    ("mineur", "Gravure runique / sorts_domaine", "Noms invalides : « Glyphe de garde » / « Glyphe de protection » en double, « Œil mystique »",
     "« Glyphe de protection » (nom de la base) ; doublon remplacé par « Protection contre une énergie » ; « Oeil magique »"),
    ("mineur", "Magicien du Sang / Pacte de sang", "Faute de frappe « touquez »", "« touchez »"),
    ("mineur", "Magicien du Sang / Maîtrise de l'hémomancie", "Faute « Vos sorts ignorant »", "« Vos sorts ignorent »"),
]

AUDIT = [
    ("info", "Tradition d'arcanes", "Graviturgie (Guide de Wildemount) absente : non ajoutée (aucune opération d'ajout de sous-classe)",
     "Tradition officielle de Wildemount, au même titre que la Chronurgie"),
]
