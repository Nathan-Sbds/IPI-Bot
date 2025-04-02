import discord
from discord import app_commands
import json
import logging
from utils.send_mail import send_mail

async def setup(client, tree):
    @tree.command(
        name="obtenir_email_promo",
        description="Obtenir l'email pour une promo",
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
        promo="Promo pour laquelle obtenir l'email",
    )
    async def obtenir_email_promo(ctx: discord.Interaction, promo: discord.Role):
        """
        Get the email for a specific promo.

        Args:
            ctx: The context of the command.
            promo (discord.Role): The promo role to get the email for.
        """
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
        try:
            with open("..email_promo.json", "r") as f:
                data = json.load(f)
                if str(promo.id) in data:
                    email = data[str(promo.id)]
                    await ctx.edit_original_response(
                        content=(
                            f"L'email pour la promo {promo.name} est : `{email}`"
                        )
                    )
                else:
                    await ctx.edit_original_response(
                        content=(
                            f"Aucun email défini pour la promo {promo.name}."
                        )
                    )
        except FileNotFoundError:
            await ctx.edit_original_response(
                content="Aucun email défini pour les promos."
            )
        except json.JSONDecodeError:
            await ctx.edit_original_response(
                content="Erreur lors de la lecture du fichier email_promo.json."
            )
        except Exception as e:
            logging.error(f'Error in command "obtenir_email_promo": {e}', exc_info=True)
            send_mail(e, "obtenir_email_promo")
            await ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande."
            )
        
if __name__ == '__main__':
    pass
