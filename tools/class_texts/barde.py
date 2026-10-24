"""Descriptions enrichies — Barde (PHB, Xanathar, Tasha ; sous-classes communautaires rééquilibrées)."""
CLASSE = "Barde"

DD_SORTS = "8 + votre bonus de maîtrise + votre modificateur de Charisme"

BASE = {
    "Incantation": (
        "Le Charisme est votre caractéristique d'incantation : le DD de sauvegarde de vos sorts est égal à "
        f"{DD_SORTS}, et votre bonus d'attaque avec un sort est égal à votre bonus de maîtrise + votre modificateur "
        "de Charisme. Vous connaissez 2 sorts mineurs de barde au niveau 1 (3 au niveau 4, 4 au niveau 10) et 4 sorts "
        "de niveau 1 ; le nombre de sorts connus augmente ensuite selon la table de progression (22 au niveau 20). "
        "Vous lancez vos sorts en dépensant des emplacements, récupérés après un repos long. Chaque fois que vous "
        "gagnez un niveau de barde, vous pouvez remplacer un sort connu par un autre sort de barde d'un niveau que vous "
        "pouvez lancer. Vous pouvez lancer un sort connu possédant le type rituel sans dépenser d'emplacement, et vous "
        "pouvez utiliser un instrument de musique comme focaliseur d'incantation."
    ),
    "Inspiration bardique (d6)": (
        "Par une action bonus, choisissez une créature autre que vous située à 18 mètres ou moins et qui peut vous "
        "entendre : elle reçoit un dé d'Inspiration bardique (d6). Dans les 10 minutes qui suivent, elle peut le lancer "
        "et ajouter le résultat à un test de caractéristique, un jet d'attaque ou un jet de sauvegarde, après avoir vu "
        "le d20 mais avant que le MD annonce la réussite ou l'échec. Une créature ne peut détenir qu'un seul de ces dés "
        "à la fois. Vous pouvez utiliser cette aptitude un nombre de fois égal à votre modificateur de Charisme "
        "(minimum 1) et récupérez toutes les utilisations après un repos long. Le dé devient un d8 au niveau 5, "
        "un d10 au niveau 10 et un d12 au niveau 15."
    ),
    "Sorts de barde supplémentaires (option Tasha)": (
        "Option du Chaudron des merveilles de Tasha : votre liste de sorts de barde s'enrichit de nouveaux sorts, "
        "que vous pouvez apprendre normalement lorsque vous gagnez ou remplacez un sort connu. Niveau 1 : Couleurs "
        "dansantes, Injonction ; niveau 2 : Aide, Agrandissement/Rapetissement, Image miroir ; niveau 3 : Forteresse "
        "d'intellect, Lenteur, Mot de guérison de groupe ; niveau 4 : Assassin imaginaire ; niveau 5 : Lien "
        "télépathique de Rary ; niveau 6 : Festin des héros ; niveau 7 : Rayons prismatiques ; niveau 8 : "
        "Antipathie/Sympathie ; niveau 9 : Mur prismatique."
    ),
    "Inspiration magique (option Tasha)": (
        "Option du Chaudron des merveilles de Tasha : une créature qui détient l'un de vos dés d'Inspiration "
        "bardique et qui lance un sort rendant des points de vie ou infligeant des dégâts peut lancer ce dé et "
        "ajouter le résultat aux points de vie rendus ou aux dégâts infligés à une seule cible du sort. Le dé est "
        "alors consommé."
    ),
    "Polyvalence bardique (option Tasha)": (
        "Option du Chaudron des merveilles de Tasha : chaque fois que vous atteignez dans cette classe un niveau qui vous "
        "accorde une Amélioration de caractéristique, vous pouvez effectuer l'un des échanges suivants, qui "
        "reflètent l'évolution de votre pratique artistique : remplacer une compétence choisie pour Expertise par "
        "une autre compétence que vous maîtrisez, ou remplacer un sort mineur de barde que vous connaissez par un "
        "autre sort mineur de la liste du barde."
    ),
    "Touche-à-tout": (
        "Vous ajoutez un bonus égal à la moitié (arrondie à l'inférieur) de votre bonus de maîtrise à tout test de caractéristique "
        "qui n'inclut pas déjà votre maîtrise. Cela s'applique notamment aux tests d'initiative (Dextérité), "
        "aux compétences et outils que vous ne maîtrisez pas et aux tests de caractéristique bruts."
    ),
    "Chanson de repos (d6)": (
        "Pendant un repos court, vous pouvez jouer de la musique ou déclamer pour revigorer vos compagnons. Si vous-même "
        "ou des créatures amicales qui entendent votre prestation récupérez des points de vie en dépensant des dés de "
        "vie à la fin de ce repos, chacune de ces créatures récupère 1d6 points de vie supplémentaires (une seule fois "
        "par repos, quel que soit le nombre de dés de vie dépensés). Le dé passe à 1d8 au niveau 9, 1d10 au niveau 13 "
        "et 1d12 au niveau 17."
    ),
    "Collège bardique": (
        "Vous rejoignez un collège bardique, une association informelle de bardes partageant les mêmes traditions : "
        "Savoir ou Vaillance (Manuel des Joueurs), Séduction, Épées ou Murmures (Xanathar), Éloquence ou Création "
        "(Tasha), ou un collège communautaire. Ce choix vous confère des aptitudes aux niveaux 3, 6 et 14."
    ),
    "Expertise": (
        "Choisissez deux compétences que vous maîtrisez : votre bonus de maîtrise est doublé pour tout test de "
        "caractéristique utilisant l'une d'elles. Ces compétences ne bénéficient plus de Touche-à-tout puisqu'elles "
        "incluent déjà votre bonus de maîtrise. Vous choisirez deux compétences supplémentaires au niveau 10."
    ),
    "Inspiration bardique (d8)": (
        "Votre dé d'Inspiration bardique devient un d8. Le fonctionnement reste le même : action bonus, une créature "
        "à 18 mètres ou moins qui peut vous entendre, utilisable dans les 10 minutes, un nombre de fois égal à votre "
        "modificateur de Charisme (minimum 1)."
    ),
    "Source d'inspiration": (
        "Vous récupérez toutes vos utilisations d'Inspiration bardique à la fin d'un repos court ou d'un repos long, "
        "et non plus seulement après un repos long. Cela vous permet d'être beaucoup plus généreux en inspiration "
        "au cours d'une journée d'aventure."
    ),
    "Contre-charme": (
        "Par une action, vous commencez une prestation (musique ou paroles) qui dure jusqu'à la fin de votre prochain "
        "tour. Pendant ce temps, vous et chaque créature amicale située à 9 mètres ou moins de vous et qui peut vous "
        "entendre obtenez l'avantage aux jets de sauvegarde contre les effets qui charment ou effraient. La "
        "prestation s'arrête prématurément si vous êtes neutralisé ou réduit au silence, ou si vous y mettez fin "
        "volontairement (aucune action requise)."
    ),
    "Chanson de repos (d8)": (
        "Les points de vie supplémentaires accordés par votre Chanson de repos passent à 1d8 pour chaque créature "
        "qui dépense au moins un dé de vie à la fin d'un repos court en entendant votre prestation."
    ),
    "Chanson de repos (d10)": (
        "Les points de vie supplémentaires accordés par votre Chanson de repos passent à 1d10 pour chaque créature "
        "qui dépense au moins un dé de vie à la fin d'un repos court en entendant votre prestation."
    ),
    "Chanson de repos (d12)": (
        "Les points de vie supplémentaires accordés par votre Chanson de repos atteignent leur maximum : 1d12 pour "
        "chaque créature qui dépense au moins un dé de vie à la fin d'un repos court en entendant votre prestation."
    ),
    "Inspiration bardique (d10)": (
        "Votre dé d'Inspiration bardique devient un d10. Toujours accordé par une action bonus à une créature à "
        "18 mètres ou moins, un nombre de fois égal à votre modificateur de Charisme (minimum 1), récupéré après un "
        "repos court ou long."
    ),
    "Expertise (supplémentaire)": (
        "Choisissez deux autres compétences que vous maîtrisez : votre bonus de maîtrise est doublé pour tout test de "
        "caractéristique qui les utilise. Vous disposez désormais de quatre compétences avec Expertise."
    ),
    "Secrets magiques": (
        "Vous avez puisé dans le savoir magique de nombreuses traditions. Choisissez deux sorts dans la liste de "
        "n'importe quelle classe (sorts mineurs compris) ; ils doivent être d'un niveau que vous pouvez lancer. Ils "
        "deviennent des sorts de barde pour vous et comptent dans votre nombre de sorts connus. Vous pourrez les "
        "remplacer plus tard par d'autres sorts issus de n'importe quelle liste lorsque vous changez un sort connu. "
        "Vous apprenez deux nouveaux sorts de cette manière aux niveaux 14 et 18."
    ),
    "Secrets magiques (niveau 14)": (
        "Nouvelle utilisation de Secrets magiques : choisissez deux sorts supplémentaires (sorts mineurs compris) dans "
        "la liste de n'importe quelle classe, d'un niveau que vous pouvez lancer. Ils comptent comme des sorts de barde "
        "et sont inclus dans votre nombre de sorts connus."
    ),
    "Inspiration bardique (d12)": (
        "Votre dé d'Inspiration bardique atteint sa taille maximale : un d12. Il s'utilise toujours par une action "
        "bonus sur une créature à 18 mètres ou moins, un nombre de fois égal à votre modificateur de Charisme "
        "(minimum 1) entre deux repos courts ou longs."
    ),
    "Secrets magiques (niveau 18)": (
        "Dernière utilisation de Secrets magiques : choisissez deux sorts supplémentaires (sorts mineurs compris) dans "
        "la liste de n'importe quelle classe, d'un niveau que vous pouvez lancer, y compris désormais des sorts de "
        "niveau 9. Ils comptent comme des sorts de barde et sont inclus dans votre nombre de sorts connus."
    ),
    "Inspiration supérieure": (
        "Lorsque vous lancez l'initiative et qu'il ne vous reste aucune utilisation d'Inspiration bardique, vous en "
        "récupérez immédiatement une. Vous pouvez ainsi toujours commencer un combat en inspirant au moins un allié."
    ),
}

