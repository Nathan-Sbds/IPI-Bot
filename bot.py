import discord,re,json,urllib.request,os,logging,cryptocode,asyncio
from discord import app_commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from datetime import datetime,timedelta

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

    while not client.is_closed():
        now = datetime.now()
        next_execution_time = datetime(now.year, now.month, now.day, 4,0,0)
        if now.weekday() > 0:
            days_until_monday = 7 - now.weekday()
            next_execution_time += timedelta(days=days_until_monday)
        
        if next_execution_time < now:
            next_execution_time += timedelta(weeks=1)

        delta = next_execution_time - now
        seconds_until_execution = delta.total_seconds()

        await asyncio.sleep(seconds_until_execution)
        await all_agenda_week_print()



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
                    return
            
            max_attempts = 3

            for attempt in range(max_attempts):
                if attempt > 0:
                    print(f"Tentative {attempt + 1}...")
                
                url = f'https://ws-edt-igs.wigorservices.net/WebPsDyn.aspx?action=posEDTLMS&serverID=G&date={date}'

                username = cryptocode.decrypt(LoginPromoJson[str(ctx.user.id)]["login"], DataJson['CRYPT'])
                password = cryptocode.decrypt(LoginPromoJson[str(ctx.user.id)]["mdp"], DataJson['CRYPT'])

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

                if "Server Error in '/' Application." in driver.page_source:
                    print("Erreur détectée dans le HTML. Relance du script...")
                    driver.quit()
                else:
                    driver.save_screenshot(f"Timeable.png")
                    driver.quit()
                    break
            file = discord.File(f"Timeable.png")
                
            user = client.get_user(ctx.user.id)
            await user.send(file=file)
            await ctx.edit_original_response(content="Ton emploi du temps t'as été envoyé en message ! Verifie bien que tu puisse recevoir des messages de ma part !")
            if os.path.exists(f"Timeable.png"):
                os.remove(f"Timeable.png")
        else:
            await ctx.edit_original_response(content="Tu ne possède pas d'identifiants enregitrés, pour cela tu peux effectuer /agenda_enregitrer !")
    except Exception as e:
        logging.error(f'Error in command "agenda": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@agenda.error
async def agenda_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)


@tree.command(name = "agenda_accorder_droit_membre", description = "Donne le droit d'acceder a votre emploi du temps a la personne ciblée (de preference de votre promo)")
@app_commands.describe(membre="Membre a qui donner le droit")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur','Apprenant IPI')
async def accorder_droit_membre(ctx, membre: discord.Member):
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
                await ctx.edit_original_response(content=f"Les accès a ton emploi du temps ont été accordé à <@{membre.id}>")
            else:
                await ctx.edit_original_response(content=f"<@{membre.id}> possède deja des identifiants")
        else:
            await ctx.edit_original_response(content="Vous ne posséder pas d'identifiants enregistrer identifiants")

        
    except Exception as e:
        logging.error(f'Error in command "accorder_droit_membre": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@accorder_droit_membre.error
async def accorder_droit_membre_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)


