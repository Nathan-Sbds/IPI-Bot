Il est necessaire de mettre un Token à ce bot dans le data.json. A la premiere execution, le bot peut mettre une periode pouvant aller jusqu'a plusieurs dizaine de minutes avant d'afficher les commandes dans discord. Cela est normal lors de sa première execution, les éxecutions suivantes seront beaucoup plus rapide si aucun changement structurel n'est effectué.

Le bot possède 19 commandes :

	- /agenda (date)

	- /agenda_accorder_droit_membre [membre]

	- /agenda_accorder_droit_role [role]

	- /agenda_desenregitrer

	- /agenda_eleve [membre] (date)

	- /agenda_enregitrer [identifiant] [mdp]

	- /agenda_modifier [identifiant] [mdp]

	- /agenda_retirer_droit_membre [membre]
	
	- /agenda_retirer_droit_role [role]

	- /agenda_voir_partage_droit

	- /assigner_role [fichier] [supprimer] [role] (role2) (role3)

	- /creer_categorie [nom_categorie] [role] (role2)

	- /creer_channel [nom_channel] [nom_categorie]

	- /ping
	
	- /supprimer_categorie [nom_categorie]

	- /supprimer_channel [nom_channel] [nom_categorie]

	- /supprimer_role [role] (role2)

	- /transferer_categorie [ancien_nom_categorie] [nouveau_nom_categorie] [ancien_nom_channel] [nouveau_nom_channel] [ancien_role] [nouveau_role]

	- /transferer_role [ancien_role] [nouveau_role] [supprimer]




La commande /assigner_role affecte le role donné en argument à toutes les personnes presentes dans le fichier .csv et ayant le nom et prenom correspondant sur discord. Si l'argument supprimer est VRAI alors toutes les personnes possedant le role avant la commande se le voient retirer.

exemple : /assigner_role b1ifd.csv @B2-IFD vrai 

	- Cette commande donnera le role @B2-IFD a toutes les personnes présentes dans le fichier b1ifd.csv après avoir retiré le role a toutes personnes le possèdant.



La commande /transferer_role permet de transferer toutes les personnes ayant un role vers un autre role. Si l'argument supprimer est VRAI alors toutes les personnes possedant le role avant la commande se le voient retirer.

exemple : /transferer_role @B1-IFD @B2-IFD vrai 

	- Cette commande donnera le role @B2-IFD à toute les personnes qui possedaient le role @B1-IFD en leur retirant le role @B1-IFD en meme temps.


La commande /creer_categorie permet de créer une categorie contenant les channels pédago, géneral, only-you et le channel vocal avec toutes les permissions pour le role donner en argument, un second role peut aussi obtenir l'acces avec l'argument role2. Pour le nom de la categorie le bot ajoute automatiquement lees = ainsi que les espaces pour une meilleure facilité d'utilisation.

exemple : /creer_categorie b1-ifd @B1-IFD 

	- Cette commande va créer une catégorie nommée ========== B2 IFD ========== ayant les channels #général-b1-ifd , #pédago-b1-ifd , #only-you et général-vocal ayant les bonnes permissions et accès pour le role @B1-IFD.



La commande /supprimer_categorie permet de supprimer entierement une categorie ainsi que les channels la composant. La commande ne fonctionnera surement pas sur les categories créées à la main.

exemple : /supprimer_categorie b1-ifd 

	- Cette commande va supprimer la catégorie nommée ========== B2 IFD ========== ainsi que tous les channels qui l'a compose.



La commande /creer_channel permet de créer un channel ayant le nom donner en argument dans la categorie donner en argument avec les permissions de la categorie.

exemple: /creer_channel intro-reseau b1-ifd 

	- Cette commande va creer le channel #intro-reseau dans la categorie ========== B2 IFD ========== en lui mettant les permissions pour les @B1-IFD qui on accès a cette categorie.



La commande /suprimmer_channel supprime le channel ayant le nom donner en argument dans la categorie donner en argument.

exemple: /supprimer_channel intro-reseau b1-ifd 

	- Cette commande va supprimer le channel #intro-reseau situé dans la catégorie ========== B2 IFD ==========
