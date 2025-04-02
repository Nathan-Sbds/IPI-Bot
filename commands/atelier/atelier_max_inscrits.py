import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_max_inscrits", description="Modifier le nombre maximum d'inscrits"
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_modify_max_inscrits(ctx, max_inscrits: int):
        """
        Modify the maximum number of participants.

        Args:
            ctx: The context of the command.
            max_inscrits (int): The maximum number of participants.
        """
        with open("././participations.json", "r") as file:
            data = json.load(file)

        participations = data["participations"]
        participation_ids = [
            participation_id
            for participation_ids_list in participations.values()
            if participation_ids_list is not None
            for participation_id in participation_ids_list
        ]

        for proposition in data["propositions"]:
            if participation_ids.count(proposition["id"]) > max_inscrits:
                await ctx.response.send_message(
                    content=f"Le nombre maximum d'inscrits ne peut pas être inférieur au nombre d'inscrits actuel",
                    ephemeral=True,
                )
                return

        data["max_inscrits"] = max_inscrits

        with open("././participations.json", "w") as file:
            json.dump(data, file)

        await ctx.response.send_message(
            content=f"Le nombre maximum d'inscrits par atelier est maintenant de {max_inscrits}",
            ephemeral=True,
        )

if __name__ == '__main__':
    pass