@tree.command(name = "agenda_accorder_droit_role", description = "Donne le droit d'acceder a votre emploi du temps a toutes les personnes ayant le role ciblé")
@app_commands.describe(role="Role a qui donner le droit")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur','Apprenant IPI')
async def accorder_droit_role(ctx, role: discord.Role):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        roles_interdits = ["Admin Serveur", "Directrice IPI", "Team Communication IPI", "Team Entreprise IPI", "Team Pedago IPI", "Formateur", "League IPI", "YAGPDB.xyz", "IPI Bot", "Alumni", "Apprenant IPI", "Join League", "Aide Infra", "Aide Dev", "Citoyen", "Filière Dev", "Filière Infra", "Membre", "WHOOP"]

        if role.name in roles_interdits or role not in ctx.user.roles:
            await ctx.edit_original_response(content="Vous ne pouvez pas accorder ce droit à ce rôle.")
            return
        
        with open("login_promo.json") as jsonFile:
            LoginPromoJson = json.load(jsonFile)
            jsonFile.close()

        for membre in role.members:
            if (str(membre.id) not in LoginPromoJson):
                nouvelle_entree = {str(membre.id): {"login" : LoginPromoJson[str(ctx.user.id)]["login"] ,"mdp" : LoginPromoJson[str(ctx.user.id)]["mdp"], "extend": True}}

                LoginPromoJson.update(nouvelle_entree)

                with open('login_promo.json', 'w') as file:
                    json.dump(LoginPromoJson, file, indent=4)
                
        await ctx.edit_original_response(content=f"Les accès a ton emploi du temps ont été accordés à toutes les personnes ayant le role {role.mention}")

    except Exception as e:
        logging.error(f'Error in command "accorder_droit_role": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@accorder_droit_role.error
async def accorder_droit_role_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name="agenda_desenregistrer", description="Supprimer toutes les entrées avec votre identifiant")
@app_commands.describe()
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur', 'Apprenant IPI')
async def desenregistrer(ctx):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("login_promo.json", 'r') as jsonFile:
            LoginPromoJson = json.load(jsonFile)

        user_id = str(ctx.user.id)
        entries_deleted = 0

        keys_to_delete = []

        refId = LoginPromoJson[str(ctx.user.id)]["login"]
        is_author = LoginPromoJson[user_id]['extend'] == False

        if is_author:
            for user_key, user_data in LoginPromoJson.items():
                if user_data["login"] == refId:
                    keys_to_delete.append(user_key)
                    entries_deleted += 1

            for key in keys_to_delete:
                del LoginPromoJson[key]

            if entries_deleted > 0:
                with open('login_promo.json', 'w') as file:
                    json.dump(LoginPromoJson, file, indent=4)

                await ctx.edit_original_response(content=f"Toutes les entrées avec l'identifiant '{cryptocode.decrypt(LoginPromoJson[str(ctx.user.id)]['login'], DataJson['CRYPT'])}' ont été supprimées avec succès")

            else:
                await ctx.edit_original_response(content=f"Aucune entrée avec l'identifiant '{cryptocode.decrypt(LoginPromoJson[str(ctx.user.id)]['login'], DataJson['CRYPT'])}' n'a été trouvée.")
        else:
            del LoginPromoJson[user_id]
            with open('login_promo.json', 'w') as file:
                json.dump(LoginPromoJson, file, indent=4)
            await ctx.edit_original_response(content=f"Tes identifiants ont bien été supprimées")

    except Exception as e:
        logging.error(f'Error in command "desenregistrer": {e}', exc_info=True)

        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")

@desenregistrer.error
async def desenregistrer_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



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
            
                    return
            max_attempts = 3

            for attempt in range(max_attempts):
                if attempt > 0:
                    print(f"Tentative {attempt + 1}...")
                
                url = f'https://ws-edt-igs.wigorservices.net/WebPsDyn.aspx?action=posEDTLMS&serverID=G&date={date}'

                username = cryptocode.decrypt(LoginPromoJson[str(membre.id)]["login"], DataJson['CRYPT'])
                password = cryptocode.decrypt(LoginPromoJson[str(membre.id)]["mdp"], DataJson['CRYPT'])

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

                if "Server Error in '/' Application." in driver.page_source:
                    print("Erreur détectée dans le HTML. Relance du script...")
                    driver.quit()
                else:
                    driver.save_screenshot(f"Timeable.png")
                    driver.quit()
                    break

            file = discord.File(f"Timeable.png")
            if os.path.exists(f"Timeable.png"):
                try:
                    os.remove(f"Timeable.png")
                except:
                    pass
            
            await ctx.edit_original_response(content="L'emploi du temps de " + membre.nick + " a été envoyé par message!")
            user = client.get_user(ctx.user.id)
            await user.send(file=file, content=f"Voici l'emploi du temps de {membre.nick}")
        else:
            await ctx.edit_original_response(content="Cette personne ne possède pas d'identifiants enregitrés !")
    except Exception as e:
        logging.error(f'Error in command "agenda_eleve": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return


@agenda_eleve.error
async def agenda_eleve_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)


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
            nouvelle_entree = {str(ctx.user.id): {"login" : cryptocode.encrypt(identifiant, DataJson['CRYPT']) ,"mdp" : cryptocode.encrypt(mdp, DataJson['CRYPT']), "extend": False}}

            LoginPromoJson.update(nouvelle_entree)

            with open('login_promo.json', 'w') as file:
                json.dump(LoginPromoJson, file, indent=4)
            await ctx.edit_original_response(content="Tes identifiants ont bien été enregitrés")

        else:
            await ctx.edit_original_response(content="Vous posséder deja des identifiants enregistrés")
    except Exception as e:
        logging.error(f'Error in command "enregitrer": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@enregitrer.error
async def enregitrer_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)


