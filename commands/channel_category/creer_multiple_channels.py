import logging
import discord
from discord import app_commands
from utils.CategoryMultipleChannelView import CategorySelectMultipleChannel

async def setup(client, tree):
    @tree.command(
        name="creer_multiple_channels",
        description="Créer des channels dans une catégorie et lui donne les bonnes permissions !",
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(
        nom_channel="Nom de base des channels a créer",
        nb_channel="Nombre de channels a créer inférieur à 20",
        limite_utilisateurs="Nombre maximum d'utilisateurs pour un salon vocal (0 pour aucune limite, voix uniquement)",
        bitrate="Débit binaire en kb pour un salon vocal (voix uniquement)"
    )
    @discord.app_commands.choices(
        type=[
            discord.app_commands.Choice(name="Vocal", value=0),
            discord.app_commands.Choice(name="Textuel", value=1),
        ]
    )
    async def creer_multiple_channels(
        ctx,
        nom_channel: str,
        nb_channel: int,
        type: discord.app_commands.Choice[int],
        limite_utilisateurs: int = 0,
        bitrate: int = 64,
    ):
        """
        Create a channel in a category and set the appropriate permissions.

        Args:
            ctx: The context of the command.
            nom_channel (str): The name of the channel to create.
            nb_channel (int): The number of channels to create (1-20).
            type (discord.app_commands.Choice[int]): The type of channel to create.
            limite_utilisateurs (int, optional): Maximum number of users for voice channels (0 for no limit).
            bitrate (int, optional): Voice channel bitrate in kb.
        """
        try:
            if nb_channel > 20:
                await ctx.response.send_message("Le nombre de channels ne peut pas dépasser 20.", ephemeral=True)
                return
            if nb_channel < 1:
                await ctx.response.send_message("Le nombre de channels doit être supérieur à 0.", ephemeral=True)
                return

            if limite_utilisateurs not in range(1, 100) and limite_utilisateurs != 0:
                await ctx.response.send_message(
                    "La limite d'utilisateurs doit être comprise entre 1 et 99, ou 0 pour aucune limite.",
                    ephemeral=True,
                )
                return

            if bitrate < 8 or bitrate > 96:
                await ctx.response.send_message(
                    "Le bitrate doit être compris entre 8 et 96 kb.",
                    ephemeral=True,
                )
                return
            categories = [category for category in ctx.guild.categories if category.name != "== Bienvenue à l'IPI Lyon ==" and category.name != "======== STAFF IPI ========" and category.name != "======= League IPI =======" and category.name != "Défis join league" and category.name != "===== Espace Citoyen =====" and category.name != "=========== WOOHP ===========" and category.name != "====== Espace Admis ======" and category.name != "======== ALUMNI ========" and category.name != "===== IPI Apprenants ====="]
            if not categories:
                await ctx.response.send_message("Il n'y a aucune catégorie sur ce serveur.", ephemeral=True)
                return

            view = CategorySelectMultipleChannel(
                categories,
                ctx,
                type.value,
                nom_channel,
                nb_channel,
                limite_utilisateurs,
                bitrate,
            )
            message = "Veuillez sélectionner une catégorie :"
            if type.value == 1:
                message += "\n\n⚠️ Le bitrate et la limite d'utilisateurs ne s'appliquent qu'aux channels vocaux et seront ignorés pour des channels textuels."

            await ctx.response.send_message(message, view=view, ephemeral=True)

        except Exception as e:
            logging.error(f'Error in command "create_channel": {e}', exc_info=True)
            print(e, "create_channel")
            await ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande."
            )
            return