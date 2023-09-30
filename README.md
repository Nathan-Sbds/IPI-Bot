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




#agenda

Cette commande permet d'afficher l'agenda de la semaine pour une date spécifiée.

Exemple d'utilisation : 

`/agenda (date)`

Fonctionnalités :
Affiche l'agenda pour la semaine.
Prend en charge une date facultative au format "jour/mois/année" (par exemple : 05/04/2024) pour afficher l'agenda à une date spécifique.

Paramètres :
date (facultatif) : La date à laquelle afficher l'agenda (au format "jour/mois/année"). Si aucun argument de date n'est fourni, l'agenda de la semaine en cours sera affiché.

Exemple d'utilisation en détail :

`/agenda 05/04/2024`

Cette commande affichera l'agenda de la semaine du 05/04/2024 pour l'utilisateur. L'image de l'agenda sera envoyée en message privé à l'utilisateur.
Si aucun argument de date n'est fourni, la commande affichera l'agenda de la semaine en cours.

 


#agenda_accorder_droit_membre

Cette commande permet de donner le droit d'accéder à votre emploi du temps à un membre spécifié, de préférence de votre promo.

Exemple d'utilisation : 

`/agenda_accorder_droit_membre [membre]`

Fonctionnalités :
Donne le droit d'accéder à votre emploi du temps à un membre spécifié.
Vérifie si le membre a déjà des identifiants enregistrés et, le cas échéant, ne les modifie pas.
Ajoute le membre à la liste des personnes autorisées à accéder à votre emploi du temps.

Paramètres :
membre : Le membre auquel donner le droit d'accéder à votre emploi du temps.

Exemple d'utilisation en détail :

`/agenda_accorder_droit_membre @utilisateur`

Cette commande accorde à l'utilisateur mentionné le droit d'accéder à votre emploi du temps. Si l'utilisateur a déjà des identifiants enregistrés, la commande ne les modifie pas. Sinon, elle ajoute le membre à la liste des personnes autorisées.


 

#agenda_accorder_droit_role

Cette commande permet de donner le droit d'accéder à votre emploi du temps à toutes les personnes ayant le rôle spécifié.

Exemple d'utilisation : 

`/agenda_accorder_droit_role [role]`

Fonctionnalités :
Donne le droit d'accéder à votre emploi du temps à toutes les personnes ayant le rôle spécifié.
Vérifie si les membres du rôle ont déjà des identifiants enregistrés et, le cas échéant, ne les modifie pas.
Ajoute les membres du rôle à la liste des personnes autorisées à accéder à votre emploi du temps.

Paramètres :
role : Le rôle auquel donner le droit d'accéder à votre emploi du temps.

Exemple d'utilisation en détail :

`/agenda_accorder_droit_role @B2-IFD`

Cette commande accorde à tous les membres du rôle spécifié le droit d'accéder à votre emploi du temps. Si les membres du rôle ont déjà des identifiants enregistrés, la commande ne les modifie pas. Sinon, elle ajoute les membres du rôle à la liste des personnes autorisées.

 


#agenda_desenregistrer

Cette commande permet aux utilisateurs de supprimer toutes les entrées associées à leur identifiant MonCampus.

Exemple d'utilisation : 

`/agenda_desenregitrer`

Fonctionnalités :
Permet aux utilisateurs de supprimer toutes les entrées associées à leur identifiant MonCampus enregistrées pour l'accès à l'emploi du temps.
Supprime toutes les entrées avec l'identifiant MonCampus actuel de l'utilisateur.

Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

Exemple d'utilisation en détail :

`/agenda_desenregistrer`

Cette commande supprime toutes les entrées associées à l'identifiant MonCampus actuel de l'utilisateur. Toutes les entrées liées à cet identifiant seront supprimées.




#agenda_eleve

Cette commande permet d'afficher l'emploi du temps d'un membre du serveur Discord. L'emploi du temps affiché est celui de la personne ciblée, à condition qu'elle se soit authentifiée en enregistrant ses identifiants MonCampus ou qu’elle ait reçue les identifiants d’un autre.

Exemple d'utilisation : 

`/agenda_eleve [membre] (date)`

Fonctionnalités :
Affiche l'emploi du temps d'un membre du serveur Discord, à condition que cette personne se soit authentifiée en enregistrant ses identifiants MonCampus.
Prend en charge la spécification d'une date facultative au format jj/mm/aaaa.

Paramètres :
membre : Mentionnez le membre du serveur Discord dont vous souhaitez afficher l'emploi du temps.
date (facultatif) : Facultatif, spécifiez la date pour laquelle vous souhaitez afficher l'emploi du temps. Utilisez le format jj/mm/aaaa.

