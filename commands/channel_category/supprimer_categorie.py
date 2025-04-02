import logging
import discord
from discord import app_commands
from utils.send_mail import send_mail

async def setup(client, tree):
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
        
if __name__ == "__main__":
    pass