@tree.command(name="agenda_modifier", description="Modifier les identifiants enregistrés")
@app_commands.describe(identifiant="Nouvel identifiant de connection MonCampus", mdp="Nouveau mot de passe de connection MonCampus")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur', 'Apprenant IPI')
async def agenda_modifier(ctx, identifiant: str, mdp: str):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("login_promo.json", 'r') as jsonFile:
            LoginPromoJson = json.load(jsonFile)

        updated_entries = 0
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
        logging.error(f'Error in command "agenda_modifier": {e}', exc_info=True)

        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")

@agenda_modifier.error
async def agenda_modifier_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name = "agenda_retirer_droit_membre", description = "Retire le droit d'acceder a votre emploi du temps a la personne ciblée")
@app_commands.describe(membre="Membre a qui retirer le droit")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur','Apprenant IPI')
async def retirer_droit_membre(ctx, membre: discord.Member):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("login_promo.json") as jsonFile:
            LoginPromoJson = json.load(jsonFile)
            jsonFile.close()
        if (str(ctx.user.id) in LoginPromoJson):
            if (str(membre.id) in LoginPromoJson):
                if (LoginPromoJson[str(ctx.user.id)]["extend"] == False) and (ctx.user.id != membre.id) and LoginPromoJson[str(ctx.user.id)]['login'] == LoginPromoJson[str(membre.id)]['login'] :

                    del LoginPromoJson[str(membre.id)]

                    with open('login_promo.json', 'w') as file:
                        json.dump(LoginPromoJson, file, indent=4)
                    await ctx.edit_original_response(content=f"Les accès a ton emploi du temps ont été retirer à <@{membre.id}>")
                else:
                    await ctx.edit_original_response(content="Vous ne posseder pas le droit de retirer les permissions a cette personnes")
            else:
                await ctx.edit_original_response(content="Cette personne ne possède pas d'identifiants enregitrés")
        else:
            await ctx.edit_original_response(content="Vous ne posséder pas d'identifiants enregistrés identifiants")
    except Exception as e:
        logging.error(f'Error in command "retirer_droit_membre": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@retirer_droit_membre.error
async def retirer_droit_membre_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name = "agenda_retirer_droit_role", description = "Retire le droit d'acceder a votre emploi du temps a toutes les personnes ayant le role ciblé")
@app_commands.describe(role="Role a qui retirer le droit")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur','Apprenant IPI')
async def retirer_droit_role(ctx, role: discord.Role):
    roles_interdits = ["Admin Serveur", "Directrice IPI", "Team Communication IPI", "Team Entreprise IPI", "Team Pedago IPI", "Formateur", "League IPI", "YAGPDB.xyz", "IPI Bot", "Alumni", "Apprenant IPI", "Join League", "Aide Infra", "Aide Dev", "Citoyen", "Filière Dev", "Filière Infra", "Membre", "WHOOP"]
    try:
        if role.name in roles_interdits or role not in ctx.user.roles:
            await ctx.edit_original_response(content="Vous ne pouvez pas retirer ce droit à ce role.")
            return

    
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("login_promo.json") as jsonFile:
            LoginPromoJson = json.load(jsonFile)
            jsonFile.close()

        for membre in role.members:
            if (str(membre.id) in LoginPromoJson) and (LoginPromoJson[str(ctx.user.id)]["extend"] == False) and (ctx.user.id != membre.id) and LoginPromoJson[str(ctx.user.id)]['login'] == LoginPromoJson[str(membre.id)]['login']:
                del LoginPromoJson[str(membre.id)]

                with open('login_promo.json', 'w') as file:
                    json.dump(LoginPromoJson, file, indent=4)

        await ctx.edit_original_response(content=f"Les accès a ton emploi du temps ont été retirer à toutes les personnes ayant le role {role.mention}")

    except Exception as e:
        logging.error(f'Error in command "retirer_droit_role": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@retirer_droit_role.error
async def retirer_droit_role_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name="agenda_voir_partage_droit", description="Voir les membres avec qui vous partagez votre agenda")
@app_commands.checks.has_any_role('Team Pedago IPI', 'Team Entreprise IPI', 'Team Communication IPI', 'Directrice IPI', 'Admin Serveur', 'Apprenant IPI')
async def voir_membres_droit(ctx):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
        with open("login_promo.json") as jsonFile:
            LoginPromoJson = json.load(jsonFile)
        
        user_login = LoginPromoJson.get(str(ctx.user.id), {}).get("login", None)
        
        if user_login:
            matching_members = [member_id for member_id, member_data in LoginPromoJson.items()
                if member_data.get("login") == user_login and member_data.get("extend", False)]
            
            if matching_members:
                member_mentions = [f"<@{member_id}>" for member_id in matching_members]
                await ctx.edit_original_response(content=f"Les membres avec qui vous partager votre agenda sont : {', '.join(member_mentions)}")
            else:
                await ctx.edit_original_response(content="Vous ne partagez actuellement pas votre agenda")
        else:
            await ctx.edit_original_response(content="Vous ne possédez pas d'identifiants enregistrés.")
        
    except Exception as e:
        logging.error(f'Error in command "voir_membres_droit": {e}', exc_info=True)
        await ctx.response.send_message(content="Une erreur s'est produite lors de l'exécution de la commande.", ephemeral=True)


