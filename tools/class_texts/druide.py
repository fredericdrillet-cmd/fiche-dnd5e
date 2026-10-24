"""Descriptions enrichies — Druide (PHB, Xanathar, Tasha ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Druide"

BASE = {
    "Druidique": (
        "Vous connaissez le druidique, la langue secrète des druides. Vous pouvez la parler et l'utiliser pour "
        "laisser des messages dissimulés. Vous et toute personne connaissant cette langue repérez automatiquement "
        "un tel message ; les autres peuvent remarquer sa présence en réussissant un test de Sagesse (Perception) "
        "DD 15, mais ne peuvent pas le déchiffrer sans recourir à la magie. Il est interdit d'enseigner cette "
        "langue à un non-druide."
    ),
    "Incantation": (
        "Vous lancez des sorts de druide en puisant dans l'essence divine de la nature ; votre caractéristique "
        "d'incantation est la Sagesse. Vous connaissez 2 sorts mineurs de druide (3 au niveau 4, 4 au niveau 10). "
        "Après chaque repos long, vous préparez dans la liste complète des sorts de druide un nombre de sorts égal "
        "à votre modificateur de Sagesse + votre niveau de druide (minimum 1), de niveaux pour lesquels vous avez "
        "des emplacements ; lancer un sort dépense un emplacement de son niveau ou d'un niveau supérieur. DD de "
        "sauvegarde des sorts = 8 + votre bonus de maîtrise + votre modificateur de Sagesse ; modificateur "
        "d'attaque des sorts = votre bonus de maîtrise + votre modificateur de Sagesse. Vous pouvez lancer comme "
        "rituel un sort préparé possédant l'étiquette rituel, et utiliser un focaliseur druidique (branche de gui, "
        "bâton d'if, totem…) à la place des composantes matérielles sans coût indiqué."
    ),
    "Forme sauvage": (
        "Par une action, vous prenez magiquement l'apparence d'une bête que vous avez déjà vue. Vous disposez de 2 "
        "utilisations, récupérées à la fin d'un repos court ou long (utilisations illimitées au niveau 20 avec "
        "Archidruide). Facteur de puissance (FP) maximal : 1/4 sans vitesse de vol ni de nage au niveau 2, 1/2 sans "
        "vitesse de vol au niveau 4, 1 au niveau 8 (Cercle de la Lune : FP 1 dès le niveau 2, puis un FP égal à "
        "votre niveau de druide divisé par 3, arrondi à l'inférieur, à partir du niveau 6 ; la transformation se "
        "fait alors par une action bonus). Vous restez transformé un nombre d'heures égal à la moitié de votre "
        "niveau de druide (arrondi à l'inférieur), jusqu'à ce que vous repreniez votre forme par une action bonus, "
        "ou jusqu'à ce que vous tombiez inconscient, à 0 PV ou mouriez. Sous cette forme, les statistiques de la "
        "bête remplacent les vôtres, mais vous conservez alignement, personnalité, Intelligence, Sagesse, Charisme, "
        "maîtrises de compétences et de jets de sauvegarde (le meilleur bonus s'applique) ; vous ne pouvez pas "
        "utiliser d'actions légendaires ni d'antre. Vous prenez les PV et dés de vie de la bête ; en revenant à "
        "votre forme normale, vous retrouvez les PV que vous aviez avant la transformation, et si vous retombez "
        "ainsi parce que la bête est tombée à 0 PV, les dégâts excédentaires sont reportés sur votre forme normale "
        "(pas d'inconscience si le report ne vous amène pas à 0 PV). Vous ne pouvez ni parler ni lancer de sorts "
        "(avant le niveau 18), mais la transformation ne rompt pas votre concentration sur un sort déjà lancé. "
        "Vous gardez vos aptitudes de classe et de race si la forme le permet physiquement (pas les sens spéciaux "
        "comme la vision dans le noir, sauf si la bête les possède). Votre équipement tombe au sol, fusionne avec "
        "la nouvelle forme ou est porté si la morphologie et la taille de la bête le permettent (choix du MJ)."
    ),
    "Sorts de druide supplémentaires (option Tasha)": (
        "Option de classe du Chaudron des merveilles de Tasha. Si votre MJ l'autorise, la liste des sorts de "
        "druide s'enrichit des sorts suivants, que vous préparez comme n'importe quel sort de druide. Niveau 2 : "
        "Augure, Flamme éternelle, Agrandissement/Rapetissement. Niveau 3 : Aura de vitalité, Arme élémentaire, "
        "Retour à la vie. Niveau 4 : Divination, Bouclier de feu. Niveau 5 : Cône de froid. Niveau 6 : "
        "Pétrification. Niveau 7 : Symbole. Niveau 9 : Prémonition."
    ),
    "Polyvalence des sorts mineurs (option Tasha)": (
        "Option de classe du Chaudron des merveilles de Tasha. Chaque fois que vous atteignez un niveau de druide "
        "qui vous octroie une Amélioration de caractéristique (niveaux 4, 8, 12, 16 et 19), vous pouvez remplacer "
        "l'un de vos sorts mineurs de druide par un autre sort mineur de la liste des sorts de druide."
    ),
    "Compagnon sauvage (option Tasha)": (
        "Option de classe du Chaudron des merveilles de Tasha. Par une action, vous dépensez une utilisation de "
        "Forme sauvage pour lancer le sort Appel de familier sans composantes matérielles. Le familier est une fée "
        "(et non une bête) et prend la forme animale de votre choix. Il disparaît au bout d'un nombre d'heures égal "
        "à la moitié de votre niveau de druide, lorsqu'il tombe à 0 PV, lorsque vous réutilisez cette aptitude ou "
        "lorsque vous mourez. Vous pouvez percevoir par ses sens et lancer vos sorts de contact par son "
        "intermédiaire, comme pour le sort."
    ),
    "Cercle druidique": (
        "Au niveau 2, vous rejoignez un cercle druidique : Lune, Terre, Rêves, Berger (Xanathar), Étoiles, Spores, "
        "Feu sauvage (Tasha) ou un cercle communautaire. Ce choix vous octroie des aptitudes aux niveaux 2, 6, 10 "
        "et 14, ainsi que, pour certains cercles, des sorts de cercle toujours préparés qui ne comptent pas dans le "
        "nombre de sorts que vous pouvez préparer chaque jour."
    ),
    "Forme sauvage améliorée (Nage)": (
        "Au niveau 4, la limite de votre Forme sauvage passe à un FP de 1/2 et vous pouvez adopter la forme de "
        "bêtes possédant une vitesse de nage (requins, crocodiles…), mais toujours pas de vitesse de vol. Les "
        "utilisations (2 par repos court) et la durée (la moitié de votre niveau de druide en heures) restent "
        "inchangées. Le Cercle de la Lune conserve sa propre limite de FP (FP 1 jusqu'au niveau 5)."
    ),
    "Forme sauvage améliorée (Vol)": (
        "Au niveau 8, la limite de votre Forme sauvage passe à un FP de 1 et vous pouvez adopter la forme de bêtes "
        "possédant une vitesse de vol (aigle géant, vautour géant…), en plus de celles qui nagent. Le Cercle de la "
        "Lune utilise à la place un FP maximal égal à votre niveau de druide divisé par 3 (arrondi à "
        "l'inférieur), soit FP 2 au niveau 8."
    ),
    "Corps intemporel": (
        "À partir du niveau 18, la magie primordiale que vous maniez ralentit votre vieillissement : votre corps "
        "ne vieillit que d'un an pour chaque tranche de 10 années écoulées. Vous restez néanmoins vulnérable au "
        "vieillissement magique (fantômes, sort Hâte…), et l'aptitude ne prolonge pas votre espérance de vie "
        "au-delà de ce ralentissement."
    ),
    "Sorts de bête": (
        "À partir du niveau 18, vous pouvez lancer bon nombre de vos sorts de druide sous n'importe quelle forme "
        "adoptée grâce à Forme sauvage. Vous pouvez accomplir les composantes verbales et somatiques d'un sort de "
        "druide sous forme de bête, mais vous êtes incapable de fournir les composantes matérielles, quelles "
        "qu'elles soient (focaliseur compris)."
    ),
    "Archidruide": (
        "Au niveau 20, vous pouvez utiliser Forme sauvage un nombre illimité de fois. De plus, vous pouvez ignorer "
        "les composantes verbales et somatiques de vos sorts de druide, ainsi que les composantes matérielles qui "
        "n'ont pas de coût indiqué et ne sont pas consommées par le sort. Ce bénéfice s'applique sous votre forme "
        "normale comme sous une forme de bête."
    ),
}

SUB = {
    "Cercle de la Lune": {
        "Forme sauvage de combat & Formes du cercle": (
            "Forme sauvage de combat : vous pouvez utiliser Forme sauvage par une action bonus au lieu d'une "
            "action. Tant que vous êtes transformé, vous pouvez par une action bonus dépenser un emplacement de "
            "sort pour récupérer 1d8 PV par niveau de l'emplacement dépensé. Formes du cercle : vous pouvez "
            "adopter la forme de bêtes de FP 1 dès le niveau 2 (sans vol avant le niveau 8, sans nage avant le "
            "niveau 4), puis, à partir du niveau 6, d'un FP maximal égal à votre niveau de druide divisé par 3 "
            "(arrondi à l'inférieur). Utilisations (2 par repos court) et durée (la moitié de votre niveau de "
            "druide en heures) sont celles de Forme sauvage."
        ),
        "Attaques primitives": (
            "À partir du niveau 6, les attaques que vous effectuez sous une forme de bête comptent comme magiques "
            "pour ce qui est de surmonter la résistance et l'immunité aux attaques et dégâts non magiques."
        ),
        "Forme sauvage élémentaire": (
            "À partir du niveau 10, vous pouvez dépenser simultanément deux utilisations de Forme sauvage pour "
            "vous transformer en élémentaire de l'air, de la terre, du feu ou de l'eau (FP 5). Les règles de "
            "Forme sauvage s'appliquent (durée, PV, report des dégâts) ; avec Forme sauvage de combat, la "
            "transformation se fait par une action bonus."
        ),
        "Mille formes": (
            "Au niveau 14, vous pouvez lancer le sort Modification d'apparence à volonté, sans dépenser "
            "d'emplacement de sort. Le sort requiert toujours votre concentration (jusqu'à 1 heure) et vous permet "
            "d'adapter votre corps (respiration aquatique, armes naturelles, changement d'apparence)."
        ),
    },
    "Cercle de la Terre": {
        "Sort mineur de druide supplémentaire & Ressourcement": (
            "Sort mineur supplémentaire : vous apprenez un sort mineur de druide de votre choix en plus de ceux "
            "que vous connaissez. Ressourcement : pendant un repos court, vous pouvez récupérer des emplacements "
            "de sorts dépensés dont la somme des niveaux est au maximum égale à la moitié de votre niveau de "
            "druide (arrondie au supérieur), aucun d'eux ne pouvant être de niveau 6 ou plus (au niveau 6 par "
            "exemple : 3 niveaux, soit un emplacement de niveau 3 ou un de niveau 2 et un de niveau 1). Une fois "
            "cette aptitude utilisée, vous devez terminer un repos long pour la réutiliser."
        ),
        "Sorts de cercle": (
            "Au niveau 2, vous choisissez le terrain où vous êtes devenu druide : Arctique, Côte, Désert, Forêt, "
            "Marais, Montagne, Outreterre ou Prairie (sélecteur « Terrain » de l'onglet Classes, visible "
            "uniquement pour le Cercle de la Terre). Ce lien mystique vous donne deux sorts de cercle aux niveaux "
            "de druide 3, 5, 7 et 9 (sorts de niveau 2, 3, 4 puis 5). Ils sont toujours préparés, ne comptent pas "
            "dans le nombre de sorts que vous pouvez préparer chaque jour et sont considérés comme des sorts de "
            "druide même s'ils n'appartiennent pas à sa liste. La fiche les ajoute automatiquement à l'onglet "
            "Magie selon le terrain choisi (Forêt par défaut)."
        ),
        "Foulée tellurique": (
            "À partir du niveau 6, traverser un terrain difficile non magique ne vous coûte aucun déplacement "
            "supplémentaire. Vous pouvez aussi traverser la végétation non magique sans être ralenti et sans subir "
            "de dégâts de ses épines ou autres dangers. Enfin, vous avez l'avantage aux jets de sauvegarde contre "
            "les plantes créées ou manipulées magiquement pour entraver les déplacements (sort Enchevêtrement, "
            "par exemple)."
        ),
        "Protégé de dame nature": (
            "Au niveau 10, vous ne pouvez plus être charmé ni effrayé par les élémentaires et les fées, et vous "
            "êtes immunisé contre le poison (dégâts et état empoisonné) et les maladies."
        ),
        "Sanctuaire de dame nature": (
            "Au niveau 14, les créatures du monde naturel sentent votre lien avec la nature et hésitent à vous "
            "attaquer. Lorsqu'une bête ou une plante vous attaque, elle doit réussir un jet de sauvegarde de "
            "Sagesse contre votre DD de sauvegarde des sorts (8 + votre bonus de maîtrise + votre modificateur de "
            "Sagesse). En cas d'échec, elle doit choisir une autre cible, sinon son attaque rate automatiquement ; "
            "en cas de réussite, elle est immunisée contre cet effet pendant 24 heures. La créature a conscience "
            "de cet effet avant d'attaquer."
        ),
    },
    "Cercle des Rêves": {
        "Baume de la cour d'été": (
            "Vous disposez d'une réserve de d6 de guérison féerique dont le nombre est égal à votre niveau de "
            "druide ; elle se reconstitue entièrement après un repos long. Par une action bonus, vous choisissez "
            "une créature que vous pouvez voir dans un rayon de 36 m et dépensez jusqu'à un nombre de dés égal à "
            "la moitié de votre niveau de druide : lancez-les, la cible récupère autant de PV que le total obtenu "
            "et gagne en outre 1 PV temporaire par dé dépensé."
        ),
        "Foyer de l'ombre et du clair de lune": (
            "À partir du niveau 6, lorsque vous prenez un repos court ou long, vous pouvez toucher un point pour "
            "y créer une sphère invisible de 9 m de rayon. Pendant le repos, vous et vos alliés dans la sphère "
            "bénéficiez d'un bonus de +5 aux tests de Dextérité (Discrétion) et de Sagesse (Perception), et la "
            "lumière des flammes nues (feu de camp, torches…) situées dans la sphère n'est pas visible de "
            "l'extérieur. L'effet prend fin à la fin du repos ou si vous quittez la sphère."
        ),
        "Chemins secrets": (
            "À partir du niveau 10, vous empruntez les voies cachées du Feywild. Par une action bonus, vous vous "
            "téléportez jusqu'à 18 m vers un espace inoccupé que vous pouvez voir. Alternativement, par une "
            "action, vous téléportez une créature consentante que vous touchez jusqu'à 9 m vers un espace "
            "inoccupé que vous pouvez voir. Utilisations : un nombre de fois égal à votre modificateur de Sagesse "
            "(minimum 1), récupérées après un repos long."
        ),
        "Arpenteur des rêves": (
            "Au niveau 14, lorsque vous terminez un repos court, vous pouvez lancer l'un des sorts suivants sans "
            "dépenser d'emplacement ni de composantes matérielles : Rêve (vous êtes le messager), Scrutation ou "
            "Cercle de téléportation. Ce dernier ouvre un portail vers le dernier endroit, sur le même plan, où "
            "vous avez terminé un repos long, même sans cercle permanent sur place. Une fois utilisée, l'aptitude "
            "se recharge après un repos long."
        ),
    },
    "Cercle du Berger": {
        "Langage de la forêt & Totem spirituel": (
            "Langage de la forêt : vous savez parler, lire et écrire le sylvestre ; les bêtes comprennent vos "
            "paroles et vous savez interpréter leurs bruits et leurs gestes. Totem spirituel : par une action "
            "bonus, vous invoquez un esprit en un point situé à 18 m ou moins ; il crée une aura de 9 m de rayon "
            "pendant 1 minute ou jusqu'à ce que vous soyez neutralisé (1 fois par repos court ou long ; une action "
            "bonus le déplace de 18 m). Ours : chaque créature de votre choix dans l'aura à son apparition gagne "
            "5 + votre niveau de druide PV temporaires, et elles ont l'avantage aux tests et jets de sauvegarde "
            "de Force dans l'aura. Faucon : par une réaction, vous donnez l'avantage à une créature de l'aura qui "
            "attaque une cible elle aussi dans l'aura ; vos alliés ont l'avantage aux tests de Sagesse "
            "(Perception) dans l'aura. Licorne : vos alliés ont l'avantage aux tests pour détecter des créatures "
            "dans l'aura, et lorsque vous lancez un sort de soins avec un emplacement, chaque créature de votre "
            "choix dans l'aura récupère en plus un nombre de PV égal à votre niveau de druide."
        ),
        "Puissant invocateur": (
            "À partir du niveau 6, les bêtes et les fées que vous invoquez ou créez avec un sort gagnent 2 PV "
            "maximum supplémentaires par dé de vie, et les attaques de leurs armes naturelles comptent comme "
            "magiques pour surmonter la résistance et l'immunité aux dégâts non magiques."
        ),
        "Esprit protecteur": (
            "À partir du niveau 10, votre Totem spirituel protège vos invocations : quel que soit l'esprit (Ours, "
            "Faucon ou Licorne), lorsqu'une bête ou une fée invoquée ou créée par l'un de vos sorts termine son "
            "tour dans l'aura, elle récupère un nombre de PV égal à la moitié de votre niveau de druide."
        ),
        "Invocation loyale": (
            "Au niveau 14, lorsque vous tombez à 0 PV ou êtes neutralisé contre votre volonté, vous bénéficiez "
            "immédiatement des effets d'Invocation d'animaux comme si le sort était lancé avec un emplacement de "
            "niveau 9 : quatre bêtes de votre choix de FP 2 ou moins apparaissent à 6 m ou moins de vous et vous "
            "défendent de leur mieux. L'effet dure 1 heure sans concentration. Une fois utilisée, l'aptitude se "
            "recharge après un repos long."
        ),
    },
    "Cercle des Astres": {
        "Carte stellaire & Forme stellaire": (
            "Carte stellaire : vous créez une carte des étoiles (objet Très Petit) qui sert de focaliseur "
            "druidique ; tant que vous l'avez, vous connaissez le sort mineur Assistance et Éclair traçant est "
            "toujours préparé. Vous pouvez lancer Éclair traçant sans dépenser d'emplacement un nombre de fois "
            "égal à votre bonus de maîtrise par repos long. Forme stellaire : par une action bonus, vous dépensez "
            "une utilisation de Forme sauvage pour prendre une forme étoilée pendant 10 minutes (lumière vive sur "
            "3 m, faible sur 3 m de plus) et choisissez une constellation. Archer : à l'activation puis par une "
            "action bonus à chacun de vos tours, attaque de sort à distance (18 m) infligeant 1d8 + votre "
            "modificateur de Sagesse dégâts radiants. Calice : quand vous lancez un sort de soins avec un "
            "emplacement, vous ou une créature à 9 m récupérez 1d8 + votre modificateur de Sagesse PV. Dragon : "
            "un résultat de 9 ou moins au d20 d'un test d'Intelligence ou de Sagesse, ou d'un jet de sauvegarde "
            "de Constitution pour maintenir votre concentration, compte comme un 10."
        ),
        "Présage cosmique": (
            "À partir du niveau 6, après chaque repos long, lancez un dé : sur un résultat pair, vous obtenez "
            "Bonne fortune ; sur un résultat impair, Mauvais sort. Lorsqu'une créature que vous pouvez voir à 9 m "
            "ou moins s'apprête à effectuer un jet d'attaque, un jet de sauvegarde ou un test de caractéristique, "
            "vous pouvez utiliser votre réaction pour ajouter (Bonne fortune) ou soustraire (Mauvais sort) 1d6 à "
            "son jet. Utilisations : un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos "
            "long."
        ),
        "Constellation scintillante": (
            "À partir du niveau 10, les dégâts de l'Archer et les soins du Calice passent de 1d8 à 2d8. Tant que "
            "le Dragon est actif, vous gagnez une vitesse de vol de 6 m et pouvez faire du surplace. De plus, "
            "au début de chacun de vos tours sous forme stellaire, vous pouvez changer de constellation."
        ),
        "Plénitude stellaire": (
            "Au niveau 14, sous forme stellaire, vous devenez partiellement incorporel : vous avez la résistance "
            "aux dégâts contondants, perforants et tranchants."
        ),
    },
    "Cercle des Spores": {
        "Symbiote & Halo de spores": (
            "Halo de spores : lorsqu'une créature que vous pouvez voir entre dans un espace situé à 3 m ou moins "
            "de vous ou y commence son tour, vous pouvez utiliser votre réaction pour lui infliger 1d4 dégâts "
            "nécrotiques, sauf si elle réussit un jet de sauvegarde de Constitution contre 8 + votre bonus de "
            "maîtrise + votre modificateur de Sagesse (1d6 au niveau 6, 1d8 au niveau 10, 1d10 au niveau 14). "
            "Vous connaissez aussi le sort mineur Contact glacial. Symbiote : par une action, vous dépensez une "
            "utilisation de Forme sauvage (sans vous transformer) et gagnez 4 × votre niveau de druide PV "
            "temporaires. Tant que ces PV temporaires durent, les dés de dégâts du Halo sont doublés et vos "
            "attaques d'arme au corps à corps infligent 1d6 dégâts nécrotiques supplémentaires. L'effet dure 10 "
            "minutes, jusqu'à la perte de ces PV temporaires ou jusqu'à ce que vous utilisiez de nouveau Forme "
            "sauvage."
        ),
        "Animation fongique": (
            "À partir du niveau 6, lorsqu'une bête ou un humanoïde de taille P ou M meurt à 3 m ou moins de vous, "
            "vous pouvez utiliser votre réaction pour l'animer : il se relève avec 1 PV en tant que zombi (profil "
            "de zombi). Il agit juste après vous dans l'ordre d'initiative, obéit à vos ordres mentaux et ne peut "
            "effectuer que l'action Attaquer ; il meurt au bout d'1 heure. Utilisations : un nombre de fois égal "
            "à votre modificateur de Sagesse (minimum 1), récupérées après un repos long."
        ),
        "Domination des spores": (
            "À partir du niveau 10, tant que votre Symbiote est actif, vous pouvez par une action bonus projeter "
            "des spores en un point situé à 9 m ou moins, où elles forment un cube de 3 m d'arête pendant 1 "
            "minute. Toute créature qui entre dans le cube ou y commence son tour subit les dégâts de votre Halo "
            "de spores, sauf si elle réussit son jet de sauvegarde de Constitution (une fois par tour au "
            "maximum). Vous ne pouvez pas utiliser la réaction du Halo tant que le cube existe ; il disparaît si "
            "vous le congédiez (action bonus), le relancez ou si le Symbiote prend fin."
        ),
        "Corps fongique": (
            "Au niveau 14, les spores fongiques qui vous imprègnent vous rendent immunisé contre les états "
            "aveuglé, assourdi, effrayé et empoisonné. De plus, tout coup critique contre vous compte comme un "
            "coup normal, sauf si vous êtes neutralisé."
        ),
    },
    "Cercle des Fournaises (Wildfire)": {
        "Convocation des fournaises": (
            "Par une action, vous dépensez une utilisation de Forme sauvage pour invoquer votre esprit du feu "
            "sauvage dans un espace inoccupé à 9 m ou moins. Chaque créature (autre que vous) située à 3 m ou "
            "moins de l'esprit à son apparition doit réussir un jet de sauvegarde de Dextérité contre 8 + votre "
            "bonus de maîtrise + votre modificateur de Sagesse ou subir 2d6 dégâts de feu. L'esprit (élémentaire "
            "de taille P, CA 13, PV 5 + 5 × votre niveau de druide, vitesse 9 m et vol 9 m en surplace, immunité "
            "au feu) agit juste après vous ; il esquive sauf si vous lui donnez un ordre par une action bonus. "
            "Graine de flamme : attaque de sort à distance (18 m), 1d6 + votre bonus de maîtrise dégâts de feu. "
            "Téléportation ardente : il se téléporte avec les créatures consentantes à 1,50 m de lui jusqu'à "
            "4,50 m ; les créatures à 1,50 m de son point de départ réussissent un JS de Dextérité ou subissent "
            "1d6 + votre bonus de maîtrise dégâts de feu. Il reste 1 heure, jusqu'à 0 PV, nouvelle invocation ou "
            "votre mort."
        ),
        "Lien amélioré": (
            "À partir du niveau 6, tant que votre esprit est invoqué, chaque fois que vous lancez un sort qui "
            "inflige des dégâts de feu ou rend des PV, lancez un d8 et ajoutez le résultat à un jet de dégâts ou "
            "de soins de ce sort. De plus, lorsque vous lancez un sort dont la portée n'est pas personnelle, il "
            "peut partir de vous ou de l'esprit."
        ),
        "Flammes cautérisantes": (
            "À partir du niveau 10, lorsqu'une créature de taille P ou plus meurt à 9 m "
            "ou moins de vous ou de votre esprit, une flamme spectrale inoffensive apparaît dans son espace "
            "pendant 1 minute. Quand une créature que vous pouvez voir entre dans cet espace, vous pouvez utiliser "
            "votre réaction pour éteindre la flamme et soit soigner la créature, soit lui infliger des dégâts de "
            "feu : 2d10 + votre modificateur de Sagesse. Utilisations : un nombre de fois égal à votre bonus de "
            "maîtrise, récupérées après un repos long."
        ),
        "Renaissance flamboyante": (
            "Au niveau 14, si votre esprit se trouve à 36 m ou moins de vous lorsque vous tombez à 0 PV et "
            "perdez connaissance, vous pouvez le faire tomber à 0 PV : vous récupérez alors la moitié de vos PV "
            "maximum et vous vous relevez immédiatement. Une fois utilisée, l'aptitude se recharge après un "
            "repos long."
        ),
    },
    "Cercle de la Mutation": {
        "Chair adaptable": (
            "Par une action bonus, vous dépensez une utilisation de Forme sauvage pour remodeler une partie de "
            "votre corps sans vous transformer, pendant 1 heure ou jusqu'à ce que vous l'annuliez (action bonus) "
            "ou utilisiez Forme sauvage. Choisissez une adaptation (modifiable par une action bonus) : vision "
            "dans le noir sur 18 m ; vitesse d'escalade et de nage égales à votre vitesse et respiration "
            "aquatique ; armes naturelles (griffes, crocs ou cornes) magiques avec lesquelles vous êtes maîtrisé, "
            "qui infligent 1d8 + votre modificateur de Sagesse dégâts tranchants, perforants ou contondants et "
            "peuvent utiliser votre Sagesse pour l'attaque. Vous pouvez lancer des sorts normalement sous cette "
            "forme partielle."
        ),
        "Mutations chimériques": (
            "À partir du niveau 6, lorsque vous utilisez Forme sauvage, vous pouvez greffer à votre forme un trait "
            "d'une seconde bête que vous avez déjà vue et dont le FP ne dépasse pas votre limite : une vitesse de "
            "déplacement (vol seulement à partir du niveau 8), un sens (vision aveugle 3 m, odorat aiguisé…), une "
            "attaque naturelle (remplaçant l'une des vôtres) ou un trait passif (amphibie, tactique de groupe, "
            "carapace donnant +2 à la CA). De plus, Chair adaptable vous octroie désormais deux adaptations à la "
            "fois."
        ),
        "Génération alchimique": (
            "À partir du niveau 10, vous avez la résistance aux dégâts d'acide et de poison et l'avantage aux jets "
            "de sauvegarde contre l'état empoisonné. Lorsque vous subissez des dégâts d'acide ou de poison, vous "
            "pouvez utiliser votre réaction pour récupérer 1d10 + votre niveau de druide PV, un nombre de fois "
            "égal à votre bonus de maîtrise par repos long. Enfin, à la fin d'un repos long, un membre ou organe "
            "perdu repousse entièrement."
        ),
        "Forme monstrueuse": (
            "Au niveau 14, vous pouvez dépenser deux utilisations de Forme sauvage pour adopter la forme d'une "
            "aberration ou d'une créature monstrueuse que vous avez déjà vue, de FP maximal égal au tiers de votre "
            "niveau de druide (arrondi à l'inférieur : FP 4 au niveau 14, FP 6 au niveau 18). Les règles de Forme "
            "sauvage s'appliquent (PV de la créature, report des dégâts, durée), mais vous n'obtenez ni ses sorts, "
            "ni ses actions légendaires ou d'antre, ni ses capacités d'incantation innée ; une capacité à "
            "recharge ne peut être utilisée qu'une fois par transformation."
        ),
    },
    "Cercle de la Sangsue": {
        "Lien de fluide vital": (
            "Lorsque vous lancez avec un emplacement un sort de druide qui inflige des dégâts ou rend des PV, "
            "vous pouvez sacrifier 3 PV par niveau de l'emplacement (perte non réductible). Ajoutez alors 1d8 par "
            "niveau de l'emplacement (5d8 maximum) soit aux soins d'une cible, soit aux dégâts infligés à une "
            "cible, ces dégâts supplémentaires étant nécrotiques. Utilisations : un nombre de fois égal à votre "
            "bonus de maîtrise, récupérées après un repos long."
        ),
        "Forme parasitaire": (
            "À partir du niveau 6, vos attaques sous Forme sauvage comptent comme magiques. Une fois par tour, "
            "lorsque vous touchez une créature (ni artificielle ni morte-vivante) avec une attaque au corps à "
            "corps sous forme de bête, vous lui infligez 1d6 dégâts nécrotiques supplémentaires (1d8 au niveau "
            "14) et gagnez autant de PV temporaires que les dégâts nécrotiques infligés."
        ),
        "Emprise de la lymphe": (
            "À partir du niveau 10, par une action, vous créez un champ de sang (sphère de 4,50 m de rayon) en un "
            "point situé à 18 m ou moins, pendant 1 minute (concentration). La zone est un terrain difficile pour "
            "vos ennemis. Une créature de votre choix qui commence son tour dans la zone doit réussir un jet de "
            "sauvegarde de Constitution contre 8 + votre bonus de maîtrise + votre modificateur de Sagesse ou "
            "subir 3d6 dégâts nécrotiques et ne pas pouvoir récupérer de PV jusqu'au début de son prochain tour "
            "(moitié des dégâts en cas de réussite). Une fois gratuite par repos long, puis en dépensant une "
            "utilisation de Forme sauvage."
        ),
        "Sanguisuga suprême": (
            "Au niveau 14, lorsqu'une créature (ni artificielle ni morte-vivante) que vous pouvez voir meurt à 9 m "
            "ou moins de vous, vous pouvez utiliser votre réaction pour absorber son fluide vital : vous "
            "récupérez une utilisation de Forme sauvage ou un emplacement de sort de niveau 3 ou inférieur, et "
            "gagnez un nombre de PV temporaires égal à votre niveau de druide. Une fois utilisée, l'aptitude se "
            "recharge après un repos court ou long."
        ),
    },
}

CORRIGE = [
    ("majeur", "Cercle de la Terre / Sorts de cercle", "Choix du terrain non modélisé (liste Forêt imposée)",
     "Champ « terrains » (8 listes officielles du PHB) + sélecteur « Terrain » dans l'onglet Classes ; les sorts "
     "de cercle suivent le terrain choisi"),
    # --- Classe de base ---
    ("mineur", "Forme sauvage", "Description très incomplète ; « action bonus ou action » ambigu",
     "Action (action bonus seulement pour le Cercle de la Lune) ; 2 utilisations par repos court ou long ; durée = "
     "moitié du niveau de druide en heures ; FP 1/4 (ni vol ni nage) niv. 2, 1/2 (pas de vol) niv. 4, 1 niv. 8 ; "
     "PV de la bête, report des dégâts excédentaires, pas de sorts"),
    ("mineur", "Compagnon sauvage (option Tasha)", "« Esprit familier sous forme de bête » sans détails",
     "Action + 1 utilisation de Forme sauvage : sort Appel de familier sans composante matérielle, familier de "
     "type fée, durée = moitié du niveau de druide en heures (TCE) ; renommée « (option Tasha) »"),
    ("mineur", "Polyvalence des sorts mineurs (option Tasha)", "Option de classe absente",
     "TCE, niveau 4 (à chaque Amélioration de caractéristique) : remplacer un sort mineur de druide par un autre ; "
     "ajoutée"),
    ("info", "Sorts de druide supplémentaires (option Tasha)", "Option de classe non mentionnée",
     "TCE ajoute des sorts à la liste du druide ; ajoutée au niveau 1 avec la liste étendue"),
    ("mineur", "Sorts de bête", "« À l'exception des composantes matérielles coûteuses »",
     "Sous forme de bête, aucune composante matérielle ne peut être fournie (PHB)"),
    ("mineur", "Archidruide", "Omet les composantes matérielles",
     "Ignore aussi les composantes matérielles sans coût et non consommées (PHB)"),
    ("info", "Incantation", "Aucune donnée chiffrée",
     "Sorts mineurs 2/3/4 (niv. 1/4/10) ; sorts préparés = modificateur de Sagesse + niveau de druide ; DD 8 + maîtrise + "
     "Sagesse ; rituels"),
    # --- Cercle de la Lune ---
    ("mineur", "Cercle de la Lune / Forme sauvage de combat & Formes du cercle",
     "Omet la progression de FP au-delà du niveau 2 ; « Guérison sauvage » n'est pas un nom officiel",
     "Formes du cercle : FP 1 au niv. 2, puis niveau de druide / 3 (arrondi inférieur) dès le niv. 6 ; soins "
     "1d8 par niveau d'emplacement inclus dans Forme sauvage de combat ; renommée « Formes du cercle »"),
    ("mineur", "Cercle de la Lune / Mille formes", "Nom « Mille visages » non officiel",
     "Thousand Forms : « Mille formes » (PHB) ; renommée"),
    # --- Cercle de la Terre ---
    ("majeur", "Cercle de la Terre / sorts_domaine",
     "Liste unique ne correspondant à aucun terrain (Nappe de brouillard et Lien avec les bêtes sont du niveau 1, "
     "Fléau et Rappel à la vie absents des listes)",
     "Remplacée par la liste officielle du terrain Forêt (Peau d'écorce, Pattes d'araignée, Appel de la foudre, "
     "Croissance végétale, Divination, Liberté de mouvement, Communion avec la nature, Passage par les arbres)"),
    ("mineur", "Cercle de la Terre / Ressourcement", "Omet la limite d'usage et l'arrondi",
     "Une fois par repos long ; moitié du niveau arrondie au supérieur ; aucun emplacement de niveau 6+"),
    ("mineur", "Cercle de la Terre / Sanctuaire de dame nature", "DD et immunité de 24 h non précisés",
     "JS de Sagesse contre le DD des sorts ; en cas de réussite immunité 24 h"),
    # --- Cercle des Rêves ---
    ("majeur", "Cercle des Rêves / Baume de la cour d'été", "Réserve fixe de 10d6",
     "Réserve de d6 égale au niveau de druide ; au plus la moitié du niveau de druide en dés par action bonus ; "
     "portée 36 m ; 1 PV temporaire par dé ; recharge au repos long"),
    ("majeur", "Cercle des Rêves / Chemins secrets", "1 fois par repos long ; action bonus pour les deux usages",
     "Utilisations = modificateur de Sagesse (min. 1) par repos long ; téléportation d'autrui par une action et "
     "au contact"),
    ("majeur", "Cercle des Rêves / sorts_domaine", "Liste de sorts de cercle inventée",
     "Le Cercle des Rêves (XGE) n'a pas de sorts de cercle : liste vidée"),
    ("mineur", "Cercle des Rêves / sorts_domaine", "Faute de frappe « Calme des emotions »",
     "Sans objet : la liste inventée a été vidée"),
    # --- Cercle du Berger ---
    ("mineur", "Cercle du Berger / Langage de la forêt & Totem spirituel", "Esprit « Aigle » ; utilisation non précisée",
     "Esprits Ours, Faucon, Licorne ; 1 fois par repos court ou long ; aura de 9 m, 1 minute"),
    ("majeur", "Cercle du Berger / Esprit protecteur", "Limité à l'aura du totem de la licorne ; soins non chiffrés",
     "Fonctionne avec n'importe quel Totem spirituel ; soins = moitié du niveau de druide (XGE)"),
    ("majeur", "Cercle du Berger / sorts_domaine", "Liste de sorts de cercle inventée",
     "Le Cercle du Berger (XGE) n'a pas de sorts de cercle : liste vidée"),
    ("mineur", "Cercle du Berger / Invocation loyale", "« Indice de Puissance »",
     "« Facteur de puissance » (FP)"),
    # --- Cercle des Astres ---
    ("majeur", "Cercle des Astres / Présage cosmique", "6 utilisations par repos long",
     "Utilisations = bonus de maîtrise par repos long ; réaction, 9 m, ±1d6"),
    ("mineur", "Cercle des Astres / Carte stellaire & Forme stellaire", "Éclair traçant « gratuitement » sans limite",
     "Éclair traçant sans emplacement un nombre de fois égal au bonus de maîtrise par repos long ; Forme stellaire "
     "par une action bonus, 10 minutes"),
    ("mineur", "Cercle des Astres / Constellation scintillante", "Omet le vol du Dragon",
     "Archer/Calice 2d8 ; Dragon : vitesse de vol 6 m et surplace"),
    ("majeur", "Cercle des Astres / sorts_domaine", "Liste de sorts inventée, dont « Périple planétaire » (inexistant)",
     "Le Cercle des Étoiles (TCE) n'a pas de sorts de cercle ; seule Éclair traçant (toujours préparé via la "
     "Carte stellaire) est conservé"),
    # --- Cercle des Spores ---
    ("majeur", "Cercle des Spores / Animation fongique", "1 fois par repos long",
     "Utilisations = modificateur de Sagesse (min. 1) par repos long (TCE)"),
    ("majeur", "Cercle des Spores / sorts_domaine",
     "« Fléau d'immunité » inexistant ; Fléau d'insectes hors liste ; manquent Doux repos, Confusion, Brume "
     "mortelle, Contagion",
     "Liste officielle : Cécité/Surdité, Doux repos (« Préservation des morts » dans la base), Animation des "
     "morts, Forme gazeuse, Flétrissement, Confusion, Brume mortelle, Contagion"),
    ("mineur", "Cercle des Spores / Symbiote & Halo de spores", "Sort mineur Contact glacial absent ; PV temporaires et progression du Halo non chiffrés",
     "Contact glacial (niv. 2) ; Symbiote = 4 PV temporaires par niveau de druide ; Halo 1d4/1d6/1d8/1d10 "
     "(niv. 2/6/10/14)"),
    # --- Cercle des Fournaises ---
    ("majeur", "Cercle des Fournaises (Wildfire) / Convocation des fournaises", "DD fixe de 14",
     "DD = 8 + bonus de maîtrise + modificateur de Sagesse (DD des sorts)"),
    ("mineur", "Cercle des Fournaises (Wildfire) / Convocation des fournaises",
     "Profil de l'esprit absent ; « durée 1 h » comme aura de dégâts",
     "Esprit : CA 13, PV 5 + 5 × niveau de druide, vol 9 m, Graine de flamme et Téléportation ardente ; les 2d6 "
     "ne s'appliquent qu'à l'apparition"),
    ("mineur", "Cercle des Fournaises (Wildfire) / Lien amélioré", "+1d8 à tout sort de dégâts",
     "Seulement aux sorts infligeant des dégâts de feu ou rendant des PV"),
    ("majeur", "Cercle des Fournaises (Wildfire) / Flammes cautérisantes", "6 utilisations par repos long",
     "Utilisations = bonus de maîtrise par repos long ; 2d10 + modificateur de Sagesse"),
    ("mineur", "Cercle des Fournaises (Wildfire) / Flammes cautérisantes", "Nom non officiel « Cautère spectrale »",
     "Cauterizing Flames : « Flammes cautérisantes » ; renommée"),
    ("mineur", "Cercle des Fournaises (Wildfire) / Renaissance flamboyante", "Limite d'usage non précisée",
     "Une fois par repos long"),
    ("majeur", "Cercle des Fournaises (Wildfire) / sorts_domaine",
     "Châtiment incandescent, Boule de feu, Mur de feu hors liste ; manquent Soins, Croissance végétale, Retour à "
     "la vie, Aura de vie, Bouclier de feu, Colonne de flamme, Soins de groupe",
     "Niv. 2 Mains brûlantes, Soins ; niv. 3 Sphère de feu, Rayon ardent ; niv. 5 Croissance végétale, Retour à la "
     "vie ; niv. 7 Aura de vie, Bouclier de feu ; niv. 9 Colonne de flamme, Soins de groupe"),
    # --- Homebrew : noms de sorts ---
    ("mineur", "Cercle de la Mutation / sorts_domaine", "« Faux repos » et « Altération » n'existent pas",
     "Remplacés par Simulacre de vie (False Life) et Modification d'apparence (Alter Self)"),
    ("info", "Cercle de la Mutation / sorts_domaine", "« Métamorphose suprême » est un sort de niveau 9",
     "Remplacé par Réincarnation (niveau 5, thème de transformation)"),
    ("mineur", "Cercle de la Sangsue / sorts_domaine", "« Vampirism » en anglais ; « Rayon d'affaiblissement » "
     "absent de la base",
     "Remplacés par Toucher du vampire (Vampiric Touch) et Rayon affaiblissant (Ray of Enfeeblement)"),
]

AUDIT = [
    ("info", "Forme sauvage améliorée (Nage) / (Vol)", "Présentées comme des aptitudes distinctes",
     "Ce sont les paliers de la table de Forme sauvage (PHB) ; conservées comme repères de niveau (4 et 8) pour "
     "l'onglet Forme sauvage, non fusionnées"),

    ("info", "Cercle des Astres / nom", "Nom « Cercle des Astres »",
     "Circle of Stars : traduction usuelle « Cercle des Étoiles » ; non renommé pour ne pas casser les fiches "
     "existantes"),
    ("info", "Cercle des Fournaises (Wildfire) / nom", "Nom mêlant français et anglais",
     "Circle of Wildfire : « Cercle du Feu sauvage » ; non renommé pour ne pas casser les fiches existantes"),
]
