Il est necessaire de mettre un Token à ce bot dans le data.json. A la premiere execution, le bot peut mettre une periode pouvant aller jusqu'a plusieurs dizaine de minutes avant d'afficher les commandes dans discord. Cela est normal lors de sa première execution, les éxecutions suivantes seront beaucoup plus rapide si aucun changement structurel n'est effectué.

Le bot possède 30 commandes :

	- /assigner_role [fichier] [supprimer] [role] (role2) (role3)

	- /atelier_activer

	- /atelier_ajouter [titre] [description]

	- /atelier_ajouter_role [role1] (role2) (role3) (role4) (role5) (role6) (role7) (role8) (role9) (role10)

	- /atelier_config

	- /atelier_desactiver

	- /atelier_inscriptions

	- /atelier_label_bouton [button_label]

	- /atelier_liste_role

	- /atelier_max_inscription [max_inscription]

	- /atelier_max_inscrits [max_inscrits]

	- /atelier_max_inscrits_promo [max_inscrits]

	- /atelier_non_inscriptions

	- /atelier_relance

	- /atelier_retirer_role [role1] (role2) (role3) (role4) (role5) (role6) (role7) (role8) (role9) (role10)

	- /atelier_supprimer

	- /creer_categorie [nom_categorie] [role] (role2)

	- /creer_channel [nom_channel] [nom_categorie]

	- /ping
	
	- /supprimer_categorie [nom_categorie]

	- /supprimer_channel [nom_channel] [nom_categorie]

	- /supprimer_role [role] (role2)

	- /transferer_categorie [ancien_nom_categorie] [nouveau_nom_categorie] [ancien_nom_channel] [nouveau_nom_channel] [ancien_role] [nouveau_role]

	- /transferer_role [ancien_role] [nouveau_role] [supprimer]

	- /vote_ajouter_image [image]

	- /vote_resultats

	- /vote_supprimer




# /assigner_role

Cette commande permet de donner un rôle spécifié à toutes les personnes dont les noms et prénoms se trouvent dans un fichier CSV joint. Elle peut également supprimer le rôle actuel des personnes si l'option correspondante est activée.

#### Exemple d'utilisation : 

`/assigner_role [fichier] [supprimer] [role] (role2) (role3)`

#### Fonctionnalités :
Donne un rôle spécifié à toutes les personnes dont les noms et prénoms sont dans le fichier CSV.
Option pour supprimer le rôle actuel des personnes.

#### Paramètres :
fichier : Fichier CSV contenant les noms et prénoms des personnes.
supprimer : Booléen indiquant s'il faut supprimer le rôle actuel des personnes.
role : Le rôle à donner aux personnes.
role2 : Un second rôle optionnel à donner aux personnes.
role3 : Un troisième rôle optionnel à donner aux personnes.

#### Exemple d'utilisation en détail :

`/assigner_role b2-ifd.csv True @B2-IFD @Apprenant IPI`

Cette commande va parcourir le fichier CSV spécifié, rechercher les noms et prénoms des personnes dans le serveur Discord, puis leur donner le rôle @B2-IFD. Si l'option True est activée, elle supprimera d'abord tous les autres rôles de ces personnes, puis ajoutera le rôle @B2-IFD et @Apprenant IPI.

 


# /atelier_activer

Cette commande permet d'activer les inscriptions pour les ateliers.

#### Exemple d'utilisation : 

`/atelier_activer`

