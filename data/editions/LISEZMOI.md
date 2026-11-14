# Données D&D 5e en français (fichiers finaux)

Extraites de 18 manuels (PHB 2014 et 2024, DMG 2014, Xanathar, Tasha, Mordenkainen, Fizban, Theros, Strixhaven, Ravenloft, Wildemount, Sword Coast, Eberron, Acquisitions Inc., Dragonlance, Bigby, Tomb of Annihilation, Princes of the Apocalypse). Tout est en français ; l'original anglais de chaque nom est dans `nom_en`. Les éditions 2014 et 2024 sont séparées par le champ `edition`.

| Fichier | Contenu |
|---|---|
| `sorts_fr.json` | 952 sorts |
| `objets_magiques_fr.json` | 754 objets magiques (dont 163 fiches de variantes : potions, parchemins par niveau, armes/armures +1/+2/+3, pierres de Ioun, figurines, instruments…) |
| `equipement_fr.json` | 677 entrées d'équipement non magique : armes, armures, outils, équipement d'aventurier, kits, montures, véhicules, marchandises, services, modes de vie, propriétés d'armes (dont maîtrises 2024), règles |
| `dons_fr.json` | 296 dons |
| `historiques_fr.json` | 76 historiques |
| `races_fr.json` | 152 races / espèces / sous-races |
| `classes_fr.json` | `classes` (26), `sous_classes` (177), `supplements_de_classe` (13, options de Tasha et Xanathar) |
| `sorts_par_classe_fr.json` | pour chaque classe (id) : les sorts qu'elle peut lancer, par niveau ; section `sous_classes` pour le Chevalier occulte et l'Escroc arcanique |
| `tables_fr.json` | 75 tables : trésor et objets par rareté (DMG 2014, Xanathar), Heroic Chronicle (Wildemount) |

## Champs communs
- `id` : identifiant stable et unique, de la forme `type-nom_anglais-édition-livre` (ex. `sort-fireball-2014-phb14`, `classe-wizard-2024-phb24`, `objet-bag-of-holding-2014-dmg14`, `arme-longsword-2014-phb14`). À utiliser pour relier les données.
- `nom` (français), `nom_en`, `nom_officiel_fr` (true = nom confirmé dans une source française, surtout aidedd.org ; false = traduction maison), `nom_valide_utilisateur`.
- `source` : `{livre, titre, titre_en, page_pdf}` (page du fichier PDF, décalée de 1 à 2 pages par rapport à la page imprimée). Titres français pour les livres traduits (Manuel des Joueurs, Guide du Maître, Le Guide complet de Xanathar, etc.).
- `edition` : 2014 ou 2024. `langue` : "fr" ; `langue_originale`.
- `alerte_traduction` : texte source abîmé, passage reconstitué (à relire). Il en reste une seule dans les fichiers.

## Liens
- Sorts : `classe_ids` (classes qui peuvent les lancer), `sous_classe_ids` (sous-classes qui les ont d'office ou y ont droit), `doublon_de` (même sort réimprimé dans un autre livre de la même édition), `restriction_acces` (ex. dunamancie réservée à certaines sous-classes).
- Classes : `sorts_par_niveau`, `nombre_de_sorts`. Sous-classes : `sorts_de_sous_classe_ids`, et `liste_de_sorts` pour le Chevalier occulte et l'Escroc arcanique (restrictions d'école en 2014, aucune en 2024).
- Objets : les variantes portent `variante: true` et `variante_de` (id de la fiche groupée) ; `doublon_de` quand la même variante existe dans deux livres (DMG et Xanathar).
- Tables : chaque ligne d'objet porte `objet_id` (id de `objets_magiques_fr.json`, fiche de la variante quand elle existe) et `objet_id_groupe` (fiche groupée).

## Conventions
- Unités métriques (mètres, kilos, litres). Prix en pièces (pc, pa, pe, po, pp) ; poids en kg. Warlock = « Occultiste » (2014 et 2024), Sorcerer = « Ensorceleur ».
- Sorts : écoles en français (abjuration, invocation, divination, enchantement, évocation, illusion, nécromancie, transmutation).
- Objets : `rarete` ∈ commun, peu commun, rare, très rare, légendaire, artefact, variable (détail dans `rarete_detail`), non précisée.
- Même chose en 2014 et en 2024 = même nom français (le nom 2014 est retenu).
- Les noms de champs qui ne s'affichent pas (`casting_time`, `range`, `components`, `duration`, `ritual`) restent en anglais ; toutes les valeurs affichées sont en français.
- Les versions de travail (anglais, fichiers par livre, sauvegardes) sont dans le dossier `version de travail`.
