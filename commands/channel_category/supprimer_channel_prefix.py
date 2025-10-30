import logging
import discord
from discord import app_commands
from utils.CategoryDeleteChannelView import CategorySelectDeleteChannel


async def setup(client, tree):
    @tree.command(
        name="supprimer_channel",
        description="Supprime un channel commençant par un texte dans une catégorie",
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(
        prefix="Préfixe du channel à supprimer",
    )
    @discord.app_commands.choices(
        type=[
            discord.app_commands.Choice(name="Vocal", value=0),
            discord.app_commands.Choice(name="Textuel", value=1),
        ]
    )
    async def delete_channel(
        ctx,
        prefix: str,
        type: discord.app_commands.Choice[int],
    ):
        try:
            categories = [
                category
                for category in ctx.guild.categories
                if category.name
                not in {
                    "== Bienvenue à l'IPI Lyon ==",
                    "======== STAFF IPI ========",
                    "======= League IPI =======",
                    "Défis join league",
                    "===== Espace Citoyen =====",
                    "=========== WOOHP ===========",
                    "====== Espace Admis ======",
                    "======== ALUMNI ========",
                    "===== IPI Apprenants =====",
                }
            ]

            if not categories:
                await ctx.response.send_message(
                    "Il n'y a aucune catégorie sur ce serveur.", ephemeral=True
                )
                return

            view = CategorySelectDeleteChannel(categories, ctx, type.value, prefix)
            await ctx.response.send_message(
                "Veuillez sélectionner une catégorie :",
                view=view,
                ephemeral=True,
            )

        except Exception as e:
            logging.error(f'Error in command "delete_channel_prefix": {e}', exc_info=True)
            if ctx.response.is_done():
                await ctx.edit_original_response(
                    content="Une erreur s'est produite lors de l'exécution de la commande."
                )
            else:
                await ctx.response.send_message(
                    "Une erreur s'est produite lors de l'exécution de la commande.",
                    ephemeral=True,
                )
            return
