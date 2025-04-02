import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_desactiver",
        description="Desactive les inscriptions pour les ateliers",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def deactivate_participation(ctx):
        """
        Deactivate registrations for workshops.

        Args:
            ctx: The context of the command.
        """
        with open("././participations.json", "r") as file:
            data = json.load(file)

        data["active"] = False

        with open("././participations.json", "w") as file:
            json.dump(data, file)

        await ctx.response.send_message(
            content="Les inscriptions sont désormais fermées", ephemeral=True
        )
if __name__ == '__main__':
    pass
