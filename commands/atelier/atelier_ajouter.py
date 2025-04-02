import discord
from discord import app_commands
import json
from utils.AtelierView import AtelierView
from utils.atelier_result_in_time import atelier_result_in_time

async def setup(client, tree):
    @tree.command(name="atelier_ajouter", description="Ajouter une proposition")
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_add_proposition(ctx, titre: str, description: str):
        """
        Add a workshop proposition.

        Args:
            ctx: The context of the command.
            titre (str): The title of the proposition.
            description (str): The description of the proposition.
        """
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("././participations.json", "r") as file:
            data = json.load(file)

        proposition_id = data["next_proposition_id"]

        view = AtelierView(client)
        client.add_view(view)
        view.timeout = None

        embed = discord.Embed(
            title=titre,
            description=description,
            color=discord.Color.red(),
        )

        message = await client.get_channel(ctx.channel_id).send(
            embed=embed,
            view=view,
        )

        data["propositions"].append(
            {
                "id": proposition_id,
                "message_id": message.id,
                "channel_id": message.channel.id,
                "titre": titre,
            }
        )

        data["next_proposition_id"] += 1

        with open("././participations.json", "w") as file:
            json.dump(data, file)

        await atelier_result_in_time(ctx, True)
        await ctx.edit_original_response(content=f"La proposition {titre} a été ajoutée.")

if __name__ == '__main__':
    pass
