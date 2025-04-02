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

if __name__ == "__main__":
    pass