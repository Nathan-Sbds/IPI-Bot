import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_relance", description="Relance les personnes n'etant pas inscrits"
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_relance(ctx):
        """
        Remind people who have not registered.

        Args:
            ctx: The context of the command.
        """
        with open("././participations.json", "r") as file:
            data = json.load(file)

        channel = client.get_channel(ctx.channel_id)
        role = discord.utils.get(ctx.guild.roles, name="Non Inscrit")

        if role:
            await channel.send(
                content=f"{role.mention} Vous n'etes pas encore inscrits à {data['max_inscription']} atelier{'s' if data['max_inscription'] > 1 else ''}, n'oubliez pas de vous inscrire !"
            )
            await ctx.response.send_message(
                content="Les personnes n'etant pas inscrites ont été relancées",
                ephemeral=True,
            )
        else:
            await ctx.response.send_message(
                content="Une erreur s'est produite", ephemeral=True
            )

if __name__ == '__main__':
    pass
