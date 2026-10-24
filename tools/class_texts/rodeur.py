"""Descriptions enrichies — Rôdeur (PHB, Xanathar, Tasha ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Rodeur"

BASE = {
    "Ennemi juré": (
        "Au niveau 1, vous choisissez un type d'ennemi juré parmi aberrations, bêtes, célestes, créatures artificielles, "
        "dragons, élémentaires, fées, fiélons, géants, créatures monstrueuses, vases, plantes ou morts-vivants, ou bien deux "
        "peuples d'humanoïdes (par exemple gnolls et orcs). Vous avez l'avantage aux tests de Sagesse (Survie) pour pister "
        "vos ennemis jurés et aux tests d'Intelligence pour vous remémorer des informations à leur sujet. Vous apprenez "
        "aussi une langue parlée par l'un d'eux, si elle en a une. Vous choisissez un ennemi juré supplémentaire (et la "
        "langue qui va avec) aux niveaux 6 et 14. L'option de Tasha Ennemi favori peut remplacer cette aptitude."
    ),
    "Ennemi favori (option Tasha)": (
        "Remplace Ennemi juré. Quand vous touchez une créature avec un jet d'attaque, vous pouvez faire appel à votre "
        "lien mystique avec la nature pour la marquer comme ennemi favori pendant 1 minute ou jusqu'à ce que vous perdiez "
        "votre concentration (comme pour un sort). La première fois à chacun de vos tours que vous touchez cette cible, y "
        "compris lors du coup qui la marque, elle subit 1d4 dégâts supplémentaires du type de l'arme ou du sort. Vous "
        "pouvez l'utiliser un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos long. Le dé "
        "supplémentaire passe à 1d6 au niveau 6 et à 1d8 au niveau 14."
    ),
    "Explorateur-né": (
        "Au niveau 1, choisissez un terrain de prédilection (arctique, côte, désert, forêt, montagne, marais, prairie ou "
        "Outreterre). Pour les tests d'Intelligence ou de Sagesse liés à ce terrain, votre bonus de maîtrise est doublé si "
        "vous maîtrisez la compétence utilisée. Lorsque vous y voyagez une heure ou plus : le terrain difficile ne ralentit "
        "pas votre groupe, vous ne pouvez pas vous perdre sauf par magie, vous restez sur vos gardes même en pistant, en "
        "cartographiant ou en cherchant de la nourriture, vous avancez discrètement à allure normale si vous êtes seul, "
        "vous trouvez deux fois plus de nourriture, et en pistant vous apprenez le nombre exact, la taille et "
        "l'ancienneté du passage des créatures. Terrain supplémentaire aux niveaux 6 et 10. L'option de Tasha "
        "Explorateur expert peut remplacer cette aptitude."
    ),
    "Explorateur expert (option Tasha)": (
        "Remplace Explorateur-né. Habile (niveau 1) : choisissez une compétence que vous maîtrisez ; votre bonus de "
        "maîtrise est doublé pour les tests qui l'utilisent. Vous apprenez aussi deux langues de votre choix. Les autres "
        "bénéfices de cette option arrivent au niveau 6 (Vagabond) et au niveau 10 (Infatigable)."
    ),
    "Style de combat": (
        "Au niveau 2, vous adoptez un style de combat qui vous est propre ; vous ne pouvez pas choisir deux fois le même "
        "style. Options du PHB : Archerie (+2 aux jets d'attaque avec les armes à distance), Défense (+1 à la CA si vous "
        "portez une armure), Duel (+2 aux dégâts quand vous maniez une arme de corps à corps à une main et aucune autre "
        "arme), Combat à deux armes (vous ajoutez votre modificateur de caractéristique aux dégâts de l'attaque de la main "
        "secondaire). Options de Tasha : Combat à l'aveugle (vision aveugle sur 3 m), Guerrier druidique (deux sorts mineurs "
        "de druide au choix, lancés avec la Sagesse) et Combat aux armes de lancer (dégainer une arme de lancer fait partie "
        "de l'attaque, +2 aux dégâts avec une arme lancée). Avec la Polyvalence martiale de Tasha, vous pouvez changer de "
        "style à chaque niveau d'Amélioration de caractéristique."
    ),
    "Incantation": (
        "À partir du niveau 2, vous lancez des sorts de rôdeur grâce à la magie de la nature, en utilisant la Sagesse. "
        "DD de sauvegarde des sorts = 8 + votre bonus de maîtrise + votre modificateur de Sagesse ; modificateur d'attaque "
        "des sorts = votre bonus de maîtrise + votre modificateur de Sagesse. Vous êtes un demi-lanceur : 2 emplacements "
        "du 1er niveau au niveau 2, 3 au niveau 3, puis des emplacements du 2e niveau au niveau 5, du 3e au niveau 9, du "
        "4e au niveau 13 et du 5e au niveau 17 ; ils se récupèrent après un repos long. Vous connaissez 2 sorts au niveau "
        "2, puis un de plus aux niveaux 3, 5, 7, 9, 11, 13, 15, 17 et 19 (11 au niveau 19). Chaque fois que vous gagnez "
        "un niveau dans cette classe, vous pouvez remplacer un sort connu par un autre sort de rôdeur d'un niveau que vous "
        "pouvez lancer. Les rôdeurs ne lancent pas de sorts en rituel. Option de Tasha : la liste de sorts du rôdeur "
        "s'enrichit de sorts supplémentaires (liste étendue)."
    ),
    "Focaliseur d'incantation (option Tasha)": (
        "Au niveau 2, vous pouvez utiliser un focaliseur druidique (branche de gui, bâton en bois vivant, totem…) comme "
        "focaliseur d'incantation pour vos sorts de rôdeur, à la place des composantes matérielles sans coût indiqué."
    ),
    "Archétype de rôdeur": (
        "Au niveau 3, vous choisissez un archétype de rôdeur (conclave) qui incarne votre idéal : Chasseur, Maître des "
        "bêtes (PHB), Traqueur des ténèbres, Arpenteur de l'horizon, Tueur de monstres (Xanathar), Gardien de l'essaim, "
        "Vagabond féerique (Tasha), Cavalier draconique (Fizban) ou une option de la communauté. Il vous accorde des "
        "aptitudes aux niveaux 3, 7, 11 et 15. Les archétypes de Xanathar et Tasha ajoutent aussi des sorts toujours "
        "connus aux niveaux de rôdeur 3, 5, 9, 13 et 17, qui ne comptent pas dans votre nombre de sorts connus."
    ),
    "Conscience primitive": (
        "Au niveau 3, par une action, vous dépensez un emplacement de sort de rôdeur pour vous mettre à l'écoute de la "
        "nature ; pendant 1 minute par niveau de l'emplacement, vous savez si l'un des types de créatures suivants se "
        "trouve à 1,5 km ou moins de vous (jusqu'à 9 km dans votre terrain de prédilection) : aberrations, célestes, "
        "dragons, élémentaires, fées, fiélons et morts-vivants. Vous n'apprenez ni leur nombre ni leur position. L'option "
        "de Tasha Conscience primordiale peut remplacer cette aptitude."
    ),
    "Conscience primordiale (option Tasha)": (
        "Remplace Conscience primitive. Vous apprenez des sorts supplémentaires à mesure que vous progressez : "
        "Communication avec les animaux (niveau 3), Sens animal (5), Communication avec les plantes (9), Localisation de "
        "créature (13) et Communion avec la nature (17). Ils ne comptent pas dans vos sorts connus, et vous pouvez lancer "
        "chacun d'eux une fois sans emplacement de sort, cette utilisation gratuite se récupérant après un repos long."
    ),
    "Polyvalence martiale (option Tasha)": (
        "Chaque fois que vous atteignez un niveau qui accorde une Amélioration de caractéristique (4, 8, 12, 16, 19), "
        "vous pouvez remplacer un style de combat que vous connaissez par un autre style de combat accessible aux rôdeurs. "
        "Ce remplacement représente l'évolution de votre entraînement martial."
    ),
    "Attaque supplémentaire": (
        "À partir du niveau 5, lorsque vous effectuez l'action Attaquer à votre tour, vous pouvez porter deux attaques au "
        "lieu d'une. Cette aptitude ne se cumule pas avec une autre Attaque supplémentaire issue d'une autre classe. Un "
        "Maître des bêtes (PHB) peut remplacer l'une de ces attaques par l'ordre donné à son compagnon d'attaquer."
    ),
    "Ennemi juré et Explorateur-né (améliorations)": (
        "Au niveau 6, vous choisissez un ennemi juré supplémentaire (et apprenez une langue qu'il parle) ainsi qu'un "
        "terrain de prédilection supplémentaire. Si vous utilisez les options de Tasha, le dé d'Ennemi favori passe à 1d6 "
        "et Explorateur expert vous accorde Vagabond à la place du terrain supplémentaire."
    ),
    "Vagabond (option Tasha)": (
        "Au niveau 6, si vous avez pris Explorateur expert : votre vitesse de marche augmente de 1,50 m et vous gagnez une "
        "vitesse d'escalade et une vitesse de nage égales à votre vitesse de marche."
    ),
    "Déplacement terrestre": (
        "À partir du niveau 8, traverser un terrain difficile non magique ne vous coûte aucun déplacement supplémentaire. "
        "Vous pouvez aussi traverser une végétation non magique sans être ralenti et sans subir de dégâts de ses épines, "
        "ronces ou autres dangers similaires. Enfin, vous avez l'avantage aux jets de sauvegarde contre les plantes créées "
        "ou manipulées magiquement pour entraver les mouvements, comme celles du sort Enchevêtrement."
    ),
    "Explorateur-né (amélioration)": (
        "Au niveau 10, vous choisissez un terrain de prédilection supplémentaire, avec tous les bénéfices d'Explorateur-né. "
        "Si vous utilisez l'option de Tasha Explorateur expert, vous gagnez Infatigable à la place."
    ),
    "Infatigable (option Tasha)": (
        "Au niveau 10, si vous avez pris Explorateur expert : par une action, vous gagnez 1d8 + votre modificateur de "
        "Sagesse points de vie temporaires (minimum 1). Utilisable un nombre de fois égal à votre bonus de maîtrise, "
        "récupérées après un repos long. De plus, chaque fois que vous terminez un repos court, votre niveau d'épuisement "
        "éventuel diminue de 1."
    ),
    "Camouflage": (
        "Au niveau 10, en passant 1 minute à vous couvrir de boue, de terre, de plantes, de suie ou d'autres matériaux "
        "naturels, vous vous camouflez. Tant que vous restez immobile contre une surface solide au moins aussi grande que "
        "vous (arbre, mur), vous gagnez un bonus de +10 à vos tests de Dextérité (Discrétion). Vous perdez ce bénéfice dès "
        "que vous vous déplacez ou utilisez une action ou une réaction, et devez recommencer. L'option de Tasha Voile de "
        "la nature peut remplacer cette aptitude."
    ),
    "Voile de la nature (option Tasha)": (
        "Remplace Camouflage. Au niveau 10, par une action bonus, vous puisez dans la nature pour devenir invisible, avec "
        "tout ce que vous portez ou transportez, jusqu'au début de votre prochain tour. Utilisable un nombre de fois égal "
        "à votre bonus de maîtrise, récupérées après un repos long."
    ),
    "Disparition": (
        "À partir du niveau 14, vous pouvez effectuer l'action Se cacher par une action bonus à votre tour. De plus, vous "
        "ne pouvez plus être pisté par des moyens non magiques, à moins que vous ne choisissiez délibérément de laisser une "
        "piste. Le pistage magique (sorts de localisation, divination) reste possible."
    ),
    "Ennemi juré (amélioration)": (
        "Au niveau 14, vous choisissez un ennemi juré supplémentaire et apprenez une langue qu'il parle. Avec l'option de "
        "Tasha, le dé d'Ennemi favori passe à 1d8."
    ),
    "Sens sauvages": (
        "Au niveau 18, vos sens développent une acuité surnaturelle. Quand vous attaquez une créature que vous ne pouvez "
        "pas voir, cette incapacité ne vous impose pas de désavantage à votre jet d'attaque. Vous connaissez aussi "
        "l'emplacement de toute créature invisible située à 9 m ou moins de vous, à condition qu'elle ne soit pas cachée et "
        "que vous ne soyez ni aveuglé ni assourdi."
    ),
    "Tueur d'ennemis": (
        "Au niveau 20, vous devenez un chasseur hors pair. Une fois à chacun de vos tours, vous pouvez ajouter votre "
        "modificateur de Sagesse au jet d'attaque ou au jet de dégâts d'une attaque portée contre l'un de vos ennemis jurés "
        "(ou la créature marquée par votre Ennemi favori si vous utilisez l'option de Tasha). Vous pouvez décider de "
        "l'utiliser avant ou après le jet, mais avant que ses effets ne soient appliqués."
    ),
}

SUB = {
    "Chasseur": {
        "Proie du chasseur": (
            "Au niveau 3, choisissez une option. Tueur de colosses : une fois par tour, quand vous touchez avec une arme "
            "une créature à qui il manque des points de vie, elle subit 1d8 dégâts supplémentaires. Tueur de géants : quand "
            "une créature de taille G ou plus que vous pouvez voir, située à 1,50 m ou moins, vous touche ou vous rate "
            "avec une attaque, vous pouvez utiliser votre réaction pour l'attaquer juste après. Briseur de hordes : une "
            "fois à chacun de vos tours, quand vous portez une attaque avec une arme, vous pouvez porter une autre attaque "
            "avec la même arme contre une autre créature située à 1,50 m ou moins de la cible initiale et à votre portée."
        ),
        "Tactique défensive": (
            "Au niveau 7, choisissez une option. Échapper à la horde : les attaques d'opportunité contre vous ont un "
            "désavantage. Défense contre les attaques multiples : quand une créature vous touche avec une attaque, vous "
            "gagnez +4 à la CA contre toutes ses attaques suivantes pendant le reste du tour. Volonté d'acier : vous avez "
            "l'avantage aux jets de sauvegarde contre l'état effrayé."
        ),
        "Attaque multiple": (
            "Au niveau 11, choisissez une option. Volée : par une action, vous portez une attaque à distance contre "
            "n'importe quel nombre de créatures situées à 3 m ou moins d'un point que vous voyez à portée de votre arme ; "
            "il vous faut une munition par cible et vous faites un jet d'attaque séparé pour chacune. Attaque "
            "tourbillonnante : par une action, vous portez une attaque au corps à corps contre chaque créature de votre "
            "choix située à 1,50 m ou moins de vous, avec un jet d'attaque séparé pour chaque cible."
        ),
        "Défense de chasseur supérieure": (
            "Au niveau 15, choisissez une option. Dérobade : quand un effet vous permet un jet de sauvegarde de Dextérité "
            "pour réduire de moitié des dégâts, vous ne subissez aucun dégât en cas de réussite et la moitié en cas "
            "d'échec. Résister à la marée : quand une créature hostile vous rate avec une attaque au corps à corps, vous "
            "pouvez utiliser votre réaction pour l'obliger à répéter la même attaque contre une autre créature de votre "
            "choix (autre qu'elle-même). Esquive instinctive : quand un attaquant que vous voyez vous touche, vous pouvez "
            "utiliser votre réaction pour réduire de moitié les dégâts de cette attaque."
        ),
    },
    "Maître des bêtes": {
        "Compagnon du rôdeur": (
            "Au niveau 3, vous liez une bête de taille M ou inférieure et de FP 1/4 ou moins. Ajoutez votre bonus de "
            "maîtrise à sa CA, à ses jets d'attaque et de dégâts, ainsi qu'à ses jets de sauvegarde et compétences "
            "maîtrisés ; ses PV maximum valent le plus élevé entre sa valeur normale et 4 × votre niveau de rôdeur. Elle "
            "agit à votre tour : par votre action, vous lui ordonnez Attaquer, Foncer, Se désengager, Esquiver ou Aider "
            "(dès le niveau 5, vous pouvez porter une attaque d'arme en plus quand elle attaque). Si elle meurt, 8 heures "
            "suffisent pour en lier une autre. L'option de Tasha Compagnon primal peut remplacer cette aptitude."
        ),
        "Compagnon primal (option Tasha)": (
            "Remplace Compagnon du rôdeur. Vous invoquez une bête primale de la terre, de la mer ou du ciel. CA 13 + votre "
            "bonus de maîtrise ; PV 5 + 5 × votre niveau de rôdeur (ciel : 4 + 4 × votre niveau de rôdeur) ; ses attaques "
            "utilisent votre modificateur d'attaque des sorts et infligent 1d8 + 2 + votre bonus de maîtrise (mer 1d6, "
            "ciel 1d4 + 3). Elle agit juste après vous et Esquive par défaut ; une action bonus lui fait faire une autre "
            "action, ou vous sacrifiez une de vos attaques pour qu'elle attaque. Morte depuis moins d'une heure, elle "
            "revient avec tous ses PV en dépensant une action et un emplacement de sort."
        ),
        "Entraînement exceptionnel": (
            "Au niveau 7, à chacun de vos tours où votre compagnon n'attaque pas, vous pouvez utiliser une action bonus "
            "pour lui ordonner de Foncer, de Se désengager, d'Esquiver ou d'Aider à son tour. De plus, ses attaques sont "
            "considérées comme magiques pour surmonter la résistance et l'immunité aux attaques non magiques. Version "
            "Tasha (Compagnon primal) : quand vous lui ordonnez une action par une action bonus, il peut aussi Foncer, Se "
            "désengager, Esquiver ou Aider par une action bonus, et chacun de ses coups peut infliger des dégâts de force "
            "au lieu de son type habituel."
        ),
        "Fureur bestiale": (
            "Au niveau 11, quand vous ordonnez à votre compagnon d'effectuer l'action Attaquer, il peut porter deux "
            "attaques, ou utiliser son action Attaques multiples s'il en possède une. Version Tasha : en outre, la "
            "première fois à chaque tour que la bête touche une créature affectée par votre sort Marque du chasseur, elle "
            "lui inflige des dégâts de force supplémentaires égaux au bonus de ce sort (1d6)."
        ),
        "Partage des sorts": (
            "Au niveau 15, quand vous lancez un sort qui vous cible vous-même, vous pouvez aussi l'appliquer à votre "
            "compagnon animal, à condition qu'il se trouve à 9 m ou moins de vous. Le sort n'utilise qu'un seul "
            "emplacement et une seule concentration (par exemple Peau d'écorce, Liberté de mouvement, Passage sans trace "
            "ou Grande foulée)."
        ),
    },
    "Traqueur des ténèbres": {
        "Magie du traqueur des ténèbres": (
            "Au niveau 3, vous apprenez Déguisement, puis Corde enchantée (niveau 5), Peur (9), Invisibilité supérieure "
            "(13) et Apparence trompeuse (17). Ces sorts comptent comme des sorts de rôdeur pour vous mais pas dans votre "
            "nombre de sorts connus."
        ),
        "Embusqué redoutable": (
            "Au niveau 3, vous ajoutez votre modificateur de Sagesse à vos jets d'initiative. Au début de votre premier "
            "tour de chaque combat, votre vitesse de marche augmente de 3 m jusqu'à la fin du tour, et si vous effectuez "
            "l'action Attaquer ce tour-là, vous pouvez porter une attaque d'arme supplémentaire dans le cadre de cette "
            "action ; si elle touche, elle inflige 1d8 dégâts supplémentaires du type de l'arme."
        ),
        "Vision des ombres": (
            "Au niveau 3, vous gagnez la vision dans le noir à 18 m (ou sa portée augmente de 9 m si vous l'aviez déjà). "
            "Dans l'obscurité, vous êtes invisible pour toute créature qui compte sur la vision dans le noir pour vous "
            "voir ; les autres sens ou la vision véritable vous perçoivent normalement."
        ),
        "Esprit de fer": (
            "Au niveau 7, vous avez appris à résister aux puissances qui tentent de vous briser l'esprit. Vous gagnez la "
            "maîtrise des jets de sauvegarde de Sagesse. Si vous la possédez déjà, vous gagnez à la place la maîtrise des "
            "jets de sauvegarde d'Intelligence ou de Charisme (au choix, une seule des deux)."
        ),
        "Rafale du traqueur": (
            "Au niveau 11, vous frappez avec une rapidité surnaturelle. Une fois à chacun de vos tours, quand vous ratez "
            "une attaque avec une arme, vous pouvez porter une autre attaque avec une arme dans le cadre de la même action. "
            "Combinée à Embusqué redoutable, cette aptitude rend votre premier tour de combat particulièrement fiable."
        ),
        "Esquive des ombres": (
            "Au niveau 15, chaque fois qu'une créature effectue un jet d'attaque contre vous sans avoir l'avantage, vous "
            "pouvez utiliser votre réaction pour lui imposer un désavantage à ce jet. Vous devez décider avant de savoir "
            "si l'attaque touche ou rate."
        ),
    },
    "Arpenteur de l'horizon": {
        "Magie de l'arpenteur de l'horizon": (
            "Au niveau 3, vous apprenez Protection contre le mal et le bien, puis Foulée brumeuse (niveau 5), Hâte (9), "
            "Bannissement (13) et Cercle de téléportation (17). Ces sorts comptent comme des sorts de rôdeur pour vous mais "
            "pas dans votre nombre de sorts connus."
        ),
        "Détection de portail": (
            "Au niveau 3, par une action, vous percevez la distance et la direction du portail planaire le plus proche "
            "situé à 1,5 km ou moins de vous. Une fois utilisée, cette aptitude se récupère après un repos court ou long."
        ),
        "Guerrier planaire": (
            "Au niveau 3, par une action bonus, choisissez une créature que vous voyez à 9 m ou moins. La prochaine fois "
            "que vous la touchez avec une arme ce tour-ci, tous les dégâts de l'attaque deviennent des dégâts de force et "
            "elle subit 1d8 dégâts de force supplémentaires (2d8 à partir du niveau 11)."
        ),
        "Pas éthéré": (
            "Au niveau 7, par une action bonus à votre tour, vous lancez le sort Forme éthérée sans dépenser "
            "d'emplacement de sort, mais le sort prend fin à la fin du tour en cours. Vous pouvez ainsi traverser murs et "
            "créatures ou échapper à une empoignade avant de revenir sur le plan matériel. Une fois par repos court ou long."
        ),
        "Frappe à distance": (
            "Au niveau 11, quand vous effectuez l'action Attaquer, vous pouvez vous téléporter jusqu'à 3 m avant chaque "
            "attaque, vers un espace inoccupé que vous voyez. Si vous attaquez au moins deux créatures différentes avec "
            "cette action, vous pouvez porter une attaque supplémentaire contre une troisième créature."
        ),
        "Défense spectrale": (
            "Au niveau 15, quand vous subissez des dégâts d'une attaque, vous pouvez utiliser votre réaction pour obtenir "
            "la résistance à tous les dégâts de cette attaque pour ce tour, en déphasant partiellement votre corps à "
            "travers le multivers."
        ),
    },
    "Tueur de monstres": {
        "Magie du tueur de monstres": (
            "Au niveau 3, vous apprenez Protection contre le mal et le bien, puis Zone de vérité (niveau 5), Cercle "
            "magique (9), Bannissement (13) et Immobilisation de monstre (17). Ces sorts comptent comme des sorts de rôdeur "
            "pour vous mais pas dans votre nombre de sorts connus."
        ),
        "Sens du chasseur": (
            "Au niveau 3, par une action, choisissez une créature que vous voyez à 18 m ou moins ; vous apprenez ses "
            "immunités, résistances et vulnérabilités aux dégâts (si elle est protégée de la divination, vous apprenez "
            "qu'elle n'en a aucune). Utilisable un nombre de fois égal à votre modificateur de Sagesse (minimum 1), "
            "récupérées après un repos long."
        ),
        "Proie du tueur": (
            "Au niveau 3, par une action bonus, désignez une créature que vous voyez à 18 m ou moins. La première fois à "
            "chaque tour que vous la touchez avec une arme, elle subit 1d6 dégâts supplémentaires du type de l'arme. "
            "L'effet dure jusqu'à ce que vous terminiez un repos court ou long, ou jusqu'à ce que vous désigniez une autre "
            "cible."
        ),
        "Défense surnaturelle": (
            "Au niveau 7, chaque fois que la cible de votre Proie du tueur vous oblige à faire un jet de sauvegarde, et "
            "chaque fois que vous faites un test de caractéristique pour échapper à son empoignade, vous ajoutez 1d6 à "
            "votre jet."
        ),
        "Némésis des mages": (
            "Au niveau 11, quand vous voyez une créature lancer un sort ou se téléporter à 18 m ou moins de vous, vous "
            "pouvez utiliser votre réaction pour tenter de l'en empêcher magiquement. La créature doit réussir un jet de "
            "sauvegarde de Sagesse contre votre DD de sauvegarde des sorts (8 + votre bonus de maîtrise + votre "
            "modificateur de Sagesse), sinon son sort ou sa téléportation échoue et est gaspillé. Une fois par repos court "
            "ou long."
        ),
        "Contre-attaque du tueur": (
            "Au niveau 15, si la cible de votre Proie du tueur vous oblige à faire un jet de sauvegarde, vous pouvez "
            "utiliser votre réaction pour porter une attaque d'arme contre elle, avant de lancer la sauvegarde. Si "
            "l'attaque touche, vous réussissez automatiquement votre jet de sauvegarde, en plus des effets normaux de "
            "l'attaque."
        ),
    },
    "Gardien des nuées": {
        "Magie du gardien de l'essaim": (
            "Au niveau 3, vous apprenez le sort mineur Main de mage (la main prend la forme de votre essaim) et le sort "
            "Lueurs féeriques, puis Toile d'araignée (niveau 5), Forme gazeuse (9), Œil magique (13) et Fléau d'insectes "
            "(17). Ces sorts comptent comme des sorts de rôdeur pour vous mais pas dans votre nombre de sorts connus."
        ),
        "Essaim rassemblé": (
            "Au niveau 3, un essaim d'esprits de la nature (insectes, oiseaux, pixies…) vous entoure. Une fois à chacun "
            "de vos tours, juste après avoir touché une créature avec une attaque, vous pouvez choisir un effet : la cible "
            "subit 1d6 dégâts perforants ; ou elle doit réussir un jet de sauvegarde de Force contre votre DD de sauvegarde "
            "des sorts (8 + votre bonus de maîtrise + votre modificateur de Sagesse) ou être déplacée horizontalement de "
            "4,50 m au maximum dans la direction de votre choix ; ou l'essaim vous déplace de 1,50 m horizontalement vers "
            "un espace inoccupé que vous voyez, sans provoquer d'attaque d'opportunité."
        ),
        "Marée frémissante": (
            "Au niveau 7, par une action bonus, l'essaim vous soulève : vous gagnez une vitesse de vol de 3 m et pouvez "
            "faire du surplace pendant 1 minute ou jusqu'à ce que vous soyez incapable d'agir. Utilisable un nombre de "
            "fois égal à votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Essaim puissant": (
            "Au niveau 11, les dégâts de l'Essaim rassemblé passent de 1d6 à 1d8. Une créature qui rate la sauvegarde de "
            "Force contre l'essaim (DD 8 + votre bonus de maîtrise + votre modificateur de Sagesse) est en outre jetée à "
            "terre. Quand l'essaim vous déplace, il vous accorde un abri partiel (demi-abri) jusqu'au début de votre "
            "prochain tour."
        ),
        "Dispersion de l'essaim": (
            "Au niveau 15, quand vous subissez des dégâts, vous pouvez utiliser votre réaction pour obtenir la résistance "
            "à ces dégâts ; vous vous dissolvez alors dans votre essaim et vous téléportez vers un espace inoccupé que vous "
            "voyez à 9 m ou moins, où vous réapparaissez avec lui. Utilisable un nombre de fois égal à votre bonus de "
            "maîtrise, récupérées après un repos long."
        ),
    },
    "Vagabond féérique": {
        "Magie du vagabond féerique": (
            "Au niveau 3, vous apprenez Charme-personne, puis Foulée brumeuse (niveau 5), Dissipation de la magie (9), "
            "Porte dimensionnelle (13) et Double illusoire (17). Ces sorts comptent comme des sorts de rôdeur pour vous "
            "mais pas dans votre nombre de sorts connus. Vous gagnez aussi un don féerique, trait cosmétique tiré de la "
            "table de Tasha (ailes de papillon illusoires, fleurs dans les cheveux, odeur de pluie…)."
        ),
        "Frappes redoutables": (
            "Au niveau 3, une fois à chacun de vos tours, quand vous touchez une créature avec une arme, vous pouvez lui "
            "infliger 1d4 dégâts psychiques supplémentaires. Ce dé passe à 1d6 au niveau 11."
        ),
        "Charme de l'autre monde": (
            "Au niveau 3, vous ajoutez votre modificateur de Sagesse (minimum +1) à tous vos tests de Charisme. Vous "
            "gagnez aussi la maîtrise d'une compétence au choix parmi Persuasion, Représentation et Tromperie."
        ),
        "Torsion envoûtante": (
            "Au niveau 7, vous avez l'avantage aux jets de sauvegarde contre les états charmé et effrayé. De plus, quand "
            "vous ou une créature que vous voyez à 36 m ou moins réussissez une sauvegarde contre ces états, vous pouvez "
            "utiliser votre réaction pour forcer une autre créature que vous voyez à 36 m ou moins à réussir un jet de "
            "sauvegarde de Sagesse contre votre DD de sauvegarde des sorts (8 + votre bonus de maîtrise + votre "
            "modificateur de Sagesse), sinon elle est charmée ou effrayée (au choix) par vous pendant 1 minute ; elle "
            "répète la sauvegarde à la fin de chacun de ses tours."
        ),
        "Renforts féeriques": (
            "Au niveau 11, vous connaissez le sort Convocation de fée, qui ne compte pas dans vos sorts connus, et le "
            "lancez sans composante matérielle. Vous pouvez le lancer une fois sans emplacement de sort, récupéré après un "
            "repos long. Chaque fois que vous le lancez, vous pouvez renoncer à la concentration : sa durée devient alors "
            "1 minute. (Vos Frappes redoutables passent aussi à 1d6 à ce niveau.)"
        ),
        "Vagabond des brumes": (
            "Au niveau 15, vous pouvez lancer Foulée brumeuse sans dépenser d'emplacement de sort un nombre de fois égal à "
            "votre modificateur de Sagesse (minimum 1), récupérées après un repos long. De plus, chaque fois que vous "
            "lancez Foulée brumeuse, vous pouvez emmener une créature consentante que vous voyez à 1,50 m ou moins : elle "
            "se téléporte vers un espace inoccupé de son choix à 1,50 m ou moins de votre point d'arrivée."
        ),
    },
    "Traqueur de sang": {
        "Pistage hématologique & Lame sanguine": (
            "Au niveau 3. Pistage hématologique : vous avez l'avantage aux tests de Sagesse (Survie) pour pister, et de "
            "Sagesse (Perception) pour repérer, toute créature ayant perdu des points de vie au cours des 48 dernières "
            "heures ; par une action, vous connaissez la direction de la plus proche de ces créatures située à 1,5 km ou "
            "moins. Lame sanguine : une fois à chacun de vos tours, quand vous touchez une créature avec une arme, vous "
            "pouvez dépenser un dé de vie : lancez-le, la cible subit autant de dégâts nécrotiques supplémentaires et "
            "devient « saignante » jusqu'à la fin de votre prochain tour. Sorts connus : Frayeur (3), Rayon affaiblissant "
            "(5), Toucher du vampire (9), Flétrissement (13), Contagion (17)."
        ),
        "Frayeur prédatrice": (
            "Au niveau 7, quand une créature à qui il manque des points de vie vous rate avec une attaque, vous pouvez "
            "utiliser votre réaction pour l'obliger à réussir un jet de sauvegarde de Sagesse contre un DD égal à 8 + votre "
            "bonus de maîtrise + votre modificateur de Sagesse, sinon elle est effrayée par vous jusqu'à la fin de votre "
            "prochain tour. Utilisable un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos long. "
            "Vous avez aussi l'avantage aux jets de sauvegarde contre l'état effrayé."
        ),
        "Exécution vampirique": (
            "Au niveau 11, quand vous infligez les dégâts de Lame sanguine, vous regagnez un nombre de points de vie égal "
            "aux dégâts nécrotiques infligés (une fois par tour). Si cette attaque est un coup critique ou réduit à 0 point "
            "de vie une créature saignante, le dé de vie dépensé vous est rendu. Une créature artificielle ou un "
            "mort-vivant ne peut pas saigner et ne déclenche pas ce soin."
        ),
        "Forme du prédateur écarlate": (
            "Au niveau 15, par une action bonus, vous prenez la forme d'une ombre sanguine pendant 1 minute : vous avez la "
            "résistance aux dégâts contondants, perforants et tranchants, l'avantage aux tests de Dextérité (Discrétion) "
            "dans la pénombre ou les ténèbres, et une fois à chacun de vos tours, vous pouvez dépenser 3 m de déplacement "
            "pour vous téléporter jusqu'à 9 m vers un espace inoccupé situé à 1,50 m ou moins d'une créature saignante que "
            "vous voyez. Une fois par repos long, ou en dépensant un emplacement de sort du 3e niveau ou supérieur."
        ),
    },
    "Artisan des pièges": {
        "Fabrication de pièges & Pose rapide": (
            "Au niveau 3, vous gagnez la maîtrise des outils de bricoleur. Lors d'un repos court ou long, vous fabriquez "
            "un nombre de pièges égal à votre bonus de maîtrise (ils se dégradent au repos long suivant). Pose rapide : "
            "par une action bonus, vous posez un piège dans un espace inoccupé à 1,50 m ou moins (ou le lancez à 4,50 m "
            "max.) ; il couvre une case de 1,50 m et se déclenche quand une créature y entre ou y termine son tour. DD de "
            "sauvegarde et de détection (Sagesse (Perception)) = 8 + votre bonus de maîtrise + votre modificateur de "
            "Sagesse. Immobilisant : JS de Dextérité ou entravé (action et test de Force contre le DD pour se libérer). "
            "Aveuglant : JS de Constitution ou aveuglé jusqu'à la fin de son prochain tour. Explosif : JS de Dextérité, "
            "2d6 dégâts de feu, moitié en cas de réussite. Au plus votre bonus de maîtrise pièges actifs à la fois. "
            "Sorts connus : Alarme (3), Immobilisation de personne (5), Glyphe de protection (9), Fabrication (13), "
            "Mur de force (17)."
        ),
        "Adaptation du terrain": (
            "Au niveau 7, vous et les créatures de votre choix ignorez les effets de vos propres pièges. Vous avez "
            "l'avantage aux tests pour repérer et désamorcer les pièges, et le terrain difficile non magique ne vous gêne "
            "pas pour en poser. Quand l'un de vos pièges se déclenche, vous pouvez utiliser votre réaction pour le réarmer "
            "aussitôt (il reste en place), un nombre de fois égal à votre modificateur de Sagesse (minimum 1) par repos long."
        ),
        "Charges concentrées": (
            "Au niveau 11, vos pièges sont perfectionnés. Le piège explosif inflige 3d6 + votre modificateur de Sagesse "
            "dégâts de feu et jette à terre une créature qui rate sa sauvegarde. Le piège immobilisant inflige en outre "
            "1d6 + votre modificateur de Sagesse dégâts perforants. Le piège aveuglant rend aussi la cible assourdie sur un "
            "échec. Une même créature ne subit les dégâts que d'un seul de vos pièges par tour."
        ),
        "Zone de mort": (
            "Au niveau 15, par une action, vous reliez jusqu'à trois de vos pièges actifs situés à 9 m ou moins les uns des "
            "autres. Quand l'un se déclenche, tous se déclenchent simultanément et chacun affecte les créatures situées "
            "dans un rayon de 3 m autour de lui au lieu de sa seule case. Une créature prise dans plusieurs zones ne "
            "subit les dégâts qu'une fois mais cumule les états. Une fois par repos long, ou en dépensant un emplacement de "
            "sort du 3e niveau ou supérieur."
        ),
    },
}

# Écarts restant volontairement non corrigés
AUDIT = [
    ("info", "Rôdeur / sous-classes",
     "Cavalier draconique (Drakewarden, Fizban) absent : les FIXES ne permettent pas de créer une sous-classe, ajout "
     "laissé à une évolution des données",
     "Fizban's Treasury of Dragons : archétype officiel optionnel"),
    ("info", "sorts_domaine (toutes sous-classes)",
     "Format conservé : niveaux stockés comme éléments de liste ('1'…'5') entre les noms de sorts, car "
     "Engine.domain_spells (et ses tests) lit ce format « paires » pour le rôdeur ; tools/check_fixes.py signale ces "
     "marqueurs comme sorts absents",
     "Format à normaliser (paires nom/niveau ou dictionnaire) en même temps que le moteur"),
    ("info", "Gardien des nuées",
     "Nom de la sous-classe non officiel : non renommée pour ne pas casser les fiches existantes (aptitudes renommées "
     "Essaim rassemblé / Essaim puissant / Dispersion de l'essaim)",
     "Tasha (FR) : Gardien de l'essaim (Swarmkeeper)"),
    ("info", "Vagabond féérique",
     "Orthographe « féérique » du nom de sous-classe : non renommée pour ne pas casser les fiches existantes",
     "« féerique »"),
]

# Écarts résolus (FIXES + nouvelles descriptions)
CORRIGE = [
    # --- Aptitudes de base ---
    ("majeur", "Ennemi juré / Explorateur passionné (Optionnel)",
     "L'option décrite (expertise, vitesse, nage/escalade) est celle d'Explorateur expert, pas un remplaçant d'Ennemi juré",
     "Tasha remplace Ennemi juré par Ennemi favori : marque 1 min (concentration), +1d4 (1d6 niv. 6, 1d8 niv. 14), bonus de maîtrise fois/repos long"),
    ("mineur", "Ennemi juré / Explorateur passionné (Optionnel)",
     "Description incomplète : langue apprise et ennemis supplémentaires absents",
     "PHB : une langue de l'ennemi, ennemi juré supplémentaire aux niveaux 6 et 14"),
    ("mineur", "Explorateur natif / Explorateur habile (Optionnel)",
     "Noms non officiels « Explorateur natif » / « Explorateur habile »",
     "PHB : Explorateur-né ; Tasha : Explorateur expert (Habile 1, Vagabond 6, Infatigable 10)"),
    ("majeur", "Rôdeur / niveaux 6, 10 et 14",
     "Aucune entrée pour les améliorations d'Ennemi juré / Explorateur-né",
     "Niveau 6 : ennemi + terrain supplémentaires ; niveau 10 : terrain supplémentaire ; niveau 14 : ennemi supplémentaire (ou Vagabond niv. 6 / Infatigable niv. 10 de Tasha)"),
    ("mineur", "Rôdeur / options de Tasha",
     "Options « Capacités de classe optionnelles » absentes : styles de combat supplémentaires, Focaliseur d'incantation, Polyvalence martiale, sorts additionnels",
     "Tasha : focaliseur druidique (niv. 2), changement de style/sort aux niveaux d'ASI, liste de sorts étendue"),
    ("mineur", "Vigilance arcanique / Conscience de la nature",
     "Noms non officiels ; description (« créatures magiques ») imprécise",
     "PHB : Conscience primitive (emplacement dépensé, 1 min/niveau, 1,5 km ou 9 km) ; Tasha : sorts gratuits Communication avec les animaux, Sens animal, etc."),
    ("mineur", "Camouflage / Invisibilité temporelle (Optionnel)",
     "Nom « Invisibilité temporelle » et nombre d'utilisations absents",
     "Tasha : Voile de la nature, action bonus, invisible jusqu'au début du prochain tour, bonus de maîtrise fois/repos long"),
    ("mineur", "Camouflage / Invisibilité temporelle (Optionnel)",
     "Le +10 en Discrétion et la minute de préparation ne sont pas indiqués",
     "PHB : 1 minute de camouflage, +10 aux tests de Discrétion tant qu'immobile contre une surface"),
    ("majeur", "Disparition",
     "« Ne peut plus être traqué par des moyens magiques »",
     "Ne peut plus être pisté par des moyens NON magiques (sauf s'il le souhaite)"),
    ("mineur", "Sens des bêtes",
     "Nom non officiel et portée de 9 m absente",
     "Sens sauvages : pas de désavantage contre les créatures non vues ; position des invisibles non cachées à 9 m"),
    ("mineur", "Style de combat",
     "Styles de Tasha (Combat à l'aveugle, Guerrier druidique, Armes de lancer) non mentionnés",
     "Tasha ajoute ces trois styles au rôdeur"),
    # --- Chasseur ---
    ("majeur", "Chasseur / Proie du chasseur",
     "« Tueur de géants (+1d8 sur cible blessée) » confond deux options",
     "Tueur de colosses = +1d8 une fois par tour sur cible blessée ; Tueur de géants = attaque en réaction contre une créature G+ à 1,50 m"),
    ("mineur", "Chasseur / Tactique défensive",
     "« Tactique de défense contre les géants » et « Volonté de fer » n'existent pas",
     "Défense contre les attaques multiples (+4 CA contre le même attaquant) et Volonté d'acier (avantage contre effrayé)"),
    ("mineur", "Chasseur / Attaque multiple",
     "Zone de la Volée non précisée ; nom « Salve »",
     "Volée : créatures à 3 m d'un point visible à portée ; Attaque tourbillonnante : créatures à 1,50 m"),
    ("mineur", "Chasseur / Défense de chasseur supérieure",
     "« Déplacement fluide » n'existe pas ; « Esquive totale » mal nommée",
     "Options : Dérobade, Résister à la marée, Esquive instinctive"),
    # --- Maître des bêtes ---
    ("majeur", "Maître des bêtes / Compagnon du rôdeur / Compagnon primordial",
     "Bonus fixe « +6 » à CA, attaque, dégâts et JS",
     "Bonus = bonus de maîtrise du rôdeur ; PV = max(normaux, 4 × niveau de rôdeur)"),
    ("mineur", "Maître des bêtes / Compagnon du rôdeur / Compagnon primordial",
     "Profils du Compagnon primal de Tasha absents",
     "CA 13 + bonus de maîtrise, PV 5 + 5 × niveau (ciel 4 + 4 ×), attaque = attaque des sorts, 1d8 + 2 + bonus de maîtrise"),
    ("mineur", "Maître des bêtes / Entraînement exceptionnel & Attaque de la bête magique",
     "Esquiver absent et attaques magiques non décrites",
     "Foncer, Se désengager, Esquiver ou Aider en action bonus ; attaques magiques (Tasha : dégâts de force)"),
    ("info", "Maître des bêtes / Fureur bestiale",
     "Bonus Marque du chasseur de la version Tasha non mentionné",
     "Tasha : +1d6 de force la 1re fois par tour contre une cible de Marque du chasseur"),
    ("mineur", "Maître des bêtes / Lien partagé",
     "Nom non officiel",
     "PHB : Partage des sorts"),
    # --- Traqueur des ténèbres ---
    ("majeur", "Traqueur des ténèbres / sorts_domaine",
     "Liste fausse : Nappe de brouillard, Flou, Rapidité, « Insondable » (inexistant)",
     "Déguisement, Corde enchantée, Peur, Invisibilité supérieure, Apparence trompeuse"),
    ("mineur", "Traqueur des ténèbres / Embuscade effrayante & Vision des ombres",
     "« Invisibilité totale dans les ténèbres » ; bonus d'initiative non chiffré",
     "Invisible seulement pour les créatures qui comptent sur la vision dans le noir ; initiative + modificateur de Sagesse"),
    ("mineur", "Traqueur des ténèbres / Mental d'acier",
     "Typo « Inteligence » ; « Sagesse/Charisme/Intelligence » ambigu ; nom",
     "Esprit de fer : maîtrise JS Sagesse, sinon Intelligence OU Charisme"),
    ("mineur", "Traqueur des ténèbres / Esquive des ombres",
     "Condition omise",
     "Utilisable seulement si l'attaquant n'a pas l'avantage"),
    # --- Arpenteur de l'horizon ---
    ("majeur", "Arpenteur de l'horizon / sorts_domaine",
     "Lévitation, Clairvoyance et Porte dimensionnelle ne sont pas les sorts du conclave",
     "Protection contre le mal et le bien, Foulée brumeuse, Hâte, Bannissement, Cercle de téléportation"),
    ("majeur", "Arpenteur de l'horizon / Détection de portail & Guerrier planaire",
     "+2d8 dès le niveau 3",
     "+1d8 de force au niveau 3, 2d8 au niveau 11"),
    ("mineur", "Arpenteur de l'horizon / Détection de portail & Guerrier planaire",
     "Limitation de Détection de portail absente",
     "Une action, une fois par repos court ou long"),
    ("mineur", "Arpenteur de l'horizon / Pas éthéré",
     "Sort nommé « Périple éthéré » ; durée et recharge imprécises",
     "Forme éthérée, se termine à la fin du tour, une fois par repos court ou long"),
    ("mineur", "Arpenteur de l'horizon / Frappe à distance",
     "« Jusqu'à 3 attaques distinctes » imprécis",
     "Attaque supplémentaire contre une 3e créature si au moins deux créatures différentes ont été attaquées"),
    # --- Tueur de monstres ---
    ("majeur", "Tueur de monstres / sorts_domaine",
     "Protection contre l'énergie et Sonde mentale au lieu des sorts officiels",
     "Protection contre le mal et le bien, Zone de vérité, Cercle magique, Bannissement, Immobilisation de monstre"),
    ("majeur", "Tueur de monstres / Sens du chasseur & Proie du tueur",
     "Sens du chasseur : 1/repos long",
     "Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long"),
    ("mineur", "Tueur de monstres / Némésis des mages",
     "« Contrer » imprécis : téléportation et DD absents",
     "Réaction contre un sort ou une téléportation à 18 m, JS Sagesse contre le DD des sorts, 1/repos court ou long"),
    ("mineur", "Tueur de monstres / Contre-attaque du tueur",
     "Effet principal omis",
     "Si l'attaque touche, la sauvegarde est automatiquement réussie"),
    # --- Gardien de l'essaim ---
    ("majeur", "Gardien des nuées / sorts_domaine",
     "Nappe de brouillard, Lévitation, Vent hurlant, Liberté de mouvement, Appel de la foudre : liste fausse",
     "Main de mage + Lueurs féeriques, Toile d'araignée, Forme gazeuse, Œil magique, Fléau d'insectes"),
    ("mineur", "Gardien des nuées / Magie de la nuée & Nuée magique",
     "Effets d'Essaim rassemblé non décrits",
     "1 fois/tour après un coup : 1d6 perforants, ou JS Force sinon déplacé de 4,50 m, ou vous déplacer de 1,50 m"),
    ("majeur", "Gardien des nuées / Marée frémissante",
     "« 6 fois/repos long » fixe",
     "Un nombre de fois égal au bonus de maîtrise par repos long"),
    ("majeur", "Gardien des nuées / Nuée spirituelle",
     "DD 14 fixe ; « +1d8 » ajouté",
     "DD = DD des sorts ; les 1d6 deviennent 1d8, mise à terre sur échec, demi-abri quand vous êtes déplacé"),
    ("majeur", "Gardien des nuées / Dispersion de la nuée",
     "« 6 fois/repos long » fixe",
     "Un nombre de fois égal au bonus de maîtrise par repos long"),
    # --- Vagabond féerique ---
    ("majeur", "Vagabond féérique / sorts_domaine",
     "Calme des émotions, « Appel de la fée » (inexistant), Domination de personne",
     "Charme-personne, Foulée brumeuse, Dissipation de la magie, Porte dimensionnelle, Double illusoire"),
    ("majeur", "Vagabond féérique / Charme mystique & Don des fées",
     "Bonus fixe +1 aux tests de Charisme",
     "Bonus = modificateur de Sagesse (minimum +1)"),
    ("majeur", "Vagabond féérique / Charme mystique & Don des fées",
     "Frappes redoutables (1d4 psychiques) absentes au niveau 3",
     "Niveau 3 : +1d4 psychiques une fois par tour ; 1d6 au niveau 11"),
    ("mineur", "Vagabond féérique / Coups effroyables & Renforts féériques",
     "Option sans concentration de Convocation de fée omise",
     "Sans composante matérielle ; peut se lancer sans concentration (durée 1 minute)"),
    ("majeur", "Vagabond féérique / Vagabond des brumes",
     "Foulée brumeuse gratuite 1/repos long",
     "Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long"),
    # --- Homebrew ---
    ("mineur", "Traqueur de sang / sorts_domaine",
     "« Vampirisme » n'est pas un nom de sort",
     "Caresse du vampire (Vampiric Touch, 3e niveau) — nom de la base : Toucher du vampire"),
    ("info", "Traqueur de sang / sorts_domaine",
     "Peur (3e niveau) et Flétrissement (4e niveau) placés aux rangs 4 et 5",
     "Liste refaite : Frayeur, Rayon affaiblissant, Toucher du vampire, Flétrissement, Contagion (niveau de sort = palier)"),
]