@voir_membres_droit.error
async def voir_membres_droit_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)





@tree.command(name = "ping", description = "Donne la latence du bot !")
async def ping(ctx):
    latency = round(client.latency * 1000)
    await ctx.response.send_message(content=f'Pong! Latence: {latency}ms', ephemeral=True)


@ping.error
async def ping_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)


@tree.command(name = "assigner_role", description = "Donne le role ciblé a toutes les personnes dans le fichier .csv")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(fichier="Fichier contenant les nom et prenom dans deux colonnes séparées", supprimer="Faut-il supprimer les personnes ayant le role actuellement ?", role="Role a donner aux personnes presentes dans le fichier", role2="Second rôle a donner", role3="Second rôle a donner")
async def assign_role(ctx, fichier: discord.Attachment, supprimer : bool, role : discord.Role, role2 : discord.Role = None, role3 : discord.Role = None):
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
                            if role2 != None:
                                await (ctx.guild.get_member(member_list[member_list.index((str(element_list[0]) + str(element_list[1])).replace(" ", "").lower())+1])).add_roles(role2)
                            if role3 != None:
                                await (ctx.guild.get_member(member_list[member_list.index((str(element_list[0]) + str(element_list[1])).replace(" ", "").lower())+1])).add_roles(role3)

                        except:

                            await (ctx.guild.get_member(member_list[member_list.index((str(element_list[1]) + str(element_list[0])).replace(" ", "").lower())+1])).add_roles(role)
                            if role2 != None:
                                await (ctx.guild.get_member(member_list[member_list.index((str(element_list[1]) + str(element_list[0])).replace(" ", "").lower())+1])).add_roles(role2)
                            if role3 != None:
                                await (ctx.guild.get_member(member_list[member_list.index((str(element_list[1]) + str(element_list[0])).replace(" ", "").lower())+1])).add_roles(role3)

                    else:

                        not_found.append(str(element_list[0]) + " " + str(element_list[1]))

                except IndexError:

                    pass

            not_found = ', '.join(not_found)
            NewMenberTxt = ', '.join([f"<@{m.id}>" for m in role.members])

            if supprimer==True:

                await ctx.edit_original_response(content=(f'Role supprimé à : {OldMemberTxt}\n\nRole donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}'))
                user = client.get_user(ctx.user.id)
                await user.send(content=(f'Role supprimé à : {OldMemberTxt}\n\nRole donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}'))
            else:

                await ctx.edit_original_response(content=(f'Role donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}'))
                user = client.get_user(ctx.user.id)
                await user.send(content=(f'Role donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}'))

        except Exception as e:

            print(e)
            await ctx.edit_original_response(content=("Fichier illisible (.csv)"))
    except Exception as e:
        logging.error(f'Error in command "assign_role": {e}', exc_info=True)
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@assign_role.error
async def assign_role_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name = "creer_categorie", description = "Créer une catégorie basique avec les channels, et permissions")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(nom_categorie="Nom de la catégorie à créer (sans les =)", role="Role ayant acces a cette catégorie", role2="Second role ayant acces a la catégorie (optionnel)")
async def create_category(ctx, nom_categorie : str, role : discord.Role, role2 : discord.Role = None):
    try:
        server = ctx.guild
        name_cat = f" {nom_categorie.upper()} "

        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        while len(name_cat) <= 27:

            name_cat = f"={name_cat}="

        categories_with_name = []
        for category in ctx.guild.categories:
            if category.name == name_cat:
                categories_with_name.append(category)

        if len(categories_with_name) > 1:
            await ctx.edit_original_response(content=(f"Il existe {len(categories_with_name)} catégories avec le nom {name_cat}. Merci de bien vouloir corriger cela !")) 

        else:
            nom_categorie = nom_categorie.replace(' ','-')
            await server.create_category(name=name_cat.upper())

            category_object = discord.utils.get(ctx.guild.categories, name=name_cat.upper())
            await category_object.set_permissions(target=role, read_messages=True, send_messages=True, connect=True, speak=True)

            if role2 != None:

                await category_object.set_permissions(target=role2, read_messages=True, send_messages=True, connect=True, speak=True)

            await category_object.set_permissions(ctx.guild.default_role, read_messages=False, connect=False)

            await server.create_text_channel(name="général-"+nom_categorie.lower(),category=category_object)
            
            pedago = discord.utils.get(ctx.guild.roles,name="Team Pedago IPI")
            communication = discord.utils.get(ctx.guild.roles,name="Team Communication IPI")
            entreprise = discord.utils.get(ctx.guild.roles,name="Team Entreprise IPI")
            directrice = discord.utils.get(ctx.guild.roles,name="Directrice IPI")
            
            await server.create_text_channel(name="général-"+nom_categorie.lower(),category=category_object)
            await discord.utils.get(ctx.guild.channels, name="général-"+nom_categorie.lower()).set_permissions(target=pedago, read_messages=True, send_messages=True, connect=True, speak=True)
            await discord.utils.get(ctx.guild.channels, name="général-"+nom_categorie.lower()).set_permissions(target=communication, read_messages=True, send_messages=True, connect=True, speak=True)
            await discord.utils.get(ctx.guild.channels, name="général-"+nom_categorie.lower()).set_permissions(target=entreprise, read_messages=True, send_messages=True, connect=True, speak=True)
            await discord.utils.get(ctx.guild.channels, name="général-"+nom_categorie.lower()).set_permissions(target=directrice, read_messages=True, send_messages=True, connect=True, speak=True)    
            
            await server.create_text_channel(name="pédago-"+nom_categorie.lower(),category=category_object)
            await discord.utils.get(ctx.guild.channels, name="pédago-"+nom_categorie.lower()).set_permissions(target=pedago, read_messages=True, send_messages=True, connect=True, speak=True)

            await server.create_text_channel(name="only-you",category=category_object)
            await server.create_voice_channel(name="général-vocal",category=category_object)
            if role2==None:

                await ctx.edit_original_response(content=(f'Catégorie {name_cat.upper()} créée pour {role} !'),)

            else:

                await ctx.edit_original_response(content=(f'Catégorie {name_cat.upper()} créee pour {role} et {role2} !'))
    except Exception as e:
        logging.error(f'Error in command "create_category": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@create_category.error
async def create_category_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name = "creer_channel", description = "Créer un channel dans une catégroei et lui donne les bonnes permissions !")
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(nom_channel="Nom du channel a créer", nom_categorie="Catégorie où créer le channel")
async def create_channel(ctx, nom_channel : str, nom_categorie : str):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        server = ctx.guild

        name_cat = f" {nom_categorie.upper()} "
        while len(name_cat) <= 27:

            name_cat = f"={name_cat}="

        categories_with_name = []
        for category in ctx.guild.categories:
            if category.name == name_cat:
                categories_with_name.append(category)

        if len(categories_with_name) > 1:
            await ctx.edit_original_response(content=(f"Il existe {len(categories_with_name)} catégories avec le nom {name_cat}. Merci de bien vouloir corriger cela !")) 

        else:

            category_object = discord.utils.get(ctx.guild.categories, name=name_cat.upper())

            await server.create_text_channel(name=nom_channel.lower(),category=category_object)

            pedago = discord.utils.get(ctx.guild.roles,name="Team Pedago IPI")
            await discord.utils.get(ctx.guild.channels, name=nom_channel.lower()).set_permissions(target=pedago, read_messages=True, send_messages=True, connect=True, speak=True)

            await ctx.edit_original_response(content=(f'Channel {nom_channel.lower()} créé dans la catégorie {name_cat.upper()} !'))
    except Exception as e:
        logging.error(f'Error in command "create_channel": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return


@create_channel.error
async def create_channel_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name = "supprimer_categorie", description = "Supprime la catégorie ainsi que les channels qu'elle contient")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(nom_categorie="Nom de la catégorie a supprimer (sans les =)")
async def delete_category(ctx, nom_categorie : str):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        name_cat = f" {nom_categorie.upper()} "
        while len(name_cat) <= 27:

            name_cat = f"={name_cat}="

        nom_categorie = nom_categorie.replace(' ',"-")

        categories_with_name = []
        for category in ctx.guild.categories:
            if category.name == name_cat:
                categories_with_name.append(category)

        if len(categories_with_name) > 1:
            await ctx.edit_original_response(content=(f"Il existe {len(categories_with_name)} catégories avec le nom {name_cat}. Merci de bien vouloir corriger cela !")) 

        else:
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
        logging.error(f'Error in command "delete_category": {e}', exc_info=True)
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@delete_category.error
async def delete_category_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name = "supprimer_channel", description = "Supprime un channel dans une catégorie")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(nom_channel="Nom du channel a supprimer", nom_categorie="Catégorie dans lequel il est situé")
async def delete_channel(ctx, nom_channel : str, nom_categorie : str):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        name_cat = f" {nom_categorie.upper()} "
        while len(name_cat) <= 27:

            name_cat = f"={name_cat}="
        
        categories_with_name = []
        for category in ctx.guild.categories:
            if category.name == name_cat:
                categories_with_name.append(category)

        if len(categories_with_name) > 1:
            await ctx.edit_original_response(content=(f"Il existe {len(categories_with_name)} catégories avec le nom {name_cat}. Merci de bien vouloir corriger cela !")) 

        else:
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
        logging.error(f'Error in command "delete_channel": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@delete_channel.error
async def delete_channel_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name = "supprimer_role", description = "Supprime le role a toutes les personnes ayant ce role")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(role="Role a retirere aux personnes", role2="Retirer le role seulement aux personnes ayant ce role")
async def supprime_role(ctx, role : discord.Role, role2 : discord.Role = None):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
        if role2 != None:
            MembersMention = ', '.join([f"<@{m.id}>" for m in role.members if m in role2.members])
            Members = ', '.join([m.display_name for m in role.members if m in role2.members])
            [await m.remove_roles(role) for m in role.members if m in role2.members]
        else:
            MembersMention = ', '.join([f"<@{m.id}>" for m in role.members])
            Members = ', '.join([m.display_name for m in role.members])
            [await m.remove_roles(role) for m in role.members]

        await ctx.edit_original_response(content=(f'Role supprimé pour : {MembersMention}'))
        user = client.get_user(ctx.user.id)
        await user.send(content=(f'Role supprimé pour : {Members}'))

    except Exception as e:
        logging.error(f'Error in command "supprime_role": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return


@supprime_role.error
async def supprime_role_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name = "transferer_categorie", description = "Transferer une catégorie à un autre rôle")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(nouveau_nom_categorie="Nom actuel de la catégorie a transferer", ancien_nom_categorie="Nouveau nom a donner a la categorie",nouveau_role="Nouveau role pouvant avoir acces a la categorie",ancien_role="Role ayant actuellement l'acces a la categorie",nouveau_nom_channel="Chaine de caractere servant a remplacer l'ancienne dans le nom des channels", ancien_nom_channel="Chaine de caractere devant etre remplacer dans le nom des channels")
async def transfert_category(ctx, ancien_nom_categorie:str, nouveau_nom_categorie:str, ancien_nom_channel:str, nouveau_nom_channel:str, ancien_role : discord.Role, nouveau_role : discord.Role):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        name_cat = f" {ancien_nom_categorie.upper()} "
        while len(name_cat) <= 27:

            name_cat = f"={name_cat}="

        categories_with_name = []
        for category in ctx.guild.categories:
            if category.name == name_cat:
                categories_with_name.append(category)

        if len(categories_with_name) > 1:
            await ctx.edit_original_response(content=(f"Il existe {len(categories_with_name)} catégories avec le nom {name_cat}. Merci de bien vouloir corriger cela !")) 

        else:    
            try:
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
                        
                        new_name = channel.name.replace(ancien_nom_channel.lower().replace(' ','-'), nouveau_nom_channel.lower().replace(' ','-'))
                        await channel.edit(name=new_name)

                        nouveau_nom_channel,ancien_nom_channel = nouveau_nom_channel.upper(),ancien_nom_channel.upper()

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
        logging.error(f'Error in command "transfert_category": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@transfert_category.error
async def transfert_category_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



@tree.command(name = "transferer_role", description = "Transfere un role a toutes les personnes ayant un autre role")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(ancien_role="Les personnes ayant ce role vont recevoir le nouveau", nouveau_role="Role a donner", supprimer="Faut-il supprimer le role actuel utilisé pour transferer ? (oui /non)")
async def transfert_role(ctx, ancien_role : discord.Role, nouveau_role : discord.Role,supprimer : bool):
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        OldMemberID = [m.id for m in ancien_role.members]
        OldMember = [f"<@{m.id}>" for m in ancien_role.members]
        OldMemberTxt = [m.display_name for m in ancien_role.members]
        NewRoleMember = [m.id for m in nouveau_role.members]
        OldMemberTxtMention = ', '.join(OldMember)
        OldMemberTxtNoMention = ', '.join(OldMemberTxt)

        if supprimer==True:

            for member in OldMemberID:

                await ctx.guild.get_member(member).remove_roles(ancien_role)
        
        for member in OldMemberID:

                await ctx.guild.get_member(member).add_roles(nouveau_role)

        NewMenberTxtMention = ', '.join([f"<@{m.id}>" for m in nouveau_role.members if m.id not in NewRoleMember])
        NewMenberTxt = ', '.join([m.display_name for m in nouveau_role.members if m.id not in NewRoleMember])
        if supprimer == True:

            await ctx.edit_original_response(content=(f'Role supprimer à : {OldMemberTxtMention}\n\nRole donné à : {NewMenberTxtMention}'))
            user = client.get_user(ctx.user.id)
            await user.send(content=(f'Role supprimer à : {OldMemberTxtNoMention}\n\nRole donné à : {NewMenberTxt}'))

        else:

            await ctx.edit_original_response(content=(f'Role donné à : {NewMenberTxtMention}'))
            user = client.get_user(ctx.user.id)
            await user.send(content=(f'Role donné à : {NewMenberTxt}'))
    except Exception as e:
        logging.error(f'Error in command "transfert_role": {e}', exc_info=True)
        
        await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
        return

@transfert_role.error
async def transfert_role_error(ctx, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions): 
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)



