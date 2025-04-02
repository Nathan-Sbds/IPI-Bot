import discord
from discord import app_commands
import json
import logging
from utils.send_mail import send_mail

async def setup(client, tree):
    @tree.command(
        name="definir_email_promo",
        description="Définir l'email pour une promo",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
        "Team IPI",
    )
    @app_commands.describe(
        email="Email à définir",
        promo="Promo à définir",
    )
    async def definir_email_promo(ctx: discord.Interaction, email: str, promo: discord.Role):
        """
        Define the email for a specific promo.

        Args:
            ctx: The context of the command.
            email (str): The email to set.
            promo (discord.Role): The promo role to assign the email to.
        """
        try:
            await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
            open ("././email_promo.json", "w").write(
                json.dumps(
                    {
                        promo.id: email.lower(),
                    },
                    indent=4,
                    ensure_ascii=False,
                )
            )
            await ctx.edit_original_response(
                content=(
                    f"L'email `{email}` a été défini pour la promo {promo.name} !"
                )
            )
        except Exception as e:
            logging.error(f'Error in command "definir_email_promo": {e}', exc_info=True)
            send_mail(e, "definir_email_promo")
            await ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande."
            )
            return
if __name__ == '__main__':
    pass
