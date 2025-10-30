import logging
import discord
from discord import app_commands
from utils.CategoryDeleteChannelView import CategorySelectDeleteMultipleChannel


async def setup(client, tree):
    @tree.command(
        name="supprimer_multiple_channels",
        description="Supprime plusieurs channels commençant par un texte dans une catégorie",
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(
        prefix="Préfixe des channels à supprimer",
        nb_channel="Nombre maximum de channels à supprimer (1-20)",
    )
    @discord.app_commands.choices(
        type=[
            discord.app_commands.Choice(name="Vocal", value=0),
            discord.app_commands.Choice(name="Textuel", value=1),
        ]
    )
    async def delete_multiple_channels(
        ctx,
        prefix: str,
        nb_channel: int,
        type: discord.app_commands.Choice[int],
    ):
        try:
            if nb_channel < 1 or nb_channel > 20:
                await ctx.response.send_message(
                    "Le nombre de channels à supprimer doit être compris entre 1 et 20.",
                    ephemeral=True,
                )
                return

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

            view = CategorySelectDeleteMultipleChannel(
                categories,
                ctx,
                type.value,
                prefix,
                nb_channel,
            )

            await ctx.response.send_message(
                "Veuillez sélectionner une catégorie :",
                view=view,
                ephemeral=True,
            )

        except Exception as e:
            logging.error(
                f'Error in command "delete_multiple_channel_prefix": {e}', exc_info=True
            )
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