#### Fonctionnalités :
Active les inscriptions pour les ateliers.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/atelier_activer`

Cette commande va activer les inscriptions pour les ateliers.

# /atelier_ajouter

Cette commande permet d'ajouter une proposition d'atelier.

#### Exemple d'utilisation : 

`/atelier_ajouter [titre] [description]`

#### Fonctionnalités :
Ajoute une proposition d'atelier avec un titre et une description.
Crée un message avec un bouton pour s'inscrire à l'atelier.

#### Paramètres :
titre : Le titre de la proposition.
description : La description de la proposition.

#### Exemple d'utilisation en détail :

`/atelier_ajouter "Atelier Python" "Apprendre les bases de Python"`

Cette commande va ajouter une proposition d'atelier intitulée "Atelier Python" avec la description "Apprendre les bases de Python". Un message avec un bouton pour s'inscrire à l'atelier sera créé dans le canal actuel.

# /atelier_ajouter_role

Cette commande permet d'ajouter des rôles à la liste des rôles pouvant utiliser le module atelier.

#### Exemple d'utilisation : 

`/atelier_ajouter_role [role1] (role2) (role3) (role4) (role5) (role6) (role7) (role8) (role9) (role10)`

#### Fonctionnalités :
Ajoute des rôles à la liste des rôles pouvant utiliser le module atelier.
Attribue le rôle "Non Inscrit" aux membres des rôles ajoutés.

#### Paramètres :
role1 : Le premier rôle à ajouter.
role2 : Le deuxième rôle à ajouter (optionnel).
role3 : Le troisième rôle à ajouter (optionnel).
role4 : Le quatrième rôle à ajouter (optionnel).
role5 : Le cinquième rôle à ajouter (optionnel).
role6 : Le sixième rôle à ajouter (optionnel).
role7 : Le septième rôle à ajouter (optionnel).
role8 : Le huitième rôle à ajouter (optionnel).
role9 : Le neuvième rôle à ajouter (optionnel).
role10 : Le dixième rôle à ajouter (optionnel).

#### Exemple d'utilisation en détail :

`/atelier_ajouter_role @B2-IFD @Apprenant IPI`

Cette commande va ajouter les rôles @B2-IFD et @Apprenant IPI à la liste des rôles pouvant utiliser le module atelier. Les membres de ces rôles recevront également le rôle "Non Inscrit".

# /atelier_config

Cette commande permet d'afficher les informations de configuration du module atelier.

#### Exemple d'utilisation : 

`/atelier_config`

#### Fonctionnalités :
Affiche les informations de configuration du module atelier.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/atelier_config`

Cette commande va afficher les informations de configuration du module atelier, y compris le statut des inscriptions, le libellé du bouton, le nombre maximum d'inscrits par atelier et par promotion, le nombre d'inscriptions possible par utilisateur, les rôles autorisés à participer et la liste des ateliers.

# /atelier_desactiver

Cette commande permet de désactiver les inscriptions pour les ateliers.

#### Exemple d'utilisation : 

`/atelier_desactiver`

#### Fonctionnalités :
Désactive les inscriptions pour les ateliers.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/atelier_desactiver`

Cette commande va désactiver les inscriptions pour les ateliers.

# /atelier_inscriptions

Cette commande permet d'afficher les inscrits des ateliers.

#### Exemple d'utilisation : 

`/atelier_inscriptions`

#### Fonctionnalités :
Affiche les inscrits des ateliers.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/atelier_inscriptions`

Cette commande va afficher les inscrits des ateliers et envoyer les informations en message privé à l'utilisateur.

# /atelier_label_bouton

Cette commande permet de modifier le texte du bouton d'inscription aux ateliers.

#### Exemple d'utilisation : 

`/atelier_label_bouton [button_label]`

#### Fonctionnalités :
Modifie le texte du bouton d'inscription aux ateliers.

#### Paramètres :
button_label : Le nouveau texte du bouton (ne doit pas dépasser 80 caractères).

#### Exemple d'utilisation en détail :

`/atelier_label_bouton "Rejoindre l'atelier"`

Cette commande va modifier le texte du bouton d'inscription aux ateliers en "Rejoindre l'atelier".

# /atelier_liste_role

Cette commande permet de lister les rôles autorisés à utiliser le module atelier.

#### Exemple d'utilisation : 

`/atelier_liste_role`

