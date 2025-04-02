import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_max_inscription",
        description="Modifier le nombre maximum d'ateliers auxquels il est possible de participer",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_modify_max_inscription(ctx, max_inscription: int):
        """
        Modify the maximum number of workshops a user can participate in.

        Args:
            ctx: The context of the command.
            max_inscription (int): The maximum number of workshops a user can participate in.
        """
        with open("././participations.json", "r") as file:
            data = json.load(file)

        if max_inscription < 1:
            await ctx.response.send_message(
                content="Le nombre maximum d'ateliers auxquels il est possible de participer doit être d'au moins 1.",
                ephemeral=True,
            )
            return

        for user_id, participations_list in data["participations"].items():
            if (
                participations_list is not None
                and len(participations_list) > max_inscription
            ):
                await ctx.response.send_message(
                    content=f"Le nombre maximum d'ateliers auxquels il est possible de participer ne peut pas être inférieur au nombre d'ateliers auxquels {ctx.guild.get_member(int(user_id)).display_name} est déjà inscrit(e).",
                    ephemeral=True,
                )
                return

        data["max_inscription"] = max_inscription

        with open("././participations.json", "w") as file:
            json.dump(data, file)

        await ctx.response.send_message(
            content=f"Le nombre maximum d'ateliers auxquels on peut participer est maintenant de {max_inscription}.",
            ephemeral=True,
        )
if __name__ == '__main__':
    pass