SUB = {
    "Collège du Savoir": {
        "Maîtrises supplémentaires": (
            "Vous gagnez la maîtrise de trois compétences de votre choix. Combinées à Touche-à-tout et Expertise, ces "
            "maîtrises font de vous un expert polyvalent capable de couvrir presque toutes les compétences du groupe."
        ),
        "Mots cinglants": (
            "Lorsqu'une créature que vous pouvez voir, située à 18 mètres ou moins de vous, effectue un jet d'attaque, "
            "un test de caractéristique ou un jet de dégâts, vous pouvez utiliser votre réaction et dépenser une "
            "utilisation d'Inspiration bardique : lancez le dé et soustrayez le résultat du jet de la créature. Vous "
            "pouvez décider après avoir vu le jet, mais avant que le MD annonce la réussite ou l'échec, ou avant que "
            "les dégâts soient infligés. La créature est immunisée si elle ne peut pas vous entendre ou si elle est "
            "immunisée contre l'état charmé."
        ),
        "Secrets magiques supplémentaires": (
            "Au niveau 6, vous apprenez deux sorts de votre choix (sorts mineurs compris) dans la liste de n'importe "
            "quelle classe, d'un niveau que vous pouvez lancer (jusqu'au niveau 3 à ce stade). Ils comptent comme des "
            "sorts de barde pour vous mais ne sont pas décomptés de votre nombre de sorts connus."
        ),
        "Capacité inégalée": (
            "Lorsque vous effectuez un test de caractéristique, vous pouvez dépenser une utilisation d'Inspiration "
            "bardique : lancez le dé et ajoutez le résultat à votre test. Vous pouvez le décider après avoir lancé le "
            "d20, mais avant que le MD annonce la réussite ou l'échec."
        ),
    },
    "Collège de la Vaillance": {
        "Maîtrises supplémentaires": (
            "Vous gagnez la maîtrise des armures intermédiaires, des boucliers et des armes de guerre, ce qui vous "
            "permet de tenir la première ligne aux côtés des combattants."
        ),
        "Inspiration martiale": (
            "Une créature qui détient l'un de vos dés d'Inspiration bardique peut aussi l'utiliser de deux façons "
            "supplémentaires : l'ajouter au jet de dégâts d'une attaque avec une arme qu'elle vient de réussir, ou, "
            "lorsqu'une attaque la vise, utiliser sa réaction pour lancer le dé et ajouter le résultat à sa CA contre "
            "cette attaque, après avoir vu le jet mais avant de savoir s'il touche."
        ),
        "Attaque supplémentaire": (
            "Lorsque vous effectuez l'action Attaquer lors de votre tour, vous pouvez attaquer deux fois au lieu d'une."
        ),
        "Magie guerrière": (
            "Lorsque vous utilisez votre action pour lancer un sort de barde, vous pouvez effectuer une attaque avec "
            "une arme par une action bonus lors du même tour."
        ),
    },
    "Collège de la Séduction": {
        "Apparence inspirante": (
            "Par une action bonus, dépensez une utilisation d'Inspiration bardique pour envelopper vos alliés d'une aura "
            "féerique. Choisissez un nombre de créatures égal à votre modificateur de Charisme (minimum 1), vous "
            "compris, situées à 18 mètres ou moins et capables de vous voir ou de vous entendre : chacune gagne 5 points "
            "de vie temporaires (8 au niveau 5, 11 au niveau 10, 14 au niveau 15). Chacune peut aussitôt utiliser sa "
            "réaction pour se déplacer d'une distance égale à sa vitesse sans provoquer d'attaques d'opportunité."
        ),
        "Représentation envoûtante": (
            "Si vous vous produisez pendant au moins 1 minute (chant, discours, danse…), vous pouvez, à la fin de la "
            "prestation, choisir un nombre d'humanoïdes égal à votre modificateur de Charisme (minimum 1) qui l'ont "
            "vue ou entendue, situés à 18 mètres ou moins. Chacun fait un jet de sauvegarde de Sagesse (DD = "
            f"{DD_SORTS}) ; en cas d'échec, il est charmé par vous pendant 1 heure : il vous idolâtre, vante vos "
            "mérites et gêne ceux qui s'opposent à vous, en évitant la violence. L'effet cesse si la cible subit des "
            "dégâts, si vous l'attaquez ou si elle vous voit attaquer ou blesser ses alliés. En cas de réussite, elle "
            "ignore que vous avez tenté de la charmer. Utilisable une fois par repos court ou long."
        ),
        "Apparence majestueuse": (
            "Par une action bonus, vous lancez Injonction sans dépenser d'emplacement de sort et prenez une apparence "
            "d'une beauté surnaturelle pendant 1 minute, ou jusqu'à la fin de votre concentration (comme pour un sort). "
            "Pendant cette durée, vous pouvez lancer Injonction par une action bonus à chacun de vos tours sans "
            "emplacement. Toute créature charmée par vous échoue automatiquement à son jet de sauvegarde contre ces "
            "Injonctions. Utilisable une fois par repos long."
        ),
        "Majesté inébranlable": (
            "Par une action bonus, vous adoptez une présence majestueuse pendant 1 minute ou jusqu'à ce que vous soyez "
            "neutralisé. Pendant cette durée, la première fois qu'une créature tente de vous attaquer lors d'un tour, "
            f"elle doit réussir un jet de sauvegarde de Charisme (DD = {DD_SORTS}). En cas d'échec, elle ne peut pas "
            "vous attaquer ce tour-ci et doit choisir une autre cible, sinon l'attaque est perdue. En cas de réussite, "
            "elle peut vous attaquer ce tour-ci mais a un désavantage à ses jets de sauvegarde contre vos sorts lors de "
            "votre prochain tour. Utilisable une fois par repos court ou long."
        ),
    },
    "Collège des Épées": {
        "Maîtrises supplémentaires": (
            "Vous gagnez la maîtrise des armures intermédiaires et du cimeterre. De plus, si vous maîtrisez une arme de "
            "corps à corps, vous pouvez l'utiliser comme focaliseur d'incantation pour vos sorts de barde."
        ),
        "Style de combat": (
            "Vous adoptez un style de combat : Duel (+2 aux dégâts lorsque vous maniez une arme de corps à corps dans "
            "une main et aucune autre arme) ou Combat à deux armes (vous ajoutez votre modificateur de caractéristique "
            "aux dégâts de l'attaque de votre arme secondaire). Vous ne pouvez pas choisir le même style deux fois, "
            "même si une autre aptitude vous en accorde un."
        ),
        "Moulinet": (
            "Lorsque vous effectuez l'action Attaquer, votre vitesse de marche augmente de 3 mètres jusqu'à la fin du "
            "tour. Si une attaque avec une arme touche, vous pouvez dépenser une utilisation d'Inspiration bardique "
            "pour réaliser un moulinet (un seul par tour) ; le dé s'ajoute aux dégâts de l'attaque, plus un effet : "
            "Défensif (le résultat s'ajoute à votre CA jusqu'au début de votre prochain tour), Tranchant (une autre "
            "créature de votre choix à 1,50 mètre ou moins de vous subit des dégâts égaux au résultat, du même type) "
            "ou Mobile (vous repoussez la cible de 1,50 mètre plus 30 cm par point du dé, puis pouvez utiliser votre "
            "réaction pour vous déplacer jusqu'à votre vitesse vers un espace à 1,50 mètre d'elle)."
        ),
        "Attaque supplémentaire": (
            "Lorsque vous effectuez l'action Attaquer lors de votre tour, vous pouvez attaquer deux fois au lieu d'une."
        ),
        "Moulinet de maître": (
            "Chaque fois que vous utilisez une option de Moulinet, vous pouvez lancer un d6 et l'utiliser à la place "
            "d'un dé d'Inspiration bardique, sans dépenser d'utilisation. Vous pouvez ainsi réaliser un moulinet à "
            "chaque tour sans épuiser votre inspiration."
        ),
    },
    "Collège des Murmures": {
        "Lame psychique": (
            "Lorsque vous touchez une créature avec une attaque d'arme, vous pouvez dépenser une utilisation "
            "d'Inspiration bardique pour infliger 2d6 dégâts psychiques supplémentaires à cette cible. Les dégâts "
            "passent à 3d6 au niveau 5, 5d6 au niveau 10 et 8d6 au niveau 15. Vous ne pouvez utiliser cette aptitude "
            "qu'une fois par round, lors de votre tour."
        ),
        "Mots de terreur": (
            "Si vous parlez à un humanoïde seul à seul pendant au moins 1 minute, vous pouvez, à la fin de la "
            f"conversation, lui imposer un jet de sauvegarde de Sagesse (DD = {DD_SORTS}). En cas d'échec, il est "
            "effrayé par vous ou par une autre créature de votre choix pendant 1 heure, ou jusqu'à ce qu'il soit "
            "attaqué ou blessé, ou qu'il voie ses alliés l'être. En cas de réussite, il ne soupçonne rien. "
            "Utilisable une fois par repos court ou long."
        ),
        "Voile de murmure": (
            "Lorsqu'un humanoïde meurt à 9 mètres ou moins de vous, vous pouvez utiliser votre réaction pour capturer "
            "son ombre, que vous conservez jusqu'à son utilisation ou jusqu'à un repos long. Par une action, vous "
            "l'utilisez pour prendre l'apparence du défunt pendant 1 heure (fin anticipée par une action bonus) et "
            "obtenez des bribes de ses souvenirs. Pour percer le déguisement, une créature doit réussir un test "
            "d'Intelligence (Investigation) opposé à votre test de Charisme (Tromperie) + 5. Utilisable une fois par "
            "repos court ou long."
        ),
        "Savoir des ombres": (
            "Par une action, vous murmurez une phrase que seule une créature de votre choix, à 9 mètres ou moins, peut "
            f"entendre. Elle fait un jet de sauvegarde de Sagesse (DD = {DD_SORTS}) et réussit automatiquement si elle "
            "ne partage aucune langue avec vous ou ne peut pas vous entendre. En cas d'échec, elle est charmée par vous "
            "pendant 8 heures, ou jusqu'à ce que vous ou vos alliés l'attaquiez ou la blessiez : persuadée que vous "
            "connaissez son secret le plus honteux, elle obéit à vos ordres sans se mettre en danger. Utilisable une "
            "fois par repos long."
        ),
    },
    "Collège de l'Éloquence": {
        "Faconde": (
            "Lorsque vous effectuez un test de Charisme (Persuasion) ou de Charisme (Tromperie), vous pouvez considérer "
            "tout résultat de 9 ou moins sur le d20 comme un 10. Votre résultat minimal est donc 10 + votre bonus de "
            "maîtrise + votre modificateur de Charisme (davantage avec Expertise)."
        ),
        "Paroles déstabilisantes": (
            "Par une action bonus, dépensez une utilisation d'Inspiration bardique et choisissez une créature que vous "
            "pouvez voir, à 18 mètres ou moins. Lancez le dé d'Inspiration : la créature soustrait le résultat de son "
            "prochain jet de sauvegarde effectué avant le début de votre prochain tour. Idéal juste avant un sort "
            "imposant une sauvegarde."
        ),
        "Inspiration indéfectible": (
            "Lorsqu'une créature ajoute l'un de vos dés d'Inspiration bardique à un test de caractéristique, un jet "
            "d'attaque ou un jet de sauvegarde et que le jet échoue malgré tout, elle conserve le dé et peut le "
            "réutiliser plus tard."
        ),
        "Discours universel": (
            "Par une action, choisissez un nombre de créatures égal à votre modificateur de Charisme (minimum 1) "
            "situées à 18 mètres ou moins. Pendant 1 heure, elles comprennent magiquement tout ce que vous dites, "
            "quelle que soit la langue employée. Utilisable une fois par repos long ; vous pouvez la réutiliser en "
            "dépensant un emplacement de sort de n'importe quel niveau."
        ),
        "Inspiration contagieuse": (
            "Lorsqu'une créature à 18 mètres ou moins réussit un test de caractéristique, un jet d'attaque ou un jet de "
            "sauvegarde grâce à votre dé d'Inspiration bardique, vous pouvez utiliser votre réaction pour encourager une "
            "autre créature à 18 mètres ou moins qui peut vous entendre : elle reçoit un dé d'Inspiration bardique sans "
            "que vous dépensiez d'utilisation. Utilisable un nombre de fois égal à votre modificateur de Charisme "
            "(minimum 1), récupéré après un repos long."
        ),
    },
    "Collège de la Création": {
        "Grain de potentiel": (
            "Quand vous accordez un dé d'Inspiration bardique, vous pouvez créer un minuscule grain de potentiel qui "
            "gravite autour de la créature. Selon l'usage du dé : test de caractéristique, la créature peut relancer "
            "le dé d'Inspiration et choisir le résultat ; jet d'attaque, le grain éclate et la cible ainsi que chaque "
            "créature de votre choix à 1,50 mètre d'elle doivent réussir un jet de sauvegarde de Constitution "
            f"(DD = {DD_SORTS}) ou subir des dégâts de tonnerre égaux au résultat du dé ; jet de sauvegarde, la "
            "créature gagne des points de vie temporaires égaux au résultat du dé + votre modificateur de Charisme "
            "(minimum 1)."
        ),
        "Créativité concrète": (
            "Par une action, vous créez un objet non magique dans un espace inoccupé à 3 mètres ou moins, sur une "
            "surface ou un liquide capable de le porter. Sa valeur ne peut dépasser 20 × votre niveau de barde po ; il "
            "est de taille M ou inférieure (G au niveau 6, TG au niveau 14). L'objet scintille légèrement et disparaît "
            "au bout d'un nombre d'heures égal à votre bonus de maîtrise ; un seul objet à la fois. Utilisable une fois "
            "par repos long, ou en dépensant un emplacement de sort de niveau 2 ou supérieur."
        ),
        "Prestation dansante": (
            "Par une action, vous animez un objet non magique de taille G ou inférieure à 9 mètres ou moins, qui "
            "devient un Objet dansant pendant 1 heure (ou jusqu'à 0 PV ou votre mort) : CA 16, points de vie égaux à "
            "10 + 5 × votre niveau de barde, vitesse 9 m et vol 9 m (stationnaire). Il agit juste après vous et obéit "
            "à vos ordres (action bonus) ; son Coup de force inflige 1d10 + votre bonus de maîtrise dégâts de force "
            "(attaque de sort). Sa Danse irrépressible modifie de 3 mètres la vitesse des créatures qui commencent leur "
            "tour à 3 mètres de lui. Une fois par repos long, ou via un emplacement de niveau 3 ou supérieur."
        ),
        "Crescendo créatif": (
            "Lorsque vous utilisez Créativité concrète, vous pouvez créer plusieurs objets à la fois : un nombre égal à "
            "votre modificateur de Charisme (minimum 2). Un seul peut atteindre la taille maximale ; les autres sont de "
            "taille P ou TP. Vous n'êtes plus limité par la valeur en po des objets créés."
        ),
    },
    "Collège des Commandants": {
        "Ordres tactiques": (
            "Par une action bonus, dépensez une utilisation d'Inspiration bardique et choisissez une créature alliée à "
            "18 mètres ou moins qui peut vous entendre. Elle peut aussitôt utiliser sa réaction pour effectuer une "
            "attaque avec une arme (elle ajoute le dé d'Inspiration au jet de dégâts si elle touche) ou pour se "
            "déplacer de la moitié de sa vitesse sans provoquer d'attaques d'opportunité."
        ),
        "Prescience de bataille": (
            "Vous ajoutez votre modificateur de Charisme (minimum 1) à vos jets d'initiative. De plus, lorsque vous "
            "lancez l'initiative, vous pouvez dépenser une utilisation d'Inspiration bardique : lancez le dé et "
            "ajoutez le résultat à l'initiative d'un nombre d'alliés égal à votre modificateur de Charisme (minimum 1) "
            "situés à 9 mètres ou moins et capables de vous entendre."
        ),
        "Hymne de ralliement": (
            "Une créature qui détient l'un de vos dés d'Inspiration bardique a l'avantage aux jets de sauvegarde contre "
            "les états charmé et effrayé. De plus, par une action, vous pouvez dépenser une utilisation d'Inspiration "
            "bardique pour mettre fin à l'état charmé ou effrayé d'une créature alliée à 18 mètres ou moins qui peut "
            "vous entendre."
        ),
        "Commandement absolu": (
            "Par une action, dépensez deux utilisations d'Inspiration bardique et choisissez jusqu'à deux créatures "
            "alliées à 18 mètres ou moins qui peuvent vous entendre. Chacune peut utiliser sa réaction pour effectuer "
            "une attaque avec une arme, en ajoutant votre dé d'Inspiration bardique au jet d'attaque et au jet de "
            "dégâts. Si les deux attaques touchent la même créature, celle-ci a un désavantage à son prochain jet de "
            "sauvegarde effectué avant la fin de votre prochain tour."
        ),
    },
    "Collège de la Discorde": {
        "Dissonance cacophonique": (
            "Par une action bonus, dépensez une utilisation d'Inspiration bardique et choisissez une créature à "
            "18 mètres ou moins qui peut vous entendre. Elle fait un jet de sauvegarde de Constitution (DD = "
            f"{DD_SORTS}). En cas d'échec, elle subit des dégâts de tonnerre égaux au résultat du dé d'Inspiration + "
            "votre modificateur de Charisme et a un désavantage à son prochain jet d'attaque avant la fin de son "
            "prochain tour. En cas de réussite, elle subit la moitié des dégâts seulement."
        ),
        "Fréquence résonnante": (
            "Lorsque vous lancez un sort de barde qui inflige des dégâts de tonnerre ou psychiques, vous pouvez "
            "considérer tout 1 obtenu sur un dé de dégâts comme un 2. À partir du niveau 10, ces sorts ignorent la "
            "résistance aux dégâts de tonnerre (mais pas l'immunité)."
        ),
        "Onde de choc acoustique": (
            "Lorsqu'une créature que vous pouvez voir arrive à 1,50 mètre ou moins de vous, vous pouvez utiliser votre "
            "réaction pour émettre une onde sonore. Elle fait un jet de sauvegarde de Force (DD = "
            f"{DD_SORTS}) : en cas d'échec, elle subit 2d8 dégâts de tonnerre et est repoussée de 3 mètres ; en cas de "
            "réussite, elle subit la moitié des dégâts et n'est pas repoussée. Utilisable un nombre de fois égal à "
            "votre bonus de maîtrise, récupéré après un repos long."
        ),
        "Crescendo destructeur": (
            "Par une action, vous libérez une surcharge sonore dans un cône de 9 mètres. Chaque créature de votre choix "
            f"dans la zone fait un jet de sauvegarde de Constitution (DD = {DD_SORTS}). En cas d'échec, elle subit 6d8 "
            "dégâts de tonnerre, est assourdie pendant 1 minute et ne peut pas effectuer de réactions jusqu'au début de "
            "votre prochain tour ; en cas de réussite, elle subit la moitié des dégâts seulement. Utilisable une fois "
            "par repos long, ou en dépensant un emplacement de sort de niveau 5 ou supérieur."
        ),
    },
}