#@tree.command(name = "print_categories", description = "Affiche le nom de categorie")
#@app_commands.checks.has_permissions(administrator=True)
async def categories(ctx):
    try:
        try:
            await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
            guild = ctx.guild
            category_names = [category.name for category in guild.categories]
            user = client.get_user(ctx.user.id)
            if category_names:
                result = "Catégories du serveur : \n\n"
                for category in guild.categories:
                    name_cat = f" {category.name.replace(' =','').replace('= ','').replace('=','').replace('  ',' ')} "
                    while len(name_cat) <= 27:
                        name_cat = f"={name_cat}="

                    result+= (name_cat) + "\n"
                await user.send(content=result)
            else:
                await ctx.edit_original_response(content="Le serveur ne possède pas de catégories.")
                return
            
        except Exception as e:
            logging.error(f'Error in command "erreur_commande": {e}', exc_info=True)
            
            await ctx.edit_original_response(content="Une erreur s'est produite lors de l'exécution de la commande.")
            return
    except discord.app_commands.errors.MissingPermissions:
        await ctx.response.send_message(content="Tu n'as pas la permission d'effectuer cette commande !", ephemeral=True)
        return
    



async def all_agenda_week_print():
    await client.wait_until_ready()

    for guild in client.guilds:
        members_with_role = []

        for member in guild.members:
            if discord.utils.get(member.roles, name="Apprenant IPI") and not discord.utils.get(member.roles, name="Admin Serveur"):
                members_with_role.append(member)
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel) and channel.name == 'agenda':
                await recur_agenda(channel, members_with_role)