#### Fonctionnalités :
Affiche la liste des rôles autorisés à utiliser le module atelier.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/atelier_liste_role`

Cette commande va afficher la liste des rôles autorisés à utiliser le module atelier.

# /atelier_max_inscription

Cette commande permet de modifier le nombre maximum d'ateliers auxquels il est possible de participer.

#### Exemple d'utilisation : 

`/atelier_max_inscription [max_inscription]`

#### Fonctionnalités :
Modifie le nombre maximum d'ateliers auxquels il est possible de participer.

#### Paramètres :
max_inscription : Le nombre maximum d'ateliers auxquels il est possible de participer.

#### Exemple d'utilisation en détail :

`/atelier_max_inscription 3`

Cette commande va modifier le nombre maximum d'ateliers auxquels il est possible de participer à 3.

# /atelier_max_inscrits

Cette commande permet de modifier le nombre maximum d'inscrits pour les ateliers.

#### Exemple d'utilisation : 

`/atelier_max_inscrits [max_inscrits]`

#### Fonctionnalités :
Modifie le nombre maximum d'inscrits pour les ateliers.

#### Paramètres :
max_inscrits : Le nombre maximum d'inscrits pour les ateliers.

#### Exemple d'utilisation en détail :

`/atelier_max_inscrits 20`

Cette commande va modifier le nombre maximum d'inscrits pour les ateliers à 20.

# /atelier_max_inscrits_promo

Cette commande permet de modifier le nombre maximum d'inscrits par promotion.

#### Exemple d'utilisation : 

`/atelier_max_inscrits_promo [max_inscrits]`

#### Fonctionnalités :
Modifie le nombre maximum d'inscrits par promotion pour les ateliers.

#### Paramètres :
max_inscrits : Le nombre maximum d'inscrits par promotion.

#### Exemple d'utilisation en détail :

`/atelier_max_inscrits_promo 5`

Cette commande va modifier le nombre maximum d'inscrits par promotion pour les ateliers à 5.

# /atelier_non_inscriptions

Cette commande permet d'afficher les personnes ne s'étant pas inscrites aux ateliers.

#### Exemple d'utilisation : 

`/atelier_non_inscriptions`

#### Fonctionnalités :
Affiche les personnes ne s'étant pas inscrites aux ateliers.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/atelier_non_inscriptions`

Cette commande va afficher les personnes ne s'étant pas inscrites aux ateliers et envoyer les informations en message privé à l'utilisateur.

# /atelier_relance

Cette commande permet de relancer les personnes n'étant pas inscrites aux ateliers.

#### Exemple d'utilisation : 

`/atelier_relance`

#### Fonctionnalités :
Relance les personnes n'étant pas inscrites aux ateliers.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/atelier_relance`

Cette commande va relancer les personnes n'étant pas inscrites aux ateliers en envoyant un message dans le canal actuel.

# /atelier_retirer_role

Cette commande permet de supprimer des rôles de la liste des rôles pouvant utiliser le module atelier.

#### Exemple d'utilisation : 

`/atelier_retirer_role [role1] (role2) (role3) (role4) (role5) (role6) (role7) (role8) (role9) (role10)`

#### Fonctionnalités :
Supprime des rôles de la liste des rôles pouvant utiliser le module atelier.
Retire le rôle "Non Inscrit" aux membres des rôles supprimés.

#### Paramètres :
role1 : Le premier rôle à supprimer.
role2 : Le deuxième rôle à supprimer (optionnel).
role3 : Le troisième rôle à supprimer (optionnel).
role4 : Le quatrième rôle à supprimer (optionnel).
role5 : Le cinquième rôle à supprimer (optionnel).
role6 : Le sixième rôle à supprimer (optionnel).
role7 : Le septième rôle à supprimer (optionnel).
role8 : Le huitième rôle à supprimer (optionnel).
role9 : Le neuvième rôle à supprimer (optionnel).
role10 : Le dixième rôle à supprimer (optionnel).

#### Exemple d'utilisation en détail :

`/atelier_retirer_role @B2-IFD @Apprenant IPI`

Cette commande va supprimer les rôles @B2-IFD et @Apprenant IPI de la liste des rôles pouvant utiliser le module atelier. Les membres de ces rôles perdront également le rôle "Non Inscrit".

# /atelier_supprimer

Cette commande permet de supprimer toutes les données et inscriptions du module atelier.

#### Exemple d'utilisation : 

`/atelier_supprimer`

