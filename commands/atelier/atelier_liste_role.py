import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_liste_role",
        description="Lister les rôles autorisés à utiliser le module atelier",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_list_role(ctx):
        """
        List the roles authorized to use the workshop module.

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

        await ctx.response.send_message(
            content=f"Les rôles autorisés à participer sont :\n{roles_list}", ephemeral=True
        )
if __name__ == '__main__':
    pass