Exemple d'utilisation en détail :

`/agenda_eleve @Membre 05/04/2024`

Cette commande affiche l'emploi du temps du membre mentionné pour la date spécifiée (facultatif). L'emploi du temps est généré en se connectant à MonCampus avec les identifiants enregistrés par le membre.

 


#agenda_enregistrer

Cette commande permet aux utilisateurs de s'enregistrer pour avoir accès à leur emploi du temps sur Discord.

Exemple d'utilisation : 

`/agenda_enregitrer [identifiant] [mdp]`

Fonctionnalités :
Enregistre les identifiants de connexion à MonCampus pour accéder à l'emploi du temps.
Empêche l'enregistrement de plusieurs ensembles d'identifiants par utilisateur.

Paramètres :
identifiant : Identifiant de connexion MonCampus.
mdp : Mot de passe de connexion MonCampus.

Exemple d'utilisation en détail :

`/agenda_enregistrer login motdepasse`

Cette commande enregistre vos identifiants de connexion MonCampus pour accéder à votre emploi du temps via Discord. Elle vérifie également si vous avez déjà enregistré des identifiants pour cette fonctionnalité et empêche l'enregistrement de plusieurs ensembles d'identifiants par utilisateur.

 


#agenda_modifier

Cette commande permet de mettre à jour les identifiants MonCampus enregistrés pour l'accès à l'emploi du temps.

Exemple d'utilisation : 

`/agenda_modifier [identifiant] [mdp]`

Fonctionnalités :
Permet aux utilisateurs de mettre à jour les identifiants MonCampus enregistrés pour l'accès à l'emploi du temps.
Met à jour les identifiants pour toutes les entrées correspondant à l'identifiant actuel de l'utilisateur.
Affiche les noms des membres dont les identifiants ont été mis à jour.

Paramètres :
identifiant : Le nouvel identifiant de connexion MonCampus.
mdp : Le nouveau mot de passe de connexion MonCampus.

Exemple d'utilisation en détail :

`/agenda_modifier login motdepasse`

Cette commande met à jour les identifiants MonCampus pour toutes les entrées correspondant à l'identifiant actuel de l'utilisateur avec les nouveaux identifiant et mot de passe fournis. Les noms des membres dont les identifiants ont été mis à jour sont affichés en réponse.

 


#agenda_retirer_droit_membre

Cette commande permet de retirer le droit d'accès à votre emploi du temps à une personne ciblée.

Exemple d'utilisation : 

`/agenda_retirer_droit_membre [membre]`

Fonctionnalités :
Retire le droit d'accéder à votre emploi du temps à la personne ciblée.
Vérifie si la personne ciblée a des identifiants enregistrés et, le cas échéant, les supprime de la liste des personnes autorisées.

Paramètres :
membre : Le membre auquel retirer le droit d'accéder à votre emploi du temps.

Exemple d'utilisation en détail :

`/agenda_retirer_droit_membre @Utilisateur`

Cette commande retire le droit d'accès à votre emploi du temps à la personne ciblée. Si la personne ciblée a des identifiants enregistrés et que ces identifiants correspondent à ceux de l'utilisateur qui exécute la commande, ils sont supprimés de la liste des personnes autorisées.

 


#agenda_retirer_droit_role

Cette commande permet de retirer le droit d'accès à votre emploi du temps à toutes les personnes ayant le rôle spécifié.

Exemple d'utilisation : 

`/agenda_retirer_droit_role [role]`

Fonctionnalités :
Retire le droit d'accéder à votre emploi du temps à toutes les personnes ayant le rôle spécifié.
Vérifie si les membres du rôle ont des identifiants enregistrés et, le cas échéant, les supprime de la liste des personnes autorisées.

Paramètres :
role : Le rôle auquel retirer le droit d'accéder à votre emploi du temps.

Exemple d'utilisation en détail :

`/agenda_retirer_droit_role @B2-IFD`

Cette commande retire à tous les membres du rôle spécifié le droit d'accéder à votre emploi du temps. Si les membres du rôle ont des identifiants enregistrés et que ces identifiants correspondent à ceux de l'utilisateur qui exécute la commande, ils sont supprimés de la liste des personnes autorisées.


 

#agenda_voir_partage_droit

Cette commande permet de voir les membres avec qui vous partagez votre agenda.

Exemple d'utilisation : 

`/agenda_voir_partage_droit`

Fonctionnalités :
Affiche les membres avec qui vous partagez votre agenda.
Vérifie si vous possédez des identifiants enregistrés pour cette fonctionnalité.