#### Fonctionnalités :
Supprime toutes les données et inscriptions du module atelier.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/atelier_supprimer`

Cette commande va supprimer toutes les données et inscriptions du module atelier.

# /creer_categorie

Cette commande permet de créer une catégorie basique avec des canaux de discussion textuels et vocaux, ainsi que de définir des autorisations pour certains rôles dans cette catégorie.

#### Exemple d'utilisation : 

`/creer_categorie [nom_categorie] [role] (role2)`

#### Fonctionnalités :
Crée une catégorie avec des canaux de discussion textuels et vocaux.
Définit des autorisations pour les rôles spécifiés dans la catégorie.

#### Paramètres :
nom_categorie : Le nom de la catégorie à créer (sans les signes "=").
role : Le rôle ayant accès à cette catégorie.
role2 : Un second rôle optionnel ayant accès à la catégorie.

#### Exemple d'utilisation en détail :

`/creer_categorie B2 IFD @B2-IFD`

Cette commande va créer une catégorie nommée "========== B2 IFD ==========" avec plusieurs canaux, y compris un canal général, un canal vocal, etc. Elle définira des autorisations pour le rôle @B2-IFD, leur permettant de lire, envoyer des messages, se connecter et parler dans les canaux de la catégorie.
Elle affichera ensuite un message indiquant que la catégorie a été créée pour les rôles spécifiés.

 


# /creer_channel

Cette commande permet de créer un canal de discussion textuel dans une catégorie spécifiée et de définir des autorisations pour certains rôles dans ce canal.

#### Exemple d'utilisation : 

`/creer_channel [nom_channel] [nom_categorie]`

#### Fonctionnalités :
Crée un canal de discussion textuel dans une catégorie spécifiée.
Définit des autorisations pour le rôle "Team Pedago IPI" dans le canal.

#### Paramètres :
nom_channel : Le nom du canal à créer.
nom_categorie : Le nom de la catégorie où créer le canal.

#### Exemple d'utilisation en détail :

`/creer_channel informations utiles B2 IFD`

Cette commande va créer un canal de discussion textuel nommé "informations-utiles" dans la catégorie "========== B2 IFD ==========" et ayant les autorisations pour le(s) rôle(s) de base de la catégorie. 
Elle affichera ensuite un message indiquant que le canal a été créé dans la catégorie spécifiée.

 


# /ping

Cette commande permet de vérifier si le bot est en ligne et de mesurer le temps de latence entre l'envoi d'un message et sa réception.

#### Exemple d'utilisation : 

`/ping`

#### Fonctionnalités :
Vérifie si le bot est en ligne.
Mesure le temps de latence entre l'envoi d'un message et sa réception.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/ping`

Cette commande va envoyer un message "Pong!" et afficher le temps de latence en millisecondes.

 


# /supprimer_categorie

Cette commande permet de supprimer une catégorie spécifique ainsi que tous les canaux qu'elle contient.

#### Exemple d'utilisation : 

`/supprimer_categorie [nom_categorie]`

#### Fonctionnalités :
Supprime la catégorie spécifiée.
Supprime tous les canaux de discussion textuels et vocaux dans cette catégorie.

#### Paramètres :
nom_categorie : Le nom de la catégorie à supprimer (sans les signes "=").

#### Exemple d'utilisation en détail :

`/supprimer_categorie B2 IFD`

Cette commande va supprimer la catégorie "========== B2 IFD ==========" ainsi que tous les canaux qu'elle contient.
Elle affichera ensuite un message indiquant que la catégorie a été supprimée.


 

# /supprimer_channel

Cette commande permet de supprimer un canal de discussion textuel dans une catégorie spécifiée.

#### Exemple d'utilisation : 

`/supprimer_channel [nom_channel] [nom_categorie]`

#### Fonctionnalités :
Supprime un canal de discussion textuel dans une catégorie spécifiée.

#### Paramètres :
nom_channel : Le nom du canal à supprimer.
nom_categorie : Le nom de la catégorie où se trouve le canal.

#### Exemple d'utilisation en détail :

`/supprimer_channel informations_utiles B2 IFD`

Cette commande va supprimer le canal de discussion textuel "informations_utile" dans la catégorie "========== B2 IFD ==========".
Elle affichera ensuite un message indiquant que le canal a été supprimé de la catégorie spécifiée.

 


# /supprimer_role

Cette commande permet de supprimer un rôle spécifié à toutes les personnes ayant ce rôle. Vous avez également la possibilité de retirer le rôle uniquement aux personnes ayant un autre rôle spécifié.

#### Exemple d'utilisation : 

`/supprimer_role [role] (role2)`

#### Fonctionnalités :
Supprime un rôle à toutes les personnes ayant ce rôle.
Option pour retirer le rôle seulement aux personnes ayant un autre rôle spécifié.

#### Paramètres :
role : Le rôle à retirer aux personnes.
role2 : Le rôle optionnel à spécifier pour retirer le rôle uniquement aux personnes ayant ce rôle.

#### Exemple d'utilisation en détail :

`/supprimer_role @Admis @Apprenant IPI`

