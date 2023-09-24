import discord,re,json,urllib.request
from discord.ext import commands
from discord import app_commands
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import os, logging

logging.basicConfig(filename='bot_errors.log', level=logging.ERROR, format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
intents = discord.Intents().all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

with open("data.json") as jsonFile:
    DataJson = json.load(jsonFile)
    jsonFile.close()

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Gerer les choses..."))
    await tree.sync()
    print("Ready!")


@tree.command(name = "assigner_role", description = "Donne le role ciblé a toutes les personnes dans le fichier .csv")
@commands.has_permissions(administrator=True)
@app_commands.describe(fichier="Fichier contenant les nom et prenom dans deux colonnes séparées", role="Role a donner aux personnes presentes dans le fichier", supprimer="Faut-il supprimer les personnes ayant le role actuellement ?")
async def assign_role(ctx, fichier: discord.Attachment, role : discord.Role, supprimer : bool):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
        
        if supprimer==True:

            OldMemberID = [m.id for m in role.members]
            OldMember = [m.display_name for m in role.members]
            for member in OldMemberID:

                await ctx.guild.get_member(member).remove_roles(role)

            OldMemberTxt = ', '.join(OldMember)

        member_list = []

        for member in ctx.guild.members:

            member_list.append(member.display_name.replace(" ", "").lower())
            member_list.append(member.id)

        try:

            all_file = []
            for row in urllib.request.urlopen(urllib.request.Request(url=str(fichier), headers={'User-Agent': 'Mozilla/5.0'})):

                element_list=[]
                for element in re.split(',|\n|\r|;|\ufeff', row.decode('utf-8')):

                    if element != "":

                        element_list.append(element)

                all_file.append(element_list)
            
            not_found=[]
            for element_list in all_file:

                try:

                    element_list[1]
                    if ((str(element_list[0]) + str(element_list[1])).replace(" ", "").lower() in member_list) or ((str(element_list[1]) + str(element_list[0])).replace(" ", "").lower() in member_list) :

                        try:

                            await (ctx.guild.get_member(member_list[member_list.index((str(element_list[0]) + str(element_list[1])).replace(" ", "").lower())+1])).add_roles(role)

                        except:

                            await (ctx.guild.get_member(member_list[member_list.index((str(element_list[1]) + str(element_list[0])).replace(" ", "").lower())+1])).add_roles(role)

                    else:

                        not_found.append(str(element_list[0]) + " " + str(element_list[1]))

                except IndexError:

                    pass

            not_found = ', '.join(not_found)
            NewMenberTxt = ', '.join([m.display_name for m in role.members])

            if supprimer==True:

                await ctx.edit_original_response(content=(f'Role supprimé à : {OldMemberTxt}\n\nRole donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}'))

            else:

                await ctx.edit_original_response(content=(f'Role donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}'))

        except Exception as e:

            print(e)
            await ctx.edit_original_response(content=("Fichier illisible (.csv)"))
    except Exception as e:
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@tree.command(name = "transferer_role", description = "Transfere un role a toutes les personnes ayant un autre role")
@commands.has_permissions(administrator=True)
@app_commands.describe(ancien_role="Les personnes ayant ce role vont recevoir le nouveau", nouveau_role="Role a donner", supprimer="Faut-il supprimer le role actuel utilisé pour transferer ? (oui /non)")
async def transfert_role(ctx, ancien_role : discord.Role, nouveau_role : discord.Role,supprimer : bool):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        OldMemberID = [m.id for m in ancien_role.members]
        OldMember = [m.display_name for m in ancien_role.members]
        OldMemberTxt = ', '.join(OldMember)

        if supprimer==True:

            for member in OldMemberID:

                await ctx.guild.get_member(member).remove_roles(ancien_role)
        
        for member in OldMemberID:

                await ctx.guild.get_member(member).add_roles(nouveau_role)

        NewMenberTxt = ', '.join([m.display_name for m in nouveau_role.members])
        if supprimer == True:

            await ctx.edit_original_response(content=(f'Role supprimer à : {OldMemberTxt}\n\nRole donné à : {NewMenberTxt}'))

        else:

            await ctx.edit_original_response(content=(f'Role donné à : {NewMenberTxt}'))
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@tree.command(name = "creer_categorie", description = "Créer une catégorie basique avec les channels, et permissions")
@commands.has_permissions(administrator=True)
@app_commands.describe(nom_categorie="Nom de la catégorie à créer (sans les =)", role="Role ayant acces a cette catégorie", role2="Second role ayant acces a la catégorie (optionnel)")
async def create_category(ctx, nom_categorie : str, role : discord.Role, role2 : discord.Role = None):
    try:
        server = ctx.guild
        name_cat = f" {nom_categorie} "

        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        while len(name_cat) <= 27:

            name_cat = f"={name_cat}="

        tmp=""
        for letter in nom_categorie:
            if letter != " ":
                tmp+=letter
            else:
                tmp+="-"

        nom_categorie = tmp
        await server.create_category(name=name_cat.upper())

        category_object = discord.utils.get(ctx.guild.categories, name=name_cat.upper())
        await category_object.set_permissions(target=role, read_messages=True, send_messages=True, connect=True, speak=True)

        if role2 != None:

            await category_object.set_permissions(target=role2, read_messages=True, send_messages=True, connect=True, speak=True)

        await category_object.set_permissions(ctx.guild.default_role, read_messages=False, connect=False)

        await server.create_text_channel(name="général-"+nom_categorie.lower(),category=category_object)
        await server.create_text_channel(name="pédago-"+nom_categorie.lower(),category=category_object)

        pedago = discord.utils.get(ctx.guild.roles,name="Team Pedago IPI")
        await discord.utils.get(ctx.guild.channels, name="pédago-"+nom_categorie.lower()).set_permissions(target=pedago, read_messages=True, send_messages=True, connect=True, speak=True)

        await server.create_text_channel(name="only-you",category=category_object)
        await server.create_voice_channel(name="général-vocal",category=category_object)
        if role2==None:

            await ctx.edit_original_response(content=(f'Catégorie {name_cat.upper()} créée pour {role} !'),)

        else:

            await ctx.edit_original_response(content=(f'Catégorie {name_cat.upper()} créee pour {role} et {role2} !'))
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@tree.command(name = "supprimer_categorie", description = "Supprime la catégorie ainsi que les channels qu'elle contient")
@commands.has_permissions(administrator=True)
@app_commands.describe(nom_categorie="Nom de la catégorie a supprimer (sans les =)")
async def delete_category(ctx, nom_categorie : str):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        name_cat = f" {nom_categorie} "
        while len(name_cat) <= 27:

            name_cat = f"={name_cat}="

        tmp=""
        for letter in nom_categorie:

            if letter != " ":

                tmp+=letter

            else:

                tmp+="-"

        nom_categorie = tmp

        try:

            category_object = discord.utils.get(ctx.guild.categories, id=(discord.utils.get(ctx.guild.categories, name=name_cat.upper()).id))
        
            if category_object is None:

                await ctx.edit_original_response(content=(f"La catégorie {name_cat.upper()} n'existe pas !"))

            else:

                try:

                    for channel in category_object.channels:

                        await channel.delete()

                    await category_object.delete()

                except discord.errors.NotFound as e:
                    
                    print(e)
                    
                await ctx.edit_original_response(content=(f'Catégorie {name_cat.upper()} supprimée !'))
            
        except AttributeError:

            await ctx.edit_original_response(content=(f"La catégorie {name_cat.upper()} n'existe pas !"))
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@tree.command(name = "creer_channel", description = "Créer un channel dans une catégroei et lui donne les bonnes permissions !")
@commands.has_permissions(manage_channels=True)
@app_commands.describe(nom_channel="Nom du channel a créer", nom_categorie="Catégorie où créer le channel")
async def create_channel(ctx, nom_channel : str, nom_categorie : str):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        server = ctx.guild
        tmp=""

        for letter in nom_channel:

            if letter != " ":

                tmp+=letter

            else:

                tmp+="-"

        name_cat = f" {nom_categorie} "
        while len(name_cat) <= 27:

            name_cat = f"={name_cat}="

        category_object = discord.utils.get(ctx.guild.categories, name=name_cat.upper())

        await server.create_text_channel(name=nom_channel.lower(),category=category_object)

        pedago = discord.utils.get(ctx.guild.roles,name="Team Pedago IPI")
        await discord.utils.get(ctx.guild.channels, name=nom_channel.lower()).set_permissions(target=pedago, read_messages=True, send_messages=True, connect=True, speak=True)

        await ctx.edit_original_response(content=(f'Channel {nom_channel.lower()} créé dans la catégorie {name_cat.upper()} !'))
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@tree.command(name = "delete_channel", description = "Supprime un channel dans une catégorie")
@commands.has_permissions(administrator=True)
@app_commands.describe(nom_channel="Nom du channel a supprimer", nom_categorie="Catégorie dans lequel il est situé")
async def delete_channel(ctx, nom_channel : str, nom_categorie : str):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        name_cat = f" {nom_categorie} "
        while len(name_cat) <= 27:

            name_cat = f"={name_cat}="

        try:

            category_object = discord.utils.get(ctx.guild.categories, id=(discord.utils.get(ctx.guild.categories, name=name_cat.upper()).id))
        
            if category_object is None:

                await ctx.edit_original_response(content=(f"La catégorie {name_cat.upper()} n'existe pas !"))

            else:

                try:

                    for channels in category_object.channels:

                        if str(channels) == nom_channel:

                            await channels.delete()

                except discord.errors.NotFound as e:

                    print(e)
                    
                await ctx.edit_original_response(content=(f'Channel {nom_channel.lower()} supprimé dans la catégorie {name_cat.upper()} !'))
            
        except AttributeError as e:

            print(e)
            await ctx.edit_original_response(content=(f"Channel {nom_channel.lower()} n'éxiste pas dans la catégorie {name_cat.upper()}"))
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return


@tree.command(name = "transferer_categorie", description = "Transferer une catégorie à un autre rôle")
@commands.has_permissions(administrator=True)
@app_commands.describe(nouveau_nom_categorie="Nom actuel de la catégorie a transferer", ancien_nom_categorie="Nouveau nom a donner a la categorie",nouveau_role="Nouveau role pouvant avoir acces a la categorie",ancien_role="Role ayant actuellement l'acces a la categorie",nouveau_nom="Chaine de caractere servant a remplacer l'ancienne dans le nom des channels", ancien_nom="Chaine de caractere devant etre remplacer dans le nom des channels")
async def transfert_category(ctx, ancien_nom_categorie:str, nouveau_nom_categorie:str, ancien_nom:str, nouveau_nom:str, ancien_role : discord.Role, nouveau_role : discord.Role):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        try:
            name_cat = f" {ancien_nom_categorie.upper()} "
            while len(name_cat) <= 27:

                name_cat = f"={name_cat}="

            category = discord.utils.get(ctx.guild.categories, id=(discord.utils.get(ctx.guild.categories, name=name_cat.upper()).id))
            
            name_cat = f" {nouveau_nom_categorie} "
            while len(name_cat) <= 27:

                name_cat = f"={name_cat.upper()}="

            await category.edit(name=name_cat.upper())

            source_permissions = category.overwrites[ancien_role]
            target_permissions = {}

            for permission, value in source_permissions:
                target_permissions[permission] = value

            new_overwrite = discord.PermissionOverwrite(**target_permissions)
            await category.set_permissions(target=nouveau_role, overwrite=new_overwrite)

            await category.set_permissions(target=ancien_role, overwrite=None)

            if category is None:
                await ctx.edit_original_response(content="La catégorie spécifiée n'existe pas.")
                return
            
            for channel in category.channels:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                    overwrites = channel.overwrites
                    
                    new_name = channel.name.replace(ancien_nom.lower().replace(' ','-'), nouveau_nom.lower().replace(' ','-'))
                    await channel.edit(name=new_name)

                    nouveau_nom,ancien_nom = nouveau_nom.upper(),ancien_nom.upper()

                    if nouveau_role is None:
                        return
                    
                    if ancien_role is None:
                        return

                    if ancien_role in overwrites:
                        
                        source_permissions = channel.overwrites[ancien_role]
                        target_permissions = {}

                        for permission, value in source_permissions:
                            target_permissions[permission] = value

                        new_overwrite = discord.PermissionOverwrite(**target_permissions)
                        await channel.set_permissions(target=nouveau_role, overwrite=new_overwrite)

                        await channel.set_permissions(target=ancien_role, overwrite=None)

            await ctx.edit_original_response(content=f'La catégorie {ancien_nom_categorie} a bien été transferer du rôle {ancien_role.name} au role {nouveau_role.name}')

        except Exception as e:
            await ctx.edit_original_response(content=f'Une erreur est survenue, veuillez verifier que tous les paramètres sont correctes puis rééssayez. Si le problème persiste veuillez contacter Nathan SABOT DRESSY')
            print(e)
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return
    

@tree.command(name = "print_categories", description = "Affiche le nom de categorie")
@commands.has_permissions(administrator=True)
async def categories(ctx):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
        guild = ctx.guild
        category_names = [category.name for category in guild.categories]
        
        if category_names:
            await ctx.channel.send(content=f"Catégories du serveur:")
            for category in guild.categories:
                name_cat = f" {category.name.replace(' =','').replace('= ','').replace('=','')} "
                while len(name_cat) <= 27:
                    name_cat = f"={name_cat}="

                category_list = (name_cat)
                await ctx.channel.send(content=f"{category_list}")
            else:
                await ctx.edit_original_response(content="Le serveur ne possède pas de catégories.")
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return
    

@tree.command(name = "agenda", description = "Affiche l'agenda pour la semaine")
@app_commands.describe(date="Agenda a la date du : (au format jour/mois/année exemple : 05/04/2024)")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur','Apprenant IPI')
async def agenda(ctx, date:str = ""):
    try:
        await ctx.response.send_message(content="J'y travaille... (cela peut prendre plusieurs secondes)", ephemeral=True)

        with open("login_promo.json") as jsonFile:
            LoginPromoJson = json.load(jsonFile)
            jsonFile.close()
        if (str(ctx.user.id) in LoginPromoJson):
            if date == "":
                date = datetime.now().strftime("%m/%d/%Y")
            else:
                try:
                    date = datetime.strptime(date, "%d/%m/%Y").date().strftime("%m/%d/%Y")
                except ValueError:
                    await ctx.edit_original_response(content="Le format de la date fournit n'est pas valide la date doit etre le la forme jj/mm/aaaa")
            
            max_attempts = 3

            for attempt in range(max_attempts):
                if attempt > 0:
                    print(f"Tentative {attempt + 1}...")
                
                url = f'https://ws-edt-igs.wigorservices.net/WebPsDyn.aspx?action=posEDTLMS&serverID=G&date={date}'

                username = LoginPromoJson[str(ctx.user.id)]["login"]
                password = LoginPromoJson[str(ctx.user.id)]["mdp"]

                firefox_options = Options()
                firefox_options.add_argument("-private")
                firefox_options.add_argument('-headless')
                driver = webdriver.Firefox(options=firefox_options)

                driver.set_window_size(1920, 1080)

                driver.get(url)

                username_input = driver.find_element(By.ID, 'username')
                password_input = driver.find_element(By.ID, 'password')
                submit_button = driver.find_element(By.NAME, "submitBtn")

                username_input.send_keys(username)
                password_input.send_keys(password)

                submit_button.click()

                wait = WebDriverWait(driver, 5)
                url_to_wait_for = "https://ws-edt-igs.wigorservices.net/WebPsDyn.aspx"
                wait.until(EC.url_contains(url_to_wait_for))

                # Vérifiez si le texte "Server Error in '/' Application." est présent dans le HTML
                if "Server Error in '/' Application." in driver.page_source:
                    print("Erreur détectée dans le HTML. Relance du script...")
                    driver.quit()
                else:
                    # Si aucune erreur n'est détectée, enregistrez la capture d'écran et quittez le script
                    driver.save_screenshot(f"Timeable.png")
                    driver.quit()
                    break
            file = discord.File(f"Timeable.png")
            if os.path.exists(f"Timeable.png"):
                try:
                    os.remove(f"Timeable.png")
                except:
                    pass
            
            await ctx.edit_original_response(content="Ton emploi du temps t'as été envoyé en message ! Verifie bien que tu puisse recevoir des messages de ma part !")
            user = client.get_user(ctx.user.id)
            await user.send(file=file)
        else:
            await ctx.edit_original_response(content="Tu ne possède pas d'identifiants enregitrés, pour cela tu peux effectuer /agenda_enregitrer !")
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@tree.command(name = "agenda_accorder_droit", description = "Donne le droit d'acceder a votre emploi du temps a la personne ciblée (de preference de votre promo)")
@app_commands.describe(membre="Membre a qui donner le droit")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur','Apprenant IPI')
async def accorder_droit(ctx, membre: discord.Member):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("login_promo.json") as jsonFile:
            LoginPromoJson = json.load(jsonFile)
            jsonFile.close()
        if (str(ctx.user.id) in LoginPromoJson):
            if (str(membre.id) not in LoginPromoJson):
                nouvelle_entree = {str(membre.id): {"login" : LoginPromoJson[str(ctx.user.id)]["login"] ,"mdp" : LoginPromoJson[str(ctx.user.id)]["mdp"], "extend": True}}

                LoginPromoJson.update(nouvelle_entree)

                with open('login_promo.json', 'w') as file:
                    json.dump(LoginPromoJson, file, indent=4)
                await ctx.edit_original_response(content="Les accès a ton emploi du temps ont été accordé à " + membre.nick)
            else:
                await ctx.edit_original_response(content="Cette personne possède deja des identifiants")
        else:
            await ctx.edit_original_response(content="Vous ne posséder pas d'identifiants enregistrer identifiants")

        await ctx.edit_original_response(content="Une erreur s'est produite")
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return
@tree.command(name = "agenda_retirer_droit", description = "Retire le droit d'acceder a votre emploi du temps a la personne ciblée")
@app_commands.describe(membre="Membre a qui retirer le droit")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur','Apprenant IPI')
async def retirer_droit(ctx, membre: discord.Member):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("login_promo.json") as jsonFile:
            LoginPromoJson = json.load(jsonFile)
            jsonFile.close()
        if (str(ctx.user.id) in LoginPromoJson):
            if (str(membre.id) in LoginPromoJson):
                if (LoginPromoJson[str(ctx.user.id)]["extend"] == False) and LoginPromoJson[str(ctx.user.id)]['login'] == LoginPromoJson[str(membre.id)]['login'] :

                    del LoginPromoJson[str(membre.id)]

                    with open('login_promo.json', 'w') as file:
                        json.dump(LoginPromoJson, file, indent=4)
                    await ctx.edit_original_response(content="Les accès a ton emploi du temps ont été retirer à " + membre.nick)
                else:
                    await ctx.edit_original_response(content="Vous ne posseder pas le droit de retirer les permissions a cette personnes")
            else:
                await ctx.edit_original_response(content="Cette personne ne possède pas d'identifiants enregitrés")
        else:
            await ctx.edit_original_response(content="Vous ne posséder pas d'identifiants enregistrés identifiants")
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@tree.command(name = "agenda_enregitrer", description = "S'enregitrer pour avoir acces a son emploi du temps sur discord")
@app_commands.describe(identifiant="Identifiant de connection MonCampus", mdp="Mot de passe de connection MonCampus")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur','Apprenant IPI')
async def enregitrer(ctx, identifiant: str, mdp : str):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("login_promo.json") as jsonFile:
            LoginPromoJson = json.load(jsonFile)
            jsonFile.close()
        if (str(ctx.user.id) not in LoginPromoJson):
            nouvelle_entree = {str(ctx.user.id): {"login" : identifiant ,"mdp" : mdp, "extend": False}}

            LoginPromoJson.update(nouvelle_entree)

            with open('login_promo.json', 'w') as file:
                json.dump(LoginPromoJson, file, indent=4)
            await ctx.edit_original_response(content="Tes identifiants ont bien été enregitrés")

        else:
            await ctx.edit_original_response(content="Vous posséder deja des identifiants enregistrés")
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return
    
@tree.command(name = "agenda_eleve", description = "Affiche l'agenda pour la semaine")
@app_commands.describe(membre="Vous allez visiualiser l'agenda de cette personne si elle s'est authentifiée (il est possible que l'emploi du temps soit celui d'une autre personne si elle lui a donnée l'acces a ce dernier)" ,date="Agenda a la date du : (au format jour/mois/année exemple : 05/04/2024)")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur')
async def agenda_eleve(ctx, membre: discord.Member ,date:str = ""):
    try:
        await ctx.response.send_message(content="J'y travaille... (cela peut prendre plusieurs secondes)", ephemeral=True)

        with open("login_promo.json") as jsonFile:
            LoginPromoJson = json.load(jsonFile)
            jsonFile.close()
        if (str(membre.id) in LoginPromoJson):
            if date == "":
                date = datetime.now().strftime("%m/%d/%Y")
            else:
                try:
                    date = datetime.strptime(date, "%d/%m/%Y").date().strftime("%m/%d/%Y")
                except ValueError:
                    await ctx.edit_original_response(content="Le format de la date fournit n'est pas valide la date doit etre le la forme jj/mm/aaaa")
            
            max_attempts = 3

            for attempt in range(max_attempts):
                if attempt > 0:
                    print(f"Tentative {attempt + 1}...")
                
                url = f'https://ws-edt-igs.wigorservices.net/WebPsDyn.aspx?action=posEDTLMS&serverID=G&date={date}'

                username = LoginPromoJson[str(membre.id)]["login"]
                password = LoginPromoJson[str(membre.id)]["mdp"]

                firefox_options = Options()
                firefox_options.add_argument("-private")
                firefox_options.add_argument('-headless')
                driver = webdriver.Firefox(options=firefox_options)

                driver.set_window_size(1920, 1080)

                driver.get(url)

                username_input = driver.find_element(By.ID, 'username')
                password_input = driver.find_element(By.ID, 'password')
                submit_button = driver.find_element(By.NAME, "submitBtn")

                username_input.send_keys(username)
                password_input.send_keys(password)

                submit_button.click()

                wait = WebDriverWait(driver, 5)
                url_to_wait_for = "https://ws-edt-igs.wigorservices.net/WebPsDyn.aspx"
                wait.until(EC.url_contains(url_to_wait_for))

                # Vérifiez si le texte "Server Error in '/' Application." est présent dans le HTML
                if "Server Error in '/' Application." in driver.page_source:
                    print("Erreur détectée dans le HTML. Relance du script...")
                    driver.quit()
                else:
                    # Si aucune erreur n'est détectée, enregistrez la capture d'écran et quittez le script
                    driver.save_screenshot(f"Timeable.png")
                    driver.quit()
                    break

            file = discord.File(f"Timeable.png")
            if os.path.exists(f"Timeable.png"):
                try:
                    os.remove(f"Timeable.png")
                except:
                    pass
            
            await ctx.edit_original_response(content="Et voici l'emploi du temps de " + membre.nick + " !")
            await ctx.channel.send(file=file)
        else:
            await ctx.edit_original_response(content="Cette personne ne possède pas d'identifiants enregitrés !")
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
        
        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return
@tree.command(name="agenda_modifier", description="Modifier les identifiants enregistrés")
@app_commands.describe(identifiant="Nouvel identifiant de connection MonCampus", mdp="Nouveau mot de passe de connection MonCampus")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur', 'Apprenant IPI')
async def agenda_modifier(ctx, identifiant: str, mdp: str):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("login_promo.json", 'r') as jsonFile:
            LoginPromoJson = json.load(jsonFile)

        updated_entries = 0  # Compteur pour le nombre d'entrées mises à jour
        updated_nicknames = []

        refId = LoginPromoJson[str(ctx.user.id)]["login"]

        for user_key, user_data in LoginPromoJson.items():
            if user_data["login"] == refId:
                user_data['login'] = identifiant
                user_data["mdp"] = mdp
                updated_entries += 1

                member = ctx.guild.get_member(int(user_key))
                if member:
                    updated_nicknames.append(member.display_name)

        if updated_entries > 0:
            with open('login_promo.json', 'w') as file:
                json.dump(LoginPromoJson, file, indent=4)

            if updated_nicknames:
                nickname_list = ", ".join(updated_nicknames)
                await ctx.edit_original_response(content=f"Le mot de passe de {updated_entries} entrées avec l'identifiant '{identifiant}' a été mis à jour avec succès. Les nicknames mis à jour sont : {nickname_list}")
            else:
                await ctx.edit_original_response(content=f"Le mot de passe de {updated_entries} entrées avec l'identifiant '{identifiant}' a été mis à jour avec succès, mais aucun utilisateur avec un nickname trouvé.")

        else:
            await ctx.edit_original_response(content="Aucun identifiant enregistré trouvé pour votre utilisateur.")

    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "modifier_entree": {e}', exc_info=True)

        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")


@tree.command(name="agenda_desenregistrer", description="Supprimer toutes les entrées avec votre identifiant")
@app_commands.describe()
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur', 'Apprenant IPI')
async def desenregistrer(ctx):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("login_promo.json", 'r') as jsonFile:
            LoginPromoJson = json.load(jsonFile)

        user_id = str(ctx.user.id)
        entries_deleted = 0  # Compteur pour le nombre d'entrées supprimées

        # Créez une copie de clés pour éviter de supprimer des clés pendant la boucle
        keys_to_delete = []

        refId = LoginPromoJson[str(ctx.user.id)]["login"]
        is_author = LoginPromoJson[user_id]['extend'] == False

        if is_author:
            for user_key, user_data in LoginPromoJson.items():
                if user_data["login"] == refId:
                    keys_to_delete.append(user_key)
                    entries_deleted += 1

            # Supprimez les clés correspondantes
            for key in keys_to_delete:
                del LoginPromoJson[key]

            if entries_deleted > 0:
                with open('login_promo.json', 'w') as file:
                    json.dump(LoginPromoJson, file, indent=4)

                await ctx.edit_original_response(content=f"Toutes les entrées avec l'identifiant '{refId}' ont été supprimées avec succès")

            else:
                await ctx.edit_original_response(content=f"Aucune entrée avec l'identifiant '{refId}' n'a été trouvée.")
        else:
            del LoginPromoJson[user_id]
            with open('login_promo.json', 'w') as file:
                json.dump(LoginPromoJson, file, indent=4)
            await ctx.edit_original_response(content=f"Tes identifiants ont bien été supprimées")

    except Exception as e:
        # Enregistrer l'erreur dans le fichier de journal
        logging.error(f'Error in command "desenregistrer": {e}', exc_info=True)

        # Modifier la réponse originale pour indiquer qu'une erreur s'est produite
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")



client.run(DataJson["DISCORD_TOKEN"])