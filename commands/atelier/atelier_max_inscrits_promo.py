import discord
from discord import app_commands
import json
from utils.atelier_get_role_count import atelier_get_role_count

async def setup(client, tree):
    @tree.command(
        name="atelier_max_inscrits_promo",
        description="Modifier le nombre maximum d'inscrits par promo",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_modify_max_inscrits_promo(ctx, max_inscrits: int):
        """
        Modify the maximum number of participants per promotion.

        Args:
            ctx: The context of the command.
            max_inscrits (int): The maximum number of participants per promotion.
        """
        with open("././participations.json", "r") as file:
            data = json.load(file)

        for proposition in data["propositions"]:
            if len(atelier_get_role_count(ctx, proposition["id"])) > max_inscrits:
                await ctx.response.send_message(
                    content=f"Le nombre maximum d'inscrits ne peut pas être inférieur au nombre d'inscrits actuel",
                    ephemeral=True,
                )
                return

        data["max_inscrits_promo"] = max_inscrits

        with open("././participations.json", "w") as file:
            json.dump(data, file)

        await ctx.response.send_message(
            content=f"Le nombre maximum d'inscrits par promo est maintenant de {max_inscrits}",
            ephemeral=True,
        )
if __name__ == '__main__':
    pass
