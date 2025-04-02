import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_supprimer",
        description="Supprimer toutes les données et inscriptions du module atelier",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_clear_all(ctx):
        """
        Clear all data and registrations of the workshop module.

        Args:
            ctx: The context of the command.
        """
        with open("././participations.json", "r") as file:
            data = json.load(file)

        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        channel = client.get_channel(ctx.channel_id)
        for propositions in data["propositions"]:
            try:
                message = await channel.fetch_message(propositions["message_id"])
                await message.delete()
            except discord.errors.NotFound:
                pass
        if data["result_id"] != 0:
            message = await channel.fetch_message(data["result_id"])
            await message.delete()

        data = {
            "max_inscription": 2,
            "max_inscrits": 14,
            "max_inscrits_promo": 4,
            "roles": [],
            "propositions": [],
            "participations": {},
            "next_proposition_id": 1,
            "result_id": 0,
            "active": False,
            "button_label": "S'inscrire à l'Atelier",
        }

        with open("././participations.json", "w") as file:
            json.dump(data, file)

        await ctx.edit_original_response(content="Toutes les données ont été supprimées")

if __name__ == '__main__':
    pass
