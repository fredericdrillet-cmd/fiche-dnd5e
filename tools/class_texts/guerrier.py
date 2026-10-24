"""Descriptions enrichies — Guerrier (PHB, Xanathar, Tasha ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Guerrier"

BASE = {
    "Style de combat": (
        "Vous adoptez un style de combat (un seul exemplaire de chaque style). Archerie : +2 aux jets d'attaque avec "
        "une arme à distance. Défense : +1 à la CA tant que vous portez une armure. Duel : +2 aux dégâts avec une arme "
        "de corps à corps tenue dans une main, sans autre arme. Arme à deux mains : relancez les 1 et 2 des dés de "
        "dégâts d'une arme de corps à corps à deux mains ou polyvalente tenue à deux mains. Combat à deux armes : "
        "ajoutez votre modificateur de caractéristique aux dégâts de l'attaque de la seconde arme. Protection (bouclier "
        "requis) : par une réaction, imposez un désavantage à une attaque visant une créature située à 1,50 m de vous. "
        "Options de Tasha : Combat aveugle (vision aveugle 3 m), Interception (réaction : réduisez de 1d10 + votre "
        "bonus de maîtrise les dégâts subis par une créature à 1,50 m, bouclier ou arme en main), Arme de lancer (+2 "
        "aux dégâts, dégainer fait partie de l'attaque), Combat à mains nues (d6, d8 sans arme ni bouclier ; 1d4 "
        "contondants au début de votre tour à la créature que vous agrippez), Technique supérieure (une manœuvre de "
        "Maître de guerre et un dé de supériorité d6, récupéré après un repos court ou long)."
    ),
    "Polyvalence martiale (option Tasha)": (
        "Capacité de classe optionnelle : chaque fois que vous atteignez un niveau qui vous accorde l'aptitude "
        "Amélioration de caractéristique, vous pouvez remplacer un style de combat que vous connaissez par un autre "
        "style accessible aux guerriers. Si vous connaissez des manœuvres (Maître de guerre ou style Technique "
        "supérieure), vous pouvez à la place remplacer une manœuvre par une autre."
    ),
    "Second souffle": (
        "Par une action bonus lors de votre tour, vous puisez dans vos réserves et récupérez 1d10 + votre niveau de "
        "guerrier points de vie. Une fois utilisée, cette aptitude n'est de nouveau disponible qu'après un repos court "
        "ou long."
    ),
    "Sursaut d'activité": (
        "Lors de votre tour, vous pouvez accomplir une action supplémentaire en plus de votre action normale et d'une "
        "éventuelle action bonus (par exemple une seconde action Attaquer). Une utilisation, récupérée après un repos "
        "court ou long ; deux utilisations entre deux repos à partir du niveau 17, mais jamais plus d'une fois par "
        "tour."
    ),
    "Archétype martial": (
        "Vous choisissez l'archétype qui oriente votre pratique du combat : Champion, Maître de guerre, Chevalier "
        "occulte (PHB), Archer arcanique, Cavalier, Samouraï (Xanathar), Chevalier runique, Soldat psi (Tasha), ou une "
        "création de la communauté. Il vous confère des aptitudes aux niveaux 3, 7, 10, 15 et 18."
    ),
    "Attaque supplémentaire": (
        "Lorsque vous effectuez l'action Attaquer lors de votre tour, vous attaquez deux fois au lieu d'une. Ces "
        "attaques peuvent viser des cibles différentes et vous pouvez vous déplacer entre elles. Le nombre d'attaques "
        "passe à trois au niveau 11 et à quatre au niveau 20."
    ),
    "Indomptable": (
        "Lorsque vous ratez un jet de sauvegarde, vous pouvez le relancer ; vous devez conserver le nouveau résultat. "
        "Une utilisation récupérée après un repos long ; deux utilisations entre deux repos longs à partir du niveau 13 "
        "et trois à partir du niveau 17."
    ),
    "Attaque supplémentaire (2)": (
        "Lorsque vous effectuez l'action Attaquer lors de votre tour, vous attaquez désormais trois fois au lieu d'une. "
        "Combinée à Sursaut d'activité, cette aptitude permet jusqu'à six attaques dans un même tour."
    ),
    "Attaque supplémentaire (3)": (
        "Lorsque vous effectuez l'action Attaquer lors de votre tour, vous attaquez désormais quatre fois au lieu d'une "
        "(huit attaques possibles avec Sursaut d'activité). Aucune autre classe n'atteint ce nombre d'attaques."
    ),
}

SUB = {
    "Champion": {
        "Critique amélioré": (
            "Vos attaques avec une arme infligent un coup critique sur un résultat de 19 ou 20 au d20."
        ),
        "Athlète remarquable": (
            "Vous ajoutez la moitié de votre bonus de maîtrise (arrondie au supérieur) à tout test de Force, de "
            "Dextérité ou de Constitution qui n'utilise pas déjà votre bonus de maîtrise (l'initiative en profite). "
            "De plus, la distance de vos sauts en longueur avec élan augmente d'un nombre de pieds égal à votre "
            "modificateur de Force (environ 30 cm par point)."
        ),
        "Style de combat supplémentaire": (
            "Vous choisissez un second style de combat parmi les options de l'aptitude Style de combat (Archerie, "
            "Défense, Duel, Arme à deux mains, Protection, Combat à deux armes et options de Tasha). Vous ne pouvez "
            "pas prendre deux fois le même style."
        ),
        "Critique supérieur": (
            "Vos attaques avec une arme infligent désormais un coup critique sur un résultat de 18, 19 ou 20 au d20."
        ),
        "Survivant": (
            "Au début de chacun de vos tours, si vous avez au plus la moitié de vos points de vie maximum "
            "mais au moins 1 point de vie, vous regagnez 5 + votre modificateur de Constitution points de vie. "
            "L'effet ne fonctionne pas si vous êtes à 0 point de vie."
        ),
    },
    "Maître de guerre": {
        "Supériorité martiale": (
            "Vous apprenez trois manœuvres (cinq au niveau 7, sept au niveau 10, neuf au niveau 15 ; vous pouvez en "
            "échanger une chaque fois que vous gagnez un niveau dans cette classe) et disposez de quatre dés de supériorité, des d8 (cinq "
            "dés au niveau 7, six au niveau 15). Une seule manœuvre par attaque ; chacune dépense un dé, et tous les "
            "dés reviennent après un repos court ou long. Les dés passent au d10 au niveau 10 et au d12 au niveau 18. "
            "Le DD des manœuvres utilise au choix la Force ou la Dextérité : 8 + votre bonus de maîtrise + votre "
            "modificateur de Force, ou 8 + votre bonus de maîtrise + votre modificateur de Dextérité."
        ),
        "Disciple de la guerre": (
            "Vous obtenez la maîtrise d'un type d'outils d'artisan de votre choix."
        ),
        "Connaître son ennemi": (
            "Si vous passez au moins 1 minute à observer ou à côtoyer une créature hors combat, "
            "vous apprenez si elle vous est égale, supérieure ou inférieure sur deux critères de votre choix parmi : "
            "valeur de Force, de Dextérité ou de Constitution, CA, points de vie actuels, total de niveaux de classe, "
            "niveaux de guerrier. À ce niveau, vous gagnez aussi un cinquième dé de supériorité et deux manœuvres."
        ),
        "Supériorité martiale améliorée (d10)": (
            "Vos dés de supériorité deviennent des d10 (ils passeront au d12 au niveau 18). Vous apprenez également "
            "deux manœuvres supplémentaires à ce niveau (sept au total)."
        ),
        "Implacable": (
            "Lorsque vous lancez l'initiative alors qu'il ne vous reste aucun dé de supériorité, vous "
            "en regagnez un. À ce niveau, vous obtenez aussi votre sixième dé de supériorité et deux nouvelles "
            "manœuvres (neuf au total)."
        ),
        "Supériorité martiale améliorée (d12)": (
            "Vos dés de supériorité deviennent des d12. Vous disposez de six dés, "
            "récupérés après un repos court ou long, et de neuf manœuvres connues."
        ),
    },
    "Chevalier occulte": {
        "Incantation": (
            "Vous apprenez deux sorts mineurs de magicien (trois au niveau 10) et trois sorts de magicien de niveau 1 "
            "(treize au niveau 20), choisis librement dans la liste du magicien parmi l'abjuration et l'évocation, "
            "sauf ceux obtenus aux niveaux 3, 8, 14 et 20 (toutes écoles). Aucune liste de sorts n'est imposée. Vos "
            "emplacements suivent la table du Chevalier occulte (deux emplacements de niveau 1 au niveau 3, jusqu'au "
            "niveau de sort 4 au niveau 19) et reviennent après un repos long. L'Intelligence est votre "
            "caractéristique d'incantation : DD = 8 + votre bonus de maîtrise + votre modificateur d'Intelligence ; "
            "attaque = votre bonus de maîtrise + votre modificateur d'Intelligence."
        ),
        "Lien avec une arme": (
            "Par un rituel d'1 heure (possible pendant un repos court), vous liez une arme à vous (deux armes au "
            "maximum ; liez-en une troisième et vous devez rompre un lien). Tant que vous êtes conscient, vous ne "
            "pouvez pas être désarmé de cette arme. Si elle se trouve sur le même plan d'existence, vous pouvez par "
            "une action bonus la faire apparaître instantanément dans votre main."
        ),
        "Magie de guerre": (
            "Lorsque vous utilisez votre action pour lancer un sort mineur, vous pouvez effectuer une attaque avec une "
            "arme par une action bonus lors du même tour."
        ),
        "Frappe occulte": (
            "Lorsque vous touchez une créature avec une attaque d'arme, elle a un désavantage au "
            "prochain jet de sauvegarde qu'elle effectue contre un sort que vous lancez avant la fin de votre "
            "prochain tour."
        ),
        "Charge arcanique": (
            "Lorsque vous utilisez Sursaut d'activité, vous pouvez vous téléporter jusqu'à 9 m vers un espace "
            "inoccupé que vous voyez, avant ou après l'action supplémentaire."
        ),
        "Magie de guerre améliorée": (
            "Lorsque vous utilisez votre action pour lancer un sort (de n'importe quel "
            "niveau), vous pouvez effectuer une attaque avec une arme par une action bonus lors du même tour."
        ),
    },
    "Archer arcanique": {
        "Savoir de l'archer arcanique": (
            "Vous obtenez la maîtrise d'Arcanes ou de Nature (au choix) et apprenez le sort mineur Prestidigitation "
            "ou Druidisme (au choix)."
        ),
        "Tir arcanique": (
            "Vous connaissez deux options (une de plus aux niveaux 7, 10, 15 et 18). Une fois par tour, lorsque vous touchez avec une flèche tirée d'un arc court ou long, vous "
            "pouvez appliquer une option ; deux utilisations, récupérées après un repos court ou long. DD = 8 + votre "
            "bonus de maîtrise + votre modificateur d'Intelligence. Options : bannissante (JS de Charisme ou bannie "
            "jusqu'à la fin de son prochain tour), charmeuse (2d6 psychiques, JS de Sagesse ou charmée par un allié), "
            "explosive (2d6 de force à 3 m autour de la cible), affaiblissante (2d6 nécrotiques, JS de Constitution "
            "ou dégâts d'arme réduits de moitié), de saisie (2d6 poison, vitesse -3 m, 2d6 tranchants si elle bouge), "
            "perforante (ligne de 9 m, JS de Dextérité, dégâts de l'arme + 1d6 perforants), chercheuse (ignore "
            "l'abri, 1d6 de force), d'ombre (2d6 psychiques, JS de Sagesse ou ne voit pas au-delà de 1,50 m)."
        ),
        "Flèche magique": (
            "Toute flèche non magique que vous tirez avec un arc court ou long devient magique pour surmonter "
            "résistances et immunités aux dégâts non magiques (l'effet cesse dès qu'elle touche ou rate). Vous "
            "apprenez aussi une nouvelle option de Tir arcanique."
        ),
        "Tir incurvé": (
            "Lorsque vous ratez une attaque avec une flèche magique, vous pouvez par une action bonus relancer le jet "
            "d'attaque contre une autre cible située à 18 m ou moins de la cible initiale."
        ),
        "Tir infaillible": (
            "Lorsque vous lancez l'initiative alors qu'il ne vous reste aucune utilisation de Tir "
            "arcanique, vous en regagnez une. Vous apprenez aussi une nouvelle option de Tir arcanique."
        ),
        "Tir arcanique amélioré": (
            "Les dégâts de vos options de Tir arcanique augmentent : 2d6 deviennent 4d6 (explosive, charmeuse, "
            "affaiblissante, de saisie, d'ombre ; la bannissante inflige aussi 2d6 de force), et 1d6 devient 2d6 "
            "(perforante, chercheuse). Vous apprenez en outre une dernière option."
        ),
    },
    "Cavalier": {
        "Maîtrise supplémentaire": (
            "Vous obtenez la maîtrise d'une compétence parmi Dressage, Histoire, Perspicacité, Représentation ou "
            "Persuasion, ou apprenez une langue de votre choix."
        ),
        "Né en selle": (
            "Vous avez l'avantage aux JS pour ne pas tomber de votre monture. Si vous en tombez d'une hauteur de 3 m "
            "ou moins sans être neutralisé, vous retombez sur vos pieds. Monter ou descendre de votre monture ne vous "
            "coûte que 1,50 m de mouvement."
        ),
        "Marque inébranlable": (
            "Lorsque vous touchez une créature avec une attaque d'arme de corps à corps, elle est marquée jusqu'à la "
            "fin de votre prochain tour (l'effet cesse si vous êtes neutralisé ou si un autre cavalier la marque). "
            "Tant qu'elle est à 1,50 m de vous, elle a un désavantage aux jets d'attaque qui ne vous visent pas. Si "
            "elle inflige des dégâts à une autre créature que vous, vous pouvez lors de votre prochain tour, par une "
            "action bonus, l'attaquer avec une arme de corps à corps avec avantage, en ajoutant la moitié de votre "
            "niveau de guerrier aux dégâts. Cette attaque bonus est utilisable un nombre de fois égal à votre "
            "modificateur de Force (minimum 1), récupérées après un repos long."
        ),
        "Manœuvre d'interposition": (
            "Lorsqu'une créature que vous voyez à 1,50 m de vous (ou vous-même) est touchée "
            "par une attaque, vous pouvez utiliser votre réaction pour ajouter 1d8 à sa CA contre cette attaque, si "
            "vous tenez une arme de corps à corps ou un bouclier. Si l'attaque touche malgré tout, la cible a la "
            "résistance à ses dégâts. Un nombre de fois égal à votre modificateur de Constitution (minimum 1), "
            "récupérées après un repos long."
        ),
        "Tenir la ligne": (
            "Les créatures provoquent une attaque d'opportunité de votre part lorsqu'elles se "
            "déplacent d'au moins 1,50 m dans votre allonge, même en se désengageant. Si cette attaque d'opportunité "
            "touche, la vitesse de la cible tombe à 0 jusqu'à la fin du tour en cours."
        ),
        "Charge féroce": (
            "Une fois par tour, si vous vous déplacez d'au moins 3 m en ligne droite vers une cible juste avant de la "
            "toucher, elle doit réussir un JS de Force (DD 8 + votre bonus de maîtrise + votre modificateur de Force) "
            "ou tomber à terre. Elle n'est renversée qu'en cas d'échec."
        ),
        "Défenseur vigilant": (
            "Une fois lors du tour de chaque autre créature, vous disposez d'une réaction spéciale utilisable "
            "uniquement pour une attaque d'opportunité. Elle ne peut pas servir lors de votre propre tour et ne "
            "consomme pas votre réaction normale."
        ),
    },
    "Samouraï": {
        "Maîtrise supplémentaire": (
            "Vous obtenez la maîtrise d'une compétence parmi Histoire, Perspicacité, Représentation ou Persuasion, ou "
            "apprenez une langue de votre choix."
        ),
        "Esprit combatif": (
            "Par une action bonus lors de votre tour, vous gagnez l'avantage à tous vos jets d'attaque avec une arme "
            "jusqu'à la fin du tour et 5 points de vie temporaires (10 au niveau 10, 15 au niveau 15). Trois "
            "utilisations, récupérées après un repos long."
        ),
        "Courtisan élégant": (
            "Lorsque vous faites un test de Charisme (Persuasion), vous ajoutez votre modificateur de Sagesse au "
            "résultat. Vous obtenez aussi la maîtrise des JS de Sagesse (ou, si vous l'avez déjà, des JS "
            "d'Intelligence ou de Charisme au choix)."
        ),
        "Esprit infatigable": (
            "Lorsque vous lancez l'initiative alors qu'il ne vous reste aucune utilisation "
            "d'Esprit combatif, vous en regagnez une. Les PV temporaires d'Esprit combatif passent à 10."
        ),
        "Frappe éclair": (
            "Une fois par tour, si vous avez l'avantage à une attaque d'arme lors de l'action "
            "Attaquer, vous pouvez y renoncer pour effectuer une attaque d'arme supplémentaire contre la même cible "
            "dans le cadre de cette action. Les PV temporaires d'Esprit combatif (aptitude du niveau 3) passent à 15."
        ),
        "Force avant la mort": (
            "Lorsque des dégâts vous font tomber à 0 PV sans vous tuer, vous pouvez utiliser "
            "votre réaction pour retarder l'inconscience et jouer immédiatement un tour supplémentaire. Si vous "
            "subissez des dégâts pendant ce tour, vous ratez des JS contre la mort normalement ; à la fin du tour, "
            "vous tombez inconscient si vous êtes toujours à 0 PV. Une utilisation, récupérée après un repos long."
        ),
    },
    "Chevalier runique": {
        "Maîtrises supplémentaires": (
            "Vous obtenez la maîtrise des outils de forgeron et apprenez à parler, lire et écrire le géant."
        ),
        "Sculpteur de runes": (
            "Vous connaissez deux runes (trois au niveau 7, quatre au niveau 10, cinq au niveau 15) parmi feu, nuage, "
            "givre et pierre (colline et tempête accessibles dès le niveau 7) ; chaque fois que vous gagnez un niveau dans cette classe, "
            "vous pouvez en échanger une. Après un repos long, vous gravez chaque rune sur un objet que vous portez "
            "(arme, armure, bouclier, bijou…) : elle accorde un bonus passif et un pouvoir utilisable une fois, "
            "récupéré après un repos court ou long. DD des runes = 8 + votre bonus de maîtrise + votre modificateur "
            "de Constitution."
        ),
        "Puissance des géants": (
            "Par une action bonus, pendant 1 minute, vous devenez de taille "
            "Grande (si l'espace le permet), avez l'avantage aux tests et JS de Force, et une fois par tour une "
            "attaque d'arme ou à mains nues qui touche inflige 1d6 dégâts supplémentaires. Un nombre de fois égal à "
            "votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Bouclier runique": (
            "Lorsqu'une créature que vous voyez à 18 m ou moins est touchée par une attaque, vous pouvez utiliser "
            "votre réaction pour forcer l'attaquant à relancer le d20 et à garder le nouveau résultat. Un nombre de "
            "fois égal à votre bonus de maîtrise, récupérées après un repos long. Vous apprenez aussi une troisième "
            "rune."
        ),
        "Grande stature": (
            "La magie des runes vous fait grandir de 3d4 pouces (environ 8 à 30 cm). Les dégâts "
            "supplémentaires de Puissance des géants passent à 1d8. Vous apprenez aussi une quatrième rune."
        ),
        "Maître des runes": (
            "Vous pouvez invoquer le pouvoir de chacune de vos runes deux fois au lieu d'une, et "
            "toutes les utilisations reviennent après un repos court ou long. Vous connaissez à présent cinq runes."
        ),
        "Colosse runique": (
            "Les dégâts supplémentaires de Puissance des géants passent à 1d10. Lorsque vous "
            "l'activez, vous pouvez devenir de taille Très grande (si l'espace le permet) et votre allonge augmente "
            "de 1,50 m tant que dure l'effet."
        ),
    },
    "Guerrier Psi (Soldat psi)": {
        "Pouvoirs psioniques": (
            "Vous disposez d'un nombre de dés d'énergie psionique égal à 2 × votre bonus de maîtrise : des d6 "
            "(d8 au niveau 5, d10 au niveau 11, d12 au niveau 17), tous récupérés après un repos long ; une fois par "
            "repos court ou long, vous pouvez en regagner un par une action bonus. Champ protecteur : par une "
            "réaction, réduisez les dégâts subis par vous ou une créature visible à 9 m d'un dé + votre modificateur "
            "d'Intelligence. Frappe psionique : une fois par tour, après un coup d'arme sur une cible à 9 m, dépensez "
            "un dé pour infliger un dé + votre modificateur d'Intelligence dégâts de force. Mouvement télékinétique : "
            "par une action, déplacez de 9 m un objet ou une créature consentante de taille Grande ou moins à 9 m "
            "(une fois par repos court ou long, ou en dépensant un dé)."
        ),
        "Adepte télékinétique": (
            "Bond psi : par une action bonus, vous obtenez une vitesse de vol égale à deux fois "
            "votre vitesse au sol jusqu'à la fin du tour (une fois par repos court ou long, ou en dépensant un dé). "
            "Poussée télékinétique : quand votre Frappe psionique inflige des dégâts, la cible doit réussir un JS de "
            "Force (DD 8 + votre bonus de maîtrise + votre modificateur d'Intelligence) ou tomber à terre, ou être "
            "repoussée jusqu'à 3 m (au choix)."
        ),
        "Esprit gardé": (
            "Vous avez la résistance aux dégâts psychiques. Au début de votre tour, si vous êtes charmé ou effrayé, "
            "vous pouvez dépenser un dé d'énergie psionique pour mettre fin à tous ces effets."
        ),
        "Rempart de force": (
            "Par une action bonus, vous choisissez des créatures (vous compris) à 9 m ou moins, "
            "jusqu'à votre modificateur d'Intelligence (minimum 1) ; elles bénéficient d'un abri partiel (+2 à la CA "
            "et aux JS de Dextérité) pendant 1 minute ou jusqu'à ce que vous soyez neutralisé. Une fois par repos "
            "long, ou en dépensant un dé d'énergie psionique."
        ),
        "Maître télékinétique": (
            "Vous pouvez lancer le sort Télékinésie sans composante, avec l'Intelligence pour caractéristique "
            "d'incantation (une fois par repos long, ou en dépensant un dé d'énergie psionique). Tant que vous vous "
            "concentrez dessus, vous pouvez effectuer une attaque d'arme par une action bonus à chacun de vos tours."
        ),
    },
    "Chevalier de Sang": {
        "Lame de sang & Saccage écarlate": (
            "Lame de sang : une fois par tour, lorsque vous touchez une créature avec une attaque d'arme de corps à "
            "corps, vous pouvez dépenser un de vos dés de vie (sans action), ou l'avoir engagé plus tôt dans le tour "
            "par une action bonus pour imprégner votre arme. Lancez-le : la cible subit des dégâts nécrotiques "
            "supplémentaires égaux au résultat. Limite : un nombre de fois égal à votre bonus de maîtrise, récupérées "
            "après un repos long, et uniquement tant qu'il vous reste des dés de vie. Saccage écarlate : si cette "
            "attaque réduit la créature à 0 PV (hors créatures artificielles et morts-vivants), vous regagnez des PV "
            "égaux à la moitié du résultat du dé (minimum 1)."
        ),
        "Pistage hématologique & Armure de sang": (
            "Pistage hématologique : vous percevez l'emplacement de toute créature située à 18 m ou moins qui n'a pas "
            "tous ses points de vie (sauf créatures artificielles et morts-vivants), même invisible, si elle n'est pas "
            "derrière un abri total. Vous avez l'avantage aux tests de Sagesse (Survie) pour pister une créature qui a "
            "perdu des PV au cours des dernières 24 heures. Armure de sang : par une action bonus, ou sans action "
            "lorsque vous obtenez un coup critique, vous gagnez des points de vie temporaires égaux à votre niveau de "
            "guerrier + votre modificateur de Constitution pendant 1 minute. Une utilisation, récupérée après un "
            "repos court ou long."
        ),
        "Châtiment de sang": (
            "Lorsqu'une créature située à 1,50 m de vous vous inflige des dégâts avec une attaque de corps à corps, "
            "vous pouvez utiliser votre réaction pour effectuer une attaque d'arme de corps à corps contre elle. Si "
            "elle touche, elle inflige 1d8 dégâts nécrotiques supplémentaires (2d8 au niveau 18 de guerrier) et peut "
            "bénéficier de Lame de sang. Un nombre de fois égal à votre bonus de maîtrise, récupérées après un repos "
            "long."
        ),
        "Frénésie sanguine": (
            "Tant que vous avez au plus la moitié de vos points de vie maximum (et au moins 1), vos attaques d'arme "
            "de corps à corps infligent 2 dégâts supplémentaires. Si vous avez au plus le quart de vos points de vie "
            "maximum, vous gagnez aussi +1 aux jets d'attaque avec ces armes et le bonus de dégâts passe à 4. L'effet "
            "cesse si vous êtes neutralisé ou si vos PV remontent au-dessus du seuil."
        ),
        "Inexorable martyr": (
            "Lorsque des dégâts vous font tomber à 0 PV sans vous tuer, vous pouvez utiliser votre réaction pour "
            "rester conscient jusqu'à la fin de votre prochain tour. Vous restez à 0 PV et agissez normalement ; "
            "chaque fois que vous subissez des dégâts, vous ratez un JS contre la mort (deux en cas de coup "
            "critique). Pendant cette durée, Lame de sang ne consomme ni dé de vie ni utilisation. À la fin de ce "
            "tour, si vous êtes toujours à 0 PV, vous tombez inconscient et stabilisé. Une utilisation, récupérée "
            "après un repos long."
        ),
    },
    "Pancratiaste": {
        "Mains d'acier & Prise de fer": (
            "Mains d'acier : vos frappes à mains nues infligent 1d6 dégâts contondants (1d8 à partir du niveau 10 de "
            "guerrier) et vous pouvez utiliser votre modificateur de Force ou votre modificateur de Dextérité, au "
            "choix, pour leurs jets d'attaque et de dégâts. Ce dé ne se cumule pas avec Arts martiaux ou le style "
            "Combat à mains nues : le plus grand s'applique. Prise de fer : lorsque vous effectuez l'action Attaquer "
            "lors de votre tour, vous pouvez par une action bonus tenter de lutter contre une créature ou de la "
            "bousculer (test de Force (Athlétisme) opposé), à condition d'avoir une main libre pour la lutte."
        ),
        "Projection dévastatrice": (
            "Lorsque vous touchez avec une frappe à mains nues une créature que vous agrippez (de taille au plus une "
            "catégorie au-dessus de la vôtre) lors de l'action Attaquer, vous pouvez la projeter : elle subit 2d8 + "
            "votre modificateur de Force dégâts contondants au lieu des dégâts normaux, la lutte prend fin et elle "
            "tombe à terre dans un espace libre à 1,50 m de vous. Elle doit aussi réussir un JS de Constitution (DD "
            "8 + votre bonus de maîtrise + votre modificateur de Force) ou être étourdie jusqu'à la fin de votre "
            "prochain tour. Si vous la projetez sur une autre créature à 1,50 m, celle-ci réussit un JS de Dextérité "
            "(même DD) ou subit 1d8 dégâts contondants et tombe à terre. Une fois par tour, un nombre de fois égal à "
            "votre bonus de maîtrise, récupérées après un repos long."
        ),
        "Garde de pugiliste": (
            "Tant que vous ne portez ni armure ni bouclier, votre CA est égale à 10 + votre modificateur de "
            "Dextérité + votre modificateur de Constitution. Cette formule ne se cumule pas avec une autre Défense "
            "sans armure (choisissez la meilleure). Vous pouvez tenir une arme ; seuls l'armure et le "
            "bouclier annulent la garde."
        ),
        "Fracas d'ossements": (
            "Vos frappes à mains nues comptent comme magiques et ignorent la résistance (mais pas l'immunité) aux "
            "dégâts contondants. Une fois par tour, lorsque vous touchez une créature avec une frappe à mains nues, "
            "elle doit réussir un JS de Constitution (DD 8 + votre bonus de maîtrise + votre modificateur de Force) "
            "ou voir sa vitesse réduite à 0 jusqu'au début de votre prochain tour."
        ),
        "Colosse du ring": (
            "Vous pouvez agripper ou bousculer une créature quelle que soit sa taille, y compris Gigantesque. Vous "
            "avez l'avantage aux tests de Force (dont Athlétisme) et aux JS de Force, et vous déplacer en traînant "
            "une créature agrippée ne réduit plus votre vitesse. Une créature que vous agrippez a un désavantage aux "
            "jets d'attaque contre d'autres cibles que vous."
        ),
    },
}

AUDIT = [
    ("info", "Archer arcanique", "Pas d'entrée au niveau 10 : non corrigé, aucune aptitude officielle à ce niveau",
     "Le niveau 10 n'apporte qu'une option de Tir arcanique supplémentaire (mentionnée dans Tir arcanique)"),
    ("info", "Guerrier Psi (Soldat psi)", "Nom de sous-classe double : non renommée pour ne pas casser les fiches existantes",
     "Nom officiel FR : « Soldat psi » (Psi Warrior)"),
    ("info", "Chevalier de Sang / sorts_domaine", "Liste de sorts sans aptitude d'incantation : conservée telle quelle (homebrew validé)",
     "Aucune aptitude ne permet de lancer ces sorts ; liste purement indicative"),
]

CORRIGE = [
    ("mineur", "Style de combat", "Noms « Duelliste » et « Combat à deux mains »",
     "Noms officiels : « Duel » et « Arme à deux mains » (Combat à deux armes est un autre style)"),
    ("mineur", "Style de combat", "Styles de Tasha non mentionnés",
     "TCE ajoute Combat aveugle, Interception, Arme de lancer, Combat à mains nues, Technique supérieure"),
    ("mineur", "Capacités de classe optionnelles (Tasha)", "Absentes des données",
     "Polyvalence martiale (niveau 4, puis à chaque Amélioration de caractéristique) : échanger un style ou une manœuvre"),
    ("mineur", "Indomptable", "Typo « niv 13 » et nouveau résultat obligatoire non précisé",
     "Relance d'un JS raté, nouveau résultat obligatoire ; 1/repos long, 2 au niveau 13, 3 au niveau 17"),
    ("info", "Sursaut d'activité", "Limite d'une utilisation par tour non mentionnée",
     "2 utilisations au niveau 17, mais une seule par tour"),
    ("majeur", "Champion / Coup critique amélioré & Athlète accompli", "Bonus d'athlète donné dès le niveau 3",
     "Niveau 3 : Critique amélioré seul ; Athlète remarquable au niveau 7"),
    ("mineur", "Champion / Athlète remarquable", "Description vague",
     "+ moitié du bonus de maîtrise (arrondi sup.) aux tests For/Dex/Con sans maîtrise ; saut en longueur + mod. de Force (pieds)"),
    ("majeur", "Champion / Coup critique supérieur & Survivant", "Survivant au niveau 15, 5 PV fixes, « moins de la moitié »",
     "Survivant au niveau 18 : 5 + modificateur de Constitution PV si PV ≤ moitié et ≥ 1"),
    ("mineur", "Champion / Survivant (Maîtrise)", "Aptitude au nom inventé, sans effet défini",
     "Niveau 18 : Survivant (régénération 5 + modificateur de Constitution)"),
    ("mineur", "Maître de guerre / Supériorité martiale & Disciple martial", "Nombre de dés (4) et de manœuvres (3), DD et récupération absents",
     "4 dés d8 (5 au niv. 7, 6 au niv. 15), repos court ou long ; DD 8 + maîtrise + mod. For ou Dex ; « Disciple de la guerre »"),
    ("mineur", "Maître de guerre / Observation de l'ennemi", "Nom et contenu imprécis",
     "« Connaître son ennemi » : 2 critères parmi For, Dex, Con, CA, PV actuels, niveaux totaux, niveaux de guerrier"),
    ("mineur", "Maître de guerre / Dés de supériorité améliorés (d10 / d12)", "Laisse entendre le d12 dès le niveau 10",
     "d10 au niveau 10, d12 au niveau 18"),
    ("mineur", "Maître de guerre / Maîtrise des dés de supériorité", "Aptitude au nom inventé",
     "Niveau 18 : Supériorité martiale améliorée (dés d12)"),
    ("info", "Maître de guerre / Relance de supériorité (Implacable)", "Déclencheur « début du combat »",
     "Se déclenche quand vous lancez l'initiative sans dé de supériorité restant"),
    ("info", "Chevalier occulte / sorts_domaine", "Liste fixe de 8 sorts",
     "Pas de sorts imposés : sorts de magicien au choix (abjuration/évocation sauf niveaux 3, 8, 14, 20)"),
    ("mineur", "Chevalier occulte / Incantation & Arme occulte", "« Arme occulte », DD et progression des sorts absents",
     "« Lien avec une arme » (rituel 1 h, 2 armes) ; DD 8 + maîtrise + mod. d'Intelligence"),
    ("mineur", "Chevalier occulte / Fragilisation occulte (Frappe arcanique)", "Nom et durée imprécis",
     "« Frappe occulte » : désavantage au prochain JS contre vos sorts avant la fin de votre prochain tour"),
    ("mineur", "Archer arcanique / Tir arcanique & Connaissances de l'archer", "« Arcane » et options/DD absents",
     "Arcanes ou Nature ; 2 options connues (+1 aux niv. 7, 10, 15, 18) ; DD 8 + maîtrise + mod. d'Intelligence"),
    ("mineur", "Archer arcanique / Tir récurrent (Implacable)", "Nom inexact",
     "« Tir infaillible » (Ever-Ready Shot), regain d'une utilisation en lançant l'initiative"),
    ("mineur", "Archer arcanique / Tir arcanique amélioré", "Seul « 4d6 » mentionné",
     "Toutes les options gagnent des dégâts (2d6→4d6, 1d6→2d6)"),
    ("mineur", "Cavalier / Maîtrise supplémentaire, Né sur un cheval & Marque tenace", "Noms inexacts, utilisations et bonus de dégâts absents",
     "« Né en selle », « Marque inébranlable » : attaque bonus avec avantage + moitié du niveau de guerrier, mod. de Force/repos long"),
    ("mineur", "Cavalier / Manœuvre défensive", "Nom inexact, résistance et utilisations absentes",
     "« Manœuvre d'interposition » : +1d8 CA puis résistance ; mod. de Constitution (min 1)/repos long"),
    ("mineur", "Cavalier / On ne passe pas (Inébranlable)", "Nom inexact, déplacement dans l'allonge non mentionné",
     "« Tenir la ligne » : attaque d'opportunité même en se désengageant, vitesse 0 si elle touche"),
    ("majeur", "Cavalier / Charge féroce", "« Mise à terre en cas de réussite au JS » : logique inversée, pas de DD",
     "À terre en cas d'échec au JS de Force DD 8 + maîtrise + mod. de Force, 1/tour"),
    ("majeur", "Samouraï / Maîtrise supplémentaire", "Esprit combatif absent au niveau 3 (placé au niveau 15)",
     "Esprit combatif au niveau 3 : action bonus, avantage + 5/10/15 PV temporaires, 3/repos long"),
    ("majeur", "Samouraï / Courtisan élégant", "Ajoute le modificateur de Charisme",
     "Ajoute le modificateur de Sagesse aux tests de Persuasion"),
    ("mineur", "Samouraï / Volonté inébranlable", "Nom inexact", "« Esprit infatigable » (Tireless Spirit)"),
    ("mineur", "Samouraï / Combativité & Frappe fulgurante", "Nom « Frappe fulgurante » et Combativité placée au niveau 15",
     "« Frappe éclair » au niveau 15 ; Esprit combatif au niveau 3"),
    ("mineur", "Samouraï / Solide face à la mort", "Nom inexact", "« Force avant la mort » : réaction, tour supplémentaire immédiat"),
    ("majeur", "Chevalier runique / Maîtrise des outils, Langue des géants & Puissance des géants", "Taille Gigantesque, +1d10 dégâts, 6 utilisations/repos long",
     "Taille Grande, +1d6 (1d8 au niv. 10, 1d10 au niv. 18), utilisations = bonus de maîtrise/repos long"),
    ("majeur", "Chevalier runique / Sculpteur de runes", "Aucune rune connue au niveau 3 dans les données",
     "Sculpteur de runes au niveau 3 : 2 runes (3/4/5 aux niveaux 7/10/15), DD 8 + maîtrise + mod. de Constitution"),
    ("mineur", "Chevalier runique / Bouclier runique", "Utilisations absentes", "Bonus de maîtrise par repos long"),
    ("mineur", "Chevalier runique / Grande carrure", "« Augmentation permanente de la taille de base »",
     "« Grande stature » : +3d4 pouces de taille (pas de catégorie) et dégâts de Puissance des géants en d8"),
    ("mineur", "Chevalier runique / Mastodonte runique", "Nom inexact, d10 et taille Très grande absents",
     "« Colosse runique » : d10, taille Très grande possible, +1,50 m d'allonge"),
    ("majeur", "Guerrier Psi (Soldat psi) / Pouvoirs psioniques", "12 dés d12 fixes",
     "2 × bonus de maîtrise dés ; d6 (d8 niv. 5, d10 niv. 11, d12 niv. 17)"),
    ("mineur", "Guerrier Psi (Soldat psi) / Applications télékinétiques", "Nom et effets imprécis",
     "« Adepte télékinétique » : Bond psi + Poussée télékinétique (JS de Force)"),
    ("mineur", "Guerrier Psi (Soldat psi) / Esprit blindé & Bulle de protection", "Rempart de force annoncé au niveau 10",
     "Niveau 10 : Esprit gardé seul ; Rempart de force au niveau 15"),
    ("mineur", "Guerrier Psi (Soldat psi) / Rempart de force supérieur", "Nom inexact",
     "« Rempart de force » : abri partiel, mod. d'Intelligence créatures, 1 minute"),
    ("mineur", "Chevalier de Sang / sorts_domaine", "« Vampirism » (nom anglais inexistant)",
     "Remplacer par « Toucher du vampire » (Vampiric Touch, niveau 3)"),
    ("mineur", "Chevalier de Sang / sorts_domaine", "« Rayon d'affaiblissement » absent de la base de sorts",
     "Nom exact dans la base : « Rayon affaiblissant » (Ray of Enfeeblement, niveau 2)"),
]
