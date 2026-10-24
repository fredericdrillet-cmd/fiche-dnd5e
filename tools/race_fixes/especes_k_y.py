"""Corrections des espèces Kobold → Yuan-ti (issues de l'audit)."""

ALT = "+2, +1 (ou +1, +1, +1)"
LIBRE = ["Commun", "Au choix"]

FIXES = [
    # ------------------------------------------------------------------ Kobold (Monstres du Multivers)
    {"op": "set", "espece": "Kobold", "champ": "caracteristiques", "valeur": ALT},
    {"op": "set", "espece": "Kobold", "champ": "langues", "valeur": LIBRE},
    {"op": "trait", "espece": "Kobold", "nom": "Taille",
     "description": "Petite (environ 60 à 90 cm de haut). Votre type de créature est Humanoïde."},
    {"op": "trait", "espece": "Kobold", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre. Dans le noir, vous ne distinguez pas les couleurs, seulement des nuances de gris."},
    {"op": "trait", "espece": "Kobold", "nom": "Cri draconique",
     "description": "Par une action bonus, vous poussez un cri draconique visant les ennemis de votre choix situés "
                    "à 3 mètres ou moins de vous. Jusqu'au début de votre prochain tour, vous et vos alliés avez "
                    "l'avantage aux jets d'attaque contre ceux de ces ennemis qui ont pu vous entendre. Utilisable "
                    "un nombre de fois égal à votre bonus de maîtrise par repos long."},
    {"op": "rename_trait", "espece": "Kobold", "nom": "Héritage", "nouveau": "Héritage kobold"},
    {"op": "trait", "espece": "Kobold", "nom": "Héritage kobold",
     "description": "Choisissez une option. Ingéniosité : maîtrise d'une compétence parmi Arcanes, Escamotage, "
                    "Investigation, Médecine et Survie. Défiance : avantage aux jets de sauvegarde pour éviter ou "
                    "mettre fin à l'état effrayé. Sorcellerie draconique : vous connaissez un sort mineur de la liste "
                    "d'ensorceleur, lancé avec l'Intelligence, la Sagesse ou le Charisme (choisi avec cette option)."},

    # ------------------------------------------------------------------ Léonin (Mythic Odysseys of Theros)
    {"op": "vitesse", "espece": "Léonin", "valeur": 10.5},
    {"op": "trait", "espece": "Léonin", "nom": "Griffes",
     "description": "Vos griffes sont des armes naturelles avec lesquelles vous pouvez porter des attaques à mains "
                    "nues. En cas de coup au but, elles infligent 1d4 + votre modificateur de Force dégâts "
                    "tranchants, au lieu des dégâts contondants normaux d'une attaque à mains nues."},
    {"op": "trait", "espece": "Léonin", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Léonin", "nom": "Instincts de chasseur",
     "description": "Vous obtenez la maîtrise d'une compétence au choix parmi Athlétisme, Intimidation, Perception "
                    "et Survie."},
    {"op": "rename_trait", "espece": "Léonin", "nom": "Rugissement", "nouveau": "Rugissement intimidant"},
    {"op": "trait", "espece": "Léonin", "nom": "Rugissement intimidant",
     "description": "Par une action bonus, vous poussez un rugissement : chaque créature de votre choix située à "
                    "3 mètres ou moins et capable de vous entendre doit réussir un jet de sauvegarde de Sagesse "
                    "(DD 8 + votre bonus de maîtrise + votre modificateur de Constitution) ou être effrayée jusqu'à "
                    "la fin de votre prochain tour. Une fois utilisé, ce trait revient après un repos court ou long."},

    # ------------------------------------------------------------------ Locathah (Locathah Rising)
    {"op": "trait", "espece": "Locathah", "nom": "Nage",
     "description": "Vous avez une vitesse de nage de 9 mètres, en plus de votre vitesse de marche de 9 mètres."},
    {"op": "trait", "espece": "Locathah", "nom": "Armure naturelle",
     "description": "Votre peau écailleuse vous protège : sans armure, votre CA est égale à 12 + votre modificateur "
                    "de Dextérité. Vous pouvez utiliser cette valeur si l'armure portée vous donnerait une CA "
                    "inférieure ; un bouclier s'applique normalement."},
    {"op": "trait", "espece": "Locathah", "nom": "Observateur et athlétique",
     "description": "Vous obtenez la maîtrise des compétences Athlétisme et Perception."},
    {"op": "trait", "espece": "Locathah", "nom": "Volonté du Léviathan",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre les états charmé, effrayé, paralysé, "
                    "empoisonné et étourdi, ainsi que contre le fait d'être endormi."},
    {"op": "trait", "espece": "Locathah", "nom": "Amphibie limitée",
     "description": "Vous respirez aussi bien l'air que l'eau. Hors de l'eau, vous devez vous immerger au moins une "
                    "fois toutes les 4 heures, sinon vous commencez à suffoquer."},

    # ------------------------------------------------------------------ Loxodon (Guide des guildes de Ravnica)
    {"op": "trait", "espece": "Loxodon", "nom": "Puissante carrure",
     "description": "Vous comptez comme une créature d'une taille de plus pour déterminer votre capacité de charge "
                    "et le poids que vous pouvez pousser, tirer ou soulever."},
    {"op": "trait", "espece": "Loxodon", "nom": "Sérénité",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre les états charmé et effrayé."},
    {"op": "trait", "espece": "Loxodon", "nom": "Armure naturelle",
     "description": "Sans armure, votre CA est égale à 12 + votre modificateur de Constitution. Vous pouvez "
                    "utiliser cette valeur si l'armure portée vous donnerait une CA inférieure ; un bouclier "
                    "s'applique normalement."},
    {"op": "trait", "espece": "Loxodon", "nom": "Trompe",
     "description": "Votre trompe peut saisir, soulever, pousser ou tirer un poids allant jusqu'à 2,5 kg × votre "
                    "valeur de Force, avec une allonge de 1,50 mètre ; elle peut aussi servir de tuba sous l'eau. "
                    "Elle ne peut ni manier d'arme ou de bouclier, ni accomplir de tâche exigeant de la précision "
                    "(outils, objets magiques, composantes somatiques)."},
    {"op": "trait", "espece": "Loxodon", "nom": "Odorat développé",
     "description": "Vous avez l'avantage aux tests de Sagesse (Perception), de Sagesse (Survie) et d'Intelligence "
                    "(Investigation) qui reposent sur l'odorat."},

    # ------------------------------------------------------------------ Minotaure (Monstres du Multivers)
    {"op": "trait", "espece": "Minotaure", "nom": "Cornes",
     "description": "Vos cornes sont des armes naturelles avec lesquelles vous portez des attaques à mains nues. "
                    "En cas de coup au but, elles infligent 1d6 + votre modificateur de Force dégâts perforants."},
    {"op": "trait", "espece": "Minotaure", "nom": "Ruée cornue",
     "description": "Juste après avoir effectué l'action Foncer pendant votre tour et vous être déplacé d'au moins "
                    "6 mètres, vous pouvez porter une attaque de corps à corps avec vos cornes par une action bonus."},
    {"op": "trait", "espece": "Minotaure", "nom": "Cornes martelantes",
     "description": "Juste après avoir touché une créature avec une attaque de corps à corps faite dans le cadre de "
                    "l'action Attaquer, vous pouvez, par une action bonus, tenter de la repousser de 3 mètres. La "
                    "cible, d'une taille au plus supérieure à la vôtre, doit réussir un jet de sauvegarde de Force "
                    "(DD 8 + votre bonus de maîtrise + votre modificateur de Force) ou être repoussée."},
    {"op": "trait", "espece": "Minotaure", "nom": "Mémoire labyrinthique",
     "description": "Vous savez toujours où se trouve le nord, et vous avez l'avantage aux tests de Sagesse (Survie) "
                    "faits pour vous orienter ou pister."},

    # ------------------------------------------------------------------ Mort-vivant (homebrew, rééquilibré)
    {"op": "set", "espece": "Mort-vivant", "champ": "langues", "valeur": LIBRE},
    {"op": "trait", "espece": "Mort-vivant", "nom": "Nature de mort-vivant",
     "description": "Vous êtes immunisé contre les maladies, avez la résistance aux dégâts de poison et l'avantage "
                    "aux jets de sauvegarde contre l'état empoisonné. Vous n'avez besoin ni de respirer, ni de "
                    "manger, ni de boire, ni de dormir : un repos long consiste pour vous en 4 heures d'inactivité "
                    "pendant lesquelles vous restez conscient."},
    {"op": "trait", "espece": "Mort-vivant", "nom": "Vulnérabilité / Résistance",
     "description": "Votre corps décharné vous donne la résistance aux dégâts perforants, mais vous êtes vulnérable "
                    "aux dégâts contondants (ils sont doublés)."},
    {"op": "trait", "espece": "Mort-vivant", "nom": "Ossature résistante",
     "description": "Lorsque vous tombez à 0 point de vie sans être tué sur le coup, et que les dégâts subis ne sont "
                    "pas radiants, vos os se réassemblent : vous tombez à 1 point de vie à la place. Une fois "
                    "utilisé, ce trait revient après un repos long."},

    # ------------------------------------------------------------------ Myconide éveillé (homebrew, rééquilibré)
    {"op": "set", "espece": "Myconide éveillé", "champ": "langues", "valeur": LIBRE},
    {"op": "trait", "espece": "Myconide éveillé", "nom": "Nature végétale",
     "description": "Votre type de créature est Plante et non Humanoïde : les effets qui ne ciblent que les "
                    "humanoïdes ne vous affectent pas. Vous n'avez pas besoin de dormir, mais devez passer un repos "
                    "long de 8 heures immobile dans l'humidité ou la pénombre."},
    {"op": "trait", "espece": "Myconide éveillé", "nom": "Réseau mycélien",
     "description": "Vous pouvez communiquer par télépathie avec toute créature située à 9 mètres ou moins de vous "
                    "qui comprend au moins une langue. La créature ne peut vous répondre par télépathie que si elle "
                    "en est elle-même capable ; le lien cesse si elle s'éloigne au-delà de 9 mètres."},
    {"op": "trait", "espece": "Myconide éveillé", "nom": "Spores pacifiantes ou toxiques",
     "description": "Par une action bonus, vous libérez des spores sur une créature située à 3 mètres ou moins, qui "
                    "doit réussir un jet de sauvegarde de Constitution (DD 8 + votre bonus de maîtrise + votre "
                    "modificateur de Constitution). Spores toxiques : en cas d'échec, elle subit 1d6 dégâts de poison "
                    "(2d6 au niveau 6, 3d6 au niveau 11, 4d6 au niveau 16) et est empoisonnée jusqu'à la fin de votre "
                    "prochain tour. Spores pacifiantes : en cas d'échec, elle ne peut pas effectuer de réaction "
                    "jusqu'à la fin de votre prochain tour. Utilisable un nombre de fois égal à votre bonus de "
                    "maîtrise par repos long."},

    # ------------------------------------------------------------------ Naïade (homebrew, rééquilibré)
    {"op": "trait", "espece": "Naïade", "nom": "Amphibie",
     "description": "Vous respirez aussi bien l'air que l'eau et avez une vitesse de nage de 9 mètres, égale à "
                    "votre vitesse de marche."},
    {"op": "trait", "espece": "Naïade", "nom": "Camouflage fluviatile",
     "description": "Vous avez l'avantage aux tests de Dextérité (Discrétion) lorsque vous êtes dans l'eau ou à "
                    "1,50 mètre ou moins d'une rivière, d'un lac ou d'une source."},
    {"op": "trait", "espece": "Naïade", "nom": "Bénédiction des eaux",
     "description": "Sorts : vous connaissez le sort mineur *Façonnage de l'eau* ; *Nappe de brouillard* (niv. 3, "
                    "1/repos long). Vous pouvez aussi lancer ce dernier avec vos emplacements de sort ; la Sagesse "
                    "est votre caractéristique d'incantation pour ces sorts."},

    # ------------------------------------------------------------------ Nain des collines (Manuel des Joueurs)
    {"op": "trait", "espece": "Nain des collines", "nom": "Résilience naine",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre le poison et la résistance aux dégâts de "
                    "poison."},
    {"op": "trait", "espece": "Nain des collines", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Nain des collines", "nom": "Maîtrise d'armes",
     "description": "Vous maîtrisez la hache d'armes, la hachette, le marteau léger et le marteau de guerre."},
    {"op": "trait", "espece": "Nain des collines", "nom": "Outils",
     "description": "Vous maîtrisez un outil d'artisan au choix : outils de forgeron, matériel de brasseur ou outils "
                    "de maçon."},
    {"op": "trait", "espece": "Nain des collines", "nom": "Connaissance de la pierre",
     "description": "Lors d'un test d'Intelligence (Histoire) portant sur l'origine d'un ouvrage de pierre, vous êtes "
                    "considéré comme maîtrisant la compétence et ajoutez le double de votre bonus de maîtrise."},
    {"op": "trait", "espece": "Nain des collines", "nom": "Ténacité naine",
     "description": "Vos points de vie maximum augmentent de 1, puis de 1 à chaque niveau supplémentaire "
                    "(+1 PV par niveau)."},
    {"op": "trait", "espece": "Nain des collines", "nom": "Vitesse naine",
     "description": "Votre vitesse de marche est de 7,50 mètres ; elle n'est pas réduite par le port d'une armure "
                    "lourde."},

    # ------------------------------------------------------------------ Nain des montagnes (Manuel des Joueurs)
    {"op": "set", "espece": "Nain des montagnes", "champ": "caracteristiques", "valeur": "Con +2, For +2"},
    {"op": "trait", "espece": "Nain des montagnes", "nom": "Résilience naine",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre le poison et la résistance aux dégâts de "
                    "poison."},
    {"op": "trait", "espece": "Nain des montagnes", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Nain des montagnes", "nom": "Armures naines",
     "description": "Vous maîtrisez les armures légères et intermédiaires."},
    {"op": "trait", "espece": "Nain des montagnes", "nom": "Maîtrise d'armes",
     "description": "Vous maîtrisez la hache d'armes, la hachette, le marteau léger et le marteau de guerre."},
    {"op": "trait", "espece": "Nain des montagnes", "nom": "Outils",
     "description": "Vous maîtrisez un outil d'artisan au choix : outils de forgeron, matériel de brasseur ou outils "
                    "de maçon."},
    {"op": "trait", "espece": "Nain des montagnes", "nom": "Connaissance de la pierre",
     "description": "Lors d'un test d'Intelligence (Histoire) portant sur l'origine d'un ouvrage de pierre, vous êtes "
                    "considéré comme maîtrisant la compétence et ajoutez le double de votre bonus de maîtrise."},
    {"op": "trait", "espece": "Nain des montagnes", "nom": "Vitesse naine",
     "description": "Votre vitesse de marche est de 7,50 mètres ; elle n'est pas réduite par le port d'une armure "
                    "lourde."},

    # ------------------------------------------------------------------ Orc (Monstres du Multivers)
    {"op": "set", "espece": "Orc", "champ": "caracteristiques", "valeur": ALT},
    {"op": "set", "espece": "Orc", "champ": "langues", "valeur": LIBRE},
    {"op": "rename_trait", "espece": "Orc", "nom": "Agressif", "nouveau": "Poussée d'adrénaline"},
    {"op": "trait", "espece": "Orc", "nom": "Poussée d'adrénaline",
     "description": "Vous pouvez effectuer l'action Foncer par une action bonus ; vous gagnez alors un nombre de "
                    "points de vie temporaires égal à votre bonus de maîtrise. Utilisable un nombre de fois égal à "
                    "votre bonus de maîtrise par repos long (les utilisations reviennent aussi après un repos court)."},
    {"op": "trait", "espece": "Orc", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "remove_trait", "espece": "Orc", "nom": "Intuition primitive"},
    {"op": "trait", "espece": "Orc", "nom": "Puissante carrure",
     "description": "Vous comptez comme une créature d'une taille de plus pour déterminer votre capacité de charge "
                    "et le poids que vous pouvez pousser, tirer ou soulever."},
    {"op": "trait", "espece": "Orc", "nom": "Endurance implacable",
     "description": "Lorsque vous tombez à 0 point de vie sans être tué sur le coup, vous pouvez tomber à 1 point de "
                    "vie à la place. Une fois utilisé, ce trait revient après un repos long."},

    # ------------------------------------------------------------------ Orc cendré (homebrew, rééquilibré)
    {"op": "trait", "espece": "Orc cendré", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Orc cendré", "nom": "Sang incandescent",
     "description": "Vous avez la résistance aux dégâts de feu."},
    {"op": "trait", "espece": "Orc cendré", "nom": "Courroux des cendres",
     "description": "Lorsqu'une créature située à 1,50 mètre ou moins vous touche avec une attaque de corps à corps, "
                    "vous pouvez utiliser votre réaction pour lui infliger 1d6 + votre modificateur de Constitution "
                    "dégâts de feu. Une fois utilisé, ce trait revient après un repos court ou long."},

    # ------------------------------------------------------------------ Owlin (Strixhaven)
    {"op": "set", "espece": "Owlin", "champ": "caracteristiques", "valeur": ALT},
    {"op": "trait", "espece": "Owlin", "nom": "Taille",
     "description": "Moyenne ou Petite, au choix lors de la création. Votre type de créature est Humanoïde."},
    {"op": "trait", "espece": "Owlin", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 36 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Owlin", "nom": "Vol",
     "description": "Grâce à vos ailes, vous avez une vitesse de vol égale à votre vitesse de marche (9 mètres). "
                    "Vous ne pouvez pas voler si vous portez une armure intermédiaire ou lourde."},
    {"op": "trait", "espece": "Owlin", "nom": "Plume silencieuse",
     "description": "Vous obtenez la maîtrise de la compétence Discrétion."},

    # ------------------------------------------------------------------ Plasmoïde (Aventures dans l'espace)
    {"op": "trait", "espece": "Plasmoïde", "nom": "Taille et type",
     "description": "Moyenne ou Petite, au choix lors de la création. Votre type de créature est Vase."},
    {"op": "trait", "espece": "Plasmoïde", "nom": "Amorphe",
     "description": "Vous pouvez vous faufiler dans un espace de 2,5 cm de large, à condition de ne rien porter "
                    "(ni équipement ni vêtements). Vous avez l'avantage aux tests de caractéristique faits pour "
                    "commencer une empoignade ou vous en libérer."},
    {"op": "trait", "espece": "Plasmoïde", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Plasmoïde", "nom": "Apnée",
     "description": "Vous pouvez retenir votre souffle pendant 1 heure."},
    {"op": "trait", "espece": "Plasmoïde", "nom": "Résistance naturelle",
     "description": "Vous avez la résistance aux dégâts d'acide et de poison, et l'avantage aux jets de sauvegarde "
                    "contre l'état empoisonné."},
    {"op": "trait", "espece": "Plasmoïde", "nom": "Modelage du corps",
     "description": "Par une action, vous remodelez votre corps pour vous doter d'une tête, d'un ou deux bras et "
                    "d'une ou deux jambes (vous portez alors vêtements et armures de taille Moyenne), ou redevenez "
                    "une masse informe. Par une action bonus, vous étirez ou résorbez un pseudopode de 15 cm de "
                    "large et 3 mètres de long, capable de manipuler un objet, ouvrir ou fermer une porte ou un "
                    "contenant, ou ramasser un objet Très petit. Le pseudopode ne peut ni attaquer, ni activer "
                    "d'objet magique, ni soulever plus de 5 kg."},

    # ------------------------------------------------------------------ Revenant (Reborn, Guide de Ravenloft)
    {"op": "set", "espece": "Revenant", "champ": "caracteristiques", "valeur": ALT},
    {"op": "trait", "espece": "Revenant", "nom": "Taille",
     "description": "Moyenne ou Petite, au choix lors de la création. Votre type de créature est Humanoïde."},
    {"op": "remove_trait", "espece": "Revenant", "nom": "Échappé à la mort"},
    {"op": "remove_trait", "espece": "Revenant", "nom": "Endurance étrange"},
    {"op": "rename_trait", "espece": "Revenant", "nom": "Immortel", "nouveau": "Nature immortelle"},
    {"op": "trait", "espece": "Revenant", "nom": "Nature immortelle",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre la mort ainsi que contre les maladies et "
                    "l'état empoisonné, et la résistance aux dégâts de poison. Vous n'avez besoin ni de manger, ni "
                    "de boire, ni de respirer, ni de dormir, et la magie ne peut pas vous endormir. Vous terminez un "
                    "repos long en 4 heures d'inactivité, pendant lesquelles vous restez conscient."},
    {"op": "trait", "espece": "Revenant", "nom": "Connaissance d'une vie antérieure",
     "description": "Juste après avoir vu le résultat du d20 d'un test de caractéristique utilisant une compétence, "
                    "vous pouvez lancer 1d6 et ajouter le résultat au test. Utilisable un nombre de fois égal à "
                    "votre bonus de maîtrise par repos long."},

    # ------------------------------------------------------------------ Sang-Maudit (Hexblood, Guide de Ravenloft)
    {"op": "set", "espece": "Sang-Maudit", "champ": "source", "valeur": "Guide de Ravenloft"},
    {"op": "set", "espece": "Sang-Maudit", "champ": "caracteristiques", "valeur": ALT},
    {"op": "trait", "espece": "Sang-Maudit", "nom": "Taille",
     "description": "Moyenne ou Petite, au choix lors de la création."},
    {"op": "trait", "espece": "Sang-Maudit", "nom": "Nature féerique",
     "description": "Votre type de créature est Fée (et non Humanoïde)."},
    {"op": "trait", "espece": "Sang-Maudit", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Sang-Maudit", "nom": "Jeton étrange",
     "description": "Par une action bonus, vous vous arrachez sans dommage une mèche, un ongle ou une dent, qui reste "
                    "magique jusqu'à votre prochain repos long. Tant qu'il l'est, vous pouvez par une action, si le "
                    "jeton est à 16 km ou moins, envoyer un message télépathique de 25 mots au plus à la créature "
                    "qui le porte, ou voir et entendre autour du jeton pendant 1 minute (vous êtes alors aveugle et "
                    "sourd à votre propre environnement). Vous ne pouvez créer un nouveau jeton qu'après un repos "
                    "long."},
    {"op": "trait", "espece": "Sang-Maudit", "nom": "Magie maudite",
     "description": "Sorts : *Déguisement* (niv. 1, 1/repos long) et *Maléfice* (niv. 1, 1/repos long), sans "
                    "emplacement. Vous pouvez aussi les lancer avec vos emplacements de sort ; caractéristique "
                    "d'incantation : Intelligence, Sagesse ou Charisme (choisie avec cette lignée)."},

    # ------------------------------------------------------------------ Satyre (Monstres du Multivers)
    {"op": "vitesse", "espece": "Satyre", "valeur": 10.5},
    {"op": "trait", "espece": "Satyre", "nom": "Type",
     "description": "Votre type de créature est Fée (et non Humanoïde). Taille Moyenne."},
    {"op": "rename_trait", "espece": "Satyre", "nom": "Bêlier", "nouveau": "Bélier"},
    {"op": "trait", "espece": "Satyre", "nom": "Bélier",
     "description": "Vous pouvez donner des coups de tête avec vos cornes, une attaque à mains nues qui inflige en "
                    "cas de coup au but 1d6 + votre modificateur de Force dégâts contondants."},
    {"op": "trait", "espece": "Satyre", "nom": "Résistance à la magie",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre les sorts."},
    {"op": "rename_trait", "espece": "Satyre", "nom": "Saut joyeux", "nouveau": "Sauts joyeux"},
    {"op": "trait", "espece": "Satyre", "nom": "Sauts joyeux",
     "description": "Lorsque vous faites un saut en longueur ou en hauteur, même sans élan, vous pouvez lancer 1d8 "
                    "et ajouter 30 cm par point obtenu à la distance couverte. Cette distance supplémentaire coûte "
                    "du mouvement normalement."},
    {"op": "trait", "espece": "Satyre", "nom": "Fêtard",
     "description": "Vous obtenez la maîtrise des compétences Représentation et Persuasion, ainsi que d'un instrument "
                    "de musique au choix."},

    # ------------------------------------------------------------------ Shadar-kai (Monstres du Multivers)
    {"op": "set", "espece": "Shadar-kai", "champ": "caracteristiques", "valeur": ALT},
    {"op": "set", "espece": "Shadar-kai", "champ": "langues", "valeur": LIBRE},
    {"op": "rename_trait", "espece": "Shadar-kai", "nom": "Trance", "nouveau": "Transe"},
    {"op": "trait", "espece": "Shadar-kai", "nom": "Transe",
     "description": "Vous n'avez pas besoin de dormir et la magie ne peut pas vous endormir. Vous terminez un repos "
                    "long en 4 heures de méditation, pendant lesquelles vous restez conscient."},
    {"op": "rename_trait", "espece": "Shadar-kai", "nom": "Bénédiction des ténèbres",
     "nouveau": "Bénédiction de la Reine corbeau"},
    {"op": "trait", "espece": "Shadar-kai", "nom": "Bénédiction de la Reine corbeau",
     "description": "Par une action bonus, vous vous téléportez magiquement dans un espace inoccupé que vous voyez, "
                    "à 9 mètres ou moins. À partir du niveau 3, vous obtenez aussi la résistance à tous les dégâts "
                    "jusqu'au début de votre prochain tour après chaque téléportation. Utilisable un nombre de fois "
                    "égal à votre bonus de maîtrise par repos long."},
    {"op": "trait", "espece": "Shadar-kai", "nom": "Résistance nécrotique",
     "description": "Vous avez la résistance aux dégâts nécrotiques."},
    {"op": "trait", "espece": "Shadar-kai", "nom": "Ascendance féerique",
     "description": "Vous avez l'avantage aux jets de sauvegarde faits pour éviter ou mettre fin à l'état charmé."},
    {"op": "trait", "espece": "Shadar-kai", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Shadar-kai", "nom": "Sens aiguisés",
     "description": "Vous obtenez la maîtrise de la compétence Perception."},

    # ------------------------------------------------------------------ Tabaxi (Monstres du Multivers)
    {"op": "set", "espece": "Tabaxi", "champ": "caracteristiques", "valeur": ALT},
    {"op": "trait", "espece": "Tabaxi", "nom": "Taille",
     "description": "Moyenne ou Petite, au choix lors de la création. Votre type de créature est Humanoïde."},
    {"op": "trait", "espece": "Tabaxi", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Tabaxi", "nom": "Talent du chat",
     "description": "Vous obtenez la maîtrise des compétences Perception et Discrétion."},
    {"op": "trait", "espece": "Tabaxi", "nom": "Griffes",
     "description": "Vos griffes vous donnent une vitesse d'escalade égale à votre vitesse de marche (9 mètres). "
                    "Ce sont aussi des armes naturelles : vos attaques à mains nues avec elles infligent 1d6 + votre "
                    "modificateur de Force dégâts tranchants."},
    {"op": "trait", "espece": "Tabaxi", "nom": "Agilité féline",
     "description": "Lorsque vous vous déplacez pendant votre tour en combat, vous pouvez doubler votre vitesse "
                    "jusqu'à la fin du tour. Vous ne pouvez plus le faire tant que vous n'avez pas passé l'un de vos "
                    "tours sans vous déplacer (0 mètre)."},

    # ------------------------------------------------------------------ Thri-kreen (Aventures dans l'espace)
    {"op": "trait", "espece": "Thri-kreen", "nom": "Taille et type",
     "description": "Moyenne ou Petite, au choix lors de la création. Votre type de créature est Monstruosité."},
    {"op": "trait", "espece": "Thri-kreen", "nom": "Carapace caméléon",
     "description": "Sans armure, votre CA est égale à 13 + votre modificateur de Dextérité ; un bouclier "
                    "s'applique normalement. Par une action, vous changez la couleur de votre carapace pour "
                    "l'accorder à votre environnement, ce qui vous donne l'avantage aux tests de Dextérité "
                    "(Discrétion) faits pour vous cacher dans ce décor."},
    {"op": "trait", "espece": "Thri-kreen", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Thri-kreen", "nom": "Bras secondaires",
     "description": "Votre deuxième paire de bras, plus petite, peut manipuler un objet, ouvrir ou fermer une porte "
                    "ou un contenant, ramasser ou poser un objet Très petit, ou manier une arme dotée de la "
                    "propriété légère."},
    {"op": "trait", "espece": "Thri-kreen", "nom": "Sans sommeil",
     "description": "Vous n'avez pas besoin de dormir et restez conscient pendant un repos long, à condition de vous "
                    "abstenir de toute activité fatigante."},
    {"op": "trait", "espece": "Thri-kreen", "nom": "Télépathie",
     "description": "Sans magie, vous ne pouvez pas parler les langues non thri-kreen : vous transmettez vos pensées "
                    "par télépathie aux créatures consentantes situées à 36 mètres ou moins. La créature n'a pas "
                    "besoin de partager une langue avec vous mais doit en comprendre au moins une ; le lien se rompt "
                    "au-delà de 36 mètres, si l'un de vous est neutralisé, ou à votre gré."},

    # ------------------------------------------------------------------ Tieffelin (Manuel des Joueurs 2014)
    {"op": "trait", "espece": "Tieffelin", "nom": "Résistance au feu",
     "description": "Vous avez la résistance aux dégâts de feu."},
    {"op": "trait", "espece": "Tieffelin", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Tieffelin", "nom": "Héritage infernal",
     "description": "Sorts : *Thaumaturgie* (sort mineur) ; *Représailles infernales* (niv. 3, 1/repos long, lancé "
                    "comme un sort de niveau 2) ; *Ténèbres* (niv. 5, 1/repos long). Le Charisme est votre "
                    "caractéristique d'incantation pour ces sorts."},

    # ------------------------------------------------------------------ Tieffelin féral (Guide de la Côte des Épées)
    {"op": "remove_trait", "espece": "Tieffelin féral", "nom": "Ailé"},
    {"op": "remove_trait", "espece": "Tieffelin féral", "nom": "Langue du diable"},
    {"op": "trait", "espece": "Tieffelin féral", "nom": "Résistance au feu",
     "description": "Vous avez la résistance aux dégâts de feu."},
    {"op": "trait", "espece": "Tieffelin féral", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Tieffelin féral", "nom": "Héritage infernal (variante au choix)",
     "description": "Sorts au choix : une seule option parmi les quatre, Charisme. Héritage infernal : *Thaumaturgie* "
                    "(sort mineur), *Représailles infernales* (niv. 3, 1/repos long, lancé comme un sort de niveau 2), "
                    "*Ténèbres* (niv. 5, 1/repos long). Langue du diable : *Moquerie cruelle* (sort mineur), "
                    "*Charme-personne* (niv. 3, 1/repos long, lancé comme un sort de niveau 2), *Discours captivant* "
                    "(niv. 5, 1/repos long). Feu infernal : comme Héritage infernal, mais *Mains brûlantes* (niv. 3, "
                    "1/repos long, lancé comme un sort de niveau 2) remplace Représailles infernales. Ailé : aucun "
                    "sort, mais une vitesse de vol de 9 mètres tant que vous ne portez pas d'armure lourde."},

    # ------------------------------------------------------------------ Tortle (Monstres du Multivers)
    {"op": "trait", "espece": "Tortle", "nom": "Taille",
     "description": "Moyenne ou Petite, au choix lors de la création. Votre type de créature est Humanoïde."},
    {"op": "trait", "espece": "Tortle", "nom": "Griffes",
     "description": "Vos griffes sont des armes naturelles : vos attaques à mains nues avec elles infligent "
                    "1d6 + votre modificateur de Force dégâts tranchants."},
    {"op": "trait", "espece": "Tortle", "nom": "Apnée",
     "description": "Vous pouvez retenir votre souffle pendant 1 heure."},
    {"op": "trait", "espece": "Tortle", "nom": "Armure naturelle",
     "description": "Votre carapace vous donne une CA de base de 17, sur laquelle votre modificateur de Dextérité "
                    "n'a aucun effet. Vous ne pouvez porter aucune armure (légère, intermédiaire ou lourde), mais un "
                    "bouclier s'applique normalement."},
    {"op": "rename_trait", "espece": "Tortle", "nom": "Défense en carapace", "nouveau": "Défense de carapace"},
    {"op": "trait", "espece": "Tortle", "nom": "Défense de carapace",
     "description": "Par une action, vous vous retirez dans votre carapace, et en sortez par une action bonus. "
                    "Tant que vous y êtes : +4 à la CA, avantage aux jets de sauvegarde de Force et de Constitution, "
                    "désavantage aux jets de sauvegarde de Dextérité, vous êtes à terre, votre vitesse est de 0 et "
                    "ne peut pas augmenter, vous ne pouvez pas prendre de réaction et votre seule action possible "
                    "est l'action bonus pour sortir."},
    {"op": "trait", "espece": "Tortle", "nom": "Intuition naturelle",
     "description": "Vous obtenez la maîtrise d'une compétence au choix parmi Dressage, Médecine, Nature, "
                    "Perception, Discrétion et Survie."},

    # ------------------------------------------------------------------ Triton (Monstres du Multivers)
    {"op": "rename_trait", "espece": "Triton", "nom": "Respiration", "nouveau": "Amphibie"},
    {"op": "trait", "espece": "Triton", "nom": "Amphibie",
     "description": "Vous respirez aussi bien l'air que l'eau, et vous avez une vitesse de nage égale à votre vitesse "
                    "de marche (9 mètres)."},
    {"op": "trait", "espece": "Triton", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "rename_trait", "espece": "Triton", "nom": "Résistance", "nouveau": "Gardien des profondeurs"},
    {"op": "trait", "espece": "Triton", "nom": "Gardien des profondeurs",
     "description": "Adapté aux abysses glacés, vous avez la résistance aux dégâts de froid."},
    {"op": "trait", "espece": "Triton", "nom": "Émissaire de la mer",
     "description": "Vous pouvez communiquer des idées simples à toute bête, tout élémentaire et toute monstruosité "
                    "dotée d'une vitesse de nage. Elle comprend vos paroles, mais vous ne la comprenez pas en retour."},
    {"op": "rename_trait", "espece": "Triton", "nom": "Magie des mers", "nouveau": "Contrôle de l'air et de l'eau"},
    {"op": "trait", "espece": "Triton", "nom": "Contrôle de l'air et de l'eau",
     "description": "Sorts : *Nappe de brouillard* (niv. 1, 1/repos long) ; *Bourrasque* (niv. 3, 1/repos long) ; "
                    "*Marche sur l'eau* (niv. 5, 1/repos long). Vous pouvez aussi les lancer avec vos emplacements de "
                    "sort ; caractéristique d'incantation : Intelligence, Sagesse ou Charisme (choisie avec cette "
                    "espèce)."},

    # ------------------------------------------------------------------ Vedalken (Guide des guildes de Ravnica)
    {"op": "trait", "espece": "Vedalken", "nom": "Précision inlassable",
     "description": "Vous maîtrisez une compétence au choix parmi Arcanes, Escamotage, Histoire, Investigation, "
                    "Médecine et Représentation, ainsi qu'un outil au choix. Lors d'un test utilisant cette "
                    "compétence ou cet outil, lancez 1d4 et ajoutez le résultat."},
    {"op": "trait", "espece": "Vedalken", "nom": "Amphibie",
     "description": "Vous absorbez l'oxygène par la peau et pouvez respirer sous l'eau pendant 1 heure au plus. "
                    "Une fois cette durée atteinte, vous devez terminer un repos long pour en bénéficier à nouveau."},

    # ------------------------------------------------------------------ Verdan (Acquisitions Incorporées)
    {"op": "trait", "espece": "Verdan", "nom": "Taille",
     "description": "Petite au niveau 1 ; vous devenez de taille Moyenne en atteignant le niveau 5."},
    {"op": "trait", "espece": "Verdan", "nom": "Guérison",
     "description": "Sang noir guérisseur : lorsque vous obtenez 1 ou 2 sur un dé de vie dépensé à la fin d'un repos "
                    "court, vous pouvez le relancer et devez garder le nouveau résultat."},
    {"op": "trait", "espece": "Verdan", "nom": "Télépathie",
     "description": "Télépathie limitée : vous pouvez parler par télépathie à toute créature que vous voyez à "
                    "9 mètres ou moins. Elle n'a pas besoin de partager une langue avec vous, mais ne peut répondre "
                    "par télépathie que si elle en est capable ; vous ne transmettez que des concepts simples."},
    {"op": "trait", "espece": "Verdan", "nom": "Persuasif",
     "description": "Vous obtenez la maîtrise de la compétence Persuasion."},
    {"op": "trait", "espece": "Verdan", "nom": "Intuition télépathique",
     "description": "Vous avez l'avantage à tous les jets de sauvegarde de Sagesse et de Charisme."},

    # ------------------------------------------------------------------ Yuan-ti (Monstres du Multivers)
    {"op": "trait", "espece": "Yuan-ti", "nom": "Taille",
     "description": "Moyenne ou Petite, au choix lors de la création. Votre type de créature est Humanoïde."},
    {"op": "trait", "espece": "Yuan-ti", "nom": "Vision dans le noir",
     "description": "Vous voyez dans la pénombre jusqu'à 18 mètres comme en lumière vive, et dans le noir comme "
                    "en pénombre (nuances de gris uniquement)."},
    {"op": "trait", "espece": "Yuan-ti", "nom": "Résistance magique",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre les sorts."},
    {"op": "trait", "espece": "Yuan-ti", "nom": "Résilience au poison",
     "description": "Vous avez l'avantage aux jets de sauvegarde contre l'état empoisonné et la résistance aux "
                    "dégâts de poison."},
    {"op": "rename_trait", "espece": "Yuan-ti", "nom": "Incantation", "nouveau": "Incantation serpentine"},
    {"op": "trait", "espece": "Yuan-ti", "nom": "Incantation serpentine",
     "description": "Sorts : *Bouffée de poison* (sort mineur) ; *Amitié avec les animaux* à volonté, en ne ciblant "
                    "que des serpents ; *Suggestion* (niv. 3, 1/repos long). Vous pouvez aussi lancer Suggestion avec "
                    "vos emplacements de sort ; caractéristique d'incantation : Intelligence, Sagesse ou Charisme "
                    "(choisie avec cette espèce)."},
]

CORRIGE = [
    ("majeur", "Kobold / Cri draconique", "6 fois/repos long, portée absente",
     "Action bonus, ennemis à 3 m, avantage jusqu'au début du prochain tour, bonus de maîtrise fois/repos long"),
    ("mineur", "Kobold / Héritage kobold", "Option Défiance absente ; trait nommé « Héritage »",
     "Renommé ; trois options MotM (Ingéniosité, Défiance, Sorcellerie draconique)"),
    ("mineur", "Kobold / caractéristiques", "+2, +1 sans alternative", "+2, +1 (ou +1, +1, +1)"),
    ("mineur", "Kobold / langues", "Commun, Draconique (Volo)", "Commun + Au choix (MotM)"),
    ("majeur", "Léonin / vitesse", "9 m par défaut", "10,5 m"),
    ("majeur", "Léonin / Rugissement intimidant", "DD 14 fixe, 1 fois/repos long",
     "Renommé ; DD 8 + maîtrise + Con, effrayé jusqu'à la fin du prochain tour, repos court ou long"),
    ("mineur", "Léonin / Griffes", "1d4 tranchants sans modificateur", "1d4 + modificateur de Force"),
    ("majeur", "Locathah / Observateur et athlétique", "Trait absent", "Ajouté : Athlétisme et Perception"),
    ("mineur", "Locathah / Armure naturelle", "Bouclier non mentionné", "12 + Dex, bouclier autorisé"),
    ("majeur", "Loxodon / Trompe", "Soulève 50 kg (fixe)",
     "2,5 kg × Force, allonge 1,50 m, tuba, aucune arme ni tâche de précision"),
    ("mineur", "Loxodon / Odorat développé", "Perception/Investigation seulement", "Ajout de Survie"),
    ("majeur", "Minotaure / Cornes martelantes", "DD 14 fixe",
     "Action bonus après attaque de l'action Attaquer, JS For DD 8 + maîtrise + For, taille max +1"),
    ("mineur", "Minotaure / Cornes", "1d6 perforants sans modificateur", "1d6 + modificateur de Force"),
    ("mineur", "Minotaure / Mémoire labyrinthique", "Connaissance du nord absente", "Ajoutée"),
    ("mineur", "Mort-vivant / langues", "Chaîne unique « Commun et une autre langue… »", "[Commun, Au choix]"),
    ("mineur", "Mort-vivant / Ossature résistante", "« Sous certaines conditions » : non chiffré",
     "Homebrew rééquilibré : 1 PV au lieu de 0 sauf dégâts radiants, 1/repos long"),
    ("mineur", "Mort-vivant / Nature de mort-vivant", "Immunité au poison (trop forte), repos non défini",
     "Homebrew rééquilibré : résistance au poison + avantage contre empoisonné, repos long de 4 h conscient"),
    ("mineur", "Myconide éveillé / Spores", "Ni DD, ni dégâts, ni portée",
     "Homebrew rééquilibré : 3 m, JS Con DD 8 + maîtrise + Con, 1d6 poison progressif, bonus de maîtrise/repos long"),
    ("mineur", "Myconide éveillé / Réseau mycélien", "« Courte portée » non chiffrée", "9 m"),
    ("info", "Myconide éveillé / langues", "Langue « Spore » inexistante", "[Commun, Au choix]"),
    ("mineur", "Naïade / Bénédiction des eaux", "« Imbibition / Façonnage de l'eau » : Imbibition n'existe pas",
     "Façonnage de l'eau ; Nappe de brouillard au niv. 3, 1/repos long ou emplacements"),
    ("mineur", "Naïade / vitesse de nage", "Nage 12 m (supérieure à la marche)",
     "Homebrew rééquilibré : nage = marche (9 m)"),
    ("mineur", "Nain des collines / armure lourde", "Vitesse non réduite par l'armure lourde non mentionnée",
     "Trait « Vitesse naine » ajouté"),
    ("mineur", "Nain des collines / traits", "Descriptions incomplètes (armes, outils, pierre, résilience)",
     "Listes et règles complètes du MdJ"),
    ("majeur", "Nain des montagnes / caractéristiques", "Con +2, For +1",
     "MdJ : Con +2 (nain) et For +2 (nain des montagnes)"),
    ("mineur", "Nain des montagnes / traits du nain", "Entraînement aux armes naines et Connaissance de la pierre absents",
     "Ajoutés"),
    ("mineur", "Nain des montagnes / armure lourde", "Vitesse non réduite par l'armure lourde non mentionnée",
     "Trait « Vitesse naine » ajouté"),
    ("mineur", "Orc / caractéristiques", "For +2, Con +1 (Volo/Eberron)", "+2, +1 (ou +1, +1, +1)"),
    ("majeur", "Orc / Poussée d'adrénaline", "« Agressif » : action bonus Foncer",
     "Renommé ; + PV temporaires = bonus de maîtrise, bonus de maîtrise fois, repos court ou long"),
    ("majeur", "Orc / Endurance implacable", "Trait absent", "Ajouté : 1 PV au lieu de 0, 1/repos long"),
    ("mineur", "Orc / Intuition primitive", "Deux compétences (Volo)", "Supprimé (absent de MotM)"),
    ("mineur", "Orc / langues", "Commun, Orc", "Commun + Au choix (MotM)"),
    ("mineur", "Orc cendré / Courroux des cendres", "Dégâts non chiffrés",
     "Homebrew rééquilibré : réaction sur attaque au corps à corps à 1,50 m, 1d6 + Con feu, repos court ou long"),
    ("mineur", "Owlin / caractéristiques", "+2, +1 sans alternative", "+2, +1 (ou +1, +1, +1)"),
    ("mineur", "Owlin / vol", "Vitesse de vol non chiffrée", "Vol = marche (9 m), précisé dans le trait"),
    ("mineur", "Plasmoïde / Apnée", "Trait absent", "Ajouté : 1 heure"),
    ("mineur", "Plasmoïde / Modelage du corps", "Pseudopode sans portée ; « Remodele »",
     "Action pour remodeler, action bonus pour un pseudopode de 3 m (≤ 5 kg)"),
    ("mineur", "Plasmoïde / taille et type", "Taille et type absents", "Moyenne ou Petite, type Vase"),
    ("mineur", "Revenant / Nature immortelle", "Avantage contre les maladies absent ; sommeil magique non mentionné ; "
     "trait éclaté en trois", "Trait unique VRGR (mort, maladies, empoisonné, poison, repos de 4 h)"),
    ("mineur", "Revenant / taille", "Taille absente", "Moyenne ou Petite"),
    ("mineur", "Revenant / caractéristiques", "+2, +1 sans alternative", "+2, +1 (ou +1, +1, +1)"),
    ("mineur", "Revenant / Connaissance d'une vie antérieure", "« Jet de capacité » imprécis",
     "Test utilisant une compétence, après le d20, bonus de maîtrise fois/repos long"),
    ("mineur", "Sang-Maudit / source", "« Dhampir/Hulder variant »", "Guide de Ravenloft"),
    ("mineur", "Sang-Maudit / Magie maudite", "Caractéristique et emplacements absents",
     "Int, Sag ou Cha au choix ; aussi via emplacements"),
    ("mineur", "Sang-Maudit / caractéristiques", "+2, +1 sans alternative", "+2, +1 (ou +1, +1, +1)"),
    ("mineur", "Sang-Maudit / Jeton étrange", "Action d'utilisation et cécité non précisées", "Précisés"),
    ("majeur", "Satyre / vitesse", "9 m par défaut", "10,5 m"),
    ("majeur", "Satyre / Sauts joyeux", "Sauts augmentés de 1d6/2 mètres", "+1d8 × 30 cm ; renommé"),
    ("mineur", "Satyre / Fêtard", "Instrument de musique absent", "Ajouté"),
    ("mineur", "Satyre / Bélier", "1d6 sans modificateur ; « Bêlier »", "Renommé ; 1d6 + modificateur de Force"),
    ("mineur", "Satyre / type", "Type absent", "Fée"),
    ("majeur", "Shadar-kai / Bénédiction de la Reine corbeau", "Résistance nécrotique, 6 fois/repos long",
     "Renommé ; bonus de maîtrise fois/repos long, résistance à tous les dégâts au niveau 3"),
    ("majeur", "Shadar-kai / Résistance nécrotique", "Pas de trait permanent séparé", "Ajouté"),
    ("mineur", "Shadar-kai / Ascendance féerique", "Trait absent", "Ajouté"),
    ("mineur", "Shadar-kai / caractéristiques", "+2, +1 sans alternative", "+2, +1 (ou +1, +1, +1)"),
    ("mineur", "Shadar-kai / langues", "Commun, Elfique (version Mordenkainen)", "Commun + Au choix (MotM)"),
    ("mineur", "Shadar-kai / Transe", "« Trance », sommeil magique non mentionné", "Renommé et complété"),
    ("majeur", "Tabaxi / vitesse d'escalade", "Escalade absente", "Escalade = marche (dans Griffes)"),
    ("mineur", "Tabaxi / caractéristiques", "+2, +1 sans alternative", "+2, +1 (ou +1, +1, +1)"),
    ("mineur", "Tabaxi / taille", "Taille absente", "Moyenne ou Petite"),
    ("mineur", "Thri-kreen / Carapace caméléon", "Changement de couleur (action) non précisé", "Précisé"),
    ("mineur", "Thri-kreen / taille et type", "Taille et type absents", "Moyenne ou Petite, type Monstruosité"),
    ("mineur", "Tieffelin / Héritage infernal", "Utilisations et niveau de lancement absents",
     "Représailles infernales niv. 3 (sort de niveau 2) 1/repos long, Ténèbres niv. 5 1/repos long, Cha"),
    ("majeur", "Tieffelin féral / variantes cumulées", "Ailé ET Langue du diable ensemble",
     "Un seul trait « variante au choix » : Héritage infernal, Langue du diable, Feu infernal ou Ailé"),
    ("majeur", "Tieffelin féral / traits de base", "Résistance au feu et vision dans le noir absentes", "Ajoutées"),
    ("majeur", "Tieffelin féral / Langue du diable", "« Envoûtement » introuvable ; niveaux absents",
     "Moquerie cruelle, Charme-personne niv. 3, Discours captivant niv. 5"),
    ("majeur", "Tortle / Défense de carapace", "Action bonus pour se retirer",
     "Action pour se retirer, action bonus pour sortir, avantage JS For/Con, à terre ; renommé"),
    ("mineur", "Tortle / Intuition naturelle", "Trait absent", "Ajouté"),
    ("mineur", "Tortle / Armure naturelle", "Bouclier non mentionné", "Bouclier autorisé, aucune armure"),
    ("mineur", "Tortle / Griffes", "1d6 sans modificateur", "1d6 + modificateur de Force"),
    ("majeur", "Triton / Contrôle de l'air et de l'eau", "Sorts sans niveau d'obtention",
     "Nappe de brouillard niv. 1, Bourrasque niv. 3, Marche sur l'eau niv. 5, 1/repos long ou emplacements"),
    ("mineur", "Triton / sort", "« *Brouillard* »", "*Nappe de brouillard*"),
    ("mineur", "Triton / Émissaire de la mer", "Trait absent", "Ajouté"),
    ("mineur", "Triton / Amphibie", "Vitesse de nage non chiffrée", "Nage = marche (9 m)"),
    ("mineur", "Vedalken / Précision inlassable", "Liste de compétences absente", "Liste GGR ajoutée"),
    ("mineur", "Verdan / taille", "Taille absente", "Petite, puis Moyenne au niveau 5"),
    ("mineur", "Yuan-ti / Incantation serpentine", "« Communication avec les serpents »",
     "Amitié avec les animaux à volonté sur les serpents ; Suggestion niv. 3 ; renommé"),
]

AUDIT = [
    ("info", "Kobold / vitesse", "Entrée 9 m redondante dans Bonus_Raciaux.json (idem Minotaure, Tortle)",
     "Valeur juste : laissée telle quelle"),
    ("info", "Locathah / langues", "« Aquan » absent de Langues.json",
     "Officiel (Locathah Rising) : conservé, noté en langue libre par le logiciel"),
    ("info", "Léonin, Loxodon, Vedalken / langues", "Langues propres absentes de Langues.json",
     "Officielles : conservées, notées en texte libre"),
    ("info", "Vitesses secondaires (nage, vol, escalade)", "Non modélisées par Bonus_Raciaux.json (marche seule)",
     "Indiquées en mètres dans les traits Owlin, Tabaxi, Triton, Locathah, Naïade, Tieffelin féral"),
    ("info", "Triton, Yuan-ti / caractéristique d'incantation",
     "core/rules.py RACE_SPELL_ABILITY impose Charisme (Volo)",
     "MotM : Int, Sag ou Cha au choix ; correction hors périmètre (fichier de code)"),
    ("info", "Naïade / caractéristique d'incantation", "Le logiciel prend la meilleure de Int/Sag/Cha",
     "Homebrew : Sagesse indiquée dans le texte ; pas d'entrée dans RACE_SPELL_ABILITY (hors périmètre)"),
    ("info", "Yuan-ti / Amitié avec les animaux", "Le logiciel classe un sort de niveau 1 en « 1 fois / repos long »",
     "MotM : à volonté sur les serpents ; texte exact, limitation du moteur"),
    ("info", "Tieffelin féral / variantes", "Toutes les options listées dans un seul trait (au choix)",
     "Le moteur affiche les sorts « au choix » : le joueur n'en retient qu'une option"),
    ("info", "Revenant / nom", "Revenant", "Nom officiel : Reborn ; espèce non renommée (contrainte)"),
    ("info", "Revenant / Héritage ancestral", "Option VRGR non modélisée",
     "Option facultative (garder des traits de l'ancienne espèce) laissée au MJ"),
    ("info", "Tieffelin / version", "Version MdJ 2014 (Cha +2, Int +1)", "Conforme à la source indiquée"),
    ("info", "Yuan-ti / version", "Résistance au poison = MotM (Volo : immunité)", "MotM 2022"),
    ("info", "Mort-vivant, Orc cendré, Myconide éveillé, Naïade / source", "Non officiel",
     "Homebrew : chiffres rééquilibrés, non audités comme officiels"),
]
