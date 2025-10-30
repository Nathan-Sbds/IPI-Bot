import discord
import logging
from discord import app_commands
from utils.CategoryUniqueChannelView import CategorySelectUniqueChannel

async def setup(client, tree):
    @tree.command(
        name="creer_channel",
        description="Créer un channel dans une catégorie et lui donne les bonnes permissions !",
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(
        nom_channel="Nom du channel a créer",
        limite_utilisateurs="Nombre maximum d'utilisateurs pour un salon vocal (0 pour illimité, voix uniquement)",
        bitrate="Débit binaire en kb pour un salon vocal (voix uniquement)"
    )
    @discord.app_commands.choices(
        type=[
            discord.app_commands.Choice(name="Vocal", value=0),
            discord.app_commands.Choice(name="Textuel", value=1),
        ]
    )
    async def create_channel(
        ctx,
        nom_channel: str,
        type: discord.app_commands.Choice[int],
        limite_utilisateurs: int = 0,
        bitrate: int = 64,
    ):
        """
        Create a channel in a category and set the appropriate permissions.

        Args:
            ctx: The context of the command.
            nom_channel (str): The name of the channel to create.
            type (discord.app_commands.Choice[int]): The type of channel to create.
            limite_utilisateurs (int, optional): Maximum number of users for a voice channel (0 for no limit).
            bitrate (int, optional): Voice channel bitrate in kb.
        """
        try:
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

            view = CategorySelectUniqueChannel(
                categories,
                ctx,
                type.value,
                nom_channel,
                limite_utilisateurs,
                bitrate,
            )
            message = "Veuillez sélectionner une catégorie :"
            if type.value == 1:
                message += "\n\n⚠️ Le bitrate et la limite d'utilisateurs ne s'appliquent qu'aux channels vocaux et seront ignorés pour un channel textuel."

            await ctx.response.send_message(message, view=view, ephemeral=True)

        except Exception as e:
            logging.error(f'Error in command "create_channel": {e}', exc_info=True)
            print(e, "create_channel")
            await ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande."
            )
            return

if __name__ == "__main__":
    pass