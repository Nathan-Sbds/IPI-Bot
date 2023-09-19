import discord,re,json,urllib.request
from discord.ext import commands
from discord import app_commands

intents = discord.Intents().all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

with open("data.json") as jsonFile:
    jsonObject = json.load(jsonFile)
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


@tree.command(name = "transferer_role", description = "Transfere un role a toutes les personnes ayant un autre role")
@commands.has_permissions(administrator=True)
@app_commands.describe(ancien_role="Les personnes ayant ce role vont recevoir le nouveau", nouveau_role="Role a donner", supprimer="Faut-il supprimer le role actuel utilisé pour transferer ? (oui /non)")
async def transfert_role(ctx, ancien_role : discord.Role, nouveau_role : discord.Role,supprimer : bool):

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


@tree.command(name = "creer_categorie", description = "Créer une catégorie basique avec les channels, et permissions")
@commands.has_permissions(administrator=True)
@app_commands.describe(nom_categorie="Nom de la catégorie à créer (sans les =)", role="Role ayant acces a cette catégorie", role2="Second role ayant acces a la catégorie (optionnel)")
async def create_category(ctx, nom_categorie : str, role : discord.Role, role2 : discord.Role = None):

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


@tree.command(name = "supprimer_categorie", description = "Supprime la catégorie ainsi que les channels qu'elle contient")
@commands.has_permissions(administrator=True)
@app_commands.describe(nom_categorie="Nom de la catégorie a supprimer (sans les =)")
async def delete_category(ctx, nom_categorie : str):

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
    

@tree.command(name = "creer_channel", description = "Créer un channel dans une catégroei et lui donne les bonnes permissions !")
@commands.has_permissions(manage_channels=True)
@app_commands.describe(nom_channel="Nom du channel a créer", nom_categorie="Catégorie où créer le channel")
async def create_channel(ctx, nom_channel : str, nom_categorie : str):

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


@tree.command(name = "delete_channel", description = "Supprime un channel dans une catégorie")
@commands.has_permissions(administrator=True)
@app_commands.describe(nom_channel="Nom du channel a supprimer", nom_categorie="Catégorie dans lequel il est situé")
async def delete_channel(ctx, nom_channel : str, nom_categorie : str):

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



@tree.command(name = "transferer_categorie", description = "Transferer une catégorie à un autre rôle")
@commands.has_permissions(administrator=True)
@app_commands.describe(nouveau_nom_categorie="Nom actuel de la catégorie a transferer", ancien_nom_categorie="Nouveau nom a donner a la categorie",nouveau_role="Nouveau role pouvant avoir acces a la categorie",ancien_role="Role ayant actuellement l'acces a la categorie",nouveau_nom="Chaine de caractere servant a remplacer l'ancienne dans le nom des channels", ancien_nom="Chaine de caractere devant etre remplacer dans le nom des channels")
async def transfert_category(ctx, ancien_nom_categorie:str, nouveau_nom_categorie:str, ancien_nom:str, nouveau_nom:str, ancien_role : discord.Role, nouveau_role : discord.Role):

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

@tree.command(name = "print_categories", description = "Affiche le nom de categorie")
@commands.has_permissions(administrator=True)
async def categories(ctx):
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


client.run(jsonObject["DISCORD_TOKEN"])