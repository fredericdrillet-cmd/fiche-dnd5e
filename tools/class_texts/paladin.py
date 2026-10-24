"""Descriptions enrichies — Paladin (PHB, Xanathar, Tasha ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Paladin"

BASE = {
    "Sens divin": (
        "Par une action, vous ouvrez vos sens à la présence d'un grand mal ou d'un grand bien. Jusqu'à la fin de "
        "votre prochain tour, vous connaissez l'emplacement et le type (céleste, fiélon ou mort-vivant) de toute "
        "créature de ces types située à 18 m ou moins de vous et qui ne se trouve pas derrière un abri total, sans "
        "connaître son identité. Vous percevez aussi, dans le même rayon, tout lieu ou objet consacré ou profané "
        "(comme par le sort Sanctification). Utilisable 1 + votre modificateur de Charisme fois (minimum 1) ; toutes "
        "les utilisations reviennent après un repos long."
    ),
    "Imposition des mains": (
        "Vous disposez d'une réserve de pouvoir curatif égale à 5 × votre niveau de paladin points de vie, qui se "
        "remplit entièrement après un repos long. Par une action, vous touchez une créature et puisez dans la "
        "réserve pour lui rendre le nombre de points de vie de votre choix, jusqu'au maximum restant. Vous pouvez "
        "aussi dépenser 5 points de la réserve pour la guérir d'une maladie ou neutraliser un poison qui l'affecte "
        "(plusieurs maladies ou poisons peuvent être traités en une seule action, 5 points chacun). Cette aptitude "
        "est sans effet sur les morts-vivants et les créatures artificielles."
    ),
    "Style de combat": (
        "Vous adoptez un style de combat qui devient votre spécialité ; vous ne pouvez pas choisir deux fois le même "
        "style. Options du Manuel des joueurs : Défense (+1 à la CA quand vous portez une armure), Duel (+2 aux dégâts "
        "avec une arme de corps à corps tenue à une main sans autre arme), Arme à deux mains (relancez les 1 et 2 aux "
        "dés de dégâts d'une arme de corps à corps tenue à deux mains) et Protection (avec un bouclier, réaction pour "
        "imposer le désavantage à une attaque visant un allié à 1,50 m). Options de Tasha : Combat en aveugle "
        "(vision aveugle à 3 m), Interception (réaction : réduisez de 1d10 + votre bonus de maîtrise les dégâts subis "
        "par un allié à 1,50 m) et Guerrier béni (deux sorts mineurs de clerc, lancés avec le Charisme). Option de "
        "Tasha « Polyvalence martiale » : voir l'aptitude correspondante (niveau 4)."
    ),
    "Incantation": (
        "Vous lancez des sorts de paladin grâce au Charisme, en utilisant un symbole sacré comme focaliseur. Après "
        "un repos long, vous préparez un nombre de sorts égal à votre modificateur de Charisme + la moitié de votre "
        "niveau de paladin (minimum 1), choisis dans la liste du paladin parmi les niveaux pour lesquels vous avez "
        "des emplacements ; les sorts de serment sont toujours préparés en plus. Emplacements : deux du 1er niveau au "
        "niveau 2, puis accès au 2e niveau au niveau 5, au 3e au niveau 9, au 4e au niveau 13 et au 5e au niveau 17 ; "
        "ils se récupèrent après un repos long. DD de sauvegarde des sorts = 8 + votre bonus de maîtrise + votre "
        "modificateur de Charisme ; bonus d'attaque des sorts = votre bonus de maîtrise + votre modificateur de "
        "Charisme. Tasha ajoute à la liste : Repos du défunt, Prière de soins, Lien de protection, Linceul spirituel "
        "et Convocation de céleste."
    ),
    "Châtiment divin": (
        "Quand vous touchez une créature avec une attaque d'arme au corps à corps, vous pouvez dépenser un "
        "emplacement de sort (sans action) pour infliger des dégâts radiants supplémentaires : 2d8 pour un "
        "emplacement du 1er niveau, +1d8 par niveau d'emplacement au-delà du 1er, jusqu'à un maximum de 5d8. Les "
        "dégâts augmentent de 1d8 supplémentaire si la cible est un mort-vivant ou un fiélon (soit jusqu'à 6d8). "
        "Vous décidez d'utiliser le châtiment après avoir su que l'attaque touche ; en cas de coup critique, les dés "
        "du châtiment sont doublés."
    ),
    "Santé divine": (
        "La magie divine qui vous traverse vous rend immunisé contre les maladies, qu'elles soient naturelles ou "
        "magiques. Cette immunité ne protège pas contre l'état empoisonné ni contre les dégâts de poison, ni contre "
        "les malédictions qui ne sont pas des maladies."
    ),
    "Serment sacré": (
        "Au niveau 3, vous prêtez le serment qui vous lie à jamais à votre cause : Dévotion, Anciens, Vengeance "
        "(PHB), Conquête, Rédemption (Xanathar), Gloire, Guetteurs (Tasha) ou un serment communautaire. Il vous "
        "accorde des sorts de serment, toujours préparés et non décomptés de vos sorts préparés (aux niveaux 3, 5, "
        "9, 13 et 17), deux options de Conduit divin, puis des aptitudes aux niveaux 7, 15 et 20. Chaque serment "
        "impose des préceptes ; les violer peut obliger le paladin à expier, voire à changer de serment."
    ),
    "Conduit divin (1/repos)": (
        "Votre serment vous permet de canaliser l'énergie divine pour produire l'un des deux effets de Conduit divin "
        "propres à votre serment. Vous disposez d'une utilisation, que vous récupérez après un repos court ou long. "
        "Si un effet exige un jet de sauvegarde, le DD est celui de vos sorts : 8 + votre bonus de maîtrise + votre "
        "modificateur de Charisme."
    ),
    "Exploitation du pouvoir divin (option Tasha)": (
        "Option de Tasha (« Harness Divine Power »). Par une action bonus, vous "
        "touchez votre symbole sacré, prononcez une prière et dépensez une utilisation de Conduit divin pour "
        "récupérer un emplacement de sort dépensé dont le niveau ne dépasse pas la moitié du bonus "
        "de maîtrise, arrondie au supérieur (1er niveau aux niveaux 3-4, 2e à partir du niveau 5). Vous pouvez le faire une fois par repos long, deux fois à partir du "
        "niveau 7 et trois fois à partir du niveau 15."
    ),
    "Polyvalence martiale (option Tasha)": (
        "Option de Tasha. Chaque fois que vous atteignez un niveau qui vous accorde l'aptitude Amélioration de "
        "caractéristique (niveaux 4, 8, 12, 16 et 19 de paladin), vous pouvez abandonner le style de combat que vous "
        "avez choisi pour en adopter un autre parmi ceux proposés au paladin (Défense, Duel, Arme à deux mains, "
        "Protection, Combat en aveugle, Interception, Guerrier béni). Ce changement reflète l'évolution de votre "
        "entraînement martial ; il n'est pas obligatoire et n'a lieu qu'à ces niveaux."
    ),
    "Attaque supplémentaire": (
        "Lorsque vous effectuez l'action Attaquer pendant votre tour, vous pouvez attaquer deux fois au lieu d'une. "
        "Cette aptitude ne se cumule pas avec l'Attaque supplémentaire d'une autre classe."
    ),
    "Aura de protection": (
        "Tant que vous êtes conscient, vous et chaque créature amicale située à 3 m ou moins de vous ajoutez votre "
        "modificateur de Charisme (minimum +1) à vos jets de sauvegarde. Le rayon de l'aura passe à 9 m au niveau 18. "
        "Plusieurs auras de paladin du même type ne se cumulent pas : une créature ne bénéficie que de la meilleure."
    ),
    "Aura de courage": (
        "Tant que vous êtes conscient, vous et les créatures amicales situées à 3 m ou moins de vous ne pouvez pas "
        "être effrayés. Une créature déjà effrayée qui entre dans l'aura voit cet état suspendu tant qu'elle s'y "
        "trouve. Le rayon passe à 9 m au niveau 18."
    ),
    "Châtiment divin amélioré": (
        "Votre ferveur imprègne chacun de vos coups : chaque fois que vous touchez une créature avec une arme de "
        "corps à corps, elle subit 1d8 dégâts radiants supplémentaires. Ces dégâts s'ajoutent automatiquement, sans "
        "dépense d'emplacement, et se cumulent avec un Châtiment divin porté sur la même attaque (dés doublés en cas "
        "de coup critique)."
    ),
    "Contact purifiant": (
        "Par une action, vous mettez fin à un sort qui vous affecte ou qui affecte une créature "
        "consentante que vous touchez, sans jet de caractéristique. Utilisable un nombre de fois égal à votre "
        "modificateur de Charisme (minimum 1) ; toutes les utilisations reviennent après un repos long."
    ),
    "Amélioration des auras": (
        "Le rayon de toutes vos auras de paladin passe de 3 m à 9 m : Aura de protection, Aura de courage et l'aura "
        "obtenue au niveau 7 grâce à votre serment (Dévotion, Garde, Conquête, Gardien, Alacrité, Sentinelle, etc.). "
        "Les conditions d'activation (être conscient, créatures amicales) restent identiques."
    ),
}

SUB = {
    "Serment de Dévotion": {
        "Conduit divin : Arme sacrée & Renvoi des impies": (
            "Arme sacrée : par une action, vous imprégnez une arme que vous tenez d'énergie positive pendant 1 minute. "
            "Vous ajoutez votre modificateur de Charisme (minimum +1) aux jets d'attaque effectués avec elle ; elle "
            "émet une lumière vive sur 6 m et une lumière faible sur 6 m de plus et est considérée comme magique. "
            "L'effet prend fin si vous lâchez l'arme ou tombez inconscient (vous pouvez aussi y mettre fin). "
            "Renvoi des impies : par une action, chaque fiélon ou mort-vivant à 9 m ou moins qui peut vous voir ou "
            "vous entendre fait un jet de sauvegarde de Sagesse (DD 8 + votre bonus de maîtrise + votre modificateur "
            "de Charisme) ; en cas d'échec, il est renvoyé pendant 1 minute ou jusqu'à ce qu'il subisse des dégâts : "
            "il doit s'éloigner de vous et ne peut pas s'approcher à 9 m ni effectuer de réaction."
        ),
        "Aura de dévotion": (
            "Tant que vous êtes conscient, vous et les créatures amicales situées à 3 m ou moins de vous ne pouvez "
            "pas être charmés. Une créature déjà charmée voit cet état suspendu tant qu'elle se trouve dans l'aura. "
            "Le rayon passe à 9 m au niveau 18."
        ),
        "Pureté de l'esprit": (
            "Vous êtes en permanence sous l'effet du sort Protection contre le mal et le bien, sans concentration : "
            "les aberrations, célestes, élémentaires, fées, fiélons et morts-vivants ont un désavantage à leurs jets "
            "d'attaque contre vous, ne peuvent pas vous charmer, vous effrayer ni vous posséder, et vous avez "
            "l'avantage aux jets de sauvegarde contre ces effets s'ils vous affectent déjà."
        ),
        "Nimbe sacré": (
            "Par une action, vous émanez une aura de lumière solaire pendant 1 minute : lumière vive sur 9 m et "
            "lumière faible sur 9 m de plus. Chaque créature ennemie qui commence son tour dans la lumière vive subit "
            "10 dégâts radiants. Pendant la durée, vous avez l'avantage aux jets de sauvegarde contre les sorts lancés "
            "par des fiélons ou des morts-vivants. Utilisable une fois par repos long."
        ),
    },
    "Serment des Anciens": {
        "Conduit divin : Courroux de la nature & Renvoi des infidèles": (
            "Courroux de la nature : par une action, des lianes spectrales jaillissent autour d'une créature que vous "
            "voyez à 3 m ou moins ; elle doit réussir un jet de sauvegarde de Force ou de Dextérité (à son choix, DD "
            "8 + votre bonus de maîtrise + votre modificateur de Charisme) ou être entravée. Elle refait le jet à la "
            "fin de chacun de ses tours et se libère sur une réussite. Renvoi des infidèles : par une action, chaque "
            "fée ou fiélon à 9 m ou moins qui peut vous entendre fait un jet de sauvegarde de Sagesse ; en cas "
            "d'échec, il est renvoyé pendant 1 minute ou jusqu'à ce qu'il subisse des dégâts, et une créature dont la "
            "véritable forme est masquée par une illusion ou une métamorphose révèle son apparence réelle."
        ),
        "Aura de garde": (
            "Une magie ancienne vous enveloppe : tant que vous êtes conscient, vous et les créatures amicales situées "
            "à 3 m ou moins de vous avez la résistance aux dégâts infligés par les sorts (y compris les sorts "
            "mineurs et les sorts lancés par objets). Le rayon passe à 9 m au niveau 18."
        ),
        "Sentinelle immortelle": (
            "Lorsque vous tombez à 0 point de vie sans être tué sur le coup, vous pouvez tomber à 1 point de vie à la "
            "place ; cette faculté se recharge après un repos long. De plus, vous ne subissez plus les inconvénients "
            "de la vieillesse et ne pouvez pas être vieilli par magie."
        ),
        "Champion antique": (
            "Par une action, vous prenez l'apparence d'une force de la nature antique pendant 1 minute. Au début de "
            "chacun de vos tours, vous regagnez 10 points de vie. Vous pouvez lancer par une action bonus les sorts de "
            "paladin dont le temps d'incantation est d'une action. Les créatures ennemies situées à 3 m ou moins de "
            "vous ont un désavantage aux jets de sauvegarde contre vos sorts de paladin et vos options de Conduit "
            "divin. Utilisable une fois par repos long."
        ),
    },
    "Serment de Vengeance": {
        "Conduit divin : Condamnation de l'ennemi & Vœu d'hostilité": (
            "Condamnation de l'ennemi : par une action, vous désignez une créature que vous voyez à 18 m ou moins ; "
            "elle fait un jet de sauvegarde de Sagesse (DD 8 + votre bonus de maîtrise + votre modificateur de "
            "Charisme ; les fiélons et morts-vivants ont un désavantage). En cas d'échec, elle est effrayée et sa "
            "vitesse tombe à 0 pendant 1 minute ou jusqu'à ce qu'elle subisse des dégâts ; en cas de réussite, sa "
            "vitesse est réduite de moitié pendant 1 minute. Vœu d'hostilité : par une action bonus, vous visez une "
            "créature à 3 m ou moins ; vous avez l'avantage à vos jets d'attaque contre elle pendant 1 minute ou "
            "jusqu'à ce qu'elle tombe à 0 point de vie ou inconsciente."
        ),
        "Vengeur implacable": (
            "Lorsque vous touchez une créature avec une attaque d'opportunité, vous pouvez, immédiatement après et "
            "dans le cadre de la même réaction, vous déplacer d'une distance égale au maximum à la moitié de votre "
            "vitesse. Ce déplacement ne provoque pas d'attaque d'opportunité."
        ),
        "Âme vengeresse": (
            "Lorsqu'une créature soumise à votre Vœu d'hostilité effectue une attaque, vous pouvez utiliser votre "
            "réaction pour faire une attaque d'arme au corps à corps contre elle si elle est à votre portée. Cette "
            "riposte a lieu après l'attaque de la créature et bénéficie de l'avantage du vœu."
        ),
        "Ange de la vengeance": (
            "Par une action, vous vous transformez pendant 1 heure : des ailes vous poussent dans le dos et vous "
            "obtenez une vitesse de vol de 18 m. Une aura de menace de 9 m vous entoure : la première fois qu'une "
            "créature ennemie y entre ou y commence son tour pendant un combat, elle doit réussir un jet de sauvegarde "
            "de Sagesse (DD 8 + votre bonus de maîtrise + votre modificateur de Charisme) ou être effrayée pendant "
            "1 minute ou jusqu'à ce qu'elle subisse des dégâts. Les jets d'attaque contre une créature ainsi effrayée "
            "ont l'avantage. Utilisable une fois par repos long."
        ),
    },
    "Serment de Conquête": {
        "Conduit divin : Présence conquérante & Frappe guidée": (
            "Présence conquérante : par une action, chaque créature de votre choix à 9 m ou moins doit réussir un jet "
            "de sauvegarde de Sagesse (DD 8 + votre bonus de maîtrise + votre modificateur de Charisme) ou être "
            "effrayée pendant 1 minute ; elle refait le jet à la fin de chacun de ses tours et met fin à l'effet sur "
            "une réussite. Frappe guidée : lorsque vous effectuez un jet d'attaque, vous pouvez dépenser le Conduit "
            "divin pour obtenir un bonus de +10 à ce jet, en décidant après avoir vu le dé mais avant de savoir si "
            "l'attaque touche."
        ),
        "Aura de conquête": (
            "Tant que vous êtes conscient, une aura menaçante de 3 m vous entoure (9 m au niveau 18). Une créature "
            "effrayée par vous qui commence son tour dans l'aura voit sa vitesse réduite à 0 et subit des dégâts "
            "psychiques égaux à la moitié de votre niveau de paladin."
        ),
        "Réprimande méprisante": (
            "Les ennemis qui osent vous frapper le regrettent : lorsqu'une créature vous touche avec une attaque (au "
            "corps à corps ou à distance), elle subit des dégâts psychiques égaux à votre modificateur de Charisme "
            "(minimum 1), à condition que vous ne soyez pas neutralisé. Aucun jet ni réaction requis."
        ),
        "Conquérant invincible": (
            "Par une action, vous devenez une incarnation de la conquête pendant 1 minute : vous avez la résistance à "
            "tous les dégâts ; lorsque vous effectuez l'action Attaquer, vous pouvez faire une attaque supplémentaire "
            "dans le cadre de cette action ; vos attaques d'arme au corps à corps infligent un coup critique sur 19 "
            "ou 20 au dé. Utilisable une fois par repos long."
        ),
    },
    "Serment de Rédemption": {
        "Conduit divin : Émissaire de paix & Réprimander la violence": (
            "Émissaire de paix : par une action bonus, vous obtenez un bonus de +5 à vos tests de Charisme "
            "(Persuasion) pendant 10 minutes. Réprimander la violence : par une réaction, immédiatement après qu'une "
            "créature située à 9 m ou moins a infligé des dégâts avec une attaque à une autre créature que vous, vous "
            "la forcez à faire un jet de sauvegarde de Sagesse (DD 8 + votre bonus de maîtrise + votre modificateur "
            "de Charisme) : elle subit des dégâts radiants égaux à ceux qu'elle vient d'infliger en cas d'échec, ou "
            "la moitié en cas de réussite."
        ),
        "Aura du gardien": (
            "Lorsqu'une créature située à 3 m ou moins de vous subit des dégâts, vous pouvez "
            "utiliser votre réaction pour subir magiquement ces dégâts à sa place. Aucun autre effet de l'attaque "
            "(état, poison…) ne vous est transféré, et ces dégâts ne peuvent pas être réduits par une autre aptitude "
            "de transfert. Le rayon passe à 9 m au niveau 18."
        ),
        "Esprit protecteur": (
            "À la fin de chacun de vos tours, si vous avez au plus la moitié de vos points de vie "
            "maximum et que vous n'êtes pas à 0 point de vie, vous regagnez 1d6 + la moitié de votre niveau de "
            "paladin points de vie."
        ),
        "Émissaire de la rédemption": (
            "Vous incarnez la paix en permanence : vous avez la résistance à tous les dégâts infligés par d'autres "
            "créatures, et chaque fois qu'une créature vous inflige des dégâts, elle subit des dégâts radiants égaux à "
            "la moitié de ceux que vous avez subis. Si vous attaquez une créature, la ciblez avec un sort ou lui "
            "infligez des dégâts autrement que par cette aptitude, vous perdez ces deux bénéfices contre elle jusqu'à "
            "la fin de votre prochain repos long."
        ),
    },
    "Serment de la Gloire": {
        "Conduit divin : Athlète d'exception & Châtiment exaltant": (
            "Athlète d'exception : par une action bonus, pendant 10 minutes, vous avez l'avantage aux tests de Force "
            "(Athlétisme) et de Dextérité (Acrobaties), vous pouvez porter, pousser, tirer et soulever deux fois plus "
            "de poids, et la distance de vos sauts en longueur et en hauteur augmente de 3 m (ce supplément coûte du "
            "déplacement). Châtiment exaltant : immédiatement après avoir infligé des dégâts avec Châtiment divin, "
            "vous pouvez par une action bonus répartir 2d8 + votre niveau de paladin points de vie temporaires entre "
            "les créatures de votre choix situées à 9 m ou moins (vous compris)."
        ),
        "Aura d'alacrité": (
            "Votre vitesse de marche augmente de 3 m. De plus, tant que vous n'êtes pas neutralisé, "
            "chaque créature alliée qui commence son tour à 1,50 m ou moins de vous gagne +3 m de vitesse de marche "
            "jusqu'à la fin de ce tour. Le rayon passe à 3 m au niveau 18."
        ),
        "Défense glorieuse": (
            "Lorsque vous ou une créature que vous voyez à 3 m ou moins êtes touché par un jet d'attaque, vous pouvez "
            "utiliser votre réaction pour ajouter votre modificateur de Charisme (minimum +1) à la CA de la cible "
            "contre cette attaque, ce qui peut la faire échouer. Si l'attaque échoue, vous pouvez effectuer une "
            "attaque d'arme contre l'attaquant s'il est à portée. Utilisable un nombre de fois égal à votre "
            "modificateur de Charisme (minimum 1) ; récupération après un repos long."
        ),
        "Légende vivante": (
            "Par une action bonus, vous rayonnez d'une gloire légendaire pendant 1 minute : vous avez l'avantage à "
            "tous les tests de Charisme ; une fois par tour, lorsque vous ratez une attaque d'arme, vous pouvez "
            "décider qu'elle touche ; lorsque vous ratez un jet de sauvegarde, vous pouvez utiliser votre réaction "
            "pour le relancer et devez garder le nouveau résultat. Utilisable une fois par repos long, ou de nouveau "
            "en dépensant un emplacement de sort du 5e niveau."
        ),
    },
    "Serment des Guetteurs": {
        "Conduit divin : Volonté du guetteur & Abjuration de l'extraplanaire": (
            "Volonté du guetteur : par une action, vous choisissez un nombre de créatures visibles à 9 m ou moins "
            "égal à votre modificateur de Charisme (minimum 1) ; pendant 1 minute, elles (et vous) avez l'avantage aux "
            "jets de sauvegarde d'Intelligence, de Sagesse et de Charisme. Abjuration de l'extraplanaire : par une "
            "action, chaque aberration, céleste, élémentaire, fée ou fiélon à 9 m ou moins qui peut vous entendre "
            "fait un jet de sauvegarde de Sagesse (DD 8 + votre bonus de maîtrise + votre modificateur de Charisme) ; "
            "en cas d'échec, il est renvoyé pendant 1 minute ou jusqu'à ce qu'il subisse des dégâts."
        ),
        "Aura de la sentinelle": (
            "Tant que vous n'êtes pas neutralisé, vous et les créatures de votre choix situées à 3 m ou moins de vous "
            "ajoutez votre bonus de maîtrise à vos jets d'initiative. Le rayon passe à 9 m au niveau 18."
        ),
        "Réprimande vigilante": (
            "Lorsque vous ou une créature que vous voyez à 9 m ou moins réussissez un jet de sauvegarde "
            "d'Intelligence, de Sagesse ou de Charisme, vous pouvez utiliser votre réaction pour infliger 2d8 + votre "
            "modificateur de Charisme dégâts de force à la créature qui a imposé ce jet de sauvegarde."
        ),
        "Rempart des mortels": (
            "Par une action bonus, vous devenez pendant 1 minute un rempart contre l'au-delà : vous obtenez vision "
            "véritable sur 36 m ; vous avez l'avantage aux jets d'attaque contre les aberrations, célestes, "
            "élémentaires, fées et fiélons ; lorsque vous touchez une telle créature et lui infligez des dégâts, vous "
            "pouvez la forcer à réussir un jet de sauvegarde de Charisme (DD de vos sorts) ou être bannie sur son plan "
            "natal si elle n'y est pas. Utilisable une fois par repos long, ou de nouveau en dépensant un emplacement "
            "de sort du 5e niveau."
        ),
    },
    "Serment du Sang": {
        "Conduit divin : Lien hématologique & Lame de sacrifice": (
            "Lien hématologique : par une action bonus, vous visez une créature que vous voyez à 9 m ou moins ; elle "
            "doit réussir un jet de sauvegarde de Constitution (DD 8 + votre bonus de maîtrise + votre modificateur de "
            "Charisme) ou être liée à vous pendant 1 minute. Une fois par tour, lorsque vous subissez des dégâts alors "
            "que la cible est à 18 m ou moins, elle subit des dégâts nécrotiques égaux à la moitié de ces dégâts "
            "(maximum votre niveau de paladin). Le lien cesse si elle tombe à 0 point de vie. Lame de sacrifice : "
            "lorsque vous touchez avec une attaque d'arme au corps à corps, vous pouvez perdre 2d6 points de vie (perte "
            "qui ne peut être réduite) pour infliger 2d8 + votre niveau de paladin dégâts nécrotiques supplémentaires."
        ),
        "Aura de transfusion": (
            "Tant que vous êtes conscient, une aura de 3 m vous entoure (9 m au niveau 18). Une seule fois entre le "
            "début de deux de vos tours, lorsque vous ou une créature amicale dans l'aura touchez une créature hostile "
            "avec une attaque au corps à corps, vous pouvez faire regagner à vous-même ou à l'attaquant un nombre de "
            "points de vie égal à votre modificateur de Charisme (minimum 1). Ne fonctionne pas contre les "
            "créatures artificielles et les morts-vivants."
        ),
        "Châtiment de vampirisme": (
            "Lorsque vous infligez des dégâts avec Châtiment divin, vous pouvez rendre ces dégâts supplémentaires "
            "nécrotiques au lieu de radiants (le bonus contre morts-vivants et fiélons s'applique toujours) et vous "
            "regagnez un nombre de points de vie égal à la moitié des dégâts infligés par les dés du châtiment "
            "(arrondie à l'inférieur). Aucun soin si la cible est une créature artificielle ou un mort-vivant."
        ),
        "Avatar du martyr écarlate": (
            "Par une action bonus, vous devenez pendant 1 minute l'avatar du sang versé : lorsque vos points de vie "
            "devraient tomber à 0, ils tombent à 1 à la place (sauf mort instantanée) ; une fois par tour, lorsque "
            "vous touchez avec une attaque d'arme, la cible subit 2d6 dégâts nécrotiques supplémentaires et vous "
            "regagnez autant de points de vie. À la fin de la transformation, vous subissez un niveau d'épuisement. "
            "Utilisable une fois par repos long."
        ),
    },
    "Serment des Cendres": {
        "Conduit divin : Flamme purificatrice & Cendres aveuglantes": (
            "Flamme purificatrice : par une action bonus, une arme que vous tenez s'embrase pendant 1 minute (lumière "
            "vive sur 6 m et faible sur 6 m de plus) et devient magique. À chaque touche, ses dégâts sont de feu ou "
            "radiants (au choix), et une fois par tour la cible subit en plus des dégâts de feu égaux à votre "
            "modificateur de Charisme (minimum 1). Cendres aveuglantes : par une action, un nuage de cendres emplit "
            "une sphère de 3 m de rayon centrée sur un point visible à 9 m ou moins ; chaque créature de votre choix "
            "dans la zone doit réussir un jet de sauvegarde de Constitution (DD 8 + votre bonus de maîtrise + votre "
            "modificateur de Charisme) ou être aveuglée jusqu'à la fin de votre prochain tour. La zone reste "
            "légèrement obscurcie jusque-là."
        ),
        "Aura du Phénix": (
            "Tant que vous êtes conscient, vous et les créatures amicales situées à 3 m ou moins de vous avez la "
            "résistance aux dégâts de feu (rayon de 9 m au niveau 18). Lorsqu'une créature amicale dans l'aura tombe "
            "à 0 point de vie sans être tuée, vous pouvez utiliser votre réaction pour déclencher une gerbe de "
            "flammes : chaque créature hostile à 3 m ou moins de cette créature fait un jet de sauvegarde de "
            "Dextérité (DD de vos sorts) et subit des dégâts de feu égaux à votre niveau de paladin en cas d'échec, "
            "ou la moitié en cas de réussite."
        ),
        "Renouveau des braises": (
            "Lorsque vous tombez à 0 point de vie sans être tué sur le coup, vous pouvez renaître de vos cendres : vous "
            "tombez à un nombre de points de vie égal à votre niveau de paladin à la place, et chaque créature de "
            "votre choix à 3 m ou moins fait un jet de sauvegarde de Dextérité (DD de vos sorts), subissant 2d8 + "
            "votre modificateur de Charisme dégâts de feu en cas d'échec, ou la moitié en cas de réussite. "
            "Utilisable une fois par repos long."
        ),
        "Avatar du brasier éternel": (
            "Par une action bonus, vous devenez pendant 1 minute un être de feu sacré : vitesse de vol de 18 m, "
            "immunité aux dégâts de feu, lumière vive sur 9 m et faible sur 9 m de plus. Chaque créature hostile qui "
            "commence son tour à 3 m ou moins de vous subit 5 dégâts de feu et 5 dégâts radiants. Vos attaques d'arme "
            "ignorent la résistance au feu. Utilisable une fois par repos long, ou de nouveau en dépensant un "
            "emplacement de sort du 5e niveau."
        ),
    },
}

CORRIGE = [
    # --- Base ---
    ("mineur", "Sens divin", "Détecte « le mal et le bien » en général",
     "Détecte célestes, fiélons et morts-vivants à 18 m (hors abri total) + lieux consacrés/profanés ; action, jusqu'à la fin du prochain tour"),
    ("mineur", "Style de combat", "Option « Combat à deux mains » ambiguë ; options de Tasha absentes",
     "Paladin : Défense, Duel, Arme à deux mains, Protection ; Tasha : Combat en aveugle, Interception, Guerrier béni"),
    ("mineur", "Polyvalence martiale (TCE)", "Option de Tasha absente — ajoutée au niveau 4 « Polyvalence martiale (option Tasha) »",
     "Niveaux 4/8/12/16/19 : possibilité de remplacer le style de combat"),
    ("mineur", "Incantation", "Nombre de sorts préparés, DD et sorts ajoutés par Tasha non indiqués",
     "Préparés = mod. Charisme + moitié du niveau de paladin (min 1) ; DD = 8 + maîtrise + Charisme ; Tasha ajoute 5 sorts"),
    ("mineur", "Châtiment divin", "Bonus +1d8 contre morts-vivants/fiélons omis ; « attaque armée » sans précision",
     "Attaque d'arme au corps à corps ; +1d8 contre mort-vivant ou fiélon (max 6d8)"),
    ("mineur", "Focaliseur de châtiment (Optionnel - TCE)", "Nom inventé ; ni action bonus, ni limite de niveau, ni utilisations — renommé « Exploitation du pouvoir divin (option Tasha) »",
     "« Harness Divine Power » : action bonus, emplacement ≤ moitié du bonus de maîtrise (arr. sup.), 1/2/3 fois par repos long aux niv. 3/7/15"),
    ("info", "Options de Tasha (paladin)", "Aucune option « Harmonious Smite » / « Châtiment harmonieux » n'existe — seules les options officielles sont présentes",
     "Options TCE : styles de combat, Polyvalence martiale, sorts supplémentaires, Harness Divine Power"),
    ("mineur", "Aura de protection", "Minimum +1 et condition « être conscient » absents ; « tous les alliés »",
     "Mod. Charisme (min +1), créatures amicales à 3 m, paladin conscient ; 9 m au niveau 18"),
    ("mineur", "Toucher purificateur", "Nom non officiel ; minimum 1 absent — renommé « Contact purifiant »",
     "VF : « Contact purifiant » ; action, mod. Charisme (min 1) utilisations / repos long"),
    ("info", "Champion sacré", "Aptitude de base inexistante (placeholder) — supprimée",
     "Au niveau 20, le paladin reçoit uniquement l'aptitude ultime de son serment"),
    # --- Dévotion ---
    ("mineur", "Serment de Dévotion / sorts", "« Protection contre le bien et le mal » (ordre inversé), « Colonne de feu »",
     "VF : Protection contre le mal et le bien ; Colonne de flamme"),
    ("majeur", "Serment de Dévotion / sorts", "Niv. 5 : Aide, « Restaurer l'innocence » (inexistant)",
     "Niv. 5 : Restauration partielle, Zone de vérité"),
    ("majeur", "Serment de Dévotion / sorts", "Niv. 9 : Lumière du jour, Réflexion",
     "Niv. 9 : Lueur d'espoir, Dissipation de la magie"),
    ("mineur", "Serment de Dévotion / Arme sacrée", "Minimum +1, lumière 6 m et durée de 1 min absents",
     "Action, 1 min, + mod. Charisme (min +1) à l'attaque, lumière vive 6 m + faible 6 m"),
    ("mineur", "Serment de Dévotion / Nimbe sacrée", "Genre (« Nimbe sacré ») ; durée 1 min et avantage aux JS absents",
     "Action, 1 min, 10 radiants en lumière vive 9 m, avantage aux JS contre sorts de fiélons/morts-vivants"),
    # --- Anciens ---
    ("majeur", "Serment des Anciens / sorts", "Niv. 3 : Enchevêtrement ; « Parler avec les animaux »",
     "Niv. 3 : Frappe piégeuse, Communication avec les animaux"),
    ("majeur", "Serment des Anciens / sorts", "Niv. 5 : Immobilisation de personne au lieu de Foulée brumeuse",
     "Niv. 5 : Rayon de lune, Foulée brumeuse"),
    ("majeur", "Serment des Anciens / sorts", "Niv. 13 : Liberté de mouvement, Forme animale",
     "Niv. 13 : Tempête de grêle, Peau de pierre"),
    ("majeur", "Serment des Anciens / sorts", "Niv. 17 : « Rejeton de la nature »",
     "Niv. 17 : Communion avec la nature, Passage par les arbres"),
    ("majeur", "Serment des Anciens / Champion antique", "« Désavantage aux sorts ennemis » (effet inversé)",
     "Les ennemis à 3 m ont un désavantage aux JS contre vos sorts de paladin et Conduit divin ; action, 1 min"),
    ("mineur", "Serment des Anciens / Courroux de la nature", "Portée 3 m et JS répété non indiqués",
     "Créature visible à 3 m, entravée, JS Force ou Dex à la fin de chacun de ses tours"),
    ("info", "Serment des Anciens / Sentinelle immortelle", "Immunité au vieillissement omise",
     "Ne subit plus les effets de l'âge, ne peut pas être vieilli magiquement"),
    # --- Vengeance ---
    ("majeur", "Serment de Vengeance / sorts", "Niv. 3 : Frayeur, « Marque du reître »",
     "Niv. 3 : Fléau, Marque du chasseur"),
    ("majeur", "Serment de Vengeance / sorts", "Niv. 5 : Rayon d'affaiblissement",
     "Niv. 5 : Immobilisation de personne, Foulée brumeuse"),
    ("majeur", "Serment de Vengeance / sorts", "Niv. 17 : « Scinder » (inexistant)",
     "Niv. 17 : Immobilisation de monstre, Scrutation"),
    ("mineur", "Serment de Vengeance / Condamnation de l'ennemi", "Portée 18 m, vitesse 0 et effet en cas de réussite absents",
     "18 m ; échec : effrayé + vitesse 0 (1 min) ; réussite : vitesse réduite de moitié"),
    ("mineur", "Serment de Vengeance / Vengeur implacable", "Déclenché par toute attaque d'opportunité",
     "Uniquement quand l'attaque d'opportunité touche ; déplacement sans provoquer d'attaque d'opportunité"),
    ("mineur", "Serment de Vengeance / Ange de la vengeance", "Durée (1 h) et vol 18 m absents",
     "Action, 1 heure, vol 18 m, aura de menace 9 m ; 1/repos long"),
    # --- Conquête ---
    ("mineur", "Serment de Conquête / sorts", "« Armure de agathys »",
     "Armure d'Agathys"),
    ("majeur", "Serment de Conquête / sorts", "Niv. 3 : Frayeur ; niv. 5 : Cécité/Surdité",
     "Niv. 3 : Armure d'Agathys, Injonction ; niv. 5 : Immobilisation de personne, Arme spirituelle"),
    ("majeur", "Serment de Conquête / sorts", "Niv. 9 : Forme spirituelle",
     "Niv. 9 : Malédiction, Peur"),
    ("majeur", "Serment de Conquête / sorts", "Niv. 13 : Domination de personne, Sanctuaire",
     "Niv. 13 : Domination de bête, Peau de pierre"),
    ("majeur", "Serment de Conquête / sorts", "Niv. 17 : Domination de monstre",
     "Niv. 17 : Brume mortelle (Cloudkill), Domination de personne"),
    ("majeur", "Serment de Conquête / Aura de conquête", "10 dégâts psychiques fixes",
     "Dégâts psychiques = moitié du niveau de paladin ; aura 3 m (9 m au niv. 18)"),
    ("mineur", "Serment de Conquête / Réprimande méprisante", "Limité au corps à corps",
     "Toute attaque qui touche ; mod. Charisme (min 1), si non neutralisé"),
    # --- Rédemption ---
    ("majeur", "Serment de Rédemption / sorts", "Liste presque entièrement fausse, sorts inexistants (Apaisement, Sanctuaire suprême, Calme absolu) et sort mineur (Résistance)",
     "3 : Sanctuaire, Sommeil ; 5 : Apaisement des émotions, Immobilisation de personne ; 9 : Contresort, Motif hypnotique ; 13 : Sphère résiliente d'Otiluke, Peau de pierre ; 17 : Immobilisation de monstre, Mur de force"),
    ("mineur", "Serment de Rédemption / Aura de sacrifice", "Nom non officiel ; utilisation de la réaction non indiquée — renommée « Aura du gardien »",
     "Aura du gardien : réaction, subir les dégâts d'une créature à 3 m"),
    ("majeur", "Serment de Rédemption / Protection spirituelle", "1d6 + 10 au début du tour — renommée « Esprit protecteur »",
     "Esprit protecteur : 1d6 + moitié du niveau de paladin à la fin du tour, si ≤ moitié des PV et > 0"),
    ("majeur", "Serment de Rédemption / Émissaire de la rédemption", "Limité à 1/repos long",
     "Permanent ; perdu contre une créature attaquée/ciblée jusqu'au prochain repos long"),
    # --- Gloire ---
    ("majeur", "Serment de la Gloire / sorts", "Guide (sort mineur), « Longstrider » (anglais), « Magie de guerre », Divination, « Périple planétaire », « Don des héros »",
     "3 : Éclair traçant, Héroïsme ; 5 : Amélioration de caractéristique, Arme magique ; 9 : Hâte, Protection contre une énergie ; 13 : Compulsion, Liberté de mouvement ; 17 : Communion, Colonne de flamme"),
    ("mineur", "Serment de la Gloire / Châtiment exaltant", "Montant des PV temporaires absent",
     "Action bonus après Châtiment divin : 2d8 + niveau de paladin PV temporaires répartis à 9 m"),
    ("mineur", "Serment de la Gloire / Aura d'entrain", "Rayon 3 m ; nom non officiel — renommée « Aura d'alacrité »",
     "+3 m de vitesse pour vous ; alliés commençant leur tour à 1,50 m : +3 m (3 m au niveau 18)"),
    ("majeur", "Serment de la Gloire / Défense glorieuse", "1/repos long",
     "Utilisations = mod. Charisme (min 1) / repos long ; réaction, cible à 3 m"),
    ("info", "Serment de la Gloire / Légende vivante", "Action bonus, limite « une fois par tour » et recharge par emplacement du 5e niveau omises",
     "Action bonus, 1 min ; 1/repos long ou emplacement du 5e niveau"),
    # --- Guetteurs ---
    ("majeur", "Serment des Guetteurs / sorts", "Détection du mal et du bien, « Fausse alarme », Aide, Zone de vérité, Clairvoyance, Œil mystique, Divination, Communication à distance",
     "3 : Alarme, Détection de la magie ; 5 : Rayon de lune, Voir l'invisible ; 9 : Contresort, Antidétection ; 13 : Aura de vie, Bannissement ; 17 : Immobilisation de monstre, Scrutation"),
    ("majeur", "Serment des Guetteurs / Aura de la sentinelle", "Bonus = mod. Charisme (ou +6) à 9 m dès le niveau 7",
     "Bonus d'initiative = bonus de maîtrise, rayon 3 m (9 m au niveau 18)"),
    ("mineur", "Serment des Guetteurs / Réprimande vigilante", "Montant des dégâts absent",
     "Réaction : 2d8 + mod. Charisme dégâts de force à la créature ayant imposé le JS"),
    ("mineur", "Serment des Guetteurs / Aplomb du guetteur", "Nombre de cibles et portée absents ; noms non officiels — renommé « Volonté du guetteur & Abjuration de l'extraplanaire »",
     "Volonté du guetteur : mod. Charisme (min 1) créatures à 9 m, avantage aux JS Int/Sag/Cha 1 min"),
    ("info", "Serment des Guetteurs / source", "« Guide de Wildemount » : source erronée — corrigée en « Chaudron des Merveilles de Tasha »",
     "Oath of the Watchers : Tasha's Cauldron of Everything (2020)"),
    # --- Homebrew : sorts ---
    ("mineur", "Serment du Sang / sorts", "« Vampirisme » et « Drain de vie » ne sont pas des sorts officiels",
     "Remplacés par Toucher du vampire (niv. 9) ; liste : Frayeur, Fléau / Rayon affaiblissant, Cécité/Surdité / Toucher du vampire, Peur / Flétrissement, Confusion / Contagion, Fléau d'insectes"),
    ("info", "Serment du Sang / sorts", "Sorts trop élevés pour leur niveau d'obtention (Rayon d'affaiblissement au niv. 3, Fléau d'insectes et Contagion niv. 5 au niv. 13)",
     "Sorts de serment : niveau de sort ≤ emplacements disponibles (1/2/3/4/5 aux niv. 3/5/9/13/17) — liste réordonnée"),
    ("mineur", "Serment des Cendres / sorts", "« Châtiment incandescent », « Rayon ardent », « Colonne de feu »",
     "Noms de la base : Châtiment calcinant, Rayon ardent, Colonne de flamme"),
    ("mineur", "Serment des Cendres / sorts", "Essaim de météores (sort du 9e niveau) inutilisable par un paladin ; Mur de feu (4e) au niv. 9",
     "Liste ≤ 5e niveau : Mains brûlantes, Châtiment calcinant / Rayon ardent, Sphère de feu / Boule de feu, Châtiment aveuglant / Mur de feu, Bouclier de feu / Colonne de flamme, Immolation"),
]

# Aucun écart volontairement laissé non corrigé.
AUDIT = []
