import discord
import logging
from discord import app_commands
from utils.send_mail import send_mail

async def setup(client, tree):
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
        
if __name__ == "__main__":
    pass