CORRIGE = [
    ("majeur", "Barde / Inspiration bardique (d6)", "Aucun nombre d'utilisations ni portée indiqués",
     "Utilisations = modificateur de Charisme (min. 1) par repos long ; cible à 18 m qui peut vous entendre"),
    ("mineur", "Barde / Secrets magiques", "Ne précise pas que les sorts mineurs sont éligibles ni le décompte",
     "Sorts mineurs compris ; comptent dans les sorts connus, niveau lançable requis"),
    ("info", "Barde / Secrets magiques supplémentaires, Secrets magiques ultimes",
     "Noms inventés pour les niveaux 14 et 18", "Le PHB répète simplement « Secrets magiques » aux niveaux 14 et 18"),
    ("mineur", "Barde / Capacités de classe optionnelles", "Option de Tasha absente : Sorts de barde supplémentaires (niv. 1)",
     "TCE ajoute des sorts à la liste de barde (ex. Couleurs dansantes, Mot de guérison de groupe…)"),
    ("mineur", "Barde / Capacités de classe optionnelles", "Option de Tasha absente : Inspiration magique (niv. 2)",
     "Le dé d'Inspiration peut s'ajouter aux soins ou aux dégâts d'un sort lancé par son détenteur"),
    ("mineur", "Barde / Capacités de classe optionnelles", "Option de Tasha absente : Polyvalence bardique (niv. 4)",
     "À chaque amélioration de caractéristique, échanger une compétence d'Expertise ou un sort mineur"),
    ("mineur", "Collège de la Vaillance / Maîtrises supérieures", "Nom différent de la traduction officielle",
     "Maîtrises supplémentaires"),
    ("majeur", "Collège de la Séduction / sorts_domaine", "Liste de 10 sorts de collège présente",
     "Le Collège de la Séduction (XGE) n'accorde aucun sort supplémentaire"),
    ("mineur", "Collège de la Séduction / sorts_domaine", "« Calme emotions » (anglais/coquille) et « Dissimulation » (sort inexistant)",
     "Calme émotions ; pas de sort « Dissimulation » en 5e"),
    ("majeur", "Collège de la Séduction / Apparence inspirante", "14 PV temporaires fixes à une seule cible",
     "5/8/11/14 PV temp. (niv. 3/5/10/15) à un nombre de créatures = modificateur de Charisme, à 18 m, action bonus"),
    ("majeur", "Collège de la Séduction / Représentation envoûtante", "1 créature, durée 1 min, 1 fois par repos long",
     "Prestation d'1 min, humanoïdes = modificateur de Charisme à 18 m, charme 1 h, 1/repos court ou long"),
    ("mineur", "Collège de la Séduction / Apparence majestueuse", "Durée et limite d'utilisation absentes",
     "1 minute (concentration), Injonction en action bonus chaque tour, 1/repos long"),
    ("majeur", "Collège de la Séduction / Majesté inébranlable", "Liée à Apparence majestueuse, sauvegarde non précisée",
     "Aptitude autonome : action bonus, 1 min, JS de Charisme contre le DD des sorts, 1/repos court ou long"),
    ("majeur", "Collège des Épées / sorts_domaine", "Liste de 10 sorts de collège présente",
     "Le Collège des Épées (XGE) n'accorde aucun sort supplémentaire"),
    ("mineur", "Collège des Épées / sorts_domaine", "« Skin of stone » (anglais) et « Entrave » (sort inexistant)",
     "Peau de pierre ; Immobilisation de personne"),
    ("mineur", "Collège des Épées / Maîtrises supérieures", "Nom non officiel et focaliseur d'arme omis",
     "Maîtrises supplémentaires ; une arme de corps à corps maîtrisée peut servir de focaliseur"),
    ("mineur", "Collège des Épées / Style de combat", "Style nommé « Duelliste »", "Style « Duel »"),
    ("mineur", "Collège des Épées / Moulinet", "Effets Tranchant et Mobile imprécis (1 cible / 1 case)",
     "Tranchant : autre créature à 1,50 m ; Mobile : 1,50 m + 30 cm par point du dé puis déplacement en réaction"),
    ("majeur", "Collège des Murmures / sorts_domaine", "Liste de 10 sorts de collège présente",
     "Le Collège des Murmures (XGE) n'accorde aucun sort supplémentaire"),
    ("mineur", "Collège des Murmures / sorts_domaine", "« Disguise self », « Invisible » (anglais/erroné), « Sonde mentale » (inexistant)",
     "Déguisement ; Invisibilité ; pas de sort « Sonde mentale » en 5e"),
    ("majeur", "Collège des Murmures / Lame psychique", "8d6 dégâts dès le niveau 3",
     "2d6 (niv. 3), 3d6 (niv. 5), 5d6 (niv. 10), 8d6 (niv. 15), une fois par round"),
    ("mineur", "Collège des Murmures / Mots de terreur", "Condition de conversation seul à seul d'1 minute omise",
     "Humanoïde seul avec vous pendant au moins 1 minute, JS de Sagesse"),
    ("mineur", "Collège des Murmures / Voile de murmure", "Capture de l'ombre (réaction, mort à 9 m) omise",
     "Réaction quand un humanoïde meurt à 9 m ; déguisement 1 h ; Tromperie + 5"),
    ("mineur", "Collège de l'Éloquence / Faconde", "« inférieur à 9 »", "Résultat de 9 ou moins compté comme 10"),
    ("majeur", "Collège de l'Éloquence / Paroles déstabilisantes", "Malus appliqué à un jet d'attaque",
     "Malus au prochain jet de sauvegarde de la cible avant le début de votre prochain tour"),
    ("majeur", "Collège de l'Éloquence / Discours universel", "Une seule créature, sans durée ni limite",
     "Créatures = modificateur de Charisme à 18 m, 1 heure, 1/repos long ou emplacement de sort"),
    ("majeur", "Collège de l'Éloquence / Inspiration contagieuse", "1 fois par repos long",
     "Utilisations = modificateur de Charisme (min. 1) par repos long, déclenchée par une réussite"),
    ("majeur", "Collège de la Création / Grain de potentiel", "PV temp. = dé + 1 ; dégâts de tonnerre sans sauvegarde ni zone",
     "PV temp. = dé + modificateur de Charisme ; tonnerre sur la cible et créatures à 1,50 m, JS de Constitution"),
    ("majeur", "Collège de la Création / Créativité concrète", "Valeur max 400 po, taille M, durée 6 h fixes",
     "Valeur 20 × niveau de barde po, taille M/G/TG selon le niveau, durée = bonus de maîtrise heures"),
    ("majeur", "Collège de la Création / Crescendo créatif", "Limité à 2 objets",
     "Objets = modificateur de Charisme (min. 2), sans limite de valeur en po"),
    ("mineur", "Collège des Commandants / sorts_domaine", "« Claire-voie » et « Ralliement de masse » : sorts inexistants",
     "Clairvoyance ? ; aucun sort « Ralliement de masse » en 5e"),
    ("mineur", "Collège de la Discorde / sorts_domaine", "« Cri de banshee » inexistant ; « Mot de pouvoir douleur » est un sort de niveau 7",
     "Remplacer par des sorts valides du niveau correspondant"),
]

AUDIT = [
    ("info", "Barde / Sorts de barde supplémentaires (option Tasha)",
     "« Antipathie/Sympathie » (niv. 8) cité dans le texte mais sort absent de la base de sorts",
     "TCE ajoute Antipathie/Sympathie à la liste de sorts de barde"),
]