async def recur_agenda(channel: discord.TextChannel, members_with_role: list):
    for member in members_with_role:
        try:
            with open("login_promo.json") as jsonFile:
                LoginPromoJson = json.load(jsonFile)
                jsonFile.close()
            if (str(member.id) in LoginPromoJson):
                max_attempts = 3
                firefox_options = Options()
                firefox_options.add_argument("-private")
                firefox_options.add_argument('-headless')
                driver = webdriver.Firefox(options=firefox_options)

                driver.set_window_size(1920, 1080)

                for attempt in range(max_attempts):
                    if attempt > 0:
                        print(f"Tentative {attempt + 1}...")
                    
                    date = datetime.now().strftime("%m/%d/%Y")
                    url = f'https://ws-edt-igs.wigorservices.net/WebPsDyn.aspx?action=posEDTLMS&serverID=G&date={date}'

                    username = cryptocode.decrypt(LoginPromoJson[str(member.id)]["login"], DataJson['CRYPT'])
                    password = cryptocode.decrypt(LoginPromoJson[str(member.id)]["mdp"], DataJson['CRYPT'])

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


                    if "Server Error in '/' Application." in driver.page_source:
                        print("Erreur détectée dans le HTML. Relance du script...")
                        driver.quit()
                    else:
                        driver.save_screenshot(f"Timeable.png")
                        driver.quit()
                        break
                message_history = []
                async for msg in channel.history(limit=100):
                    message_history.append(msg)

                for msg in message_history:
                    if msg.author == client.user:
                        print(msg.content)
                        await msg.delete()
                        break 
                file = discord.File(f"Timeable.png")    
                await channel.send(file=file)
                if os.path.exists(f"Timeable.png"):
                    os.remove(f"Timeable.png")
                return
        except Exception as e:
            logging.error(f'Error in command "agenda": {e}', exc_info=True)
            
            await channel.send(content="Une erreur s'est produite lors de l'exécution de la commande.")
            return       
client.run(DataJson["DISCORD_TOKEN"])