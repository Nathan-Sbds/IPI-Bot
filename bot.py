import discord,json,logging,os
from discord import app_commands
from utils.AtelierView import AtelierView
from utils.ResultView import ResultView

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
folder_path = "./Attachments"

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

try:
    with open("email_promo.json", "r") as file:
        dataEmail = json.load(file)
except FileNotFoundError:
    dataEmail = {}
    with open("email_promo.json", "w") as file:
        json.dump(dataEmail, file)

try:
    with open("participations.json", "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = {"max_inscription": 2, "max_inscrits": 14, "max_inscrits_promo": 4, "roles": [], "propositions": [], "participations": {}, "next_proposition_id": 1, "result_id": 0, "active": False, "button_label": "S'inscrire \u00e0 l'Atelier"}
    with open("participations.json", "w") as file:
        json.dump(data, file)

privateCommandsList = ["ping", "clear_dm"]

@client.event
async def on_ready():
    """
    Event handler for when the bot is ready.
    """
    await client.change_presence(
        status=discord.Status.online, activity=discord.Game("Gerer les choses...")
    )

    for filename in os.listdir('./commands'):
        if os.path.isdir(os.path.join('./commands', filename)):
            for command_file in os.listdir(f'./commands/{filename}'):
                if command_file.endswith('.py'):
                    try:
                        module = __import__(f'commands.{filename}.{command_file[:-3]}', fromlist=['setup'])
                        if hasattr(module, 'setup'):
                            await module.setup(client, tree)
                            print(f"Loaded command: {command_file[:-3]} from {filename}")
                    except Exception as e:
                        logging.error(f"Error loading command {command_file} from {filename}: {e}", exc_info=True)


    await tree.sync()

    for _ in dataSecret["images"]:
        view = ResultView()
        client.add_view(view)

    for _ in data["propositions"]:
        view = AtelierView()
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

@client.event
async def on_button_click(interaction: discord.Interaction, button: discord.ui.Button):
    """
    Event handler for button clicks.
    """
    if "button" in button.custom_id or "vote_button" in button.custom_id:
        view = client.get_view(button.view.id)
        await view.button_callback(interaction, button)

client.run(DataJson["DISCORD_TOKEN"])