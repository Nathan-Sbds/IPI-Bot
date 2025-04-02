import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_inscriptions", description="Afficher les inscrits des ateliers"
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_show_inscrits(ctx):
        """
        Show the participants of the workshops.

        Args:
            ctx: The context of the command.
        """
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("././participations.json", "r") as file:
            data = json.load(file)

        for proposition in data["propositions"]:
            embed = discord.Embed(
                title="Inscriptions",
                description="Voici les inscrits aux ateliers :",
                color=discord.Color.green(),
            )
            proposition_id = proposition["id"]
            proposition_titre = proposition["titre"]
            proposition_voters = ""
            for voter in data["participations"]:
                if proposition_id in data["participations"][voter]:
                    member = ctx.guild.get_member(int(voter))
                    if member:
                        proposition_voters += f"- {member.display_name}\n"

            embed.add_field(
                name=f"Atelier : {proposition_titre}",
                value=f"{proposition_voters}",
                inline=False,
            )
            user = client.get_user(ctx.user.id)
            await user.send(embed=embed)
        await ctx.edit_original_response(
            content="Les inscrits ont été envoyés en message privé"
        )
if __name__ == '__main__':
    pass