Paramètres :
Cette commande n'accepte aucun paramètre.

Exemple d'utilisation en détail :

`/agenda_voir_partage_droit`

Cette commande affiche les membres avec qui vous partagez votre agenda. Si vous ne partagez pas actuellement votre agenda avec d'autres membres, elle vous informera également de cette situation.




#assigner_role

Cette commande permet de donner un rôle spécifié à toutes les personnes dont les noms et prénoms se trouvent dans un fichier CSV joint. Elle peut également supprimer le rôle actuel des personnes si l'option correspondante est activée.

Exemple d'utilisation : 

`/assigner_role [fichier] [supprimer] [role] (role2) (role3)`

Fonctionnalités :
Donne un rôle spécifié à toutes les personnes dont les noms et prénoms sont dans le fichier CSV.
Option pour supprimer le rôle actuel des personnes.

Paramètres :
fichier : Fichier CSV contenant les noms et prénoms des personnes.
supprimer : Booléen indiquant s'il faut supprimer le rôle actuel des personnes.
role : Le rôle à donner aux personnes.
role2 : Un second rôle optionnel à donner aux personnes.
role3 : Un troisième rôle optionnel à donner aux personnes.

Exemple d'utilisation en détail :

`/assigner_role b2-ifd.csv True @B2-IFD @Apprenant IPI`

Cette commande va parcourir le fichier CSV spécifié, rechercher les noms et prénoms des personnes dans le serveur Discord, puis leur donner le rôle @B2-IFD. Si l'option True est activée, elle supprimera d'abord tous les autres rôles de ces personnes, puis ajoutera le rôle @B2-IFD et @Apprenant IPI.

 


#creer_categorie

Cette commande permet de créer une catégorie basique avec des canaux de discussion textuels et vocaux, ainsi que de définir des autorisations pour certains rôles dans cette catégorie.

Exemple d'utilisation : 

`/creer_categorie [nom_categorie] [role] (role2)`

Fonctionnalités :
Crée une catégorie avec des canaux de discussion textuels et vocaux.
Définit des autorisations pour les rôles spécifiés dans la catégorie.

Paramètres :
nom_categorie : Le nom de la catégorie à créer (sans les signes "=").
role : Le rôle ayant accès à cette catégorie.
role2 : Un second rôle optionnel ayant accès à la catégorie.

Exemple d'utilisation en détail :

`/creer_categorie B2 IFD @B2-IFD`

Cette commande va créer une catégorie nommée "========== B2 IFD ==========" avec plusieurs canaux, y compris un canal général, un canal vocal, etc. Elle définira des autorisations pour le rôle @B2-IFD, leur permettant de lire, envoyer des messages, se connecter et parler dans les canaux de la catégorie.
Elle affichera ensuite un message indiquant que la catégorie a été créée pour les rôles spécifiés.

 


#creer_channel

Cette commande permet de créer un canal de discussion textuel dans une catégorie spécifiée et de définir des autorisations pour certains rôles dans ce canal.

Exemple d'utilisation : 

`/creer_channel [nom_channel] [nom_categorie]`

Fonctionnalités :
Crée un canal de discussion textuel dans une catégorie spécifiée.
Définit des autorisations pour le rôle "Team Pedago IPI" dans le canal.

Paramètres :
nom_channel : Le nom du canal à créer.
nom_categorie : Le nom de la catégorie où créer le canal.

Exemple d'utilisation en détail :

`/creer_channel informations utiles B2 IFD`

Cette commande va créer un canal de discussion textuel nommé "informations-utiles" dans la catégorie "========== B2 IFD ==========" et ayant les autorisations pour le(s) rôle(s) de base de la catégorie. 
Elle affichera ensuite un message indiquant que le canal a été créé dans la catégorie spécifiée.

 


#supprimer_categorie

Cette commande permet de supprimer une catégorie spécifique ainsi que tous les canaux qu'elle contient.

Exemple d'utilisation : 

`/supprimer_categorie [nom_categorie]`

Fonctionnalités :
Supprime la catégorie spécifiée.
Supprime tous les canaux de discussion textuels et vocaux dans cette catégorie.

Paramètres :
nom_categorie : Le nom de la catégorie à supprimer (sans les signes "=").

Exemple d'utilisation en détail :

`/supprimer_categorie B2 IFD`

Cette commande va supprimer la catégorie "========== B2 IFD ==========" ainsi que tous les canaux qu'elle contient.
Elle affichera ensuite un message indiquant que la catégorie a été supprimée.


 

#supprimer_channel

