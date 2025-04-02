import discord
import logging
from discord import app_commands
from utils.send_mail import send_mail

async def setup(client, tree):
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

if __name__ == "__main__":
    pass