import discord
from discord import app_commands
import logging
from utils.send_mail import send_mail

async def setup(client, tree):

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
        
if __name__ == "__main__":
    pass