Cette commande va retirer le rôle @Admis à toutes les personnes ayant ce rôle, mais seulement si elles ont également le rôle @Apprenant IPI. Si @Apprenant IPI n'est pas spécifié dans la commande, le rôle @Admis sera retiré à toutes les personnes ayant ce rôle.
Elle affichera ensuite un message indiquant les personnes auxquelles le rôle a été supprimé.

 


# /transferer_categorie

Cette commande permet de transférer une catégorie existante à un autre rôle, tout en remplaçant une chaîne de caractères dans le nom des canaux de la catégorie.

#### Exemple d'utilisation : 

`/transferer_categorie [ancien_nom_categorie] [nouveau_nom_categorie] [ancien_nom_channel] [nouveau_nom_channel] [ancien_role] [nouveau_role]`

#### Fonctionnalités :
Change le nom de la catégorie.
Transfère les autorisations de l'ancien rôle au nouveau rôle.
Remplace une chaîne de caractères dans le nom des canaux de la catégorie.

#### Paramètres :
ancien_nom_categorie : Le nom actuel de la catégorie à transférer.
nouveau_nom_categorie : Le nouveau nom à donner à la catégorie.
ancien_nom_channel : La chaîne de caractères à remplacer dans le nom des canaux.
nouveau_nom_channel : La chaîne de caractères de remplacement dans le nom des canaux.
ancien_role : Le rôle ayant actuellement accès à la catégorie.
nouveau_role : Le nouveau rôle pouvant avoir accès à la catégorie.

#### Exemple d'utilisation en détail :

`/transferer_categorie B1 IFD B2 IFD b1 b2 @B1-IFD @B2-IFD`

Cette commande va changer le nom de la catégorie "========== B1 IFD ==========" en "========== B2 IFD ==========", transférer les autorisations du rôle "B1-IFD" au rôle "B2-IFD", et remplacer "b1" par "b2" dans le nom des canaux de cette catégorie.
Elle affichera ensuite un message indiquant que la catégorie a été transférée avec succès.

 


# /transferer_role

Cette commande permet de transférer un rôle spécifié à toutes les personnes ayant un autre rôle. Vous avez également la possibilité de supprimer le rôle actuel des personnes ayant le rôle d'origine.

#### Exemple d'utilisation : 
`/transferer_role [ancien_role] [nouveau_role] [supprimer]`


#### Fonctionnalités :
Transfère un rôle à toutes les personnes ayant un autre rôle.
Option pour supprimer le rôle actuel des personnes.

#### Paramètres :
ancien_role : Le rôle d'origine des personnes qui recevront le nouveau rôle.
nouveau_role : Le rôle à donner aux personnes.
supprimer : Booléen indiquant s'il faut supprimer le rôle actuel des personnes ayant le rôle d'origine.

#### Exemple d'utilisation en détail :

`/transferer_role @B1-IFD @B2-IFD True`

Cette commande va donner le rôle @B2-IFD à toutes les personnes ayant le rôle @B1-IFD. Si l'option True est activée, elle supprimera également le rôle @B1-IFD de ces personnes.
Elle affichera ensuite un message indiquant les personnes auxquelles le rôle a été donné ou supprimé.

# /vote_ajouter_image

Cette commande permet d'ajouter une image pour le vote.

#### Exemple d'utilisation : 

`/vote_ajouter_image [image]`

#### Fonctionnalités :
Ajoute une image pour le vote.
Crée un message avec un bouton pour voter pour l'image.

#### Paramètres :
image : L'image à ajouter pour le vote.

#### Exemple d'utilisation en détail :

`/vote_ajouter_image @image`

Cette commande va ajouter l'image spécifiée pour le vote et créer un message avec un bouton pour voter pour l'image.

# /vote_resultats

Cette commande permet d'afficher les résultats du vote.

#### Exemple d'utilisation : 

`/vote_resultats`

#### Fonctionnalités :
Affiche les résultats du vote.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/vote_resultats`

Cette commande va afficher les résultats du vote.

# /vote_supprimer

Cette commande permet de supprimer toutes les données et votes.

#### Exemple d'utilisation : 

`/vote_supprimer`

#### Fonctionnalités :
Supprime toutes les données et votes.

#### Paramètres :
Cette commande n'accepte pas de paramètres supplémentaires.

#### Exemple d'utilisation en détail :

`/vote_supprimer`

Cette commande va supprimer toutes les données et votes.
