import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_config",
        description="Afficher les informations de configuration du module atelier",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_show_config(ctx):
        """
        Show the configuration information of the workshop module.

        Args:
            ctx: The context of the command.
        """
        with open("././participations.json", "r") as file:
            data = json.load(file)

        roles_id = data["roles"]
        roles = []
        for role_id in roles_id:
            roles.append(ctx.guild.get_role(role_id))

        roles_list = ""

        for role in roles:
            roles_list += f"- {role.name}\n"

        atelier_list = ""
        for proposition in data["propositions"]:
            atelier_list += f"- {proposition['titre']}\n"

        if data["active"]:
            active = "Inscriptions ouvertes"
        else:
            active = "Inscriptions fermées"

        embed = discord.Embed(
            title="__Configuration__",
            description="Voici les informations de configuration :",
            color=discord.Color.green(),
        )

        embed.add_field(
            name=f"Statut des inscriptions :",
            value=f"{active}",
            inline=False,
        )

        embed.add_field(
            name=f"Libellé du bouton :",
            value=f"{data['button_label']}",
            inline=False,
        )

        embed.add_field(
            name=f"Nombre maximum d'inscrits par atelier :",
            value=f"{data['max_inscrits']}",
            inline=False,
        )

        embed.add_field(
            name=f"Nombre maximum d'inscrits par promo :",
            value=f"{data['max_inscrits_promo']}",
            inline=False,
        )

        embed.add_field(
            name="Nombre d'inscription possible par utilisateur",
            value=f"{data['max_inscription']}",
            inline=False,
        )

        embed.add_field(
            name=f"Rôles autorisés à participer :",
            value=f"{roles_list}",
            inline=False,
        )

        embed.add_field(
            name=f"Ateliers :",
            value=f"{atelier_list}",
            inline=False,
        )

        await ctx.response.send_message(embed=embed, ephemeral=True)

if __name__ == '__main__':
    pass
