import discord, re, json, urllib.request, os, logging, cryptocode, smtplib
from discord import app_commands
from datetime import datetime
from PIL import Image
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from discord.gateway import DiscordClientWebSocketResponse

# Configure logging
logging.basicConfig(
    filename="bot_errors.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Initialize Discord client and command tree
intents = discord.Intents().all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
folder_path = "Attachments"

# Load data from JSON files
with open("data.json") as jsonFile:
    DataJson = json.load(jsonFile)
    jsonFile.close()

try:
    with open("secret_santa.json", "r") as file:
        dataSecret = json.load(file)
except FileNotFoundError:
    dataSecret = {"votes": {}, "images": [], "next_image_id": 1, "result_id": 0}
    with open("secret_santa.json", "w") as file:
        json.dump(dataSecret, file)

privateCommandsList = ["ping", "clear_dm"]

def send_mail(errorBot, command):
    """
    Send an email notification when an error occurs.

    Args:
        errorBot (str): The error message.
        command (str): The command that caused the error.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = cryptocode.decrypt(DataJson["MAIL_ID"], DataJson["CRYPT"])
    smtp_password = cryptocode.decrypt(DataJson["MAIL_MDP"], DataJson["CRYPT"])

    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()
    smtp.login(smtp_username, smtp_password)

    sender_email = "IPI Bot"
    recipient_email = DataJson["SEND_TO"]
    subject = "[IPI Bot] Une erreur est survenue"
    message_text = f'Une erreur est survenue le {datetime.now().strftime("%d/%m/%Y")} à {datetime.now().strftime("%H:%M:%S")} dans la commande "{command}" : \n\n{errorBot}'

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(message_text, "plain"))
    smtp.sendmail(sender_email, recipient_email, msg.as_string())
    smtp.quit()

@client.event
async def on_ready():
    """
    Event handler for when the bot is ready.
    """
    await client.change_presence(
        status=discord.Status.online, activity=discord.Game("Gerer les choses...")
    )
    await tree.sync()

    for image_info in dataSecret["images"]:
        image_id = image_info["id"]
        view = MyView()
        client.add_view(view)

    for propositions in data["propositions"]:
        proposition_id = propositions["id"]
        view = MyViewAtelier()
        client.add_view(view)

    print(f"Logged in as {client.user.name}")
    print("Ready!")

@client.event
async def on_interaction(ctx):
    """
    Event handler for interactions.
    """
    if (
        ctx.channel.type == discord.ChannelType.private
        and ctx.data["name"] not in privateCommandsList
    ):
        await ctx.response.send_message(
            "Le bot ne prend pas en charge les messages privés.", ephemeral=True
        )

### Commandes Votes ###

@tree.command(name="vote_ajouter_image", description="Ajouter une image")
@app_commands.checks.has_permissions(administrator=True)
async def add_image(ctx, image: discord.Attachment):
    """
    Add an image for voting.

    Args:
        ctx: The context of the command.
        image (discord.Attachment): The image to be added.
    """
    await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

    with open("secret_santa.json", "r") as file:
        dataSecret = json.load(file)

    # Make sure the folder exists; if not, create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save the attachment with its original filename
    file_path = os.path.join(
        folder_path,
        f"Photo_{dataSecret['next_image_id']}.{image.filename.split('.')[-1]}",
    )
    await image.save(file_path)

    image_id = dataSecret["next_image_id"]

    # Create a vote option for the added image
    view = MyView()  # Pass the image ID to the view constructor
    client.add_view(view)
    view.timeout = None  # Set the timeout to None to make the view persistent

    embed = discord.Embed(
        title=f"Photo {image_id} :",
        description="Cliquez sur le bouton ci-dessous pour voter pour cette image.",
        color=discord.Color.red(),
    )
    embed.set_image(
        url=f"attachment://Photo_{image_id}.{image.filename.split('.')[-1]}"
    )

    message = await client.get_channel(ctx.channel_id).send(
        file=discord.File(
            os.path.join(
                folder_path, f"Photo_{image_id}.{image.filename.split('.')[-1]}"
            )
        ),
        embed=embed,
        view=view,
    )

    dataSecret["images"].append(
        {
            "id": image_id,
            "file": f"Photo_{image_id}.{image.filename.split('.')[-1]}",
            "message_id": message.id,
        }
    )

    dataSecret["next_image_id"] += 1

    # Save the data to the JSON file
    with open("secret_santa.json", "w") as file:
        json.dump(dataSecret, file)

    await result_in_time(ctx, True)
    await ctx.edit_original_response(content=f"L'image {image_id} a été ajoutée.")

@client.event
async def on_button_click(interaction: discord.Interaction, button: discord.ui.Button):
    """
    Event handler for button clicks.
    """
    if "vote_button" in button.custom_id:
        view = client.get_view(button.view.id)
        await view.button_callback(interaction, button)

@tree.command(
    name="vote_supprimer", description="Supprimer toutes les données et votes"
)
@app_commands.checks.has_permissions(administrator=True)
async def clear_all(ctx):
    """
    Clear all voting data and votes.

    Args:
        ctx: The context of the command.
    """
    global dataSecret
    await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

    for image in dataSecret["images"]:
        channel = client.get_channel(ctx.channel_id)
        message = await channel.fetch_message(image["message_id"])
        await message.delete()
    if dataSecret["result_id"] != 0:
        message = await channel.fetch_message(dataSecret["result_id"])
        await message.delete()

    dataSecret = {"votes": {}, "images": [], "next_image_id": 1, "result_id": 0}

    # Save the data to the JSON file
    with open("secret_santa.json", "w") as file:
        json.dump(dataSecret, file)

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

    await ctx.edit_original_response(content="Toutes les données ont été supprimées")

@tree.command(name="vote_resultats", description="Afficher les résultats")
@app_commands.checks.has_permissions(administrator=True)
async def show_results(ctx):
    """
    Show the voting results.

    Args:
        ctx: The context of the command.
    """
    await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

    with open("secret_santa.json", "r") as file:
        dataSecret = json.load(file)

    # Get the results
    votes = dataSecret["votes"]
    image_ids = [int(vote_id) for vote_id in votes.values()]
    image_data = [image for image in dataSecret["images"]]

    # Create an embed to display the results
    embed_detail = discord.Embed(
        title="Résultat du Vote",
        description="Voici les résultats détaillées du vote :",
        color=discord.Color.green(),
    )

    img1_vote = -1
    img1_name = ""
    img2_vote = -1
    img2_name = ""
    img3_vote = -1
    img3_name = ""

    for image in image_data:
        image_id = image["id"]
        image_filename = image["file"]
        vote_count = image_ids.count(image_id)
        if vote_count > img3_vote:
            img3_vote = vote_count
            img3_name = image_filename
            if vote_count > img2_vote:
                img3_vote, img2_vote = img2_vote, img3_vote
                img3_name, img2_name = img2_name, img3_name
                if vote_count > img1_vote:
                    img2_vote, img1_vote = img1_vote, img2_vote
                    img2_name, img1_name = img1_name, img2_name

        embed_detail.add_field(
            name=f"Photo {image_id}:",
            value=f"{vote_count} vote{'s' if vote_count > 1 else ''}",
            inline=False,
        )

    if img1_vote > 0:
        image_fond = Image.open("Img/Podium.png").convert("RGBA")
        couronne = Image.open("Img/Couronne.png").convert("RGBA")

        # Ouvrir les trois images à coller
        if img1_name != "":
            image1 = Image.open(f"Attachments/{img3_name}").convert("RGBA")
        else:
            image1 = Image.open(f"Img/Null.png").convert("RGBA")

        if img2_name != "":
            image2 = Image.open(f"Attachments/{img2_name}").convert("RGBA")
        else:
            image2 = Image.open(f"Img/Null.png").convert("RGBA")

        if img3_name != "":
            image3 = Image.open(f"Attachments/{img1_name}").convert("RGBA")
        else:
            image3 = Image.open(f"Img/Null.png").convert("RGBA")

        # Redimensionner les trois images à une largeur de 545 tout en maintenant les proportions
        largeur_souhaitee = 545
        hauteur_souhaitee1 = (largeur_souhaitee * image1.height) // image1.width
        hauteur_souhaitee2 = (largeur_souhaitee * image2.height) // image2.width
        hauteur_souhaitee3 = (largeur_souhaitee * image3.height) // image3.width

        image1 = image1.resize((largeur_souhaitee, hauteur_souhaitee1))
        image2 = image2.resize((largeur_souhaitee, hauteur_souhaitee2))
        image3 = image3.resize((largeur_souhaitee, hauteur_souhaitee3))

        # Coller les trois images sur l'image de fond aux positions spécifiées
        position1 = (333, 1979 - image1.height)
        position2 = (1699, 1867 - image2.height)
        position3 = (1009, 1587 - image3.height)
        positionc = (1337, 1587 - image3.height - 114)

        image_fond.paste(image1, position1, image1)
        image_fond.paste(image2, position2, image2)
        image_fond.paste(image3, position3, image3)
        image_fond.paste(couronne, positionc, couronne)

        image_fond.save("Img/result_podium.png")

        # Envoie l'embed avec les fichiers locaux sur le canal où la commande a été utilisée
        embed = discord.Embed(
            title="Le Podium", description="Et le grand gagant est...", color=0xFFD700
        )  # Couleur dorée

        embed.set_image(url=f"attachment://result_podium.png")

        await client.get_channel(ctx.channel_id).send(
            embed=embed, file=discord.File("Img/result_podium.png")
        )
        await client.get_channel(ctx.channel_id).send(embed=embed_detail)
        await ctx.edit_original_response(
            content=f"Les résultats ont été postés dans le channel <#{ctx.channel_id}>.",
        )
    else:
        await ctx.edit_original_response(
            content="Il n'y a pas de résultats à afficher."
        )

async def result_in_time(ctx, msg_delete: bool = False):
    """
    Display real-time voting results.

    Args:
        ctx: The context of the command.
        msg_delete (bool): Whether to delete the previous result message.
    """
    with open("secret_santa.json", "r") as file:
        dataSecret = json.load(file)

    # Get the results
    votes = dataSecret["votes"]
    image_ids = [int(vote_id) for vote_id in votes.values()]
    image_data = [image for image in dataSecret["images"]]

    # Create an embed to display the results
    embed = discord.Embed(
        title="Résultat en temps réel du Vote",
        description="Voici les résultats actuels du vote :",
        color=discord.Color.green(),
    )

    max_votes = 0
    for image in image_data:
        image_id = image["id"]
        image_filename = image["file"]
        vote_count = image_ids.count(image_id)
        if vote_count > max_votes:
            max_votes = vote_count
            image_max = image

        embed.add_field(
            name=f"Photo {image_id}:",
            value=f"{vote_count} vote{'s' if vote_count > 1 else ''}",
            inline=False,
        )

    if max_votes > 0:
        if msg_delete or dataSecret["result_id"] == 0:
            if dataSecret["result_id"] != 0:
                channel = client.get_channel(ctx.channel_id)
                message = await channel.fetch_message(dataSecret["result_id"])
                await message.delete()

            message = await client.get_channel(ctx.channel_id).send(embed=embed)

            dataSecret["result_id"] = message.id

            with open("secret_santa.json", "w") as file:
                json.dump(dataSecret, file)
        else:
            channel = client.get_channel(ctx.channel_id)
            message = await channel.fetch_message(dataSecret["result_id"])
            await message.edit(embed=embed)

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Voter", style=discord.ButtonStyle.red, custom_id=f"vote_button"
    )
    async def button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback for the vote button.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button that was clicked.
        """
        with open("secret_santa.json", "r") as file:
            dataSecret = json.load(file)

        user_id = str(interaction.user.id)

        if user_id in dataSecret["votes"]:
            del dataSecret["votes"][user_id]

        for image in dataSecret["images"]:
            if image["message_id"] == interaction.message.id:
                dataSecret["votes"][user_id] = image["id"]
                selected_image = image["id"]
                break

        # Save the data to the JSON file
        with open("secret_santa.json", "w") as file:
            json.dump(dataSecret, file)

        await interaction.response.send_message(
            f"Vous avez voté pour l'image {selected_image}.", ephemeral=True
        )

        await result_in_time(interaction)

############################ Commandes Atelier ############################

try:
    with open("participations.json", "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = {
        "max_inscription": 2,
        "max_inscrits": 14,
        "max_inscrits_promo": 4,
        "roles": [],
        "propositions": [],
        "participations": {},
        "next_proposition_id": 1,
        "result_id": 0,
        "active": False,
        "button_label": "S'inscrire à l'Atelier",
    }

    with open("participations.json", "w") as file:
        json.dump(data, file)
        file.close()

@tree.command(name="atelier_ajouter", description="Ajouter une proposition")
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_add_proposition(ctx, titre: str, description: str):
    """
    Add a workshop proposition.

    Args:
        ctx: The context of the command.
        titre (str): The title of the proposition.
        description (str): The description of the proposition.
    """
    await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

    with open("participations.json", "r") as file:
        data = json.load(file)

    proposition_id = data["next_proposition_id"]

    view = MyViewAtelier()
    client.add_view(view)
    view.timeout = None

    embed = discord.Embed(
        title=titre,
        description=description,
        color=discord.Color.red(),
    )

    message = await client.get_channel(ctx.channel_id).send(
        embed=embed,
        view=view,
    )

    data["propositions"].append(
        {
            "id": proposition_id,
            "message_id": message.id,
            "channel_id": message.channel.id,
            "titre": titre,
        }
    )

    data["next_proposition_id"] += 1

    with open("participations.json", "w") as file:
        json.dump(data, file)

    await atelier_result_in_time(ctx, True)
    await ctx.edit_original_response(content=f"La proposition {titre} a été ajoutée.")

@tree.command(
    name="atelier_ajouter_role",
    description="Ajouter un rôle a la liste des roles pouvant utiliser le module atelier",
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_add_role(
    ctx,
    role1: discord.Role,
    role2: discord.Role = None,
    role3: discord.Role = None,
    role4: discord.Role = None,
    role5: discord.Role = None,
    role6: discord.Role = None,
    role7: discord.Role = None,
    role8: discord.Role = None,
    role9: discord.Role = None,
    role10: discord.Role = None,
):
    """
    Add roles to the list of roles that can use the workshop module.

    Args:
        ctx: The context of the command.
        role1 (discord.Role): The first role to add.
        role2 (discord.Role, optional): The second role to add.
        role3 (discord.Role, optional): The third role to add.
        role4 (discord.Role, optional): The fourth role to add.
        role5 (discord.Role, optional): The fifth role to add.
        role6 (discord.Role, optional): The sixth role to add.
        role7 (discord.Role, optional): The seventh role to add.
        role8 (discord.Role, optional): The eighth role to add.
        role9 (discord.Role, optional): The ninth role to add.
        role10 (discord.Role, optional): The tenth role to add.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
    members = []
    data["roles"].append(role1.id)
    for member in role1.members:
        members.append(member)
    multiple = False
    if role2 is not None:
        data["roles"].append(role2.id)
        multiple = True
        for member in role2.members:
            members.append(member)
    if role3 is not None:
        data["roles"].append(role3.id)
        multiple = True
        for member in role3.members:
            members.append(member)
    if role4 is not None:
        data["roles"].append(role4.id)
        multiple = True
        for member in role4.members:
            members.append(member)
    if role5 is not None:
        data["roles"].append(role5.id)
        multiple = True
        for member in role5.members:
            members.append(member)
    if role6 is not None:
        data["roles"].append(role6.id)
        multiple = True
        for member in role6.members:
            members.append(member)
    if role7 is not None:
        data["roles"].append(role7.id)
        multiple = True
        for member in role7.members:
            members.append(member)
    if role8 is not None:
        data["roles"].append(role8.id)
        multiple = True
        for member in role8.members:
            members.append(member)
    if role9 is not None:
        data["roles"].append(role9.id)
        multiple = True
        for member in role9.members:
            members.append(member)
    if role10 is not None:
        data["roles"].append(role10.id)
        multiple = True
        for member in role10.members:
            members.append(member)

    non_inscrit_role = discord.utils.get(ctx.guild.roles, name="Non Inscrit")

    if not non_inscrit_role:
        non_inscrit_role = await ctx.guild.create_role(
            name="Non Inscrit", color=discord.Color(0xFFFF00)
        )
    for member in members:
        if non_inscrit_role not in member.roles:
            await member.add_roles(non_inscrit_role)

    with open("participations.json", "w") as file:
        json.dump(data, file)

    await ctx.edit_original_response(
        content=f"Le{'s' if multiple else ''} rôle{'s' if multiple else ''} {role1.name}{f', {role2.name}' if role2 is not None else ''}{f', {role3.name}' if role3 is not None else ''}{f', {role4.name}' if role4 is not None else ''}{f', {role5.name}' if role5 is not None else ''}{f', {role6.name}' if role6 is not None else ''}{f', {role7.name}' if role7 is not None else ''}{f', {role8.name}' if role8 is not None else ''}{f', {role9.name}' if role9 is not None else ''}{f', {role10.name}' if role10 is not None else ''} {'ont' if multiple else 'a'} été ajouté{'s' if multiple else ''} aux rôles autorisés à participer",
    )


@tree.command(
    name="atelier_retirer_role",
    description="Supprimer un/des rôle ayant la possibilité d'utiliser le module atelier",
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_remove_role(
    ctx,
    role1: discord.Role,
    role2: discord.Role = None,
    role3: discord.Role = None,
    role4: discord.Role = None,
    role5: discord.Role = None,
    role6: discord.Role = None,
    role7: discord.Role = None,
    role8: discord.Role = None,
    role9: discord.Role = None,
    role10: discord.Role = None,
):
    """
    Remove roles from the list of roles that can use the workshop module.

    Args:
        ctx: The context of the command.
        role1 (discord.Role): The first role to remove.
        role2 (discord.Role, optional): The second role to remove.
        role3 (discord.Role, optional): The third role to remove.
        role4 (discord.Role, optional): The fourth role to remove.
        role5 (discord.Role, optional): The fifth role to remove.
        role6 (discord.Role, optional): The sixth role to remove.
        role7 (discord.Role, optional): The seventh role to remove.
        role8 (discord.Role, optional): The eighth role to remove.
        role9 (discord.Role, optional): The ninth role to remove.
        role10 (discord.Role, optional): The tenth role to remove.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
    members = []
    data["roles"].remove(role1.id)
    multiple = False
    for member in role1.members:
        members.append(member)

    if role2 is not None:
        data["roles"].remove(role2.id)
        multiple = True
        for member in role2.members:
            members.append(member)
    if role3 is not None:
        data["roles"].remove(role3.id)
        multiple = True
        for member in role3.members:
            members.append(member)
    if role4 is not None:
        data["roles"].remove(role4.id)
        multiple = True
        for member in role4.members:
            members.append(member)
    if role5 is not None:
        data["roles"].remove(role5.id)
        multiple = True
        for member in role5.members:
            members.append(member)
    if role6 is not None:
        data["roles"].remove(role6.id)
        multiple = True
        for member in role6.members:
            members.append(member)
    if role7 is not None:
        data["roles"].remove(role7.id)
        multiple = True
        for member in role7.members:
            members.append(member)
    if role8 is not None:
        data["roles"].remove(role8.id)
        multiple = True
        for member in role8.members:
            members.append(member)
    if role9 is not None:
        data["roles"].remove(role9.id)
        multiple = True
        for member in role9.members:
            members.append(member)
    if role10 is not None:
        data["roles"].remove(role10.id)
        multiple = True
        for member in role10.members:
            members.append(member)

    non_inscrit_role = discord.utils.get(ctx.guild.roles, name="Non Inscrit")

    if non_inscrit_role:
        for member in members:
            if non_inscrit_role in member.roles:
                await member.remove_roles(non_inscrit_role)

    with open("participations.json", "w") as file:
        json.dump(data, file)

    await ctx.edit_original_response(
        content=f"Le{'s' if multiple else ''} rôle{'s' if multiple else ''} {role1.name}{f', {role2.name}' if role2 is not None else ''}{f', {role3.name}' if role3 is not None else ''}{f', {role4.name}' if role4 is not None else ''}{f', {role5.name}' if role5 is not None else ''}{f', {role6.name}' if role6 is not None else ''}{f', {role7.name}' if role7 is not None else ''}{f', {role8.name}' if role8 is not None else ''}{f', {role9.name}' if role9 is not None else ''}{f', {role10.name}' if role10 is not None else ''} ont été supprimés des rôles autorisés à participer",
    )


@tree.command(
    name="atelier_liste_role",
    description="Lister les rôles autorisés à utiliser le module atelier",
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_list_role(ctx):
    """
    List the roles authorized to use the workshop module.

    Args:
        ctx: The context of the command.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    roles_id = data["roles"]
    roles = []
    for role_id in roles_id:
        roles.append(ctx.guild.get_role(role_id))

    roles_list = ""

    for role in roles:
        roles_list += f"- {role.name}\n"

    await ctx.response.send_message(
        content=f"Les rôles autorisés à participer sont :\n{roles_list}", ephemeral=True
    )


@tree.command(
    name="atelier_max_inscrits_promo",
    description="Modifier le nombre maximum d'inscrits par promo",
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_modify_max_inscrits_promo(ctx, max_inscrits: int):
    """
    Modify the maximum number of participants per promotion.

    Args:
        ctx: The context of the command.
        max_inscrits (int): The maximum number of participants per promotion.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    for proposition in data["propositions"]:
        if len(atelier_get_role_count(ctx, proposition["id"])) > max_inscrits:
            await ctx.response.send_message(
                content=f"Le nombre maximum d'inscrits ne peut pas être inférieur au nombre d'inscrits actuel",
                ephemeral=True,
            )
            return

    data["max_inscrits_promo"] = max_inscrits

    with open("participations.json", "w") as file:
        json.dump(data, file)

    await ctx.response.send_message(
        content=f"Le nombre maximum d'inscrits par promo est maintenant de {max_inscrits}",
        ephemeral=True,
    )


@tree.command(
    name="atelier_max_inscrits", description="Modifier le nombre maximum d'inscrits"
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_modify_max_inscrits(ctx, max_inscrits: int):
    """
    Modify the maximum number of participants.

    Args:
        ctx: The context of the command.
        max_inscrits (int): The maximum number of participants.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    participations = data["participations"]
    participation_ids = [
        participation_id
        for participation_ids_list in participations.values()
        if participation_ids_list is not None
        for participation_id in participation_ids_list
    ]

    for proposition in data["propositions"]:
        if participation_ids.count(proposition["id"]) > max_inscrits:
            await ctx.response.send_message(
                content=f"Le nombre maximum d'inscrits ne peut pas être inférieur au nombre d'inscrits actuel",
                ephemeral=True,
            )
            return

    data["max_inscrits"] = max_inscrits

    with open("participations.json", "w") as file:
        json.dump(data, file)

    await ctx.response.send_message(
        content=f"Le nombre maximum d'inscrits par atelier est maintenant de {max_inscrits}",
        ephemeral=True,
    )


@tree.command(
    name="atelier_max_inscription",
    description="Modifier le nombre maximum d'ateliers auxquels il est possible de participer",
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_modify_max_inscription(ctx, max_inscription: int):
    """
    Modify the maximum number of workshops a user can participate in.

    Args:
        ctx: The context of the command.
        max_inscription (int): The maximum number of workshops a user can participate in.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    if max_inscription < 1:
        await ctx.response.send_message(
            content="Le nombre maximum d'ateliers auxquels il est possible de participer doit être d'au moins 1.",
            ephemeral=True,
        )
        return

    for user_id, participations_list in data["participations"].items():
        if (
            participations_list is not None
            and len(participations_list) > max_inscription
        ):
            await ctx.response.send_message(
                content=f"Le nombre maximum d'ateliers auxquels il est possible de participer ne peut pas être inférieur au nombre d'ateliers auxquels {ctx.guild.get_member(int(user_id)).display_name} est déjà inscrit(e).",
                ephemeral=True,
            )
            return

    data["max_inscription"] = max_inscription

    with open("participations.json", "w") as file:
        json.dump(data, file)

    await ctx.response.send_message(
        content=f"Le nombre maximum d'ateliers auxquels on peut participer est maintenant de {max_inscription}.",
        ephemeral=True,
    )


@tree.command(
    name="atelier_label_bouton",
    description="Modifier le texte du bouton (ne doit pas depasser 80 caractères)",
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_modify_button_label(ctx, button_label: str):
    """
    Modify the button label.

    Args:
        ctx: The context of the command.
        button_label (str): The new button label.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)
    if len(button_label) > 80:
        await ctx.response.send_message(
            content="Le texte du bouton ne peut pas dépasser 80 caractères.",
            ephemeral=True,
        )
        return

    data["button_label"] = button_label

    with open("participations.json", "w") as file:
        json.dump(data, file)

    for view in client.persistent_views:
        if isinstance(view, MyViewAtelier):
            view.children[0].label = data["button_label"]

    for propositions in data["propositions"]:
        proposition_id = propositions["id"]
        view = MyViewAtelier()
        view.children[0].label = data["button_label"]
        message_id = int(propositions["message_id"])
        channel_id = int(propositions["channel_id"])
        channel = client.get_channel(channel_id)

        if channel:
            message = await channel.fetch_message(message_id)
            await message.edit(
                view=view, content=message.content, embed=message.embeds[0]
            )
            client.add_view(view, message_id=int(propositions["message_id"]))

    await ctx.response.send_message(
        content=f"Le texte du bouton est maintenant {button_label}", ephemeral=True
    )


@tree.command(
    name="atelier_config",
    description="Afficher les informations de configuration du module atelier",
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_show_config(ctx):
    """
    Show the configuration information of the workshop module.

    Args:
        ctx: The context of the command.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    roles_id = data["roles"]
    roles = []
    for role_id in roles_id:
        roles.append(ctx.guild.get_role(role_id))

    roles_list = ""

    for role in roles:
        roles_list += f"- {role.name}\n"

    atelier_list = ""
    for proposition in data["propositions"]:
        atelier_list += f"- {proposition['titre']}\n"

    if data["active"]:
        active = "Inscriptions ouvertes"
    else:
        active = "Inscriptions fermées"

    embed = discord.Embed(
        title="__Configuration__",
        description="Voici les informations de configuration :",
        color=discord.Color.green(),
    )

    embed.add_field(
        name=f"Statut des inscriptions :",
        value=f"{active}",
        inline=False,
    )

    embed.add_field(
        name=f"Libellé du bouton :",
        value=f"{data['button_label']}",
        inline=False,
    )

    embed.add_field(
        name=f"Nombre maximum d'inscrits par atelier :",
        value=f"{data['max_inscrits']}",
        inline=False,
    )

    embed.add_field(
        name=f"Nombre maximum d'inscrits par promo :",
        value=f"{data['max_inscrits_promo']}",
        inline=False,
    )

    embed.add_field(
        name="Nombre d'inscription possible par utilisateur",
        value=f"{data['max_inscription']}",
        inline=False,
    )

    embed.add_field(
        name=f"Rôles autorisés à participer :",
        value=f"{roles_list}",
        inline=False,
    )

    embed.add_field(
        name=f"Ateliers :",
        value=f"{atelier_list}",
        inline=False,
    )

    await ctx.response.send_message(embed=embed, ephemeral=True)


@client.event
async def on_button_click(interaction: discord.Interaction, button: discord.ui.Button):
    """
    Event handler for button clicks.
    """
    if "button" in button.custom_id:
        view = client.get_view(button.view.id)
        await view.button_callback(interaction, button)


@tree.command(
    name="atelier_supprimer",
    description="Supprimer toutes les données et inscriptions du module atelier",
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_clear_all(ctx):
    """
    Clear all data and registrations of the workshop module.

    Args:
        ctx: The context of the command.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

    channel = client.get_channel(ctx.channel_id)
    for propositions in data["propositions"]:
        try:
            message = await channel.fetch_message(propositions["message_id"])
            await message.delete()
        except discord.errors.NotFound:
            pass
    if data["result_id"] != 0:
        message = await channel.fetch_message(data["result_id"])
        await message.delete()

    data = {
        "max_inscription": 2,
        "max_inscrits": 14,
        "max_inscrits_promo": 4,
        "roles": [],
        "propositions": [],
        "participations": {},
        "next_proposition_id": 1,
        "result_id": 0,
        "active": False,
        "button_label": "S'inscrire à l'Atelier",
    }

    with open("participations.json", "w") as file:
        json.dump(data, file)

    await ctx.edit_original_response(content="Toutes les données ont été supprimées")


@tree.command(
    name="atelier_inscriptions", description="Afficher les inscrits des ateliers"
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_show_inscrits(ctx):
    """
    Show the participants of the workshops.

    Args:
        ctx: The context of the command.
    """
    await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

    with open("participations.json", "r") as file:
        data = json.load(file)

    for proposition in data["propositions"]:
        embed = discord.Embed(
            title="Inscriptions",
            description="Voici les inscrits aux ateliers :",
            color=discord.Color.green(),
        )
        proposition_id = proposition["id"]
        proposition_titre = proposition["titre"]
        proposition_voters = ""
        for voter in data["participations"]:
            if proposition_id in data["participations"][voter]:
                member = ctx.guild.get_member(int(voter))
                if member:
                    proposition_voters += f"- {member.display_name}\n"
                else:
                    print(voter)
        embed.add_field(
            name=f"Atelier : {proposition_titre}",
            value=f"{proposition_voters}",
            inline=False,
        )
        user = client.get_user(ctx.user.id)
        await user.send(embed=embed)
    await ctx.edit_original_response(
        content="Les inscrits ont été envoyés en message privé"
    )


@tree.command(
    name="atelier_non_inscriptions",
    description="Afficher les personnes ne s'etant pas inscrits",
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_non_inscrit(ctx):
    """
    Show the people who have not registered.

    Args:
        ctx: The context of the command.
    """
    await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

    with open("participations.json", "r") as file:
        data = json.load(file)

    roles_id = data["roles"]
    roles = []
    for role_id in roles_id:
        roles.append(ctx.guild.get_role(role_id))

    for role in roles:
        non_participants = []
        for member in role.members:
            member_id = str(member.id)
            if member_id not in data["participations"]:
                non_participants.append({f"{member_id}": 0})

            elif len(data["participations"][member_id]) < data["max_inscription"]:
                non_participants.append(
                    {f"{member_id}": len(data["participations"][member_id])}
                )

        non_participant_text = f"Les personnes n'ayant pas participer suffisamment de fois de la promo {role.name} sont : \nNom de la personne (Nombre d'atelier auquel il/elle est inscrit)\n\n"
        for member_data in non_participants:
            for member_id, participation_time in member_data.items():
                non_participant_text += f"- **{ctx.guild.get_member(int(member_id)).display_name}** ({participation_time})\n"

        if len(non_participant_text) != 0:
            user = client.get_user(ctx.user.id)
            await user.send(content=non_participant_text)
        else:
            await ctx.edit_original_response(
                content=f"Toutes les personnes de la promo {role.name} ont votés {data['max_inscription']} fois"
            )

    await ctx.edit_original_response(
        content="Les personnes n'ayant pas participer suffisamment de fois ont été envoyés en message privé"
    )


async def atelier_result_in_time(interaction, msg_delete: bool = False):
    """
    Display real-time workshop results.

    Args:
        interaction: The interaction object.
        msg_delete (bool): Whether to delete the previous result message.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    participations = data["participations"]
    participation_ids = [
        participation_id
        for participation_ids_list in participations.values()
        if participation_ids_list is not None
        for participation_id in participation_ids_list
    ]

    propositions_data = data["propositions"]

    embed = discord.Embed(
        title="Ateliers",
        description="Voici les participants actuellement enregistrées :",
        color=discord.Color.green(),
    )

    max_votes = 0
    for proposition in propositions_data:
        proposition_id = proposition["id"]
        proposition_titre = proposition["titre"]
        vote_count = participation_ids.count(proposition_id)
        if vote_count > max_votes:
            max_votes = vote_count
            proposition_max = proposition

        embed.add_field(
            name=f"Atelier : {proposition_titre}",
            value=f"- {vote_count} participant{'s' if vote_count > 1 else ''}{' - Places non disponibles' if vote_count >= data['max_inscrits'] else ''}",
            inline=False,
        )

    if max_votes > 0:
        if msg_delete or data["result_id"] == 0:
            if data["result_id"] != 0:
                channel = interaction.channel
                message = await channel.fetch_message(data["result_id"])
                await message.delete()

            message = await interaction.channel.send(embed=embed)

            data["result_id"] = message.id

            with open("participations.json", "w") as file:
                json.dump(data, file)
        else:
            channel = interaction.channel
            message = await channel.fetch_message(data["result_id"])
            await message.edit(embed=embed)


@tree.command(
    name="atelier_activer", description="Active les inscriptions pour les ateliers"
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def activate_participation(ctx):
    """
    Activate registrations for workshops.

    Args:
        ctx: The context of the command.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    data["active"] = True

    with open("participations.json", "w") as file:
        json.dump(data, file)

    await ctx.response.send_message(
        content="Les inscriptions sont maintenant ouvertes", ephemeral=True
    )


@tree.command(
    name="atelier_desactiver",
    description="Desactive les inscriptions pour les ateliers",
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def deactivate_participation(ctx):
    """
    Deactivate registrations for workshops.

    Args:
        ctx: The context of the command.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    data["active"] = False

    with open("participations.json", "w") as file:
        json.dump(data, file)

    await ctx.response.send_message(
        content="Les inscriptions sont désormais fermées", ephemeral=True
    )


@tree.command(
    name="atelier_relance", description="Relance les personnes n'etant pas inscrits"
)
@app_commands.checks.has_any_role(
    "Team Pedago IPI",
    "Team Entreprise IPI",
    "Team Communication IPI",
    "Directrice IPI",
    "Admin Serveur",
)
async def atelier_relance(ctx):
    """
    Remind people who have not registered.

    Args:
        ctx: The context of the command.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    channel = client.get_channel(ctx.channel_id)
    role = discord.utils.get(ctx.guild.roles, name="Non Inscrit")

    if role:
        await channel.send(
            content=f"{role.mention} Vous n'etes pas encore inscrits à {data['max_inscription']} atelier{'s' if data['max_inscription'] > 1 else ''}, n'oubliez pas de vous inscrire !"
        )
        await ctx.response.send_message(
            content="Les personnes n'etant pas inscrites ont été relancées",
            ephemeral=True,
        )
    else:
        await ctx.response.send_message(
            content="Une erreur s'est produite", ephemeral=True
        )


def atelier_get_role_count(ctx: discord.Interaction, proposition_id: int):
    """
    Get the count of roles for a proposition.

    Args:
        ctx (discord.Interaction): The interaction object.
        proposition_id (int): The ID of the proposition.

    Returns:
        dict: A dictionary with role IDs as keys and counts as values.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    roles_id = data["roles"]
    roles = []
    for role_id in roles_id:
        roles.append(ctx.guild.get_role(role_id))

    role_counter = {}
    for role in roles:
        for member in role.members:
            member_id = str(member.id)
            if str(member.id) in data["participations"]:
                if proposition_id in data["participations"][str(member.id)]:
                    if role.id not in role_counter:
                        role_counter[role.id] = 0
                    role_counter[role.id] += 1

    return role_counter


def atelier_get_participation_count(member_id: int):
    """
    Get the count of participations for a member.

    Args:
        member_id (int): The ID of the member.

    Returns:
        int: The count of participations.
    """
    with open("participations.json", "r") as file:
        data = json.load(file)

    participations = data["participations"]
    participation_ids = [
        participation_id
        for participation_ids_list in participations.values()
        if participation_ids_list is not None
        for participation_id in participation_ids_list
    ]
    return participation_ids.count(member_id)


class MyViewAtelier(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label=data["button_label"], style=discord.ButtonStyle.red, custom_id="button"
    )
    async def button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback for the workshop button.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button that was clicked.
        """
        with open("participations.json", "r") as file:
            data = json.load(file)

        if data["active"]:
            user_id = str(interaction.user.id)
            user_participations = data["participations"].get(user_id, [])

            if not isinstance(user_participations, list):
                user_participations = []

            if len(user_participations) < data["max_inscription"]:
                for proposition in data["propositions"]:
                    if proposition["message_id"] == interaction.message.id:
                        if proposition["id"] not in user_participations:
                            for role in interaction.user.roles:
                                if role.id in data["roles"]:
                                    if (
                                        atelier_get_participation_count(
                                            proposition["id"]
                                        )
                                        < data["max_inscrits"]
                                    ):
                                        for role_member in atelier_get_role_count(
                                            interaction, proposition["id"]
                                        ):
                                            if (
                                                atelier_get_role_count(
                                                    interaction, proposition["id"]
                                                )[role_member]
                                                >= data["max_inscrits_promo"]
                                                and interaction.user.id == role_member
                                            ):
                                                await interaction.response.send_message(
                                                    f"Le nombre maximum d'inscrits de votre promo a été atteint.",
                                                    ephemeral=True,
                                                )
                                                return

                                        confirmview = MyViewAtelierConfirm(
                                            interaction, interaction.user
                                        )
                                        client.add_view(confirmview)

                                        await interaction.response.send_message(
                                            f"Souhaitez-vous valider votre inscription à l'atelier {proposition['titre']} ? Vous ne pourrez pas vous désinscrire après. (https://discord.com/channels/{interaction.guild.id}/{interaction.channel_id}/{interaction.message.id})",
                                            view=confirmview,
                                            ephemeral=True,
                                        )

                                        return

                                    else:
                                        await interaction.response.send_message(
                                            "Le nombre d'inscrit autorisé a été atteint.",
                                            ephemeral=True,
                                        )
                                        return
                            await interaction.response.send_message(
                                "Vos rôles ne vous permettent pas de vous inscrire à cet atelier.",
                                ephemeral=True,
                            )

                        else:
                            await interaction.response.send_message(
                                "Vous avez déjà voté pour cette proposition.",
                                ephemeral=True,
                            )
                            return

                with open("participations.json", "w") as file:
                    json.dump(data, file)

                await atelier_result_in_time(interaction)
            else:
                await interaction.response.send_message(
                    f"Vous avez déjà voté pour {data['max_inscription']} proposition{'s' if int(data['max_inscription'])>1 else ''}. Vous ne pouvez pas voter davantage.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                "L'inscription n'est pas encore ouverte, mais vous pouvez prendre connaissance des ateliers proposés. Réessayez un peu plus tard.",
                ephemeral=True,
            )


class MyViewAtelierConfirm(discord.ui.View):
    def __init__(self, interactionMaster: discord.Interaction, author):
        super().__init__(timeout=None)
        self.interactionMaster = interactionMaster
        self.author = author

    proposition_id = None

    @discord.ui.button(
        label="Oui", style=discord.ButtonStyle.green, custom_id="confirm"
    )
    async def confirm_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback for the confirm button.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button that was clicked.
        """
        if interaction.user.id == self.author.id:
            user_id = str(interaction.user.id)

            with open("participations.json", "r") as file:
                data = json.load(file)

            if data["active"]:
                message_id = int(
                    interaction.message.content.split("https://discord.com/channels/")[
                        1
                    ].split("/")[2][:-1]
                )

                for proposition in data["propositions"]:
                    if proposition["message_id"] == message_id:
                        proposition_id = proposition["id"]
                if user_id not in data["participations"]:
                    data["participations"][user_id] = []

                if proposition_id not in data["participations"].get(user_id, []):
                    data["participations"][user_id].append(proposition_id)

                    with open("participations.json", "w") as file:
                        json.dump(data, file)

                    if len(data["participations"][user_id]) >= int(
                        data["max_inscription"]
                    ):
                        non_inscrit_role = discord.utils.get(
                            interaction.guild.roles, name="Non Inscrit"
                        )

                        if non_inscrit_role:
                            member = interaction.guild.get_member(int(user_id))
                            if non_inscrit_role in member.roles:
                                await member.remove_roles(non_inscrit_role)

                    if (
                        data["max_inscription"] - len(data["participations"][user_id])
                        == 0
                    ):
                        for proposition in data["propositions"]:
                            if proposition["id"] == proposition_id:
                                nb_atelier_restant = data["max_inscription"] - len(
                                    data["participations"][user_id]
                                )
                                await interaction.response.edit_message(
                                    content=f"Vous avez confirmé votre inscription à l'atelier {proposition['titre']}.\nVous ne pouvez pas vous inscrire à un autre atelier. Merci de votre inscription.",
                                    view=None,
                                )
                                await atelier_result_in_time(interaction)
                                return

                    else:
                        for proposition in data["propositions"]:
                            if proposition["id"] == proposition_id:
                                nb_atelier_restant = data["max_inscription"] - len(
                                    data["participations"][user_id]
                                )
                                await interaction.response.edit_message(
                                    content=f"Vous avez confirmé votre inscription à l'atelier {proposition['titre']}.\nVous pouvez vous inscrire à {nb_atelier_restant} autre{'s' if nb_atelier_restant > 1 else ''} atelier{'s' if nb_atelier_restant > 1 else ''}.",
                                    view=None,
                                )
                                await atelier_result_in_time(interaction)
                else:
                    await interaction.response.send_message(
                        "Vous avez déjà voté pour cette proposition.", ephemeral=True
                    )

    @discord.ui.button(label="Non", style=discord.ButtonStyle.red, custom_id="cancel")
    async def cancel_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback for the cancel button.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button that was clicked.
        """
        await interaction.response.edit_message(
            content="Votre inscription a été annulée.", view=None
        )


@tree.command(name="ping", description="Donne la latence du bot !")
async def ping(ctx):
    """
    Get the bot's latency.

    Args:
        ctx: The context of the command.
    """
    latency = round(client.latency * 1000)
    await ctx.response.send_message(
        content=f"Pong! Latence: {latency}ms", ephemeral=True
    )


@tree.command(
    name="assigner_role",
    description="Donne le role ciblé a toutes les personnes dans le fichier .csv",
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    fichier="Fichier contenant les nom et prenom dans deux colonnes séparées",
    supprimer="Faut-il supprimer les personnes ayant le role actuellement ?",
    role="Role a donner aux personnes presentes dans le fichier",
    role2="Second rôle a donner",
    role3="Second rôle a donner",
)
async def assign_role(
    ctx,
    fichier: discord.Attachment,
    supprimer: bool,
    role: discord.Role,
    role2: discord.Role = None,
    role3: discord.Role = None,
):
    """
    Assign a role to all people in the CSV file.

    Args:
        ctx: The context of the command.
        fichier (discord.Attachment): The CSV file containing names.
        supprimer (bool): Whether to remove the role from current members.
        role (discord.Role): The role to assign.
        role2 (discord.Role, optional): The second role to assign.
        role3 (discord.Role, optional): The third role to assign.
    """
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        if supprimer == True:
            OldMemberID = [m.id for m in role.members]
            OldMember = [m.display_name for m in role.members]
            for member in OldMemberID:
                await ctx.guild.get_member(member).remove_roles(role)

            OldMemberTxt = ", ".join(OldMember)

        member_list = []

        for member in ctx.guild.members:
            member_list.append(member.display_name.replace(" ", "").lower())
            member_list.append(member.id)

        try:
            all_file = []
            for row in urllib.request.urlopen(
                urllib.request.Request(
                    url=str(fichier), headers={"User-Agent": "Mozilla/5.0"}
                )
            ):
                element_list = []
                for element in re.split(",|\n|\r|;|\ufeff", row.decode("utf-8")):
                    if element != "":
                        element_list.append(element)

                all_file.append(element_list)

            not_found = []
            for element_list in all_file:
                try:
                    element_list[1]
                    if (
                        (str(element_list[0]) + str(element_list[1]))
                        .replace(" ", "")
                        .lower()
                        in member_list
                    ) or (
                        (str(element_list[1]) + str(element_list[0]))
                        .replace(" ", "")
                        .lower()
                        in member_list
                    ):
                        try:
                            await ctx.guild.get_member(
                                member_list[
                                    member_list.index(
                                        (str(element_list[0]) + str(element_list[1]))
                                        .replace(" ", "")
                                        .lower()
                                    )
                                    + 1
                                ]
                            ).add_roles(role)
                            if role2 != None:
                                await ctx.guild.get_member(
                                    member_list[
                                        member_list.index(
                                            (
                                                str(element_list[0])
                                                + str(element_list[1])
                                            )
                                            .replace(" ", "")
                                            .lower()
                                        )
                                        + 1
                                    ]
                                ).add_roles(role2)
                            if role3 != None:
                                await ctx.guild.get_member(
                                    member_list[
                                        member_list.index(
                                            (
                                                str(element_list[0])
                                                + str(element_list[1])
                                            )
                                            .replace(" ", "")
                                            .lower()
                                        )
                                        + 1
                                    ]
                                ).add_roles(role3)

                        except:
                            await ctx.guild.get_member(
                                member_list[
                                    member_list.index(
                                        (str(element_list[1]) + str(element_list[0]))
                                        .replace(" ", "")
                                        .lower()
                                    )
                                    + 1
                                ]
                            ).add_roles(role)
                            if role2 != None:
                                await ctx.guild.get_member(
                                    member_list[
                                        member_list.index(
                                            (
                                                str(element_list[1])
                                                + str(element_list[0])
                                            )
                                            .replace(" ", "")
                                            .lower()
                                        )
                                        + 1
                                    ]
                                ).add_roles(role2)
                            if role3 != None:
                                await ctx.guild.get_member(
                                    member_list[
                                        member_list.index(
                                            (
                                                str(element_list[1])
                                                + str(element_list[0])
                                            )
                                            .replace(" ", "")
                                            .lower()
                                        )
                                        + 1
                                    ]
                                ).add_roles(role3)

                    else:
                        not_found.append(
                            str(element_list[0]) + " " + str(element_list[1])
                        )

                except IndexError:
                    pass

            not_found = ", ".join(not_found)
            NewMenberTxt = ", ".join([f"<@{m.id}>" for m in role.members])

            too_much = False
            if len(not_found + NewMenberTxt) > 1900:
                too_much = True

            if supprimer == True:
                if too_much == False:
                    await ctx.edit_original_response(
                        content=(
                            f"Role supprimé à : {OldMemberTxt}\n\nRole donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                        )
                    )
                    user = client.get_user(ctx.user.id)
                    await user.send(
                        content=(
                            f"Role supprimé à : {OldMemberTxt}\n\nRole donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                        )
                    )
                else:
                    user = client.get_user(ctx.user.id)
                    with open("message.txt", "w", encoding="utf-8") as file:
                        file.write(
                            f"Role supprimé à : {OldMemberTxt}\n\nRole donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                        )
                    await user.send(file=discord.File("message.txt"))
            else:
                if too_much == False:
                    await ctx.edit_original_response(
                        content=(
                            f"Role donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                        )
                    )
                    user = client.get_user(ctx.user.id)
                    await ctx.edit_original_response(
                        content=(
                            f"Role donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                        )
                    )
                else:
                    user = client.get_user(ctx.user.id)
                    with open("message.txt", "w", encoding="utf-8") as file:
                        file.write(
                            f"Role donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                        )
                    await user.send(file=discord.File("message.txt"))

        except Exception as e:
            send_mail(e, "assign_role")
            print(e)
            await ctx.edit_original_response(content=("Fichier illisible (.csv)"))
    except Exception as e:
        logging.error(f'Error in command "assign_role": {e}', exc_info=True)
        send_mail(e, "assign_role")
        await ctx.edit_original_response(
            content="Une erreur s'est produite lors de l'exécution de la commande."
        )
        return


@tree.command(
    name="clear_dm",
    description="Supprime les messages envoyés par le bot en message privé. Utilisable en message privé uniquement.",
)
async def clear_messages(ctx):
    """
    Clear messages sent by the bot in private messages.

    Args:
        ctx: The context of the command.
    """
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.response.send_message(
            content="Cette commande n'est disponible qu'en messages privés.",
            ephemeral=True,
        )
    else:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
        async for msg in ctx.channel.history(limit=None):
            if msg.author == client.user:
                await msg.delete()
        await ctx.edit_original_response(content="Et voila !")


@tree.command(
    name="creer_categorie",
    description="Créer une catégorie basique avec les channels, et permissions",
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    nom_categorie="Nom de la catégorie à créer (sans les =)",
    role="Role ayant acces a cette catégorie",
    role2="Second role ayant acces a la catégorie (optionnel)",
)
async def create_category(
    ctx, nom_categorie: str, role: discord.Role, role2: discord.Role = None
):
    """
    Create a basic category with channels and permissions.

    Args:
        ctx: The context of the command.
        nom_categorie (str): The name of the category to create.
        role (discord.Role): The role that will have access to the category.
        role2 (discord.Role, optional): The second role that will have access to the category.
    """
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
            await ctx.edit_original_response(
                content=(
                    f"Il existe {len(categories_with_name)} catégories avec le nom {name_cat}. Merci de bien vouloir corriger cela !"
                )
            )

        else:
            nom_categorie = nom_categorie.replace(" ", "-")
            await server.create_category(name=name_cat.upper())

            category_object = discord.utils.get(
                ctx.guild.categories, name=name_cat.upper()
            )
            await category_object.set_permissions(
                target=role,
                read_messages=True,
                send_messages=True,
                connect=True,
                speak=True,
            )

            if role2 != None:
                await category_object.set_permissions(
                    target=role2,
                    read_messages=True,
                    send_messages=True,
                    connect=True,
                    speak=True,
                )

            await category_object.set_permissions(
                ctx.guild.default_role, read_messages=False, connect=False
            )

            pedago = discord.utils.get(ctx.guild.roles, name="Team Pedago IPI")
            communication = discord.utils.get(
                ctx.guild.roles, name="Team Communication IPI"
            )
            entreprise = discord.utils.get(ctx.guild.roles, name="Team Entreprise IPI")
            directrice = discord.utils.get(ctx.guild.roles, name="Directrice IPI")

            general = await server.create_text_channel(
                name="général-" + nom_categorie.lower(), category=category_object
            )
            await discord.utils.get(
                ctx.guild.channels, name="général-" + nom_categorie.lower()
            ).set_permissions(
                target=pedago,
                read_messages=True,
                send_messages=True,
                connect=True,
                speak=True,
            )
            await discord.utils.get(
                ctx.guild.channels, name="général-" + nom_categorie.lower()
            ).set_permissions(
                target=communication,
                read_messages=True,
                send_messages=True,
                connect=True,
                speak=True,
            )
            await discord.utils.get(
                ctx.guild.channels, name="général-" + nom_categorie.lower()
            ).set_permissions(
                target=entreprise,
                read_messages=True,
                send_messages=True,
                connect=True,
                speak=True,
            )
            await discord.utils.get(
                ctx.guild.channels, name="général-" + nom_categorie.lower()
            ).set_permissions(
                target=directrice,
                read_messages=True,
                send_messages=True,
                connect=True,
                speak=True,
            )

            await general.clone(name="docs-" + nom_categorie.lower())

            await server.create_text_channel(
                name="pédago-" + nom_categorie.lower(), category=category_object
            )
            await discord.utils.get(
                ctx.guild.channels, name="pédago-" + nom_categorie.lower()
            ).set_permissions(
                target=pedago,
                read_messages=True,
                send_messages=True,
                connect=True,
                speak=True,
            )

            await server.create_text_channel(name="only-you", category=category_object)
            await server.create_voice_channel(
                name="général-vocal", category=category_object
            )
            if role2 == None:
                await ctx.edit_original_response(
                    content=(f"Catégorie {name_cat.upper()} créée pour {role} !"),
                )

            else:
                await ctx.edit_original_response(
                    content=(
                        f"Catégorie {name_cat.upper()} créee pour {role} et {role2} !"
                    )
                )
    except Exception as e:
        logging.error(f'Error in command "create_category": {e}', exc_info=True)
        send_mail(e, "create_category")
        await ctx.edit_original_response(
            content="Une erreur s'est produite lors de l'exécution de la commande."
        )
        return

class CategorySelectUniqueChannel(discord.ui.View):
    def __init__(self, categories_select, ctx, type_channel, name):
        super().__init__()
        self.add_item(CategoryDropdownUniqueChannel(categories_select, ctx, type_channel, name))

class CategoryDropdownUniqueChannel(discord.ui.Select):
    def __init__(self, categories_select, ctx, type_channel, name):
        options = [
            discord.SelectOption(label=category.name.replace("=",""), value=category.name) for category in categories_select
        ]
        self.ctx = ctx
        self.type_channel = type_channel
        self.name = name
        super().__init__(placeholder="Choisissez une catégorie...", options=options)


    async def callback(self, interaction: discord.Interaction):
        category_object = discord.utils.get(
                self.ctx.guild.categories, name=self.values[0]
            )
        try:
            self.ctx.edit_original_response(content="J'y travaille...")

            server = self.ctx.guild

            if self.type_channel == 0:
                await server.create_voice_channel(
                    name=self.name.lower(), category=category_object
                )
            else:
                await server.create_text_channel(
                    name=self.name.lower(), category=category_object
                )

            pedago = discord.utils.get(self.ctx.guild.roles, name="Team Pedago IPI")
            await discord.utils.get(
                self.ctx.guild.channels, name=self.name.lower()
            ).set_permissions(
                target=pedago,
                read_messages=True,
                send_messages=True,
                connect=True,
                speak=True,
            )

            creator = discord.utils.get(self.ctx.guild.members, id=self.ctx.user.id)
            await discord.utils.get(
                self.ctx.guild.channels, name=self.name.lower()
            ).set_permissions(
                target=creator,
                read_messages=True,
                send_messages=True,
                connect=True,
                speak=True,
            )

            await self.ctx.edit_original_response(
                content=(
                    f"Channel {self.name.lower()} créé !"
                ), view=None
            )
        except Exception as e:
            logging.error(f'Error in command "create_channel": {e}', exc_info=True)
            print(e, "create_channel")
            await self.ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande.", view=None
            )
            return

@tree.command(
    name="creer_channel",
    description="Créer un channel dans une catégorie et lui donne les bonnes permissions !",
)
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(
    nom_channel="Nom du channel a créer"
)
@discord.app_commands.choices(
    type=[
        discord.app_commands.Choice(name="Vocal", value=0),
        discord.app_commands.Choice(name="Textuel", value=1),
    ]
)
async def create_channel(ctx, nom_channel: str, type: discord.app_commands.Choice[int]):
    """
    Create a channel in a category and set the appropriate permissions.

    Args:
        ctx: The context of the command.
        nom_channel (str): The name of the channel to create.
        type (discord.app_commands.Choice[int]): The type of channel to create.
    """
    try:
        categories = [category for category in ctx.guild.categories if category.name != "== Bienvenue à l'IPI Lyon ==" and category.name != "======== STAFF IPI ========" and category.name != "======= League IPI =======" and category.name != "Défis join league" and category.name != "===== Espace Citoyen =====" and category.name != "=========== WOOHP ===========" and category.name != "====== Espace Admis ======" and category.name != "======== ALUMNI ========" and category.name != "===== IPI Apprenants ====="]
        if not categories:
            await ctx.response.send_message("Il n'y a aucune catégorie sur ce serveur.", ephemeral=True)
            return

        view = CategorySelectUniqueChannel(categories, ctx, type.value, nom_channel)
        await ctx.response.send_message("Veuillez sélectionner une catégorie :", view=view, ephemeral=True)

    except Exception as e:
        logging.error(f'Error in command "create_channel": {e}', exc_info=True)
        print(e, "create_channel")
        await ctx.edit_original_response(
            content="Une erreur s'est produite lors de l'exécution de la commande."
        )
        return


class CategorySelectMultipleChannel(discord.ui.View):
    def __init__(self, categories_select, ctx, type_channel, name, nb_channel):
        super().__init__()
        self.add_item(CategoryDropdownMultipleChannel(categories_select, ctx, type_channel, name, nb_channel))

class CategoryDropdownMultipleChannel(discord.ui.Select):
    def __init__(self, categories_select, ctx, type_channel, name, nb_channel):
        options = [
            discord.SelectOption(label=category.name.replace("=",""), value=category.name) for category in categories_select
        ]
        self.ctx = ctx
        self.type_channel = type_channel
        self.name = name
        self.nb_channel = nb_channel
        super().__init__(placeholder="Choisissez une catégorie...", options=options)


    async def callback(self, interaction: discord.Interaction):
        category_object = discord.utils.get(
                self.ctx.guild.categories, name=self.values[0]
            )
        try:
            self.ctx.edit_original_response(content="J'y travaille...")
            server = self.ctx.guild
            pedago = discord.utils.get(self.ctx.guild.roles, name="Team Pedago IPI")
            creator = discord.utils.get(self.ctx.guild.members, id=self.ctx.user.id)

            for i in range(self.nb_channel):
                if self.type_channel == 0:
                    await server.create_voice_channel(
                        name=self.name.lower()+"-"+str(i+1), category=category_object
                    )
                else:
                    await server.create_text_channel(
                        name=self.name.lower()+"-"+str(i+1), category=category_object
                    )

                await discord.utils.get(
                    self.ctx.guild.channels, name=self.name.lower()+"-"+str(i+1)
                ).set_permissions(
                    target=pedago,
                    read_messages=True,
                    send_messages=True,
                    connect=True,
                    speak=True,
                )

                await discord.utils.get(
                    self.ctx.guild.channels, name=self.name.lower()+"-"+str(i+1)
                ).set_permissions(
                    target=creator,
                    read_messages=True,
                    send_messages=True,
                    connect=True,
                    speak=True,
                )

            await self.ctx.edit_original_response(
                content=(
                    f"Les channels ont été créés !"
                ), view=None
            )
        except Exception as e:
            logging.error(f'Error in command "create_channel": {e}', exc_info=True)
            print(e, "create_channel")
            await self.ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande.", view=None
            )
            return

@tree.command(
    name="creer_multiple_channels",
    description="Créer des channels dans une catégorie et lui donne les bonnes permissions !",
)
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(
    nom_channel="Nom de base des channels a créer",
    nb_channel="Nombre de channels a créer"
)
@discord.app_commands.choices(
    type=[
        discord.app_commands.Choice(name="Vocal", value=0),
        discord.app_commands.Choice(name="Textuel", value=1),
    ]
)
async def creer_multiple_channels(ctx, nom_channel: str, nb_channel:int , type: discord.app_commands.Choice[int]):
    """
    Create a channel in a category and set the appropriate permissions.

    Args:
        ctx: The context of the command.
        nom_channel (str): The name of the channel to create.
        type (discord.app_commands.Choice[int]): The type of channel to create.
    """
    try:
        categories = [category for category in ctx.guild.categories if category.name != "== Bienvenue à l'IPI Lyon ==" and category.name != "======== STAFF IPI ========" and category.name != "======= League IPI =======" and category.name != "Défis join league" and category.name != "===== Espace Citoyen =====" and category.name != "=========== WOOHP ===========" and category.name != "====== Espace Admis ======" and category.name != "======== ALUMNI ========" and category.name != "===== IPI Apprenants ====="]
        if not categories:
            await ctx.response.send_message("Il n'y a aucune catégorie sur ce serveur.", ephemeral=True)
            return

        view = CategorySelectMultipleChannel(categories, ctx, type.value, nom_channel, nb_channel)
        await ctx.response.send_message("Veuillez sélectionner une catégorie :", view=view, ephemeral=True)

    except Exception as e:
        logging.error(f'Error in command "create_channel": {e}', exc_info=True)
        print(e, "create_channel")
        await ctx.edit_original_response(
            content="Une erreur s'est produite lors de l'exécution de la commande."
        )
        return



@tree.command(
    name="supprimer_categorie",
    description="Supprime la catégorie ainsi que les channels qu'elle contient",
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(nom_categorie="Nom de la catégorie a supprimer (sans les =)")
async def delete_category(ctx, nom_categorie: str):
    """
    Delete a category and its channels.

    Args:
        ctx: The context of the command.
        nom_categorie (str): The name of the category to delete.
    """
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        name_cat = f" {nom_categorie.upper()} "
        while len(name_cat) <= 27:
            name_cat = f"={name_cat}="

        nom_categorie = nom_categorie.replace(" ", "-")

        categories_with_name = []
        for category in ctx.guild.categories:
            if category.name == name_cat:
                categories_with_name.append(category)

        if len(categories_with_name) < 1:
            await ctx.edit_original_response(
                content=(
                    f"Il n'existe pas de catégorie avec le nom {name_cat}. Merci de bien vouloir corriger cela !"
                )
            )
        elif len(categories_with_name) > 1:
            await ctx.edit_original_response(
                content=(
                    f"Il existe {len(categories_with_name)} catégories avec le nom {name_cat}. Cela n'est pas possible de définir laquelle supprimer. Merci de bien vouloir corriger cela !"
                )
            )

        else:
            try:
                category_object = discord.utils.get(
                    ctx.guild.categories,
                    id=(
                        discord.utils.get(
                            ctx.guild.categories, name=name_cat.upper()
                        ).id
                    ),
                )

                if category_object is None:
                    await ctx.edit_original_response(
                        content=(f"La catégorie {name_cat.upper()} n'existe pas !")
                    )

                else:
                    try:
                        for channel in category_object.channels:
                            await channel.delete()

                        await category_object.delete()

                    except discord.errors.NotFound as e:
                        print(e)
                        send_mail(e, "delete_category")
                    await ctx.edit_original_response(
                        content=(f"Catégorie {name_cat.upper()} supprimée !")
                    )

            except AttributeError:
                await ctx.edit_original_response(
                    content=(f"La catégorie {name_cat.upper()} n'existe pas !")
                )
    except Exception as e:
        logging.error(f'Error in command "delete_category": {e}', exc_info=True)
        send_mail(e, "delete_category")
        await ctx.edit_original_response(
            content="Une erreur s'est produite lors de l'exécution de la commande."
        )
        return

@tree.command(
    name="supprimer_channel", description="Supprime un channel dans une catégorie"
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    nom_channel="Nom du channel a supprimer",
    nom_categorie="Catégorie dans lequel il est situé",
)
async def delete_channel(ctx, nom_channel: str, nom_categorie: str):
    """
    Delete a channel in a category.

    Args:
        ctx: The context of the command.
        nom_channel (str): The name of the channel to delete.
        nom_categorie (str): The category where the channel is located.
    """
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
            await ctx.edit_original_response(
                content=(
                    f"Il existe {len(categories_with_name)} catégories avec le nom {name_cat}. Merci de bien vouloir corriger cela !"
                )
            )

        else:
            try:
                category_object = discord.utils.get(
                    ctx.guild.categories,
                    id=(
                        discord.utils.get(
                            ctx.guild.categories, name=name_cat.upper()
                        ).id
                    ),
                )

                if category_object is None:
                    await ctx.edit_original_response(
                        content=(f"La catégorie {name_cat.upper()} n'existe pas !")
                    )

                else:
                    try:
                        for channels in category_object.channels:
                            if str(channels) == nom_channel:
                                await channels.delete()

                    except discord.errors.NotFound as e:
                        print(e)

                    await ctx.edit_original_response(
                        content=(
                            f"Channel {nom_channel.lower()} supprimé dans la catégorie {name_cat.upper()} !"
                        )
                    )

            except AttributeError as e:
                send_mail(e, "delete_channel")
                print(e)
                await ctx.edit_original_response(
                    content=(
                        f"Channel {nom_channel.lower()} n'éxiste pas dans la catégorie {name_cat.upper()}"
                    )
                )
    except Exception as e:
        logging.error(f'Error in command "delete_channel": {e}', exc_info=True)
        send_mail(e, "delete_channel")
        await ctx.edit_original_response(
            content="Une erreur s'est produite lors de l'exécution de la commande."
        )
        return

@tree.command(
    name="supprimer_role",
    description="Supprime le role a toutes les personnes ayant ce role",
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    role="Role a retirere aux personnes",
    role_condition="Retirer le role seulement aux personnes ayant ce role",
)
async def supprime_role(ctx, role: discord.Role, role_condition: discord.Role = None):
    """
    Remove a role from all people who have it.

    Args:
        ctx: The context of the command.
        role (discord.Role): The role to remove.
        role_condition (discord.Role, optional): The role condition to check.
    """
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
        if role_condition != None:
            MembersMention = ", ".join(
                [f"<@{m.id}>" for m in role.members if m in role_condition.members]
            )
            Members = ", ".join(
                [m.display_name for m in role.members if m in role_condition.members]
            )
            [
                await m.remove_roles(role)
                for m in role.members
                if m in role_condition.members
            ]
        else:
            MembersMention = ", ".join([f"<@{m.id}>" for m in role.members])
            Members = ", ".join([m.display_name for m in role.members])
            [await m.remove_roles(role) for m in role.members]

        await ctx.edit_original_response(
            content=(f"Role supprimé pour : {MembersMention}")
        )
        user = client.get_user(ctx.user.id)
        await user.send(content=(f"Role supprimé pour : {Members}"))

    except Exception as e:
        logging.error(f'Error in command "supprime_role": {e}', exc_info=True)
        send_mail(e, "supprime_role")
        await ctx.edit_original_response(
            content="Une erreur s'est produite lors de l'exécution de la commande."
        )
        return


@tree.command(
    name="transferer_categorie", description="Transferer une catégorie à un autre rôle"
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    nouveau_nom_categorie="Nom actuel de la catégorie a transferer",
    ancien_nom_categorie="Nouveau nom a donner a la categorie",
    nouveau_role="Nouveau role pouvant avoir acces a la categorie",
    ancien_role="Role ayant actuellement l'acces a la categorie",
    nouveau_nom_channel="Chaine de caractere servant a remplacer l'ancienne dans le nom des channels",
    ancien_nom_channel="Chaine de caractere devant etre remplacer dans le nom des channels",
)
async def transfert_category(
    ctx,
    ancien_nom_categorie: str,
    nouveau_nom_categorie: str,
    ancien_nom_channel: str,
    nouveau_nom_channel: str,
    ancien_role: discord.Role,
    nouveau_role: discord.Role,
):
    """
    Transfer a category to another role.

    Args:
        ctx: The context of the command.
        ancien_nom_categorie (str): The current name of the category to transfer.
        nouveau_nom_categorie (str): The new name to give to the category.
        ancien_nom_channel (str): The string to replace in the channel names.
        nouveau_nom_channel (str): The new string to replace the old one in the channel names.
        ancien_role (discord.Role): The role currently having access to the category.
        nouveau_role (discord.Role): The new role that will have access to the category.
    """
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
            await ctx.edit_original_response(
                content=(
                    f"Il existe {len(categories_with_name)} catégories avec le nom {name_cat}. Merci de bien vouloir corriger cela !"
                )
            )

        else:
            try:
                category = discord.utils.get(
                    ctx.guild.categories,
                    id=(
                        discord.utils.get(
                            ctx.guild.categories, name=name_cat.upper()
                        ).id
                    ),
                )

                name_cat = f" {nouveau_nom_categorie} "
                while len(name_cat) <= 27:
                    name_cat = f"={name_cat.upper()}="

                await category.edit(name=name_cat.upper())

                source_permissions = category.overwrites[ancien_role]
                target_permissions = {}

                for permission, value in source_permissions:
                    target_permissions[permission] = value

                new_overwrite = discord.PermissionOverwrite(**target_permissions)
                await category.set_permissions(
                    target=nouveau_role, overwrite=new_overwrite
                )

                await category.set_permissions(target=ancien_role, overwrite=None)

                if category is None:
                    await ctx.edit_original_response(
                        content="La catégorie spécifiée n'existe pas."
                    )
                    return

                for channel in category.channels:
                    if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                        overwrites = channel.overwrites

                        new_name = channel.name.replace(
                            ancien_nom_channel.lower().replace(" ", "-"),
                            nouveau_nom_channel.lower().replace(" ", "-"),
                        )
                        await channel.edit(name=new_name)

                        nouveau_nom_channel, ancien_nom_channel = (
                            nouveau_nom_channel.upper(),
                            ancien_nom_channel.upper(),
                        )

                        if nouveau_role is None:
                            return

                        if ancien_role is None:
                            return

                        if ancien_role in overwrites:
                            source_permissions = channel.overwrites[ancien_role]
                            target_permissions = {}

                            for permission, value in source_permissions:
                                target_permissions[permission] = value

                            new_overwrite = discord.PermissionOverwrite(
                                **target_permissions
                            )
                            await channel.set_permissions(
                                target=nouveau_role, overwrite=new_overwrite
                            )

                            await channel.set_permissions(
                                target=ancien_role, overwrite=None
                            )

                await ctx.edit_original_response(
                    content=f"La catégorie {ancien_nom_categorie} a bien été transferer du rôle {ancien_role.name} au role {nouveau_role.name}"
                )

            except Exception as e:
                send_mail(e, "transfert_category")
                await ctx.edit_original_response(
                    content=f"Une erreur est survenue, veuillez verifier que tous les paramètres sont correctes puis rééssayez. Si le problème persiste veuillez contacter Nathan SABOT DRESSY"
                )
                print(e)
    except Exception as e:
        logging.error(f'Error in command "transfert_category": {e}', exc_info=True)
        send_mail(e, "transfert_category")
        await ctx.edit_original_response(
            content="Une erreur s'est produite lors de l'exécution de la commande."
        )
        return


@tree.command(
    name="transferer_role",
    description="Transfere un role a toutes les personnes ayant un autre role",
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    ancien_role="Les personnes ayant ce role vont recevoir le nouveau",
    nouveau_role="Role a donner",
    supprimer="Faut-il supprimer le role actuel utilisé pour transferer ? (oui /non)",
)
async def transfert_role(
    ctx, ancien_role: discord.Role, nouveau_role: discord.Role, supprimer: bool
):
    """
    Transfer a role to all people who have another role.

    Args:
        ctx: The context of the command.
        ancien_role (discord.Role): The role that people currently have.
        nouveau_role (discord.Role): The role to assign.
        supprimer (bool): Whether to remove the current role used for transfer.
    """
    try:
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        OldMemberID = [m.id for m in ancien_role.members]
        OldMember = [f"<@{m.id}>" for m in ancien_role.members]
        OldMemberTxt = [m.display_name for m in ancien_role.members]
        NewRoleMember = [m.id for m in nouveau_role.members]
        OldMemberTxtMention = ", ".join(OldMember)
        OldMemberTxtNoMention = ", ".join(OldMemberTxt)

        if supprimer == True:
            for member in OldMemberID:
                await ctx.guild.get_member(member).remove_roles(ancien_role)

        for member in OldMemberID:
            await ctx.guild.get_member(member).add_roles(nouveau_role)

        NewMenberTxtMention = ", ".join(
            [f"<@{m.id}>" for m in nouveau_role.members if m.id not in NewRoleMember]
        )
        NewMenberTxt = ", ".join(
            [m.display_name for m in nouveau_role.members if m.id not in NewRoleMember]
        )
        if supprimer == True:
            await ctx.edit_original_response(
                content=(
                    f"Role supprimer à : {OldMemberTxtMention}\n\nRole donné à : {NewMenberTxtMention}"
                )
            )
            user = client.get_user(ctx.user.id)
            await user.send(
                content=(
                    f"Role supprimer à : {OldMemberTxtNoMention}\n\nRole donné à : {NewMenberTxt}"
                )
            )

        else:
            await ctx.edit_original_response(
                content=(f"Role donné à : {NewMenberTxtMention}")
            )
            user = client.get_user(ctx.user.id)
            await user.send(content=(f"Role donné à : {NewMenberTxt}"))
    except Exception as e:
        logging.error(f'Error in command "transfert_role": {e}', exc_info=True)
        send_mail(e, "transfert_role")
        await ctx.edit_original_response(
            content="Une erreur s'est produite lors de l'exécution de la commande."
        )
        return

# @tree.command(name = "print_categories", description = "Affiche le nom de categorie")
# @app_commands.checks.has_permissions(administrator=True)
async def categories(ctx):
    """
    Print the names of categories.

    Args:
        ctx: The context of the command.
    """
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

                    result += (name_cat) + "\n"
                await user.send(content=result)
            else:
                await ctx.edit_original_response(
                    content="Le serveur ne possède pas de catégories."
                )
                return

        except Exception as e:
            logging.error(f'Error in command "print_categories": {e}', exc_info=True)
            send_mail(e, "print_categories")
            await ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande."
            )
            return
    except discord.app_commands.errors.MissingPermissions:
        await ctx.response.send_message(
            content="Tu n'as pas la permission d'effectuer cette commande !",
            ephemeral=True,
        )
        return

@atelier_add_proposition.error
@atelier_add_role.error
@atelier_remove_role.error
@atelier_list_role.error
@atelier_modify_max_inscrits_promo.error
@atelier_modify_max_inscrits.error
@atelier_modify_max_inscription.error
@atelier_modify_button_label.error
@atelier_show_config.error
@atelier_clear_all.error
@atelier_show_inscrits.error
@atelier_non_inscrit.error
@activate_participation.error
@deactivate_participation.error
@atelier_relance.error
@ping.error
@assign_role.error
@clear_messages.error
@create_category.error
@create_channel.error
@creer_multiple_channels.error
@delete_category.error
@delete_channel.error
@supprime_role.error
@transfert_category.error
@transfert_role.error
async def error_handler(ctx, error):
    """
    Error handler for the create_category command.

    Args:
        ctx: The context of the command.
        error: The error that occurred.
    """
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await ctx.response.send_message(
            content="Tu n'as pas la permission d'effectuer cette commande !",
            ephemeral=True,
        )

client.run(DataJson["DISCORD_TOKEN"])