Cette commande permet de supprimer un canal de discussion textuel dans une catégorie spécifiée.

Exemple d'utilisation : 

`/supprimer_channel [nom_channel] [nom_categorie]`

Fonctionnalités :
Supprime un canal de discussion textuel dans une catégorie spécifiée.

Paramètres :
nom_channel : Le nom du canal à supprimer.
nom_categorie : Le nom de la catégorie où se trouve le canal.

Exemple d'utilisation en détail :

`/supprimer_channel informations_utiles B2 IFD`

Cette commande va supprimer le canal de discussion textuel "informations_utile" dans la catégorie "========== B2 IFD ==========".
Elle affichera ensuite un message indiquant que le canal a été supprimé de la catégorie spécifiée.

 


#supprimer_role

Cette commande permet de supprimer un rôle spécifié à toutes les personnes ayant ce rôle. Vous avez également la possibilité de retirer le rôle uniquement aux personnes ayant un autre rôle spécifié.

Exemple d'utilisation : 

`/supprimer_role [role] (role2)`

Fonctionnalités :
Supprime un rôle à toutes les personnes ayant ce rôle.
Option pour retirer le rôle seulement aux personnes ayant un autre rôle spécifié.

Paramètres :
role : Le rôle à retirer aux personnes.
role2 : Le rôle optionnel à spécifier pour retirer le rôle uniquement aux personnes ayant ce rôle.

Exemple d'utilisation en détail :

`/supprimer_role @Admis @Apprenant IPI`

Cette commande va retirer le rôle @Admis à toutes les personnes ayant ce rôle, mais seulement si elles ont également le rôle @Apprenant IPI. Si @Apprenant IPI n'est pas spécifié dans la commande, le rôle @Admis sera retiré à toutes les personnes ayant ce rôle.
Elle affichera ensuite un message indiquant les personnes auxquelles le rôle a été supprimé.

 


#transferer_categorie

Cette commande permet de transférer une catégorie existante à un autre rôle, tout en remplaçant une chaîne de caractères dans le nom des canaux de la catégorie.

Exemple d'utilisation : 

`/transferer_categorie [ancien_nom_categorie] [nouveau_nom_categorie] [ancien_nom_channel] [nouveau_nom_channel] [ancien_role] [nouveau_role]`

Fonctionnalités :
Change le nom de la catégorie.
Transfère les autorisations de l'ancien rôle au nouveau rôle.
Remplace une chaîne de caractères dans le nom des canaux de la catégorie.

Paramètres :
ancien_nom_categorie : Le nom actuel de la catégorie à transférer.
nouveau_nom_categorie : Le nouveau nom à donner à la catégorie.
ancien_nom_channel : La chaîne de caractères à remplacer dans le nom des canaux.
nouveau_nom_channel : La chaîne de caractères de remplacement dans le nom des canaux.
ancien_role : Le rôle ayant actuellement accès à la catégorie.
nouveau_role : Le nouveau rôle pouvant avoir accès à la catégorie.

Exemple d'utilisation en détail :

`/transferer_categorie B1 IFD B2 IFD b1 b2 @B1-IFD @B2-IFD`

Cette commande va changer le nom de la catégorie "========== B1 IFD ==========" en "========== B2 IFD ==========", transférer les autorisations du rôle "B1-IFD" au rôle "B2-IFD", et remplacer "b1" par "b2" dans le nom des canaux de cette catégorie.
Elle affichera ensuite un message indiquant que la catégorie a été transférée avec succès.

 


#transferer_role

Cette commande permet de transférer un rôle spécifié à toutes les personnes ayant un autre rôle. Vous avez également la possibilité de supprimer le rôle actuel des personnes ayant le rôle d'origine.

Exemple d'utilisation : 
`/transferer_role [ancien_role] [nouveau_role] [supprimer]`


Fonctionnalités :
Transfère un rôle à toutes les personnes ayant un autre rôle.
Option pour supprimer le rôle actuel des personnes.

Paramètres :
ancien_role : Le rôle d'origine des personnes qui recevront le nouveau rôle.
nouveau_role : Le rôle à donner aux personnes.
supprimer : Booléen indiquant s'il faut supprimer le rôle actuel des personnes ayant le rôle d'origine.

Exemple d'utilisation en détail :

`/transferer_role @B1-IFD @B2-IFD True`

Cette commande va donner le rôle @B2-IFD à toutes les personnes ayant le rôle @B1-IFD. Si l'option True est activée, elle supprimera également le rôle @B1-IFD de ces personnes.
Elle affichera ensuite un message indiquant les personnes auxquelles le rôle a été donné ou supprimé.
